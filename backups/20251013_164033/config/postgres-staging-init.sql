-- PostgreSQL Initialization Script for TTA Staging Environment
-- Creates necessary databases, users, and initial schema

-- Set client encoding and timezone
SET client_encoding = 'UTF8';
SET timezone = 'UTC';

-- Create staging-specific database if it doesn't exist
SELECT 'CREATE DATABASE tta_staging'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'tta_staging');

-- Connect to the staging database
\c tta_staging;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create staging-specific schemas
CREATE SCHEMA IF NOT EXISTS tta_core;
CREATE SCHEMA IF NOT EXISTS tta_player;
CREATE SCHEMA IF NOT EXISTS tta_session;
CREATE SCHEMA IF NOT EXISTS tta_analytics;
CREATE SCHEMA IF NOT EXISTS tta_testing;

-- Set search path
SET search_path TO tta_core, tta_player, tta_session, tta_analytics, public;

-- Create staging user management tables
CREATE TABLE IF NOT EXISTS tta_core.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',

    -- Staging-specific fields
    is_test_user BOOLEAN DEFAULT false,
    test_group VARCHAR(50),
    staging_notes TEXT
);

-- Create player profiles table
CREATE TABLE IF NOT EXISTS tta_player.profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES tta_core.users(id) ON DELETE CASCADE,
    display_name VARCHAR(100) NOT NULL,
    avatar_url VARCHAR(500),
    preferences JSONB DEFAULT '{}',
    statistics JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Staging-specific fields
    test_scenario VARCHAR(100),
    performance_metrics JSONB DEFAULT '{}'
);

-- Create characters table
CREATE TABLE IF NOT EXISTS tta_player.characters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES tta_core.users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    attributes JSONB DEFAULT '{}',
    backstory TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,

    -- Staging-specific fields
    test_character BOOLEAN DEFAULT false,
    validation_status VARCHAR(20) DEFAULT 'pending'
);

-- Create sessions table
CREATE TABLE IF NOT EXISTS tta_session.sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES tta_core.users(id) ON DELETE CASCADE,
    character_id UUID REFERENCES tta_player.characters(id) ON DELETE SET NULL,
    world_id VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    session_data JSONB DEFAULT '{}',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Staging-specific fields
    test_session BOOLEAN DEFAULT false,
    concurrent_users INTEGER DEFAULT 1,
    performance_data JSONB DEFAULT '{}'
);

-- Create session messages table
CREATE TABLE IF NOT EXISTS tta_session.messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES tta_session.sessions(id) ON DELETE CASCADE,
    message_type VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Staging-specific fields
    response_time_ms INTEGER,
    ai_model_used VARCHAR(100)
);

-- Create analytics tables for staging
CREATE TABLE IF NOT EXISTS tta_analytics.events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES tta_core.users(id) ON DELETE SET NULL,
    session_id UUID REFERENCES tta_session.sessions(id) ON DELETE SET NULL,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Staging-specific fields
    test_run_id UUID,
    environment VARCHAR(20) DEFAULT 'staging'
);

-- Create testing-specific tables
CREATE TABLE IF NOT EXISTS tta_testing.test_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    test_type VARCHAR(50) NOT NULL,
    configuration JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'pending',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    results JSONB DEFAULT '{}',

    -- Performance metrics
    total_users INTEGER,
    concurrent_users INTEGER,
    duration_seconds INTEGER,
    success_rate DECIMAL(5,4),
    avg_response_time_ms INTEGER
);

CREATE TABLE IF NOT EXISTS tta_testing.test_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_run_id UUID NOT NULL REFERENCES tta_testing.test_runs(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,4),
    metric_unit VARCHAR(20),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_username ON tta_core.users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON tta_core.users(email);
CREATE INDEX IF NOT EXISTS idx_users_test_user ON tta_core.users(is_test_user);
CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON tta_player.profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_characters_user_id ON tta_player.characters(user_id);
CREATE INDEX IF NOT EXISTS idx_characters_test ON tta_player.characters(test_character);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON tta_session.sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON tta_session.sessions(status);
CREATE INDEX IF NOT EXISTS idx_sessions_test ON tta_session.sessions(test_session);
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON tta_session.messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON tta_session.messages(created_at);
CREATE INDEX IF NOT EXISTS idx_events_user_id ON tta_analytics.events(user_id);
CREATE INDEX IF NOT EXISTS idx_events_session_id ON tta_analytics.events(session_id);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON tta_analytics.events(timestamp);
CREATE INDEX IF NOT EXISTS idx_test_runs_status ON tta_testing.test_runs(status);
CREATE INDEX IF NOT EXISTS idx_test_metrics_run_id ON tta_testing.test_metrics(test_run_id);

-- Create functions for staging
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON tta_core.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON tta_player.profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_characters_updated_at BEFORE UPDATE ON tta_player.characters
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert staging-specific seed data
INSERT INTO tta_core.users (username, email, password_hash, is_test_user, test_group) VALUES
('staging_admin', 'admin@staging.tta', '$2b$12$staging_hash_placeholder', true, 'admin'),
('test_user_1', 'user1@staging.tta', '$2b$12$staging_hash_placeholder', true, 'basic'),
('test_user_2', 'user2@staging.tta', '$2b$12$staging_hash_placeholder', true, 'basic'),
('load_test_user', 'load@staging.tta', '$2b$12$staging_hash_placeholder', true, 'load_test')
ON CONFLICT (username) DO NOTHING;

-- Create staging-specific views
CREATE OR REPLACE VIEW tta_analytics.staging_metrics AS
SELECT
    DATE_TRUNC('hour', timestamp) as hour,
    event_type,
    COUNT(*) as event_count,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(DISTINCT session_id) as unique_sessions
FROM tta_analytics.events
WHERE environment = 'staging'
GROUP BY DATE_TRUNC('hour', timestamp), event_type
ORDER BY hour DESC;

-- Grant permissions
GRANT USAGE ON SCHEMA tta_core TO tta_staging_user;
GRANT USAGE ON SCHEMA tta_player TO tta_staging_user;
GRANT USAGE ON SCHEMA tta_session TO tta_staging_user;
GRANT USAGE ON SCHEMA tta_analytics TO tta_staging_user;
GRANT USAGE ON SCHEMA tta_testing TO tta_staging_user;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA tta_core TO tta_staging_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA tta_player TO tta_staging_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA tta_session TO tta_staging_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA tta_analytics TO tta_staging_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA tta_testing TO tta_staging_user;

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA tta_core TO tta_staging_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA tta_player TO tta_staging_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA tta_session TO tta_staging_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA tta_analytics TO tta_staging_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA tta_testing TO tta_staging_user;

-- Create staging-specific stored procedures
CREATE OR REPLACE FUNCTION tta_testing.create_test_run(
    p_name VARCHAR(200),
    p_description TEXT,
    p_test_type VARCHAR(50),
    p_configuration JSONB DEFAULT '{}'
) RETURNS UUID AS $$
DECLARE
    test_run_id UUID;
BEGIN
    INSERT INTO tta_testing.test_runs (name, description, test_type, configuration)
    VALUES (p_name, p_description, p_test_type, p_configuration)
    RETURNING id INTO test_run_id;

    RETURN test_run_id;
END;
$$ LANGUAGE plpgsql;

-- Staging environment marker
COMMENT ON DATABASE tta_staging IS 'TTA Staging Database - Homelab Environment';

-- Log initialization completion
DO $$
BEGIN
    RAISE NOTICE 'TTA Staging Database initialized successfully';
    RAISE NOTICE 'Environment: staging';
    RAISE NOTICE 'Schemas created: tta_core, tta_player, tta_session, tta_analytics, tta_testing';
    RAISE NOTICE 'Test users created: 4';
    RAISE NOTICE 'Ready for staging deployment';
END $$;
