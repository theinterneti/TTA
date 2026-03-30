// Logseq: [[TTA.dev/Tests/E2e-staging/Helpers/Database-helpers]]
/**
 * Database Helper Utilities for E2E Tests
 *
 * Provides utilities for verifying data persistence in Redis and Neo4j
 * during E2E testing. Helps validate that game state is properly stored.
 */

import { STAGING_CONFIG } from './staging-config';

/**
 * Redis connection helper
 */
export class RedisHelper {
  private host: string;
  private port: number;

  constructor(host?: string, port?: number) {
    this.host = host || STAGING_CONFIG.databases.redis.host;
    this.port = port || STAGING_CONFIG.databases.redis.port;
  }

  /**
   * Check if Redis is accessible
   */
  async isAccessible(): Promise<boolean> {
    try {
      const response = await fetch(`http://${this.host}:${this.port}/ping`, {
        method: 'GET',
        timeout: 5000,
      });
      return response.ok;
    } catch {
      return false;
    }
  }

  /**
   * Get session data from Redis
   */
  async getSessionData(sessionId: string): Promise<any> {
    try {
      const response = await fetch(
        `http://${this.host}:${this.port}/get/session:${sessionId}`,
        { timeout: 5000 }
      );

      if (!response.ok) {
        return null;
      }

      return await response.json();
    } catch {
      return null;
    }
  }

  /**
   * Verify session exists
   */
  async sessionExists(sessionId: string): Promise<boolean> {
    const data = await this.getSessionData(sessionId);
    return data !== null;
  }

  /**
   * Get cache data
   */
  async getCacheData(key: string): Promise<any> {
    try {
      const response = await fetch(
        `http://${this.host}:${this.port}/get/${key}`,
        { timeout: 5000 }
      );

      if (!response.ok) {
        return null;
      }

      return await response.json();
    } catch {
      return null;
    }
  }

  /**
   * Clear all test data from Redis
   */
  async clearTestData(): Promise<void> {
    try {
      await fetch(`http://${this.host}:${this.port}/flushdb`, {
        method: 'POST',
        timeout: 5000,
      });
    } catch {
      console.warn('Failed to clear Redis test data');
    }
  }
}

/**
 * Neo4j connection helper
 */
export class Neo4jHelper {
  private uri: string;
  private username: string = 'neo4j';
  private password: string = 'password';

  constructor(uri?: string) {
    this.uri = uri || STAGING_CONFIG.databases.neo4j.uri;
  }

  /**
   * Check if Neo4j is accessible
   */
  async isAccessible(): Promise<boolean> {
    try {
      const response = await fetch(`${this.uri.replace('bolt://', 'http://')}/db/neo4j/exec`, {
        method: 'POST',
        headers: {
          'Authorization': `Basic ${Buffer.from(`${this.username}:${this.password}`).toString('base64')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ statements: [{ statement: 'RETURN 1' }] }),
        timeout: 5000,
      });
      return response.ok;
    } catch {
      return false;
    }
  }

  /**
   * Query Neo4j for character data
   */
  async getCharacterData(characterId: string): Promise<any> {
    try {
      const response = await fetch(`${this.uri.replace('bolt://', 'http://')}/db/neo4j/exec`, {
        method: 'POST',
        headers: {
          'Authorization': `Basic ${Buffer.from(`${this.username}:${this.password}`).toString('base64')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          statements: [
            {
              statement: 'MATCH (c:Character {id: $id}) RETURN c',
              parameters: { id: characterId },
            },
          ],
        }),
        timeout: 5000,
      });

      if (!response.ok) {
        return null;
      }

      const data = await response.json();
      return data.results?.[0]?.data?.[0]?.row?.[0];
    } catch {
      return null;
    }
  }

  /**
   * Query Neo4j for world data
   */
  async getWorldData(worldId: string): Promise<any> {
    try {
      const response = await fetch(`${this.uri.replace('bolt://', 'http://')}/db/neo4j/exec`, {
        method: 'POST',
        headers: {
          'Authorization': `Basic ${Buffer.from(`${this.username}:${this.password}`).toString('base64')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          statements: [
            {
              statement: 'MATCH (w:World {id: $id}) RETURN w',
              parameters: { id: worldId },
            },
          ],
        }),
        timeout: 5000,
      });

      if (!response.ok) {
        return null;
      }

      const data = await response.json();
      return data.results?.[0]?.data?.[0]?.row?.[0];
    } catch {
      return null;
    }
  }

  /**
   * Clear test data from Neo4j
   */
  async clearTestData(): Promise<void> {
    try {
      await fetch(`${this.uri.replace('bolt://', 'http://')}/db/neo4j/exec`, {
        method: 'POST',
        headers: {
          'Authorization': `Basic ${Buffer.from(`${this.username}:${this.password}`).toString('base64')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          statements: [
            {
              statement: 'MATCH (n:TestData) DETACH DELETE n',
            },
          ],
        }),
        timeout: 5000,
      });
    } catch {
      console.warn('Failed to clear Neo4j test data');
    }
  }
}

/**
 * Verify data persistence across databases
 */
export async function verifyDataPersistence(
  characterId: string,
  worldId: string
): Promise<{ redis: boolean; neo4j: boolean }> {
  const redis = new RedisHelper();
  const neo4j = new Neo4jHelper();

  const [redisData, neo4jData] = await Promise.all([
    redis.getSessionData(characterId),
    neo4j.getCharacterData(characterId),
  ]);

  return {
    redis: redisData !== null,
    neo4j: neo4jData !== null,
  };
}

/**
 * Wait for data to be persisted
 */
export async function waitForDataPersistence(
  characterId: string,
  timeout: number = 10000
): Promise<boolean> {
  const startTime = Date.now();
  const redis = new RedisHelper();

  while (Date.now() - startTime < timeout) {
    const exists = await redis.sessionExists(characterId);
    if (exists) {
      return true;
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }

  return false;
}
