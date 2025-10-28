# OpenHands GitHub Integration - Quick Start Guide

## ✅ Automated Steps (Completed)

The following steps have been completed automatically using GitHub CLI:

1. ✅ **Branch pushed** to GitHub: `feature/openhands-github-integration`
2. ✅ **Pull Request created**: PR #99
   - **URL**: https://github.com/theinterneti/TTA/pull/99
   - **Title**: feat: Add OpenHands GitHub integration for async development tasks
   - **Status**: Open (ready for review)
   - **Base**: `main` ← **Head**: `feature/openhands-github-integration`

## ⏳ Manual Steps Required

You need to complete these steps manually before testing the integration:

### Step 1: Configure GitHub Secrets (Required)

You must add **three secrets** to your GitHub repository. These secrets are required for the OpenHands workflow to authenticate and function properly.

#### **A. Navigate to Secrets Configuration Page**

**Open this URL in your browser:**
```
https://github.com/theinterneti/TTA/settings/secrets/actions
```

You should see the "Actions secrets and variables" page.

---

#### **B. Add Secret #1: OPENROUTER_API_KEY**

1. Click **"New repository secret"** button
2. Fill in the form:
   - **Name**: `OPENROUTER_API_KEY`
   - **Secret**: 
     - Open your `.env` file in the TTA repository
     - Find the line: `OPENROUTER_API_KEY=sk-or-v1-...`
     - Copy everything **after** the `=` sign (the `sk-or-v1-...` part)
     - Paste it in the "Secret" field
3. Click **"Add secret"**

**Example:**
```bash
# In your .env file:
OPENROUTER_API_KEY=sk-or-v1-abc123xyz789...

# Copy this part: sk-or-v1-abc123xyz789...
```

---

#### **C. Add Secret #2: PAT_TOKEN**

This requires creating a GitHub Personal Access Token first.

**Step C.1: Create GitHub Personal Access Token**

1. **Open this URL in a new browser tab:**
   ```
   https://github.com/settings/tokens/new
   ```

2. **Fill in the token creation form:**
   - **Note**: `OpenHands TTA Integration`
   - **Expiration**: Select `90 days` (recommended)
     - Or choose `Custom` if you prefer a different duration

3. **Select scopes** (scroll down to find these checkboxes):
   - ✅ **`repo`** - Full control of private repositories
     - This will automatically check all sub-items under `repo`
   - ✅ **`workflow`** - Update GitHub Action workflows

4. **Scroll to bottom** and click **"Generate token"**

5. **⚠️ CRITICAL**: Copy the token **immediately**!
   - The token looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - **You will NOT be able to see it again!**
   - Save it temporarily in a secure location (text file, password manager, etc.)

**Step C.2: Add PAT as Secret**

1. Go back to: https://github.com/theinterneti/TTA/settings/secrets/actions
2. Click **"New repository secret"**
3. Fill in the form:
   - **Name**: `PAT_TOKEN`
   - **Secret**: Paste the token you just created (the `ghp_xxx...` value)
4. Click **"Add secret"**

---

#### **D. Add Secret #3: PAT_USERNAME**

1. Click **"New repository secret"**
2. Fill in the form:
   - **Name**: `PAT_USERNAME`
   - **Secret**: `theinterneti` (your GitHub username)
3. Click **"Add secret"**

---

#### **E. Verify All Secrets Are Configured**

1. Go to: https://github.com/theinterneti/TTA/settings/secrets/actions
2. You should see **exactly three secrets** listed:
   - `OPENROUTER_API_KEY`
   - `PAT_TOKEN`
   - `PAT_USERNAME`

✅ **Secrets configuration complete!**

---

### Step 2: Test the Integration (Automated Script)

After configuring the secrets, run the automated test script:

```bash
bash scripts/create_openhands_test_issue.sh
```

**What this script does:**
1. Creates a test issue with title: `[TEST] OpenHands Integration Verification`
2. Adds a comment with `@openhands-agent` to trigger the workflow
3. Provides links to monitor progress

**Expected output:**
```
🤖 Creating OpenHands test issue...
✅ Test issue created: https://github.com/theinterneti/TTA/issues/XXX
📝 Issue number: #XXX
⏳ Waiting 3 seconds before adding comment...
🚀 Triggering OpenHands workflow...
✅ OpenHands workflow triggered!

📊 Next steps:
  1. Check workflow status: https://github.com/theinterneti/TTA/actions
  2. Monitor issue comments: https://github.com/theinterneti/TTA/issues/XXX
  3. Watch for PR creation: https://github.com/theinterneti/TTA/pulls
```

---

### Step 3: Monitor Test Progress

#### **A. Check GitHub Actions Workflow**

1. **Go to**: https://github.com/theinterneti/TTA/actions
2. **Look for**: "OpenHands Issue Resolver" workflow (should start within 10-30 seconds)
3. **Click on the workflow** to see real-time logs
4. **Wait for completion** (typically 2-5 minutes)

**Using GitHub CLI:**
```bash
# List recent workflow runs
gh run list --workflow=openhands-resolver.yml --limit 5

# View specific run logs
gh run view <run-id> --log
```

#### **B. Check Issue Comments**

1. The test issue will receive status updates from OpenHands
2. Look for:
   - ✅ Success message: "OpenHands has completed processing this issue"
   - ❌ Error message: "OpenHands encountered an error"

#### **C. Check for Pull Request**

1. **Go to**: https://github.com/theinterneti/TTA/pulls
2. **Look for**: A new PR created by OpenHands
3. **PR should**:
   - Reference the test issue number
   - Contain a file `openhands-test.txt`
   - Have the correct file content

**Using GitHub CLI:**
```bash
# List recent PRs
gh pr list --limit 5

# View specific PR
gh pr view <pr-number>
```

---

### Step 4: Verify Test Results

#### **Success Criteria**

✅ **Test is successful if:**
1. GitHub Actions workflow completed without errors
2. OpenHands posted a success comment on the test issue
3. A new PR was created by OpenHands
4. The PR contains `openhands-test.txt` with correct content

#### **What to Do After Successful Test**

1. **Review the test PR**:
   ```bash
   gh pr view <test-pr-number>
   gh pr diff <test-pr-number>
   ```

2. **Close the test PR** (don't merge it):
   ```bash
   gh pr close <test-pr-number> --comment "Test successful. Closing test PR."
   ```

3. **Close the test issue**:
   ```bash
   gh issue close <test-issue-number> --comment "Integration test successful!"
   ```

4. **Merge the integration PR** (PR #99):
   ```bash
   gh pr merge 99 --squash --delete-branch
   ```

5. **Start using OpenHands** for real development tasks!

---

### Step 5: Start Using OpenHands

Once the integration is verified and PR #99 is merged, you can start using OpenHands:

#### **Basic Usage**

1. Create or open a GitHub issue
2. Add a comment: `@openhands-agent [task description]`
3. Wait for OpenHands to create a PR
4. Review and merge the PR

#### **Example Tasks**

**Generate Tests:**
```
@openhands-agent Please generate comprehensive unit tests for src/agent_orchestration/circuit_breaker.py with 100% coverage
```

**Add Type Hints:**
```
@openhands-agent Please add type hints to all functions in src/utils/helpers.py
```

**Refactor Code:**
```
@openhands-agent Please refactor the authentication module to use dependency injection pattern
```

**Create Documentation:**
```
@openhands-agent Please generate API documentation for all endpoints in src/api/routes.py
```

---

## Troubleshooting

### Workflow Doesn't Start

**Symptoms**: No workflow appears in GitHub Actions after commenting `@openhands-agent`

**Solutions**:
1. Verify PR #99 is merged (workflow file must be in `main` branch)
2. Check comment syntax is exactly `@openhands-agent` (case-sensitive)
3. Ensure you're commenting on an **issue** (not a PR or discussion)
4. Verify GitHub Actions is enabled: https://github.com/theinterneti/TTA/settings/actions

### Workflow Fails with Authentication Error

**Symptoms**: Workflow fails with "401 Unauthorized" or "Authentication failed"

**Solutions**:
1. Verify all three secrets are set correctly
2. Check PAT hasn't expired: https://github.com/settings/tokens
3. Ensure PAT has `repo` and `workflow` scopes
4. Regenerate PAT if needed and update `PAT_TOKEN` secret

### Workflow Fails with API Error

**Symptoms**: Workflow fails with "API key invalid" or "Rate limit exceeded"

**Solutions**:
1. Verify `OPENROUTER_API_KEY` is correct
2. Check OpenRouter account: https://openrouter.ai/keys
3. Verify API key is active and has credits
4. Try again after a few minutes (rate limit)

### No PR Created

**Symptoms**: Workflow completes but no PR appears

**Solutions**:
1. Check workflow logs for errors
2. Verify task description was clear enough
3. Try a simpler task (e.g., create a text file)
4. Check if OpenHands posted error in issue comments

---

## Quick Reference

### URLs

- **PR #99**: https://github.com/theinterneti/TTA/pull/99
- **Secrets Config**: https://github.com/theinterneti/TTA/settings/secrets/actions
- **Create PAT**: https://github.com/settings/tokens/new
- **GitHub Actions**: https://github.com/theinterneti/TTA/actions
- **Issues**: https://github.com/theinterneti/TTA/issues
- **Pull Requests**: https://github.com/theinterneti/TTA/pulls

### Commands

```bash
# Create test issue (automated)
bash scripts/create_openhands_test_issue.sh

# Monitor workflow runs
gh run list --workflow=openhands-resolver.yml --limit 5
gh run view <run-id> --log

# Check PRs
gh pr list --limit 5
gh pr view <pr-number>

# Merge integration PR after successful test
gh pr merge 99 --squash --delete-branch
```

---

**Last Updated**: 2025-10-28
**Status**: Ready for secrets configuration and testing

