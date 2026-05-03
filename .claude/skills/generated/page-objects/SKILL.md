---
name: page-objects
description: "Skill for the Page-objects area of TTA. 231 symbols across 24 files."
---

# Page-objects

231 symbols | 24 files | Cohesion: 79%

## When to Use

- Working with code in `tests/`
- Understanding how check, count, testSecureHeaders work
- Modifying page-objects-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/e2e/page-objects/WorldSelectionPage.ts` | WorldSelectionPage, goto, getWorldByName, clickViewDetails, clickCustomizeWorld (+17) |
| `tests/e2e/page-objects/CharacterManagementPage.ts` | CharacterManagementPage, selectMultipleCharacters, bulkDeleteCharacters, filterCharacters, sortCharacters (+15) |
| `tests/e2e/page-objects/LoginPage.ts` | login, fillUsername, fillPassword, clickLogin, expectErrorMessage (+13) |
| `tests/e2e/page-objects/ChatPage.ts` | ChatPage, sendMessageWithEnter, waitForMessageSent, sendMessage, waitForAssistantResponse (+13) |
| `tests/e2e-staging/page-objects/BasePage.ts` | getElement, fillInput, selectOption, getElements, getAllTextContents (+12) |
| `tests/e2e/page-objects/SettingsPage.ts` | SettingsPage, goToAccessibilityTab, updateAccessibilitySettings, saveSettings, expectPageLoaded (+12) |
| `tests/e2e-staging/page-objects/LoginPage.ts` | clearForm, isSubmitButtonEnabled, expectLoginFormVisible, login, loginWithDemo (+10) |
| `tests/e2e-staging/page-objects/CharacterCreationPage.ts` | fillCharacterName, fillAppearance, fillBackground, selectPersonalityTraits, selectTherapeuticGoals (+10) |
| `tests/e2e-staging/page-objects/DashboardPage.ts` | getRecentSessionsCount, getCharacterCount, expectNavigationMenu, getWelcomeMessage, DashboardPage (+8) |
| `tests/e2e-staging/page-objects/GameplayPage.ts` | getLatestAiResponse, getAllChatMessages, clickActionButton, goto, expectGameplayLoaded (+7) |

## Entry Points

Start here when exploring this area:

- **`check`** (Function) — `tests/unit/common/test_retry_helpers.py:53`
- **`count`** (Function) — `tests/fakes/fake_repository.py:63`
- **`testSecureHeaders`** (Function) — `tests/e2e-staging/helpers/security-testing-helpers.ts:267`
- **`AdvancedAnalyticsDashboard`** (Function) — `src/player_experience/frontend/src/components/AdvancedAnalytics/AdvancedAnalyticsDashboard.tsx:97`
- **`waitForNetworkIdle`** (Function) — `tests/e2e-staging/helpers/test-helpers.ts:14`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `WorldSelectionPage` | Class | `tests/e2e/page-objects/WorldSelectionPage.ts` | 7 |
| `SettingsPage` | Class | `tests/e2e/page-objects/SettingsPage.ts` | 7 |
| `ProgressPage` | Class | `tests/e2e/page-objects/ProgressPage.ts` | 7 |
| `PreferencesPage` | Class | `tests/e2e/page-objects/PreferencesPage.ts` | 7 |
| `ModelManagementPage` | Class | `tests/e2e/page-objects/ModelManagementPage.ts` | 7 |
| `LoginPage` | Class | `tests/e2e/page-objects/LoginPage.ts` | 8 |
| `DashboardPage` | Class | `tests/e2e/page-objects/DashboardPage.ts` | 7 |
| `ChatPage` | Class | `tests/e2e/page-objects/ChatPage.ts` | 7 |
| `CharacterManagementPage` | Class | `tests/e2e/page-objects/CharacterManagementPage.ts` | 8 |
| `BasePage` | Class | `tests/e2e/page-objects/BasePage.ts` | 6 |
| `WorldSelectionPage` | Class | `tests/e2e-staging/page-objects/WorldSelectionPage.ts` | 12 |
| `LoginPage` | Class | `tests/e2e-staging/page-objects/LoginPage.ts` | 11 |
| `GameplayPage` | Class | `tests/e2e-staging/page-objects/GameplayPage.ts` | 12 |
| `DashboardPage` | Class | `tests/e2e-staging/page-objects/DashboardPage.ts` | 10 |
| `CharacterCreationPage` | Class | `tests/e2e-staging/page-objects/CharacterCreationPage.ts` | 12 |
| `BasePage` | Class | `tests/e2e-staging/page-objects/BasePage.ts` | 12 |
| `check` | Function | `tests/unit/common/test_retry_helpers.py` | 53 |
| `count` | Function | `tests/fakes/fake_repository.py` | 63 |
| `testSecureHeaders` | Function | `tests/e2e-staging/helpers/security-testing-helpers.ts` | 267 |
| `AdvancedAnalyticsDashboard` | Function | `src/player_experience/frontend/src/components/AdvancedAnalytics/AdvancedAnalyticsDashboard.tsx` | 97 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `CreateCharacter → GetElement` | intra_community | 4 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Services | 2 calls |

## How to Explore

1. `gitnexus_context({name: "check"})` — see callers and callees
2. `gitnexus_query({query: "page-objects"})` — find related execution flows
3. Read key files listed above for implementation details
