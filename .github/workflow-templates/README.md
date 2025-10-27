# GitHub Actions Workflow Templates

**Version**: 1.0.0
**Last Updated**: 2025-10-27
**Status**: Production-ready

## Overview

This directory contains best-practice GitHub Actions workflow templates for the TTA project. These templates follow current GitHub Actions standards and incorporate lessons learned from our CI/CD infrastructure improvements.

## Available Templates

### 1. Python CI Template (`python-ci-template.yml`)

**Purpose**: Comprehensive Python testing, linting, and security scanning

**Features**:

- ✅ UV package manager (v0.8.17+) with caching
- ✅ Multi-version Python testing (3.11, 3.12)
- ✅ Ruff linting and formatting
- ✅ Pyright type checking
- ✅ Bandit security scanning with SARIF output
- ✅ Coverage reporting (Codecov integration)
- ✅ Test result artifacts

**Actions Used**:

- `actions/checkout@v4`
- `actions/setup-python@v5`
- `astral-sh/setup-uv@v1`
- `actions/cache@v4`
- `actions/upload-artifact@v4`
- `codecov/codecov-action@v4`
- `github/codeql-action/upload-sarif@v3`

**Usage**:

```bash
cp .github/workflow-templates/python-ci-template.yml .github/workflows/ci.yml
# Edit the template to match your project structure
```


### 2. Docker Build Template (`docker-build-template.yml`)

**Purpose**: Secure Docker image building with vulnerability scanning

**Features**:

- ✅ Docker Buildx with multi-platform support
- ✅ GitHub Container Registry (GHCR) integration
- ✅ Automatic semantic versioning from tags
- ✅ Build cache optimization (GitHub Actions cache)
- ✅ Trivy security scanning with SARIF output
- ✅ Hadolint Dockerfile validation
- ✅ SBOM (Software Bill of Materials) generation
- ✅ Image provenance attestation

**Actions Used**:

- `docker/setup-buildx-action@v3`
- `docker/login-action@v3`
- `docker/metadata-action@v5`
- `docker/build-push-action@v5`
- `aquasecurity/trivy-action@master`
- `hadolint/hadolint-action@v3.1.0`

**Usage**:

```bash
cp .github/workflow-templates/docker-build-template.yml .github/workflows/docker.yml
# Update IMAGE_NAME and Dockerfile path
```


## Best Practices Implemented

### General

1. **Action Versions**: Using latest stable versions (v4/v5)
2. **Timeouts**: All jobs have timeout limits to prevent hung workflows
3. **Permissions**: Minimal required permissions specified
4. **Caching**: Aggressive caching for faster builds
5. **Artifacts**: Proper retention policies (7-30 days)

### Python-Specific

1. **Package Manager**: UV (modern, fast dependency resolver)
2. **Dependency Locking**: uv.lock for reproducible builds
3. **Matrix Testing**: Multiple Python versions
4. **Type Safety**: Pyright for static type checking
5. **Security**: Bandit scanning with SARIF integration

### Docker-Specific

1. **Build Kit**: Enabled by default for better caching
2. **Multi-stage**: Support for optimized images
3. **Security Scanning**: Trivy for vulnerabilities
4. **SBOM**: Automatic generation for supply chain security
5. **Provenance**: Attestation for build verification

## Lessons Learned (Applied to Templates)

### From Our CI/CD Improvements (Oct 2025)

1. **Docker Build Context**
   - Problem: `.dockerignore` excluding required files
   - Solution: Careful `.dockerignore` patterns documented in templates

2. **Metadata Tags**
   - Problem: Invalid `{{branch}}` template in PR contexts
   - Solution: Use `type=sha` and `type=ref` patterns only

3. **CodeQL Setup**
   - Problem: Running npm ci without package.json
   - Solution: Check for file existence before installation steps

4. **SBOM Generation**
   - Problem: Outdated CLI syntax for cyclonedx-py
   - Solution: Use `environment --of` instead of `requirements --format`

5. **Frontend Dependencies**
   - Problem: SBOM tools need installed dependencies
   - Solution: Run npm ci before SBOM generation

## Customization Guide

### Python CI Template

1. **Python Versions**: Update `matrix.python-version` for your supported versions
2. **Test Command**: Modify pytest command in "Run tests with coverage" step
3. **Coverage**: Add/remove coverage providers (Codecov, Coveralls, etc.)
4. **Additional Tools**: Add mypy, pylint, or other tools as needed

### Docker Build Template

1. **Registry**: Change `REGISTRY` env var for other registries (Docker Hub, AWS ECR)
2. **Platforms**: Add `platforms: linux/amd64,linux/arm64` for multi-arch
3. **Build Args**: Add `build-args` to pass environment variables
4. **Multiple Images**: Duplicate job for different Dockerfiles

## Testing Templates Locally

### Python CI

```bash
# Install act (https://github.com/nektos/act)
brew install act  # macOS
# or
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run workflow locally
act -j test -j lint -j security
```

### Docker Build

```bash
# Test Docker build locally
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --cache-from type=local,src=/tmp/.buildx-cache \
  --cache-to type=local,dest=/tmp/.buildx-cache-new \
  .

# Test Trivy scan
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image your-image:latest
```

## Troubleshooting

### Common Issues

1. **UV Cache Not Working**
   - Ensure `enable-cache: true` in setup-uv action
   - Check cache key includes `uv.lock` hash

2. **Docker Build Cache Misses**
   - Verify `cache-from: type=gha` and `cache-to: type=gha,mode=max`
   - Check Docker Buildx version (>= 0.11)

3. **SARIF Upload Failures**
   - Ensure `security-events: write` permission
   - Verify SARIF file exists before upload

4. **Timeout Issues**
   - Increase `timeout-minutes` for slow jobs
   - Use `strategy.fail-fast: false` for matrix jobs

## Version History

- **1.0.0** (2025-10-27): Initial release
  - Python CI template with UV, Ruff, Pyright
  - Docker build template with Trivy, Hadolint
  - Applied lessons from CI/CD infrastructure improvements

## Contributing

When updating templates:

1. Test changes in a real workflow first
2. Update version number and changelog
3. Document any new best practices
4. Verify all action versions are latest stable

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [UV Package Manager](https://github.com/astral-sh/uv)
- [Ruff Linter](https://github.com/astral-sh/ruff)
- [Trivy Scanner](https://github.com/aquasecurity/trivy)
