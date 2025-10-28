# OpenHands Test Issue Example

Use this template to create a test issue and verify the OpenHands GitHub integration is working correctly.

## Step 1: Create Test Issue

1. Go to https://github.com/theinterneti/TTA/issues/new
2. Use the following content:

---

**Title**: `[TEST] OpenHands Integration Verification`

**Body**:
```markdown
## Test Task

This is a test issue to verify the OpenHands GitHub integration is working correctly.

## Task Description

Create a simple Python utility function that:
1. Takes a list of numbers as input
2. Returns the sum of all even numbers in the list
3. Includes comprehensive docstring with examples
4. Includes type hints

## Requirements

- Function name: `sum_even_numbers`
- Location: Create new file `src/utils/math_helpers.py`
- Include docstring with:
  - Description
  - Args documentation
  - Returns documentation
  - Example usage
- Use type hints (List[int] -> int)
- Handle empty list (return 0)

## Expected Output

```python
from typing import List

def sum_even_numbers(numbers: List[int]) -> int:
    """
    Calculate the sum of all even numbers in a list.

    Args:
        numbers: A list of integers to process

    Returns:
        The sum of all even numbers in the list, or 0 if no even numbers exist

    Examples:
        >>> sum_even_numbers([1, 2, 3, 4, 5, 6])
        12
        >>> sum_even_numbers([1, 3, 5])
        0
        >>> sum_even_numbers([])
        0
    """
    return sum(num for num in numbers if num % 2 == 0)
```

---

**Labels**: Add `openhands-task` label

---

## Step 2: Trigger OpenHands

After creating the issue, add a comment:

```
@openhands-agent Please implement the function described above with all requirements
```

## Step 3: Monitor Progress

1. **Check GitHub Actions**:
   - Go to https://github.com/theinterneti/TTA/actions
   - Look for "OpenHands Issue Resolver" workflow
   - Click on the running workflow to see logs

2. **Check Issue Comments**:
   - OpenHands will post status updates as comments
   - Look for success/failure messages

3. **Check Pull Requests**:
   - Go to https://github.com/theinterneti/TTA/pulls
   - Look for a new PR created by OpenHands
   - PR title should reference the issue number

## Step 4: Verify Results

1. **Review the PR**:
   - Check that `src/utils/math_helpers.py` was created
   - Verify the function matches requirements
   - Check docstring and type hints

2. **Test Locally** (optional):
   ```bash
   # Checkout the PR branch
   gh pr checkout <PR_NUMBER>

   # Test the function
   python -c "from src.utils.math_helpers import sum_even_numbers; print(sum_even_numbers([1,2,3,4,5,6]))"
   # Expected output: 12
   ```

3. **Provide Feedback** (if needed):
   ```
   @openhands-agent Please add a unit test file at tests/unit/utils/test_math_helpers.py
   ```

4. **Merge or Close**:
   - If satisfied, merge the PR
   - If this was just a test, close the PR and issue

## Expected Timeline

- **Workflow Trigger**: Immediate (within seconds)
- **Workflow Execution**: 2-5 minutes
- **PR Creation**: Within 5 minutes of comment

## Troubleshooting

### Workflow Doesn't Start

**Check**:
1. Workflow file exists at `.github/workflows/openhands-resolver.yml`
2. Comment contains exactly `@openhands-agent` (case-sensitive)
3. You're commenting on an issue (not PR or discussion)
4. GitHub Actions is enabled for the repository

**Fix**:
- Verify workflow file is committed to the repository
- Try commenting again with exact syntax
- Check repository settings → Actions → General → "Allow all actions"

### Workflow Fails Immediately

**Check**:
1. GitHub Secrets are configured:
   - `OPENROUTER_API_KEY`
   - `PAT_TOKEN`
   - `PAT_USERNAME`
2. PAT token has correct permissions (repo, workflow)
3. PAT token hasn't expired

**Fix**:
- Go to https://github.com/theinterneti/TTA/settings/secrets/actions
- Verify all three secrets exist
- Regenerate PAT if expired

### Workflow Runs But No PR Created

**Check**:
1. Workflow logs for errors
2. OpenRouter API key is valid
3. Rate limits on free model

**Fix**:
- Check workflow logs in GitHub Actions
- Verify API key at https://openrouter.ai/keys
- Wait a few minutes and try again (rate limit)

### PR Created But Code Is Wrong

**This is expected for a test!** OpenHands may not get it perfect on the first try.

**Fix**:
- Comment on the PR with `@openhands-agent` and specific feedback
- Example: `@openhands-agent Please add error handling for None input`
- OpenHands will update the PR

## Success Criteria

✅ **Integration is working if**:
1. Workflow triggers when you comment `@openhands-agent`
2. Workflow completes without errors
3. OpenHands creates a Pull Request
4. PR contains the requested file with reasonable code

❌ **Integration needs debugging if**:
1. Workflow doesn't trigger at all
2. Workflow fails with authentication errors
3. Workflow fails with API errors
4. No PR is created after successful workflow

## Next Steps After Successful Test

1. **Close the test issue and PR** (if you don't want to keep them)
2. **Start using OpenHands for real tasks**:
   - Generate tests for existing modules
   - Create boilerplate code
   - Refactor code to patterns
3. **Document your workflow** in team documentation
4. **Share with team members** how to use OpenHands

## Alternative Simple Test

If the above test is too complex, try this minimal test:

**Issue Title**: `[TEST] Simple OpenHands Test`

**Issue Body**:
```markdown
Create a file `test.txt` with the content "Hello from OpenHands!"

@openhands-agent Please create the file described above
```

This tests the basic workflow without requiring code generation.

---

**Last Updated**: 2025-10-28
**Status**: Test Template for POC Verification
