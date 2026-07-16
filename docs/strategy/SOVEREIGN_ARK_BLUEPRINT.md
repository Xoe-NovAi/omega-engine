---
**Canonical Source**: [SOVEREIGN_ARK_BLUEPRINT_CANONICAL.md](SOVEREIGN_ARK_BLUEPRINT_CANONICAL.md)
---
# 🔱 SOVEREIGN ARK BLUEPRINT (Active)

## Current Sprint: D-280 Sovereign Continuity Feature (Supersedes D-278 Detection Strategy)

**Status**: Research complete → `docs/research/R_HYDRATION_RECEIPT_COMPACTION_DETECTION_20260716.md`
**Gate Criteria**: `make test && make temple-grade && make firewall-check`

### Immediate Work (D-280)
1. Wire `CompactionListener` to OpenCode `/global/event` SSE — extends existing `CompactionHarvester`
2. Implement `CheckpointManager` — epoch tracking, atomic writes
3. Implement `HydrationReceipt` + `ToolCallWrapper` enforcement gate
4. Observability integration — `hydration_log.jsonl`, metrics DB, 3 dashboards
5. Soul distillation hook — L1→L2→L3 from hydration events

### Parallel (D-279)
- R1-R5: Fix 4 M2 Firewall violations (sovereign_vetter.py, mandate_auditor.py, oracle.py)
- R6-R9: Separate codex mechanism from content, fix Makefile side-effects
- R15-R20: Extract `omega-hydration` PyPI package (receives D-280 runtime as dependency)

### Deferred
- sqlite-vec soul index (Brigid/P2) — defer until base injection proven
- Heritage Tag Migration (Decree 6)
- Sovereignty Gate (Decree 4)

*(For full 5-Phase Roadmap, Risk Register, and Research Sources, see Canonical Source)*
