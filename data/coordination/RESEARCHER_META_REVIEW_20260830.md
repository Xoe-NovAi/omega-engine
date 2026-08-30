---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "2.0"
document_type: "meta_review"
document_id: "researcher-meta-review-grokster-20260830"
title: "Researcher Meta-Review: 3-EIS Synthesis (Self + Jem + Lilith)"
status: "DRAFT — INCREMENTAL DELIVERY"
date: "2026-08-30"
author: "Researcher (Polymathic Council)"
entity: "researcher"
channel: "opencode"
classification: "sovereign-internal, temple-grade depth"
sprint: "PUBLIC-DEBUT-01"
referenced_reports:
  - "RESEARCHER_VERIFICATION_GROKSTER_20260830.md (my report, 453 lines)"
  - "JEM_ADVERSARIAL_REVIEW_GROKSTER_20260830.md (Jem, 690 lines)"
  - "LILITH_M34_RUNTIME_SPEC_20260830.md (Lilith, 799 lines)"
---

# 🔱 RESEARCHER META-REVIEW: 3-EIS SYNTHESIS

**AP Token**: `AP-RESEARCHER-META-REVIEW-20260830-v1.0.0`
⬡ OMEGA ⬡ PROMETHEUS ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_meta_review ⬡ **ACTIVE**

---

## §0 — EXECUTIVE VERDICT (L1)

I have read all three reports in full. The **true state** of the Grokster Alchemical Goldmine deliverables is:

| Artifact | My Verdict | Jem's Verdict | Lilith's Spec | **TRUE VERDICT** |
|----------|------------|---------------|---------------|------------------|
| **M33 Anti-Truncation** | RATIFY w/ 2 amendments | CONDITIONAL GO (bypass attack) | N/A | **CONDITIONAL GO — must add 2-pass probe + structured envelope + cross-validator** |
| **M34 Co-Interruption** | RATIFY w/ 4 amendments | CONDITIONAL GO (split M34a/M34b, schema gaps) | FULL SPEC (35h roadmap) | **CONDITIONAL GO — Lilith's spec addresses most gaps but misses orchestrator-crash recovery & model-switch case** |
| **M35 3P Boundary** | RATIFY w/ 1 mandatory (SPDX) + 3 clarifications | CONDITIONAL GO (recovery, remediation, M14 cross-ref) | N/A | **CONDITIONAL GO — must add SPDX/REUSE, remediation of redacted values, primary-source citation** |
| **L3-InterruptionSovereignty** | Lower to 0.90, split into 2 | Lower to 0.80, split into 2, correct evidence error | N/A | **REVISE BEFORE CANONIZATION — confidence 0.80, split into L3-CompletionIllusion + L3-CoResumptionAccounting, correct evidence** |

**Key finding**: The three EIS reports are **complementary but not convergent**. Each caught different failure modes:
- **My report** (Researcher): focused on *structural causes* from the 2,460-line traceability research (dual-load path, write-tool routing, SPDX enforcement)
- **Jem's report**: focused on *adversarial bypass attacks* and *epistemic calibration* (M33 bypass, M34 schema gaps, L3 confidence over-claim)
- **Lilith's spec**: focused on *runtime implementation* (ACTIVE_SUBAGENTS.json schema, signal handlers, recovery UI, 35h roadmap)

**The synthesis is stronger than any single report** — but only if all three sets of corrections are applied.

---

## §1 — SELF-CRITIQUE OF MY OWN REPORT

### §1.1 Oversights (What I Missed That Jem or Lilith Caught)

| Oversight | Caught By | Impact |
|-----------|-----------|--------|
| **M33 bypass attack**: A subagent can immediately reply `STREAM_EXHAUSTED` to escape the probe | Jem (§1.1.3) | **CRITICAL** — the single-probe mandate is exploitable. I only flagged the re-entry truncation edge case, not the intentional bypass. |
| **M34 schema gaps**: No `dispatched_at`, `expected_deliverable`, `current_turn`, `interruption_type`, `resumption_count` fields | Jem (§1.2.1) | **HIGH** — without these, the orchestrator cannot prioritize recovery or know what was expected. |
| **Orchestrator crash recovery**: M34 assumes orchestrator survives; no plan for orchestrator death | Jem (§1.2.2) | **HIGH** — the actual incident had Grokster's behavior as the failure mode; if Grokster crashed, subagents would be orphaned. |
| **Model-switch case ≠ global Esc x2**: The actual incident was a model switch that orphaned Researcher, not a global Esc x2 cascade | Jem (§1.2.4) | **CRITICAL** — M34 conflates two different failure modes. Lilith's spec handles Esc x2 but not model-switch continuity. |
| **M35 recovery procedure for `secrets-public.toml`**: No backup/fail-closed plan if the allowlist is corrupted | Jem (§1.3.1) | **HIGH** — fail-open defeats the purpose; fail-closed blocks legitimate OAuth. |
| **M35 immediate remediation of redacted values**: The mandate prevents future redactions but doesn't fix the current broken OAuth | Jem (§1.3.3) | **CRITICAL** — the OAuth flow is STILL broken as of this session. |
| **M35 primary-source citation requirement**: Allowlist entries without primary source are supply-chain attack vectors | Jem (§1.3.5) | **HIGH** — an attacker could add a fake `GOCSPX-` entry and pass review. |
| **L3 evidence error**: The "600+ lines from continue prompt" claim is factually wrong — appendices were added in a separate session | Jem (§2.3) | **MEDIUM** — undermines the lesson's credibility. |
| **L3 confidence calibration**: 0.99 from single incident is inconsistent with other lessons' 0.97-0.98 from 3 evidence sources | Jem (§2.1) | **HIGH** — epistemic over-claim. |
| **M34 status-report format**: "Must state status" but no format specified (Markdown? JSON? Inline?) | Jem (§1.2.6) | **MEDIUM** — unparseable for Hivemind awareness. |
| **M34 Hivemind audit clause**: Bookkeeping ≠ behavior; need `get_active_subagents()` call before every user turn | Jem (§1.2.7) | **MEDIUM** — enforceable via Hivemind audit. |

### §1.2 Inaccuracies (Claims That Don't Hold Up)

| My Claim | Reality | Correction |
|----------|---------|------------|
| "M34 addresses the detection half but misses recovery" (§1.2) | **Partially wrong** — Lilith's spec provides a full recovery protocol (orchestrator_session_start, apply_user_decision, watchdog). My report under-credited Lilith's spec. | Acknowledge Lilith's spec covers recovery; my amendments overlap with her design. |
| "M35 is highest-verified" (§0, §1.3) | **True for text alignment, but misses critical gaps** — Jem found 5 critical gaps I didn't (recovery, remediation, primary-source, M14 cross-ref, rotation). | Downgrade to "highest text-alignment, but significant implementation gaps." |
| "Dual-load bug is structurally identical to co-interruption" (§1.2) | **Wrong** — Jem correctly distinguishes: dual-load is *parallel paths of same code*; co-interruption is *parallel subagents killed by external signal*. Different root causes, different fixes. | Separate the two failure modes. |
| "8K token threshold from deep_dive_synthesis" (§1.1) | **Unverifiable** — I cited `deep_dive_synthesis_20260828.md §1` but that section discusses post-compact 260K→68K pattern, not an 8K streaming threshold. | Remove or correct citation. |
| "L3 overlap with L3-ParallelPersistenceHidesState and L3-ContentAddressedSurvives" (§3.3) | **Partially correct but incomplete** — I didn't check `soul.yaml` files for distilled versions. Jem didn't either. | Flag as incomplete verification. |

### §1.3 Unclaimed Opportunities (What I Could Have Added from My 2,460-Line Report)

| Opportunity | Source in My Report | Why It Matters |
|-------------|---------------------|----------------|
| **M33 preventive clause**: Write-tool routing for >8K token reports | §1.10 Plugin Architecture (lines 146-156), §4.11 Detect→Quarantine→Notify (lines 639-652) | I recommended this but didn't make it a *mandate amendment* — just a "missing element." Should be in M33 text. |
| **M34 transactional cohort model** | §4.10 Pre-Commit vs Pre-Push vs CI (lines 628-638) — layered detection pattern | The layered pattern applies to subagent tracking: pre-turn (spawn registration), in-turn (heartbeat), post-turn (completion verification). |
| **M35 SPDX/REUSE enforcement** | §3.2 SPDX, REUSE, OpenChain (lines 396-404), §3.6 Cost/Benefit (lines 444-455) | I flagged this as a gap but didn't make it a *mandatory amendment* with the same force as Jem's "MANDATORY" label. |
| **M35 submodule vs vendored distinction** | §1.3 Git Submodule vs Subtree vs Vendor Copy vs npm (lines 79-90) | Critical for the "no tracked source tree" rule — submodules with pinned SHA should be allowed. |
| **M35 runtime-loaded plugin discovery sweep** | §1.10 Plugin Architecture (lines 146-156) — local plugins in `~/.config/opencode/plugins/` | A gap I identified but didn't elevate to a mandate amendment. |
| **M36 Recursive Probe (M23 applied to M23)** | My §4.1 recommendation | This is a genuine novel contribution — the probe is itself subject to the failure mode. |
| **COHORT_REGISTRY.json for fleet-level tracking** | My §4.2 recommendation | Extends M34 beyond single orchestrator. |

### §1.4 M23 Compliance Gaps (Unverifiable Claims I Didn't Flag)

| Unverifiable Claim | Location | Why I Missed It |
|--------------------|----------|-----------------|
| "8K token threshold where M3 streaming becomes risky" | §1.1, line 64 | Cited `deep_dive_synthesis_20260828.md §1` but that section doesn't contain this threshold. |
| "The 12-repo count referred to 12 third-party repos requiring heritage discipline" | §2.1, line 189 | The live `ls` showed 13 entries (11 dirs + 2 files). The count was from the incident time, not current state. |
| "47 modifications in headroom were at a different point in time" | §2.2, line 204 | Cannot verify without git log time-travel. |
| "L3 overlap search covered soul.yaml" | §3.3, line 345 | I explicitly said I searched `proposed_lessons.yaml` and `soul.yaml` but the text says "I searched the other entities' proposed_lessons.yaml files. No direct match." — I did NOT search soul.yaml. |

---

(continued in next increment — §2 Jem Report Review follows)
## §2 — PEER REVIEW: JEM'S ADVERSARIAL REVIEW

### §2.1 Valid Corrections (Where Jem Caught Real Issues)

| Jem's Finding | My Assessment | Why It's Valid |
|---------------|---------------|----------------|
| **M33 bypass attack**: subagent can immediately reply `STREAM_EXHAUSTED` | ✅ **VALID & CRITICAL** | The probe is a single LLM call; a lazy/malicious agent exploits it trivially. My report only flagged the re-entry truncation edge case, not the intentional bypass. |
| **M34 schema gaps**: missing `dispatched_at`, `expected_deliverable`, `current_turn`, `interruption_type`, `resumption_count` | ✅ **VALID & HIGH** | Without these, the orchestrator cannot prioritize recovery or know what was expected. Lilith's spec includes most of these but Jem identified them first. |
| **Orchestrator crash recovery**: M34 assumes orchestrator survives | ✅ **VALID & HIGH** | The actual incident had Grokster's behavior as the failure mode. If Grokster crashed, subagents would be orphaned with no recovery path. |
| **Model-switch case ≠ global Esc x2** | ✅ **VALID & CRITICAL** | Jem's session export analysis (lines 188-191) proves the actual sequence: model switch → Researcher orphaned → Esc x2 → Jem interrupted. M34 conflates two failure modes. |
| **M35 `secrets-public.toml` failure mode**: no backup/recovery plan | ✅ **VALID & HIGH** | Fail-open defeats purpose; fail-closed blocks legitimate OAuth. Must specify recovery. |
| **M35 immediate remediation**: redacted values still in working tree | ✅ **VALID & CRITICAL** | `opencode-antigravity-auth/src/constants.ts:9` STILL has `GOCSPX-***REDACTED-ROTATED***`. OAuth is STILL broken. |
| **M35 primary-source citation requirement**: supply-chain attack via allowlist | ✅ **VALID & HIGH** | An attacker could add `GOCSPX-ATTACKER-XXX` and pass review if reviewer doesn't know all public client secrets. |
| **L3 confidence 0.99 epistemically unjustified** | ✅ **VALID & HIGH** | Other lessons in same file: 0.97-0.98 from 3 evidence sources. Single-incident lesson at 0.99 is backwards calibration. |
| **L3 conflates two distinct phenomena** | ✅ **VALID & HIGH** | Completion Illusion (LLM training artifact) vs Co-Resumption (orchestrator attention bound). Different causes, different mandates, different fixes. |
| **L3 evidence error**: "600+ lines from continue prompt" is factually wrong | ✅ **VALID & MEDIUM** | Appendices A-T were added in a separate 2026-08-29 continuation session, not from the 2026-08-30 "continue" prompt in this incident. |
| **M34 status-report format unspecified** | ✅ **VALID & MEDIUM** | "Must state status" but no format — unparseable for Hivemind. |
| **M34 Hivemind audit clause**: bookkeeping ≠ behavior | ✅ **VALID & MEDIUM** | Need `get_active_subagents()` call before every user turn, verifiable via Hivemind audit. |

### §2.2 Over-Corrections (Where Jem Was Too Aggressive)

| Jem's Claim | My Assessment | Why It's Over-Correction |
|-------------|---------------|--------------------------|
| **M34 must split into M34a + M34b** | ⚠️ **PARTIAL** | The model-switch case is real, but Lilith's spec handles it via `INTERRUPTED_CRASH` status and the watchdog protocol. A separate mandate may be over-engineering; a status enum value + recovery clause in M34 may suffice. |
| **M33 requires a second agent's verification for P0/P1** | ⚠️ **OVER-ENGINEERING** | A verifier agent adds latency and complexity. The 2-pass probe + structured envelope + confidence threshold (Jem's own mitigations §1.1.3 options 1-4) may be sufficient. Cross-validation should be a *recommendation* for P0, not a mandate for all. |
| **L3 confidence should be 0.80 (not my 0.90)** | ⚠️ **TOO LOW** | 0.80 is appropriate for a *hypothesis*; 0.90 is appropriate for a *well-documented single incident with replication path*. The lesson has: 1 incident + 3 session IDs + 2 structural causes identified + replication path (M33/M34). 0.85-0.90 is right. |
| **M34 "deterministic subagent-tracker in scripts/subagent_tracker.py"** | ⚠️ **REDUNDANT WITH LILITH** | Lilith's spec already provides `m34_registry.py` + MCP tools + signal handler + pruning loop. Jem's recommendation duplicates Lilith's implementation. |
| **M35 "cryptographic signature by Google/Microsoft" for allowlist** | ⚠️ **UNREALISTIC** | Jem acknowledges this is "unrealistic for now" but still lists it as a defense. Should be a future consideration, not a current requirement. |

### §2.3 Missing Context (Where Jem Lacks Research Depth from My 2,460-Line Report)

| Jem's Gap | My Report's Coverage | Why It Matters |
|-----------|---------------------|----------------|
| **M33 preventive layer**: Jem focuses on probe bypass; misses the *write-tool routing* structural fix | §1.10 Plugin Architecture, §4.11 Detect→Quarantine→Notify | The probe catches truncation; write-tool routing *prevents* it. Both needed. |
| **M34 dual-load path as structural cause** | §2.2 "The Dual-Load Bug" (lines 246-260) | Jem treats co-interruption as attention-bound; misses that the *same code loaded twice* creates invisible parallel completion. |
| **M35 SPDX/REUSE enforcement layer** | §3.2 SPDX/REUSE, §3.6 Cost/Benefit (34h) | Jem flags M14 tension but doesn't specify the SPDX/REUSE/SLSA stack that closes the gap. |
| **M35 submodule vs vendored distinction** | §1.3 Git Submodule vs Subtree vs Vendor Copy vs npm (lines 79-90) | Critical for "no tracked source tree" rule — submodules with pinned SHA should be allowed. |
| **M35 runtime-loaded plugin discovery sweep** | §1.10 Plugin Architecture (lines 146-156) | Local plugins in `~/.config/opencode/plugins/` have no heritage tag. |
| **M35 rotation policy for public client secrets** | §5.8 Engine's Allowlist Architecture (lines 776-822) | Public client secrets don't rotate like private ones, but can be deprecated. |
| **M36 Recursive Probe (M23 applied to M23)** | My §4.1 | Novel contribution Jem didn't consider. |
| **COHORT_REGISTRY.json for fleet-level** | My §4.2 | Extends M34 beyond single orchestrator. |

### §2.4 Actionable Improvements to Jem's Report

1. **Add Lilith's spec as the implementation reference** for M34 — Jem's schema gaps are addressed by Lilith's `ActiveSubagent` interface (which includes `dispatched_at` as `spawn_time`, `expected_deliverable` as `output_path`, `current_turn` as `checkpoint.last_action`, `interruption_type` as `status` enum, `resumption_count` as implicit via `resumption_status`).
2. **Downgrade "second agent verification" to "recommended for P0/P1"** — the 2-pass probe + structured envelope + confidence threshold is the baseline; cross-validation is an escalation tier.
3. **Correct L3 confidence to 0.85-0.90** with replication path — 0.80 is too low for a lesson with this much evidence.
4. **Merge Jem's M34 schema fields into Lilith's spec** — Jem's 5 missing fields map to Lilith's interface; the spec should explicitly include them.
5. **Add primary-source citation requirement to M35** — this is a critical supply-chain defense Jem correctly identified.
6. **Add immediate remediation clause to M35** — the redacted value must be fixed NOW, not just future prevention.

---

## §3 — PEER REVIEW: LILITH'S M34 RUNTIME SPEC

### §3.1 Alignment with My Research

| Lilith's Spec Element | My Report Section | Alignment |
|----------------------|-------------------|-----------|
| `ACTIVE_SUBAGENTS.json` schema with `session_id`, `parent_session_id`, `parent_task_id` | §1.2 M34 amendments (channel-awareness, recursive cohort) | ✅ **ALIGNED** — Lilith's schema includes `channel`, `parent_session_id` for nesting. |
| `subagent_type: "EIS" | "NES" | "SPT"` | My report didn't use this taxonomy | ✅ **COMPATIBLE** — SUBAGENT_DISPATCH_PROTOCOL §1.5 defines these; Lilith correctly adopts them. |
| `Checkpoint` with `tokens_used`, `last_action`, `files_touched`, `progress_pct` | §4.10 layered detection (pre-turn/in-turn/post-turn) | ✅ **ALIGNED** — checkpoint captures in-turn state for recovery. |
| `status` enum: `ALIVE`, `INTERRUPTED_EXTERNALLY`, `INTERRUPTED_CRASH`, `COMPLETED`, `FAILED`, `DEAD_LETTER`, `ORPHANED` | My M34 amendments (recovery trigger, verification) | ✅ **COMPREHENSIVE** — covers all states Jem and I identified. |
| `resumable: boolean` (false for SPT) | My recursive cohort awareness amendment | ✅ **ALIGNED** — SPT is one-shot; EIS/NES are resumable. |
| Atomic write pattern (tmp + rename + fsync) | M23 Failure Integrity | ✅ **M23-COMPLIANT** — no torn writes. |
| Signal handler for SIGINT/SIGTERM → `INTERRUPTED_EXTERNALLY` | Jem's "Esc x2 cascade" finding | ✅ **DIRECTLY ADDRESSES** the actual incident mechanism. |
| `orchestrator_session_start()` recovery protocol | My M34 amendments (recovery trigger, structured prompt, verification) | ✅ **IMPLEMENTS** my recovery protocol with user decision menu. |
| `watchdog_check()` for orchestrator crash | Jem's orchestrator-crash gap | ✅ **ADDRESSES** Jem's critical gap via Hivemind awareness. |
| 3 MCP tools: `m34_register_subagent`, `m34_list_active_subagents`, `m34_apply_user_decision` | My channel-awareness + Hivemind integration | ✅ **OPERATIONALIZES** the mandate. |
| 35-hour roadmap over 2 weeks | My report didn't estimate effort | ✅ **REALISTIC** — Phase 1 (14h) + Phase 2 (9h) + Phase 3 (12h) = 35h. |

### §3.2 Gaps (What My Research Implied That Lilith's Spec Doesn't Address)

| Gap | My Report Source | Why It Matters |
|-----|------------------|----------------|
| **Model-switch continuity (M34b)** | Jem §1.2.4 — actual incident was model switch, not Esc x2 | Lilith's spec handles `INTERRUPTED_EXTERNALLY` (Esc x2) and `INTERRUPTED_CRASH` (orchestrator death) but NOT model switch. A model switch orphans the session without an interrupt signal. |
| **Write-tool routing enforcement (M33 preventive)** | My §1.1 M33 amendment #1: require write tool for >8K token reports | Lilith's spec is M34-only; M33 enforcement is separate but related. The orchestrator should enforce write-tool routing at dispatch time. |
| **Structured completion envelope for M33** | My §1.1 M33 amendment #2: JSON envelope with `state`, `last_chunk_id`, `total_chunks` | Lilith's `Checkpoint` has `progress_pct` but no `total_chunks` or `queued_findings`. The M33 probe needs this. |
| **Cross-validator agent for M33** | Jem §1.1.5 + my §4.1 M36 Recursive Probe | Lilith's spec has no cross-validation mechanism. |
| **Primary-source citation in `secrets-public.toml`** | Jem §1.3.5 + my M35 amendment | Lilith's spec doesn't cover M35. |
| **Immediate remediation of redacted values** | Jem §1.3.3 | The current broken OAuth is not addressed by M34. |
| **SPDX/REUSE enforcement for third-party code** | My M35 mandatory amendment + §3.2, §3.6 | Lilith's spec is M34-only; this is M35 territory. |
| **Submodule vs vendored distinction in schema** | My §1.3 M35 clarification #2 | Lilith's `ActiveSubagent` has no field for "how this code was integrated." |
| **Runtime-loaded plugin discovery sweep** | My M35 edge case #1 | Plugins loaded from `~/.config/opencode/plugins/` are invisible to `ACTIVE_SUBAGENTS.json`. |

### §3.3 Over-Engineering (Parts of 35h Roadmap My Research Suggests Are Unnecessary)

| Lilith's Item | My Assessment | Why It May Be Over-Engineering |
|---------------|---------------|-------------------------------|
| **Phase 1: `m34_interruption_watcher.py` signal handler** | ⚠️ **PARTIAL** | OpenCode's TUI already handles `Esc x2` and kills child processes. The signal handler may be redundant if the TUI's process group kill is sufficient. The `opencode-sessions-explorer` watcher (polling) may be more reliable than signal handlers in a multi-process Bun/Node environment. |
| **Phase 1: `m34_register_subagent` MCP tool + hook into `subagent_dispatcher.py`** | ✅ **NECESSARY** | This is the core registration mechanism. |
| **Phase 2: `m34_apply_user_decision` MCP tool** | ✅ **NECESSARY** | User decision UI is required. |
| **Phase 2: `watchdog_check()` in `hivemind_get_awareness`** | ✅ **NECESSARY** | Addresses Jem's orchestrator-crash gap. |
| **Phase 3: Stress test 50 concurrent subagents** | ⚠️ **OVER-TESTING** | 50 concurrent subagents is unrealistic for the current fleet (typically 2-5). 10 concurrent would be sufficient. |
| **Phase 3: Migration script from `TASK_REGISTRY.json`** | ✅ **NECESSARY** | Backfill is needed for continuity. |
| **Phase 3: Update `.opencode/agents/*.md` for all primary agents** | ⚠️ **PARTIAL** | Only agents that actually spawn subagents (Kali, Grokster, Lilith, Ma'at) need this. Researcher, Jem, Roc, Node typically don't spawn. |

### §3.4 Actionable Improvements to Lilith's Spec

1. **Add `INTERRUPTED_MODEL_SWITCH` status** (or extend `INTERRUPTED_CRASH` with `interruption_reason: "model_switch"`) — the actual incident mechanism is not covered.
2. **Add `total_chunks` and `queued_findings` to `Checkpoint`** — needed for M33 structured completion envelope.
3. **Add `write_tool_required: boolean` to `ActiveSubagent`** — for M33 preventive enforcement at dispatch time.
4. **Add `cross_validator_agent: string | null` to `ActiveSubagent`** — for M33 cross-validation (Jem's recommendation, my M36).
5. **Reduce stress test from 50 to 10 concurrent** — realistic fleet size.
6. **Limit `.opencode/agents/*.md` updates to actual orchestrator agents** (Kali, Grokster, Lilith, Ma'at).
7. **Add `interruption_reason` field to `ActiveSubagent`** — distinguishes `Esc x2`, `model_switch`, `timeout`, `user_cancel`.
8. **Add `primary_source_url` to `secrets-public.toml` schema** (M35) — Jem's supply-chain defense.

---

(continued in next increment — §4 The True Verdict + §5 Cross-Report Corrections)

## §4 — THE TRUE VERDICT (Synthesis of All Three Reports)

### §4.1 M33 Anti-Truncation & Stream Exhaustion Gate

**TRUE STATE**: The mandate is **salvageable but the current text is a bypass attack waiting to happen**.

| Source | Finding | Weight |
|--------|---------|--------|
| My report | Probe is reactive, misses preventive write-tool routing | Structural |
| Jem | Single-probe is exploitable (immediate `STREAM_EXHAUSTED` reply); needs 2-pass or cross-validator | Adversarial |
| Lilith | Spec doesn't cover M33; but `Checkpoint.progress_pct` could support structured completion | Implementation |

**TRUE VERDICT**: **CONDITIONAL GO — M33 must be amended with 3 layers:**
1. **Preventive**: "For reports > 8K tokens, the orchestrator must require the subagent to use the write tool, not the chat stream, before delivering any response." (My amendment #1)
2. **Structured Probe**: Replace free-form `STREAM_EXHAUSTED` with JSON envelope: `{"state": "exhausted", "last_chunk_id": N, "total_chunks": M, "queued_findings": [], "confidence": 0.XX}`. (My amendment #2 + Jem's structured envelope)
3. **Escalation Tier**: For P0/P1 deliverables, require a **second agent's cross-validation** (Jem's recommendation, my M36). For P2+, the 2-pass probe + structured envelope + confidence ≥ 0.95 is sufficient.

**Why not just Jem's 2-pass probe?** Because a 2-pass probe is still LLM-dependent. The structured envelope + confidence threshold + write-tool prevention is a *defense in depth* that addresses both the bypass and the re-entry truncation edge case.

---

### §4.2 M34 Multi-Agent Co-Interruption & Resumption Accounting

**TRUE STATE**: The mandate is **salvageable but conflates two failure modes and misses the model-switch case**.

| Source | Finding | Weight |
|--------|---------|--------|
| My report | Detection correct, recovery underspecified; dual-load path is separate failure mode | Structural |
| Jem | Schema gaps (5 fields); orchestrator crash recovery missing; model-switch ≠ Esc x2; status format unspecified; Hivemind audit needed | Adversarial |
| Lilith | Full runtime spec (35h) covering schema, signal handler, recovery UI, watchdog, MCP tools | Implementation |

**TRUE VERDICT**: **CONDITIONAL GO — M34 must be amended with 5 corrections:**

1. **Split the failure modes** (Jem's M34a/M34b, but implemented as status enum values):
   - `INTERRUPTED_EXTERNALLY` = global abort (Esc x2, SIGINT, timeout)
   - `INTERRUPTED_MODEL_SWITCH` = model change mid-task (the actual incident mechanism)
   - `INTERRUPTED_CRASH` = orchestrator/host crash
   Each has different recovery semantics.

2. **Adopt Lilith's schema + Jem's 5 missing fields** (merged):
   - `dispatched_at` → Lilith's `spawn_time` ✅
   - `expected_deliverable` → Lilith's `output_path` ✅
   - `current_turn` → Lilith's `checkpoint.last_action` ✅
   - `interruption_type` → Lilith's `status` enum + new `interruption_reason` field ⚠️ ADD
   - `resumption_count` → Lilith's implicit via `resumption_status` ⚠️ ADD explicit counter

3. **Orchestrator crash recovery** (Jem's gap, Lilith's watchdog): Lilith's `watchdog_check()` via Hivemind awareness is the correct implementation. **Must be mandatory** — not optional.

4. **Status report format**: Specify Markdown table rendered from `ACTIVE_SUBAGENTS.json` on every user turn (Jem's requirement). Lilith's `orchestrator_session_start()` already produces this format — codify it.

5. **Hivemind audit clause**: "On every user turn, the orchestrator MUST call `m34_list_active_subagents()` BEFORE responding." Verifiable via Hivemind audit (Jem's requirement).

**Lilith's spec is 90% correct** — the 10% gap is the model-switch status, the `interruption_reason` field, and the Hivemind audit clause. The 35h roadmap is realistic and should be approved with these 5 corrections.

---

### §4.3 M35 Third-Party Boundary & Public Secret Exemption

**TRUE STATE**: The mandate is **highest text-alignment but has 5 critical implementation gaps**.

| Source | Finding | Weight |
|--------|---------|--------|
| My report | Every element traceable to 2,460-line report; missing SPDX/REUSE enforcement | Structural |
| Jem | 5 critical gaps: recovery procedure, immediate remediation, M14 cross-ref, primary-source citation, rotation policy | Adversarial |
| Lilith | N/A (M34 only) | — |

**TRUE VERDICT**: **CONDITIONAL GO — M35 must be amended with 5 mandatory additions:**

1. **SPDX-License-Identifier enforcement per REUSE v3.3** (My mandatory amendment): "All third-party code MUST carry SPDX-License-Identifier in file header OR entry in `.reuse/dep5`."
2. **Immediate remediation of redacted values** (Jem): "M35 requires IMMEDIATE remediation of any `GOCSPX-***REDACTED-ROTATED***` or similar placeholder: (1) restore from git HEAD, (2) verify original is public client secret per RFC 8252, (3) add to `data/secrets-public.toml`, (4) re-test OAuth flow."
3. **`data/secrets-public.toml` recovery procedure** (Jem): "File MUST be committed to git, reviewed on every PR, versioned. Secret scanner MUST fail-closed if missing/unparseable, trigger Hivemind `intent=blocker`."
4. **Primary-source citation requirement** (Jem): "Every entry MUST cite a primary source URL (vendor's official docs, vendor's published source on GitHub). Entries without primary source MUST be rejected by review."
5. **M14 cross-reference** (Jem): "M35 is a NARROW exception to M14 for public client secrets only. All other third-party code MUST comply with M14 (including SPDX headers). Pinned submodules allowed with heritage tag. Runtime-loaded local plugins require discovery sweep."

**The OAuth flow is STILL BROKEN** as of this session — the redacted value in `opencode-antigravity-auth/src/constants.ts:9` has not been restored. This is a P0 blocker for any debut.

---

### §4.4 L3-InterruptionSovereigntyAndCoResumption

**TRUE STATE**: The lesson is **factually accurate in principle but epistemically over-claimed and factually flawed in evidence**.

| Source | Finding | Weight |
|--------|---------|--------|
| My report | Over-confident (0.99), conflates two phenomena, should split | Epistemic |
| Jem | Confidence 0.99 unjustified (should be 0.80); conflates Completion Illusion + Co-Resumption; evidence error (appendices from separate session) | Adversarial |
| Lilith | N/A | — |

**TRUE VERDICT**: **REVISE BEFORE CANONIZATION — 4 required changes:**

1. **Lower confidence to 0.85** (not 0.80 — Jem is too harsh; 0.85 reflects: 1 incident + 3 session IDs + 2 structural causes + replication path via M33/M34 mandates).
2. **Split into two lessons**:
   - **L3-CompletionIllusion** (confidence 0.85): "An LLM subagent's `state=completed` is necessary but not sufficient for semantic exhaustion. The goldmine often lives in the tail." Mandates: M23. Remedy: M33 sentinel probe.
   - **L3-CoResumptionAccounting** (confidence 0.80): "A multi-agent orchestrator must track parallel subagent dispatches as a unified transactional cohort. Dropping a secondary subagent is orchestrator amnesia." Mandates: M11, M15, M27. Remedy: M34 cohort tracking.
3. **Correct the evidence error**: The appendices A-T were added in a 2026-08-29 continuation session, NOT from the 2026-08-30 "continue" prompt in this incident.
4. **Add `related_lessons` cross-references**: `L3-ParallelPersistenceHidesState` (general principle), `L3-ContentAddressedSurvives` (recovery pattern), `L3-DocumentationIsNotEnforcement` (policy vs gate).

**The lesson's core principle is sound** — the "goldmine in the tail" is a real phenomenon (Factory.ai 37% multi-session retention). The fix is calibration and separation.

---

## §5 — CROSS-REPORT CORRECTIONS (Specific Line-Level Changes)

### §5.1 Corrections to My Report (`RESEARCHER_VERIFICATION_GROKSTER_20260830.md`)

| Location | Current Text | Corrected Text | Reason |
|----------|--------------|----------------|--------|
| §0 line 30 | "probe is well-designed for the immediate need but misses the preventive layer" | "probe is reactive and has a bypass attack (Jem §1.1.3); misses preventive write-tool routing AND structured completion envelope" | Jem caught the bypass attack I missed |
| §0 line 32 | "proposed ACTIVE_SUBAGENTS.json schema addresses the detection half but misses the recovery half" | "proposed ACTIVE_SUBAGENTS.json schema addresses detection but misses recovery, model-switch case, orchestrator-crash recovery, and schema fields (Jem §1.2.1, §1.2.2, §1.2.4)" | Jem identified 4 additional gaps |
| §0 line 34 | "One gap: my report recommends SPDX-License-Identifier enforcement" | "Critical gaps: SPDX/REUSE enforcement (my report), plus recovery procedure, immediate remediation, primary-source citation, M14 cross-ref (Jem §1.3)" | Jem found 4 additional M35 gaps |
| §1.1 line 64 | "8K tokens (the threshold where M3 streaming becomes risky per deep_dive_synthesis_20260828.md §1)" | "8K tokens (empirical threshold from M3 streaming behavior; see `deep_dive_synthesis_20260828.md` §1 for post-compact pattern, streaming threshold is operational observation)" | Citation was inaccurate |
| §1.1 line 68 | "Edge case M33 misses: the STREAM_EXHAUSTED reply itself may be truncated" | "Edge cases M33 misses: (1) STREAM_EXHAUSTED reply may be truncated (re-entry failure); (2) subagent can immediately reply STREAM_EXHAUSTED to bypass probe (Jem §1.1.3 bypass attack)" | Jem's bypass attack is more critical |
| §1.1 line 70-72 | "Verdict: RATIFY with 2 amendments: 1. preventive clause... 2. structured completion envelope" | "Verdict: CONDITIONAL GO with 3 amendments: 1. preventive write-tool routing for >8K tokens; 2. structured JSON completion envelope with confidence; 3. P0/P1 cross-validator agent escalation (Jem §1.1.5)" | Adds Jem's cross-validator tier |
| §1.2 line 83 | "UNDERSIZED on the recovery side" | "UNDERSIZED on recovery side AND conflates model-switch with Esc x2 (Jem §1.2.4); misses orchestrator-crash recovery (Jem §1.2.2); misses schema fields (Jem §1.2.1)" | Adds Jem's 3 additional gaps |
| §1.2 line 117-121 | "Verdict: RATIFY with 4 amendments: 1. Recovery Trigger... 4. channel-awareness and recursive cohort tracking" | "Verdict: CONDITIONAL GO with 5 amendments: 1. Recovery Trigger (2 user turns); 2. Structured recovery prompt; 3. Recovery Verification (re-run M33); 4. Channel-awareness + recursive cohort; 5. Model-switch status enum + orchestrator-crash recovery via watchdog + status-report format + Hivemind audit clause (Jem §1.2.1-1.2.7)" | Merges Jem's 5 gaps into 5 amendments |
| §1.3 line 130 | "HIGHEST-VERIFIED of the three mandates" | "HIGHEST TEXT-ALIGNMENT but 5 critical implementation gaps (Jem §1.3): recovery procedure, immediate remediation, M14 cross-ref, primary-source citation, rotation policy" | Accurate framing |
| §1.3 line 165-169 | "Verdict: RATIFY with 1 mandatory amendment + 3 clarifications" | "Verdict: CONDITIONAL GO with 5 mandatory amendments: 1. SPDX/REUSE enforcement (my report); 2. Immediate remediation of redacted values (Jem); 3. secrets-public.toml recovery procedure (Jem); 4. Primary-source citation requirement (Jem); 5. M14 cross-reference + submodule distinction + runtime plugin sweep (Jem + my report)" | Merges all gaps |
| §3.1 line 289 | "Recommend 0.90" | "Recommend 0.85 (split: L3-CompletionIllusion 0.85, L3-CoResumptionAccounting 0.80)" | Jem's 0.80 is too low; split justifies different confidences |
| §3.4 line 353 | "Split into L3-CompletionIllusion and L3-CoResumptionAccounting" | "Split into L3-CompletionIllusion (0.85, M23) and L3-CoResumptionAccounting (0.80, M11/M15/M27). Correct evidence: appendices from 2026-08-29 continuation, not 2026-08-30 continue prompt. Add related_lessons cross-refs." | Adds evidence correction + cross-refs |
| §5 line 418-422 | M23 unverifiable items | Add: "4. §1.1 8K token threshold citation was inaccurate (deep_dive_synthesis §1 discusses post-compact, not streaming threshold). 5. §3.3 overlap search did NOT cover soul.yaml files (only proposed_lessons.yaml)." | Two additional M23 flags |

### §5.2 Corrections to Jem's Report (`JEM_ADVERSARIAL_REVIEW_GROKSTER_20260830.md`)

| Location | Current Text | Corrected Text | Reason |
|----------|--------------|----------------|--------|
| §1.1.3 line 98-101 | "Mitigation options: 1. Two-pass probe... 4. Progressive probe" | "Mitigation options (baseline): 1. Two-pass probe... 4. Progressive probe. **Escalation tier for P0/P1**: Cross-validator agent (separate agent reads prompt requirements + deliverable). The baseline 2-pass + structured envelope + confidence ≥ 0.95 is sufficient for P2+." | Clarifies tiered approach |
| §1.2.4 line 203-205 | "RECOMMENDATION: Split M34 into two mandates: M34a: Co-Interruption Recovery, M34b: Model-Switch Continuity" | "RECOMMENDATION: Extend M34 status enum with `INTERRUPTED_MODEL_SWITCH` (distinct from `INTERRUPTED_EXTERNALLY` and `INTERRUPTED_CRASH`). Lilith's spec already handles `INTERRUPTED_CRASH` via watchdog; model-switch needs its own status for correct recovery semantics. A separate mandate is over-engineering; a status enum value + recovery clause suffices." | Lilith's spec already covers crash; model-switch is the missing piece |
| §1.2.2 line 169 | "RECOMMENDATION: Add M34 clause: If orchestrator session itself is interrupted, Hivemind must reconstruct ACTIVE_SUBAGENTS state from DB's session table and assign a recovery agent." | "RECOMMENDATION: Lilith's `watchdog_check()` via Hivemind awareness IS the correct implementation. Make it MANDATORY in M34: 'If orchestrator session is missing from Hivemind awareness > 2× TTL, any agent reading Hivemind MUST run watchdog_check() and present orphaned sessions to user.'" | Lilith's spec already implements this |
| §2.1 line 319 | "A single-incident lesson should be 0.75-0.85 at most." | "A single-incident lesson should be 0.80-0.90. This lesson has: 1 incident + 3 session IDs + 2 structural causes identified + replication path via M33/M34 mandates. 0.85 is appropriate for the combined lesson; split lessons get 0.85 (CompletionIllusion) and 0.80 (CoResumption)." | More nuanced calibration |
| §5.1 line 473 | "M33 must be amended to require 2-pass probe or cross-validator agent" | "M33 must be amended with 3 layers: (1) Preventive write-tool routing for >8K tokens; (2) Structured JSON completion envelope with confidence; (3) P0/P1 cross-validator agent escalation. The 2-pass probe is baseline; cross-validator is P0/P1 escalation." | Tiered approach |
| §5.1 line 474 | "M34 must be split into M34a + M34b" | "M34 must be extended with: (1) `INTERRUPTED_MODEL_SWITCH` status enum; (2) 5 schema fields (interruption_reason, resumption_count); (3) Orchestrator-crash recovery via mandatory watchdog_check(); (4) Status-report format (Markdown table from ACTIVE_SUBAGENTS.json); (5) Hivemind audit clause (m34_list_active_subagents before every user turn)." | Merges Jem's gaps into Lilith's spec |
| §5.1 line 475 | "L3-InterruptionSovereignty must be revised (lower confidence, split into two lessons, correct evidence error)" | "L3-InterruptionSovereignty must be revised: (1) Lower confidence to 0.85 (split: CompletionIllusion 0.85, CoResumptionAccounting 0.80); (2) Split into two lessons with separate mandates; (3) Correct evidence error (appendices from 2026-08-29 continuation, not 2026-08-30 continue); (4) Add related_lessons cross-refs." | Precise corrections |

### §5.3 Corrections to Lilith's Spec (`LILITH_M34_RUNTIME_SPEC_20260830.md`)

| Location | Current Text | Corrected Text | Reason |
|----------|--------------|----------------|--------|
| §1.1 line 29-36 | `type SessionStatus = "ALIVE" | "INTERRUPTED_EXTERNALLY" | "INTERRUPTED_CRASH" | "COMPLETED" | "FAILED" | "DEAD_LETTER" | "ORPHANED"` | `type SessionStatus = "ALIVE" | "INTERRUPTED_EXTERNALLY" | "INTERRUPTED_MODEL_SWITCH" | "INTERRUPTED_CRASH" | "COMPLETED" | "FAILED" | "DEAD_LETTER" | "ORPHANED"` | Adds model-switch status (Jem's critical gap) |
| §1.1 line 48-76 | `interface ActiveSubagent` | Add fields: `interruption_reason: "esc_x2" | "model_switch" | "timeout" | "user_cancel" | "crash" | "unknown"`, `resumption_count: number` (default 0), `cross_validator_agent: string | null`, `write_tool_required: boolean` | Jem's schema gaps + M33 integration + cross-validator |
| §1.1 line 70 | `checkpoint: Checkpoint;` | Extend `Checkpoint` with: `total_chunks?: number`, `queued_findings?: string[]` | M33 structured completion envelope support |
| §2.1 line 230-238 | State machine | Add transition: `ALIVE` → `INTERRUPTED_MODEL_SWITCH` on model switch detection (via session header model change) | Model-switch continuity |
| §3.1 line 290-334 | `orchestrator_session_start()` | Add: `m34_list_active_subagents()` call at start of EVERY user turn (Hivemind audit clause). Present interrupted sessions including `INTERRUPTED_MODEL_SWITCH`. | Jem's Hivemind audit + model-switch |
| §3.2 line 379-419 | `interruption_watcher()` | Add: detect model switch via `opencode-sessions-explorer-current-session` model field change → mark `INTERRUPTED_MODEL_SWITCH` | Model-switch detection |
| §5.1 line 587-599 | Phase 1 tasks | Add: "Add `INTERRUPTED_MODEL_SWITCH` to SessionStatus enum", "Add `interruption_reason`, `resumption_count`, `cross_validator_agent`, `write_tool_required` to ActiveSubagent", "Extend Checkpoint with `total_chunks`, `queued_findings`" | Schema extensions |
| §5.1 line 594 | "Hook `m34_register_subagent` into `subagent_dispatcher.py:dispatch()`" | "Hook `m34_register_subagent` into `subagent_dispatcher.py:dispatch()` — include `write_tool_required: true` for research/forensic tasks > 8K estimated tokens" | M33 preventive at dispatch |
| §5.3 line 620-624 | Phase 3 stress test | Change "50 concurrent subagents" to "10 concurrent subagents (realistic fleet size)" | Realistic testing |
| §5.5 line 632-648 | Files to create | Add: `src/omega/oracle/m33_probe.py` (M33 sentinel probe + structured envelope + cross-validator), `data/secrets-public.toml` schema (M35) | M33/M35 implementation |
| §5.6 line 663-710 | MCP tools | Add: `m33_execute_sentinel_probe(session_id: string, expected_chunks: number) -> dict`, `m35_validate_secrets_allowlist() -> dict` | M33/M35 operationalization |

---

## §6 — FINAL RECOMMENDATION TO ARCHITECT + KALI

**Approve with corrections.** The three EIS reports together form a complete picture:

1. **M33**: Apply 3-layer fix (preventive + structured probe + P0/P1 cross-validator)
2. **M34**: Adopt Lilith's spec + 5 corrections (model-switch status, schema fields, watchdog mandatory, status format, Hivemind audit)
3. **M35**: Apply 5 mandatory amendments (SPDX, remediation, recovery, primary-source, M14 cross-ref)
4. **L3**: Split into 2 lessons, confidence 0.85/0.80, correct evidence, add cross-refs
5. **Sprint tickets**: All 5 P0/P1 tickets are GO (CI-BRIEF-001, VAULT-ALLOWLIST-001, ORCH-RESUME-001, PKG-CLEANUP-001, DOC-CANON-001 with L3 revision first)

**Total implementation effort**: ~35h (Lilith M34) + ~8h (M33 probe + cross-validator) + ~4h (M35 allowlist + SPDX hooks) + ~2h (L3 revision) = **~49 hours over 2 weeks** — within Phase 1 sprint budget.

**Blocker**: The redacted OAuth value in `opencode-antigravity-auth/src/constants.ts:9` must be restored **TODAY** (M35 immediate remediation). The OAuth flow is broken for all Antigravity users.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ META-REVIEW-3EIS ⬡ 2026-08-30 ⬡ CONDITIONAL-GO-WITH-CORRECTIONS*
