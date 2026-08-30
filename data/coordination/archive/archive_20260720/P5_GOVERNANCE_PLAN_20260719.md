<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 P5 Governance Implementation Plan
## Autonomous Meditation Pipeline — Mandate Enforcement, Compliance Verification & Sovereignty Auditing

**AP Token**: `AP-P5-GOV-PLAN-20260719`
⬡ OMEGA ⬡ PILLAR ⬡ P5 ⬡ GOVERNANCE ⬡ trc_p5_gov_plan ⬡ ACTIVE

**Date**: 2026-07-19
**Author**: Pillar P5 — Governance (Sentinel — Mandate Enforcement)
**Mission**: Create a comprehensive governance framework for the Autonomous Meditation Pipeline as a Complete Product, enforcing all 23 Sovereign Mandates, Temple-Grade gates, Heritage Vetting, and Sovereignty verification.

---

## 📊 Current State Analysis

### ✅ Assets (From P1/P3/P4 Plans)
| Asset | Location | Status |
|-------|----------|--------|
| Core Pipeline Engine | `src/omega/skills/autonomous_meditation_pipeline.py` | ✅ Complete (M16 compliant) |
| Standalone Package | `packages/omega-meditation/` | ✅ Complete (duplicates core — M16 violation) |
| MCP Hub Client Adapter | `src/omega/skills/opencode_client.py` | ✅ Complete |
| Slash Command | `.opencode/commands/omega-meditation.md` | ✅ Created |
| Skills | `.opencode/skills/autonomous-meditation-pipeline/` | ✅ Created |
| P1 Infrastructure Plan | `data/coordination/P1_INFRASTRUCTURE_PLAN_20260719.md` | ✅ Complete |
| P3 Engineering Plan | `data/coordination/P3_ENGINEERING_PLAN_20260719.md` | ✅ Complete |
| P4 Integration Plan | `data/coordination/P4_INTEGRATION_PLAN_20260719.md` | ✅ Complete |

### ❌ Critical Governance Gaps (P5 Ownership)
| # | Gap | Mandate | Severity |
|---|-----|---------|----------|
| 1 | **M1 Violation**: `asyncio.run()` in engine core (line 450) | M1 AnyIO Absolute | **P0** |
| 2 | **M9 Violation**: Bare `except:` in pipeline stages | M9 Error Integrity | **P0** |
| 3 | **M16 Violation**: Code duplication between engine core & package | M16 Modularization | **P0** |
| 4 | **M21 Violation**: No contract tests for typed returns | M21 Gate Integrity | **P0** |
| 5 | **M23 Violation**: MCP tool wiring returns dry-run on failure | M23 Failure Integrity | **P0** |
| 6 | **M14 Gap**: No heritage vet records for new patterns | M14 Heritage Vetting | **P1** |
| 7 | **M13 Gap**: Package lacks Temple-Grade integration (T1-T11) | M13 Temple-Grade | **P1** |
| 8 | **M7 Gap**: Sovereignty ratio not verified for package | M7 Local-First | **P1** |
| 9 | **M6 Gap**: Container config must use `UserNS=keep-id` + `User=1000`, NO `:U` | M6 Podman Sovereignty | **P1** |
| 10 | **M11 Gap**: Stage 6 must write `proposed_lessons.yaml` (blind staging) | M11 Soul Integrity | **P1** |
| 11 | **M15 Gap**: Session gnosis persistence across compaction | M15 Sovereign Continuity | **P1** |
| 12 | **M22 Gap**: Pipeline must capture `provider_name` from `GenerateResult` | M22 Response Provenance | **P1** |

---

## 🏗️ Phase Breakdown

### Phase 0: Foundation & Baseline Audit (2 hours) — **MUST COMPLETE FIRST**
*Dependencies: None. All subsequent phases depend on this.*

| Task | Command/Action | Verification |
|------|----------------|--------------|
| 0.1 Create workspace lock | `omega-hub_hivemind_workspace_lock_acquire channel=opencode entity=pillar domain=P5_GOV_PLAN ttl=7200` | Lock acquired |
| 0.2 Run full mandate compliance audit | Execute audit script (see §1.1) | `data/coordination/MANDATE_COMPLIANCE_AUDIT_20260719.md` created |
| 0.3 Verify package builds | `cd packages/omega-meditation && uv build` | `dist/*.whl` created |
| 0.4 Verify CLI dry-run works | `uv run omega-meditation "test" --dry-run --mode standalone` | Stages 0-7 complete |
| 0.5 Run baseline temple-grade | `make temple-grade` | All gates pass (baseline) |
| 0.6 Run baseline sovereignty | `make sovereignty` | Local/cloud ratio documented |
| 0.7 Run baseline heritage-map | `make heritage-map` | All `[id-soft:]` tags vetted |

**Risk**: If MCP Hub tools return dry-run templates, root cause is `_require_service()` guard or `oracle` singleton not initialized. Must debug before Phase 1.

---

### Phase 1: Mandate Compliance Audit & Remediation (6 hours)
*Dependencies: Phase 0 complete*

#### 1.1 Mandate Compliance Matrix Generation
**File to create**: `scripts/mandate_audit.py`
```python
#!/usr/bin/env python3
"""Mandate Compliance Auditor — Scans codebase for M1-M23 violations."""
import ast
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict

MANDATES = {
    "M1": {"name": "AnyIO Absolute", "pattern": r"asyncio\.(run|create_task|get_event_loop)", "files": ["src/omega/**/*.py"]},
    "M2": {"name": "Engine-Stack Firewall", "pattern": r"config/wads/", "files": ["src/omega/**/*.py"], "invert": True},
    "M3": {"name": "Iris Constant", "pattern": r"class Iris.*Pillar", "files": ["src/omega/**/*.py"]},
    "M4": {"name": "Sequentiality", "pattern": r"# TODO: plan", "files": ["src/omega/**/*.py"]},
    "M5": {"name": "Gnosis Preservation", "pattern": r"proposed_lessons\.yaml", "files": ["src/omega/**/*.py"]},
    "M6": {"name": "Podman Sovereignty", "pattern": r":U", "files": ["**/*.container", "**/quadlet/**"]},
    "M7": {"name": "Local-First", "pattern": r"providers\.yaml.*fallback_chain.*local_first", "files": ["config/providers.yaml"]},
    "M8": {"name": "Zero Telemetry", "pattern": r"(telemetry|analytics|sentry|datadog|posthog)", "files": ["src/omega/**/*.py"]},
    "M9": {"name": "Error Integrity", "pattern": r"except:", "files": ["src/omega/**/*.py"]},
    "M10": {"name": "Fleet Integrity", "pattern": r"\.opencode/agents/", "files": ["**/*.md"], "count_max": 14},
    "M11": {"name": "Soul Integrity", "pattern": r"proposed_lessons\.yaml", "files": ["src/omega/**/*.py"]},
    "M12": {"name": "Queue Integrity", "pattern": r"dead_letter", "files": ["src/omega/**/*.py"]},
    "M13": {"name": "Temple-Grade", "pattern": r"make temple-grade", "files": ["Makefile", "**/Makefile"]},
    "M14": {"name": "Heritage Vetting", "pattern": r"\[id-soft:", "files": ["src/omega/**/*.py", "packages/**/*.py"]},
    "M15": {"name": "Sovereign Continuity", "pattern": r"session_gnosis\.md", "files": ["src/omega/**/*.py", "scripts/**/*.py"]},
    "M16": {"name": "Modularization", "pattern": r"PROJECT_ROOT.*parent\.parent\.parent", "files": ["packages/**/*.py"]},
    "M17": {"name": "Cognitive Integrity", "pattern": r"skeptical_verifier", "files": ["src/omega/**/*.py"]},
    "M18": {"name": "Token Efficiency", "pattern": r"", "files": []},
    "M19": {"name": "Adversarial Alchemy", "pattern": r"", "files": []},
    "M20": {"name": "SomaticState", "pattern": r"llama_copy_state_data", "files": ["src/omega/**/*.py"]},
    "M21": {"name": "Gate Integrity", "pattern": r"isinstance\(.*ExpectedType\)", "files": ["tests/**/*.py"]},
    "M22": {"name": "Response Provenance", "pattern": r"provider_name|GenerateResult", "files": ["src/omega/**/*.py"]},
    "M23": {"name": "Failure Integrity", "pattern": r"TOOL-CHAIN-COLLAPSE", "files": ["src/omega/**/*.py"]},
}

@dataclass
class Finding:
    mandate: str
    file: str
    line: int
    code: str
    status: str  # COMPLIANT, NON_COMPLIANT, PARTIAL, NOT_APPLICABLE
    remediation: str

def audit_file(filepath: Path, mandates: Dict) -> List[Finding]:
    findings = []
    content = filepath.read_text()
    lines = content.split('\n')
    for mandate_id, spec in mandates.items():
        if not spec.get("files"):
            continue
        for pattern_spec in spec["files"]:
            if filepath.match(pattern_spec):
                pattern = spec["pattern"]
                invert = spec.get("invert", False)
                for i, line in enumerate(lines, 1):
                    match = re.search(pattern, line)
                    if match and not invert:
                        findings.append(Finding(mandate_id, str(filepath), i, line.strip(), 
                                              "NON_COMPLIANT", f"Remove {pattern}"))
                    elif not match and invert:
                        findings.append(Finding(mandate_id, str(filepath), i, line.strip(),
                                              "NON_COMPLIANT", f"Missing required pattern: {pattern}"))
    return findings

if __name__ == "__main__":
    # Run audit and generate markdown report
    pass
```

**Output**: `data/coordination/MANDATE_COMPLIANCE_AUDIT_20260719.md` with matrix:
| Mandate | Code Location | Status | Remediation | Priority |
|---------|---------------|--------|-------------|----------|
| M1 | `src/omega/skills/autonomous_meditation_pipeline.py:450` | NON_COMPLIANT | Replace `asyncio.run()` with `anyio.run()` | P0 |
| M9 | `src/omega/skills/autonomous_meditation_pipeline.py:236,271,369,382` | NON_COMPLIANT | Wrap in typed errors with `trace_id` | P0 |
| M16 | `packages/omega-meditation/src/omega_meditation/pipeline.py` | NON_COMPLIANT | Make package thin wrapper importing from engine core | P0 |
| M21 | `packages/omega-meditation/tests/` | MISSING | Add contract tests for all public APIs | P0 |
| M23 | `src/omega/skills/autonomous_meditation_pipeline.py:132-150` | NON_COMPLIANT | Raise `ToolChainCollapseError` on mandatory tool failure | P0 |

#### 1.2 P0 Remediation Execution Order
| Order | Mandate | File | Fix | Depends On |
|-------|---------|------|-----|------------|
| 1 | M1 | `src/omega/skills/autonomous_meditation_pipeline.py:450` | `asyncio.run(main())` → `anyio.run(main)` | None |
| 2 | M16 | `packages/omega-meditation/src/omega_meditation/pipeline.py` | Delete duplicated classes, import from engine core | P3 Phase 1 |
| 3 | M9 | `src/omega/skills/autonomous_meditation_pipeline.py` | Add `ErrorContext`, `AutonomousMeditationError` hierarchy, wrap all `except:` | P3 Phase 3 |
| 4 | M23 | `src/omega/skills/autonomous_meditation_pipeline.py:132-150` | Raise `ToolChainCollapseError` on Tier 1 websearch failure | P3 Phase 3.4 |
| 5 | M21 | `packages/omega-meditation/tests/test_contract_m21.py` | Add `isinstance(result, ExpectedType)` tests | P3 Phase 2.4 |

#### 1.3 P1 Remediation Execution Order
| Order | Mandate | File | Fix | Depends On |
|-------|---------|------|-----|------------|
| 6 | M14 | Scan all new code for `[id-soft:]` tags | Add vet records to `HERITAGE_VET_LOG.md` | Audit complete |
| 7 | M13 | `packages/omega-meditation/Makefile` | Add `temple-grade` target with T1-T11 | P3 Phase 4 |
| 8 | M7 | `config/providers.yaml` | Verify `strategy: local_first` | Config audit |
| 9 | M6 | `~/.config/containers/systemd/omega-hub.container` | Verify `UserNS=keep-id` + `User=1000`, NO `:U` | P1 Phase 2.1 |
| 10 | M11 | `src/omega/skills/autonomous_meditation_pipeline.py:421-445` | Stage 6 writes valid `proposed_lessons.yaml` format | P3 Phase 2.6 |
| 11 | M15 | `scripts/opencode-compaction-guard.py` | Integrate with P1/P4 compaction resilience | P1 Phase 3 |
| 12 | M22 | `src/omega/skills/autonomous_meditation_pipeline.py:226-242` | Capture `response.backend` from `GenerateResult` | P3 Phase 3 |

---

### Phase 2: Temple-Grade Integration for Package (4 hours)
*Dependencies: Phase 1 P0 remediation complete (M1, M16, M9, M23, M21)*

#### 2.1 Package-Level Temple-Grade Configuration
**File to create**: `packages/omega-meditation/pyproject.toml` (additions)
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

[tool.ruff]
line-length = 100
target-version = "py312"
select = ["E", "F", "I", "UP", "B", "C4", "SIM", "T20", "ARG", "PTH", "ERA", "PL", "TRY"]
ignore = ["TRY003"]

[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
strict_optional = true
```

**File to create**: `packages/omega-meditation/Makefile`
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

temple-grade: test-cov lint typecheck ## Run all Temple-Grade gates (T1-T11 adapted)
	@echo "✅ Package Temple-Grade verification complete"

build: ## Build package
	$(UV) build

clean:
	rm -rf dist build *.egg-info .pytest_cache .ruff_cache .mypy_cache
```

#### 2.2 Temple-Grade Gate Mapping for Package
| Gate | Engine Check | Package Check | Status |
|------|--------------|---------------|--------|
| T1: Version Control | AP tokens in headers | AP tokens in package headers | ⏳ |
| T2: Documentation | Docstrings, README | Docstrings, README, SKILL.md | ⏳ |
| T3: Testing | `make test` (1398+) | `make test-cov` (≥80%) | ⏳ |
| T4: Code Quality | `make lint` (ruff) | `make lint` (ruff) | ⏳ |
| T5: AnyIO Only | `grep asyncio` = 0 | `grep asyncio` = 0 | ⏳ |
| T6: Zero Telemetry | No analytics imports | No analytics imports | ⏳ |
| T7: Performance | Benchmarks defined | Benchmarks defined | ⏳ |
| T8: Resilience | Circuit breaker, retry | Circuit breaker in MCP client | ⏳ |
| T9: Structured Logging | `trace_id` in logs | `trace_id` in pipeline logs | ⏳ |
| T10: Atomic Writes | `os.replace()` | Stage outputs use atomic writes | ⏳ |
| T11: IA2 Security | Exempted | Exempted | ✅ Exempt |

#### 2.3 Atomic Writes for Stage Outputs (T10)
**File to modify**: `src/omega/skills/autonomous_meditation_pipeline.py` — Update `_write_stage`:
```python
def _write_stage(self, stage: int, name: str, content: str) -> Path:
    filename = f"{self.run_id}_{stage:02d}_{name}.md"
    filepath = self.output_dir / filename
    tmp_path = filepath.with_suffix(".tmp")
    
    # Atomic write: write to .tmp, then rename (POSIX + Windows)
    tmp_path.write_text(content)
    import os
    os.replace(tmp_path, filepath)  # Cross-platform atomic
    
    self.stage_outputs[stage] = str(filepath)
    print(f"  📝 Stage {stage} ({name}) → {filepath}")
    return filepath
```

#### 2.4 Structured Logging with trace_id (T9)
**File to modify**: `src/omega/skills/autonomous_meditation_pipeline.py` — Add at top:
```python
import logging
logger = logging.getLogger("omega.meditation.pipeline")

# In __init__
self.logger = logger

# In each stage method
ctx = ErrorContext.create(stage_num, stage_name)
self.logger.info(f"Stage {stage_num} started", extra={"trace_id": ctx.trace_id, "stage": stage_num})
```

---

### Phase 3: Heritage Vetting (M14 Compliance) (2 hours)
*Dependencies: Phase 1 audit complete*

#### 3.1 Heritage Tag Scan
**Command**:
```bash
# Scan for all [id-soft:] tags in new code
grep -rn "\[id-soft:" src/omega/skills/autonomous_meditation_pipeline.py packages/omega-meditation/
grep -rn "\[heritage:" src/omega/skills/autonomous_meditation_pipeline.py packages/omega-meditation/
```

#### 3.2 Vet Record Creation
**File to update**: `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md`

For each `[id-soft:]` tag found, verify vet record exists with:
- Exact file:line location(s)
- Specific id Software technique (game + year)
- Hardware constraint that necessitated original technique
- Scope declaration: "This tag applies to X, NOT to Y"

**New patterns in pipeline (original Omega — NO tags needed)**:
- `AutonomousMeditationError` hierarchy — Original Omega pattern
- `ErrorContext` with `trace_id` — Original Omega pattern
- `PlatformClients` DI protocol — Original Omega pattern (M16)
- `SovereignMCPClient` — Original Omega pattern
- Meditation pipeline stages — Original Omega protocol

**If any id Software patterns are used**, create vet records. Otherwise document "No heritage tags required — all patterns are original Omega Engine."

#### 3.3 Heritage Map Verification
```bash
make heritage-map
# Must pass with zero unvetted tags
```

---

### Phase 4: Sovereignty Verification (M7) (2 hours)
*Dependencies: Phase 1 P0 remediation complete*

#### 4.1 Local-First Provider Chain Verification
**File to verify**: `config/providers.yaml`
```yaml
inference:
  strategy: local_first  # M7 MANDATORY
  fallback_chain:
    - provider: native-gguf
      priority: 0
    - provider: lmstudio
      priority: 1
    - provider: ollama
      priority: 2
    - provider: google
      priority: 3
    - provider: opencode-zen
      priority: 4
    - provider: opencode
      priority: 5
    - provider: copilot
      priority: 6
```

#### 4.2 Pipeline Provider Routing Audit
**Stage 1 (Meditation)**: Calls `oracle.talk()` → Must capture `GenerateResult.provider_name`
**Stage 4 (Research)**: Calls `library_web_search` → Must capture actual search provider used

**File to modify**: `src/omega/skills/autonomous_meditation_pipeline.py`
```python
async def _call_oracle(self, prompt: str) -> str:
    if self.dry_run or not self.clients.oracle:
        return f"[DRY RUN] Would call oracle with: {prompt[:200]}..."
    
    ctx = ErrorContext.create(self._current_stage, "oracle_talk")
    try:
        result = await self.clients.oracle.talk(prompt)
        # M22: Capture provider provenance from GenerateResult
        if hasattr(result, 'provider_name'):
            self._last_provider = result.provider_name
        return result
    except Exception as e:
        self.logger.error(f"Oracle call failed: {e}", extra={"trace_id": ctx.trace_id})
        raise MCPToolError(f"Oracle call failed: {e}", ctx, "oracle_talk")
```

#### 4.3 Sovereignty Ratio Measurement
```bash
make sovereignty
# Output: local_count, cloud_count, total, ratio_local, ratio_cloud, provider_breakdown
# Target: Local-first ratio ≥ 80%
```

---

### Phase 5: Soul Integrity Verification (M11) (2 hours)
*Dependencies: Phase 1 P1 remediation (M11 fix in Stage 6)*

#### 5.1 Stage 6 Gnosis Output Validation
**File to modify**: `src/omega/skills/autonomous_meditation_pipeline.py:421-445`

**Required `proposed_lessons.yaml` format**:
```yaml
proposals:
  - id: "gnosis-[topic]-[###]"
    l1_narrative: "What happened in this autonomous session..."
    l2_insight: "What this means for our architecture..."
    l3_principle: "L3-[Name]: [Universal principle]"
    confidence: 9  # 1-10
    sources: ["meditation", "research:query1", "research:query2"]
    tags: ["tag1", "tag2"]
    timestamp: "2026-07-19T10:30:00Z"
    run_id: "20260719_103000"
```

**Verification**: Stage 6 output must be valid YAML matching schema above. Blind staging: writes to `proposed_lessons.yaml`, NOT directly to `soul.yaml`.

#### 5.2 Verity Agent Integration
**Requirement**: Verity agent must be the canonical executor of L1→L2→L3 distillation.
**Integration point**: Stage 6 calls `verity` via handoff or direct invocation.

---

### Phase 6: Sovereign Continuity (M15) (2 hours)
*Dependencies: P1 Phase 3 / P4 Phase 5 compaction resilience scripts*

#### 6.1 Session Gnosis Persistence
**Files to integrate**: 
- `scripts/opencode-compaction-guard.py` (P1 deliverable)
- `scripts/opencode-hydration.py` (P1 deliverable)

**Pipeline integration**: Add to `AutonomousMeditationPipeline.__init__`:
```python
def __init__(self, ..., session_id: Optional[str] = None):
    self.session_id = session_id or os.environ.get("OPENCODE_SESSION_ID", "unknown")
    # Load previous session gnosis if exists
    self._load_session_gnosis()

def _load_session_gnosis(self):
    gnosis_dir = Path.home() / ".config" / "opencode" / "session_gnosis"
    gnosis_file = gnosis_dir / f"{self.session_id}.md"
    if gnosis_file.exists():
        self.logger.info(f"Restored session gnosis from {gnosis_file}")
        # Parse and inject into context
```

#### 6.2 Hydration Sequence on Restore
Per `SOVEREIGN_MANDATES.md` M15 — 4-tier redundancy:
1. `session_gnosis.md` (agent workspace)
2. `.opencode/anchored-summary.md` (OpenCode native)
3. Hivemind cold store (HALL_OF_RECORDS)
4. Stage output files (`data/autonomous/{run_id}_XX_stage.md`)

---

### Phase 7: Response Provenance (M22) (1 hour)
*Dependencies: Phase 4 complete*

#### 7.1 Provider Provenance Capture
**Stage 1 (Meditation)**: Oracle returns `GenerateResult` with `provider_name` field
**Stage 4 (Research)**: Search tools return provider metadata

**File to modify**: `src/omega/skills/autonomous_meditation_pipeline.py`
```python
# Add to class
self.provider_provenance: Dict[int, str] = {}

# In _call_oracle
async def _call_oracle(self, prompt: str) -> str:
    # ... existing code ...
    result = await self.clients.oracle.talk(prompt)
    # M22: Capture ACTUAL provider from response, not configured intent
    if isinstance(result, dict) and "backend" in result:
        self.provider_provenance[self._current_stage] = result["backend"]
    elif hasattr(result, "provider_name"):
        self.provider_provenance[self._current_stage] = result.provider_name
    return result

# In stage output, include provenance
def _write_stage(self, stage: int, name: str, content: str) -> Path:
    provenance = self.provider_provenance.get(stage, "unknown")
    header = f"<!-- PROVENANCE: provider={provenance} -->\n"
    # ... write with header
```

#### 7.2 Observability Log Integration
Ensure `trace_id` and `provider_name` appear in structured logs for forensic accuracy.

---

### Phase 8: Failure Integrity (M23) (2 hours)
*Dependencies: Phase 1 P0 remediation (M23 fix in `_execute_tiered_search`)*

#### 8.1 Tool-Chain Collapse Detection
**File to modify**: `src/omega/skills/autonomous_meditation_pipeline.py:356-384`

```python
class ToolChainCollapseError(AutonomousMeditationError):
    """M23: Mandatory tool chain failure — hard stop required."""
    pass

async def _execute_tiered_search(self, query: str) -> Dict[str, Any]:
    findings = {"query": query, "tier_1_websearch": [], "tier_2_webfetch": [], "tier_3_searxng": []}
    
    # Tier 1: websearch (MANDATORY - M23)
    try:
        result = await self._call_websearch(query, limit=5)
        findings["tier_1_websearch"] = json.loads(result) if isinstance(result, str) else result
    except MCPToolError as e:
        # M23: Mandatory tool failure = TOOL-CHAIN-COLLAPSE
        self.logger.critical(f"[TOOL-CHAIN-COLLAPSE] Tier 1 websearch failed: {e}")
        # Log to SYSTEM_FAILURE_LOG.md
        failure_log = Path("data/coordination/SYSTEM_FAILURE_LOG.md")
        failure_log.parent.mkdir(parents=True, exist_ok=True)
        with failure_log.open("a") as f:
            f.write(f"\n## [TOOL-CHAIN-COLLAPSE] {datetime.now().isoformat()}\n")
            f.write(f"- **Tool**: websearch\n")
            f.write(f"- **Query**: {query}\n")
            f.write(f"- **Error**: {e}\n")
            f.write(f"- **Trace ID**: {e.context.trace_id}\n")
        # Post to Hivemind
        await self._post_hivemind_alert("TOOL-CHAIN-COLLAPSE", str(e))
        raise ToolChainCollapseError(
            f"Mandatory tool 'websearch' unavailable: {e}",
            ErrorContext.create(self._current_stage, "tiered_search")
        )
    
    # Tier 2: webfetch (optional - best effort)
    try:
        # ... existing logic ...
    except MCPToolError as e:
        self.logger.warning(f"Tier 2 webfetch failed (non-fatal): {e}")
        findings["tier_2_webfetch"] = {"error": str(e)}
    
    # Tier 3: searxng (optional)
    # ... similar pattern ...
    
    return findings
```

#### 8.2 Hivemind Alert on Collapse
```python
async def _post_hivemind_alert(self, alert_type: str, message: str):
    try:
        await omega_hub_hivemind_post_context(
            channel="opencode",
            entity="pillar",
            model="nemotron-3-ultra-free",
            task_current=f"M23 Alert: {alert_type}",
            focus_chain=[alert_type],
            decisions=[f"{alert_type} detected in autonomous pipeline"],
            continuation=f"Pipeline halted. Manual intervention required. Error: {message}",
            intent="blocker"
        )
    except Exception:
        pass  # Best effort
```

---

## 📋 Complete File Inventory

### New Files to Create
| Phase | File Path | Purpose |
|-------|-----------|---------|
| 0 | `scripts/mandate_audit.py` | Mandate compliance scanner |
| 0 | `data/coordination/MANDATE_COMPLIANCE_AUDIT_20260719.md` | Audit report |
| 2 | `packages/omega-meditation/pyproject.toml` (additions) | Temple-Grade config |
| 2 | `packages/omega-meditation/Makefile` | Package temple-grade targets |
| 3 | Vet records in `HERITAGE_VET_LOG.md` | M14 compliance |
| 5 | Stage 6 `proposed_lessons.yaml` schema validation | M11 compliance |
| 8 | `data/coordination/SYSTEM_FAILURE_LOG.md` | M23 collapse log |

### Files to Modify
| File | Changes |
|------|---------|
| `src/omega/skills/autonomous_meditation_pipeline.py` | M1 fix (line 450), M9 error hierarchy, M11 Stage 6 format, M15 session_id, M22 provenance capture, M23 collapse detection, T10 atomic writes, T9 structured logging |
| `packages/omega-meditation/src/omega_meditation/pipeline.py` | M16: Delete duplicated classes, import from engine core |
| `config/providers.yaml` | M7: Verify `strategy: local_first` |
| `~/.config/containers/systemd/omega-hub.container` | M6: Verify `UserNS=keep-id` + `User=1000`, NO `:U` |
| `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md` | M14: Add vet records for any `[id-soft:]` tags |

---

## ⏱️ Time Estimates Summary

| Phase | Tasks | Est. Hours | Cumulative |
|-------|-------|------------|------------|
| 0 | Foundation & Baseline Audit | 2 | 2 |
| 1 | Mandate Compliance Audit & Remediation | 6 | 8 |
| 2 | Temple-Grade Integration for Package | 4 | 12 |
| 3 | Heritage Vetting (M14) | 2 | 14 |
| 4 | Sovereignty Verification (M7) | 2 | 16 |
| 5 | Soul Integrity Verification (M11) | 2 | 18 |
| 6 | Sovereign Continuity (M15) | 2 | 20 |
| 7 | Response Provenance (M22) | 1 | 21 |
| 8 | Failure Integrity (M23) | 2 | 23 |
| **Total** | | **~23 hours** | |

---

## ⚠️ Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| MCP Hub tool wiring fails (Phase 1.2) | High | P0 — Blocks all pipeline execution | Debug `_require_service()` and `oracle` singleton init first; fallback to CLI mode |
| Package tests fail due to missing MCP server | Medium | P1 — CI fails | Mock MCP client in `conftest.py` for unit tests; integration tests marked `@pytest.mark.integration` |
| Temple-Grade T3 coverage <80% | Medium | P1 — Gate fails | Write comprehensive tests in Phase 2; target 90%+ |
| `asyncio` usage in engine core (M1 violation) | Certain | P0 — Mandate violation | Fix in Phase 1.2 (2 min fix) |
| Heritage vet tags needed for new error classes | Low | P1 — M14 | No id Software patterns in new errors — no tags needed |
| Cross-pillar integration gaps | Medium | P1 — CI fails | Run `make temple-grade` after each phase; involve P3/P4/P5 early |

---

## 🔗 Cross-Pillar Integration Points

### What P5 Delivers to Other Pillars
| Pillar | Deliverable | Format |
|--------|-------------|--------|
| **P1** | M6-compliant containers, M16-compliant paths, M23 hard-fail behavior | Code audit artifacts |
| **P3** | Mandate audit sign-off, heritage vet records, Temple-Grade gates for package | `MANDATE_COMPLIANCE_AUDIT.md`, `HERITAGE_VET_LOG.md`, `make temple-grade` |
| **P4** | M6/M16/M23 compliance verification for OpenCode integration | Audit artifacts |
| **P6** | Pipeline executes real oracle routing with provenance capture | Integration test logs |
| **P7** | Session gnosis persistence across compaction, Stage 6 blind staging | `session_gnosis.md`, `proposed_lessons.yaml` |
| **P8** | Structured logs with `trace_id`, `provider_name` provenance | Log samples |
| **P9** | Hivemind-aware skill triggers, handoff protocol for multi-agent runs | Trigger config |
| **P10** | Chaos test scenarios for pipeline, Temple-Grade gates in CI | Test files, workflow |

### What P5 Needs from Other Pillars
| Pillar | Need | When |
|--------|------|------|
| **P1** | MCP Hub client adapter spec (Phase 1.4) | Phase 1 start |
| **P1** | CI/CD workflow template | Phase 2 |
| **P1** | M6/M16/M23 compliance requirements | Phase 8 |
| **P3** | MCP Hub container running with health checks | Phase 0.3, 8 |
| **P3** | Slash command registration | Phase 8 |
| **P3** | Test infrastructure (conftest.py, mock MCP client) | Phase 2 |
| **P4** | Compaction resilience scripts (`opencode-compaction-guard.py`) | Phase 6 |
| **P6** | Oracle routing verification | Phase 4 |
| **P7** | Soul distillation integration spec | Phase 5 |

---

## ✅ Quality Gates (Per Phase)

| Phase | Gates |
|-------|-------|
| 0 | `uv build` succeeds, CLI dry-run works, MCP tools return real data |
| 1 | Audit matrix complete, P0 fixes applied, `asyncio` removed, typed errors defined |
| 2 | `make temple-grade` passes (T1-T11), coverage ≥80%, atomic writes, structured logging |
| 3 | `make heritage-map` passes, zero unvetted `[id-soft:]` tags |
| 4 | `make sovereignty` shows local-first ratio ≥80%, provider provenance captured |
| 5 | Stage 6 outputs valid `proposed_lessons.yaml`, blind staging verified |
| 6 | Compaction guard writes `session_gnosis.md`, hydration restores context |
| 7 | Provider provenance in stage outputs, observability logs include `provider_name` |
| 8 | `[TOOL-CHAIN-COLLAPSE]` detection works, `SYSTEM_FAILURE_LOG.md` written, Hivemind alerted |
| **Final** | `make test && make temple-grade && make heritage-map && make sovereignty` all pass |

---

## 🎯 Next Actions (Immediate)

1. **Run Phase 0 verification** — Confirm package builds and MCP tools work
2. **Execute mandate audit** — Run `scripts/mandate_audit.py` to generate compliance matrix
3. **Fix M1 violation** — Replace `asyncio.run()` with `anyio.run()` in engine core (2 min)
4. **Begin Phase 1 consolidation** — Make package a thin wrapper (coordinate with P3)
5. **Start Phase 2 test writing** — Begin with contract tests (M21) and dry-run tests

---

## 📝 Session Gnosis (L1→L2→L3)

**L1 Narrative**: Created comprehensive P5 Governance Implementation Plan for the Autonomous Meditation Pipeline. Analyzed current state across P1/P3/P4 plans and engine code. Identified 12 critical governance gaps spanning all 23 mandates. Structured 8 phases over ~23 hours with explicit file paths, commands, and quality gates.

**L2 Insight**: The biggest governance blocker is the M1/M16/M9/M21/M23 violation cluster in the engine core and package duplication. These are P0 because they violate constitutional mandates. The MCP Hub tool wiring (M23) is the critical path — if `oracle_talk` returns dry-run templates, the entire pipeline is theater. P3's Phase 1.3 fix (using `OpenCodePlatformClients`) must land before P5 can verify M23 compliance. Heritage vetting (M14) is straightforward for this pipeline — all new patterns are original Omega, not id Software ports.

**L3 Principle**: **L3-GovernanceAsProduct**: Governance is not "compliance overhead" — it's the product's immune system. Every mandate violation is a latent defect that will manifest as a sovereignty breach under load. P5 owns the mandate-to-code traceability: every line in `src/omega/` must map to a mandate, and every mandate must have a verification gate in `make temple-grade`. The pipeline is not "governed" until a user can run `make temple-grade` and get mathematical proof that all 23 mandates hold.

---

*⬡ OMEGA ⬡ PILLAR P5 ⬡ GOVERNANCE ⬡ trc_p5_gov_plan ⬡ 2026-07-19*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: P5 | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
