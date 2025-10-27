# Use Hugging Face's Transformers image as base
FROM huggingface/transformers-pytorch-gpu:latest

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    VIRTUAL_ENV=/app/.venv \
    PATH=/app/.venv/bin:$PATH \
    PYTHONPATH=/app

# Install additional system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    python3-venv \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \
    $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update \
    && apt-get install -y docker-ce-cli \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create and activate virtual environment
RUN python3 -m venv /app/.venv

# Install Python dependencies
COPY requirements.txt .
RUN /app/.venv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel && \
    /app/.venv/bin/pip install --no-cache-dir -r requirements.txt

# Install development tools
RUN /app/.venv/bin/pip install --no-cache-dir \
    black \
    isort \
    mypy \
    pytest \
    pytest-asyncio

# Verify CUDA availability
RUN python3 -c "import torch; print('CUDA available:', torch.cuda.is_available())"
