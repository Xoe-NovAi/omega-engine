# 🔱 KALI DOCKET — OpenCode /compact Fragility Investigation
# ⬡ OMEGA ⬡ KALI ⬡ D-kal-060/061/062/063 ⬡ 2026-06-10
# Hardened by: DeepSeek V4 Flash parallel review

**Sessions**: ses_6d63dfacec1b (Kali) · ses_8abd1171681c (DeepSeek V4 Flash)
**Priority**: HIGH (P1)
**Status**: REVIEWED — Hardened strategy defined, posted to Hivemind for team discussion
**Hivemind**: ses_8abd1171681c — D-kal-061 (grace-period rollout), D-kal-062 (no manual edits), D-kal-063 (lessons union)

---

## §1 The Report

The user reported that during an OpenCode `/compact` operation, the previous
agent was **mid-diagnosis** — it had just run a `python3 -c "import yaml; ..."`
command to verify that `soul.yaml` parsed correctly after compaction. The
compression interrupted the agent mid-thought, context was lost, and the agent
would need to re-establish continuity post-compaction.

The trace:
```
Thought: 3.3s
The user wants me to:
1. "Fully diagnose the situation" regarding the YAML structural fragility
2. Post findings to the Hivemind
3. Create a new anchored summary from the conversation history

<tool_call: python3 -c "import yaml ... parse soul.yaml ...">
```

Then **/compact** ran. The Python diagnostic tool call was in-flight.

---

## §2 Root Cause Analysis

### 2A: Immediate Problem — Mid-Diagnosis Interruption

OpenCode's `/compact` compresses the conversation window, dropping older
messages. If an agent is mid-way through a multi-step diagnostic (e.g., has
launched a Python process to validate YAML but hasn't received the result yet),
the compaction destroys the agent's working context. Post-compaction, the agent
starts fresh — it doesn't know what it was doing, what it had already verified,
or what remains.

**Risk**: This can lead to:
- Duplicate work (re-running already-completed diagnostics)
- Silent data loss (the agent was mid-write when compacted)
- Agent confusion (losing the chain of reasoning)

### 2B: Systemic Problem — Soul.yaml Structural Sprawl

The **root cause** is NOT YAML syntax corruption. All 98 soul.yaml files parse
cleanly. The problem is **structural bloat** in Kali's soul.yaml:

| Metric | Value | Status |
|--------|-------|--------|
| File size | **113,636 bytes** | ⚠ Excessive |
| Line count | **1,755 lines** | ⚠ Excessive |
| Parse time | ~50ms (negligible) | ✅ OK |
| Round-trip loss | **0%** | ✅ No data loss |
| `evolution[]` entries | **0** (empty) | ❌ Broken |
| Sessions completed | **27** (per `sessions_completed`) | ✅ Tracked |
| Top-level writeback keys | **16** | ❌ Sprawl |
| `lessons_learned` (top) | **7** | ❌ Dual source |
| `soul_evolution.lessons_learned` | **9** | ❌ Dual source |

**The pattern**: Each session write-back creates a **new top-level key**:
- `soul_writeback_20260605`
- `soul_writeback_20260605T0525Z`
- `soul_writeback_20260605T0535Z`
- `soul_writeback_20260606`
- `soul_writeback_20260607_hivemind_fix`
- `soul_writeback_20260607_coordination_protocol`
- `soul_writeback_20260607_deep_research` (13,269 chars!)
- `soul_writeback_20260607_crystallized_strategy`
- `soul_writeback_20260608_strategy_finalization`
- `soul_writeback_20260609_knowledge_gap_synthesis`
- `soul_writeback_20260609_hivemind_release`
- `coordination_session_20260605`
- `coordination_session_20260606`
- `grand_overview_session_20260605`

**Why this is a problem**:
- The `soul_evolution.evolution` array is supposed to hold all session writebacks
- Instead, each session adds a new top-level key
- The file grows **laterally** (more top-level keys) instead of **vertically**
  (appending to `evolution[]`)
- Over time, this creates a sprawling YAML that's hard for ANY agent to navigate
- Post-compaction, an agent must re-read the entire 113KB file to understand
  what happened — wasting tokens and time

### 2C: Quasi-Problem — 82 Stub Soul Files

82 of 98 entity soul.yaml files have NO evolution or lessons data. These are
mostly orphan entities (`ent_0` through `ent_49`) plus untouched Pillar entities.
These are harmless but consume `ls` and glob overhead.

---

## §3 Hardened Strategy — DeepSeek V4 Flash Peer Review (D-kal-061/062/063)

Kali's original docket was reviewed by DeepSeek V4 Flash through parallel
analysis. **3 critical corrections** were identified:

### Correction 1: `soul_evolution.evolution[]` Does NOT Exist

Kali's plan assumed `evolution[]` was the "correct" existing structure. It
is not. `soul_evolution` has these keys: `sessions_completed`, `soul_power`,
`last_distillation`, `trajectory`, `lessons_learned`, `distillation_log`.
**No `evolution` key exists.**

This shifts the fix from "migrate into existing structure" to **create
structure, then backfill**. Fundamentally different risk profile.

### Correction 2: Session Log and Writeback Keys Have ZERO Overlap

```
session_log entries:  7 (milestone-focused project records)
writeback keys:      12 (individual agent session records)
intersection:        ZERO
```

They are **completely different datasets**. Kali's plan treated them as
overlapping. A migration that assumes one is a subset of the other will
produce inaccurate history.

### Correction 3: The Two lessons_learned Are Not Duplicates

```
soul_evolution.lessons_learned: 9 high-level topic summaries
top-level lessons_learned:      7 rich L1/L2/L3 structures with metadata
intersection:                   ZERO
```

Both sets are valuable and completely different. This is a **union**, not
a deduplication. Kali's plan said "16 → 9 (merged)" — wrong. Correct is
"16 entries, union of both sets."

---

## §4 Three-Phase Rollout Plan (D-kal-061)

### Phase 1: Create + Seed (Lossless — 1 Python script)

1. Create `soul_evolution.evolution[]` as a new array
2. Move the 3 `coordination_session_*` dicts into it (already structured YAML)
3. Add the 7 `session_log` entries as evolution records
4. **Do NOT delete originals yet** — dual-write for safety

**Result**: `evolution[]`: 0 → 10 entries. Top-level keys preserved as fallback.

### Phase 2: Backfill (Acceptably Lossy — 2 Python scripts)

**Script 2a**: Parse 6 writeback strings containing L3/lesson indicators
(`soul_writeback_20260607_*`, `20260608_*`, `20260609_*`).
Extract via regex: `r"L3:\s*(.+?)(?:\n\s*\n|\n\s*#|\n\s*Next:)"`
Append with `type: backfilled_session`, `extraction_quality: lossy|clean`.

**Script 2b**: Write remaining 6 narrative-only writebacks as
`type: narrative_session`, `has_lessons: false`.

### Phase 3: Unify + Lock (1 script + 1 code change + 1 doc change)

**Script 3**:
1. Merge both `lessons_learned` into `soul_evolution.lessons_learned` (16 entries)
2. Remove top-level `lessons_learned`
3. Update `sessions_completed` to true count
4. Validate all 12 writeback keys have matching `evolution[]` entry
5. **Only then** remove the 12 top-level `soul_writeback_*` keys

**Code change** (D-kal-062):
```python
# New method in SoulDistiller
def append_evolution_entry(self, entity_name, date, session_type, summary, lessons=None):
    """Append to soul_evolution.evolution[] — canonical path."""
```

**Doc change** (Mandate 11 protocol update):
- DO NOT create top-level `soul_writeback_*` keys
- DO use `SoulDistiller.append_evolution_entry()` or `omega soul-append`
- Schema: `{date, type, model, summary, lessons[], metrics}`

### CI Gate: `make soul-structure`

```python
import re, yaml
with open("data/entities/kali/soul.yaml") as f:
    data = yaml.safe_load(f)
wb_keys = [k for k in data if re.match(r"soul_writeback_|coordination_session_|grand_overview_", k)]
if wb_keys:
    print(f"FAIL: {len(wb_keys)} legacy top-level keys remain")
    exit(1)
if "evolution" not in data.get("soul_evolution", {}):
    print("FAIL: soul_evolution.evolution[] is missing")
    exit(1)
exit(0)
```

### Grace Period

~3 sessions of dual-write compatibility before old keys are deleted.
Agents may still write old format during grace period, with a deprecation
warning.

---

## §5 Expected Benefits (Revised)

| Benefit | Magnitude | Note |
|---------|-----------|------|
| Soul.yaml size reduction | ~80% (113KB → ~20KB) | After all 3 phases |
| Top-level keys reduction | 31 → ~15 | Essential keys only |
| `evolution[]` population | 0 → 27+ entries | Full history including session_log |
| Lessons merged | 16 entries (union of both sets) | NOT 9 — both sets are unique |
| Post-compaction recovery | Significantly faster | Smaller file, structured navigation |
| Agent confusion risk | Reduced | Clean structure stops lateral sprawl |
| Migration safety | 3 independent phases | Each reversible, each testable |

---

## §6 Hivemind State at Investigation Time

| Agent | Model | Task |
|-------|-------|------|
| roc_racoon | gemini-3.5-flash | Diagnosis update: 4 issues from S2-C re-evaluated for S2-D |
| lilith | deepseek-v4-flash | Strategic assessment of Gemma 4 31B work + response to Roc S2-D |
| cli_gemini | gemini-2.0-flash | Completed initial onboarding research, identified critical gaps |

**System**: Healthy. CPU idle (0.32 load). 7.95GB available RAM. 4 Podman
containers running. 33GB free on omega_library.

---

*Docket prepared by: Kali (Transcendent Oversoul) + DeepSeek V4 Flash (Hardened Review)*
*Mandate 11 compliance: Findings posted to Hivemind ses_6d63dfacec1b + ses_8abd1171681c*
*Decisions: D-kal-061 (grace-period rollout), D-kal-062 (no manual edits), D-kal-063 (lessons union)*
*Next: Team discusses hardened strategy → Execute Phase 1 migration script → Test → Phase 2 → Phase 3*
