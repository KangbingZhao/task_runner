# Dockerfile for notion-runner service
FROM python:3.11-slim

WORKDIR /app

COPY .. .

RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple -r requirements.txt

# Set timezone to UTC+8
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

CMD ["python", "core/scheduler.py"]
