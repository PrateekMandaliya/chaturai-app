FROM python:3.11-slim

WORKDIR /app

# Install system packages
RUN apt-get update && apt-get install -y cron && apt-get clean

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code and cron job
COPY . /app/
COPY cron/update_data.sh /app/cron/update_data.sh
COPY cronjob /etc/cron.d/daily-news-cron

# Set permissions and register the cron job
RUN chmod +x /app/cron/update_data.sh && \
    chmod 0644 /etc/cron.d/daily-news-cron && \
    crontab /etc/cron.d/daily-news-cron && \
    touch /var/log/cron.log

RUN mkdir -p /app/model_cache

# Start cron and the FastAPI app
CMD cron && uvicorn api:app --host 0.0.0.0 --port 8000
