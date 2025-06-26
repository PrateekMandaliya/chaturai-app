FROM python:3.10-slim

WORKDIR /app/backend

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend .         
COPY cron /app/cron    
COPY backend/cronjob /etc/cron.d/daily-news-cron

# Install cron and setup job
RUN apt-get update && apt-get install -y cron && \
    chmod 0644 /etc/cron.d/daily-news-cron && \
    crontab /etc/cron.d/daily-news-cron && \
    touch /var/log/cron.log
