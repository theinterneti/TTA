# TTA Backup Service Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    cron \
    redis-tools \
    postgresql-client \
    awscli \
    && rm -rf /var/lib/apt/lists/*

# Install Neo4j backup tools
RUN wget -O - https://debian.neo4j.com/neotechnology.gpg.key | apt-key add - && \
    echo 'deb https://debian.neo4j.com stable 5' | tee -a /etc/apt/sources.list.d/neo4j.list && \
    apt-get update && \
    apt-get install -y neo4j-client && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /neo4j-backups /redis-backups /app/logs

# Set permissions
RUN chmod +x /app/scripts/*.sh

# Create cron job for scheduled backups
RUN echo "0 2 * * * /app/scripts/backup.sh >> /app/logs/backup.log 2>&1" | crontab -

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python /app/health_check.py

# Expose metrics port
EXPOSE 8080

# Start the backup service
CMD ["python", "/app/backup_service.py"]
