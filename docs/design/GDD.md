# TTA — Game Design Document
## Therapeutic Text Adventure

**Version:** 1.0
**Status:** Living Document
**Last Updated:** 2026-02-19
**Audience:** Developers, designers, AI agents working on TTA

---

## Table of Contents

1. [Vision & Overview](#1-vision--overview)
2. [Core Philosophy](#2-core-philosophy)
3. [Game World](#3-game-world)
4. [Player Experience](#4-player-experience)
5. [Core Gameplay Loop](#5-core-gameplay-loop)
6. [AI Agent Architecture](#6-ai-agent-architecture)
7. [Knowledge Graph](#7-knowledge-graph)
8. [Therapeutic Framework](#8-therapeutic-framework)
9. [Entertainment-First Design](#9-entertainment-first-design)
10. [Technical Architecture](#10-technical-architecture)
11. [User Types & Journeys](#11-user-types--journeys)
12. [Development Roadmap](#12-development-roadmap)
13. [Ethical Framework](#13-ethical-framework)
14. [Source Documents](#14-source-documents)

---

## 1. Vision & Overview

TTA (Therapeutic Text Adventure) is a text-based adventure game set in an infinite multiverse. It merges immersive interactive narrative with subtly integrated therapeutic benefit, targeting individuals who seek personal growth or may not have access to — or may be resistant to — traditional mental health services.

**The core promise:** An engaging adventure game that happens to be good for you. Not therapy dressed up as a game, but a game that quietly delivers therapeutic value.

### 1.1 Project Goals

- Provide a unique, personalized, potentially healing experience through text-based adventure
- Use player choices, AI-driven narratives, and a knowledge graph to create a dynamic, responsive world
- Offer a safe space for players to explore their inner worlds and confront personal challenges
- Create a "living, breathing world" that responds to player choices
- Reach individuals who wouldn't seek traditional mental health support

### 1.2 Target Audience

Primary: Individuals seeking personalized, engaging interactive experiences — specifically those who may not access or may resist traditional mental health services.

Secondary: Players who simply enjoy deep, AI-driven narrative games.

See [user-journey-matrix.md](user-journey-matrix.md) for detailed breakdown of 6 user categories.

---

## 2. Core Philosophy

### 2.1 Design Principles

| Principle | Description |
|-----------|-------------|
| **Player-Centricity** | The player's experience is the top priority |
| **Entertainment-First** | Fun and immersion lead; therapy follows invisibly |
| **Concept-Driven Design** | The game world is built on universal human concepts |
| **AI Collaboration** | AI agents are integral partners in dynamic narrative |
| **Modular Design** | Components can be developed and iterated independently |
| **Interconnectedness** | Player actions have meaningful, far-reaching consequences |
| **Healing Potential** | Therapeutic concepts subtly support self-discovery |
| **Emergent Gameplay** | Unexpected events arise from system interactions |
| **Ethical Grounding** | Player safety, well-being, responsible AI are non-negotiable |

### 2.2 The Entertainment-First Imperative

The interface, language, and presentation are entertainment-first. Clinical terminology is translated to adventure language:

| Clinical | Adventure |
|----------|-----------|
| Therapeutic goals | Personal objectives |
| Session | Adventure |
| Patient | Player / Adventurer |
| Therapeutic intensity | Experience depth |
| Progress tracking | Achievement progress |
| Crisis support | Emergency help |

Players in default mode never see clinical language. Healthcare providers can toggle to clinical mode. See [entertainment-first-design.md](entertainment-first-design.md) for the full translation system.

### 2.3 Narrative Therapy as Foundation

TTA's therapeutic approach is rooted in **narrative therapy**: people make meaning of their lives through the stories they tell. Problems are not the person — they are separate entities that can be explored and challenged.

The game acts as an investigator or co-explorer of the player's experience, never as an instructor. Players are authors of their own story.

---

## 3. Game World

### 3.1 The Multiverse

The core setting is an **infinite multiverse** — countless parallel universes, each with unique physical laws, histories, cultures, and inhabitants. This provides a nearly limitless playground for storytelling and diverse experiences.

### 3.2 The Nexus

The Nexus is a central hub connecting all universes. It exists outside individual universe boundaries and serves as the point of access and transition between them.

- Each universe has a unique manifestation within the Nexus
- Connections can be one-way, two-way, stable, or unstable
- The Nexus Manager Agent (NMA) manages all connections
- Players typically encounter the Nexus during the Genesis sequence

### 3.3 Established Universes

| Universe | Description |
|----------|-------------|
| **Aethelgard** | High fantasy + emerging technology; magic is tangible; multiple factions |
| **Musketeer Earth** | Fictionalized 17th century; chivalry, political intrigue, swashbuckling |
| **Steampunk Earth** | Victorian aesthetics + steam-powered technology; airships, class conflict |
| **Post-Apocalyptic Earth** | Ravaged future; scarce resources; survival focus |
| **Our Universe** | Real-world representation; enhanced via web resources |
| **Alternate Earths** | Player-specific worlds shaped by individual choices and history |

### 3.4 Universe Connections

- **Bleedthrough**: Elements from one universe leak into another
- **Resonance**: Events or choices in one universe affect others
- Players may encounter connections as unstable portals, strange phenomena, or synchronicities

---

## 4. Player Experience

### 4.1 Text-Based Interaction

The game is driven by natural language input. Players type commands; the game responds with descriptive text, dialogue, and outcomes. The core loop: exploration, interaction, character development, narrative progression.

### 4.2 The Genesis Sequence

The onboarding process where a player creates their character and universe:

1. **Seed Concept** — Player provides a core idea or theme
2. **Universe Parameters** — Player + Universe Generator Agent define the fundamental laws
3. **World Generation** — World Builder Agent generates initial worlds
4. **Character Generation** — Character Creator Agent generates initial characters
5. **Nexus Connection** — Nexus Manager Agent establishes the universe's connection to the Nexus

The sequence is designed to feel like a meaningful creative act, not a form. The "strange mundane" onboarding scenarios (see [onboarding-scenarios.md](onboarding-scenarios.md)) establish the tone: ordinary moments that hint at something larger.

### 4.3 Exploration

- Players uncover how their universe connects to the Nexus
- Characters may travel between universes via exotic, unique methods
- Narrative Generator Agent + World Builder Agent + Lore Keeper Agent collaborate to describe locations
- All game entities are persisted in the knowledge graph

### 4.4 Character Development

- Characters are created during Genesis and developed through play
- The system tracks personality traits, relationships, motivations, and history
- Player choices shape character arc; character arc shapes therapeutic journey
- Psychological profiling, trauma tracking, and addiction tracking are maintained subtly

### 4.5 Dynamic Narrative Progression

The narrative is not static. It unfolds dynamically based on:
- Player choices and their cascading consequences
- AI-generated content responding to the current game state
- The evolving knowledge graph

Player decisions have meaningful consequences that ripple across the game world.

---

## 5. Core Gameplay Loop

```
Player Input
    ↓
Input Processor Agent (IPA) — parses intent, extracts entities
    ↓
AI Agent Orchestration (LangGraph) — routes to appropriate agent(s)
    ↓
AI Agent Processing — generates response, adhering to metaconcepts
    ↓
Narrative Generator Agent (NGA) — synthesizes final output
    ↓
Data Storage (Neo4j) — updates knowledge graph
    ↓
Output to Player
```

### 5.1 Example Scenarios

**Exploration:**
- `go north` → IPA identifies movement → WBA queries graph → generates location description → NGA presents it

**Interaction:**
- `talk to the guard` → NGA queries guard's personality + history → generates contextual dialogue

**Combat:**
- `attack goblin with sword` → Combat Agent calculates outcome → NGA narrates result

**Therapeutic Intervention:**
- `I feel lost and alone` → IPA identifies emotional state → Therapeutic Agent queries concepts → offers choice: explore feelings or focus on strengths → narrative branches accordingly

### 5.2 Metaconcepts

All agent actions adhere to global metaconcepts:
- Do No Harm
- Respect Player Agency
- Maintain Narrative Consistency
- Promote Self-Reflection
- Provide Support and Encouragement
- Protect Player Privacy

---

## 6. AI Agent Architecture

### 6.1 Agent Roster

| Agent | Role |
|-------|------|
| **IPA** — Input Processor Agent | Parses player input, identifies intent, extracts entities |
| **NGA** — Narrative Generator Agent | Synthesizes all agent outputs into final text |
| **WBA** — World Builder Agent | Generates and manages locations, environments, objects |
| **CCA** — Character Creator Agent | Creates characters with traits, relationships, motivations |
| **LKA** — Lore Keeper Agent | Ensures lore consistency; manages concept mapping |
| **NMA** — Nexus Manager Agent | Manages inter-universe connections and travel |
| **UGA** — Universe Generator Agent | Guides the Genesis sequence |
| **POA** — Player Onboarding Agent | Guides new players through initial experience |
| **NTA** — Nexus Travel Agent | Manages player travel between universes |
| **TA** — Therapeutic Agent | Provides subtle therapeutic interventions and support |

### 6.2 Orchestration (LangGraph)

LangGraph manages the workflow, activating appropriate agents based on IPA output and current game state. Agents communicate via:
- **Request-Response**: One agent requests info from another
- **Delegation**: One agent delegates a complex task
- **Publish-Subscribe**: Agents broadcast events; others subscribe

### 6.3 Prompt Construction

Each prompt includes:
1. Metaconcepts (global instructions)
2. Agent role and task definition
3. Contextual information (relevant knowledge graph data)
4. Available tools (LangChain tool definitions)
5. Output format instructions

### 6.4 Chain-of-Retrieval Augmented Generation (CoRAG)

Agents use CoRAG — iterative retrieval from the knowledge graph via dynamically generated sub-queries — to refine responses with increasing context depth.

---

## 7. Knowledge Graph

The Neo4j knowledge graph is the engine of TTA. It stores all game state, entities, relationships, lore, and therapeutic concepts.

### 7.1 Core Node Types

`Abstract`, `AIAgent`, `Category`, `Character`, `Concept`, `Culture`, `Event`, `Faction`, `Item`, `Language`, `Location`, `Metaconcept`, `Nexus`, `Prompt`, `PromptChain`, `Region`, `TimeSystem`, `TimePoint`, `TimeUnit`, `TimeBranch`, `Universe`, `Player`

### 7.2 Event Model

Every meaningful change in the game world is recorded as an Event:

```cypher
(:Event {
  type: string,          // "Battle", "Discovery", "Conversation"
  description: string,
  location: string,
  time: datetime,
  duration: duration (optional),
  participants: array (optional)
})

(:Event)-[:OCCURS_AT]->(:TimePoint)
(:Event)-[:IMPACTS]->(:Character|:Location|:Item|...)
(:Event)-[:IMPACTS_BELIEF]->(:Character)
(:Event)-[:CAUSED_BY]->(:Event)
(:Event)-[:PART_OF]->(:Event)
```

Every object has a timeline: `(:Object)-[:HAS_TIMELINE]->(:Timeline)-[:CONTAINS_EVENT]->(:Event)`

### 7.3 Time System

A hybrid time model supports:
- Linear and non-linear narrative progression
- Multiple time systems per universe (e.g., Aethelgardian Time vs. Multiverse Standard Time)
- Branching timelines
- Cross-universe temporal relationships

### 7.4 Character Schema

```cypher
(:Character {
  id: UUID, name, appearance, background,
  personality_traits: [],
  character_goals: [],
  comfort_level: int (1-10),
  therapeutic_intensity: LOW|MEDIUM|HIGH,
  therapeutic_goals: [],
  big_five: {},
  shadow_self: {}
})
(:User)-[:OWNS]->(:Character)
```

See [data-model.md](data-model.md) for the full schema.

---

## 8. Therapeutic Framework

### 8.1 Eight Evidence-Based Approaches

TTA integrates eight therapeutic frameworks, woven into narrative mechanics rather than presented explicitly:

| Framework | Core Mechanic |
|-----------|--------------|
| **CBT** | Thought records via character journal; behavioral experiments through choices |
| **DBT** | Emotion regulation via story pacing; distress tolerance via consequence navigation |
| **Mindfulness** | Present-moment scene descriptions; body scan via environmental awareness |
| **ACT** | Values clarification through character goal-setting; psychological flexibility via world-hopping |
| **Trauma-Informed Care** | Safety-first world design; player control over pacing and content |
| **Motivational Interviewing** | Collaborative dialogue with NPCs; change talk embedded in story progression |
| **SFBT** | Strength identification through character achievement; scaling progress via character levels |
| **Narrative Therapy** | Story reframing via alternate universe choices; externalization through character creation |

See [evidence-based-frameworks.md](evidence-based-frameworks.md) for detailed implementation strategies.

### 8.2 Subtle Integration Mechanisms

- **Concept Mapping**: Therapeutic concepts (Trauma, Resilience, Acceptance, Self-Compassion, Mindfulness) are nodes in the knowledge graph. AI agents draw on these to color narratives without labeling them.
- **Dynamic Narrative Generation**: If a player's choices indicate a need for self-compassion, the game offers situations to practice it — never stating this explicitly.
- **Character Arcs**: NPC arcs model therapeutic journeys (struggle → setback → growth). Players witness therapeutic processes through characters they care about.
- **Philosophical Dialogue**: NPCs engage in philosophical discussion that provokes self-reflection, without instructing the player what to think.
- **Hidden Storylines**: Deep exploration reveals storylines that address trauma, addiction, and self-discovery as rewards for engagement.

### 8.3 Crisis Protocol

- Content moderation system filters harmful content automatically
- Crisis detection triggers gentle offers of real-world resources
- Human-in-the-Loop (HITL) review for flagged content
- TTA is explicitly not a replacement for professional therapy

### 8.4 Therapeutic Matching

The system tracks player psychology over time and adapts the framework emphasis. A player showing CBT-compatible patterns receives more thought-record opportunities; a player in crisis receives trauma-informed pacing.

---

## 9. Entertainment-First Design

### 9.1 UI Mode System

Two interface modes:
- **Entertainment Mode** (default for players): Adventure language, immersive framing
- **Clinical Mode** (default for clinicians): Clinical terminology, outcome tracking

Players can toggle if allowed; clinicians default to clinical.

### 9.2 Onboarding: The Mundane-Strange Transition

The onboarding experience begins in a player's ordinary reality and introduces the uncanny:
- A bus stop shimmer reveals ghostly figures boarding a phantom bus
- A café latte swirls into cryptic symbols
- A library book opens itself to a message addressed to the reader

This establishes the tone: the extraordinary is hiding in the ordinary. The player's journey into the multiverse begins with the realization that their own world is stranger than they thought.

See [onboarding-scenarios.md](onboarding-scenarios.md) for 13+ scenario examples.

---

## 10. Technical Architecture

### 10.1 Three-Layer Architecture

```
Layer 1: TTA.dev (Universal Toolkit)
  — Domain-agnostic workflow primitives
  — CachePrimitive, RetryPrimitive, TimeoutPrimitive
  — Works for any application (recipe app, trading bot, etc.)

Layer 2: TTA Game Toolkit (Narrative Extensions)
  — Narrative-specific extensions of TTA.dev primitives
  — Agent orchestration, therapeutic safety monitoring
  — Character/world management, session context

Layer 3: TTA Game (Player-Facing)
  — Player experience (React/TS frontend)
  — Living worlds (world state management)
  — All user-facing features
```

**Decision rule**: "Could this work for a recipe app?" → TTA.dev. "Is it narrative/therapeutic?" → TTA.

See [architecture.md](architecture.md) for full decision tree and component breakdown.

### 10.2 Technology Stack

| Component | Technology |
|-----------|-----------|
| Frontend | React 18+ / TypeScript / Redux Toolkit / Tailwind CSS |
| Backend | Python 3.11+ / FastAPI |
| Primary DB | Neo4j 5.x (graph database) |
| Cache / Sessions | Redis 7.x |
| AI Orchestration | LangGraph |
| AI Framework | LangChain |
| Primary LLM | Qwen2.5 (local) / OpenRouter (cloud) |
| Data Validation | Pydantic |
| TTA.dev Primitives | tta-dev-primitives, tta-observability-integration |

### 10.3 API Status (as of 2025-01-23)

| Area | Status |
|------|--------|
| Auth (register, login) | ✅ Implemented |
| User settings | ✅ Implemented |
| Character management | ❌ Not implemented |
| World management | ❌ Not implemented |
| Session management | ❌ Not implemented |
| AI model status | 🔶 Partial |

See [technical-specifications.md](technical-specifications.md) for full API reference and database schemas.

---

## 11. User Types & Journeys

Six user categories, each with distinct entry points, workflows, and success metrics:

| Type | Description | Default Mode |
|------|-------------|-------------|
| **Players** | End users seeking therapeutic storytelling | Entertainment |
| **Patients** | Clinical users in formal healthcare settings | Clinical (clinician-managed) |
| **Clinical Staff** | Therapists and healthcare providers | Clinical |
| **Public Users** | General audience exploring the platform | Entertainment |
| **Developers** | Technical team building the platform | Clinical |
| **Administrators** | System managers and operators | Clinical |

See [user-journey-matrix.md](user-journey-matrix.md) for detailed entry points, authentication flows, permission levels, and success metrics for each type.

---

## 12. Development Roadmap

### Phase 0: Foundation (Current)
- Repo cleanup and organization ← in progress
- Specs written and organized ← this document
- TTA.dev repackaged and installable
- Local environment stable and documented

### Phase 1: Core Functionality
- Core knowledge graph structure implemented (Neo4j)
- Genesis sequence functional
- Basic AI agent pipeline (IPA → LangGraph → NGA)
- Character creation and persistence
- Basic exploration loop

### Phase 2: Expansion
- World management (worlds, locations, factions)
- NPC system with relationship tracking
- Session management and save/restore
- Therapeutic agent integrated
- Entertainment-first UI complete

### Phase 3: Advanced Features
- Collective Unconscious (cross-player knowledge graph)
- AI-driven therapeutic support (with clinical review)
- Universal economy system
- Multi-universe travel via Nexus

### Phase 4: Polish & Validation
- Clinical validation with mental health professionals
- User acceptance testing
- Performance optimization
- Accessibility compliance
- A/B testing of engagement vs. therapeutic outcomes

---

## 13. Ethical Framework

### 13.1 Core Commitments

- **Privacy**: Data minimization, anonymization, informed consent, local LLM preference
- **Bias Mitigation**: Diverse character representation, inclusive language, ongoing monitoring
- **Therapeutic Responsibility**: TTA is not therapy. It is a safe space for self-discovery. Crisis protocols are in place.
- **Content Safety**: AI filtering + HITL moderation. Players can report. Moderator tools provided.
- **Transparency**: Players understand what the game is. No manipulation.
- **Responsible AI**: AI behavior is monitored and adjusted continuously.

### 13.2 Clinical Consultation

A formal clinical consultation process (4 phases) validates all therapeutic content:
1. Framework development review
2. System implementation review
3. Content validation
4. Pilot testing

Consultants require 5+ years clinical practice. See [clinical-consultation-framework.md](clinical-consultation-framework.md).

---

## 14. Source Documents

All source materials that inform this GDD:

| Document | Location | Content |
|----------|----------|---------|
| TTA 7 Design Document | [TTA-7-design-document.md](TTA-7-design-document.md) | Original design doc — multiverse, genesis, agents, modules |
| Core Gameplay Loop | [core-gameplay-loop.md](core-gameplay-loop.md) | Loop components, agent roles, metaconcepts |
| Therapeutic Integration | [therapeutic-integration.md](therapeutic-integration.md) | Philosophical depth on the therapeutic approach |
| Amazing Ideas | [amazing-ideas.md](amazing-ideas.md) | Dream Weaving, Collective Unconscious, concept-based quests |
| Data Model | [data-model.md](data-model.md) | Event model, time system, Neo4j schema |
| Onboarding Scenarios | [onboarding-scenarios.md](onboarding-scenarios.md) | 13+ mundane-to-strange transition examples |
| Entertainment-First Design | [entertainment-first-design.md](entertainment-first-design.md) | Terminology translation system, UI modes, components |
| Technical Specifications | [technical-specifications.md](technical-specifications.md) | Full API reference, DB schemas, security specs |
| Evidence-Based Frameworks | [evidence-based-frameworks.md](evidence-based-frameworks.md) | 8 therapeutic approaches with implementation strategies |
| Clinical Consultation Framework | [clinical-consultation-framework.md](clinical-consultation-framework.md) | Validation process, consultant requirements |
| User Journey Matrix | [user-journey-matrix.md](user-journey-matrix.md) | 6 user types, journeys, success metrics |
| Architecture | [architecture.md](architecture.md) | Three-layer architecture, decision tree, component breakdown |

---

*This document is the authoritative Game Design Document for TTA. It should be updated as the design evolves. All other design documents in `docs/design/` are source materials that feed into this GDD.*
