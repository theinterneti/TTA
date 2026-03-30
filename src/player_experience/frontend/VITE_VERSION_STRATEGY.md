# Vite Version Management Strategy

**Date**: October 27, 2025
**Status**: Active
**Strategy**: Intelligent Dual-Version Management

## Problem

- **Main App**: Uses Vite 7.1.6 (latest, best performance)
- **Storybook**: Only supports Vite ≤6.2.5 (as of Storybook 8.6.14)

## Solution: Dual-Version Approach

We maintain TWO separate Vite installations intelligently:

### Architecture

```
├── package.json (Vite 7 for main app)
├── .storybook/
│   └── package.json (Vite 6 for Storybook only)
└── scripts/
    └── storybook-wrapper.sh (Automatic version switcher)
```

### Implementation

**1. Main `package.json`** - Uses Vite 7
```json
{
  "dependencies": {
    "vite": "^7.1.6"  // Main app uses Vite 7
  }
}
```

**2. `.storybook/package.json`** - Uses Vite 6
```json
{
  "name": "tta-storybook-env",
  "private": true,
  "dependencies": {
    "vite": "^6.0.0",  // Storybook uses Vite 6
    "@storybook/react-vite": "^8.6.14"
  }
}
```

**3. Wrapper Scripts** - Automatic switching
```bash
# npm run storybook → Uses Vite 6
# npm run dev → Uses Vite 7
# npm run build → Uses Vite 7
```

## How It Works

### Starting Storybook
```bash
npm run storybook
# → Runs: scripts/storybook-wrapper.sh
# → Installs .storybook/node_modules with Vite 6
# → Starts Storybook with isolated Vite 6 environment
```

### Starting Main App
```bash
npm run dev
# → Uses main node_modules with Vite 7
# → No conflicts, no version issues
```

## Benefits

✅ **Zero Conflicts**: Each tool uses its preferred Vite version
✅ **No Downgrades**: Main app stays on cutting-edge Vite 7
✅ **Transparent**: Developers don't need to think about it
✅ **Future-Proof**: Easy to remove when Storybook supports Vite 7
✅ **CI/CD Compatible**: Works seamlessly in pipelines

## Migration Path

When Storybook officially supports Vite 7:

1. Remove `.storybook/package.json`
2. Remove `scripts/storybook-wrapper.sh`
3. Update main `package.json` Storybook dependencies
4. Update scripts to use direct Storybook commands
5. Delete this document

## Technical Details

### Node Module Resolution
- Main app: `node_modules/vite@7.1.6`
- Storybook: `.storybook/node_modules/vite@6.0.0`
- NODE_PATH ensures correct resolution per context

### Script Switching Logic
```bash
# .storybook/package.json takes precedence when running Storybook
cd .storybook && npm install && npm run storybook-dev
```

### Performance Impact
- **Disk Space**: +~50MB for duplicate Vite installation
- **Build Time**: +~10s on first Storybook start (Vite 6 install)
- **Runtime**: No impact - each tool optimal for its version

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Downgrade Vite to 6.x globally | Lose Vite 7 performance gains |
| Remove Storybook | Lose component documentation & visual testing |
| Use experimental alpha | Too risky for production |
| Monorepo separation | Over-engineered for this use case |

## Maintenance

- **Update Main App Vite**: `npm install vite@latest`
- **Update Storybook Vite**: Edit `.storybook/package.json`
- **Monitor**: Check Storybook releases for Vite 7 support

---

**This is a temporary bridge solution until Storybook officially supports Vite 7.**


---
**Logseq:** [[TTA.dev/Player_experience/Frontend/Vite_version_strategy]]
