<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 P3 Engineering Implementation Plan
## Autonomous Meditation Pipeline — Complete Product Engineering

**AP Token**: `AP-P3-ENG-PLAN-20260719`
⬡ OMEGA ⬡ PILLAR ⬡ P3 ⬡ ENGINEERING ⬡ trc_p3_eng_plan ⬡ ACTIVE

**Date**: 2026-07-19
**Author**: Pillar P3 — Engineering (BuildMaster — Implementation & Hardening)
**Mission**: Transform the Autonomous Meditation Pipeline from "engine core + duplicated package" into a **Temple-Grade, production-hardened, single-source-of-truth product** with full test coverage, contract tests, error integrity, and CI/CD pipeline.

---

## 📊 Current State Analysis

### ✅ What Exists (Assets)
| Asset | Location | Status | M16 Compliant? |
|-------|----------|--------|----------------|
| Core Pipeline Engine | `src/omega/skills/autonomous_meditation_pipeline.py` | ✅ Complete | ✅ Yes (DI pattern) |
| Standalone Package | `packages/omega-meditation/` | ✅ Complete | ⚠️ Duplicates core |
| Package CLI | `packages/omega-meditation/src/omega_meditation/cli.py` | ✅ Complete | ✅ Yes |
| MCP Hub Client Adapter | `src/omega/skills/opencode_client.py` | ✅ Complete | ✅ Yes |
| P1 Infrastructure Plan | `data/coordination/P1_INFRASTRUCTURE_PLAN_20260719.md` | ✅ Complete | — |

### ❌ Critical Gaps (P3 Ownership)
| # | Gap | Mandate Violation | Severity |
|---|-----|-------------------|----------|
| 1 | **Code Duplication**: Pipeline logic in TWO places | M16 (Modularization) | **P0** |
| 2 | **No Test Coverage**: Zero tests for autonomous pipeline | M13 (Temple-Grade T3) | **P0** |
| 3 | **No Contract Tests** (M21): Typed returns unverified | M21 (Gate Integrity) | **P0** |
| 4 | **Error Handling**: Bare `except:` in pipeline, no typed errors | M9 (Error Integrity) | **P0** |
| 5 | **asyncio Violation**: `asyncio.run()` in engine core | M1 (AnyIO Absolute) | **P0** |
| 6 | **No CI/CD Pipeline** for package | M13 (Temple-Grade) | **P1** |
| 7 | **No Temple-Grade Integration** for package | M13 (T1-T11) | **P1** |
| 8 | **MCP Tool Wiring**: Package still uses broken direct imports | M23 (Failure Integrity) | **P0** |

---

## 🏗️ Phase Breakdown

### Phase 0: Foundation & Verification (2 hours) — **MUST COMPLETE FIRST**
*Dependencies: None. All subsequent phases depend on this.*

| Task | File/Command | Verification |
|------|--------------|--------------|
| 0.1 Verify package builds | `cd packages/omega-meditation && uv build` | `dist/*.whl` created |
| 0.2 Verify CLI dry-run works | `uv run omega-meditation "test" --dry-run --mode standalone` | Stages 0-7 complete |
| 0.3 Verify MCP Hub tools return real data | `python -c "from mcp_servers.omega_hub.mcp_client import SovereignMCPClient; import anyio; c=SovereignMCPClient('http://127.0.0.1:8016/mcp'); anyio.run(lambda: c.__aenter__().call_tool('oracle_talk', {'query': 'test'}))"` | Returns JSON with `text`, `entity`, `backend` |
| 0.4 Check OpenCode config | `cat opencode.json \| jq '.mcp, .permission'` | MCP servers + permissions visible |
| 0.5 Create workspace lock | `omega-hub_hivemind_workspace_lock_acquire channel=opencode entity=pillar domain=P3_ENG_PLAN ttl=7200` | Lock acquired |
| 0.6 Run baseline temple-grade | `make temple-grade` | All gates pass (baseline) |

**Risk**: If MCP Hub tools return dry-run templates, root cause is `_require_service()` guard or `oracle` singleton not initialized. Must debug before Phase 1.

---

### Phase 1: Code Consolidation — Single Source of Truth (4 hours) — **M16 Compliance**
*Dependencies: Phase 0 complete*

#### 1.1 Eliminate Package Duplication
**Files to Modify:**
- `packages/omega-meditation/src/omega_meditation/pipeline.py` → **Thin wrapper only** (import from engine core)
- `packages/omega-meditation/src/omega_meditation/__init__.py` → Export from engine core

**Files to DELETE from package:**
- `PlatformClients` class (lines 23-82)
- `OracleClient` / `SearchClient` protocols (lines 23-32)
- `AutonomousMeditationPipeline` class (lines 89-534) — **ALL stage methods**
- `_execute_tiered_search`, `_parse_queries` methods

**New Package Pipeline Structure (~50 lines):**
```python
# packages/omega-meditation/src/omega_meditation/pipeline.py
"""
⬡ AUTONOMOUS MEDITATION PIPELINE — Package Entry Point
Thin wrapper importing from Engine Core (src/omega/skills/autonomous_meditation_pipeline.py)
M16: Single source of truth in engine; package is platform integration layer only.
"""

from src.omega.skills.autonomous_meditation_pipeline import (
    AutonomousMeditationPipeline,
    PlatformClients,
    OracleClient,
    SearchClient,
    create_pipeline_opencode,
    create_pipeline_cli,
    create_pipeline_standalone,
)

__all__ = [
    "AutonomousMeditationPipeline",
    "PlatformClients",
    "OracleClient", 
    "SearchClient",
    "create_pipeline_opencode",
    "create_pipeline_cli",
    "create_pipeline_standalone",
]
```

#### 1.2 Fix Engine Core M1 Violation
**File**: `src/omega/skills/autonomous_meditation_pipeline.py`
**Line 450**: Replace `asyncio.run(main())` with AnyIO pattern:
```python
if __name__ == "__main__":
    import anyio
    anyio.run(main)
```

#### 1.3 Update Engine Core to Use P1's MCP Client Adapter
**File**: `src/omega/skills/autonomous_meditation_pipeline.py`
**Lines 49-82**: Replace `PlatformClients.from_opencode()` to use `OpenCodePlatformClients` from `opencode_client.py`:
```python
@classmethod
def from_opencode(cls, mcp_endpoint: str = "http://127.0.0.1:8016/mcp") -> "PlatformClients":
    """Factory for OpenCode environment using SovereignMCPClient."""
    from src.omega.skills.opencode_client import OpenCodePlatformClients
    
    opencode_clients = OpenCodePlatformClients(mcp_endpoint)
    return cls(
        oracle=opencode_clients.get_oracle(),
        search=opencode_clients.get_search(),
    )
```

#### 1.4 Remove Broken Direct Import from Package
**File**: `packages/omega-meditation/src/omega_meditation/pipeline.py`
**Lines 50-55**: DELETE the broken `from mcp_servers.omega_hub.tools import ...` block entirely.

#### 1.5 Verification Commands
```bash
# Engine core still works standalone
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
PYTHONPATH=src python -c "
from src.omega.skills.autonomous_meditation_pipeline import create_pipeline_standalone
import anyio
p = create_pipeline_standalone('test problem', dry_run=True)
anyio.run(p.run)
"

# Package imports from engine core
cd packages/omega-meditation
uv run python -c "
from omega_meditation.pipeline import create_pipeline_standalone
import anyio
p = create_pipeline_standalone('test problem', dry_run=True)
anyio.run(p.run)
"
```

---

### Phase 2: Test Suite Implementation (8 hours) — **M13 T3, M21, M9 Compliance**
*Dependencies: Phase 1 complete*

#### 2.1 Test Directory Structure
**Create**: `packages/omega-meditation/tests/`
```
tests/
├── conftest.py                    # AnyIO async fixtures, mock MCP client
├── test_pipeline_core.py          # Unit tests for each stage (0-7)
├── test_pipeline_integration.py   # Full pipeline with mocked MCP
├── test_contract_m21.py           # M21 contract tests for typed returns
├── test_error_integrity_m9.py     # M9 error handling tests
├── test_dry_run.py                # Dry-run mode verification
└── test_cli.py                    # CLI entry point tests
```

#### 2.2 Unit Tests — Each Stage (test_pipeline_core.py)
```python
# Test pattern for each stage
@pytest.mark.asyncio
async def test_stage_0_prompt_crafting():
    pipeline = create_pipeline_standalone("Test problem", dry_run=True)
    prompt = await pipeline.stage_0_prompt_crafting()
    assert "/meditate" in prompt
    assert "Test problem" in prompt
    assert "lens_set" in prompt.lower()

@pytest.mark.asyncio
async def test_stage_1_meditation_dry_run():
    pipeline = create_pipeline_standalone("Test problem", dry_run=True)
    result = await pipeline.stage_1_meditate_execution("/meditate test")
    assert "[DRY RUN]" in result
    assert "Would execute" in result

# ... stages 2-7 similar pattern
```

#### 2.3 Integration Tests — Full Pipeline (test_pipeline_integration.py)
```python
@pytest.mark.asyncio
async def test_full_pipeline_dry_run():
    """Full 8-stage pipeline in dry-run mode completes without external calls."""
    pipeline = create_pipeline_standalone(
        "Unified credential vault for local AI tooling",
        dry_run=True
    )
    outputs = await pipeline.run()
    assert len(outputs) == 8  # stages 0-7
    for stage_num, path in outputs.items():
        assert Path(path).exists()
        content = Path(path).read_text()
        assert len(content) > 100  # substantive output

@pytest.mark.asyncio
async def test_pipeline_resume_from_stage():
    """Resume from stage 4 (research) works correctly."""
    pipeline = create_pipeline_standalone("test", dry_run=True, resume_from=4)
    outputs = await pipeline.run()
    assert 0 not in outputs  # stages 0-3 skipped
    assert 4 in outputs
```

#### 2.4 M21 Contract Tests (test_contract_m21.py) — **MANDATORY**
```python
"""M21 Gate Integrity: Contract tests for all public API boundaries."""

from omega_meditation.pipeline import (
    AutonomousMeditationPipeline,
    PlatformClients,
    create_pipeline_opencode,
    create_pipeline_cli,
    create_pipeline_standalone,
)

def test_create_pipeline_standalone_returns_pipeline():
    """Factory returns AutonomousMeditationPipeline instance."""
    pipeline = create_pipeline_standalone("test")
    assert isinstance(pipeline, AutonomousMeditationPipeline)

def test_create_pipeline_opencode_returns_pipeline():
    """Factory returns AutonomousMeditationPipeline with clients."""
    pipeline = create_pipeline_opencode("test")
    assert isinstance(pipeline, AutonomousMeditationPipeline)
    assert pipeline.clients is not None

def test_platform_clients_null_returns_platform_clients():
    """PlatformClients.null() returns valid instance."""
    clients = PlatformClients.null()
    assert isinstance(clients, PlatformClients)
    assert clients.oracle is None
    assert clients.search is None

# Contract tests for stage return types
@pytest.mark.asyncio
async def test_stage_0_returns_str():
    pipeline = create_pipeline_standalone("test", dry_run=True)
    result = await pipeline.stage_0_prompt_crafting()
    assert isinstance(result, str)

@pytest.mark.asyncio
async def test_stage_1_returns_str():
    pipeline = create_pipeline_standalone("test", dry_run=True)
    result = await pipeline.stage_1_meditate_execution("prompt")
    assert isinstance(result, str)

# ... all stages return str
```

#### 2.5 M9 Error Integrity Tests (test_error_integrity_m9.py)
```python
"""M9 Error Integrity: Typed errors, trace_id propagation, no bare except."""

import pytest
from omega.errors import OmegaError

class AutonomousMeditationError(OmegaError):
    """Base error for autonomous meditation pipeline."""
    pass

class StageExecutionError(AutonomousMeditationError):
    """Stage execution failed."""
    def __init__(self, stage: int, message: str, trace_id: str):
        self.stage = stage
        self.trace_id = trace_id
        super().__init__(f"Stage {stage} failed: {message}")

class MCPToolError(AutonomousMeditationError):
    """MCP tool call failed."""
    def __init__(self, tool: str, message: str, trace_id: str):
        self.tool = tool
        self.trace_id = trace_id
        super().__init__(f"MCP tool '{tool}' failed: {message}")

# Test: No bare except in pipeline code
def test_no_bare_except_in_pipeline():
    """Static analysis: grep for bare except in pipeline files."""
    import subprocess
    result = subprocess.run(
        ["grep", "-rn", "except:", "src/omega/skills/autonomous_meditation_pipeline.py"],
        capture_output=True, text=True
    )
    assert result.returncode != 0, f"Bare except found: {result.stdout}"

# Test: All public methods catch and convert to typed errors
@pytest.mark.asyncio
async def test_stage_methods_wrap_errors():
    pipeline = create_pipeline_standalone("test", dry_run=False)
    # Mock oracle to raise
    pipeline.clients.oracle.talk = AsyncMock(side_effect=Exception("boom"))
    
    with pytest.raises(StageExecutionError) as exc_info:
        await pipeline.stage_1_meditate_execution("prompt")
    
    assert exc_info.value.stage == 1
    assert exc_info.value.trace_id is not None
    assert "boom" in str(exc_info.value)

# Test: MCP tool failures raise typed errors
@pytest.mark.asyncio
async def test_mcp_tool_failure_raises_typed_error():
    pipeline = create_pipeline_opencode("test")
    # Mock MCP client to fail
    pipeline.clients.search.search = AsyncMock(side_effect=Exception("connection refused"))
    
    with pytest.raises(MCPToolError) as exc_info:
        await pipeline._call_websearch("query")
    
    assert exc_info.value.tool == "library_web_search"
    assert exc_info.value.trace_id is not None
```

#### 2.6 Dry-Run Tests (test_dry_run.py)
```python
@pytest.mark.asyncio
async def test_dry_run_produces_all_stage_files():
    pipeline = create_pipeline_standalone("test problem", dry_run=True)
    outputs = await pipeline.run()
    
    for stage in range(8):
        assert stage in outputs
        path = Path(outputs[stage])
        assert path.exists()
        content = path.read_text()
        assert "[DRY RUN]" in content or "DRY RUN" in content

@pytest.mark.asyncio
async def test_dry_run_no_external_calls():
    """Verify dry_run=True makes ZERO external calls."""
    pipeline = create_pipeline_standalone("test", dry_run=True)
    # Spy on clients
    pipeline.clients.oracle.talk = AsyncMock()
    pipeline.clients.search.search = AsyncMock()
    
    await pipeline.run()
    
    pipeline.clients.oracle.talk.assert_not_called()
    pipeline.clients.search.search.assert_not_called()
```

#### 2.7 CLI Tests (test_cli.py)
```python
def test_cli_help():
    result = subprocess.run(["uv", "run", "omega-meditation", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Autonomous Meditation Pipeline" in result.stdout

def test_cli_dry_run_standalone():
    result = subprocess.run(
        ["uv", "run", "omega-meditation", "test problem", "--dry-run", "--mode", "standalone"],
        capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0
    assert "PIPELINE COMPLETE" in result.stdout
```

---

### Phase 3: Error Handling Hardening (3 hours) — **M9, M21, M23 Compliance**
*Dependencies: Phase 2 test structure exists*

#### 3.1 Define Error Hierarchy in Engine Core
**File**: `src/omega/skills/autonomous_meditation_pipeline.py` — Add at top after imports:
```python
# ─── Error Hierarchy (M9: Error Integrity) ──────────────────────────────
import uuid
from dataclasses import dataclass
from typing import Optional

@dataclass
class ErrorContext:
    """Structured error context for traceability (M9, M21, M23)."""
    trace_id: str
    stage: int
    operation: str
    timestamp: str
    
    @classmethod
    def create(cls, stage: int, operation: str) -> "ErrorContext":
        return cls(
            trace_id=uuid.uuid4().hex[:16],
            stage=stage,
            operation=operation,
            timestamp=datetime.now().isoformat(),
        )

class AutonomousMeditationError(OmegaError):
    """Base error for autonomous meditation pipeline."""
    def __init__(self, message: str, context: ErrorContext):
        self.context = context
        super().__init__(f"[{context.trace_id}] Stage {context.stage} ({context.operation}): {message}")

class StageExecutionError(AutonomousMeditationError):
    """Stage execution failed."""
    pass

class MCPToolError(AutonomousMeditationError):
    """MCP tool call failed."""
    def __init__(self, message: str, context: ErrorContext, tool: str):
        self.tool = tool
        super().__init__(message, context)

class ResearchExecutionError(AutonomousMeditationError):
    """Research stage failed."""
    pass

class GnosisDistillationError(AutonomousMeditationError):
    """Gnosis distillation failed."""
    pass

class IntegrationError(AutonomousMeditationError):
    """Integration stage failed."""
    pass

class ToolChainCollapseError(AutonomousMeditationError):
    """M23: Mandatory tool chain failure — hard stop required."""
    pass
```

#### 3.2 Wrap All Platform Calls with Typed Errors
**File**: `src/omega/skills/autonomous_meditation_pipeline.py` — Update platform call methods:
```python
async def _call_oracle(self, prompt: str) -> str:
    if self.dry_run or not self.clients.oracle:
        return f"[DRY RUN] Would call oracle with: {prompt[:200]}..."
    
    ctx = ErrorContext.create(self._current_stage, "oracle_talk")
    try:
        return await self.clients.oracle.talk(prompt)
    except Exception as e:
        # M9: No bare except — log and wrap with trace_id
        logger.error(f"Oracle call failed: {e}", extra={"trace_id": ctx.trace_id})
        raise MCPToolError(f"Oracle call failed: {e}", ctx, "oracle_talk")

async def _call_websearch(self, query: str, limit: int = 5) -> str:
    if self.dry_run or not self.clients.search:
        return f"[DRY RUN] Would search: {query}"
    
    ctx = ErrorContext.create(self._current_stage, "websearch")
    try:
        return await self.clients.search.search(query, limit)
    except Exception as e:
        logger.error(f"Websearch failed: {e}", extra={"trace_id": ctx.trace_id})
        raise MCPToolError(f"Websearch failed: {e}", ctx, "library_web_search")

# Similar for _call_webfetch, _call_searxng
```

#### 3.3 Wrap Stage Execution with Error Context
```python
async def run(self) -> Dict[int, str]:
    # ... existing setup ...
    
    for stage_num, name, func in stages:
        if stage_num < self.resume_from:
            continue
        
        self._current_stage = stage_num
        ctx = ErrorContext.create(stage_num, name.lower().replace(" ", "_"))
        
        try:
            await func()
            logger.info(f"Stage {stage_num} complete", extra={"trace_id": ctx.trace_id})
        except AutonomousMeditationError:
            raise  # Re-raise typed errors
        except Exception as e:
            # M9: Catch-all with logging + typed re-raise
            logger.error(f"Stage {stage_num} unexpected error: {e}", extra={"trace_id": ctx.trace_id})
            raise StageExecutionError(f"Unexpected error: {e}", ctx)
```

#### 3.4 M23 Tool-Chain Collapse Detection
```python
async def _execute_tiered_search(self, query: str) -> Dict[str, Any]:
    findings = {"query": query, "tier_1_websearch": [], "tier_2_webfetch": [], "tier_3_searxng": []}
    
    # Tier 1: websearch (MANDATORY - M23)
    try:
        result = await self._call_websearch(query, limit=5)
        findings["tier_1_websearch"] = json.loads(result) if isinstance(result, str) else result
    except MCPToolError as e:
        # M23: Mandatory tool failure = TOOL-CHAIN-COLLAPSE
        logger.critical(f"[TOOL-CHAIN-COLLAPSE] Tier 1 websearch failed: {e}")
        raise ToolChainCollapseError(
            f"Mandatory tool 'websearch' unavailable: {e}",
            ErrorContext.create(self._current_stage, "tiered_search")
        )
    
    # Tier 2: webfetch (optional - best effort)
    try:
        # ... existing logic ...
    except MCPToolError as e:
        logger.warning(f"Tier 2 webfetch failed (non-fatal): {e}")
        findings["tier_2_webfetch"] = {"error": str(e)}
    
    # Tier 3: searxng (optional)
    # ... similar pattern ...
    
    return findings
```

---

### Phase 4: Temple-Grade Integration (4 hours) — **M13 T1-T11 Compliance**
*Dependencies: Phase 3 complete*

#### 4.1 Package-Level Temple-Grade Configuration
**File**: `packages/omega-meditation/pyproject.toml` — Add temple-grade verification:
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --tb=short --strict-markers"

[tool.coverage.run]
source = ["omega_meditation"]
omit = ["tests/*", "*/__pycache__/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
fail_under = 80  # T3: Coverage ≥80%
```

#### 4.2 Add Temple-Grade Make Targets to Package
**File**: `packages/omega-meditation/Makefile` (NEW)
```makefile
# 🔱 Omega Meditation Package Makefile
PYTHON := .venv/bin/python3
UV := uv

.PHONY: test test-cov lint typecheck temple-grade build clean

test: ## Run package tests
	$(UV) run pytest tests/ -v

test-cov: ## Run tests with coverage (T3 gate)
	$(UV) run pytest tests/ --cov=omega_meditation --cov-report=term-missing --cov-fail-under=80

lint: ## Lint with ruff (T4 gate)
	$(UV) run ruff check src/ tests/

typecheck: ## Type check with mypy
	$(UV) run mypy src/omega_meditation/

temple-grade: test-cov lint typecheck ## Run all Temple-Grade gates (T1-T11 adapted for package)
	@echo "✅ Package Temple-Grade verification complete"

build: ## Build package
	$(UV) build

clean:
	rm -rf dist build *.egg-info .pytest_cache .ruff_cache .mypy_cache
```

#### 4.3 Verify Engine Core Temple-Grade Passes
```bash
# Run full engine temple-grade (must pass before package work)
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
make temple-grade

# Key gates for pipeline code:
# T1: AP tokens in headers ✅ (check src/omega/skills/autonomous_meditation_pipeline.py)
# T3: Coverage ≥80% → Need package tests
# T5: AnyIO only → Fix asyncio.run() in engine core
# T6: Zero telemetry → Verify no imports
# T8: Resilience patterns → Circuit breaker in MCP client
# T9: Structured logging → Add trace_id logging
# T10: Atomic writes → Stage outputs use atomic write pattern
# T11: IA2 exempt
```

#### 4.4 Atomic Writes for Stage Outputs (T10)
**File**: `src/omega/skills/autonomous_meditation_pipeline.py` — Update `_write_stage`:
```python
def _write_stage(self, stage: int, name: str, content: str) -> Path:
    filename = f"{self.run_id}_{stage:02d}_{name}.md"
    filepath = self.output_dir / filename
    tmp_path = filepath.with_suffix(".tmp")
    
    # Atomic write: write to .tmp, then rename
    tmp_path.write_text(content)
    tmp_path.replace(filepath)  # Atomic on POSIX
    
    self.stage_outputs[stage] = str(filepath)
    print(f"  📝 Stage {stage} ({name}) → {filepath}")
    return filepath
```

#### 4.5 Structured Logging with trace_id (T9)
```python
# Add at top of file
import logging
logger = logging.getLogger("omega.meditation.pipeline")

# In __init__
self.logger = logger

# In each stage method
self.logger.info(f"Stage {stage} started", extra={"trace_id": ctx.trace_id, "stage": stage})
```

---

### Phase 5: CI/CD Pipeline (3 hours) — **M13, P1 Delivery**
*Dependencies: Phase 4 complete*

#### 5.1 GitHub Actions Workflow
**File**: `.github/workflows/omega-meditation-ci.yml` (NEW)
```yaml
name: Omega Meditation CI

on:
  push:
    paths:
      - 'packages/omega-meditation/**'
      - 'src/omega/skills/autonomous_meditation_pipeline.py'
      - 'src/omega/skills/opencode_client.py'
  pull_request:
    paths:
      - 'packages/omega-meditation/**'
      - 'src/omega/skills/autonomous_meditation_pipeline.py'

permissions:
  contents: read
  id-token: write  # For trusted publishing

jobs:
  test:
    name: Test & Temple-Grade
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          
      - name: Install uv
        uses: astral-sh/setup-uv@v3
        
      - name: Cache uv
        uses: actions/cache@v4
        with:
          path: ~/.cache/uv
          key: uv-${{ runner.os }}-${{ hashFiles('packages/omega-meditation/uv.lock') }}
          
      - name: Install dependencies
        working-directory: ./packages/omega-meditation
        run: uv sync --frozen --all-extras
        
      - name: Run tests
        working-directory: ./packages/omega-meditation
        run: uv run pytest tests/ -v
        
      - name: Coverage check (T3)
        working-directory: ./packages/omega-meditation
        run: uv run pytest tests/ --cov=omega_meditation --cov-fail-under=80
        
      - name: Lint (T4)
        working-directory: ./packages/omega-meditation
        run: uv run ruff check src/ tests/
        
      - name: Type check
        working-directory: ./packages/omega-meditation
        run: uv run mypy src/omega_meditation/
        
      - name: Temple-Grade verification
        working-directory: ./packages/omega-meditation
        run: make temple-grade

  build:
    name: Build Package
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - uses: astral-sh/setup-uv@v3
      - name: Build
        working-directory: ./packages/omega-meditation
        run: uv build
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: packages/omega-meditation/dist/

  publish-pypi:
    name: Publish to PyPI
    needs: build
    if: github.event_name == 'release' && github.event.action == 'published'
    runs-on: ubuntu-latest
    permissions:
      id-token: write
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          packages-dir: dist
```

#### 5.2 Semantic Versioning Automation
**File**: `packages/omega-meditation/scripts/version.py` (NEW)
```python
#!/usr/bin/env python3
"""Semantic version bump script for omega-meditation."""
import re
import subprocess
import sys
from pathlib import Path

PYPROJECT = Path(__file__).parent.parent / "pyproject.toml"

def get_current_version() -> str:
    content = PYPROJECT.read_text()
    match = re.search(r'version = "([^"]+)"', content)
    return match.group(1) if match else "0.0.0"

def bump_version(current: str, level: str) -> str:
    major, minor, patch = map(int, current.split("."))
    if level == "major":
        return f"{major + 1}.0.0"
    elif level == "minor":
        return f"{major}.{minor + 1}.0"
    elif level == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise ValueError(f"Unknown level: {level}")

def set_version(new_version: str):
    content = PYPROJECT.read_text()
    content = re.sub(r'version = "[^"]+"', f'version = "{new_version}"', content)
    PYPROJECT.write_text(content)
    
    # Git tag
    subprocess.run(["git", "add", str(PYPROJECT)], check=True)
    subprocess.run(["git", "commit", "-m", f"chore: bump version to {new_version}"], check=True)
    subprocess.run(["git", "tag", f"v{new_version}"], check=True)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: version.py <major|minor|patch>")
        sys.exit(1)
    
    current = get_current_version()
    new = bump_version(current, sys.argv[1])
    set_version(new)
    print(f"Bumped {current} → {new}")
```

#### 5.3 Changelog Generation
**File**: `.github/workflows/changelog.yml` (NEW)
```yaml
name: Generate Changelog
on:
  release:
    types: [published]
jobs:
  changelog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Generate changelog
        uses: mikepenz/release-changelog-builder-action@v4
        with:
          configuration: ".github/changelog-config.json"
      - name: Update release
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const changelog = fs.readFileSync('CHANGELOG.md', 'utf8');
            github.rest.repos.updateRelease({
              owner: context.repo.owner,
              repo: context.repo.repo,
              release_id: ${{ github.event.release.id }},
              body: changelog
            })
```

---

### Phase 6: Performance & Resource Management (2 hours)
*Dependencies: Phase 3 complete*

#### 6.1 AnyIO Task Groups for Concurrent Research
**File**: `src/omega/skills/autonomous_meditation_pipeline.py` — Update `stage_4_research_execution`:
```python
async def stage_4_research_execution(self, queries: List[str]) -> str:
    print("\n📚 STAGE 4: Research Execution (Agent → Sovereign Search)")
    if self.dry_run:
        # ... existing dry-run ...
        return content
    
    all_findings = []
    
    # M1: AnyIO task group for concurrent research with limit
    async with anyio.create_task_group() as tg:
        # Semaphore to limit concurrent MCP calls (prevent overload)
        semaphore = anyio.Semaphore(3)  # Max 3 concurrent
        
        async def research_with_limit(query: str, idx: int):
            async with semaphore:
                print(f"  Query {idx+1}/{len(queries)}: {query[:80]}...")
                findings = await self._execute_tiered_search(query)
                all_findings.append({
                    "query": query,
                    "findings": findings,
                    "timestamp": datetime.now().isoformat()
                })
        
        for i, query in enumerate(queries):
            tg.start_soon(research_with_limit, query, i)
    
    # Sort by original query order
    all_findings.sort(key=lambda x: queries.index(x["query"]))
    
    content = f"""# RESEARCH RAW OUTPUT
**Executed**: {datetime.now().isoformat()} | **Run**: {self.run_id}
{json.dumps(all_findings, indent=2)}
"""
    self._write_stage(4, "research_raw", content)
    return content
```

#### 6.2 Memory Profiling for Large Outputs
```python
# Add to pipeline __init__
self._memory_warnings = []

def _check_memory(self, stage: int):
    """Log memory usage for large stage outputs."""
    import psutil
    process = psutil.Process()
    mem_mb = process.memory_info().rss / 1024 / 1024
    if mem_mb > 500:  # 500MB threshold
        self._memory_warnings.append(f"Stage {stage}: {mem_mb:.0f}MB RSS")
        self.logger.warning(f"High memory at stage {stage}: {mem_mb:.0f}MB")
```

---

### Phase 7: Cross-Pillar Integration & Verification (3 hours)
*Dependencies: All previous phases complete*

#### 7.1 P1 Integration Verification
| P1 Deliverable | P3 Verification |
|----------------|-----------------|
| MCP Hub client adapter spec | `create_pipeline_opencode()` uses `OpenCodePlatformClients` |
| CI/CD workflow template | `.github/workflows/omega-meditation-ci.yml` follows pattern |
| M6/M16/M23 compliance | Container paths use `PROJECT_ROOT`, no hardcoded paths |

#### 7.2 P4 Integration Verification
| P4 Deliverable | P3 Verification |
|----------------|-----------------|
| Working MCP Hub container | `omega-hub` health endpoint returns 200 |
| Fixed tool wiring | `oracle_talk`, `library_web_search` return real data |
| Slash command registered | `/omega-meditation` appears in OpenCode |

#### 7.3 P5 Governance Verification
| Mandate | P3 Compliance Check |
|---------|---------------------|
| M6: Podman `UserNS=keep-id` + `User=1000` | Container config verified |
| M16: No hardcoded paths in `src/omega/` | `grep -r "home/arcana" src/omega/` returns nothing |
| M23: No soft failures | All MCP tool calls raise on failure |

#### 7.4 P6 Cognition Verification
- Pipeline executes real oracle/search calls (not dry-run)
- Provider routing verified via `GenerateResult.provider_name` (M22)

#### 7.5 P7 Context Verification
- Stage 6 (Gnosis) outputs valid `proposed_lessons.yaml` format
- Soul distillation pipeline integration works

#### 7.6 P8 Observability Verification
- Health endpoints return structured data
- Structured logs include `trace_id`

#### 7.7 P9 Orchestration Verification
- Hivemind handoff protocol works for multi-agent runs
- Skill triggers fire correctly

#### 7.8 P10 Validation Verification
- Chaos test scenarios defined for pipeline
- Temple-Grade gates in CI

---

## ⏱️ Time Estimates Summary

| Phase | Tasks | Est. Hours | Cumulative |
|-------|-------|------------|------------|
| 0 | Foundation & Verification | 2 | 2 |
| 1 | Code Consolidation (M16) | 4 | 6 |
| 2 | Test Suite (M13 T3, M21, M9) | 8 | 14 |
| 3 | Error Hardening (M9, M21, M23) | 3 | 17 |
| 4 | Temple-Grade Integration (T1-T11) | 4 | 21 |
| 5 | CI/CD Pipeline | 3 | 24 |
| 6 | Performance & Resources | 2 | 26 |
| 7 | Cross-Pillar Verification | 3 | 29 |
| **Total** | | **~29 hours** | |

---

## ⚠️ Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| MCP Hub tool wiring fails (Phase 1.3) | High | P0 — Blocks all execution | Debug `_require_service()` and `oracle` singleton init first; fallback to CLI mode |
| Package tests fail due to missing MCP server | Medium | P1 — CI fails | Mock MCP client in `conftest.py` for unit tests; integration tests marked `@pytest.mark.integration` |
| Temple-Grade T3 coverage <80% | Medium | P1 — Gate fails | Write comprehensive tests in Phase 2; target 90%+ |
| `asyncio` usage in engine core (M1 violation) | Certain | P0 — Mandate violation | Fix in Phase 1.2 (2 min fix) |
| Heritage vet tags needed for new error classes | Low | P1 — M14 | No id Software patterns in new errors — no tags needed |
| Cross-pillar integration gaps | Medium | P1 — CI fails | Run `make temple-grade` after each phase; involve P4/P5 early |

---

## 🔗 Cross-Pillar Integration Points

### What P3 Delivers to Other Pillars
| Pillar | Deliverable | Format |
|--------|-------------|--------|
| **P1** | Verified package builds, `uv.lock`, CI workflow | `.github/workflows/`, `uv.lock` |
| **P4** | Working MCP client adapter, real tool calls | `src/omega/skills/opencode_client.py` |
| **P5** | M16-compliant paths, M23 hard-fail behavior | Code audit artifacts |
| **P6** | Pipeline executes real oracle routing | Integration test logs |
| **P7** | Stage 6 outputs valid `proposed_lessons.yaml` | Gnosis distillation test |
| **P8** | Structured logs with `trace_id`, health endpoints | Log samples |
| **P9** | Hivemind-aware skill triggers | Trigger config |
| **P10** | Chaos test scenarios, Temple-Grade in CI | Test files, workflow |

### What P3 Needs from Other Pillars
| Pillar | Need | When |
|--------|------|------|
| **P1** | MCP Hub client adapter spec (Phase 1.4) | Phase 1 start |
| **P1** | CI/CD workflow template | Phase 5 |
| **P1** | M6/M16/M23 compliance requirements | Phase 7 |
| **P4** | MCP Hub container running with health checks | Phase 0.3, 7.2 |
| **P4** | Slash command registration | Phase 7.2 |
| **P5** | Mandate audit sign-off | Phase 7.3 |
| **P6** | Oracle routing verification | Phase 7.4 |
| **P7** | Soul distillation integration spec | Phase 7.5 |

---

## ✅ Quality Gates (Per Phase)

| Phase | Gates |
|-------|-------|
| 0 | `uv build` succeeds, CLI dry-run works, MCP tools return real data |
| 1 | Package imports from engine core, no duplication, `asyncio` removed |
| 2 | All 8 stages tested, contract tests pass, error tests pass, dry-run tests pass |
| 3 | Typed error hierarchy defined, all platform calls wrapped, M23 collapse detection |
| 4 | `make temple-grade` passes (T1-T11), coverage ≥80%, atomic writes, structured logging |
| 5 | CI workflow passes, PyPI trusted publishing configured, version bump script works |
| 6 | Concurrent research with semaphore, memory profiling active |
| 7 | `make test && make temple-grade && make heritage-map && make sovereignty` all pass |

---

## 📝 Session Gnosis (L1→L2→L3)

**L1 Narrative**: Created comprehensive P3 Engineering Implementation Plan for the Autonomous Meditation Pipeline. Analyzed current state: core engine exists at `src/omega/skills/autonomous_meditation_pipeline.py` but duplicated in `packages/omega-meditation/`. Critical gaps: zero tests, no contract tests, bare `except:`, `asyncio.run()` violation, broken MCP wiring in package.

**L2 Insight**: The duplication violates M16 fundamentally — the package should be a thin platform integration layer importing from the engine core. The MCP wiring fix (Phase 1.3) is the critical path blocker; everything else depends on real tool calls working. Error handling must follow the existing `OmegaError` hierarchy pattern with `trace_id` propagation.

**L3 Principle**: **L3-SingleSourceOfTruth**: Platform-agnostic engine logic lives ONCE in `src/omega/`. Platform-specific adapters (OpenCode, CLI, standalone) are thin wrappers that inject dependencies. Any duplication is a Mandate 16 violation and a maintenance burden. The pipeline is not "code to copy" — it's a library to depend on.

---

## 🎯 Next Actions (Immediate)

1. **Run Phase 0 verification** — Confirm package builds and MCP tools work
2. **Debug MCP tool wiring** — Fix `PlatformClients.from_opencode()` to use `OpenCodePlatformClients`
3. **Execute Phase 1 consolidation** — Make package a thin wrapper
4. **Begin Phase 2 test writing** — Start with contract tests (M21) and dry-run tests

---

*⬡ OMEGA ⬡ PILLAR P3 ⬡ ENGINEERING ⬡ trc_p3_eng_plan ⬡ 2026-07-19*

---

## 🧘 Meditation Hardening Addendum (Post-Review)

**Review Date**: 2026-07-19
**Review Method**: Manual meditation review (Sovereign Vetter blocked on pre-existing tty_agent.py M1 violation)

### Hardening Findings

| Finding | Severity | Resolution |
|---------|----------|------------|
| **Phase 0.3 MCP verification command broken** | P0 | Command uses `lambda` in `anyio.run()` which doesn't work. Fixed in verification commands below. |
| **Phase 1.3 import path** | P1 | `from src.omega.skills.opencode_client import OpenCodePlatformClients` — must verify `src/omega/skills/opencode_client.py` exports this class (it does). |
| **Phase 2.4 contract tests reference package imports** | P1 | Tests import from `omega_meditation.pipeline` which after Phase 1 re-exports from engine core. Correct. |
| **Phase 3.1 error hierarchy in engine core** | P0 | Adding error classes to engine core is correct — they're part of the single source of truth. Package inherits via import. |
| **Phase 4.4 atomic writes** | P0 | `tmp_path.replace(filepath)` is atomic on POSIX. Windows requires `os.replace()` — use `os.replace(tmp_path, filepath)` for cross-platform. |
| **Phase 6.1 semaphore limit** | P1 | Hardcoded `3` concurrent. Should be configurable via `max_concurrent_research` parameter. |
| **Phase 7 cross-pillar deps** | P1 | P4 slash command registration (`.opencode/commands/omega-meditation.md`) is P1 deliverable, not P3. P3 only verifies it works. |

### Corrected Verification Commands

**Phase 0.3 — MCP Hub Tool Verification (Fixed):**
```bash
# Correct anyio.run usage
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
.venv/bin/python -c "
import anyio
from mcp_servers.omega_hub.mcp_client import SovereignMCPClient

async def test():
    async with SovereignMCPClient('http://127.0.0.1:8016/mcp') as client:
        result = await client.call_tool('oracle_talk', {'query': 'test'})
        print(result.content[0] if result.content else 'empty')

anyio.run(test)
"
```

**Phase 1.5 — Engine Core Standalone Test (Fixed):**
```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
PYTHONPATH=src .venv/bin/python -c "
import anyio
from src.omega.skills.autonomous_meditation_pipeline import create_pipeline_standalone

async def test():
    p = create_pipeline_standalone('test problem', dry_run=True)
    await p.run()

anyio.run(test)
"
```

### Additional Hardening Items

1. **Cross-platform atomic writes** (Phase 4.4):
   ```python
   import os
   os.replace(tmp_path, filepath)  # Works on Windows + POSIX
   ```

2. **Configurable research concurrency** (Phase 6.1):
   ```python
   def __init__(self, ..., max_concurrent_research: int = 3, **kwargs):
       self.max_concurrent_research = max_concurrent_research
       # ...
   
   # In stage_4:
   semaphore = anyio.Semaphore(self.max_concurrent_research)
   ```

3. **Pre-existing M1 violation in tty_agent.py** (outside P3 scope):
   - File: `src/omega/agents/tty_agent.py:14` uses `import asyncio`
   - This blocks Sovereign Vetter but doesn't block P3 work
   - Track separately for P3/P5 joint remediation

4. **Heritage vet for new error classes** (Phase 3.1):
   - New error classes (`AutonomousMeditationError`, `StageExecutionError`, etc.) are **original Omega Engine patterns**
   - No `[id-soft:]` tags needed — they don't derive from id Software techniques
   - M14 compliance: No vet records required for original patterns

5. **M22 Response Provenance in pipeline**:
   - Stage 1 (Meditation) calls oracle → should capture `provider_name` from `GenerateResult`
   - Add to stage output metadata for forensic accuracy

### Updated Risk: MCP Hub Tool Wiring

**Root Cause Analysis** (from P1 Plan Phase 1.4):
The `omega_hub_oracle_talk` tool is registered via `@mcp.tool()` decorator. The `_require_service()` guard checks if `oracle` singleton is initialized. In OpenCode context, the MCP server runs in a separate process — the pipeline must connect via `SovereignMCPClient` (JSON-RPC), not import the tool functions directly.

**P1's `opencode_client.py` already implements this correctly.** Phase 1.3 just needs to wire the engine core to use it.

### Sequencing Confirmation

The phase ordering is correct:
1. **Phase 0** → Verifies the foundation (MCP Hub, package build, temple-grade baseline)
2. **Phase 1** → Eliminates duplication (M16), fixes M1 violation, wires MCP correctly
3. **Phase 2** → Tests the consolidated code (requires Phase 1 complete)
4. **Phase 3** → Hardens errors in the now-tested code
5. **Phase 4** → Temple-Grade gates on tested, hardened code
6. **Phase 5** → CI/CD for the verified package
7. **Phase 6** → Performance optimization on solid foundation
8. **Phase 7** → Cross-pillar integration verification

**No phase can be parallelized** — each depends on the previous phase's output.

---

*⬡ OMEGA ⬡ PILLAR P3 ⬡ ENGINEERING ⬡ trc_p3_eng_plan ⬡ 2026-07-19*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: P3 | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
