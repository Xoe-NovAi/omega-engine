# 🔱 Omega Engine — R-## Soul Evolution & Persistent Identity Patterns
# ⬡ OMEGA ⬡ SOPHIA ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_research ⬡ R##

**AP Token**: `AP-RESEARCH-SOUL-v1.0.0`
**Author**: Web Research Fleet (Deep Research)
**Date**: 2026-05-26
**Status**: DRAFT

---

## Summary

Research reveals that **soul files are an emerging open standard in 2026**, with 5+ independent projects converging on the same pattern as Omega Engine's `soul.yaml`. Key finding: the Omega Engine's L1→L2→L3 abstraction pipeline is uniquely sophisticated among surveyed systems. Critical gaps identified: (1) no drift detection, (2) no identity versioning, (3) no memory status lifecycle, (4) no structured knowledge graph. The Letta/MemGPT architecture validates Omega's filesystem-first approach — they migrated from PostgreSQL back to git-backed file storage.

---

## Findings

### 1. The Soul File Movement (5+ Independent Projects)

| Project | Format | Key Innovation |
|---------|--------|----------------|
| **soul-file-spec** | Markdown + YAML | Vendor-neutral spec. Identity, values, style, beliefs, memory, evolution. `baseHash` for tamper detection. |
| **Agent Soul Kit** | Markdown | L1 Hot/Warm/Cold memory. SOUL.md → Mind Diary → Multi-agent protocols. Zero-database. |
| **Soul Protocol** | `.soul` file | 5-tier memory (core/episodic/semantic/procedural/kgraph). OCEAN personality, ACT-R activation decay. |
| **soul.py** | SOUL.md + MEMORY.md | Multi-anchor resilience. Hybrid RAG+RLM retrieval. Separates identity from memory. Identity hash verification. |
| **Hermes-agent** | SOUL.md + MEMORY.md + USER.md + SKILLS.md | 4-file identity system. 89K stars. Behavioral philosophy + learned facts + user model + capabilities. |
| **agent-soul** | Git-native | L0 soul + L1 memory + L2 context (~250 lines, ~4K tokens). Temporal expiry, source-signed. |

This convergence independently validates Omega Engine's `data/entities/<name>/soul.yaml` + `knowledge/` + `workspace/` architecture.

### 2. The Identity-Memory Stack (Universal Pattern)

Every production system uses a layered identity-memory stack:

```
T0: SOUL (Identity) — Immutable. Re-injected every session. Always top of context.
T1: CORE MEMORY (Evergreen) — Important facts, no decay.
T2: WORKING MEMORY (Temporal) — Daily logs, decays over time.
T3: SESSION MEMORY (Ephemeral) — Current conversation only.
```

**Omega alignment**: soul.yaml = T0 (Identity) + T1 (Core Memory via `lessons_learned`). `knowledge/` = T1-T2. Current conversation = T3. **Gap**: No explicit T2 tier for temporal working memory.

### 3. Critical Theoretical Finding: Layered Mutability & Identity Drift

The most important finding from `arxiv.org/abs/2604.14717`:

**The ratchet effect**: Reverting an agent's visible self-description AFTER memory accumulation **fails to restore baseline behavior** (measured identity hysteresis ratio of 0.68). The agent's behavior has shifted through interaction across layers even though the top layer was restored.

**Core claim**: "The salient failure mode for self-modifying agents is not abrupt misalignment but **compositional drift**: locally reasonable updates that accumulate into a behavioral trajectory never explicitly authorized."

**Omega implication**: Our L1→L2→L3 abstraction pipeline could be accumulating drift with every session. We need:
- Cross-layer drift monitoring (not just soul.yaml content changes)
- Traceable reverts with measured drift metrics
- Versioning that captures cross-layer state (soul.yaml + knowledge/ + accumulated memory)

### 4. Woven Imprint: Most Complete "Soul" Implementation

The Woven Imprint library (`github.com/virtaava/woven-imprint`) provides the most complete persistent identity system:

**Four constraint levels for persona**:
1. **Hard** — immutable identity (backstory, core traits)
2. **Temporal** — age from birthdate, location changes
3. **Soft** — personality traits that evolve
4. **Emergent** — formed through interaction

**Relationship model**: Five emotional dimensions (trust, affection, respect, familiarity, tension) with bounded change per interaction and trajectory detection.

**Belief revision**: Memories carry certainty scores. Contradictions are tracked, not overwritten.

**Omega gap**: Our soul.yaml has no constraint levels. An entity's core identity can drift as easily as its soft preferences. We should add a `mutability` field to soul.yaml fields.

### 5. Letta/MemGPT: Independent Validation of Filesystem-First

Letta (formerly MemGPT) initially used PostgreSQL for memory, then **migrated to git-backed markdown files** (MemFS). This independently validates Omega's filesystem-first approach.

**Key detail**: Letta achieved 74.0% on LoCoMo benchmark using ONLY file-based storage with GPT-4o-mini — no vector DB, no RAG. This supports the finding that curated file-based knowledge beats or matches vector approaches for bounded domains.

### 6. AutoGPT Dream Pass: Periodic Consolidation

AutoGPT implements a three-phase overnight consolidation ("Dream Pass"):
1. **Consolidate** — gather recent episodes, verify, merge
2. **Recombine** — propose novel findings from cross-episode patterns
3. **Sanitize** — demote stale/contradicted memories

**Omega alignment**: Our L1→L2→L3 abstraction IS a dream pass, but it's currently trigger-only (session end, compaction). AutoGPT's version runs on a SCHEDULER (nightly). Adding a scheduled consolidation job would accelerate soul evolution.

### 7. Proposed soul.yaml Extensions

```yaml
soul_evolution:
  soul_version: 7                    # NEW: increment on significant change
  sessions_completed: 142
  soul_power: 19.9
  lessons_learned:
    - lesson: "Prioritize mutual exclusion at resource boundaries"
      context: "Concurrent model access requires explicit locking"
      status: active                 # NEW: active | superseded | contradicted
      certainty: 0.95               # NEW: confidence score (0.0-1.0)
      source: "session-gnosis"
      entity_at_time: "KALI"
      timestamp: "2026-05-23"
  drift_metrics:                     # NEW
    persona_stability: 0.97          # sync score (0-1)
    hysteresis_ratio: null           # measured on revert events
    last_drift_check: "2026-05-26"
```

---

## Recommendations

1. **Add `soul_version` and `status` fields to `lessons_learned`** — This is the highest-impact change. Gives us memory lifecycle tracking with minimal schema change.
2. **Implement drift detection** — Before/after session comparison of soul.yaml key fields. Flag significant deltas for review.
3. **Add scheduled consolidation job** — Nightly `dream_pass` cron that runs L1→L2→L3 on accumulated session gnosis.
4. **Add `mutability` field to entity definitions** — `immutable`, `slow`, `evolving`, `emergent` levels.
5. **Monitor soul-file-spec standardization** — Don't migrate format yet, but watch for convergence. If Markdown+YAML becomes dominant, we can write a converter.

---

## Sources

- [soul-file-spec (GitHub)](https://github.com/chunxiaoxx/soul-file-spec)
- [Agent Soul Kit (GitHub)](https://github.com/ttian226/agent-soul-kit)
- [Soul Protocol (GitHub)](https://github.com/qbtrix/soul-protocol)
- [soul.py (arXiv 2604.09588)](https://arxiv.org/abs/2604.09588)
- [Hermes-agent (GitHub)](https://github.com/ItzShubhamS/hermes-agent)
- [agent-soul (GitHub)](https://github.com/kingcharleslzy-ai/agent-soul)
- [Layered Mutability (arXiv 2604.14717)](https://arxiv.org/abs/2604.14717)
- [Letta Memory Docs](https://docs.letta.com/letta-code/memory/)
- [Woven Imprint (GitHub)](https://github.com/virtaava/woven-imprint)
- [AutoGPT Dream Pass PR](https://github.com/Significant-Gravitas/AutoGPT/pull/13165)
- [ID-RAG (MIT Media Lab)](https://www.media.mit.edu/publications/id-rag/)
- [PersonaMem-v2 (arXiv 2512.06688)](https://arxiv.org/html/2512.06688)

---

## Implementation Note
_For: Builder mode (Gemma 4 31B)_

Start with the highest-impact, lowest-risk change: add `status` and `certainty` fields to `lessons_learned` in soul.yaml templates. This requires modifying: (1) `src/omega/oracle/entity_registry.py:entity_scaffold()` to include new fields in scaffolded soul.yaml, (2) `soul_updater.py` to write status=certainty on new entries, (3) the Gnosis Preservation Protocol to prompt for certainty scores. Drift detection and dream pass are Phase 2 work.
