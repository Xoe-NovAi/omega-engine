# 🔱 Grokster KB — Master Index
**Version**: 2.1.0 | **Last Updated**: 2026-08-26 | **last_verified**: 2026-08-26
**Owner**: grokster (Cross-Platform Expertise Specialist) | **Governance**: ADR-002 Living Document Protocol
**rot_class**: slow (this index) — sub-docs carry their own rot_class

---

## Navigation

### platforms/ — Development Platform Expertise
| Doc | Scope | rot_class |
|---|---|---|
| `platforms/opencode/PLAYBOOK.md` | OpenCode CLI canonical operating practices (sessions, task_id continuation, permissions, MCP, skills, plugins, DEV-12 routing) | medium |
| `platforms/opencode/ARCHITECTURE.md` | How OpenCode works: session DB, message/part model, parent/child genealogy, compaction (D-602), plugin hooks, sessions-explorer suite | medium |
| `platforms/opencode/CONFIG_REFERENCE.md` | Full opencode.json key surface + house values + V1/V2 compaction families + provider/variant maps | fast |
| `platforms/opencode/GOTCHAS.md` | 20 verified traps (G1-G20): plugin path split-semantics, variant inertness, db pipe truncation, 87× token overcount, silent-stall taxonomy | fast |
| `platforms/CLI_IDE_ECOSYSTEM.md` | LEGACY v1.0 cross-platform MCP configs — superseded by opencode/ module + `data/coordination/PLATFORM_GNOSIS_MAP_20260818.md`; retained pending merge | stale |

### other_platforms/ — Secondary Platform Coverage
| Doc | Scope | rot_class |
|---|---|---|
| `other_platforms/CLINE_GEMINI_ANTIGRAVITY.md` | Durable Cline rulings (D-557/D-563), Gemini nuggets, Antigravity pattern | medium |
| `other_platforms/CODEX_CLAUDE_CODE_VSCODE.md` | Honest shallow-state + prioritized research-first list | slow |

### grok_ecosystem/
| Doc | Scope | rot_class |
|---|---|---|
| `grok_ecosystem/GROK_FLEET_ARCHITECTURE.md` | 8 CLI accounts (ACP), Web personas; GAP-08 framing superseded by D-360′ — refresh pending | medium |

### search/
| Doc | Scope | rot_class |
|---|---|---|
| `search/SOVEREIGN_SEARCH.md` | 5-tier router: diagram, classification, TTL, fallback chain — CANONICAL | slow |
| `search/SOVEREIGN_SEARCH_PROTOCOL.md` | MERGED 2026-08-26 → SOVEREIGN_SEARCH.md (stub retained) | — |

### vault/
| Doc | Scope | rot_class |
|---|---|---|
| `vault/OMEGA_VAULT.md` | V-1 MVP spec-of-record: architecture, 16-account schema — CANONICAL | slow |
| `vault/OMEGA_VAULT_ARCHITECTURE.md` | MERGED 2026-08-26 → OMEGA_VAULT.md (stub retained) | — |

### communication/ · human_agent/
| Doc | Scope | rot_class |
|---|---|---|
| `communication/AGENT_COMMUNICATION.md` | Hivemind, dispatch, STRP — refresh pending (pre-D-586) | medium |
| `human_agent/HUMAN_AGENT_RELATION.md` | Witness Protocol, L1→L2→L3, Human Time Tax — timeless | slow |

### Fleet-Level Cross-References (not in this tree — authoritative elsewhere)
- `EXPERT_SESSIONS.md` (this root) — my pageable expert-session index per D-586
- `MINING_LOG.md` (this root) — 22-source provenance log for the 2026-08-26 mine
- `data/coordination/PLATFORM_GNOSIS_MAP_20260818.md` — fleet platform-maturity map
- `config/domains/platforms/` — runtime-loadable domain module (curator: grokster per curators.yaml)

---

## Golden Rules (unchanged from v1)
1. Domain-first organization (KB-D-001) · 2. Insight/reference split · 3. Every doc carries freshness metadata · 4. Merge, never orphan — stubs stay for inbound links
