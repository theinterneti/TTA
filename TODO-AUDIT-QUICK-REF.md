# 🚀 TTA TODO Audit - Quick Reference Card

**Print this page or bookmark it for daily use**

---

## 📍 Quick Commands

```bash
# All commands run from project root
cd /home/thein/recovered-tta-storytelling

# Generate report (weekly review)
python3 scripts/todo-audit.py report

# Scan codebase TODOs
python3 scripts/todo-audit.py scan

# Find broken issue links
python3 scripts/todo-audit.py orphans

# Export to Logseq
python3 scripts/todo-audit.py export

# Sync GitHub issues
python3 scripts/todo-audit.py sync
```

---

## 📂 Key Files

| File | Purpose | Update Frequency |
|------|---------|------------------|
| `.augment/TODO-AUDIT.md` | Main audit document | Weekly |
| `TODO-AUDIT-SUMMARY.md` | Executive summary | Weekly |
| `.augment/README-TODO-AUDIT.md` | User guide | As needed |
| `scripts/todo-audit.py` | Automation script | As needed |
| `.augment/logseq/config.edn` | Logseq config | Rarely |

---

## ✍️ TODO Format

### ✅ GOOD Examples

```python
# TODO(#55): Implement component_registry module
# Clear reference to GitHub issue #55

# TODO: [HIGH] Add authentication tests - SECURITY
# Priority marker and category tag

# TODO: Refactor database connection (Effort: 2 days)
# Includes effort estimate

# TODO(@alice): Review error handling logic
# Assignment to team member
```

### ❌ BAD Examples

```python
# TODO: fix this
# Too vague, no context

# todo refactor
# Wrong format, not scannable

# TODO: implement everything
# Not actionable, too broad
```

---

## 🔍 Quick Searches

### Find TODOs in Component

```bash
# Authentication TODOs
grep -r "TODO" src/player_experience/

# Model Management TODOs
grep -r "TODO" src/components/model_management/

# All high priority TODOs
grep -r "TODO.*HIGH" src/
```

### Check TODO Health

```bash
# TODOs referencing issues
grep -r "TODO(#" src/ | wc -l

# TODOs without issue links
grep -r "TODO[^(]" src/ | wc -l

# Security TODOs
grep -r "TODO.*SECURITY" src/
```

---

## 🏷️ Priority Tags

Use in TODO comments:

- `[HIGH]` or `[CRITICAL]` → High priority
- `[MEDIUM]` or `[IMPORTANT]` → Medium priority
- `[LOW]` or no tag → Low priority

**Keywords** (auto-detected):
- `critical`, `urgent`, `blocker`, `security` → HIGH
- `important`, `soon`, `mvp` → MEDIUM

---

## 🎯 Category Tags

Use in TODO comments:

- `#mvp-blocker` - Blocks MVP completion
- `#security` - Security-related
- `#performance` - Performance optimization
- `#refactoring` - Code quality improvement
- `#documentation` - Docs needed
- `#testing` - Test coverage gap

---

## 📊 Status Workflow

```
TODO → DOING → WAITING → DONE
       ↓
     BLOCKED → LATER
       ↓
   CANCELLED
```

**Markers**:
- `TODO` - Not started
- `DOING` - In progress
- `WAITING` - Awaiting dependency
- `BLOCKED` - Cannot proceed
- `LATER` - Deferred (post-MVP)
- `DONE` - Completed
- `CANCELLED` - No longer needed

---

## 🎨 Logseq Query Snippets

Copy-paste into Logseq:

### MVP Blockers

```clojure
#+BEGIN_QUERY
{:title "🔥 MVP Blockers"
 :query [:find (pull ?b [*])
         :where
         [?b :block/marker "TODO"]
         [?b :block/content ?content]
         [(clojure.string/includes? ?content "#mvp-blocker")]]}
#+END_QUERY
```

### High Priority

```clojure
#+BEGIN_QUERY
{:title "⚡ High Priority"
 :query [:find (pull ?b [*])
         :where
         [?b :block/marker "TODO"]
         [?b :block/content ?content]
         (or
           [(clojure.string/includes? ?content "[HIGH]")]
           [(clojure.string/includes? ?content "CRITICAL")])]}
#+END_QUERY
```

### In Progress

```clojure
#+BEGIN_QUERY
{:title "🚀 In Progress"
 :query [:find (pull ?b [*])
         :where
         [?h :block/marker ?marker]
         [(contains? #{"DOING" "NOW"} ?marker)]]}
#+END_QUERY
```

---

## 🔗 Quick Links

### Documentation

- Main Audit: `.augment/TODO-AUDIT.md`
- User Guide: `.augment/README-TODO-AUDIT.md`
- This Card: `TODO-AUDIT-QUICK-REF.md`

### External

- GitHub Issues: https://github.com/theinterneti/TTA/issues
- Project Board: https://github.com/users/theinterneti/projects/
- Logseq: https://logseq.com/

---

## 📅 Weekly Checklist

**Every Monday** (Sprint Planning):

- [ ] Run `python3 scripts/todo-audit.py report`
- [ ] Review MVP blockers
- [ ] Clean up orphaned TODOs
- [ ] Update GitHub issue statuses
- [ ] Export to Logseq for planning
- [ ] Assign TODOs to sprint

**Every Friday** (Sprint Review):

- [ ] Check completed TODOs
- [ ] Update audit document
- [ ] Close resolved GitHub issues
- [ ] Document learnings
- [ ] Generate weekly report

---

## 🚨 Pre-Commit Checklist

**Before committing code with TODOs**:

- [ ] TODO has clear description
- [ ] Linked to GitHub issue if applicable
- [ ] Priority tagged if high/medium
- [ ] Effort estimated if >1 day
- [ ] Not referencing closed issue
- [ ] Proper format (scannable)

**Quick Check**:

```bash
# Check for orphaned TODOs in your changes
git diff --cached | grep "TODO(#"
```

---

## 💡 Pro Tips

1. **Link Early**: Add issue reference immediately
2. **Be Specific**: "Implement auth" → "Implement OAuth 2.0 login flow"
3. **Estimate Effort**: Helps sprint planning
4. **Tag Security**: Makes audits easier
5. **Update Often**: Weekly audit keeps system current
6. **Use Logseq**: Queries save hours of manual filtering

---

## 🛟 Emergency Contacts

**System Not Working?**

1. Check Python version: `python3 --version` (need 3.10+)
2. Check GitHub CLI: `gh --version` (install if missing)
3. Check file permissions: `ls -la scripts/todo-audit.py`

**Need Help?**

- Read: `.augment/README-TODO-AUDIT.md`
- Check: `AGENTS.md` (project context)
- Open: GitHub issue with label `audit-system`

---

## 📈 Key Metrics (Current)

**As of 2025-11-01**:

- 📊 GitHub Issues: 51 open
- 📝 Code TODOs: 209 total
- 🔥 High Priority: 9 items
- ⚠️ Orphaned: 6 items
- 🚨 MVP Blockers: 6 issues

**Targets**:

- Reduce TODOs: 10/week
- Close Issues: 3-5/week
- Zero Orphans: Always
- <10 High Priority: Maintain

---

**💾 Save this page** | **🖨️ Print for desk reference** | **🔖 Bookmark in browser**

---

*Last Updated: 2025-11-01 | Next Review: 2025-11-08*
