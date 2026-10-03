# 🔱 CANONICAL DECISIONS — Immutable Decision Ledger (D-521 to D-612)
**AP Token**: `AP-CANONICAL-DECISIONS-20260829-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ jem-2.0 ⬡ opencode ⬡ trc_canonical_decisions ⬡ ACTIVE

**Date**: 2026-08-29
**Status**: CANONICAL — Consolidated from `data/coordination/DECISION_LEDGER.md` (D-VOS-001..018) + `data/coordination/ACTIVE_SPRINT.json` (D-521..D-612) + `docs/decisions/PIVOT_LOG.md` (D-603) + `STRATEGY_CORPUS_MAP.md` §2 + `SOVEREIGN_ARK_BLUEPRINT.md` §8

**Format**: Each decision is immutable, append-only. Superseded decisions are marked but never deleted.

---

## 📜 DECISION FORMAT

```
## D-XXX: [Title]
**Date**: YYYY-MM-DD
**Realm**: [REALM]
**Decision**: [What was decided]
**Rationale**: [Why — connects to vision/mandates]
**Alternatives Considered**: [What was rejected]
**Impact**: [Downstream effects]
**Reversible?**: [Yes/No + conditions]
**Supersedes**: [Previous decision IDs]
**Author**: [Who made the decision]
**Session**: [Session ID]
**Status**: [ACTIVE | SUPERSEDED | ARCHIVED]
```

---

## 🏛️ FOUNDATIONAL DECISIONS (D-VOS-001..018)

### D-VOS-001: Vision Operating System (VOS) v1.0 Instantiation
**Date**: 2026-08-14 | **Realm**: ALL (Meta) | **Status**: SUPERSEDED by D-VOS-018
**Decision**: Instantiate VOS v1.0 — 7-realm decomposition with sovereign owners, state files, interface contracts, coordination layer.
**Rationale**: Vision too massive for single context window (~10,000 hours). 7 realms: Engine Core, Stacks, Fleet, Memory, Heritage, Omegaverse, Community.
**Impact**: 7 state.yaml files created. VISION_ANCHOR.md as SSOT. DECISION_LEDGER.md created.
**Superseded by**: D-VOS-018 (Hybrid Plan — keeps ADR ledger + Vision SSOT, retires realm state.yaml/workspace briefs/realm_cli.py)

### D-VOS-002: Session-End Hook Preserves Agent Proposals
**Date**: 2026-08-14 | **Realm**: MEMORY | **Status**: ACTIVE
**Decision**: Patch `.opencode/hooks/session_end.py` to preserve agent-written proposals in `proposed_lessons.yaml` instead of overwriting with `proposals: []`.
**Rationale**: M5/M11 compliance hook was destroying agent self-authorship. Agents write proposals per AGENTS.md step 6.5, then hook erased them.
**Impact**: Agent L1→L2→L3 proposals now survive session end. Distillation pipeline integrity restored.
**Reversible**: Yes — revert commit 2b3b2803

### D-VOS-003: Soul Validator — Expand VALID_SOUL_VERSIONS
**Date**: 2026-08-14 | **Realm**: MEMORY/FLEET | **Status**: ACTIVE
**Decision**: Expand `SOUL_VERSION = "6.1"` to `VALID_SOUL_VERSIONS = {"6.1", "7.0", "7.1", "7.2"}` in `soul_validator.py`.
**Rationale**: Old check silently skipped strict validation for v7.x entities (kali, roc_racoon). Critical gap.
**Impact**: kali and roc_racoon now receive strict Pydantic validation.
**Reversible**: Yes — revert commit 2b3b2803

### D-VOS-004: Soul Validator — LIVE_FEED → HMC_COLLABORATION_HUB
**Date**: 2026-08-14 | **Realm**: FLEET | **Status**: ACTIVE
**Decision**: Replace `LIVE_FEED` reference with `HMC_COLLABORATION_HUB` in fallback soul coordination.
**Rationale**: `LIVE_FEED` purged per M27; fallback soul still referenced it, creating self-perpetuating bug loop.
**Reversible**: Yes — revert commit 2b3b2803

### D-VOS-005: SOVEREIGN_MANDATES.md Header Correction
**Date**: 2026-08-14 | **Realm**: GOVERNANCE | **Status**: ACTIVE
**Decision**: Correct header from "Twenty-Five Laws" to "Twenty-Seven Laws" (M26/M27 added 2026-08-14).
**Rationale**: Header contradicted actual mandate count (27). Violated M26 transparency.
**Reversible**: Yes — revert commit 2b3b2803

### D-VOS-006: M22 SSOT Check Fix (False Positive)
**Date**: 2026-08-14 | **Realm**: ENGINE_CORE/GOVERNANCE | **Status**: ACTIVE
**Decision**: Fix broken M22 SSOT check in Makefile — grep pattern `grep -v "inference.fallback_chain"` was false positive flagging ALL `is_cloud:` entries. Replaced with proper YAML parsing via `scripts/check_m22_ssot.py`.
**Rationale**: M22 check completely broken — falsely flagged 12 correct `is_cloud` entries. If M22 broken, other mandate checks may give false confidence.
**Impact**: Mandate audit (ENG-002) triggered for all other checks.
**Reversible**: Yes — revert Makefile + scripts/check_m22_ssot.py

### D-VOS-007: Test Context Packer Tuple Return Fix
**Date**: 2026-08-14 | **Realm**: ENGINE_CORE | **Status**: ACTIVE
**Decision**: Fix `tests/contract/test_context_packer.py` to handle tuple return from `packer.pack()` — `(output_dir, pack_id, pack_timestamp)`.
**Rationale**: API evolved but test wasn't updated. One of 96 test failures.
**Reversible**: Yes

### D-VOS-008: 96 Test Failures — Root Cause Analysis
**Date**: 2026-08-14 | **Realm**: ALL | **Status**: ACTIVE (analysis)
**Decision**: Categorize 96 failures: Class A (~20 real code bugs), Class B (~50 test/code drift), Class C (~26 integration/service).
**Rationale**: Not all failures equal. Class A = fix code; Class B = update tests; Class C = defer behind `@pytest.mark.integration`.
**Impact**: Remediation sprint prioritizes Class A+B, defers Class C.

### D-VOS-009: Public Debut PR — Three-Phase Launch Plan
**Date**: 2026-08-14 | **Realm**: COMMUNITY | **Status**: ACTIVE
**Decision**: Debut PR = public launch with 3 frozen phases: Phase 0 (Foundation), Phase 1 (Community Experience), Phase 2 (Launch Polish).
**Rationale**: Debut must "hit like a bomb." Community tests 6 claims immediately: local-first, zero telemetry, sovereign architecture, heritage-honest, extensible, production quality.
**Reversible**: No — launch commitment

### D-VOS-010: Vision Decomposition — 7 Sovereign Realms
**Date**: 2026-08-14 | **Realm**: ALL (Meta) | **Status**: SUPERSEDED by D-VOS-018
**Decision**: 7 realms: Engine Core (Ma'at), Stacks (Ma'at), Fleet (Kali), Memory (Lilith), Heritage (Doom_Guy), Omegaverse (Lilith), Community (Kali).
**Superseded by**: D-VOS-018 (Hybrid — keeps ADR ledger + Vision SSOT, retires realm state.yaml/workspace briefs/realm_cli.py/Omegaverse realm)

### D-VOS-011: PKEXEC Privilege Escalation Directive
**Date**: 2026-08-14 | **Realm**: FLEET/COMMUNITY | **Status**: ACTIVE
**Decision**: Agents with sysadmin tasks MUST use `pkexec` instead of `sudo`.
**Rationale**: User has pkexec configured; reduces Architect interrupts for privileged operations.
**Reversible**: Yes

### D-VOS-012: Audit-First Approach Before Remediation Sprint
**Date**: 2026-08-14 | **Realm**: GOVERNANCE | **Status**: ACTIVE
**Decision**: Before remediation sprint, audit mandate checks for false positives, run coverage analysis, heritage sweep, triage 96 failures.
**Rationale**: M22 check was completely broken. If M22 broken, M1/M7/M8/M9/M23 may also give false confidence.
**Impact**: ENG-002 (mandate audit) is Phase 0 task. Heritage sweep (HRT-001) and coverage analysis added.

### D-VOS-013: Ratify 3-PR Path (PR-A Initial, PR-B Real M2, PR-C Dead-Code Quarantine)
**Date**: 2026-08-15 | **Realm**: ALL (Meta) | **Status**: ACTIVE
**Decision**: Ratify 3-PR path: PR-A (public surface honesty), PR-B (amend ENG-001, fix real M2 hits), PR-C (per-module dead-code quarantine after import graph).
**Rationale**: Grok CLI verdict technically sound. Carmack's 4-commit nuclear plan wrong on M2 diagnosis, module paths, vault liveness, strategy-doc requirements.
**Supersedes**: Carmack's 4-commit nuclear plan (ho_29df6a4d77f2)

### D-VOS-014: Reject Carmack's 4-Commit Nuclear Plan
**Date**: 2026-08-15 | **Realm**: ALL (Meta) | **Status**: ACTIVE
**Decision**: Explicitly reject nuclear plan — 6 fatal errors verified by Grok CLI and Kali live probes.
**Rationale**: M2 misdiagnosed, zero-ref paths wrong, vault NOT dead code, strategy docs required by AGENTS.md, VOS not ancient theater.
**Impact**: Prevents catastrophic damage. Establishes grep-as-architecture is not acceptable.

### D-VOS-015: Amend ENG-001 (M2 Firewall Fix)
**Date**: 2026-08-15 | **Realm**: ENGINE_CORE | **Status**: ACTIVE
**Decision**: Amend ENG-001 from "Remove 146 WAD term leaks" to: "M2 = stack-specific leaks, not token WAD. Run `FirewallChecker.scan()`. Fix real hits only (hardcoded entity names, `from config.wads.`)."
**Rationale**: "146 WAD term leaks" factually wrong. `FirewallChecker.scan()` = 0 errors, 0 warnings across 271 files. Test failures are session headers + coordination metadata — NOT stack logic.
**Impact**: ENG-001 now reflects actual M2 enforcement. PR-B fixes real violations only.

### D-VOS-016: Add TRACKING_ARCHITECTURE.md to Keep-List
**Date**: 2026-08-15 | **Realm**: GOVERNANCE | **Status**: ACTIVE
**Decision**: Explicitly add `data/coordination/TRACKING_ARCHITECTURE.md` to PR-C keep-list. It was omitted from Carmack's keep-list; Grok CLI caught this.
**Rationale**: TRACKING_ARCHITECTURE.md is the M27 constitution — 5-tier tracking architecture. Deleting it would brick coordination system.

### D-VOS-017: Log Carmack Mandate Violations to SYSTEM_FAILURE_LOG
**Date**: 2026-08-15 | **Realm**: GOVERNANCE | **Status**: ACTIVE
**Decision**: Create `data/coordination/SYSTEM_FAILURE_LOG.md` and log Carmack's mandate violations from rejected nuclear plan: M4 (cowboy sed), M23 (vault-delete-to-green), M14 (heritage strip risk), M26/M27 (strategy-doc purge), M8 (git add -A ships secrets), False M2.
**Rationale**: M23 requires logging failures. A rejected plan with mandate-violating actions is a systemic near-miss. Pattern (grep-as-architecture, vanity counts, delete-the-failing-test) is recurring.

### D-VOS-018: VOS Hybrid Plan (Option C) Approved
**Date**: 2026-08-15 | **Realm**: ALL (Meta) | **Status**: ACTIVE
**Decision**: Approve Option C (Hybrid): Keep `DECISION_LEDGER.md` (ADR pattern), `VISION_ANCHOR.md` (Vision SSOT); Retire 7 realm state.yaml, 7 workspace briefs, `realm_cli.py`, Omegaverse realm (archive); Add: Realm contract validator in `make temple-grade`, realm sections in `HMC_COLLABORATION_HUB.md`, auto-generate VISION_ANCHOR realm health from `ACTIVE_SPRINT.json`.
**Rationale**: Researcher (web) + Roc_Racoon (local) confirmed: architecture sound (Team Topologies, ADR, DDD), implementation dead code (1/10 integration). Hybrid keeps high-value artifacts, removes coordination overhead, adds enforcement.
**Supersedes**: D-VOS-001 (VOS instantiation) — modifies implementation, keeps architecture

---

## 🎯 EXECUTION-CAMPAIGN DECISIONS (D-521..D-612 from ACTIVE_SPRINT.json)

### D-521: SDP Elevated to Core Architectural Pillar — DEFERRED
**Date**: 2026-08-17 | **Realm**: MEMORY | **Status**: DEFERRED
**Decision**: Sovereign Distillation Pipeline elevated to core slot but DEFERRED (post-debut).
**Rationale**: SDP = Human Protocol (D-538) — `HUMAN PROTOCOL — DO NOT IMPLEMENT` until 10 manual executions.

### D-522: Ground Truth — Nemotron 3 Ultra = 1M, Laguna S 2.1 = 262K
**Date**: 2026-08-17 | **Realm**: MODEL_FLEET | **Status**: PRESERVED
**Decision**: Context window ground truth preserved for config.

### D-526: zswap > zRAM for Desktop with NVMe — RATIFIED
**Date**: 2026-08-20 | **Realm**: INFRASTRUCTURE | **Status**: RATIFIED
**Decision**: 16GB NVMe swap, zswap enabled (25% pool, lzo_rle, zsmalloc), zRAM DISABLED, swappiness=100, cgroup MemoryMax=6G.
**Rationale**: Carmack + Researcher + Jem + LongCat + Nemotron consensus. zswap uses NVMe bandwidth efficiently; zRAM competes for RAM.

### D-527: Never Run zswap and zRAM Simultaneously — RATIFIED
**Date**: 2026-08-20 | **Realm**: INFRASTRUCTURE | **Status**: RATIFIED
**Decision**: Mutually exclusive. zswap + zRAM together causes double-compression thrashing.

### D-532: KALI-RATIFY-ROC-READINESS-20260816 — Ratified
**Date**: 2026-08-16 | **Realm**: FLEET | **Status**: RATIFIED
**Decision**: Remediation plan ratified.

### D-533: THIS MONTH'S SSOT = DEBUT_REMEDIATION_MANUAL_20260817.md §5
**Date**: 2026-08-17 | **Realm**: GOVERNANCE | **Status**: ACTIVE
**Decision**: Execution authority = Manual + ACTIVE_SPRINT.json (PUBLIC-DEBUT-01). Ark §4 is read-only vision.

### D-534: Publication (PUB-1) and Runtime Deletion (DEL-1) Are Separate Cuts
**Date**: 2026-08-17 | **Realm**: RELEASE | **Status**: ACTIVE
**Decision**: PUB-1 = allowlist filter for GitHub; DEL-1 = runtime code deletion. Separate mechanics, separate weeks.

### D-535: Vault Not Wired for Debut — Invert V-1 from Build/Wire to Hide/Delete
**Date**: 2026-08-17 | **Realm**: VAULT | **Status**: SUPERSEDED by D-565/D-566
**Decision**: Vault not in debut. V-1 inverted from build/wire to hide/delete.

### D-536: One Router — ProviderSelector + providers.yaml
**Date**: 2026-08-17 | **Realm**: ENGINE_CORE | **Status**: ACTIVE (BINDING)
**Decision**: Single router only. Delete `TriageRouter`, `SemanticRouter`, `RoutingTable`. `ProviderSelector` is canonical.
**Rationale**: Multiple routers = conflicting routing decisions, untestable, violates M23 (no soft-fail theater).

### D-537: UO Phase 1 Library Swaps + UO §2.6 Three-Vault Adoption REJECTED for Debut
**Date**: 2026-08-17 | **Realm**: ENGINE_CORE | **Status**: REJECTED
**Decision**: Un-overengineering Phase 1 (5 library swaps) and three-vault adoption rejected for debut scope.

### D-538: SDP / Cognitive Sovereignty §7 / Qdrant / JIT Graph RAG / Instruction Router = PARKED
**Date**: 2026-08-17 | **Realm**: MEMORY/RESEARCH | **Status**: PARKED
**Decision**: All post-debut. SDP = Human Protocol (10 manual executions first).

### D-539: CP-3 Not Publicly True Until INST-1 Passes on Machine Without warp-proxy-pool
**Date**: 2026-08-17 | **Realm**: RELEASE | **Status**: ACTIVE
**Decision**: "CP-3 (install honesty)" claim only valid after fresh clone `pip install -e .[native,cli]` works without warp-proxy-pool.

### D-540: Corpus Map Rule 2 Inverted for This Campaign
**Date**: 2026-08-17 | **Realm**: GOVERNANCE | **Status**: ACTIVE
**Decision**: No ticket in ACTIVE_SPRINT = dead. Nothing is executable unless Manual/ACTIVE_SPRINT re-activates it.

### D-548: INST-1 BLOCKED — 6 Critical Fixes Required Before DEL-1
**Date**: 2026-08-20 | **Realm**: RELEASE | **Status**: ACTIVE
**Decision**: INST-1 has 6 critical fixes (fix1,3,5 done; fix2,4,6 ready). DEL-1 cannot begin until INST-1 complete.

### D-549: DEL-1 Scope Validated But Requires Observability Emission Spec for Router Collapse
**Date**: 2026-08-20 | **Realm**: RELEASE | **Status**: ACTIVE
**Decision**: DEL-1 Week 2 router collapse needs observability emission spec before execution.

### D-550: Test Suite Baseline Must Be Green (0 Failures) Before DEL-1 Week 1
**Date**: 2026-08-20 | **Realm**: TESTING | **Status**: ACTIVE
**Decision**: Full pytest suite must pass 0 failures before any deletion campaign begins.

### D-551: God-Module Freeze Requires Atomic Split of oracle.py + model_gateway.py in DEL-1 Week 2
**Date**: 2026-08-20 | **Realm**: ENGINE_CORE | **Status**: ACTIVE
**Decision**: `oracle.py` (1459 lines) + `model_gateway.py` (1582 lines) must be atomically split during DEL-1 Week 2 with contract tests at each step.

### D-552: Vault Path A (Delete from Product Surface) Recommended Over Path B
**Date**: 2026-08-20 | **Realm**: VAULT | **Status**: SUPERSEDED by D-565/D-566
**Decision**: Path A = delete `src/omega/vault/` from product surface; Path B = 50-line minimal. Path A recommended.

### D-553: release/debut Branch from Allowlist Is the Publication Mechanic
**Date**: 2026-08-20 | **Realm**: RELEASE | **Status**: ACTIVE
**Decision**: `release/debut` branch created by `scripts/apply_public_allowlist.sh` is the publication mechanic.

### D-557: Cline DeepSeek V4 Flash = 1M Context — Primary Surgical Tool for DEL-1 Week 2
**Date**: 2026-08-20 | **Realm**: TOOLING | **Status**: ACTIVE
**Decision**: DeepSeek V4 Flash (1M context via OpenRouter) is the primary model for cross-file surgery during DEL-1 Week 2.

### D-558: Fleet Architecture PARKED per Carmack — Only DeepSeek-Assisted IntentRouter Extraction Survives
**Date**: 2026-08-20 | **Realm**: FLEET | **Status**: PARKED
**Decision**: Fleet architecture parked. Only DeepSeek-assisted IntentRouter extraction survives for debut.

### D-559: INST-1 Execution Model Assignment
**Date**: 2026-08-20 | **Realm**: TOOLING | **Status**: ACTIVE
**Decision**: Nemotron 30B for logic/bash fixes; DeepSeek 1M for cross-file surgery.

### D-560: DEL-1 Week 2 Workflow — Human-Driven Incremental Extraction
**Date**: 2026-08-20 | **Realm**: RELEASE | **Status**: ACTIVE
**Decision**: Human-driven incremental extraction with contract tests at each step. Not automated mass deletion.

### D-561: OOM Test Is Test Bug — Expect DENY_THRASHING
**Date**: 2026-08-20 | **Realm**: TESTING | **Status**: ACTIVE
**Decision**: OOM test failure is correct C-2′ fusion behavior (DENY_THRASHING), not a code bug.

### D-562: Vault Path B (50-Line Minimal, Keyring Only) + DELETE omega vault CLI Entirely
**Date**: 2026-08-20 | **Realm**: VAULT | **Status**: SUPERSEDED by D-565/D-566/D-568
**Decision**: Path B for post-debut; delete CLI entirely.

### D-563: 1 Active Cline Instance Max; 8 Accounts = Rate-Limit Resilience Not Parallelism
**Date**: 2026-08-20 | **Realm**: TOOLING | **Status**: ACTIVE
**Decision**: Cline fleet = 8 accounts for rate-limit resilience, not parallel execution. Max 1 active instance.

### D-565: D-562 SUPERSEDED for Debut — Vault Deletion Is Post-Debut Scope
**Date**: 2026-08-20 | **Realm**: VAULT | **Status**: ACTIVE
**Decision**: For `release/debut` branch: exclude `src/omega/vault/` via `PUBLIC_ALLOWLIST.txt`. Zero code changes to vault during PUBLIC-DEBUT-01.

### D-566: D-535 CLARIFIED — Hide Means PUBLIC_ALLOWLIST.txt Exclusion, Not Code Deletion
**Date**: 2026-08-20 | **Realm**: VAULT | **Status**: ACTIVE
**Decision**: "Hide" = allowlist exclusion. VaultCore stays in forge/private repo.

### D-567: D-532 SUPERSEDED for Debut — bury_credential Applies to Post-Debut Vault Sprint Only
**Date**: 2026-08-20 | **Realm**: VAULT | **Status**: ACTIVE
**Decision**: `bury_credential` logic only for post-debut vault work.

### D-568: VaultCore NON-FUNCTIONAL — DELETE as Dead Code, ADD CredentialProvider
**Date**: 2026-08-20 | **Realm**: VAULT | **Status**: ACTIVE
**Decision**: `VaultCore` is non-functional as key source (13 consumers/19 sites, 5 outside src/omega). Delete as dead code. Add `CredentialProvider`. `EncryptionBackend` primary = `python-age` (NOT `pyrage`).

### D-569: Ratify Dynamic Prompt + Planner/Executor + Domain Loading as POST-DEBUT Cognitive Architecture Blueprint (Horizon 3)
**Date**: 2026-08-25 | **Realm**: COGNITIVE | **Status**: ACTIVE
**Decision**: DP-1..DP-8 registered. Owners: Ma'at S0–P3/P7–P8/P10, Kali S4–P5, Verity S6, Researcher S9. Incremental on existing components (ContextBuilder, SelectiveHydration, HybridOrchestrator, ProviderSelector, Context Packer, SDP).

### D-570: Qdrant SCHEDULED to Replace sqlite-vec POST-DEBUT (Horizon 2)
**Date**: 2026-08-25 | **Realm**: MEMORY | **Status**: ACTIVE
**Decision**: Qdrant replaces sqlite-vec post-debut. REACTIVATES `RESEARCHER_QDRANT_MIGRATION_GAPS_20260816.md`. Debut keeps sqlite-vec; DEL-1 Week 1 deletes dead QdrantAdapter; revival at `src/omega/oracle/adapters/qdrant_adapter.py`.

### D-571..D-577: NotebookLM v2.0 Arbitration Ratified
**Date**: 2026-08-25 | **Realm**: RESEARCH | **Status**: ACTIVE
**Decision**: `notebooklm-py` tool, HYBRID cost, 80 DR budget, 6-notebook canonical, SDP gate, 5-25 density, master_token auth.

### D-578..D-584: Phase 0 Tracker Lock-In — 6 New Post-Debut Workstreams
**Date**: 2026-08-20 | **Realm**: ALL | **Status**: ACTIVE
**Decision**: 6 workstreams ratified: GN (Gemini Notebook), DS (Documentation System), LI (Local Inference Opt), KD (Knowledge Domains), HR (Headroom Integration), ZS (zswap Subsystem).

### D-582/D-583: GEMINI-NOTEBOOK Free-Tier-Only Arbitration
**Date**: 2026-08-25 | **Realm**: RESEARCH | **Status**: ACTIVE
**Decision**: 3 accounts, 30 DR/mo (corrected: free Deep Research = 10/mo NOT 30), 2-NB, `notebooklm-py[mcp]`, `master_token.json`, SDP §10 gate.

### CARMACK-REVIEW-20260820: Context Injection Phase 1 ACCEPTED WITH MODIFICATIONS
**Date**: 2026-08-20 | **Realm**: ENGINE_CORE | **Status**: ACTIVE
**Decision**: Phase 1 accepted with modifications; Phase 2/3 40% cuts; Qdrant+Headroom Phase 2/3; Hardware-honest Tier 0 viable (18K base tokens, Qwen3-4B/4B-Thinking/1.7B sequential, q8_0 KV, zswap+NVMe).

### D-601: Model Window Economics Doctrine (6 Laws + Challenge Mechanism)
**Date**: 2026-08-23 | **Realm**: COGNITIVE | **Status**: ACTIVE (BINDING DOCTRINE)
**Decision**: 6 laws: Ascending Windows, Priming Ceilings (≤85% window), Cheap Prime/Expensive Cognate, Digest Before Descent, Family Diversity Weights, Distill Before Switch. Challenge mechanism codified: disputed claims → roc_racoon mines recorded data → verdict with receipts.

### D-603: Latest Pivot Log Entry
**Date**: 2026-08-26 | **Realm**: GOVERNANCE | **Status**: ACTIVE
**Decision**: Latest entry in `docs/decisions/PIVOT_LOG.md`. (Content not yet mined — see PIVOT_LOG.md)

---

### D-ARCHANGEL-001: Archangel Architecture — Agent Hardware Awareness
**Date**: 2026-09-07 | **Realm**: ENGINE_CORE | **Status**: ACTIVE
**Decision**: Agent prompts receive immutable hardware register at dispatch (TTL=30s). The `SystemEnvelopeInjector` wraps `HardwareMonitor` and `ModelGateway` to generate a frozen `RuntimeHardwareRegister` prepended to every agent's context as `[SYSTEM REGISTER: BARE-METAL PHYSICAL BOUNDARY]`. M33Probe gains dynamic write-tool threshold scaling (memory pressure/thermal/OOM).
**Rationale**: Resolves the Ontological Void — agents historically hallucinate hardware (e.g., Turn 9 Nemotron/ASUS hallucination) because they lack ground-truth hardware register. The envelope creates a mathematical contradiction penalty in attention weights for any token contradicting the register.
**Alternatives Considered**: 
- DHAL-only (system-level adaptation only) — rejected: doesn't address agent-level hallucination
- Runtime config file — rejected: git-committed config breaks multi-node; stale reads
- Model fine-tuning on hardware facts — rejected: parametric knowledge still hallucinates under pressure
**Impact**: 
- M33Probe dynamic threshold (2K-8K tokens) scales with memory pressure/thermal/OOM
- Every subagent dispatch injects envelope after M33Probe, before prompt build
- Hallucination basin crushed: statistical paths predicting "Nemotron 3 Ultra on ASUS ExpertBook" face massive contradiction penalty
- Graceful degradation: envelope failure logs warning, dispatch continues
**Reversible?**: Yes — remove injection hook in `subagent_dispatcher.py`
**Supersedes**: N/A (new architecture)
**Author**: Researcher (via GSCA co-design)
**Session**: ses_fd81c19dcffe1nkbPqFg5kRt2v
**Status**: ACTIVE

---

## 📊 DECISION SUMMARY TABLE

| ID | Title | Realm | Status | Reversible |
|----|-------|-------|--------|------------|
| D-VOS-001 | VOS v1.0 Instantiation | ALL | SUPERSEDED | No |
| D-VOS-002 | Session-End Hook Preserves Proposals | MEMORY | ACTIVE | Yes |
| D-VOS-003 | Soul Validator VALID_SOUL_VERSIONS | MEMORY/FLEET | ACTIVE | Yes |
| D-VOS-004 | Soul Validator LIVE_FEED→HUB | FLEET | ACTIVE | Yes |
| D-VOS-005 | Mandate Header Correction | GOVERNANCE | ACTIVE | Yes |
| D-VOS-006 | M22 SSOT Check Fix | ENGINE_CORE | ACTIVE | Yes |
| D-VOS-007 | Context Packer Tuple Fix | ENGINE_CORE | ACTIVE | Yes |
| D-VOS-008 | 96 Test Failures Triage | ALL | ACTIVE | N/A |
| D-VOS-009 | Public Debut 3-Phase Plan | COMMUNITY | ACTIVE | No |
| D-VOS-010 | 7 Sovereign Realms | ALL | SUPERSEDED | No |
| D-VOS-011 | PKEXEC Privilege Directive | FLEET | ACTIVE | Yes |
| D-VOS-012 | Audit-First Approach | GOVERNANCE | ACTIVE | Yes |
| D-VOS-013 | Ratify 3-PR Path | ALL | ACTIVE | Yes |
| D-VOS-014 | Reject Nuclear Plan | ALL | ACTIVE | N/A |
| D-VOS-015 | Amend ENG-001 | ENGINE_CORE | ACTIVE | Yes |
| D-VOS-016 | TRACKING_ARCHITECTURE.md Keep-List | GOVERNANCE | ACTIVE | N/A |
| D-VOS-017 | Log Mandate Violations | GOVERNANCE | ACTIVE | Yes |
| D-VOS-018 | VOS Hybrid Plan (Option C) | ALL | ACTIVE | Yes |
| D-521 | SDP Core Pillar | MEMORY | DEFERRED | — |
| D-522 | Nemotron/Laguna Context Truth | MODEL_FLEET | PRESERVED | — |
| D-526 | zswap > zRAM | INFRASTRUCTURE | RATIFIED | — |
| D-527 | Never zswap+zRAM | INFRASTRUCTURE | RATIFIED | — |
| D-532 | ROC Readiness Ratified | FLEET | RATIFIED | — |
| D-533 | SSOT = Manual + Sprint | GOVERNANCE | ACTIVE | — |
| D-534 | PUB-1 ≠ DEL-1 | RELEASE | ACTIVE | — |
| D-535 | Vault Not Wired | VAULT | SUPERSEDED | — |
| D-536 | One Router | ENGINE_CORE | ACTIVE | No |
| D-537 | UO Phase 1 Rejected | ENGINE_CORE | REJECTED | — |
| D-538 | SDP/Qdrant/JIT/IR PARKED | MEMORY/RESEARCH | PARKED | — |
| D-539 | CP-3 Gate | RELEASE | ACTIVE | — |
| D-540 | Corpus Map Rule 2 Inverted | GOVERNANCE | ACTIVE | — |
| D-548 | INST-1 Blocked (6 Fixes) | RELEASE | ACTIVE | — |
| D-549 | DEL-1 Needs Observability Spec | RELEASE | ACTIVE | — |
| D-550 | Test Suite Green Before DEL-1 | TESTING | ACTIVE | — |
| D-551 | Atomic Split oracle.py + model_gateway.py | ENGINE_CORE | ACTIVE | — |
| D-552 | Vault Path A Recommended | VAULT | SUPERSEDED | — |
| D-553 | release/debut = Allowlist | RELEASE | ACTIVE | — |
| D-557 | Cline DeepSeek = DEL-1 Tool | TOOLING | ACTIVE | — |
| D-558 | Fleet Architecture PARKED | FLEET | PARKED | — |
| D-559 | INST-1 Model Assignment | TOOLING | ACTIVE | — |
| D-560 | DEL-1 Week 2 Human-Driven | RELEASE | ACTIVE | — |
| D-561 | OOM Test = Correct Behavior | TESTING | ACTIVE | — |
| D-562 | Vault Path B + Delete CLI | VAULT | SUPERSEDED | — |
| D-563 | 1 Cline Instance Max | TOOLING | ACTIVE | — |
| D-565 | Vault Exclusion = Allowlist | VAULT | ACTIVE | — |
| D-566 | Hide = Allowlist Exclusion | VAULT | ACTIVE | — |
| D-567 | bury_credential = Post-Debut | VAULT | ACTIVE | — |
| D-568 | VaultCore Dead → CredentialProvider | VAULT | ACTIVE | — |
| D-569 | Cognitive Architecture Blueprint | COGNITIVE | ACTIVE | — |
| D-570 | Qdrant Replaces sqlite-vec | MEMORY | ACTIVE | — |
| D-571..577 | NotebookLM v2.0 Arbitration | RESEARCH | ACTIVE | — |
| D-578..584 | Phase 0 Lock-In (6 Workstreams) | ALL | ACTIVE | — |
| D-582/583 | Gemini Notebook Free-Tier | RESEARCH | ACTIVE | — |
| CARMACK-REVIEW | Context Injection Phase 1 Accepted | ENGINE_CORE | ACTIVE | — |
| D-601 | Model Window Economics (6 Laws) | COGNITIVE | ACTIVE | — |
| D-603 | PIVOT_LOG Latest | GOVERNANCE | ACTIVE | — |
| **D-ARCHANGEL-001** | **Archangel Architecture — Agent Hardware Awareness** | **ENGINE_CORE** | **ACTIVE** | **—** |

---

## 🔍 GAPS: DECISIONS NEEDED BUT NOT MADE

| Gap | Description | Blocked On |
|-----|-------------|------------|
| **D-XXX** | Architect ruling on ZS adjudication (D-584 zswap+NVMe vs Carmack-H-1 zRAM-only) | Architect |
| **D-XXX** | Fleet pool size beyond 14 (M10 cap) — slot eviction policy | Architect + Kali |
| **D-XXX** | Qdrant migration trigger threshold (>500k vectors vs. earlier) | Ma'at + Verity |
| **D-XXX** | Heritage vet record threshold for new `[id-soft:]` tags (≥7/10 scope) | Doom_Guy |
| **D-XXX** | Community installer scope (Sovereign Installer) — curl\|bash vs. guided | Fleet |
| **D-XXX** | WAD Marketplace governance model (community modules) | Fleet |
| **D-XXX** | R-24 Soul-to-Visual Mapping assignment (unassigned critical path) | Architect |
| **D-XXX** | Legacy GitHub repo mining (Correction 5) — download before public | Architect |
| **D-XXX** | Sovereign Ark linguistic era mapping (VISION_ANCHOR §11) | Recursive specialist |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ CANONICAL-DECISIONS ⬡ 2026-08-29*
<!-- PROVENANCE-CORRECTED 2026-08-30T03:06:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: jem-2.0 | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

