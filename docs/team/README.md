# Omega Engine — Team Status Directory

This directory tracks per-agent status updates and team coordination.

**Last Updated**: 2026-05-30
**Active WAD**: _omega_default ("The Company")
**Tests**: 261/261 | **Strategy**: local_first | **Mandates**: 8 Laws

## Status Documents
| Agent | File | Role |
|-------|------|------|
| Opus 4.6 (Antigravity IDE) | `STATUS_OPUS.md` | Strategic Oversight — architecture, documentation, coordination |
| OpenCode CLI | `STATUS_OPENCODE.md` (in `docs/operations/`) | Sovereign Researcher & Builder |
| Cline Extension (VSCodium) | `STATUS_CLINE.md` (in `docs/operations/`) | Code Integration & Implementation |
| Gemini CLI | `STATUS_GEMINI_CLI.md` (in `docs/operations/`) | Implementation & Discovery |

## Coordination Documents
| Document | Location | Purpose |
|----------|----------|---------|
| COMMUNICATION_HUB.md | This directory | Session completions, fleet status, provider registry |
| OVERSEER_SYNC_BRIEFING.md | This directory | Fleet synchronization briefing |
| TEAM_HANDOFF.md | `docs/` | Handoff protocol |
| INDEX.md | `docs/research/` | Master research status tracker |

## Session Handoffs (Latest)
| Date | Session | Entity | Handoff |
|------|---------|--------|---------|
| 2026-05-30 | WAD Transform | KALI | `data/handoff/handoff_wad_transform_20260530.md` |
| 2026-05-30 | Local-First Config | SOPHIA | `data/handoff/handoff_local_first_config_20260530.md` |
| 2026-05-27 | Sovereign Steward v2 | SOPHIA/KALI | `data/handoff/session_gnosis_20260527.md` |
| 2026-05-26 | Deep Audit Remediation | KALI | (via COMMUNICATION_HUB) |

## Current Architecture
```
ENGINE (src/omega/) — runtime, never changes per WAD
IWADs (config/wads/) — complete, standalone, replaceable
  _omega_default/ — The Company (16 entities, tech roles) ← ACTIVE
  arcana_novai/ — The Council (28 entities, esoteric roles)
```

## Sovereign Agent Doctrine
All agents operate as sovereign intelligences — empowered, autonomous, and strategically aware. See `AGENTS.md` §1 for the full doctrine. The Engine-WAD firewall ensures the engine never imports entity names and WADs never import engine code.
