# Archived Components


> **Note**: The `platform_tta_dev` directory has been migrated to the TTA.dev repository.
> See https://github.com/yourusername/TTA.dev for the toolkit components.



This directory contains deprecated tools and experiments that are no longer actively maintained or integrated into the TTA platform.

## Archive Policy

Components are moved here when:

- They have been superseded by newer implementations
- Experimental features were not adopted
- Integration complexity outweighed benefits
- Platform architecture shifted away from the approach

Archived code is retained for:

- Historical reference
- Potential future revival if requirements change
- Learning from past experiments

## Contents

### kiro/

- **Deprecated**: 2024-Q4
- **Reason**: Experimental specification framework that was not fully adopted
- **Migration Path**: N/A (experimental tooling)
- **Notes**: `.kiro/` specs and related infrastructure. Not integrated into main workflows.

### openhands/

- **Deprecated**: 2024-Q4
- **Reason**: Agent orchestration approach superseded by platform_tta_dev agentic primitives
- **Migration Path**: See `platform_tta_dev/components/` for current agent orchestration
- **Notes**: Includes integration code, tests, and documentation. Replaced by serena, cline, and ACE framework integration.

### openhands_legacy/

- **Deprecated**: 2024-Q3
- **Reason**: Earlier iteration of OpenHands integration
- **Migration Path**: Consolidated into openhands/ archive
- **Notes**: Legacy experiments and prototypes from earlier development phases.

### gemini/

- **Deprecated**: 2024-Q4
- **Reason**: GitHub workflow automation experiments superseded by cline/serena integration
- **Migration Path**: See `.github/workflows/` for current CI/CD automation
- **Notes**: Gemini-based workflow experiments. Functionality now handled by platform_tta_dev components.

### github_workflows_gemini/

- **Deprecated**: 2024-Q4
- **Reason**: Part of gemini workflow experiments
- **Migration Path**: Current workflows in `.github/workflows/`
- **Notes**: Related to gemini/ archive above.

## Historical Documentation

See `legacy_README.md` for the original legacy directory documentation.

## Reactivation Process

If you need to reactivate archived code:

1. Review the deprecation reason and migration path
2. Check if current platform provides equivalent functionality
3. If revival is necessary:
   - Create an issue describing the use case
   - Tag with `archaeology` label
   - Get architectural approval before moving code back
   - Update dependencies and adapt to current platform architecture

## Maintenance

This archive is **not maintained**:

- No dependency updates
- No security patches
- No compatibility guarantees
- Code may not run on current platform

Use for reference only.

---

**Last Updated**: 2025-11-16
**Archive Policy Version**: 1.0


---
**Logseq:** [[TTA.dev/_archive/Readme]]
