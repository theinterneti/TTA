# GitHub Scripts

This directory contains automation scripts for managing GitHub repository configuration.

## Branch Protection Configuration

### Quick Start

```bash
# Make script executable
chmod +x .github/scripts/configure-branch-protection.sh

# Run the script
.github/scripts/configure-branch-protection.sh
```

### What It Does

The `configure-branch-protection.sh` script configures branch protection rules optimized for solo developer workflow:

**Main Branch Protection:**
- ✅ Requires status checks (unit, integration) to pass
- ✅ Requires 1 approval (can self-approve or use auto-merge)
- ✅ Prevents force pushes
- ✅ Enforces linear history
- ✅ Allows admin bypass for emergencies
- ✅ Auto-deletes branches after merge

**Develop Branch Protection (if exists):**
- ✅ Requires unit tests only
- ✅ No approval required
- ✅ More flexible for experimentation

### Prerequisites

1. **GitHub CLI installed:**
   ```bash
   # macOS
   brew install gh

   # Linux
   curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
   sudo apt update
   sudo apt install gh

   # Windows
   winget install --id GitHub.cli
   ```

2. **Authenticate with GitHub:**
   ```bash
   gh auth login
   ```

### Manual Configuration

If you prefer to configure manually via GitHub web UI:

1. Go to: https://github.com/theinterneti/TTA/settings/branches
2. Click "Add branch protection rule"
3. Branch name pattern: `main`
4. Configure settings:
   - ✅ Require a pull request before merging
   - ✅ Require approvals: 1
   - ✅ Dismiss stale pull request approvals when new commits are pushed
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - Status checks: `unit`, `integration`
   - ✅ Require conversation resolution before merging
   - ✅ Require linear history
   - ✅ Do not allow bypassing the above settings (uncheck for admin bypass)
   - ❌ Allow force pushes (keep unchecked)
   - ❌ Allow deletions (keep unchecked)
5. Click "Create" or "Save changes"

### Verification

After configuration, verify the protection rules:

```bash
# View main branch protection
gh api /repos/theinterneti/TTA/branches/main/protection

# Test with a sample PR
# 1. Create a feature branch
# 2. Make a change and push
# 3. Create PR to main
# 4. Verify status checks are required
# 5. Verify approval is required
```

### Updating Status Checks

As new workflows are added, update the required status checks:

```bash
# Add a new required status check
gh api --method PUT \
  -H "Accept: application/vnd.github+json" \
  "/repos/theinterneti/TTA/branches/main/protection" \
  -f required_status_checks[strict]=true \
  -f "required_status_checks[contexts][]=unit" \
  -f "required_status_checks[contexts][]=integration" \
  -f "required_status_checks[contexts][]=code-quality / Lint and Format"
```

### Troubleshooting

**Error: "Branch not protected"**
- The branch protection hasn't been configured yet
- Run the configuration script

**Error: "Resource not accessible by integration"**
- You don't have admin permissions on the repository
- Contact repository owner

**Error: "Validation failed: Contexts must be an array"**
- Check the JSON syntax in the API call
- Ensure contexts are properly formatted

**Status checks not appearing:**
- Ensure the workflow has run at least once
- Check workflow names match exactly
- Verify workflow is not disabled

### Evolution Plan

The branch protection will evolve as workflows are added:

**Phase 1 (Current):**
- `unit`
- `integration`

**Phase 2 (After code-quality.yml):**
- `code-quality / Lint and Format`
- `code-quality / Type Check`

**Phase 3 (After security fixes):**
- `security-scan / Security Scan`

**Phase 4 (After docker-build.yml):**
- `docker-build / Build and Validate`

**Phase 5 (Full protection):**
- `e2e-tests / E2E Tests (chromium - auth)`
- `e2e-tests / E2E Tests (chromium - dashboard)`

### Related Documentation

- [Branch Protection Configuration](../repository-config/branch-protection-solo-dev.yml) - Detailed configuration
- [GitHub Branch Protection Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [GitHub CLI Docs](https://cli.github.com/manual/)

### Support

For issues or questions:
1. Check the troubleshooting section above
2. Review GitHub's branch protection documentation
3. Create an issue in the repository
