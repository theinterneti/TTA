"""
# Logseq: [[TTA/Components/Dolt/Schema]]
Dolt world state schema definitions — SQL migrations for branching world state.

Issue: #281
"""

from __future__ import annotations

# World state table — the canonical state of the world at any branch
WORLD_STATE_SCHEMA = """
CREATE TABLE IF NOT EXISTS world_state (
    id              VARCHAR(36)     NOT NULL,
    world_id        VARCHAR(36)     NOT NULL,
    player_id       VARCHAR(36)     NOT NULL DEFAULT '',
    session_id      VARCHAR(36)     NOT NULL DEFAULT '',
    location        VARCHAR(255)    NOT NULL DEFAULT '',
    tension_level   FLOAT           NOT NULL DEFAULT 0.0,
    crisis_level    VARCHAR(20)     NOT NULL DEFAULT 'low',
    turn_count      INT             NOT NULL DEFAULT 0,
    world_flags     JSON            NOT NULL DEFAULT (JSON_OBJECT()),
    npc_states      JSON            NOT NULL DEFAULT (JSON_OBJECT()),
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_world_player (world_id, player_id),
    INDEX idx_session (session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""".strip()

# Session snapshots — point-in-time captures at choice points or session boundaries
SESSION_SNAPSHOT_SCHEMA = """
CREATE TABLE IF NOT EXISTS session_snapshots (
    id              VARCHAR(36)     NOT NULL,
    session_id      VARCHAR(36)     NOT NULL,
    player_id       VARCHAR(36)     NOT NULL,
    world_id        VARCHAR(36)     NOT NULL,
    snapshot_type   VARCHAR(20)     NOT NULL DEFAULT 'choice_point',
    state_json      JSON            NOT NULL,
    dolt_commit     VARCHAR(64)     NOT NULL DEFAULT '',
    turn_number     INT             NOT NULL DEFAULT 0,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_session (session_id),
    INDEX idx_player_world (player_id, world_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""".strip()

# Player branches — maps player+session to a Dolt branch name
PLAYER_BRANCH_SCHEMA = """
CREATE TABLE IF NOT EXISTS player_branches (
    id              VARCHAR(36)     NOT NULL,
    player_id       VARCHAR(36)     NOT NULL,
    session_id      VARCHAR(36)     NOT NULL,
    world_id        VARCHAR(36)     NOT NULL,
    branch_name     VARCHAR(255)    NOT NULL,
    base_commit     VARCHAR(64)     NOT NULL DEFAULT '',
    status          VARCHAR(20)     NOT NULL DEFAULT 'active',
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_player_session (player_id, session_id),
    INDEX idx_world (world_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""".strip()

ALL_SCHEMAS = [WORLD_STATE_SCHEMA, SESSION_SNAPSHOT_SCHEMA, PLAYER_BRANCH_SCHEMA]
