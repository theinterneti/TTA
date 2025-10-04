/**
 * Mock API Server for E2E Testing
 * Provides a lightweight mock backend for Playwright tests
 */

const express = require('express');
const cors = require('cors');
const { WebSocketServer } = require('ws');
const http = require('http');

const app = express();
const server = http.createServer(app);
const wss = new WebSocketServer({ server });

// Middleware
app.use(cors({
  origin: ['http://localhost:3000', 'http://localhost:8000'],
  credentials: true
}));
app.use(express.json());

// In-memory storage
let players = new Map();
let characters = new Map();
let sessions = new Map();
let chatHistory = new Map();
let settings = new Map();

// Mock data generators
const generateId = () => Math.random().toString(36).substr(2, 9);

const mockPlayer = (id = generateId()) => ({
  id,
  username: `player_${id}`,
  email: `player_${id}@example.com`,
  created_at: new Date().toISOString(),
  last_login: new Date().toISOString(),
  preferences: {
    theme: 'light',
    notifications: true
  }
});

const mockCharacter = (playerId, id = generateId()) => ({
  id,
  player_id: playerId,
  name: `Character ${id}`,
  description: `A test character for player ${playerId}`,
  story: `This character was created for testing purposes.`,
  avatar_url: null,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString()
});

const mockSession = (playerId, characterId, id = generateId()) => ({
  id,
  player_id: playerId,
  character_id: characterId,
  world_id: 'test-world',
  status: 'active',
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  metadata: {}
});

// Initialize mock data
const testPlayerId = 'test-player-1';
players.set(testPlayerId, mockPlayer(testPlayerId));

const testCharacterId = 'test-character-1';
characters.set(testCharacterId, mockCharacter(testPlayerId, testCharacterId));

const testSessionId = 'test-session-1';
sessions.set(testSessionId, mockSession(testPlayerId, testCharacterId, testSessionId));

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Authentication endpoints
app.post('/auth/login', (req, res) => {
  const { username, password } = req.body;
  
  if (!username || !password) {
    return res.status(400).json({ error: 'Username and password required' });
  }
  
  // Mock authentication - accept any credentials for testing
  const player = mockPlayer();
  player.username = username;
  players.set(player.id, player);
  
  res.json({
    access_token: `mock_token_${player.id}`,
    refresh_token: `mock_refresh_${player.id}`,
    player: player
  });
});

app.post('/auth/logout', (req, res) => {
  res.json({ message: 'Logged out successfully' });
});

// Player endpoints
app.get('/players/:playerId', (req, res) => {
  const player = players.get(req.params.playerId);
  if (!player) {
    return res.status(404).json({ error: 'Player not found' });
  }
  res.json(player);
});

app.put('/players/:playerId', (req, res) => {
  const player = players.get(req.params.playerId);
  if (!player) {
    return res.status(404).json({ error: 'Player not found' });
  }
  
  Object.assign(player, req.body);
  player.updated_at = new Date().toISOString();
  players.set(req.params.playerId, player);
  
  res.json(player);
});

// Character endpoints
app.get('/players/:playerId/characters', (req, res) => {
  const playerCharacters = Array.from(characters.values())
    .filter(char => char.player_id === req.params.playerId);
  res.json(playerCharacters);
});

app.post('/players/:playerId/characters', (req, res) => {
  const character = mockCharacter(req.params.playerId);
  Object.assign(character, req.body);
  characters.set(character.id, character);
  res.status(201).json(character);
});

app.get('/players/:playerId/characters/:characterId', (req, res) => {
  const character = characters.get(req.params.characterId);
  if (!character || character.player_id !== req.params.playerId) {
    return res.status(404).json({ error: 'Character not found' });
  }
  res.json(character);
});

app.put('/players/:playerId/characters/:characterId', (req, res) => {
  const character = characters.get(req.params.characterId);
  if (!character || character.player_id !== req.params.playerId) {
    return res.status(404).json({ error: 'Character not found' });
  }
  
  Object.assign(character, req.body);
  character.updated_at = new Date().toISOString();
  characters.set(req.params.characterId, character);
  
  res.json(character);
});

app.delete('/players/:playerId/characters/:characterId', (req, res) => {
  const character = characters.get(req.params.characterId);
  if (!character || character.player_id !== req.params.playerId) {
    return res.status(404).json({ error: 'Character not found' });
  }
  
  characters.delete(req.params.characterId);
  res.status(204).send();
});

// Session endpoints
app.get('/players/:playerId/sessions', (req, res) => {
  const playerSessions = Array.from(sessions.values())
    .filter(session => session.player_id === req.params.playerId);
  res.json(playerSessions);
});

app.post('/players/:playerId/sessions', (req, res) => {
  const session = mockSession(req.params.playerId, req.body.character_id);
  Object.assign(session, req.body);
  sessions.set(session.id, session);
  res.status(201).json(session);
});

// Chat endpoints
app.get('/sessions/:sessionId/messages', (req, res) => {
  const messages = chatHistory.get(req.params.sessionId) || [];
  res.json(messages);
});

app.post('/sessions/:sessionId/messages', (req, res) => {
  const sessionId = req.params.sessionId;
  const messages = chatHistory.get(sessionId) || [];
  
  const message = {
    id: generateId(),
    session_id: sessionId,
    content: req.body.message,
    sender: 'user',
    timestamp: new Date().toISOString()
  };
  
  messages.push(message);
  chatHistory.set(sessionId, messages);
  
  // Simulate AI response
  setTimeout(() => {
    const aiResponse = {
      id: generateId(),
      session_id: sessionId,
      content: `AI response to: ${req.body.message}`,
      sender: 'ai',
      timestamp: new Date().toISOString()
    };
    
    messages.push(aiResponse);
    chatHistory.set(sessionId, messages);
    
    // Broadcast to WebSocket clients
    wss.clients.forEach(client => {
      if (client.readyState === 1) { // WebSocket.OPEN
        client.send(JSON.stringify(aiResponse));
      }
    });
  }, 1000);
  
  res.status(201).json(message);
});

// Settings endpoints
app.get('/players/:playerId/settings/:category', (req, res) => {
  const key = `${req.params.playerId}_${req.params.category}`;
  const playerSettings = settings.get(key) || {};
  res.json(playerSettings);
});

app.put('/players/:playerId/settings/:category', (req, res) => {
  const key = `${req.params.playerId}_${req.params.category}`;
  settings.set(key, req.body);
  res.json({ success: true });
});

// Data export endpoint
app.get('/players/:playerId/data/export', (req, res) => {
  const player = players.get(req.params.playerId);
  const playerCharacters = Array.from(characters.values())
    .filter(char => char.player_id === req.params.playerId);
  const playerSessions = Array.from(sessions.values())
    .filter(session => session.player_id === req.params.playerId);
  
  const exportData = {
    player,
    characters: playerCharacters,
    sessions: playerSessions,
    exported_at: new Date().toISOString()
  };
  
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Content-Disposition', 'attachment; filename="user-data.json"');
  res.json(exportData);
});

// Data deletion endpoint
app.delete('/players/:playerId/data', (req, res) => {
  // Delete all player data
  players.delete(req.params.playerId);
  
  // Delete characters
  for (const [id, character] of characters.entries()) {
    if (character.player_id === req.params.playerId) {
      characters.delete(id);
    }
  }
  
  // Delete sessions
  for (const [id, session] of sessions.entries()) {
    if (session.player_id === req.params.playerId) {
      sessions.delete(id);
      chatHistory.delete(id);
    }
  }
  
  res.status(204).send();
});

// WebSocket connection handling
wss.on('connection', (ws) => {
  console.log('WebSocket client connected');
  
  ws.on('message', (data) => {
    try {
      const message = JSON.parse(data.toString());
      console.log('Received WebSocket message:', message);
      
      // Echo back for testing
      ws.send(JSON.stringify({
        type: 'echo',
        data: message,
        timestamp: new Date().toISOString()
      }));
    } catch (error) {
      console.error('WebSocket message error:', error);
    }
  });
  
  ws.on('close', () => {
    console.log('WebSocket client disconnected');
  });
});

// Error handling
app.use((error, req, res, next) => {
  console.error('API Error:', error);
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
const PORT = process.env.PORT || 8000;
server.listen(PORT, () => {
  console.log(`Mock API server running on http://localhost:${PORT}`);
  console.log(`Health check: http://localhost:${PORT}/health`);
  console.log(`API docs: http://localhost:${PORT}/docs`);
});

module.exports = { app, server };
