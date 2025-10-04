FROM python:3.11-slim

WORKDIR /app

# Install required packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy health check service
COPY health_check_service.py .
COPY config.yaml .

# Create non-root user for security
RUN useradd -m -u 1000 healthcheck && \
    chown -R healthcheck:healthcheck /app

# Switch to non-root user
USER healthcheck

# Expose metrics port
EXPOSE 8080

# Run the health check service
CMD ["python", "health_check_service.py"]
