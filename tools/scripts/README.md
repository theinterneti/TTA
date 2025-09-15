# TTA Scripts

This directory contains scripts for the TTA project.

## Directories

- **dev**: Development scripts
- **docker**: Docker-related scripts
- **maintenance**: Maintenance scripts
- **utils**: Utility scripts
- **setup**: Setup scripts

## Main Scripts

### Development Environment

- **augster_startup.sh**: 🚀 **The Augster Startup Script** - Comprehensive TTA development environment initialization
  - Automated service management (Redis, Neo4j, FastAPI)
  - Health verification and monitoring setup
  - Multiple startup modes (development, testing, production-ready)
  - See [README_AUGSTER_STARTUP.md](README_AUGSTER_STARTUP.md) for detailed documentation
- **setup_dev_environment.sh**: Basic development environment setup (Python, uv, pre-commit)

### Shell Optimization

- **optimized_bashrc**: ⚡ **Optimized Shell Configuration** - High-performance shell setup
  - 99.5% faster startup time (595ms → 3ms)
  - Lazy loading of expensive tools (pyenv, nvm, etc.)
  - Context-aware tool loading for TTA projects
  - TTA-specific aliases and development shortcuts
- **install_optimized_shell.sh**: Safe installation script with backup and rollback
- **shell_performance_test.sh**: Performance benchmarking and testing script
- **shell_optimization_analysis.md**: Detailed analysis and optimization strategy
- **shell_optimization_summary.md**: Complete performance results and implementation guide

### Organization and Maintenance

- **organize_tta.sh**: Main script to organize the TTA repository
- **organize_files.sh**: Script to organize files in the TTA repository
- **organize_documentation.sh**: Script to organize documentation in the TTA repository
- **ensure_docker_consistency.sh**: Script to ensure Docker and DevContainer consistency across repositories
