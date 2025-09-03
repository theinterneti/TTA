#!/usr/bin/env python3
"""
Therapeutic Chat Interface Test Server.

A simple FastAPI server to test the Therapeutic Chat Interface System
with a web-based interface for comprehensive browser testing.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import our therapeutic chat interface
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.components.user_experience.therapeutic_chat_interface import (
    TherapeuticChatInterface,
    MessageType,
    ConversationState,
    TherapeuticFramework,
)

from src.components.user_experience.universal_accessibility_system import (
    UniversalAccessibilitySystem,
)

from src.components.user_experience.advanced_user_interface_engine import (
    AdvancedUserInterfaceEngine,
)

from src.components.user_experience.engagement_optimization_system import (
    EngagementOptimizationSystem,
)

from src.components.advanced_therapeutic_intelligence.intelligent_personalization_engine import (
    IntelligentPersonalizationEngine,
)

from src.components.therapeutic_systems import (
    TherapeuticConsequenceSystem,
    TherapeuticEmotionalSafetySystem,
    TherapeuticAdaptiveDifficultyEngine,
    TherapeuticCharacterDevelopmentSystem,
    TherapeuticIntegrationSystem,
    TherapeuticGameplayLoopController,
    TherapeuticReplayabilitySystem,
    TherapeuticCollaborativeSystem,
    TherapeuticErrorRecoveryManager,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global chat interface instance
chat_interface: TherapeuticChatInterface = None
active_connections: Dict[str, WebSocket] = {}

app = FastAPI(
    title="Therapeutic Chat Interface Test Server",
    description="Test server for comprehensive browser testing of the Therapeutic Chat Interface System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize the therapeutic chat interface and supporting systems."""
    global chat_interface
    
    logger.info("🌐 Initializing Therapeutic Chat Interface Test Server")
    
    # Initialize chat interface
    chat_interface = TherapeuticChatInterface()
    await chat_interface.initialize()
    
    # Initialize supporting systems
    accessibility_system = UniversalAccessibilitySystem()
    await accessibility_system.initialize()
    
    ui_engine = AdvancedUserInterfaceEngine()
    await ui_engine.initialize()
    
    engagement_system = EngagementOptimizationSystem()
    await engagement_system.initialize()
    
    personalization_engine = IntelligentPersonalizationEngine()
    await personalization_engine.initialize()
    
    # Initialize therapeutic systems
    consequence_system = TherapeuticConsequenceSystem()
    await consequence_system.initialize()
    
    emotional_safety = TherapeuticEmotionalSafetySystem()
    await emotional_safety.initialize()
    
    adaptive_difficulty = TherapeuticAdaptiveDifficultyEngine()
    await adaptive_difficulty.initialize()
    
    character_development = TherapeuticCharacterDevelopmentSystem()
    await character_development.initialize()
    
    therapeutic_integration = TherapeuticIntegrationSystem()
    await therapeutic_integration.initialize()
    
    gameplay_controller = TherapeuticGameplayLoopController()
    await gameplay_controller.initialize()
    
    replayability_system = TherapeuticReplayabilitySystem()
    await replayability_system.initialize()
    
    collaborative_system = TherapeuticCollaborativeSystem()
    await collaborative_system.initialize()
    
    error_recovery_manager = TherapeuticErrorRecoveryManager()
    await error_recovery_manager.initialize()
    
    # Inject dependencies
    therapeutic_systems = {
        "consequence_system": consequence_system,
        "emotional_safety_system": emotional_safety,
        "adaptive_difficulty_engine": adaptive_difficulty,
        "character_development_system": character_development,
        "therapeutic_integration_system": therapeutic_integration,
        "gameplay_loop_controller": gameplay_controller,
        "replayability_system": replayability_system,
        "collaborative_system": collaborative_system,
        "error_recovery_manager": error_recovery_manager,
    }
    
    chat_interface.inject_accessibility_system(accessibility_system)
    chat_interface.inject_ui_engine(ui_engine)
    chat_interface.inject_engagement_system(engagement_system)
    chat_interface.inject_personalization_engine(personalization_engine)
    chat_interface.inject_therapeutic_systems(**therapeutic_systems)
    
    logger.info("✅ Therapeutic Chat Interface Test Server initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown the therapeutic chat interface."""
    global chat_interface
    if chat_interface:
        await chat_interface.shutdown()
    logger.info("🔄 Therapeutic Chat Interface Test Server shutdown complete")

@app.get("/", response_class=HTMLResponse)
async def get_test_interface():
    """Serve the test interface HTML."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Therapeutic Chat Interface Test</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            
            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                width: 100%;
                max-width: 1200px;
                height: 80vh;
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
                padding: 20px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 2rem;
                margin-bottom: 10px;
            }
            
            .header p {
                opacity: 0.9;
                font-size: 1.1rem;
            }
            
            .main-content {
                display: flex;
                flex: 1;
                overflow: hidden;
            }
            
            .sidebar {
                width: 300px;
                background: #f8f9fa;
                border-right: 1px solid #e9ecef;
                padding: 20px;
                overflow-y: auto;
            }
            
            .chat-area {
                flex: 1;
                display: flex;
                flex-direction: column;
            }
            
            .messages {
                flex: 1;
                padding: 20px;
                overflow-y: auto;
                background: #fafafa;
            }
            
            .message {
                margin-bottom: 15px;
                padding: 12px 16px;
                border-radius: 12px;
                max-width: 80%;
                word-wrap: break-word;
            }
            
            .message.user {
                background: #007bff;
                color: white;
                margin-left: auto;
                text-align: right;
            }
            
            .message.assistant {
                background: white;
                border: 1px solid #e9ecef;
                margin-right: auto;
            }
            
            .message.crisis {
                background: #dc3545;
                color: white;
                border-left: 4px solid #721c24;
            }
            
            .message.system {
                background: #28a745;
                color: white;
                text-align: center;
                margin: 0 auto;
            }
            
            .input-area {
                padding: 20px;
                background: white;
                border-top: 1px solid #e9ecef;
                display: flex;
                gap: 10px;
            }
            
            .input-area input {
                flex: 1;
                padding: 12px 16px;
                border: 1px solid #ddd;
                border-radius: 25px;
                font-size: 16px;
                outline: none;
            }
            
            .input-area input:focus {
                border-color: #007bff;
                box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
            }
            
            .input-area button {
                padding: 12px 24px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-size: 16px;
                transition: background 0.3s;
            }
            
            .input-area button:hover {
                background: #0056b3;
            }
            
            .input-area button:disabled {
                background: #6c757d;
                cursor: not-allowed;
            }
            
            .session-info {
                background: white;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 20px;
                border: 1px solid #e9ecef;
            }
            
            .session-info h3 {
                color: #495057;
                margin-bottom: 10px;
                font-size: 1.1rem;
            }
            
            .session-info p {
                color: #6c757d;
                font-size: 0.9rem;
                margin-bottom: 5px;
            }
            
            .controls {
                background: white;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 20px;
                border: 1px solid #e9ecef;
            }
            
            .controls h3 {
                color: #495057;
                margin-bottom: 15px;
                font-size: 1.1rem;
            }
            
            .control-group {
                margin-bottom: 15px;
            }
            
            .control-group label {
                display: block;
                margin-bottom: 5px;
                color: #495057;
                font-weight: 500;
            }
            
            .control-group select,
            .control-group input {
                width: 100%;
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            
            .control-group button {
                width: 100%;
                padding: 10px;
                background: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                margin-top: 5px;
            }
            
            .control-group button:hover {
                background: #218838;
            }
            
            .status {
                padding: 10px;
                border-radius: 4px;
                margin-bottom: 10px;
                font-size: 14px;
            }
            
            .status.connected {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            
            .status.disconnected {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
            
            .metrics {
                background: white;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #e9ecef;
            }
            
            .metrics h3 {
                color: #495057;
                margin-bottom: 15px;
                font-size: 1.1rem;
            }
            
            .metric {
                display: flex;
                justify-content: space-between;
                margin-bottom: 8px;
                font-size: 14px;
            }
            
            .metric-label {
                color: #6c757d;
            }
            
            .metric-value {
                color: #495057;
                font-weight: 500;
            }
            
            @media (max-width: 768px) {
                .main-content {
                    flex-direction: column;
                }
                
                .sidebar {
                    width: 100%;
                    max-height: 200px;
                }
                
                .container {
                    height: 95vh;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>💬 Therapeutic Chat Interface Test</h1>
                <p>Comprehensive browser testing of the TTA Therapeutic Chat Interface System</p>
            </div>
            
            <div class="main-content">
                <div class="sidebar">
                    <div id="status" class="status disconnected">
                        🔴 Disconnected
                    </div>
                    
                    <div class="session-info">
                        <h3>📋 Session Info</h3>
                        <p><strong>Session ID:</strong> <span id="sessionId">Not started</span></p>
                        <p><strong>User ID:</strong> <span id="userId">test_user_001</span></p>
                        <p><strong>State:</strong> <span id="sessionState">Not started</span></p>
                        <p><strong>Messages:</strong> <span id="messageCount">0</span></p>
                    </div>
                    
                    <div class="controls">
                        <h3>🎛️ Controls</h3>
                        
                        <div class="control-group">
                            <label for="therapeuticGoals">Therapeutic Goals:</label>
                            <select id="therapeuticGoals" multiple>
                                <option value="anxiety_management">Anxiety Management</option>
                                <option value="depression_recovery">Depression Recovery</option>
                                <option value="stress_reduction">Stress Reduction</option>
                                <option value="mindfulness_practice">Mindfulness Practice</option>
                                <option value="emotional_regulation">Emotional Regulation</option>
                                <option value="crisis_intervention">Crisis Intervention</option>
                            </select>
                        </div>
                        
                        <div class="control-group">
                            <button onclick="startSession()">🚀 Start New Session</button>
                            <button onclick="endSession()">🛑 End Session</button>
                        </div>
                        
                        <div class="control-group">
                            <button onclick="testCrisisMessage()">🚨 Test Crisis Detection</button>
                            <button onclick="testFrameworkSelection()">🧠 Test Framework Selection</button>
                        </div>
                    </div>
                    
                    <div class="metrics">
                        <h3>📊 Metrics</h3>
                        <div class="metric">
                            <span class="metric-label">Response Time:</span>
                            <span class="metric-value" id="responseTime">-</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Framework:</span>
                            <span class="metric-value" id="lastFramework">-</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Crisis Risk:</span>
                            <span class="metric-value" id="crisisRisk">-</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Confidence:</span>
                            <span class="metric-value" id="confidence">-</span>
                        </div>
                    </div>
                </div>
                
                <div class="chat-area">
                    <div id="messages" class="messages">
                        <div class="message system">
                            Welcome to the Therapeutic Chat Interface Test! Click "Start New Session" to begin.
                        </div>
                    </div>
                    
                    <div class="input-area">
                        <input 
                            type="text" 
                            id="messageInput" 
                            placeholder="Type your message here..." 
                            disabled
                            onkeypress="handleKeyPress(event)"
                        >
                        <button id="sendButton" onclick="sendMessage()" disabled>Send</button>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            let ws = null;
            let currentSessionId = null;
            let messageCount = 0;
            
            // Connect to WebSocket
            function connect() {
                ws = new WebSocket('ws://localhost:8000/ws/chat');
                
                ws.onopen = function(event) {
                    updateStatus('connected', '🟢 Connected');
                    console.log('Connected to chat server');
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    handleMessage(data);
                };
                
                ws.onclose = function(event) {
                    updateStatus('disconnected', '🔴 Disconnected');
                    console.log('Disconnected from chat server');
                    
                    // Attempt to reconnect after 3 seconds
                    setTimeout(connect, 3000);
                };
                
                ws.onerror = function(error) {
                    console.error('WebSocket error:', error);
                    updateStatus('disconnected', '🔴 Connection Error');
                };
            }
            
            function updateStatus(className, text) {
                const status = document.getElementById('status');
                status.className = `status ${className}`;
                status.textContent = text;
            }
            
            function handleMessage(data) {
                console.log('Received message:', data);
                
                if (data.type === 'session_started') {
                    currentSessionId = data.session_id;
                    document.getElementById('sessionId').textContent = data.session_id.substring(0, 8) + '...';
                    document.getElementById('sessionState').textContent = data.state;
                    document.getElementById('messageInput').disabled = false;
                    document.getElementById('sendButton').disabled = false;
                    
                    addMessage('system', 'Session started successfully! You can now send messages.');
                    
                } else if (data.type === 'message_response') {
                    const response = data.response;
                    
                    // Update metrics
                    document.getElementById('responseTime').textContent = `${response.processing_time_ms.toFixed(2)}ms`;
                    document.getElementById('lastFramework').textContent = response.therapeutic_frameworks[0] || 'default';
                    document.getElementById('crisisRisk').textContent = response.crisis_risk_level.toFixed(2);
                    document.getElementById('confidence').textContent = response.confidence_score.toFixed(2);
                    
                    // Add response message
                    const messageClass = response.message_type === 'crisis_intervention' ? 'crisis' : 'assistant';
                    addMessage(messageClass, response.content);
                    
                    messageCount++;
                    document.getElementById('messageCount').textContent = messageCount;
                    
                } else if (data.type === 'session_ended') {
                    document.getElementById('sessionState').textContent = 'Ended';
                    document.getElementById('messageInput').disabled = true;
                    document.getElementById('sendButton').disabled = true;
                    
                    addMessage('system', 'Session ended. Summary: ' + data.summary.summary_text);
                    
                } else if (data.type === 'error') {
                    addMessage('system', 'Error: ' + data.message);
                }
            }
            
            function addMessage(type, content) {
                const messagesDiv = document.getElementById('messages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${type}`;
                messageDiv.textContent = content;
                messagesDiv.appendChild(messageDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
            
            function startSession() {
                if (!ws || ws.readyState !== WebSocket.OPEN) {
                    alert('Not connected to server');
                    return;
                }
                
                const goals = Array.from(document.getElementById('therapeuticGoals').selectedOptions)
                    .map(option => option.value);
                
                if (goals.length === 0) {
                    goals.push('general_support');
                }
                
                const message = {
                    type: 'start_session',
                    user_id: 'test_user_001',
                    therapeutic_goals: goals,
                    session_config: {
                        max_duration: 60,
                        enable_crisis_detection: true
                    }
                };
                
                ws.send(JSON.stringify(message));
                messageCount = 0;
            }
            
            function endSession() {
                if (!currentSessionId) {
                    alert('No active session');
                    return;
                }
                
                const message = {
                    type: 'end_session',
                    session_id: currentSessionId
                };
                
                ws.send(JSON.stringify(message));
                currentSessionId = null;
            }
            
            function sendMessage() {
                const input = document.getElementById('messageInput');
                const messageText = input.value.trim();
                
                if (!messageText || !currentSessionId) {
                    return;
                }
                
                // Add user message to chat
                addMessage('user', messageText);
                
                // Send to server
                const message = {
                    type: 'user_message',
                    session_id: currentSessionId,
                    content: messageText,
                    metadata: {
                        timestamp: new Date().toISOString()
                    }
                };
                
                ws.send(JSON.stringify(message));
                input.value = '';
            }
            
            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }
            
            function testCrisisMessage() {
                if (!currentSessionId) {
                    alert('Please start a session first');
                    return;
                }
                
                document.getElementById('messageInput').value = "I can't take this anymore. I just want to end it all.";
                sendMessage();
            }
            
            function testFrameworkSelection() {
                if (!currentSessionId) {
                    alert('Please start a session first');
                    return;
                }
                
                const frameworks = [
                    "I keep thinking that everything will go wrong.",
                    "I'm feeling overwhelmed with intense emotions.",
                    "I want to be more present and mindful.",
                    "What strategies have worked for me before?"
                ];
                
                const randomMessage = frameworks[Math.floor(Math.random() * frameworks.length)];
                document.getElementById('messageInput').value = randomMessage;
                sendMessage();
            }
            
            // Initialize connection when page loads
            window.onload = function() {
                connect();
            };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for chat communication."""
    await websocket.accept()
    connection_id = f"conn_{datetime.now().timestamp()}"
    active_connections[connection_id] = websocket
    
    logger.info(f"WebSocket connection established: {connection_id}")
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            logger.info(f"Received message: {message['type']}")
            
            if message["type"] == "start_session":
                # Start new chat session
                session = await chat_interface.start_chat_session(
                    user_id=message["user_id"],
                    therapeutic_goals=message["therapeutic_goals"],
                    session_config=message.get("session_config", {})
                )
                
                await websocket.send_text(json.dumps({
                    "type": "session_started",
                    "session_id": session.session_id,
                    "user_id": session.user_id,
                    "state": session.conversation_state.value,
                    "goals": session.session_goals
                }))
                
            elif message["type"] == "user_message":
                # Process user message
                response = await chat_interface.process_user_message(
                    session_id=message["session_id"],
                    message_content=message["content"],
                    message_metadata=message.get("metadata", {})
                )
                
                await websocket.send_text(json.dumps({
                    "type": "message_response",
                    "response": {
                        "message_id": response.message_id,
                        "message_type": response.message_type.value,
                        "content": response.content,
                        "processing_time_ms": response.processing_time_ms,
                        "confidence_score": response.confidence_score,
                        "therapeutic_frameworks": [fw.value for fw in response.therapeutic_frameworks],
                        "crisis_risk_level": response.crisis_risk_level,
                        "response_priority": response.response_priority.value,
                        "requires_human_review": response.requires_human_review
                    }
                }))
                
            elif message["type"] == "end_session":
                # End chat session
                summary = await chat_interface.end_chat_session(
                    session_id=message["session_id"]
                )
                
                await websocket.send_text(json.dumps({
                    "type": "session_ended",
                    "session_id": message["session_id"],
                    "summary": summary
                }))
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket connection closed: {connection_id}")
        active_connections.pop(connection_id, None)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        }))

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    if chat_interface:
        health = await chat_interface.health_check()
        return health
    else:
        raise HTTPException(status_code=503, detail="Chat interface not initialized")

@app.get("/api/metrics")
async def get_metrics():
    """Get system metrics."""
    if chat_interface:
        return chat_interface.chat_system_metrics
    else:
        raise HTTPException(status_code=503, detail="Chat interface not initialized")

if __name__ == "__main__":
    uvicorn.run(
        "chat_test_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
