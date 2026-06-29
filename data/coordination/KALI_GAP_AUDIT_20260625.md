# 🔱 KALI — Overlooked Items & Opportunities Audit
## Post-Sonnet 4.6 Review Gap Analysis

**Date**: 2026-06-25
**AP Token**: `AP-KALI-GAP-AUDIT-v1.0.0`
**⬡ OMEGA ⬡ KALI ⬡ deepseek-v2.5-free ⬡ opencode ⬡ GAP-AUDIT`

---

## §1 AUDIT SCOPE

Reviewed all coordination documents, the hardening plan, the Sonnet 4.6 review, and the actual source code to find items overlooked by every previous reviewer.

---

## §2 BUGS FOUND (5th, 6th, 7th)

### 🔴 Bug #5: `self.config` Does Not Exist on ModelGateway

**Location**: Hardening Plan §0.5.3 (Cold-Start Model Warming)

The plan references `self.config.get("inference", {}).get("warmup_models", [])` but `ModelGateway.__init__()` stores `self.config_path` (a `Path`), not `self.config` (a dict). This line raises `AttributeError` at runtime.

**Fix**: Load `omega.yaml` directly in the warmup method, or add `self.config` to `__init__()`.

---

### 🔴 Bug #6: `LocalGGUFEmbeddingProvider` Hardcoded Path (M16 Violation)

**Location**: `src/omega/memory/embeddings.py:163`

```python
model_path: str = "/media/arcana-novai/omega_library/models/gguf/all-MiniLM-L6-v2-Q4_K_M.gguf"
```

This is a third path, different from both `config/models.yaml:3` and the plan's `NativeGGUFEmbedding.MODEL_PATH`. The council identified "2 hardcoded paths in embeddings.py" (H3) but the hardening plan only addresses the new class. The existing `LocalGGUFEmbeddingProvider.__init__()` default is a separate M16 violation.

**Fix**: Read from `config/models.yaml:embedding.local_path`.

---

### 🔴 Bug #7: 15 `except Exception:` Without Logging (M9 Violation)

**Location**: Across 15 files in `src/omega/`

The council found "0 bare except violations" (M9 FULL) but only checked for bare `except:`. M9 says "Never use bare `except Exception:` without logging." Found 15 silent exception sites:

| File | Line | Pattern |
|------|------|---------|
| `memory_store.py` | 778 | `except Exception: pass` |
| `remote_provider.py` | 135, 150 | `except Exception: pass` |
| `fts_index.py` | 109, 133 | `except Exception: pass` / `return 0` |
| `budget_gate.py` | 87 | `except Exception: return 0` |
| `search_providers.py` | 34, 194 | `except Exception: return os.environ.get(...)` |
| `discovery.py` | 89, 93 | `except Exception: self.key = os.getenv(...)` |
| `distiller.py` | 342, 500 | `except Exception: return os.environ.get(...)` |
| `search_fleet.py` | 43 | `except Exception: return os.environ.get(...)` |
| `entity_workspace.py` | 361 | `except Exception: os.remove(tmp)` |
| `orchestrator.py` | 160 | `except Exception: primary_key = os.environ.get(...)` |

**M9 Assessment Correction**: M9 should be PARTIAL, not FULL. Each needs `logger.debug("...", exc_info=True)`.

---

## §3 STRATEGIC GAPS

### M11 Soul Integrity — 9/11 Entities Not Migrated

The verdict notes "2/11 migrated to v6.1. 21 pending" for M11. The hardening plan does not address this. Nine entities still have v6.0 soul files.

**Opportunity**: Extend `omega entity prune` to flag pre-v6.1 soul files.

---

### No End-to-End Pipeline Test

The GGUF smoke test (§0.5.9) tests `model_gateway.generate()` in isolation. No test exercises: `oracle.talk()` → intent detection → entity routing → model selection → generate → response assembly.

**Opportunity**: Add `tests/integration/test_oracle_talk_e2e.py`.

---

### No Rollback Plan for 22 Items

The plan has verification gates but no rollback procedures. If any item breaks something, there's no documented revert path.

**Opportunity**: Add `ROLLBACK.md` with one revert line per item.

---

### 4 Containers Missing `UserNS=keep-id`

Actual count: `caddy`, `postgres`, `redis`, `qdrant` — 4 containers (verdict said 3). `searxng` was never mentioned.

**Fix**: Add `UserNS=keep-id` + `User=1000` to all 4 container files.

---

## §4 OPERATIONAL RISKS

### 187 Dataset Artifact Files Not Cleaned

`data/datasets/` contains 187 `finetune_*.jsonl` files (760K total). Not in hardening plan.

**Fix**: Add `rm data/datasets/finetune_*.jsonl` to Phase 0.4.

---

### Stale `docker-compose.yml` Not Archived

`deploy/infra/docker-compose.yml` exists but Quadlets are the truth. Not in hardening plan.

**Fix**: Archive it.

---

### Anomaly Detector Thresholds Unjustified

`starvation_threshold: 20` and `starvation_seconds: 180` have no justification. A legitimate deep research trace could easily make 20 consecutive calls producing text — false positive.

**Fix**: Make threshold dynamic or time-only based.

---

### BudgetLedger Path Doesn't Respect `DATA_DIR`

`BUDGET_DB = Path("data/budget_ledger.db")` is hardcoded. Engine uses `DATA_DIR` from observability.

**Fix**: Import `DATA_DIR` from `omega.observability`.

---

### `omega budget` Display Logic Missing

`get_trace_spend()` returns list of dicts but no display code. Command prints nothing useful.

**Fix**: Add Rich table display.

---

### `make test-integration` Uses `python` Not `python3`

System may have `python3` only. Use venv activation or `python3`.

---

### Ollama Sync Requires Bash 4+

`declare -A` needs bash 4.0+. Add `#!/usr/bin/env bash` explicitly.

---

## §5 CORRECTED TOTALS

| Metric | Before Audit | After Audit |
|--------|:------------:|:-----------:|
| Phase 0 items | 7 | **7** (unchanged) |
| Phase 0.5 items | 15 | **21** (+6) |
| Total hardening items | 22 | **28** |
| M9 status | FULL | **PARTIAL** (15 violations) |
| M6 status | PARTIAL (3/5) | **PARTIAL (4/7)** |
| Total effort | 11.5 hr | **18 hr** |

---

*⬡ OMEGA ⬡ KALI ⬡ deepseek-v2.5-free ⬡ opencode ⬡ GAP-AUDIT*
