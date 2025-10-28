# OpenHands GitHub Integration - Setup Checklist

Use this checklist to set up the OpenHands GitHub integration for the TTA repository.

## Prerequisites

- [ ] You have admin access to the TTA GitHub repository
- [ ] You have an OpenRouter account with API key
- [ ] You have your OpenRouter API key from `.env` file

## Setup Steps

### 1. Create GitHub Personal Access Token (PAT)

- [ ] Go to https://github.com/settings/tokens/new
- [ ] Set token name: `OpenHands TTA Integration`
- [ ] Set expiration: 90 days (or custom)
- [ ] Select scopes:
  - [ ] ✅ `repo` (Full control of private repositories)
  - [ ] ✅ `workflow` (Update GitHub Action workflows)
- [ ] Click "Generate token"
- [ ] **Copy the token immediately** (save it somewhere safe temporarily)

### 2. Add GitHub Secrets

- [ ] Go to https://github.com/theinterneti/TTA/settings/secrets/actions
- [ ] Click "New repository secret"
- [ ] Add `OPENROUTER_API_KEY`:
  - [ ] Name: `OPENROUTER_API_KEY`
  - [ ] Value: Copy from your `.env` file (the value after `OPENROUTER_API_KEY=`)
  - [ ] Click "Add secret"
- [ ] Add `PAT_TOKEN`:
  - [ ] Click "New repository secret"
  - [ ] Name: `PAT_TOKEN`
  - [ ] Value: Paste the GitHub PAT you created in step 1
  - [ ] Click "Add secret"
- [ ] Add `PAT_USERNAME`:
  - [ ] Click "New repository secret"
  - [ ] Name: `PAT_USERNAME`
  - [ ] Value: `theinterneti`
  - [ ] Click "Add secret"

### 3. Verify Secrets Are Set

- [ ] Go to https://github.com/theinterneti/TTA/settings/secrets/actions
- [ ] Confirm you see three secrets:
  - [ ] `OPENROUTER_API_KEY`
  - [ ] `PAT_TOKEN`
  - [ ] `PAT_USERNAME`

### 4. Commit and Push Workflow Files

- [ ] Verify you're on the `feature/openhands-github-integration` branch
- [ ] Check files exist:
  - [ ] `.github/workflows/openhands-resolver.yml`
  - [ ] `docs/openhands/GITHUB_INTEGRATION.md`
  - [ ] `docs/openhands/SETUP_CHECKLIST.md`
  - [ ] `docs/openhands/TEST_ISSUE_EXAMPLE.md`
  - [ ] `.github/ISSUE_TEMPLATE/openhands-task.md`
- [ ] Commit the files:
  ```bash
  git add .github/workflows/openhands-resolver.yml
  git add docs/openhands/GITHUB_INTEGRATION.md
  git add docs/openhands/SETUP_CHECKLIST.md
  git add docs/openhands/TEST_ISSUE_EXAMPLE.md
  git add .github/ISSUE_TEMPLATE/openhands-task.md
  git commit -m "feat: Add OpenHands GitHub integration workflow and documentation"
  ```
- [ ] Push to GitHub:
  ```bash
  git push -u origin feature/openhands-github-integration
  ```

### 5. Create Pull Request

- [ ] Go to https://github.com/theinterneti/TTA/pulls
- [ ] Click "New pull request"
- [ ] Set base: `main` (or your default branch)
- [ ] Set compare: `feature/openhands-github-integration`
- [ ] Title: `feat: Add OpenHands GitHub integration for async development tasks`
- [ ] Description:
  ```markdown
  ## Summary

  Adds OpenHands GitHub integration to enable async development task execution using free LLM models.

  ## Changes

  - Added GitHub Actions workflow (`.github/workflows/openhands-resolver.yml`)
  - Added comprehensive documentation (`docs/openhands/GITHUB_INTEGRATION.md`)
  - Added setup checklist (`docs/openhands/SETUP_CHECKLIST.md`)
  - Added test issue example (`docs/openhands/TEST_ISSUE_EXAMPLE.md`)
  - Added issue template for OpenHands tasks

  ## How to Use

  1. Create or comment on a GitHub issue
  2. Mention `@openhands-agent` with task description
  3. OpenHands runs asynchronously and creates a PR
  4. Review and merge the PR

  ## Testing

  Follow the test issue example in `docs/openhands/TEST_ISSUE_EXAMPLE.md` to verify the integration works.

  ## Documentation

  See `docs/openhands/GITHUB_INTEGRATION.md` for complete usage guide.
  ```
- [ ] Click "Create pull request"
- [ ] **Do NOT merge yet** - test first!

### 6. Test the Integration

- [ ] Follow the test issue example in `docs/openhands/TEST_ISSUE_EXAMPLE.md`
- [ ] Create a test issue
- [ ] Comment with `@openhands-agent` to trigger workflow
- [ ] Verify workflow runs successfully
- [ ] Verify OpenHands creates a PR
- [ ] Review the PR and verify it contains expected changes

### 7. Merge and Deploy

- [ ] If test is successful, merge the PR from step 5
- [ ] Delete the test issue and PR (if you don't want to keep them)
- [ ] Start using OpenHands for real development tasks!

## Verification

After completing all steps, verify:

- [ ] GitHub Secrets are configured (3 secrets)
- [ ] Workflow file is in the repository
- [ ] Documentation is accessible
- [ ] Test issue triggers workflow successfully
- [ ] OpenHands creates PR with expected content

## Troubleshooting

If something doesn't work, check:

1. **Secrets Configuration**:
   - All three secrets exist
   - Values are correct (no extra spaces)
   - PAT has correct permissions

2. **Workflow File**:
   - File is committed to repository
   - File is in correct location (`.github/workflows/`)
   - YAML syntax is valid

3. **GitHub Actions**:
   - Actions are enabled for repository
   - Workflow has correct permissions
   - No rate limits on GitHub Actions

4. **OpenRouter API**:
   - API key is valid
   - Account has credits/quota
   - Free model is available

## Getting Help

If you encounter issues:

1. Check workflow logs in GitHub Actions
2. Review `docs/openhands/GITHUB_INTEGRATION.md` troubleshooting section
3. Check OpenHands documentation: https://docs.all-hands.dev
4. Create an issue in the TTA repository

## Next Steps

After successful setup:

1. **Document your workflow** - Add notes about how you use OpenHands
2. **Share with team** - If working with others, share this guide
3. **Monitor usage** - Track OpenRouter API usage and costs
4. **Iterate** - Improve task descriptions based on results
5. **Expand** - Consider adding more triggers (labels, PR comments)

---

**Estimated Setup Time**: 15-20 minutes

**Last Updated**: 2025-10-28
**Status**: Setup Guide for POC
