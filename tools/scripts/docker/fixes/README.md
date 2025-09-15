# TTA Docker Fixes

This directory contains scripts for fixing common Docker-related issues in the TTA project.

## Scripts

- **fix_docker_access.sh**: Fix Docker access permissions
- **fix_docker_access_existing.sh**: Fix Docker access for existing containers
- **fix_docker_access_simple.sh**: Simple Docker access fix
- **fix_docker_in_container.sh**: Fix Docker-in-Docker issues
- **fix_docker_socket.sh**: Fix Docker socket issues
- **fix_docker_socket_permissions.sh**: Fix Docker socket permissions
- **fix_docker_socket_simple.sh**: Simple Docker socket fix

## Common Issues and Solutions

### Docker Socket Permissions

If you encounter permission issues with the Docker socket, use:

```bash
./scripts/docker/fixes/fix_docker_socket_permissions.sh
```

### Docker-in-Docker Issues

If you're having issues with Docker-in-Docker, use:

```bash
./scripts/docker/fixes/fix_docker_in_container.sh
```

### Docker Access Issues

If you're having issues with Docker access, use:

```bash
./scripts/docker/fixes/fix_docker_access.sh
```

For existing containers, use:

```bash
./scripts/docker/fixes/fix_docker_access_existing.sh
```

## Related Documentation

For more information on Docker configuration and troubleshooting in the TTA project, see:

- [Docker Configuration](../../../Documentation/setup/docker/README.md)
- [Docker Troubleshooting](../../../Documentation/deployment/troubleshooting/troubleshooting.md)
- [Docker Deployment](../../../Documentation/deployment/docker/docker-deployment.md)
