#!/bin/bash
# Convenience wrapper for component promotion workflow
# Creates promotion issue and adds to project board
# Usage: project-promote-component.sh <component_name> <target_stage>

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
OWNER="theinterneti"
REPO="TTA"

# Help text
show_help() {
    cat << EOF
Usage: $(basename "$0") <component_name> <target_stage> [OPTIONS]

Create a promotion request issue and add it to the project board.

ARGUMENTS:
    component_name          Component to promote (e.g., "Model Management")
    target_stage            Target stage (Staging|Production)

OPTIONS:
    -h, --help              Show this help message
    -c, --coverage NUM      Current test coverage percentage
    -b, --blockers NUM      Number of known blockers
    -g, --group GROUP       Functional group (Core|AI|Player|Therapeutic)
    --dry-run               Show what would be created without making changes

EXAMPLES:
    # Promote Model Management to Staging
    $(basename "$0") "Model Management" Staging --coverage 100 --group AI

    # Promote Carbon to Production
    $(basename "$0") "Carbon" Production --coverage 95 --group Core

    # Dry run
    $(basename "$0") "Gameplay Loop" Staging --dry-run

EOF
}

# Parse arguments
COMPONENT_NAME=""
TARGET_STAGE=""
TEST_COVERAGE=""
BLOCKER_COUNT="0"
FUNCTIONAL_GROUP=""
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
        -c|--coverage)
            TEST_COVERAGE="$2"
            shift 2
            ;;
        -b|--blockers)
            BLOCKER_COUNT="$2"
            shift 2
            ;;
        -g|--group)
            FUNCTIONAL_GROUP="$2"
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
            if [ -z "$COMPONENT_NAME" ]; then
                COMPONENT_NAME="$1"
            elif [ -z "$TARGET_STAGE" ]; then
                TARGET_STAGE="$1"
            else
                echo -e "${RED}✗${NC} Unexpected argument: $1"
                show_help
                exit 1
            fi
            shift
            ;;
    esac
done

# Validate arguments
if [ -z "$COMPONENT_NAME" ] || [ -z "$TARGET_STAGE" ]; then
    echo -e "${RED}✗${NC} Component name and target stage required"
    show_help
    exit 1
fi

# Validate target stage
case $TARGET_STAGE in
    Staging|Production)
        ;;
    *)
        echo -e "${RED}✗${NC} Invalid target stage: $TARGET_STAGE (use Staging|Production)"
        exit 1
        ;;
esac

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

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Determine current stage
determine_current_stage() {
    case $TARGET_STAGE in
        Staging)
            CURRENT_STAGE="Development"
            ;;
        Production)
            CURRENT_STAGE="Staging"
            ;;
    esac
}

# Create issue body
create_issue_body() {
    cat << EOF
## Component: $COMPONENT_NAME

**Current Environment:** $CURRENT_STAGE
**Target Environment:** $TARGET_STAGE
EOF

    if [ -n "$TEST_COVERAGE" ]; then
        echo "**Test Coverage:** $TEST_COVERAGE%"
    fi

    if [ -n "$FUNCTIONAL_GROUP" ]; then
        echo "**Functional Group:** $FUNCTIONAL_GROUP"
    fi

    cat << EOF

### Promotion Criteria

EOF

    if [ "$TARGET_STAGE" = "Staging" ]; then
        cat << EOF
- [ ] Test coverage ≥70%
- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] No critical linting errors
- [ ] No critical type errors
- [ ] README documentation complete
- [ ] MATURITY.md updated

EOF
    else
        cat << EOF
- [ ] Test coverage ≥80%
- [ ] All tests passing (unit, integration, E2E)
- [ ] 7-day staging validation complete
- [ ] Performance benchmarks met
- [ ] Security audit passed
- [ ] Production deployment plan reviewed
- [ ] Rollback procedure documented
- [ ] Monitoring and alerting configured

EOF
    fi

    if [ "$BLOCKER_COUNT" != "0" ]; then
        cat << EOF
### Known Blockers

This component has $BLOCKER_COUNT known blocker(s). See related issues with label \`blocker:$COMPONENT_NAME\`.

EOF
    fi

    cat << EOF
### Acceptance Criteria

- ✅ All promotion criteria met
- ✅ Component maturity workflow validation passed
- ✅ Stakeholder approval obtained

### Related

- Component maturity workflow: \`docs/development/COMPONENT_MATURITY_WORKFLOW.md\`
- Promotion guide: \`docs/development/COMPONENT_PROMOTION_GUIDE.md\`

---

*This promotion request was created by: \`scripts/project-promote-component.sh\`*
EOF
}

# Create promotion issue
create_promotion_issue() {
    local title="[PROMOTION] $COMPONENT_NAME: $CURRENT_STAGE → $TARGET_STAGE"
    local body=$(create_issue_body)
    local labels="promotion:requested"

    if [ -n "$FUNCTIONAL_GROUP" ]; then
        case $FUNCTIONAL_GROUP in
            Core)
                labels="$labels,component:core-infrastructure"
                ;;
            AI)
                labels="$labels,component:ai-agent"
                ;;
            Player)
                labels="$labels,component:player-experience"
                ;;
            Therapeutic)
                labels="$labels,component:therapeutic"
                ;;
        esac
    fi

    if [ "$DRY_RUN" = true ]; then
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo -e "${CYAN}[DRY RUN] Would Create Issue${NC}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo -e "${BLUE}Title:${NC} $title"
        echo -e "${BLUE}Labels:${NC} $labels"
        echo ""
        echo -e "${BLUE}Body:${NC}"
        echo "$body"
        echo ""
        return 0
    fi

    log_info "Creating promotion issue..."

    ISSUE_URL=$(gh issue create \
        --repo "$OWNER/$REPO" \
        --title "$title" \
        --body "$body" \
        --label "$labels")

    ISSUE_NUMBER=$(echo "$ISSUE_URL" | grep -oP '\d+$')

    log_success "Created issue #$ISSUE_NUMBER"
    echo "  URL: $ISSUE_URL"
}

# Add to project board
add_to_project() {
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would add issue to project board"
        return 0
    fi

    log_info "Adding issue to project board..."

    # Build command
    CMD="scripts/project-add-issue.sh $ISSUE_NUMBER --stage $CURRENT_STAGE --target $TARGET_STAGE"

    if [ -n "$TEST_COVERAGE" ]; then
        CMD="$CMD --coverage $TEST_COVERAGE"
    fi

    if [ -n "$BLOCKER_COUNT" ]; then
        CMD="$CMD --blockers $BLOCKER_COUNT"
    fi

    if [ -n "$FUNCTIONAL_GROUP" ]; then
        CMD="$CMD --group $FUNCTIONAL_GROUP"
    fi

    # Execute
    if ! $CMD; then
        log_warning "Failed to add to project board automatically"
        echo "You can add it manually with:"
        echo "  $CMD"
    else
        log_success "Added to project board"
    fi
}

# Trigger validation workflow
trigger_validation() {
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would trigger validation workflow"
        return 0
    fi

    log_info "Validation workflow will run automatically on label 'promotion:requested'"
    log_info "Monitor progress at: https://github.com/$OWNER/$REPO/actions"
}

# Main execution
main() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${BLUE}Component Promotion Request${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    determine_current_stage

    echo -e "${BLUE}Component:${NC} $COMPONENT_NAME"
    echo -e "${BLUE}Promotion:${NC} $CURRENT_STAGE → $TARGET_STAGE"
    if [ -n "$TEST_COVERAGE" ]; then
        echo -e "${BLUE}Test Coverage:${NC} $TEST_COVERAGE%"
    fi
    if [ -n "$FUNCTIONAL_GROUP" ]; then
        echo -e "${BLUE}Functional Group:${NC} $FUNCTIONAL_GROUP"
    fi
    if [ "$BLOCKER_COUNT" != "0" ]; then
        echo -e "${YELLOW}Blockers:${NC} $BLOCKER_COUNT"
    fi
    echo ""

    create_promotion_issue

    if [ "$DRY_RUN" = false ]; then
        add_to_project
        trigger_validation

        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo -e "${GREEN}✓ Promotion Request Created!${NC}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "Next steps:"
        echo "  1. Monitor validation: https://github.com/$OWNER/$REPO/actions"
        echo "  2. Address any blockers identified"
        echo "  3. Wait for approval from stakeholders"
        echo "  4. Deploy to $TARGET_STAGE when approved"
        echo ""
    fi
}

main
