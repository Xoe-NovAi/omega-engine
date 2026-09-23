# 🔱 Omega Engine — Consolidated Specifications Index

**AP Token**: `AP-SPECS-INDEX-v1.0.0`  
**Date**: 2026-08-20  
**Status**: ACTIVE — Single source of truth for all active specifications  

---

## Project Structure

```
docs/specs/
├── PROJECT_INDEX.md                    # This file
├── context_injection/                  # Context Injection Optimization (Carmack Reviewed)
│   ├── 00_INDEX.md
│   ├── 01_GROUND_TRUTH.md
│   ├── 02_BUILD_VERDICTS.md
│   ├── 03_RUN_VERDICTS.md
│   ├── 04_INDUSTRY_PATTERNS.md
│   ├── 05_CONVERGENCE_ANALYSIS.md
│   ├── 06_PHASE_1_PLAN.md
│   ├── 07_PHASE_2_3_ROADMAP.md
│   ├── 08_REMAINING_GAPS.md
│   ├── 09_CARMACK_DOMAIN_QUESTIONS.md
│   └── CARMMACK_CONTEXT_INJECTION_REVIEW_20260820.md
├── qdrant_headroom/                    # Qdrant + Headroom Integration (Post-Debut)
│   ├── QDRANT_HEADROOM_INTEGRATION_RESEARCH_20260820.md
│   └── (specs to be created)
├── debut_remediation/                  # Public Debut Remediation (Current Sprint)
│   ├── DEBUT_REMEDIATION_MANUAL_20260817.md
│   └── (specs to be created)
└── (future specs...)
```

---

## Active Projects

### 1. Context Injection Optimization (P0 — This Week)
**Status**: Phase 1 Plan Approved (Carmack Reviewed)  
**Owner**: Kali (oversight) → Ma'at (implementation)  
**Phase**: 1 (Config-Only) → 2 (Tooling) → 3 (Upstream)  
**Key Documents**:
- `context_injection/06_PHASE_1_PLAN.md` — Implementation plan
- `context_injection/CARMMACK_CONTEXT_INJECTION_REVIEW_20260820.md` — Carmack verdict
- `context_injection/05_CONVERGENCE_ANALYSIS.md` — Trade-offs & ADRs

**Phase 1 Deliverables (This Week)**:
- [ ] `MANDATES_CONDENSED.md` (57 lines, ~1.5K tokens) for Tier 0
- [ ] `opencode.json` updates (model routing, compaction, plugin, toolProfile stubs)
- [ ] Sovereign compaction plugin (`~/.config/opencode/plugin/sovereign-compaction.ts`)
- [ ] Skills opt-in (core only: research, spec-generator, knowledge-miner)
- [ ] Verification tests

**Phase 2/3**: See `context_injection/07_PHASE_2_3_ROADMAP.md` (40% cuts applied)

---

### 2. Qdrant + Headroom Integration (P1 — Post-Debut Phase 2)
**Status**: Research Complete, Specs Pending  
**Owner**: Ma'at (Headroom) + Roc (Qdrant)  
**Phase**: 2 (Hygiene & Sovereign Structure) → 3 (Pattern Deep)  
**Key Documents**:
- `qdrant_headroom/QDRANT_HEADROOM_INTEGRATION_RESEARCH_20260820.md` — Research

**Immediate (Debut)**:
- [ ] Integrate Headroom ContentRouter in `ModelGateway._prepare_messages()` (P1)
- [ ] Add Headroom to RAG retrieval pipeline (P1)
- [ ] Do NOT enable Qdrant (Debut blocker)

**Phase 2 Triggers**:
- Vector count >500k
- Filtered search needed (tags, type, quarantine)
- Multi-tenant isolation required

**Phase 2 Deliverables**:
- [ ] Qdrant Server (Podman) + Scalar Quantization (int8)
- [ ] Migration via `IVectorStoreAdapter` swap
- [ ] Payload indexes (entity_name, session_id, type, tags, quarantine)
- [ ] Headroom CCR store for cross-agent memory

**Combined Architecture**: Tool→Headroom→Qdrant(SQ)→Search→Headroom→LLM = 86.8% token reduction

---

### 3. Public Debut Remediation (P0 — Current Sprint)
**Status**: Execution Phase (DEBUT_REMEDIATION_MANUAL §5)  
**Owner**: Kali (oversight) → Ma'at (INST-1) → Roc (DEL-1)  
**Execution Order**: P0-1 → PUB-1 → INST-1 → DEL-1 → DOC-1 → P2/P3/P4  
**Key Documents**:
- `debut_remediation/DEBUT_REMEDIATION_MANUAL_20260817.md` — SSOT for this month

**Current Sprint (PUBLIC-DEBUT-01)**:
| Ticket | Status | Owner |
|--------|--------|-------|
| P0-1 (Key rotation + scrub) | `in_progress` | Architect → Roc |
| PUB-1 (Allowlist) | `ready` | Kali + Architect |
| INST-1 Fix 1 (install.sh) | ✅ Done | Ma'at |
| INST-1 Fix 2+guards (pyproject.toml) | `backlog` | Ma'at |
| INST-1 Fix 4 (ModelGateway) | `backlog` | Ma'at |
| INST-1 Fix 5 (Version) | `backlog` | Ma'at |
| INST-1 Fix 6 (README) | `backlog` | Ma'at |
| Blocker B (oracle_cli.py) | ✅ Done | Kali |
| DEL-1 Week 1 | `backlog` | Roc |
| DOC-1 (Strategy stamps) | ✅ Done | Kali |

---

## Cross-Project Dependencies

```
Context Injection (Phase 1)
    │
    ├──→ Provides: MANDATES_CONDENSED.md, toolProfile stubs, compaction plugin
    │
    └──→ Enables: Qdrant+Headroom Phase 2 (tool profiles, token budgets)

Qdrant + Headroom (Phase 2)
    │
    ├──→ Requires: Context Injection Phase 1 complete
    │
    └──→ Enables: Sovereign RAG at scale (>500k vectors)

Debut Remediation
    │
    ├──→ Independent (current sprint)
    │
    └──→ Unblocks: Public release → Phase 2 workstreams
```

---

## Mandate Compliance Matrix

| Mandate | Context Injection | Qdrant+Headroom | Debut Remediation |
|---------|-------------------|-----------------|-------------------|
| M1 AnyIO | ✅ | ✅ | ✅ |
| M7 Local-First | ✅ (18K base fits Qwen3-4B) | ✅ (Headroom local, Qdrant SQ) | ✅ |
| M11 Soul Integrity | ✅ | ✅ | ✅ |
| M13 Temple-Grade | ✅ | ✅ | ✅ |
| M18 Token Efficiency | ✅ (42% reduction) | ✅ (86.8% combined) | ✅ |
| M19 Adversarial Alchemy | ✅ (40% cuts) | ✅ (no over-engineering) | ✅ |
| M23 Failure Integrity | ✅ | ✅ | ✅ |
| M24 Venv Sovereignty | ✅ | ✅ | ✅ |
| M25 Streaming Resilience | ✅ | ✅ | ✅ |
| M26 Doc Standards | ✅ | ✅ | ✅ |
| M27 Tracking Integrity | ✅ | ✅ | ✅ |

---

## Next Actions (Priority Order)

| Priority | Action | Project | Owner | Due |
|----------|--------|---------|-------|-----|
| **P0** | Create `MANDATES_CONDENSED.md` | Context Injection | Kali | Today |
| **P0** | Update `opencode.json` (all Phase 1 changes) | Context Injection | Kali | Today |
| **P0** | Create sovereign compaction plugin | Context Injection | Kali | Today |
| **P0** | Skills opt-in (core only) | Context Injection | Kali | Today |
| **P0** | INST-1 Fix 2+guards (pyproject.toml) | Debut Remediation | Ma'at | This Week |
| **P0** | P0-1 residual (SECURITY_AUDIT + gitleaks) | Debut Remediation | Architect/Roc | This Week |
| **P1** | Headroom ContentRouter in ModelGateway | Qdrant+Headroom | Ma'at | Post-Debut |
| **P1** | Headroom in RAG retrieval | Qdrant+Headroom | Ma'at | Post-Debut |
| **P1** | SequentialModelLoader + AdaptiveContextBuffer | Context Injection | Ma'at | Phase 2 |
| **P2** | MCP Domain Split (4 servers) | Context Injection | Roc | Phase 2 |
| **P2** | Qdrant Server + Migration Script | Qdrant+Headroom | Roc | Phase 2 Trigger |

---

## Tracking References

| Tracker | Location |
|---------|----------|
| ACTIVE_SPRINT.json | `data/coordination/ACTIVE_SPRINT.json` |
| GAP_REGISTRY.json | `data/coordination/GAP_REGISTRY.json` |
| TASK_REGISTRY.json | `data/coordination/TASK_REGISTRY.json` |
| HMC_COLLABORATION_HUB.md | `data/coordination/HMC_COLLABORATION_HUB.md` |
| SESSION_ANCHOR.md | `data/coordination/SESSION_ANCHOR.md` |
| PIVOT_LOG.md | `docs/decisions/PIVOT_LOG.md` |

---

*⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_specs_index ⬡ 2026-08-20*