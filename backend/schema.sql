-- StarHubClusterMonitor 数据库结构
-- 对应 Project3 的 4 张原始表：host_detail / mod_detail / disk_tsar / pref_tsar
-- 说明：MySQL 保留字 mod / desc 在内部列名中改为 metric / mod_desc，对外 JSON 仍用 mod / desc

CREATE DATABASE IF NOT EXISTS starhub
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE starhub;

-- 维度表：主机
CREATE TABLE IF NOT EXISTS host (
  hostid    VARCHAR(32)  PRIMARY KEY,
  hostname  VARCHAR(64),
  owner     VARCHAR(32),
  model     VARCHAR(32),
  location1 VARCHAR(32),
  location2 VARCHAR(32)
);

-- 维度表：指标字典
CREATE TABLE IF NOT EXISTS mod_dim (
  metric    VARCHAR(32)  PRIMARY KEY,   -- 原始文件中的 mod
  type      VARCHAR(16),
  mod_desc  VARCHAR(64),                -- 原始文件中的 desc
  unit      VARCHAR(16),
  tag       VARCHAR(32)
);

-- 事实表：磁盘 I/O 指标
CREATE TABLE IF NOT EXISTS disk_metric (
  id      BIGINT AUTO_INCREMENT PRIMARY KEY,
  ts      BIGINT NOT NULL,
  hostid  VARCHAR(32),
  type    VARCHAR(16),
  metric  VARCHAR(32),
  value   DOUBLE,
  tag     VARCHAR(32),
  dt      DATETIME,
  INDEX idx_host_dt (hostid, dt),
  INDEX idx_metric_dt (metric, dt)
);

-- 事实表：系统性能综合指标
CREATE TABLE IF NOT EXISTS pref_metric (
  id      BIGINT AUTO_INCREMENT PRIMARY KEY,
  ts      BIGINT NOT NULL,
  hostid  VARCHAR(32),
  type    VARCHAR(16),
  metric  VARCHAR(32),
  value   DOUBLE,
  tag     VARCHAR(32),
  dt      DATETIME,
  INDEX idx_host_dt (hostid, dt),
  INDEX idx_metric_dt (metric, dt)
);
