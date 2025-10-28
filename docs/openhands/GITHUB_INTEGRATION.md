# OpenHands GitHub Integration Guide

## Overview

This guide explains how to use OpenHands as an async development assistant integrated into the TTA repository workflow. OpenHands runs tasks in the background using free LLM models (DeepSeek Chat V3.1) via GitHub Actions, allowing you to submit development tasks without blocking your main workflow.

## How It Works

1. **Create or comment on a GitHub issue** with a task description
2. **Mention `@openhands-agent`** in your comment to trigger OpenHands
3. **GitHub Actions workflow runs automatically** in the background
4. **OpenHands creates a Pull Request** with the completed work
5. **Review and merge** the PR when ready

## Setup Instructions

### 1. Configure GitHub Secrets

You need to add three secrets to your GitHub repository:

1. **Navigate to Repository Settings**:
   - Go to `https://github.com/theinterneti/TTA/settings/secrets/actions`

2. **Add Required Secrets**:

   | Secret Name | Value | Description |
   |-------------|-------|-------------|
   | `OPENROUTER_API_KEY` | Your OpenRouter API key | Found in your `.env` file |
   | `PAT_TOKEN` | GitHub Personal Access Token | Create at https://github.com/settings/tokens |
   | `PAT_USERNAME` | `theinterneti` | Your GitHub username |

### 2. Create GitHub Personal Access Token (PAT)

1. Go to https://github.com/settings/tokens/new
2. Set **Token name**: `OpenHands TTA Integration`
3. Set **Expiration**: 90 days (or custom)
4. Select **Scopes**:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
5. Click **Generate token**
6. **Copy the token immediately** (you won't see it again!)
7. Add it as `PAT_TOKEN` secret in repository settings

### 3. Verify Workflow File

The workflow file should be at `.github/workflows/openhands-resolver.yml`. If it's not there, create it from the template in this repository.

## Usage

### Basic Usage

1. **Create a new issue** or **open an existing issue**
2. **Add a comment** with the following format:

```
@openhands-agent Please [task description]
```

**Example**:
```
@openhands-agent Please generate comprehensive unit tests for the circuit_breaker.py module with 100% coverage
```

### What Tasks Are Suitable?

OpenHands works best for **time-consuming but straightforward tasks**:

✅ **Good Tasks**:
- Generate unit tests for a module
- Write boilerplate code (API endpoints, models, schemas)
- Refactor code to follow specific patterns
- Add type hints to existing code
- Generate documentation from code
- Implement simple features with clear specifications

❌ **Not Suitable**:
- Complex architectural decisions
- Tasks requiring deep context about the entire codebase
- Interactive debugging sessions
- Tasks requiring human judgment or creativity

### Checking Task Status

1. **GitHub Actions Tab**: View workflow runs at `https://github.com/theinterneti/TTA/actions`
2. **Issue Comments**: OpenHands posts status updates as comments
3. **Pull Requests**: Check for new PRs created by OpenHands

### Reviewing Results

1. **OpenHands creates a Pull Request** with the completed work
2. **Review the PR** like any other PR:
   - Check the code changes
   - Run tests locally if needed
   - Request changes if necessary
3. **Provide feedback** by commenting on the PR with `@openhands-agent` to request modifications
4. **Merge the PR** when satisfied

## Advanced Usage

### Iterative Refinement

You can refine OpenHands' work by commenting on the PR:

```
@openhands-agent Please add edge case tests for empty input and None values
```

OpenHands will update the PR with the requested changes.

### Multiple Tasks in Parallel

You can trigger multiple OpenHands tasks simultaneously by:
1. Creating multiple issues
2. Commenting `@openhands-agent` on each issue
3. Each task runs independently in parallel

## Troubleshooting

### Workflow Doesn't Trigger

**Symptoms**: No GitHub Actions workflow runs after commenting `@openhands-agent`

**Solutions**:
1. Verify the workflow file exists at `.github/workflows/openhands-resolver.yml`
2. Check that you're commenting on an **issue** (not a PR or discussion)
3. Ensure the comment contains exactly `@openhands-agent` (case-sensitive)
4. Check GitHub Actions is enabled for the repository

### Workflow Fails with Authentication Error

**Symptoms**: Workflow fails with "Authentication failed" or "401 Unauthorized"

**Solutions**:
1. Verify `PAT_TOKEN` secret is set correctly
2. Ensure the PAT has `repo` and `workflow` scopes
3. Check the PAT hasn't expired
4. Verify `PAT_USERNAME` matches your GitHub username

### Workflow Fails with LLM API Error

**Symptoms**: Workflow fails with "API key invalid" or "Rate limit exceeded"

**Solutions**:
1. Verify `OPENROUTER_API_KEY` secret is set correctly
2. Check your OpenRouter account has credits/quota
3. Verify the API key is active at https://openrouter.ai/keys
4. Try a different free model if DeepSeek is unavailable

### OpenHands Creates Incorrect Code

**Symptoms**: PR contains code that doesn't meet requirements

**Solutions**:
1. **Provide more detailed task descriptions** with specific requirements
2. **Comment on the PR** with `@openhands-agent` to request changes
3. **Close the PR** and create a new issue with clearer instructions
4. **Manually edit the PR** if changes are minor

## Integration with Other AI Agents

### Augment Agent

Augment Agent can create issues and trigger OpenHands:

```python
# Example: Augment creates issue for OpenHands
issue_body = """
## Task
Generate unit tests for circuit_breaker.py

## Requirements
- 100% code coverage
- Test all edge cases
- Use pytest fixtures

@openhands-agent Please implement the above requirements
"""
```

### GitHub Copilot

Copilot can suggest creating OpenHands tasks:

1. Copilot identifies time-consuming task
2. Suggests creating GitHub issue
3. You approve and create issue with `@openhands-agent`
4. OpenHands handles it asynchronously

## Best Practices

1. **Be Specific**: Provide clear, detailed task descriptions
2. **One Task Per Issue**: Keep issues focused on single tasks
3. **Review Thoroughly**: Always review OpenHands' PRs before merging
4. **Iterate**: Use PR comments to refine the work
5. **Use for Batch Work**: Reserve OpenHands for time-consuming tasks
6. **Monitor Costs**: Track OpenRouter usage even with free models

## Example Workflow

### Scenario: Generate Tests for New Module

1. **Create Issue**:
   ```
   Title: Generate tests for new authentication module

   Body:
   We need comprehensive unit tests for `src/auth/token_validator.py`

   Requirements:
   - Test all public methods
   - Include edge cases (expired tokens, invalid signatures)
   - Use pytest fixtures for test data
   - Aim for 100% coverage

   @openhands-agent Please generate these tests
   ```

2. **Wait for Workflow**:
   - GitHub Actions triggers automatically
   - Check status at https://github.com/theinterneti/TTA/actions

3. **Review PR**:
   - OpenHands creates PR with test file
   - Review the generated tests
   - Run tests locally: `pytest tests/unit/auth/test_token_validator.py`

4. **Request Changes** (if needed):
   ```
   @openhands-agent Please add tests for the refresh_token() method
   ```

5. **Merge PR**:
   - Once satisfied, merge the PR
   - Tests are now part of the codebase

## Configuration Reference

### Workflow Configuration

The workflow is configured in `.github/workflows/openhands-resolver.yml`:

```yaml
env:
  LLM_MODEL: "deepseek/deepseek-chat-v3.1:free"  # Free LLM model
  LLM_BASE_URL: "https://openrouter.ai/api/v1"   # OpenRouter API
```

### Supported Free Models

You can change the model by editing the workflow file:

- `deepseek/deepseek-chat-v3.1:free` (Default, recommended)
- `google/gemini-flash-1.5:free`
- `meta-llama/llama-3.1-8b-instruct:free`

## Security Considerations

1. **API Keys**: Never commit API keys to the repository
2. **Secrets**: Use GitHub Secrets for sensitive data
3. **PR Review**: Always review OpenHands' code before merging
4. **Permissions**: The workflow has minimal required permissions
5. **Rate Limits**: Free models have rate limits - monitor usage

## Support

For issues or questions:
1. Check this documentation first
2. Review workflow logs in GitHub Actions
3. Check OpenHands documentation: https://docs.all-hands.dev
4. Create an issue in the TTA repository

---

**Last Updated**: 2025-10-28
**Status**: Active - Proof of Concept
