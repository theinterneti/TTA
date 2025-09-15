# Documentation Deployment Guide

This guide explains how to deploy TTA documentation to various platforms.

## Automated Deployment

### GitHub Pages (Primary)

The documentation is automatically deployed to GitHub Pages when changes are pushed to the `main` branch.

**Setup:**
1. Enable GitHub Pages in repository settings
2. Set source to "GitHub Actions"
3. The `.github/workflows/docs.yml` workflow handles the rest

**Access:** https://theinterneti.github.io/TTA/

### Pull Request Previews

Documentation previews are generated for pull requests:
1. Build artifacts are created for each PR
2. Download the `pr-documentation-preview` artifact
3. Extract and open `index.html` locally

## Manual Deployment

### Local Build and Serve

```bash
# Build documentation
cd docs/sphinx
uv run sphinx-build -b html . _build/html

# Serve locally
cd _build/html
python -m http.server 8000
# Visit http://localhost:8000
```

### Deploy to Custom Server

```bash
# Build documentation
./scripts/build_docs.sh

# Copy to server (example)
rsync -avz docs/sphinx/_build/html/ user@server:/var/www/tta-docs/

# Or use SCP
scp -r docs/sphinx/_build/html/* user@server:/var/www/tta-docs/
```

## Platform-Specific Deployments

### Netlify

1. Connect your GitHub repository to Netlify
2. Set build command: `cd docs/sphinx && uv run sphinx-build -b html . _build/html`
3. Set publish directory: `docs/sphinx/_build/html`
4. Add environment variables if needed

### Vercel

Create `vercel.json` in project root:

```json
{
  "buildCommand": "cd docs/sphinx && uv run sphinx-build -b html . _build/html",
  "outputDirectory": "docs/sphinx/_build/html",
  "installCommand": "uv pip install -r requirements.txt && uv pip install -r requirements-dev.txt"
}
```

### Read the Docs

1. Import project from GitHub
2. Configure in `.readthedocs.yaml`:

```yaml
version: 2

build:
  os: ubuntu-22.04
  tools:
    python: "3.11"

sphinx:
  configuration: docs/sphinx/conf.py

python:
  install:
    - requirements: requirements.txt
    - requirements: requirements-dev.txt
```

## Documentation Versioning

### Version Strategy

- `latest`: Always points to main branch
- `stable`: Latest stable release
- `v1.0`, `v1.1`, etc.: Specific versions

### Creating Version Branches

```bash
# Create version branch
git checkout -b docs/v1.0 v1.0.0

# Update version in conf.py
sed -i 's/version = .*/version = "1.0"/' docs/sphinx/conf.py
sed -i 's/release = .*/release = "1.0.0"/' docs/sphinx/conf.py

# Commit and push
git commit -am "docs: set version to 1.0.0"
git push origin docs/v1.0
```

## Monitoring and Maintenance

### Health Checks

The documentation deployment includes several quality checks:

1. **Link Checking**: Validates all external links
2. **Coverage Report**: Identifies undocumented modules
3. **Build Warnings**: Ensures clean builds
4. **Metrics Collection**: Tracks documentation statistics

### Updating Documentation

1. **Content Updates**: Edit RST/MD files in `docs/sphinx/`
2. **API Changes**: Run `sphinx-apidoc` to regenerate API docs
3. **Configuration**: Update `docs/sphinx/conf.py` as needed
4. **Styling**: Modify `docs/sphinx/_static/custom.css`

### Troubleshooting

**Build Failures:**
- Check Python path and imports
- Verify all dependencies are installed
- Review Sphinx warnings and errors

**Missing API Documentation:**
- Ensure modules are importable
- Check `sphinx-apidoc` exclusion patterns
- Verify docstring formatting

**Broken Links:**
- Run `sphinx-build -b linkcheck` locally
- Update or remove broken external links
- Fix internal cross-references

## Performance Optimization

### Build Speed

- Use `sphinx-build -j auto` for parallel builds
- Cache dependencies in CI/CD
- Exclude unnecessary files from autodoc

### Site Performance

- Optimize images and static assets
- Enable compression on web server
- Use CDN for static content
- Implement proper caching headers

## Security Considerations

### Access Control

- Use branch protection rules
- Require PR reviews for documentation changes
- Limit who can trigger deployments

### Content Security

- Sanitize user-contributed content
- Validate external links
- Monitor for sensitive information in docs

## Backup and Recovery

### Backup Strategy

- Documentation source is in Git (primary backup)
- Built documentation artifacts stored in CI/CD
- Regular exports to external storage

### Recovery Procedures

1. **Source Recovery**: Restore from Git history
2. **Build Recovery**: Re-run CI/CD pipeline
3. **Site Recovery**: Redeploy from artifacts

## Analytics and Monitoring

### Usage Analytics

- Google Analytics integration
- GitHub Pages insights
- Custom event tracking

### Performance Monitoring

- Page load times
- Search functionality
- User engagement metrics

## Future Enhancements

### Planned Features

- Multi-language support
- Interactive API explorer
- Video tutorials integration
- Community contribution system

### Technical Improvements

- Progressive Web App features
- Offline documentation access
- Advanced search capabilities
- Real-time collaboration tools
