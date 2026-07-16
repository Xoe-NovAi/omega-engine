---
**Canonical Source**: [PIVOT_LOG_CANONICAL.md](PIVOT_LOG_CANONICAL.md)
**Query**: `omega context search "D-XXX"`
---
# 🔱 PIVOT LOG (Active Index)

| Decision | Summary | Status |
|---|---|---|
| D-275 | Institutionalize Wave 3 refinement meta-process | Active |
| D-276 | Implement ContextProtocol pipeline (15K budget) | Active |
| D-277 | Soul Hydration Pipeline — fix schema mismatch, add soul_utils.py, hydration sequence, soul-verify gate | Active |
| D-278 | Rehydration System Hardening — atomic writes, entity resolution, identity recovery, handoff TTL, non-blocking observability, rolling window anchor, contract + chaos tests | Active |
| D-279 | Hydration System Portability & M2 Firewall Remediation — 4 M2 violations, mechanism-content separation, config-driven protocol, handoff-based pruning, omega-hydration package | Active |
| D-280 | Sovereign Continuity Feature — SSE-based compaction detection, epoch-scoped receipts, CheckpointManager, CompactionListener, ToolCallWrapper enforcement gate | Active |

*(For full history D1-D274, see Canonical Source)*

### D-281: Substrate Repair Execution Strategy (Option A + C)
* **Date**: 2026-07-16
* **Context**: The Omega Engine has three pending workstreams: D-277 (Soul Hydration), D-279 (M2 Firewall), and D-280 (Sovereign Continuity/Compaction Detection). Synthesis revealed that D-277 and D-279 are critical Phase 0 substrate repairs, while D-280 is a Phase 1+ feature. Furthermore, soul injection (D-277) is silently failing for 28/31 entities due to a schema mismatch and a read/write loop gap.
* **Decision**: 
  1. Merge D-277 (Items 1-2) and D-279 (M2 fixes + Codex separation) into a focused 4-Phase execution plan.
  2. Defer D-280 (Compaction Detection), `soul-verify` gate, and `omega-hydration` PyPI extraction to a future sprint.
  3. Commit code strictly per-phase to isolate changes.
  4. Fix the soul read/write race by having `soul_utils.py` read `proposed_lessons.yaml` (approved proposals) as a primary source.
* **Phases**:
  - Phase I: Option C Core (soul_utils.py + oracle.py fix)
  - Phase II: Force Multiplier (config_resolver.py + WadLoader API)
  - Phase III: M2 Firewall Remediation (hierarchy, entity_registry, scraper)
  - Phase IV: Codex Mechanism Separation (hydration_header.md + Makefile fixes)
