#!/bin/bash
# Master TTA Testing Automation
# One command to rule them all!

set -e

clear

cat << 'BANNER'
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   🚀 TTA AUTOMATED TESTING - COMPLETE INTEGRATION 🚀          ║
║                                                                ║
║   Powered by Keploy - Zero Manual Test Writing                ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
BANNER

echo ""
echo "📊 Test Suite Status:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check what's available
SIMPLE_API_STATUS="❌ Not Running"
PLAYER_API_STATUS="❌ Not Running"

if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    SIMPLE_API_STATUS="✅ Running"
fi

if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    PLAYER_API_STATUS="✅ Running"
fi

TEST_COUNT=$(ls -1 keploy/tests/*.yaml 2>/dev/null | wc -l || echo "0")

echo "  Simple Test API (Port 8000): $SIMPLE_API_STATUS"
echo "  Player Experience API (Port 8080): $PLAYER_API_STATUS"
echo "  Recorded Test Cases: $TEST_COUNT"
echo ""

# Menu
while true; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "What would you like to do?"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "  1) 🎬 Record New Tests (Simple API)"
    echo "  2) 🧪 Run All Automated Tests"
    echo "  3) 📊 View Test Results"
    echo "  4) 🔄 Re-record Tests (Fresh)"
    echo "  5) 🎮 Record Player Experience API Tests (when available)"
    echo "  6) 📈 Generate Coverage Report"
    echo "  7) 🚀 Full Workflow (Record + Test + Report)"
    echo "  8) ⚙️  Setup Pre-Commit Hook"
    echo "  9) 📝 View Documentation"
    echo "  0) 🚪 Exit"
    echo ""
    read -p "Enter choice [0-9]: " choice

    case $choice in
        1)
            echo ""
            ./record-real-api-tests.sh
            read -p "Press Enter to continue..."
            ;;
        2)
            echo ""
            ./complete-keploy-workflow.sh
            read -p "Press Enter to continue..."
            ;;
        3)
            echo ""
            echo "📊 Test Results:"
            ls -lh keploy/tests/
            echo ""
            read -p "View a specific test? (filename or Enter to skip): " testfile
            if [ -n "$testfile" ]; then
                cat "keploy/tests/$testfile"
            fi
            read -p "Press Enter to continue..."
            ;;
        4)
            echo ""
            echo "🔄 Re-recording all tests..."
            rm -rf keploy/tests/*.yaml
            ./record-real-api-tests.sh
            read -p "Press Enter to continue..."
            ;;
        5)
            echo ""
            echo "🎮 Player Experience API Recording"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            if [ "$PLAYER_API_STATUS" == "✅ Running" ]; then
                echo "Player API is running! Recording tests..."
                # TODO: Implement when Player API is ready
                echo "⚠️  Coming soon - template available in keploy/PLAYER_API_TEMPLATE.md"
            else
                echo "ℹ️  Player Experience API is not running"
                echo ""
                echo "To record Player API tests:"
                echo "  1. Start Player API: uv run uvicorn src.player_experience.api.app:app --port 8080"
                echo "  2. Run this option again"
            fi
            read -p "Press Enter to continue..."
            ;;
        6)
            echo ""
            echo "📈 Generating Coverage Report..."
            uv run pytest tests/unit/ --cov=src --cov-report=html
            xdg-open htmlcov/index.html 2>/dev/null || echo "Report generated in htmlcov/index.html"
            read -p "Press Enter to continue..."
            ;;
        7)
            echo ""
            echo "🚀 Running Full Workflow..."
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ./record-real-api-tests.sh
            echo ""
            ./complete-keploy-workflow.sh
            echo ""
            echo "📊 Generating coverage report..."
            uv run pytest tests/unit/ --cov=src --cov-report=term-missing
            read -p "Press Enter to continue..."
            ;;
        8)
            echo ""
            echo "⚙️  Installing Pre-Commit Hook..."
            chmod +x pre-commit-keploy.sh
            ln -sf ../../pre-commit-keploy.sh .git/hooks/pre-commit
            echo "✅ Pre-commit hook installed!"
            echo ""
            echo "Now automated tests will run before every commit."
            read -p "Press Enter to continue..."
            ;;
        9)
            echo ""
            echo "📝 Documentation Files:"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "  1. KEPLOY_AUTOMATION_COMPLETE.md - Complete guide"
            echo "  2. TESTING_GUIDE.md - Testing strategy"
            echo "  3. KEPLOY_READY.md - Setup guide"
            echo "  4. keploy/TEST_MANIFEST.md - Test coverage"
            echo ""
            read -p "Enter number to view (or Enter to skip): " docnum
            case $docnum in
                1) less KEPLOY_AUTOMATION_COMPLETE.md;;
                2) less TESTING_GUIDE.md;;
                3) less KEPLOY_READY.md;;
                4) less keploy/TEST_MANIFEST.md;;
            esac
            ;;
        0)
            echo ""
            echo "👋 Thanks for using TTA Automated Testing!"
            echo ""
            echo "📚 Quick Reference:"
            echo "  - Record tests: ./record-real-api-tests.sh"
            echo "  - Run tests: ./complete-keploy-workflow.sh"
            echo "  - Full workflow: ./master-tta-testing.sh"
            echo ""
            exit 0
            ;;
        *)
            echo "❌ Invalid choice. Please try again."
            sleep 2
            ;;
    esac

    clear
    cat << 'BANNER'
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   🚀 TTA AUTOMATED TESTING - COMPLETE INTEGRATION 🚀          ║
║                                                                ║
║   Powered by Keploy - Zero Manual Test Writing                ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
BANNER
    echo ""
    TEST_COUNT=$(ls -1 keploy/tests/*.yaml 2>/dev/null | wc -l || echo "0")
    echo "📊 Current Status: $TEST_COUNT test cases ready"
    echo ""
done
