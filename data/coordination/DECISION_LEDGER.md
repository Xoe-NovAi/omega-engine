<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 📜 Omega Engine — Decision Ledger
## Immutable History of Architectural & Strategic Decisions

**AP Token**: `AP-DECISION-LEDGER-20260814`  
**Status**: CANONICAL — Every decision is immutable, append-only  
**Last Updated**: 2026-08-14T00:00:00Z  
**Updated By**: Kali  
**VOS Version**: 1.0.0

---

## 📋 How to Use This Ledger

1. **Every architectural/strategic decision** gets an entry (D-VOS-XXX)
2. **Agents query this** to understand WHY, not just WHAT
3. **Realm owners** log decisions affecting their realm
4. **The MaKaLi Council** verdicts are logged here
5. **The Architect** resolves cross-realm conflicts, logged here
6. **Append-only** — decisions are never edited, only superseded

---

## 🏛️ Decision Format

```
## D-VOS-XXX: [Title]
**Date**: YYYY-MM-DD
**Realm**: [REALM]
**Decision**: [What was decided]
**Rationale**: [Why — connects to vision/mandates]
**Alternatives Considered**: [What was rejected]
**Impact**: [Downstream effects on other realms]
**Reversible?**: [Yes/No + conditions]
**Supersedes**: [Previous decision IDs]
**Author**: [Who made the decision]
**Session**: [Session ID]
```

---

## 📜 Decision Log

### D-VOS-001: Vision Operating System (VOS) v1.0 Instantiation
**Date**: 2026-08-14
**Realm**: ALL (Meta)
**Decision**: Instantiate the Vision Operating System (VOS) v1.0 — a 7-realm decomposition of the Omega Engine vision into sovereign, agent-operated subsystems with persistent state, interface contracts, and a coordination layer that survives context death.
**Rationale**: The vision is too massive for any single context window (~10,000 hours of development). The VOS decomposes it into 7 manageable realms (Engine Core, Stacks, Fleet, Memory, Heritage, Omegaverse, Community), each with an owner agent, state file, interface contract, and evolution log. This ensures the vision persists across sessions, models, and context deaths.
**Alternatives Considered**:
- Single monolithic vision document (rejected: too large, no domain ownership)
- Per-agent memory only (rejected: no cross-realm coordination)
- No structure (rejected: current state — vision fragmented across agents)
**Impact**: All 7 realms now have state.yaml files. VISION_ANCHOR.md created as the single source of truth. DECISION_LEDGER.md created for immutable history. Realm CLI to be built.
**Reversible?**: No — foundational architecture decision
**Supersedes**: None
**Author**: Kali (ratified by Architect)
**Session**: ses_vos_init_20260814

---

### D-VOS-002: Session-End Hook Preserves Agent Proposals
**Date**: 2026-08-14
**Realm**: MEMORY
**Decision**: Patch `.opencode/hooks/session_end.py` to preserve agent-written proposals in `proposed_lessons.yaml` instead of overwriting with `proposals: []`.
**Rationale**: The M5/M11 compliance hook was actively destroying agent self-authorship. Agents write proposals per AGENTS.md step 6.5, then the hook fires and erases them with an empty stub. This was a critical data-loss bug violating M5 (Gnosis Preservation) and M11 (Soul Integrity).
**Alternatives Considered**:
- Remove the hook entirely (rejected: loses session timestamp tracking)
- Keep empty overwrite (rejected: destroys agent proposals)
**Impact**: Agent-written L1→L2→L3 proposals now survive session end. Distillation pipeline integrity restored.
**Reversible?**: Yes — revert commit 2b3b2803
**Supersedes**: None
**Author**: Kali
**Session**: ses_vos_init_20260814
**Commit**: 2b3b2803

---

### D-VOS-003: Soul Validator — Expand VALID_SOUL_VERSIONS
**Date**: 2026-08-14
**Realm**: MEMORY / FLEET
**Decision**: Expand `SOUL_VERSION = "6.1"` to `VALID_SOUL_VERSIONS = {"6.1", "7.0", "7.1", "7.2"}` in `soul_validator.py` so that kali (v7.2) and roc_racoon (v7.1) receive strict Pydantic validation instead of being silently skipped.
**Rationale**: The old backward-compatibility check silently skipped strict validation for any entity whose `soul_version` != "6.1". This meant kali and roc_racoon (both v7.x) were never validated — a critical gap. The fix ensures all entities receive strict validation.
**Alternatives Considered**:
- Force-migrate all souls to 6.1 (rejected: breaks v7.x entities)
- Keep silent skip (rejected: entities never validated)
**Impact**: kali and roc_racoon now receive strict Pydantic validation. Any invalid soul_version raises SoulValidationError.
**Reversible?**: Yes — revert commit 2b3b2803
**Supersedes**: None
**Author**: Kali
**Session**: ses_vos_init_20260814
**Commit**: 2b3b2803

---

### D-VOS-004: Soul Validator — LIVE_FEED → HMC_COLLABORATION_HUB
**Date**: 2026-08-14
**Realm**: FLEET
**Decision**: Replace `LIVE_FEED` reference with `HMC_COLLABORATION_HUB` in `soul_validator.py`'s fallback soul coordination protocols.
**Rationale**: The `LIVE_FEED` pattern was purged in favor of `HMC_COLLABORATION_HUB` (per M27 tracking architecture). The fallback soul still referenced the deprecated `LIVE_FEED`, creating a self-perpetuating bug loop where soul corruption → fallback → LIVE_FEED reference reborn.
**Alternatives Considered**: None (direct fix)
**Impact**: Fallback souls no longer perpetuate the deprecated LIVE_FEED pattern.
**Reversible?**: Yes — revert commit 2b3b2803
**Supersedes**: None
**Author**: Kali
**Session**: ses_vos_init_20260814
**Commit**: 2b3b2803

---

### D-VOS-005: SOVEREIGN_MANDATES.md Header Correction
**Date**: 2026-08-14
**Realm**: GOVERNANCE
**Decision**: Correct `SOVEREIGN_MANDATES.md` header from "The Twenty-Five Laws" to "The Twenty-Seven Laws" (M26/M27 added 2026-08-14 were not reflected in the header).
**Rationale**: The header contradicted the actual mandate count (27 mandates). This violated M26 (Doc Standards) transparency — the document claimed 25 laws but contained 27.
**Alternatives Considered**: None (direct fix)
**Impact**: Header now accurately reflects 27 mandates.
**Reversible?**: Yes — revert commit 2b3b2803
**Supersedes**: None
**Author**: Kali
**Session**: ses_vos_init_20260814
**Commit**: 2b3b2803

---

### D-VOS-006: M22 SSOT Check Fix (False Positive)
**Date**: 2026-08-14
**Realm**: ENGINE_CORE / GOVERNANCE
**Decision**: Fix the broken M22 SSOT check in `Makefile` — the grep pattern `grep -v "inference.fallback_chain"` was a false positive that flagged ALL `is_cloud:` entries as "outside fallback_chain" because the YAML structure doesn't contain that literal string. Replaced with proper YAML parsing via `scripts/check_m22_ssot.py`.
**Rationale**: The M22 check was completely broken — it falsely flagged all 12 `is_cloud` entries (which were all correctly inside `fallback_chain`) as violations. This is a critical finding: **if M22's check was broken, other mandate checks may also be giving false confidence.** This triggered the mandate audit task (ENG-002).
**Alternatives Considered**:
- Fix grep pattern (rejected: YAML structure can't be parsed by grep)
- Remove check (rejected: loses M22 enforcement)
**Impact**: M22 check now correctly validates `is_cloud` only appears in `inference.fallback_chain`. Mandate audit (ENG-002) triggered for all other checks.
**Reversible?**: Yes — revert Makefile + scripts/check_m22_ssot.py
**Supersedes**: None
**Author**: Kali
**Session**: ses_vos_init_20260814

---

### D-VOS-007: Test Context Packer Tuple Return Fix
**Date**: 2026-08-14
**Realm**: ENGINE_CORE
**Decision**: Fix `tests/contract/test_context_packer.py` to handle the tuple return from `packer.pack()` — `(output_dir, pack_id, pack_timestamp)` instead of treating it as a string path.
**Rationale**: The test was failing because `packer.pack()` returns a tuple, but the test treated `output_dir` as a Path string. This is a test/code drift issue — the API evolved but the test wasn't updated.
**Alternatives Considered**:
- Change pack() to return only output_dir (rejected: pack_id and pack_timestamp are useful)
- Keep test broken (rejected: test failure)
**Impact**: Test now passes. This is one of the 96 test failures being addressed.
**Reversible?**: Yes
**Supersedes**: None
**Author**: Kali
**Session**: ses_vos_init_20260814

---

### D-VOS-008: 96 Test Failures — Root Cause Analysis
**Date**: 2026-08-14
**Realm**: ALL
**Decision**: Categorize the 96 test failures into 3 classes:
- **Class A (Real Code Bugs, ~20)**: test_firewall_m2.py (146 WAD leaks), test_contract_m21.py (wrong provider_name, missing ProviderName import, MockProvider missing top_p)
- **Class B (Test/Code Drift, ~50)**: test_metrics_db.py (schema version 1≠3), test_observability.py (sync test calls async method)
- **Class C (Integration/Service, ~26)**: test_qdrant_index.py, test_search_tools.py, test_sqlite_vec_adapter.py (require running services)
**Rationale**: The 96 failures are NOT all equal. Class A are real code bugs that must be fixed. Class B are tests that never updated when code changed. Class C require running services. This triage informs the remediation sprint.
**Alternatives Considered**: Treat all 96 equally (rejected: wastes effort on integration tests)
**Impact**: Remediation sprint (Phase 0) prioritizes Class A (code bugs) and Class B (test drift), defers Class C (integration) behind `@pytest.mark.integration`.
**Reversible?**: N/A (analysis)
**Supersedes**: None
**Author**: Kali
**Session**: ses_vos_init_20260814

---

### D-VOS-009: Public Debut PR — Three-Phase Launch Plan
**Date**: 2026-08-14
**Realm**: COMMUNITY
**Decision**: The Omega Engine's initial PR is a **public debut** to the AI community — "irreversibly change the landscape of local AI and take power from corporations and hand it to the people." The launch plan has 3 frozen phases:
- **Phase 0 (Foundation)**: make test-unit green, mandate gates genuinely passing, heritage clean, souls compliant
- **Phase 1 (Community Experience)**: installer, WAD template, QUICKSTART, CONTRIBUTING
- **Phase 2 (Launch Polish)**: README, demo, announcement, v1.0.0-debut tag
**Rationale**: The debut must "hit like a bomb." The community will test 6 claims immediately: local-first, zero telemetry, sovereign architecture, heritage-honest, extensible, production quality. If any fail on first try, the bomb fizzles.
**Alternatives Considered**:
- Internal checkpoint (rejected: user wants public debut)
- Trusted collaborator review (rejected: user wants community launch)
**Impact**: All 7 realms now have Phase 0-2 tasks assigned. Community realm has 12 tasks (COM-001..COM-012).
**Reversible?**: No — launch commitment
**Supersedes**: None
**Author**: Architect (User) + Kali
**Session**: ses_vos_init_20260814

---

### D-VOS-010: Vision Decomposition — 7 Sovereign Realms
**Date**: 2026-08-14
**Realm**: ALL (Meta)
**Decision**: Decompose the Omega Engine vision into 7 sovereign realms, each with a dedicated owner agent, state file, interface contract, and evolution log:
1. **Engine Core** (Ma'at/N3) — WAD Loader, Query Router, Provider Fabric, Memory Store, Godot Bridge
2. **Stacks** (Ma'at/N4) — WAD format, community template, XOE packaging
3. **Fleet** (Kali) — 14 entities, MaKaLi Council, Node slots, Hivemind
4. **Memory** (Lilith/N7) — Soul Architecture v2, Mnemosyne, L1→L2→L3, cross-pollination
5. **Heritage** (Doom_Guy) — [id-soft:] vetting, id Software patterns
6. **Omegaverse** (Lilith/N6) — Godot Bridge, Soul-to-Visual (R-24), P2P Soul Prints
7. **Community** (Kali) — Installer, QUICKSTART, CONTRIBUTING, CI, launch
**Rationale**: The vision is too massive for any single context window. Realm decomposition gives each domain a sovereign owner, persistent state, and clear interface. Realms communicate only through declared interfaces — no realm reaches into another's internals.
**Alternatives Considered**:
- 3 realms (Engine/Stack/Community) (rejected: too coarse, loses domain ownership)
- 14 realms (one per agent) (rejected: too fine, coordination overhead)
**Impact**: 7 state.yaml files created. Realm CLI to be built. All future work organized by realm.
**Reversible?**: No — foundational architecture
**Supersedes**: None
**Author**: Kali (ratified by Architect)
**Session**: ses_vos_init_20260814

---

### D-VOS-011: PKEXEC Privilege Escalation Directive
**Date**: 2026-08-14
**Realm**: FLEET / COMMUNITY
**Decision**: Agents with system administration tasks (N1 Infrastructure, Architect) MUST use `pkexec` instead of `sudo` for privileged operations. The environment has pkexec configured; agents should not prompt the user for sudo.
**Rationale**: The user has pkexec and wants agents to know they have pkexec rights without being told repeatedly. This reduces Architect interrupts for privileged operations.
**Alternatives Considered**:
- sudo (rejected: user prefers pkexec)
- No privilege escalation (rejected: PHASE-0 security tasks need it)
**Impact**: Agents use pkexec for P0-1..P0-4 security tasks. Directive to be added to AGENTS.md.
**Reversible?**: Yes
**Supersedes**: None
**Author**: Architect (User) + Kali
**Session**: ses_vos_init_20260814

---

### D-VOS-012: Audit-First Approach Before Remediation Sprint
**Date**: 2026-08-14
**Realm**: GOVERNANCE
**Decision**: Before executing the full remediation sprint (R-01..R-21), audit the mandate checks for false positives (like the M22 bug), run coverage analysis, heritage sweep, and triage the 96 failures. This prevents shipping another "ready" that isn't.
**Rationale**: The M22 check was completely broken (false positive on all 12 is_cloud entries). If M22 was broken, M1/M7/M8/M9/M23 may also be giving false confidence. We must verify our gates are trustworthy before trusting them.
**Alternatives Considered**:
- Execute remediation sprint immediately (rejected: may fix tests but not broken gates)
- Skip audit (rejected: M22 proved gates can be broken)
**Impact**: ENG-002 (mandate audit) is now a Phase 0 task. Heritage sweep (HRT-001) and coverage analysis added.
**Reversible?**: Yes
**Supersedes**: None
**Author**: Kali
**Session**: ses_vos_init_20260814

---

## 📊 Decision Summary

| ID | Title | Realm | Reversible |
|----|-------|-------|------------|
| D-VOS-001 | VOS v1.0 Instantiation | ALL | No |
| D-VOS-002 | Session-End Hook Preserves Proposals | MEMORY | Yes |
| D-VOS-003 | Soul Validator — VALID_SOUL_VERSIONS | MEMORY/FLEET | Yes |
| D-VOS-004 | Soul Validator — LIVE_FEED→HUB | FLEET | Yes |
| D-VOS-005 | Mandate Header Correction | GOVERNANCE | Yes |
| D-VOS-006 | M22 SSOT Check Fix | ENGINE_CORE | Yes |
| D-VOS-007 | Context Packer Tuple Fix | ENGINE_CORE | Yes |
| D-VOS-008 | 96 Test Failures Triage | ALL | N/A |
| D-VOS-009 | Public Debut PR — 3-Phase Plan | COMMUNITY | No |
| D-VOS-010 | 7 Sovereign Realms | ALL | No |
| D-VOS-011 | PKEXEC Privilege Directive | FLEET | Yes |
| D-VOS-012 | Audit-First Approach | GOVERNANCE | Yes |

---

**This ledger is immutable. Append-only. Every decision references the vision and mandates.**

⬡ OMEGA ⬡ KALI ⬡ DECISION-LEDGER ⬡ 2026-08-14 ⬡ CANONICAL
---

## 📜 Decision Log (Continued)

### D-VOS-013: Ratify 3-PR Path (PR-A Initial, PR-B Real M2, PR-C Dead-Code Quarantine)
**Date**: 2026-08-15
**Realm**: ALL (Meta)
**Decision**: Ratify the revised 3-PR path proposed by Carmack after Grok CLI review:
- **PR-A**: `chore/public-surface-honesty` — public surface only, no src/ redesign, no config/wads/ rename, no vault deletion, no strategy corpus purge
- **PR-B**: `fix/eng-001-real-m2` — amend ENG-001, run FirewallChecker.scan(), fix real hits only
- **PR-C**: `chore/dead-code-quarantine` — per-module after import graph, not blocking publish
**Rationale**: Grok CLI's verdict is technically sound and verified by Kali's live probes. The 3-PR path is small, honest, reversible. Carmack's original 4-commit nuclear plan was wrong on M2 diagnosis, module paths, vault liveness, and strategy-doc requirements.
**Alternatives Considered**: Execute nuclear plan (rejected — would ship secrets, break heritage, delete live code, brick agent OS)
**Impact**: Initial PR scope frozen. Team clarity on path. No more scope churn.
**Reversible?**: Yes — git revert
**Supersedes**: Carmack's 4-commit nuclear plan (ho_29df6a4d77f2)
**Author**: Kali (ratified by Architect)
**Session**: `ses_vos_hybrid_plan_20260815`

---

### D-VOS-014: Reject Carmack's 4-Commit Nuclear Plan
**Date**: 2026-08-15
**Realm**: ALL (Meta)
**Decision**: Explicitly reject Carmack's original 4-commit nuclear plan (ho_29df6a4d77f2).
**Rationale**: Plan contained 6 fatal errors verified by Grok CLI and Kali's live probes:
1. M2 misdiagnosed (word count ≠ firewall violation)
2. Zero-ref module paths factually wrong
3. Vault is NOT dead code (30 files, 6+ live importers)
4. "0 code refs ⇒ delete strategy docs" wrong (AGENTS.md requires them)
5. VOS is yesterday's commit, not ancient theater
6. git add -A ships secrets, temple-grade thin, 1h15 fiction
**Alternatives Considered**: None — plan was fundamentally flawed
**Impact**: Prevents catastrophic damage. Establishes that grep-as-architecture is not acceptable.
**Reversible?**: N/A (rejection of unexecuted plan)
**Supersedes**: None
**Author**: Kali (ratified by Architect)
**Session**: `ses_vos_hybrid_plan_20260815`

---

### D-VOS-015: Amend ENG-001 (M2 Firewall Fix)
**Date**: 2026-08-15
**Realm**: ENGINE_CORE
**Decision**: Amend ENG-001 from "Remove 146 WAD term leaks from src/omega/" to:
> "M2 = stack-specific leaks, not token WAD. Run `FirewallChecker.scan()`. Fix real hits only (hardcoded entity names, `from config.wads.`)."
**Rationale**: The "146 WAD term leaks" claim was factually wrong. `FirewallChecker.scan()` = 0 errors, 0 warnings across 271 files. The test_firewall_m2.py failures are session headers (`⬡ OMEGA ⬡ ROC_RACOON ⬡`) and `source_entity="kali"` coordination metadata — NOT stack-specific logic. Grok CLI caught this as the load-bearing error.
**Alternatives Considered**: Keep ENG-001 as written (rejected — would execute mass rename based on false premise)
**Impact**: ENG-001 now reflects actual M2 enforcement. PR-B will fix real violations only.
**Reversible?**: Yes — git revert
**Supersedes**: ENG-001 in VISION_ANCHOR.md, realm state files, PHASE_0_BRIEF.md
**Author**: Kali (ratified by Architect)
**Session**: `ses_vos_hybrid_plan_20260815`

---

### D-VOS-016: Add TRACKING_ARCHITECTURE.md to Keep-List
**Date**: 2026-08-15
**Realm**: GOVERNANCE
**Decision**: Explicitly add `data/coordination/TRACKING_ARCHITECTURE.md` to the keep-list for PR-C (dead-code quarantine). It was omitted from Carmack's keep-list; Grok CLI caught this.
**Rationale**: TRACKING_ARCHITECTURE.md is the M27 constitution — the 5-tier tracking architecture that all agents must follow. Deleting it would brick the coordination system.
**Alternatives Considered**: None — omission was an error
**Impact**: TRACKING_ARCHITECTURE.md preserved in PR-C keep-list.
**Reversible?**: N/A (addition to list)
**Supersedes**: None
**Author**: Kali (ratified by Architect)
**Session**: `ses_vos_hybrid_plan_20260815`

---

### D-VOS-017: Log Carmack Mandate Violations to SYSTEM_FAILURE_LOG
**Date**: 2026-08-15
**Realm**: GOVERNANCE
**Decision**: Create `data/coordination/SYSTEM_FAILURE_LOG.md` and log Carmack's mandate violations from the rejected nuclear plan:
- M4 (cowboy sed across 344 sites)
- M23 (vault-delete-to-green = simulated rigor)
- M14 (heritage strip risk on wad_loader.py vet-043/044)
- M26/M27 (strategy-doc purge vs AGENTS.md requirements)
- M8 (git add -A ships secrets)
- False M2 (word count misdiagnosed as firewall violation)
**Note**: These were PROPOSED in a plan REJECTED before execution — caught by Grok CLI review. This is a near-miss worth logging honestly per M23 Failure Integrity.
**Rationale**: M23 requires logging failures to SYSTEM_FAILURE_LOG. A rejected plan with mandate-violating actions is a systemic near-miss. The pattern (grep-as-architecture, vanity counts, delete-the-failing-test) is recurring and must be documented.
**Alternatives Considered**: Not logging (rejected — M23 violation, pattern would repeat)
**Impact**: SYSTEM_FAILURE_LOG.md now exists with two entries (2026-07-06 researcher collapse, 2026-08-15 Carmack near-miss). Pattern documented.
**Reversible?**: Yes — file can be edited
**Supersedes**: None
**Author**: Kali
**Session**: `ses_vos_hybrid_plan_20260815`

---

### D-VOS-018: VOS Hybrid Plan (Option C) Approved
**Date**: 2026-08-15
**Realm**: ALL (Meta)
**Decision**: Approve Option C (Hybrid) for VOS future:
- **Keep**: `DECISION_LEDGER.md` (ADR pattern), `VISION_ANCHOR.md` (Vision SSOT)
- **Retire**: 7 realm state.yaml, 7 workspace briefs, `realm_cli.py`, Omegaverse realm (archive)
- **Add**: Realm contract validator in `make temple-grade`, realm sections in `HMC_COLLABORATION_HUB.md`, auto-generate VISION_ANCHOR realm health from ACTIVE_SPRINT.json
**Rationale**: Researcher (web) + Roc_Racoon (local) both confirmed: architecture sound (Team Topologies, ADR, DDD), implementation dead code (1/10 integration — zero code imports, zero runtime consumers, zero agent awareness). Hybrid keeps high-value artifacts, removes coordination overhead, adds enforcement.
**Alternatives Considered**: 
- A (Full Integrate — 15 hrs, over-engineering for current scale)
- B (Full Retire — loses ADR ledger + Vision SSOT, both proven valuable)
**Impact**: ~3 hrs implementation; removes ~17 dead files; adds CI enforcement via Hub.
**Reversible?**: Yes — git restore
**Supersedes**: D-VOS-001 (VOS instantiation) — modifies implementation, keeps architecture
**Author**: Kali (ratified by Architect)
**Session**: `ses_vos_hybrid_plan_20260815`

---

## 📊 Decision Summary (Updated)

| ID | Title | Realm | Reversible |
|----|-------|-------|------------|
| D-VOS-001 | VOS v1.0 Instantiation | ALL | No |
| D-VOS-002 | Session-End Hook Preserves Proposals | MEMORY | Yes |
| D-VOS-003 | Soul Validator — VALID_SOUL_VERSIONS | MEMORY/FLEET | Yes |
| D-VOS-004 | Soul Validator — LIVE_FEED→HUB | FLEET | Yes |
| D-VOS-005 | Mandate Header Correction | GOVERNANCE | Yes |
| D-VOS-006 | M22 SSOT Check Fix | ENGINE_CORE | Yes |
| D-VOS-007 | Context Packer Tuple Fix | ENGINE_CORE | Yes |
| D-VOS-008 | 96 Test Failures Triage | ALL | N/A |
| D-VOS-009 | Public Debut PR — 3-Phase Plan | COMMUNITY | No |
| D-VOS-010 | 7 Sovereign Realms | ALL | No |
| D-VOS-011 | PKEXEC Privilege Directive | FLEET | Yes |
| D-VOS-012 | Audit-First Approach | GOVERNANCE | Yes |
| D-VOS-013 | Ratify 3-PR Path | ALL | Yes |
| D-VOS-014 | Reject Nuclear Plan | ALL | N/A |
| D-VOS-015 | Amend ENG-001 | ENGINE_CORE | Yes |
| D-VOS-016 | TRACKING_ARCHITECTURE.md Keep-List | GOVERNANCE | N/A |
| D-VOS-017 | Log Mandate Violations | GOVERNANCE | Yes |
| D-VOS-018 | VOS Hybrid Plan (Option C) | ALL | Yes |

---

**This ledger is immutable. Append-only. Every decision references the vision and mandates.**

⬡ OMEGA ⬡ KALI ⬡ DECISION-LEDGER ⬡ 2026-08-15 ⬡ CANONICAL
