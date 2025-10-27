#!/bin/bash
# Interactive script to update custom field values for a project item
# Usage: project-update-fields.sh <issue_number>

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
CONFIG_FILE=".github/project-config.env"
OWNER="theinterneti"
REPO="TTA"

# Help text
show_help() {
    cat << EOF
Usage: $(basename "$0") <issue_number> [OPTIONS]

Interactively update custom field values for a project item.

ARGUMENTS:
    issue_number            GitHub issue number to update

OPTIONS:
    -h, --help              Show this help message
    --non-interactive       Use command-line arguments instead of prompts
    -s, --stage STAGE       Set Current Stage
    -t, --target TARGET     Set Target Stage
    -g, --group GROUP       Set Functional Group
    -c, --coverage NUM      Set Test Coverage
    -b, --blockers NUM      Set Blocker Count

EXAMPLES:
    # Interactive mode
    $(basename "$0") 42

    # Non-interactive mode
    $(basename "$0") 40 --non-interactive --stage Staging --coverage 85

EOF
}

# Parse arguments
ISSUE_NUMBER=""
INTERACTIVE=true
NEW_STAGE=""
NEW_TARGET=""
NEW_GROUP=""
NEW_COVERAGE=""
NEW_BLOCKERS=""

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
        --non-interactive)
            INTERACTIVE=false
            shift
            ;;
        -s|--stage)
            NEW_STAGE="$2"
            shift 2
            ;;
        -t|--target)
            NEW_TARGET="$2"
            shift 2
            ;;
        -g|--group)
            NEW_GROUP="$2"
            shift 2
            ;;
        -c|--coverage)
            NEW_COVERAGE="$2"
            shift 2
            ;;
        -b|--blockers)
            NEW_BLOCKERS="$2"
            shift 2
            ;;
        -*)
            echo -e "${RED}✗${NC} Unknown option: $1"
            show_help
            exit 1
            ;;
        *)
            if [ -z "$ISSUE_NUMBER" ]; then
                ISSUE_NUMBER="$1"
            fi
            shift
            ;;
    esac
done

# Load configuration
load_config() {
    if [ ! -f "$CONFIG_FILE" ]; then
        echo -e "${RED}✗${NC} Configuration file not found: $CONFIG_FILE"
        echo "Run: scripts/project-setup.sh --save-config"
        exit 1
    fi

    source "$CONFIG_FILE"
}

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

# Get project item ID for issue
get_item_id() {
    log_info "Finding project item for issue #$ISSUE_NUMBER..."

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
                                    title
                                }
                            }
                            fieldValues(first: 20) {
                                nodes {
                                    ... on ProjectV2ItemFieldSingleSelectValue {
                                        name
                                        field {
                                            ... on ProjectV2SingleSelectField {
                                                name
                                            }
                                        }
                                    }
                                    ... on ProjectV2ItemFieldNumberValue {
                                        number
                                        field {
                                            ... on ProjectV2Field {
                                                name
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    ' -f owner="$OWNER" -F number="$PROJECT_NUMBER")

    ITEM_ID=$(echo "$ITEMS_DATA" | jq -r --argjson num "$ISSUE_NUMBER" '
        .data.user.projectV2.items.nodes[] |
        select(.content.number == $num) | .id
    ')

    if [ -z "$ITEM_ID" ] || [ "$ITEM_ID" = "null" ]; then
        log_error "Issue #$ISSUE_NUMBER not found in project"
        echo "Add it first with: scripts/project-add-issue.sh $ISSUE_NUMBER"
        exit 1
    fi

    # Get current values
    CURRENT_STAGE=$(echo "$ITEMS_DATA" | jq -r --argjson num "$ISSUE_NUMBER" '
        .data.user.projectV2.items.nodes[] |
        select(.content.number == $num) |
        .fieldValues.nodes[] |
        select(.field.name == "Current Stage") | .name // "Not set"
    ')

    CURRENT_TARGET=$(echo "$ITEMS_DATA" | jq -r --argjson num "$ISSUE_NUMBER" '
        .data.user.projectV2.items.nodes[] |
        select(.content.number == $num) |
        .fieldValues.nodes[] |
        select(.field.name == "Target Stage") | .name // "Not set"
    ')

    CURRENT_GROUP=$(echo "$ITEMS_DATA" | jq -r --argjson num "$ISSUE_NUMBER" '
        .data.user.projectV2.items.nodes[] |
        select(.content.number == $num) |
        .fieldValues.nodes[] |
        select(.field.name == "Functional Group") | .name // "Not set"
    ')

    CURRENT_COVERAGE=$(echo "$ITEMS_DATA" | jq -r --argjson num "$ISSUE_NUMBER" '
        .data.user.projectV2.items.nodes[] |
        select(.content.number == $num) |
        .fieldValues.nodes[] |
        select(.field.name == "Test Coverage") | .number // 0
    ')

    CURRENT_BLOCKERS=$(echo "$ITEMS_DATA" | jq -r --argjson num "$ISSUE_NUMBER" '
        .data.user.projectV2.items.nodes[] |
        select(.content.number == $num) |
        .fieldValues.nodes[] |
        select(.field.name == "Blocker Count") | .number // 0
    ')

    ISSUE_TITLE=$(echo "$ITEMS_DATA" | jq -r --argjson num "$ISSUE_NUMBER" '
        .data.user.projectV2.items.nodes[] |
        select(.content.number == $num) | .content.title
    ')

    log_success "Found: $ISSUE_TITLE"
}

# Display current values
display_current_values() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${CYAN}Current Field Values${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${BLUE}Issue:${NC} #$ISSUE_NUMBER - $ISSUE_TITLE"
    echo ""
    echo -e "${BLUE}Current Stage:${NC} $CURRENT_STAGE"
    echo -e "${BLUE}Target Stage:${NC} $CURRENT_TARGET"
    echo -e "${BLUE}Functional Group:${NC} $CURRENT_GROUP"
    echo -e "${BLUE}Test Coverage:${NC} $CURRENT_COVERAGE%"
    echo -e "${BLUE}Blocker Count:${NC} $CURRENT_BLOCKERS"
    echo ""
}

# Interactive prompts
prompt_for_updates() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${CYAN}Update Field Values${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Press Enter to keep current value, or enter new value:"
    echo ""

    # Current Stage
    echo -e "${BLUE}Current Stage${NC} (Development|Staging|Production) [$CURRENT_STAGE]:"
    read -r NEW_STAGE
    [ -z "$NEW_STAGE" ] && NEW_STAGE="$CURRENT_STAGE"

    # Target Stage
    echo -e "${BLUE}Target Stage${NC} (Staging|Production) [$CURRENT_TARGET]:"
    read -r NEW_TARGET
    [ -z "$NEW_TARGET" ] && NEW_TARGET="$CURRENT_TARGET"

    # Functional Group
    echo -e "${BLUE}Functional Group${NC} (Core|AI|Player|Therapeutic) [$CURRENT_GROUP]:"
    read -r NEW_GROUP
    [ -z "$NEW_GROUP" ] && NEW_GROUP="$CURRENT_GROUP"

    # Test Coverage
    echo -e "${BLUE}Test Coverage${NC} (0-100) [$CURRENT_COVERAGE]:"
    read -r NEW_COVERAGE
    [ -z "$NEW_COVERAGE" ] && NEW_COVERAGE="$CURRENT_COVERAGE"

    # Blocker Count
    echo -e "${BLUE}Blocker Count${NC} [$CURRENT_BLOCKERS]:"
    read -r NEW_BLOCKERS
    [ -z "$NEW_BLOCKERS" ] && NEW_BLOCKERS="$CURRENT_BLOCKERS"

    echo ""
}

# Update field
update_field() {
    local field_id="$1"
    local value_type="$2"
    local value="$3"

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
    esac
}

# Apply updates
apply_updates() {
    log_info "Applying updates..."

    # Update Current Stage
    if [ "$NEW_STAGE" != "$CURRENT_STAGE" ] && [ "$NEW_STAGE" != "Not set" ]; then
        case $NEW_STAGE in
            Development)
                update_field "$FIELD_CURRENT_STAGE_ID" "singleSelectOptionId" "$OPTION_DEVELOPMENT_ID"
                log_success "Updated Current Stage: Development"
                ;;
            Staging)
                update_field "$FIELD_CURRENT_STAGE_ID" "singleSelectOptionId" "$OPTION_STAGING_ID"
                log_success "Updated Current Stage: Staging"
                ;;
            Production)
                update_field "$FIELD_CURRENT_STAGE_ID" "singleSelectOptionId" "$OPTION_PRODUCTION_ID"
                log_success "Updated Current Stage: Production"
                ;;
        esac
    fi

    # Update Target Stage
    if [ "$NEW_TARGET" != "$CURRENT_TARGET" ] && [ "$NEW_TARGET" != "Not set" ]; then
        case $NEW_TARGET in
            Staging)
                update_field "$FIELD_TARGET_STAGE_ID" "singleSelectOptionId" "$OPTION_TARGET_STAGING_ID"
                log_success "Updated Target Stage: Staging"
                ;;
            Production)
                update_field "$FIELD_TARGET_STAGE_ID" "singleSelectOptionId" "$OPTION_TARGET_PRODUCTION_ID"
                log_success "Updated Target Stage: Production"
                ;;
        esac
    fi

    # Update Functional Group
    if [ "$NEW_GROUP" != "$CURRENT_GROUP" ] && [ "$NEW_GROUP" != "Not set" ]; then
        case $NEW_GROUP in
            Core)
                update_field "$FIELD_FUNCTIONAL_GROUP_ID" "singleSelectOptionId" "$OPTION_CORE_INFRA_ID"
                log_success "Updated Functional Group: Core Infrastructure"
                ;;
            AI)
                update_field "$FIELD_FUNCTIONAL_GROUP_ID" "singleSelectOptionId" "$OPTION_AI_AGENT_ID"
                log_success "Updated Functional Group: AI/Agent Systems"
                ;;
            Player)
                update_field "$FIELD_FUNCTIONAL_GROUP_ID" "singleSelectOptionId" "$OPTION_PLAYER_EXP_ID"
                log_success "Updated Functional Group: Player Experience"
                ;;
            Therapeutic)
                update_field "$FIELD_FUNCTIONAL_GROUP_ID" "singleSelectOptionId" "$OPTION_THERAPEUTIC_ID"
                log_success "Updated Functional Group: Therapeutic Content"
                ;;
        esac
    fi

    # Update Test Coverage
    if [ "$NEW_COVERAGE" != "$CURRENT_COVERAGE" ]; then
        update_field "$FIELD_TEST_COVERAGE_ID" "number" "$NEW_COVERAGE"
        log_success "Updated Test Coverage: $NEW_COVERAGE%"
    fi

    # Update Blocker Count
    if [ "$NEW_BLOCKERS" != "$CURRENT_BLOCKERS" ]; then
        update_field "$FIELD_BLOCKER_COUNT_ID" "number" "$NEW_BLOCKERS"
        log_success "Updated Blocker Count: $NEW_BLOCKERS"
    fi

    # Always update Last Updated
    TODAY=$(date -I)
    update_field "$FIELD_LAST_UPDATED_ID" "date" "$TODAY"
    log_success "Updated Last Updated: $TODAY"
}

# Main execution
main() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${BLUE}Update Project Item Fields${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    load_config
    get_item_id
    display_current_values

    if [ "$INTERACTIVE" = true ]; then
        prompt_for_updates
    fi

    apply_updates

    echo ""
    echo -e "${GREEN}✓ Updates Complete!${NC}"
    echo "View project: https://github.com/users/$OWNER/projects/$PROJECT_NUMBER"
    echo ""
}

main
