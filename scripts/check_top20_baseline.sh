#!/bin/bash
# Script to check Pyright errors for top 20 high-value modules

echo "=== Pyright Baseline Check for Top 20 Modules ==="
echo "Date: $(date)"
echo ""

# Top 20 modules for annotation (from Phase 1D-Revised)
MODULES=(
    # API Layer (8 modules)
    "src/player_experience/api/routers/auth.py"
    "src/player_experience/api/routers/players.py"
    "src/player_experience/api/routers/characters.py"
    "src/player_experience/api/routers/sessions.py"
    "src/player_experience/api/routers/chat.py"
    "src/player_experience/api/routers/gameplay.py"
    "src/player_experience/api/middleware.py"
    "src/player_experience/api/auth.py"
    
    # Service Layer (7 modules)
    "src/player_experience/services/auth_service.py"
    "src/player_experience/services/gameplay_service.py"
    "src/player_experience/managers/player_profile_manager.py"
    "src/player_experience/managers/session_integration_manager.py"
    "src/player_experience/managers/character_avatar_manager.py"
    "src/player_experience/services/personalization_service.py"
    "src/player_experience/services/narrative_service.py"
    
    # Database Layer (5 modules)
    "src/player_experience/database/player_profile_repository.py"
    "src/player_experience/database/session_repository.py"
    "src/player_experience/database/character_repository.py"
    "src/player_experience/database/user_repository.py"
    "src/player_experience/database/redis_client.py"
)

TOTAL_ERRORS=0
TOTAL_WARNINGS=0
TOTAL_FILES=0

for module in "${MODULES[@]}"; do
    if [ -f "$module" ]; then
        echo "Checking: $module"
        
        # Run Pyright and capture JSON output
        OUTPUT=$(pyright "$module" --outputjson 2>&1)
        
        # Extract error and warning counts
        ERRORS=$(echo "$OUTPUT" | jq -r '.summary.errorCount // 0' 2>/dev/null || echo "0")
        WARNINGS=$(echo "$OUTPUT" | jq -r '.summary.warningCount // 0' 2>/dev/null || echo "0")
        
        echo "  Errors: $ERRORS, Warnings: $WARNINGS"
        
        TOTAL_ERRORS=$((TOTAL_ERRORS + ERRORS))
        TOTAL_WARNINGS=$((TOTAL_WARNINGS + WARNINGS))
        TOTAL_FILES=$((TOTAL_FILES + 1))
    else
        echo "⚠️  File not found: $module"
    fi
    echo ""
done

echo "=== Summary ==="
echo "Total files checked: $TOTAL_FILES"
echo "Total errors: $TOTAL_ERRORS"
echo "Total warnings: $TOTAL_WARNINGS"
echo "Average errors per file: $(echo "scale=2; $TOTAL_ERRORS / $TOTAL_FILES" | bc)"
echo ""
echo "Baseline established: $(date)"

