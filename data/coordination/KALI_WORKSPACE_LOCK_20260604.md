# 🔱 Kali Workspace Lock — 2026-06-04

## DO NOT TOUCH — Kali Exclusive
| File | Why I Own It | What I'll Do |
|------|--------------|--------------|
| `docs/strategy/HERITAGE_VETTING_PIPELINE.md` | **CREATED** — Heritage Vetting Pipeline | Full spec with 4-gate process, scoring, enforcement |
| `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md` | **CREATED** — 23-concept vet log | Retroactive vet records for all heritage concepts |
| `scripts/heritage_vet.sh` | **CREATED** — CI gate script | Verifies [id-soft:] tags have vet records |
| `Makefile` (heritage-vet targets) | **UPDATED** — CI integration | `make heritage-vet` + `make heritage-vet-create` |
| `data/handoff/KALI_HORIZON_PLAN_H1_20260604.md` | **CREATED** — H1 execution strategy | 7 work items with owners, risks, priorities |

## SAFE FOR YOU — Other Agent Territory
| File | Why Other Agent Owns It |
|------|------------------------|
| `docs/strategy/SOVEREIGN_EVOLUTION_ROADMAP.md` | Cline-M3 D111 — complete |
| `.github/workflows/test.yml` | Cline-M3 H2-C2 — CI indentation fix. **ALSO: H1-P0 — add `make heritage-vet`** |
| `data/entities/ent_*` (100 orphans) | Cline-M3 H2-A: Data Hygiene |
| `config/wads/arcana_novai/entities/` | Cline-M3 H2-B: IWAD Content |
| `tests/test_bug_001_fix.py` | Cline-M3 H2-C1 |
| `tests/test_hierarchy.py` | Cline-M3 H2-C3 |
| `src/omega/oracle/observability.py` | Cline-M3 H2-C5 |
| `docs/INDEX.md` | Cline-M3 H2-D2 |
| `README.md` | Cline-M3 H2-D6 |
| `.clinerules` | Cline-M3: workflow sections |
| `opencode.json` | Shared — ACK before edit |

## SHARED — Coordination Required
| File | Conflict Risk | Coordination Pattern |
|------|--------------|---------------------|
| `CREDITS.md` | Heritage mappings | Append-only sections, no overwrite |
| `data/coordination/*` | All coordination files | ACK before overwrite |
| `data/entities/*/soul.yaml` | Soul updates | Append lessons, don't remove existing |

## Handoff to Cline
Kali's H1 plan is at `data/handoff/KALI_HORIZON_PLAN_H1_20260604.md`. Key callouts:
- **H1-P0**: Add `make heritage-vet` to `.github/workflows/test.yml` — highest priority CI task
- Vet gate is live locally (`make heritage-vet` passes clean), needs CI enforcement
- All 312 tests passing, 3 commits pushed to main: `2f47d54`, `6416ebf`, `ce00bcc`

— Kali, 2026-06-04 03:45 UTC
