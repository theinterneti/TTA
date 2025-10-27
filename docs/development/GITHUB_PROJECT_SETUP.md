# GitHub Project Setup Guide: TTA Component Maturity Tracker

## Overview

This guide provides step-by-step instructions for creating the "TTA Component Maturity Tracker" GitHub Project board.

**Note**: GitHub Projects (new version) must be created via the GitHub web UI. The classic Projects API has been deprecated.

---

## Prerequisites

- Admin access to the TTA repository
- GitHub account with Projects access

---

## Step 1: Create the Project

1. Navigate to https://github.com/theinterneti/TTA
2. Click on the **"Projects"** tab
3. Click **"New project"** (green button)
4. Select **"Start from scratch"**
5. Enter project details:
   - **Project name**: `TTA Component Maturity Tracker`
   - **Description**: `Track component maturity progression through Development → Staging → Production stages`
   - **Visibility**: `Private` (or `Public` if you want it visible to all)
6. Click **"Create project"**

---

## Step 2: Configure Board View (Default)

The Board view is created by default. Configure the columns:

1. Click on the **"Board"** tab (should be selected by default)
2. Rename/create columns:
   - **Column 1**: `📋 Backlog` (rename "Todo")
   - **Column 2**: `🔨 Development` (rename "In Progress")
   - **Column 3**: `🧪 Staging` (add new column)
   - **Column 4**: `🚀 Production` (add new column)
   - **Column 5**: `🔒 Archived` (rename "Done")

3. To add a new column:
   - Click **"+ Add column"** on the right
   - Enter column name
   - Click **"Save"**

4. To rename a column:
   - Click the **"⋯"** menu on the column header
   - Select **"Rename"**
   - Enter new name
   - Click **"Save"**

---

## Step 3: Add Custom Fields

1. Click on the **"⋯"** menu in the top-right corner
2. Select **"Settings"**
3. Scroll to **"Custom fields"** section
4. Click **"+ New field"** for each field below:

### Field 1: Functional Group
- **Field name**: `Functional Group`
- **Field type**: `Single select`
- **Options**:
  - `Core Infrastructure` (color: green)
  - `AI/Agent Systems` (color: purple)
  - `Player Experience` (color: orange)
  - `Therapeutic Content` (color: blue)
  - `Monitoring & Operations` (color: teal)

### Field 2: Current Stage
- **Field name**: `Current Stage`
- **Field type**: `Single select`
- **Options**:
  - `Backlog` (color: gray)
  - `Development` (color: yellow)
  - `Staging` (color: blue)
  - `Production` (color: green)
  - `Archived` (color: red)

### Field 3: Target Stage
- **Field name**: `Target Stage`
- **Field type**: `Single select`
- **Options**:
  - `Development` (color: yellow)
  - `Staging` (color: blue)
  - `Production` (color: green)
  - `N/A` (color: gray)

### Field 4: Promotion Blocker Count
- **Field name**: `Promotion Blocker Count`
- **Field type**: `Number`

### Field 5: Test Coverage
- **Field name**: `Test Coverage`
- **Field type**: `Number`
- **Note**: Enter as percentage (e.g., 85 for 85%)

### Field 6: Last Updated
- **Field name**: `Last Updated`
- **Field type**: `Date`

### Field 7: Owner
- **Field name**: `Owner`
- **Field type**: `People`

### Field 8: Priority
- **Field name**: `Priority`
- **Field type**: `Single select`
- **Options**:
  - `Critical` (color: red)
  - `High` (color: orange)
  - `Medium` (color: yellow)
  - `Low` (color: gray)

### Field 9: Dependencies
- **Field name**: `Dependencies`
- **Field type**: `Text`

---

## Step 4: Create Table View

1. Click **"+ New view"** in the top-left
2. Select **"Table"** layout
3. Name it: `Table View`
4. Click **"Create"**

The table view will automatically show all custom fields. You can:
- Reorder columns by dragging column headers
- Sort by clicking column headers
- Filter using the filter button
- Group by any field

**Recommended column order:**
1. Title (Component Name)
2. Functional Group
3. Current Stage
4. Target Stage
5. Promotion Blocker Count
6. Test Coverage
7. Priority
8. Owner
9. Last Updated
10. Dependencies

---

## Step 5: Create Roadmap View

1. Click **"+ New view"** in the top-left
2. Select **"Roadmap"** layout
3. Name it: `Roadmap View`
4. Click **"Create"**

Configure the roadmap:
1. Click **"⋯"** menu on the view
2. Select **"Settings"**
3. Configure:
   - **Date field**: Use `Last Updated` or create a new `Target Date` field
   - **Group by**: `Functional Group` or `Current Stage`
   - **Zoom level**: `Months` or `Quarters`

---

## Step 6: Configure Automation (Optional)

GitHub Projects supports workflow automation:

1. Click **"⋯"** menu in top-right
2. Select **"Workflows"**
3. Enable built-in workflows:
   - **Auto-add to project**: Automatically add issues with specific labels
   - **Auto-archive items**: Archive items when closed
   - **Item closed**: Move to "Archived" column when closed

**Recommended automation:**
- **When**: Issue is labeled with `promotion:requested`
- **Then**: Add to project in "Development" or "Staging" column

---

## Step 7: Link Repository

1. In project settings, scroll to **"Manage access"**
2. Ensure the TTA repository is linked
3. This allows issues and PRs to be added to the project

---

## Step 8: Initial Setup Verification

Verify your project has:
- ✅ 5 columns in Board view (Backlog, Development, Staging, Production, Archived)
- ✅ 9 custom fields (Functional Group, Current Stage, Target Stage, Promotion Blocker Count, Test Coverage, Last Updated, Owner, Priority, Dependencies)
- ✅ Table view created
- ✅ Roadmap view created
- ✅ Automation configured (optional)

---

## Next Steps

After creating the project:
1. Create issue templates (Phase 2)
2. Create documentation (Phase 2)
3. Add components to the project (Phase 3)
4. Create promotion milestones (Phase 3)

---

## Troubleshooting

### Can't find Projects tab
- Ensure you have admin access to the repository
- Projects may be disabled in repository settings

### Custom fields not showing
- Refresh the page
- Check that you're in the correct project

### Automation not working
- Verify repository is linked to project
- Check workflow configuration
- Ensure labels exist in repository

---

## Reference

- [GitHub Projects Documentation](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [GitHub Projects Automation](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project)
