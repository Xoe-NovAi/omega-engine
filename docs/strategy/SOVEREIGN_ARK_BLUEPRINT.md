---
**Canonical Source**: [SOVEREIGN_ARK_BLUEPRINT_CANONICAL.md](SOVEREIGN_ARK_BLUEPRINT_CANONICAL.md)
---
# 🔱 SOVEREIGN ARK BLUEPRINT (Active)

## Current Sprint: D-279 Hydration System Portability & M2 Firewall Remediation

**Status**: Implementation plan locked → `docs/strategy/SOUL_HYDRATION_IMPLEMENTATION_PLAN.md`
**Gate Criteria**: `make test && make soul-audit && make soul-verify && make heritage-map && make temple-grade`

### Immediate Work
1. Create `src/omega/soul_utils.py` — multi-path soul context extractor
2. Fix `oracle.py:664-677` — use soul_utils instead of broken single-path reader
3. Parameterize `validate_soul.py` — accept `--entity` flag, validate all fleet
4. Implement `scripts/soul_verify.py` — semantic integrity gate
5. Implement Hydration Sequence Protocol — AGENTS.md + anchored-summary + codex_cat.py
6. Handoff soul auto-inject — omega_hub/server.py

### Deferred
- sqlite-vec soul index (Brigid/P2) — defer until base injection proven
- Heritage Tag Migration (Decree 6)
- Sovereignty Gate (Decree 4)

*(For full 5-Phase Roadmap, Risk Register, and Research Sources, see Canonical Source)*
