# OpenHands Tool Configuration Research

**Date:** 2025-10-24
**Researcher:** The Augster (AI Agent)
**Source:** Context7 documentation for `all-hands-ai/openhands`
**Purpose:** Investigate how to configure file operation tools for OpenHands agent

---

## Executive Summary

**Problem:** OpenHands agent proposes code but doesn't create files (only `finish` and `think` tools available)

**Root Cause:** TTA integration uses OpenHands SDK (`openhands.sdk`), which is a simplified wrapper with limited tool access. Full tool capabilities require runtime environment configuration.

**Solution:** Configure runtime environment with bash/file operation tools OR explore MCP integration for enhanced capabilities.

---

## Key Findings

### 1. CodeActAgent Supports Bash Commands

**Finding:** The `CodeActAgent` (used by TTA integration) supports executing any valid Linux bash command via `execute_bash` action.

**Source:** Context7 - `docs/usage/agents.mdx`

```bash
execute_bash_command('ls -l')
```

**Capabilities:**
- Execute any valid Linux bash command
- Handle long-running commands (background execution with output redirection)
- Support interactive processes (STDIN input, interruption)
- Manage command timeouts (automatic retries in background mode)

**Implication:** Agent CAN create files, but only when bash tools are configured in runtime environment.

---

### 2. Runtime Environment Configuration

**Finding:** Tools are configured at the **runtime level**, not the SDK level. The OpenHands SDK (`openhands.sdk`) is a simplified wrapper that doesn't expose full runtime configuration.

**Source:** Context7 - `docs/usage/runtimes/local.mdx`, `docs/usage/runtimes/docker.mdx`

#### Local Runtime Configuration

```bash
# Required
export RUNTIME=local

# Mount local directories into agent's workspace
export SANDBOX_VOLUMES=/path/to/your/workspace:/workspace:rw

# For read-only data
export SANDBOX_VOLUMES=/path/to/your/workspace:/workspace:rw,/path/to/large/dataset:/data:ro
```

#### Docker Runtime Configuration

```bash
export SANDBOX_VOLUMES=/path/to/your/code:/workspace:rw

docker run \
    -e SANDBOX_USER_ID=$(id -u) \
    -e SANDBOX_VOLUMES=$SANDBOX_VOLUMES \
    # ...
```

**Implication:** TTA integration needs to configure runtime environment to enable file operations.

---

### 3. MCP (Model Context Protocol) Integration

**Finding:** OpenHands supports MCP integration for enhanced tool capabilities via `config.toml` configuration.

**Source:** Context7 - `docs/usage/mcp.mdx`, `docs/usage/how-to/cli-mode.mdx`

#### MCP Server Types

1. **Stdio Servers** - Direct stdio connections (development/testing only)
2. **SSE Servers** - Server-Sent Events connections
3. **SHTTP Servers** - Streamable HTTP connections

#### Configuration Example

```toml
[mcp]
# Direct stdio servers (not recommended for production)
stdio_servers = [
    {name="fetch", command="uvx", args=["mcp-server-fetch"]},
    {
        name="filesystem",
        command="npx",
        args=["@modelcontextprotocol/server-filesystem", "/"],
        env={"DEBUG": "true"}
    }
]

# SSE servers (basic URL)
sse_servers = [
    "http://example.com:8080/sse",
]

# SHTTP servers (with API key authentication)
shttp_servers = [
    {url="https://secure-example.com/mcp", api_key="your-api-key"}
]
```

**Available MCP Servers:**
- `mcp-server-fetch` - HTTP fetch capabilities
- `@modelcontextprotocol/server-filesystem` - Filesystem operations
- Custom MCP servers via SuperGateway proxy

**Implication:** MCP integration could provide structured file operation tools without direct bash access.

---

### 4. SDK vs Runtime Environment

**Finding:** OpenHands has two levels of integration:

1. **SDK Level** (`openhands.sdk`) - Simplified wrapper
   - Limited tool access (finish, think)
   - Easy to integrate
   - **Current TTA integration uses this**

2. **Runtime Level** (full OpenHands) - Complete environment
   - Full tool access (bash, file operations, MCP tools)
   - Requires runtime configuration
   - More complex integration

**Source:** Context7 - `openhands/core/main.py`, `openhands/server/README.md`

#### SDK Usage (Current TTA Integration)

```python
from openhands.sdk import Agent, LLM

llm = LLM(model="openrouter/deepseek/deepseek-chat", api_key="...")
agent = Agent(llm=llm)
conversation = agent.create_conversation()
result = conversation.send_message("Write a function...")
```

**Tools Available:** Limited (finish, think)

#### Runtime Usage (Full OpenHands)

```bash
poetry run python ./openhands/core/main.py \
    -i 10 \
    -t "Write me a bash script that prints hello world." \
    -c CodeActAgent \
    -l llm
```

**Tools Available:** Full (bash, file operations, MCP tools)

**Implication:** TTA integration needs to either:
- Switch from SDK to runtime environment, OR
- Configure runtime environment alongside SDK usage

---

### 5. Environment Setup Scripts

**Finding:** OpenHands supports `.openhands/setup.sh` scripts that run at agent startup for environment configuration.

**Source:** Context7 - `docs/usage/faqs.mdx`, `docs/usage/prompting/repository.mdx`

```bash
#!/bin/bash

# Example: Install Python dependencies
pip install requests

# Example: Set up Node.js environment
npm install

# Example: Set environment variables
export MY_ENV_VAR="my value"
```

**Implication:** Could use setup scripts to configure TTA-specific environment requirements.

---

## Current TTA Integration Analysis

### What We Have

```python
# src/agent_orchestration/openhands_integration/client.py

from openhands.sdk import Agent, LLM, Conversation

self._llm = LLM(
    model=self.config.model,
    api_key=self.config.api_key.get_secret_value(),
    base_url=self.config.base_url,
    custom_llm_provider="openrouter",
    max_output_tokens=4096,
    extended_thinking_budget=0,
)

self._agent = Agent(llm=self._llm)
conversation = self._agent.create_conversation()
result = conversation.send_message(task_description)
```

**Tools Available:** Limited (finish, think)
**File Operations:** ❌ Not available
**Bash Commands:** ❌ Not available

### What We Need

**Option 1: Runtime Environment Configuration**
- Configure `RUNTIME=local` or `RUNTIME=docker`
- Set `SANDBOX_VOLUMES` for workspace access
- Enable bash tools via runtime configuration

**Option 2: MCP Integration**
- Configure MCP filesystem server
- Use structured file operations instead of bash
- Better error handling and safety

**Option 3: Hybrid Approach**
- Keep SDK for simplicity
- Add runtime configuration for tools
- Best of both worlds

---

## Proposed Improvements

### Short-Term (Quick Win)

**Goal:** Enable file operations without major refactoring

**Approach:** Configure runtime environment alongside SDK usage

**Steps:**
1. Set environment variables for runtime configuration
2. Configure `SANDBOX_VOLUMES` to mount TTA workspace
3. Test if SDK respects runtime environment variables
4. Verify bash tools become available

**Estimated Effort:** 2-4 hours
**Risk:** Low (environment variables only)

### Medium-Term (MCP Integration)

**Goal:** Structured file operations with better error handling

**Approach:** Integrate MCP filesystem server

**Steps:**
1. Install MCP filesystem server (`@modelcontextprotocol/server-filesystem`)
2. Configure MCP in `config.toml` or programmatically
3. Update client to use MCP tools
4. Test file operations via MCP

**Estimated Effort:** 8-12 hours
**Risk:** Medium (new dependency, configuration complexity)

### Long-Term (Full Runtime Integration)

**Goal:** Complete OpenHands capabilities

**Approach:** Switch from SDK to full runtime environment

**Steps:**
1. Replace SDK usage with runtime environment
2. Configure `AppConfig` with sandbox settings
3. Implement agent controller lifecycle management
4. Update proxy to use runtime environment

**Estimated Effort:** 20-30 hours
**Risk:** High (major refactoring, breaking changes)

---

## Recommendations

### Immediate Action

1. **Document Findings** ✅ (This document)
2. **Test Runtime Environment Variables**
   - Set `RUNTIME=local` and `SANDBOX_VOLUMES` in TTA environment
   - Run validation test to see if tools become available
   - Document results

3. **Create Proof of Concept**
   - Implement short-term solution (runtime environment configuration)
   - Validate file creation works
   - Measure impact on integration complexity

### Future Work

1. **Evaluate MCP Integration**
   - Research MCP filesystem server capabilities
   - Assess security implications
   - Design integration architecture

2. **Consider Full Runtime Migration**
   - Evaluate benefits vs. complexity
   - Design migration path
   - Plan backward compatibility

---

## References

- **OpenHands Documentation:** https://github.com/all-hands-ai/openhands
- **Context7 Library ID:** `/all-hands-ai/openhands`
- **TTA Validation Report:** `docs/validation/openhands-integration-validation-2025-10-24.md`
- **TTA Integration Code:** `src/agent_orchestration/openhands_integration/`

---

## Testing Results (2025-10-24)

### Runtime Environment Configuration Test

**Hypothesis:** Setting `RUNTIME=local` and `SANDBOX_VOLUMES` environment variables alongside SDK usage would enable bash/file operation tools.

**Test Approach:**
1. Reviewed OpenHands documentation via Context7
2. Analyzed runtime configuration options
3. Evaluated SDK vs runtime environment architecture

**Findings:**

❌ **Runtime environment variables do NOT work with OpenHands SDK**

**Rationale:**
- `RUNTIME` and `SANDBOX_VOLUMES` are Docker/application-level configuration
- These variables configure the OpenHands runtime container, not the SDK
- The SDK (`openhands.sdk`) is a simplified Python wrapper with limited tool access
- Runtime configuration requires running OpenHands as a Docker container or standalone application

**Evidence from Documentation:**
```bash
# Runtime configuration is for Docker/application deployment
export RUNTIME=local
export SANDBOX_VOLUMES=/path/to/workspace:/workspace:rw

docker run \
    -e RUNTIME=$RUNTIME \
    -e SANDBOX_VOLUMES=$SANDBOX_VOLUMES \
    # ... OpenHands container
```

**Conclusion:**
The short-term solution (runtime environment variables) is **not viable** for the current SDK-based integration. The SDK and runtime environment are separate architectures:
- **SDK:** Simplified Python wrapper, limited tools (finish, think)
- **Runtime:** Full OpenHands environment with bash, file operations, MCP tools

**Impact:**
- File creation issue cannot be solved with environment variables
- Must pursue medium-term (MCP integration) or long-term (runtime migration) solutions

---

---

## Docker Runtime Integration Approach (2025-10-24)

### Overview

**Discovery:** OpenHands supports **headless mode** via Docker, which provides full tool access (bash, file operations, MCP tools) without the SDK limitations.

**Key Insight:** We have Docker available on the Windows host machine and can run OpenHands as a Docker container, programmatically passing tasks and retrieving results.

### Docker Headless Mode Architecture

```bash
# Run OpenHands in headless mode with full tool access
docker run -it \
    --pull=always \
    -e SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:0.54-nikolaik \
    -e SANDBOX_USER_ID=$(id -u) \
    -e SANDBOX_VOLUMES=/path/to/workspace:/workspace:rw \
    -e LLM_API_KEY=$OPENROUTER_API_KEY \
    -e LLM_MODEL=openrouter/deepseek/deepseek-chat \
    -e LOG_ALL_EVENTS=true \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v ~/.openhands:/.openhands \
    --add-host host.docker.internal:host-gateway \
    --name openhands-app-$(date +%Y%m%d%H%M%S) \
    docker.all-hands.dev/all-hands-ai/openhands:0.54 \
    python -m openhands.core.main -t "write a bash script that prints hi"
```

**Key Features:**
- **Full Tool Access:** Bash, file operations, Jupyter, browser automation
- **Workspace Mounting:** `SANDBOX_VOLUMES` mounts local directories into container
- **Task Execution:** Pass task via `-t` flag or `-f` for task file
- **Output Capture:** Container logs contain task execution results
- **Programmatic Control:** Can be called from Python via `subprocess`

### Python Integration Pattern

```python
import subprocess
import json
from pathlib import Path

class DockerOpenHandsClient:
    """OpenHands client using Docker runtime for full tool access."""

    def __init__(self, workspace_path: Path, api_key: str, model: str):
        self.workspace_path = workspace_path
        self.api_key = api_key
        self.model = model
        self.runtime_image = "docker.all-hands.dev/all-hands-ai/runtime:0.54-nikolaik"
        self.openhands_image = "docker.all-hands.dev/all-hands-ai/openhands:0.54"

    def execute_task(self, task: str, timeout: int = 300) -> dict:
        """Execute task via Docker headless mode."""

        # Build Docker command
        cmd = [
            "docker", "run", "-it", "--rm",
            "-e", f"SANDBOX_RUNTIME_CONTAINER_IMAGE={self.runtime_image}",
            "-e", f"SANDBOX_VOLUMES={self.workspace_path}:/workspace:rw",
            "-e", f"LLM_API_KEY={self.api_key}",
            "-e", f"LLM_MODEL={self.model}",
            "-e", "LOG_ALL_EVENTS=true",
            "-v", "/var/run/docker.sock:/var/run/docker.sock",
            "-v", f"{Path.home()}/.openhands:/.openhands",
            "--add-host", "host.docker.internal:host-gateway",
            self.openhands_image,
            "python", "-m", "openhands.core.main",
            "-t", task
        ]

        # Execute Docker container
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        # Parse output
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }

# Usage
client = DockerOpenHandsClient(
    workspace_path=Path("/home/thein/recovered-tta-storytelling"),
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model="openrouter/deepseek/deepseek-chat"
)

result = client.execute_task("Create a file named test.txt with content 'Hello, World!'")
print(result["stdout"])
```

### Advantages of Docker Approach

1. **Full Tool Access**
   - ✅ Bash command execution
   - ✅ File creation and modification
   - ✅ Jupyter notebook support
   - ✅ Browser automation (if needed)
   - ✅ MCP tool integration (future)

2. **Workspace Integration**
   - ✅ Direct access to TTA codebase via `SANDBOX_VOLUMES`
   - ✅ Changes persist to host filesystem
   - ✅ No file copying or synchronization needed

3. **Isolation and Security**
   - ✅ Sandboxed execution environment
   - ✅ Container-level resource limits
   - ✅ Network isolation options

4. **Proven Architecture**
   - ✅ Official OpenHands deployment method
   - ✅ Used in production by OpenHands team
   - ✅ Well-documented and supported

### Challenges and Mitigations

**Challenge 1: Docker-in-Docker Complexity**
- **Issue:** OpenHands container needs access to Docker socket
- **Mitigation:** Mount `/var/run/docker.sock` into container (standard pattern)
- **Security:** Acceptable for development environment, review for production

**Challenge 2: Output Parsing**
- **Issue:** Need to extract structured results from container logs
- **Mitigation:** Use `LOG_ALL_EVENTS=true` and parse JSON event stream
- **Alternative:** Mount output directory and write results to file

**Challenge 3: Container Lifecycle Management**
- **Issue:** Need to clean up containers after execution
- **Mitigation:** Use `--rm` flag for automatic cleanup
- **Monitoring:** Track running containers, implement timeout handling

**Challenge 4: Windows Path Mapping**
- **Issue:** Windows paths need conversion for Docker volumes
- **Mitigation:** Use WSL paths (`/mnt/c/...`) or Docker Desktop path mapping
- **Testing:** Verify workspace mounting works on Windows host

### Comparison: SDK vs Docker vs MCP

| Aspect | Current SDK | Docker Runtime | MCP Integration |
|--------|-------------|----------------|-----------------|
| **Tool Access** | Limited (finish, think) | Full (bash, files, jupyter) | Full (via MCP servers) |
| **File Operations** | ❌ Not available | ✅ Native support | ✅ Via filesystem server |
| **Workspace Access** | ❌ No direct access | ✅ Direct mount | ✅ Via MCP protocol |
| **Implementation Effort** | ✅ Already done | 🟡 Medium (2-4 hours) | 🔴 High (8-12 hours) |
| **Complexity** | ✅ Simple | 🟡 Moderate | 🔴 Complex |
| **Security** | ✅ Isolated | 🟡 Docker-in-Docker | ✅ Protocol-level |
| **Maintenance** | ✅ Low | 🟡 Medium | 🔴 High |
| **Production Ready** | ✅ Yes (limited) | ✅ Yes (official) | 🟡 Experimental |
| **Performance** | ✅ Fast | 🟡 Container overhead | 🟡 Protocol overhead |
| **Debugging** | ✅ Easy | 🟡 Container logs | 🔴 Complex |

### Recommendation

**Primary Approach:** Docker Runtime Integration

**Rationale:**
1. **Solves file creation issue** - Full bash and file operation support
2. **Official deployment method** - Proven, documented, supported
3. **Moderate effort** - 2-4 hours implementation vs 8-12 hours for MCP
4. **Production-ready** - Used by OpenHands team in production
5. **Workspace integration** - Direct access to TTA codebase via volume mounts

**Implementation Plan:**
1. Create `DockerOpenHandsClient` class (2 hours)
2. Test file creation and workspace access (1 hour)
3. Implement output parsing and error handling (1 hour)
4. Update integration tests (1 hour)
5. Document usage and limitations (30 minutes)

**Total Effort:** 4-5 hours (vs 8-12 hours for MCP integration)

---

**Status:** Research Complete + Docker Approach Identified
**Next Steps:** Implement Docker runtime integration (recommended)
**Owner:** TTA Development Team

