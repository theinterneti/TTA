#!/bin/bash
# Add an issue to the TTA Component Maturity Tracker project
# Usage: project-add-issue.sh <issue_number> [options]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
CONFIG_FILE=".github/project-config.env"
OWNER="theinterneti"
REPO="TTA"

# Help text
show_help() {
    cat << EOF
Usage: $(basename "$0") <issue_number> [OPTIONS]

Add an issue to the TTA Component Maturity Tracker project board.

ARGUMENTS:
    issue_number            GitHub issue number to add

OPTIONS:
    -h, --help              Show this help message
    -s, --stage STAGE       Set Current Stage (Development|Staging|Production)
    -t, --target TARGET     Set Target Stage (Staging|Production)
    -g, --group GROUP       Set Functional Group (Core|AI|Player|Therapeutic)
    -c, --coverage NUM      Set Test Coverage percentage (0-100)
    -b, --blockers NUM      Set Blocker Count
    --dry-run               Show what would be done without making changes

EXAMPLES:
    # Add issue #42 to project
    $(basename "$0") 42

    # Add issue with initial field values
    $(basename "$0") 40 --stage Development --target Staging --coverage 100

    # Add issue with functional group
    $(basename "$0") 41 --stage Development --group AI --blockers 2

EOF
}

# Load configuration
load_config() {
    if [ ! -f "$CONFIG_FILE" ]; then
        echo -e "${RED}✗${NC} Configuration file not found: $CONFIG_FILE"
        echo "Run: scripts/project-setup.sh --save-config"
        exit 1
    fi

    source "$CONFIG_FILE"

    # Validate required variables
    if [ -z "$PROJECT_ID" ]; then
        echo -e "${RED}✗${NC} PROJECT_ID not set in $CONFIG_FILE"
        exit 1
    fi
}

# Parse arguments
ISSUE_NUMBER=""
CURRENT_STAGE=""
TARGET_STAGE=""
FUNCTIONAL_GROUP=""
TEST_COVERAGE=""
BLOCKER_COUNT=""
DRY_RUN=false

if [ $# -eq 0 ]; then
    show_help
    exit 1
fi

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -s|--stage)
            CURRENT_STAGE="$2"
            shift 2
            ;;
        -t|--target)
            TARGET_STAGE="$2"
            shift 2
            ;;
        -g|--group)
            FUNCTIONAL_GROUP="$2"
            shift 2
            ;;
        -c|--coverage)
            TEST_COVERAGE="$2"
            shift 2
            ;;
        -b|--blockers)
            BLOCKER_COUNT="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -*)
            echo -e "${RED}✗${NC} Unknown option: $1"
            show_help
            exit 1
            ;;
        *)
            if [ -z "$ISSUE_NUMBER" ]; then
                ISSUE_NUMBER="$1"
            else
                echo -e "${RED}✗${NC} Unexpected argument: $1"
                show_help
                exit 1
            fi
            shift
            ;;
    esac
done

# Validate issue number
if [ -z "$ISSUE_NUMBER" ]; then
    echo -e "${RED}✗${NC} Issue number required"
    show_help
    exit 1
fi

# Utility functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# Get issue node ID
get_issue_id() {
    log_info "Fetching issue #$ISSUE_NUMBER..."

    ISSUE_DATA=$(gh api graphql -f query='
        query($owner: String!, $repo: String!, $number: Int!) {
            repository(owner: $owner, name: $repo) {
                issue(number: $number) {
                    id
                    title
                    state
                }
            }
        }
    ' -f owner="$OWNER" -f repo="$REPO" -F number="$ISSUE_NUMBER")

    ISSUE_ID=$(echo "$ISSUE_DATA" | jq -r '.data.repository.issue.id')
    ISSUE_TITLE=$(echo "$ISSUE_DATA" | jq -r '.data.repository.issue.title')
    ISSUE_STATE=$(echo "$ISSUE_DATA" | jq -r '.data.repository.issue.state')

    if [ -z "$ISSUE_ID" ] || [ "$ISSUE_ID" = "null" ]; then
        log_error "Issue #$ISSUE_NUMBER not found"
        exit 1
    fi

    log_success "Found issue: $ISSUE_TITLE ($ISSUE_STATE)"
}

# Add issue to project
add_to_project() {
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would add issue #$ISSUE_NUMBER to project"
        return 0
    fi

    log_info "Adding issue to project..."

    RESULT=$(gh api graphql -f query='
        mutation($projectId: ID!, $contentId: ID!) {
            addProjectV2ItemById(input: {
                projectId: $projectId
                contentId: $contentId
            }) {
                item {
                    id
                }
            }
        }
    ' -f projectId="$PROJECT_ID" -f contentId="$ISSUE_ID")

    ITEM_ID=$(echo "$RESULT" | jq -r '.data.addProjectV2ItemById.item.id')

    if [ -z "$ITEM_ID" ] || [ "$ITEM_ID" = "null" ]; then
        # Check if already exists
        ERROR_MSG=$(echo "$RESULT" | jq -r '.errors[0].message // empty')
        if [[ "$ERROR_MSG" == *"already exists"* ]]; then
            log_success "Issue already in project"
            # Get existing item ID
            ITEM_ID=$(get_existing_item_id)
        else
            log_error "Failed to add issue to project"
            echo "$RESULT" | jq .
            exit 1
        fi
    else
        log_success "Added to project (Item ID: $ITEM_ID)"
    fi
}

# Get existing item ID
get_existing_item_id() {
    ITEMS_DATA=$(gh api graphql -f query='
        query($owner: String!, $number: Int!) {
            user(login: $owner) {
                projectV2(number: $number) {
                    items(first: 100) {
                        nodes {
                            id
                            content {
                                ... on Issue {
                                    number
                                }
                            }
                        }
                    }
                }
            }
        }
    ' -f owner="$OWNER" -F number="$PROJECT_NUMBER")

    echo "$ITEMS_DATA" | jq -r --argjson num "$ISSUE_NUMBER" '
        .data.user.projectV2.items.nodes[] |
        select(.content.number == $num) | .id
    '
}

# Update field value
update_field() {
    local field_id="$1"
    local value_type="$2"
    local value="$3"

    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would update field to: $value"
        return 0
    fi

    # Build GraphQL mutation based on value type
    case $value_type in
        singleSelectOptionId)
            gh api graphql -f query='
                mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
                    updateProjectV2ItemFieldValue(input: {
                        projectId: $projectId
                        itemId: $itemId
                        fieldId: $fieldId
                        value: { singleSelectOptionId: $optionId }
                    }) {
                        projectV2Item {
                            id
                        }
                    }
                }
            ' -f projectId="$PROJECT_ID" -f itemId="$ITEM_ID" -f fieldId="$field_id" -f optionId="$value" > /dev/null
            ;;
        number)
            gh api graphql -f query='
                mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $number: Float!) {
                    updateProjectV2ItemFieldValue(input: {
                        projectId: $projectId
                        itemId: $itemId
                        fieldId: $fieldId
                        value: { number: $number }
                    }) {
                        projectV2Item {
                            id
                        }
                    }
                }
            ' -f projectId="$PROJECT_ID" -f itemId="$ITEM_ID" -f fieldId="$field_id" -F number="$value" > /dev/null
            ;;
        date)
            gh api graphql -f query='
                mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $date: Date!) {
                    updateProjectV2ItemFieldValue(input: {
                        projectId: $projectId
                        itemId: $itemId
                        fieldId: $fieldId
                        value: { date: $date }
                    }) {
                        projectV2Item {
                            id
                        }
                    }
                }
            ' -f projectId="$PROJECT_ID" -f itemId="$ITEM_ID" -f fieldId="$field_id" -f date="$value" > /dev/null
            ;;
        *)
            log_error "Unknown value type: $value_type"
            return 1
            ;;
    esac
}

# Update fields based on arguments
update_fields() {
    if [ -z "$CURRENT_STAGE" ] && [ -z "$TARGET_STAGE" ] && [ -z "$FUNCTIONAL_GROUP" ] && [ -z "$TEST_COVERAGE" ] && [ -z "$BLOCKER_COUNT" ]; then
        log_info "No field updates requested"
        return 0
    fi

    log_info "Updating field values..."

    # Update Current Stage
    if [ -n "$CURRENT_STAGE" ]; then
        case $CURRENT_STAGE in
            Development)
                update_field "$FIELD_CURRENT_STAGE_ID" "singleSelectOptionId" "$OPTION_DEVELOPMENT_ID"
                log_success "Set Current Stage: Development"
                ;;
            Staging)
                update_field "$FIELD_CURRENT_STAGE_ID" "singleSelectOptionId" "$OPTION_STAGING_ID"
                log_success "Set Current Stage: Staging"
                ;;
            Production)
                update_field "$FIELD_CURRENT_STAGE_ID" "singleSelectOptionId" "$OPTION_PRODUCTION_ID"
                log_success "Set Current Stage: Production"
                ;;
            *)
                log_error "Invalid stage: $CURRENT_STAGE (use Development|Staging|Production)"
                ;;
        esac
    fi

    # Update Target Stage
    if [ -n "$TARGET_STAGE" ]; then
        case $TARGET_STAGE in
            Staging)
                update_field "$FIELD_TARGET_STAGE_ID" "singleSelectOptionId" "$OPTION_TARGET_STAGING_ID"
                log_success "Set Target Stage: Staging"
                ;;
            Production)
                update_field "$FIELD_TARGET_STAGE_ID" "singleSelectOptionId" "$OPTION_TARGET_PRODUCTION_ID"
                log_success "Set Target Stage: Production"
                ;;
            *)
                log_error "Invalid target: $TARGET_STAGE (use Staging|Production)"
                ;;
        esac
    fi

    # Update Functional Group
    if [ -n "$FUNCTIONAL_GROUP" ]; then
        case $FUNCTIONAL_GROUP in
            Core)
                update_field "$FIELD_FUNCTIONAL_GROUP_ID" "singleSelectOptionId" "$OPTION_CORE_INFRA_ID"
                log_success "Set Functional Group: Core Infrastructure"
                ;;
            AI)
                update_field "$FIELD_FUNCTIONAL_GROUP_ID" "singleSelectOptionId" "$OPTION_AI_AGENT_ID"
                log_success "Set Functional Group: AI/Agent Systems"
                ;;
            Player)
                update_field "$FIELD_FUNCTIONAL_GROUP_ID" "singleSelectOptionId" "$OPTION_PLAYER_EXP_ID"
                log_success "Set Functional Group: Player Experience"
                ;;
            Therapeutic)
                update_field "$FIELD_FUNCTIONAL_GROUP_ID" "singleSelectOptionId" "$OPTION_THERAPEUTIC_ID"
                log_success "Set Functional Group: Therapeutic Content"
                ;;
            *)
                log_error "Invalid group: $FUNCTIONAL_GROUP (use Core|AI|Player|Therapeutic)"
                ;;
        esac
    fi

    # Update Test Coverage
    if [ -n "$TEST_COVERAGE" ]; then
        update_field "$FIELD_TEST_COVERAGE_ID" "number" "$TEST_COVERAGE"
        log_success "Set Test Coverage: $TEST_COVERAGE%"
    fi

    # Update Blocker Count
    if [ -n "$BLOCKER_COUNT" ]; then
        update_field "$FIELD_BLOCKER_COUNT_ID" "number" "$BLOCKER_COUNT"
        log_success "Set Blocker Count: $BLOCKER_COUNT"
    fi

    # Update Last Updated
    TODAY=$(date -I)
    update_field "$FIELD_LAST_UPDATED_ID" "date" "$TODAY"
    log_success "Set Last Updated: $TODAY"
}

# Main execution
main() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${BLUE}Add Issue to Project Board${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    load_config
    get_issue_id
    add_to_project
    update_fields

    echo ""
    echo -e "${GREEN}✓ Complete!${NC}"
    echo "View project: https://github.com/users/$OWNER/projects/$PROJECT_NUMBER"
    echo ""
}

main
