// Logseq: [[TTA.dev/Player_experience/Franchise_worlds/Examples/Franchiseworlddemo]]
/**
 * Franchise World System Demo
 *
 * Demonstrates the complete franchise world system with working examples
 * showing integration with TTA systems and therapeutic functionality.
 */

import { FranchiseWorldIntegration } from '../integration/TTAIntegration.js';
import { ArchetypeTemplateManager } from '../characters/ArchetypeTemplates.js';
import { WorldDetails, TherapeuticApproach } from '../types/TTATypes.js';

/**
 * Demo class showcasing franchise world capabilities
 */
export class FranchiseWorldDemo {
  private integration: FranchiseWorldIntegration;

  constructor() {
    this.integration = new FranchiseWorldIntegration();
  }

  /**
   * Demonstrate complete franchise world system
   */
  async runCompleteDemo(): Promise<void> {
    console.log('🎮 TTA Franchise World System Demo');
    console.log('=====================================\n');

    // Demo 1: List all available worlds
    await this.demoWorldListing();

    // Demo 2: Detailed world exploration
    await this.demoWorldExploration();

    // Demo 3: Character archetype system
    await this.demoCharacterArchetypes();

    // Demo 4: Therapeutic integration
    await this.demoTherapeuticIntegration();

    // Demo 5: Session customization
    await this.demoSessionCustomization();

    console.log('\n🎉 Demo completed successfully!');
    console.log('The franchise world system is ready for integration with TTA platform.');
  }

  /**
   * Demo 1: Show all available franchise worlds
   */
  private async demoWorldListing(): Promise<void> {
    console.log('📚 Available Franchise Worlds:');
    console.log('------------------------------');

    const allWorlds = await this.integration.getAllFranchiseWorlds();

    allWorlds.forEach((world, index) => {
      console.log(`${index + 1}. ${world.name} (${world.world_id})`);
      console.log(`   Genre: ${world.world_id.includes('sci') ? 'Sci-Fi' : 'Fantasy'}`);
      console.log(`   Description: ${world.description}`);
      console.log(`   Therapeutic Themes: ${world.therapeutic_themes.join(', ')}`);
      console.log(`   Difficulty: ${world.difficulty_level}`);
      console.log(`   Estimated Duration: ${world.estimated_duration.hours} hours`);
      console.log('');
    });

    // Show genre-specific filtering
    console.log('🏰 Fantasy Worlds:');
    const fantasyWorlds = await this.integration.getFranchiseWorldsByGenre('fantasy');
    fantasyWorlds.forEach(world => console.log(`   - ${world.name}`));

    console.log('\n🚀 Sci-Fi Worlds:');
    const scifiWorlds = await this.integration.getFranchiseWorldsByGenre('sci-fi');
    scifiWorlds.forEach(world => console.log(`   - ${world.name}`));
    console.log('');
  }

  /**
   * Demo 2: Detailed exploration of a specific world
   */
  private async demoWorldExploration(): Promise<void> {
    console.log('🏰 Detailed World Exploration: Eldermere Realms');
    console.log('-----------------------------------------------');

    const world = await this.integration.getFranchiseWorld('eldermere_realms');
    if (!world) {
      console.log('❌ World not found');
      return;
    }

    console.log(`📖 ${world.name}`);
    console.log(`${world.long_description}\n`);

    console.log('🌍 Setting:');
    console.log(`${world.setting_description}\n`);

    console.log('👥 Key Characters:');
    world.key_characters.forEach(char => {
      console.log(`   - ${char.name} (${char.role}): ${char.description}`);
    });
    console.log('');

    console.log('📚 Main Storylines:');
    world.main_storylines.forEach((storyline, index) => {
      console.log(`   ${index + 1}. ${storyline}`);
    });
    console.log('');

    console.log('🧠 Therapeutic Techniques:');
    world.therapeutic_techniques_used.forEach(technique => {
      console.log(`   - ${technique.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}`);
    });
    console.log('');

    console.log('⚠️  Content Warnings:');
    world.content_warnings.forEach(warning => {
      console.log(`   - ${warning}`);
    });
    console.log('');
  }

  /**
   * Demo 3: Character archetype system
   */
  private async demoCharacterArchetypes(): Promise<void> {
    console.log('👥 Character Archetype System');
    console.log('-----------------------------');

    const archetypes = ArchetypeTemplateManager.getAllArchetypes();

    console.log(`📊 Available Archetypes: ${archetypes.length}`);
    console.log('');

    archetypes.forEach(archetype => {
      console.log(`🎭 ${archetype.name} (${archetype.archetypeId})`);
      console.log(`   Role: ${archetype.role}`);
      console.log(`   Therapeutic Function: ${archetype.therapeuticFunction}`);
      console.log(`   Key Traits: ${archetype.personality.traits.join(', ')}`);
      console.log(`   Growth Arc: ${archetype.personality.growth_arc}`);
      console.log('');
    });

    // Demo archetype adaptation
    console.log('🔄 Archetype Adaptation Demo:');
    const wiseMentor = ArchetypeTemplateManager.getArchetype('wise_mentor');
    if (wiseMentor) {
      const fantasyVersion = ArchetypeTemplateManager.adaptArchetypeForWorld(
        wiseMentor,
        'fantasy',
        'Eldermere Realms'
      );
      const scifiVersion = ArchetypeTemplateManager.adaptArchetypeForWorld(
        wiseMentor,
        'sci-fi',
        'Stellar Confederation'
      );

      console.log(`   Fantasy Version: ${fantasyVersion.name}`);
      console.log(`   Sci-Fi Version: ${scifiVersion.name}`);
    }
    console.log('');
  }

  /**
   * Demo 4: Therapeutic integration capabilities
   */
  private async demoTherapeuticIntegration(): Promise<void> {
    console.log('🧠 Therapeutic Integration Demo');
    console.log('-------------------------------');

    const world = await this.integration.getFranchiseWorld('arcanum_academy');
    if (!world) {
      console.log('❌ World not found');
      return;
    }

    console.log(`🎓 Analyzing: ${world.name}`);
    console.log('');

    console.log('🎯 Therapeutic Approaches:');
    world.therapeutic_approaches.forEach(approach => {
      console.log(`   - ${approach.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}`);
    });
    console.log('');

    console.log('📈 Therapeutic Readiness Score:');
    console.log(`   ${(world.recommended_therapeutic_readiness * 100).toFixed(0)}% - ${this.getReadinessDescription(world.recommended_therapeutic_readiness)}`);
    console.log('');

    console.log('🎲 Prerequisites:');
    if (world.prerequisites.length === 0) {
      console.log('   None - suitable for all players');
    } else {
      world.prerequisites.forEach(prereq => {
        console.log(`   - ${prereq.type}: ${prereq.description}`);
      });
    }
    console.log('');

    // Demo therapeutic technique matching
    console.log('🔍 Therapeutic Technique Analysis:');
    const cbtTechniques = world.therapeutic_techniques_used.filter(t =>
      t.includes('cognitive') || t.includes('restructuring') || t.includes('reframing')
    );
    const mindfulnessTechniques = world.therapeutic_techniques_used.filter(t =>
      t.includes('mindfulness') || t.includes('awareness') || t.includes('meditation')
    );

    console.log(`   CBT Techniques: ${cbtTechniques.length}`);
    console.log(`   Mindfulness Techniques: ${mindfulnessTechniques.length}`);
    console.log('');
  }

  /**
   * Demo 5: Session customization
   */
  private async demoSessionCustomization(): Promise<void> {
    console.log('⚙️  Session Customization Demo');
    console.log('-----------------------------');

    // Simulate different player preferences
    const playerProfiles = [
      {
        name: 'Anxious Student',
        preferences: {
          therapeutic_intensity: 0.3,
          narrative_pace: 'slow',
          interaction_frequency: 'minimal',
          session_length: 30,
          avoid_topics: ['academic_pressure']
        }
      },
      {
        name: 'Social Learner',
        preferences: {
          therapeutic_intensity: 0.7,
          narrative_pace: 'medium',
          interaction_frequency: 'frequent',
          session_length: 60,
          focus_areas: ['friendship_building', 'social_skills']
        }
      },
      {
        name: 'Adventure Seeker',
        preferences: {
          therapeutic_intensity: 0.8,
          narrative_pace: 'fast',
          interaction_frequency: 'balanced',
          session_length: 90,
          focus_areas: ['courage_building', 'leadership']
        }
      }
    ];

    for (const profile of playerProfiles) {
      console.log(`👤 ${profile.name}:`);

      // Get world configuration
      const world = await this.integration.getFranchiseWorld('eldermere_realms');
      if (!world) continue;

      // This would normally create customized parameters
      console.log(`   Recommended Session Length: ${profile.preferences.session_length} minutes`);
      console.log(`   Therapeutic Intensity: ${(profile.preferences.therapeutic_intensity * 100).toFixed(0)}%`);
      console.log(`   Narrative Pace: ${profile.preferences.narrative_pace}`);
      console.log(`   Interaction Style: ${profile.preferences.interaction_frequency}`);

      if (profile.preferences.focus_areas) {
        console.log(`   Focus Areas: ${profile.preferences.focus_areas.join(', ')}`);
      }

      if (profile.preferences.avoid_topics) {
        console.log(`   Avoiding: ${profile.preferences.avoid_topics.join(', ')}`);
      }

      console.log('');
    }
  }

  /**
   * Helper method to describe therapeutic readiness
   */
  private getReadinessDescription(score: number): string {
    if (score < 0.3) return 'Low therapeutic content - suitable for casual play';
    if (score < 0.6) return 'Moderate therapeutic content - some self-reflection required';
    if (score < 0.8) return 'High therapeutic content - active engagement with personal growth';
    return 'Intensive therapeutic content - deep self-exploration and commitment required';
  }

  /**
   * Quick validation test
   */
  async runValidationTest(): Promise<boolean> {
    console.log('🔍 Running System Validation...');

    try {
      // Test world loading
      const worlds = await this.integration.getAllFranchiseWorlds();
      if (worlds.length === 0) {
        console.log('❌ No worlds loaded');
        return false;
      }

      // Test archetype system
      const archetypes = ArchetypeTemplateManager.getAllArchetypes();
      if (archetypes.length === 0) {
        console.log('❌ No archetypes loaded');
        return false;
      }

      // Test world-specific loading
      const testWorld = await this.integration.getFranchiseWorld('eldermere_realms');
      if (!testWorld) {
        console.log('❌ Cannot load specific world');
        return false;
      }

      // Test simulation validation
      const isValid = await this.integration.validateWorldForSimulation('eldermere_realms');
      if (!isValid) {
        console.log('❌ World not suitable for simulation');
        return false;
      }

      console.log('✅ All validation tests passed');
      return true;
    } catch (error) {
      console.log(`❌ Validation failed: ${error}`);
      return false;
    }
  }
}

/**
 * Main demo execution
 */
export async function runFranchiseWorldDemo(): Promise<void> {
  const demo = new FranchiseWorldDemo();

  // Run validation first
  const isValid = await demo.runValidationTest();
  if (!isValid) {
    console.log('❌ System validation failed. Please check configuration.');
    return;
  }

  // Run complete demo
  await demo.runCompleteDemo();
}

// Export for direct execution
if (require.main === module) {
  runFranchiseWorldDemo().catch(console.error);
}
