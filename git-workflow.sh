#!/usr/bin/env bash
# Intelligent Branch, Commit, and Merge Helper for TTA
# This script helps manage git workflow with best practices

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

print_header() {
    echo -e "\n${BLUE}════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

# Get current branch
get_current_branch() {
    git branch --show-current
}

# Get default branch
get_default_branch() {
    git symbolic-ref refs/remotes/TTA/HEAD 2>/dev/null | sed 's@^refs/remotes/TTA/@@' || echo "main"
}

# Check if branch exists
branch_exists() {
    git show-ref --verify --quiet "refs/heads/$1"
}

# Show current status
show_status() {
    print_header "Current Git Status"
    
    local current_branch=$(get_current_branch)
    local default_branch=$(get_default_branch)
    
    echo "Current Branch: ${GREEN}$current_branch${NC}"
    echo "Default Branch: ${CYAN}$default_branch${NC}"
    echo "Repository: $(git remote get-url TTA 2>/dev/null || echo 'Unknown')"
    echo ""
    
    # Show uncommitted changes
    local staged=$(git diff --cached --name-only | wc -l)
    local unstaged=$(git diff --name-only | wc -l)
    local untracked=$(git ls-files --others --exclude-standard | wc -l)
    
    echo "Changes:"
    echo "  Staged:    ${GREEN}$staged${NC} files"
    echo "  Unstaged:  ${YELLOW}$unstaged${NC} files"
    echo "  Untracked: ${CYAN}$untracked${NC} files"
    
    # Show recent commits
    echo ""
    echo "Recent commits:"
    git log --oneline --graph -5 --color=always
}

# Create feature branch
create_feature_branch() {
    print_header "Create Feature Branch"
    
    local current_branch=$(get_current_branch)
    local base_branch="${1:-development}"
    
    echo "Current branch: $current_branch"
    echo "Base branch: $base_branch"
    echo ""
    
    # Update base branch
    print_info "Updating base branch: $base_branch"
    git fetch TTA "$base_branch"
    
    # Suggest branch name
    echo ""
    echo "Branch naming conventions:"
    echo "  feature/your-feature-name    - New features"
    echo "  fix/bug-description          - Bug fixes"
    echo "  docs/documentation-update    - Documentation"
    echo "  test/testing-improvements    - Tests"
    echo "  refactor/code-refactoring    - Refactoring"
    echo "  chore/maintenance-task       - Maintenance"
    echo ""
    
    read -p "Enter new branch name: " branch_name
    
    if [ -z "$branch_name" ]; then
        print_error "Branch name cannot be empty"
        return 1
    fi
    
    if branch_exists "$branch_name"; then
        print_error "Branch '$branch_name' already exists"
        return 1
    fi
    
    # Create and checkout branch
    git checkout -b "$branch_name" "TTA/$base_branch"
    print_success "Created and switched to branch: $branch_name"
    
    # Show status
    git status --short
}

# Intelligent commit
smart_commit() {
    print_header "Smart Commit"
    
    # Check if there are changes
    if [ -z "$(git status --porcelain)" ]; then
        print_warning "No changes to commit"
        return 0
    fi
    
    # Show changes
    echo "Changes to commit:"
    git status --short
    echo ""
    
    # Suggest staging
    read -p "Stage all changes? (Y/n): " stage_all
    if [[ ! "$stage_all" =~ ^[Nn]$ ]]; then
        git add .
        print_success "Staged all changes"
    fi
    
    # Show what's staged
    local staged_count=$(git diff --cached --name-only | wc -l)
    if [ "$staged_count" -eq 0 ]; then
        print_warning "No files staged for commit"
        read -p "Stage specific files? (y/N): " stage_specific
        if [[ "$stage_specific" =~ ^[Yy]$ ]]; then
            git add -p
        else
            return 0
        fi
    fi
    
    echo ""
    echo "Staged files:"
    git diff --cached --name-only --color=always | head -20
    local remaining=$((staged_count - 20))
    if [ $remaining -gt 0 ]; then
        echo "... and $remaining more files"
    fi
    
    # Commit message guide
    echo ""
    echo "Conventional Commit Format:"
    echo "  ${GREEN}feat${NC}(scope): add new feature"
    echo "  ${YELLOW}fix${NC}(scope): fix bug"
    echo "  ${BLUE}docs${NC}(scope): update documentation"
    echo "  ${CYAN}test${NC}(scope): add tests"
    echo "  ${YELLOW}refactor${NC}(scope): refactor code"
    echo "  ${CYAN}chore${NC}(scope): maintenance"
    echo "  ${GREEN}ci${NC}(scope): CI/CD changes"
    echo ""
    
    # Get commit message
    read -p "Commit message: " commit_msg
    
    if [ -z "$commit_msg" ]; then
        print_error "Commit message cannot be empty"
        return 1
    fi
    
    # Add body if needed
    read -p "Add detailed description? (y/N): " add_body
    if [[ "$add_body" =~ ^[Yy]$ ]]; then
        echo "Enter description (Ctrl+D when done):"
        commit_body=$(cat)
        git commit -m "$commit_msg" -m "$commit_body"
    else
        git commit -m "$commit_msg"
    fi
    
    print_success "Committed changes"
    
    # Show the commit
    git log -1 --stat --color=always
}

# Sync with remote
sync_branch() {
    print_header "Sync Branch with Remote"
    
    local current_branch=$(get_current_branch)
    local base_branch="${1:-development}"
    
    echo "Current branch: $current_branch"
    echo "Base branch: $base_branch"
    echo ""
    
    # Fetch updates
    print_info "Fetching updates from remote..."
    git fetch TTA --prune
    
    # Check if base branch has updates
    local local_hash=$(git rev-parse "TTA/$base_branch" 2>/dev/null || echo "")
    local remote_hash=$(git rev-parse "TTA/$base_branch" 2>/dev/null || echo "")
    
    if [ -n "$local_hash" ] && [ "$local_hash" != "$remote_hash" ]; then
        print_warning "Base branch '$base_branch' has updates"
        
        # Show what's new
        echo ""
        echo "New commits in $base_branch:"
        git log --oneline "$current_branch..TTA/$base_branch" | head -10
        echo ""
        
        read -p "Rebase onto $base_branch? (Y/n): " do_rebase
        if [[ ! "$do_rebase" =~ ^[Nn]$ ]]; then
            print_info "Rebasing onto TTA/$base_branch..."
            if git rebase "TTA/$base_branch"; then
                print_success "Rebase successful"
            else
                print_error "Rebase had conflicts. Resolve them and run: git rebase --continue"
                return 1
            fi
        fi
    else
        print_success "Already up to date with $base_branch"
    fi
    
    # Push if needed
    if git rev-parse --verify "TTA/$current_branch" 2>/dev/null; then
        local behind=$(git rev-list --count "TTA/$current_branch..$current_branch" 2>/dev/null || echo "0")
        if [ "$behind" -gt 0 ]; then
            print_warning "Your branch is $behind commit(s) ahead of remote"
            read -p "Push to remote? (Y/n): " do_push
            if [[ ! "$do_push" =~ ^[Nn]$ ]]; then
                git push TTA "$current_branch"
                print_success "Pushed to remote"
            fi
        fi
    else
        print_info "Branch not on remote yet"
        read -p "Push to remote? (Y/n): " do_push
        if [[ ! "$do_push" =~ ^[Nn]$ ]]; then
            git push -u TTA "$current_branch"
            print_success "Pushed to remote and set upstream"
        fi
    fi
}

# Create pull request
create_pr() {
    print_header "Create Pull Request"
    
    local current_branch=$(get_current_branch)
    local base_branch="${1:-development}"
    
    if ! command -v gh &> /dev/null; then
        print_error "GitHub CLI (gh) not installed"
        echo "Install: https://cli.github.com/"
        return 1
    fi
    
    # Make sure branch is pushed
    if ! git rev-parse --verify "TTA/$current_branch" 2>/dev/null; then
        print_warning "Branch not pushed to remote"
        read -p "Push now? (Y/n): " do_push
        if [[ ! "$do_push" =~ ^[Nn]$ ]]; then
            git push -u TTA "$current_branch"
        else
            return 1
        fi
    fi
    
    echo "Creating PR: $current_branch → $base_branch"
    echo ""
    
    # Get PR title from recent commit
    local default_title=$(git log -1 --pretty=%s)
    read -p "PR Title [$default_title]: " pr_title
    pr_title=${pr_title:-$default_title}
    
    # Get PR body
    echo ""
    echo "PR Description (Ctrl+D when done, or press Enter for template):"
    local pr_body=$(cat)
    
    if [ -z "$pr_body" ]; then
        pr_body="## Description
<!-- Describe your changes -->

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings generated"
    fi
    
    # Ask about draft
    read -p "Create as draft PR? (y/N): " is_draft
    local draft_flag=""
    if [[ "$is_draft" =~ ^[Yy]$ ]]; then
        draft_flag="--draft"
    fi
    
    # Create PR
    gh pr create \
        --base "$base_branch" \
        --title "$pr_title" \
        --body "$pr_body" \
        $draft_flag
    
    print_success "Pull request created!"
    
    # Show PR
    gh pr view
}

# Merge strategies
merge_branch() {
    print_header "Merge Branch"
    
    local source_branch="${1:-$(get_current_branch)}"
    local target_branch="${2:-development}"
    
    echo "Source: $source_branch"
    echo "Target: $target_branch"
    echo ""
    
    # Fetch latest
    git fetch TTA --prune
    
    # Check if we're on target branch
    local current=$(get_current_branch)
    if [ "$current" != "$target_branch" ]; then
        print_info "Switching to $target_branch"
        git checkout "$target_branch"
    fi
    
    # Update target
    print_info "Updating $target_branch"
    git pull TTA "$target_branch"
    
    # Merge strategy
    echo ""
    echo "Merge strategies:"
    echo "  1) Merge commit (preserves history)"
    echo "  2) Squash merge (single commit)"
    echo "  3) Rebase merge (linear history)"
    echo ""
    read -p "Choose strategy (1-3): " strategy
    
    case $strategy in
        1)
            print_info "Performing merge commit..."
            git merge --no-ff "$source_branch" -m "merge: $source_branch into $target_branch"
            ;;
        2)
            print_info "Performing squash merge..."
            git merge --squash "$source_branch"
            echo "Enter commit message for squashed commit:"
            read squash_msg
            git commit -m "$squash_msg"
            ;;
        3)
            print_info "Performing rebase merge..."
            git rebase "$source_branch"
            ;;
        *)
            print_error "Invalid strategy"
            return 1
            ;;
    esac
    
    print_success "Merge complete"
    
    # Push
    read -p "Push to remote? (Y/n): " do_push
    if [[ ! "$do_push" =~ ^[Nn]$ ]]; then
        git push TTA "$target_branch"
        print_success "Pushed to remote"
    fi
}

# Branch cleanup
cleanup_branches() {
    print_header "Branch Cleanup"
    
    # Show merged branches
    echo "Merged branches (safe to delete):"
    git branch --merged | grep -v "\*" | grep -v "main" | grep -v "development" | grep -v "staging"
    echo ""
    
    read -p "Delete merged branches? (y/N): " do_delete
    if [[ "$do_delete" =~ ^[Yy]$ ]]; then
        git branch --merged | grep -v "\*" | grep -v "main" | grep -v "development" | grep -v "staging" | xargs -n 1 git branch -d
        print_success "Deleted merged branches"
    fi
    
    # Show stale remote branches
    echo ""
    echo "Stale remote-tracking branches:"
    git remote prune TTA --dry-run
    echo ""
    
    read -p "Prune stale remote branches? (y/N): " do_prune
    if [[ "$do_prune" =~ ^[Yy]$ ]]; then
        git remote prune TTA
        print_success "Pruned stale branches"
    fi
}

# Show menu
show_menu() {
    echo -e "\n${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║   Git Workflow Manager                 ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"
    
    echo "1) Show status"
    echo "2) Create feature branch"
    echo "3) Smart commit"
    echo "4) Sync with remote"
    echo "5) Create pull request"
    echo "6) Merge branch"
    echo "7) Cleanup branches"
    echo "8) View commit history"
    echo "9) Stash changes"
    echo "0) Quick workflow (commit + sync + PR)"
    echo "q) Quit"
    echo ""
    echo -n "Choose option: "
}

# View commit history
view_history() {
    print_header "Commit History"
    
    echo "Options:"
    echo "  1) Last 10 commits"
    echo "  2) Last 20 commits"
    echo "  3) Graph view (all branches)"
    echo "  4) Search commits"
    echo ""
    read -p "Choose (1-4): " choice
    
    case $choice in
        1) git log --oneline --graph -10 --color=always ;;
        2) git log --oneline --graph -20 --color=always ;;
        3) git log --oneline --graph --all --decorate --color=always | head -30 ;;
        4)
            read -p "Search for: " search_term
            git log --all --grep="$search_term" --oneline --color=always
            ;;
    esac
}

# Stash management
manage_stash() {
    print_header "Stash Management"
    
    echo "1) Stash changes"
    echo "2) List stashes"
    echo "3) Apply stash"
    echo "4) Pop stash"
    echo "5) Drop stash"
    echo ""
    read -p "Choose (1-5): " choice
    
    case $choice in
        1)
            read -p "Stash message: " msg
            git stash push -m "$msg"
            print_success "Changes stashed"
            ;;
        2)
            git stash list --color=always
            ;;
        3)
            git stash list --color=always
            read -p "Stash number (0): " num
            git stash apply "stash@{${num:-0}}"
            ;;
        4)
            git stash list --color=always
            read -p "Stash number (0): " num
            git stash pop "stash@{${num:-0}}"
            ;;
        5)
            git stash list --color=always
            read -p "Stash number (0): " num
            git stash drop "stash@{${num:-0}}"
            ;;
    esac
}

# Quick workflow
quick_workflow() {
    print_header "Quick Workflow (Commit + Sync + PR)"
    
    # Commit
    smart_commit || return 1
    
    # Sync
    echo ""
    sync_branch || return 1
    
    # PR
    echo ""
    read -p "Create pull request? (Y/n): " create_pr_choice
    if [[ ! "$create_pr_choice" =~ ^[Nn]$ ]]; then
        create_pr
    fi
    
    print_success "Workflow complete!"
}

# Main
main() {
    if [ $# -eq 0 ]; then
        # Interactive mode
        while true; do
            show_menu
            read -r choice
            case $choice in
                1) show_status ;;
                2) create_feature_branch ;;
                3) smart_commit ;;
                4) sync_branch ;;
                5) create_pr ;;
                6) merge_branch ;;
                7) cleanup_branches ;;
                8) view_history ;;
                9) manage_stash ;;
                0) quick_workflow ;;
                q|Q) 
                    print_success "Goodbye!"
                    exit 0
                    ;;
                *) print_error "Invalid option" ;;
            esac
            
            echo ""
            echo "Press Enter to continue..."
            read -r
        done
    else
        # Command line mode
        case "$1" in
            status) show_status ;;
            branch) create_feature_branch "$2" ;;
            commit) smart_commit ;;
            sync) sync_branch "$2" ;;
            pr) create_pr "$2" ;;
            merge) merge_branch "$2" "$3" ;;
            cleanup) cleanup_branches ;;
            history) view_history ;;
            stash) manage_stash ;;
            quick) quick_workflow ;;
            *)
                echo "Usage: $0 [command]"
                echo ""
                echo "Commands:"
                echo "  status              - Show current status"
                echo "  branch [base]       - Create feature branch"
                echo "  commit              - Smart commit"
                echo "  sync [base]         - Sync with remote"
                echo "  pr [base]           - Create pull request"
                echo "  merge [src] [tgt]   - Merge branches"
                echo "  cleanup             - Clean up branches"
                echo "  history             - View history"
                echo "  stash               - Manage stash"
                echo "  quick               - Quick workflow"
                echo ""
                echo "Run without arguments for interactive menu"
                exit 1
                ;;
        esac
    fi
}

main "$@"
