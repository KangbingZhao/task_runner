## 一、项目目标

构建一个可在内网服务器运行的、模块化的个人自动任务平台，用于定时执行个人任务（如生成 Notion 日记、同步数据等），具备任务管理、状态记录、失败容错和可扩展性。

---

## 二、系统组成

### 1. 配置系统（.env + JSON）

- `.env` 文件：存储全局密钥、路径、调度参数等敏感配置
    - 例：NOTION_TOKEN、NOTION_DATABASE_ID
- `tasks_config.json`：存储所有任务的元信息
    - 是否启用
    - **调度计划（使用 cron 表达式）**
    - 任务备注说明

### 示例：tasks_config.json

```json
{
  "daily_journal": {
    "enabled": true,
    "cron": "0 0 * * *",
    "description": "每日创建 Notion 日记"
  },
  "weekly_review": {
    "enabled": false,
    "cron": "0 8 * * 1",
    "description": "每周一生成周报模板"
  }
}

```

---

## 三、任务模块系统

### 1. 模块结构

- 所有任务均实现统一接口：`run()` 方法
- 模块按文件独立存放于 `tasks/` 目录中
- 系统主程序通过注册表统一调度执行

### 2. 幂等执行

- 每个任务需保证自身幂等性：即重复运行不会产生副作用或重复数据

---

## 四、调度器设计（scheduler.py）

### 调度框架：

- 使用 Python [APScheduler](https://apscheduler.readthedocs.io/) 实现调度逻辑
- 支持 cron 表达式调度
- 所有任务在 APScheduler 的线程池中异步运行，不阻塞主进程

### 调度流程：

1. 读取 `.env` 环境变量和 `tasks_config.json` 任务配置
2. 注册所有启用任务，设定对应 cron 调度计划
3. 定期由 APScheduler 自动触发运行任务
4. 执行完成后记录状态（成功/失败/耗时）到日志与数据库

### APScheduler 特性：

- 后台调度器（可作为守护线程常驻）
- 内建线程池，支持并发
- 支持暂停/恢复任务

---

## 五、任务执行记录（SQLite）

### 数据库存储：`task_log.db`

- 表：`task_logs`
    - `id`: 主键
    - `task_name`: 任务名
    - `status`: success / failed
    - `run_time`: 执行时间（datetime）
    - `duration`: 执行耗时（秒）
    - `message`: 日志信息 / 错误描述（JSON 格式）

---

## 六、日志系统（本地日志文件）

### 记录方式：

- 使用 Python `logging` 模块记录至 `logs/task.log`
- 自动按天切割，保留最近 7 天
- 日志内容包括：启动时间、任务名、状态、异常信息、耗时

---

## 七、部署与运行

### 推荐部署方式：

- 项目整体打包为 **Docker 镜像**，便于部署和迁移
- 将 `.env` 文件、`tasks_config.json`、日志目录和 SQLite 数据库通过 volume 挂载至容器
- Docker 启动命令即为 `python scheduler.py`

### 示例目录结构：

```bash
notion-task-runner/
├── Dockerfile
├── scheduler.py
├── tasks/
├── logs/               # 挂载宿主机
├── .env                # 挂载宿主机
├── tasks_config.json   # 挂载宿主机
├── task_log.db         # 持久化数据库

```

### 示例启动命令：

```bash
docker run -d \
  --name notion-runner \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/tasks_config.json:/app/tasks_config.json \
  -v $(pwd)/task_log.db:/app/task_log.db \
  notion-runner-image

```

---

## 八、未来可扩展功能

### Web 控制台（Flask + SQLite）

- 展示所有任务执行状态
- 提供启用/禁用开关操作
- 展示历史日志、错误信息、执行统计

### 通知系统（可选）

- 失败任务通过邮件 / 推送通知提醒
- 配置失败重试次数

### 高级调度（可选）

- 多主机支持任务分发
- 支持并发运行任务（使用线程池）

---

## 九、安全与容错

- 所有敏感信息存储于 `.env`，不入库
- 任务失败自动记录但不阻塞其他任务
- 调度器具备时间判断逻辑，防止重复执行

---

## 十、适用场景

- Notion 相关日记、周报自动化
- 本地备份、自定义日志收集、时间追踪
- 微信读书、豆瓣等定期数据抓取同步
- 自用番茄钟统计日报生成