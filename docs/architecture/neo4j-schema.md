# TTA Neo4j Schema Design

> **Status:** Active — Milestone 1 (World Seed)
> **Issue:** [#272](https://github.com/theinterneti/TTA/issues/272)
> **Code:** `src/common/neo4j_schema.py`

---

## Overview

TTA uses Neo4j as its live world graph — storing the state of every location, NPC,
faction, event, and rule that grounds LLM responses in real world facts.

The WorldContextBuilder (#275) traverses this graph 2–3 hops from the player's
current scene to assemble a `WorldContext` object passed to every NGA prompt.

---

## Node Labels

### `Location`

A physical place in the game world (room, region, landmark).

| Property | Type | Required | Notes |
|---|---|---|---|
| `id` | string | ✓ | UUID, unique constraint |
| `name` | string | ✓ | Display name |
| `description` | string | ✓ | Narrative description |
| `zone_id` | string | | FK → Zone.id |
| `location_type` | string | | `room`, `outdoor`, `landmark`, `dungeon` |
| `is_accessible` | boolean | | Default `true` |
| `properties` | map | | Freeform world-specific properties |
| `created_at` | datetime | ✓ | |
| `updated_at` | datetime | ✓ | |

**Constraints:** `location_id` UNIQUE  
**Indexes:** `(name)`, `(zone_id)`, `(location_type)`

---

### `NPC`

A non-player character living in the world.

| Property | Type | Required | Notes |
|---|---|---|---|
| `id` | string | ✓ | UUID, unique constraint |
| `name` | string | ✓ | |
| `role` | string | ✓ | `merchant`, `guard`, `quest_giver`, `ally`, `antagonist` |
| `faction_id` | string | | FK → Faction.id |
| `current_location_id` | string | | FK → Location.id |
| `disposition` | string | | `friendly`, `neutral`, `hostile` |
| `dialogue_style` | string | | LLM prompt hint |
| `health_state` | string | | `alive`, `injured`, `dead` |
| `is_active` | boolean | ✓ | Whether NPC participates in scenes |
| `properties` | map | | Freeform world-specific properties |
| `created_at` | datetime | ✓ | |
| `updated_at` | datetime | ✓ | |

**Constraints:** `npc_id` UNIQUE  
**Indexes:** `(name)`, `(faction_id)`, `(current_location_id)`, `(is_active)`

---

### `WorldRule`

An immutable or slowly-changing lore rule that governs what is possible.  
Examples: "magic is forbidden in the capital", "iron doors cannot be broken".

| Property | Type | Required | Notes |
|---|---|---|---|
| `id` | string | ✓ | UUID, unique constraint |
| `name` | string | ✓ | Short identifier |
| `description` | string | ✓ | Full rule text injected into prompts |
| `scope` | string | ✓ | `global`, `zone`, `location` |
| `scope_id` | string | | FK → Zone.id or Location.id if scoped |
| `category` | string | | `magic`, `physics`, `social`, `narrative` |
| `priority` | integer | | Higher = applied first in conflict |
| `is_active` | boolean | ✓ | |
| `created_at` | datetime | ✓ | |

**Constraints:** `world_rule_id` UNIQUE  
**Indexes:** `(scope)`, `(scope_id)`, `(is_active)`, `(category)`

---

### `WorldEvent`

A time-bounded occurrence that changes world state.  
Examples: "festival in progress", "bandit raid", "plague spreading".

| Property | Type | Required | Notes |
|---|---|---|---|
| `id` | string | ✓ | UUID, unique constraint |
| `name` | string | ✓ | |
| `description` | string | ✓ | Narrative description |
| `event_type` | string | ✓ | `combat`, `social`, `environmental`, `narrative` |
| `location_id` | string | | Where it occurs |
| `zone_id` | string | | If zone-wide |
| `started_at` | datetime | ✓ | |
| `expires_at` | datetime | | Null = permanent until resolved |
| `is_active` | boolean | ✓ | |
| `severity` | string | | `minor`, `moderate`, `major`, `catastrophic` |
| `properties` | map | | Additional event metadata |

**Constraints:** `world_event_id` UNIQUE  
**Indexes:** `(is_active)`, `(location_id)`, `(zone_id)`, `(event_type)`, `(expires_at)`

---

### `PlayerCharacter`

The player's in-game avatar.

| Property | Type | Required | Notes |
|---|---|---|---|
| `id` | string | ✓ | UUID, unique constraint |
| `player_id` | string | ✓ | FK → external player identity |
| `name` | string | ✓ | Character name |
| `current_location_id` | string | ✓ | FK → Location.id |
| `faction_id` | string | | Current faction affiliation |
| `health_state` | string | ✓ | `healthy`, `injured`, `critical` |
| `emotional_state` | string | | Therapeutic context |
| `inventory` | list[string] | | Item IDs |
| `skills` | list[string] | | Skill IDs |
| `created_at` | datetime | ✓ | |
| `updated_at` | datetime | ✓ | |

**Constraints:** `player_character_id` UNIQUE  
**Indexes:** `(player_id)`, `(current_location_id)`

---

### `Faction`

A political, social, or narrative group that NPCs and the player can belong to.

| Property | Type | Required | Notes |
|---|---|---|---|
| `id` | string | ✓ | UUID, unique constraint |
| `name` | string | ✓ | |
| `description` | string | ✓ | |
| `alignment` | string | | `lawful`, `neutral`, `chaotic` |
| `is_active` | boolean | ✓ | |
| `home_location_id` | string | | Primary base |
| `created_at` | datetime | ✓ | |

**Constraints:** `faction_id` UNIQUE  
**Indexes:** `(name)`, `(is_active)`

---

### `Zone`

A logical grouping of locations (district, dungeon, wilderness area).

| Property | Type | Required | Notes |
|---|---|---|---|
| `id` | string | ✓ | UUID, unique constraint |
| `name` | string | ✓ | |
| `description` | string | ✓ | |
| `zone_type` | string | | `city`, `wilderness`, `dungeon`, `overworld` |
| `danger_level` | integer | | 1–10 |
| `is_active` | boolean | ✓ | |
| `created_at` | datetime | ✓ | |

**Constraints:** `zone_id` UNIQUE  
**Indexes:** `(name)`, `(zone_type)`

---

## Relationship Types

| Relationship | From | To | Direction | Cardinality | Properties |
|---|---|---|---|---|---|
| `CONNECTED_TO` | Location | Location | undirected | M:M | `travel_time`, `requires_key` (bool) |
| `LIVES_IN` | NPC | Location | → | M:1 | `since` (datetime), `is_primary` (bool) |
| `HAS_RELATIONSHIP` | NPC | NPC | → | M:M | `rel_type` (string), `strength` (float 0–1) |
| `HAD_EVENT` | Location | WorldEvent | → | M:M | — |
| `INVOLVED` | NPC | WorldEvent | → | M:M | `role` (string) |
| `IN_ZONE` | Location | Zone | → | M:1 | — |
| `GOVERNED_BY` | Location | WorldRule | → | M:M | `since` (datetime) |
| `MEMBER_OF` | NPC | Faction | → | M:1 | `rank` (string), `since` (datetime) |
| `MEMBER_OF` | PlayerCharacter | Faction | → | M:1 | `rank`, `since` |
| `CURRENTLY_AT` | PlayerCharacter | Location | → | 1:1 | `since` (datetime) |
| `AFFECTED_BY` | Location | WorldEvent | → | M:M | — |
| `AFFECTS_ZONE` | WorldEvent | Zone | → | M:M | — |
| `APPLIES_TO_ZONE` | WorldRule | Zone | → | M:M | — |
| `APPLIES_TO_LOCATION` | WorldRule | Location | → | M:M | — |

---

## WorldContextBuilder Traversal Pattern

For a player at location `L`, the traversal assembles context in three tiers:

```
Tier 1 (hop 0): L properties + WorldRules GOVERNED_BY L
Tier 2 (hop 1): NPCs LIVES_IN L, WorldEvents HAD_EVENT L, Locations CONNECTED_TO L
Tier 3 (hop 2): NPCs MEMBER_OF Faction, WorldRules APPLIES_TO_ZONE (Zone IN_ZONE L)
```

Maximum depth: **3 hops** (configurable). Target query time: **< 50ms p99**.

---

## Existing Gameplay Loop Nodes (compatibility)

The `GameplayLoopSchema` in `src/components/gameplay_loop/database/schema.py` defines
additional nodes (`GameplaySession`, `NarrativeScene`, `PlayerChoice`, etc.) that
operate in the same database. The world-graph nodes above are separate labels with
no overlapping constraint names.

---

## Cypher Constraint & Index Reference

All constraints and indexes are managed by `src/common/neo4j_schema.py`.
Run at startup via `await WorldGraphSchema.initialize(driver)`.

See also: [WorldContextBuilder spec](../research/) | [#261 WorldContextBuilder epic](https://github.com/theinterneti/TTA/issues/261)
