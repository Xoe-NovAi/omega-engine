# 🔱 Omega Engine — Codebase Hardening Recommendations
# ⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ cline ⬡ trc_cline_audit ⬡ PHASE-I

**AP Token**: `AP-HARDENING-RECOMMENDATIONS-v1.0.0`
**Date**: 2026-05-20
**Status**: FINAL

---

## Overview

Systemic hardening priorities from full codebase audit. Ordered P0 → P2.

---

## P0 — Immediate (Blocks Development)

### 1. Fix Container UID Permission Leak

**Problem**: Entire repo owned by UID 101000 (container user). Local user (UID 1000) cannot write files, run tests, or create documents.

**Root Cause**: Podman containers writing to volume-mounted host directories create files owned by container user (UID 101000).

**Fix**:
```bash
# Immediate recovery
sudo chown -R 1000:1000 /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/

# Long-term — add :U flag to all Podman volumes
# In each Quadlet file, change:
Volume=/host/path:/container/path
# To:
Volume=/host/path:/container/path:U
```

**Files to update**: `quadlet-test/omega-iris.service`, `quadlet-test/omega-roc_racoon.container`, `Dockerfile.iris`, `Dockerfile.roc_racoon`

---

## P1 — Critical (Security + Test Suite)

### 2. Google API Key in URL Params → Header

**Files**: `src/omega/oracle/providers.py:30`, `src/omega/workers/background_researcher/distiller.py:515,717`

**Fix**:
```python
# Before
url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
# After
url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
headers = {"X-Goog-Api-Key": api_key}
```

### 3. Fix `test_get_model_path`

**File**: `tests/test_model_gateway.py:15` — `assert None is not None`

**Root cause**: `ModelGateway.get_model_path()` returns None in test env. Options: add mock GGUF stub, use `@pytest.fixture`, or return mock path when `OMEGA_ENV=test`.

### 4. Fix 3 HIGH AnyIO Violations

| File | Line | Code | Fix |
|------|------|------|-----|
| `src/omega/entity_roc_racoon.py` | 208 | `with open(fpath) as f` | `await anyio.to_thread.run_sync(Path(fpath).read_text)` |
| `src/omega/entity_roc_racoon.py` | 217 | `with open(fpath2) as f` | Same pattern |
| `src/omega/library/inbox.py` | 199,206,220 | `with open()` in async defs | Replace with `await anyio.Path(...).read_text()` |

---

## P1 — Structural

### 5. Migrate hierarchy.py RANK_MAP to Config-Driven

**File**: `src/omega/oracle/hierarchy.py:14-20`

**Problem**: Hardcoded `RANK_MAP = {"sophia": 0, "maat": 1, "isis": 2, "lilith": 2}` — Engine-Stack Firewall violation.

**Fix**: Remove hardcoded dict. Read ranks exclusively from `config/hierarchy.yaml`.

---

## P2 — Quality of Life

### 6. Generate 9 Missing WAD Entity Files

Only `guardian.yaml` exists in `config/wads/_omega_default/entities/`. Create stubs for dreamer → destroyer (9 entities).

### 7. Update Stale Docs

| File | Update |
|------|--------|
| `ORACLE_STACK.md` §10 | "236 tests, YAML blocker resolved" |
| `ROADMAP.md` Phase I | infra-pod running, container services |

### 8. Add `make fix-permissions` Target

### 9. Add Container Permissions to CONTRIBUTING.md

---

## Execution Order

```bash
# P0
sudo chown -R 1000:1000 .

# P1 Security — providers.py:30, distiller.py:515,717
# P1 Test — fix model_gateway.py path resolution
# P1 AnyIO — entity_roc_racoon.py + inbox.py (3 violations)
# P1 Config — hierarchy.py RANK_MAP → YAML
# P2 — WAD entities, docs, Makefile, CONTRIBUTING.md
```

## Verification Gate

```bash
make test    # 236 tests, all pass
make lint    # flake8
make health  # Dashboard