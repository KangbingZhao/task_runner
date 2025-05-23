import os
import json
import logging
import importlib
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
from peewee import *
import pathlib
from logging.handlers import RotatingFileHandler
from jsonschema import validate, ValidationError

def setup_logging():
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger("task_runner")
    logger.setLevel(logging.INFO)
    
    # 配置文件处理器
    file_handler = RotatingFileHandler("logs/task.log", maxBytes=10 * 1024 * 1024, backupCount=7)
    # 配置终端处理器
    console_handler = logging.StreamHandler()
    
    # 设置日志格式
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加两个处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# SQLite db setup
db_path = os.getenv('DB_PATH', 'task_log.db')
# Ensure the database directory exists
if not os.path.dirname(db_path):
    db_path = os.path.join(os.getcwd(), db_path)
os.makedirs(os.path.dirname(db_path), exist_ok=True)
db = SqliteDatabase(db_path)

class TaskLog(Model):
    task_name = CharField()
    status = CharField()
    run_time = DateTimeField()
    duration = IntegerField()
    message = TextField(null=True)
    class Meta:
        database = db

def wrap_task(task_name, func, logger):
    def job():
        start_time = datetime.datetime.now()
        try:
            func()
            duration = (datetime.datetime.now() - start_time).seconds
            logger.info(f"{task_name} completed in {duration}s")
        except Exception as e:
            duration = (datetime.datetime.now() - start_time).seconds
            logger.error(f"{task_name} failed in {duration}s with error: {e}")
            logger.exception(e)
    return job

def register_tasks(scheduler, logger, task_config):
    for task_name, meta in task_config.items():
        if meta.get("enabled", False):
            module = importlib.import_module(f"tasks.{task_name}")
            if not hasattr(module, "run"):
                logger.error(f"任务 {task_name} 缺少 run() 方法，跳过注册")
                print(f"[ERROR] 任务 {task_name} 缺少 run() 方法，跳过注册")
                continue
            cron_expr = meta["cron"]
            cron_fields = cron_expr.strip().split()
            if len(cron_fields) == 6:
                trigger = CronTrigger(second=cron_fields[0], minute=cron_fields[1], hour=cron_fields[2],
                                      day=cron_fields[3], month=cron_fields[4], day_of_week=cron_fields[5])
            elif len(cron_fields) == 5:
                trigger = CronTrigger.from_crontab(cron_expr)
            else:
                raise ValueError(f"Invalid cron expression for task {task_name}: {cron_expr}")
            scheduler.add_job(wrap_task(task_name, module.run, logger), trigger=trigger, id=task_name)
            logger.info(f"Task {task_name} registered with cron: {cron_expr}")
            print(f"[INFO] 任务 {task_name} 已加载，cron: {cron_expr}")

def get_version():
    version_file = pathlib.Path(__file__).parent.parent / "VERSION"
    if version_file.exists():
        return version_file.read_text().strip()
    return "unknown"

def main():
    load_dotenv()
    logger = setup_logging()
    version = get_version()
    print(f"[INFO] Notion Task Runner 版本: {version}")
    logger.info(f"Notion Task Runner 版本: {version}")
    db_path = os.getenv('DB_PATH', 'task_log.db')
    logger.info(f"使用数据库：{db_path}")
    print(f"[INFO] 使用数据库：{db_path}")
    db.connect()
    db.create_tables([TaskLog], safe=True)
    with open("config/tasks_config.json") as f:
        task_config = json.load(f)

    task_schema = {
        "type": "object",
        "patternProperties": {
            "^[a-zA-Z_][a-zA-Z0-9_]*$": {
                "type": "object",
                "required": ["enabled", "cron", "description"],
                "properties": {
                    "enabled": {"type": "boolean"},
                    "cron": {"type": "string"},
                    "description": {"type": "string"}
                }
            }
        }
    }

    try:
        validate(instance=task_config, schema=task_schema)
        logger.info("任务配置校验通过")
    except ValidationError as ve:
        logger.error(f"任务配置校验失败: {ve}")
        raise ve

    scheduler = BackgroundScheduler()
    register_tasks(scheduler, logger, task_config)
    scheduler.start()
    print("[INFO] 调度器启动成功，正在等待任务调度...")
    try:
        import time
        while True:
            time.sleep(5)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

if __name__ == "__main__":
    main()
