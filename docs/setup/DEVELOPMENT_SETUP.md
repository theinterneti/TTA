# TTA Development Setup Guide

This guide covers the enhanced development environment for the TTA (Therapeutic Text Adventure) project, including monitoring, logging, and development experience improvements.

## 🚀 Quick Start

### Option 1: VS Code Dev Container (Recommended)
1. Open the project in VS Code
2. Install the "Dev Containers" extension
3. Press `Ctrl+Shift+P` and select "Dev Containers: Reopen in Container"
4. Wait for the container to build and start
5. All services will be available with hot reloading enabled

### Option 2: Manual Docker Compose
```bash
# Start core TTA services
docker-compose -f tta.dev/docker-compose.yml up -d

# Add hot reloading for development
docker-compose -f tta.dev/docker-compose.yml -f docker-compose.hotreload.yml up

# Start monitoring stack (optional)
docker-compose -f monitoring/docker-compose.monitoring.yml up -d
```

## 📊 Monitoring & Observability

### Prometheus + Grafana Stack
The monitoring stack provides comprehensive observability for your TTA services:

**Start monitoring:**
```bash
cd monitoring
docker-compose up -d
```

**Access points:**
- **Grafana Dashboard**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Loki Logs**: http://localhost:3100

**Features:**
- Container metrics (CPU, memory, network)
- System metrics (disk, load, processes)
- Application metrics (API response times, error rates)
- Centralized logging with Loki
- Pre-configured dashboards for TTA services

### Metrics Collection
The stack automatically collects metrics from:
- TTA API services (ports 8001-8005)
- Redis database
- Neo4j graph database
- System resources
- Docker containers

## 🔧 Development Experience

### VS Code Dev Container
The `.devcontainer/devcontainer.json` provides:
- **Pre-configured Python environment** with UV package manager
- **Essential VS Code extensions** for Python, Docker, Git, and TTA development
- **Port forwarding** for all TTA services and monitoring tools
- **Integrated terminal** with Zsh and Oh My Zsh
- **Docker-in-Docker** support for container management

**Included Extensions:**
- Python development (Black, Flake8, Pylint, Jupyter)
- Docker and container tools
- Git and GitHub integration
- Database tools (Redis, Neo4j)
- API testing tools
- YAML and configuration file support

### Hot Reloading Development
Use `docker-compose.hotreload.yml` for fast development iteration:

```bash
# Start with hot reloading
docker-compose -f tta.dev/docker-compose.yml -f docker-compose.hotreload.yml up

# Or specific services
docker-compose -f tta.dev/docker-compose.yml -f docker-compose.hotreload.yml up admin-api clinical-api
```

**Hot reloading features:**
- Source code mounted as volumes
- Uvicorn auto-reload enabled
- Development environment variables
- Builder stage containers for faster rebuilds
- Cached volume mounts for better performance

## 🗂️ Project Structure

```
/
├── monitoring/                     # Monitoring and observability
│   ├── docker-compose.monitoring.yml
│   ├── prometheus/
│   │   └── prometheus.yml
│   ├── grafana/
│   │   ├── datasources/
│   │   └── dashboards/
│   └── promtail/
│       └── promtail.yml
├── .devcontainer/                  # VS Code dev container
│   ├── devcontainer.json
│   └── docker-compose.dev.yml
├── docker-compose.hotreload.yml    # Hot reloading overrides
├── tta.dev/                        # Core development services
└── tta.prototype/                  # Prototype environment
```

## 🛠️ Development Workflows

### Daily Development
1. **Start dev container**: Open in VS Code dev container
2. **Code changes**: Edit files with automatic hot reloading
3. **Test APIs**: Use Thunder Client or REST Client extensions
4. **Monitor**: Check Grafana dashboards for performance
5. **Debug**: Use integrated Python debugger

### Performance Monitoring
1. **Start monitoring stack**: `docker-compose -f monitoring/docker-compose.monitoring.yml up -d`
2. **Access Grafana**: http://localhost:3001
3. **View metrics**: Container health, API performance, resource usage
4. **Check logs**: Centralized logging in Grafana with Loki

### Database Management
- **Redis**: Use Redis extension in VS Code or Redis Commander at http://localhost:8081
- **Neo4j**: Access Neo4j Browser at http://localhost:7474

## 🔍 Troubleshooting

### Common Issues

**Docker build failures:**
- Clear Docker cache: `docker system prune -a`
- Rebuild without cache: `docker-compose build --no-cache`

**Port conflicts:**
- Check running services: `docker ps`
- Stop conflicting containers: `docker stop <container_name>`

**Hot reloading not working:**
- Ensure source code is mounted correctly
- Check file permissions in WSL2
- Restart containers: `docker-compose restart`

**Monitoring not showing data:**
- Verify Prometheus targets: http://localhost:9090/targets
- Check service health endpoints
- Review Prometheus configuration

### Performance Tips

**For WSL2 users:**
- Keep source code in WSL2 filesystem for better performance
- Use cached volume mounts for dependencies
- Allocate sufficient memory to Docker Desktop

**For development:**
- Use builder stage containers for faster rebuilds
- Enable Docker BuildKit for improved caching
- Use tmpfs volumes for temporary data

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [VS Code Dev Containers](https://code.visualstudio.com/docs/remote/containers)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Loki Documentation](https://grafana.com/docs/loki/)

## 🎯 Next Steps

1. **Customize dashboards**: Create TTA-specific Grafana dashboards
2. **Add alerting**: Configure Prometheus alerts for critical metrics
3. **Extend logging**: Add structured logging to TTA services
4. **Performance testing**: Use monitoring to identify bottlenecks
5. **CI/CD integration**: Incorporate monitoring into deployment pipelines
