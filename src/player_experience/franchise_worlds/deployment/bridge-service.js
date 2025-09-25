#!/usr/bin/env node

/**
 * TTA Franchise World Bridge Service
 * 
 * HTTP service wrapper for Node.js bridge scripts to enable
 * containerized execution and better error handling.
 */

const express = require('express');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.BRIDGE_PORT || 3001;
const LOG_LEVEL = process.env.LOG_LEVEL || 'info';

// Middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Logging utility
function log(level, message, data = null) {
  if (LOG_LEVEL === 'debug' || level !== 'debug') {
    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      level,
      message,
      data
    };
    console.log(JSON.stringify(logEntry));
  }
}

// Available bridge scripts
const BRIDGE_SCRIPTS = {
  'get-worlds': 'get-worlds.js',
  'convert-world': 'convert-world.js',
  'get-archetypes': 'get-archetypes.js',
  'adapt-archetype': 'adapt-archetype.js',
  'validate-world': 'validate-world.js',
  'create-parameters': 'create-parameters.js',
  'initialize-system': 'initialize-system.js'
};

// Execute bridge script
async function executeBridgeScript(scriptName, args = null) {
  return new Promise((resolve, reject) => {
    const scriptFile = BRIDGE_SCRIPTS[scriptName];
    if (!scriptFile) {
      reject(new Error(`Unknown script: ${scriptName}`));
      return;
    }

    const scriptPath = path.join(__dirname, 'scripts', scriptFile);
    
    // Check if script exists
    if (!fs.existsSync(scriptPath)) {
      reject(new Error(`Script file not found: ${scriptPath}`));
      return;
    }

    const nodeArgs = ['node', scriptPath];
    if (args) {
      nodeArgs.push(JSON.stringify(args));
    }

    log('debug', `Executing script: ${scriptName}`, { args });

    const child = spawn('node', [scriptPath, ...(args ? [JSON.stringify(args)] : [])], {
      cwd: path.join(__dirname, 'scripts'),
      stdio: ['pipe', 'pipe', 'pipe']
    });

    let stdout = '';
    let stderr = '';

    child.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    child.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    child.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(stdout);
          log('debug', `Script completed: ${scriptName}`, { code, result });
          resolve(result);
        } catch (parseError) {
          log('error', `Failed to parse script output: ${scriptName}`, { stdout, parseError: parseError.message });
          reject(new Error(`Invalid JSON output from script: ${parseError.message}`));
        }
      } else {
        log('error', `Script failed: ${scriptName}`, { code, stderr, stdout });
        reject(new Error(`Script failed with code ${code}: ${stderr || stdout}`));
      }
    });

    child.on('error', (error) => {
      log('error', `Script execution error: ${scriptName}`, { error: error.message });
      reject(error);
    });

    // Timeout after 30 seconds
    setTimeout(() => {
      child.kill('SIGTERM');
      reject(new Error(`Script timeout: ${scriptName}`));
    }, 30000);
  });
}

// API Routes

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'tta-franchise-bridge',
    version: '1.0.0'
  });
});

// Get all worlds
app.get('/worlds', async (req, res) => {
  try {
    const genre = req.query.genre;
    const args = genre ? { genre } : null;
    const result = await executeBridgeScript('get-worlds', args);
    res.json(result);
  } catch (error) {
    log('error', 'Failed to get worlds', { error: error.message });
    res.status(500).json({ error: error.message });
  }
});

// Convert world to TTA format
app.post('/worlds/:worldId/convert', async (req, res) => {
  try {
    const { worldId } = req.params;
    const result = await executeBridgeScript('convert-world', { worldId });
    res.json(result);
  } catch (error) {
    log('error', 'Failed to convert world', { worldId: req.params.worldId, error: error.message });
    res.status(500).json({ error: error.message });
  }
});

// Get all archetypes
app.get('/archetypes', async (req, res) => {
  try {
    const { archetypeId, role } = req.query;
    const args = {};
    if (archetypeId) args.archetypeId = archetypeId;
    if (role) args.role = role;
    
    const result = await executeBridgeScript('get-archetypes', Object.keys(args).length > 0 ? args : null);
    res.json(result);
  } catch (error) {
    log('error', 'Failed to get archetypes', { error: error.message });
    res.status(500).json({ error: error.message });
  }
});

// Adapt archetype for world
app.post('/archetypes/:archetypeId/adapt', async (req, res) => {
  try {
    const { archetypeId } = req.params;
    const { worldGenre, worldContext } = req.body;
    
    if (!worldGenre || !worldContext) {
      return res.status(400).json({ error: 'worldGenre and worldContext are required' });
    }
    
    const result = await executeBridgeScript('adapt-archetype', {
      archetypeId,
      worldGenre,
      worldContext
    });
    res.json(result);
  } catch (error) {
    log('error', 'Failed to adapt archetype', { 
      archetypeId: req.params.archetypeId, 
      error: error.message 
    });
    res.status(500).json({ error: error.message });
  }
});

// Validate world
app.post('/worlds/:worldId/validate', async (req, res) => {
  try {
    const { worldId } = req.params;
    const result = await executeBridgeScript('validate-world', { worldId });
    res.json(result);
  } catch (error) {
    log('error', 'Failed to validate world', { worldId: req.params.worldId, error: error.message });
    res.status(500).json({ error: error.message });
  }
});

// Create customized parameters
app.post('/worlds/:worldId/parameters', async (req, res) => {
  try {
    const { worldId } = req.params;
    const { playerPreferences } = req.body;
    
    if (!playerPreferences) {
      return res.status(400).json({ error: 'playerPreferences are required' });
    }
    
    const result = await executeBridgeScript('create-parameters', {
      worldId,
      playerPreferences
    });
    res.json(result);
  } catch (error) {
    log('error', 'Failed to create parameters', { 
      worldId: req.params.worldId, 
      error: error.message 
    });
    res.status(500).json({ error: error.message });
  }
});

// Initialize system
app.post('/system/initialize', async (req, res) => {
  try {
    const result = await executeBridgeScript('initialize-system');
    res.json(result);
  } catch (error) {
    log('error', 'Failed to initialize system', { error: error.message });
    res.status(500).json({ error: error.message });
  }
});

// System status
app.get('/system/status', async (req, res) => {
  try {
    const result = await executeBridgeScript('initialize-system');
    res.json({
      ...result,
      bridgeService: {
        status: 'operational',
        timestamp: new Date().toISOString(),
        availableScripts: Object.keys(BRIDGE_SCRIPTS)
      }
    });
  } catch (error) {
    log('error', 'Failed to get system status', { error: error.message });
    res.status(500).json({ 
      error: error.message,
      bridgeService: {
        status: 'degraded',
        timestamp: new Date().toISOString()
      }
    });
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  log('error', 'Unhandled error', { error: error.message, stack: error.stack });
  res.status(500).json({ error: 'Internal server error' });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Endpoint not found' });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  log('info', `TTA Franchise Bridge Service started on port ${PORT}`);
  log('info', 'Available scripts:', { scripts: Object.keys(BRIDGE_SCRIPTS) });
});

// Graceful shutdown
process.on('SIGTERM', () => {
  log('info', 'Received SIGTERM, shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', () => {
  log('info', 'Received SIGINT, shutting down gracefully');
  process.exit(0);
});
