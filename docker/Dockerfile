# Dockerfile for notion-runner service
FROM python:3.11-slim

WORKDIR /app

COPY .. .

RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple -r requirements.txt

CMD ["python", "core/scheduler.py"]
