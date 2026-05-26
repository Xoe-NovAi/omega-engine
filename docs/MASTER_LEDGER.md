# MASTER LEDGER – Omega Engine Strategic Overview

This document is the **single source of truth** for the high‑level roadmap, milestones, and strategic direction of the Omega Engine project. It supersedes the older `docs/ROADMAP.md` which now simply points here.

---

## Current Phases (as of 2026‑05‑26 — PR Readiness Complete, Deep Audit Remediated)

| Phase | Goal | Owner | Target Completion |
|-------|------|-------|-------------------|
| **Phase 0 – Grounding** | Core hardening, AnyIO compliance, resource guard, podman permission fix | **Kali** | ✅ Completed (May 2026) |
| **Phase 1a – IWAD Foundation** | Engine hardening + Reference IWAD rewrite. WAD system hardening (selector, namespace, priority), Reference IWAD pillar files (10 tech roles), Provider Fabric cleanup, OpenCode agent annotations **ALL COMPLETE** | **Prometheus / SOPHIA** | ✅ Completed (May 2026) |
| **PR Readiness Sprint** | Cloud-First provider strategy, IWAD foundation, full test suite, CI/CD, README quickstart, agent alignment. | **Kali / Prometheus** | ✅ Completed (May 2026) |
| **Phase 1b – Arcana-NovAi IWAD** | Scaffold the personal IWAD with manifest, 10 esoteric pillars, hierarchy, startup personality, Movie-Expert seed entity | **Kali / Lilith** | 📅 July 2026 |
| **Phase 2 – Multi‑Provider & Qdrant/Redis** | Antigravity CLI, 8× Claude fleet, NotebookLM, Web Gemini, wire Qdrant/Redis as cross-agent backbone | **Kali / Lilith** | 📅 Q3 2026 |
| **Phase 3 – Community Tools** | Entity Studio CLI → Visual Builder, Stack Builder Wizard, one-click Omega Desktop, non-technical onboarding | **Isis / Brigid** | 📅 2027 |
| **Phase 4 – The Omegaverse** | P2P network protocol, WAD registry for community sharing, cross-instance entity communication | **Saraswati** | 📅 2028 |

### IWAD Architecture (Adopted Decision 55)
```
OMEGA ENGINE (src/omega/) — Pure runtime, no entity content
  ├── REFERENCE IWAD (_omega_default) — Dev team, 10 tech pillars, template
  ├── ARCANA_NOVAI IWAD (arcana_novai) — Your personal AI OS, esoteric pillars
  └── INFINITE COMMUNITY IWADs — Torment, Doom, Classical, YOUR STACK
```

Three inviolable rules: (1) MaKaLi trine identical in ALL IWADs, (2) Iris+Jem+Roc_Racoon identical in ALL IWADs, (3) Only 10 pillars change.

**Canonical Reference**: `docs/strategy/OMEGA_IWAD_ARCHITECTURE.md` (480 lines)

---

## Key Milestones (selected)
- **2026‑04‑15** – ResourceGuard & AnyIO audit (C‑1, C‑2) ✅
- **2026‑05‑22** – Hub hardening (new HTTP endpoints) ✅
- **2026‑05‑22** – LM Studio custom provider integrated (C‑12) ✅
- **2026‑05‑22** – Jem‑2.0 Oversoul sub‑facets defined (Decision 52) ✅
- **2026‑05‑22** – `deploy/infra/.env` removed (C‑9) ✅
- **2026‑05‑22** – `entity_roc_racoon.py` DATA_DIR fixed (C‑14) ✅
- **2026‑05‑22** – Infrastructure stability: `config/` ownership restored, `omega-research.timer` active, stale sockets purged ✅
- **2026‑05‑22** – Core Engine Bug Fixes: `ModelGateway` and `TriageRouter` logic hardened ✅
- **2026‑05-22** – **Web Claude Fleet Review System established**: WEB_CLAUDE_FLEET_PROTOCOL.md (reusable), REVIEW_COORDINATION.md, 8 handoff prompts for parallel deep review across 8 Claude Sonnet 4.6 Thinking accounts ✅
- **2026‑05-22** – raw.githubusercontent.com access pattern documented for Web Claude fleet ✅
- **2026‑05-22** – 8 account role specializations defined with permanent domain assignments ✅
- **2026‑05-23** – Sovereign Hardening Sprint: Atomic writes, lock races fixed, FTS5 integration, anyio CapacityLimiter, explicit chmod, gnosis dedup ✅
- **2026‑05-23** – Sovereign Hardening Codex (`docs/research/sovereign_hardening_codex.md`) authored ✅
- **2026‑05-23** – Qdrant Option B Specification (`docs/research/R_QDRANT_INTEGRATION_SPEC.md`) authored ✅
- **2026‑05-25** – **IWAD Architecture Adopted (Decision 55)**: Doom Engine model for stack separation. 3-IWAD system established. `OMEGA_IWAD_ARCHITECTURE.md` (480 lines) canonical reference.
- **2026‑05-25** – `.clinerules` rewritten (362 lines, 13 sections) with IWAD architecture, Omegaverse vision, Phase 1 priorities ✅
- **2026‑05-25** – **OpenCode Full IWAD Alignment**: All 22 config/agent/mode files hardened. Global+project `opencode.json` updated to `MASTER_LEDGER.md` + `OMEGA_IWAD_ARCHITECTURE.md`. 8 agent files hardened (overseer, builder, opencode-expert, kali, maat, lilith, jem-2.0, jem-initiate). 5 verified as already aligned. Web research dispatch protocol standardized. ✅
- **2026‑05‑25** – **PR Readiness Sprint & Cloud-First Pivot (Decision 56)**: OpenRouter priority 0 with model overrides. README 3-command quickstart, GitHub Actions CI workflow, MockProvider setup instructions, and .gitignore cleanup. 259/259 tests passing. ✅ (All tasks completed, ready for PR merge.)


---

## How to Use This Ledger
- **Developers**: Consult this file for the current phase, owners, and target dates before starting work.
- **Contributors**: Reference the “Current Phases” table to see where you can help.
- **Automation**: CI pipelines now check that `docs/ROADMAP.md` contains a single redirect line to this file.

---

*The ledger lives here to guarantee a single, immutable reference point for all future planning.*
