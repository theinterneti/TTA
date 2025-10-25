# TTA Single-Player Storytelling Experience - Comprehensive Test Plan

## Overview

This document outlines a comprehensive testing strategy for TTA's single-player storytelling experience, focusing on user enjoyment and game-first presentation while ensuring therapeutic features remain subtle and well-integrated.

## Primary Objectives

1. **Test all single-player features from a fun-focused user perspective**
2. **Ensure storytelling/gaming experience prominence with subtle therapeutic integration**
3. **Compare narrative quality across multiple AI models**
4. **Conduct systematic testing using real anonymized user profiles**

## Model Testing Configuration

### Local AI Models
1. **Qwen2.5-7B-Instruct** (current)
   - Strengths: Fast inference, creative storytelling
   - Focus: Baseline performance measurement

2. **Llama-3.1-8B-Instruct** (recommended addition)
   - Strengths: Narrative coherence, character consistency
   - Focus: Long-term story development

### OpenRouter Models (Free Tier)
1. **Meta-Llama/Llama-3.1-8B-Instruct**
   - Strengths: Balanced narrative and therapeutic integration
   - Focus: Professional-grade storytelling

2. **Mistral-7B-Instruct-v0.3**
   - Strengths: Conversational flow, creativity
   - Focus: Engaging dialogue and character interactions

## Single-Player Features Test Coverage

### Core Features
1. **Character Creation & Management**
   - Character creation flow (appearance, background, therapeutic profile)
   - Character avatar system and progression
   - Character development over time

2. **Interactive Narrative Engine**
   - Story generation and adaptation
   - Choice architecture and meaningful consequences
   - Narrative coherence across sessions
   - Emergent event generation

3. **Session Management**
   - Session creation, continuation, and termination
   - Context preservation between sessions
   - Progress tracking and milestone achievement

4. **Therapeutic Integration (Subtle)**
   - Natural integration without clinical feel
   - Crisis detection and safety mechanisms
   - Growth opportunities and insights

5. **World Management**
   - World compatibility and selection
   - Living world evolution and consistency
   - Setting immersion and believability

6. **Player Dashboard & Progress**
   - Progress visualization and achievements
   - Personalized recommendations
   - Engagement metrics tracking

## Evaluation Framework

### User Experience Metrics (Primary Focus)
- **Fun Factor Score** (1-10): Overall enjoyment and entertainment value
- **Engagement Level**: Time spent, session frequency, return rate
- **Narrative Immersion**: Story believability, character connection
- **Game Flow**: Pacing, choice meaningfulness, progression satisfaction

### Narrative Quality Assessment
- **Creativity & Originality**: Unique story elements, surprising developments
- **Character Consistency**: Voice, personality, development arcs
- **Plot Coherence**: Logical progression, cause-and-effect relationships
- **Dialogue Quality**: Natural conversation, character-appropriate speech
- **World-building Depth**: Rich settings, consistent lore, immersive details

### Therapeutic Balance Evaluation
- **Subtlety Score**: How naturally therapeutic elements are integrated
- **Growth Opportunities**: Meaningful character development moments
- **Safety Handling**: Crisis detection and appropriate responses
- **Progress Facilitation**: Gentle guidance toward therapeutic goals

### Technical Performance
- **Response Time**: Average generation speed per model
- **Consistency**: Session-to-session narrative continuity
- **Error Handling**: Graceful recovery from issues
- **Resource Efficiency**: Memory and computational requirements

## Test Scenarios & User Journeys

### Scenario 1: New Player Onboarding
- Character creation experience
- First session tutorial and guidance
- Initial world selection and setup
- Early choice impact demonstration

### Scenario 2: Multi-Session Story Continuity
- Character and world state persistence
- Long-term consequence tracking
- Relationship development over time
- Narrative arc progression

### Scenario 3: Crisis Scenario Handling
- Therapeutic safety mechanism activation
- Appropriate response and support
- Seamless integration with gameplay
- Recovery and continuation

### Scenario 4: Character Development Journey
- Personal growth through gameplay
- Skill and trait evolution
- Milestone achievement and celebration
- Therapeutic goal progression

### Scenario 5: Choice Consequence Exploration
- Meaningful decision points
- Short and long-term impact tracking
- Alternative path exploration
- Replayability assessment

## Anonymized Test Profiles

### Profile Categories (Privacy-Compliant)
1. **Gaming Enthusiast + Anxiety Management**
   - Tech-savvy, enjoys complex narratives
   - Seeks stress relief through immersive experiences

2. **Creative Writer + Depression Support**
   - Values storytelling quality and character depth
   - Benefits from creative expression opportunities

3. **Professional + Stress Management**
   - Limited time, needs efficient engagement
   - Prefers structured progress and clear goals

4. **Student + Social Anxiety**
   - Relates to coming-of-age themes
   - Benefits from social skill development scenarios

5. **Retiree + Life Transition Support**
   - Appreciates slower pacing and reflection
   - Values wisdom and life experience themes

6. **Parent + Work-Life Balance**
   - Seeks brief but meaningful interactions
   - Benefits from family and relationship themes

## Model Comparison Matrix

### Evaluation Dimensions (Weighted)
- **Narrative Quality** (40%): Creativity, consistency, depth
- **User Engagement** (30%): Fun factor, immersion, retention
- **Therapeutic Integration** (20%): Subtlety, effectiveness, safety
- **Technical Performance** (10%): Speed, reliability, efficiency

### Scoring System
- Each dimension scored 1-10
- Weighted average for overall model score
- Qualitative examples and specific feedback
- Recommendations for optimal use cases

## Implementation Timeline

### Phase 1: Infrastructure Setup (Week 1)
- Model configuration system implementation
- Testing framework development
- Anonymized profile generator creation

### Phase 2: Test Execution (Weeks 2-3)
- Automated scenario testing across all models
- Manual evaluation and scoring
- Data collection and analysis

### Phase 3: Analysis & Reporting (Week 4)
- Comparative analysis generation
- Recommendation formulation
- Final report compilation

## Success Criteria

### Primary Success Indicators
- **Fun Factor**: Average score ≥ 7.5/10 across all models
- **Therapeutic Balance**: Subtle integration without clinical feel
- **Narrative Quality**: Consistent, engaging storytelling
- **User Retention**: High session completion rates

### Model Selection Criteria
- Optimal balance of narrative quality and user engagement
- Appropriate therapeutic integration subtlety
- Technical performance meeting response time requirements
- Cost-effectiveness for production deployment

## Privacy & Compliance

- All test profiles fully anonymized using existing privacy service
- GDPR/HIPAA compliant data handling
- No real user data utilized
- Synthetic profiles based on therapeutic patterns
- Secure data storage and processing

## Deliverables

1. **Comprehensive Test Results Report**
2. **Model Comparison Matrix with Recommendations**
3. **User Experience Analysis and Insights**
4. **Technical Performance Benchmarks**
5. **Implementation Guidelines for Optimal Model Selection**
