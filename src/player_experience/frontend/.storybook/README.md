# Dual Vite Version Setup - Quick Start

## What's Happening?

Your frontend now intelligently manages TWO Vite versions:
- **Vite 7.1.6** - For main React app (cutting-edge performance)
- **Vite 6.0.0** - For Storybook only (compatibility requirement)

## Why?

Storybook 8.6.14 doesn't support Vite 7 yet. This setup lets you use Vite 7 for your main app while keeping Storybook working with Vite 6.

## Usage (No Changes Required!)

### Starting Storybook
```bash
npm run storybook
# → Automatically uses Vite 6 (compatible version)
# → Opens at http://localhost:6006
```

### Building Storybook
```bash
npm run build-storybook
# → Builds with Vite 6
# → Output: storybook-static/
```

### Running Storybook Tests
```bash
npm run test:storybook
# → Runs test runner with Vite 6
```

### Main App (No Changes)
```bash
npm run start     # Uses Vite 7
npm run build     # Uses Vite 7
npm run test      # Uses Vite 7
```

## Advanced Commands

### Clean Storybook Environment
```bash
npm run storybook:clean
# Removes .storybook/node_modules
```

### Reinstall Storybook
```bash
npm run storybook:reinstall
# Clean + fresh install of Storybook dependencies
```

## How It Works

1. **Main `package.json`**: Contains Vite 7 for your React app
2. **`.storybook/package.json`**: Separate environment with Vite 6
3. **Wrapper Script**: Automatically switches between versions

```
src/player_experience/frontend/
├── package.json (Vite 7 - main app)
├── node_modules/ (Vite 7)
├── .storybook/
│   ├── package.json (Vite 6 - Storybook only)
│   └── node_modules/ (Vite 6)
└── scripts/
    └── storybook-wrapper.sh (Auto-switcher)
```

## First Time Setup

The wrapper script handles everything automatically. First run will:
1. Detect `.storybook/package.json`
2. Install Storybook dependencies with Vite 6
3. Start Storybook

**No manual intervention required!**

## Troubleshooting

### Storybook won't start
```bash
npm run storybook:reinstall
```

### Version conflicts
```bash
# Clean everything and start fresh
npm run storybook:clean
rm -rf node_modules package-lock.json
npm install
npm run storybook
```

### Check Vite versions
```bash
# Main app Vite version
npm list vite

# Storybook Vite version
cd .storybook && npm list vite && cd ..
```

## When Will This Change?

This is a **temporary solution** until Storybook officially supports Vite 7 (estimated Q1 2026).

When that happens:
1. We'll merge both environments
2. Remove `.storybook/package.json`
3. Remove wrapper scripts
4. Use Vite 7 everywhere

## CI/CD Compatibility

The wrapper script works seamlessly in CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Build Storybook
  run: npm run build-storybook
  # → Automatically uses Vite 6
```

No special configuration needed!

## Performance Impact

- **Disk Space**: +~50MB (separate Vite 6 installation)
- **First Run**: +~10-15 seconds (Vite 6 install)
- **Subsequent Runs**: No overhead
- **Runtime**: Each tool uses its optimal Vite version

## Questions?

See `VITE_VERSION_STRATEGY.md` for technical details.

---

**Status**: ✅ Active (Oct 2025)
**Maintenance**: Check Storybook releases monthly for Vite 7 support
