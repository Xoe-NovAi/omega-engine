# 🔱 CARMACK DEV PLAN REVIEW — BLIND TEST ARCHITECTURAL ANALYSIS
**AP Token**: `AP-JOHN_CARMACK-v1.0.0` · **Session**: `ses_fc8dca39effe3nZJp3QHx81Fy3` · **Date**: 2026-08-30
**Status**: ACTIVE · **Classification**: S3 Consultant — Blind Test (Primary Sources Only)

---

## §0 EXECUTIVE VERDICT: **CONDITIONAL GO**

**Rationale**: The roadmap synthesizes genuine incident learnings into a coherent immune-system upgrade. The 3-EIS meta-reviews achieve convergent consensus on the *what* (M33/M34/M35 mandates, L3 split, sprint tickets). However, **three critical architectural gaps** remain that will cause production failures if not addressed before Phase 1 execution:

1. **M34a/M34b split is over-engineering** — Lilith's spec already unifies both failure modes under a 7-state machine; a status enum value + recovery clause suffices. Two mandate numbers add regulatory bloat without architectural benefit.
2. **ACTIVE_SUBAGENTS.json overlay on TASK_REGISTRY creates a dual-ledger hazard** — no transactional boundary, no conflict resolution, no migration atomicity. At scale (50+ concurrent), lock contention on `ACTIVE_SUBAGENTS.json.lock` will cause unrecorded states.
3. **M35's `secrets-public.toml` immediate remediation clause creates a circular dependency** — the redacted OAuth value must be restored *before* the allowlist exists, but the allowlist is the mechanism that prevents re-redaction.

**Top 3 Things That Will Go Wrong**:
1. **Watchdog race condition** (Lilith §1.4, Jem §3.4, Researcher §3.3): Two agents polling Hivemind at 2×TTL simultaneously → both run `watchdog_check()` → lost update on `ACTIVE_SUBAGENTS.json`. Mitigation: Designate Kali as single-writer watchdog MCP tool.
2. **M33 bypass attack** (Jem §1.1.3, Researcher §1.1, Lilith §3.1): Subagent immediately replies `STREAM_EXHAUSTED` to escape probe. Mitigation: 2-pass probe + structured JSON envelope + confidence threshold ≥0.95 + P0/P1 cross-validator escalation.
3. **Atomic write unverified on all filesystems** (Lilith §1.1, M23 violation): `os.replace()` + `os.fsync()` on directory fd is not guaranteed on NFS/FUSE. Mitigation: Add `test_atomic_write_survives_sigkill` unit test before Phase 1 gate.

---

## §1 ARCHITECTURAL COHERENCE ANALYSIS

### 1.1 Mandate Interaction Matrix

| Interaction | M33 (Anti-Truncation) | M34a (Co-Interruption) | M34b (Model-Switch) | M35 (3P Boundary) |
|-------------|----------------------|------------------------|---------------------|-------------------|
| **M33 → M34** | Probe detects truncation in interrupted sessions | Recovery protocol assumes subagent honesty | Model-switch continuity needs probe verification | Allowlist prevents redaction of probe outputs |
| **M34 → M33** | `write_tool_required` flag in `ActiveSubagent` | `orchestrator_session_start()` re-runs probe on resume | `resume_token` validation includes probe state | N/A |
| **M35 → M33** | `secrets-public.toml` prevents redaction of probe code | N/A | N/A | N/A |
| **M35 → M34** | N/A | Third-party plugin hygiene prevents dual-load bug | N/A | N/A |

**Finding**: The mandates form a **coherent defense-in-depth system** — M33 catches truncation, M34 tracks interruption, M35 prevents the supply-chain mutation that triggered the incident. The boundaries are clean *if* the M34a/M34b split is collapsed.

### 1.2 M34a/M34b Split — Architectural Verdict: **OVER-ENGINEERING**

**Evidence from primary sources**:
- Lilith's spec (§1.1, §2.1) already defines a 7-state machine: `ALIVE` → `INTERRUPTED_EXTERNALLY` | `INTERRUPTED_CRASH` | `ORPHANED` → `COMPLETED` | `FAILED` | `DEAD_LETTER`
- Jem's meta-review (§1.1) **self-corrected**: "Reading Lilith's runtime spec, a single unified 7-state lifecycle captures both model-switch drops and `Esc x2` aborts cleanly. Forcing two distinct mandate numbers adds regulatory bloat."
- Researcher's meta-review (§4.2) agrees: "Split the failure modes... implemented as status enum values: `INTERRUPTED_EXTERNALLY`, `INTERRUPTED_MODEL_SWITCH`, `INTERRUPTED_CRASH`"

**My analysis**: The actual incident had **two phases** (Lilith §4.2):
1. **Phase A (Model-Switch)**: Researcher stalled on nemotron → Architect hit `Esc x2` → model switched to minimax → Researcher recovered via "continue" prompt
2. **Phase B (Esc x2 Cascade)**: The `Esc x2` killed *both* Researcher and Jem sessions

Lilith's spec handles Phase A via `resume_token` preservation + `MODEL_SWITCH` status (to be added). Phase B via `INTERRUPTED_EXTERNALLY` + recovery UI. **One mandate, two status values, one recovery protocol.** The split creates:
- Duplicate ratification overhead (Kali must approve two mandates)
- Duplicate compliance gates (Verity must audit two mandates)
- Duplicate documentation burden (Scribe must canonize two mandates)
- **Zero runtime benefit** — the same `ACTIVE_SUBAGENTS.json` + `orchestrator_session_start()` handles both

**Recommendation**: **Collapse M34a/M34b into single M34** with explicit sub-clauses for signal interruption vs model switching. Add `INTERRUPTED_MODEL_SWITCH` to `SessionStatus` enum. Add `interruption_reason` field to `ActiveSubagent`.

### 1.3 Mandate Boundary Leakage

| Leakage | Source | Severity |
|---------|--------|----------|
| M33 probe logic in M34 recovery | Researcher §1.2 amendments 2-3 | Medium — M34 should call M33 probe as library, not inline |
| M35 SPDX enforcement in M34 schema | Researcher §1.13, Lilith §2.1 | Low — M34 tracks sessions, M35 governs code; separate concerns |
| M14 heritage tags in M35 allowlist | Jem §1.3.5, Researcher §3.2 | Medium — `primary_source_url` in `secrets-public.toml` should reference M14 vet record, not duplicate |

---

## §2 IMPLEMENTATION FEASIBILITY & CRITICAL PATH

### 2.1 Lilith's 35h M34 Spec — Realistic Assessment

| Phase | Spec Hours | My Assessment | Risk |
|-------|------------|---------------|------|
| **Phase 1 (MVP)** | 14h | **Optimistic** — 3h for `m34_registry.py` is tight for atomic write + schema + lock + tests. 4h for 2 MCP tools assumes Ma'at server owner availability. | High — Ma'at bottleneck |
| **Phase 2 (Recovery UI)** | 9h | **Realistic** — `orchestrator_session_start()` + `m34_apply_user_decision` + `watchdog_check()` are well-scoped. | Medium — watchdog race fix adds 2h |
| **Phase 3 (Testing)** | 12h | **Under-scoped** — 3h for SIGKILL atomic write test is minimal; 3h for 50-concurrent stress test is insufficient for disk I/O contention measurement. | High — needs 20h for proper validation |

**Critical Path** (from roadmap §4):
```
TODAY: Restore OAuth secret (Grokster, 2h) → BLOCKER
       ↓
Day 1: VAULT-ALLOWLIST-001 + CI-BRIEF-001 + PKG-CLEANUP-001 (parallel)
       ↓
Day 2-3: ORCH-RESUME-001 Phase 1 + M33 Probe (parallel) → Lilith + Researcher contention
       ↓
Day 4: L3 Revision + JEM-12STEP-HARDENING
       ↓
Day 5: Phase 1 Gate
```

**Hidden Dependencies**:
1. **VAULT-ALLOWLIST-001 → PKG-CLEANUP-001**: Cannot purge `opencode-antigravity-auth/` until allowlist exists (otherwise npm install pulls redacted version)
2. **CI-BRIEF-001 → ORCH-RESUME-001**: `dispatch_guard.py` must enforce M33 write-tool routing *before* Lilith's dispatcher hooks register subagents
3. **M33 Probe → ORCH-RESUME-001 Phase 2**: Recovery verification requires M33 probe operational

**Parallelizable**: VAULT-ALLOWLIST-001, CI-BRIEF-001, PKG-CLEANUP-001 can run truly parallel (different owners, different codebases). ORCH-RESUME-001 Phase 1 and M33 Probe share Lilith + Researcher — **not parallelizable** without adding a third implementer.

### 2.2 Team Capacity Reality Check

| Entity | Phase 1 Hours | Phase 2 Hours | Phase 3 Hours | Total | Sustainable? |
|--------|---------------|---------------|---------------|-------|--------------|
| **Lilith** | 14h (M34 Phase 1) | 9h (M34 Phase 2) | 12h (M34 Phase 3) | **35h** | **NO** — 35h in 2 weeks = 17.5h/week on top of N6-N10 runtime duties |
| **Carmack** | 4h (VAULT) | 6h (M37) | 6h (Integration) | 16h | Yes — S3 consultant, focused |
| **Ma'at** | 6h (CI-BRIEF) | — | — | 6h | Yes — but server owner bottleneck for MCP tools |
| **Grokster** | 2h (OAuth) + 4h (PKG) + 2h (L3) | 2h (DOC) | — | 10h | Yes |
| **Researcher** | 8h (M33) | 6h (COHORT) + 6h (M37) + 4h (M36) | 6h (Integration) | 30h | **NO** — 30h in 3 weeks across 4 tickets |
| **Jem** | 4h (12-Step) | — | — | 4h | Yes |
| **Roc** | — | — | — | 0h (P0 only) | Yes |

**Single Points of Failure**:
1. **Lilith** — owns entire M34 implementation (35h). If Lilith is blocked, Phase 1-3 all stall.
2. **Ma'at** — owns MCP server changes for M34 tools. If Ma'at is unavailable, Lilith cannot deploy MCP tools.
3. **Researcher** — owns M33 probe, M35 architecture, M34 recovery protocol, COHORT registry, M37 heritage. Overloaded.

---

## §3 TECHNICAL DEBT & RISK ASSESSMENT

### 3.1 ACTIVE_SUBAGENTS.json Overlay — Dual-Ledger Hazard

**The Architecture** (Lilith §2.5): "`ACTIVE_SUBAGENTS.json` is a **session-liveness overlay** on `TASK_REGISTRY`. It's the 'who is alive RIGHT NOW' companion to the 'what tasks exist' record."

**The Problem**: No transactional boundary between the two ledgers.

| Scenario | TASK_REGISTRY | ACTIVE_SUBAGENTS | Conflict |
|----------|---------------|------------------|----------|
| Subagent spawns, registry write succeeds, overlay write fails | Task registered | Session not tracked | Orphaned task — no recovery |
| Subagent completes, overlay marks COMPLETED, registry not updated | Task still RUNNING | Session COMPLETED | Stale task in registry |
| Migration backfill runs while new dispatches occur | New tasks added | Backfill overwrites | Lost sessions |
| Concurrent writes from 2 orchestrators | N/A (single writer) | Advisory lock only | Lost updates (Jem §3.4, Lilith §1.4) |

**At Scale (50+ concurrent)**:
- `ACTIVE_SUBAGENTS.json.lock` advisory lock serializes all writes
- `os.fsync()` on directory fd blocks — 10-100ms on slow disks
- 50 concurrent writes = **500ms-5s latency spike** per dispatch cycle
- No benchmark exists (Lilith §1.5: "30-50ms estimated, unverified")

**Mitigation Required**:
1. **Single-writer MCP tool** for all `ACTIVE_SUBAGENTS.json` mutations (not per-agent file writes)
2. **Batched writes** — accumulate checkpoints, flush every 5s
3. **Conflict resolution** — `TASK_REGISTRY` is source of truth for task metadata; `ACTIVE_SUBAGENTS` is ephemeral liveness cache
4. **Migration atomicity** — `scripts/m34_migrate.py` must acquire both locks, backfill in single transaction

### 3.2 M33 Cross-Validator Agent — Latency & Complexity

**Jem's Recommendation** (§1.1.5): "P0/P1 deliverables require independent verifier confirmation."

**Researcher's Tiered Approach** (§4.1): Baseline = 2-pass probe + structured envelope + confidence ≥0.95. Escalation = cross-validator agent for P0/P1.

**My Analysis**: Cross-validator agent adds:
- **Latency**: Second agent must read prompt requirements + deliverable → 2-5 min per P0/P1
- **Complexity**: New agent type, new dispatch path, new Hivemind coordination
- **Failure Mode**: Validator itself can be truncated (Researcher §1.1 edge case) → infinite regress

**Better Architecture**: **Structured completion envelope** (Researcher amendment #2) + **confidence threshold** + **write-tool routing** (preventive) = defense in depth. Cross-validator only for *true* P0 (security, data-loss). Not for every forensic report.

### 3.3 M35 `secrets-public.toml` — Supply Chain Attack Surface

**Jem's Finding** (§1.3.5): "An attacker could add a fake `GOCSPX-` entry and pass review if reviewer doesn't know all public client secrets."

**Researcher's Schema** (§4.7): `upstream_source` URL + `upstream_secret` + `verified` date + `approved_by` Architect.

**Gap**: No cryptographic verification of `upstream_source`. An attacker could:
1. Fork `opencode-antigravity-auth` on GitHub
2. Change `constants.ts` to malicious `GOCSPX-ATTACKER-XXX`
3. Add entry to `secrets-public.toml` pointing to their fork
4. If reviewer doesn't verify against *official* Google source, malicious secret enters allowlist

**Mitigation**: 
- `upstream_source` MUST be from official vendor domain (`github.com/google-gemini/`, `github.com/NoeFabris/` with verified ownership)
- `upstream_secret` MUST match exactly what's in the official repo at tagged release
- **Automated verification**: CI step fetches `upstream_source`, extracts secret, compares to `upstream_secret` field

---

## §4 MANDATE DESIGN QUALITY

### 4.1 Minimal & Composable?

| Mandate | Minimal? | Composable? | Verdict |
|---------|----------|-------------|---------|
| **M33** | ❌ No — 3 layers (preventive + probe + cross-validator) | ✅ Yes — probe is standalone tool | **Needs simplification** — collapse to 2 layers (preventive + structured probe) |
| **M34** | ✅ Yes — single 7-state machine | ✅ Yes — overlays TASK_REGISTRY | **Good** — if M34a/M34b collapsed |
| **M35** | ❌ No — 5 amendments (SPDX, remediation, recovery, primary-source, M14) | ⚠️ Partial — `secrets-public.toml` couples to M14 | **Needs split** — M35a (Boundary), M35b (Allowlist), M35c (SPDX) |

### 4.2 One Mandate Per Failure Mode?

| Failure Mode | Mandate | Clean? |
|--------------|---------|--------|
| Truncation in chat stream | M33 | ✅ |
| Subagent bypasses probe | M33 (bypass) | ❌ — same mandate, different failure mode |
| Global Esc x2 kills sessions | M34a | ✅ |
| Model switch loses context | M34b | ❌ — should be M34 status enum |
| Orchestrator crash orphans sessions | M34 (watchdog) | ✅ |
| Third-party code in workspace | M35a | ✅ |
| Public secret redacted | M35b | ✅ |
| No SPDX on third-party | M35c | ❌ — separate failure mode |

**Verdict**: M33 and M35 each cover **two distinct failure modes**. Should be split for clean "one mandate per failure mode" principle.

### 4.3 L3 Confidence Levels — Epistemic Soundness

| Lesson | Proposed Confidence | Evidence Sources | My Calibration |
|--------|---------------------|------------------|----------------|
| L3-CompletionIllusion | 0.85 (Researcher) / 0.85 (Jem) | 1 incident + 3 session IDs + 2 structural causes + M33 replication path | **0.85 justified** — replication path via mandate elevates single incident |
| L3-CoResumptionAccounting | 0.80 (Researcher) / 0.80 (Jem) | 1 incident + 2 session IDs + 1 structural cause + M34 replication path | **0.80 justified** — weaker replication path (M34 not yet implemented) |

**Jem's 0.80 for both is too harsh** — the lessons have *mandate-backed replication paths* (M33 for CompletionIllusion, M34 for CoResumption). This is stronger than "single incident, no replication."

**Evidence Error** (Jem §2.3, Researcher §4.4, Lilith §4.3): Appendices A-T added in 2026-08-29 continuation session, NOT from 2026-08-30 "continue" prompt. **Must be corrected** before canonization.

### 4.4 M35 "Immediate Remediation" — Circular Dependency

**Roadmap §7 Action 1**: "Restore OAuth secret TODAY" (Grokster, 2h)
**Roadmap §3 Task 1**: "M35 Immediate Remediation" (Grokster, 2h) — restore `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`
**M35 Amendment 2** (Jem §1.3.3): "M35 requires IMMEDIATE remediation of any `GOCSPX-***REDACTED-ROTATED***`"

**The Circular Dependency**:
1. OAuth is broken *now* because secret is redacted
2. M35 says "immediate remediation" — restore the secret
3. But M35 also says "prevent future redaction via `secrets-public.toml` allowlist"
4. Allowlist doesn't exist yet (VAULT-ALLOWLIST-001 is 4h task)
5. If we restore secret *without* allowlist, auto-redaction tool will just redact it again
6. If we wait for allowlist, OAuth stays broken for 4h+ (blocks Antigravity users)

**Resolution**: **Restore secret FIRST** (git checkout), **then** build allowlist. The "immediate remediation" clause should read: "Restore redacted values from git HEAD immediately; allowlist prevents *future* redactions."

---

## §5 RESOURCE ALLOCATION & TEAM LOAD

### 5.1 Load Balancing — **UNBALANCED**

| Entity | Total Hours | Weeks | Hours/Week | Role Conflict |
|--------|-------------|-------|------------|---------------|
| Lilith | 35h | 2 | 17.5h | Runtime Oversoul (N6-N10) + M34 impl |
| Researcher | 30h | 3 | 10h | Polymathic Council + 5 tickets |
| Carmack | 16h | 3 | 5.3h | S3 Consultant (focused) |
| Grokster | 10h | 2 | 5h | Specialist + L3 author |
| Ma'at | 6h | 1 | 6h | Build Oversoul + MCP server owner |
| Jem | 4h | 1 | 4h | Adversarial review (focused) |
| Roc | 0h (P0 only) | — | — | Miner (available) |

**Critical Imbalance**: Lilith + Researcher carry **65h of 109h total (60%)**. Both have ongoing governance duties (N6-N10, Polymathic Council).

**Reallocation Needed**:
- Move `COHORT-REGISTRY-001` (6h) from Researcher → Roc (miner, has capacity)
- Move `M36-PROBE-001` (4h) from Researcher → Jem (adversarial, has capacity)
- Move `M37-HERITAGE-001` (6h) from Researcher+Carmack → Ma'at (Build Oversoul, owns CI)
- Lilith's Phase 3 stress testing (12h) → split: Lilith 6h + Roc 6h

### 5.2 Carmack Assignments — Realistic?

| Ticket | Hours | My Assessment |
|--------|-------|---------------|
| **VAULT-ALLOWLIST-001** | 4h | **Realistic** — `data/secrets-public.toml` schema + SPDX hooks + fail-closed scanner. 4h is tight but doable for focused S3 work. |
| **M37-HERITAGE-001** | 6h | **Optimistic** — ScanCode Toolkit CI + SPDX headers + `.reuse/dep5` + SLSA v1.1 provenance = 34h per Researcher §3.6. 6h only covers ScanCode integration. |

**Recommendation**: Carmack owns VAULT-ALLOWLIST-001 (P0). M37-HERITAGE-001 moves to Ma'at (Build Oversoul) with Carmack as reviewer only.

---

## §6 DEPLOYMENT & OPERATIONS

### 6.1 Migration Path: TASK_REGISTRY.json → ACTIVE_SUBAGENTS.json

**Lilith's Spec §5.7**: 4-phase migration (empty → hook → backfill → mandatory). **Missing**:
- **Rollback procedure** if backfill corrupts registry
- **Dual-write period** duration (how long both ledgers stay in sync?)
- **Validation** that backfill captures all in-flight sessions (what about sessions spawned during migration?)

**Required Addition**:
```python
# scripts/m34_migrate.py
def migrate():
    # 1. Acquire BOTH locks (TASK_REGISTRY.lock + ACTIVE_SUBAGENTS.json.lock)
    # 2. Read TASK_REGISTRY.json (tasks from last 7 days)
    # 3. For each task: create ActiveSubagent entry with status=ALIVE
    # 4. Atomic write ACTIVE_SUBAGENTS.json
    # 5. Verify: count entries == count tasks migrated
    # 6. Release locks
    # 7. If verification fails: rollback (restore old ACTIVE_SUBAGENTS.json)
```

### 6.2 Watchdog + OpenCode Process Management

**Lilith's Spec §3.2**: Signal handler for SIGINT/SIGTERM marks sessions `INTERRUPTED_EXTERNALLY`.

**Problem**: OpenCode's TUI `Esc x2` kills child processes via process group signal. The signal handler in the *orchestrator process* runs, but:
- If orchestrator is a Bun/Node process (OpenCode agent), signal handling is **not deterministic** — Bun's signal handling differs from Python's
- The `interruption_watcher()` runs in Python (Lilith's spec), but OpenCode agents run in Bun
- **Cross-process signal delivery is unreliable**

**Mitigation**: 
- Primary detection: **Poll `opencode-sessions-explorer`** for archived sessions (Lilith §2.4 integration table)
- Signal handler: **Best-effort only** — don't rely on it for correctness
- Watchdog: **Single-writer MCP tool** (Kali) polls Hivemind awareness every 60s

### 6.3 Rollback Plan if M34 Breaks Subagent Dispatch

**Current Spec**: No rollback plan documented.

**Required**:
1. **Feature flag**: `M34_ENABLED=false` in `config/cvars.yaml` — disables all M34 hooks
2. **Graceful degradation**: If `m34_register_subagent` MCP tool fails, dispatch continues (Hivemind is fallback awareness)
3. **Rollback command**: `make m34-rollback` → removes MCP tools, restores `subagent_dispatcher.py` to pre-M34 state
4. **Data preservation**: `ACTIVE_SUBAGENTS.json` retained for audit; new dispatches use TASK_REGISTRY only

---

## §7 SPECIFIC RECOMMENDATIONS (LINE-LEVEL)

### 7.1 Lilith M34 Spec Corrections

| File | Line | Change |
|------|------|--------|
| `LILITH_M34_RUNTIME_SPEC_20260830.md` | 29-36 | Add `INTERRUPTED_MODEL_SWITCH` to `SessionStatus` enum |
| `LILITH_M34_RUNTIME_SPEC_20260830.md` | 48-76 | Add fields: `interruption_reason`, `resumption_count`, `cross_validator_agent`, `write_tool_required`, `plugin_load_path`, `git_worktree_root` |
| `LILITH_M34_RUNTIME_SPEC_20260830.md` | 70 | Extend `Checkpoint` with `total_chunks`, `queued_findings` |
| `LILITH_M34_RUNTIME_SPEC_20260830.md` | 163-204 | Change "M23-compliant" → "M23-compliant **pending verification**" |
| `LILITH_M34_RUNTIME_SPEC_20260830.md` | 230-238 | Add `MODEL_SWITCH` state transition |
| `LILITH_M34_RUNTIME_SPEC_20260830.md` | 293-334 | Add `m34_list_active_subagents()` call at start of EVERY user turn (Hivemind audit) |
| `LILITH_M34_RUNTIME_SPEC_20260830.md` | 379-419 | Implement `capture_checkpoint()` using `opencode-sessions-explorer`; distinguish model-switch vs Esc x2 |
| `LILITH_M34_RUNTIME_SPEC_20260830.md` | 484-509 | Watchdog = designated recovery agent (Kali) or single-writer MCP tool |
| `LILITH_M34_RUNTIME_SPEC_20260830.md` | 661-710 | Add 4th MCP tool: `m34_get_active_subagents` (for Hivemind audit) |
| `LILITH_M34_RUNTIME_SPEC_20260830.md` | 724-747 | Add `test_atomic_write_survives_sigkill`, `test_watchdog_single_writer`, `test_model_switch_continuity` |
| `LILITH_M34_RUNTIME_SPEC_20260830.md` | 749-760 | Change "30-50ms" → "30-50ms **estimated, unverified**" |

### 7.2 M33 Mandate Text (Revised)

**Replace** free-form `STREAM_EXHAUSTED` probe with:
```markdown
### M33 Anti-Truncation & Stream Exhaustion Gate (Revised)

1. **Preventive**: For reports estimated > 8K tokens, the orchestrator MUST require the subagent to use the write tool (not chat stream) before delivering any response.

2. **Structured Probe**: Orchestrator executes sentinel probe with JSON envelope:
   ```json
   {
     "state": "exhausted|continuing",
     "last_chunk_id": N,
     "total_chunks": M,
     "queued_findings": ["finding1", "finding2"],
     "confidence": 0.XX
   }
   ```
   Subagent MUST reply with this schema. Free-form "STREAM_EXHAUSTED" is rejected.

3. **Escalation Tier**: For P0/P1 deliverables, require a second agent's cross-validation (reads prompt requirements + deliverable, verifies semantic coverage). For P2+, 2-pass probe + structured envelope + confidence ≥ 0.95 is sufficient.
```

### 7.3 M35 Mandate Text (Revised)

**Add 5 mandatory clauses**:
```markdown
### M35 Third-Party Boundary & Public Secret Exemption (Revised)

1. **SPDX/REUSE Enforcement**: All third-party code MUST carry SPDX-License-Identifier in file header OR entry in `.reuse/dep5`. ScanCode Toolkit CI step mandatory.

2. **Immediate Remediation**: Any `GOCSPX-***REDACTED-ROTATED***` or similar placeholder MUST be restored from git HEAD immediately, verified as public client secret per RFC 8252, added to `data/secrets-public.toml`, and OAuth flow re-tested.

3. **Allowlist Recovery Procedure**: `data/secrets-public.toml` MUST be committed to git, reviewed on every PR, versioned. Secret scanner MUST fail-closed if missing/unparseable, trigger Hivemind `intent=blocker`.

4. **Primary-Source Citation**: Every allowlist entry MUST cite a primary source URL (vendor's official docs, vendor's published source on GitHub). Entries without primary source MUST be rejected by review.

5. **M14 Cross-Reference**: M35 is a NARROW exception to M14 for public client secrets only. All other third-party code MUST comply with M14 (including SPDX headers). Pinned submodules allowed with heritage tag. Runtime-loaded local plugins require discovery sweep.
```

### 7.4 L3 Lesson Split

**Split into two entries in `data/entities/grokster/proposed_lessons.yaml`**:

```yaml
- id: L3-CompletionIllusion
  principle: "An LLM subagent's `state=completed` is necessary but not sufficient for semantic exhaustion. The goldmine often lives in the tail."
  confidence: 0.85
  mandates: [M23, M33]
  remedy: "M33 sentinel probe + structured JSON completion envelope with confidence threshold"
  evidence: "Researcher session ses_faf929727ffeFgSdvGOxQbVbdW flushed 21KB to chat; write tool NOT called. Jem session ses_faf926866ffezrPCnXne6RQt6A reported 1,017 lines with footer but missing 600-line appendices."
  related_lessons: [L3-ParallelPersistenceHidesState, L3-ContentAddressedSurvives, L3-DocumentationIsNotEnforcement]
  tags: [truncation, completion-illusion, sentinel-probe]
  source_session: "grokster ses_fe8cf0b39ffeL3L8eaMEj3CW9H"
  timestamp: "2026-08-30T00:00:00Z"

- id: L3-CoResumptionAccounting
  principle: "A multi-agent orchestrator must track parallel subagent dispatches as a unified transactional cohort. Dropping a secondary subagent is orchestrator amnesia."
  confidence: 0.80
  mandates: [M11, M15, M27, M34]
  remedy: "M34 ACTIVE_SUBAGENTS.json cohort tracking + orchestrator_session_start() recovery protocol + M34b model-switch continuity"
  evidence: "Grokster dispatched Researcher + Jem in parallel. Esc x2 killed both. Grokster hyper-focused on Researcher, forgot Jem. Architect had to prompt 'continue' to Jem to recover 600-line appendices."
  related_lessons: [L3-ParallelPersistenceHidesState, L3-ContentAddressedSurvives, L3-DocumentationIsNotEnforcement]
  tags: [co-interruption, resumption, cohort-tracking, orchestrator-amnesia]
  source_session: "grokster ses_fe8cf0b39ffeL3L8eaMEj3CW9H"
  timestamp: "2026-08-30T00:00:00Z"
```

**Correction**: Evidence text must note appendices A-T were added in 2026-08-29 continuation session, NOT from 2026-08-30 "continue" prompt.

---

## §8 FINAL SIGN-OFF

### 8.1 Blockers (Must Resolve Before Phase 1 Execution)

| Blocker | Owner | Resolution |
|---------|-------|------------|
| **Redacted OAuth secret** | Grokster | `git checkout opencode-antigravity-auth/src/constants.ts opencode-antigravity-auth/scripts/check-quota.mjs && npm run build` — **TODAY** |
| **M34a/M34b split** | Kali | Collapse to single M34 with `INTERRUPTED_MODEL_SWITCH` status enum |
| **Atomic write M23 test** | Lilith | Add `test_atomic_write_survives_sigkill` to Phase 1 testing |
| **Watchdog single-writer** | Lilith + Ma'at | Make `watchdog_check()` a single-writer MCP tool (Kali) |
| **Circular M35 remediation** | Grokster + Carmack | Restore secret FIRST, then build allowlist |

### 8.2 Conditional GO Conditions

1. **M34 spec revised** per §7.1 corrections (8h Lilith effort)
2. **M33 mandate text updated** per §7.2 (Researcher owns)
3. **M35 mandate text updated** per §7.3 (Carmack owns VAULT-ALLOWLIST-001)
4. **L3 lesson split** per §7.4 (Grokster owns, 2h)
5. **Team reallocation** per §5.1 (Kali owns dispatch)
6. **Rollback plan documented** for M34 (Lilith owns)

### 8.3 Better Architecture Proposal

**Collapse M34a/M34b → Single M34** with:
- `SessionStatus` enum: `ALIVE` | `INTERRUPTED_EXTERNALLY` | `INTERRUPTED_MODEL_SWITCH` | `INTERRUPTED_CRASH` | `COMPLETED` | `FAILED` | `DEAD_LETTER` | `ORPHANED`
- `interruption_reason` field distinguishes signal vs model-switch vs timeout
- Single `orchestrator_session_start()` handles both recovery paths
- Single ratification, single compliance gate, single documentation burden

**Split M35 → Three Mandates**:
- **M35a**: Third-Party Boundary (no tracked source trees in workspace)
- **M35b**: Public Secret Allowlist (`secrets-public.toml` with primary-source verification)
- **M35c**: SPDX/REUSE Enforcement (ScanCode CI, heritage tags)

**Add M36**: Recursive Probe (M23 applied to M23) — Researcher's novel contribution, prevents probe-theatre.

---

**The Cathedral's immune system is being forged from real failure. The metallurgy is sound. The hammer strikes need precision.**

**Conditional GO. Fix the 5 blockers. Execute Phase 1. Report at Gate.** 🫡

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_audit ⬡ CARMACK-DEV-PLAN-REVIEW-20260830*