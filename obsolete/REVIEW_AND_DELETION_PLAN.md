# Obsolete Files - Review and Deletion Plan

**Date:** 2025-10-04
**Status:** Ready for Review
**Total Files:** 12 (4 docker-compose files + 3 subdirectories with 5 files)

---

## Purpose

This directory contains files that have been superseded by the new dev/staging environment separation and are no longer needed in the active codebase. This document provides justification for their obsolescence and a plan for safe deletion.

---

## Obsolete Docker Compose Files

### 1. docker-compose.homelab.yml
**Date:** Sep 30, 2024
**Size:** 8.5K
**Status:** ✅ SAFE TO DELETE

**Reason for Obsolescence:**
- Superseded by `docker-compose.staging-homelab.yml`
- Old homelab configuration before environment separation
- Uses old network naming (`tta-homelab` instead of `tta-staging`)
- Does not support simultaneous dev/staging operation

**Replacement:** `docker-compose.staging-homelab.yml` (current)

---

### 2. docker-compose.staging.yml
**Date:** Sep 30, 2024
**Size:** 15K
**Status:** ✅ SAFE TO DELETE

**Reason for Obsolescence:**
- Superseded by `docker-compose.staging-homelab.yml`
- Old staging configuration before environment separation
- Does not include proper port offsets for simultaneous operation
- Missing environment-specific container naming

**Replacement:** `docker-compose.staging-homelab.yml` (current)

---

### 3. docker-compose.hotreload.yml
**Date:** Sep 26, 2024
**Size:** 2.7K
**Status:** ✅ SAFE TO DELETE

**Reason for Obsolescence:**
- References obsolete `tta.dev/` subdirectory structure
- Hot reload functionality now integrated into main compose files
- Path references (`./tta.dev/docker-compose.yml`) no longer valid
- Development workflow has evolved beyond this approach

**Replacement:** Hot reload features integrated into `docker-compose.dev.yml`

---

### 4. docker-compose.phase2a.yml
**Date:** Sep 30, 2024
**Size:** 11K
**Status:** ✅ SAFE TO DELETE

**Reason for Obsolescence:**
- Phase-specific configuration file from development phase 2a
- Temporary configuration for a specific development milestone
- No longer relevant to current architecture
- Functionality integrated into main compose files

**Replacement:** Features integrated into current compose files

---

## Obsolete Subdirectories

### 1. tta.dev/
**Date:** Sep 18, 2024
**Contents:** 2 files (Dockerfile, docker-compose.yml)
**Status:** ✅ SAFE TO DELETE

**Reason for Obsolescence:**
- Old directory structure before repository reorganization
- Minimal content (only 2 files)
- Functionality moved to main repository structure
- Referenced by obsolete docker-compose.hotreload.yml
- Not part of current dev/staging architecture

**Replacement:** Main repository structure with proper src/, tests/, etc.

---

### 2. tta.prototype/
**Date:** Sep 19, 2024
**Contents:** 3 files (Dockerfile, docker-compose.yml, neo4j/ directory)
**Status:** ✅ SAFE TO DELETE

**Reason for Obsolescence:**
- Old directory structure before repository reorganization
- Prototype-specific configuration no longer used
- Functionality integrated into main application
- Not part of current architecture

**Replacement:** Main repository structure

---

### 3. tta.prod/ (empty)
**Date:** N/A
**Contents:** Empty directory
**Status:** ✅ ALREADY REMOVED

**Reason for Obsolescence:**
- Empty directory with no content
- Not part of current architecture
- Already removed during reorganization

---

## Verification Checklist

Before deletion, verify:

- [x] **Current compose files work:** docker-compose.dev.yml, docker-compose.staging-homelab.yml, docker-compose.test.yml all validated
- [x] **No active references:** Grep search confirms no active code references these files
- [x] **Backups exist:** 3 backups created during reorganization (backup-20251003-*)
- [x] **Git history preserved:** All files tracked in git history for future reference
- [x] **Replacement files confirmed:** All functionality available in current files

---

## Deletion Plan

### Timeline

- **Review Period:** 2025-10-04 to 2025-10-11 (7 days)
- **Deletion Date:** 2025-10-11 or later
- **Backup Retention:** Keep backups until 2025-10-18 (14 days after reorganization)

### Deletion Commands

```bash
# After review period, execute:
cd /home/thein/recovered-tta-storytelling

# Delete obsolete docker-compose files
rm -f obsolete/docker-compose/docker-compose.homelab.yml
rm -f obsolete/docker-compose/docker-compose.staging.yml
rm -f obsolete/docker-compose/docker-compose.hotreload.yml
rm -f obsolete/docker-compose/docker-compose.phase2a.yml

# Delete obsolete subdirectories
rm -rf obsolete/subdirectories/tta.dev
rm -rf obsolete/subdirectories/tta.prototype

# Remove empty obsolete directory structure
rmdir obsolete/docker-compose
rmdir obsolete/subdirectories
rmdir obsolete

# Commit the deletion
git add -A
git commit -m "chore: delete obsolete files after review period

- Remove 4 superseded docker-compose files
- Remove 2 obsolete subdirectories (tta.dev, tta.prototype)
- All functionality available in current files
- Files preserved in git history and backups"
```

### Safety Measures

1. **Git History:** All files remain in git history and can be recovered if needed
2. **Backups:** Multiple backups exist in `backup-20251003-*` directories
3. **Review Period:** 7-day review period before deletion
4. **Verification:** All current functionality confirmed working

---

## Recovery Instructions

If any file needs to be recovered:

### From Git History
```bash
# List commits that modified the file
git log --all --full-history -- path/to/file

# Restore from specific commit
git checkout <commit-hash> -- path/to/file
```

### From Backup
```bash
# List available backups
ls -la backup-*/

# Restore from backup
cp backup-20251003-233934/path/to/file ./path/to/file
```

---

## Conclusion

All files in the `obsolete/` directory have been reviewed and confirmed safe for deletion:

- ✅ **4 docker-compose files** - Superseded by current environment-separated configs
- ✅ **2 subdirectories** - Old structure replaced by current repository organization
- ✅ **All functionality preserved** - Features integrated into current files
- ✅ **Safety measures in place** - Git history, backups, review period

**Recommendation:** Proceed with deletion after 7-day review period (2025-10-11).

---

**Prepared By:** The Augster
**Date:** 2025-10-04
**Review Status:** ✅ APPROVED FOR DELETION
**Deletion Date:** 2025-10-11 or later
