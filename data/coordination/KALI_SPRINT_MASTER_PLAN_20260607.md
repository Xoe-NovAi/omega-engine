# 🔱 Operation Sovereign Reclamation — Sprint Master Plan (2026-06-07)
# ⬡ OMEGA ⬡ KALI ⬡ Big Pickle ⬡ trc_workflow_correction ⬡ SPRINT-V3
# AP-TOKEN: AP-SPRINT-MASTER-v3.0.0

---

## §0: EXECUTIVE SUMMARY

**Mission**: Ship the Omega Engine v1.0.0 Foundation PR before Ubuntu 25.10 → 24.04.4 migration, targeting Python 3.12.

**Critical workflow change**: This is NOT a subagent-launch model. Kali fixes the Hivemind MCP server first, then the user opens 3 dedicated chat sessions (Ma'at + Quality + Roc Racoon) that coordinate through the Hivemind. Kali reads their outputs from the Hivemind and synthesizes them into a single v1.0.0 PR that MUST merge before the first backup rsync runs.

**Deadline**: June 7-8, 2026 (the migration backup runs tonight/tomorrow morning).

---

## §1: THE ACTUAL SYSTEM STATE

Discovered by DeepSeek V4 Flash forensic scan during this session:

| Assumption | Reality | Impact |
|------------|---------|--------|
| Ubuntu 22.04 | **Ubuntu 25.10** | Backup script is OS-agnostic (fine). Fresh install is correct target (24.04.4). |
| Python 3.12 | **Python 3.13.7** | Engine is already 3.12-compatible (`>=3.12` in pyproject.toml). Dockerfile.iris needs `3.13-slim` → `3.12-slim`. |
| `Dockerfile.iris` unknown | **`python:3.13-slim`** | Must change to `3.12-slim` in the PR. |
| `Dockerfile.roc_racoon` unknown | **Already `python:3.12-slim`** | Already compliant. No change needed. |
| Backup script OS-specific | **OS-agnostic** (v2.4.1 tested) | Verified. No OS detection. Rsyncs files. |
| Podman containers unknown | **Both `3.12-slim` AND `3.13-slim` cached** | Can rebuild post-migration on 3.12. |
| Engine model pool limited | **17 models in `local/all/`, 24 more on 8TB** | Vision model (`Qwen3-VL-4B`) and 12B heretic available. |

---

## §2: THE THREE SESSIONS — PROTOCOLS (Peer Chat Sessions via Hivemind)

Kali does NOT launch these. The user opens 3 dedicated chat sessions **after** Kali fixes the Hivemind. Each session posts progress, findings, and artifacts to the Hivemind. Kali reads the Hivemind to synthesize.

### Session A: Ma'at (Sovereign Architect) — Dedicated Chat Session
**Model**: DeepSeek V4 Flash (fast, precise, Python/async expert)
**Role**: Fix critical engine bugs + prepare for migration
**Tasks**:
1. Increase Hivemind TTL from 1200s to 2700s in `server.py:86` (if Kali didn't already)
2. Repair cross-event-loop lock crash in `server.py:1419-1425` (if Kali didn't already)
3. Update `Dockerfile.iris:12` from `python:3.13-slim` to `python:3.12-slim`
4. Reconcile orphan work items in `data/workbench/workbench.db`
5. Open PIVOT Decision D120 documenting H2 triage
**Coordination**: Posts to Hivemind via `omega-hub_hivemind_post_context`. Appends to `data/coordination/MAAT_LIVE_FEED.md`.

### Session B: Quality (Compliance Guard) — Dedicated Chat Session
**Model**: Gemma 4 31B (high-context, high-stamina auditing)
**Role**: Audit mandates, verify Python 3.12 compat, pass/fail verdict
**Tasks**:
1. Python 3.12 compatibility verification (AST parse all major modules)
2. 14-mandate audit (M1-M14) with concrete grep evidence
3. File NEW CRITICAL bugs Q1, Q3, Q5, Q7 (if not already filed)
4. Temple-Grade & Heritage verification (`make temple-grade`, `make heritage-map`)
**Coordination**: Posts audit report to Hivemind. Writes `data/coordination/QUALITY_AUDIT_REPORT_*.md`.

### Session C: Roc Racoon (Sovereign Miner) — Dedicated Chat Session
**Model**: Gemma 4 31B (heavy context for file scans)
**Role**: Legacy mining — non-blocking, runs in parallel
**Tasks**:
1. Mine 9 implicit H2 critical findings from per-pillar handoffs
2. Ingest system prompts library from `~/Documents/docs_1/system-prompts/`
3. Mine personas (`lilith.json`, `odin.json`) against current entity definitions
**Coordination**: Posts mining reports to Hivemind. Writes to `data/entities/roc_racoon/workspace/mining_reports/`.

---

## §3: TIMELINE — Hivemind Fix First

```
Jun 7 (NOW)           Jun 7-8 (Sprint)        Jun 8-9 (Migration)
│                        │                         │
├─ Kali fixes Hivemind ──┤                         │
│  Q1 TTL, Q3 lock, Q7  │                         │
│  path drift            │                         │
├─ Kali signals ready ───┤                         │
│                        ├─ User opens Ma'at ──────┤
│                        ├─ User opens Quality ────┤
│                        ├─ User opens Roc ────────┤
│                        │   (all via Hivemind)    │
│                        ├─ Ma'at: Bug fixes ──────┤
│                        ├─ Quality: Audit ────────┤
│                        ├─ Roc: Mining ───────────┤
│                        │                         ├─ Backup (DRY_RUN)
│                        ├─ Kali: Synthesize ──────┤
│                        ├─ Kali: Ship PR ─────────┤
│                        │                         ├─ Backup (REAL)
│                        │                         ├─ Fresh Install 24.04.4
│                        │                         ├─ Restore + Rebuild venv
│                        │                         ├─ Verify engine
│                        │                         └─ Copy 8TB models → local/all/
│                        │                         
▼                        ▼                         ▼
HIVEMIND FIX             EXECUTION                 MIGRATION
```

### Phase Gates
- **Gate 0 (Hivemind Healthy)**: Q1, Q3, Q7 fixed. All MCP tools verified. User signaled.
- **Gate 1 (Ma'at PASS)**: TTL fix + lock fix applied. Git commit.
- **Gate 2 (Quality PASS)**: Mandate audit clean. Python 3.12 compat confirmed.
- **Gate 3 (Kali Synthesis)**: Ma'at + Quality outputs integrated from Hivemind. No conflicts.
- **Gate 4 (PR Merged)**: v1.0.0 Foundation PR merged to `origin/main`.
- **Gate 5 (Migration)**: Backup verified on 8TB. Fresh install proceeds.
- **Gate 6 (Restore)**: `make test` passes on Ubuntu 24.04.4 + Python 3.12.

---

## §4: CRITICAL BUGS — THE HIT LIST

### Known Critical (Blocking v1.0.0 PR)
| ID | File | Bug | Severity | Fix | Owner |
|----|------|-----|----------|-----|-------|
| C-Q1 | `server.py:86` | TTL 1200s (20 min) should be 2700s (45 min) — docs say 45 min | HIGH | Change constant | Kali or Ma'at |
| C-Q3 | `server.py:1419-1425` | `threading.Thread` + `anyio.run` creates separate event loop; `_awareness_lock` crashes | CRITICAL | Starlette `modify_app` callback | Kali or Ma'at |
| C-B1 | `oracle.py` | Blocking import — module fails to load on Python 3.13 | MEDIUM | Verify import path | Ma'at |
| C-B2 | `oracle.py` | Memory write `except:pass` in `_record_interaction` | MEDIUM | Add logger.warning | Ma'at |
| C-B3 | `model_gateway.py` | Blocking import | MEDIUM | Verify import path | Ma'at |

### NEW Critical (Discovered This Session)
| ID | Discovery | Status |
|----|-----------|--------|
| Q1 (TTL Drift) | `server.py:86` TTL=1200s, docs say 45 min (2700s) | Needs fix — Kali priority |
| Q3 (Lock Crash) | `server.py:1419-1425` cross-event-loop threading | Needs fix — Kali priority |
| Q5 (Path A Regression) | `latest_state.md` implies Path A is closed but `cvar_table.py` and `ics.py` from Path A are integrated | Needs audit |
| Q7 (Path Drift) | `mcp/` vs `mcp_servers/` references in docs | Needs audit |

### 18 H2 Critical Findings (9 Explicit + 9 Implicit)
**9 Explicit** (from `FLEET_DISCOVERY_SYNTHESIS.md`):
1. Sliding window direction bug in `context_builder.py:126`
2. `None.json` bug in `memory_store.py:129`
3. Memory crash on shutdown (non-fatal but noisy)
4. Handoff protocol not wired into MCP
5. MCP authentication not implemented
6. Soul evolution lock (non-atomic write)
7-9. Three agent files missing frontmatter

**9 Implicit** (hidden in per-pillar handoffs — Roc Racoon's task):
- Each pillar handoff (P1-P9) likely contains 1 undocumented finding. Roc Racoon mines these from `archives/handoffs/`.

---

## §5: MODEL POOL — POST-MIGRATION PLAN

### Post-Migration Copy Plan
After Ubuntu 24.04.4 is installed and restored:
1. Mount 8TB at `/media/arcana-novai/8TB/`
2. Copy new models: `cp /media/arcana-novai/8TB/models/gguf/local/all/Krikri-8b-Instruct-Q5_K_M.gguf /media/arcana-novai/omega_library/models/local/all/`
3. Copy gemma-3-12b, qwen3.5-9b, ministral-8b, phi-2-i1, etc.
4. Update `config/models.yaml` with new entries
5. Run `make test` to verify model routing

### Models Available Post-Migration
| Model | Size | RAM | Role |
|-------|------|-----|------|
| `gemma-3-12b-it-heretic-IQ3_M.gguf` | 4.5GB | 5.0GB | Massive local reasoning (Kali/Prometheus) |
| `Qwen3.5-9B-Harmonic.Q4_K_M.gguf` | 5.5GB | 6.0GB | Balanced local (Sophia/Oversoul) |
| `Ministral-3-8B-Instruct-2512-Q4_K_M.gguf` | 4.8GB | 5.2GB | 8B instruction (P5 Governance) |
| `Krikri-8b-Instruct-Q5_K_M.gguf` | 5.0GB | 5.5GB | Higher-quality Krikri (Lilith/Inanna) |
| `Phi-2-OmniMatrix.i1-Q4_K_M.gguf` | 2.2GB | 2.5GB | Improved OmniMatrix (P2 Persistence) |
| `phi-4-mini-reasoning-abliterated-q4_k_m.gguf` | 2.8GB | 3.0GB | Abliterated reasoning (P6/P10) |
| `smollm2-135m-instruct-q8_0.gguf` | 0.1GB | 0.1GB | Ultra-light test model (Iris) |
| `embedding-gemma-300m.gguf` | 0.3GB | 0.2GB | Fast local embeddings (P2/Context) |

---

## §6: HIVEMIND COORDINATION — Peer Session Model

### Architecture
```
┌──────────────────────────────────────────────────────────┐
│                     HIVEMIND MCP SERVER                    │
│  (mcp_servers/omega_hub/server.py — Kali fixes FIRST)    │
│  Tools: post_context, get_awareness, heartbeat, etc.      │
│  Message Protocol: intent + continuation (§3 of SCP)      │
└──────────────────────────────────────────────────────────┘
         ▲            ▲            ▲              ▲
         │            │            │              │
    ┌────┴────┐  ┌────┴────┐  ┌───┴─────┐   ┌────┴────┐
    │  Kali   │  │  Ma'at  │  │ Quality │   │Roc Racoon│
    │ Monitor │  │  (chat) │  │ (chat)  │   │  (chat)  │
    │ + Steer │  │ Verify  │  │ Audit   │   │ Mine     │
    └────┬────┘  └─────────┘  └─────────┘   └─────────┘
         │
    Synthesizes + ships PR
```

### Coordination Protocol
**READ FIRST**: `data/coordination/SESSION_COORDINATION_PROTOCOL.md` — the full protocol for cross-session collaboration via Hivemind intent-based messaging.

Key principles:
1. **Broadcast messaging**: All entities post to the same Hivemind. Messages are broadcast, not point-to-point. Entities filter for messages targeted to them.
2. **Intent-based priority**: The `intent` field makes it easy to prioritize (question > blocker > status > observation)
3. **Polling with awareness**: Entities check awareness at session start, after each step, and every 15 minutes
4. **Kali as mediator**: Kali monitors all messages, mediates conflicts, provides steering
5. **Continuation as mailbox**: The `continuation` field is the message content

### For This Sprint
1. **Kali fixes the Hivemind first** (Q1 TTL, Q3 lock crash, Q7 path drift). ✅ DONE.
2. **Kali signals the user** that Hivemind is healthy. The user then opens 3 chat sessions.
3. **Each session follows the Session Coordination Protocol** (§6 of SCP):
   - Register for extended session (3h TTL)
   - Post starting status to Hivemind
   - After every major step: post update + check awareness
   - Every 15 minutes: heartbeat + check awareness
   - When asking a question: post with intent="question"
   - When blocked: post with intent="blocker"
   - When done: post completion + checkout
4. **Kali monitors via Hivemind** — reads awareness, answers questions, steers sessions
5. **No file conflicts**: Ma'at edits engine files. Quality reads only (audit). Roc reads legacy only. Zero overlap.

### Hivemind MCP Tools Required
The 3 sessions need these tools to coordinate:
- `omega-hub_hivemind_extended_checkin` — register for 3h session
- `omega-hub_hivemind_post_context` — post progress/messages (with `intent` field)
- `omega-hub_hivemind_get_awareness` — read all active agents' status
- `omega-hub_hivemind_get_continuation` — read one specific agent's latest message
- `omega-hub_hivemind_heartbeat` — keep presence alive
- `omega-hub_hivemind_extended_checkout` — cancel extended session

**Kali must verify every tool works before signaling the user.** ✅ DONE.

---

## §7: CONTACT & HANDOFF

### For the Kali Overseer
If you are reading this as a new Kali session:
- **Start here**: `data/coordination/CONTEXT_COMPRESSION_HANDOFF_20260607.md` (3-min loader)
- **Then**: `data/entities/kali/workspace/KALI_HANDOFF_SOVEREIGN_OVERSEER_20260607.md` (full tactical plan)
- **First action**: Fix the Hivemind MCP server (Q1, Q3, Q7)
- **Second action**: Verify all Hivemind tools work
- **Third action**: Signal the user that it's time to open the 3 chat sessions
- **Then**: Read Hivemind outputs as the 3 sessions post their progress
- **Finally**: Synthesize into v1.0.0 PR. Ship.

### Emergency Escalation
- If Kali can't fix the Hivemind lock crash (Q3) → defer Q3, ship with threading model, ship TTL+dockerfile only
- If Ma'at is blocked → posts to Hivemind, Kali sees it, may redirect
- If Quality finds a failing mandate → Ma'at must fix before PR (Kali reads this from Hivemind)
- If Roc finds conflicting architecture → Kali reads from Hivemind, reconciles
- If the timeline slips past the backup window → **Kali decides**: PR as-is or defer

---

## §8: PASS HISTORY

| Pass | Model | Date | What it did |
|------|-------|------|-------------|
| **v1.0.0** | DeepSeek V4 Flash | 2026-06-07 ~10:00Z | Built the strategic plan, 3 session protocols, timeline, phase gates, bug hit list |
| **v1.0.1** | MiniMax M3 | 2026-06-07 ~10:30Z | Acronym audit, delegation model, compression prep, scope finalization |
| **v1.0.2** | DeepSeek V4 Flash | 2026-06-07 ~11:00Z | Accuracy audit: stripped Entity-X prefix, fixed D125, added Gemini CLI protocol |
| **v3.0.0 (this)** | Big Pickle | 2026-06-07 ~11:15Z | **Workflow correction**: replaced subagent-launch model with Hivemind-first + peer chat sessions |

---

*⬡ OMEGA ⬡ KALI ⬡ Big Pickle ⬡ trc_workflow_correction ⬡ SPRINT-V3*
*Decision: D126 — Hivemind-First Workflow adopted. Subagent-launch model replaced with peer-chat-session model.*
