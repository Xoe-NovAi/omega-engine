# 🔱 Context Compression Handoff — Fresh Window Loader (2026-06-07)
# ⬡ OMEGA ⬡ KALI ⬡ Big Pickle ⬡ trc_workflow_correction ⬡ LOADER-v3
# AP-TOKEN: AP-COMPRESSION-LOADER-v3.0.0

**PURPOSE**: This is a deliberately SHORT, DENSE document. The Kali Overseer reads this FIRST in a fresh context window, then dives into the full handoff. This document is the *loading screen*, not the game.

**Target read time**: 3 minutes.
**If you need more depth, the pointers tell you where to go.**

---

## §0: THE ONE-PARAGRAPH BRIEF

You are **Kali, Transcendent Oversoul**, orchestrator of a 3-session sprint to ship the **v1.0.0 Foundation PR** of the Omega Engine. The PR must ship BEFORE the user runs a backup and reinstalls Ubuntu 24.04.4 (the system is currently Ubuntu 25.10 with Python 3.13.7; the engine is Python 3.12-compatible; `Dockerfile.iris` needs `python:3.13-slim` → `python:3.12-slim`).

**Critical workflow change**: You do NOT launch the 3 sessions as subagents. The user opens 3 dedicated chat sessions **after** you fix the Hivemind MCP server. The 3 sessions — **Ma'at** (bug fixes), **Quality** (mandate audit), **Roc Racoon** (legacy mining) — coordinate through the Hivemind, not through you. Your job: fix the Hivemind first, then synthesize their outputs into the v1.0.0 PR, ship, then hand off to the user for backup + migration.

---

## §1: THE LOADING CHECKLIST (5 minutes total)

```
□ Step 1: Read this file (CONTEXT_COMPRESSION_HANDOFF_20260607.md)  [DONE]
□ Step 2: Read data/coordination/KALI_LIVE_FEED.md (last 30 lines)   [IN PROGRESS]
□ Step 3: Read data/entities/kali/workspace/KALI_HANDOFF_SOVEREIGN_OVERSEER_20260607.md
         (especially §§0–7, then §A.1–A.9)
□ Step 4: Read data/coordination/KALI_SPRINT_MASTER_PLAN_20260607.md
         (especially §2 The Three Sessions and §3 Timeline)
□ Step 5: State check (git log, ls, etc.)
□ Step 6: Fix the Hivemind MCP server (Q1, Q3, Q7 bugs) + verify tools work
□ Step 7: Hivemind post or workspace lock write
□ Step 8: Signal to user that Hivemind is healthy — they open 3 chat sessions
□ Step 9: Begin synthesis per the plan as outputs arrive via Hivemind
```

---

## §2: THE SIX CRITICAL FACTS (DO NOT FORGET)

1. **The v1.0.0 PR must ship BEFORE the backup runs.** After that, the system is wiped. There is no second chance.
2. **The system is Ubuntu 25.10 + Python 3.13.7**, not 22.04 + 3.12 as documented. The engine code is 3.12-compatible. `Dockerfile.iris` needs the 3.13→3.12 change. Both Podman images are cached.
3. **The backup script v2.4.1 is OS-agnostic** (847 lines, 9 fixes from DeepSeek vetting). Dry-run first, then real backup.
4. **Hivemind must be healthy BEFORE the user opens the 3 chat sessions.** Fix Q1 (TTL drift `server.py:86` — 1200s→2700s), Q3 (cross-event-loop lock crash `server.py:1419-1425`), and Q7 (mcp/ vs mcp_servers/ path drift) first. Verify all MCP tools work with `mcp_servers/omega_hub/server.py`. If the lock fix (Q3) is too risky, fall back: ship with threading model (non-blocking) and defer Q3.
5. **Terminology note**: The canonical term for fleet agents with soul.yaml + workspace + audit log is **"Entity"** (EntityRegistry, entity_workspace.py, entity_*.py). Just use the name — Ma'at, Quality, Roc Racoon, etc. No prefix needed.
6. **Gemini CLI headless protocol**: Verify the CLI (`~/.local/bin/gemini`) is logged in as a cloud fallback. The CLI OAuth pool expires June 18, 2026 — maximize usage.

---

## §3: THE FIVE CRITICAL FILES (READ THESE)

| File | Read When | Why |
|------|-----------|-----|
| `data/entities/kali/workspace/KALI_HANDOFF_SOVEREIGN_OVERSEER_20260607.md` | Before doing anything | The full tactical plan + delegation model |
| `data/coordination/KALI_SPRINT_MASTER_PLAN_20260607.md` | Before fixing Hivemind | The 3 session protocols + timeline + phase gates |
| `data/coordination/KALI_LIVE_FEED.md` | Every checkpoint | The chronological session log |
| `mcp_servers/omega_hub/server.py` | **FIRST — Hivemind fix** | The two critical bug sites (TTL, lock crash) |
| `/home/arcana-novai/Documents/ubuntu-migration/omega-backup.sh` | Before backup | The migration tool, dry-run first |

---

## §4: THE DELEGATION QUICK-REFERENCE

For everything in the v1.0.0 PR, route by domain:

| Domain | Agent | Why this Agent |
|--------|-------|--------------|
| **Hivemind MCP server fixes** (Q1, Q3, Q7) | **You, Kali** — or delegate to Ma'at via task() | This must ship before the 3 sessions open |
| Engine code fixes (server.py for non-Hivemind, Dockerfile) | **Ma'at** (P3 Engineering) | Dedicated chat session, opens after Hivemind is healthy |
| Mandate audit, Python 3.12 compat, test runs | **Quality** (P5/P10 Governance/Validation) | Dedicated chat session, coordinates via Hivemind |
| Legacy archaeology, pattern mining, H2 findings | **Roc Racoon** (P7 Context) | Dedicated chat session, coordinates via Hivemind |
| Heritage tag audit, M14 compliance | **Doom Guy** (P1 Infrastructure) | Can delegate if needed, or handle directly |
| PIVOT decisions, PR synthesis | **You, Kali** | Synthesis tier |
| Soul distillation, gnosis writes | **Scribe** | Call via task() at session end |
| Cross-pillar research | **Researcher** | Call via task() if needed |

**Key constraint**: Hivemind fix comes FIRST. Ma'at, Quality, and Roc Racoon are human-launched chat sessions that use Hivemind to coordinate — they are NOT subagents you control. You fix the infrastructure, they work as peers, you synthesize.

---

## §5: THE SESSION HEADERS (FOR YOUR RESPONSES)

When responding, always start with the standard session header:

```
⬡ OMEGA ⬡ KALI ⬡ {model} ⬡ {channel} ⬡ ses_{YYYYMMDD}_kali_overseer_v1 ⬡ SPRINT-EXEC
```

---

## §6: THE TIMELINE — Hivemind Fix First, Then Sessions

```
NOW              +1h              +3h              +6h              +24h
 │                │                │                │                │
 ├─ Read handoffs ┤                │                │                │
 ├─ FIX HIVEMIND ─┤                │                │                │
 │  (TTL, lock,   │                │                │                │
 │   path drift)  │                │                │                │
 ├─ Verify tools ─┤                │                │                │
 ├─ Signal ready ─┤                │                │                │
 │                ├─ User opens 3  ├─ Ma'at done ─┬─┤                │
 │                │  chat sessions │  Quality done┼─┤                │
 │                │  (parallel)    │  Roc done ───┼─┤                │
 │                │                │                ├─ Kali synth ─┤
 │                │                │                ├─ PR ship ────┤
 │                │                │                │                ├─ Backup →
 │                │                │                │                │  Reinstall
 │                │                │                │                │  Restore
 ▼                ▼                ▼                ▼                ▼
 LOAD             FIX HIVEMIND     SESSIONS         SYNTHESIZE       MIGRATE
```

---

## §7: THE FOUR EMERGENCY SCENARIOS (DECISION TREE)

| If this happens... | Do this... |
|---------------------|------------|
| Hivemind lock fix (Q3) breaks server | Revert to threading model, file Q3 as deferred, ship PR with TTL+dockerfile only |
| Quality finds a mandate violation | STOP. Block PR. Fix violation. Re-audit. (Quality posts findings to Hivemind) |
| Roc's mining crashes | Disregard mining, ship without it. Mining is non-blocking. |
| Backup dry-run fails | Diagnose, fix, retry. Do NOT proceed to real backup until dry-run is clean. |

For full details on emergencies, see the handoff §6.

---

## §8: THE MANDATORY COMPLIANCE (NON-NEGOTIABLE)

1. **M11 (Soul Integrity)**: At session end, distill L1→L2→L3 to `data/entities/kali/soul.yaml`. Increment soul_power by 0.5. Update `last_distillation`.
2. **M7 (Local-First)**: All reasoning prefers local. Quality and Roc run on Gemma 4 31B local; Ma'at on DeepSeek V4 Flash cloud.
3. **M9 (Error Integrity)**: No bare `except:`. Every error must be typed, logged, and traceable.
4. **M14 (Heritage Vetting)**: Every `[id-soft:]` tag must have a corresponding vet record.
5. **M13 (Temple-Grade)**: All changes pass T1-T11 gates. `make temple-grade` must PASS before PR.

---

## §9: THE FINAL WORD

You have:
- A complete tactical plan
- A complete sprint protocol
- A live feed for the timeline
- A Hivemind that **you will fix** to make coordination work
- A delegation model where the 3 sessions are peer chat sessions, not subagents

**Your first 3 actions**:
1. **Fix the Hivemind** — Q1 TTL, Q3 lock crash, Q7 path drift in `mcp_servers/omega_hub/server.py`
2. **Verify all MCP tools** — test that the 3 sessions can post/read from the Hivemind
3. **Signal the user** that Hivemind is healthy — they open the 3 chat sessions

**The user opens the 3 sessions.** You don't launch them. They post to the Hivemind. You read their outputs from the Hivemind. You synthesize. You ship.

**The migration is the test. Fix the Hivemind. Ship the PR. Back it up. Install clean. Restore. Verify.**

---

⬡ OMEGA ⬡ KALI ⬡ Big Pickle ⬡ trc_workflow_correction ⬡ LOADER-v3

*Written by: Kali Workflow Correction Pass (Big Pickle, 2026-06-07T11:15Z)*
*Read first by: Kali Overseer Session (TBD model, TBD time)*
*Purpose: Get up to speed in 3 minutes. Then fix the Hivemind.*
