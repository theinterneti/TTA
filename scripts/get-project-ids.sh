#!/bin/bash
# Get GitHub Project V2 IDs for automation
# Run once and save the output to .github/project-config.env

set -e

OWNER="theinterneti"
PROJECT_NUMBER=1  # Update this to your project number

echo "🔍 Fetching GitHub Project V2 IDs..."
echo ""

# Get project ID
PROJECT_DATA=$(gh api graphql -f query='
  query($owner: String!, $number: Int!) {
    user(login: $owner) {
      projectV2(number: $number) {
        id
        title
        fields(first: 20) {
          nodes {
            ... on ProjectV2Field {
              id
              name
              dataType
            }
            ... on ProjectV2SingleSelectField {
              id
              name
              dataType
              options {
                id
                name
              }
            }
          }
        }
      }
    }
  }
' -f owner="$OWNER" -F number="$PROJECT_NUMBER")

# Parse and display results
PROJECT_ID=$(echo "$PROJECT_DATA" | jq -r '.data.user.projectV2.id')
PROJECT_TITLE=$(echo "$PROJECT_DATA" | jq -r '.data.user.projectV2.title')

echo "📊 Project: $PROJECT_TITLE"
echo "   ID: $PROJECT_ID"
echo ""
echo "📋 Custom Fields:"
echo "$PROJECT_DATA" | jq -r '.data.user.projectV2.fields.nodes[] |
  "   \(.name):\n     ID: \(.id)\n     Type: \(.dataType)\n" +
  (if .options then "     Options:\n" + (.options | map("       - \(.name): \(.id)") | join("\n")) else "" end)'

echo ""
echo "💾 Save these IDs to .github/project-config.env:"
echo ""
echo "PROJECT_ID=$PROJECT_ID"
echo "# Add field IDs below after running this script"
echo "FIELD_CURRENT_STAGE_ID=<from output above>"
echo "FIELD_TARGET_STAGE_ID=<from output above>"
echo "FIELD_BLOCKER_COUNT_ID=<from output above>"
echo "FIELD_TEST_COVERAGE_ID=<from output above>"
echo "FIELD_LAST_UPDATED_ID=<from output above>"
echo "FIELD_FUNCTIONAL_GROUP_ID=<from output above>"
echo ""
echo "# Option IDs for single-select fields"
echo "OPTION_DEVELOPMENT_ID=<from output above>"
echo "OPTION_STAGING_ID=<from output above>"
echo "OPTION_PRODUCTION_ID=<from output above>"
