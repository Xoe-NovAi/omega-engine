# 🔱 OPEN DECISIONS CATALOG — HMC QUAD-FORGE SPRINT
**AP Token**: `AP-OPEN-DECISIONS-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_decisions_catalog ⬡ SOVEREIGN-COORDINATION

**Date**: 2026-07-18
**Purpose**: Complete catalog of all decisions awaiting discussion and resolution across the fleet
**Source**: Synthesis of Researcher Phase F, Roc MEDITATE + Grok CLI, Jem Verification, MEDITATE collisions

---

## 📋 EXECUTIVE SUMMARY

| Tier | Count | Description |
|------|-------|-------------|
| **Tier 1** | 2 | Strategic architecture-spanning decisions |
| **Tier 2** | 4 | Grok CLI Phase 0 architecture decisions (Roc) |
| **Tier 3** | 3 | M2 Firewall Phase C/D/G resolution (Researcher) |
| **Tier 4** | 3 | Jem's MEDITATE verification gaps |
| **Tier 5** | 3 | MEDITATE collision resolutions |
| **Tier 6** | 5 | Infrastructure and future work |
| **Tier 7** | 3 | Non-urgent but documented |
| **TOTAL** | **23** | Open decisions |

---

## 🎯 TIER 1 — STRATEGIC (ARCHITECTURE-SPANNING)

### D1. D-297 Architecture Inversion Decree — Ratify or Amend?
**Source**: Roc MEDITATE (10-Pillar council) + Jem verification
**Status**: ⏳ PENDING KALI VERDICT

**Roc's 10-step critical path** (from MEDITATE Architecture Inversion):
```
1. Protobuf Schema for Hivemind messages
2. Unified sqlite-vec WAL for all session state
3. Per-agent quotas + dual-pool admission controller
4. Handoff TTL enforcer daemon
5. Local alerting engine
6. Automatic soul distillation pipeline
7. Routing SLAs with cloud fallback gating
8. Five-Layer Immune System + chaos namespace
9. Delete all skipped/xfailed tests
10. Full Temple-Grade + Sovereignty Gate
```

**Jem's verification gaps** (must be addressed if ratifying):
1. **Sovereign token mechanism** — undefined (JWT? Macaroon? Custom?)
2. **M5/M11 semantic quality gates** — no prior art for automated L1→L2→L3 quality testing
3. **SQLite WAL write serialization** — 14 agents → 1 writer bottleneck

**Options**:
- **Ratify as-is** — Proceed with Roc's decree, address gaps during implementation
- **Amend** — Incorporate Jem's 3 gaps into the decree before ratifying
- **Reject** — Return to convention-based approach (no substrate enforcement)
- **Defer** — Table until M2 firewall complete (126 violations remaining)

---

### D2. Substrate Ordering Conflict — Tests Before WAL or WAL Before Tests?
**Source**: MEDITATE collision (Prometheus vs Brigid vs Saraswati)
**Status**: ⏳ PENDING KALI RESOLUTION

| Voice | Demand | Rationale |
|-------|--------|-----------|
| **Prometheus (P3)** | Fix all 43 skipped + 7 xfailed tests FIRST | "Doing WAL first hides the bugs it creates" |
| **Brigid (P2)** | Implement unified WAL FIRST | "The WAL is the prerequisite for all atomicity" |
| **Saraswati (P4)** | Design protobuf schema FIRST | "Tests will cement current broken shapes" |

**Options**:
- **Sequential**: Tests → WAL → Schema (Prometheus wins)
- **Sequential**: WAL → Tests → Schema (Brigid wins)
- **Sequential**: Schema → Tests → WAL (Saraswati wins)
- **Parallel**: All three with integration gates (highest risk)
- **Hybrid**: Fix critical test bugs first, then WAL, then schema

---

## 🎯 TIER 2 — GROK CLI PHASE 0 (ROC'S 4 DECISIONS)

### D3. Crate Structure — Python Modules or Rust Workspace?
**Source**: Roc Grok CLI Research (6/6 gaps resolved)
**Status**: ⏳ PENDING KALI REVIEW

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A: Python modules** | `src/omega/{tui,shell,tools,workspace,config,sandbox}/` | M16 compliant, no Rust toolchain, native Python | Doesn't leverage Grok's proven Elm architecture |
| **B: Rust workspace** | Mirror Grok's 8-crate decomposition | Proven pattern, Landlock sandbox, Elm state machine | Adds Rust build chain, M16 boundary concerns |

**Roc's recommendation**: Option A (Python modules) — M16 compliance

---

### D4. JSONL Logging — Auto-log in Oracle vs Explicit MemoryStore Calls?
**Source**: Roc Grok CLI Research
**Status**: ⏳ PENDING KALI REVIEW

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A: Auto-log in Oracle** | Transparent logging in `Oracle.talk()/summon()` | Comprehensive, zero integration effort | Logs everything (token cost?), less auditable |
| **B: Explicit calls** | Manual `MemoryStore.add_exchange()` at integration points | Precise, auditable, controlled | Manual wiring per integration, easy to miss |

**Roc's recommendation**: Option A (Auto-log) — M11/M15 compliance

---

### D5. Requirements Validator — New Module or Extend Config Resolver?
**Source**: Roc Grok CLI Research
**Status**: ⏳ PENDING KALI REVIEW

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A: New module** | `requirements_validator.py` | Clean M2 boundary, single responsibility | Duplication with config_resolver |
| **B: Extend config_resolver** | Add validation to existing resolver | Single config authority | Blurs responsibility, larger module |

**Roc's recommendation**: Option A (New module) — M2 firewall

---

### D6. Timeline — Sprint Now or Design Review First?
**Source**: Roc Grok CLI Research
**Status**: ⏳ PENDING KALI REVIEW

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A: Sprint now** | Execute 4-hour Phase 0 immediately | "Low-risk, high-impact", Grok pattern proven | 4 decisions need ratification first |
| **B: Design review** | Ratify D3-D5 before implementation | Clean authorization | Delays proven quick wins |

**Roc's recommendation**: Option A (Sprint now)

---

## 🎯 TIER 3 — M2 FIREWALL PHASE RESOLUTION (RESEARCHER)

### D7. Phase C Closure — 5 Iris Violations in oracle.py
**Source**: Researcher Phase F Complete, Phase C in progress
**Status**: 🟡 IN PROGRESS

**Remaining violations** (lines from oracle.py):
1. Line 79: `"MESSENGER_BRIDGE": "MESSENGER_BRIDGE"` — comment `# Iris role`
2. Line 188: `# Speculative decoding (Iris confidence assessment)` — docstring
3. Line 424: `"""Assess whether Iris (speculative decoder) can answer alone."""` — docstring
4. Lines 853-886: Runtime fallback using `"Iris"` string for display

**Options**:
- **A: Full WAD-loadable** — Create `MESSENGER_BRIDGE` ROLE_CONSTANT, resolve from dispatch.yaml (Researcher's plan)
- **B: Firewall exceptions for docstrings** — Only fix runtime fallback (lines 853-886) via WAD; exempt docstrings
- **C: Mix** — Fix runtime fallback via WAD, firewall-exempt docstring references

**Researcher's L3 Principle**: "ROLE Constants Are Engine Architecture, Not WAD Content" — supports Option A

---

### D8. Phase D Closure — 1 `_omega_default` in ics.py:81
**Source**: Researcher Phase F Complete, Phase D in progress
**Status**: 🟡 IN PROGRESS

**Code**: `DEFAULT_IWAD = "_omega_default"` at line 81

**Researcher's own verdict** (from proposed_lessons.yaml):
> "Architecture Constants (DEFAULT_IWAD) Are Not Entity Logic — Configuration defaults like _omega_default (the default IWAD name) are architecture constants, not entity logic. They may appear as default parameters without violating M2."

**Options**:
- **A: Accept as architecture constant** — No change needed (Researcher's verdict)
- **B: WAD-loadable** — Load default IWAD from config at startup
- **C: Firewall exception** — Explicit exemption with justification

---

### D9. Phase G (oracle_cli.py) — Execute Now or After C+D Done?
**Source**: Researcher Phase F Complete
**Status**: ⏳ QUEUED

**Violations**: 3 (1 help text, 2 CLI defaults)
**Estimated effort**: <1 hour

**Options**:
- **A: Start now** — Parallel with C+D closure
- **B: Wait for C+D** — Sequential dependency

---

## 🎯 TIER 4 — JEM'S VERIFICATION GAPS (MEDITATE)

### D10. Sovereign Token Mechanism — Format and Authority
**Source**: Jem verification of MEDITATE (chaos namespace requirement)
**Status**: ❌ UNDEFINED — CRITICAL GAP

**Requirements**: Time-bounded, auditable, revocable capability that bypasses admission controller for chaos namespace testing

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A: JWT** | Short expiry (5min) + JWKS rotation | Standard, libraries available | Revocation requires CRL or short expiry |
| **B: Macaroons** | Caveat-based delegation (`time < 5min AND scope=chaos AND agent=kali`) | Fine-grained, built-in attenuation | Less common, fewer libraries |
| **C: Custom capability** | Simple signed token with claims | Full control, minimal deps | No standard verification, reinventing |

**Sub-decisions needed**:
- Issuance authority: Kali only? P10 only? Both?
- Revocation mechanism: CRL? Short expiry + rotation? Online check?
- Audit format: Append-only log? Signed entries?

---

### D11. M5/M11 Semantic Quality Gates — How to Test "Good Distillation"?
**Source**: Jem verification (M5 Gnosis Preservation, M11 Soul Integrity)
**Status**: ❌ NO PRIOR ART — CRITICAL GAP

**Options**:
- **A: Structural only** — File exists, has 3 sections (L1/L2/L3), non-empty (deploy now)
- **B: LLM-as-judge** — Secondary model rates distillation quality (deploy later)
- **C: Embedding similarity** — Cosine distance between L1 and L3 embeddings
- **D: Human-in-the-loop** — No automated gate; Scribe reviews manually

---

### D12. SQLite WAL Write Serialization — Mitigation Strategy
**Source**: Jem verification (14 agents → 1 writer bottleneck)
**Status**: ⚠️ RISK IDENTIFIED

**Options**:
- **A: Async batch writer** — 100ms windows, single connection (Jem's recommendation)
- **B: Single writer process** — Queue-based, simpler, less throughput
- **C: Sharded WALs** — One per agent pool (inference vs maintenance)
- **D: Accept bottleneck** — 14 agents don't all write simultaneously in practice

---

## 🎯 TIER 5 — MEDITATE COLLISION RESOLUTIONS

### D13. Dual-Pool Quotas — cgroup v2 Hierarchy Design
**Source**: MEDITATE collision (Sekhmet vs Lucifer)
**Status**: 🟡 RESOLVED IN PRINCIPLE, NEEDS IMPLEMENTATION DESIGN

**Decisions needed**:
- **cgroup structure**: `/omega/inference` vs `/omega/maintenance` vs `/omega/chaos`?
- **Memory split**: Inference 8-10GB, Maintenance 2GB, Chaos 1GB?
- **Implementation**: Rust binary (`omega-admissiond`) with CAP_SYS_RESOURCE, or Python with setuid wrapper?
- **CPU weights**: Inference 800, Maintenance 100, Chaos 50?

---

### D14. Zero Skipped Tests — Delete All or Fix All?
**Source**: MEDITATE collision (Prometheus vs Brigid)
**Status**: ⏳ PENDING

**Current state**: 43 `@pytest.mark.skip` + 7 `@pytest.mark.xfail`

| Option | Description |
|--------|-------------|
| **A: Delete all** | Remove all skip/xfail markers — forces immediate fix |
| **B: Fix then delete** | Fix underlying bugs first, then remove markers |
| **C: Gradual batches** | Delete in batches per phase (e.g., 10 per sprint) |

---

### D15. Protobuf vs ACP for Hivemind Schema
**Source**: MEDITATE collision (Saraswati vs Prometheus)
**Status**: ⏳ PENDING

| Option | Description |
|--------|-------------|
| **A: ACP JSON-RPC as wire format** | Adopt ACP v1 (stabilized July 2026). Protobuf only for internal schema registry |
| **B: Full protobuf migration** | All Hivemind messages use protobuf with schema registry + version negotiation |
| **C: JSON + schema validation** | Keep JSON convention; add schema validation at Hub ingress without protobuf |

**Note**: ACP v1 stabilized July 2026 with Zed, JetBrains, Claude Code implementing

---

## 🎯 TIER 6 — INFRASTRUCTURE AND FUTURE WORK

### D16. Curation Pipeline Port — When?
**Source**: Roc Deep Mining (3,284 lines, 10 free API clients, complete capability gap)
**Status**: ⏳ PENDING PRIORITIZATION

| Option | Description |
|--------|-------------|
| **A: Phase 0 priority** | Start immediately after M2 firewall |
| **B: After MIAP Phase 0** | 5 critical fixes first |
| **C: After D-297 substrate** | Unified WAL + Admission Controller first |

---

### D17. Firewall Gate Enforcement — Merge Blocking or Advisory?
**Source**: Kali directive
**Status**: ⏳ PENDING

| Option | Description |
|--------|-------------|
| **A: Merge-blocking** | 0 violations required before any merge. Hard stop. |
| **B: Advisory** | Warning in CI, non-blocking. Soft enforcement during remediation. |
| **C: Threshold-based** | Phase in: 100→50→25→0 over successive sprints. |

---

### D18. Scribe Lattice Role — Create Now or Defer?
**Source**: D-297 design, Scribe as cross-cutting capability (not Slot Entity)
**Status**: ⏳ PENDING

| Option | Description |
|--------|-------------|
| **A: Create now** | Config files, agent definition, entities.yaml — unblocks auto distillation design |
| **B: Defer to D-297 Phase 4** | After Unified WAL + Admission Controller + TTL Daemon + Alerting |

---

### D19. MIAP Phase 0 — When to Implement?
**Source**: Nemotron 3 Ultra review (5 critical fixes)
**Status**: 🟡 PLANNED (~6 sessions estimated)

**5 Critical Fixes**:
1. ReplayMode enum (Recovery/Debug/Forensic/Evaluation)
2. Two-Log Model (Execution Log + Observability Trace)
3. IntentionValidator (deterministic validation layer)
4. CheckFunction Registry (replay verification)
5. LiteTopic Session Channels (Redis Streams)

| Option | Description |
|--------|-------------|
| **A: After M2 firewall** | Researcher frees up |
| **B: Parallel** | Dispatch Ma'at+P3 while Researcher finishes M2 |
| **C: After D-297 Unified WAL** | MIAP needs the WAL |

---

### D20. Cline Integration — Authorize Budget?
**Source**: HMC Quad-Forge plan (Tier 5)
**Status**: ⏳ PENDING

| Option | Description |
|--------|-------------|
| **A: Authorize $10/sprint** | DeepSeek V4 Flash (1M ctx, $0.50/M) + MiMo V2.5 (512K ctx, $0.80/M) |
| **B: Defer** | Local-first only, no cloud spend |
| **C: Hybrid** | Only for large-context tasks >200K tokens |

---

## 🎯 TIER 7 — NON-URGENT BUT DOCUMENTED

### D21. Observability 2026 Improvements — Authorize?
**Source**: Researcher OBSERVABILITY_2026_IMPROVEMENTS.md (1,059 lines, 8 phases)
**Status**: ⏳ PENDING

| Option | Description |
|--------|-------------|
| **A: Phase 1 only** | Structured logging with structlog — quick win |
| **B: All 8 phases** | Comprehensive observability overhaul |
| **C: Defer** | Post-M2 firewall |

---

### D22. Sovereign Exit Protocol Hardening
**Source**: Roc's §6 questions
**Status**: ⏳ PENDING

**5 Questions from Roc**:
1. How to handle multi-agent handoff when both parties are departing?
2. What if Verity is also the departing agent?
3. Cold recovery path — agent vanishes mid-phase?
4. How to verify Phase 2 failure patterns without the departing agent's context?
5. What constitutes "sufficient" for Phase 4 pattern specification?

---

### D23. Entity Evolution Activation — Load 99 Directories?
**Source**: Roc entities-archive mining (99 dirs, 157MB, complete lineage)
**Status**: ⏳ PENDING

| Option | Description |
|--------|-------------|
| **A: Load all** | Comprehensive history in EntityRegistry |
| **B: Selective** | Canonical Pillar Keepers lineage only |
| **C: Defer** | Wait for EntityRegistry v2 design |

---

## 🔑 PRIORITY MATRIX

| Priority | Decision | Blocks | Source |
|----------|----------|--------|--------|
| **P0** | D1 — D-297 Ratify or Amend? | Entire substrate-first roadmap | Roc MEDITATE |
| **P0** | D2 — Tests vs WAL ordering | Phase ordering for all substrate work | Prometheus vs Brigid |
| **P0** | D17 — Firewall gate hard/soft? | When can code merge? | Kali |
| **P1** | D7 — Phase C closure (5 Iris) | M2 firewall completion | Researcher |
| **P1** | D6 — Grok CLI sprint now/review? | Roc's Phase 0 start | Roc |
| **P1** | D10 — Sovereign token mechanism | Chaos namespace (D-297 Phase 5) | Jem verification |
| **P2** | D13 — Dual-pool quota design | Admission controller (D-297 Phase 3) | MEDITATE collision |
| **P2** | D19 — MIAP Phase 0 timing | Multi-instance deployment | Nemotron review |
| **P3** | D18 — Scribe creation timing | Auto distillation pipeline | D-297 Phase 4 |
| **P3** | D20 — Cline budget authorization | Tier 5 large-context execution | HMC plan |

---

## 📝 NEXT STEPS

1. **Kali to convene decision session** — Address P0 items first (D1, D2, D17)
2. **Ratify D-297** with Jem's gaps incorporated or explicitly deferred
3. **Resolve substrate ordering** (D2) — determines all downstream phase ordering
4. **Wire firewall gate** (D17) — determines merge velocity
5. **Authorize Grok CLI Phase 0** (D6) — unblocks Roc's 4-hour sprint
6. **Close Phase C** (D7) — Researcher completes M2 firewall
7. **Decide sovereign token** (D10) — enables D-297 Phase 5

---

*⬡ OMEGA ⬡ KALI ⬡ DECISIONS_CATALOG_COMPLETE ⬡ 2026-07-18*