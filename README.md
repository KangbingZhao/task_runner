# Notion Task Runner

一个可在内网服务器运行的、模块化的个人自动任务平台。支持定时执行任务（如生成 Notion 日记、同步数据等），具备任务管理、状态记录、失败容错和可扩展性。

## 目录结构

```
notion-task-runner/
├── config/                # 配置文件目录
│   ├── .env
│   └── tasks_config.json
├── core/                  # 核心代码（调度、日志、数据库等）
│   └── scheduler.py
├── tasks/                 # 任务模块，每个任务一个文件
│   └── daily_journal.py
├── logs/                  # 日志目录
├── requirements.txt       # Python 依赖
├── Makefile               # 一键构建/运行脚本
├── Dockerfile             # Docker 镜像构建文件
└── README.md
```

## 快速开始

> **注意：首次使用前请先安装 uv 工具（推荐用 pipx 安装）：**
> ```bash
> pipx install uv
> ```
> 或参考 [uv 官方文档](https://github.com/astral-sh/uv)。

### 1. 安装依赖（推荐使用 [uv](https://github.com/astral-sh/uv) 工具）

```bash
make build
```
- 自动创建 `.venv` 虚拟环境并用 uv 安装依赖，不污染全局 Python。

### 2. 运行调度器

```bash
make run
```
- 激活虚拟环境并启动任务调度主程序。

### 3. 清理虚拟环境

```bash
make clean
```

### 4. Docker 部署

构建镜像（推荐使用阿里云加速器）：
```bash
docker build --network=host -t notion-runner-image .
```
> 如需全局加速，可在 ~/.docker/config.json 配置阿里云镜像加速器，详见[官方文档](https://cr.console.aliyun.com/cn-hangzhou/instance/mirrors)。

运行容器（可选挂载外部 db 文件）：
```bash
docker run -d \
  --name notion-runner \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/config/.env:/app/config/.env \
  -v $(pwd)/config/tasks_config.json:/app/config/tasks_config.json \
  # 如需持久化数据库，可挂载本地 db 文件（可选）
  -v $(pwd)/task_log.db:/app/task_log.db \
  notion-runner-image
```
> 如果未挂载 db 文件，容器会自动创建空数据库并打印提示日志；如挂载则会检测并提示已加载外部 db。

### 5. 运行测试

```bash
make test
```
- 激活虚拟环境并运行 tests 目录下所有自动化测试。

### 6. 构建 Docker 镜像

```bash
make docker-build
```
- 一键构建 notion-runner-image 镜像。

## 主要功能
- 任务模块化，统一接口，易于扩展
- 支持 cron 表达式定时调度
- 日志自动切割，保留最近 7 天
- 任务执行状态持久化（SQLite）
- 配置与代码分离，便于维护

## 依赖
- Python 3.8+
- uv（推荐，极快的包管理工具）
- APScheduler
- peewee
- python-dotenv
- requests

## 配置说明
- `config/.env`：存放 Notion Token、数据库 ID 等敏感信息
- `config/tasks_config.json`：任务启用、调度计划、描述等元信息

## 任务开发
- 在 `tasks/` 目录下新建 Python 文件，实现 `run()` 方法即可
- 任务需保证幂等性

---
如有问题请查阅 `doc/prd.md` 或联系项目维护者。
