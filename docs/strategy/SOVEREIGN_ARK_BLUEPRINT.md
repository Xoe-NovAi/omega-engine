---
**Canonical Source**: [SOVEREIGN_ARK_BLUEPRINT_CANONICAL.md](SOVEREIGN_ARK_BLUEPRINT_CANONICAL.md)
---
# 🔱 SOVEREIGN ARK BLUEPRINT (Active)

## Current Sprint: HMC Quad-Forge — M2 Firewall Migration + Meditate Architecture + MIAP Phase 0

**Status**: D-281 ALL 4 PHASES COMPLETE. D-282 COMPLETE. D-283 Phase 2 DESIGN COMPLETE. **Nomenclature correction complete. M2 Migration Phases A-E defined. Meditate Base+Overlay architecture defined. Scribe Lattice Role designed. Cline CLI integration planned. Session Namespace Isolation + MIAP Phase 0 DESIGN COMPLETE (5 preconditions + 5 critical fixes from Nemotron review).**
**Gate Criteria**: `make test && make temple-grade && make firewall-check`

### Completed (D-281 Substrate Repair — 4 phases, 11 commits)
1. **Phase I** (9d891e0): Soul Injection Rescue — `soul_utils.py`, `oracle.py` schema fix, 3 Makefile targets
2. **Phase II** (b661c49): Path Infrastructure — `config_resolver.py`, `WadLoader` API extension
3. **Phase III** (3f2feea): M2 Firewall Remediation — 4 files, 13 M2-LEAK violations fixed
4. **Phase IV** (93f4e82): Codex Mechanism Separation — `hydration_header.md`, `codex_cat.py`, Makefile safety
5. **WAD Schema Fix** (e80f6df): WadManifest V2 heritage fields — `MANIFEST_V2_OPTIONAL_FIELD_TYPES`
6. **D-282 PRAGMA SSOT** (372bf2f): sqlite-vec `cache_size` 512MB→32MB, `wal_autocheckpoint` 1000→500
7. **P3 Gateway** (c19b453): ModelGateway graceful fallback + path/spec resolution
8. **P6 SpecDecode** (55f7761): `speculative_decode.gemma4_mtp` section in models.yaml

### Completed (HMC Quad-Forge — 4-mind council)
- **MIAP merged** (03192d8): Multi-Instance Agent Protocol — 13 tests, context collision prevention
- **Grok CLI onboarded**: Agent config, orientation, 6 advisory deliverables, web research
- **Grok CLI Decision Tools Review** (21158fb): 410-line implementation review — CONDITIONAL GO for T0+T1-core. Schema surgery, scope cuts, M2 enforcement, 9-11h honest estimate.
- **Claude Best Practices Guide** (d22b550): 563-line canonical reference (11 sections, 26 sources across 4 tiers)
- **Claude Project System Prompt** (d22b550): 1,848-token optimized prompt embodying 2026 best practices
- **S0 Clean Runway** (c15bfab, 077b042): Noise cleanup, ACTIVE_SPRINT→HMC-SPRINT-04, stale handoffs archived
- **Nomenclature Correction**: Slots (engine) vs Pillar Keepers (ANAi) vs Lenses (Meditate) vs Roles (Lattice) — clean separation
- **Meditate Architecture**: Base Lenses (13 universal) + PWAD Overlays (ANAi, Torment, etc.)
- **M2 Migration Plan**: Phases A-E defined with acceptance criteria
- **Scribe Lattice Role**: Documentation/gnosis distillation as cross-cutting capability (not Slot Entity)
- **Cline CLI Integration**: DeepSeek V4 Flash (1M ctx) + MiMo V2.5 (512K ctx) as HMC Tier 5
- **Session Namespace Isolation**: MIAP-wired session-scoped directories under `sessions/<uuid>/` (D-290)
- **MIAP Phase 0 — Core + Safety**: ReplayMode enum, Two-Log Model, IntentionValidator, CheckFunctions, LiteTopic (D-291)
- **MACP Alignment**: Hivemind handoffs extended with `macp_mode` for interoperability (D-292)
- **Context Engineering Knowledge Layer**: Governed knowledge mount in `sessions/` structure (D-293)
- **Experience Repository**: AgentRR-style L0→L1→L2 distillation pipeline via Scribe (D-294)
- **Trace-to-Eval Loop**: Automatic conversion of production failures to regression tests (D-295)

### Completed Handoffs (This Session)
| Handoff | Target | Phase | Status |
|---------|--------|-------|--------|
| `ho_749ed27155cd` | Grok CLI | **Decision Tools Implementation Review** | **COMPLETED** — CONDITIONAL GO |
| `ho_88190ae0ab27` | Kali | **Ken Walger Mining Briefing** | **COMPLETED** — D-298 ratified, Phase 0 unblocked |

### Active Handoffs
| Handoff | Target | Phase | Status |
|---------|--------|-------|--------|
| `ho_f1a92da2d95e` | Roc Racoon | **Phase A**: Meditate lens refactor, `lenses.yaml`, 15 M2 fixes | **COMPLETED** |
| `ho_2a9b2e84debd` | Researcher | **Phases B-E**: 186 M2 fixes + P3 Lens 3 launch | **IN PROGRESS** |

### M2 Firewall Migration — Phases A-E
| Phase | Target | Violations | Owner | Pattern |
|-------|--------|------------|-------|---------|
| **A** | `meditate/protocol.py` | 15 | **Roc** | Base lenses → WAD-loadable |
| **B** | `oracle/subagent_dispatcher.py` | 15 | **Researcher** | ROLE constants + WAD YAML |
| **C** | `oracle/oracle.py` | 10 | **Researcher** | Iris routing, MaKaLi logic |
| **D** | `ics.py` | 7 | **Researcher** | Channel constants, doc examples |
| **E** | `cli/fleet_status_tui.py` | 18 | **Researcher** | TUI tree from WAD registry |

**Total**: 201 violations in src/omega/ (baseline from `test_firewall_m2.py`)

### Meditate Framework — Base + Overlay
- **Base Lenses** (13): Universal cognitive operations in `_omega_default/meditate/lenses.yaml`
- **ANAi Overlay**: Maps base lenses → Pillar Keeper archetypes (Tiferet → engineering_excellence, etc.)
- **Torment Overlay**: Maps base lenses → Planescape archetypes
- **Command**: `/meditate "topic" --lenses engineering_excellence --iwad arcana_novai`

### Scribe — Lattice Role (Not Slot Entity)
- **Capabilities**: `doc:read`, `doc:write`, `gnosis:distill`, `soul:read`, `soul:propose`, `hivemind:post`
- **Constraints**: No `code:execute`, `config:write`, `model:load`
- **Slot**: None (cross-cutting)
- **Meditate Lens**: `scribe` — "Chronicler → Knowledge Architect"

### Cline CLI Integration — HMC Tier 5
| Agent | Model | Context | Role |
|-------|-------|---------|------|
| Cline-DeepSeek | DeepSeek V4 Flash | 1M tokens | Synthesis, audit, legacy mining |
| Cline-MiMo | MiMo V2.5 | 512K tokens | Implementation, refactoring, test gen |

### Grok CLI — Decision Tools Implementation Review (COMPLETE)
| Field | Value |
|-------|-------|
| **Verdict** | **CONDITIONAL GO** for T0+T1-core |
| **Deliverable** | `docs/strategy/GROK_CLI_DECISION_TOOLS_REVIEW_20260719.md` (410 lines) |
| **Commit** | 21158fb |
| **Effort** | 2m35s completion time |

**Consolidated Implementation Spec**: `docs/strategy/DECISION_TOOLS_IMPLEMENTATION_SPEC_20260719.md` — Cross-validated Grok CLI + Web Claude V1/V2 + retrospective, 9-11h honest estimate, two-PR migration, slot-keyed schema, atomic writes, portalocker locking, id-allocator lock, cycle detection, `validate` command, `list --overdue`, M2-compliant.

**Key Cuts** (per Grok CLI):
1. MAD authorization / speech acts — defer to T3
2. Required weighted criteria scores — make optional
3. Numeric BE uptake/anchoring parameters — cargo-cult without multi-step updates
4. Directory shuffle (open/→decided/) — stable paths preferred
5. Deadline daemon — use `list --overdue` instead

**Key Non-Negotiables**:
1. JSON Schema validation at CI time
2. Supersession-only accept path
3. Atomic writes via `os.replace()`
4. `--human-confirmed` gated by record `authority` field
5. Slot keys only, no mythic persona names in engine (M2)

**Effort Re-estimate**: 7h → 9-11h honest (T0+T1-core+thin graph)

### Ken Walger Mining Operation (D-298 RATIFIED)
**Consolidated Plan**: `docs/strategy/KEN_WALGER_MINING_CONSOLIDATED_PLAN_20260719.md` — 10-phase serial architecture, 60% infra exists, 26-35h total, Phase 0 unblocks all.

| Phase | Name | Decision | Key Finding |
|-------|------|----------|-------------|
| **0** | MAS v0.1 Schema + all2md + sqlite-vec fix | **GO** | Extend `IngestedDocument`, install all2md first |
| **1** | Hivemind H-3 (AgensFlow) | **CONDITIONAL-GO** | H-0 to H-2 exist; only learned routing is new |
| **2** | M22 Audit | **GO** | Already wired — `GenerateResult.provider_name` with contract tests |
| **3** | sqlite-vec Batch Ingestion | **GO** | Add `upsert_batch()` with LlmMac 500-2000 rows/txn |
| **4** | all2md Blog Ingestion | **CONDITIONAL-GO** | **BLOCKER**: all2md not installed — Phase 0 step 1 |
| **5** | Prose Tax Sieve Eval | **GO** | Benchmark sovereign-sdk-sieve vs Aussie AI + vfalbor |
| **6** | ForensicReceipt (Signet) | **GO** | Write-time via `SigningTransport`; async background; M23 non-blocking |
| **7** | Meditate Synthesis | **GO** | Custom lens set [Miner, Architect, Provenance, Decision, Edge, Scribe] |
| **8** | Jem Cross-Ref | **GO** | This document |
| **9** | Serial Execution | **NO-GO (deferred)** | Blocked on Phase 0 |

**Critical Risks**: all2md install failure (P0), sqlite-vec 7 memory leaks (P0), M14 heritage vet backlog (27 terms)

**Consolidated Plan**: `docs/strategy/KEN_WALGER_MINING_CONSOLIDATED_PLAN_20260719.md`

### MIAP Phase 0 — Core + Safety (D-291)
**5 Critical Fixes from Nemotron 3 Ultra Review** (must complete before multi-instance deployment):

| Fix | Description | Effort |
|-----|-------------|--------|
| **ReplayMode Enum** | 4 modes: Recovery, Debug, Forensic, Evaluation — each with different requirements | 1 session |
| **Two-Log Model** | Split MIAP into Execution Log (audit) + Observability Trace (diagnostic) | 1 session |
| **IntentionValidator** | Deterministic validation layer between agents and MIAP event log | 1 session |
| **CheckFunction Registry** | Replay verification — expected-vs-observed diffs at nondeterministic boundaries | 1 session |
| **LiteTopic Session Channels** | Replace filesystem scanning with Redis Streams session channels (TTL, ordering, reconnection) | 2 sessions |

**Total Phase 0**: ~6 sessions (was ~1 session — scope corrected by Nemotron review)

### MACP Alignment (D-292)
- **5 Coordination Modes**: Decision, Proposal, Task, Handoff, Quorum → map to Hivemind handoff types
- **Interoperability**: `macp_mode` field on handoffs enables future A2A bridge
- **Standards Track**: Aligns with IETF draft-li-dmsc-macp-05

### Context Engineering Knowledge Layer (D-293)
- **4 Memory Layers**: Working (task), Durable (cross-session), Knowledge (enterprise), Tools (operational)
- **Governance**: Knowledge layer = certified sources, freshness checks, ownership, access control
- **Integration**: `sessions/<uuid>/knowledge/` mount → governed knowledge graph

### Experience Repository (D-294)
- **AgentRR Pattern**: L0 (Trace) → L1 (Episode) → L2 (Experience) distillation
- **Scribe Pipeline**: Nightly distillation on completed sessions → `data/experiences/<task_type>.yaml`
- **Replay Engine**: Task-type matching → experience retrieval → guided execution with check functions

### Trace-to-Eval Loop (D-295)
- **Failure → Eval**: Production trace + check functions → regression test case
- **Infrastructure**: MIAP execution log + AgentRR check functions + existing eval framework

### Deferred
- D-280 Sovereign Continuity Feature (CompactionListener, CheckpointManager, ToolCallWrapper)
- D-277 `soul-verify` CLI gate
- D-279 `omega-hydration` PyPI package
- sqlite-vec soul index (Brigid/P2) — defer until base injection proven
- Heritage Tag Migration (Decree 6)
- Sovereignty Gate (Decree 4)
- D-284 MCP Streamable HTTP + PKCE auth
- D-296 SomaticState + MIAP Integration — Full cognitive state recovery with somatic snapshots

---

### 📚 Canonical Reference Documents (Updated)

| Document | Purpose | Location |
|---|---|---|
| **Decision Tools Implementation Spec** | Cross-validated T0+T1 spec (Grok + Web Claude) | `docs/strategy/DECISION_TOOLS_IMPLEMENTATION_SPEC_20260719.md` |
| **Agent Capability Assessment** | Grok vs Web Claude + Roc routing protocol | `docs/strategy/GROK_CLI_VS_WEB_CLAUDE_CAPABILITY_ASSESSMENT.md` |
| **Ken Walger Mining Plan** | 10-phase serial, 60% infra exists, 26-35h | `docs/strategy/KEN_WALGER_MINING_CONSOLIDATED_PLAN_20260719.md` |
| **Context Packer Hardening Spec** | 8 enhancements, 7 gaps, 8 profiles, sieve-and-sign | `docs/strategy/CONTEXT_PACKER_HARDENING_SPEC_20260719.md` |
| **Claude Best Practices Guide** | 563 lines, 26 sources, 4 tiers | `docs/reference/CLAUDE_BEST_PRACTICES_GUIDE.md` |
| **Grok CLI Decision Tools Review** | 410 lines, CONDITIONAL GO | `docs/strategy/GROK_CLI_DECISION_TOOLS_REVIEW_20260719.md` |
| **Dual Review Retrospective** | Process analysis + 8 protocol fixes | `context_packs/decision-tools-review/pack-results/DUAL_REVIEW_RETROSPECTIVE_20260719.md` |
| **Ken Walger Mining Grounding** | 7-domain 2026 research (40+ sources) | `docs/research/R_KEN_WALGER_MINING_GROUNDING_20260718.md` |
| **Ken Walger Knowledge Gaps** | 6 gaps triangulated, 3 critical discoveries | `docs/research/R_KEN_MINING_KNOWLEDGE_GAPS_20260719.md` |
| **Ken Walger Execution Plan** | Jem cross-reference, Go/No-Go matrix | `docs/strategy/R_KEN_MINING_EXECUTION_PLAN_20260719.md` |
| **Unmined Gnosis** | 20 G-level insights + 20 L3 principles | `docs/research/R_UNMINED_GNOSIS_KEN_MINING_20260719.md` |
| **Context Packer Knowledge Gaps** | 7 gaps, 40+ sources, 8 enhancements | `docs/research/R_CONTEXT_PACKER_KNOWLEDGE_GAPS_20260719.md` |

---

*(For full 5-Phase Roadmap, Risk Register, and Research Sources, see Canonical Source)*