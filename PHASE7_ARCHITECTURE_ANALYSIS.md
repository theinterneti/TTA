# Phase 7 Task Execution & Monitoring Architecture Analysis

## Executive Summary

**CRITICAL FINDING**: The current architecture has a fundamental design flaw that prevents continuous monitoring from working. Each Python process creates its own isolated `ExecutionEngine` instance with its own in-memory `TaskQueue`. There is **NO inter-process communication (IPC)** or **shared state mechanism** between processes.

**Result**: Tasks submitted to one engine instance are invisible to other engine instances, making monitoring impossible with the current design.

---

## 1. Execution Engine Architecture

### 1.1 Task Queue Storage (In-Memory Only)

**File**: `src/agent_orchestration/openhands_integration/task_queue.py`

```python
class TaskQueue:
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._queue: asyncio.PriorityQueue[tuple[int, QueuedTask]] = (
            asyncio.PriorityQueue(maxsize=max_size)  # ← IN-MEMORY ONLY
        )
        self._tasks: dict[str, QueuedTask] = {}  # ← IN-MEMORY ONLY
        self._lock = asyncio.Lock()
```

**Key Facts**:
- `asyncio.PriorityQueue` is an in-memory queue
- `_tasks` dict stores task metadata in memory
- No Redis, database, or file-based persistence
- No mechanism to share state across processes

### 1.2 Queue Isolation Across Processes

**File**: `src/agent_orchestration/openhands_integration/execution_engine.py`

```python
class ExecutionEngine:
    def __init__(self, config: OpenHandsConfig, ...):
        self.queue = TaskQueue(max_size=queue_size)  # ← NEW INSTANCE PER ENGINE
        # ... other initialization
```

**Key Facts**:
- Each `ExecutionEngine` instance creates its own `TaskQueue`
- Each Python process gets its own engine instance
- No shared queue across processes
- Each process has completely isolated task state

---

## 2. Task Submission Flow - The Root Cause

### 2.1 CLI Command: `run-engine`

**File**: `src/agent_orchestration/openhands_integration/cli.py:179-201`

```python
@cli.command()
def run_engine(workers: int, duration: int) -> None:
    """Run execution engine."""
    integration_config = OpenHandsIntegrationConfig.from_env()
    config = OpenHandsConfig(...)
    engine = ExecutionEngine(config, max_concurrent_tasks=workers)  # ← ENGINE #1
    
    async def run():
        await engine.start()
        click.echo(f"Engine running with {workers} workers for {duration}s")
        await asyncio.sleep(duration)
        await engine.stop()
    
    asyncio.run(run())
```

**What Happens**:
1. Creates ENGINE #1 with its own TaskQueue
2. Starts 5 workers that process tasks from ENGINE #1's queue
3. Runs for 3600 seconds
4. Workers only see tasks in ENGINE #1's queue

### 2.2 Task Submission: `submit_task` CLI Command

**File**: `src/agent_orchestration/openhands_integration/cli.py:51-102`

```python
@cli.command()
def submit_task(...) -> None:
    """Submit a task for execution."""
    integration_config = OpenHandsIntegrationConfig.from_env()
    config = OpenHandsConfig(...)
    engine = ExecutionEngine(config)  # ← ENGINE #2 (DIFFERENT INSTANCE!)
    
    async def run():
        await engine.start()
        task_id = await engine.submit_task(task)  # ← ADDS TO ENGINE #2's QUEUE
        click.echo(f"Task submitted: {task_id}")
        await engine.stop()
    
    asyncio.run(run())
```

**What Happens**:
1. Creates ENGINE #2 (completely separate from ENGINE #1)
2. Adds task to ENGINE #2's queue
3. Immediately stops ENGINE #2
4. Task is lost when ENGINE #2 exits
5. ENGINE #1 never sees this task

### 2.3 Monitoring: `queue_stats` CLI Command

**File**: `src/agent_orchestration/openhands_integration/cli.py:133-153`

```python
@cli.command()
def queue_stats() -> None:
    """Get queue statistics."""
    integration_config = OpenHandsIntegrationConfig.from_env()
    config = OpenHandsConfig(...)
    engine = ExecutionEngine(config)  # ← ENGINE #3 (ANOTHER DIFFERENT INSTANCE!)
    
    async def run():
        stats = await engine.get_queue_stats()  # ← QUERIES ENGINE #3's EMPTY QUEUE
        click.echo(json.dumps(stats, indent=2))
    
    asyncio.run(run())
```

**What Happens**:
1. Creates ENGINE #3 (completely separate from ENGINE #1 and #2)
2. Queries ENGINE #3's queue (which is always empty)
3. Returns 0 tasks, 0 completed, 0 failed
4. Never queries ENGINE #1 (the running engine)

---

## 3. Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ PROCESS 1: run-engine (PID 7076)                               │
│ ┌──────────────────────────────────────────────────────────┐   │
│ │ ExecutionEngine #1                                       │   │
│ │ ┌────────────────────────────────────────────────────┐   │   │
│ │ │ TaskQueue #1 (IN-MEMORY)                           │   │   │
│ │ │ - _queue: asyncio.PriorityQueue                    │   │   │
│ │ │ - _tasks: {task_id: QueuedTask, ...}              │   │   │
│ │ │ - 41 tasks queued                                  │   │   │
│ │ └────────────────────────────────────────────────────┘   │   │
│ │ Workers: 5 (processing tasks from TaskQueue #1)         │   │
│ └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↑
                              │ (ISOLATED - NO IPC)
                              │
┌─────────────────────────────────────────────────────────────────┐
│ PROCESS 2: phase7_submit_to_running_engine.py                  │
│ ┌──────────────────────────────────────────────────────────┐   │
│ │ ExecutionEngine #2 (TEMPORARY)                           │   │
│ │ ┌────────────────────────────────────────────────────┐   │   │
│ │ │ TaskQueue #2 (IN-MEMORY)                           │   │   │
│ │ │ - 41 tasks added here                              │   │   │
│ │ │ - Process exits → Queue destroyed                  │   │   │
│ │ └────────────────────────────────────────────────────┘   │   │
│ └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↑
                              │ (ISOLATED - NO IPC)
                              │
┌─────────────────────────────────────────────────────────────────┐
│ PROCESS 3: phase7_monitor_progress.py                          │
│ ┌──────────────────────────────────────────────────────────┐   │
│ │ ExecutionEngine #3 (TEMPORARY)                           │   │
│ │ ┌────────────────────────────────────────────────────┐   │   │
│ │ │ TaskQueue #3 (IN-MEMORY, EMPTY)                    │   │   │
│ │ │ - 0 tasks (never sees tasks from #1 or #2)        │   │   │
│ │ └────────────────────────────────────────────────────┘   │   │
│ └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Why Monitoring Returns Zero Tasks

1. **Monitoring script calls**: `python -m src.agent_orchestration.openhands_integration.cli queue-stats`
2. **CLI creates**: New ExecutionEngine #3 with empty TaskQueue #3
3. **Queries**: TaskQueue #3 (which has 0 tasks)
4. **Returns**: `{"total_tasks": 0, "queued": 0, ...}`
5. **Never queries**: ExecutionEngine #1 (the running engine with 41 tasks)

**Result**: Monitoring always shows 0 tasks, even though ENGINE #1 has 41 tasks queued.

---

## 5. Root Cause Summary

| Component | Current | Problem |
|-----------|---------|---------|
| Queue Storage | In-memory asyncio.PriorityQueue | Not shared across processes |
| Engine Instances | One per process | No IPC between engines |
| Task Submission | Creates new engine, adds task, exits | Task lost when process exits |
| Monitoring | Creates new engine, queries empty queue | Never sees running engine's tasks |
| State Persistence | None | No way to recover state |

---

## 6. Why This Happened

The Phase 6 documentation mentions:
> "Redis integration for persistent queue" as a Phase 8 feature

The current implementation was designed for **single-process execution** where one engine runs and processes tasks. It was **not designed for multi-process task submission and monitoring**.

---

## 7. Proposed Solutions

### Solution A: Shared File-Based Queue (Minimal Change)
- Write queue state to JSON file periodically
- All processes read/write to same file
- Pros: Simple, no external dependencies
- Cons: Not atomic, potential race conditions

### Solution B: Redis-Based Queue (Proper Solution)
- Move TaskQueue to use Redis instead of asyncio.PriorityQueue
- All processes share same Redis queue
- Pros: Atomic, scalable, persistent
- Cons: Requires Redis, more complex

### Solution C: Single Engine Process with IPC (Hybrid)
- Keep ENGINE #1 running
- Submit tasks via file/socket to ENGINE #1
- Monitor ENGINE #1's state via file/socket
- Pros: Works with current code, minimal changes
- Cons: Requires IPC mechanism

### Solution D: Modify CLI to Connect to Running Engine (Quick Fix)
- Detect if engine is already running
- Connect to existing engine instead of creating new one
- Pros: Minimal code changes
- Cons: Requires process discovery mechanism

---

## 8. Recommended Immediate Fix

**Use Solution C + File-Based State Export**:

1. Modify ExecutionEngine to periodically write queue state to file
2. Modify CLI commands to read from file instead of creating new engine
3. Implement simple file-based task submission queue
4. This bridges the gap until Redis integration (Phase 8)

**Implementation**:
- Add `_state_file` to ExecutionEngine
- Periodically write `get_queue_stats()` to file
- Modify CLI to read from state file
- Create file-based task submission mechanism

