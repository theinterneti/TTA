#!/usr/bin/env python3
"""
Simple FastAPI server for Keploy testing
Runs on http://localhost:8000
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="TTA Simple Test API", version="1.0.0")

# In-memory storage
sessions: dict[str, dict] = {}


class SessionCreate(BaseModel):
    user_id: str
    game_type: str = "adventure"


class SessionResponse(BaseModel):
    session_id: str
    user_id: str
    game_type: str
    status: str


@app.get("/")
async def root():
    """Root endpoint"""
    return {"service": "TTA Simple Test API", "version": "1.0.0", "status": "running"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "sessions_count": len(sessions)}


@app.post("/api/v1/sessions", response_model=SessionResponse)
async def create_session(session: SessionCreate):
    """Create a new game session"""
    import uuid

    session_id = str(uuid.uuid4())

    sessions[session_id] = {
        "session_id": session_id,
        "user_id": session.user_id,
        "game_type": session.game_type,
        "status": "active",
    }

    return sessions[session_id]


@app.get("/api/v1/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get session by ID"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    return sessions[session_id]


@app.get("/api/v1/sessions", response_model=list[SessionResponse])
async def list_sessions():
    """List all sessions"""
    return list(sessions.values())


@app.delete("/api/v1/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    del sessions[session_id]
    return {"status": "deleted", "session_id": session_id}


if __name__ == "__main__":
    print("🚀 Starting TTA Simple Test API on http://localhost:8000")
    print("📝 API Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
