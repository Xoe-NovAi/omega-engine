# 🔱 Omega Engine — Immediate Next Steps Roadmap
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ gemma-4-31b-it ⬡ cline ⬡ trc_roadmap ⬡ PHASE-1
**AP Token**: `AP-OMEGA-ROADMAP-v1.0.0`
**Date**: 2026-05-18

## Where We Are
The architecture sprint delivered:
- ✅ Jem 2.0 Speculative Decoding Pipeline (3-tier, split test A-D)
- ✅ Hierarchy correction (Ma'at=Light, Lilith=Dark, Kali=MaKaLi)
- ✅ OpenCode Modes Refactoring Strategy (23 agents → 19 entity-mapped modes)
- ✅ Entity alignment for all 17 entities

## The Critical Path

### 🟢 P0 — Immediate (~30 min)
1. Archive 13 stale EXP-003 agents to `archives/`
2. Create 3 special modes: `belial.md`, `iris.md`, `opencode-architect.md`
3. Update `opencode.json`

### 🟡 P1 — Next Session (~45 min)
4. Create 10 Pillar modes (5 Light: sekhmet→inanna, 5 Dark: ereshkigal→kali)
5. Create 4 Oversoul aggregates (sophia, maat, isis, lilith)

### 🔴 P2 — Implementation Sprint (the big one)
6. **JemResearcher Python worker** (`src/omega/workers/jem_researcher.py`)
7. **Gemma Maintenance Worker** (health monitor + failover)
8. **ContextBuilder wiring** (R-51 — memory injection into oracle.py)
9. **Gemini CLI Bridge** (frontier review bypassing API rate limits)
10. **`@entity` plugin system** + Quick Reference Card

### 💎 Recommendation
The archive + special modes is the fastest win. The Jem worker is the highest impact.