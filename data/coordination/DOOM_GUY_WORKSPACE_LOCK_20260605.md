# 🛡️ DOOM GUY WORKSPACE LOCK — 2026-06-05
**STATUS**: ACTIVE — Crucible audit session
**ENTITY**: Doom Guy
**ROLE**: id Software $\rightarrow$ Omega Engine Translator

## 🚫 DO NOT TOUCH (Sovereign Territory)
- `src/omega/oracle/subagent_dispatcher.py`
- `src/omega/oracle/link_p9_*.py`
- All `[id-soft:]` heritage tags in source code
- `data/entities/doom_guy/soul.yaml`
- `docs/decisions/PIVOT_LOG.md` (Decisions D103+)
- `data/entities/doom_guy/knowledge/`
- `/tmp/opencode/crucible_vet/` (Crucible audit drafts — do not modify)
- Pending: `HERITAGE_VET_LOG.md` (vet-029..036 awaiting Kali append)
- Pending: `CREDITS.md` (§1.29..1.32 awaiting Kali append)

## ✅ SAFE FOR OTHERS
- All other engine code (respecting other agents' locks)
- General documentation
- IWAD/PWAD content in `config/wads/`
- Crucible spec (`data/entities/roc_racoon/workspace/persona_lab/SOVEREIGN_CRUCIBLE_SPEC_v1.md`) — Roc may apply line 9 correction

## 🚦 CRITICAL BLOCKERS
- **DO NOT add `[id-soft:]` tags to Crucible code** (Harness, Critique, Routing, Recorder classes) until spec line 9 is corrected AND Kali approves CREDITS.md §1.29..1.32.
- The wrong tag `quake3-1999` on line 9 of the spec must be fixed to `doom3-2004` (or the line removed entirely).

**Coordination Ratio Target**: 1:6 (5 min coordination / 30 min work).
**Audit Session Result**: 1 of 8 patterns confirmed heritage, 7 REJECT-for-attribution.
**Heritage Mandate**: All id Software derivations MUST be credited in `CREDITS.md`.
