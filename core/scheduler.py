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

def setup_logging():
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger("task_runner")
    logger.setLevel(logging.INFO)
    
    # 配置文件处理器
    file_handler = logging.FileHandler("logs/task.log")
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
            TaskLog.create(task_name=task_name, status="success", run_time=start_time, duration=duration)
            logger.info(f"{task_name} success")
        except Exception as e:
            duration = (datetime.datetime.now() - start_time).seconds
            TaskLog.create(task_name=task_name, status="failed", run_time=start_time, duration=duration, message=str(e))
            logger.exception(f"{task_name} failed")
    return job

def register_tasks(scheduler, logger, task_config):
    for task_name, meta in task_config.items():
        if meta.get("enabled", False):
            module = importlib.import_module(f"tasks.{task_name}")
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
