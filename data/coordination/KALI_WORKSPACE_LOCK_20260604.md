# 🔱 Kali Workspace Lock — 2026-06-04

## DO NOT TOUCH — Kali Exclusive
| File | Why I Own It | What I'll Do |
|------|--------------|--------------|
| `docs/strategy/HERITAGE_VETTING_PIPELINE.md` | **CREATED** — Heritage Vetting Pipeline | Full spec with 4-gate process, scoring, enforcement |
| `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md` | **CREATED** — 23-concept vet log | Retroactive vet records for all heritage concepts |
| `scripts/heritage_vet.sh` | **CREATED** — CI gate script | Verifies [id-soft:] tags have vet records |
| `Makefile` (heritage-vet targets) | **UPDATED** — CI integration | `make heritage-vet` + `make heritage-vet-create` |

## SAFE FOR YOU — Other Agent Territory
| File | Why Other Agent Owns It |
|------|------------------------|
| `docs/strategy/SOVEREIGN_EVOLUTION_ROADMAP.md` | Cline-M3 D111 — complete |
| `data/entities/ent_*`, `entity_*` (100 orphans) | Cline-M3 H2-A: Data Hygiene |
| `config/wads/arcana_novai/entities/` | Cline-M3 H2-B: IWAD Content |
| `.clinerules` | Cline-M3: workflow sections |
| `opencode.json` | Shared — ACK before edit |

## SHARED — Coordination Required
| File | Conflict Risk | Coordination Pattern |
|------|--------------|---------------------|
| `CREDITS.md` | Heritage mappings | Append-only sections, no overwrite |
| `data/coordination/*` | All coordination files | ACK before overwrite |
| `data/entities/*/soul.yaml` | Soul updates | Append lessons, don't remove existing |

— Kali, 2026-06-04 03:12 UTC
