---
name: page-objects
description: "Skill for the Page-objects area of TTA. 221 symbols across 18 files."
---

# Page-objects

221 symbols | 18 files | Cohesion: 79%

## When to Use

- Working with code in `tests/`
- Understanding how waitForNetworkIdle, loginWithDemoCredentials, BasePage work
- Modifying page-objects-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/e2e/page-objects/WorldSelectionPage.ts` | WorldSelectionPage, getWorldByName, clickViewDetails, clickCustomizeWorld, clickSelectWorld (+16) |
| `tests/e2e/page-objects/CharacterManagementPage.ts` | CharacterManagementPage, filterCharacters, sortCharacters, selectMultipleCharacters, bulkDeleteCharacters (+15) |
| `tests/e2e/page-objects/LoginPage.ts` | login, fillUsername, fillPassword, clickLogin, expectErrorMessage (+13) |
| `tests/e2e/page-objects/ChatPage.ts` | ChatPage, checkAccessibility, sendMessage, sendMessageWithEnter, waitForMessageSent (+13) |
| `tests/e2e/page-objects/SettingsPage.ts` | SettingsPage, saveSettings, expectPageLoaded, goToTherapeuticTab, goToNotificationsTab (+12) |
| `tests/e2e-staging/page-objects/BasePage.ts` | getElement, fillInput, selectOption, waitForPageLoad, getElements (+10) |
| `tests/e2e-staging/page-objects/CharacterCreationPage.ts` | fillCharacterName, fillAppearance, fillBackground, selectPersonalityTraits, selectTherapeuticGoals (+10) |
| `tests/e2e-staging/page-objects/LoginPage.ts` | clearForm, isSubmitButtonEnabled, login, loginWithDemo, expectLoginFormVisible (+10) |
| `tests/e2e-staging/page-objects/DashboardPage.ts` | getRecentSessionsCount, getCharacterCount, expectNavigationMenu, getWelcomeMessage, DashboardPage (+8) |
| `tests/e2e-staging/page-objects/GameplayPage.ts` | goto, expectGameplayLoaded, clickActionButton, getLatestAiResponse, getAllChatMessages (+7) |

## Entry Points

Start here when exploring this area:

- **`waitForNetworkIdle`** (Function) — `tests/e2e-staging/helpers/test-helpers.ts:14`
- **`loginWithDemoCredentials`** (Function) — `tests/e2e-staging/helpers/test-helpers.ts:32`
- **`BasePage`** (Class) — `tests/e2e/page-objects/BasePage.ts:6`
- **`CharacterManagementPage`** (Class) — `tests/e2e/page-objects/CharacterManagementPage.ts:8`
- **`ChatPage`** (Class) — `tests/e2e/page-objects/ChatPage.ts:7`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `BasePage` | Class | `tests/e2e/page-objects/BasePage.ts` | 6 |
| `CharacterManagementPage` | Class | `tests/e2e/page-objects/CharacterManagementPage.ts` | 8 |
| `ChatPage` | Class | `tests/e2e/page-objects/ChatPage.ts` | 7 |
| `DashboardPage` | Class | `tests/e2e/page-objects/DashboardPage.ts` | 7 |
| `LoginPage` | Class | `tests/e2e/page-objects/LoginPage.ts` | 8 |
| `ModelManagementPage` | Class | `tests/e2e/page-objects/ModelManagementPage.ts` | 7 |
| `PreferencesPage` | Class | `tests/e2e/page-objects/PreferencesPage.ts` | 7 |
| `ProgressPage` | Class | `tests/e2e/page-objects/ProgressPage.ts` | 7 |
| `SettingsPage` | Class | `tests/e2e/page-objects/SettingsPage.ts` | 7 |
| `WorldSelectionPage` | Class | `tests/e2e/page-objects/WorldSelectionPage.ts` | 7 |
| `BasePage` | Class | `tests/e2e-staging/page-objects/BasePage.ts` | 12 |
| `CharacterCreationPage` | Class | `tests/e2e-staging/page-objects/CharacterCreationPage.ts` | 12 |
| `DashboardPage` | Class | `tests/e2e-staging/page-objects/DashboardPage.ts` | 10 |
| `GameplayPage` | Class | `tests/e2e-staging/page-objects/GameplayPage.ts` | 12 |
| `LoginPage` | Class | `tests/e2e-staging/page-objects/LoginPage.ts` | 11 |
| `WorldSelectionPage` | Class | `tests/e2e-staging/page-objects/WorldSelectionPage.ts` | 12 |
| `waitForNetworkIdle` | Function | `tests/e2e-staging/helpers/test-helpers.ts` | 14 |
| `loginWithDemoCredentials` | Function | `tests/e2e-staging/helpers/test-helpers.ts` | 32 |
| `getElement` | Method | `tests/e2e-staging/page-objects/BasePage.ts` | 37 |
| `fillInput` | Method | `tests/e2e-staging/page-objects/BasePage.ts` | 60 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `CreateCharacter → GetElement` | intra_community | 4 |

## How to Explore

1. `context({name: "waitForNetworkIdle"})` — see callers and callees
2. `query({search_query: "page-objects"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings (source→sink data flows), when indexed with `--pdg`
