#!/bin/bash

# Test script for CharacterCreationForm restoration
# This script helps verify the restored component works correctly

set -e

echo "🎭 CharacterCreationForm Restoration Test Script"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print success
success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Function to print error
error() {
    echo -e "${RED}✗${NC} $1"
}

# Function to print info
info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

echo "Step 1: Checking file existence..."
if [ -f "src/player_experience/frontend/src/components/Character/CharacterCreationForm.tsx" ]; then
    success "CharacterCreationForm.tsx exists"

    # Check file size
    FILE_SIZE=$(wc -l < "src/player_experience/frontend/src/components/Character/CharacterCreationForm.tsx")
    if [ "$FILE_SIZE" -gt 800 ]; then
        success "File has $FILE_SIZE lines (expected > 800)"
    else
        error "File only has $FILE_SIZE lines (expected > 800)"
        exit 1
    fi
else
    error "CharacterCreationForm.tsx not found"
    exit 1
fi

echo ""
echo "Step 2: Checking imports..."
if grep -q "import.*validateName.*characterValidation" "src/player_experience/frontend/src/components/Character/CharacterCreationForm.tsx"; then
    success "Validation utility imported"
else
    error "Validation utility not imported"
    exit 1
fi

if grep -q "import.*createCharacter.*characterSlice" "src/player_experience/frontend/src/components/Character/CharacterCreationForm.tsx"; then
    success "Redux action imported"
else
    error "Redux action not imported"
    exit 1
fi

echo ""
echo "Step 3: Checking component structure..."
if grep -q "const renderStep1" "src/player_experience/frontend/src/components/Character/CharacterCreationForm.tsx"; then
    success "Step 1 render function exists"
else
    error "Step 1 render function missing"
    exit 1
fi

if grep -q "const renderStep2" "src/player_experience/frontend/src/components/Character/CharacterCreationForm.tsx"; then
    success "Step 2 render function exists"
else
    error "Step 2 render function missing"
    exit 1
fi

if grep -q "const renderStep3" "src/player_experience/frontend/src/components/Character/CharacterCreationForm.tsx"; then
    success "Step 3 render function exists"
else
    error "Step 3 render function missing"
    exit 1
fi

echo ""
echo "Step 4: Checking validation functions..."
if grep -q "const validateStep1" "src/player_experience/frontend/src/components/Character/CharacterCreationForm.tsx"; then
    success "Step 1 validation exists"
else
    error "Step 1 validation missing"
    exit 1
fi

if grep -q "const validateStep2" "src/player_experience/frontend/src/components/Character/CharacterCreationForm.tsx"; then
    success "Step 2 validation exists"
else
    error "Step 2 validation missing"
    exit 1
fi

if grep -q "const validateStep3" "src/player_experience/frontend/src/components/Character/CharacterCreationForm.tsx"; then
    success "Step 3 validation exists"
else
    error "Step 3 validation missing"
    exit 1
fi

echo ""
echo "Step 5: Checking array field management..."
if grep -q "const addArrayItem" "src/player_experience/frontend/src/components/Character/CharacterCreationForm.tsx"; then
    success "addArrayItem function exists"
else
    error "addArrayItem function missing"
    exit 1
fi

if grep -q "const removeArrayItem" "src/player_experience/frontend/src/components/Character/CharacterCreationForm.tsx"; then
    success "removeArrayItem function exists"
else
    error "removeArrayItem function missing"
    exit 1
fi

if grep -q "const addTherapeuticGoal" "src/player_experience/frontend/src/components/Character/CharacterCreationForm.tsx"; then
    success "addTherapeuticGoal function exists"
else
    error "addTherapeuticGoal function missing"
    exit 1
fi

echo ""
echo "Step 6: Checking TypeScript compilation..."
cd src/player_experience/frontend
if npm run type-check 2>&1 | grep -q "CharacterCreationForm"; then
    error "TypeScript errors found in CharacterCreationForm"
    npm run type-check 2>&1 | grep -A 5 "CharacterCreationForm"
    exit 1
else
    success "No TypeScript errors in CharacterCreationForm"
fi
cd ../../..

echo ""
echo "Step 7: Checking integration with CharacterManagement..."
if grep -q "import CharacterCreationForm" "src/player_experience/frontend/src/pages/CharacterManagement/CharacterManagement.tsx"; then
    success "CharacterCreationForm imported in CharacterManagement"
else
    error "CharacterCreationForm not imported in CharacterManagement"
    exit 1
fi

if grep -q "showCreateForm" "src/player_experience/frontend/src/pages/CharacterManagement/CharacterManagement.tsx"; then
    success "showCreateForm state exists in CharacterManagement"
else
    error "showCreateForm state missing in CharacterManagement"
    exit 1
fi

echo ""
echo "Step 8: Checking documentation..."
if [ -f "CHARACTER_CREATION_FORM_RESTORATION.md" ]; then
    success "Restoration documentation exists"
else
    error "Restoration documentation missing"
    exit 1
fi

echo ""
echo "================================================"
echo -e "${GREEN}✓ All checks passed!${NC}"
echo ""
echo "Next steps for manual testing:"
echo "1. Start the development server:"
echo "   cd src/player_experience/frontend && npm start"
echo ""
echo "2. Navigate to Character Management page"
echo ""
echo "3. Click 'Create Character' button"
echo ""
echo "4. Test the multi-step form:"
echo "   - Step 1: Fill in basic information"
echo "   - Step 2: Add personality traits and goals"
echo "   - Step 3: Add therapeutic profile"
echo "   - Submit and verify character is created"
echo ""
echo "5. Verify character appears in the character list"
echo ""
echo "For automated E2E testing:"
echo "   npx playwright test tests/e2e/specs/character-management.spec.ts"
echo ""
echo "================================================"
