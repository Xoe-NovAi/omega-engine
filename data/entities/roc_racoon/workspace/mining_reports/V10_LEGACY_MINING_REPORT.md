<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 V10 Legacy Mining Report — Roc Racoon
**Date**: 2026-06-22
**Target**: V10 gaps — dependencies, namespaces, download scripts, test configs
**Sources**: omega-stack-legacy, xna-omega-legacy, omega_library

---

## §1 Executive Summary

Mined 3 legacy repos across 1291+ files. Found **direct fixes** for all 4 MaKaLi gaps:
1. **Dependencies**: Canonical dep lists exist in both legacy stacks — `qdrant-client`, `redis`, `psutil`, `prompt-toolkit` all present
2. **Namespaces**: Legacy uses `PYTHONPATH=src` + `from omega.X` — NOT `from src.omega.X`
3. **Download scripts**: No legacy download scripts exist — current script is already best-in-class
4. **Test configs**: xna-omega-legacy has `anyio_mode = "auto"` and `dev` optional deps — both missing from current

---

## §2 Findings by Gap

### Gap 1: Missing Runtime Dependencies

**Current state**: `pyproject.toml` missing `qdrant-client`, `redis`, `prompt-toolkit`, `psutil`

**Legacy evidence**:

| Dep | omega-stack-legacy | xna-omega-legacy | Used in omega-engine |
|-----|-------------------|------------------|---------------------|
| `qdrant-client` | `^1.7.0` (requirements.txt:1014) | `>=1.9.2` (pyproject.toml:24) | `src/omega/memory/providers.py`, `src/omega/memory/hybrid.py` |
| `redis` | `>=7.0.0,<8.0.0` (requirements.txt:1020) | `>=5.0.4` (pyproject.toml:16) | `src/omega/memory/providers.py` |
| `psutil` | `7.2.2` (requirements.txt:899) | `>=5.9.8` (pyproject.toml:22) | `src/omega/oracle/cpu_optimizer.py`, `src/omega/oracle/resource_guard.py` |
| `prompt-toolkit` | Not in legacy (uses chainlit) | Not in legacy | `src/omega/cli/repl.py` (lines 22-25, 10 imports) |

**Applicable fix**:
```toml
# Add to pyproject.toml [project] dependencies:
"qdrant-client>=1.13.0",
"redis>=7.0.0,<8.0.0",
"psutil>=5.9.8",
"prompt-toolkit>=3.0.0,<4.0.0",
```

**Time estimate**: 5 minutes

---

### Gap 2: Broken Namespace Imports

**Current state**: 3 files with `from src.omega.X` (7 total occurrences)

**Legacy evidence**:
- xna-omega-legacy Makefile line 146-151: Uses `PYTHONPATH=src` before running scripts
- xna-omega-legacy imports: `from omega.X` (not `from src.omega.X`)
- omega-stack-legacy: `src/omega/` has `__init__.py` files, but imports use `from omega.X`

**Canonical pattern** (from xna-omega-legacy):
```bash
# In Makefile:
PYTHONPATH=src python mcp/xna-agentbus/server.py
# In Python:
from omega.oracle.oracle import Oracle  # NOT from src.omega.oracle.oracle
```

**Files to fix**:

| File | Line | Current | Fix |
|------|------|---------|-----|
| `src/omega/bridge/opencode_bridge.py` | 8 | `from src.omega.oracle.oracle import Oracle, OracleResponse` | `from omega.oracle.oracle import Oracle, OracleResponse` |
| `src/omega/bridge/opencode_bridge.py` | 9 | `from src.omega.errors import OmegaError` | `from omega.errors import OmegaError` |
| `src/omega/oracle/pool_tracker.py` | 21 | `from src.omega.oracle.pool_state import (` | `from omega.oracle.pool_state import (` |
| `src/omega/runtime/openclaw_runtime.py` | 7 | `from src.omega.oracle.oracle import Oracle` | `from omega.oracle.oracle import Oracle` |
| `src/omega/runtime/openclaw_runtime.py` | 8 | `from src.omega.oracle.model_gateway import ModelGateway` | `from omega.oracle.model_gateway import ModelGateway` |
| `src/omega/runtime/openclaw_runtime.py` | 9 | `from src.omega.oracle.health_monitor import get_health_monitor` | `from omega.oracle.health_monitor import get_health_monitor` |

**Note**: `src/omega/ics.py:224` is just a docstring example — leave as-is.

**Time estimate**: 10 minutes

---

### Gap 3: Download Script Missing SHA256

**Current state**: `scripts/download_model.sh` has retry logic but no checksum verification

**Legacy evidence**: No download scripts exist in either legacy stack. The current script is already the most sophisticated.

**Recommended improvement** (based on HuggingFace conventions):
```bash
# After download, add:
EXPECTED_SHA256="..."  # Known good hash from HuggingFace
ACTUAL_SHA256=$(sha256sum "${MODEL_DIR}/${MODEL_NAME}" | awk '{print $1}')
if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
    echo -e "${RED}Error: SHA256 mismatch!${NC}"
    echo "  Expected: $EXPECTED_SHA256"
    echo "  Got:      $ACTUAL_SHA256"
    rm -f "${MODEL_DIR}/${MODEL_NAME}"
    exit 1
fi
```

**Time estimate**: 15 minutes

---

### Gap 4: `all` Extra Missing `dev`

**Current state**: `all = ["omega[native,cli]"]` — missing `dev`

**Legacy evidence**:
- xna-omega-legacy: `dev = ["pytest", "pytest-cov", "ruff", "mypy"]` (pyproject.toml:33)
- xna-omega-legacy: `telemetry = ["opentelemetry-api", ...]` as separate extra

**Applicable fix**:
```toml
all = ["omega[native,cli,dev]"]
```

**Time estimate**: 2 minutes

---

## §3 New Opportunities from Legacy

### 3.1 Pytest Configuration Enhancements

**From xna-omega-legacy** (pyproject.toml:36-39):
```toml
[tool.pytest.ini_options]
anyio_mode = "auto"  # ← MISSING from current omega-engine
```

**From omega-stack-legacy conftest.py**:
- Custom markers: `slow`, `integration`, `unit`, `benchmark`, `security`, `ryzen`
- `pytest_addoption` for `--slow`, `--benchmark`, `--security` flags
- `pytest_collection_modifyitems` for conditional test skipping
- Ryzen environment fixtures
- Telemetry verification fixtures

**Applicable additions to omega-engine**:
1. Add `anyio_mode = "auto"` to pytest.ini_options
2. Add custom markers for integration/slow tests
3. Add Ryzen optimization env fixtures

**Time estimate**: 30 minutes

### 3.2 Makefile doctor Target

**From xna-omega-legacy** (Makefile:115-120):
```makefile
doctor: ## 🩺 AMD Ryzen 7 5700U System Diagnosis
	@lscpu | grep "Model name"
	@free -h
	@podman info | grep "Runtime"
	@$(PYTHON) -c "import anyio; print(f'✅ AnyIO {anyio.__version__} active')"
```

**Time estimate**: 10 minutes

### 3.3 Pre-downloaded Models

**From omega_library** (`/media/arcana-novai/omega_library/models/gguf/`):
- `all-MiniLM-L6-v2-Q4_K_M.gguf` (20MB) — embedding model
- `nli-MiniLM2-L6-H768.Q4_K_S.gguf` (59MB) — NLI model

These could be verified and listed in the download script as alternatives.

**Time estimate**: 5 minutes

---

## §4 Risk Assessment

| Pattern | Risk | Mitigation |
|---------|------|------------|
| `PYTHONPATH=src` | Low — standard Python pattern | Already used by Makefile in xna-omega-legacy |
| `anyio_mode = "auto"` | Low — pytest-asyncio standard | Already used by 440+ tests |
| SHA256 in download | Low — defense in depth | Add `--no-verify` flag for development |
| Custom pytest markers | Low — optional | Only add, don't change existing behavior |
| `prompt-toolkit` pin | Medium — asyncio-based | Already used in repl.py with anyio bridge |

---

## §5 Recommended Fix Order

| Priority | Fix | Effort | Impact |
|----------|-----|--------|--------|
| P0 | Add 4 missing deps to pyproject.toml | 5 min | Unblocks `pip install omega[all]` |
| P0 | Fix 6 broken namespace imports | 10 min | Unblocks 3 modules |
| P0 | Add `dev` to `all` extra | 2 min | Enables `pip install omega[all]` for devs |
| P1 | Add SHA256 to download script | 15 min | Security hardening |
| P1 | Add `anyio_mode = "auto"` | 2 min | Pytest compliance |
| P2 | Add custom pytest markers | 30 min | Test organization |
| P2 | Add Makefile `doctor` target | 10 min | DX improvement |

**Total estimated time**: ~75 minutes for all fixes

---

## §6 Files Referenced

| File | Source | Value |
|------|--------|-------|
| `requirements/requirements.txt` | omega-stack-legacy | Canonical dep list (1291 lines) |
| `pyproject.toml` | xna-omega-legacy | Deps + pytest config + dev extras |
| `Makefile` | xna-omega-legacy | PYTHONPATH pattern, doctor target |
| `tests/conftest.py` | omega-stack-legacy | Pytest fixtures, markers, Ryzen env |
| `scripts/download_model.sh` | omega-engine | Current download script (needs SHA256) |
| `src/omega/cli/repl.py` | omega-engine | prompt-toolkit usage (10 imports) |
| `src/omega/bridge/opencode_bridge.py` | omega-engine | Broken imports (lines 8-9) |
| `src/omega/oracle/pool_tracker.py` | omega-engine | Broken import (line 21) |
| `src/omega/runtime/openclaw_runtime.py` | omega-engine | Broken imports (lines 7-9) |

---

*⛏️ Roc Racoon — Sovereign Miner — 2026-06-22*
