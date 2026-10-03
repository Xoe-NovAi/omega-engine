# 🔧 TOOL REVIEW — CARMACK (Slot S3: Engineering & Substrate)

**Reviewer:** John Carmack (Slot S3 — Engineering & Substrate)
**Date:** 2026-09-22
**Source:** TOOL_AUDIT_20260922.md + live hub probes (tools/call) + primary source code (tools.py, gateway.py, state.py, oracle.py)
**Confidence:** 10/10 for code-verified findings; 9/10 for live probes (live server runs repo tree with `omega` resolved via sys.path to `src/`)

---

## Verdict Table

| Tool | Verdict | Rationale |
|------|---------|-----------|
| `check_models_directory` | **KEEP** | Works live (10 GGUF models). Directly feeds `spawn_local_worker` model selection — an agent must see the inventory before choosing a model. One glob, ~0ms. The `_deprecated` marker pointing to a CLI is wrong-headed: agents call MCP tools, not CLIs. Remove the deprecation marker, keep the tool. |
| `check_podman_storage` | **CONSOLIDATE** | Works live (3.6GB) but near-zero agent utility — `podman system df` via bash is equivalent. Fold the `size_mb` metric into `system_stats`' podman section (the summary collector already reports running/total containers). 5-line addition. Low priority. |
| `system_stats` | **NEEDS_INFO** | The intended unified tool is **BROKEN TWICE**: (1) blocked by the h2 service-init failure (live-verified), (2) calls `_get_system_summary()` / `_get_hardware_detail()` which are **undefined in the entire repo** — after the h2 fix it will NameError. The two helpers must be implemented (~20 lines wrapping the existing collectors) before this can replace the fragmented pair. Do NOT remove the working pair until this is fixed. |
| `get_system_stats` | **CONSOLIDATE** | Works live (zRAM/CPU/disk/GPU/podman summary). Currently the ONLY working summary tool — fold into `system_stats(detail='summary')` once that is repaired. Keep until then. |
| `get_hardware_stats` | **CONSOLIDATE** | Works live (per-core %, topology, L3 victim cache confirmed on Ryzen 5700U). Fold into `system_stats(detail='hardware')` once repaired. Keep until then. |
| `headroom_retrieve` | **KEEP** | Backed by real code: `oracle.retrieve_headroom_content` (oracle.py:907) → `HeadroomStore.retrieve`. This is the decompression half of the Headroom system — agents receive `ref_id`s in compressed context and need this to recover fidelity. Blocked only by the shared h2 P0. HR workstream is post-debut but the plumbing exists and works. |
| `local_queue_cat` | **CONSOLIDATE** | Three tools for one queue is surface bloat. Fold into a single `local_queue` (action=cat) matching the codebase's own unified dispatch convention (github, hivemind_handoff, library_inbox, oracle_debug). |
| `local_queue_list` | **CONSOLIDATE** | Fold into `local_queue` (action=list). |
| `local_queue_status` | **CONSOLIDATE** | Fold into `local_queue` (action=status). |
| `spawn_local_worker` | **KEEP** | Core local inference primitive (M7 local-first). **Currently DOWN live** (h2 init failure) — P0. Also: **duplicate registration bug** — two definitions in tools.py (lines 253 and 377); FastMCP keeps the FIRST (live schema has no `top_p`), so the second variant with `top_p` is dead code. Delete the shadowed duplicate. |
| `sovereignty_ratio` | **KEEP** | Works live (22% local / 78% cloud). Canonical Sovereignty Scorecard (M7/D203). The council needs this number to enforce local-first. The 22% figure is a wake-up call, not a reason to remove the tool. |

---

## httpx[h2] dependency

**Severity: P0 — service-wide outage, not a system_stats bug.**

**Root cause (code-verified):**
- `gateway.py:102` — `http2=http_config.get("http2", True)` (default **True**)
- `github_tools.py:38` — `http2=True`
- Both construct an httpx-family `AsyncClient` with HTTP/2 enabled, but the hub venv has **no `h2` package** (verified: no h2/hpack/hyperframe in site-packages). Both `httpx` 0.28.1 and `httpx2` 2.5.0 declare `h2` as an optional extra — neither is installed with it.
- `pyproject.toml:31` pins `httpx2==2.5.0` **without** the `[http2]` extra — a dependency declaration gap.

**Impact (live-verified):** `_init_services()` fails → `_init_error` set → **every tool calling `_require_service()` fails**: `system_stats`, `headroom_retrieve`, `spawn_local_worker`, `local_queue_*`, `oracle_*`, `sovereign_search`, etc. The local inference path (M7) is DOWN.

**Fix (quick, ~5 minutes):**
1. Immediate: `pip install 'httpx[http2]'` in the hub venv (pulls `h2<5,>=3` + hpack + hyperframe, ~1MB).
2. Permanent: change `pyproject.toml:31` to `httpx2[http2]==2.5.0` and reinstall — so the next fresh venv doesn't regress.

**Owner:** Ma'at (build governance) — it is a dependency declaration gap in the build manifest. Do NOT band-aid with `http2: false` in omega.yaml; HTTP/2 is worth keeping for the gateway. Install the package.

---

## Summary

**Counts:** KEEP 4 · REMOVE 0 · CONSOLIDATE 6 · NEEDS_INFO 1

**Recommended final surface for Slot S3 (11 → 6 tools, −45%):**

| Tool | Role |
|------|------|
| `check_models_directory` | Model inventory (feeds spawn_local_worker) |
| `headroom_retrieve` | Headroom decompression |
| `spawn_local_worker` | Local inference primitive (dedupe the shadowed copy) |
| `sovereignty_ratio` | Sovereignty scorecard |
| `system_stats` | Unified stats — **must implement `_get_system_summary`/`_get_hardware_detail` first**; absorbs get_system_stats + get_hardware_stats + podman size |
| `local_queue` | Unified queue ops (absorbs cat/list/status) |

**Sequencing constraint (do not violate):** `get_system_stats` and `get_hardware_stats` must NOT be removed until `system_stats` is repaired and live-verified. Removing the working pair while the replacement NameErrors would leave the engine with zero stats tools — that is the kind of "theater" this audit exists to prevent.

**Blocking dependency:** the h2 install is P0 and precedes all of the above — the local worker pool, headroom, and unified stats are all dark until it lands.

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ SLOT-S3-ENGINEERING ⬡ TOOL-REVIEW-20260922*