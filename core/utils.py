import os
from dotenv import load_dotenv

def load_env():
    """
    加载 config/.env 中的环境变量，适用于所有任务。
    """
    load_dotenv(dotenv_path="config/.env")
