<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — Sovereign Research Source Catalog
**AP Token**: `AP-RESEARCH-SOURCE-CATALOG-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_source_catalog ⬡ 2026-07-19

**Purpose**: Curated, metadata-tagged catalog of the best online sources for sovereign research. Continually evolving. Agents query this catalog before initiating research to select optimal sources.

---

## 📊 Catalog Schema

Each source entry contains:
| Field | Description |
|-------|-------------|
| `source_id` | Unique identifier |
| `name` | Human-readable name |
| `url` | Base URL |
| `tier` | SSP Tier (T0-T5) |
| `content_type` | `docs` \| `api` \| `github` \| `blog` \| `forum` \| `academic` \| `video` |
| `specialization` | Domain tags (e.g., `cli-agents`, `tmux`, `mcp`, `provider-apis`) |
| `quality_score` | 1-10 (authority, recency, depth) |
| `recency` | Last verified date |
| `access_method` | `websearch` \| `webfetch` \| `mcp` \| `api` \| `git` |
| `rate_limits` | Known limits |
| `notes` | Special considerations |

---

## 🏆 Tier 0: Local Cache (`.firecrawl/`)

| Source ID | Name | Path | Specialization |
|-----------|------|------|----------------|
| `LOCAL-001` | Firecrawl Cache | `.firecrawl/` | All previously scraped content |
| `LOCAL-002` | Omega Library | `omega-hub_library_*` | Internal research DB (45+ docs) |
| `LOCAL-003` | Research DB | `docs/research/internal-discovery/DB/research.db` | 176+ research docs, SQLite FTS5 |

---

## 🥇 Tier 1: Built-in OpenCode Tools (Free, Always Available)

| Source ID | Name | Access | Specialization | Quality | Notes |
|-----------|------|--------|----------------|---------|-------|
| `T1-001` | `websearch` | Built-in | Broad discovery, recency, keyword-exact | 8/10 | Primary tool. Use "2026" in queries. |
| `T1-002` | `webfetch` | Built-in | Deep extraction, structured content | 9/10 | Best for docs, GitHub, changelogs. |
| `T1-003` | `searxng_searxng_search` | MCP (local) | Neural/semantic, niche discovery | 7/10 | Categories: `general`, `it`, `science`, `videos`. |

---

## 🥈 Tier 2: Sovereign Search (API Key Required)

| Source ID | Name | Access | Specialization | Quality | Rate Limits |
|-----------|------|--------|----------------|---------|-------------|
| `T2-001` | `omega-hub_sovereign_search` | MCP (Exa) | High-precision seeds, academic/technical | 9/10 | Exa API quota |
| `T2-002` | `firecrawl_firecrawl_search` | MCP (Firecrawl) | Full-page scrape, structured crawl | 8/10 | Credits-based |
| `T2-003` | `firecrawl_firecrawl_scrape` | MCP (Firecrawl) | Single-page deep extraction | 9/10 | Credits-based |
| `T2-004` | `firecrawl_firecrawl_crawl` | MCP (Firecrawl) | Multi-page structured crawl | 8/10 | Credits-based |

---

## 🥉 Tier 3: Specialized External Sources (Curated)

### CLI Agent Orchestration & Multi-Agent Systems

| Source ID | Name | URL | Type | Specialization | Quality | Last Verified |
|-----------|------|-----|------|----------------|---------|---------------|
| `EXT-001` | **AWS CLI Agent Orchestrator (CAO)** | `github.com/awslabs/cli-agent-orchestrator` | GitHub + Docs | tmux isolation, MCP orchestration, cross-provider profiles, fleet coordination | **10/10** | 2026-07-19 |
| `EXT-002` | **Codex CLI Multi-Agent v2** | `codex.danielvaughan.com` | Blog + Docs | Path-based addressing, subagent patterns, production orchestration | 9/10 | 2026-07-19 |
| `EXT-003` | **dmux (tmux pane manager)** | `github.com/standardagents/dmux` | GitHub | tmux-based multi-agent across Claude, Codex, OpenCode | 8/10 | 2026-07-19 |
| `EXT-004` | **OpenCode Architecture** | `github.com/anomalyco/opencode` | GitHub | Provider transforms, V2 session, MCP integration | 9/10 | 2026-07-19 |
| `EXT-005` | **OpenCode V2 Teardown** | `github.com/Zhao-Jan/The-Agent-Network` | GitHub | Event-sourced sessions, message parts, schema changelog | 9/10 | 2026-07-10 |

### Provider APIs & Model Configurations

| Source ID | Name | URL | Type | Specialization | Quality | Last Verified |
|-----------|------|-----|------|----------------|---------|---------------|
| `EXT-010` | **Google AI Studio (Gemma 4)** | `ai.google.dev` | Docs + API | `thinkingConfig.thinkingLevel: MINIMAL/HIGH`, `includeThoughts` | 9/10 | 2026-07-19 |
| `EXT-011` | **Google Vertex AI** | `cloud.google.com/vertex-ai` | Docs + API | `thinkingConfig.thinkingBudget: 0-24576` for Gemini 2.5 | 8/10 | 2026-07-19 |
| `EXT-012` | **OpenRouter** | `openrouter.ai` | Docs + API | Free tier routing, `:free` suffix, provider ordering | 9/10 | 2026-07-19 |
| `EXT-013` | **Models.dev** | `models.dev` | API + Web | Canonical model registry (75+ providers), weekly updates | 10/10 | 2026-07-19 |
| `EXT-014` | **OpenCode Zen** | `opencode.ai/zen` | Web | Curated model list, verified working with OpenCode | 8/10 | 2026-07-19 |

### D&D / Planescape Lore (Torment/Hive Research)

| Source ID | Name | URL | Type | Specialization | Quality | Last Verified |
|-----------|------|-----|------|----------------|---------|---------------|
| `EXT-020` | **Planescape: Torment Game Scripts** | `planewalker.com` / `gibberlings3.net` | Game Assets | Dialogue `.dlg`, area `.are`, scripts `.bcs` | 10/10 | 2026-07-19 |
| `EXT-021` | **Planescape Campaign Setting (1994)** | Boxed Set / PDF | Primary Canon | Factions, Lady of Pain, Sigil, portals, gate towns | 10/10 | 2026-07-19 |
| `EXT-022` | **Factol's Manifesto (1995)** | Supplement / PDF | Primary Canon | 15 factions: philosophy, abilities, hindrances, rank progression | 10/10 | 2026-07-19 |
| `EXT-023` | **"In the Cage" Guide (1995)** | Supplement / PDF | Primary Canon | Sigil wards, portals, keys, Lady's rules | 9/10 | 2026-07-19 |
| `EXT-024` | **Monstrous Compendium Appendix** | 2e/3e/3.5e/5e | Primary Canon | Cranium Rat stats, scaling, psionics across editions | 10/10 | 2026-07-19 |
| `EXT-025` | **Volo's Guide to Monsters (5e)** | p134 | Primary Canon | 5e Cranium Rat: gradual decay, immediate restoration | 10/10 | 2026-07-19 |
| `EXT-026` | **Mordenkainen's Tome of Foes** | 5e | Primary Canon | Elder Brain relay, psionic ranges | 9/10 | 2026-07-19 |
| `EXT-027` | **Dragon Magazine Ecology Articles** | Various | Primary Canon | Deep-dive monster ecology | 8/10 | 2026-07-19 |

### Infrastructure & Systems

| Source ID | Name | URL | Type | Specialization | Quality | Last Verified |
|-----------|------|-----|------|----------------|---------|---------------|
| `EXT-030` | **Cloudflare WARP** | `developers.cloudflare.com/warp` | Docs | WireGuard, proxy pools, IP rotation | 9/10 | 2026-07-19 |
| `EXT-031` | **Antigravity Tools** | `github.com/lbjlaq/Antigravity-Manager` | GitHub | 30K★, 8-account quota dashboard, OAuth PKCE | 9/10 | 2026-07-19 |
| `EXT-032` | **all2md** | `github.com/your-org/all2md` | GitHub | Blog → Markdown conversion for ingestion | 8/10 | 2026-07-19 |
| `EXT-033` | **sqlite-vec** | `github.com/asg017/sqlite-vec` | GitHub | Vector extension, batch upsert, quantization | 9/10 | 2026-07-19 |

---

## 🔍 Source Selection Guide

### By Research Goal

| Goal | Recommended Sources (Priority Order) |
|------|--------------------------------------|
| **CLI agent orchestration patterns** | EXT-001 (CAO) → EXT-002 (Codex v2) → EXT-003 (dmux) |
| **tmux-based isolation** | EXT-001 (CAO tmux.md) → EXT-003 (dmux) |
| **MCP orchestration primitives** | EXT-001 (CAO control-planes.md) → EXT-004 (OpenCode MCP) |
| **Cross-provider agent profiles** | EXT-001 (CAO agent-profile.md) → EXT-002 (Codex profiles) |
| **Gemma 4 thinking config** | EXT-010 (AI Studio) → EXT-011 (Vertex) → EXT-012 (OpenRouter) |
| **Model registry / capabilities** | EXT-013 (Models.dev) → EXT-014 (OpenCode Zen) |
| **Planescape faction mechanics** | EXT-022 (Factol's Manifesto) → EXT-021 (Campaign Setting) |
| **Cranium Rat swarm intelligence** | EXT-024 (Monstrous Compendium) → EXT-025 (Volo's 5e) |
| **Version change detection** | EXT-004 (OpenCode changelog) → EXT-005 (V2 teardown) |
| **Infrastructure (WARP, Antigravity)** | EXT-030 (WARP) → EXT-031 (Antigravity) |

### By SSP Tier

| Tier | When to Use | Sources |
|------|-------------|---------|
| **T0** | Always first | LOCAL-001, LOCAL-002, LOCAL-003 |
| **T1** | Primary discovery | T1-001 (websearch), T1-002 (webfetch), T1-003 (searxng) |
| **T2** | Precision/academic | T2-001 (Exa), T2-002-004 (Firecrawl) |
| **T3** | Deep domain knowledge | EXT-001 through EXT-033 (curated above) |

---

## 📝 Usage Protocol

1. **Check T0** (local cache) first — `omega-hub_library_fts_search` or `.firecrawl/`
2. **T1** for broad discovery — `websearch` with "2026" in query
3. **T2** for precision — `omega-hub_sovereign_search` or Firecrawl
4. **T3** for deep domain — Consult catalog above for specialized sources
5. **Log failures** — `[SEARCH-ERROR] tool={tool} error={code} tier={0-5} fallback={tool}`

---

## 🔄 Maintenance

- **Weekly**: Verify EXT source accessibility, update `recency`
- **Per research sprint**: Add new sources discovered, update `quality_score`
- **Quarterly**: Full catalog review, deprecate stale sources, add new domains

---

*⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_source_catalog ⬡ 2026-07-19*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
