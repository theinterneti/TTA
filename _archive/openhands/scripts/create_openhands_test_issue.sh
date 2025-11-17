#!/bin/bash
# Script to create OpenHands test issue and trigger the workflow
# Usage: bash scripts/create_openhands_test_issue.sh

set -e

echo "🤖 Creating OpenHands test issue..."

# Create the test issue
ISSUE_URL=$(gh issue create \
  --title "[TEST] OpenHands Integration Verification" \
  --body "## Test Task

This is a test issue to verify the OpenHands GitHub integration is working correctly.

## Task Description

Create a simple text file with a greeting message.

## Requirements

- File name: \`openhands-test.txt\`
- File location: Root directory of the repository
- File content: \`Hello from OpenHands! Integration test successful.\`

## Expected Outcome

A new file \`openhands-test.txt\` should be created in the root directory with the specified content.

---

**Note**: This is a test issue. The file will be deleted after verification.")

echo "✅ Test issue created: $ISSUE_URL"

# Extract issue number from URL
ISSUE_NUMBER=$(echo "$ISSUE_URL" | grep -oP '\d+$')

echo "📝 Issue number: #$ISSUE_NUMBER"
echo ""
echo "⏳ Waiting 3 seconds before adding comment..."
sleep 3

# Add comment to trigger OpenHands
echo "🚀 Triggering OpenHands workflow..."
gh issue comment "$ISSUE_NUMBER" \
  --body "@openhands-agent Please create the file described above with the exact content specified in the requirements"

echo ""
echo "✅ OpenHands workflow triggered!"
echo ""
echo "📊 Next steps:"
echo "  1. Check workflow status: https://github.com/theinterneti/TTA/actions"
echo "  2. Monitor issue comments: $ISSUE_URL"
echo "  3. Watch for PR creation: https://github.com/theinterneti/TTA/pulls"
echo ""
echo "⏱️  Expected timeline:"
echo "  - Workflow starts: 10-30 seconds"
echo "  - Workflow completes: 2-5 minutes"
echo "  - PR created: Within 5 minutes"
echo ""
echo "🔍 To view workflow logs:"
echo "  gh run list --workflow=openhands-resolver.yml --limit 1"
echo "  gh run view <run-id> --log"

