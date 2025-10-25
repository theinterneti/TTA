---
type: "agent_requested"
description: "Use GitHub API for repository operations, issue management, and CI/CD integration"
---

# Use GitHub for Repository Operations and CI/CD Integration

## Rule Priority
**HIGH** - Apply when working with GitHub repositories, issues, PRs, or CI/CD workflows

## When to Use GitHub Tools

Prefer GitHub API for repository operations:

### 1. Issue Management
- **Use**: `github-api` with `/repos/{owner}/{repo}/issues` path
- **When**: Creating, updating, or querying issues
- **Example**: Creating issues for bugs, querying open issues, updating issue status

### 2. Pull Request Operations
- **Use**: `github-api` with `/repos/{owner}/{repo}/pulls` path
- **When**: Creating, reviewing, or merging pull requests
- **Example**: Creating PRs for feature branches, checking PR status, merging approved PRs

### 3. Commit History
- **Use**: `github-api` with `/repos/{owner}/{repo}/commits` or `/search/commits` path
- **When**: Searching commits, checking commit history
- **Example**: Finding commits by author, searching commit messages, checking commit details

### 4. Repository Data
- **Use**: `github-api` with `/repos/{owner}/{repo}` path
- **When**: Querying repository information
- **Example**: Getting repository details, checking stars/forks, listing branches

### 5. CI/CD Status
- **Use**: `github-api` with `/repos/{owner}/{repo}/commits/{sha}/check-runs` or `/commits/{sha}/status` path
- **When**: Checking workflow runs, test results, CI status
- **Example**: Verifying tests passed, checking deployment status, monitoring CI failures

### 6. Release Management
- **Use**: `github-api` with `/repos/{owner}/{repo}/releases` path
- **When**: Creating or managing releases
- **Example**: Creating release tags, publishing releases, listing release assets

## Benefits

- **Integrated Workflow**: Direct access to GitHub resources without leaving agent context
- **Structured Data**: Returns parsed JSON data, not raw HTML
- **Authentication Handled**: Uses configured GitHub credentials automatically
- **Rate Limit Aware**: Respects GitHub API rate limits
- **Comprehensive API**: Access to all GitHub API endpoints

## Concrete Examples

### Example 1: List Issues and PRs for Current Repository

```python
# List open issues (limited to current repo)
github-api(
    path="/repos/theinterneti/TTA/issues",
    method="GET",
    data={"state": "open", "per_page": 10},
    summary="List open issues in TTA repository"
)

# List PRs using is:pr filter
github-api(
    path="/repos/theinterneti/TTA/issues",
    method="GET",
    data={"q": "is:pr", "state": "open"},
    summary="List open pull requests"
)

# List my assigned issues
github-api(
    path="/repos/theinterneti/TTA/issues",
    method="GET",
    data={"assignee": "theinterneti", "state": "open"},
    summary="List my assigned issues"
)
```

### Example 2: Create Pull Request

```python
# Create PR for feature branch
github-api(
    path="/repos/theinterneti/TTA/pulls",
    method="POST",
    data={
        "title": "Add narrative branching feature",
        "body": "Implements narrative branching with Neo4j graph storage",
        "head": "feature/narrative-branching",
        "base": "main"
    },
    summary="Create PR for narrative branching feature"
)
```

### Example 3: Check CI Status for Commit

```python
# Check CI status using check-runs (more detailed)
github-api(
    path="/repos/theinterneti/TTA/commits/abc123/check-runs",
    method="GET",
    summary="Check CI status for commit abc123"
)

# Check CI status using status (covers more CIs)
github-api(
    path="/repos/theinterneti/TTA/commits/abc123/status",
    method="GET",
    summary="Check overall CI status for commit abc123"
)
```

### Example 4: Search Code and Commits

```python
# Search code in repository
github-api(
    path="/search/code",
    method="GET",
    data={"q": "AgentOrchestrator repo:theinterneti/TTA"},
    summary="Search for AgentOrchestrator in TTA repository"
)

# Search commits by author
github-api(
    path="/search/commits",
    method="GET",
    data={"q": "author:theinterneti repo:theinterneti/TTA"},
    summary="Search commits by theinterneti"
)

# Search commits by message
github-api(
    path="/search/commits",
    method="GET",
    data={"q": "fix bug repo:theinterneti/TTA"},
    summary="Search commits with 'fix bug' in message"
)
```

### Example 5: Manage Releases

```python
# List releases
github-api(
    path="/repos/theinterneti/TTA/releases",
    method="GET",
    summary="List all releases"
)

# Create new release
github-api(
    path="/repos/theinterneti/TTA/releases",
    method="POST",
    data={
        "tag_name": "v1.0.0",
        "name": "TTA v1.0.0",
        "body": "First stable release with narrative engine and agent orchestration",
        "draft": False,
        "prerelease": False
    },
    summary="Create v1.0.0 release"
)
```

## When NOT to Use GitHub API

**Use our workflow tools instead:**

1. **Git operations** - Use git-workflow.sh
   ```bash
   # ✅ Interactive workflow
   ./git-workflow.sh
   
   # ✅ Or direct commands
   ./git-workflow.sh commit    # Smart commits
   ./git-workflow.sh pr        # Create PR
   ./git-workflow.sh sync      # Sync with remote
   ```

2. **Workflow validation** - Use github-workflow-validator.sh
   ```bash
   ./github-workflow-validator.sh all     # All checks
   ./github-workflow-validator.sh syntax  # YAML validation
   ```

3. **Environment management** - Use uv-manager.sh
   ```bash
   ./uv-manager.sh verify    # Verify setup
   ./uv-manager.sh info      # Environment info
   ```

4. **File operations** - Use view/edit tools for local files
5. **Code search** - Use codebase-retrieval for local search

## Tool Selection Guide

### Decision Tree: GitHub API vs git commands vs codebase-retrieval

```
Need to interact with GitHub resources?
├─ Issues/PRs → Use GitHub API
│   ├─ Create, update, query issues
│   ├─ Create, review, merge PRs
│   └─ Check PR status
│
├─ CI/CD status → Use GitHub API
│   ├─ Check workflow runs
│   ├─ Verify test results
│   └─ Monitor deployments
│
├─ Repository data → Use GitHub API
│   ├─ Get repo info
│   ├─ List branches
│   └─ Search commits
│
Need to perform local git operations?
├─ Commit/push/rebase → Use launch-process with git
│   ├─ git commit
│   ├─ git push
│   └─ git rebase
│
Need to search code?
├─ Local codebase → Use codebase-retrieval
├─ GitHub repository → Use GitHub API /search/code
│
Need to read file contents?
├─ Local files → Use view or Serena
└─ GitHub files → Use GitHub API /repos/{owner}/{repo}/contents/{path}
```

## Default Workflow

### Using GitHub CLI (gh) - Recommended
Use `gh` CLI for common operations - cleaner and more reliable:

```bash
# PR operations
gh pr create --base development --title "feat: description"
gh pr list
gh pr view 65
gh pr status

# Workflow operations
gh run list
gh run watch
gh workflow list

# Issue operations
gh issue list
gh issue create --title "Bug: description"
```

### Management Scripts Available
Use our integrated workflow tools in root directory:

- **git-workflow.sh**: Smart commits, branching, PR creation
- **github-workflow-validator.sh**: Validate workflows, check runs
- **uv-manager.sh**: Environment management

### GitHub API Usage
For API operations not covered by CLI:

1. **Use summary parameter**: Clear description of API call
2. **Use details=false**: Only use details=true when needed
3. **Small page sizes**: Set per_page to 10-20
4. **Check rate limits**: Monitor API usage
5. **Verify CI after push**: Check status after commits

## Performance Considerations

### Rate Limiting

**Respect GitHub API rate limits:**
```python
# ✅ Good: Use small page sizes
github-api(
    path="/repos/theinterneti/TTA/issues",
    data={"per_page": 10}  # Small page size
)

# ❌ Avoid: Large page sizes
github-api(
    path="/repos/theinterneti/TTA/issues",
    data={"per_page": 100}  # Too large, wastes rate limit
)
```

### Query Efficiency

**Use filters to reduce results:**
```python
# ✅ Good: Filter by state and assignee
github-api(
    path="/repos/theinterneti/TTA/issues",
    data={"state": "open", "assignee": "theinterneti"}
)

# ❌ Avoid: Fetching all issues then filtering
github-api(
    path="/repos/theinterneti/TTA/issues",
    data={"state": "all"}  # Too many results
)
```

### Details Parameter

**Use details=false by default:**
```python
# ✅ Good: Essential fields only
github-api(
    path="/repos/theinterneti/TTA/issues",
    details=False  # Default, essential fields only
)

# ❌ Avoid: All fields when not needed
github-api(
    path="/repos/theinterneti/TTA/issues",
    details=True  # Large response, slow
)
```

## TTA-Specific Use Cases

### Create PRs for Component Promotions

```python
# Create PR for staging promotion
github-api(
    path="/repos/theinterneti/TTA/pulls",
    method="POST",
    data={
        "title": "Promote narrative-engine to staging",
        "body": "Component maturity: dev → staging. All quality gates passed.",
        "head": "staging/narrative-engine",
        "base": "staging"
    },
    summary="Create PR for narrative-engine staging promotion"
)
```

### Check CI Status After Pushing Changes

```python
# Get latest commit SHA
github-api(
    path="/repos/theinterneti/TTA/commits",
    data={"per_page": 1},
    summary="Get latest commit SHA"
)

# Check CI status
github-api(
    path="/repos/theinterneti/TTA/commits/{sha}/check-runs",
    summary="Check CI status for latest commit"
)
```

### Query Issues for Bug Tracking

```python
# List open bugs
github-api(
    path="/repos/theinterneti/TTA/issues",
    data={"labels": "bug", "state": "open"},
    summary="List open bug issues"
)

# List high-priority issues
github-api(
    path="/repos/theinterneti/TTA/issues",
    data={"labels": "priority:high", "state": "open"},
    summary="List high-priority issues"
)
```

## Troubleshooting

### Authentication Errors

**Symptom:** API calls fail with 401 Unauthorized

**Solutions:**
1. Verify GitHub credentials are configured
2. Check token has required permissions (repo, workflow, etc.)
3. Regenerate token if expired
4. Verify token is not revoked

### Rate Limiting

**Symptom:** API calls fail with 403 Forbidden (rate limit exceeded)

**Solutions:**
1. Reduce API call frequency
2. Use smaller page sizes (per_page parameter)
3. Cache results when possible
4. Wait for rate limit reset (check X-RateLimit-Reset header)
5. Use authenticated requests (higher rate limit)

### Permission Denied

**Symptom:** API calls fail with 403 Forbidden (insufficient permissions)

**Solutions:**
1. Verify token has required scopes (repo, workflow, admin:org, etc.)
2. Check repository access (public vs private)
3. Verify user has write access for POST/PATCH/PUT operations
4. Check organization permissions for org-level operations

### Resource Not Found

**Symptom:** API calls fail with 404 Not Found

**Solutions:**
1. Verify repository owner and name are correct
2. Check issue/PR number exists
3. Verify commit SHA is valid
4. Check branch name is correct
5. Ensure resource hasn't been deleted

### API Changes

**Symptom:** API calls fail with unexpected errors or responses

**Solutions:**
1. Verify API path is current (check GitHub API docs)
2. Check for deprecated endpoints
3. Update to new API version if available
4. Review GitHub API changelog for breaking changes
5. Test API calls with curl to isolate issues

## Integration with Other Rules

### MCP Tool Selection
- **Primary:** Use GitHub API for GitHub operations (see `Use-your-tools.md`)
- **Complement:** Use launch-process for local git operations
- **Fallback:** Use web-fetch for GitHub web pages

### Development Workflows
- **PR Creation:** Integrate GitHub API in component promotion workflow (see `integrated-workflow.md`)
- **CI Monitoring:** Check CI status after pushing changes
- **Issue Tracking:** Create issues for bugs and feature requests

### AI Context Management
- **Session Tracking:** Track GitHub operations in context sessions (see `ai-context-management.md`)
- **Decision Documentation:** Store PR/issue links in memories

## Related Documentation

- **MCP Tool Selection:** `Use-your-tools.md` - When to use GitHub API vs other MCP tools
- **Integrated Workflow:** `integrated-workflow.md` - GitHub integration in spec-to-production pipeline
- **System Prompt:** GitHub API tool signature and parameters
- **GitHub API Docs:** https://docs.github.com/en/rest

## Summary

**Primary use:** GitHub repository operations, issue management, PR operations, CI/CD status

**Key tool:** `github-api`

**When to use:** Issues, PRs, CI status, repository data, releases, code/commit search

**When NOT to use:** Local git operations (use git commands), file content (use Serena/view), non-GitHub repos

## Quick Reference

**Repository:** theinterneti/TTA  
**Remote:** TTA (not origin)  
**Main branches:** main, staging, development  
**Python:** 3.12 with UV package manager

**Workflow tools in root:**
- git-workflow.sh - Git operations
- github-workflow-validator.sh - Workflow validation  
- uv-manager.sh - Environment management

**Documentation:**
- .github/GITHUB_INTEGRATION_GUIDE.md - Complete guide
- GITHUB_QUICK_REF.md - Quick reference
- BRANCHING_STRATEGY.md - Branch/merge strategy

---

**Status:** Active
**Last Updated:** 2025-10-25
**Related Rules:** `Use-your-tools.md`, `integrated-workflow.md`
