FROM python:3.11-slim

WORKDIR /app

# Install required system tools (cron, curl etc.)
RUN apt-get update && apt-get install -y cron && apt-get clean

# Copy backend files
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend .

# Copy the cron script and cron job definition
COPY cron /app/cron
COPY backend/cronjob /etc/cron.d/daily-news-cron

# Give permissions and register cronjob
RUN chmod +x /app/cron/update_data.sh && \
    chmod 0644 /etc/cron.d/daily-news-cron && \
    crontab /etc/cron.d/daily-news-cron

# Ensure cron logs are created
RUN touch /var/log/cron.log

# Run cron + app
CMD cron && uvicorn api:app --host 0.0.0.0 --port 8000