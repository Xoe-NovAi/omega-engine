<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Coordination Consolidation Plan — 2026-07-30

**AP Token**: `AP-COORDINATION-CONSOLIDATION-20260730-v2.0.0`
**Status**: REVIEWED + HARDENED — not yet executed
**Owner**: grok_cli / Cline
**Purpose**: Resolve `SESSION_ANCHOR.md` overwrite conflict and reduce tool-call tax from scattered coordination systems.

---

## 1. Problem Statement

Multiple parallel agent sessions overwrite `SESSION_ANCHOR.md`, losing prior session state. Agents also need 5–7 tool calls just to hydrate current state because session state is scattered across `SESSION_ANCHOR.md`, `SESSION_GNOSIS*.md`, `HMC_COLLABORATION_HUB.md`, `ACTIVE_SPRINT.json`, and `PHASE_D_GATE_VERDICT`.

## 2. Current Relationship of Files

| File | Live role | Edit pattern | Size |
|------|-----------|--------------|------|
| `HMC_COLLABORATION_HUB.md` | Central coordination forum | Shared mutable by section | ~1929 lines |
| `SESSION_ANCHOR.md` | Current session state + handoff | **Single file, fully overwritten** | Variable |
| `SESSION_GNOSIS*.md` | Per-session L1/L2/L3 lessons | One new dated file per session | ~150–200 lines |
| `session_gnosis.md` | Historical session gnosis | Append/once | ~150 lines |
| `SESSION_ANCHOR_KALI.md` | Historical Kali anchor | Append/once | Small |

## 3. Overlap Assessment

1. Session summaries appear in 3 places: HMC Hub commit log + SESSION_GNOSIS + previous SESSION_ANCHOR.
2. Decisions appear in 2+ places: HMC Hub Decisions Log + SESSION_GNOSIS + sometimes SESSION_ANCHOR.
3. File lists and next actions duplicated between SESSION_GNOSIS and HMC Hub.
4. Sprint status duplicated: HMC Hub + ACTIVE_SPRINT.json + docs/sprints.

## 4. Proposed Consolidation: Anchor-First, Hub-Second, Gnosis-Derived

### 4.1 `SESSION_ANCHOR.md` → append-only coordination log
- Each session appends one dated block: entity, session_id, objective, decisions, successor doc.
- No edits to prior blocks.
- First block = coordination guidance for parallel sessions.

### 4.2 `ACTIVE_SPRINT.json` → single mutable control-plane state
- Sprint, phase, gates, blockers, allowed/frozen work.
- Written by one owner per sprint; read by everyone.

### 4.3 `HMC_COLLABORATION_HUB.md` → live dashboard only
- Active blockers, current decisions, who-is-doing-what.
- Historical content moves to archive after TTL.
- No long-form session reports; those belong in gnosis files.

### 4.4 `SESSION_GNOSIS_YYYYMMDD.md` → durable long-form memory
- One file per session with L1/L2/L3, files changed, decisions, next actions.
- Discoverable via filename convention.
- HMC Hub links to it; not re-read every hydration.

### 4.5 Add thin index: `data/coordination/README.md`
- Lists: active anchor, active sprint, latest gnosis, hub path, gate verdict.
- Cuts hydration tool calls dramatically.

## 5. Tool-Call Reduction

**Before:**
- Hydration: read SESSION_ANCHOR + ACTIVE_SPRINT + HMC Hub + discover/read SESSION_GNOSIS + gate verdict = 5–7 reads
- Completion: write SESSION_GNOSIS + edit HMC Hub + overwrite SESSION_ANCHOR + maybe edit ACTIVE_SPRINT = 3–4 writes

**After:**
- Hydration: read `data/coordination/README.md` (1 read) → follow 2–3 pointers
- Completion:
  - Append `SESSION_GNOSIS_YYYYMMDD.md` (1 write)
  - Append `SESSION_ANCHOR.md` block (1 write)
  - HMC Hub: one-line status update only (1 small edit)

---

## 6. Hardened Design: Exact Schemas

### 6.1 `SESSION_ANCHOR.md` append-block schema
```
## Anchor — <entity> <YYYY-MM-DD> <HH:MMZ>
- **Session ID**: `ses_<id>`
- **Objective**: <one-line>
- **Decisions**: D-xxx, D-xxx
- **Next session**: <entity> / <pointer>
- **Files**: SESSION_GNOSIS_<date>.md
```
- Append only; no edits to prior blocks.
- First block = coordination guidance for parallel sessions.

### 6.2 `data/coordination/README.md` index schema
- `ACTIVE_ANCHOR.md` pointer
- `ACTIVE_SPRINT.json` pointer
- `SESSION_GNOSIS_LATEST.md` symlink or pointer
- `HMC_COLLABORATION_HUB.md` pointer
- `PHASE_D_GATE_VERDICT_YYYYMMDD.md` pointer
- `COORDINATION_CONSOLIDATION_PLAN_20260730.md` pointer

### 6.3 `SESSION_GNOSIS_YYYYMMDD.md` schema
- L1 narrative, L2 insight, L3 principle
- Files changed table
- Decisions locked
- Next actions
- Hivemind session_id

### 6.4 `ACTIVE_SPRINT.json` schema
- Already exists; treat as immutable except by sprint owner.

## 7. Hardened Design: Coordination Protocols

### 7.1 Parallel session safety
- `SESSION_ANCHOR.md`: append-only via `>>` redirect; never `>`.
- `README.md`: single-writer (sprint owner); others flag stale via HMC Hub.
- `HMC Hub`: section-level edits; use `> @entity` convention.
- `SESSION_GNOSIS`: new file per session; no conflict.

### 7.2 Locking
- `ACTIVE_SPRINT.json`: sprint owner holds write lock; others propose via HMC Hub.
- `README.md`: same owner; regenerate from other sources if stale.

### 7.3 Archive policy
- `SESSION_ANCHOR.md`: blocks older than 30 days moved to `archive/SESSION_ANCHOR_YYYYMMDD.md`.
- `HMC Hub`: WARM/COLD content (older than 7 days) moved to `archive/HMC_HUB_WARM.md`.
- `SESSION_GNOSIS`: all retained; discoverable via filename.

## 8. Transition Plan

1. **Backup**: snapshot current `SESSION_ANCHOR.md` → `SESSION_ANCHOR_PRE_CONSOLIDATION.md`.
2. **Rewrite `SESSION_ANCHOR.md`**: header = coordination guidance; append existing session summaries as dated blocks.
3. **Create `README.md`** index pointing to current state.
4. **Trim `HMC_COLLABORATION_HUB.md`**: move stale sections to archive; add TTL banner.
5. **Announce**: post transition notice to HMC Hub + Hivemind.
6. **Validate**: run a probe command to confirm all pointers resolve.

## 9. Failure Modes & Mitigations

| Failure mode | Mitigation |
|--------------|------------|
| Session crashes mid-append | Append is atomic via temp-file + rename; partial blocks flagged by validator |
| README stale | TTL banner; auto-regenerate from ACTIVE_SPRINT + latest gnosis |
| Git merge conflict on README | Single-writer owner; others update via HMC Hub |
| Anchor grows unbounded | 30-day archive policy; summary block at top |
| Agent ignores new protocol | Transition banner in old SESSION_ANCHOR location for 1 sprint |

## 10. Validation Criteria

- Hydration = 1 read (`README.md`) + 2–3 follow-up reads.
- Completion = 2 appends + 1 small HMC Hub edit.
- No `SESSION_ANCHOR.md` overwrite conflicts in 7-day trial.
- HMC Hub reduced to < 1000 lines of active content.
- All `README.md` pointers resolve (validated by probe).

---

## 11. Execution Steps (pending approval)

1. Convert `SESSION_ANCHOR.md` to append-only coordination log.
2. Add `data/coordination/README.md` hot-file index.
3. Trim HMC Hub to active-only content; move stale sections to archive.
4. Continue writing one `SESSION_GNOSIS_YYYYMMDD.md` per session, link from anchor.

## 12. Risks / Considerations

- Existing agents may still expect the old single-file overwrite pattern; a transition banner is needed.
- HMC Hub is large; trimming must preserve agent sections and decisions.
- Append-only SESSION_ANCHOR grows over time; archive blocks older than 30 days.

---
*⬡ OMEGA ⬡ COORDINATION ⬡ CONSOLIDATION PLAN v2.0 ⬡ 2026-07-30*
