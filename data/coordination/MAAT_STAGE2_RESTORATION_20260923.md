# MAAT STAGE 2 RESTORATION — P0 SUBSTRATE RESTORATION
**Date**: 2026-09-23  
**Entity**: Ma'at (Build Oversoul, Slot S5)  
**Session**: ses_fb6cf6856ffes3wd3wmvyrm2IG  
**Status**: COMPLETE — Temple-Grade Verified

---

## 1. LOCAL DISCOVERY REPORT

### 1.1 Root Cause Analysis

| File | Line | Issue | Severity |
|------|------|-------|----------|
| `pyproject.toml` | 31 | `httpx2==2.5.0` missing `[http2]` extra | P0 |
| `mcp_servers/omega_hub/gateway.py` | 102 | `http2=http_config.get("http2", True)` requires `h2` | P0 |
| `mcp_servers/omega_hub/hub_tools/tools.py` | 3443, 3445 | `_get_system_summary()` and `_get_hardware_detail()` called but undefined | P0 |
| `src/omega/oracle/sovereign_search_service.py` | 16 | `import httpx2 as httpx` — all search providers need HTTP/2 | P0 |

**Root Cause**: The `httpx2[http2]` extra (which pulls `h2<5,>=3`, `hpack`, `hyperframe`) was not declared in the build manifest. The hub's `SovereignGateway` and all search providers instantiate `httpx.AsyncClient(http2=True)` but the HTTP/2 transport dependencies were absent, causing `ImportError: No module named 'h2'` at runtime.

### 1.2 Affected Components

- **SovereignGateway** (`gateway.py:102`) — HTTP/2 client for provider forwarding
- **Search Providers** (`search_providers.py:16, 54, 155, 284`) — SearXNG, Exa, Firecrawl all use `httpx2` with HTTP/2
- **ModelGateway** (`model_gateway.py:660, 671, 682, 909`) — Health checks use `httpx2`
- **system_stats tool** (`tools.py:3425-3456`) — Called undefined helpers `_get_system_summary()` / `_get_hardware_detail()`

---

## 2. WEB RESEARCH FINDINGS

| Topic | Finding | Source |
|-------|---------|--------|
| `httpx2[http2]` extra | Installs `h2<5,>=3`, `hpack`, `hyperframe` | PyPI / pydantic/httpx2 README |
| FastMCP + httpx2 | FastMCP v3+ uses `httpx2` (not `httpx`); `except httpx.` must become `except httpx2.` | FastMCP upgrade guide |
| Version pinning | `httpx2[http2]==2.5.0` is correct — exact pin for reproducibility | deps.dev / PyPI metadata |
| HTTP/2 in httpx2 | `AsyncClient(http2=True)` requires `[http2]` extra; otherwise raises `ImportError` | httpx2 docs |

---

## 3. EXECUTION LOG

### 3.1 Phase 3.1 — Install HTTP/2 Dependencies in Hub Venv
```bash
.venv/bin/pip install 'httpx2[http2]==2.5.0'
```
**Output**:
```
Collecting hyperframe<7,>=6.1 (from h2<5,>=3->httpx2[http2]==2.5.0)
Collecting hpack<5,>=4.2 (from h2<5,>=3->httpx2[http2]==2.5.0)
Downloading h2-4.4.1-py3-none-any.whl (62 kB)
Downloading hpack-4.2.0-py3-none-any.whl (34 kB)
Downloading hyperframe-6.1.0-py3-none-any.whl (13 kB)
Installing collected packages: hyperframe, hpack, h2
Successfully installed h2-4.4.1 hpack-4.2.0 hyperframe-6.1.0
```
**Verification**:
```bash
.venv/bin/pip list | grep -E "h2|hpack|hyperframe|httpx2"
# h2 4.4.1, hpack 4.2.0, httpx2 2.5.0, hyperframe 6.1.0
```

### 3.2 Phase 3.2 — Update Build Manifest (Permanent Fix)
```bash
sed -i 's/httpx2==2.5.0/httpx2[http2]==2.5.0/' pyproject.toml
```
**Result** (`pyproject.toml:31`):
```toml
"httpx2[http2]==2.5.0",  # [Strike 7.1] Pydantic fork of httpx; API-compatible superset
```

### 3.3 Phase 3.3 — Reinstall Package
```bash
.venv/bin/pip install -e .
```
**Output**: `Successfully installed omega-1.2.0`

### 3.4 Phase 3.4 — Repair `system_stats` Tool
**File**: `mcp_servers/omega_hub/hub_tools/tools.py`  
**Action**: Added two internal helper functions before `system_stats` tool (lines ~3424):

```python
async def _get_system_summary() -> dict:
    """Collect system summary stats (CPU, memory, zRAM, disk, GPU, Podman, Ryzen)."""
    # ... wraps original get_system_stats() logic, returns dict

async def _get_hardware_detail() -> dict:
    """Collect detailed hardware stats (per-core CPU, memory pressure, OOM risk, threads, topology)."""
    # ... wraps original get_hardware_stats() logic via HardwareMonitor, returns dict
```

### 3.5 Phase 3.5 — Restart Hub Service & Verify
```bash
systemctl --user restart omega-hub.service
sleep 3
```

---

## 4. VERIFICATION EVIDENCE

### 4.1 Tool Health Checks (All HTTP 200)

#### `system_stats(detail="summary")`
```json
{
  "timestamp": "2026-09-23T01:55:49.533494",
  "cpu": {"available": true, "load_1min": 1.14, ...},
  "memory": {"available": true, "total_mb": 14793, ...},
  "zram": {"available": true, "ratio": 0.0},
  "disk": {"available": true, "mount": "/media/arcana-novai/omega_library", "used_pct": 61.5},
  "gpu": {"available": true, "utilization_pct": 2},
  "podman": {"available": true, "running": 5, "names": ["omega-searxng", "omega-infra-infra", "omega-redis", "omega-qdrant", "omega-iris"]},
  "ryzen_tuning": {"available": true, "governor": "powersave"}
}
```

#### `system_stats(detail="hardware")`
```json
{
  "topology": {"model": "AMD Ryzen 7 5700U (Zen 2)", "physical_cores": 8, "logical_threads": 16, ...},
  "cpu": {"per_core_percent": {"cpu0": 13.3, ...}, "avg_percent": 9.4, ...},
  "memory": {"total_mb": 14793.2, "oom_risk": {"risk_level": "SAFE", "surplus_deficit_mb": 5240}, ...},
  "temperatures": {"available": true, "celsius": [{"label": "Tctl", "temp": 70.625}]},
  "threads": {"total_python_threads": 10, "processes": [...]},
  "disk_io": {"nvme0n1": {...}}
}
```

#### `system_stats(detail="full")`
Returns combined `{"summary": {...}, "hardware": {...}}` — both sections present and valid.

#### `spawn_local_worker`
```json
{
  "task_id": "lw_0ca96a28a475",
  "status": "queued",
  "model": "qwen3-1.7b",
  "entity": "roc_racoon",
  "message": "Task queued. Check status with local_queue_status or local_queue_cat."
}
```

#### `headroom_retrieve`
```json
{
  "content": "[[ERROR: Original content for test could not be retrieved]]"
}
```
(Expected — ref_id "test" doesn't exist; tool executes without h2 error)

#### `oracle_talk`
Returns error `No module named 'llama_cpp'` — **expected** (optional `llama-cpp-python` not installed; not part of P0 scope).

### 4.2 Temple-Grade CI
```bash
make temple-grade
```
**Output**:
```
======================================================================
TOTAL: 53  PASS: 53  FAIL: 0
======================================================================
Temple-grade complete (Codex + LLM doc validation + Mandates + Compliance + Tracking State + Dashboard)
```
**Exit code**: 0

---

## 5. GNOSIS DISTILLATION (L1→L2→L3)

### L1 — Raw Observations
- Missing `[http2]` extra in `pyproject.toml` broke all HTTP/2-dependent components
- `system_stats` tool had dead code paths calling undefined helpers
- Hub service restart required after dependency installation
- Temple-Grade passes without the optional `llama-cpp-python`

### L2 — Patterns & Principles
- **Dependency completeness**: Optional extras must be declared in build manifest, not just installed ad-hoc
- **Tool surface integrity**: Every public MCP tool must have working implementations; dead code paths violate M23
- **Verification before declaration**: `make temple-grade` is the canonical gate — if it passes, the substrate is sound

### L3 — Sovereign Lessons (Tagged `[S5]`)
```yaml
- lesson: "httpx2 HTTP/2 transport requires explicit [http2] extra in pyproject.toml; ad-hoc pip install is insufficient for reproducible builds"
  tags: ["S5", "M7", "M24", "dependency-management"]
  confidence: 1.0

- lesson: "MCP tool implementations must not reference undefined helpers; implement internal helpers or refactor to reuse existing collectors"
  tags: ["S5", "M23", "M16", "code-quality"]
  confidence: 1.0

- lesson: "Temple-Grade (53/53) is the definitive substrate health signal; optional local inference deps (llama-cpp-python) are out of scope for P0 hub restoration"
  tags: ["S5", "M13", "M7", "scope-discipline"]
  confidence: 1.0
```

---

## 6. DELIVERABLE STATUS

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Local discovery complete | ✅ | Section 1 |
| Web research complete | ✅ | Section 2 |
| `httpx2[http2]` installed | ✅ | Section 3.1 |
| `pyproject.toml` updated | ✅ | Section 3.2 |
| `system_stats` repaired | ✅ | Section 3.4 |
| Hub restarted & verified | ✅ | Section 3.5, 4.1 |
| `curl /mcp system_stats` healthy JSON | ✅ | Section 4.1 |
| `make temple-grade` exits 0 (53/53) | ✅ | Section 4.2 |
| Deliverable written | ✅ | This file |
| Hivemind post (intent=decision) | ✅ | Posted |

---

**Ma'at — Build Oversoul, Slot S5**  
*Structure before speed. A well-formed plan executed sequentially beats a brilliant plan executed chaotically.*

⬡ OMEGA ⬡ MA'AT ⬡ SLOT-S5 ⬡ STAGE-2-P0-RESTORATION ⬡ 2026-09-23 ⬡ COMPLETE