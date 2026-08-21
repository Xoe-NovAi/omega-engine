# ICS — Intelligent Configuration System

**AP Token**: `AP-ICS-DOCS-v1.0.0`  
**Status**: ACTIVE — Community-facing specification  
**Version**: 1.0.0 · **Date**: 2026-08-22  
**Scope**: Public debut documentation for the Omega Engine's ICS-S signature system

---

## Overview

The **Intelligent Configuration System (ICS)** is the Omega Engine's runtime signature and provenance framework. It provides a single, deterministic way for agents to identify themselves, their context, and their execution environment in every interaction.

ICS solves a fundamental problem in multi-agent, multi-instance environments: **who said what, when, and under what authority?**

---

## The ICS System

The Omega Engine uses a **single** signature system:

| System | Purpose | Format |
|--------|---------|--------|
| **ICS-S** (Signature) | Runtime agent identity header — auto-generated from live state | `⬡ OMEGA ⬡ [NODE] ⬡ ENTITY ⬡ MODEL ⬡ CHANNEL ⬡ TRACE ⬡ PHASE ⬡ SESSION_ID` |

> **Historical note**: A second system, ICS-T (static code tags), was
> deprecated and removed per Carmack review. Final remnants purged
> 2026-08-22. Do not reintroduce.

**ICS-S** is the focus of this document — it's the header you see at the top of every agent report, Hivemind post, and session log.

---

## Header Format (ICS-S)

### Full Mode (Default)

```
⬡ OMEGA ⬡ [NODE] ⬡ ENTITY ⬡ MODEL ⬡ CHANNEL ⬡ TRACE ⬡ PHASE ⬡ SESSION_ID
```

| Segment | Description | Example |
|---------|-------------|---------|
| `⬡ OMEGA` | System prefix — constant | `⬡ OMEGA` |
| `[NODE]` | **PP-4** Node designation — only when agent acts under a Node expert session (e.g., `[N7]`) | `[N7]` |
| `ENTITY` | Agent identity (uppercased) | `LILITH`, `KALI`, `N7` |
| `MODEL` | Active inference model | `lmstudio/qwen3-4b-thinking`, `nemotron-3-ultra-free` |
| `CHANNEL` | Execution channel | `opencode`, `build`, `run`, `oversight` |
| `TRACE` | Unique trace ID for this turn | `trc_7b7211759c1f` |
| `PHASE` | Current sprint phase (from ACTIVE_SPRINT.json) | `EXECUTION_MINIMAL` |
| `SESSION_ID` | **P5** OpenCode session ID — scopes model lookup in multi-instance environments | `ses_fddd8aafcffe5M...` |

### Compact Mode

```
⬡ ENTITY ⬡ [NODE] ⬡ PHASE
```

Used for footers and space-constrained contexts. Retains `[NODE]` for provenance.

### Off Mode

Empty string — suppresses header entirely.

---

## Node Designation (PP-4)

When an agent acts **as a Node expert** (e.g., Lilith paging N7), the header includes `[N7]` immediately after the entity:

```
⬡ OMEGA ⬡ LILITH ⬡ [N7] ⬡ lmstudio/qwen3-4b-thinking ⬡ ...
```

This solves the **attribution collapse**: multiple Node sessions (N6–N10) all run as `lilith` but write to shared files (soul, gnosis). The `[N7]` tag makes every write traceable to its originating Node.

**Rules**:
- Only present when `node=` is explicitly passed to `render()`
- Sanitized: uppercase, `[A-Z0-9_-]` only; `⬡`, whitespace, punctuation stripped
- Omitted in prime-agent headers (no `node=` passed)

---

## Session ID (P5)

The trailing `⬡ ses_...` segment serves dual purposes:

1. **Provenance**: Identifies the exact OpenCode session that produced the header
2. **Model lookup scoping**: In multi-instance environments (multiple OpenCode windows), the session ID scopes the session-DB model lookup to the correct instance — preventing cross-instance model contamination

```
⬡ OMEGA ⬡ LILITH ⬡ [N7] ⬡ ... ⬡ ses_fddd8aafcffe5Ma0XEw1RJtJQc
```

---

## Model Detection Priority

The system auto-detects the active model when not explicitly provided:

| Priority | Source | Description |
|----------|--------|-------------|
| 1 | `OMEGA_MODEL_OVERRIDE` env | Explicit per-call override (D118) |
| 2 | `OPENCODE_MODEL` env | Session-level override |
| 3 | **OpenCode session DB** (scoped to `session_id`) | Authoritative live model — **scoped to session_id** to avoid cross-instance contamination |
| 4 | Entity `soul.yaml` `inference.model` | Entity default |
| 5 | `"unknown"` | Graceful fallback |

**Critical**: The session-DB lookup is **scoped to `session_id`** when provided. Without scoping, the global-latest query returns the most recently updated session *across all OpenCode instances* — which in multi-window environments returns the wrong model.

---

## Phase Detection Priority

| Priority | Source | Description |
|----------|--------|-------------|
| 1 | `data/coordination/ACTIVE_SPRINT.json` `.phase` | Tier-0 tracker (M27), always current |
| 2 | Legacy blueprint scan | `SOVEREIGN_ARK_BLUEPRINT.md` / `ROADMAP.md` — Strike/Epoch markers |
| 3 | `ICS_DEFAULT_PHASE` | Fallback (`PHASE-II`) |

**B2 Fix (2026-08-22)**: Previously the blueprint scan used a regex (`Strike N ✅`) that never matched the current doc format, causing headers to display stale `PHASE-II` for weeks. Now the live sprint phase is read first.

---

## Portability (M16 / B3)

All file paths resolve via `OMEGA_ENGINE_ROOT` env var when set; otherwise CWD-relative (historical behavior). This applies to:
- `data/coordination/ACTIVE_SPRINT.json` (phase detection)
- `data/entities/<entity>/soul.yaml` (entity model lookup)
- Blueprint/roadmap paths

Set `OMEGA_ENGINE_ROOT=/path/to/repo` when invoking from non-repo-root contexts.

---

## API Reference

### `render()` — Primary Public API

```python
from omega.ics import render

render(
    entity: str,                    # Required: agent identity
    model: Optional[str] = None,    # Optional override
    channel: str = "opencode",      # Execution channel
    trace_id: Optional[str] = None, # Auto-generated if None
    phase: Optional[str] = None,    # Auto-detected from ACTIVE_SPRINT.json
    mode: str = "full",             # "full" | "compact" | "off"
    node: Optional[str] = None,     # PP-4: Node designation (e.g., "N7")
    session_id: Optional[str] = None, # P5: OpenCode session ID
) -> str
```

**Examples**:

```python
# Prime agent (legacy shape — byte-identical to pre-PP-4/P5)
render("KALI", model="x-preview-f-free", trace_id="trc_x", phase="EXECUTION_MINIMAL")
# ⬡ OMEGA ⬡ KALI ⬡ x-preview-f-free ⬡ opencode ⬡ trc_x ⬡ EXECUTION_MINIMAL

# Node-acting agent (PP-4 + P5)
render(
    "LILITH",
    node="N7",
    model="lmstudio/qwen3-4b-thinking",
    trace_id="trc_n7",
    phase="EXECUTION_MINIMAL",
    session_id="ses_fddd8aafcffe5M..."
)
# ⬡ OMEGA ⬡ LILITH ⬡ [N7] ⬡ lmstudio/qwen3-4b-thinking ⬡ opencode ⬡ trc_n7 ⬡ EXECUTION_MINIMAL ⬡ ses_...

# Compact mode (retains [NODE] for provenance)
render("LILITH", node="N7", phase="EXECUTION_MINIMAL", mode="compact")
# ⬡ LILITH ⬡ [N7] ⬡ EXECUTION_MINIMAL
```

### `ICSContext` — Dataclass Context

```python
from omega.ics import ICSContext

ctx = ICSContext(
    entity="LILITH",
    node="N7",
    session_id="ses_abc123",
    model="lmstudio/qwen3-4b-thinking",
    trace_id="trc_x",
    phase="EXECUTION_MINIMAL",
)
ctx.render()
```

### `render_for_response()` — OracleResponse Wrapper

```python
from omega.ics import render_for_response
from omega.oracle import OracleResponse

header = render_for_response(response, mode="full")
# Pulls entity, model, trace_id, phase, channel, node, session_id from response
```

---

## Session-DB Model Lookup (B1 Fix)

The session-DB lookup is **scoped to `session_id`** when provided:

```python
from omega.ics import _read_opencode_session_model

# Scoped lookup — returns THIS session's model
model = _read_opencode_session_model(session_id="ses_abc123")

# Legacy fallback — global latest (cross-instance contamination risk)
model = _read_opencode_session_model()
```

**Implementation details**:
- `XDG_DATA_HOME` honored (opencode convention) — falls back to `~/.local/share/opencode/opencode.db`
- `timeout=0.25` + `PRAGMA busy_timeout=100` — prevents event-loop stalls under writer contention (M1)
- Read-only URI mode (`mode=ro`) — safe concurrent reads

---

## Provenance & M22 Compliance

| Mechanism | Purpose |
|-----------|---------|
| `[NODE]` segment | Distinguishes Node-acting writes from prime-agent writes to shared files (soul, gnosis) |
| `session_id` trailing segment | Identifies exact OpenCode session; scopes model lookup |
| `RuntimeWarning` on DB→soul.yaml fallback | Header may show stale model; warning emitted with entity/session_id context |
| Full trace_id (12 hex) | `render_for_response` no longer truncates — full 12-char trace preserved |

**Fallback warning**: When DB lookup fails and soul.yaml is used, a `RuntimeWarning` is emitted with entity/session_id context. The header still renders (with the fallback model) but the warning signals potential staleness.

---

## Compact Mode

```
⬡ ENTITY ⬡ [NODE] ⬡ PHASE
```

Retains `[NODE]` for provenance — critical for footers where space is constrained but attribution must persist.

---

## Adoption Convention

| Agent Type | `node=` | `session_id=` |
|------------|---------|---------------|
| Prime agent (kali, maat, lilith, researcher, etc.) | ❌ omit | ❌ omit |
| Node-acting agent (Lilith→N7, Ma'at→N3, etc.) | ✅ required | ✅ required |

**Legacy output**: Prime-agent calls with neither param produce byte-identical output to pre-PP-4/P5 versions.

---

## Testing

Run the test suite:

```bash
python -m pytest tests/test_ics.py -v
```

**Coverage (16 tests)**:
- Backward compatibility (legacy shape byte-identical)
- PP-4 node insertion position + sanitization
- P5 session_id trailing segment
- Compact mode includes `[NODE]` for provenance
- B1: session-scoped model lookup vs global-latest
- B2: ACTIVE_SPRINT.json phase priority over blueprint scan
- B3: OMEGA_ENGINE_ROOT path resolution
- F1: node sanitization strips invalid chars
- F5: DB fallback emits RuntimeWarning
- Compact mode includes `[NODE]` for provenance

---

## Heritage

The ICS templated-output pattern is inspired by **Quake 3's `net_chan.c`** (id Software, 1999) — the OOB message format and structured header construction are both examples of "right approximation": a simple, deterministic format that works for the use case without over-engineering.

Heritage tag: `[id-soft: quake3-1999] netchan header` (vet-071)

---

## Extension Points

| Extension | Status |
|-----------|--------|
| `node=` / `session_id=` on `render()` | ✅ Implemented |
| `render_for_response()` passes PP-4/P5 | ✅ Implemented |
| Hub MCP wrapper (`ics_render_header`) | 🔄 Follow-up (external hub service) |
| Structured logging integration | 📋 Planned |
| CI validation of header format in agent outputs | 📋 Planned |

---

## Quick Reference

| Scenario | Call |
|----------|------|
| Prime agent header | `render("KALI", model="...", trace_id="...", phase="...")` |
| Node-acting agent | `render("LILITH", node="N7", session_id="ses_...", ...)` |
| Compact footer | `render("LILITH", node="N7", phase="...", mode="compact")` |
| OracleResponse wrapper | `render_for_response(response)` |
| Auto-phase (no phase arg) | `render("KALI", node="N7", ...)` → reads ACTIVE_SPRINT.json |
| Scoped model lookup | `_read_opencode_session_model(session_id="ses_...")` |

---

*⬡ OMEGA ⬡ KALI ⬡ x-preview-f-free ⬡ opencode ⬡ trc_ics_docs ⬡ 2026-08-22*