# TTA Frontend-Backend Integration Guide

**Document Purpose**: Comprehensive integration guide for connecting the TTA frontend with existing backend systems  
**Target Audience**: Frontend development team  
**Last Updated**: September 14, 2025  
**Status**: Ready for implementation

## 🎯 Executive Summary

The TTA frontend implementation is **professionally developed** with excellent architecture, but requires specific integration work to connect with the sophisticated backend systems (AI agent orchestration, living worlds, player experience APIs) that are already operational.

### Key Findings
- ✅ **Frontend Quality**: Production-ready React/TypeScript implementation with comprehensive API client
- 🔴 **Integration Gaps**: API endpoint mismatches, data model inconsistencies, missing WebSocket handlers
- ⚡ **Timeline**: 3-4 weeks for full integration with clear, actionable steps
- 🎯 **Priority**: High - Backend systems are ready and waiting for frontend connection

## 📋 Current Implementation Strengths

### ✅ Excellent Foundation
- **Comprehensive API Client**: 46+ endpoints implemented in `src/services/api.ts`
- **Professional Architecture**: Redux Toolkit, Material-UI, TypeScript throughout
- **Therapeutic Design**: Custom theme with calming colors and crisis support integration
- **WebSocket Ready**: Socket.io client with event handling framework
- **Complete Documentation**: Extensive docs in `frontend/docs/` directory

### ✅ Key Files Analysis
```
frontend/src/
├── services/
│   ├── api.ts          ✅ Comprehensive API client (318 lines)
│   └── websocket.ts    ✅ Socket.io integration (333 lines)
├── types/
│   └── therapeutic.ts  ✅ Complete TypeScript definitions (332 lines)
├── store/
│   ├── store.ts        ✅ Redux configuration
│   └── slices/         ✅ State management slices
└── pages/              ✅ React components with Material-UI
```

## 🔴 Critical Integration Issues

### Issue 1: API Endpoint Path Mismatches

**Problem**: Frontend expects different paths than backend provides

**Frontend Expects** (`src/services/api.ts`):
```typescript
// Characters
async getPlayerCharacters(playerId: string): Promise<ApiResponse<Character[]>> {
  const response = await this.api.get(`/api/v1/players/${playerId}/characters`);
  return response.data;
}

// User info
async getCurrentUser(): Promise<UserAccount> {
  const response = await this.api.get('/api/v1/auth/me');
  return response.data;
}
```

**Backend Provides** (`src/player_experience/api/routers/`):
```python
# Characters - different path structure
@router.get("/", summary="List characters")  # /api/v1/characters/
async def list_characters()

# Missing endpoint
# /api/v1/auth/me - NOT IMPLEMENTED
```

**Fix Required**: Update backend routes or frontend paths (see Action Items)

### Issue 2: Data Model Naming Conventions

**Problem**: Frontend uses camelCase, backend uses snake_case

**Frontend Model** (`src/types/therapeutic.ts`):
```typescript
export interface Character {
  characterId: string;        // camelCase
  playerId: string;
  createdAt: string;
  lastActive: string;
  isActive: boolean;
}
```

**Backend Model** (`src/player_experience/api/routers/characters.py`):
```python
class CharacterResponse(BaseModel):
    character_id: str          # snake_case
    player_id: str
    created_at: str
    last_active: str
    is_active: bool
```

**Fix Required**: Data transformation layer (see Implementation section)

### Issue 3: WebSocket Event Mismatches

**Problem**: Frontend expects events that backend doesn't emit

**Frontend Expects** (`src/services/websocket.ts`):
```typescript
// Therapeutic events
'therapeutic:milestone_achieved': (data: { milestoneId: string; description: string }) => void;
'therapeutic:crisis_detected': (data: { level: 'low' | 'medium' | 'high'; context: string }) => void;
'therapeutic:support_needed': (data: { type: string; urgency: 'low' | 'medium' | 'high' }) => void;

// System events
'system:notification': (data: { type: string; message: string }) => void;
'system:error': (data: { error: string; code?: string }) => void;
```

**Backend WebSocket** (`src/player_experience/api/routers/chat.py`):
```python
# Basic chat implementation exists but missing therapeutic events
@router.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    # Limited event handling
```

**Fix Required**: Implement therapeutic event handlers in backend

## 🛠️ Implementation Plan

### Phase 1: Core API Fixes (Week 1) - HIGH PRIORITY

#### Task 1.1: Fix Authentication Endpoints
**File**: `src/player_experience/api/routers/auth.py`

**Add Missing Endpoint**:
```python
@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_player: TokenData = Depends(get_current_active_player)
) -> UserResponse:
    # Implementation needed
    pass
```

#### Task 1.2: Create Data Transformation Layer
**File**: `frontend/src/services/transformers.ts` (CREATE NEW)

```typescript
// Transform backend snake_case to frontend camelCase
export const transformCharacter = (backendChar: any): Character => ({
  characterId: backendChar.character_id,
  playerId: backendChar.player_id,
  name: backendChar.name,
  createdAt: backendChar.created_at,
  lastActive: backendChar.last_active,
  isActive: backendChar.is_active,
  // ... transform all fields
});

// Transform frontend camelCase to backend snake_case
export const transformCharacterRequest = (frontendChar: Partial<Character>) => ({
  character_id: frontendChar.characterId,
  player_id: frontendChar.playerId,
  name: frontendChar.name,
  created_at: frontendChar.createdAt,
  last_active: frontendChar.lastActive,
  is_active: frontendChar.isActive,
  // ... transform all fields
});
```

#### Task 1.3: Update API Client
**File**: `frontend/src/services/api.ts`

**Add Transformations**:
```typescript
import { transformCharacter, transformCharacterRequest } from './transformers';

// Update existing methods
async getPlayerCharacters(playerId: string): Promise<ApiResponse<Character[]>> {
  const response = await this.api.get('/api/v1/characters/'); // Updated path
  return {
    ...response.data,
    data: response.data.data.map(transformCharacter)
  };
}

async createCharacter(characterData: Omit<Character, 'characterId' | 'createdAt' | 'lastActive'>): Promise<ApiResponse<Character>> {
  const transformedData = transformCharacterRequest(characterData);
  const response = await this.api.post('/api/v1/characters/', transformedData);
  return {
    ...response.data,
    data: transformCharacter(response.data.data)
  };
}
```

### Phase 2: WebSocket Integration (Week 2) - HIGH PRIORITY

#### Task 2.1: Backend WebSocket Events
**File**: `src/player_experience/api/routers/chat.py`

**Add Therapeutic Event Handlers**:
```python
async def emit_milestone_achieved(websocket: WebSocket, milestone_data: dict):
    await websocket.send_text(json.dumps({
        "event": "therapeutic:milestone_achieved",
        "data": {
            "milestoneId": milestone_data["id"],
            "description": milestone_data["description"]
        }
    }))

async def emit_crisis_detected(websocket: WebSocket, crisis_data: dict):
    await websocket.send_text(json.dumps({
        "event": "therapeutic:crisis_detected", 
        "data": {
            "level": crisis_data["level"],
            "context": crisis_data["context"]
        }
    }))
```

#### Task 2.2: Frontend WebSocket Path Update
**File**: `frontend/src/services/websocket.ts`

**Update Connection Path**:
```typescript
// Current (line 58)
this.socket = io(`${this.baseURL}/ws/chat`, {

// Update to match backend
this.socket = io(`${this.baseURL}/api/v1/chat`, {
```

### Phase 3: Missing Backend Endpoints (Week 2-3) - MEDIUM PRIORITY

#### Task 3.1: Progress Tracking API
**File**: `src/player_experience/api/routers/progress.py` (CREATE NEW)

```python
@router.get("/players/{player_id}/progress")
async def get_player_progress(player_id: str) -> dict:
    # Implementation needed for dashboard
    pass
```

#### Task 3.2: World Management Features
**File**: `src/player_experience/api/routers/worlds.py`

**Add Missing Endpoints**:
```python
@router.get("/featured")
async def get_featured_worlds() -> list[WorldSummary]:
    pass

@router.get("/search")
async def search_worlds(q: str, filters: dict = None) -> list[WorldSummary]:
    pass
```

## 🧪 Testing Strategy

### Integration Testing Setup
**File**: `frontend/src/tests/integration/api.test.ts` (CREATE NEW)

```typescript
import { ttaApi } from '../services/api';

describe('API Integration Tests', () => {
  beforeAll(async () => {
    // Setup test authentication
    await ttaApi.login({ username: 'test', password: 'test' });
  });

  it('should fetch user profile', async () => {
    const user = await ttaApi.getCurrentUser();
    expect(user.username).toBeDefined();
  });

  it('should create and fetch character', async () => {
    const character = await ttaApi.createCharacter(mockCharacterData);
    expect(character.characterId).toBeDefined();
    
    const characters = await ttaApi.getPlayerCharacters(character.playerId);
    expect(characters.data).toContainEqual(character);
  });
});
```

### WebSocket Testing
**File**: `frontend/src/tests/integration/websocket.test.ts` (CREATE NEW)

```typescript
import { ttaWebSocket } from '../services/websocket';

describe('WebSocket Integration Tests', () => {
  it('should receive therapeutic events', (done) => {
    ttaWebSocket.on('therapeutic:milestone_achieved', (data) => {
      expect(data.description).toBeDefined();
      done();
    });
    
    // Trigger milestone in test
  });
});
```

## 📚 Documentation Resources

Your frontend team has access to comprehensive documentation in `frontend/docs/`:

### Key Documentation Files
- **`docs/README.md`**: Main documentation hub with complete navigation
- **`docs/API_QUICK_REFERENCE.md`**: Fast access to API endpoints and examples
- **`docs/DEVELOPMENT_SETUP.md`**: Complete environment setup guide
- **`docs/integration/`**: Service integration specifications
- **`docs/therapeutic-content/`**: Safety protocols and crisis support requirements

### Documentation Categories
```
frontend/docs/
├── api/                    # API specifications and contracts
├── design-system/          # UI/UX guidelines and therapeutic theming
├── business-logic/         # Therapeutic workflows and game mechanics
├── data-models/           # TypeScript interfaces and data structures
├── integration/           # WebSocket events and service integration
├── therapeutic-content/   # Safety protocols and crisis detection
├── testing/              # Testing strategies and requirements
├── examples/             # Code examples and implementation guides
└── guides/               # User guides and development workflows
```

### Using the Documentation
1. **Start with** `docs/README.md` for project overview
2. **Reference** `docs/API_QUICK_REFERENCE.md` for daily development
3. **Follow** `docs/DEVELOPMENT_SETUP.md` for environment configuration
4. **Check** `docs/integration/` for WebSocket and service requirements

## ⚡ Immediate Action Items

### This Week (High Priority)
- [ ] **Fix API endpoint paths** - Update backend routes or frontend client
- [ ] **Implement `/api/v1/auth/me` endpoint** in backend
- [ ] **Create data transformation layer** in `frontend/src/services/transformers.ts`
- [ ] **Add CORS configuration** for `http://localhost:3000`
- [ ] **Update WebSocket connection path** in frontend

### Next Week (Medium Priority)  
- [ ] **Implement therapeutic WebSocket events** in backend
- [ ] **Add progress tracking API** for dashboard functionality
- [ ] **Complete missing world management endpoints**
- [ ] **Create integration test suite**

### Following Weeks (Lower Priority)
- [ ] **Implement export functionality** (characters, worlds, sessions)
- [ ] **Add advanced therapeutic features** (crisis detection, milestone tracking)
- [ ] **Performance optimization** and caching
- [ ] **Comprehensive end-to-end testing**

## 🚀 Getting Started

1. **Review this document** completely
2. **Check current backend status** - Run `python src/main.py start` to verify services
3. **Start with Phase 1, Task 1.1** - Fix authentication endpoints
4. **Reference documentation** in `frontend/docs/` as needed
5. **Test each integration** before moving to next task

## 📞 Support Resources

- **Documentation Hub**: `frontend/docs/README.md`
- **API Reference**: `frontend/docs/API_QUICK_REFERENCE.md`
- **Development Setup**: `frontend/docs/DEVELOPMENT_SETUP.md`
- **Crisis Support Protocols**: `frontend/docs/therapeutic-content/`

## 🔧 Environment Configuration

### Backend Configuration
**File**: `src/player_experience/api/config.py`

**Add CORS for Frontend**:
```python
# Update CORS origins
CORS_ORIGINS = [
    "http://localhost:3000",  # Frontend dev server
    "https://localhost:3000", # Frontend HTTPS
    "http://localhost:8080",  # API server
]
```

### Frontend Environment
**File**: `frontend/.env` (CREATE NEW)

```bash
# API Configuration
REACT_APP_API_BASE_URL=http://localhost:8080
REACT_APP_WS_BASE_URL=http://localhost:8080

# Development Settings
REACT_APP_ENVIRONMENT=development
REACT_APP_DEBUG_MODE=true

# Therapeutic Settings
REACT_APP_CRISIS_HOTLINE=988
REACT_APP_CRISIS_TEXT=741741
```

### Database Requirements
The backend requires Neo4j and Redis to be running:

```bash
# Start databases using Docker Compose
cd /home/thein/recovered-tta-storytelling
docker-compose -f config/docker-compose.yml up -d

# Verify services
curl http://localhost:8080/health
```

## 🎯 Specific Code Examples

### Complete API Client Update
**File**: `frontend/src/services/api.ts`

**Replace existing methods with transformed versions**:
```typescript
// Update the TTAApiClient class methods
async getPlayerCharacters(playerId: string): Promise<ApiResponse<Character[]>> {
  // Use current player's characters endpoint
  const response = await this.api.get('/api/v1/characters/');
  return {
    status: 'success',
    data: response.data.map(transformCharacter),
    message: 'Characters retrieved successfully'
  };
}

async createCharacter(characterData: Omit<Character, 'characterId' | 'createdAt' | 'lastActive'>): Promise<ApiResponse<Character>> {
  const transformedData = transformCharacterRequest(characterData);
  const response = await this.api.post('/api/v1/characters/', transformedData);
  return {
    status: 'success',
    data: transformCharacter(response.data),
    message: 'Character created successfully'
  };
}

// Add missing authentication method
async getCurrentUser(): Promise<UserAccount> {
  const response = await this.api.get('/api/v1/auth/me');
  return transformUser(response.data);
}
```

### Redux Store Integration
**File**: `frontend/src/store/slices/charactersSlice.ts`

**Replace mock data with real API calls**:
```typescript
// Update fetchCharacters thunk
export const fetchCharacters = createAsyncThunk(
  'characters/fetchCharacters',
  async (playerId: string, { rejectWithValue }) => {
    try {
      const response = await ttaApi.getPlayerCharacters(playerId);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch characters');
    }
  }
);

// Update createCharacter thunk
export const createCharacter = createAsyncThunk(
  'characters/createCharacter',
  async (characterData: Omit<Character, 'characterId' | 'createdAt' | 'lastActive'>, { rejectWithValue }) => {
    try {
      const response = await ttaApi.createCharacter(characterData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to create character');
    }
  }
);
```

## 🚨 Crisis Support Integration

### Critical Requirements
The frontend includes comprehensive crisis support that must be maintained:

**File**: `frontend/src/components/common/CrisisSupport.tsx`
- Always accessible within 2 clicks
- 24/7 hotline integration (988, 741741)
- Crisis detection event handling

**WebSocket Crisis Events**:
```typescript
// Frontend expects these crisis events
ttaWebSocket.on('therapeutic:crisis_detected', (data) => {
  // Immediate crisis support activation
  setCrisisLevel(data.level);
  showCrisisSupport();
});

ttaWebSocket.on('therapeutic:support_needed', (data) => {
  // Therapeutic support escalation
  showTherapeuticSupport(data.type, data.urgency);
});
```

**Backend Implementation Needed**:
```python
# Add to chat.py WebSocket handler
async def detect_crisis_content(message: str) -> dict:
    # Crisis detection logic
    if crisis_detected:
        return {
            "level": "high",  # low, medium, high
            "context": "Crisis indicators detected in message",
            "recommended_action": "immediate_support"
        }
    return None

async def handle_message(websocket: WebSocket, message: dict):
    # Process message
    crisis_data = await detect_crisis_content(message["content"])
    if crisis_data:
        await emit_crisis_detected(websocket, crisis_data)
```

## 📊 Progress Tracking Integration

### Dashboard Data Requirements
**File**: `frontend/src/pages/Dashboard.tsx`

The dashboard expects specific progress data:
```typescript
interface DashboardData {
  sessionsCompleted: number;
  currentStreak: number;
  totalProgress: number;
  nextMilestone: string;
  recentSessions: SessionSummary[];
  therapeuticMetrics: TherapeuticMetrics;
}
```

**Backend API Needed**:
```python
# File: src/player_experience/api/routers/progress.py
@router.get("/players/{player_id}/dashboard")
async def get_player_dashboard(
    player_id: str,
    current_player: TokenData = Depends(get_current_active_player)
) -> DashboardData:
    # Aggregate player progress data
    return {
        "sessions_completed": session_count,
        "current_streak": calculate_streak(player_id),
        "total_progress": calculate_overall_progress(player_id),
        "next_milestone": get_next_milestone(player_id),
        "recent_sessions": get_recent_sessions(player_id, limit=5),
        "therapeutic_metrics": get_therapeutic_metrics(player_id)
    }
```

## 🔄 Real-time Session Management

### WebSocket Session Events
**Frontend Implementation** (`src/services/websocket.ts`):
```typescript
// Session lifecycle events
joinSession(sessionId: string): void {
  if (this.socket && this.socket.connected) {
    this.socket.emit('session:join', { sessionId });
    this.currentSessionId = sessionId;
  }
}

// Handle session updates
setupSessionHandlers(): void {
  this.socket.on('session:started', (data) => {
    dispatch(updateSessionStatus({ sessionId: data.sessionId, status: 'active' }));
  });

  this.socket.on('session:progress_update', (data) => {
    dispatch(updateSessionProgress(data));
  });
}
```

**Backend WebSocket Handler Needed**:
```python
# Add to chat.py
async def handle_session_join(websocket: WebSocket, data: dict):
    session_id = data["sessionId"]
    # Add websocket to session room
    await websocket.send_text(json.dumps({
        "event": "session:joined",
        "data": {"sessionId": session_id}
    }))

async def broadcast_session_update(session_id: str, update_data: dict):
    # Broadcast to all websockets in session
    for ws in session_websockets.get(session_id, []):
        await ws.send_text(json.dumps({
            "event": "session:progress_update",
            "data": update_data
        }))
```

## 🧪 Testing Implementation

### Integration Test Setup
**File**: `frontend/src/tests/setup.ts` (CREATE NEW)

```typescript
import { configureStore } from '@reduxjs/toolkit';
import { render } from '@testing-library/react';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';

// Test store configuration
export const createTestStore = () => configureStore({
  reducer: {
    auth: authReducer,
    characters: charactersReducer,
    // ... other reducers
  },
});

// Test wrapper component
export const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const store = createTestStore();

  return (
    <Provider store={store}>
      <BrowserRouter>
        <ThemeProvider theme={therapeuticTheme}>
          {children}
        </ThemeProvider>
      </BrowserRouter>
    </Provider>
  );
};

// Custom render function
export const renderWithProviders = (ui: React.ReactElement) => {
  return render(ui, { wrapper: TestWrapper });
};
```

### API Integration Tests
**File**: `frontend/src/tests/integration/auth.test.ts` (CREATE NEW)

```typescript
import { ttaApi } from '../../services/api';

describe('Authentication Integration', () => {
  const testCredentials = {
    username: 'test_user',
    password: 'test_password'
  };

  beforeEach(() => {
    // Clear any existing tokens
    ttaApi.clearAuthToken();
  });

  it('should login and receive valid token', async () => {
    const response = await ttaApi.login(testCredentials);

    expect(response.accessToken).toBeDefined();
    expect(response.userInfo).toBeDefined();
    expect(response.userInfo.username).toBe(testCredentials.username);
  });

  it('should get current user after login', async () => {
    await ttaApi.login(testCredentials);
    const user = await ttaApi.getCurrentUser();

    expect(user.username).toBe(testCredentials.username);
    expect(user.therapeuticPreferences).toBeDefined();
  });

  it('should handle token refresh', async () => {
    await ttaApi.login(testCredentials);
    const refreshResponse = await ttaApi.refreshToken();

    expect(refreshResponse.accessToken).toBeDefined();
  });
});
```

---

**Integration Status**: 🔄 **READY TO BEGIN**
**Backend Systems**: ✅ **OPERATIONAL** (Agent orchestration, living worlds, player experience APIs)
**Frontend Implementation**: ✅ **PRODUCTION-READY** (Needs integration work)
**Estimated Timeline**: 3-4 weeks for full integration

**Next Step**: Begin with Phase 1, Task 1.1 - Fix authentication endpoints
