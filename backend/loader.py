# -*- coding: utf-8 -*-
"""
将 Project3 的 4 张原始 .dat 表灌入 MySQL(starhub)。
对应表：
  host_detail.dat   -> host
  mod_detail.dat    -> mod_dim   (文件列 mod->列 metric, desc->列 mod_desc)
  disk_tsar.dat     -> disk_metric
  pref_tsar.dat     -> pref_metric  (ts 毫秒 -> dt DATETIME，即"时间戳解析")
支持环境变量(便于 Docker)：MYSQL_HOST/MYSQL_PORT/MYSQL_USER/MYSQL_PASSWORD/MYSQL_DB/DATADIR
"""
import os
import glob
import pymysql

MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3307"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "123456")
MYSQL_DB = os.getenv("MYSQL_DB", "starhub")
DATADIR = os.getenv("DATADIR", r"e:/code/Project3")


def conn():
    return pymysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER,
                           password=MYSQL_PASSWORD, database=MYSQL_DB,
                           charset="utf8mb4", autocommit=False)


def read_tsv(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("\t")
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            rows.append(line.split("\t"))
    return header, rows


def load_host(cur):
    header, rows = read_tsv(os.path.join(DATADIR, "host_detail.dat"))
    data = [(r[0], r[1], r[2], r[3], r[4], r[5]) for r in rows]
    cur.executemany(
        "INSERT IGNORE INTO host (hostid,hostname,owner,model,location1,location2) VALUES (%s,%s,%s,%s,%s,%s)",
        data)
    return len(data)


def load_mod(cur):
    header, rows = read_tsv(os.path.join(DATADIR, "mod_detail.dat"))
    data = [(r[0], r[1], r[2], r[3], r[4]) for r in rows]  # mod,type,desc,unit,tag
    cur.executemany(
        "INSERT IGNORE INTO mod_dim (metric,type,mod_desc,unit,tag) VALUES (%s,%s,%s,%s,%s)",
        data)
    return len(data)


def load_metric(cur, filename, table):
    header, rows = read_tsv(os.path.join(DATADIR, filename))
    # 文件列: ts, hostid, type, mod, value, tag
    # 目标列: ts, hostid, type, metric, value, tag, dt
    # dt 由 FROM_UNIXTIME(ts/1000) 计算（毫秒时间戳 -> DATETIME）
    sql = ("INSERT INTO " + table +
           " (ts,hostid,type,metric,value,tag,dt) "
           "VALUES (%s,%s,%s,%s,%s,%s,FROM_UNIXTIME(%s/1000))")
    data = [(int(r[0]), r[1], r[2], r[3], float(r[4]), r[5], int(r[0])) for r in rows]
    cur.executemany(sql, data)
    return len(data)


def main():
    c = conn()
    try:
        with c.cursor() as cur:
            n_host = load_host(cur)
            n_mod = load_mod(cur)
            n_disk = load_metric(cur, "disk_tsar.dat", "disk_metric")
            n_pref = load_metric(cur, "pref_tsar.dat", "pref_metric")
            c.commit()
            print(f"载入完成 -> host:{n_host}  mod_dim:{n_mod}  disk_metric:{n_disk}  pref_metric:{n_pref}")
    finally:
        c.close()


if __name__ == "__main__":
    main()
