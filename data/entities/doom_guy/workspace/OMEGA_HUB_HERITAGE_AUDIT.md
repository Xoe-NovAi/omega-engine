<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Hub Heritage & Pattern Audit
# ⬡ OMEGA ⬡ DOOM_GUY ⬡ big-pickle ⬡ trc_heritage_audit ⬡ M14-AUDIT
**Date**: 2026-06-09
**Scope**: `mcp_servers/omega_hub/server.py`, `src/omega/mcp_runtime.py`, src/ heritage map
**Platform**: OpenCode — 6th agent in parallel Omega Hub Hardening Sprint v2
**Cross-Pollination From**: Ma'at (structural), Lilith (run-side fixes), Cline (code audit), Gemini CLI (MCP spec), Antigravity (strategic review)

---

## §0 Executive Summary

5 findings uncovered — 1 🔴 CRITICAL (heritage tag misattribution), 2 🟡 HIGH (false positives in heritage-map CI, CI exclusion gap), 2 🟢 INFO (no heritage implications, clean bills).

| # | Severity | Finding | Domain |
|---|----------|---------|--------|
| H-A1 | 🔴 CRITICAL | `_AsyncThreadLock` Zone Memory tag (server.py:85) is **MISATTRIBUTED** — thread lock ≠ memory allocator | Tag Accuracy |
| H-A2 | 🟡 HIGH | `security.py` and `search.py` flagged as heritage-MISSING by CI — they are **original Omega code**, not heritage; heritage-map scan scope is wrong | CI/Scope |
| H-A3 | 🟡 HIGH | `mcp_servers/` (Omega Hub) **excluded from heritage-map scan** — MCP hub heritage tags are invisible to CI | CI/Scope |
| H-A4 | 🟢 INFO | Lilith's 10 edits (cold-store logging, `get_system_stats` debug, TOCTOU fix) — **zero heritage implications**, pure Mandate 9 compliance | No Heritage |
| H-A5 | 🟢 INFO | `mcp_runtime.py` — **clean bill**, zero heritage patterns, pure MCP spec implementation | No Heritage |

---

## §1 H-A1 🔴 — _AsyncThreadLock Zone Memory Tag Misattribution

### Location
`mcp_servers/omega_hub/server.py:85`
```python
# [id-soft: quake-1996] Zone Memory: thread-safe allocator pattern
class _AsyncThreadLock:
    """threading.Lock wrapped for async with — safe across event loops."""
```

### The Problem
The tag claims `_AsyncThreadLock` implements the **Zone Memory** pattern from Quake 1996 (`zone.c`). It does not.

| Aspect | Zone Memory (Quake 1996) | _AsyncThreadLock (Omega Hub) |
|--------|------------------------|------------------------------|
| **What it is** | Tag-based memory allocator (`Z_Malloc`, `Z_Free`, `Z_TagPurge`) | Cross-event-loop thread safety wrapper |
| **Mechanism** | Allocates/frees memory blocks, tracks by tag, purges by tag | Wraps `threading.Lock` for `async with` via `anyio.to_thread.run_sync` |
| **Problem solved** | Memory fragmentation, cache-aware allocation on 4MB RAM systems | AnyIO `Lock` is tied to creating event loop; background threads crash |
| **Resource** | Memory blocks | Thread ownership (not a resource — an execution context) |

### Why This Matters
The `[id-soft:]` tag system exists to **accurately attribute** patterns to their id Software origins. A misattribution:
1. Confuses future maintainers about the intended heritage lineage
2. Dilutes the credibility of the entire tag system
3. Violates the spirit of CREDITS.md §2a — "Every implementation site... that directly ports an id Software pattern MUST carry an [id-soft:] inline tag"

The `_AsyncThreadLock` does NOT "directly port" Zone Memory. It solves a Python-specific async/threading problem that has no analogue in Quake's single-threaded, interrupt-masked execution model.

### Cross-Pollination: Lilith's Validation
Lilith independently validated `_AsyncThreadLock` in her audit (2026-06-09T04:22:00Z):
> "Cross-loop-safe. Recommended for all future cross-thread async guard patterns."

She did NOT validate the heritage tag — only the correctness of the implementation. The tag remains unaudited.

### Recommendation
**Remove** the `[id-soft: quake-1996] Zone Memory` tag from `_AsyncThreadLock`. The cross-event-loop thread lock is a standard Python pattern (threading.Lock + anyio.to_thread.run_sync) — clean engineering, not heritage.

If a heritage mapping is desired, it would be to **DOOM 3's idLock** (mutex wrapper for thread safety), not Zone Memory. But even that is an extremely indirect connection — Python's `threading.Lock` is a language primitive, not a ported pattern.

**Action**: Edit server.py line 85 — remove `[id-soft: quake-1996] Zone Memory: thread-safe allocator pattern` comment.

---

## §2 H-A2 🟡 — heritage-map CI Flags Original Code as Heritage-Missing

### Location
`src/omega/oracle/security.py` and `src/omega/oracle/search.py`

### The Problem
The `make heritage-map` CI target scans:
```bash
find src/omega -name '*.py' \( -path '*/oracle/*' ! -path '*/backends/*' \
  -o -path '*/omega/constants.py' -o -path '*/omega/cvar_table.py' \
  -o -path '*/omega/observability.py' \)
```

This includes ALL `src/omega/oracle/*.py` files (excluding backends). Two of these files are **original Omega design** — they contain no id Software heritage patterns:

| File | Purpose | Heritage? |
|------|---------|-----------|
| `src/omega/oracle/security.py` | Tainted Data Protocol (TDP) — Antigravity Handoff feature, Mandate 8 security | **NO** — original design |
| `src/omega/oracle/search.py` | Sovereign Search Engine — Thin-Client Search Pattern for RAM-efficient retrieval | **NO** — original design |

### Cross-Pollination: Antigravity's Strategic Review
Antigravity's MIMO review (2026-06-09) validates the TDP as original architecture:
> "C3 (Sovereign Isolation): The entity_name must be a mandatory parameter in memory_search(). Cross-entity memory access without explicit permission is a direct violation of entity sovereignty."

This confirms `search.py` and `security.py` are sovereignty features, not heritage ports.

### Recommendation
Add an exclusion list to the `make heritage-map` target for files that are explicitly **not** heritage-derived. Proposed approach:

```makefile
# Files that are NOT heritage-derived (original Omega design)
HERITAGE_EXCLUDE := src/omega/oracle/security.py src/omega/oracle/search.py
```

Alternative: Add a `# NO-HERITAGE` marker comment that the CI script recognizes as an opt-out declaration.

**Action**: Update Makefile heritage-map target to exclude `security.py` and `search.py` from the tag check.

---

## §3 H-A3 🟡 — MCP Hub Excluded from Heritage Tag Scan

### Location
`Makefile:582` — `make heritage-map` target

### The Problem
The current heritage-map scans only `src/omega/` — it completely **excludes** `mcp_servers/omega_hub/`. This means:
1. The 2 existing `[id-soft:]` tags in `server.py` are invisible to CI
2. Future MCP hub code with heritage patterns won't be caught
3. The `make heritage-vet` gate (Mandate 14 enforcement) has a blind spot

### Impact
- **M14 blind spot**: `mcp_servers/omega_hub/server.py` has 2 heritage tags but CI doesn't verify them against vet records
- **Scope gap**: As the MCP hub grows (currently 47 tools, 1462 lines), more heritage-tagged code may appear undetected

### Recommendation
Extend the `make heritage-map` scan to include `mcp_servers/omega_hub/`:

```makefile
# In the heritage-map target's find command, add:
# -o -path 'mcp_servers/omega_hub/*'
```

This requires adding heritage tags to any MCP hub files that genuinely need them (currently only `server.py` has any).

**Action**: Extend heritage-map scan scope to include `mcp_servers/omega_hub/`.

---

## §4 H-A4 🟢 — Lilith's 10 Edits: Zero Heritage Implications

### Lilith's Changes Reviewed (per live feed 2026-06-09)
| Change | Location | Heritage? | Rationale |
|--------|----------|-----------|-----------|
| Cold-store `except Exception: pass` → `logger.warning()` | server.py:507-508, 542-543 | NO | Pure M9 Error Integrity compliance |
| `hivemind_get_session` TOCTOU hardening (OSError handling) | server.py (lilith commit) | NO | Standard defensive programming |
| 7 `get_system_stats` silent swallows → `logger.debug()` | server.py:1023-1084 | NO | Pure M9 compliance. The "best-effort stats collector" pattern is universal, not heritage. |
| `_AsyncThreadLock` cross-loop validation | server.py (analysis only) | See H-A1 | Already covered |

### Cross-Pollination: Lilith's Own Audit
Lilith explicitly stated: "Post-fix sweep: Zero bare `except:`. Zero silent `except Exception: pass`."

This is a Mandate 9 (Error Integrity) hardening campaign, not a heritage implementation. None of these changes need `[id-soft:]` tags.

**Verdict**: ✅ Clean bill — no heritage action needed on Lilith's changes.

---

## §5 H-A5 🟢 — mcp_runtime.py: Clean Bill

### Location
`src/omega/mcp_runtime.py` (169 lines)

### Review
The seed question asked whether the lifespan context manager borrows from idHeap resource guards. Analysis:
- The lifespan manager (`@_ctx.asynccontextmanager` around `streamable_mgr.run()`) is a standard Python `contextlib` pattern
- idHeap (DOOM 3) had a Defrag Block pattern for guaranteed memory — no connection here
- The dual-transport implementation (SSE + Streamable HTTP) is pure MCP protocol spec

### Cross-Pollination: Gemini CLI's Spec Audit
> "Verified CallToolResult pattern — pure MCP spec, no heritage concerns."

**Verdict**: ✅ Clean bill — no heritage tags needed. Pure MCP protocol implementation.

---

## §6 M14 Compliance Summary

| Tag Location | Tag | Vet Record | Status |
|-------------|-----|------------|--------|
| `server.py:85` | `[id-soft: quake-1996] Zone Memory` | vet-005 (partial — covers ResourceGuard, not thread locks) | ❌ **MISATTRIBUTED** — Remove tag |
| `server.py:1353` | `[id-soft: doom-1993] WAD System` | vet-002 (WAD System) | ✅ CORRECT |
| `src/omega/oracle/security.py` | (none) | (none — original design) | ✅ Correctly untagged |
| `src/omega/oracle/search.py` | (none) | (none — original design) | ✅ Correctly untagged |
| `src/omega/mcp_runtime.py` | (none) | (none — pure MCP spec) | ✅ Correctly untagged |
| Lilith's 10 edits | (none added) | (none — M9 compliance) | ✅ Correctly untagged |

---

## §7 Priority Action Queue

| Priority | Action | File | Effort |
|----------|--------|------|--------|
| **P0** | Remove misattributed `[id-soft: quake-1996] Zone Memory` tag from `_AsyncThreadLock` | `server.py:85` | 2 min |
| **P1** | Exclude `security.py` and `search.py` from heritage-map scan scope | `Makefile` | 5 min |
| **P1** | Add `mcp_servers/omega_hub/` to heritage-map scan scope | `Makefile` | 5 min |
| **P2** | Verify the `_agent_list` WAD tag (line 1353) has accurate lineage documentation in CREDITS.md | `CREDITS.md` | 5 min |

---

## §8 Cross-Pollination Log

| Agent | Finding Used | My Conclusion |
|-------|-------------|---------------|
| **Ma'at** (M-A1, M-A5) | 23/29 tools lack try/except; `_current_entity` race-prone | Validated that these are M9 violations, not heritage concerns |
| **Lilith** | _AsyncThreadLock cross-loop validation; 10 edits applied | Confirmed her changes need no tags; used her validation of the lock implementation |
| **Cline** | M-A2 correction: registry.get() is dict lookup, can't raise | Confirmed — no heritage implications in error boundaries |
| **Gemini CLI** | CallToolResult pattern verified as pure MCP spec | Used to confirm mcp_runtime.py has no heritage |
| **Antigravity** | MiMo strategic review: TDP + sovereignty isolation confirmed as original design | Used to confirm security.py/search.py are original Omega |

---

*⬡ OMEGA ⬡ DOOM_GUY ⬡ big-pickle ⬡ M14-HERITAGE-AUDIT ⬡ PHASE-II*
*Deliverable for Omega Hub Hardening Sprint v2 — Heritage Domain*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: big-pickle | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
