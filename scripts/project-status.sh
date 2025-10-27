#!/bin/bash
# Display status of the TTA Component Maturity Tracker project
# Usage: project-status.sh [options]

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

# Help text
show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Display the current status of the TTA Component Maturity Tracker project board.

OPTIONS:
    -h, --help              Show this help message
    -s, --stage STAGE       Filter by Current Stage (Development|Staging|Production)
    -g, --group GROUP       Filter by Functional Group (Core|AI|Player|Therapeutic)
    -f, --format FORMAT     Output format (table|json|csv) [default: table]
    -l, --limit NUM         Limit number of items to display [default: 50]
    --summary-only          Show only summary statistics

EXAMPLES:
    # Show all items
    $(basename "$0")

    # Show only Development stage items
    $(basename "$0") --stage Development

    # Show only AI/Agent Systems group
    $(basename "$0") --group AI

    # Show summary only
    $(basename "$0") --summary-only

    # Export to JSON
    $(basename "$0") --format json > project-status.json

EOF
}

# Parse arguments
FILTER_STAGE=""
FILTER_GROUP=""
OUTPUT_FORMAT="table"
LIMIT=50
SUMMARY_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -s|--stage)
            FILTER_STAGE="$2"
            shift 2
            ;;
        -g|--group)
            FILTER_GROUP="$2"
            shift 2
            ;;
        -f|--format)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        -l|--limit)
            LIMIT="$2"
            shift 2
            ;;
        --summary-only)
            SUMMARY_ONLY=true
            shift
            ;;
        *)
            echo -e "${RED}✗${NC} Unknown option: $1"
            show_help
            exit 1
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

# Fetch project data
fetch_project_data() {
    log_info "Fetching project data..."

    PROJECT_DATA=$(gh api graphql -f query='
        query($owner: String!, $number: Int!, $limit: Int!) {
            user(login: $owner) {
                projectV2(number: $number) {
                    title
                    url
                    items(first: $limit) {
                        totalCount
                        nodes {
                            id
                            content {
                                ... on Issue {
                                    number
                                    title
                                    state
                                    url
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
                                    ... on ProjectV2ItemFieldDateValue {
                                        date
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
    ' -f owner="$OWNER" -F number="$PROJECT_NUMBER" -F limit="$LIMIT")

    log_success "Data fetched"
}

# Display summary
display_summary() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${CYAN}TTA Component Maturity Tracker - Summary${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    PROJECT_TITLE=$(echo "$PROJECT_DATA" | jq -r '.data.user.projectV2.title')
    PROJECT_URL=$(echo "$PROJECT_DATA" | jq -r '.data.user.projectV2.url')
    TOTAL_ITEMS=$(echo "$PROJECT_DATA" | jq -r '.data.user.projectV2.items.totalCount')

    echo -e "${BLUE}Project:${NC} $PROJECT_TITLE"
    echo -e "${BLUE}URL:${NC} $PROJECT_URL"
    echo -e "${BLUE}Total Items:${NC} $TOTAL_ITEMS"
    echo ""

    # Count by stage
    DEV_COUNT=$(echo "$PROJECT_DATA" | jq '[.data.user.projectV2.items.nodes[] | .fieldValues.nodes[] | select(.field.name == "Current Stage" and .name == "Development")] | length')
    STAGING_COUNT=$(echo "$PROJECT_DATA" | jq '[.data.user.projectV2.items.nodes[] | .fieldValues.nodes[] | select(.field.name == "Current Stage" and .name == "Staging")] | length')
    PROD_COUNT=$(echo "$PROJECT_DATA" | jq '[.data.user.projectV2.items.nodes[] | .fieldValues.nodes[] | select(.field.name == "Current Stage" and .name == "Production")] | length')

    echo -e "${BLUE}By Stage:${NC}"
    echo "  Development: $DEV_COUNT"
    echo "  Staging: $STAGING_COUNT"
    echo "  Production: $PROD_COUNT"
    echo ""

    # Count by functional group
    CORE_COUNT=$(echo "$PROJECT_DATA" | jq '[.data.user.projectV2.items.nodes[] | .fieldValues.nodes[] | select(.field.name == "Functional Group" and .name == "Core Infrastructure")] | length')
    AI_COUNT=$(echo "$PROJECT_DATA" | jq '[.data.user.projectV2.items.nodes[] | .fieldValues.nodes[] | select(.field.name == "Functional Group" and .name == "AI/Agent Systems")] | length')
    PLAYER_COUNT=$(echo "$PROJECT_DATA" | jq '[.data.user.projectV2.items.nodes[] | .fieldValues.nodes[] | select(.field.name == "Functional Group" and .name == "Player Experience")] | length')
    THERAPEUTIC_COUNT=$(echo "$PROJECT_DATA" | jq '[.data.user.projectV2.items.nodes[] | .fieldValues.nodes[] | select(.field.name == "Functional Group" and .name == "Therapeutic Content")] | length')

    echo -e "${BLUE}By Functional Group:${NC}"
    echo "  Core Infrastructure: $CORE_COUNT"
    echo "  AI/Agent Systems: $AI_COUNT"
    echo "  Player Experience: $PLAYER_COUNT"
    echo "  Therapeutic Content: $THERAPEUTIC_COUNT"
    echo ""

    # Average test coverage
    AVG_COVERAGE=$(echo "$PROJECT_DATA" | jq '[.data.user.projectV2.items.nodes[].fieldValues.nodes[] | select(.field.name == "Test Coverage") | .number] | if length > 0 then add / length else null end')
    if [ "$AVG_COVERAGE" != "null" ] && [ -n "$AVG_COVERAGE" ]; then
        printf "${BLUE}Average Test Coverage:${NC} %.1f%%\n" "$AVG_COVERAGE"
    else
        echo -e "${BLUE}Average Test Coverage:${NC} N/A"
    fi

    # Total blockers
    TOTAL_BLOCKERS=$(echo "$PROJECT_DATA" | jq '[.data.user.projectV2.items.nodes[].fieldValues.nodes[] | select(.field.name == "Blocker Count") | .number] | add')
    if [ "$TOTAL_BLOCKERS" != "null" ]; then
        echo -e "${BLUE}Total Blockers:${NC} $TOTAL_BLOCKERS"
    else
        echo -e "${BLUE}Total Blockers:${NC} 0"
    fi
    echo ""
}

# Display table
display_table() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${CYAN}Project Items${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Table header
    printf "%-6s %-40s %-12s %-12s %-10s %-8s\n" "Issue" "Title" "Stage" "Target" "Coverage" "Blockers"
    printf "%-6s %-40s %-12s %-12s %-10s %-8s\n" "------" "----------------------------------------" "------------" "------------" "----------" "--------"

    # Process each item
    echo "$PROJECT_DATA" | jq -r '.data.user.projectV2.items.nodes[] |
        {
            number: .content.number,
            title: .content.title,
            stage: ([.fieldValues.nodes[] | select(.field.name == "Current Stage") | .name] | first // "N/A"),
            target: ([.fieldValues.nodes[] | select(.field.name == "Target Stage") | .name] | first // "N/A"),
            coverage: ([.fieldValues.nodes[] | select(.field.name == "Test Coverage") | .number] | first // 0),
            blockers: ([.fieldValues.nodes[] | select(.field.name == "Blocker Count") | .number] | first // 0),
            group: ([.fieldValues.nodes[] | select(.field.name == "Functional Group") | .name] | first // "N/A")
        } |
        "\(.number)|\(.title)|\(.stage)|\(.target)|\(.coverage)|\(.blockers)|\(.group)"
    ' | while IFS='|' read -r number title stage target coverage blockers group; do
        # Apply filters
        if [ -n "$FILTER_STAGE" ] && [ "$stage" != "$FILTER_STAGE" ]; then
            continue
        fi

        if [ -n "$FILTER_GROUP" ]; then
            case $FILTER_GROUP in
                Core)
                    [ "$group" != "Core Infrastructure" ] && continue
                    ;;
                AI)
                    [ "$group" != "AI/Agent Systems" ] && continue
                    ;;
                Player)
                    [ "$group" != "Player Experience" ] && continue
                    ;;
                Therapeutic)
                    [ "$group" != "Therapeutic Content" ] && continue
                    ;;
            esac
        fi

        # Truncate title if too long
        if [ ${#title} -gt 40 ]; then
            title="${title:0:37}..."
        fi

        # Format coverage
        if [ "$coverage" != "0" ]; then
            coverage_str=$(printf "%.1f%%" "$coverage")
        else
            coverage_str="N/A"
        fi

        printf "%-6s %-40s %-12s %-12s %-10s %-8s\n" "#$number" "$title" "$stage" "$target" "$coverage_str" "$blockers"
    done

    echo ""
}

# Display JSON
display_json() {
    echo "$PROJECT_DATA" | jq '.data.user.projectV2.items.nodes[] |
        {
            issue_number: .content.number,
            title: .content.title,
            state: .content.state,
            url: .content.url,
            current_stage: ([.fieldValues.nodes[] | select(.field.name == "Current Stage") | .name] | first),
            target_stage: ([.fieldValues.nodes[] | select(.field.name == "Target Stage") | .name] | first),
            functional_group: ([.fieldValues.nodes[] | select(.field.name == "Functional Group") | .name] | first),
            test_coverage: ([.fieldValues.nodes[] | select(.field.name == "Test Coverage") | .number] | first),
            blocker_count: ([.fieldValues.nodes[] | select(.field.name == "Blocker Count") | .number] | first),
            last_updated: ([.fieldValues.nodes[] | select(.field.name == "Last Updated") | .date] | first)
        }
    ' | jq -s .
}

# Display CSV
display_csv() {
    echo "Issue,Title,State,Stage,Target,Group,Coverage,Blockers,Last Updated,URL"
    echo "$PROJECT_DATA" | jq -r '.data.user.projectV2.items.nodes[] |
        {
            number: .content.number,
            title: .content.title,
            state: .content.state,
            url: .content.url,
            stage: ([.fieldValues.nodes[] | select(.field.name == "Current Stage") | .name] | first // ""),
            target: ([.fieldValues.nodes[] | select(.field.name == "Target Stage") | .name] | first // ""),
            group: ([.fieldValues.nodes[] | select(.field.name == "Functional Group") | .name] | first // ""),
            coverage: ([.fieldValues.nodes[] | select(.field.name == "Test Coverage") | .number] | first // 0),
            blockers: ([.fieldValues.nodes[] | select(.field.name == "Blocker Count") | .number] | first // 0),
            updated: ([.fieldValues.nodes[] | select(.field.name == "Last Updated") | .date] | first // "")
        } |
        [.number, .title, .state, .stage, .target, .group, .coverage, .blockers, .updated, .url] |
        @csv
    '
}

# Main execution
main() {
    load_config
    fetch_project_data

    display_summary

    if [ "$SUMMARY_ONLY" = false ]; then
        case $OUTPUT_FORMAT in
            table)
                display_table
                ;;
            json)
                display_json
                ;;
            csv)
                display_csv
                ;;
            *)
                echo -e "${RED}✗${NC} Unknown format: $OUTPUT_FORMAT"
                exit 1
                ;;
        esac
    fi
}

main
