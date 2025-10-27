# TTA Player Experience API Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install UV package manager with pinned version for reproducibility
RUN pip install --no-cache-dir uv==0.4.18

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync --frozen --no-dev --no-install-project || \
    uv pip install fastapi uvicorn redis neo4j psycopg2-binary pydantic python-jose[cryptography] passlib[bcrypt] python-multipart

# Copy application code
COPY . /app/src/player_experience/api/
COPY ../../ /app/src/

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create necessary directories
RUN mkdir -p logs && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Set Python path
ENV PYTHONPATH=/app

# Run the application
CMD ["python", "-m", "uvicorn", "src.player_experience.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
