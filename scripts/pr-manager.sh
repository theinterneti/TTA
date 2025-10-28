#!/bin/bash
# PR Management Helper Script
# Provides CLI tools for managing PRs with automation

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
error() {
    echo -e "${RED}ERROR: $1${NC}" >&2
    exit 1
}

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if gh CLI is installed
check_gh_cli() {
    if ! command -v gh &> /dev/null; then
        error "GitHub CLI (gh) is not installed. Install from: https://cli.github.com/"
    fi
}

# List all open PRs
list_prs() {
    info "Fetching open PRs..."
    gh pr list --state open --json number,title,author,createdAt,updatedAt,reviewDecision,statusCheckRollup \
        --template '{{range .}}{{printf "#%v" .number | color "blue"}} - {{.title}} (@{{.author.login}})
  Created: {{timeago .createdAt}} | Updated: {{timeago .updatedAt}}
  Review: {{.reviewDecision | color "yellow"}} | Checks: {{.statusCheckRollup | len}} pending
{{end}}'
}

# Get PR details
pr_details() {
    local pr_number="$1"

    info "Fetching details for PR #${pr_number}..."
    gh pr view "$pr_number" --json title,author,body,reviewDecision,reviews,statusCheckRollup,labels,comments \
        --template '# {{.title}}

**Author**: @{{.author.login}}
**Review Decision**: {{.reviewDecision}}
**Labels**: {{range .labels}}{{.name}} {{end}}

## Description
{{.body}}

## Reviews ({{.reviews | len}})
{{range .reviews}}
- {{.author.login}}: {{.state}} ({{timeago .submittedAt}})
{{end}}

## Status Checks ({{.statusCheckRollup | len}})
{{range .statusCheckRollup}}
- {{.name}}: {{.conclusion}}
{{end}}

## Comments ({{.comments | len}})
{{range .comments}}
---
**{{.author.login}}** ({{timeago .createdAt}}):
{{.body}}
{{end}}
'
}

# Approve PR with optional comment
approve_pr() {
    local pr_number="$1"
    local comment="${2:-LGTM! ✅}"

    info "Approving PR #${pr_number}..."
    gh pr review "$pr_number" --approve --body "$comment"
    success "PR #${pr_number} approved!"
}

# Request changes on PR
request_changes() {
    local pr_number="$1"
    local comment="${2:-Please address the feedback}"

    warning "Requesting changes on PR #${pr_number}..."
    gh pr review "$pr_number" --request-changes --body "$comment"
    success "Change request submitted for PR #${pr_number}"
}

# Enable auto-merge for PR
enable_automerge() {
    local pr_number="$1"

    info "Enabling auto-merge for PR #${pr_number}..."
    gh pr merge "$pr_number" --auto --squash
    success "Auto-merge enabled for PR #${pr_number}"
}

# Disable auto-merge for PR
disable_automerge() {
    local pr_number="$1"

    info "Disabling auto-merge for PR #${pr_number}..."
    gh pr merge "$pr_number" --disable-auto
    success "Auto-merge disabled for PR #${pr_number}"
}

# Merge PR immediately (skip auto-merge)
merge_pr() {
    local pr_number="$1"
    local method="${2:-squash}"  # squash, merge, or rebase

    warning "Merging PR #${pr_number} immediately (method: ${method})..."
    gh pr merge "$pr_number" "--${method}" --delete-branch
    success "PR #${pr_number} merged!"
}

# Check Copilot review status
check_copilot_review() {
    local pr_number="$1"

    info "Checking Copilot review for PR #${pr_number}..."

    # Get review comments
    local comments
    comments=$(gh api "/repos/{owner}/{repo}/pulls/${pr_number}/comments" \
        --jq '[.[] | select(.user.login | contains("copilot"))] | length')

    if [ "$comments" -eq 0 ]; then
        success "No Copilot review comments found"
    else
        warning "${comments} Copilot review comments found"

        # Show unresolved comments
        gh api "/repos/{owner}/{repo}/pulls/${pr_number}/comments" \
            --jq '.[] | select(.user.login | contains("copilot")) | select(.resolved == false) | "- \(.path):\(.line) - \(.body | .[0:100])..."'
    fi
}

# Auto-resolve Copilot comments on modified files
auto_resolve_copilot() {
    local pr_number="$1"

    info "Auto-resolving Copilot comments on modified files for PR #${pr_number}..."

    # Get all unresolved Copilot comments (top-level only)
    local comments
    comments=$(gh api "/repos/{owner}/{repo}/pulls/${pr_number}/comments" \
        --jq '[.[] | select(.user.login | contains("copilot")) | select(.in_reply_to_id == null)]')

    local total=$(echo "$comments" | jq 'length')

    if [ "$total" -eq 0 ]; then
        info "No unresolved Copilot comments found"
        return
    fi

    # Get modified files in PR
    local modified_files
    modified_files=$(gh pr view "$pr_number" --json files --jq '.files[].path')

    local resolved=0
    local comment_ids=$(echo "$comments" | jq -r '.[] | @json')

    while IFS= read -r comment_json; do
        local cid=$(echo "$comment_json" | jq -r '.id')
        local cpath=$(echo "$comment_json" | jq -r '.path')

        # Check if file was modified
        if echo "$modified_files" | grep -q "^${cpath}$"; then
            # Check if already has resolution reply
            local has_reply=$(gh api "/repos/{owner}/{repo}/pulls/comments/${cid}" \
                --jq '.body | contains("✅ Auto-resolved") or contains("✅ Resolved")')

            if [ "$has_reply" = "true" ]; then
                continue
            fi

            # Add resolution reply
            gh api "/repos/{owner}/{repo}/pulls/${pr_number}/comments/${cid}/replies" \
                -X POST \
                -f body='✅ **Auto-resolved**: File was modified to address this feedback.

ℹ️ If this issue persists, Copilot will comment again on the next review.' \
                >/dev/null 2>&1

            if [ $? -eq 0 ]; then
                ((resolved++))
                info "Resolved comment on ${cpath}"
            fi
        fi
    done < <(echo "$comments" | jq -c '.[]')

    local remaining=$((total - resolved))

    if [ $resolved -gt 0 ]; then
        success "Auto-resolved ${resolved}/${total} Copilot comment(s)"
    fi

    if [ $remaining -gt 0 ]; then
        warning "${remaining} comment(s) remain (files not modified or already resolved)"
    fi
}

# Bulk approve all ready PRs
bulk_approve() {
    info "Finding PRs ready for approval..."

    local prs
    prs=$(gh pr list --state open --json number,statusCheckRollup,reviewDecision \
        --jq '.[] | select(.statusCheckRollup | all(.conclusion == "success")) | select(.reviewDecision != "APPROVED") | .number')

    if [ -z "$prs" ]; then
        info "No PRs ready for approval"
        return
    fi

    echo "PRs ready for approval:"
    echo "$prs"

    read -p "Approve all? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        for pr in $prs; do
            approve_pr "$pr" "✅ Auto-approved: All checks passing"
        done
        success "Approved all ready PRs"
    fi
}

# Watch PR status (continuous monitoring)
watch_pr() {
    local pr_number="$1"
    local interval="${2:-30}"

    info "Watching PR #${pr_number} (updates every ${interval}s, Ctrl+C to stop)..."

    while true; do
        clear
        echo "=== PR #${pr_number} Status ($(date)) ==="
        pr_details "$pr_number"
        sleep "$interval"
    done
}

# Show PR workflow status
workflow_status() {
    local pr_number="$1"

    info "Fetching workflow runs for PR #${pr_number}..."
    gh run list --workflow=pr-automation.yml --json number,status,conclusion,createdAt \
        --template '{{range .}}Run #{{.number}}: {{.status}} ({{.conclusion}}) - {{timeago .createdAt}}
{{end}}'
}

# Main menu
show_help() {
    cat << EOF
${BLUE}TTA PR Management Helper${NC}

${GREEN}Usage:${NC}
  $0 <command> [arguments]

${GREEN}Commands:${NC}
  ${YELLOW}list${NC}                           List all open PRs
  ${YELLOW}details${NC} <pr_number>            Show detailed PR information
  ${YELLOW}approve${NC} <pr_number> [comment]  Approve a PR
  ${YELLOW}changes${NC} <pr_number> [comment]  Request changes on a PR
  ${YELLOW}automerge${NC} <pr_number>          Enable auto-merge
  ${YELLOW}disable-auto${NC} <pr_number>       Disable auto-merge
  ${YELLOW}merge${NC} <pr_number> [method]     Merge PR immediately (squash/merge/rebase)
  ${YELLOW}copilot${NC} <pr_number>            Check Copilot review status
  ${YELLOW}resolve${NC} <pr_number>            Auto-resolve Copilot comments on modified files
  ${YELLOW}bulk-approve${NC}                   Approve all ready PRs
  ${YELLOW}watch${NC} <pr_number> [seconds]    Watch PR status continuously
  ${YELLOW}workflow${NC} <pr_number>           Show workflow run status

${GREEN}Examples:${NC}
  $0 list
  $0 details 73
  $0 approve 73 "Great work! 🎉"
  $0 automerge 73
  $0 copilot 73
  $0 resolve 73
  $0 bulk-approve
  $0 watch 73 30

${GREEN}Configuration:${NC}
  Requires GitHub CLI (gh) to be installed and authenticated.
  Run: ${YELLOW}gh auth login${NC}

EOF
}

# Main script
main() {
    check_gh_cli

    case "${1:-}" in
        list)
            list_prs
            ;;
        details)
            [ -z "${2:-}" ] && error "PR number required"
            pr_details "$2"
            ;;
        approve)
            [ -z "${2:-}" ] && error "PR number required"
            approve_pr "$2" "${3:-LGTM! ✅}"
            ;;
        changes)
            [ -z "${2:-}" ] && error "PR number required"
            request_changes "$2" "${3:-Please address the feedback}"
            ;;
        automerge)
            [ -z "${2:-}" ] && error "PR number required"
            enable_automerge "$2"
            ;;
        disable-auto)
            [ -z "${2:-}" ] && error "PR number required"
            disable_automerge "$2"
            ;;
        merge)
            [ -z "${2:-}" ] && error "PR number required"
            merge_pr "$2" "${3:-squash}"
            ;;
        copilot)
            [ -z "${2:-}" ] && error "PR number required"
            check_copilot_review "$2"
            ;;
        resolve)
            [ -z "${2:-}" ] && error "PR number required"
            auto_resolve_copilot "$2"
            ;;
        bulk-approve)
            bulk_approve
            ;;
        watch)
            [ -z "${2:-}" ] && error "PR number required"
            watch_pr "$2" "${3:-30}"
            ;;
        workflow)
            [ -z "${2:-}" ] && error "PR number required"
            workflow_status "$2"
            ;;
        help|--help|-h|"")
            show_help
            ;;
        *)
            error "Unknown command: $1. Run '$0 help' for usage."
            ;;
    esac
}

main "$@"
