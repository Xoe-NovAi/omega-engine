<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 P4 Integration Implementation Plan
## Autonomous Meditation Pipeline — Complete Product Integration

**AP Token**: `AP-P4-INTEGRATION-PLAN-20260719`
⬡ OMEGA ⬡ PILLAR ⬡ P4 ⬡ INTEGRATION ⬡ trc_p4_integration_plan ⬡ ACTIVE

**Date**: 2026-07-19
**Author**: Pillar P4 — Integration (Bridge — MCP & Communication)
**Mission**: Deliver the **OpenCode slash command, global skill system, MCP Hub wiring, agent permissions, compaction resilience, and cross-platform communication** for the Autonomous Meditation Pipeline as a complete product.

---

## 📊 Current State Analysis

### ✅ What Exists (Assets)
| Asset | Location | Status | Notes |
|-------|----------|--------|-------|
| Core Pipeline Engine | `src/omega/skills/autonomous_meditation_pipeline.py` | ✅ Complete | Platform-agnostic, M16 compliant, DI pattern |
| Standalone Package | `packages/omega-meditation/` | ✅ Complete | CLI entry points, `pyproject.toml` |
| MCP Hub Server | `mcp_servers/omega_hub/server.py` | ✅ Running | FastMCP + Streamable HTTP on :8016/mcp |
| MCP Hub Tools | `mcp_servers/omega_hub/tools.py` | ✅ 50+ tools | `oracle_talk`, `library_web_search`, `sovereign_search`, etc. |
| MCP Client Adapter | `src/omega/skills/opencode_client.py` | ✅ Complete | `SovereignMCPClient` + `OpenCodePlatformClients` |
| Meditate Command | `.opencode/commands/meditate.md` | ✅ Complete | Full protocol with Kali host |
| Research Pipeline Skill | `.opencode/skills/meditate-research-pipeline/` | ✅ Complete | 5-stage skill with quality gates |
| Autonomous Pipeline Skill | `.opencode/skills/autonomous-meditation-pipeline/` | ✅ Complete | 7-stage fully autonomous skill |
| OpenCode Config | `opencode.json` | ✅ Partial | MCP servers configured, **permissions missing** |
| P1 Infrastructure Plan | `data/coordination/P1_INFRASTRUCTURE_PLAN_20260719.md` | ✅ Complete | 6 phases, ~24 hours |
| P3 Engineering Plan | `data/coordination/P3_ENGINEERING_PLAN_20260719.md` | ✅ Complete | 8 phases, ~29 hours |

### ❌ Critical Gaps (P4 Ownership)
| # | Gap | Impact | Priority | Owner |
|---|-----|--------|----------|-------|
| 1 | **No `/omega-meditation` slash command** | Users can't invoke pipeline directly | **P0** | P4 |
| 2 | **Skill triggers not defined** | No automatic pipeline execution | **P0** | P4 |
| 3 | **MCP Hub tool wiring broken** | Pipeline returns dry-run templates, not real data | **P0** | P4 + P3 |
| 4 | **Agent permissions for `skill` tool not configured** | Agents can't invoke skills | **P0** | P4 |
| 5 | **Global skill install path not set up** | Skills not discoverable by OpenCode | **P0** | P4 |
| 6 | **No compaction resilience plugin** | Session state lost on compaction | **P1** | P4 + P1 |
| 7 | **MCP Hub health/ready endpoints missing** | Container orchestration can't verify health | **P1** | P4 |
| 8 | **MCP protocol compliance (D-284)** | Streamable HTTP + PKCE auth needed | **P1** | P4 |
| 9 | **Cross-platform communication unverified** | CLI/Standalone/OpenCode modes untested | **P1** | P4 |

---

## 🏗️ Phase Breakdown

### Phase 0: Foundation & Verification (2 hours) — **MUST COMPLETE FIRST**
*Dependencies: None. All subsequent phases depend on this.*

| Task | File/Command | Verification |
|------|--------------|--------------|
| 0.1 Verify package builds | `cd packages/omega-meditation && uv build` | `dist/*.whl` created |
| 0.2 Verify CLI dry-run works | `uv run omega-meditation "test" --dry-run --mode standalone` | Stages 0-7 complete |
| 0.3 Verify MCP Hub tools return real data | `python -c "from mcp_servers.omega_hub.mcp_client import SovereignMCPClient; import anyio; c=SovereignMCPClient('http://127.0.0.1:8016/mcp'); anyio.run(lambda: c.__aenter__().call_tool('oracle_talk', {'query': 'test'}))"` | Returns JSON with `text`, `entity`, `backend` |
| 0.4 Check OpenCode config structure | `cat opencode.json \| jq '.mcp, .permission'` | MCP servers + permissions visible |
| 0.5 Create workspace lock | `omega-hub_hivemind_workspace_lock_acquire channel=opencode entity=pillar domain=P4_INTEGRATION_PLAN ttl=7200` | Lock acquired |

**Risk**: If MCP Hub tools return dry-run templates, root cause is `_require_service()` guard or `oracle` singleton not initialized. Must debug before Phase 1.

---

### Phase 1: OpenCode Slash Command & Skill System (4 hours)
*Dependencies: Phase 0 complete*

#### 1.1 Slash Command Definition
**File to create**: `.opencode/commands/omega-meditation.md`

```markdown
---
description: Autonomous Meditation Pipeline — Problem → Architecture → Research → Gnosis → Integration
agent: kali
subtask: false
---

# ⬡ OMEGA MEDITATION — Autonomous Pipeline
**Protocol**: `AutonomousMeditation-v1.0` | **Heritage**: Omega Engine Meditation Protocol + Sovereign Search
**Mechanism**: 7-stage autonomous pipeline (Prompt Craft → Meditate → Synthesize → Research → Ground → Gnosis → Integrate)

## Usage
```
/omega-meditation "Your problem statement here"
/omega-meditation "Problem" --mode cli
/omega-meditation "Problem" --resume-from 3
/omega-meditation "Problem" --dry-run
```

## Arguments
- **Problem statement** (required): The problem to process through the pipeline
- `--mode`: `opencode` (default, uses MCP Hub), `cli` (subprocess), `standalone` (dry-run)
- `--resume-from`: Stage number 0-7 to resume from
- `--dry-run`: Execute without external calls
- `--output-dir`: Custom output directory

## Pipeline Stages
| Stage | Name | Agent | Output |
|-------|------|-------|--------|
| 0 | Prompt Crafting | Self | Crafted `/meditate` prompt with lens rationale |
| 1 | Meditation Execution | Kali (via `/meditate`) | Raw multi-persona output |
| 2 | Intuitive Synthesis | Kali | Architecture, non-negotiables, MVP, metrics |
| 3 | Research Prompt Crafting | Self | Tiered search queries from synthesis gaps |
| 4 | Research Execution | Sovereign Search (T0-T5) | Prior art, benchmarks, failure modes |
| 5 | Grounded Report | Self | Verified claims, corrected assumptions, risk adjustments |
| 6 | Gnosis Distillation | Verity | L1→L2→L3 proposals → `proposed_lessons.yaml` |
| 7 | Integration | Ma'at | PIVOT_LOG entry, workbench items, Temple-Grade gates |

## Quality Gates (Auto-run on completion)
- `make temple-grade` (T1-T11)
- `make heritage-map` (M14)
- `make sovereignty` (M7)
- `make test` (1398+ tests)

## Output Location
`data/autonomous/{run_id}_XX_stage.md` — All stages persisted for audit/resume
```

#### 1.2 Global Skill Installation & Unified Manifest
**Directory to create**: `~/.config/opencode/skills/autonomous-meditation-pipeline/`

```bash
mkdir -p ~/.config/opencode/skills/autonomous-meditation-pipeline
# Merge both skill definitions into unified SKILL.md
cp -r .opencode/skills/meditate-pipeline/* ~/.config/opencode/skills/autonomous-meditation-pipeline/
cp -r .opencode/skills/meditate-research-pipeline/* ~/.config/opencode/skills/autonomous-meditation-pipeline/
cp -r .opencode/skills/autonomous-meditation-pipeline/* ~/.config/opencode/skills/autonomous-meditation-pipeline/
```

**Unified Skill Manifest** (`~/.config/opencode/skills/autonomous-meditation-pipeline/SKILL.md`):
- Merge `meditate-pipeline` + `meditate-research-pipeline` + `autonomous-meditation-pipeline`
- Single entry point: `/autonomous-meditation` or `/meditate-pipeline` or `/meditate-research`
- Declare required permissions: `skill`, `mcp`, `bash`, `read`, `write`

#### 1.3 Skill Trigger Definitions
**File to create**: `~/.config/opencode/skills/autonomous-meditation-pipeline/triggers.yaml`

```yaml
triggers:
  - pattern: "meditate on|autonomous meditation|run meditation pipeline"
    skill: autonomous-meditation-pipeline
    agent: kali
    priority: high
  - pattern: "problem.*architecture|architecture.*problem"
    skill: autonomous-meditation-pipeline
    agent: kali
    priority: medium
  - pattern: "research.*grounded|grounded.*research"
    skill: autonomous-meditation-pipeline
    agent: kali
    priority: medium
  - pattern: "deep research|comprehensive research|tiered research"
    skill: autonomous-meditation-pipeline
    agent: kali
    priority: medium
```

#### 1.4 Agent Permission Configuration
**File to modify**: `opencode.json`

Add to `permission` section:
```json
"permission": {
  "tool": {
    "skill": "allow",
    "mcp": "allow"
  },
  "agent": {
    "kali": { "skill": "allow", "tool": "allow" },
    "pillar": { "skill": "allow", "tool": "allow" },
    "maat": { "skill": "allow", "tool": "allow" },
    "verity": { "skill": "allow", "tool": "allow" },
    "lilith": { "skill": "allow", "tool": "allow" },
    "makali": { "skill": "allow", "tool": "allow" },
    "jem": { "skill": "allow", "tool": "allow" },
    "researcher": { "skill": "allow", "tool": "allow" }
  }
}
```

#### 1.5 MCP Hub Tool Wiring Fix (Coordination with P3)
**Root Cause**: The `autonomous_meditation_pipeline.py` `PlatformClients.from_opencode()` tries to import MCP tool functions directly, but they're registered as `@mcp.tool()` handlers (JSON-RPC), not callable Python functions.

**Fix**: Use the existing `SovereignMCPClient` from `mcp_servers.omega_hub.mcp_client` via `OpenCodePlatformClients` in `src/omega/skills/opencode_client.py`.

**File to modify**: `src/omega/skills/autonomous_meditation_pipeline.py` (lines 49-82)

```python
@classmethod
def from_opencode(cls, mcp_endpoint: str = "http://127.0.0.1:8016/mcp") -> "PlatformClients":
    """Factory for OpenCode environment using SovereignMCPClient."""
    from src.omega.skills.opencode_client import OpenCodePlatformClients
    
    opencode_clients = OpenCodePlatformClients(mcp_endpoint)
    
    class OpenCodeOracle:
        def __init__(self, oracle_client):
            self._oracle = oracle_client
        
        async def talk(self, prompt: str) -> str:
            return await self._oracle.talk(prompt)
    
    class OpenCodeSearch:
        def __init__(self, search_client):
            self._search = search_client
        
        async def search(self, query: str, limit: int = 5) -> str:
            return await self._search.search(query, limit)
        
        async def fetch(self, url: str) -> str:
            return await self._search.fetch(url)
        
        async def searxng(self, query: str, limit: int = 5) -> str:
            return await self._search.searxng(query, limit)
    
    return cls(
        oracle=OpenCodeOracle(opencode_clients.get_oracle()),
        search=OpenCodeSearch(opencode_clients.get_search()),
    )
```

**P3 Coordination**: P3 Phase 1.3 implements this exact fix in the engine core. P4 verifies the MCP Hub server exposes tools correctly via streamable-http.

#### 1.6 Verification Commands
```bash
# Test slash command appears in OpenCode
opencode --help | grep omega-meditation

# Test skill triggers fire
# In OpenCode: "meditate on unified credential vault"
# Should auto-invoke autonomous-meditation-pipeline skill

# Test MCP tool calls return real data
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
.venv/bin/python -c "
import anyio
from mcp_servers.omega_hub.mcp_client import SovereignMCPClient

async def test():
    async with SovereignMCPClient('http://127.0.0.1:8016/mcp') as client:
        result = await client.call_tool('oracle_talk', {'query': 'test'})
        print('oracle_talk:', result.content[0][:200] if result.content else 'empty')
        result = await client.call_tool('library_web_search', {'query': 'test', 'limit': 3})
        print('library_web_search:', result.content[0][:200] if result.content else 'empty')

anyio.run(test)
"
```

---

### Phase 2: MCP Hub Server Hardening (3 hours)
*Dependencies: Phase 1 complete (slash command must work for container health checks)*

#### 2.1 Health Check Endpoints
**File to modify**: `mcp_servers/omega_hub/server.py`

Add after line 159 (existing `_health` endpoint):

```python
async def _ready(request: Request) -> JSONResponse:
    """Kubernetes-style readiness probe — checks oracle singleton, tool registry, dependencies."""
    checks = {
        "oracle": "unknown",
        "tools": 0,
        "hivemind": "unknown",
        "library": "unknown",
        "research": "unknown",
    }
    
    # Check oracle singleton
    try:
        if oracle is not None:
            checks["oracle"] = "ready"
        else:
            checks["oracle"] = "not_initialized"
    except Exception as e:
        checks["oracle"] = f"error: {e}"
    
    # Check tool registry
    try:
        checks["tools"] = len(mcp._tool_manager._tools)
    except Exception:
        checks["tools"] = "error"
    
    # Check hivemind
    try:
        if _hot_store is not None:
            checks["hivemind"] = "ready"
        else:
            checks["hivemind"] = "not_initialized"
    except Exception:
        checks["hivemind"] = "error"
    
    # Overall readiness
    all_ready = all(v in ("ready", "unknown") or (isinstance(v, int) and v > 0) for v in checks.values())
    status_code = 200 if all_ready else 503
    
    return JSONResponse({
        "status": "ready" if all_ready else "not_ready",
        "checks": checks,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }, status_code=status_code)


async def _health(request: Request) -> JSONResponse:
    """Liveness probe — basic server health."""
    return JSONResponse({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "2.2.0",
        "oracle": "ready" if oracle is not None else "initializing",
        "tools": len(mcp._tool_manager._tools),
    })
```

Add routes to `hub_routes`:
```python
hub_routes = [
    Route("/health", _health),
    Route("/ready", _ready),
    # ... existing routes
]
```

#### 2.2 Structured Logging with trace_id
**File to modify**: `mcp_servers/omega_hub/middleware.py` (or add to server.py)

```python
import logging
import uuid
from contextvars import ContextVar

_trace_id: ContextVar[str] = ContextVar("trace_id", default="")

class TraceIdFilter(logging.Filter):
    def filter(self, record):
        record.trace_id = _trace_id.get() or "none"
        return True

# Add to logging config
logging.getLogger("omega.hub").addFilter(TraceIdFilter())
```

#### 2.3 CORS Configuration for OpenCode Web Access
**File to modify**: `mcp_servers/omega_hub/server.py` in `run_mcp` call or `apply_security`

```python
from starlette.middleware.cors import CORSMiddleware

# In apply_security or run_mcp:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # OpenCode web UI
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 2.4 Rate Limiting on Tool Endpoints
**File to modify**: `mcp_servers/omega_hub/middleware.py`

```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import time
from collections import defaultdict

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/mcp") or request.url.path.startswith("/proxy"):
            client_ip = request.client.host
            now = time.time()
            # Clean old requests
            self.requests[client_ip] = [t for t in self.requests[client_ip] if now - t < 60]
            
            if len(self.requests[client_ip]) >= self.requests_per_minute:
                return JSONResponse(
                    {"error": "Rate limit exceeded", "retry_after": 60},
                    status_code=429
                )
            
            self.requests[client_ip].append(now)
        
        return await call_next(request)
```

#### 2.5 Verification Commands
```bash
# Start MCP Hub
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
python mcp_servers/omega_hub/server.py &

# Test health endpoint
curl -s http://127.0.0.1:8016/health | jq .

# Test ready endpoint
curl -s http://127.0.0.1:8016/ready | jq .

# Test CORS
curl -H "Origin: http://localhost:3000" -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" -X OPTIONS \
  http://127.0.0.1:8016/mcp -v
```

---

### Phase 3: MCP Protocol Compliance (D-284 Alignment) (3 hours)
*Dependencies: Phase 2 complete*

#### 3.1 Streamable HTTP Transport Verification
**Current State**: `opencode.json` already configures `type: "streamable-http"` for `omega-hub` ✅

**Verification**: Ensure MCP Hub server uses Streamable HTTP (not SSE):
```python
# In server.py - verify FastMCP is configured for streamable-http
# The run_mcp function in omega/mcp_runtime.py should handle this
```

#### 3.2 PKCE OAuth Flow Support (Future-Proofing)
**File to create**: `mcp_servers/omega_hub/oauth.py`

```python
"""PKCE OAuth 2.1 + Dynamic Client Registration (RFC 7591) for remote MCP servers."""
import secrets
import hashlib
import base64
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlencode, parse_qs, urlparse

@dataclass
class PKCEChallenge:
    code_verifier: str
    code_challenge: str
    code_challenge_method: str = "S256"
    state: str = ""

    @classmethod
    def generate(cls) -> "PKCEChallenge":
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip("=")
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip("=")
        state = base64.urlsafe_b64encode(secrets.token_bytes(16)).decode().rstrip("=")
        return cls(code_verifier=code_verifier, code_challenge=code_challenge, state=state)

    def authorization_url(self, auth_server: str, client_id: str, redirect_uri: str, scope: str = "mcp") -> str:
        params = {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
            "code_challenge": self.code_challenge,
            "code_challenge_method": self.code_challenge_method,
            "state": self.state,
        }
        return f"{auth_server}/authorize?{urlencode(params)}"

    def exchange_code(self, token_endpoint: str, client_id: str, redirect_uri: str, code: str) -> dict:
        import httpx
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "code_verifier": self.code_verifier,
        }
        response = httpx.post(token_endpoint, data=data)
        response.raise_for_status()
        return response.json()
```

#### 3.3 Dynamic Client Registration (RFC 7591)
```python
async def register_client(registration_endpoint: str, redirect_uris: list, client_name: str = "Omega Engine") -> dict:
    import httpx
    data = {
        "client_name": client_name,
        "redirect_uris": redirect_uris,
        "grant_types": ["authorization_code", "refresh_token"],
        "response_types": ["code"],
        "token_endpoint_auth_method": "none",  # PKCE public client
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(registration_endpoint, json=data)
        response.raise_for_status()
        return response.json()
```

#### 3.4 Tool Annotations for Agent Discoverability
**File to modify**: `mcp_servers/omega_hub/tools.py` — Add annotations to each `@mcp.tool()`

```python
@mcp.tool(
    name="oracle_talk",
    description="Route a query to the optimal entity via Oracle routing. Returns entity response with provider provenance.",
    annotations={
        "readOnlyHint": True,
        "idempotentHint": False,
        "openWorldHint": True,
    }
)
async def oracle_talk(query: str) -> str:
    ...
```

---

### Phase 4: Cross-Platform Communication Verification (3 hours)
*Dependencies: Phase 1 complete (slash command), Phase 2 complete (MCP Hub running)*

#### 4.1 Three-Mode Execution Matrix
| Mode | Transport | Use Case | Entry Point |
|------|-----------|----------|-------------|
| **OpenCode** | MCP Hub JSON-RPC via `SovereignMCPClient` | Primary — full agent integration | `/omega-meditation` slash command |
| **CLI** | Subprocess calls to `opencode` + `websearch` | Headless/CI execution | `omega-meditation "problem" --mode cli` |
| **Standalone** | Dry-run only (no external calls) | Testing/offline development | `omega-meditation "problem" --mode standalone --dry-run` |

#### 4.2 CLI Mode Implementation
**File to modify**: `src/omega/skills/autonomous_meditation_pipeline.py` — `PlatformClients.from_cli()`

```python
@classmethod
def from_cli(cls, oracle_cmd: str = "opencode", search_cmd: str = "websearch") -> "PlatformClients":
    """Factory for CLI environment (subprocess calls)."""
    import subprocess
    import json
    
    class CLIOracle:
        def __init__(self, cmd: str):
            self.cmd = cmd
        
        async def talk(self, prompt: str) -> str:
            # Use opencode as subprocess with prompt
            proc = await anyio.run_process(
                [self.cmd, "run", "--prompt", prompt],
                capture_output=True
            )
            return proc.stdout.decode() if proc.returncode == 0 else f"Error: {proc.stderr.decode()}"
    
    class CLISearch:
        def __init__(self, cmd: str):
            self.cmd = cmd
        
        async def search(self, query: str, limit: int = 5) -> str:
            proc = await anyio.run_process(
                [self.cmd, query, "--limit", str(limit), "--format", "json"],
                capture_output=True
            )
            return proc.stdout.decode() if proc.returncode == 0 else "[]"
        
        async def fetch(self, url: str) -> str:
            proc = await anyio.run_process(
                ["webfetch", url, "--format", "markdown"],
                capture_output=True
            )
            return proc.stdout.decode() if proc.returncode == 0 else ""
        
        async def searxng(self, query: str, limit: int = 5) -> str:
            proc = await anyio.run_process(
                ["searxng", "search", query, "--limit", str(limit), "--format", "json"],
                capture_output=True
            )
            return proc.stdout.decode() if proc.returncode == 0 else "[]"
    
    return cls(oracle=CLIOracle(oracle_cmd), search=CLISearch(search_cmd))
```

#### 4.3 Verification Matrix
```bash
# Test all three modes
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine

# Mode 1: OpenCode (requires running OpenCode session with MCP Hub)
/omega-meditation "Test problem" --mode opencode --dry-run

# Mode 2: CLI (requires opencode CLI installed)
uv run omega-meditation "Test problem" --mode cli --dry-run

# Mode 3: Standalone (always works)
uv run omega-meditation "Test problem" --mode standalone --dry-run

# Verify outputs are equivalent in structure
ls -la data/autonomous/ | grep test
```

---

### Phase 5: Compaction Resilience Integration (3 hours)
*Dependencies: Phase 1 complete (needs OpenCode hooks)*

#### 5.1 OpenCode Compaction Hook Research
**Finding**: OpenCode does not natively support compaction hooks. Workaround: Wrapper script approach.

#### 5.2 Compaction Guard Script
**File to create**: `scripts/opencode-compaction-guard.py`

```python
#!/usr/bin/env python3
"""
OpenCode Compaction Resilience Guard
Monitors for compaction triggers and auto-writes session_gnosis.md
Integrates with P1's compaction-guard infrastructure.
"""
import json
import sys
import os
from pathlib import Path
from datetime import datetime

SESSION_GNOSIS_DIR = Path.home() / ".config" / "opencode" / "session_gnosis"
SESSION_GNOSIS_DIR.mkdir(parents=True, exist_ok=True)

def write_session_gnosis(session_id: str, context: dict):
    """Write session state before compaction."""
    gnosis_file = SESSION_GNOSIS_DIR / f"{session_id}.md"
    content = f"""# SESSION GNOSIS — {session_id}
**Captured**: {datetime.now().isoformat()}
**Reason**: Pre-compaction preservation

## Context
{json.dumps(context, indent=2)}

## Active Tasks
{context.get('active_tasks', 'Unknown')}

## Key Decisions
{context.get('decisions', 'None')}

## Continuation Notes
{context.get('continuation', 'Resume from last checkpoint')}
"""
    gnosis_file.write_text(content)
    print(f"[compaction-guard] Wrote session gnosis to {gnosis_file}", file=sys.stderr)

def main():
    if len(sys.argv) < 2:
        print("Usage: opencode-compaction-guard <session_id> [context_json]", file=sys.stderr)
        sys.exit(1)
    
    session_id = sys.argv[1]
    context = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    write_session_gnosis(session_id, context)

if __name__ == "__main__":
    main()
```

#### 5.3 Hydration Sequence on Session Restore
**File to create**: `scripts/opencode-hydration.py`

```python
#!/usr/bin/env python3
"""
Session Hydration — Restores context from session_gnosis.md
Called at OpenCode session start.
"""
import json
from pathlib import Path

def hydrate_session(session_id: str) -> dict:
    gnosis_file = Path.home() / ".config" / "opencode" / "session_gnosis" / f"{session_id}.md"
    if gnosis_file.exists():
        content = gnosis_file.read_text()
        return {"restored": True, "gnosis": content, "session_id": session_id}
    return {"restored": False, "session_id": session_id}

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: opencode-hydration <session_id>", file=sys.stderr)
        sys.exit(1)
    
    session_id = sys.argv[1]
    result = hydrate_session(session_id)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
```

#### 5.4 OpenCode Wrapper Integration
**File to create**: `scripts/opencode-wrapper.sh`

```bash
#!/bin/bash
# Wrapper that injects compaction guard and hydration

SESSION_ID="${OPENCODE_SESSION_ID:-$(uuidgen)}"
export OPENCODE_SESSION_ID="$SESSION_ID"

# Pre-hydration
python3 scripts/opencode-hydration.py "$SESSION_ID" > /tmp/opencode_hydration_$$.json

# Run OpenCode with compaction monitoring
# Note: OpenCode doesn't expose compaction hooks directly
# This is a best-effort wrapper; true hooks require OpenCode plugin API
exec opencode "$@"
```

#### 5.5 Integration with P1's Infrastructure
**P1 Deliverable**: `scripts/opencode-compaction-guard.py` and `scripts/opencode-hydration.py`
**P4 Integration**: Hook into OpenCode session lifecycle via wrapper or plugin when available

---

### Phase 6: Cross-Pillar Integration & Verification (3 hours)
*Dependencies: All previous phases complete*

#### 6.1 P1 Integration Verification
| P1 Deliverable | P4 Verification |
|----------------|-----------------|
| MCP Hub client adapter spec | `create_pipeline_opencode()` uses `OpenCodePlatformClients` |
| CI/CD workflow template | `.github/workflows/omega-meditation-ci.yml` follows pattern |
| M6/M16/M23 compliance | Container paths use `PROJECT_ROOT`, no hardcoded paths |

#### 6.2 P3 Integration Verification
| P3 Deliverable | P4 Verification |
|----------------|-----------------|
| Working MCP Hub container | `omega-hub` health endpoint returns 200 |
| Fixed tool wiring | `oracle_talk`, `library_web_search` return real data |
| Slash command registered | `/omega-meditation` appears in OpenCode |

#### 6.3 P5 Governance Verification
| Mandate | P4 Compliance Check |
|---------|---------------------|
| M6: Podman `UserNS=keep-id` + `User=1000` | Container config verified |
| M16: No hardcoded paths in `src/omega/` | `grep -r "home/arcana" src/omega/` returns nothing |
| M23: No soft failures | All MCP tool calls raise on failure |

#### 6.4 P6 Cognition Verification
- Pipeline executes real oracle/search calls (not dry-run)
- Provider routing verified via `GenerateResult.provider_name` (M22)

#### 6.5 P7 Context Verification
- Stage 6 (Gnosis) outputs valid `proposed_lessons.yaml` format
- Soul distillation pipeline integration works

#### 6.6 P8 Observability Verification
- Health endpoints return structured data
- Structured logs include `trace_id`

#### 6.7 P9 Orchestration Verification
- Hivemind handoff protocol works for multi-agent runs
- Skill triggers fire correctly

#### 6.8 P10 Validation Verification
- Chaos test scenarios defined for pipeline
- Temple-Grade gates in CI

---

## ⏱️ Time Estimates Summary

| Phase | Tasks | Est. Hours | Cumulative |
|-------|-------|------------|------------|
| 0 | Foundation & Verification | 2 | 2 |
| 1 | OpenCode Slash Command & Skill System | 4 | 6 |
| 2 | MCP Hub Server Hardening | 3 | 9 |
| 3 | MCP Protocol Compliance (D-284) | 3 | 12 |
| 4 | Cross-Platform Communication | 3 | 15 |
| 5 | Compaction Resilience | 3 | 18 |
| 6 | Cross-Pillar Integration & Verification | 3 | 21 |
| **Total** | | **~21 hours** | |

---

## ⚠️ Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| MCP Hub tool wiring fails (Phase 1.5) | High | P0 — Blocks all pipeline execution | Debug `_require_service()` and `oracle` singleton init first; fallback to CLI mode |
| OpenCode compaction hooks don't exist | High | P1 — Session state loss | Implement best-effort wrapper; document limitation; track OpenCode plugin API |
| Skill triggers don't fire | Medium | P0 — No auto-invocation | Test trigger patterns thoroughly; verify `triggers.yaml` syntax |
| Agent permissions misconfigured | Medium | P0 — Skills unusable | Verify `opencode.json` permission structure; test each agent |
| PyPI/Homebrew publishing fails | Low | P1 — Distribution blocked | Document manual `uv publish` with API token as backup |
| Cross-pillar integration gaps | Medium | P1 — CI fails | Run `make temple-grade` after each phase; involve P3/P5 early |

---

## 🔗 Cross-Pillar Integration Points

### What P4 Delivers to Other Pillars
| Pillar | Deliverable | Format |
|--------|-------------|--------|
| **P1** | Verified slash command, skill triggers, agent permissions | `.opencode/commands/`, `~/.config/opencode/skills/`, `opencode.json` |
| **P3** | Working MCP Hub container, fixed tool wiring, slash command | Container health, tool call logs, OpenCode integration |
| **P5** | M6-compliant containers, M16-compliant paths, M23 hard-fail behavior | Code audit artifacts |
| **P6** | Pipeline executes real oracle routing | Integration test logs |
| **P7** | Session gnosis persistence across compaction | `session_gnosis.md` files |
| **P8** | Health endpoints, structured logs with `trace_id` | `/health`, `/ready`, log samples |
| **P9** | Hivemind-aware skill triggers | Trigger config |
| **P10** | Chaos test scenarios, Temple-Grade in CI | Test files, workflow |

### What P4 Needs from Other Pillars
| Pillar | Need | When |
|--------|------|------|
| **P1** | MCP Hub client adapter spec (Phase 1.4) | Phase 1 start |
| **P1** | CI/CD workflow template | Phase 6 |
| **P1** | M6/M16/M23 compliance requirements | Phase 6 |
| **P3** | MCP Hub container running with health checks | Phase 0.3, 6.2 |
| **P3** | Slash command registration | Phase 6.2 |
| **P5** | Mandate audit sign-off | Phase 6.3 |
| **P6** | Oracle routing verification | Phase 6.4 |
| **P7** | Soul distillation integration spec | Phase 6.5 |

---

## ✅ Quality Gates (Per Phase)

| Phase | Gates |
|-------|-------|
| 0 | `uv build` succeeds, CLI dry-run works, MCP tools return real data |
| 1 | `/omega-meditation` slash command appears in OpenCode, skill triggers fire, MCP calls return real results |
| 2 | `systemctl --user start omega-hub` works, health endpoint returns 200, logs rotate |
| 3 | Streamable HTTP verified, PKCE flow implemented, tool annotations present |
| 4 | All three modes (OpenCode/CLI/Standalone) produce equivalent output structure |
| 5 | Compaction guard writes `session_gnosis.md`, hydration restores context |
| 6 | `make test && make temple-grade && make heritage-map && make sovereignty` all pass |

---

## 🎯 Next Actions (Immediate)

1. **Run Phase 0 verification** — Confirm package builds and MCP tools work
2. **Debug MCP tool wiring** — Fix `PlatformClients.from_opencode()` to use proper MCP client
3. **Create slash command** — `.opencode/commands/omega-meditation.md`
4. **Configure agent permissions** — Update `opencode.json`
5. **Begin container setup** — Podman Quadlet for omega-hub (coordinate with P1)
6. **Install global skill** — `~/.config/opencode/skills/autonomous-meditation-pipeline/`

---

## 📝 Session Gnosis (L1→L2→L3)

**L1 Narrative**: Created comprehensive P4 Integration Implementation Plan for the Autonomous Meditation Pipeline. Analyzed current state: core engine exists, MCP Hub running, skills defined, but critical integration gaps remain — no slash command, no skill triggers, broken MCP wiring, missing agent permissions, no compaction resilience. Structured 6 phases over ~21 hours with explicit file paths, commands, and quality gates.

**L2 Insight**: The biggest blocker is MCP Hub tool wiring — the pipeline's `PlatformClients.from_opencode()` tries to import MCP tool functions directly, but they're registered as MCP tools (JSON-RPC), not Python callables. This must be fixed before any OpenCode integration works. The compaction resilience is a known OpenCode limitation requiring wrapper workarounds. P1 and P3 have detailed plans that P4 must coordinate with closely.

**L3 Principle**: **L3-IntegrationAsProduct**: Integration is not "glue" — it's the product delivery mechanism. Every gap between "engine works" and "user runs one command" is a product defect. P4 owns the entire critical path from MCP Hub health to slash command to skill trigger to agent permission to compaction survival. The pipeline is not "integrated" until a user can type `/omega-meditation "problem"` and get a research-grounded architecture with zero manual steps.

---

*⬡ OMEGA ⬡ PILLAR P4 ⬡ INTEGRATION ⬡ trc_p4_integration_plan ⬡ 2026-07-19*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: P4 | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
