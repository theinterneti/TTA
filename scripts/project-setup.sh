#!/bin/bash
# TTA Component Maturity Tracker - Project Setup Script
# Creates GitHub Project V2 with all required custom fields
# Safe to run multiple times (idempotent)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
OWNER="theinterneti"
PROJECT_TITLE="TTA Component Maturity Tracker"
CONFIG_FILE=".github/project-config.env"
CONFIG_TEMPLATE=".github/project-config.env.template"

# Help text
show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Create and configure the TTA Component Maturity Tracker GitHub Project V2.
This script is idempotent - safe to run multiple times.

OPTIONS:
    -h, --help              Show this help message
    -p, --project-number N  Use existing project number N (skip creation)
    -s, --save-config       Save configuration to $CONFIG_FILE
    -v, --validate-only     Only validate existing setup
    --dry-run               Show what would be done without making changes

EXAMPLES:
    # First-time setup (creates project and fields)
    $(basename "$0") --save-config

    # Use existing project #1
    $(basename "$0") --project-number 1 --save-config

    # Validate existing setup
    $(basename "$0") --validate-only

EOF
}

# Load configuration
load_config() {
    if [ ! -f "$CONFIG_FILE" ]; then
        log_error "Configuration file not found: $CONFIG_FILE"
        echo "Run: scripts/project-setup.sh --save-config"
        return 1
    fi

    source "$CONFIG_FILE"

    # Validate required variables
    if [ -z "$PROJECT_ID" ]; then
        log_error "PROJECT_ID not set in $CONFIG_FILE"
        return 1
    fi

    return 0
}

# Parse arguments
PROJECT_NUMBER=""
SAVE_CONFIG=false
VALIDATE_ONLY=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -p|--project-number)
            PROJECT_NUMBER="$2"
            shift 2
            ;;
        -s|--save-config)
            SAVE_CONFIG=true
            shift
            ;;
        -v|--validate-only)
            VALIDATE_ONLY=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            echo -e "${RED}Error: Unknown option $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Utility functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    if ! command -v gh &> /dev/null; then
        log_error "GitHub CLI (gh) is not installed"
        echo "Install it from: https://cli.github.com/"
        exit 1
    fi

    if ! command -v jq &> /dev/null; then
        log_error "jq is not installed"
        echo "Install it with: sudo apt-get install jq"
        exit 1
    fi

    # Check gh auth
    if ! gh auth status &> /dev/null; then
        log_error "Not authenticated with GitHub CLI"
        echo "Run: gh auth login"
        exit 1
    fi

    log_success "Prerequisites OK"
}

# Get user ID
get_user_id() {
    log_info "Getting user ID..."
    USER_ID=$(gh api graphql -f query='
        query {
            viewer {
                id
                login
            }
        }
    ' | jq -r '.data.viewer.id')

    if [ -z "$USER_ID" ]; then
        log_error "Failed to get user ID"
        exit 1
    fi

    log_success "User ID: $USER_ID"
}

# Find existing project
find_existing_project() {
    log_info "Searching for existing project '$PROJECT_TITLE'..."

    EXISTING_PROJECT=$(gh api graphql -f query='
        query($owner: String!) {
            user(login: $owner) {
                projectsV2(first: 20) {
                    nodes {
                        id
                        number
                        title
                    }
                }
            }
        }
    ' -f owner="$OWNER" | jq -r --arg title "$PROJECT_TITLE" '
        .data.user.projectsV2.nodes[] | select(.title == $title) | {id, number}
    ')

    if [ -n "$EXISTING_PROJECT" ]; then
        PROJECT_ID=$(echo "$EXISTING_PROJECT" | jq -r '.id')
        PROJECT_NUMBER=$(echo "$EXISTING_PROJECT" | jq -r '.number')
        log_success "Found existing project #$PROJECT_NUMBER"
        return 0
    else
        log_warning "Project not found"
        return 1
    fi
}

# Create project
create_project() {
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would create project: $PROJECT_TITLE"
        return 0
    fi

    log_info "Creating project '$PROJECT_TITLE'..."

    RESULT=$(gh api graphql -f query='
        mutation($ownerId: ID!, $title: String!) {
            createProjectV2(input: {
                ownerId: $ownerId
                title: $title
            }) {
                projectV2 {
                    id
                    number
                    url
                }
            }
        }
    ' -f ownerId="$USER_ID" -f title="$PROJECT_TITLE")

    PROJECT_ID=$(echo "$RESULT" | jq -r '.data.createProjectV2.projectV2.id')
    PROJECT_NUMBER=$(echo "$RESULT" | jq -r '.data.createProjectV2.projectV2.number')
    PROJECT_URL=$(echo "$RESULT" | jq -r '.data.createProjectV2.projectV2.url')

    if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "null" ]; then
        log_error "Failed to create project"
        echo "$RESULT" | jq .
        exit 1
    fi

    log_success "Created project #$PROJECT_NUMBER"
    log_info "URL: $PROJECT_URL"
}

# Get existing fields
get_existing_fields() {
    gh api graphql -f query='
        query($owner: String!, $number: Int!) {
            user(login: $owner) {
                projectV2(number: $number) {
                    fields(first: 50) {
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
    ' -f owner="$OWNER" -F number="$PROJECT_NUMBER"
}

# Create custom field
create_field() {
    local field_name="$1"
    local field_type="$2"
    shift 2
    local options=("$@")

    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would create field: $field_name ($field_type)"
        return 0
    fi

    log_info "Creating field: $field_name ($field_type)..."

    # Build mutation based on field type
    if [ "$field_type" = "SINGLE_SELECT" ]; then
        # Build options JSON
        local options_json="["
        for opt in "${options[@]}"; do
            IFS='|' read -r name color desc <<< "$opt"
            options_json+="{name: \"$name\", color: $color, description: \"$desc\"},"
        done
        options_json="${options_json%,}]"

        RESULT=$(gh api graphql -f query="
            mutation {
                createProjectV2Field(input: {
                    projectId: \"$PROJECT_ID\"
                    dataType: $field_type
                    name: \"$field_name\"
                    singleSelectOptions: $options_json
                }) {
                    projectV2Field {
                        ... on ProjectV2SingleSelectField {
                            id
                            name
                        }
                    }
                }
            }
        ")
    else
        RESULT=$(gh api graphql -f query="
            mutation {
                createProjectV2Field(input: {
                    projectId: \"$PROJECT_ID\"
                    dataType: $field_type
                    name: \"$field_name\"
                }) {
                    projectV2Field {
                        ... on ProjectV2Field {
                            id
                            name
                        }
                    }
                }
            }
        ")
    fi

    FIELD_ID=$(echo "$RESULT" | jq -r '.data.createProjectV2Field.projectV2Field.id')

    if [ -z "$FIELD_ID" ] || [ "$FIELD_ID" = "null" ]; then
        # Check if error is "already exists"
        ERROR_MSG=$(echo "$RESULT" | jq -r '.errors[0].message // empty')
        if [[ "$ERROR_MSG" == *"already been taken"* ]]; then
            log_warning "Field '$field_name' already exists"
            return 0
        else
            log_error "Failed to create field '$field_name'"
            echo "$RESULT" | jq .
            return 1
        fi
    fi

    log_success "Created field: $field_name"
}

# Setup all required fields
setup_fields() {
    log_info "Setting up custom fields..."

    # Current Stage (single-select)
    create_field "Current Stage" "SINGLE_SELECT" \
        "Development|GRAY|Component in active development" \
        "Staging|YELLOW|Component deployed to staging for validation" \
        "Production|GREEN|Component deployed to production"

    # Target Stage (single-select)
    create_field "Target Stage" "SINGLE_SELECT" \
        "Staging|YELLOW|Promotion target: Staging" \
        "Production|GREEN|Promotion target: Production"

    # Functional Group (single-select)
    create_field "Functional Group" "SINGLE_SELECT" \
        "Core Infrastructure|BLUE|Neo4j, Docker, Carbon" \
        "AI/Agent Systems|PURPLE|Model Management, LLM, Agent Orchestration" \
        "Player Experience|PINK|Gameplay Loop, Character Arc, Player Interface" \
        "Therapeutic Content|ORANGE|Narrative Coherence, Therapeutic Systems"

    # Test Coverage (number)
    create_field "Test Coverage" "NUMBER"

    # Blocker Count (number)
    create_field "Blocker Count" "NUMBER"

    # Last Updated (date)
    create_field "Last Updated" "DATE"

    log_success "All fields configured"
}

# Display configuration
display_configuration() {
    log_info "Retrieving final configuration..."

    FIELDS_DATA=$(get_existing_fields)

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${GREEN}✓ Project Setup Complete${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${BLUE}Project Information:${NC}"
    echo "  Title: $PROJECT_TITLE"
    echo "  Number: #$PROJECT_NUMBER"
    echo "  ID: $PROJECT_ID"
    echo ""
    echo -e "${BLUE}Custom Fields:${NC}"
    echo "$FIELDS_DATA" | jq -r '.data.user.projectV2.fields.nodes[] |
        select(.name | IN("Current Stage", "Target Stage", "Functional Group", "Test Coverage", "Blocker Count", "Last Updated")) |
        "  \(.name):\n    ID: \(.id)\n    Type: \(.dataType)" +
        (if .options then "\n    Options:\n" + (.options | map("      - \(.name): \(.id)") | join("\n")) else "" end) + "\n"'
    echo ""
}

# Save configuration to file
save_configuration() {
    if [ "$SAVE_CONFIG" = false ]; then
        log_info "Skipping config save (use --save-config to enable)"
        return 0
    fi

    log_info "Saving configuration to $CONFIG_FILE..."

    FIELDS_DATA=$(get_existing_fields)

    # Extract field IDs
    FIELD_CURRENT_STAGE_ID=$(echo "$FIELDS_DATA" | jq -r '.data.user.projectV2.fields.nodes[] | select(.name == "Current Stage") | .id')
    FIELD_TARGET_STAGE_ID=$(echo "$FIELDS_DATA" | jq -r '.data.user.projectV2.fields.nodes[] | select(.name == "Target Stage") | .id')
    FIELD_FUNCTIONAL_GROUP_ID=$(echo "$FIELDS_DATA" | jq -r '.data.user.projectV2.fields.nodes[] | select(.name == "Functional Group") | .id')
    FIELD_TEST_COVERAGE_ID=$(echo "$FIELDS_DATA" | jq -r '.data.user.projectV2.fields.nodes[] | select(.name == "Test Coverage") | .id')
    FIELD_BLOCKER_COUNT_ID=$(echo "$FIELDS_DATA" | jq -r '.data.user.projectV2.fields.nodes[] | select(.name == "Blocker Count") | .id')
    FIELD_LAST_UPDATED_ID=$(echo "$FIELDS_DATA" | jq -r '.data.user.projectV2.fields.nodes[] | select(.name == "Last Updated") | .id')

    # Extract option IDs for Current Stage
    OPTION_DEVELOPMENT_ID=$(echo "$FIELDS_DATA" | jq -r '.data.user.projectV2.fields.nodes[] | select(.name == "Current Stage") | .options[] | select(.name == "Development") | .id')
    OPTION_STAGING_ID=$(echo "$FIELDS_DATA" | jq -r '.data.user.projectV2.fields.nodes[] | select(.name == "Current Stage") | .options[] | select(.name == "Staging") | .id')
    OPTION_PRODUCTION_ID=$(echo "$FIELDS_DATA" | jq -r '.data.user.projectV2.fields.nodes[] | select(.name == "Current Stage") | .options[] | select(.name == "Production") | .id')

    # Extract option IDs for Target Stage
    OPTION_TARGET_STAGING_ID=$(echo "$FIELDS_DATA" | jq -r '.data.user.projectV2.fields.nodes[] | select(.name == "Target Stage") | .options[] | select(.name == "Staging") | .id')
    OPTION_TARGET_PRODUCTION_ID=$(echo "$FIELDS_DATA" | jq -r '.data.user.projectV2.fields.nodes[] | select(.name == "Target Stage") | .options[] | select(.name == "Production") | .id')

    # Extract option IDs for Functional Group
    OPTION_CORE_INFRA_ID=$(echo "$FIELDS_DATA" | jq -r '.data.user.projectV2.fields.nodes[] | select(.name == "Functional Group") | .options[] | select(.name == "Core Infrastructure") | .id')
    OPTION_AI_AGENT_ID=$(echo "$FIELDS_DATA" | jq -r '.data.user.projectV2.fields.nodes[] | select(.name == "Functional Group") | .options[] | select(.name == "AI/Agent Systems") | .id')
    OPTION_PLAYER_EXP_ID=$(echo "$FIELDS_DATA" | jq -r '.data.user.projectV2.fields.nodes[] | select(.name == "Functional Group") | .options[] | select(.name == "Player Experience") | .id')
    OPTION_THERAPEUTIC_ID=$(echo "$FIELDS_DATA" | jq -r '.data.user.projectV2.fields.nodes[] | select(.name == "Functional Group") | .options[] | select(.name == "Therapeutic Content") | .id')

    # Create config file
    cat > "$CONFIG_FILE" << EOF
# GitHub Project V2 Configuration
# Generated by scripts/project-setup.sh on $(date)
# DO NOT commit this file to git (should be in .gitignore)

# Project ID
PROJECT_ID=$PROJECT_ID
PROJECT_NUMBER=$PROJECT_NUMBER

# Field IDs
FIELD_CURRENT_STAGE_ID=$FIELD_CURRENT_STAGE_ID
FIELD_TARGET_STAGE_ID=$FIELD_TARGET_STAGE_ID
FIELD_BLOCKER_COUNT_ID=$FIELD_BLOCKER_COUNT_ID
FIELD_TEST_COVERAGE_ID=$FIELD_TEST_COVERAGE_ID
FIELD_LAST_UPDATED_ID=$FIELD_LAST_UPDATED_ID
FIELD_FUNCTIONAL_GROUP_ID=$FIELD_FUNCTIONAL_GROUP_ID

# Option IDs for Current Stage field
OPTION_DEVELOPMENT_ID=$OPTION_DEVELOPMENT_ID
OPTION_STAGING_ID=$OPTION_STAGING_ID
OPTION_PRODUCTION_ID=$OPTION_PRODUCTION_ID

# Option IDs for Target Stage field
OPTION_TARGET_STAGING_ID=$OPTION_TARGET_STAGING_ID
OPTION_TARGET_PRODUCTION_ID=$OPTION_TARGET_PRODUCTION_ID

# Option IDs for Functional Group field
OPTION_CORE_INFRA_ID=$OPTION_CORE_INFRA_ID
OPTION_AI_AGENT_ID=$OPTION_AI_AGENT_ID
OPTION_PLAYER_EXP_ID=$OPTION_PLAYER_EXP_ID
OPTION_THERAPEUTIC_ID=$OPTION_THERAPEUTIC_ID
EOF

    log_success "Configuration saved to $CONFIG_FILE"

    # Ensure it's in .gitignore
    if ! grep -q "^.github/project-config.env$" .gitignore 2>/dev/null; then
        echo ".github/project-config.env" >> .gitignore
        log_success "Added $CONFIG_FILE to .gitignore"
    fi
}

# Validate setup
validate_setup() {
    log_info "Validating setup..."

    local errors=0

    # Check project exists
    if [ -z "$PROJECT_ID" ]; then
        log_error "Project ID not found"
        ((errors++))
    fi

    # Check required fields exist
    FIELDS_DATA=$(get_existing_fields)
    REQUIRED_FIELDS=("Current Stage" "Target Stage" "Functional Group" "Test Coverage" "Blocker Count" "Last Updated")

    for field in "${REQUIRED_FIELDS[@]}"; do
        if ! echo "$FIELDS_DATA" | jq -e ".data.user.projectV2.fields.nodes[] | select(.name == \"$field\")" > /dev/null; then
            log_error "Required field missing: $field"
            ((errors++))
        fi
    done

    if [ $errors -eq 0 ]; then
        log_success "Validation passed"
        return 0
    else
        log_error "Validation failed with $errors error(s)"
        return 1
    fi
}

# Main execution
main() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${BLUE}TTA Component Maturity Tracker - Project Setup${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    check_prerequisites
    get_user_id

    if [ "$VALIDATE_ONLY" = true ]; then
        # Load existing configuration
        if ! load_config; then
            exit 1
        fi

        # If project number not specified, try to use from config
        if [ -z "$PROJECT_NUMBER" ]; then
            if [ -n "$PROJECT_NUMBER" ]; then
                log_info "Using project #$PROJECT_NUMBER from config"
            elif ! find_existing_project; then
                log_error "No project found and no project number specified"
                exit 1
            fi
        fi
        validate_setup
        exit $?
    fi

    # Find or create project
    if [ -n "$PROJECT_NUMBER" ]; then
        log_info "Using specified project #$PROJECT_NUMBER"
        EXISTING_PROJECT=$(gh api graphql -f query='
            query($owner: String!, $number: Int!) {
                user(login: $owner) {
                    projectV2(number: $number) {
                        id
                        title
                    }
                }
            }
        ' -f owner="$OWNER" -F number="$PROJECT_NUMBER")

        PROJECT_ID=$(echo "$EXISTING_PROJECT" | jq -r '.data.user.projectV2.id')
        if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "null" ]; then
            log_error "Project #$PROJECT_NUMBER not found"
            exit 1
        fi
        log_success "Found project #$PROJECT_NUMBER"
    else
        if ! find_existing_project; then
            create_project
        fi
    fi

    # Setup fields
    setup_fields

    # Display and save configuration
    display_configuration
    save_configuration

    # Validate
    validate_setup

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${GREEN}✓ Setup Complete!${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Next steps:"
    echo "  1. View your project: https://github.com/users/$OWNER/projects/$PROJECT_NUMBER"
    if [ "$SAVE_CONFIG" = true ]; then
        echo "  2. Configuration saved to: $CONFIG_FILE"
        echo "  3. Configure GitHub Secrets for CI/CD automation"
    else
        echo "  2. Run with --save-config to save configuration"
    fi
    echo "  4. Use scripts/project-add-issue.sh to add issues"
    echo "  5. Use scripts/project-status.sh to view project status"
    echo ""
}

main
