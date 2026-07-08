# -*- coding: utf-8 -*-
"""
StarHubClusterMonitor 数据预处理脚本
读取 Project3 中的 4 张表(.dat)，聚合并输出前端大屏所需的 dashboard_data.json
表关系(星型模型):
  维度表: host_detail(hostid), mod_detail(mod)
  事实表: disk_tsar(hostid,mod,ts,value), pref_tsar(hostid,mod,ts,value)
"""
import os
import json
import math
import pandas as pd

BASE = r"e:/code/Project3"
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "data")
OUT_PATH = os.path.join(OUT_DIR, "dashboard_data.json")

DISK_UTIL_MODS = ["sda_util", "sdb_util", "sdc_util", "sdd_util", "sde_util"]


def load_tsv(name):
    return pd.read_csv(os.path.join(BASE, name), sep="\t")


def main():
    host_df = load_tsv("host_detail.dat")
    mod_df = load_tsv("mod_detail.dat")
    disk_df = load_tsv("disk_tsar.dat")
    pref_df = load_tsv("pref_tsar.dat")

    # 时间解析
    for df in (disk_df, pref_df):
        df["dt"] = pd.to_datetime(df["ts"], unit="ms")
        df["hour"] = df["dt"].dt.floor("h")

    hosts = []
    for _, r in host_df.iterrows():
        hosts.append({
            "hostid": r["hostid"],
            "hostname": r["hostname"],
            "owner": r["owner"],
            "model": r["model"],
            "location1": r["location1"],
            "location2": r["location2"],
        })

    # ---------- 概览指标卡 ----------
    cpu_all = pref_df.loc[pref_df["mod"] == "cpu_usage", "value"]
    mem_used = pref_df.loc[pref_df["mod"] == "mem_used", "value"]
    mem_free = pref_df.loc[pref_df["mod"] == "mem_free", "value"]
    mem_buff = pref_df.loc[pref_df["mod"] == "mem_buff", "value"]
    mem_cache = pref_df.loc[pref_df["mod"] == "mem_cache", "value"]
    mem_total = mem_used + mem_free + mem_buff + mem_cache
    mem_pct = (mem_used / mem_total * 100).mean()
    du = disk_df[disk_df["mod"].isin(DISK_UTIL_MODS)]["value"]
    load_all = pref_df.loc[pref_df["mod"] == "load1", "value"]

    # 逐主机平均指标用于状态判定
    host_status = []
    alert_count = 0
    for hid in host_df["hostid"]:
        hpref = pref_df[pref_df["hostid"] == hid]
        hdisk = disk_df[disk_df["hostid"] == hid]
        cpu = hpref.loc[hpref["mod"] == "cpu_usage", "value"].mean()
        mu = hpref.loc[hpref["mod"] == "mem_used", "value"]
        mf = hpref.loc[hpref["mod"] == "mem_free", "value"]
        mb = hpref.loc[hpref["mod"] == "mem_buff", "value"]
        mc = hpref.loc[hpref["mod"] == "mem_cache", "value"]
        mt = (mu + mf + mb + mc)
        mem = (mu / mt * 100).mean() if len(mt) and mt.mean() > 0 else 0
        disk = hdisk[hdisk["mod"].isin(DISK_UTIL_MODS)]["value"].mean()
        net_in = hpref.loc[hpref["mod"] == "net_in", "value"].mean()
        load = hpref.loc[hpref["mod"] == "load1", "value"].mean()
        level = "ok"
        if cpu > 80 or disk > 85 or mem > 85:
            level = "warn"
        if cpu > 90 or disk > 95:
            level = "critical"
        if level != "ok":
            alert_count += 1
        host_status.append({
            "hostid": hid,
            "hostname": host_df.loc[host_df["hostid"] == hid, "hostname"].iloc[0],
            "location1": host_df.loc[host_df["hostid"] == hid, "location1"].iloc[0],
            "model": host_df.loc[host_df["hostid"] == hid, "model"].iloc[0],
            "cpu": round(float(cpu), 1),
            "mem": round(float(mem), 1),
            "disk": round(float(disk), 1),
            "netIn": round(float(net_in), 1),
            "load": round(float(load), 2),
            "status": level,
        })

    overview = {
        "totalHosts": int(len(host_df)),
        "onlineHosts": int(len(host_df)),
        "avgCpu": round(float(cpu_all.mean()), 1),
        "avgMem": round(float(mem_pct), 1),
        "avgDisk": round(float(du.mean()), 1),
        "avgLoad": round(float(load_all.mean()), 2),
        "alertCount": int(alert_count),
    }

    # ---------- 分布类 ----------
    room_dist = host_df["location1"].value_counts().sort_index()
    model_dist = host_df["model"].value_counts().sort_values(ascending=False)
    owner_dist = host_df["owner"].value_counts().sort_values(ascending=False)

    # ---------- 时序趋势(按小时聚合集群均值) ----------
    def hourly_avg(df, mods):
        sub = df[df["mod"].isin(mods)]
        return sub.groupby("hour")["value"].mean()

    cpu_h = hourly_avg(pref_df, ["cpu_usage"])
    net_in_h = hourly_avg(pref_df, ["net_in"])
    net_out_h = hourly_avg(pref_df, ["net_out"])
    load_h = hourly_avg(pref_df, ["load1"])
    proc_h = hourly_avg(pref_df, ["proc_run"])
    disk_h = hourly_avg(disk_df, DISK_UTIL_MODS)

    # 内存使用率按小时(逐小时计算 used/(used+free+buff+cache))
    mem_rate = {}
    for hr, grp in pref_df.groupby("hour"):
        mu = grp.loc[grp["mod"] == "mem_used", "value"].mean()
        mf = grp.loc[grp["mod"] == "mem_free", "value"].mean()
        mb = grp.loc[grp["mod"] == "mem_buff", "value"].mean()
        mc = grp.loc[grp["mod"] == "mem_cache", "value"].mean()
        tot = mu + mf + mb + mc
        mem_rate[hr] = (mu / tot * 100) if tot > 0 else 0

    # 统一时间轴(取 cpu 序列的小时索引)
    times = sorted(cpu_h.index)
    time_labels = [t.strftime("%m-%d %H:00") for t in times]
    perf_trend = {
        "times": time_labels,
        "cpu": [round(float(cpu_h.get(t, 0)), 1) for t in times],
        "mem": [round(float(mem_rate.get(t, 0)), 1) for t in times],
        "disk": [round(float(disk_h.get(t, 0)), 1) for t in times],
        "netIn": [round(float(net_in_h.get(t, 0)), 1) for t in times],
        "netOut": [round(float(net_out_h.get(t, 0)), 1) for t in times],
        "load": [round(float(load_h.get(t, 0)), 2) for t in times],
        "procRun": [round(float(proc_h.get(t, 0)), 1) for t in times],
    }

    # ---------- 磁盘I/O TOP(主机排行, 按平均磁盘利用率) ----------
    disk_top = sorted(host_status, key=lambda x: x["disk"], reverse=True)[:10]
    disk_top = [{"name": h["hostid"], "value": h["disk"]} for h in disk_top]

    # ---------- 告警列表(阈值扫描) ----------
    alerts = []
    for hid in host_df["hostid"]:
        hpref = pref_df[pref_df["hostid"] == hid]
        hdisk = disk_df[disk_df["hostid"] == hid]
        last_cpu = hpref.loc[hpref["mod"] == "cpu_usage", "value"].max()
        last_disk = hdisk[hdisk["mod"].isin(DISK_UTIL_MODS)]["value"].max()
        last_load = hpref.loc[hpref["mod"] == "load1", "value"].max()
        if last_cpu > 80:
            alerts.append({"host": hid, "metric": "CPU使用率", "value": round(float(last_cpu), 1),
                           "level": "critical" if last_cpu > 90 else "warn",
                           "time": hpref.loc[hpref["mod"] == "cpu_usage", "dt"].max().strftime("%Y-%m-%d %H:%M")})
        if last_disk > 85:
            alerts.append({"host": hid, "metric": "磁盘利用率", "value": round(float(last_disk), 1),
                           "level": "critical" if last_disk > 95 else "warn",
                           "time": hdisk.loc[hdisk["mod"].isin(DISK_UTIL_MODS), "dt"].max().strftime("%Y-%m-%d %H:%M")})
        if last_load > 8:
            alerts.append({"host": hid, "metric": "1分钟负载", "value": round(float(last_load), 2),
                           "level": "warn", "time": hpref.loc[hpref["mod"] == "load1", "dt"].max().strftime("%Y-%m-%d %H:%M")})
    alerts.sort(key=lambda a: a["time"], reverse=True)
    alerts = alerts[:30]

    result = {
        "meta": {
            "project": "StarHubClusterMonitor",
            "title": "星枢·服务器集群监控大屏",
            "generatedAt": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "timeRange": {
                "start": pref_df["dt"].min().strftime("%Y-%m-%d %H:%M"),
                "end": pref_df["dt"].max().strftime("%Y-%m-%d %H:%M"),
            },
            "hostCount": int(len(host_df)),
            "modCount": int(len(mod_df)),
        },
        "hosts": hosts,
        "overview": overview,
        "hostStatus": host_status,
        "roomDist": [{"name": str(k), "value": int(v)} for k, v in room_dist.items()],
        "modelDist": [{"name": str(k), "value": int(v)} for k, v in model_dist.items()],
        "ownerDist": [{"name": str(k), "value": int(v)} for k, v in owner_dist.items()],
        "perfTrend": perf_trend,
        "diskTop": disk_top,
        "alerts": alerts,
    }

    # 清洗 NaN / Infinity 为非标准 JSON（Python json 默认会写出 NaN，浏览器/打包器无法解析）
    def sanitize(o):
        if isinstance(o, dict):
            return {k: sanitize(v) for k, v in o.items()}
        if isinstance(o, list):
            return [sanitize(v) for v in o]
        if isinstance(o, float) and (math.isnan(o) or math.isinf(o)):
            return None
        return o
    result = sanitize(result)

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, allow_nan=False)
    print("Wrote", os.path.abspath(OUT_PATH))
    print("hosts:", len(hosts), "alerts:", len(alerts), "timePoints:", len(time_labels))


if __name__ == "__main__":
    main()
