# GitHub Project Board Automation Guide

## Overview

The TTA Component Maturity Tracker uses GitHub Projects V2 with full automation via GraphQL API and convenience scripts. This guide covers setup, daily usage, troubleshooting, and automation behavior.

## Table of Contents

1. [Initial Setup](#initial-setup)
2. [Daily Usage](#daily-usage)
3. [Available Scripts](#available-scripts)
4. [Automation Behavior](#automation-behavior)
5. [Manual Operations](#manual-operations)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Usage](#advanced-usage)

---

## Initial Setup

### Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- `jq` installed for JSON processing
- Bash shell (WSL2 compatible)

```bash
# Install prerequisites (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install gh jq

# Authenticate with GitHub
gh auth login
```

### Step 1: Create Project and Configure Fields

Run the setup script to create the project board and all custom fields:

```bash
./scripts/project-setup.sh --save-config
```

This will:
- ✅ Create "TTA Component Maturity Tracker" project (if not exists)
- ✅ Add all required custom fields:
  - Current Stage (single-select: Development, Staging, Production)
  - Target Stage (single-select: Staging, Production)
  - Functional Group (single-select: Core Infrastructure, AI/Agent Systems, Player Experience, Therapeutic Content)
  - Test Coverage (number)
  - Blocker Count (number)
  - Last Updated (date)
- ✅ Retrieve all project/field/option IDs
- ✅ Save configuration to `.github/project-config.env`
- ✅ Add `.github/project-config.env` to `.gitignore`

**Expected Output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Project Setup Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Project Information:
  Title: TTA Component Maturity Tracker
  Number: #1
  ID: PVT_kwHOChRix84...

Custom Fields:
  Current Stage:
    ID: PVTSSF_lAHOChRix84...
    Type: SINGLE_SELECT
    Options:
      - Development: abc123
      - Staging: def456
      - Production: ghi789
  ...
```

### Step 2: Configure GitHub Secrets (for CI/CD)

For automated workflows to work, configure GitHub repository secrets:

1. Go to: `https://github.com/theinterneti/TTA/settings/secrets/actions`
2. Add the following secrets (copy values from `.github/project-config.env`):

```
PROJECT_ID
PROJECT_NUMBER
FIELD_CURRENT_STAGE_ID
FIELD_TARGET_STAGE_ID
FIELD_BLOCKER_COUNT_ID
FIELD_TEST_COVERAGE_ID
FIELD_LAST_UPDATED_ID
FIELD_FUNCTIONAL_GROUP_ID
OPTION_DEVELOPMENT_ID
OPTION_STAGING_ID
OPTION_PRODUCTION_ID
OPTION_TARGET_STAGING_ID
OPTION_TARGET_PRODUCTION_ID
OPTION_CORE_INFRA_ID
OPTION_AI_AGENT_ID
OPTION_PLAYER_EXP_ID
OPTION_THERAPEUTIC_ID
```

3. Also add `GH_PROJECT_TOKEN` with a GitHub Personal Access Token that has:
   - `repo` scope
   - `project` scope
   - `write:org` scope (if using organization projects)

### Step 3: Validate Setup

```bash
./scripts/project-setup.sh --validate-only
```

**Expected Output:**
```
ℹ Validating setup...
✓ Validation passed
```

---

## Daily Usage

### Common Workflows

#### 1. Create Component Promotion Request

```bash
# Promote Model Management to Staging
./scripts/project-promote-component.sh "Model Management" Staging \
  --coverage 100 \
  --group AI \
  --blockers 0

# Promote Carbon to Production
./scripts/project-promote-component.sh "Carbon" Production \
  --coverage 95 \
  --group Core
```

This will:
- Create a promotion issue with proper title and body
- Add labels (`promotion:requested`, component labels)
- Add issue to project board
- Set initial field values
- Trigger automated validation workflow

#### 2. Add Existing Issue to Project

```bash
# Add issue #42 to project
./scripts/project-add-issue.sh 42

# Add with initial field values
./scripts/project-add-issue.sh 40 \
  --stage Development \
  --target Staging \
  --coverage 100 \
  --group AI
```

#### 3. Update Field Values

```bash
# Interactive mode (prompts for each field)
./scripts/project-update-fields.sh 42

# Non-interactive mode
./scripts/project-update-fields.sh 40 \
  --non-interactive \
  --stage Staging \
  --coverage 85 \
  --blockers 1
```

#### 4. View Project Status

```bash
# Show all items with summary
./scripts/project-status.sh

# Filter by stage
./scripts/project-status.sh --stage Development

# Filter by functional group
./scripts/project-status.sh --group AI

# Show summary only
./scripts/project-status.sh --summary-only

# Export to JSON
./scripts/project-status.sh --format json > status.json

# Export to CSV
./scripts/project-status.sh --format csv > status.csv
```

---

## Available Scripts

### `scripts/project-setup.sh`

**Purpose:** One-time setup of project board and fields

**Usage:**
```bash
./scripts/project-setup.sh [OPTIONS]

OPTIONS:
  -h, --help              Show help message
  -p, --project-number N  Use existing project number N
  -s, --save-config       Save configuration to .github/project-config.env
  -v, --validate-only     Only validate existing setup
  --dry-run               Show what would be done
```

**Examples:**
```bash
# First-time setup
./scripts/project-setup.sh --save-config

# Use existing project #1
./scripts/project-setup.sh --project-number 1 --save-config

# Validate setup
./scripts/project-setup.sh --validate-only
```

### `scripts/project-add-issue.sh`

**Purpose:** Add an issue to the project board with optional field values

**Usage:**
```bash
./scripts/project-add-issue.sh <issue_number> [OPTIONS]

OPTIONS:
  -h, --help              Show help message
  -s, --stage STAGE       Set Current Stage
  -t, --target TARGET     Set Target Stage
  -g, --group GROUP       Set Functional Group
  -c, --coverage NUM      Set Test Coverage (0-100)
  -b, --blockers NUM      Set Blocker Count
  --dry-run               Show what would be done
```

**Examples:**
```bash
# Add issue #42
./scripts/project-add-issue.sh 42

# Add with field values
./scripts/project-add-issue.sh 40 \
  --stage Development \
  --target Staging \
  --coverage 100 \
  --group AI
```

### `scripts/project-update-fields.sh`

**Purpose:** Update custom field values for a project item

**Usage:**
```bash
./scripts/project-update-fields.sh <issue_number> [OPTIONS]

OPTIONS:
  -h, --help              Show help message
  --non-interactive       Use CLI args instead of prompts
  -s, --stage STAGE       Set Current Stage
  -t, --target TARGET     Set Target Stage
  -g, --group GROUP       Set Functional Group
  -c, --coverage NUM      Set Test Coverage
  -b, --blockers NUM      Set Blocker Count
```

**Examples:**
```bash
# Interactive mode
./scripts/project-update-fields.sh 42

# Non-interactive mode
./scripts/project-update-fields.sh 40 \
  --non-interactive \
  --stage Staging \
  --coverage 85
```

### `scripts/project-status.sh`

**Purpose:** Display current project board status

**Usage:**
```bash
./scripts/project-status.sh [OPTIONS]

OPTIONS:
  -h, --help              Show help message
  -s, --stage STAGE       Filter by Current Stage
  -g, --group GROUP       Filter by Functional Group
  -f, --format FORMAT     Output format (table|json|csv)
  -l, --limit NUM         Limit items to display
  --summary-only          Show only summary statistics
```

**Examples:**
```bash
# Show all items
./scripts/project-status.sh

# Filter by stage
./scripts/project-status.sh --stage Development

# Export to JSON
./scripts/project-status.sh --format json > status.json
```

### `scripts/project-promote-component.sh`

**Purpose:** Create promotion request and add to project board

**Usage:**
```bash
./scripts/project-promote-component.sh <component_name> <target_stage> [OPTIONS]

OPTIONS:
  -h, --help              Show help message
  -c, --coverage NUM      Current test coverage
  -b, --blockers NUM      Number of blockers
  -g, --group GROUP       Functional group
  --dry-run               Show what would be created
```

**Examples:**
```bash
# Promote to Staging
./scripts/project-promote-component.sh "Model Management" Staging \
  --coverage 100 \
  --group AI

# Promote to Production
./scripts/project-promote-component.sh "Carbon" Production \
  --coverage 95 \
  --group Core
```

---

## Automation Behavior

### Automated Operations

The following operations happen automatically via GitHub Actions:

#### 1. **Issue Added to Project** (on label `promotion:requested`)
- **Trigger:** Issue labeled with `promotion:requested`
- **Workflow:** `.github/workflows/project-board-automation.yml`
- **Actions:**
  - Add issue to project board
  - Comment on issue confirming addition
  - Trigger validation workflow

#### 2. **Field Updates on Validation** (on label `promotion:validated` or `promotion:blocked`)
- **Trigger:** Issue labeled with `promotion:validated` or `promotion:blocked`
- **Workflow:** `.github/workflows/project-board-automation.yml`
- **Actions:**
  - Parse issue title for component and stages
  - Extract test coverage from validation comments
  - Update project board fields

#### 3. **Promotion Approval** (on label `promotion:approved`)
- **Trigger:** Issue labeled with `promotion:approved`
- **Workflow:** `.github/workflows/project-board-automation.yml`
- **Actions:**
  - Comment on issue with next steps
  - Update project board status

#### 4. **Promotion Completion** (on label `promotion:completed`)
- **Trigger:** Issue labeled with `promotion:completed`
- **Workflow:** `.github/workflows/project-board-automation.yml`
- **Actions:**
  - Update Current Stage to Target Stage
  - Clear Target Stage
  - Close promotion issue
  - Comment on issue confirming completion

#### 5. **Blocker Count Updates** (on blocker issue changes)
- **Trigger:** Issue with `blocker:*` label opened/closed/labeled
- **Workflow:** `.github/workflows/project-board-automation.yml`
- **Actions:**
  - Find related promotion issue
  - Count open blocker issues
  - Update Blocker Count field

### Workflow Files

- **`.github/workflows/update-project-board.yml`** - Reusable workflow for all project updates
- **`.github/workflows/project-board-automation.yml`** - Event-driven automation triggers
- **`.github/workflows/component-promotion-validation.yml`** - Validation workflow (calls update-project-board.yml)

---

## Manual Operations

The following operations require manual intervention:

### 1. **Initial Project Creation**
- Run `./scripts/project-setup.sh --save-config` once

### 2. **GitHub Secrets Configuration**
- Manually add secrets to repository settings (one-time)

### 3. **Stakeholder Approval**
- Review promotion requests
- Add `promotion:approved` label manually

### 4. **Deployment Execution**
- Deploy to staging/production environments
- Add `promotion:completed` label after successful deployment

### 5. **Project Board Views/Columns**
- Customize project board layout in GitHub UI
- Create custom views and filters

---

## Troubleshooting

### Common Issues

#### Issue: "Configuration file not found"
**Error:**
```
✗ Configuration file not found: .github/project-config.env
Run: scripts/project-setup.sh --save-config
```

**Solution:**
```bash
./scripts/project-setup.sh --save-config
```

#### Issue: "Issue not found in project"
**Error:**
```
✗ Issue #42 not found in project
Add it first with: scripts/project-add-issue.sh 42
```

**Solution:**
```bash
./scripts/project-add-issue.sh 42
```

#### Issue: "Failed to create field - already exists"
**Behavior:** Script shows warning but continues

**Explanation:** This is normal - the script is idempotent and skips existing fields

#### Issue: GitHub Actions workflow not triggering
**Checklist:**
1. Verify `GH_PROJECT_TOKEN` secret is configured
2. Check workflow file syntax: `.github/workflows/project-board-automation.yml`
3. Verify issue has correct label (e.g., `promotion:requested`)
4. Check Actions tab for error messages

#### Issue: Field values not updating
**Checklist:**
1. Verify `.github/project-config.env` has correct IDs
2. Check GitHub Secrets match local config
3. Verify issue is in project board
4. Check workflow logs for errors

### Debug Mode

Enable debug output in scripts:

```bash
# Add to script or run with bash -x
bash -x ./scripts/project-status.sh
```

### Validate Configuration

```bash
# Check local config
cat .github/project-config.env

# Validate project setup
./scripts/project-setup.sh --validate-only

# Check project status
./scripts/project-status.sh --summary-only
```

---

## Advanced Usage

### Custom Field Queries

Query project data directly with GraphQL:

```bash
gh api graphql -f query='
  query {
    user(login: "theinterneti") {
      projectV2(number: 1) {
        items(first: 10) {
          nodes {
            content {
              ... on Issue {
                number
                title
              }
            }
          }
        }
      }
    }
  }
'
```

### Batch Operations

Update multiple issues:

```bash
# Add multiple issues to project
for issue in 40 41 42; do
  ./scripts/project-add-issue.sh $issue --stage Development
done
```

### Integration with Other Tools

Export project data for analysis:

```bash
# Export to JSON for processing
./scripts/project-status.sh --format json | jq '.[] | select(.test_coverage < 70)'

# Export to CSV for spreadsheet
./scripts/project-status.sh --format csv > project-export.csv
```

### CI/CD Integration

Use scripts in CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Update project board
  run: |
    ./scripts/project-add-issue.sh ${{ github.event.issue.number }} \
      --stage Development \
      --coverage ${{ steps.coverage.outputs.percentage }}
```

---

## Summary

### What's Automated ✅
- Issue addition to project board
- Field updates based on validation results
- Blocker count tracking
- Promotion workflow state transitions
- Last Updated timestamp

### What's Manual ⚠️
- Initial project setup (one-time)
- GitHub Secrets configuration (one-time)
- Stakeholder approval decisions
- Deployment execution
- Custom view/column configuration

### Key Benefits 🎯
- **Zero manual UI interaction** for routine operations
- **Idempotent scripts** - safe to run multiple times
- **WSL2 compatible** - works in solo developer environment
- **Comprehensive automation** - minimal manual intervention
- **Easy troubleshooting** - clear error messages and validation

---

For more information, see:
- [Component Maturity Workflow](./COMPONENT_MATURITY_WORKFLOW.md)
- [Component Promotion Guide](./COMPONENT_PROMOTION_GUIDE.md)
- [GitHub Projects V2 Documentation](https://docs.github.com/en/issues/planning-and-tracking-with-projects)


---
**Logseq:** [[TTA.dev/Docs/Development/Github_project_automation]]
