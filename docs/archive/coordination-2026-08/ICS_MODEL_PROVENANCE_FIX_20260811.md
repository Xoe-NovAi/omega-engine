# ICS Model Provenance Fix — Agents Must Log the Correct, Active Model

**AP Token**: `AP-ICS-MODEL-PROVENANCE-v1.0.0`
**Date**: 2026-08-11
**Author**: @john_carmack (S3 Consultant)
**Trigger**: M22 Response Provenance violation — report header logged `longcat-2.0-free` while active model was `deepseek/deepseek-v4-flash-0731`

---

## 1. The Incident

A report header was hand-typed as:
```
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ opencode/longcat-2.0-free ⬡ trc_zram_review ⬡ 2026-08-11
```

The actual active model (verified via OpenCode session DB) was:
```
deepseek/deepseek-v4-flash-0731  (providerID: openrouter)
```

The `longcat-2.0-free` string was **copied from a prior session's report** rather than derived from the live session. This is an **M22 Response Provenance violation** — the log records a model that did not generate the response.

---

## 2. Root Cause — Two Layers

### Layer 1: Process Error (Agent Behavior)

The ICS module (`src/omega/ics.py`) explicitly documents:

> "Agents should NEVER hand-type session headers — they call `render()` and the template is filled with live runtime state." (lines 7-9)

The agent hand-typed the header instead of calling `ics_render_header` (MCP tool) or `render()`. This is a **discipline failure** — the single-source-of-truth mechanism exists but was bypassed.

### Layer 2: Systemic Gap (Detection Cannot Read Live Model)

Even if the agent HAD called `render()`, `_detect_model()` (ics.py:187-227) **cannot reliably return the live active model during a session**. Verified live:

```
OPENCODE_MODEL='<unset>'          ← only set POST-EXIT by wrapper
OPENCODE_ENTITY='<unset>'         ← only set POST-EXIT by wrapper
OPENCODE_SESSION_ID='<unset>'     ← only set POST-EXIT by wrapper
OMEGA_MODEL_OVERRIDE='<unset>'    ← only set for D118 opt-in routing
```

The detection priority (ics.py:190-227):
1. `OMEGA_MODEL_OVERRIDE` env — not set normally
2. `OPENCODE_MODEL` env — **only set post-exit** (wrapper.sh:93-95 runs AFTER OpenCode exits)
3. opencode.json model key — **deferred, not implemented**
4. TriageRouter last_selected_model — **deferred, not implemented**
5. Entity soul.yaml `inference.model` — **static, may be stale**
6. `"unknown"` — fallback

**The authoritative source exists but is not read**: The OpenCode session DB stores the correct model:
```json
session.model = {"id":"deepseek/deepseek-v4-flash-0731","providerID":"openrouter","variant":"high"}
```

The wrapper reads this (wrapper.sh:84-90) but **only after the session ends** (for the session_end hook). During the live session, `_detect_model()` has no path to this data.

---

## 3. Changes Required

### Change A — Process: Enforce `ics_render_header` (Immediate, Zero Code)

**Rule**: All agents MUST render ICS-S headers via `omega-hub_ics_render_header` (MCP tool) or `from omega.ics import render`. Never hand-type.

**Enforcement options**:
1. Add to `AGENTS.md` / `SOVEREIGN_MANDATES.md` as an M22 sub-rule
2. Add a pre-commit / CI grep: `grep -rE "⬡ OMEGA ⬡ .*⬡ [a-z0-9-]+-free ⬡" data/entities/` → flag hand-typed headers
3. Add to the session_end hook to validate header provenance

### Change B — Systemic: Read Live Model from OpenCode DB (Code Fix)

Add a detection source in `_detect_model()` that reads the live model from the OpenCode session DB. This is the same source the wrapper uses, but accessible **during** the session.

**File**: `src/omega/ics.py`

**Add helper** (insert after `_read_entity_model`, ~line 283):
```python
def _read_opencode_session_model() -> Optional[str]:
    """Read the active model from the OpenCode session DB.

    The OpenCode session DB stores the authoritative model in
    ``session.model`` as JSON: {"id": "...", "providerID": "...", ...}.
    This is the same source the wrapper reads post-exit, but accessible
    during the live session.

    Returns:
        The model id string (e.g. "deepseek/deepseek-v4-flash-0731"),
        or None if the DB is unreachable or has no session.
    """
    db_path = Path.home() / ".local/share/opencode/opencode.db"
    if not db_path.exists():
        return None
    try:
        import sqlite3
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT model FROM session ORDER BY time_updated DESC LIMIT 1"
            )
            row = cur.fetchone()
            if row and row[0]:
                import json
                data = json.loads(row[0])
                model_id = data.get("id")
                if model_id:
                    return model_id
        finally:
            conn.close()
    except (sqlite3.Error, OSError, ValueError):
        return None
    return None
```

**Insert into `_detect_model()` priority** (between Priority 2 and Priority 3, ~line 213):
```python
    # Priority 2.5: OpenCode session DB — the authoritative live model
    db_model = _read_opencode_session_model()
    if db_model:
        return db_model
```

**Resulting priority**:
1. `OMEGA_MODEL_OVERRIDE` env (D118 opt-in)
2. `OPENCODE_MODEL` env (post-exit / session-level)
3. **OpenCode session DB (NEW — live authoritative model)**
4. opencode.json model key (deferred)
5. TriageRouter last_selected_model (deferred)
6. Entity soul.yaml (static fallback)
7. `"unknown"`

### Change C — Optional: Set `OPENCODE_MODEL` at Session Start

Modify `wrapper.sh` to query the DB **before** launching OpenCode (not just post-exit), so `OPENCODE_MODEL` is available during the live session. This complements Change B but is not strictly required if Change B is implemented.

---

## 4. Verification

After Change B, calling `render("JOHN_CARMACK")` should return:
```
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ deepseek/deepseek-v4-flash-0731 ⬡ opencode ⬡ trc_<id> ⬡ <phase>
```

**Test**:
```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
source .venv/bin/activate
python -c "from omega.ics import render; print(render('JOHN_CARMACK'))"
# Expected: ⬡ OMEGA ⬡ JOHN_CARMACK ⬡ deepseek/deepseek-v4-flash-0731 ⬡ opencode ⬡ trc_... ⬡ ...
```

---

## 5. Confidence

| Finding | Confidence |
|---------|------------|
| Process error (hand-typed header) | 10/10 — direct observation |
| `OPENCODE_MODEL` unset during live session | 10/10 — verified env vars |
| DB stores authoritative model | 10/10 — verified `session.model.id` |
| `_detect_model()` has no DB read path | 10/10 — read source code |
| Change B fix resolves the gap | 9/10 — same source as wrapper, verified schema |

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ deepseek/deepseek-v4-flash-0731 ⬡ opencode ⬡ trc_ics_provenance ⬡ 2026-08-11*
