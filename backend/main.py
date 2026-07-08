# -*- coding: utf-8 -*-
"""
StarHubClusterMonitor 后端 (FastAPI)
从 MySQL(starhub) 读取 4 张表并聚合，提供大屏所需 REST API。
端点：
  GET /api/health
  GET /api/meta
  GET /api/overview      指标卡
  GET /api/hosts         主机状态矩阵
  GET /api/distribution  机房/型号/负责人分布
  GET /api/trend         集群性能趋势(按小时)
  GET /api/disk-top      磁盘I/O TOP
  GET /api/alerts        实时告警
  GET /api/dashboard     以上全部(前端一次性拉取)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import db

DISK_UTIL = ['sda_util', 'sdb_util', 'sdc_util', 'sdd_util', 'sde_util']
DISK_UTIL_SQL = "', '".join(DISK_UTIL)

app = FastAPI(title="StarHubClusterMonitor API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)


def _status_of(cpu, mem, disk):
    if cpu > 90 or disk > 95:
        return "critical"
    if cpu > 80 or disk > 85 or mem > 85:
        return "warn"
    return "ok"


def get_host_status():
    pref = db.query("""
        SELECT h.hostid, h.hostname, h.owner, h.model, h.location1,
               AVG(CASE WHEN p.metric='cpu_usage' THEN p.value END) AS cpu,
               AVG(CASE WHEN p.metric='mem_used'  THEN p.value END) AS mu,
               AVG(CASE WHEN p.metric='mem_free'  THEN p.value END) AS mf,
               AVG(CASE WHEN p.metric='mem_buff'  THEN p.value END) AS mb,
               AVG(CASE WHEN p.metric='mem_cache' THEN p.value END) AS mc,
               AVG(CASE WHEN p.metric='net_in'    THEN p.value END) AS net_in,
               AVG(CASE WHEN p.metric='load1'     THEN p.value END) AS `load`
        FROM `host` h LEFT JOIN pref_metric p ON p.hostid=h.hostid
        GROUP BY h.hostid, h.hostname, h.owner, h.model, h.location1
    """)
    disk = {r["hostid"]: r["disk"] for r in db.query(
        f"SELECT hostid, AVG(value) AS disk FROM disk_metric "
        f"WHERE metric IN ('{DISK_UTIL_SQL}') GROUP BY hostid")}

    result = []
    for r in pref:
        mu, mf, mb, mc = r["mu"] or 0, r["mf"] or 0, r["mb"] or 0, r["mc"] or 0
        tot = mu + mf + mb + mc
        mem = round(mu / tot * 100, 1) if tot > 0 else 0
        dsk = round(disk.get(r["hostid"]) or 0, 1)
        cpu = round(r["cpu"] or 0, 1)
        result.append({
            "hostid": r["hostid"], "hostname": r["hostname"],
            "owner": r["owner"], "model": r["model"], "location1": r["location1"],
            "cpu": cpu, "mem": mem, "disk": dsk,
            "netIn": round(r["net_in"] or 0, 1), "load": round(r["load"] or 0, 2),
            "status": _status_of(cpu, mem, dsk),
        })
    return result


def get_overview(hosts):
    n = len(hosts) or 1
    avg = lambda k: round(sum(h[k] for h in hosts) / n, 1)
    alert = sum(1 for h in hosts if h["status"] != "ok")
    return {
        "totalHosts": len(hosts), "onlineHosts": len(hosts),
        "avgCpu": avg("cpu"), "avgMem": avg("mem"),
        "avgDisk": avg("disk"), "avgLoad": round(sum(h["load"] for h in hosts) / n, 2),
        "alertCount": alert,
    }


def get_distribution():
    room = db.query("SELECT location1 AS name, COUNT(*) AS value FROM `host` GROUP BY location1 ORDER BY location1")
    model = db.query("SELECT model AS name, COUNT(*) AS value FROM `host` GROUP BY model ORDER BY value DESC")
    owner = db.query("SELECT owner AS name, COUNT(*) AS value FROM `host` GROUP BY owner ORDER BY value DESC")
    return (room, model, owner)


def get_trend():
    pref = db.query(f"""
        SELECT DATE_FORMAT(dt,'%Y-%m-%d %H:00') AS hr,
               AVG(CASE WHEN metric='cpu_usage' THEN value END) AS cpu,
               AVG(CASE WHEN metric='mem_used'  THEN value END) AS mu,
               AVG(CASE WHEN metric='mem_free'  THEN value END) AS mf,
               AVG(CASE WHEN metric='mem_buff'  THEN value END) AS mb,
               AVG(CASE WHEN metric='mem_cache' THEN value END) AS mc,
               AVG(CASE WHEN metric='net_in'    THEN value END) AS net_in,
               AVG(CASE WHEN metric='net_out'   THEN value END) AS net_out,
               AVG(CASE WHEN metric='load1'     THEN value END) AS `load`,
               AVG(CASE WHEN metric='proc_run'  THEN value END) AS procRun
        FROM pref_metric GROUP BY hr ORDER BY hr
    """)
    disk = {r["hr"]: r["disk"] for r in db.query(
        f"SELECT DATE_FORMAT(dt,'%Y-%m-%d %H:00') AS hr, AVG(value) AS disk "
        f"FROM disk_metric WHERE metric IN ('{DISK_UTIL_SQL}') GROUP BY hr")}

    times, cpu, mem, dsk, ni, no, load, proc = [], [], [], [], [], [], [], []
    for r in pref:
        mu, mf, mb, mc = r["mu"] or 0, r["mf"] or 0, r["mb"] or 0, r["mc"] or 0
        tot = mu + mf + mb + mc
        times.append(r["hr"])
        cpu.append(round(r["cpu"] or 0, 1))
        mem.append(round(mu / tot * 100, 1) if tot > 0 else 0)
        dsk.append(round(disk.get(r["hr"]) or 0, 1))
        ni.append(round(r["net_in"] or 0, 1))
        no.append(round(r["net_out"] or 0, 1))
        load.append(round(r["load"] or 0, 2))
        proc.append(round(r["procRun"] or 0, 1))
    return {"times": times, "cpu": cpu, "mem": mem, "disk": dsk,
            "netIn": ni, "netOut": no, "load": load, "procRun": proc}


def get_disk_top(hosts):
    top = sorted(hosts, key=lambda h: h["disk"], reverse=True)[:10]
    return [{"name": h["hostid"], "value": h["disk"]} for h in top]


def get_alerts():
    pref_max = db.query(f"""
        SELECT t.hostid, t.metric, t.value, t.dt FROM pref_metric t
        INNER JOIN (
            SELECT hostid, metric, MAX(value) mv FROM pref_metric
            WHERE metric IN ('cpu_usage','load1') GROUP BY hostid, metric
        ) m ON m.hostid=t.hostid AND m.metric=t.metric AND m.mv=t.value
    """)
    disk_max = db.query(f"""
        SELECT t.hostid, t.metric, t.value, t.dt FROM disk_metric t
        INNER JOIN (
            SELECT hostid, MAX(value) mv FROM disk_metric
            WHERE metric IN ('{DISK_UTIL_SQL}') GROUP BY hostid
        ) m ON m.hostid=t.hostid AND m.mv=t.value
    """)
    alerts = []
    for r in pref_max:
        metric, val = r["metric"], round(r["value"], 2)
        if metric == "cpu_usage" and val > 80:
            alerts.append({"host": r["hostid"], "metric": "CPU使用率", "value": round(val, 1),
                           "level": "critical" if val > 90 else "warn",
                           "time": r["dt"].strftime("%Y-%m-%d %H:%M")})
        if metric == "load1" and val > 8:
            alerts.append({"host": r["hostid"], "metric": "1分钟负载", "value": round(val, 2),
                           "level": "warn", "time": r["dt"].strftime("%Y-%m-%d %H:%M")})
    for r in disk_max:
        val = round(r["value"], 2)
        if val > 85:
            alerts.append({"host": r["hostid"], "metric": "磁盘利用率", "value": round(val, 1),
                           "level": "critical" if val > 95 else "warn",
                           "time": r["dt"].strftime("%Y-%m-%d %H:%M")})
    alerts.sort(key=lambda a: a["time"], reverse=True)
    return alerts[:30]


def get_meta():
    row = db.query("SELECT MIN(dt) AS start, MAX(dt) AS end FROM pref_metric")[0]
    hc = db.query("SELECT COUNT(*) AS c FROM `host`")[0]["c"]
    mc = db.query("SELECT COUNT(*) AS c FROM mod_dim")[0]["c"]
    return {
        "project": "StarHubClusterMonitor",
        "title": "星枢·服务器集群监控大屏",
        "generatedAt": row["end"].strftime("%Y-%m-%d %H:%M:%S") if row["end"] else "",
        "timeRange": {
            "start": row["start"].strftime("%Y-%m-%d %H:%M") if row["start"] else "",
            "end": row["end"].strftime("%Y-%m-%d %H:%M") if row["end"] else "",
        },
        "hostCount": hc, "modCount": mc,
    }


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/meta")
def meta():
    return get_meta()


@app.get("/api/overview")
def overview():
    return get_overview(get_host_status())


@app.get("/api/hosts")
def hosts():
    return get_host_status()


@app.get("/api/distribution")
def distribution():
    room, model, owner = get_distribution()
    return {"roomDist": room, "modelDist": model, "ownerDist": owner}


@app.get("/api/trend")
def trend():
    return get_trend()


@app.get("/api/disk-top")
def disk_top():
    return get_disk_top(get_host_status())


@app.get("/api/alerts")
def alerts():
    return get_alerts()


@app.get("/api/dashboard")
def dashboard():
    hosts = get_host_status()
    room, model, owner = get_distribution()
    return {
        "meta": get_meta(),
        "hosts": db.query("SELECT hostid, hostname, owner, model, location1, location2 FROM `host`"),
        "overview": get_overview(hosts),
        "hostStatus": hosts,
        "roomDist": room, "modelDist": model, "ownerDist": owner,
        "perfTrend": get_trend(),
        "diskTop": get_disk_top(hosts),
        "alerts": get_alerts(),
    }
