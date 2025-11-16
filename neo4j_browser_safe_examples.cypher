// Neo4j Browser Safe Character Creation Examples
// These examples are guaranteed to work without crashes

// ============================================================
// SAFE EXAMPLE 1: Basic Character with String Array Traits
// ============================================================
CREATE (c:Character {
    id: 'char_' + randomUUID(),
    name: 'Brave Knight',
    description: 'A valiant defender of the realm',
    personality_traits: ['brave', 'honorable', 'protective', 'loyal'],
    stat_strength: 16,
    stat_wisdom: 12,
    stat_charisma: 14,
    stat_constitution: 15,
    level: 5,
    experience: 1250,
    health: 100,
    mana: 50,
    created_at: datetime()
})
RETURN c;

// ============================================================
// SAFE EXAMPLE 2: Character with Location Relationship
// ============================================================
CREATE (c:Character {
    id: 'char_' + randomUUID(),
    name: 'Elven Ranger',
    description: 'A skilled tracker and archer',
    personality_traits: ['observant', 'patient', 'nature-loving', 'independent'],
    stat_dexterity: 18,
    stat_wisdom: 15,
    stat_constitution: 12,
    stat_perception: 16,
    level: 3,
    experience: 750,
    created_at: datetime()
}),
(l:Location {
    id: 'loc_' + randomUUID(),
    name: 'Whispering Woods',
    description: 'An ancient forest filled with secrets',
    terrain_type: 'forest',
    danger_level: 3,
    created_at: datetime()
})
CREATE (c)-[:LOCATED_AT]->(l)
RETURN c, l;

// ============================================================
// SAFE EXAMPLE 3: Character with Equipment (Using Relationships)
// ============================================================
CREATE (c:Character {
    id: 'char_' + randomUUID(),
    name: 'Seasoned Warrior',
    description: 'A battle-hardened fighter',
    personality_traits: ['determined', 'tactical', 'protective'],
    stat_strength: 17,
    stat_constitution: 16,
    stat_dexterity: 13,
    level: 8,
    experience: 3200,
    created_at: datetime()
}),
(w:Equipment {
    id: 'eq_' + randomUUID(),
    name: 'Enchanted Longsword',
    type: 'weapon',
    damage: 12,
    enchantment: 'fire',
    rarity: 'rare',
    created_at: datetime()
}),
(a:Equipment {
    id: 'eq_' + randomUUID(),
    name: 'Plate Armor',
    type: 'armor',
    defense: 8,
    weight: 45,
    rarity: 'common',
    created_at: datetime()
}),
(s:Equipment {
    id: 'eq_' + randomUUID(),
    name: 'Tower Shield',
    type: 'shield',
    defense: 5,
    block_chance: 25,
    rarity: 'uncommon',
    created_at: datetime()
})
CREATE (c)-[:EQUIPPED]->(w)
CREATE (c)-[:EQUIPPED]->(a)
CREATE (c)-[:EQUIPPED]->(s)
RETURN c, w, a, s;

// ============================================================
// SAFE EXAMPLE 4: Character with Guild Membership
// ============================================================
CREATE (c:Character {
    id: 'char_' + randomUUID(),
    name: 'Arcane Scholar',
    description: 'A master of magical arts',
    personality_traits: ['intelligent', 'curious', 'methodical', 'ambitious'],
    stat_intelligence: 19,
    stat_wisdom: 16,
    stat_constitution: 10,
    level: 12,
    experience: 8500,
    spell_slots: 15,
    mana: 200,
    created_at: datetime()
}),
(g:Guild {
    id: 'guild_' + randomUUID(),
    name: 'Circle of Arcane Knowledge',
    description: 'Masters of magical theory and practice',
    guild_type: 'academic',
    member_count: 47,
    founded: date('2020-03-15'),
    created_at: datetime()
})
CREATE (c)-[:MEMBER_OF {rank: 'Senior Scholar', joined_date: date()}]->(g)
RETURN c, g;

// ============================================================
// SAFE EXAMPLE 5: Multiple Characters with Relationships
// ============================================================
CREATE (c1:Character {
    id: 'char_' + randomUUID(),
    name: 'Captain Sarah',
    description: 'Leader of the city guard',
    personality_traits: ['leadership', 'just', 'protective', 'disciplined'],
    stat_strength: 15,
    stat_charisma: 17,
    stat_wisdom: 14,
    level: 10,
    rank: 'Captain',
    created_at: datetime()
}),
(c2:Character {
    id: 'char_' + randomUUID(),
    name: 'Guard Tom',
    description: 'Loyal city guard',
    personality_traits: ['loyal', 'dutiful', 'brave'],
    stat_strength: 14,
    stat_constitution: 15,
    level: 4,
    rank: 'Guard',
    created_at: datetime()
}),
(c3:Character {
    id: 'char_' + randomUUID(),
    name: 'Scout Elena',
    description: 'Swift messenger and scout',
    personality_traits: ['quick', 'observant', 'reliable'],
    stat_dexterity: 17,
    stat_perception: 16,
    level: 6,
    rank: 'Scout',
    created_at: datetime()
})
CREATE (c1)-[:COMMANDS]->(c2)
CREATE (c1)-[:COMMANDS]->(c3)
CREATE (c2)-[:ALLIES_WITH]->(c3)
RETURN c1, c2, c3;

// ============================================================
// QUERY EXAMPLES: Retrieve Character Information
// ============================================================

// Query 1: List all characters with their traits
MATCH (c:Character)
RETURN c.name as name,
       c.description as description,
       c.personality_traits as traits,
       c.level as level,
       c.experience as experience
ORDER BY c.name;

// Query 2: Characters with their locations
MATCH (c:Character)
OPTIONAL MATCH (c)-[:LOCATED_AT]->(l:Location)
RETURN c.name as character_name,
       c.personality_traits as traits,
       l.name as location,
       l.terrain_type as terrain
ORDER BY c.name;

// Query 3: Characters with their equipment
MATCH (c:Character)
OPTIONAL MATCH (c)-[:EQUIPPED]->(e:Equipment)
RETURN c.name as character_name,
       collect(e.name) as equipment,
       collect(e.type) as equipment_types
ORDER BY c.name;

// Query 4: Guild members
MATCH (c:Character)-[r:MEMBER_OF]->(g:Guild)
RETURN c.name as member_name,
       g.name as guild_name,
       r.rank as rank,
       r.joined_date as joined
ORDER BY g.name, r.rank;

// Query 5: Character relationships
MATCH (c1:Character)-[r]->(c2:Character)
RETURN c1.name as from_character,
       type(r) as relationship_type,
       c2.name as to_character
ORDER BY c1.name;

// ============================================================
// UPDATE EXAMPLES: Safe Character Modifications
// ============================================================

// Update 1: Level up a character
MATCH (c:Character {name: 'Brave Knight'})
SET c.level = c.level + 1,
    c.experience = c.experience + 500,
    c.stat_strength = c.stat_strength + 1
RETURN c.name, c.level, c.experience;

// Update 2: Add new personality trait
MATCH (c:Character {name: 'Elven Ranger'})
SET c.personality_traits = c.personality_traits + ['experienced']
RETURN c.name, c.personality_traits;

// Update 3: Change character location
MATCH (c:Character {name: 'Seasoned Warrior'})-[r:LOCATED_AT]->(old:Location)
DELETE r
WITH c
MATCH (new:Location {name: 'Whispering Woods'})
CREATE (c)-[:LOCATED_AT]->(new)
RETURN c.name, new.name as new_location;

// ============================================================
// CLEANUP EXAMPLES: Remove Test Data
// ============================================================

// Remove all test characters (use with caution!)
// MATCH (c:Character) WHERE c.name CONTAINS 'Test' DELETE c;

// Remove specific character by ID
// MATCH (c:Character {id: 'specific_character_id'}) DETACH DELETE c;

// Remove all relationships of a specific type
// MATCH ()-[r:EQUIPPED]->() DELETE r;
