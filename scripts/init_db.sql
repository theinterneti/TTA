-- TTA Database Initialization Script
-- This script sets up the basic database structure for the TTA platform

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS tta_core;
CREATE SCHEMA IF NOT EXISTS tta_player;
CREATE SCHEMA IF NOT EXISTS tta_clinical;
CREATE SCHEMA IF NOT EXISTS tta_analytics;

-- Set search path
SET search_path TO tta_core, tta_player, tta_clinical, tta_analytics, public;

-- Create basic tables
CREATE TABLE IF NOT EXISTS tta_core.system_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key VARCHAR(255) UNIQUE NOT NULL,
    value JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tta_player.players (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    profile JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS tta_player.sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    player_id UUID REFERENCES tta_player.players(id) ON DELETE CASCADE,
    session_data JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_players_email ON tta_player.players(email);
CREATE INDEX IF NOT EXISTS idx_players_username ON tta_player.players(username);
CREATE INDEX IF NOT EXISTS idx_sessions_player_id ON tta_player.sessions(player_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON tta_player.sessions(status);

-- Insert default configuration
INSERT INTO tta_core.system_config (key, value) VALUES
    ('app_version', '"1.0.0"'),
    ('maintenance_mode', 'false'),
    ('max_sessions_per_user', '5')
ON CONFLICT (key) DO NOTHING;
