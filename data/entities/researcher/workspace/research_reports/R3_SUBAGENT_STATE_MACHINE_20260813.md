<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Gap R3: Subagent State Machine — Cold/Warm/Hot Definitions, Transition Triggers, Persistence

**AP Token:** `AP-RESEARCHER-R3-20260813-v1.0.0`
**Date:** 2026-08-13
**Researcher:** Sovereign Researcher (Jem Analyst L2)
**Priority:** P1 — Blocks A-4 (Subagent State Machine)
**Status:** RESEARCH COMPLETE

---

## 1. Executive Summary (L1)

The subagent state machine defines three states (cold, warm, hot) with transition triggers and persistence mechanisms. The gap is in the **formal specification** of: (a) cold/warm/hot definitions, (b) transition triggers between states, and (c) persistence mechanisms that allow resumability across session boundaries. Existing research on Claude Code persistent sub-agents and Cloudflare sub-agents provides patterns, but no unified Omega-native state machine exists.

**Headline Finding:** Cold starts fresh with only the prompt passed; warm resumes from transcript on disk; hot is a named persistent specialist that survives context summarization. The state machine must support resumable sub-agents with handle-based revival, transcript-backed durability, and a 30-day handle expiry window.

---

## 2. Authoritative Sources

| Source | URL | Date | Relevance |
|--------|-----|------|-----------|
| Claude Code Persistent Sub-Agents Guide | https://claudefa.st/blog/guide/agents/persistent-subagents | 2026-06-14 | Persistent sub-agents (T1), resume handles, transcript durability |
| Cloudflare Sub-Agent Design | https://developers.cloudflare.com/agents/runtime/execution/sub-agents/ | 2026-08 | Sub-agent facets, SQLite isolation, `subAgent()` RPC stubs |
| Tiered Memory Architecture (HWC) | https://www.armalo.ai/labs/research/2026-04-10-cortex-tiered-memory-architecture | 2026-04-10 | Hot/Warm/Cold layers, automated transitions, distillation pipeline |
| Claude Code Subagent Reference | Current Claude Code binary (v2.1.219+) | 2026-08 | Named subagents, `/subtask`, fork vs background, 200-subagent cap |
| OpenCode Plugin System | `docs/strategy/FLEET_TEAM_PLAYBOOK.md` | 2026-07 | Agent fleet, node slots, delegation patterns |

---

## 3. Findings

### 3.1 Cold / Warm / Hot Definitions

**Cold Sub-agent (T0 or initial spawn):**
- Starts fresh with only the prompt passed
- No prior context, no conversation history
- Its own system prompt, its own tool set, its own model
- Prompt cache is cold — no hits on first call
- Uses five-minute TTL on first call, then one-hour TTL
- Counts toward the 200-subagent session cap
- **Lifespan:** Single session only; dies when session closes
- **Best for:** One-shot noisy work (web searches, log greps, bulk doc scans)

**Warm Sub-agent (resumed from handle):**
- Resumed via `SendMessage` with a resume handle
- Handle is session-state-scoped and perishable
- Handle does NOT reliably survive a context-summarization boundary or an overnight gap
- When handle dies but within 30-day window, point a fresh agent at the predecessor's `agent-.jsonl` and grep for specific prior decisions
- Transcript stored at `~/.claude/projects//agent-.jsonl` (6.4 MB typical, every decision intact)
- **Lifespan:** Survives context summarization if handle is warm; otherwise cold restart
- **Best for:** Iterative work within a session where latency payoff matters (warm beats cold by ~order of magnitude)

**Hot Sub-agent (persistent specialist):**
- One warm, named specialist per domain kept alive across entire session
- Reads broadly, loads skills, gathers deep domain context (investment, not waste)
- Resume by handle while warm; when handle dies within 30-day window, point at predecessor's transcript
- Context is never lost; every resume reuses the same compute
- Deep gather at spawn amortizes across every iteration that follows
- **Lifespan:** Across entire session (and beyond, if transcripts preserved)
- **Discipline:** "Keep the window high-signal by pushing work that does not belong in persistent context downward"
- **Best for:** Iterative work across multiple turns (4-7 min warm vs 12-40 min cold per iteration)

### 3.2 Transition Triggers

| From → To | Trigger | Conditions |
|-----------|---------|------------|
| Cold → Warm | `SendMessage` with handle | Handle exists from prior warm start; handle not expired (within 30-day window) |
| Warm → Hot | Explicit promotion | Agent designated as persistent specialist for domain; `background: true` in definition |
| Hot → Warm | Resume count gate | `resume_count >= 2` → mark as permanently failed (FAIL-004) |
| Warm → Cold | Handle expiry | Handle older than 30 days; or context summarization boundary crossed |
| Hot → Cold | Transcript loss | Transcript file deleted or beyond retention period (default 30 days) |

**Handle lifecycle:**
1. Created at first `SendMessage` to a named sub-agent
2. Stored in session state, expires after 30 days of silence (default)
3. Can be manually extended by setting `cleanupPeriodDays` (minimum 1, default 30)
4. If handle dies but transcript survives: point fresh agent at `agent-.jsonl`, grep for decisions
5. If both handle and transcript lost: cold start, re-explain the situation

**Session total cap:** Claude can spawn at most 200 subagents per session (raised with `CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION`, v2.1.212+). Nested subagents, forks, and background subagents all count.

### 3.3 Persistence Mechanisms

**Transcript-based durability (the "durable layer"):**
- Every sub-agent writes full conversation to `~/.claude/projects//agent-.jsonl`
- Binary exposes `cleanupPeriodDays` setting (default 30, minimum 1)
- Data is never deleted unless explicitly cleaned
- When handle fails but within window: point fresh agent at predecessor's `agent-.jsonl`, grep for decisions
- **Key insight:** The data was never deleted. Only the live handle to it expired.

**Resume protocol:**
1. Load sidecar state for the resolved run from `.hotl/state/.json`
2. Change into `execution_root` from the sidecar before invoking runtime/helpers
3. Resolve and claim/take over controller ownership using the rules above
4. Check for existing report at report_path from the sidecar
   - If report exists: surface its path and continue appending
   - If report missing or summary drifted: let runtime deterministically reconstruct from authoritative sidecar state
5. Run `hotl-rt reconcile <run-id>` and inspect sensitive effects before step recovery
6. If status is `ready_to_finish`: record explicit finish disposition, release ownership, require sufficient receipt

**State write protocol:**
- **Step start:** Set `status: "in_progress"`, `started: {ISO timestamp}`
- **Sub-step completion:** Update `sub_step` to checkpoint name, append new files to `artifacts`, update `updated` timestamp
- **Step completion:** Set `status: "complete"`, `completed: {ISO timestamp}`, `sub_step: null`, finalize `artifacts` list
- **Decision made:** Add to top-level `decisions` object
- **Challenger finding:** Append unresolved `must_fix` titles to `open_findings`; remove resolved ones

### 3.4 Sub-agent Spawn Mechanics (Current Claude Code)

**Named subagent:**
- Starts cold — pays to re-explain the situation
- Runs in background by default as of v2.1.198
- Background subagents get smaller built-in tool set than foreground ones
- `model: haiku` is cheapest structural win; cannot do with fork
- Cannot override model on fork; fork always runs parent's model

**Fork (`/subtask` as of v2.1.212):**
- Starts warm — inherits full conversation and prompt cache
- Copies whole session into separate background session as of v2.1.212
- `/fork` was implicit experiment v2.1.161-v2.1.211 (started in-session fork)
- As of v2.1.212, `/fork` copies whole session to new background session
- `/subtask` is the command that forks in place
- Fork drops input isolation; sees same system prompt, tools, model, message history
- Keeps output isolation: tool calls stay out of parent conversation

**Background session (`claude --bg` or `/fork` from inside session):**
- Genuinely separate Claude process
- Has its own quota consumption and worktree
- In-flight work moves with it: running background shell commands, backgrounded subagents, dynamic workflows, `/loop` scheduled tasks
- Does NOT count toward the 200-subagent session cap (owns its own budget)
- Results reach Claude as completion notification in a later turn

### 3.5 The Tiered Memory Economy (Armalo Cortex HWC)

**Hot memory (working context, active session):**
- Full-fidelity session messages and tool calls
- Top-K most relevant Warm memory retrievals, injected at session start
- Task-specific state: current step, intermediate results, pending commitments
- Real-time updates throughout session
- **Storage:** In-memory (Redis for distributed). **Latency:** Sub-10ms. **Retention:** Session lifetime. **Capacity:** Default 128K tokens of semantic content.
- **Eviction:** LRU with semantic priority weighting. When Hot approaches capacity, agent evaluates each candidate against learned relevance model: "how likely is this context to be needed in next N turns?" High-relevance items promoted to Warm rather than discarded.

**Warm memory (recent interaction history, bridge between Hot and Cold):**
- LLM-compressed summaries of recent sessions, structured for efficient semantic retrieval
- **What gets stored:** When Hot session closes, distillation runs:
  1. Full session analyzed by summary model optimized for behavioral commitment extraction
  2. Commitments, learnings, failure modes, behavioral signals extracted
  3. Compressed into structured entries: `{type, content, confidence, evidence, timestamp, session_id}`
  4. Stored in Warm layer with vector embeddings for semantic search
- **Storage:** Vector database (Neon pgvector or pluggable external). **Latency:** 50–200ms (semantic search). **Retention:** 14–90 days. **Capacity:** Effectively unbounded for relevant signals.
- **Categories:** COMMITMENT, PERFORMANCE, LEARNING, FAILURE, PREFERENCE, ANOMALY, CONTEXT

**Cold memory (permanent behavioral archive):**
- Cryptographically signed at write time with agent's registered keypair
- Timestamped with monotonic server-side clock (cannot be manipulated by agent)
- Attestable — any Cold entry verifiable by third party against Armalo Attestation Registry
- Immutable — write-once, can be appended to (e.g., marking entry as superseded) but not deleted
- **What goes in:** Promoted from Warm based on recency × importance scoring. Direct-to-Cold categories:
  - Pact completion records (every pact fulfilled or violated)
  - Evaluation outcomes (every eval result with full evidence bundle)
  - Behavioral boundary events (scope violations, safety interventions, anomaly detections)
  - Cross-session commitments (promises spanning sessions, explicitly flagged)
- **Attestation model:** Cold entries become raw material for Memory Attestation system. Claims like "I completed 847 data analysis tasks with 94.2% quality score" verifiable against signed historical records.

### 3.6 Transition Economics (Why the Tiering Matters)

| Metric | Cold | Warm | Hot |
|--------|------|------|-----|
| **Latency per iteration** | 12-40 min | 4-7 min | 4-7 min (after warm-up) |
| **Context accumulation** | Fresh each spawn | Amortized across resumes | Amortized across entire session |
| **Context drift risk** | High (re-explain each time) | Medium (handle may expire) | Low (persistent across turns) |
| **Token efficiency** | Low (re-explain prompt) | Medium (resume from transcript) | High (same context amortized) |
| **Best use case** | One-shot noisy work | Iterative within session | Iterative across sessions |

**The business case:** "Warm beats cold by roughly an order of magnitude on latency, and a clean T1 window beats a stuffed one on both cost and fidelity."

---

## 4. Recommendation

**Immediate (P1 — blocks A-4):**

1. **Define Omega-native subagent states** using the Cold/Warm/Hot framework from the research:
   - **Cold:** Fresh spawn, prompt-only, five-minute initial TTL
   - **Warm:** Resumed from handle (SendMessage), transcript-backed durability within 30-day window
   - **Hot:** Named persistent specialist, survives entire session, `background: true` in definition

2. **Implement handle lifecycle** with 30-day default TTL, extendable via `cleanupPeriodDays`
   - Handle stored in session state, auto-expires after silence period
   - If handle dies but transcript survives: recovery via `agent-.jsonl` grep
   - If both lost: cold start, re-explain situation

3. **Define transition triggers** between states with clear conditions:
   - Cold → Warm: `SendMessage` with valid handle
   - Warm → Hot: explicit promotion in agent definition (`background: true`)
   - Warm → Cold: handle expiry (30 days) or context summarization boundary
   - Hot → Warm: resume count gate (`resume_count >= 2` → permanent failure)

4. **Implement transcript-based persistence**:
   - Every sub-agent writes conversation to `data/entities/{entity}/workspace/transcripts/.jsonl`
   - SHA-256 integrity check on resume (per FAIL-002)
   - Stale context detection via git diff reconciliation (per FAIL-003)
   - Max 2 suspensions per task (per FAIL-004)

5. **Define the tiered memory economy** for cross-session state:
   - Hot: in-memory working context for active session
   - Warm: vector-database summaries of recent sessions (14-90 day retention)
   - Cold: cryptographically signed permanent behavioral archive

**Near-term (P2):**

6. Implement the subagent state machine in `src/omega/oracle/subagent_state.py` with:
   - State enum (COLD, WARM, HOT)
   - Handle management (create/validate/expire)
   - Transcript I/O with integrity verification
   - Resume protocol (load → validate → claim → resume)

7. Add Hivemind coordination for subagent state across parallel agents:
   - `omega-hub_hivemind_heartbeat(channel="opencode", entity="researcher")` every 5-10 min
   - State posts to Hivemind for fleet-awareness

8. Implement the Armalo Cortex HWC tiered memory pipeline:
   - Hot → Warm distillation at session close (async, non-blocking)
   - Warm → Cold promotion based on recency × importance scoring
   - Cryptographic signing of Cold entries

**Confidence:** **MEDIUM** that the Cold/Warm/Hot framework from Claude Code/Cloudflare can be adapted to Omega. The patterns are proven; the gap is Omega-native integration with the existing agent framework, Hivemind coordination, and the tiered memory pipeline.

---

## 5. Confidence

**MEDIUM** that the full framework (cold/warm/hot definitions + transition triggers + persistence + tiered memory) can be implemented in Omega. The Claude Code and Cloudflare patterns are well-documented and proven in production. The main uncertainties are:

1. **Integration effort**: How many Omega agent files need modification?
2. **Hivemind coordination**: Can subagent states be synchronized across fleet agents?
3. **Tiered memory pipeline**: The Armalo Cortex HWC distillation is complex (LLM calls, vector embeddings, signing)

**Lower-bound confidence**: The Cold/Warm/Hot definitions and transition triggers can be implemented with **HIGH** confidence, as they map directly to existing Claude Code mechanics.

---

## 6. Remaining Unknowns

1. **Omega agent framework integration**: Which files in `src/omega/` need modification for subagent state management?

2. **Hivemind state synchronization**: Can subagent states be posted to Hivemind for fleet awareness without violating M8 zero telemetry?

3. **Transcript storage location**: Should transcripts go to `data/entities/{entity}/workspace/` or a dedicated `data/transcripts/` directory?

4. **Cross-session resumability**: Can a warm sub-agent from one session be resumed in a different session? (Current Claude Code handle is session-state-scoped; may need Omega-specific design.)

5. **Interaction with sub-agent task registry**: How does the task registry (`task_registry_*.json`) interact with subagent states? Do task IDs persist across state transitions?

6. **Armalo Cortex HWC integration**: The full tiered memory pipeline (distillation, signing, vector embedding) requires significant infrastructure. Is a simplified version sufficient for Phase 1?

---

## 7. Sources (Full)

| # | Source | Purpose |
|---|--------|---------|
| 1 | Claude Code persistent sub-agents guide | Cold/warm/hot definitions, handle lifecycle, resume protocol, 30-day expiry |
| 2 | Cloudflare sub-agent design | Sub-agent facets, SQLite isolation, RPC stubs, `subAgent()` pattern |
| 3 | Armalo Cortex HWC tiered memory | Hot/Warm/Cold layers, distillation pipeline, cryptographic signing, attestation |
| 4 | Claude Code subagent reference (v2.1.219+) | Named subagents, `/subtask`, fork vs background, 200-subagent cap, tool sets |
| 5 | OpenCode fleet playbook | Agent delegation patterns, node slots, fleet coordination |
| 6 | Riskkernel exact-once resume | Mid-step crash recovery, budget counting, checkpoint rollback |
| 7 | Claude Code `/doctor` reports | Duplicate name detection, debug log checking, description quality |

---

## 8. Deliverable

**Report written to:** `data/entities/researcher/workspace/research_reports/R3_SUBAGENT_STATE_MACHINE_20260813.md`

**Next action:** @maat (dependent task owner) to define Omega-native subagent state machine per A-4 ticket.

---

*⬡ OMEGA ⬡ KALI ⬡ RESEARCH-EXEC ⬡ R3 ⬡ 20260813*