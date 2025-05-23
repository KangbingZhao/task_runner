FROM python:3.11-slim

WORKDIR /app

COPY . .

# 使用阿里云 PyPI 镜像加速安装依赖
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple -r requirements.txt

CMD ["python", "core/scheduler.py"]
