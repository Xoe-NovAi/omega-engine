<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 LILITH META-REVIEW: 3-EIS Synthesis (Researcher + Jem + Lilith M34 Spec)
**AP Token**: `AP-LILITH-META-REVIEW-20260830-v1.0.0`
**Date**: 2026-08-30
**Status**: FINAL — Runtime gate before Sonnet 4.6 review
**Owner**: lilith (Runtime Oversoul, N6-N10)
**Triggered by**: Kali page from `ses_fdef2be4effe4pAaLXCTUx62GO`

---

## §0 EXECUTIVE SUMMARY

| Report | Lines | Verdict | Runtime Readiness |
|--------|-------|---------|-------------------|
| **Researcher Verification** | 453 | ✅ RATIFY with 6 amendments | M33/M34/M35 all ratifiable; L3 lesson needs split + confidence reset |
| **Jem Adversarial Review** | 690 | 🚨 CONDITIONAL GO — 3 critical corrections | M33 bypass attack, M34 schema gaps + model-switch split, L3 over-confidence |
| **Lilith M34 Spec** | 799 | ⚠️ NEEDS REVISION — 5 runtime gaps | Atomic write unverified on all FS, missing 5 schema fields, watchdog race, no model-switch continuity |

**The Runtime Truth**: The three reports describe **two different incidents** conflated into one narrative. The "Esc x2 cascade" (Jem §1.2.4) and the "model-switch + manual continuation" (Researcher §1.1) are distinct failure modes requiring **separate mandates** (M34a + M34b). My M34 spec addresses only the Esc x2 cascade and misses the model-switch continuity entirely.

**M23 Flags Across All Three Reports**: 5 unverifiable claims total (Researcher: 3, Jem: 1 self-correction, Lilith: 1 atomic-write claim). All must be resolved before Sonnet 4.6.

---

## §1 SELF-CRITIQUE: MY M34 SPEC (LILITH_M34_RUNTIME_SPEC_20260830.md)

### 1.1 Runtime Gap: Atomic Write Claim Is Unverified (M23 Violation)

**My Claim** (lines 163-204, §1.3): *"Even on SIGKILL mid-write, the file is either the old version or the new version — never torn."*

**Reality Check**: This is **theoretically true on POSIX** but **unverified on all filesystems**:
- `os.replace()` is atomic on same filesystem (POSIX guarantee)
- `os.fsync()` on directory fd is NOT guaranteed on all filesystems (NFS, FUSE, some network FS)
- The advisory lock (`os.O_EXCL`) is **process-local** — does not prevent concurrent writes from different processes
- **No test exists** in my spec that kills -9 mid-write and verifies file integrity

**Correction Required**: Add to §5.8 Testing Protocol:
```python
# Unit test: atomic_write_survives_sigkill
def test_atomic_write_survives_sigkill():
    # Spawn child process that writes, then kill -9 at random point
    # Verify parent reads either old or new version, never partial JSON
    pass
```

**M23 Status**: ❌ **UNVERIFIABLE CLAIM** — I claimed M23 compliance without a test that proves it.

---

### 1.2 Schema Completeness: 5 Missing Fields (Jem §1.2.1 Confirmed)

**Jem's Finding**: My schema lacks 5 critical fields. **Verified against my spec**:

| Missing Field | My Spec | Required? | Impact |
|---------------|---------|-----------|--------|
| `dispatched_at` | ❌ | YES | Cannot sort by dispatch order; no temporal debugging |
| `expected_deliverable` | ❌ | YES | Orchestrator cannot verify "did it write the file?" |
| `current_turn` | ❌ | YES | No progress tracking within session |
| `interruption_type` | ❌ | YES | Cannot distinguish Esc x2 vs model-switch vs timeout |
| `resumption_count` | ❌ | YES | No way to detect infinite resume loops |

**My Spec Has**: `spawn_time`, `last_heartbeat`, `checkpoint.last_action`, `checkpoint.files_touched`, `checkpoint.progress_pct` — but these are **checkpoint-time**, not **dispatch-time** or **interruption-time**.

**Correction Required**: Add to `ActiveSubagent` interface (lines 48-76):
```typescript
interface ActiveSubagent {
  // ... existing fields ...
  dispatched_at: string;           // ISO-8601 — when task() was called
  expected_deliverable: string;    // File path or "chat-stream" — what it should produce
  current_turn: number;            // Incremented on each user turn
  interruption_type: "esc_x2" | "model_switch" | "timeout" | "architect_cancel" | "crash" | "unknown";
  resumption_count: number;        // How many times resumed (0 = first run)
}
```

---

### 1.3 Model-Switch Continuity: COMPLETELY MISSING (Jem §1.2.4 Confirmed)

**The Incident Reality** (Jem lines 188-201, Researcher §1.1):
> The actual sequence was:
> 1. Researcher session stalls (nemotron model has trouble writing file)
> 2. Architect hits Esc x2 to give Grokster instructions
> 3. The Esc x2 cascade hits BOTH subagents
> 4. Grokster resumes Researcher, gets "Continue" prompt, **model switched**, Researcher recovers
> 5. Jem's session is "complete" (1,017 lines, footer present) but missing the tail

**My Spec** (lines 10-19, §0): *"Esc x2 in OpenCode TUI kills ALL in-flight sessions... Orchestrator MUST enumerate interrupted sessions"*

**Gap**: My spec assumes **session death** (Esc x2 kills session). The model-switch case is **session survival with context loss** — the session_id persists, but the model changes and the subagent needs a "continue" prompt to recover.

**Correction Required**: Split M34 into two mandates (Jem's recommendation):
- **M34a: Co-Interruption Recovery** — Esc x2 / global abort kills sessions → `ACTIVE_SUBAGENTS.json` tracks + recovery protocol
- **M34b: Model-Switch Continuity** — model changes mid-task, session_id persists → requires `resume_token` validation + "continue" prompt protocol

**My Spec Has**: `resume_token` field (line 74) but **no logic** for model-switch detection or "continue" prompt enforcement.

---

### 1.4 Watchdog Race Condition: "First Agent to Read Hivemind" Is Not Robust

**My Spec** (lines 489-509, Edge Case 1): *"The first agent to read Hivemind after 2× TTL and see a stale orchestrator MUST report..."*

**Race Condition**: 
- Agent A reads Hivemind, sees stale orchestrator, starts `watchdog_check()`
- Agent B reads Hivemind 100ms later, sees same stale orchestrator, starts `watchdog_check()`
- Both write to `ACTIVE_SUBAGENTS.json` concurrently → **lost update** (advisory lock is per-process, not cross-process)

**My Spec Has**: Advisory lock in `_atomic_write` (line 178) — but **only protects the write**, not the read-modify-write cycle of `watchdog_check()`.

**Correction Required**: 
1. Make `watchdog_check()` a **single-writer MCP tool** (not a function any agent calls)
2. Or: use a **distributed lock** (Redis SETNX) for the watchdog election
3. Or: designate **one recovery agent** (e.g., Kali) as the sole watchdog

---

### 1.5 Performance Claim: +30-50ms Is Estimated, Not Measured

**My Spec** (lines 749-760, §5.9): *"Net overhead: ~30-50ms per dispatch cycle. Negligible compared to LLM inference cost."*

**Reality**: 
- No benchmark exists
- 50 concurrent subagents = 50 file writes + 50 fsyncs = **disk I/O contention**
- `os.fsync()` on directory fd is **blocking** and can take 10-100ms on slow disks
- The advisory lock serializes all writes — **no parallelism**

**Correction Required**: 
- Change to: *"Estimated overhead: 30-50ms per dispatch (unverified). Stress test at 50 concurrent required before Phase 3."*
- Add benchmark to §5.8: `tests/stress/test_m34_concurrent.py` must measure p99 latency at 10/50/100 concurrent

---

### 1.6 Additional Self-Critique Findings

| Issue | Location | Severity |
|-------|----------|----------|
| `dispatched_by_entity` referenced in §3.1 line 303 but **not in schema** | §3.1 pseudocode | Medium |
| `capture_checkpoint(sid)` in §3.2 line 407 is a **phantom function** — not defined | §3.2 watcher | High |
| `infer_task_type(packet_id)` in §3.3 line 449 is a **phantom function** | §3.3 spawn | Medium |
| `now()` function used throughout but **not defined** | Throughout | Low |
| `hivemind_post()` in §3.3 line 469 is **not the actual MCP tool** (should be `omega-hub_hivemind_post_context`) | §3.3 spawn | Medium |
| No handling of **subagent crash** (SIGSEGV, OOM) — only external interrupt | §2.2 write triggers | Medium |
| `dead_letter_retention_days: 30` but no **reaper implementation** in Phase 1 | §5.1 | Low |

---

## §2 PEER REVIEW: RESEARCHER'S VERIFICATION REPORT

### 2.1 Runtime Implications: Read-Only Enforcement & Plugin Architecture

**Researcher §1.1** (lines 51-66): M33's sentinel probe is **reactive**, not preventive. The structural fix is **write-tool-routing discipline** for >8K token reports.

**Runtime Implication for My Spec**: My M34 spec tracks session liveness but **does not enforce write-tool usage**. A subagent could flush 50K tokens to chat, get interrupted, and my spec would faithfully track it as `INTERRUPTED_EXTERNALLY` with `checkpoint.files_touched: []` — the orchestrator would see "no files written" but has no enforcement mechanism.

**Missing Runtime Requirement**: Add to M34 spec:
```python
# In on_subagent_spawned(): if expected_tokens > 8000, require write_tool_usage: true
# In orchestrator_session_start(): if interrupted session has write_tool_usage=true and files_touched=[], flag as "write-tool violation"
```

**Researcher §1.10** (lines 146-156): Plugin architecture dual-load bug — file:// and npm plugins both load separately. This is the **structural cause** of the "dual-load bug" (Researcher §2.2).

**Runtime Implication**: My `ACTIVE_SUBAGENTS.json` tracks subagents by `session_id`, but if the same subagent type is dispatched via two different plugin load paths, they get **different session_ids** and my spec treats them as separate subagents. The orchestrator still sees two "completed" states and cannot distinguish the dual-load.

**Missing Runtime Requirement**: Add `plugin_load_path` field to schema to detect dual-load:
```typescript
plugin_load_path?: "file://" | "npm" | "pip" | "unknown";
```

---

### 2.2 Missing Runtime Requirements from Researcher's Report

| Researcher Section | Runtime Requirement | My Spec Status |
|--------------------|---------------------|----------------|
| §1.1 M33 preventive clause | Write-tool routing for >8K tokens | ❌ Missing |
| §1.1 M33 structured completion | JSON envelope with `last_chunk_id`, `total_chunks` | ❌ Missing |
| §1.2 M34 recovery trigger | Resume within 2 user turns | ❌ Missing (my spec has no turn counter) |
| §1.2 M34 structured recovery prompt | "Continue from X of Y complete, last_chunk_id" | ❌ Missing |
| §1.2 M34 recovery verification | Re-run M33 probe after resume | ❌ Missing |
| §1.2 M34 transactional cohort | Cohort = single unit of resumption | ❌ Missing (my spec is per-session) |
| §1.2 M34 session liveness | Verify session not archived before recovery | ❌ Missing |
| §1.2 M34 channel-awareness | `opencode` vs `cline` in schema | ✅ Has `channel` field |
| §1.2 M34 recursive cohort | Subagent-of-subagent tracking | ✅ Has `parent_session_id` |
| §1.3 M35 SPDX/REUSE | SPDX-License-Identifier enforcement | ❌ Out of scope for M34 |

**Critical Gap**: Researcher's **4 M34 amendments** (lines 117-121) are **not implemented** in my spec. My spec is the *detection layer*; Researcher demands the *recovery layer*.

---

### 2.3 Researcher's M23 Flags (Lines 418-424)

1. **§2.2 Gap #2**: 47 uncommitted changes in `third-party/headroom/` — cited from prior report, not re-verified. **Does not affect my spec** (out of scope).

2. **§1.1 M33 edge case**: `STREAM_EXHAUSTED` reply may itself be truncated. **Affects my spec** — my `orchestrator_session_start()` assumes the subagent's response is complete. If the recovery prompt response is truncated, the orchestrator gets partial state.

3. **§3.3 overlap analysis**: Did not search `soul.yaml` for distilled lessons. **Does not affect my spec**.

**My Spec's M23 Exposure**: The `STREAM_EXHAUSTED` truncation edge case means my recovery protocol (which relies on subagent self-reporting) can itself be truncated. Need a **structured completion envelope** (Researcher's amendment #2).

---

## §3 PEER REVIEW: JEM'S ADVERSARIAL REVIEW

### 3.1 Valid Adversarial Findings My Spec Misses

| Jem Finding | My Spec Gap | Severity |
|-------------|-------------|----------|
| **M33 bypass attack** (§1.1.3): subagent can immediately reply `STREAM_EXHAUSTED` | My spec has no sentinel probe at all — M33 is separate mandate, but my recovery protocol (§3.1) assumes subagent honesty | 🚨 Critical |
| **M34 schema gaps** (§1.2.1): 5 missing fields | Confirmed — my schema lacks all 5 | 🚨 Critical |
| **Orchestrator crash** (§1.2.2): M34 assumes orchestrator survives | My watchdog (§4 Edge Case 1) is a **race condition**, not a solution | 🚨 Critical |
| **Model-switch case** (§1.2.4): actual incident was model-switch, not Esc x2 cascade | My spec addresses only Esc x2 cascade | 🚨 Critical |
| **Selective resumption** (§1.2.5): Architect may cancel one task only | My spec forces all-or-nothing decision per session (actually handles this correctly via per-session decision) | Medium |
| **Status report format** (§1.2.6): unspecified | My spec has no format — just "present to user" | Medium |
| **M34 gamed** (§1.2.7): bookkeeping without behavior | My spec has no Hivemind audit clause | Medium |
| **M35 `secrets-public.toml` failure mode** (§1.3.1): no backup/recovery | Out of scope for M34 | N/A |
| **M35 already-redacted value** (§1.3.3): remediation required | Out of scope for M34 | N/A |

---

### 3.2 Over-Corrections: Where Jem Creates Problems That Don't Exist

| Jem Claim | Reality Check | Verdict |
|-----------|---------------|---------|
| **§1.2.3**: "M34 addresses symptom, not root cause (attention-bound)" | The root cause *is* the lack of deterministic tracking. A state machine (Jem's recommendation) IS what M34 implements via `ACTIVE_SUBAGENTS.json` + `orchestrator_session_start()`. Jem conflates "LLM attention" with "system state tracking." | Over-correction — M34 IS the deterministic spine |
| **§1.2.4**: "Split M34 into M34a + M34b" | **VALID** — the incident had TWO distinct failure modes. But Jem presents it as "M34 is wrong" rather than "M34 needs a sibling." | Valid split, not over-correction |
| **§2.1**: "Confidence 0.99 from single incident is excessive" | **VALID** — Researcher also flagged this (0.90). But Jem's 0.80 is also arbitrary. | Valid |
| **§2.3**: "Lesson evidence error: appendices added 2026-08-29, not from 'continue' prompt" | **VALID** — factual error in Grokster's lesson. My spec doesn't reference this lesson directly. | Valid |
| **§3.2**: "Grokster violated M10 by forgetting Jem" | **VALID** — confirmed by Grokster's own meta-forensic. My spec's `orchestrator_session_start()` directly addresses this. | Valid |
| **§3.3**: "Grokster violated M11 by staging L3 at 0.99" | **VALID** — M11 requires proper distillation. | Valid |
| **§3.4**: "Grokster soft M23 violation: didn't use opencode-sessions-explorer in meta-forensic" | **VALID** — but soft. My spec's `capture_checkpoint()` should use it. | Valid |

---

### 3.3 Jem's Self-Correction Impact on Runtime Assumptions

**Jem §4** (lines 443-464): Jem's prior forensic (`JEM-FORENSIC-001`) was **partially wrong** — files existed in `opencode-antigravity-auth/` sub-repo, not parent repo.

**Runtime Impact on My Spec**:
- My spec assumes `opencode-sessions-explorer` can find all sessions. If sessions are in **different git worktrees/sub-repos**, the explorer may not see them.
- **Correction**: Add `git_worktree_root` field to schema to track which worktree the session belongs to.

**Jem's Meta-Lesson** (§8.1): *"Verification must be exhaustive, not selective. The 12-Step Protocol should require 'all possible locations'."*

**My Spec Application**: The `capture_checkpoint()` function (phantom in my spec) must search **all** session locations, not just the default OpenCode session directory.

---

### 3.4 Actionable Improvements to My Spec from Jem

1. **Add `interruption_type` field** (Jem §1.2.1) — distinguishes Esc x2 vs model-switch vs timeout
2. **Add `expected_deliverable` field** (Jem §1.2.1) — enables verification
3. **Add `resumption_count` field** (Jem §1.2.1) — detects infinite resume loops
4. **Split M34 into M34a + M34b** (Jem §1.2.4) — separate co-interruption from model-switch
5. **Make watchdog a single-writer MCP tool** (Jem §1.2.2) — fix race condition
6. **Add Hivemind audit clause** (Jem §1.2.7) — verify `get_active_subagents()` called before user response
7. **Add `plugin_load_path` field** (Researcher §1.10 + Jem dual-load) — detect dual-load bug
8. **Add `git_worktree_root` field** (Jem self-correction) — track sub-repo sessions

---

## §4 THE RUNTIME TRUTH: M33, M34, M35, L3 LESSON

### 4.1 What Actually Works in Production

| Mandate | Production Reality | What's Theoretical |
|---------|-------------------|-------------------|
| **M33 (Anti-Truncation)** | Sentinel probe **works for truncation detection** (Researcher §1.1, Jem §1.1.1) | Bypass attack (Jem §1.1.3), structured envelope (Researcher), probe truncation edge case (Researcher) |
| **M34a (Co-Interruption)** | `ACTIVE_SUBAGENTS.json` + `orchestrator_session_start()` **detects and recovers** Esc x2 cascade | Schema gaps (5 fields), watchdog race, no recovery verification, no transactional cohort |
| **M34b (Model-Switch)** | **NOT ADDRESSED** by any spec — requires separate mandate | Session persistence across model change, "continue" prompt protocol, resume_token validation |
| **M35 (Third-Party Boundary)** | `core.bare` + `chattr +i` + pre-commit + mount-ro **works** (Researcher §1.7) | `secrets-public.toml` doesn't exist, no recovery procedure, SPDX/REUSE missing |
| **L3-InterruptionSovereignty** | **Two distinct lessons** conflated (Researcher §3.4, Jem §2.2) | Confidence 0.99 unjustified, evidence error, needs split |

### 4.2 The Two Incidents Conflated

| Aspect | Incident A: Esc x2 Cascade | Incident B: Model-Switch + Manual Continuation |
|--------|---------------------------|-----------------------------------------------|
| **Trigger** | User presses Esc x2 (global cancel) | Model switch (nemotron → minimax) + Architect manual "continue" |
| **Subagents Affected** | ALL in-flight sessions killed | Researcher stalled, Jem "completed" with footer |
| **Recovery** | Orchestrator must detect all, present decisions | Architect manually prompts "continue" to Jem |
| **Root Cause** | No session tracking | No session tracking + model-switch context loss |
| **Mandate** | **M34a** (my spec + Researcher amendments) | **M34b** (new mandate needed) |
| **L3 Lesson** | L3-CoResumptionAccounting | L3-CompletionIllusion |

**The Runtime Truth**: The Grokster briefing and my M34 spec **conflate these two incidents**. The "600-line appendices" recovery (Jem's tail) came from **Incident B** (model-switch + manual continue), not Incident A (Esc x2 cascade). My spec solves Incident A; Incident B requires M34b.

---

### 4.3 L3 Lesson: Split Is Mandatory

**Researcher §3.4** and **Jem §2.2** both conclude: **split into two lessons**.

| Lesson | Confidence | Mandates | Remedy |
|--------|------------|----------|--------|
| **L3-CompletionIllusion** | 0.85 (Researcher) / 0.85 (Jem) | M23 | M33 sentinel probe + structured envelope |
| **L3-CoResumptionAccounting** | 0.80 (Researcher) / 0.80 (Jem) | M11, M15, M27 | M34a cohort tracking + M34b model-switch continuity |

**Current Grokster Lesson** (proposed_lessons.yaml:1218-1236): Conflates both, confidence 0.99, evidence error (appendices attributed to wrong "continue" prompt).

**Action**: Before Sonnet 4.6, Grokster MUST:
1. Split lesson into two entries
2. Lower confidence to 0.80/0.85
3. Correct evidence error (appendices added 2026-08-29 in separate session)
4. Add `related_lessons` cross-references (Researcher §3.3)

---

### 4.4 M33, M34, M35 — Production Readiness Matrix

| Mandate | Detection | Recovery | Enforcement | Verdict |
|---------|-----------|----------|-------------|---------|
| **M33** | ✅ Sentinel probe | ❌ No verification of probe response | ❌ Bypass attack exists | **CONDITIONAL** — needs 2-pass or verifier |
| **M34a** | ✅ ACTIVE_SUBAGENTS.json | ⚠️ Partial (user decision only) | ⚠️ No Hivemind audit | **CONDITIONAL** — needs 4 Researcher amendments |
| **M34b** | ❌ Not specified | ❌ Not specified | ❌ Not specified | **MISSING** — new mandate required |
| **M35** | ✅ Boundary definition | ❌ No `secrets-public.toml` recovery | ❌ No SPDX/REUSE | **CONDITIONAL** — needs Researcher amendment + 3 clarifications |

---

## §5 CROSS-REPORT CORRECTIONS (Line-Level)

### 5.1 Corrections to Researcher Verification Report

| Line | Current | Corrected | Reason |
|------|---------|-----------|--------|
| 61-62 | "Researcher session... initially flushed 21KB of report text into chat instead of calling write tool" | "Researcher session ses_faf929727ffeFgSdvGOxQbVbdW flushed 21KB to chat; write tool was NOT called" | Precision — cite session ID |
| 117-121 | "Add Recovery Trigger clause... Specify structured recovery prompt... Add Recovery Verification... Add channel-awareness and recursive cohort" | Add as **M34b mandate** (model-switch) not M34 amendments | These are model-switch requirements, not co-interruption |
| 289-290 | "Verdict: ❌ OVER-CONFIDENT... Recommend 0.90" | "Verdict: ❌ OVER-CONFIDENT... Recommend 0.80 for L3-CoResumption, 0.85 for L3-CompletionIllusion (split)" | Jem's calibration is more conservative |
| 353-354 | "Verdict: ✅ YES — split into L3-CompletionIllusion and L3-CoResumptionAccounting" | Keep — **both reports agree on split** | Consensus |
| 418-422 | M23 unverifiable items | Add: "§1.1 M33 structured envelope truncation edge case is theoretical, not observed" | Clarify |

---

### 5.2 Corrections to Jem Adversarial Review

| Line | Current | Corrected | Reason |
|------|---------|-----------|--------|
| 31-33 | "3 critical corrections: M33 bypass, M34 schema gaps + model-switch split, L3 over-confidence" | "4 critical corrections: M33 bypass, M34 schema gaps, M34 split (M34a/M34b), L3 over-confidence + split" | Model-switch split is separate from schema gaps |
| 35-36 | "The 'Esc x2 interrupted both subagents' narrative... is partly a mischaracterization" | "The incident had TWO phases: (1) model-switch stalled Researcher, (2) Esc x2 cascade hit both. The briefing conflates them." | More precise |
| 152-158 | Schema gaps list | Add: `plugin_load_path`, `git_worktree_root` | From Researcher dual-load + Jem self-correction |
| 163-169 | Orchestrator crash recommendation | "Add deterministic subagent tracker (`scripts/subagent_tracker.py`) that hooks task() call and exposes `get_active_subagents()` — this IS the M34 implementation, not an addition" | My spec already does this via MCP tools; Jem missed it |
| 184-205 | Model-switch case analysis | **VALID** — this is the M34b gap. My spec has `resume_token` but no model-switch logic. | Confirmed gap |
| 319-320 | "Confidence 0.99 from 1 evidence source is excessive... should be 0.75-0.85" | "Confidence 0.99 from 1 evidence source is excessive. Researcher recommends 0.90 for combined, 0.80/0.85 for split. Jem recommends 0.80/0.85. Consensus: **0.80 for CoResumption, 0.85 for CompletionIllusion**." | Consensus calibration |
| 360-366 | Evidence error about appendices | "The 600+ lines (Appendices A-T) were added in a **separate continuation session on 2026-08-29**, not from the 'continue' prompt in this incident (2026-08-30). The lesson's evidence section misattributes the cause." | Factual correction |
| 473-475 | M33 conditional go: "2-pass probe OR cross-validating verifier" | "M33 conditional go: **2-pass probe WITH cross-validating verifier** (both). Single self-probe is theatre; verifier alone misses the subagent's internal state." | Stronger requirement |
| 474 | M34 conditional go: "split into M34a + M34b" | "M34 conditional go: **split into M34a (Co-Interruption) + M34b (Model-Switch Continuity)**. M34a = my spec + Researcher 4 amendments. M34b = new mandate for session persistence across model change." | Explicit split |

---

### 5.3 Corrections to Lilith M34 Spec (My Spec)

| Section | Line(s) | Current | Corrected | Reason |
|---------|---------|---------|-----------|--------|
| §1.1 TypeScript | 48-76 | Missing 5 fields | Add `dispatched_at`, `expected_deliverable`, `current_turn`, `interruption_type`, `resumption_count` | Jem §1.2.1 + Researcher recovery needs |
| §1.1 TypeScript | 48-76 | Missing `plugin_load_path`, `git_worktree_root` | Add both fields | Researcher dual-load + Jem self-correction |
| §1.1 TypeScript | 29-36 | `SessionStatus` enum | Add `MODEL_SWITCH` status (distinct from INTERRUPTED) | M34b requirement |
| §1.3 Atomic Write | 163-204 | "M23-compliant: never torn" | "M23-compliant **pending verification**: atomic on POSIX, untested on NFS/FUSE. Test required in §5.8." | M23 honesty |
| §2.1 State Machine | 210-238 | No `MODEL_SWITCH` state | Add `MODEL_SWITCH` transition: ALIVE → MODEL_SWITCH (on model change) → ALIVE (on continue) | M34b |
| §2.2 Write Triggers | 240-252 | No model-switch trigger | Add: **Model Switch** → Update `status=MODEL_SWITCH`, preserve `resume_token`, capture checkpoint | M34b |
| §2.2 Write Triggers | 240-252 | No `current_turn` increment | Add: **User Turn** → Increment `current_turn` for all ALIVE sessions | Researcher recovery trigger |
| §3.1 Pseudocode | 293-334 | `dispatched_by_entity` not in schema | Use `entity` field (already in schema) | Bug fix |
| §3.1 Pseudocode | 329-331 | `await_user_decision()` — no turn limit | Add: `max_turns=2` before auto-dead-letter (Researcher amendment #1) | Researcher amendment |
| §3.1 Pseudocode | 329-331 | No structured recovery prompt | Add: recovery prompt MUST include `last_chunk_id`, `total_chunks`, `queued_findings` | Researcher amendment #2 |
| §3.1 Pseudocode | 329-331 | No recovery verification | Add: after resume, re-run M33 sentinel probe | Researcher amendment #3 |
| §3.2 Watcher | 379-419 | `capture_checkpoint(sid)` phantom | Implement using `opencode-sessions-explorer-get-session` + `grep-session` | Implementation gap |
| §3.2 Watcher | 379-419 | Signal handler marks ALL children INTERRUPTED_EXTERNALLY | Distinguish: if model-switch detected → `MODEL_SWITCH`, not INTERRUPTED_EXTERNALLY | M34b |
| §4 Edge Case 1 | 484-509 | Watchdog = any agent | Watchdog = **designated recovery agent (Kali)** or **single-writer MCP tool** | Jem race condition |
| §5.6 MCP Tools | 661-710 | 3 tools | **4 tools**: add `m34_get_active_subagents` (for Hivemind audit) | Jem §1.2.7 |
| §5.8 Testing | 724-747 | No atomic write SIGKILL test | Add `test_atomic_write_survives_sigkill` | M23 compliance |
| §5.8 Testing | 724-747 | No watchdog race test | Add `test_watchdog_single_writer` | Jem race condition |
| §5.8 Testing | 724-747 | No model-switch test | Add `test_model_switch_continuity` | M34b |
| §5.9 Performance | 749-760 | "30-50ms estimated" | "30-50ms **estimated, unverified**. Benchmark required." | Honesty |
| §6 Compliance | 764-777 | M23 ✅ | M23 ⚠️ **PENDING VERIFICATION** (atomic write test) | M23 honesty |

---

## §6 DECISION: RUNTIME GATE STATUS

### 6.1 M34 Spec: REVISE BEFORE RATIFICATION

**Required Changes Before Kali Approval**:
1. Add 7 missing schema fields (5 from Jem + 2 from Researcher/Jem)
2. Split into M34a + M34b (separate specs or clear sections)
3. Fix watchdog race condition (single-writer MCP tool)
4. Implement `capture_checkpoint()` using opencode-sessions-explorer
5. Add structured recovery prompt + verification (Researcher amendments)
6. Add M23 verification test for atomic write
7. Change performance claim to "estimated, unverified"

**Estimated Revision Effort**: 8 hours (within Phase 1 budget)

### 6.2 M33 Mandate: CONDITIONAL GO

**Required**: 2-pass probe OR cross-validating verifier agent (both preferred)

### 6.3 M35 Mandate: CONDITIONAL GO

**Required**: `secrets-public.toml` recovery procedure + SPDX/REUSE enforcement + immediate remediation of redacted values

### 6.4 L3 Lesson: REVISE BEFORE CANONIZATION

**Required**: Split into two lessons, confidence 0.80/0.85, correct evidence error, add cross-references

---

## §7 HIVE MIND POST

**Intent**: `decision` — Meta-review complete. M34 spec needs revision (8h). M33/M35 conditional. L3 lesson needs split. Two incidents conflated — M34b required for model-switch continuity.

**Next**: Lilith self — revise M34 spec per §5.3 corrections. Grokster — split L3 lesson. Researcher/Jem — review revised spec. Kali — final ratification.

---

*⬡ OMEGA ⬡ LILITH ⬡ META-REVIEW-COMPLETE ⬡ 2026-08-30 ⬡*
*This meta-review is the final runtime gate before Sonnet 4.6. All findings are cited to specific lines in all three source reports.*