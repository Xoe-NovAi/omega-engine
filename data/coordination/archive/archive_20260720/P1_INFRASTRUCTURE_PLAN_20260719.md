<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 P1 Infrastructure Implementation Plan
## Autonomous Meditation Pipeline — Complete Product Deployment

**AP Token**: `AP-P1-INFRA-PLAN-20260719`
⬡ OMEGA ⬡ PILLAR ⬡ P1 ⬡ INFRASTRUCTURE ⬡ trc_p1_infra_plan ⬡ ACTIVE

**Date**: 2026-07-19
**Author**: Pillar P1 — Infrastructure (SysAdmin — Environment Hardening, Containers, Deployment)
**Mission**: Transform the Autonomous Meditation Pipeline from "engine core + partial package" into a **fully deployed, user-facing, OpenCode-integrated, standalone-installable system**.

---

## 📊 Current State Analysis

### ✅ What Exists (Assets)
| Asset | Location | Status | Notes |
|-------|----------|--------|-------|
| Core Pipeline Engine | `src/omega/skills/autonomous_meditation_pipeline.py` | ✅ Complete | Platform-agnostic, M16 compliant, dependency injection |
| Standalone Package | `packages/omega-meditation/` | ✅ Complete | `pyproject.toml`, CLI entry points (`omega-meditation`, `meditate-auto`) |
| Package Factories | `packages/omega-meditation/src/omega_meditation/pipeline.py` | ✅ Complete | `create_pipeline_opencode`, `create_pipeline_cli`, `create_pipeline_standalone` |
| CLI Entry Point | `packages/omega-meditation/src/omega_meditation/cli.py` | ✅ Complete | Argparse with `--mode`, `--dry-run`, `--resume-from` |
| MCP Hub Tools | `mcp_servers/omega_hub/tools.py` | ✅ Available | `oracle_talk`, `oracle_summon`, `library_web_search`, `oracle_summon_local` |
| Meditate Command | `.opencode/commands/meditate.md` | ✅ Complete | Full protocol with Kali host |
| Research Pipeline Skill | `.opencode/skills/meditate-research-pipeline/` | ✅ Complete | 5-stage skill with quality gates |

### ❌ Critical Gaps (From User Requirements)
| # | Gap | Impact | Priority |
|---|-----|--------|----------|
| 1 | No `/omega-meditation` slash command | Users can't invoke pipeline directly | **P0** |
| 2 | Skill triggers not defined for auto-invocation | No automatic pipeline execution | **P0** |
| 3 | MCP Hub tool integration returns dry-run templates | Pipeline can't execute real searches/oracle calls | **P0** |
| 4 | Agent permissions for `skill` tool not configured | Agents can't invoke skills | **P0** |
| 5 | Global skill install path not set up | Skills not discoverable by OpenCode | **P0** |
| 6 | No compaction resilience plugin | Session state lost on compaction | **P1** |
| 7 | No skill scripts for direct execution | Can't run `omega-meditation` from PATH | **P1** |
| 8 | Distribution (PyPI/Homebrew) not published | Users can't `pip install` or `brew install` | **P1** |

---

## 🏗️ Phase Breakdown

### Phase 0: Foundation & Verification (2 hours) — **MUST COMPLETE FIRST**
*Dependencies: None. All subsequent phases depend on this.*

| Task | File/Command | Verification |
|------|--------------|--------------|
| 0.1 Verify package builds | `cd packages/omega-meditation && uv build` | `dist/*.whl` created |
| 0.2 Verify CLI entry points work | `uv run omega-meditation "test" --dry-run --mode standalone` | Dry run completes |
| 0.3 Verify MCP Hub tools return real data | `python -c "from mcp_servers.omega_hub.tools import oracle_talk; import asyncio; print(asyncio.run(oracle_talk('test')))"` | Returns JSON with `text`, `entity`, `backend` |
| 0.4 Check OpenCode config structure | `cat opencode.json \| jq '.mcp, .permission'` | MCP servers + permissions visible |
| 0.5 Create workspace lock | `omega-hub_hivemind_workspace_lock_acquire channel=opencode entity=pillar domain=P1_INFRA_PLAN ttl=7200` | Lock acquired |

**Risk**: If MCP Hub tools return dry-run templates, the root cause is likely the `_require_service()` guard or the `oracle` singleton not being initialized. Must debug before Phase 1.

---

### Phase 1: OpenCode Integration Infrastructure (4 hours)
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

#### 1.2 Global Skill Installation Path
**Directory to create**: `~/.config/opencode/skills/autonomous-meditation-pipeline/`

```bash
mkdir -p ~/.config/opencode/skills/autonomous-meditation-pipeline
cp -r .opencode/skills/meditate-pipeline/* ~/.config/opencode/skills/autonomous-meditation-pipeline/
cp -r .opencode/skills/meditate-research-pipeline/* ~/.config/opencode/skills/autonomous-meditation-pipeline/
```

**Skill manifest** (`~/.config/opencode/skills/autonomous-meditation-pipeline/SKILL.md`):
- Merge both skill definitions
- Add `triggers` section for auto-invocation

#### 1.3 Agent Permission Configuration
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
    "verity": { "skill": "allow", "tool": "allow" }
  }
}
```

#### 1.4 MCP Hub Tool Wiring Fix
**Root Cause Analysis**: The `omega_hub_oracle_talk` and `omega_hub_library_web_search` imports in `autonomous_meditation_pipeline.py` fail because:
1. The `mcp_servers.omega_hub.tools` module exports functions decorated with `@mcp.tool()` — these are MCP tool handlers, not directly callable Python functions
2. The `_require_service()` guard checks for `oracle` singleton initialization
3. In OpenCode context, the MCP client calls tools via JSON-RPC, not direct Python imports

**Fix**: Use the existing `SovereignMCPClient` from `mcp_servers.omega_hub.mcp_client` to connect to the local omega-hub MCP server

**File to create**: `src/omega/skills/opencode_client.py`
```python
"""OpenCode MCP Client Adapter — Uses SovereignMCPClient to call local omega-hub tools"""
import anyio
from typing import Optional
from mcp_servers.omega_hub.mcp_client import SovereignMCPClient, MCPToolResult

class OpenCodeMCPClient:
    """Calls local MCP Hub tools through the MCP protocol using SovereignMCPClient."""
    
    def __init__(self, mcp_endpoint: str = "http://127.0.0.1:8016/mcp"):
        self.endpoint = mcp_endpoint
        self._client: Optional[SovereignMCPClient] = None
    
    async def _get_client(self) -> SovereignMCPClient:
        if self._client is None:
            self._client = SovereignMCPClient(self.endpoint)
            await self._client.__aenter__()
        return self._client
    
    async def close(self):
        if self._client:
            await self._client.__aexit__(None, None, None)
            self._client = None
    
    async def oracle_talk(self, query: str) -> str:
        client = await self._get_client()
        result: MCPToolResult = await client.call_tool("oracle_talk", {"query": query})
        return result.content[0] if result.content else "{}"
    
    async def library_web_search(self, query: str, limit: int = 5) -> str:
        client = await self._get_client()
        result: MCPToolResult = await client.call_tool("library_web_search", {"query": query, "limit": limit})
        return result.content[0] if result.content else "{}"
    
    async def webfetch(self, url: str) -> str:
        client = await self._get_client()
        result: MCPToolResult = await client.call_tool("webfetch", {"url": url})
        return result.content[0] if result.content else ""
    
    async def searxng_search(self, query: str, limit: int = 5) -> str:
        client = await self._get_client()
        result: MCPToolResult = await client.call_tool("searxng_search", {"query": query, "limit": limit})
        return result.content[0] if result.content else "{}"


class OpenCodePlatformClients:
    """PlatformClients implementation using OpenCodeMCPClient."""
    
    def __init__(self, mcp_endpoint: str = "http://127.0.0.1:8016/mcp"):
        self.mcp_client = OpenCodeMCPClient(mcp_endpoint)
    
    class Oracle:
        def __init__(self, mcp_client: OpenCodeMCPClient):
            self.mcp_client = mcp_client
        
        async def talk(self, prompt: str) -> str:
            return await self.mcp_client.oracle_talk(prompt)
    
    class Search:
        def __init__(self, mcp_client: OpenCodeMCPClient):
            self.mcp_client = mcp_client
        
        async def search(self, query: str, limit: int = 5) -> str:
            return await self.mcp_client.library_web_search(query, limit)
        
        async def fetch(self, url: str) -> str:
            return await self.mcp_client.webfetch(url)
        
        async def searxng(self, query: str, limit: int = 5) -> str:
            return await self.mcp_client.searxng_search(query, limit)
    
    def get_oracle(self) -> Oracle:
        return self.Oracle(self.mcp_client)
    
    def get_search(self) -> Search:
        return self.Search(self.mcp_client)
    
    async def close(self):
        await self.mcp_client.close()
```

**File to modify**: `src/omega/skills/autonomous_meditation_pipeline.py`
- Replace `PlatformClients.from_opencode()` to use `OpenCodePlatformClients`
- Remove direct imports from `mcp_servers.omega_hub.tools`
- Update `create_pipeline_opencode` factory to pass the new client

#### 1.5 Skill Trigger Definitions
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
```

---

### Phase 2: Container & Deployment Infrastructure (6 hours)
*Dependencies: Phase 1 complete (slash command must work for container health checks)*

#### 2.1 Podman Quadlet for MCP Hub Server
**File to create**: `/etc/containers/systemd/omega-hub.container` (system) or `~/.config/containers/systemd/omega-hub.container` (user)

```ini
[Unit]
Description=Omega Engine MCP Hub Server
After=network-online.target
Wants=network-online.target

[Container]
Image=ghcr.io/xoe-novai/omega-hub:latest
# M6: UserNS=keep-id + User=1000, NO :U flag on shared volumes
UserNS=keep-id
User=1000
# Volume mounts (host → container)
Volume=/home/arcana-novai/Documents/Xoe-NovAi/omega-engine:/workspace:Z
Volume=/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data:/workspace/data:Z
Volume=/home/arcana-novai/.config/opencode:/home/arcana-novai/.config/opencode:Z
# Environment
Environment=PYTHONPATH=/workspace/src
Environment=OMEGA_CONFIG_DIR=/workspace/config
# Port mapping
PublishPort=8016:8016
# Health check
HealthCmd=curl -f http://localhost:8016/health || exit 1
HealthInterval=30
HealthTimeout=10
HealthRetries=3
HealthStartPeriod=10

[Service]
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
```

#### 2.2 Systemd Service Units for Supporting Services
**Files to create**:
- `~/.config/systemd/user/searxng.service`
- `~/.config/systemd/user/firecrawl.service`

```ini
# searxng.service
[Unit]
Description=SearXNG Metasearch Engine
After=network-online.target

[Service]
Type=exec
ExecStart=/usr/bin/podman run --rm --name searxng \
  -p 8018:8080 \
  -v /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/config/searxng:/etc/searxng:Z \
  docker.io/searxng/searxng:latest
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
```

#### 2.3 Health Check Endpoints
**File to modify**: `mcp_servers/omega_hub/server.py`
- Add `/health` endpoint returning `{"status": "healthy", "oracle": "ready", "tools": N}`
- Add `/ready` endpoint for Kubernetes-style readiness probes

#### 2.4 Log Rotation & Persistence
**File to create**: `/etc/logrotate.d/omega-engine` (system) or `~/.config/logrotate/omega-engine` (user)

```
/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0640 arcana-novai arcana-novai
    sharedscripts
    postrotate
        systemctl --user reload omega-hub > /dev/null 2>&1 || true
    endscript
}
```

---

### Phase 3: Compaction Resilience (3 hours)
*Dependencies: Phase 1 complete (needs OpenCode hooks)*

#### 3.1 OpenCode Compaction Hook
**Research Finding**: OpenCode does not natively support compaction hooks. Workaround: Use a wrapper script that monitors session state.

**File to create**: `scripts/opencode-compaction-guard.py`

```python
#!/usr/bin/env python3
"""
OpenCode Compaction Resilience Guard
Monitors for compaction triggers and auto-writes session_gnosis.md
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
    print(f"[compaction-guard] Wrote session gnosis to {gnosis_file}")

def main():
    # Called by OpenCode wrapper with session context
    if len(sys.argv) < 2:
        print("Usage: opencode-compaction-guard <session_id> [context_json]")
        sys.exit(1)
    
    session_id = sys.argv[1]
    context = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    write_session_gnosis(session_id, context)

if __name__ == "__main__":
    main()
```

#### 3.2 Hydration Sequence on Session Restore
**File to create**: `scripts/opencode-hydration.py`

```python
#!/usr/bin/env python3
"""
Session Hydration — Restores context from session_gnosis.md
"""
import json
from pathlib import Path

def hydrate_session(session_id: str) -> dict:
    gnosis_file = Path.home() / ".config" / "opencode" / "session_gnosis" / f"{session_id}.md"
    if gnosis_file.exists():
        content = gnosis_file.read_text()
        # Parse and return structured context
        return {"restored": True, "gnosis": content}
    return {"restored": False}
```

#### 3.3 OpenCode Wrapper Script
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

---

### Phase 4: Dependency & Environment Management (2 hours)
*Dependencies: Phase 0 complete*

#### 4.1 UV Lockfile & Reproducible Builds
**File to verify**: `packages/omega-meditation/uv.lock` (auto-generated by `uv lock`)

```bash
cd packages/omega-meditation
uv lock --upgrade
uv sync --frozen
```

#### 4.2 Virtual Environment Isolation for Global Skills
**File to create**: `scripts/install-global-skill.sh`

```bash
#!/bin/bash
# Installs omega-meditation skill in isolated venv

SKILL_DIR="$HOME/.config/opencode/skills/autonomous-meditation-pipeline"
VENV_DIR="$SKILL_DIR/.venv"

python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip uv
uv pip install -e /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/packages/omega-meditation
deactivate

# Create wrapper script
cat > "$SKILL_DIR/omega-meditation" << 'EOF'
#!/bin/bash
source "$HOME/.config/opencode/skills/autonomous-meditation-pipeline/.venv/bin/activate"
exec omega-meditation "$@"
EOF
chmod +x "$SKILL_DIR/omega-meditation"
```

#### 4.3 Dependency Version Pinning Strategy
**Policy** (document in `packages/omega-meditation/DEPENDENCY_POLICY.md`):
- **Core deps** (`anyio`, `pyyaml`, `rich`): Pin to `>=min,<next_major` (e.g., `anyio>=4.4,<5`)
- **Optional deps** (`mcp`, `click`): Pin to `>=min,<next_major`
- **Dev deps**: Pin exact versions in `uv.lock` only
- **Security updates**: Run `uv lock --upgrade` monthly, test with `make test`

---

### Phase 5: Distribution & Publishing (4 hours)
*Dependencies: Phase 2 complete (container tested), Phase 4 complete (lockfile frozen)*

#### 5.1 PyPI Publishing Workflow
**File to create**: `.github/workflows/publish-pypi.yml`

```yaml
name: Publish to PyPI
on:
  release:
    types: [published]
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to publish (e.g., 1.0.1)'
        required: true

permissions:
  id-token: write  # For trusted publishing
  contents: read

jobs:
  build-and-publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install uv
        uses: astral-sh/setup-uv@v3
      - name: Build package
        working-directory: ./packages/omega-meditation
        run: uv build
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          packages-dir: ./packages/omega-meditation/dist
```

**Trusted Publishing Setup** (one-time):
1. Go to PyPI → Project Settings → Trusted Publishers
2. Add: `github.com/xoe-novai/omega-engine` with workflow `publish-pypi.yml`
3. No API tokens needed — uses OIDC

#### 5.2 Homebrew Tap Creation
**Repository to create**: `homebrew-omega` (under `xoe-novai` org)

**Formula generation** (using `homebrew-pypi-poet`):
```bash
# One-time setup
brew tap xoe-novai/omega
brew install homebrew-pypi-poet

# Generate formula
cd packages/omega-meditation
poet -f omega-meditation > /tmp/omega-meditation.rb
# Edit formula: add desc, homepage, license, test block
cp /tmp/omega-meditation.rb ~/homebrew-omega/Formula/omega-meditation.rb
```

**Formula template** (`Formula/omega-meditation.rb`):
```ruby
class OmegaMeditation < Formula
  desc "Autonomous Meditation Pipeline — Problem → Architecture → Research → Gnosis"
  homepage "https://github.com/xoe-novai/omega-engine"
  url "https://pypi.org/packages/source/o/omega-meditation/omega-meditation-1.0.0.tar.gz"
  sha256 "SHA256_FROM_PYPI"
  license "MIT"
  depends_on "python@3.12"
  
  def install
    python3 = Formula["python@3.12"].opt_bin/"python3"
    system python3, "-m", "pip", "install", "--prefix=#{libexec}", "."
    bin.install_symlink libexec/"bin/omega-meditation"
    bin.install_symlink libexec/"bin/meditate-auto"
  end
  
  test do
    system bin/"omega-meditation", "test problem", "--dry-run", "--mode", "standalone"
  end
end
```

**GitHub Action for Homebrew** (`.github/workflows/homebrew.yml`):
```yaml
name: Update Homebrew Formula
on:
  release:
    types: [published]
jobs:
  update-formula:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/checkout@v4
        with:
          repository: xoe-novai/homebrew-omega
          token: ${{ secrets.HOMEBREW_TAP_TOKEN }}
          path: homebrew-omega
      - name: Update formula
        run: |
          cd homebrew-omega
          # Use poet or manual update
          git config user.name "github-actions"
          git config user.email "actions@github.com"
          git commit -am "Update omega-meditation to ${{ github.event.release.tag_name }}"
          git push
```

#### 5.3 Standalone Executable (PyInstaller/Nuitka) — Optional
**Evaluation**: For a Python CLI with MCP dependencies, `pipx install omega-meditation` is preferred over standalone binaries. PyInstaller struggles with dynamic MCP imports.

**Decision**: **Defer** standalone binary. Document `pipx install omega-meditation` as primary install method.

---

### Phase 6: Cross-Pillar Integration & Verification (3 hours)
*Dependencies: All previous phases complete*

#### 6.1 P3 Engineering — CI/CD Pipeline
**What P1 delivers to P3**:
- `uv.lock` file for reproducible builds
- GitHub Actions workflows for test + publish
- `make temple-grade` integration in CI

**File to create**: `.github/workflows/ci.yml`
```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync --frozen
      - run: make test
      - run: make temple-grade
      - run: make heritage-map
      - run: make sovereignty
```

#### 6.2 P4 Integration — MCP Hub Verification
**What P1 delivers to P4**:
- Working `omega-hub` container with health checks
- MCP tool wiring fixed (Phase 1.4)
- OpenCode slash command registered

**Verification command**:
```bash
# In OpenCode session
/omega-meditation "Test problem" --dry-run --mode opencode
# Should execute stages 0-7 with real MCP tool calls
```

#### 6.3 P5 Governance — Mandate Compliance Check
**What P1 delivers to P5**:
- M6: Podman Quadlet uses `UserNS=keep-id` + `User=1000`, NO `:U` flag ✅
- M16: No hardcoded paths in `src/omega/` — all paths via `PROJECT_ROOT` or config ✅
- M23: No soft failures — MCP tool calls raise on failure, not return dry-run ✅

**Verification**: `make temple-grade` must pass T6 (AnyIO only), T10 (Atomic writes)

---

## 📋 Complete File Inventory

### New Files to Create
| Phase | File Path | Purpose |
|-------|-----------|---------|
| 1.1 | `.opencode/commands/omega-meditation.md` | Slash command definition |
| 1.2 | `~/.config/opencode/skills/autonomous-meditation-pipeline/SKILL.md` | Global skill manifest |
| 1.2 | `~/.config/opencode/skills/autonomous-meditation-pipeline/triggers.yaml` | Auto-invocation triggers |
| 1.3 | `opencode.json` (modified) | Agent permissions for skill tool |
| 1.4 | `src/omega/skills/opencode_client.py` | MCP Hub client adapter |
| 1.4 | `src/omega/skills/autonomous_meditation_pipeline.py` (modified) | Use new client adapter |
| 2.1 | `~/.config/containers/systemd/omega-hub.container` | Podman Quadlet for MCP Hub |
| 2.2 | `~/.config/systemd/user/searxng.service` | SearXNG systemd service |
| 2.2 | `~/.config/systemd/user/firecrawl.service` | Firecrawl systemd service |
| 2.3 | `mcp_servers/omega_hub/server.py` (modified) | Health check endpoints |
| 2.4 | `~/.config/logrotate/omega-engine` | Log rotation config |
| 3.1 | `scripts/opencode-compaction-guard.py` | Pre-compaction state save |
| 3.2 | `scripts/opencode-hydration.py` | Session restore |
| 3.3 | `scripts/opencode-wrapper.sh` | OpenCode wrapper |
| 4.2 | `scripts/install-global-skill.sh` | Isolated skill venv installer |
| 4.3 | `packages/omega-meditation/DEPENDENCY_POLICY.md` | Version pinning policy |
| 5.1 | `.github/workflows/publish-pypi.yml` | PyPI trusted publishing |
| 5.2 | `homebrew-omega/Formula/omega-meditation.rb` | Homebrew formula |
| 5.2 | `.github/workflows/homebrew.yml` | Homebrew tap update |
| 6.1 | `.github/workflows/ci.yml` | CI pipeline |

### Files to Modify
| File | Changes |
|------|---------|
| `opencode.json` | Add `permission.tool.skill`, `permission.agent.*.skill` |
| `src/omega/skills/autonomous_meditation_pipeline.py` | Replace `PlatformClients.from_opencode()` with `OpenCodeMCPClient` |
| `mcp_servers/omega_hub/server.py` | Add `/health` and `/ready` endpoints |
| `packages/omega-meditation/pyproject.toml` | Verify version, entry points, optional deps |

---

## ⏱️ Time Estimates Summary

| Phase | Tasks | Est. Hours | Cumulative |
|-------|-------|------------|------------|
| 0 | Foundation & Verification | 2 | 2 |
| 1 | OpenCode Integration | 4 | 6 |
| 2 | Container & Deployment | 6 | 12 |
| 3 | Compaction Resilience | 3 | 15 |
| 4 | Dependency Management | 2 | 17 |
| 5 | Distribution & Publishing | 4 | 21 |
| 6 | Cross-Pillar Integration | 3 | 24 |
| **Total** | | **~24 hours** | |

---

## ⚠️ Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| MCP Hub tool wiring fails (Phase 1.4) | High | P0 — Blocks all pipeline execution | Debug `_require_service()` and `oracle` singleton init first; fallback to CLI mode |
| OpenCode compaction hooks don't exist | High | P1 — Session state loss | Implement best-effort wrapper; document limitation; track OpenCode plugin API |
| Podman Quadlet permission issues (M6) | Medium | P1 — Container can't write to host volumes | Test `UserNS=keep-id` + `User=1000` without `:U` flag; verify UID mapping |
| PyPI trusted publishing setup fails | Low | P1 — Manual token fallback | Document manual `uv publish` with API token as backup |
| Homebrew formula test fails | Medium | P2 — Formula rejected | Test formula locally with `brew install --build-from-source ./Formula/omega-meditation.rb` |
| Cross-pillar integration gaps | Medium | P1 — CI fails | Run `make temple-grade` after each phase; involve P3/P4/P5 early |

---

## ✅ Quality Gates (Per Phase)

| Phase | Gates |
|-------|-------|
| 0 | `uv build` succeeds, CLI dry-run works, MCP tools return real data |
| 1 | `/omega-meditation` slash command appears in OpenCode, skill triggers fire, MCP calls return real results |
| 2 | `systemctl --user start omega-hub` works, health endpoint returns 200, logs rotate |
| 3 | Compaction guard writes `session_gnosis.md`, hydration restores context |
| 4 | `uv lock --upgrade` produces reproducible lockfile, global skill installs in isolated venv |
| 5 | `pipx install omega-meditation` works, `brew install xoe-novai/omega/omega-meditation` works |
| 6 | `make test && make temple-grade && make heritage-map && make sovereignty` all pass |

---

## 🔗 Cross-Pillar Integration Points

| Pillar | What P1 Delivers | What P1 Needs |
|--------|------------------|---------------|
| **P3 Engineering** | CI/CD workflows, reproducible builds, `uv.lock` | CI runner access, test matrix config |
| **P4 Integration** | Working MCP Hub container, fixed tool wiring, slash command | MCP protocol compliance verification |
| **P5 Governance** | M6-compliant containers, M16-compliant paths, M23 hard-fail behavior | Mandate audit sign-off |
| **P6 Cognition** | Pipeline executes real oracle/search calls | Oracle routing verification |
| **P7 Context** | Session gnosis persistence across compaction | Soul distillation integration (Stage 6) |
| **P8 Observability** | Health endpoints, structured logs | Metrics export format |
| **P9 Orchestration** | Hivemind-aware skill triggers | Handoff protocol for multi-agent runs |
| **P10 Validation** | Temple-Grade gates in CI | Chaos test scenarios |

---

## 🎯 Next Actions (Immediate)

1. **Run Phase 0 verification** — Confirm package builds and MCP tools work
2. **Debug MCP tool wiring** — Fix `PlatformClients.from_opencode()` to use proper MCP client
3. **Create slash command** — `.opencode/commands/omega-meditation.md`
4. **Configure agent permissions** — Update `opencode.json`
5. **Begin container setup** — Podman Quadlet for omega-hub

---

## 📝 Session Gnosis (L1→L2→L3)

**L1 Narrative**: Created comprehensive P1 Infrastructure Implementation Plan for the Autonomous Meditation Pipeline. Identified 8 critical gaps from current state to fully deployed product. Structured 6 phases over ~24 hours with explicit file paths, commands, and quality gates.

**L2 Insight**: The biggest blocker is MCP Hub tool wiring — the pipeline's `PlatformClients.from_opencode()` tries to import MCP tool functions directly, but they're registered as MCP tools (JSON-RPC), not Python callables. This must be fixed before any OpenCode integration works. The compaction resilience is a known OpenCode limitation requiring wrapper workarounds.

**L3 Principle**: **L3-InfrastructureAsProduct**: Infrastructure is not "plumbing" — it's the product delivery mechanism. Every gap between "engine works" and "user runs one command" is a product defect. P1 owns the entire critical path from source to installed binary.

---

*⬡ OMEGA ⬡ PILLAR P1 ⬡ INFRASTRUCTURE ⬡ trc_p1_infra_plan ⬡ 2026-07-19*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: P1 | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
