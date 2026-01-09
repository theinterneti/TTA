# TTA Documentation Quick Reference


> **Note**: The `platform_tta_dev` directory has been migrated to the TTA.dev repository.
> See https://github.com/yourusername/TTA.dev for the toolkit components.



> 🎯 **Quick navigation guide after repository cleanup**

## 📚 Where to Find Things

### Need a How-To Guide?
📂 **Check `docs/guides/`**
- Testing workflows → `docs/guides/testing.md`
- Docker setup → `docs/guides/docker-quick-start.md`
- Database usage → `docs/guides/database-quick-ref.md`
- Advanced testing → `docs/guides/advanced-testing.md`

### Need Current Status?
📊 **Check `docs/status/`**
- Current sprint → `docs/status/current-sprint.md`
- P0 components → `docs/status/p0-components.md`
- Component maturity → `docs/status/component-maturity.md`

### Setting Up Environment?
⚙️ **Check `docs/setup/`**
- Dev environment → `docs/setup/dev-environment.md`
- MCP servers → `docs/setup/mcp-servers.md`
- VSCode database → `docs/setup/vscode-database.md`

### Need Architecture/Deep Docs?
🧠 **Check `~/repos/TTA-notes/pages/`** (Logseq Knowledge Base)
- 306 interconnected documents
- Architecture, components, agents, workflows
- Navigation guide → `docs/reference/logseq-kb.md`

### Looking for Historical Reports?
🗄️ **Check `.archive/`**
- Organized by category and date
- Phase reports, test results, logs
- Archive guide → `.archive/README.md`

## 🎯 Quick Start by Role

### New Contributor
1. `CONTRIBUTING.md` - Contribution guidelines
2. `docs/setup/dev-environment.md` - Get set up
3. `docs/guides/testing.md` - Learn testing workflow
4. `platform_tta_dev/components/augment/kb/TTA___Architecture___Docs Architecture Overview.md` - Understand system

### Developer (Existing)
- **Daily:** `docs/status/current-sprint.md`
- **Architecture:** `platform_tta_dev/components/augment/kb/TTA___Architecture___*`
- **Debugging:** `docs/guides/database-quick-ref.md`
- **Testing:** `docs/guides/testing.md`

### DevOps/Infrastructure
- **Docker:** `docs/guides/docker-quick-start.md`
- **Deployment:** `platform_tta_dev/components/augment/kb/TTA___Workflows___Docs Deployment*`
- **Monitoring:** `platform_tta_dev/components/augment/kb/TTA___Workflows___Operations Monitoring*`

### QA/Testing
- **Test Guide:** `docs/guides/testing.md`
- **Advanced:** `docs/guides/advanced-testing.md`
- **Test Results:** `.archive/test-results/`

## 📊 Documentation Structure

```
TTA/
├── 📄 Essential (Root - 10 files)
│   ├── README.md
│   ├── CONTRIBUTING.md
│   ├── AGENTS.md (→ KB)
│   └── ...
│
├── 📖 Active Docs (docs/)
│   ├── guides/      → How-to documentation
│   ├── status/      → Current dashboards
│   ├── setup/       → Environment setup
│   ├── development/ → Process docs
│   └── reference/   → Quick references
│
├── 🧠 Knowledge Base (platform_tta_dev/components/augment/kb/)
│   └── 306 docs     → Architecture, components, deep context
│
└── 🗄️ Archive (.archive/)
    └── By category  → Historical reports, logs, results
```

## 🔍 Search Tips

### Finding Files
```bash
# Search in docs
find docs/ -name "*test*"

# Search in KB
find platform_tta_dev/components/augment/kb/ -name "*Component*"

# Search in archive
find .archive/ -name "*Phase*"
```

### Grepping Content
```bash
# Search docs content
grep -r "docker" docs/

# Search KB content
grep -r "circuit breaker" platform_tta_dev/components/augment/kb/

# Search everywhere
grep -r "redis" . --include="*.md"
```

## 🆘 Common Questions

**Q: Where did all the status reports go?**
A: `.archive/status-reports/2025-10/` and organized by category

**Q: Where's the architecture documentation?**
A: `platform_tta_dev/components/augment/kb/TTA___Architecture___*` (Logseq KB)

**Q: Where are the old logs?**
A: `.archive/logs/2025-10/` (organized by month)

**Q: How do I navigate the KB?**
A: See `docs/reference/logseq-kb.md` for navigation guide

**Q: Can I still find historical test results?**
A: Yes! `.archive/test-results/2025-10/`

## 📅 Maintenance

- **Root:** Keep at 10-15 essential files
- **docs/status/:** Update dashboards weekly
- **docs/guides/:** Update as processes change
- **.archive/:** Automated cleanup (90-day retention for logs)

## 🛠️ Cleanup Scripts

Located in `scripts/cleanup/`:
- `organize-repo-phase1.sh` - Logs & temp files
- `organize-repo-phase2.sh` - Status reports
- `organize-repo-phase3.sh` - Documentation hierarchy

Run monthly to maintain organization.

---

**Last Updated:** 2025-11-02
**Cleanup Report:** `CLEANUP_FINAL_REPORT.md`


---
**Logseq:** [[TTA.dev/Docs_quick_ref]]
