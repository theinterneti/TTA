/**
 * Test Data Management Utilities
 *
 * Provides utilities for:
 * - Automated test data generation
 * - Database seeding
 * - Test data cleanup
 * - Database state reset
 */

import { STAGING_CONFIG } from './staging-config';

export interface TestCharacter {
  id?: string;
  name: string;
  appearance: string;
  background: string;
  personality: string[];
  createdAt?: Date;
}

export interface TestWorld {
  id?: string;
  name: string;
  description: string;
  setting: string;
  theme: string;
  createdAt?: Date;
}

export interface TestUser {
  id?: string;
  username: string;
  email: string;
  password: string;
  role: 'user' | 'admin';
  createdAt?: Date;
}

/**
 * Generate random test character
 */
export function generateTestCharacter(seed?: number): TestCharacter {
  const names = [
    'Aria',
    'Zephyr',
    'Luna',
    'Kai',
    'Nova',
    'Sage',
    'River',
    'Storm',
    'Echo',
    'Ember',
  ];
  const appearances = [
    'Tall with silver hair',
    'Short with blue eyes',
    'Athletic build with scars',
    'Elegant with flowing robes',
    'Rugged with weathered face',
  ];
  const backgrounds = [
    'Former warrior seeking redemption',
    'Mysterious traveler from distant lands',
    'Scholar searching for ancient knowledge',
    'Outcast seeking a new home',
    'Adventurer chasing legends',
  ];
  const personalities = [
    ['brave', 'loyal', 'determined'],
    ['cunning', 'witty', 'charming'],
    ['wise', 'patient', 'thoughtful'],
    ['passionate', 'impulsive', 'creative'],
    ['cautious', 'analytical', 'reserved'],
  ];

  const index = seed ? seed % names.length : Math.floor(Math.random() * names.length);

  return {
    name: names[index],
    appearance: appearances[Math.floor(Math.random() * appearances.length)],
    background: backgrounds[Math.floor(Math.random() * backgrounds.length)],
    personality: personalities[Math.floor(Math.random() * personalities.length)],
  };
}

/**
 * Generate random test world
 */
export function generateTestWorld(seed?: number): TestWorld {
  const names = [
    'Eldoria',
    'Mystral',
    'Aethermoor',
    'Shadowvale',
    'Crystalheim',
    'Sunspire',
    'Darkwood',
    'Starfall',
  ];
  const settings = [
    'Medieval fantasy',
    'Cyberpunk future',
    'Post-apocalyptic wasteland',
    'Magical academy',
    'Underwater kingdom',
  ];
  const themes = [
    'Adventure',
    'Mystery',
    'Romance',
    'Horror',
    'Comedy',
    'Drama',
  ];

  const index = seed ? seed % names.length : Math.floor(Math.random() * names.length);

  return {
    name: names[index],
    description: `A mysterious world full of adventure and wonder`,
    setting: settings[Math.floor(Math.random() * settings.length)],
    theme: themes[Math.floor(Math.random() * themes.length)],
  };
}

/**
 * Generate random test user
 */
export function generateTestUser(seed?: number): TestUser {
  const timestamp = Date.now();
  const randomId = Math.random().toString(36).substring(7);

  return {
    username: `testuser_${timestamp}_${randomId}`,
    email: `testuser_${timestamp}_${randomId}@test.local`,
    password: 'TestPassword123!@#',
    role: 'user',
  };
}

/**
 * Seed Redis with test data
 */
export async function seedRedisTestData(
  sessionId: string,
  userData: Record<string, any>
): Promise<void> {
  try {
    const response = await fetch(`http://${STAGING_CONFIG.redis.host}:${STAGING_CONFIG.redis.port}/set/session:${sessionId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      throw new Error(`Failed to seed Redis: ${response.statusText}`);
    }

    console.log(`✅ Seeded Redis with session ${sessionId}`);
  } catch (error) {
    console.error('❌ Failed to seed Redis:', error);
    throw error;
  }
}

/**
 * Seed Neo4j with test data
 */
export async function seedNeo4jTestData(
  character: TestCharacter,
  world: TestWorld
): Promise<void> {
  try {
    const response = await fetch(`http://${STAGING_CONFIG.neo4j.host}:${STAGING_CONFIG.neo4j.port}/seed`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        character,
        world,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to seed Neo4j: ${response.statusText}`);
    }

    console.log(`✅ Seeded Neo4j with character and world`);
  } catch (error) {
    console.error('❌ Failed to seed Neo4j:', error);
    throw error;
  }
}

/**
 * Clear Redis test data
 */
export async function clearRedisTestData(pattern: string = 'session:*'): Promise<void> {
  try {
    const response = await fetch(
      `http://${STAGING_CONFIG.redis.host}:${STAGING_CONFIG.redis.port}/clear?pattern=${pattern}`,
      { method: 'DELETE' }
    );

    if (!response.ok) {
      throw new Error(`Failed to clear Redis: ${response.statusText}`);
    }

    console.log(`✅ Cleared Redis test data`);
  } catch (error) {
    console.error('❌ Failed to clear Redis:', error);
    throw error;
  }
}

/**
 * Clear Neo4j test data
 */
export async function clearNeo4jTestData(): Promise<void> {
  try {
    const response = await fetch(
      `http://${STAGING_CONFIG.neo4j.host}:${STAGING_CONFIG.neo4j.port}/clear`,
      { method: 'DELETE' }
    );

    if (!response.ok) {
      throw new Error(`Failed to clear Neo4j: ${response.statusText}`);
    }

    console.log(`✅ Cleared Neo4j test data`);
  } catch (error) {
    console.error('❌ Failed to clear Neo4j:', error);
    throw error;
  }
}

/**
 * Reset database to known state
 */
export async function resetDatabaseState(): Promise<void> {
  try {
    console.log('🔄 Resetting database state...');

    await clearRedisTestData();
    await clearNeo4jTestData();

    console.log('✅ Database reset complete');
  } catch (error) {
    console.error('❌ Failed to reset database:', error);
    throw error;
  }
}

/**
 * Create test dataset
 */
export async function createTestDataset(
  count: number = 5
): Promise<{ characters: TestCharacter[]; worlds: TestWorld[] }> {
  const characters: TestCharacter[] = [];
  const worlds: TestWorld[] = [];

  for (let i = 0; i < count; i++) {
    characters.push(generateTestCharacter(i));
    worlds.push(generateTestWorld(i));
  }

  return { characters, worlds };
}

/**
 * Populate test database
 */
export async function populateTestDatabase(
  characterCount: number = 5,
  worldCount: number = 5
): Promise<void> {
  try {
    console.log(`🌱 Populating test database with ${characterCount} characters and ${worldCount} worlds...`);

    const dataset = await createTestDataset(Math.max(characterCount, worldCount));

    // Seed characters and worlds
    for (let i = 0; i < characterCount; i++) {
      await seedNeo4jTestData(dataset.characters[i], dataset.worlds[i]);
    }

    console.log('✅ Test database populated');
  } catch (error) {
    console.error('❌ Failed to populate test database:', error);
    throw error;
  }
}

/**
 * Cleanup test data after test run
 */
export async function cleanupTestData(): Promise<void> {
  try {
    console.log('🧹 Cleaning up test data...');

    await resetDatabaseState();

    console.log('✅ Test data cleanup complete');
  } catch (error) {
    console.error('❌ Failed to cleanup test data:', error);
    throw error;
  }
}

/**
 * Get test data statistics
 */
export async function getTestDataStatistics(): Promise<{
  redisKeys: number;
  neo4jNodes: number;
}> {
  try {
    const redisResponse = await fetch(
      `http://${STAGING_CONFIG.redis.host}:${STAGING_CONFIG.redis.port}/stats`
    );
    const neo4jResponse = await fetch(
      `http://${STAGING_CONFIG.neo4j.host}:${STAGING_CONFIG.neo4j.port}/stats`
    );

    const redisStats = await redisResponse.json();
    const neo4jStats = await neo4jResponse.json();

    return {
      redisKeys: redisStats.keys || 0,
      neo4jNodes: neo4jStats.nodes || 0,
    };
  } catch (error) {
    console.error('❌ Failed to get test data statistics:', error);
    return { redisKeys: 0, neo4jNodes: 0 };
  }
}

