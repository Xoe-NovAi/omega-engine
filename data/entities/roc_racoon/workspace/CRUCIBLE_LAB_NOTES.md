# 🔬 Roc Racoon — Crucible Lab Notes
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ CRUCIBLE ⬡ WAVE-0 ⬡ 2026-06-06

## §0 Status

| Item | Status |
|------|--------|
| Spec v2.0 | ✅ COMPLETE — `data/entities/kali/workspace/crucible_finale/CRUCIBLE_FINAL_SPEC_v2.md` |
| Heritage Vetting | ✅ COMPLETE — 1 promoted (idHeap), 7 rejected for ML context |
| Soul Integrity | ✅ COMPLETE — 0 duplicate IDs, 54 directives, 54 lessons |
| Wave 0 Scaffolding | ⏳ PENDING — `src/omega/crucible/` directory creation |
| Wave 0 Config | ⏳ PENDING — `routing_strategies` nested in `providers.yaml` |
| Wave 0 Observability | ⏳ PENDING — `rating` field → structured dict in `observability.py` |

## §1 Spec v2.0 Summary

The Sovereign Crucible is a 3-pass cross-model training pipeline:

1. **Candidate Pass**: Entity generates response using its default model
2. **Critique Pass**: M3 (MiniMax M3) performs pairwise A/B comparison with position randomization
3. **Distill Pass**: Filters for structural novelty (not stylistic flair), writes to knowledge graph

### Key Parameters
- `batch_size: 1` (serial execution, OOM prevention on Ryzen 5700U)
- `weekly_budget_usd: 5.00` (cloud API cost cap)
- `critic_model: minimax/minimax-m3` (default judge)
- `position_randomization: true` (eliminates LLM-as-judge bias)

### Wave-Based Implementation
| Wave | Name | Scope | Status |
|------|------|-------|--------|
| W0 | Foundation | Scaffold, config, observability fix | ⏳ PENDING |
| W1 | The Harness | Parallel model dispatch, CLI, atomic YAML | FUTURE |
| W2 | The Critic | Pairwise comparison, M3 judge, scoring | FUTURE |
| W3 | The Distiller | Novelty filter, knowledge graph write | FUTURE |
| W4 | The Loop | Feedback loop, soul.yaml integration | FUTURE |

## §2 Heritage Vetting Results

| Pattern | Verdict | Reason |
|---------|---------|--------|
| `[id-soft: doom3-2004] idHeap` | ✅ PROMOTED | Storage tiering (Hot/Warm/Cold) maps to 3-tier allocator |
| `[id-soft: quake-1996] 4-Tier Memory` | ❌ REJECTED | Crucible TTL tiers are memory management for artifacts, NOT zone memory |
| `[id-soft: doom-1993] BSP Culling` | ❌ REJECTED | No visibility planes in ML training |
| `[id-soft: doom-1993] Zone Memory` | ❌ REJECTED | No tag-based allocation in Python |
| `[id-soft: quake-1996] Surface Cache` | ❌ REJECTED | No PVS in training pipeline |
| `[id-soft: quake3-1999] netchan` | ❌ REJECTED | No UDP fragmentation in MCP |
| `[id-soft: quake3-1999] FISR` | ❌ REJECTED | No fixed-point math in Python |
| `[id-soft: doom-1993] High-Bit Trick` | ❌ REJECTED | No bitfield encoding in Python |

## §3 Soul.yaml Fixes Applied

### Duplicate IDs Resolved
| Original | Fixed To | Reason |
|----------|----------|--------|
| `rr-041` (duplicate at line 576) | `rr-045` | Active Hivemind dialog lesson |
| `rr-046` (directive in lessons) | `d-rr-048` | Moved to directives section |
| `rr-047` (directive in lessons) | `d-rr-049` | Moved to directives section |
| Hybrid block (d-rr-049 + epistemic) | Split into `d-rr-049` + `rr-050` | Separated directive from lesson |

### New Directives Added
| ID | Directive |
|----|-----------|
| `d-rr-050` | Crucible spec v2.0 is the canonical blueprint |
| `d-rr-051` | M3 is the default Critic for Critique Pass |
| `d-rr-052` | M14 Heritage Vetting applies to training pipelines |
| `d-rr-053` | Batch size = 1, weekly budget = $5.00 |

### New Lessons Added
| ID | Lesson |
|----|--------|
| `rr-050` | Epistemic honesty is the foundation of agent trust |
| `rr-051` | Crucible trains the JUDGE, not the MODEL |
| `rr-052` | Heritage Vetting Gate applies to ML modules |
| `rr-053` | Session exports are the substrate for identity continuity |
| `rr-054` | The 54.6KB compaction floor is deterministic |

## §4 Next Actions

1. **Wave 0**: Scaffold `src/omega/crucible/` package with `__init__.py`
2. **Wave 0**: Register `ZONEID_CRUCIBLE` and `ZONEID_CRITIQUE` in `constants.py`
3. **Wave 0**: Nest `routing_strategies` under `inference:` in `providers.yaml`
4. **Wave 0**: Rewrite `observability.py:record_training_example()` rating field
5. **Wave 1**: Implement `src/omega/crucible/harness.py` (parallel model dispatch)

---
*Last Updated: 2026-06-06 (Session 4 — Soul Integrity Restoration)*
*Roc Racoon — Sovereign Miner & Knowledge Curator*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: CRUCIBLE | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
