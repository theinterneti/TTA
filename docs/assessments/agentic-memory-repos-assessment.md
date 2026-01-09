# Assessment: Agentic Memory Repositories for TTA Integration

**Date:** 2025-11-03
**Assessed by:** GitHub Copilot
**Repositories:**
- **ACE (Agentic Context Engine):** https://github.com/kayba-ai/agentic-context-engine
- **Eion:** https://github.com/eiondb/eion

---

## Executive Summary

Both repositories offer sophisticated approaches to AI agent memory management, but serve different purposes and architectural needs within TTA:

- **ACE (Agentic Context Engine)**: Best for **in-context learning and strategy accumulation** through a Generator-Reflector-Curator pattern. Ideal for TTA's therapeutic narrative agents that need to learn from player interactions.

- **Eion**: Best for **multi-agent memory coordination** with Neo4j knowledge graphs and PostgreSQL vector storage. More suitable for TTA's agent orchestration layer where multiple agents need shared memory.

**Recommendation:** **Selective Integration** - Use ACE patterns for individual therapeutic agents, and consider Eion's architecture principles for multi-agent coordination.

---

## 1. Agentic Context Engine (ACE)

### Overview
- **Language:** Python
- **License:** MIT
- **Stars:** 482 ⭐
- **Maturity:** Active development, v0.3.0+
- **Core Concept:** Context-based learning through Generator → Reflector → Curator workflow

### Architecture Quality: ⭐⭐⭐⭐⭐

**Strengths:**
1. **Clean Three-Role Pattern**
   ```python
   # Well-defined separation of concerns
   Generator: Executes tasks using playbook strategies
   Reflector: Analyzes outcomes, tags helpful/harmful strategies
   Curator: Updates playbook with delta operations
   ```

2. **Flexible LLM Integration**
   - `LiteLLMClient` supports 100+ providers (OpenAI, Anthropic, Claude, Gemini)
   - `TransformersLLMClient` for local models
   - `LangChainLLMClient` for LangChain ecosystem
   - Clean `LLMClient` abstraction for custom providers

3. **Playbook System** (Core Innovation)
   - JSON-serializable "living document" of strategies
   - Delta operations: ADD, UPDATE, TAG, REMOVE
   - Bullet tagging: helpful/harmful/neutral
   - Persistent across sessions
   - **Perfect for TTA's therapeutic strategy accumulation**

4. **Observability Integration**
   ```python
   # Built-in Opik tracing (optional)
   from ace.observability import configure_opik
   configure_opik(project_name="ace-therapy-agent")
   ```

5. **Testing Infrastructure**
   - Comprehensive unit tests with `DummyLLMClient`
   - Benchmark suite (SQuAD, FINER, MMLU, HellaSwag)
   - Mutation testing (100% scores)
   - Train/test splits to prevent overfitting

### Code Quality: ⭐⭐⭐⭐½

**Strengths:**
- Type hints throughout (`GeneratorOutput`, `ReflectorOutput`, `CuratorOutput`)
- Retry logic with exponential backoff
- JSON parsing with error recovery
- Customizable prompts via templates
- Clean error handling patterns

**Weaknesses:**
- Some prompt templates hardcoded in Chinese (internationalization needed)
- Limited async support (mostly synchronous LLM calls)
- No built-in circuit breaker patterns (TTA would need to add)

### TTA Integration Potential: ⭐⭐⭐⭐⭐

**Excellent Fit For:**

1. **IPA (Input Processing Agent)**
   - Playbook: "Therapeutic input validation strategies"
   - Generator: Process player input
   - Reflector: Analyze therapeutic safety
   - Curator: Update safety guidelines

2. **NGA (Narrative Generation Agent)**
   - Playbook: "Narrative pacing and therapeutic framing"
   - Generator: Create narrative responses
   - Reflector: Evaluate therapeutic impact
   - Curator: Refine narrative techniques

3. **WBA (World Building Agent)**
   - Playbook: "World state consistency rules"
   - Generator: Update world state
   - Reflector: Check for contradictions
   - Curator: Maintain world model integrity

**Integration Architecture:**
```python
# TTA-specific ACE adapter
from ace import Generator, Reflector, Curator, Playbook, OfflineAdapter
from tta.agents import TherapeuticAgent

class TherapeuticACEAgent(TherapeuticAgent):
    def __init__(self, agent_id: str, llm_client):
        # Load agent-specific playbook
        self.playbook = Playbook.load_from_file(
            f".augment/playbooks/{agent_id}_playbook.json"
        )
        self.generator = Generator(llm_client)
        self.reflector = Reflector(llm_client)
        self.curator = Curator(llm_client)

    async def process_with_learning(self, input_data):
        # Generate response
        output = self.generator.generate(
            question=input_data.content,
            context=self._build_context(input_data),
            playbook=self.playbook
        )

        # Reflect on outcome
        reflection = self.reflector.reflect(
            question=input_data.content,
            generator_output=output,
            playbook=self.playbook,
            feedback=await self._evaluate_therapeutic_safety(output)
        )

        # Update playbook
        curator_output = self.curator.curate(
            reflection=reflection,
            playbook=self.playbook,
            question_context="therapeutic interaction",
            progress=f"session_{input_data.session_id}"
        )
        self.playbook.apply_delta(curator_output.delta)

        return output.final_answer
```

### Challenges for TTA:

1. **No Multi-Agent Coordination** - ACE is designed for single-agent learning
   - **Solution:** Use ACE per-agent, coordinate via TTA's Redis messaging

2. **No Graph-Based Memory** - Playbook is flat JSON
   - **Solution:** Integrate with TTA's Neo4j for cross-agent strategy sharing

3. **Synchronous by Default** - Not optimized for async workflows
   - **Solution:** Wrap ACE calls in TTA's async primitives with circuit breakers

### Licensing: ✅ MIT License
- **Commercial use:** Allowed
- **Modification:** Allowed
- **Attribution required:** Yes
- **Compatible with TTA's licensing**

---

## 2. Eion Database

### Overview
- **Language:** Go (backend) + Python (extraction service)
- **License:** AGPL-3.0
- **Stars:** 130 ⭐
- **Maturity:** Early stage (v0.1.4), active development
- **Core Concept:** Shared memory storage for multi-agent systems

### Architecture Quality: ⭐⭐⭐⭐

**Strengths:**

1. **Hybrid Storage Architecture**
   ```
   PostgreSQL + pgvector: Conversation history, semantic search
   Neo4j: Knowledge graph with temporal relationships
   Python Extraction Service: Entity/relationship extraction
   ```

2. **MCP Server Integration**
   - Model Context Protocol (MCP) for standardized agent communication
   - 8 built-in tools (4 memory, 4 knowledge)
   - LangChain and Claude Desktop integration
   - **Aligns with TTA's protocol bridge patterns**

3. **Multi-Agent Patterns**
   ```
   Sequential Agency: Agent A → context → Agent B → Eion
   Concurrent Agency: Multiple agents with live context sync
   Guest Access: External agent controlled access
   ```

4. **Temporal Knowledge Graph**
   - Automatic conflict resolution for temporal relationships
   - Edge validity tracking with ValidFrom/ValidUntil
   - Checksum-based deduplication
   - **Could enhance TTA's narrative consistency**

5. **Real Production Embeddings**
   - `all-MiniLM-L6-v2` (384 dimensions)
   - sentence-transformers integration
   - **Same model family TTA could standardize on**

### Code Quality: ⭐⭐⭐⭐

**Strengths:**
- Go microservice architecture with health checks
- Structured logging (zap)
- Database migration system
- Integration tests with Neo4j/PostgreSQL
- Configuration via YAML + environment variables

**Weaknesses:**
- Limited error handling in Python extraction service
- Some TODOs in knowledge retrieval paths
- MCP server subprocess management could be more robust
- Documentation incomplete for some API endpoints

### TTA Integration Potential: ⭐⭐⭐⭐

**Good Fit For:**

1. **Agent Orchestration Layer**
   - Shared memory across IPA, WBA, NGA
   - Session-based context management
   - Multi-agent coordination

2. **Knowledge Graph Integration**
   - Replace or complement TTA's existing Neo4j setup
   - Temporal relationship tracking for narrative consistency
   - Entity extraction for world building

3. **MCP Protocol Adoption**
   - Standardize agent communication
   - Tool-based API for agent actions
   - Compatible with TTA's message coordination

**Integration Architecture:**
```python
# TTA Agent Orchestration with Eion
from eion_client import EionSessionClient

class TTAAgentOrchestrator:
    def __init__(self):
        self.eion = EionSessionClient(base_url="http://localhost:8080")
        self.agents = {
            "IPA": InputProcessingAgent(),
            "WBA": WorldBuildingAgent(),
            "NGA": NarrativeGenerationAgent()
        }

    async def orchestrate_turn(self, session_id, player_input):
        # Store player input in shared memory
        await self.eion.add_memory(
            session_id=session_id,
            agent_id="orchestrator",
            user_id=session_id,
            messages=[{"role": "user", "content": player_input}]
        )

        # Sequential agent processing with shared context
        for agent_id, agent in self.agents.items():
            # Retrieve relevant memories
            memories = await self.eion.search_memory(
                session_id=session_id,
                agent_id=agent_id,
                query=player_input,
                limit=10
            )

            # Agent processes with context
            result = await agent.process(player_input, memories)

            # Store agent output back to shared memory
            await self.eion.add_memory(
                session_id=session_id,
                agent_id=agent_id,
                user_id=session_id,
                messages=[{"role": "assistant", "content": result}]
            )
```

### Challenges for TTA:

1. **AGPL-3.0 License** ⚠️
   - Copyleft license requires open-sourcing modifications
   - **Concern:** TTA's commercial deployment plans
   - **Options:**
     - Contact Eion team for commercial license
     - Use as inspiration, not direct integration
     - Deploy as separate microservice with API boundary

2. **Go Backend** - TTA is Python-native
   - **Mitigation:** Eion provides HTTP API + MCP integration
   - Could run as sidecar service in Docker

3. **Early Stage** - v0.1.4, documentation incomplete
   - **Risk:** Breaking changes in future versions
   - **Mitigation:** Pin to specific version, contribute upstream

4. **No Circuit Breaker Patterns**
   - Missing resilience patterns TTA already has
   - **Solution:** Wrap Eion calls in TTA's existing circuit breakers

### Licensing: ⚠️ AGPL-3.0

- **Commercial use:** Allowed BUT requires open-sourcing modifications
- **Modification:** Allowed (must open-source)
- **Attribution required:** Yes
- **Network use = distribution** - AGPL's key restriction
- **TTA Impact:** Could require open-sourcing TTA's orchestration layer if tightly integrated

---

## 3. Comparative Analysis

| Aspect | ACE | Eion | TTA Current State |
|--------|-----|------|-------------------|
| **Primary Focus** | In-context learning | Multi-agent memory | Agent orchestration |
| **Memory Model** | Playbook (strategies) | Session + Knowledge graph | Redis messages + Neo4j |
| **Multi-Agent** | ❌ Single agent | ✅ Native multi-agent | ✅ Redis-based coordination |
| **Learning** | ✅ Self-improvement | ❌ Static knowledge | ⚠️ Manual tuning |
| **Persistence** | JSON playbooks | PostgreSQL + Neo4j | Redis (ephemeral) + Neo4j |
| **LLM Flexibility** | ✅ 100+ providers | ⚠️ Indirect (via agents) | ✅ OpenRouter API |
| **Observability** | Opik integration | Basic health checks | Grafana + Prometheus |
| **License** | MIT ✅ | AGPL-3.0 ⚠️ | Mixed (mostly MIT) |
| **Maturity** | Medium (0.3.0) | Early (0.1.4) | Development phase |
| **Testing** | ✅ Comprehensive | ⚠️ Basic | ✅ Comprehensive battery |
| **Async Support** | ⚠️ Limited | ✅ Go concurrency | ✅ Python asyncio |
| **Circuit Breakers** | ❌ None | ❌ None | ✅ Built-in |
| **TTA Fit** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | - |

---

## 4. Recommendations for TTA

### Option 1: **Adopt ACE for Therapeutic Agent Learning** ⭐ **RECOMMENDED**

**What:**
- Integrate ACE's Generator-Reflector-Curator pattern into TTA agents
- Use playbooks for therapeutic strategy accumulation
- Maintain per-agent playbooks in `.augment/playbooks/`

**Why:**
- **MIT license** - No restrictions
- **Perfect fit** for TTA's therapeutic learning goals
- **Complements** existing architecture (doesn't replace)
- **Low risk** - Pure Python, well-tested

**Implementation Plan:**
```python
# Phase 1: Proof of Concept (1 week)
1. Install ACE framework: `uv add ace-framework`
2. Create TherapeuticACEAgent wrapper
3. Implement playbook persistence in .augment/playbooks/
4. Test with IPA agent on sample therapeutic scenarios

# Phase 2: Integration (2 weeks)
1. Wrap ACE calls in circuit breakers
2. Integrate with TTA's observability (Grafana)
3. Add async wrappers for non-blocking operation
4. Implement playbook versioning and rollback

# Phase 3: Expansion (3 weeks)
1. Deploy to all three agent types (IPA, WBA, NGA)
2. Create cross-agent playbook insights in Neo4j
3. Build playbook visualization dashboard
4. Tune reflection prompts for therapeutic contexts
```

**Risks:**
- Synchronous LLM calls may slow orchestration → Mitigate with async wrappers
- Playbooks could grow large → Implement pruning strategies
- Prompt templates need therapeutic customization → Create TTA-specific prompts

### Option 2: **Adopt Eion Architecture Principles** (NOT Direct Integration)

**What:**
- **Don't integrate Eion code** due to AGPL-3.0
- **Adopt architectural patterns:** MCP protocol, hybrid storage, temporal graphs
- Build TTA-native implementation

**Why:**
- AGPL-3.0 license conflicts with potential commercial use
- Eion is early stage (breaking changes likely)
- TTA already has similar infrastructure (Redis, Neo4j)

**Implementation Plan:**
```python
# Phase 1: MCP Protocol Evaluation (1 week)
1. Research Model Context Protocol specification
2. Assess fit with TTA's Protocol Bridge pattern
3. Create MCP adapter for existing TTA agents

# Phase 2: Temporal Graph Enhancement (2 weeks)
1. Add ValidFrom/ValidUntil fields to Neo4j relationships
2. Implement automatic conflict resolution (inspired by Eion)
3. Build checksum-based deduplication

# Phase 3: Session Memory Service (3 weeks)
1. Create TTA-native session memory manager
2. Integrate PostgreSQL for persistent conversation history
3. Build semantic search API using existing embeddings
```

**Risks:**
- Reinventing the wheel → Mitigate by learning from Eion's design
- Licensing uncertainty if code is too similar → Ensure clean-room implementation
- Complexity increase → Keep scope minimal, iterate

### Option 3: **Hybrid Approach** ⭐⭐ **BALANCED**

**What:**
- Use **ACE for agent learning** (direct integration)
- Use **Eion patterns for memory architecture** (inspiration only)
- Keep TTA's existing orchestration layer

**Why:**
- Best of both worlds: proven learning + proven memory
- ACE's MIT license allows direct use
- Eion's patterns improve TTA's existing Neo4j/Redis setup

**Implementation Plan:**
```
Week 1-2: ACE Integration (as Option 1, Phase 1-2)
Week 3-4: Memory Architecture Refinement (inspired by Eion)
Week 5-6: Integration Testing and Tuning
```

---

## 5. Detailed Integration Scenarios

### Scenario A: ACE for Therapeutic Narrative Learning

```python
# src/agent_orchestration/ace_integration/therapeutic_ace_agent.py
from ace import Generator, Reflector, Curator, Playbook, LiteLLMClient
from src.agent_orchestration.circuit_breaker import CircuitBreaker
from src.common.observability import MetricsCollector

class TherapeuticACEAgent:
    """ACE-enhanced agent with therapeutic learning capabilities."""

    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type  # IPA, WBA, NGA

        # Load or create playbook
        playbook_path = f".augment/playbooks/{agent_type}_{agent_id}.json"
        self.playbook = (
            Playbook.load_from_file(playbook_path)
            if Path(playbook_path).exists()
            else Playbook()
        )

        # Initialize ACE components with circuit breakers
        llm_client = LiteLLMClient(
            model="openrouter/anthropic/claude-3.5-sonnet",
            api_key=os.getenv("OPENROUTER_API_KEY")
        )
        self.generator = Generator(llm_client)
        self.reflector = Reflector(llm_client)
        self.curator = Curator(llm_client)

        # TTA-specific circuit breakers
        self.generator_cb = CircuitBreaker(f"{agent_id}_generator")
        self.reflector_cb = CircuitBreaker(f"{agent_id}_reflector")

        # Metrics
        self.metrics = MetricsCollector(f"ace_{agent_type}")

    async def process_with_learning(
        self,
        input_data: dict,
        therapeutic_context: dict
    ) -> dict:
        """Process input with ACE learning loop."""

        # Generate response (with circuit breaker)
        try:
            output = await self.generator_cb.call(
                self.generator.generate,
                question=input_data["content"],
                context=self._build_therapeutic_context(therapeutic_context),
                playbook=self.playbook
            )
        except CircuitBreakerOpenError:
            # Fallback to non-ACE processing
            return await self._fallback_process(input_data)

        # Evaluate therapeutic safety
        safety_feedback = await self._evaluate_therapeutic_safety(output)

        # Reflect on outcome (async wrapped)
        reflection = await asyncio.to_thread(
            self.reflector.reflect,
            question=input_data["content"],
            generator_output=output,
            playbook=self.playbook,
            feedback=safety_feedback["assessment"],
            ground_truth=therapeutic_context.get("expected_response")
        )

        # Curate playbook updates (background task)
        asyncio.create_task(self._curate_playbook(reflection, therapeutic_context))

        # Metrics
        self.metrics.record_generation(
            bullet_ids=output.bullet_ids,
            helpful_bullets=len([b for b in reflection.bullet_tags if b.tag == "helpful"]),
            harmful_bullets=len([b for b in reflection.bullet_tags if b.tag == "harmful"])
        )

        return {
            "response": output.final_answer,
            "reasoning": output.reasoning,
            "strategies_applied": output.bullet_ids,
            "safety_score": safety_feedback["score"]
        }

    async def _curate_playbook(self, reflection, context):
        """Background task to update playbook."""
        try:
            curator_output = await self.reflector_cb.call(
                self.curator.curate,
                reflection=reflection,
                playbook=self.playbook,
                question_context=f"{self.agent_type}_therapeutic",
                progress=f"session_{context.get('session_id')}"
            )

            # Apply delta
            self.playbook.apply_delta(curator_output.delta)

            # Persist playbook
            self.playbook.save_to_file(
                f".augment/playbooks/{self.agent_type}_{self.agent_id}.json"
            )

            # Log to Neo4j for cross-agent learning
            await self._log_strategy_to_neo4j(curator_output.delta)

        except Exception as e:
            logger.error(f"Playbook curation failed: {e}")

    async def _evaluate_therapeutic_safety(self, output):
        """TTA-specific therapeutic safety evaluation."""
        # Integrate with existing TTA safety validator
        from src.common.safety import TherapeuticSafetyValidator
        validator = TherapeuticSafetyValidator()

        return await validator.validate(
            content=output.final_answer,
            context=output.reasoning
        )

    async def _log_strategy_to_neo4j(self, delta):
        """Log successful strategies to Neo4j for cross-agent learning."""
        from src.infrastructure.neo4j import Neo4jGameplayManager
        neo4j = Neo4jGameplayManager()

        for op in delta.operations:
            if op.type == "ADD":
                await neo4j.add_strategy_node(
                    agent_type=self.agent_type,
                    section=op.section,
                    content=op.content,
                    success_count=1
                )
```

### Scenario B: Eion-Inspired Memory Architecture (Clean Room)

```python
# src/agent_orchestration/memory/tta_session_memory.py
"""
TTA Session Memory Manager - Inspired by Eion's architecture patterns
(Clean-room implementation to avoid AGPL-3.0 licensing issues)
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import asyncio

@dataclass
class TTAMemoryMessage:
    """Session message with semantic embedding."""
    uuid: str
    role: str  # "user", "assistant", "system"
    content: str
    embedding: List[float]
    created_at: datetime
    session_id: str
    agent_id: str

class TTASessionMemoryManager:
    """
    TTA-native session memory manager.
    Inspired by Eion's hybrid storage but implemented from scratch.
    """

    def __init__(self, postgres_conn, neo4j_conn, redis_conn):
        self.pg = postgres_conn  # Conversation history
        self.neo4j = neo4j_conn  # Knowledge graph
        self.redis = redis_conn  # Hot cache

    async def add_memory(
        self,
        session_id: str,
        agent_id: str,
        messages: List[dict],
        skip_knowledge_extraction: bool = False
    ):
        """Store memory with optional knowledge extraction."""

        # Generate embeddings
        from src.common.embeddings import EmbeddingService
        embedder = EmbeddingService()

        memory_messages = []
        for msg in messages:
            embedding = await embedder.embed(msg["content"])
            memory_messages.append(TTAMemoryMessage(
                uuid=str(uuid.uuid4()),
                role=msg["role"],
                content=msg["content"],
                embedding=embedding,
                created_at=datetime.utcnow(),
                session_id=session_id,
                agent_id=agent_id
            ))

        # Store in PostgreSQL + pgvector
        await self._store_in_postgres(memory_messages)

        # Cache in Redis (5 minute TTL)
        await self._cache_in_redis(session_id, memory_messages)

        # Extract knowledge to Neo4j (background task)
        if not skip_knowledge_extraction:
            asyncio.create_task(
                self._extract_to_neo4j(session_id, memory_messages)
            )

    async def search_memory(
        self,
        session_id: str,
        query: str,
        limit: int = 10,
        min_score: float = 0.7
    ) -> List[TTAMemoryMessage]:
        """Semantic search across session memories."""

        # Check Redis cache first
        cached = await self._check_cache(session_id, query)
        if cached:
            return cached

        # Generate query embedding
        from src.common.embeddings import EmbeddingService
        embedder = EmbeddingService()
        query_embedding = await embedder.embed(query)

        # Semantic search in PostgreSQL
        results = await self.pg.fetch(
            """
            SELECT uuid, role, content, created_at,
                   1 - (embedding <=> $1::vector) as similarity
            FROM session_memories
            WHERE session_id = $2
              AND 1 - (embedding <=> $1::vector) >= $3
            ORDER BY embedding <=> $1::vector
            LIMIT $4
            """,
            query_embedding,
            session_id,
            min_score,
            limit
        )

        return [self._row_to_message(row) for row in results]

    async def _extract_to_neo4j(self, session_id, messages):
        """Extract entities and relationships to Neo4j knowledge graph."""

        # TTA's existing extraction logic (enhanced with temporal tracking)
        from src.infrastructure.knowledge_extraction import KnowledgeExtractor
        extractor = KnowledgeExtractor()

        for msg in messages:
            entities, relationships = await extractor.extract(msg.content)

            # Store with temporal validity (Eion-inspired)
            for entity in entities:
                await self.neo4j.merge_entity(
                    name=entity.name,
                    type=entity.type,
                    properties={
                        **entity.properties,
                        "valid_from": msg.created_at,
                        "session_id": session_id,
                        "source_message_uuid": msg.uuid
                    }
                )

            for rel in relationships:
                await self.neo4j.merge_relationship(
                    source=rel.source,
                    target=rel.target,
                    type=rel.type,
                    properties={
                        **rel.properties,
                        "valid_from": msg.created_at,
                        "session_id": session_id,
                        "checksum": self._compute_checksum(rel)
                    }
                )

    def _compute_checksum(self, relationship) -> str:
        """Checksum for deduplication (Eion-inspired)."""
        import hashlib
        data = f"{relationship.source}:{relationship.type}:{relationship.target}"
        return hashlib.sha256(data.encode()).hexdigest()
```

---

## 6. Risk Assessment

### ACE Integration Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Synchronous LLM calls block orchestration | Medium | Wrap in `asyncio.to_thread()` or use async LLM clients |
| Playbooks grow unbounded | Low | Implement pruning: keep top-N helpful bullets |
| Prompt templates in Chinese | Low | Create English therapeutic prompts |
| No built-in circuit breakers | Medium | Use TTA's existing circuit breaker wrapper |
| Learning from harmful strategies | High | Enhanced reflection with safety validator |

### Eion Integration Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| AGPL-3.0 license contamination | **Critical** | **Don't integrate code directly** - patterns only |
| Early stage breaking changes | Medium | Pin version, contribute to stability |
| Go backend adds complexity | Low | Use as HTTP microservice |
| Documentation incomplete | Medium | Read source code, contribute docs |
| No circuit breakers | Medium | TTA already has this pattern |

---

## 7. Next Steps

### Immediate Actions (Week 1)

1. **ACE Proof of Concept**
   ```bash
   # Install ACE
   cd ~/recovered-tta-storytelling
   uv add ace-framework

   # Create test playbook
   mkdir -p .augment/playbooks
   python scripts/test_ace_therapeutic_agent.py
   ```

2. **Review Current TTA Memory Architecture**
   - Audit `src/infrastructure/neo4j/gameplay_manager.py`
   - Identify gaps ACE/Eion patterns could fill
   - Document current limitations

3. **Create Integration Proposal**
   - Technical design doc for ACE integration
   - Architecture diagram showing ACE + TTA orchestration
   - Timeline and resource estimates

### Short-Term Goals (Weeks 2-4)

1. **ACE Integration**
   - Wrap IPA agent with ACE learning
   - Create therapeutic prompt templates
   - Build playbook visualization dashboard

2. **Memory Architecture Enhancement**
   - Add temporal tracking to Neo4j relationships (Eion-inspired)
   - Implement checksum-based deduplication
   - Build session memory search API

3. **Testing & Validation**
   - Run TTA comprehensive battery with ACE agents
   - Measure playbook growth and pruning effectiveness
   - Validate therapeutic safety with learned strategies

### Long-Term Goals (Months 2-3)

1. **Full ACE Rollout**
   - All three agent types (IPA, WBA, NGA) using ACE
   - Cross-agent strategy sharing via Neo4j
   - Playbook evolution analytics

2. **MCP Protocol Evaluation**
   - Research Model Context Protocol fit with TTA
   - Build MCP adapter for TTA agents
   - Evaluate Claude Desktop integration

3. **Production Hardening**
   - Circuit breakers around all ACE calls
   - Async wrappers for non-blocking operation
   - Grafana dashboards for ACE metrics

---

## 8. Conclusion

Both repositories offer valuable patterns for TTA:

✅ **ACE (Recommended for Direct Integration)**
- MIT license - no restrictions
- Perfect for therapeutic agent learning
- Clean architecture, well-tested
- Low integration risk

⚠️ **Eion (Use Patterns Only - No Direct Integration)**
- AGPL-3.0 license - too restrictive
- Excellent architectural patterns
- Early stage - risky for direct use
- Learn from their design, implement TTA-native

**Final Recommendation:** Integrate ACE for agent learning, adopt Eion's memory architecture patterns (clean-room implementation). This gives TTA sophisticated therapeutic learning capabilities while maintaining licensing flexibility.

---

## Appendix A: Code Samples

### ACE Integration Example

See `Scenario A: ACE for Therapeutic Narrative Learning` above.

### Eion-Inspired Pattern Example

See `Scenario B: Eion-Inspired Memory Architecture (Clean Room)` above.

### Testing Strategy

```python
# tests/integration/test_ace_therapeutic_agent.py
import pytest
from src.agent_orchestration.ace_integration import TherapeuticACEAgent

@pytest.mark.asyncio
async def test_ace_agent_learns_from_therapeutic_interaction():
    """Test ACE agent improves therapeutic responses over multiple turns."""

    # Initialize agent with empty playbook
    agent = TherapeuticACEAgent("ipa-001", "IPA")
    assert len(agent.playbook.bullets()) == 0

    # Simulate therapeutic interaction requiring reflection
    unsafe_input = {
        "content": "I feel like giving up on everything.",
        "session_id": "test-session-123"
    }
    therapeutic_context = {
        "player_emotional_state": "distressed",
        "session_stage": "crisis_intervention"
    }

    # First response (no strategies yet)
    response1 = await agent.process_with_learning(unsafe_input, therapeutic_context)

    # Wait for background curation
    await asyncio.sleep(2)

    # Playbook should now have learned strategies
    playbook_after = agent.playbook
    assert len(playbook_after.bullets()) > 0

    # Find crisis intervention strategies
    crisis_bullets = [
        b for b in playbook_after.bullets()
        if "crisis" in b.content.lower() or "safety" in b.content.lower()
    ]
    assert len(crisis_bullets) > 0

    # Second similar interaction should apply learned strategies
    response2 = await agent.process_with_learning(unsafe_input, therapeutic_context)

    # Verify strategies were applied
    assert len(response2["strategies_applied"]) > 0
    assert response2["safety_score"] >= 0.8  # High safety due to learned strategies
```

---

## Appendix B: References

- **ACE Paper:** https://arxiv.org/abs/2510.04618
- **ACE Repository:** https://github.com/kayba-ai/agentic-context-engine
- **ACE Documentation:** https://github.com/kayba-ai/agentic-context-engine/blob/main/docs/
- **Eion Repository:** https://github.com/eiondb/eion
- **Eion Website:** https://www.eiondb.com/
- **Model Context Protocol:** https://modelcontextprotocol.io/
- **TTA Architecture Docs:** `.augment/kb/TTA___Architecture___*`
- **TTA Testing Standards:** `.github/instructions/testing-battery.instructions.md`

---

**Assessment Complete** ✅

*This document provides a comprehensive analysis for TTA leadership to make an informed decision on integrating agentic memory patterns. The recommendation prioritizes ACE for direct integration (therapeutic learning) while learning from Eion's architectural wisdom without licensing risk.*


---
**Logseq:** [[TTA.dev/Docs/Assessments/Agentic-memory-repos-assessment]]
