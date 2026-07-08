# 星枢 · 服务器集群监控大屏 (StarHubClusterMonitor)

基于 **Vue3 + Vite + DataV + ECharts** 的服务器集群监控数据大屏，数据来源于 `Project3` 中的 4 张 `.dat` 表（星型模型），视觉风格为 **星海深蓝·北斗金**。

## 一、4 张表的关联关系（星型模型）

| 表                | 类型   | 主键/外键                                          | 说明                                                                   |
| ----------------- | ------ | -------------------------------------------------- | ---------------------------------------------------------------------- |
| `host_detail.dat` | 维度表 | `hostid`(PK)                                       | 主机信息：hostname / owner / model / location1(机房) / location2(机柜) |
| `mod_detail.dat`  | 维度表 | `mod`(PK)                                          | 指标字典：type / desc / unit / tag（disk 与 pref 两类）                |
| `disk_tsar.dat`   | 事实表 | `hostid`(FK) → host_detail, `mod`(FK) → mod_detail | 磁盘 I/O 指标（ts / value）                                            |
| `pref_tsar.dat`   | 事实表 | `hostid`(FK) → host_detail, `mod`(FK) → mod_detail | 系统性能（CPU/内存/网络/负载/进程）                                    |

- 两事实表通过 **(hostid, ts)** 关联，描述同一主机、同一时刻的多维指标。
- 数据规模：20 台主机、55 项指标、约 7 天（5 分钟粒度）；`disk_tsar` 12,001 条、`pref_tsar` 67,201 条。

## 二、目录结构

```
StarHubClusterMonitor/
├── backend/
│   ├── main.py              # FastAPI 后端：8 个 REST 端点
│   ├── db.py                # MySQL 连接助手
│   ├── loader.py            # .dat → MySQL 灌入脚本
│   ├── schema.sql           # 建表 SQL
│   ├── requirements.txt     # Python 依赖
│   └── Dockerfile           # 后端镜像
├── scripts/
│   └── build_data.py        # Python 预处理：.dat → dashboard_data.json
├── src/
│   ├── data/
│   │   └── dashboard_data.json   # 预加工后的大屏数据（静态兜底）
│   ├── components/
│   │   ├── DashboardHeader.vue    # 顶部标题/时钟/元信息
│   │   ├── MetricCards.vue        # 指标卡（数字翻牌）
│   │   ├── HostMatrix.vue         # 20 节点状态热力矩阵
│   │   ├── LeftPanel.vue          # 机房/型号/负责人分布
│   │   ├── CenterTrend.vue        # 集群性能趋势
│   │   ├── RightPanel.vue         # 磁盘I/O TOP/网络/负载进程
│   │   ├── AlertTicker.vue        # 底部实时告警滚动
│   │   ├── ChartBox.vue           # DataV 边框 + 标题封装
│   │   └── BaseChart.vue          # ECharts 封装
│   ├── utils/data.js             # 数据入口（轮询 /api/dashboard）
│   ├── App.vue                   # 大屏主布局（自适应缩放）
│   ├── main.js
│   └── style.css                 # 星海深蓝·北斗金主题
├── docker-compose.yml      # 一键编排 backend + frontend
├── Dockerfile              # 前端多阶段构建（node → nginx）
├── nginx.conf              # Nginx 配置（SPA + /api 反向代理）
├── vite.config.js          # Vite 配置（开发代理）
├── package.json
└── index.html
```

## 三、运行方式

### 方式一：Docker Compose（推荐）

```bash
# 确保 MySQL 容器 mysql8 已运行（端口 3307）
docker compose up -d --build

# 访问
# 前端大屏：http://localhost
# 后端 API：http://localhost:8080/api/...
```

### 方式二：本地开发

```bash
# 1. 安装依赖
npm install --cache .npmcache

# 2. 启动后端（需先启动 MySQL 并灌入数据）
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080

# 3. 启动前端（另开终端）
npm run dev

# 4. 访问 http://localhost:5173
```

## 四、数据灌入

```bash
# 1. 连接 MySQL 建表
docker exec -i mysql8 mysql -uroot -p123456 < backend/schema.sql

# 2. 灌入 .dat 数据
cd backend
python loader.py
```

## 五、大屏模块说明

- **指标卡**：集群节点总数、在线节点、平均 CPU、平均磁盘利用率、活跃告警。
- **主机状态矩阵**：20 节点按 CPU/磁盘利用率着色（绿=正常 / 橙=预警 / 红=严重）。
- **左侧**：机房分布（玫瑰饼）、服务器型号分布（条形）、负责人分布（环形）。
- **中间**：集群性能趋势（CPU/内存/磁盘/负载按小时聚合时序）。
- **右侧**：磁盘 I/O TOP（主机排行）、网络流量（入站/出站面积图）、系统负载 & 进程数。
- **底部**：实时告警滚动列表（阈值：CPU>80%、磁盘>85%、负载>8）。

## 六、API 端点

| 端点                    | 说明                   |
| ----------------------- | ---------------------- |
| `GET /api/health`       | 健康检查               |
| `GET /api/meta`         | 项目元信息             |
| `GET /api/overview`     | 指标卡聚合             |
| `GET /api/hosts`        | 主机状态矩阵           |
| `GET /api/distribution` | 机房/型号/负责人分布   |
| `GET /api/trend`        | 集群性能趋势（按小时） |
| `GET /api/disk-top`     | 磁盘 I/O TOP10         |
| `GET /api/alerts`       | 实时告警列表           |
| `GET /api/dashboard`    | 以上全部数据一次性返回 |

## 七、技术栈

- **前端**：Vue 3 + Vite + DataV (Vue3) + ECharts 5
- **后端**：Python 3.11 + FastAPI + Uvicorn + PyMySQL
- **数据库**：MySQL 8.0（Docker 容器，端口 3307）
- **部署**：Docker Compose + Nginx（多阶段构建）

## 八、许可证

MIT
