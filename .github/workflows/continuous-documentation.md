---
name: Continuous Documentation
description: Keep README and architecture docs aligned with code changes
on:
  pull_request:
    types: [closed]
    branches: [main, staging]
  push:
    paths:
      - 'src/**/*.py'
  workflow_dispatch:
    inputs:
      module_path:
        description: 'Module path to document (e.g., src/agent_orchestration/circuit_breaker.py)'
        required: false
permissions: read-all
tools:
  - github-cli
  - mkdocs
  - python-ast
  - git
agents:
  - docs-agent
---

# Continuous Documentation Workflow

This workflow automatically synchronizes documentation with code changes. When PRs are merged or new modules are added, @docs-agent extracts docstrings, generates API documentation, and updates MkDocs site.

## Objective

Eliminate documentation drift by automatically updating docs within 1 hour of code changes. Target: <5% documentation drift, 0 broken links.

---

## Step 1: Detect Code Changes

**Executor**: GitHub Actions runner

**Duration**: ~2 minutes

### Actions

1. Get diff from merged PR or recent commits
2. Identify affected modules:
   - New Python files in `src/`
   - Modified files with docstring changes (detect `"""` in diff)
   - Changed function signatures (detect `def` or `async def` changes)
3. Check if documentation exists for changed modules
4. Generate change manifest for @docs-agent

### Commands

```bash
# If triggered by PR merge
if [ -n "$PR_NUMBER" ]; then
  # Get changed files from PR
  gh pr view $PR_NUMBER --json files --jq -r '.files[].path' | grep "\.py$" > changed-files.txt

  # Find docstring changes
  gh pr diff $PR_NUMBER | grep -E '^\+.*"""' > docstring-changes.txt
fi

# If triggered by push, check recent commits
if [ -z "$PR_NUMBER" ]; then
  git diff HEAD~1 HEAD --name-only | grep "src/.*\.py$" > changed-files.txt
  git diff HEAD~1 HEAD | grep -E '^\+.*"""' > docstring-changes.txt
fi

# Check for new modules (files not in docs/)
while read file; do
  DOC_FILE="docs/${file#src/}"
  DOC_FILE="${DOC_FILE%.py}.md"
  if [ ! -f "$DOC_FILE" ]; then
    echo "$file" >> undocumented-modules.txt
  fi
done < changed-files.txt

# Generate change manifest
cat > change-manifest.json << EOF
{
  "pr_number": ${PR_NUMBER:-null},
  "merged_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "changed_files": $(cat changed-files.txt | jq -R . | jq -s .),
  "docstring_changes": $(wc -l < docstring-changes.txt),
  "new_modules": $(cat undocumented-modules.txt 2>/dev/null | jq -R . | jq -s . || echo "[]")
}
EOF
```

### Expected Output

`change-manifest.json` listing modules that need documentation updates.

---

## Step 2: Extract Documentation

**Executor**: @docs-agent

**Duration**: ~5 minutes

### Actions

1. Parse docstrings from changed modules using Python AST
2. Extract function signatures with full type hints
3. Find usage examples from test files
4. Identify related architecture diagrams to update
5. Generate documentation fragments for each module

### Commands

```bash
# Extract docstrings with AST
for module in $(cat changed-files.txt); do
  uv run python scripts/extract_docstrings.py "$module" \
    --output "docs/generated/$(basename ${module%.py}).md"
done

# Find usage examples from tests
for module in $(cat changed-files.txt); do
  MODULE_NAME=$(basename ${module%.py})
  grep -r "$MODULE_NAME" tests/ --include="*.py" -A 10 -B 2 > examples-$MODULE_NAME.txt
done

# Check existing documentation references
for module in $(cat changed-files.txt); do
  MODULE_NAME=$(basename ${module%.py})
  grep -r "$MODULE_NAME" docs/ --include="*.md" || echo "No existing docs for $MODULE_NAME"
done
```

### Expected Output

For each changed module:
- Extracted docstrings with signatures
- Usage examples from tests
- List of docs needing updates

---

## Step 3: Update Documentation

**Executor**: @docs-agent

**Duration**: ~8 minutes

### Actions

1. Create new branch: `docs/auto-update-{module-name}-{timestamp}`
2. For new modules:
   - Create new doc file in `docs/components/` or `docs/architecture/`
   - Add entry to `mkdocs.yml` navigation
   - Update README.md component list if public API
3. For existing modules:
   - Update API documentation sections
   - Refresh code examples from tests
   - Update "Last Updated" timestamp
4. Build MkDocs site to verify: `uv run mkdocs build --strict`

### Commands

```bash
# Create branch
TIMESTAMP=$(date +%s)
MODULE_NAME=$(basename ${CHANGED_FILE%.py})
BRANCH="docs/auto-update-${MODULE_NAME}-${TIMESTAMP}"
git checkout -b $BRANCH

# Generate API documentation
uv run python scripts/generate_api_docs.py "$CHANGED_FILE" \
  --output "docs/architecture/${MODULE_NAME}-api.md"

# Update mkdocs.yml navigation (manual edit or use yq if available)
# Add: - ${MODULE_NAME} API: architecture/${MODULE_NAME}-api.md

# Build and verify
uv run mkdocs build --strict 2>&1 | tee mkdocs-build.log

# Check for warnings or errors
if grep -q "ERROR\|WARNING" mkdocs-build.log; then
  echo "❌ MkDocs build issues detected"
  exit 1
fi
```

### Expected Output

- New/updated documentation files
- Updated `mkdocs.yml` navigation
- Successful MkDocs build

---

## Step 4: Validate Documentation

**Executor**: @docs-agent

**Duration**: ~3 minutes

### Actions

1. Build MkDocs site with strict mode (fails on warnings)
2. Check for broken internal links
3. Verify all code examples are valid Python (compile check)
4. Validate cross-references to `.github/instructions/`
5. Generate preview URL for review

### Commands

```bash
# Build with strict validation
uv run mkdocs build --strict

# Check for broken internal links
grep -r "\]\(\.\." docs/ --include="*.md" | while read line; do
  FILE=$(echo "$line" | cut -d: -f1)
  LINK=$(echo "$line" | grep -o "\](.*)" | sed 's/](\(.*\))/\1/')
  LINK_FILE=$(dirname "$FILE")/$LINK

  if [ ! -f "$LINK_FILE" ]; then
    echo "❌ Broken link in $FILE: $LINK"
  fi
done

# Validate code blocks compile (extract and test)
uv run python scripts/validate_code_blocks.py docs/

# Start preview server for manual review
uv run mkdocs serve --dev-addr localhost:8000 &
SERVER_PID=$!
sleep 3

# Test preview is accessible
if curl -s http://localhost:8000 > /dev/null; then
  echo "✅ Preview available at http://localhost:8000"
else
  echo "❌ Preview server failed to start"
fi

# Cleanup
kill $SERVER_PID 2>/dev/null || true
```

### Expected Output

Validation results:
```json
{
  "mkdocs_build": "success",
  "broken_links": [],
  "invalid_code_blocks": [],
  "cross_references_valid": true,
  "preview_url": "http://localhost:8000"
}
```

---

## Step 5: Create Documentation PR

**Executor**: GitHub CLI (gh)

**Duration**: ~2 minutes

### Actions

1. Commit documentation changes
2. Push branch to remote
3. Create draft PR with:
   - Link to original code PR
   - Summary of documentation changes
   - MkDocs build validation results
   - Preview URL
4. Add labels: `documentation`, `automated`, `docs-agent`
5. Request review from documentation maintainers

### Commands

```bash
# Commit changes
git add docs/ mkdocs.yml README.md
git commit -m "docs: auto-update ${MODULE_NAME} API documentation

Generated from PR #${PR_NUMBER} merged to main.

- Extracted docstrings from ${CHANGED_FILE}
- Generated API documentation
- Updated mkdocs.yml navigation
- Validated build and links
"

# Push branch
git push origin $BRANCH

# Create draft PR
gh pr create \
  --draft \
  --title "docs: auto-update ${MODULE_NAME} API documentation" \
  --body-file .github/templates/docs-agent-pr-template.md \
  --label "documentation,automated,docs-agent" \
  --reviewer @theinterneti

# Link to code PR
PR_NUM=$(gh pr list --head $BRANCH --json number --jq '.[0].number')
gh pr comment $PR_NUM --body "📝 Auto-generated from code PR #${PR_NUMBER}"
```

### Expected Output

Draft PR with:
- Documentation updates
- Build validation confirmation
- Preview link
- Connection to original code PR

---

## Step 6: Continuous Sync

**Executor**: GitHub Actions (scheduled daily)

**Duration**: ~5 minutes

### Actions

1. Daily scan for documentation drift:
   - Compare last modified dates: `src/` vs `docs/`
   - Identify modules modified >7 days ago without doc updates
   - Check for undocumented public APIs
2. Weekly full documentation rebuild
3. Monthly architecture diagram refresh

### Commands

```bash
# Find modules newer than their docs (potential drift)
find src/ -name "*.py" -type f | while read src_file; do
  doc_file="docs/${src_file#src/}"
  doc_file="${doc_file%.py}.md"

  if [ -f "$doc_file" ]; then
    if [ "$src_file" -nt "$doc_file" ]; then
      echo "$src_file (modified $(stat -c %y $src_file | cut -d' ' -f1))" >> stale-docs.txt
    fi
  else
    echo "$src_file (no docs exist)" >> undocumented.txt
  fi
done

# Check for undocumented public functions
uv run python scripts/find_undocumented_apis.py src/ > undocumented-apis.txt

# If drift detected, create reminder issue
if [ -s stale-docs.txt ] || [ -s undocumented-apis.txt ]; then
  gh issue create \
    --title "Documentation Drift Detected ($(date +%Y-%m-%d))" \
    --body "$(cat stale-docs.txt undocumented-apis.txt)" \
    --label "documentation,drift,docs-agent"
fi
```

### Metrics Tracked

- Time from code merge to docs PR creation
- Documentation coverage (% of public APIs documented)
- Broken link count (target: 0)
- Documentation staleness (modules >7 days old without doc updates)

---

## Success Criteria

✅ Documentation PR created within 1 hour of code merge
✅ API docs auto-generated from docstrings
✅ Code examples always up-to-date
✅ <5% documentation drift (<5% of modules without recent doc updates)
✅ MkDocs builds without warnings
✅ Zero broken links

---

## Failure Handling

- **Build Fails**: Create GitHub issue with build log, do not create PR
- **Broken Links**: Fix automatically if possible, else report in issue
- **PR Creation Fails**: Retry 3 times with backoff, then create issue
- **Boundary Violation**: Halt, alert security team via GitHub issue

---

**Last Updated**: 2026-03-06
**Status**: Active agentic workflow
