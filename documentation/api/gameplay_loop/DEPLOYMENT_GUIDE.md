# Deployment Guide - Complete Gameplay Loop

## Overview

This guide provides step-by-step instructions for deploying the complete gameplay loop implementation in various environments, from development to production.

## Prerequisites

### System Requirements

**Minimum Requirements**:
- CPU: 2 cores, 2.4 GHz
- RAM: 4 GB
- Storage: 20 GB available space
- Network: Stable internet connection

**Recommended Requirements**:
- CPU: 4+ cores, 3.0+ GHz
- RAM: 8+ GB
- Storage: 50+ GB SSD
- Network: High-speed internet with low latency

### Software Dependencies

**Core Dependencies**:
- Python 3.9+
- Redis 6.0+
- Neo4j 4.4+
- Node.js 16+ (for frontend integration)

**Python Packages**:
```bash
fastapi>=0.104.0
uvicorn>=0.24.0
websockets>=11.0
redis>=5.0.0
neo4j>=5.13.0
pydantic>=2.4.0
asyncio-mqtt>=0.13.0
pytest>=7.4.0
```

## Development Environment Setup

### 1. Repository Setup

```bash
# Clone the repository
git clone https://github.com/your-org/TTA.git
cd TTA

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

**Redis Setup**:
```bash
# Install Redis (Ubuntu/Debian)
sudo apt update
sudo apt install redis-server

# Start Redis service
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify Redis is running
redis-cli ping  # Should return "PONG"
```

**Neo4j Setup**:
```bash
# Install Neo4j (Ubuntu/Debian)
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.com stable 4.4' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt update
sudo apt install neo4j

# Start Neo4j service
sudo systemctl start neo4j
sudo systemctl enable neo4j

# Access Neo4j browser at http://localhost:7474
# Default credentials: neo4j/neo4j (change on first login)
```

### 3. Configuration

**Environment Variables**:
```bash
# Create .env file
cat > .env << EOF
# Database Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Application Configuration
DEBUG=true
LOG_LEVEL=DEBUG
SECRET_KEY=your_secret_key_here

# Gameplay Configuration
MAX_CONCURRENT_INSTANCES_PER_PLAYER=5
MAX_BRANCHES_PER_PLAYER=10
WEBSOCKET_HEARTBEAT_INTERVAL=30

# Safety Configuration
THERAPEUTIC_SAFETY_ENABLED=true
CRISIS_DETECTION_SENSITIVITY=0.8
AUTO_INTERVENTION_ENABLED=true

# Agent Orchestration
AGENT_ORCHESTRATION_ENABLED=true
AGENT_ORCHESTRATION_TIMEOUT=30
EOF
```

**Service Configuration**:
```bash
# Copy configuration template
cp config/gameplay_loop.yaml.template config/gameplay_loop.yaml

# Edit configuration as needed
nano config/gameplay_loop.yaml
```

### 4. Database Initialization

```bash
# Run database setup script
python scripts/setup_database.py

# Load initial data
python scripts/load_therapeutic_worlds.py
python scripts/setup_agent_proxies.py
```

### 5. Development Server

```bash
# Start development server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Or use the development script
./scripts/dev_server.sh
```

**Verify Installation**:
```bash
# Check health endpoint
curl http://localhost:8000/health

# Check detailed health
curl http://localhost:8000/health/detailed

# Test WebSocket connection (using wscat)
npm install -g wscat
wscat -c ws://localhost:8000/ws/gameplay/test_player/test_session
```

## Production Deployment

### Option 1: Docker Deployment

**1. Create Dockerfile**:
```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**2. Create docker-compose.yml**:
```yaml
version: '3.8'

services:
  tta-gameplay:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=redis
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=production_password
    depends_on:
      - redis
      - neo4j
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - tta-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped
    networks:
      - tta-network

  neo4j:
    image: neo4j:5.13
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/production_password
      - NEO4J_PLUGINS=["apoc"]
      - NEO4J_dbms_security_procedures_unrestricted=apoc.*
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
    restart: unless-stopped
    networks:
      - tta-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - tta-gameplay
    restart: unless-stopped
    networks:
      - tta-network

volumes:
  redis_data:
  neo4j_data:
  neo4j_logs:

networks:
  tta-network:
    driver: bridge
```

**3. Deploy with Docker Compose**:
```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f tta-gameplay

# Scale the application
docker-compose up -d --scale tta-gameplay=3
```

### Option 2: Kubernetes Deployment

**1. Create Kubernetes manifests**:

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: tta-gameplay
---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: tta-config
  namespace: tta-gameplay
data:
  REDIS_HOST: "redis-service"
  NEO4J_URI: "bolt://neo4j-service:7687"
  THERAPEUTIC_SAFETY_ENABLED: "true"
---
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: tta-secrets
  namespace: tta-gameplay
type: Opaque
data:
  NEO4J_PASSWORD: <base64-encoded-password>
  SECRET_KEY: <base64-encoded-secret>
---
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tta-gameplay
  namespace: tta-gameplay
spec:
  replicas: 3
  selector:
    matchLabels:
      app: tta-gameplay
  template:
    metadata:
      labels:
        app: tta-gameplay
    spec:
      containers:
      - name: tta-gameplay
        image: tta-gameplay:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: tta-config
        - secretRef:
            name: tta-secrets
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: tta-gameplay-service
  namespace: tta-gameplay
spec:
  selector:
    app: tta-gameplay
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
---
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: tta-gameplay-ingress
  namespace: tta-gameplay
  annotations:
    nginx.ingress.kubernetes.io/websocket-services: "tta-gameplay-service"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "3600"
spec:
  rules:
  - host: tta-gameplay.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: tta-gameplay-service
            port:
              number: 80
```

**2. Deploy to Kubernetes**:
```bash
# Apply manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n tta-gameplay
kubectl get services -n tta-gameplay

# View logs
kubectl logs -f deployment/tta-gameplay -n tta-gameplay

# Scale deployment
kubectl scale deployment tta-gameplay --replicas=5 -n tta-gameplay
```

### Option 3: Cloud Platform Deployment

**AWS ECS Deployment**:
```json
{
  "family": "tta-gameplay",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "tta-gameplay",
      "image": "your-account.dkr.ecr.region.amazonaws.com/tta-gameplay:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "REDIS_HOST",
          "value": "your-redis-cluster.cache.amazonaws.com"
        }
      ],
      "secrets": [
        {
          "name": "NEO4J_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:neo4j-password"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/tta-gameplay",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

## Load Balancer Configuration

### Nginx Configuration

```nginx
# nginx.conf
upstream tta_gameplay {
    server tta-gameplay-1:8000;
    server tta-gameplay-2:8000;
    server tta-gameplay-3:8000;
}

server {
    listen 80;
    server_name tta-gameplay.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tta-gameplay.yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # WebSocket support
    location /ws/ {
        proxy_pass http://tta_gameplay;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # API endpoints
    location /api/ {
        proxy_pass http://tta_gameplay;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health checks
    location /health {
        proxy_pass http://tta_gameplay;
        access_log off;
    }
}
```

## Monitoring and Observability

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'tta-gameplay'
    static_configs:
      - targets: ['tta-gameplay:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "TTA Gameplay Loop Metrics",
    "panels": [
      {
        "title": "Active WebSocket Connections",
        "type": "stat",
        "targets": [
          {
            "expr": "tta_websocket_connections_active"
          }
        ]
      },
      {
        "title": "Story Generation Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(tta_stories_generated_total[5m])"
          }
        ]
      },
      {
        "title": "Therapeutic Interventions",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(tta_therapeutic_interventions_total[5m])"
          }
        ]
      }
    ]
  }
}
```

## Security Configuration

### SSL/TLS Setup

```bash
# Generate SSL certificate (Let's Encrypt)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tta-gameplay.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Firewall Configuration

```bash
# UFW configuration
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### Environment Security

```bash
# Secure environment variables
chmod 600 .env

# Use secrets management
# AWS: AWS Secrets Manager
# Azure: Azure Key Vault
# GCP: Google Secret Manager
# Kubernetes: Kubernetes Secrets
```

## Backup and Recovery

### Database Backup

```bash
#!/bin/bash
# backup_databases.sh

# Redis backup
redis-cli --rdb /backup/redis/dump_$(date +%Y%m%d_%H%M%S).rdb

# Neo4j backup
neo4j-admin backup --backup-dir=/backup/neo4j --name=graph_$(date +%Y%m%d_%H%M%S)

# Upload to cloud storage
aws s3 sync /backup/ s3://your-backup-bucket/tta-gameplay/
```

### Automated Backup

```yaml
# k8s/cronjob-backup.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: database-backup
  namespace: tta-gameplay
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: backup-tool:latest
            command: ["/scripts/backup_databases.sh"]
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          restartPolicy: OnFailure
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-pvc
```

## Troubleshooting

### Common Issues

**1. WebSocket Connection Failures**:
```bash
# Check WebSocket endpoint
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
  http://localhost:8000/ws/gameplay/test_player/test_session

# Check nginx WebSocket configuration
nginx -t
systemctl reload nginx
```

**2. Database Connection Issues**:
```bash
# Test Redis connection
redis-cli -h localhost -p 6379 ping

# Test Neo4j connection
cypher-shell -a bolt://localhost:7687 -u neo4j -p password
```

**3. High Memory Usage**:
```bash
# Monitor memory usage
docker stats tta-gameplay
kubectl top pods -n tta-gameplay

# Check for memory leaks
python -m memory_profiler src/main.py
```

### Log Analysis

```bash
# View application logs
docker-compose logs -f tta-gameplay
kubectl logs -f deployment/tta-gameplay -n tta-gameplay

# Search for errors
grep -i error /var/log/tta-gameplay/app.log

# Monitor real-time logs
tail -f /var/log/tta-gameplay/app.log | grep -i "therapeutic\|safety"
```

## Performance Optimization

### Application Tuning

```python
# uvicorn_config.py
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
```

### Database Optimization

```bash
# Redis optimization
echo 'vm.overcommit_memory = 1' >> /etc/sysctl.conf
echo 'net.core.somaxconn = 65535' >> /etc/sysctl.conf

# Neo4j optimization
echo 'dbms.memory.heap.initial_size=2G' >> /etc/neo4j/neo4j.conf
echo 'dbms.memory.heap.max_size=4G' >> /etc/neo4j/neo4j.conf
```

## Maintenance

### Regular Maintenance Tasks

```bash
#!/bin/bash
# maintenance.sh

# Clean up old logs
find /var/log/tta-gameplay -name "*.log" -mtime +30 -delete

# Clean up expired sessions
python scripts/cleanup_expired_sessions.py

# Update dependencies
pip install --upgrade -r requirements.txt

# Restart services
docker-compose restart tta-gameplay
```

### Health Monitoring

```bash
#!/bin/bash
# health_check.sh

# Check service health
curl -f http://localhost:8000/health || exit 1

# Check database connections
redis-cli ping || exit 1
cypher-shell -a bolt://localhost:7687 -u neo4j -p password "RETURN 1" || exit 1

# Check disk space
df -h | awk '$5 > 80 {print $0}' | grep -q . && exit 1

echo "All health checks passed"
```

This completes the comprehensive deployment guide for the complete gameplay loop implementation.
