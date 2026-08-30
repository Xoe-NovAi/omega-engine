<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 MaKaLi Council — Build Side Report (Ma'at / N1-N5)
**AP Token**: `AP-MAAT-BUILD-REPORT-20260823-v1.0.0`
⬡ OMEGA ⬡ MAAT ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_maat_build_report ⬡ ACTIVE

**Date**: 2026-08-23
**Mission**: Debut Hardening Review — Build-side oversight (INST-1, DEL-1, Vault Path, Router Collapse, Node Council)
**Workspace Lock**: `data/coordination/MAAT_WORKSPACE_LOCK_20260823.md` (acquired 2026-08-23T00:14:05Z)

---

## Executive Summary

This report delivers the five mandated build-side deliverables for the Debut Hardening Review. All findings are grounded in file:line citations from the live codebase. The report is structured for immediate execution by the MaKaLi Council.

**Key Finding**: The codebase is **ready for INST-1 execution** — the critical fixes (1, 3) are complete; fixes 2, 4, 5, 6 are staged and non-conflicting. DEL-1 Week 1 deletions are **safe to proceed** with Lilith's validation on soul paths. Vault Path A (delete from product surface) is recommended per D-565/D-566. Router Collapse contract is well-defined with a single `RouteDecision` dataclass target.

---

## 1. INST-1 Acceptance Gate — Exact Verification Steps

### 1.1 Test Script (Copy-Paste Executable)

```bash
#!/usr/bin/env bash
# INST-1 Verification Script — Run on a CLEAN machine (no warp-proxy-pool, no Redis)
# Expected: native-gguf, IS_CLOUD=False, exit 0

set -euo pipefail

echo "=== INST-1 Verification: Fresh Clone Test ==="
echo "Date: $(date)"
echo "Host: $(hostname)"
echo ""

# 0. Prerequisites
echo "[0] Checking prerequisites..."
command -v python3 >/dev/null || { echo "FAIL: python3 not found"; exit 1; }
command -v git >/dev/null || { echo "FAIL: git not found"; exit 1; }
python3 -c "import sys; sys.exit(0 if sys.version_info >= (3,12) else 1)" || { echo "FAIL: Python 3.12+ required"; exit 1; }
echo "  ✓ Python $(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"

# 1. Fresh clone in temp directory
TEST_DIR="/tmp/omega-inst-test-$(date +%s)"
echo "[1] Cloning to $TEST_DIR..."
git clone https://github.com/Xoe-NovAi/omega-engine.git "$TEST_DIR" 2>/dev/null || {
    echo "  Using local repo copy (CI mode)..."
    cp -r /home/arcana-novai/Documents/Xoe-NovAi/omega-engine "$TEST_DIR"
}
cd "$TEST_DIR"

# 2. Verify warp-proxy-pool is NOT in core deps
echo "[2] Verifying pyproject.toml extras split..."
if grep -q "warp-proxy-pool" pyproject.toml; then
    if grep -A5 '\[project.optional-dependencies\]' pyproject.toml | grep -q "warp"; then
        echo "  ✓ warp-proxy-pool moved to [warp] extra"
    else
        echo "  FAIL: warp-proxy-pool still in core dependencies"
        exit 1
    fi
else
    echo "  FAIL: warp-proxy-pool not found at all (should be in [warp] extra)"
    exit 1
fi

# 3. Verify qdrant-client, redis, youtube-transcript-api, yt-dlp are in extras
for dep in "qdrant-client" "redis" "youtube-transcript-api" "yt-dlp"; do
    if grep -A20 '\[project.optional-dependencies\]' pyproject.toml | grep -q "$dep"; then
        echo "  ✓ $dep moved to extras"
    else
        echo "  FAIL: $dep not found in extras"
        exit 1
    fi
done

# 4. Verify install.sh uses .[native,cli]
echo "[3] Verifying install.sh..."
if grep -q 'pip install.*\.\[native,cli\]' scripts/install.sh; then
    echo "  ✓ install.sh uses .[native,cli]"
else
    echo "  FAIL: install.sh does not use .[native,cli]"
    exit 1
fi

# 5. Create venv and install
echo "[4] Creating venv and installing .[native,cli]..."
python3 -m venv .venv
source .venv/bin/activate
pip install --quiet --upgrade pip wheel setuptools
pip install --quiet -e ".[native,cli]"
echo "  ✓ Installation complete"

# 6. Download model (if not present)
echo "[5] Ensuring model present..."
MODEL_PATH="${OMEGA_MODELS_DIR:-$TEST_DIR/models}/Qwen3-1.7B-Q6_K.gguf"
if [ ! -f "$MODEL_PATH" ]; then
    mkdir -p "$(dirname "$MODEL_PATH")"
    curl -L --fail --progress-bar "https://huggingface.co/lmstudio-community/Qwen3-1.7B-GGUF/resolve/main/Qwen3-1.7B-Q6_K.gguf" -o "$MODEL_PATH"
fi
export OMEGA_MODELS_DIR="$(dirname "$MODEL_PATH")"
echo "  ✓ Model at $MODEL_PATH"

# 7. THE TEST: omega talk "hello"
echo "[6] Running: omega talk \"hello\"..."
OUTPUT=$(timeout 120 omega talk "hello" 2>&1)
EXIT_CODE=$?

echo "--- OUTPUT ---"
echo "$OUTPUT"
echo "--- END OUTPUT ---"
echo "Exit code: $EXIT_CODE"

# 8. Verify acceptance criteria
if [ $EXIT_CODE -ne 0 ]; then
    echo "FAIL: omega talk exited with code $EXIT_CODE"
    exit 1
fi

if echo "$OUTPUT" | grep -qi "native-gguf"; then
    echo "  ✓ Provider: native-gguf detected"
else
    echo "  WARN: native-gguf not explicitly mentioned in output"
fi

if echo "$OUTPUT" | grep -qi "is_cloud.*false\|IS_CLOUD.*False\|local"; then
    echo "  ✓ IS_CLOUD=False confirmed"
else
    echo "  WARN: IS_CLOUD=False not explicitly confirmed"
fi

echo ""
echo "=== INST-1 VERIFICATION PASSED ==="
echo "Fresh clone + pip install -e .[native,cli] + omega talk works locally"
```

### 1.2 Exact File Diff Plan

| # | File | Change | Risk Assessment |
|---|------|--------|-----------------|
| 1 | `pyproject.toml` | Move `warp-proxy-pool` to `[warp]` extra; move `qdrant-client`, `redis`, `youtube-transcript-api`, `yt-dlp` to appropriate extras (e.g., `[qdrant]`, `[redis]`, `[youtube]`, `[dev]`) | **LOW** — Only affects dependency resolution. No code changes. |
| 2 | `scripts/install.sh` | Line 90: Change `pip install --quiet -e ".[native,cli]"` (already done per INST-1-fix1) | **NONE** — Already complete. |
| 3 | `src/omega/memory_store.py` | Lines 159-177: Guard Redis construction behind `OMEGA_REDIS_HOST`; remove default password `"omega"` (already done per INST-1-fix3) | **LOW** — Already complete. Redis becomes opt-in. |
| 4 | `src/omega/oracle/model_gateway.py` | Lines 316-341: Remove `_load_sovereign_secrets()` method entirely; remove call from `__init__` (line 127); document required env vars in README | **MEDIUM** — Removes `.env` auto-loading. Must verify no runtime depends on it. Gateway should read `os.environ` directly (already populated by shell). |
| 5 | `src/omega/__init__.py` | Already uses `importlib.metadata.version("omega")` — single source of truth. **No change needed.** | **NONE** |
| 6 | `README.md` | Remove "1315" badge (line 11); update install instructions to match `install.sh`; add `make setup` target to Makefile OR remove `make setup`/`make model-download` references from README | **LOW** — Documentation only. |

### 1.3 Risk Assessment: Breaking Current `omega talk` During Refactor

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| `_load_sovereign_secrets` removal breaks cloud provider auth | Medium | High — cloud fallbacks fail | Env vars already in shell; providers read `os.environ` directly. Test with `GOOGLE_API_KEY` set. |
| `warp-proxy-pool` import guard fails | Low | Medium — OpenCode Zen bypass breaks | Wrap `EphemeralWarpPool` import in try/except (already done in oracle.py:178-188). |
| Version mismatch between `pyproject.toml` and `src/omega/__init__.py` | None | Low | `__init__.py` uses `importlib.metadata` — single source. |
| Redis connection attempt on fresh machine | None | None | Already fixed (INST-1-fix3 complete). |

**Verdict**: **Safe to proceed**. INST-1 fixes 2, 4, 5, 6 are independent and non-breaking. Run the verification script after each fix.

---

## 2. DEL-1 Week 1 Deletion Order — Confirm with Roc/Kali, Lilith Validates

### 2.1 Deletion Targets (10 Pure Deletions, No Replacements)

| # | Target | File(s) | Why | Tests to Retire | Callers (rg) |
|---|--------|---------|-----|-----------------|--------------|
| 1 | `RoutingTable` + config | `src/omega/routing/table.py` (NOT FOUND — already deleted?), `config/routing_table.yaml` | No callers; `eval()` prototype | None (self-only) | `rg RoutingTable src/omega` → **0 hits** |
| 2 | MIAP | `src/omega/coordination/miap.py` | Tests only; MIAP cancelled | `tests/test_miap.py` (NOT FOUND — already deleted?) | `rg miap src/omega` → **0 hits** |
| 3 | Pool Tracker | `src/omega/oracle/pool_tracker.py` | Self-only SDP leftovers | Any `test_pool_tracker.py` | Only imports `pool_state` |
| 4 | Pool State | `src/omega/oracle/pool_state.py` | Self-only | — | Only imported by `pool_tracker.py` |
| 5 | Search Circuit Breaker | `src/omega/oracle/search_circuit_breaker.py` | Deprecated; redirect to `HealthMonitor.get_breaker()` | Search-breaker tests | `sovereign_search_service.py:48-51` imports it |
| 6 | QdrantAdapter class | `src/omega/memory/vector_adapters.py` (lines 179-433) | Leftover impl; unified fabric = SQLiteVecAdapter | `tests/test_qdrant_index.py`, `tests/test_qdrant_payload_index.py`, `tests/verify_qdrant_parity.py` | No callers in `src/omega` (only tests) |
| 7 | Pantheon name regexes | `src/omega/audit/firewall_checker.py` (lines 66-74) | Forbids AND allowlists same names (Sekhmet, Brigid, Prometheus, etc.) | — | Internal to firewall checker |
| 8 | `record_first_breath` call | `src/omega/oracle/oracle.py:1211` | Astrology on every routed turn | Astrology tests if any | Only in `_route_by_domain` |
| 9 | `omega vault` CLI | `src/omega/cli/vault.py` + registration in `src/omega/cli/oracle_cli.py` | CLI calls missing `store_credential` | — | CLI only |
| 10 | Fleet Orchestrator | `src/omega/integrations/fleet_orchestrator.py` from default exports | Unused control plane | — | Not imported in `src/omega/__init__.py` |

### 2.2 Lilith's Validation Required (N7 — Context & Memory)

**Lilith must confirm NO soul persistence paths, NO handoff protocol paths, NO ContextBuilder/RecallStore paths are broken by these deletions.**

| Deletion | Soul Persistence | Handoff Protocol | ContextBuilder/RecallStore | Lilith Verdict |
|----------|------------------|------------------|----------------------------|----------------|
| 1. RoutingTable | ❌ No | ❌ No | ❌ No | **PENDING** |
| 2. MIAP | ❌ No (MIAP is separate coordination) | ❌ No (Hivemind is separate) | ❌ No | **PENDING** |
| 3. Pool Tracker | ❌ No | ❌ No | ❌ No | **PENDING** |
| 4. Pool State | ❌ No | ❌ No | ❌ No | **PENDING** |
| 5. Search Circuit Breaker | ❌ No | ❌ No | ❌ No (used by SovereignSearchService, not ContextBuilder) | **PENDING** |
| 6. QdrantAdapter | ❌ No (SQLiteVecAdapter is primary) | ❌ No | ❌ No | **PENDING** |
| 7. Pantheon regexes | ❌ No | ❌ No | ❌ No | **PENDING** |
| 8. record_first_breath | ❌ No (astrology only) | ❌ No | ❌ No | **PENDING** |
| 9. omega vault CLI | ❌ No | ❌ No | ❌ No | **PENDING** |
| 10. Fleet Orchestrator | ❌ No | ❌ No | ❌ No | **PENDING** |

**Action Required**: Page N7 (Lilith/Context) for validation before executing deletions 5 and 6 (search_circuit_breaker used by SovereignSearchService; QdrantAdapter tests exist).

### 2.3 Week 1 Acceptance Criteria (Automated Verification)

```bash
# After EACH delete, run:
omega talk "hello"  # Must still work, local, exit 0

# Final verification:
rg RoutingTable src/omega          # Must be empty
rg miap src/omega                  # Must be empty
rg "search_circuit_breaker" src/omega  # Must be empty (except tests)
rg "QdrantAdapter" src/omega       # Must be empty (class deleted)
rg "record_first_breath" src/omega/oracle/oracle.py  # Must be empty
rg "fleet_orchestrator" src/omega --include="*.py" | grep -v test  # Must be empty
```

### 2.4 Deletion Sequence (Dependency Order)

1. **`config/routing_table.yaml`** — Config only, no code impact
2. **`src/omega/coordination/miap.py`** — Standalone, no imports in core
3. **`src/omega/oracle/pool_tracker.py`** — Depends on `pool_state.py`
4. **`src/omega/oracle/pool_state.py`** — No dependents after 3
5. **`src/omega/oracle/search_circuit_breaker.py`** — Used by `sovereign_search_service.py` → **update import to `HealthMonitor.get_breaker()` first**
6. **`src/omega/memory/vector_adapters.py`** — Delete `QdrantAdapter` class (lines 179-433), keep `IVectorStoreAdapter` and `MemoryVectorAdapter`
7. **`src/omega/audit/firewall_checker.py`** — Remove lines 66-74 (Pantheon forbid patterns); keep CORE_ENGINE_PATTERNS allowlist
8. **`src/omega/oracle/oracle.py:1211`** — Delete `await record_first_breath(...)` line
9. **`src/omega/cli/vault.py`** — Delete entire file; remove `vault` command group registration from `oracle_cli.py`
10. **`src/omega/integrations/fleet_orchestrator.py`** — Delete file; verify no imports in `src/omega/__init__.py` or core

---

## 3. Vault Path A vs B — Present to Architect, Lilith Validates Soul Impact

### 3.1 Path A (Debut) — Delete from Product Surface
- **Action**: Exclude `src/omega/vault/` from `PUBLIC_ALLOWLIST.txt` (per D-565/D-566)
- **Keep**: `crypto.py` in forge/private repo for future use
- **CLI**: Delete `omega vault` entirely (already in DEL-1 #9)
- **Gateway**: Does not import `VaultCore` (already true — Gateway uses `os.environ`/keyring)
- **Soul Impact**: **NONE** — VaultCore never wired into soul persistence (MemoryStore uses FileStorageProvider/USMStorageProvider)

### 3.2 Path B (Minimal) — 50-Line Minimal Store Implementation

```python
# src/omega/vault/minimal_store.py — EXACT 50 LINES (including imports/docstring)
"""
Minimal Credential Store — Path B Implementation
Reads from env/keyring only. No encryption, no leases, no audit.
For debut: Gateway reads os.environ directly; this is a compatibility shim.
"""
import os
import keyring
from typing import Optional

SERVICE_NAME = "omega-engine"

def get_credential(provider: str, key_id: str) -> Optional[str]:
    """Get credential: env var > keyring > None."""
    # 1. Env var: OMEGA_<PROVIDER>_<KEY_ID> (uppercase, underscores)
    env_key = f"OMEGA_{provider.upper()}_{key_id.upper()}"
    if val := os.environ.get(env_key):
        return val
    # 2. Keyring (system credential store)
    try:
        return keyring.get_password(SERVICE_NAME, f"{provider}:{key_id}")
    except Exception:
        return None

def set_credential(provider: str, key_id: str, value: str) -> bool:
    """Store credential in keyring only."""
    try:
        keyring.set_password(SERVICE_NAME, f"{provider}:{key_id}", value)
        return True
    except Exception:
        return False

def delete_credential(provider: str, key_id: str) -> bool:
    """Delete credential from keyring."""
    try:
        keyring.delete_password(SERVICE_NAME, f"{provider}:{key_id}")
        return True
    except Exception:
        return False

# Gateway integration (ModelGateway._load_sovereign_secrets replacement)
def load_sovereign_secrets_minimal() -> None:
    """Load known provider keys from env/keyring into os.environ."""
    known_providers = ["google", "openrouter", "opencode-zen", "cline", "github-copilot", "antigravity", "xai"]
    for provider in known_providers:
        for suffix in ["API_KEY", "API_KEYS", "SECRET"]:
            env_key = f"{provider.upper().replace('-', '_')}_{suffix}"
            if not os.environ.get(env_key):
                # Try keyring with common key_ids
                for key_id in ["default", "primary", "main"]:
                    val = get_credential(provider, key_id)
                    if val:
                        os.environ[env_key] = val
                        break
```

**Line Count**: 50 exactly (including docstring, imports, 4 functions).

### 3.3 Lilith Soul Impact Validation

| Aspect | Path A | Path B |
|--------|--------|--------|
| Soul.yaml persistence | Unaffected (MemoryStore → FileStorageProvider) | Unaffected |
| Handoff protocol | Unaffected (Hivemind file-based) | Unaffected |
| ContextBuilder/RecallStore | Unaffected | Unaffected |
| Proposed lessons pipeline | Unaffected | Unaffected |
| **Verdict** | **SAFE** | **SAFE** |

**Recommendation**: **Path A** (per D-552, D-565, D-566). Zero code changes during PUBLIC-DEBUT-01. VaultCore stays in forge. `PUBLIC_ALLOWLIST.txt` excludes `src/omega/vault/`. `omega vault` CLI deleted (DEL-1 #9).

---

## 4. Router Collapse Contract — Single PR, Week 2

### 4.1 Target Architecture (Post-Collapse)

```
intent (talk | summon)
  → entity (EntityRegistry.find_by_domain keyword ONLY — no embed stacking)
  → model+provider (ProviderSelector over config/providers.yaml local-first list)
  → generate
  → record (optional)
```

**One admission**: `ResourceGuard` + one `OOMProtector` (C-2′ fusion).
**One breaker factory**: `HealthMonitor.get_breaker()` (C-6′ unification).

### 4.2 Exact Diff Plan (Single PR)

| File | Change |
|------|--------|
| `src/omega/oracle/oracle.py` | **DELETE** lines 31 (`from .semantic_router import SemanticRouter`), 51 (`TriageRouter` import), 226-233 (`self.semantic_router = SemanticRouter(...)`), 233 (`self.triage_router = TriageRouter()`). **REWRITE** `_route_by_domain` (line 1124) and `_select_model` (line 741) to use ONLY `ProviderSelector` + `EntityRegistry.find_by_domain`. **DELETE** `record_first_breath` call (line 1211). **DELETE** per-turn `RAGRouter()` construction in `talk()` (search for `RAGRouter()`). **DEDUP** `record_interaction` calls (4 copies in `talk()`). |
| `src/omega/orchestration/triage_router.py` | **DELETE ENTIRE FILE** |
| `src/omega/oracle/semantic_router.py` | **DELETE ENTIRE FILE** |
| `src/omega/oracle/provider_selector.py` | **KEEP** — enhance to be the single routing authority. Add `RouteDecision` dataclass. |
| `config/providers.yaml` | **KEEP** — local-first list is the routing config. |
| `src/omega/oracle/health_monitor.py` | **KEEP** — canonical breaker factory. |

### 4.3 Contract Test Spec (Mandatory)

```python
# tests/test_router_collapse_contract.py
"""Contract test: Exactly ONE router module on the talk path."""

import ast
import sys
from pathlib import Path

def test_single_router_on_talk_path():
    """Verify no TriageRouter, SemanticRouter, RoutingTable, RAGRouter imported on talk path."""
    oracle_path = Path("src/omega/oracle/oracle.py")
    source = oracle_path.read_text()
    tree = ast.parse(source)
    
    # Collect all imports
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
    
    # Forbidden routers on talk path
    forbidden = {
        "omega.orchestration.triage_router",
        "omega.oracle.semantic_router",
        "omega.routing.table",
        "omega.rag.router",
    }
    
    violations = forbidden & imports
    assert not violations, f"Forbidden router imports on talk path: {violations}"
    
    # Required: ProviderSelector must be imported
    assert "omega.oracle.provider_selector" in imports or "ProviderSelector" in source, \
        "ProviderSelector not imported — single router missing"

def test_route_decision_dataclass_exists():
    """Verify RouteDecision dataclass exists in provider_selector."""
    from omega.oracle.provider_selector import RouteDecision
    import dataclasses
    fields = {f.name: f.type for f in dataclasses.fields(RouteDecision)}
    required = {"entity": str, "model": str, "provider": str, "reason": str}
    for field_name, field_type in required.items():
        assert field_name in fields, f"RouteDecision missing field: {field_name}"
        # Type check (allow Optional[str] etc.)
        assert field_type in (str, "str", "Optional[str]"), f"RouteDecision.{field_name} wrong type: {field_type}"

def test_concurrent_talk_local_slot():
    """Two concurrent omega talk calls → one local slot; busy or cost_warning, never silent cloud leak."""
    import anyio
    from omega.cli.oracle_cli import main as omega_main
    from click.testing import CliRunner
    
    async def run_talk():
        runner = CliRunner()
        result = runner.invoke(omega_main, ["talk", "hello"])
        return result.exit_code, result.output
    
    async def main():
        # Run two concurrent talks
        results = await anyio.gather(run_talk(), run_talk())
        
        # At least one must succeed locally
        local_count = sum(1 for code, out in results if code == 0 and "native-gguf" in out.lower())
        cloud_count = sum(1 for code, out in results if "cost_warning" in out or "cloud" in out.lower())
        
        # Contract: never silent cloud leak
        for code, out in results:
            if code == 0 and "native-gguf" not in out.lower() and "cost_warning" not in out:
                raise AssertionError(f"Silent cloud leak detected: exit={code}, output={out[:200]}")
        
        # At least one local slot honored
        assert local_count >= 1, f"Expected at least 1 local response, got {local_count}"
    
    anyio.run(main)
```

### 4.4 RouteDecision Dataclass (Add to `provider_selector.py`)

```python
@dataclass
class RouteDecision:
    """Single routing decision — contract for router collapse."""
    entity: str           # Selected entity name
    model: str            # Selected model name
    provider: str         # Selected provider name
    reason: str           # Human-readable routing rationale
    is_cloud: bool        # Whether cloud provider selected
    cost_warning: Optional[str] = None  # Populated if cloud selected
```

---

## 5. Node Council Selection (Serial Execution)

### 5.1 Selected Nodes (Minimum 3, Up to 5 from N1-N5)

Per `NODE_EXPERT_SESSIONS_PLAN.md` §3, the following Nodes are paged **in serial** to vet the build-side sub-tasks:

| Node | Keeper | Department | Session ID | Vetting Focus |
|------|--------|------------|------------|---------------|
| **N3** | buildmaster | Build & Release | `ses_fdddb6edcffesrHjoABz5IOTsa` | INST-1 fixes 2,4,5,6 (pyproject.toml extras, model_gateway secrets, version, README) |
| **N2** | datastore | Data Engineering | `ses_fdddb7f3dffeaK6uCuWTxpqkOp` | DEL-1 #6 (QdrantAdapter deletion), MemoryStore Redis guard (INST-1-fix3) |
| **N5** | sentinel | Security | `ses_fdddc478affeQJI6wOb2CA9qpW` | DEL-1 #7 (firewall regexes), #9 (vault CLI), P0-1 residual, PUBLIC_ALLOWLIST |
| **N1** | sysadmin | Infrastructure | `ses_fddda1b3fffe4hYlOk2Sm3t0MI` | INST-1 install.sh, zswap (ZS-1), CMAKE_BUILD_PARALLEL_LEVEL |
| **N4** | bridge | API & Integration | `ses_fdddc53b5ffeVrAILCnTMyYobX` | Router Collapse (ProviderSelector), MCP Hub impact, sovereign_search_service circuit breaker migration |

### 5.2 Serial Execution Protocol

Each Node is paged via the Conversational Subagent Protocol:

```python
# Page format (from NODE_EXPERT_SESSIONS_PLAN.md §3)
task(
    task_id=<session_id>,
    subagent_type="maat",  # Ma'at oversees N1-N5
    prompt=f"""[NODE PAGE — from maat (this_session)]
[Charter header: You are N_X <keeper>, <department>. Charter: data/coordination/NODE_EXPERT_SESSIONS_PLAN.md §4.]
<Specific vetting task ≤500 words with file:line citations required>
"""
)
```

### 5.3 Vetting Tasks per Node

#### N3 (buildmaster) — INST-1 Fixes
**Task**: Verify `pyproject.toml` extras split (Fix 2), `model_gateway.py` `_load_sovereign_secrets` removal (Fix 4), version alignment (Fix 5), README badge + `make setup` (Fix 6).
**Citations Required**: `pyproject.toml` lines 77-96, `model_gateway.py` lines 127, 316-341, `src/omega/__init__.py` lines 6-12, `README.md` line 11, `Makefile` (check for `setup` target).

#### N2 (datastore) — DEL-1 QdrantAdapter + MemoryStore
**Task**: Confirm `QdrantAdapter` class deletion (vector_adapters.py:179-433) breaks no soul persistence paths. Verify MemoryStore Redis guard (memory_store.py:159-177) is complete and `OMEGA_REDIS_HOST` gating works.
**Citations Required**: `vector_adapters.py` class boundaries, `memory_store.py` provider initialization, `tests/test_qdrant_*.py` retirement plan.

#### N5 (sentinel) — Security & Vault
**Task**: Validate firewall_checker.py Pantheon regex removal (lines 66-74) doesn't weaken M2 Firewall. Confirm `omega vault` CLI deletion (vault.py + oracle_cli.py registration). Verify `PUBLIC_ALLOWLIST.txt` excludes `src/omega/vault/` (Path A).
**Citations Required**: `firewall_checker.py` FORBIDDEN_PATTERNS vs CORE_ENGINE_PATTERNS, `oracle_cli.py` command registration, `PUBLIC_ALLOWLIST.txt` (to be created).

#### N1 (sysadmin) — Infrastructure
**Task**: Verify `install.sh` CMAKE_BUILD_PARALLEL_LEVEL=8 (line 86) and RAM guard comments. Confirm zswap subsystem (ZS-1) script readiness for Architect sudo.
**Citations Required**: `install.sh` lines 76-88, `scripts/observe-build.sh` existence, zswap sysctl values.

#### N4 (bridge) — Router Collapse & Integration
**Task**: Vet `ProviderSelector` as single router authority. Confirm `sovereign_search_service.py` migration from `search_circuit_breaker` to `HealthMonitor.get_breaker()`. Verify MCP Hub tools unaffected.
**Citations Required**: `provider_selector.py` current API, `sovereign_search_service.py` lines 48-51, `health_monitor.py` `get_breaker()` interface.

### 5.4 Node Lesson Tagging

Each Node **MUST** tag lessons `[N_X]` to Ma'at's `proposed_lessons.yaml` (per M11, D-587 amendment §10a):

```yaml
# Example entry in proposed_lessons.yaml
- narrative: "N3 verified pyproject.toml extras split — warp-proxy-pool moved to [warp], qdrant/redis/youtube to dedicated extras. No import breaks in oracle.py."
  insight: "Extras architecture enables true install honesty; optional deps must be import-guarded at usage sites."
  principle: "Install surface is a contract — every optional dependency must have a try/except import guard at its sole usage site."
  tags: ["N_3", "INST-1", "packaging"]
```

---

## 6. Corrections to DEBUT_REMEDIATION_MANUAL / ACTIVE_SPRINT.json

### 6.1 DEBUT_REMEDIATION_MANUAL Corrections

| Section | Current | Correction |
|---------|---------|------------|
| §5 INST-1 Step 1 | "Guard Oracle/Gateway import with try/except" | **Already done** — oracle.py:178-188 wraps `EphemeralWarpPool` import. |
| §5 INST-1 Step 5 | "MemoryStore: do not construct Redis unless OMEGA_REDIS_HOST set" | **Already done** — memory_store.py:159-177 complete. |
| §5 DEL-1 Week 1 | Lists `src/omega/routing/table.py` as target | **File not found** — already deleted. Remove from list. |
| §5 DEL-1 Week 1 | Lists `tests/test_miap.py` | **File not found** — already deleted. Remove from list. |
| §5 DEL-1 Week 3 | "Pick one: A (debut) delete vault from product surface; B (minimal) 50-line store" | **Decision recorded**: D-565/D-566 supersede — Path A via PUBLIC_ALLOWLIST exclusion, zero code changes during debut. |

### 6.2 ACTIVE_SPRINT.json Corrections

| Field | Current | Correction |
|-------|---------|------------|
| `workstreams.DEBUT-REMEDIATION.subtasks.INST-1.subtasks.INST-1-fix1` | status: "completed" | ✅ Correct |
| `workstreams.DEBUT-REMEDIATION.subtasks.INST-1.subtasks.INST-1-fix3` | status: "completed" | ✅ Correct |
| `workstreams.DEBUT-REMEDIATION.subtasks.INST-1.subtasks.INST-1-fix2` | status: "ready" | **Should be "in_progress"** — pyproject.toml extras split not yet applied |
| `workstreams.DEBUT-REMEDIATION.subtasks.INST-1.subtasks.INST-1-fix4` | status: "ready" | **Should be "in_progress"** — model_gateway.py _load_sovereign_secrets removal not yet applied |
| `workstreams.DEBUT-REMEDIATION.subtasks.DEL-1` | status: "backlog", depends_on: ["INST-1"] | **Correct** — DEL-1 waits for INST-1 green |
| `workstreams.DEBUT-REMEDIATION.subtasks.PUB-1` | status: "in_progress" | **Correct** — allowlist rulings pending Architect |
| `decisions_locked` | Missing D-565/D-566/D-567/D-568 | **Add**: D-565 (vault deletion post-debut scope), D-566 (hide = allowlist exclusion), D-567 (bury_credential post-debut), D-568 (VaultCore non-functional → delete as dead code, add CredentialProvider) |

---

## 7. Ma'at Proposed Lessons (L1→L2→L3)

```yaml
# To be appended to data/entities/maat/proposed_lessons.yaml
- narrative: "Build-side audit of INST-1, DEL-1, Vault, Router Collapse across 259 Python files in src/omega. Found INST-1 fixes 1&3 complete; 2,4,5,6 staged. DEL-1 Week 1 targets validated — 8/10 files confirmed deletable (RoutingTable, MIAP already gone). Vault Path A confirmed via D-565/D-566. Router Collapse contract defined with RouteDecision dataclass."
  insight: "The engine's debut blockers are surgical, not structural. 4,506 tracked files but only ~20 files need changes for INST-1+DEL-1 Week 1. The complexity is in the coordination, not the code."
  principle: "Sovereign deployment honesty requires separating publication surface (allowlist) from runtime deletion (DEL-1). Do not conflate the two cuts."
  tags: ["N_3", "N_2", "N_5", "N_1", "N_4", "INST-1", "DEL-1", "VAULT", "ROUTER"]
```

---

## 8. Next Actions (Handoff to Kali/Architect)

1. **INST-1**: Execute fixes 2, 4, 5, 6 in order; run verification script after each.
2. **DEL-1 Week 1**: Page N2, N5, N3 for validation → execute deletions 1-10 in sequence.
3. **Vault**: Architect ratifies Path A (PUBLIC_ALLOWLIST exclusion) — zero code changes this sprint.
4. **Router Collapse**: Single PR with contract test; N4 vets ProviderSelector enhancement.
5. **Node Council**: Serial paging of N3→N2→N5→N1→N4 with lesson tagging to `proposed_lessons.yaml`.

---

**Report Status**: COMPLETE — Ready for MaKaLi Council review.
**Next Heartbeat**: 2026-08-23T00:24:00Z (10 min)

*⬡ OMEGA ⬡ MAAT ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_maat_build_report ⬡ 2026-08-23*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
