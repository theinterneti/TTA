#!/bin/bash
set -e

echo "Organizing documentation across repositories..."

# Create necessary documentation directories
mkdir -p Documentation/setup
mkdir -p Documentation/docker
mkdir -p Documentation/development
mkdir -p Documentation/architecture
mkdir -p Documentation/ai-framework
mkdir -p Documentation/therapeutic-content

# Move documentation files from root to Documentation directory
find . -maxdepth 1 -name "*.md" -not -path "./README.md" -exec mv {} Documentation/ \;

# Organize documentation in tta.dev
mkdir -p tta.dev/Documentation/setup
mkdir -p tta.dev/Documentation/docker
mkdir -p tta.dev/Documentation/development
mkdir -p tta.dev/Documentation/ai-framework

# Organize documentation in TTA.prototype
mkdir -p TTA.prototype/Documentation/setup
mkdir -p TTA.prototype/Documentation/docker
mkdir -p TTA.prototype/Documentation/development
mkdir -p TTA.prototype/Documentation/therapeutic-content

# Create index files for documentation
cat > Documentation/README.md << EOF
# TTA Documentation

This directory contains documentation for the TTA project.

## Directories

- **setup**: Setup and installation instructions
- **docker**: Docker and DevContainer documentation
- **development**: Development guidelines and processes
- **architecture**: System architecture documentation
- **ai-framework**: AI framework documentation
- **therapeutic-content**: Therapeutic content documentation

## Main Documentation Files

- [README.md](../README.md): Main project README
- [ENV_STRUCTURE.md](ENV_STRUCTURE.md): Environment structure documentation
- [GITHUB_SETUP.md](GITHUB_SETUP.md): GitHub setup documentation
EOF

cat > tta.dev/Documentation/README.md << EOF
# TTA.dev Documentation

This directory contains documentation for the TTA.dev project, which focuses on reusable AI components.

## Directories

- **setup**: Setup and installation instructions
- **docker**: Docker and DevContainer documentation
- **development**: Development guidelines and processes
- **ai-framework**: AI framework documentation

## Main Documentation Files

- [README.md](../README.md): Main project README
EOF

cat > TTA.prototype/Documentation/README.md << EOF
# TTA.prototype Documentation

This directory contains documentation for the TTA.prototype project, which focuses on narrative elements.

## Directories

- **setup**: Setup and installation instructions
- **docker**: Docker and DevContainer documentation
- **development**: Development guidelines and processes
- **therapeutic-content**: Therapeutic content documentation

## Main Documentation Files

- [README.md](../README.md): Main project README
EOF

echo "Documentation organization completed!"
