#!/bin/bash
# Git Pre-Commit Hook for Automated Testing
# Install: ln -s ../../pre-commit-keploy.sh .git/hooks/pre-commit

set -e

echo "🔍 Pre-Commit: Running Automated Tests"
echo "========================================"
echo ""

# Run quick tests (skip if files haven't changed in relevant areas)
CHANGED_FILES=$(git diff --cached --name-only)

if echo "$CHANGED_FILES" | grep -qE '(^src/|^simple_test_api\.py|\.py$)'; then
    echo "📝 Python files changed, running tests..."
    echo ""

    # 1. Quick format check
    echo "🎨 Checking code format..."
    uv run ruff format --check src/ tests/ || {
        echo "❌ Format check failed. Run: uv run ruff format src/ tests/"
        exit 1
    }

    # 2. Run Keploy tests
    echo "🧪 Running Keploy automated tests..."

    # Start API if not running
    if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
        uv run python simple_test_api.py > /tmp/api.log 2>&1 &
        API_PID=$!
        sleep 3
        STARTED_API=true
    fi

    # Run tests
    if uv run python run-keploy-tests.py; then
        echo "✅ All Keploy tests passed!"
    else
        echo "❌ Keploy tests failed. Fix issues before committing."
        [ "$STARTED_API" = true ] && kill $API_PID 2>/dev/null
        exit 1
    fi

    # Cleanup
    [ "$STARTED_API" = true ] && kill $API_PID 2>/dev/null

    echo ""
    echo "✅ Pre-commit checks passed!"
else
    echo "ℹ️  No Python files changed, skipping tests"
fi

echo ""
echo "✅ Ready to commit!"
exit 0
