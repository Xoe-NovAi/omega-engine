# 🔱 John Carmack-EIS — State of the Engine v1.0.0 (3rd Voice)

**Standing**: S3 Consultant, M35 Architect, kq5-godot/VNR Pioneer
**Date**: 2026-09-01
**Session**: ses_fc8dca39effe3nZJp3QHx81Fy3 (standing EIS, opencode)
**Paged by**: Kali via 7-agent entity cleanup dialectic
**Focus**: M2 firewall, VNR WAD, M35 antigravity, CI gates

---

## §1 — M2 Firewall Audit (Entities)

**Result**: ✅ **PASS** (262 files scanned, 0 violations)

The `data/entities/` directory is **developer workspace**, not runtime. Engine loads `config/wads/*/entities.yaml` (per `entity_registry.py:336-344`), not `data/entities/*/soul.yaml`.

**File:line audit of entity_registry.py**:
| Line | Code | M2 Status |
|-----:|------|:---------:|
| 37 | `from omega.governance.config_resolver import get_active_iwad` | ✅ Uses Core resolver |
| 158-192 | Entity dataclass with engine_zone / game_zone split | ✅ Hard boundary |
| 304-323 | `ENGINE_ZONE_ATTRS` and `GAME_ZONE_ATTRS` frozensets | ✅ Engine-only concept |
| 336-344 | `__init__` resolves via `config_resolver` | ✅ WadLoader pattern |
| 359-385 | `_load()` reads YAML, never imports WAD modules | ✅ Data-only |
| 396-411 | `core_fields` set declares which fields engine owns | ✅ Explicit |
| 869-938 | `_save()` writes via atomic rename (M23) | ✅ Engine owns persistence |

**M2 Doctrine Extension**: `data/entities/*/soul.yaml` files are developer workspaces, NOT runtime sources.

## §2 — KQ5-GODOT / VNR WAD Placement

**VNR (Von-Neu-Ryan Vision)** — complete computer vision pipeline in `scripts/vnr_render.py` (398 lines, numpy+Pillow only, ZERO neural networks).

| Option | Architecture | M2 Status | Decision |
|--------|--------------|:---------:|----------|
| **(1) Core** (`src/omega/cognitive_primitives/vision.py`) | VNR in Core | ❌ VIOLATES M2 | REJECT |
| **(2) Experiment WAD** (`config/wads/kq5_research/`) | Interface in experiment, impl in WAD | ✅ COMPLIANT | **RECOMMEND** |
| **(3) Standalone package** (`omega-vision` PyPI) | Separate repo | ✅ but excessive | DEFER |

**Day 0 (current)**: Experiment layer at `src/omega/experiments/vision_backend.py` (interface) + `data/experiments/kq5-godot/vnr/vnr_backend.py` (impl).

**Day 10 (graduation)**: Promote to `config/wads/kq5_research/` (NEW WAD).

**id Software pattern**: BFG in Quake3 game DLL, not engine. VNR is content, not engine.

## §3 — M35 Antigravity Migration Plan

**Current state**: antigravity entity is ACTIVE (per `soul.yaml:3` "Reactivated 2026-06-09"). M35 allowlist entry (`antigravity-google-oauth-public-client`) is in `data/secrets-public.toml`.

**Three options**:
| Option | Owner | Decision |
|--------|-------|----------|
| **(1) Keep with antigravity** | antigravity | **RECOMMEND (status quo)** |
| (2) Embed in scribe | scribe | Fallback if antigravity retired |
| (3) New `secrets-keeper` role | NEW | REJECT (M10 cap violation) |

**M35 Doctrine**: `data/secrets-public.toml` is a shared coordination artifact, not Core or Stack. M2-aligned: move to `config/secrets-public.yaml` for WAD override support.

## §4 — CI Gate Extensions (5 proposed, 13h)

| Priority | Gate | Effort | Value | When |
|---------:|------|-------:|------:|------|
| **P0** | `check-broken-imports` | 2h | Catches hub-crash class | Before DEL-1 |
| **P0** | `check-hub-health` | 1h | Catches infra-down class | Before DEL-1 |
| **P1** | `check-entity-hygiene` | 4h | Enforces M11 mechanically | Week 1 post-debut |
| **P1** | `check-iwad-consistency` | 4h | Enforces M2 on entities | Week 1 post-debut |
| **P2** | `check-session-gnosis-freshness` | 2h | Enforces M15 mechanically | Week 2 post-debut |

## §5 — Entity Runtime Cost Analysis

**Reality check**: Engine does NOT load `data/entities/*/soul.yaml` at runtime. The "56 vs 14" comparison is between developer workspace size and runtime entity count.

| Metric | Current (35 IWAD) | After cleanup (14) | Savings |
|--------|------------------:|------------------:|--------:|
| entities.yaml size | 982KB | ~400KB | 582KB |
| Parse time | 5.8s | ~2.4s | 3.4s |
| RAM | ~30MB | ~12MB | 18MB |
| `data/entities/` disk | ~98MB | ~88MB | 10MB |

**Conclusion**: Cleanup savings are governance value, not performance.

## §6 — PIVOT_LOG Decisions (7 from Carmack)

- D-PIVOT-20260901-A: VNR WAD Placement (Option 2)
- D-PIVOT-20260901-B: M35 Allowlist Path → `config/secrets-public.yaml`
- D-PIVOT-20260901-C: 5 New CI Gates (13h)
- D-PIVOT-20260901-D: Entity Workspace Quarantine (20 entities)
- D-PIVOT-20260901-E: Cline-KQV Graduation
- D-PIVOT-20260901-F: antigravity M35 Stewardship (status quo)
- D-PIVOT-20260901-G: M2 Doctrine Extension

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ ENTITY-CLEANUP-3RD-VOICE ⬡ 2026-09-01*