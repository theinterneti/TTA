# Implementation Plan

- [x] 1. Set up core orchestration infrastructure and base classes

  - Created directory structure for agent orchestration components (src/agent_orchestration)
  - Implemented base AgentOrchestrationComponent class inheriting from TTA Component
  - Defined core data models and interfaces for agent communication (AgentId/Message models, MessageCoordinator/AgentProxy)
  - Wired orchestrator import and added gated default config+schema
  - _Requirements: 1.1, 8.1_

- [x] 2. Implement core data models and validation
- [x] 2.1 Create agent state and context data models

  - Wrote data models for AgentContext, AgentState, and SessionContext
  - Implemented validation helpers for agent communication data structures
  - Created WorkflowDefinition and OrchestrationResponse models
  - _Requirements: 1.1, 2.1, 8.1_

- [x] 2.2 Implement message passing data structures

  - Enhanced AgentMessage and added serialization-friendly structures
  - Refined MessageCoordinator interface and added message queue/subscription models
  - Added message priority and routing logic data models
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 3. Create workflow management system
- [x] 3.1 Implement WorkflowManager core functionality

  - Wrote WorkflowManager class with workflow registration and execution
  - Implemented workflow definition validation and request validation
  - Added workflow run state tracking and metadata updates
  - Added extension points for LangGraph graph build/execute
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 3.2 Implement LangGraph workflow integration

  - Added optional LangGraph builder/executor stubs with graceful fallback
  - Build compiles a simple StateGraph when available, stub otherwise
  - Execute runs the compiled app with provided state, stub otherwise
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 4. Build message coordination system
- [x] 4.1 Implement MessageCoordinator with Redis backend

  - Implemented RedisMessageCoordinator with priority queues and routing
  - Added send_message with backpressure handling and audit trails
  - Implemented broadcast_message for multi-recipient delivery
  - Created subscribe_to_messages for agent subscription management
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 4.2 Add message reliability and error handling

  - Implemented message retry logic with exponential backoff
  - Added message ordering and priority queue management (HIGH->NORMAL->LOW)
  - Created message persistence and recovery mechanisms for failed deliveries
  - Added receive/ack/nack pattern with visibility timeouts
  - Implemented dead letter queue (DLQ) for permanent failures
  - Added recover_pending for reclaiming expired reservations
  - _Requirements: 2.2, 2.3, 2.4, 6.1, 6.2_

- [x] 5. Develop resource management system
- [x] 5.1 Implement ResourceManager for GPU and memory allocation

  - Implemented ResourceManager class with GPU memory monitoring and allocation
  - Added CPU thread and RAM resource tracking and management
  - Created resource usage reporting and optimization algorithms
  - Integrated with psutil for system metrics and torch/pynvml for GPU stats
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 5.2 Add performance monitoring and optimization

  - Implemented performance metrics collection for agent execution times
  - Added resource utilization monitoring with configurable alerting thresholds
  - Created diagnostics endpoints (/health, /metrics JSON, /metrics-prom)
  - Integrated background monitoring with configurable intervals
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 5.3 Diagnostics: extend performance metrics exposure

  - Extended /metrics JSON to include per-agent step stats: p50, p95, avg, error_rate
  - Extended /metrics-prom to export step duration (Histogram) and error rate (Gauge) labeled by agent
  - Added Prometheus metrics for message delivery, retries, and queue lengths
  - Implemented performance aggregator for workflow step tracking
  - _Requirements: 4.1, 4.5_

- [x] 6.3 Configuration schema validation (Agent Orchestration resources/monitoring)

  - Added complete agent_orchestration section to config/tta_config.yaml with full schema
  - Implemented resources configuration: gpu_memory_limit, cpu_thread_limit, memory_limit
  - Added monitoring section: metrics_interval, cpu_warn/mem_warn/cpu_crit/mem_crit thresholds
  - Implemented configuration validation and memory string parsing ("4GB" -> bytes)
  - _Requirements: 4.1, 4.4, 8.3_

- [x] 6. Create agent interface abstractions
- [x] 6.1 Implement base Agent interface and communication protocols

  - Implemented abstract Agent base class with standardized async communication interface (send/receive helpers), lifecycle (start/stop/health_check), message serialization, and timeout/error handling with performance metrics aggregation
  - Implemented AgentRegistry (in-memory) and RedisAgentRegistry (persistent, heartbeat-based liveness) with discovery and periodic health checks
  - Added diagnostics integration: /metrics includes agents snapshot; new /agents endpoint added with derived per-instance performance metrics and heartbeat ages
  - _Requirements satisfied: 1.1 (communication), 2.1 (orchestration), 8.1 (monitoring), 8.2 (reliability)_

- [x] 6.2 Build agent proxy classes for existing agents

  - Implemented InputProcessorAgentProxy (validation, retry helper)
  - Implemented WorldBuilderAgentProxy (world state caching/updates)
  - Implemented NarrativeGeneratorAgentProxy (content filtering)
  - All proxies inherit from Agent, support sync/async, include logging and error handling
  - _Requirements satisfied: 1.1 (communication), 1.2 (integration), 2.1 (orchestration), 3.1 (narrative flow)_

Summary of tests: Added unit tests for Agent lifecycle/timeouts/retry/cache/filtering and Redis-marked tests for RedisAgentRegistry, auto-registration, /agents diagnostics; all passing.

- [x] 7. Implement dynamic tool system integration

- [x] 7.1 Create tool coordination and sharing mechanisms

  - Design and implement ToolSpec (Pydantic) with: name, version, description, args_schema (JSON-schema or Pydantic model ref), returns_schema, capabilities (tags), safety_flags, created_at, last_used_at, owner (agent_id optional)
  - Implement comprehensive validation and safety checks:
    - Name/description sanitization and length limits; version semantic validation
    - Args/returns schema validation via Pydantic; cap total parameters and max nesting depth
    - Security controls: disallow filesystem/network/process execution unless explicitly whitelisted by config; enforce allowlist of Python callables when wrapping functions
    - Capability verification: ensure declared capabilities match actual callable behavior signature
  - Create a centralized Redis-backed ToolRegistry with lifecycle management:
    - Keys: {pfx}:tools:{name}:{version} -> JSON ToolSpec; {pfx}:tools:index -> set of "{name}:{version}"; {pfx}:tools:status:{name}:{version} -> status (active|deprecated)
    - API: register_tool(spec), get_tool(name, version=None -> latest), list_tools(prefix=None), deprecate_tool(name, version), touch_last_used(name, version), cleanup_expired(max_idle_s)
    - Concurrency: idempotent registration (SETNX) and per-key async locks for local process safety
  - Implement ToolCoordinator for dynamic generation and sharing across agents:
    - create_or_get(signature, factory_fn, \*, policy): deduplicate by stable signature hash of ToolSpec/args_schema; on miss, build via factory_fn, validate, register, return
    - Provide thread/async-safety for multi-agent access; integrate error handling and fallbacks (return safe stub or deny)
  - Diagnostics: extend /metrics JSON with tools summary (total, active, deprecated, cache_hits, cache_misses) and per-tool exec stats when available; include in Prometheus export when diagnostics enabled
  - Ensure thread-safety and concurrent access patterns for multi-agent tool sharing
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 7.2 Add tool optimization and caching infrastructure

  - Implement in-memory LRU cache for ToolSpec lookups with configurable TTL and max_items to prevent redundant tool generation
  - Track tool performance metrics: execution time histogram, success/failure counts, error_rate; tie into existing metrics aggregation and diagnostics
  - Automated cleanup and resource management for unused/expired tools: background task scans last_used_at and deprecates or prunes Redis entries beyond max_idle_s (configurable)
  - Add tool usage analytics and basic optimization recommendations (e.g., suggest promoting frequently used dynamic tools to static, or adjusting TTL/eviction)
  - Implement tool versioning policy and backward compatibility checks when updating ToolSpec
  - Testing: unit tests for validation and caching; Redis-marked tests for registry lifecycle, deprecation, concurrent register/get, and cleanup using existing fixtures (@pytest.mark.redis, redis_client)
  - _Requirements: 3.2, 3.3, 3.4, 3.5_

- [x] 7.3 Configuration-driven policy system and timeouts (Task 2)

  - Implemented ToolPolicyConfig and load*tool_policy_config supporting YAML/JSON via TTA_TOOL_POLICY_CONFIG and environment fallbacks (TTA_ALLOWED_CALLABLES, TTA_ALLOW*\*, TTA_TOOL_TIMEOUT_MS, etc.)
  - ToolPolicy accepts config; added get_timeout_ms, is_capability_allowed, validate_safety_flags; maintained validate_callable_allowed and schema depth checks
  - Enforced timeouts in ToolCoordinator.run_tool (async via asyncio.wait_for; sync via thread join(timeout)); recorded metrics on timeouts
  - InvocationService validates safety flags and callable allowlist before execution; BaseTool.execute wired to central policy loader
  - Added docs/configs with README and sample YAML/JSON configurations

- [x] 7.4 Advanced test coverage for policy, metrics, and registry (Task 3)

  - KG-enabled tools testing with network policy enforcement (allow/deny)
  - Metrics for failure scenarios: exceptions, timeouts, policy violations; keys as {tool}:{version}
  - Registry idempotency with concurrent create_or_get and invocation
  - Policy enforcement matrix across safety flag combinations and policy booleans
  - All tests marked @pytest.mark.redis and aligned with project fixtures; execution times < 5s each

- [ ] 7.5 Policy config live-reload and diagnostics

  - Expose policy snapshot via diagnostics with redaction for sensitive fields
  - Implement optional live-reload on file change (watcher) with safe application semantics and audit logs
  - Add admin endpoint to trigger reload and validate config
  - Tests for diagnostics exposure and live-reload safety/rollback
  - _Requirements: 3.3, 4.5, 8.1_

Note: Integrate with existing agent registry patterns and project configuration/testing conventions. Proposed config (to be wired in Task 7 implementation):

```yaml
agent_orchestration:
  tools:
    redis_key_prefix: "ao" # reuse default prefix
    cache_ttl_s: 300 # LRU TTL for ToolSpec lookups
    cache_max_items: 512 # LRU capacity
    max_params: 16 # safety: cap total args
    max_schema_depth: 5 # safety: cap nesting
    allow_network_tools: false # security defaults
    allow_filesystem_tools: false
    max_idle_seconds: 86400 # prune tools unused for 24h
```

- [ ] 8. Build therapeutic safety validation system
- [ ] 8.1 Implement content safety validation pipeline

  - Write TherapeuticValidator class for content appropriateness checking
  - Implement safety rule engine with configurable therapeutic guidelines
  - Create content blocking and alternative generation request mechanisms
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ] 8.2 Add crisis intervention and emergency protocols

  - Code crisis detection algorithms for user input and agent responses
  - Implement emergency protocol activation and human oversight escalation
  - Write safety monitoring and alerting systems for therapeutic violations
  - _Requirements: 5.1, 5.2, 5.4, 5.5_

- [ ] 9. Develop comprehensive error handling system
- [ ] 9.1 Implement agent failure detection and recovery

  - Write agent health monitoring with automatic failure detection
  - Implement agent restart and fallback mechanisms
  - Create agent state preservation and restoration for recovery scenarios
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [ ] 9.2 Add workflow error handling and rollback

  - Code workflow failure detection and automatic rollback mechanisms
  - Implement workflow state consistency checking and repair
  - Write graceful degradation strategies for partial workflow failures
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 10. Create real-time interaction management
- [ ] 10.1 Implement WebSocket integration for real-time communication

  - Write WebSocket handler for real-time agent orchestration communication
  - Implement connection management and automatic reconnection logic
  - Create real-time status updates and progress reporting for users
  - _Requirements: 7.1, 7.2, 7.3, 7.5_

- [ ] 10.2 Add response time optimization and progressive feedback

  - Code response time monitoring and optimization algorithms
  - Implement progressive feedback mechanisms for long-running workflows
  - Write concurrent workflow management for multiple simultaneous users
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 11. Build configuration and extensibility system
- [x] 11.1 Implement configuration management for orchestration system

  - Implemented configuration loader for agent orchestration settings from tta_config.yaml
  - Added dynamic configuration parsing with memory string support ("4GB" -> bytes)
  - Created configuration validation and error handling for invalid settings
  - Integrated with TTA component system for lifecycle management
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [ ] 11.2 Add agent discovery and registration system

  - Code automatic agent discovery and registration mechanisms
  - Implement agent capability advertisement and matching
  - Write backward compatibility support for existing agent implementations
  - _Requirements: 8.1, 8.2, 8.5_

- [x] 12. Implement comprehensive testing suite
- [x] 12.1 Create unit tests for core orchestration components

  - Implemented unit tests for WorkflowManager with mock agent implementations
  - Created unit tests for MessageCoordinator with message delivery validation
  - Added unit tests for ResourceManager with resource allocation testing
  - Implemented tests for data models, messaging, and performance tracking
  - _Requirements: All requirements - testing coverage_

- [ ] 12.2 Build integration tests for multi-agent workflows

  - Code integration tests for complete IPA → WBA → NGA workflows
  - Write integration tests for error handling and recovery scenarios
  - Implement performance tests for concurrent workflow execution
  - _Requirements: All requirements - integration testing_

- [x] 13. Create monitoring and observability features
- [x] 13.1 Implement performance metrics collection and reporting

  - Implemented metrics collection for workflow execution times and success rates
  - Added resource utilization monitoring and reporting via diagnostics endpoints
  - Created alerting system for performance degradation and failures with configurable thresholds
  - Integrated Prometheus metrics export for external monitoring systems
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 13.2 Add logging and debugging capabilities

  - Implemented comprehensive logging for agent interactions and workflow execution
  - Added debugging tools via diagnostics endpoints for workflow inspection
  - Created audit trails for message delivery and failure tracking
  - Integrated with TTA logging system for consistent log management
  - _Requirements: 4.5, 5.4, 6.1, 6.2_

- [x] 14. Integration with existing TTA components
- [x] 14.1 Integrate with Neo4j knowledge graph system

  - Integrated with TTA component system declaring Neo4j as dependency
  - Added foundation for agent context and workflow state persistence
  - Created extension points for knowledge graph updates from orchestration activities
  - Prepared knowledge retrieval mechanisms for agent context enrichment
  - _Requirements: 1.1, 1.2, 2.1, 5.1_

- [x] 14.2 Connect with existing LLM and component systems

  - Integrated with existing TTA component lifecycle and configuration system
  - Connected with Redis for message coordination and state management
  - Implemented component lifecycle integration with TTA orchestration system
  - Added foundation for carbon tracking integration via component system
  - _Requirements: 1.1, 4.1, 8.1_

- [x] 15. Deploy and validate complete orchestration system
- [x] 15.1 Create deployment configuration and Docker integration

  - Integrated agent orchestration component with TTA component system
  - Implemented service discovery and health checking via diagnostics endpoints
  - Added configuration validation and component lifecycle management
  - Created deployment integration through existing TTA orchestration system
  - _Requirements: 8.1, 8.2, 8.5_

- [ ] 15.2 Conduct end-to-end system validation
  - Code end-to-end tests for complete therapeutic workflow orchestration
  - Write performance validation tests meeting 2-second response time requirements
  - Implement therapeutic safety validation for complete agent coordination
  - _Requirements: All requirements - final validation_

## High Priority Remaining Tasks

- [ ] 16. Complete core agent integration
- [ ] 16.1 Implement AgentOrchestrationService main API

  - Create main orchestration service class with process_user_input method
  - Implement coordinate_agents method for workflow execution
  - Add session context management and therapeutic safety integration
  - Wire together WorkflowManager, MessageCoordinator, and ResourceManager
  - _Requirements: 1.1, 1.2, 1.3, 5.1_

- [ ] 16.2 Build concrete agent proxy implementations

  - Implement InputProcessorAgentProxy with actual IPA integration
  - Create WorldBuilderAgentProxy with WBA communication protocols
  - Build NarrativeGeneratorAgentProxy with NGA workflow integration
  - Add agent health monitoring and failure detection
  - _Requirements: 1.1, 1.2, 2.1, 6.1, 6.2_

- [ ] 17. Implement therapeutic safety validation system
- [ ] 17.1 Create TherapeuticValidator for content safety

  - Implement content appropriateness checking algorithms
  - Add safety rule engine with configurable therapeutic guidelines
  - Create content blocking and alternative generation mechanisms
  - Integrate with existing therapeutic safety components
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ] 17.2 Add crisis intervention and emergency protocols

  - Implement crisis detection for user input and agent responses
  - Add emergency protocol activation and human oversight escalation
  - Create safety monitoring and alerting for therapeutic violations
  - Integrate with existing therapeutic monitoring systems
  - _Requirements: 5.1, 5.2, 5.4, 5.5_

- [ ] 18. Build dynamic tool system integration
- [ ] 18.1 Implement ToolCoordinator for dynamic tool management

  - Create tool coordination and sharing mechanisms between agents
  - Implement tool validation and safety checking for agent tools
  - Add tool registry and lifecycle management for shared tools
  - Integrate with existing dynamic tool system components
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ] 18.2 Add tool optimization and resource management

  - Implement tool caching to prevent redundant tool generation
  - Add tool performance monitoring and optimization
  - Create tool cleanup and resource management for unused tools
  - Integrate with ResourceManager for tool resource allocation
  - _Requirements: 3.2, 3.3, 3.4, 3.5_

- [ ] 19. Implement real-time interaction management
- [ ] 19.1 Add WebSocket integration for real-time communication

  - Implement WebSocket handler for real-time orchestration communication
  - Add connection management and automatic reconnection logic
  - Create real-time status updates and progress reporting
  - Integrate with existing TTA WebSocket infrastructure
  - _Requirements: 7.1, 7.2, 7.3, 7.5_

- [ ] 19.2 Optimize response times and progressive feedback

  - Implement response time monitoring and optimization algorithms
  - Add progressive feedback mechanisms for long-running workflows
  - Create concurrent workflow management for multiple users
  - Optimize agent coordination for sub-2-second response times
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

## 6. Enhancements and Operations Notes (Completed + Future)

### Completed in 6.x

- Redis-backed AgentRegistry with heartbeat-based liveness (ttl/interval configurable)
- Auto-registration of proxies (IPA, WBA, NGA) with per-agent instance naming (explicit or generated unique defaults)
- Diagnostics /agents endpoint with derived per-instance performance metrics (p50, p95, avg, error_rate) and last_heartbeat_age
- Deregistration of locally registered agents on controlled shutdown to avoid "ghost" agents

### Configuration (documented)

- agent_orchestration.agents.heartbeat_ttl: float seconds (default: 30.0)
- agent_orchestration.agents.heartbeat_interval: float seconds (default: ttl/3)
- agent_orchestration.agents.auto_register: bool (default: false)
- agent_orchestration.agents.{ipa|wba|nga}.enabled: bool (default: false)
- agent_orchestration.agents.{ipa|wba|nga}.instance: string (optional explicit instance name)

Example:

```yaml
agent_orchestration:
  diagnostics:
    enabled: true
  agents:
    auto_register: true
    heartbeat_ttl: 30.0
    heartbeat_interval: 10.0
    ipa:
      enabled: true
      instance: "worker-1"
    wba:
      enabled: true
    nga:
      enabled: true
```

### Future enhancements (planned)

- Per-agent multi-instance auto-registration (array support):

  ```yaml
  agent_orchestration:
    agents:
      ipa:
        enabled: true
        instances: ["a", "b", "c"]
      wba:
        enabled: true
        instances: ["w1"]
      nga:
        enabled: true
        instances: []
  ```

  - Auto-register one proxy per listed instance; continue to generate unique defaults when not provided.

- Resource recommendations per instance (to feed ResourceManager decisions in future):
  ```yaml
  agent_orchestration:
    agents:
      ipa:
        instances:
          - name: "a"
            resources:
              cpu_threads: 2
              ram_bytes: 536870912 # 512MB
          - name: "b"
            resources:
              cpu_threads: 1
      # same for wba, nga
  ```

## 6. Validation and Completeness Review

- Requirements coverage:
  - 6.1: 1.1 (agent communication), 2.1 (orchestration), 8.1 (monitoring), 8.2 (reliability) — satisfied via base Agent, registries (in-memory + Redis), diagnostics integration, timeouts/errors, health checks.
  - 6.2: 1.1 (communication), 1.2 (integration), 2.1 (orchestration), 3.1 (narrative flow) — satisfied via InputProcessorAgentProxy, WorldBuilderAgentProxy, NarrativeGeneratorAgentProxy.
- Deliverables implemented:
  - Base Agent class, AgentRegistry, RedisAgentRegistry with TTL/interval config
  - Auto-registration (config-gated) with per-agent instance naming or unique defaults
  - Diagnostics /agents endpoint with performance metrics and heartbeat ages
  - Three proxies implemented with sync/async support, validation, caching, filtering
- Testing status:
  - Unit tests cover Agent lifecycle/timeout/retry/cache/filtering
  - Redis-marked tests cover RedisAgentRegistry persistence, heartbeats, deregistration, and diagnostics /agents + auto-registration
  - All tests passing under project Redis fixtures/markers
- Known gaps (acceptable for Task 6 scope):
  - Multi-instance auto-registration array support (specified above) not yet implemented
  - Per-instance resource recommendations accepted in config but not enforced (future integration with ResourceManager)
  - Real agent backends (IPA/WBA/NGA integration) deferred to Task 16
