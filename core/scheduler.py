import os
import json
import logging
import importlib
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
from peewee import *

# Load env
load_dotenv()

# Setup logging
os.makedirs("logs", exist_ok=True)
logger = logging.getLogger("task_runner")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("logs/task.log")
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# SQLite db setup
db = SqliteDatabase('task_log.db')

class TaskLog(Model):
    task_name = CharField()
    status = CharField()
    run_time = DateTimeField()
    duration = IntegerField()
    message = TextField(null=True)
    class Meta:
        database = db

db.connect()
db.create_tables([TaskLog])

# Load task config
with open("config/tasks_config.json") as f:
    task_config = json.load(f)

# Dynamic import and registration
scheduler = BackgroundScheduler()

def wrap_task(task_name, func):
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

for task_name, meta in task_config.items():
    if meta.get("enabled", False):
        module = importlib.import_module(f"tasks.{task_name}")
        cron_expr = meta["cron"]
        trigger = CronTrigger.from_crontab(cron_expr)
        scheduler.add_job(wrap_task(task_name, module.run), trigger=trigger, id=task_name)
        logger.info(f"Task {task_name} registered with cron: {cron_expr}")
        print(f"[INFO] 任务 {task_name} 已加载，cron: {cron_expr}")

scheduler.start()
print("[INFO] 调度器启动成功，正在等待任务调度...")

# Keep the script alive
try:
    import time
    while True:
        time.sleep(5)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
