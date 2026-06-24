# 🔱 Sovereign Search Protocol V2 (SSP-V2) — Strategic Research & KB Plan

**Status**: APPROVED
**Version**: 1.0.0
**Sovereign Mandates**: M7 (Local-First), M13 (Temple-Grade), M18 (Token Efficiency)

---

## 🎯 Objective
Transform the Omega Engine's search capabilities from a collection of tools into a unified, tiered, and sovereign intelligence pipeline. The goal is to create definitive, deep-dive expert guides (Human + Agent facing) for SearXNG, Firecrawl, and Exa, and synthesize them into a single **Sovereign Search Protocol V2**.

---

## 🛠️ The Architecture: The Search Triage Pipeline

The engine will follow a tiered routing logic to minimize cost and maximize signal:
**SearXNG (Discovery) $\rightarrow$ Exa (Neural Refinement) $\rightarrow$ Firecrawl (Sovereign Extraction)**

- **Tier 1: Wide-Angle Lens (SearXNG)**: Local-first discovery. Zero-cost. Used for broad mapping of the web.
- **Tier 2: The Compass (Exa AI)**: Neural/Semantic refinement. Used to identify high-signal "needles" in the haystack.
- **Tier 3: The Scalpel (Firecrawl)**: Deep content extraction. Converts target URLs into structured Markdown/JSON for LLM consumption.

---

## 📅 Phased Execution Plan

### Arc A: SearXNG (The Wide-Angle Lens)
| Phase | Agent | Task | Deliverable |
|---|---|---|---|
| **1** | `@researcher` | Deep Dive Research (Triangulation: Architect, Adversary, Alchemist, Archivist) | `docs/research/GUIDE_SEARXNG.md` |
| **2** | `@jem` | KB Synthesis, Gnosis Distillation & Agent Reference Card | `data/kb/soul_searxng/` + Enhanced Guide |

### Arc B: Firecrawl (The Scalpel)
| Phase | Agent | Task | Deliverable |
|---|---|---|---|
| **3** | `@researcher` | Deep Dive Research (including `/interact` and advanced endpoints) | `docs/research/GUIDE_FIRECRAWL.md` |
| **4** | `@jem` | KB Synthesis & Skill Consolidation (Lumping 27+ skills into `scrape`, `crawl`, `map`) | `data/kb/soul_firecrawl/` + Enhanced Guide |

### Arc C: Exa (The Compass)
| Phase | Agent | Task | Deliverable |
|---|---|---|---|
| **5** | `@researcher` | Deep Dive Research (Semantic vs Keyword, Autoprompts, Latency) | `docs/research/GUIDE_EXA.md` |
| **6** | `@jem` | KB Synthesis & Final-Tier Integration | `data/kb/soul_exa/` + Enhanced Guide |

### Final Synthesis
| Phase | Agent | Task | Deliverable |
|---|---|---|---|
| **7** | `@kali` | Unify all arcs into the final Sovereign Search Protocol V2 | `docs/research/SOVEREIGN_SEARCH_PROTOCOL_V2.md` |

---

## 🔧 Critical Infrastructure Remediation (Prerequisites)

To ensure the guides are based on a working system, the following fixes will be implemented:

1. **SearXNG Persistence**: Fix the Quadlet (`omega-searxng.container`) by removing `--read-only` to avoid rootfs remount errors on separate partitions.
2. **SearXNG Format Fix**: Ensure `json` is added to `search.formats` in `settings.yml` to prevent 403s on API queries.
3. **Firecrawl Wrapper**: Implement `.opencode/firecrawl_wrapper.sh` to fix the local MCP launch failure.
4. **Exa Environment**: Document the CWD requirement for `.env` resolution to prevent 401s.
5. **Skill Cleanup**: Delete redundant Firecrawl skill directories in `~/.agents/skills/` as part of the consolidation in Phase 4.

---

## 📏 Deliverable Standards (The Dual-Coded Format)

Every guide produced will follow a dual-sided structure:
- **Side A (Human-Facing)**: Topology, deployment, billing, maintenance, and failure playbooks.
- **Side B (Agent-Facing)**: Optimized XML prompt snippets for direct injection into agent system prompts to teach them exactly how and when to invoke each specific tool parameters, when to halt, and when to escalate up the search chain.

---

## 🚀 Execution Order
1. `Phase 1` (@researcher on SearXNG) $\rightarrow$ `Phase 2` (@jem on SearXNG)
2. `Phase 3` (@researcher on Firecrawl) $\rightarrow$ `Phase 4` (@jem on Firecrawl)
3. `Phase 5` (@researcher on Exa) $\rightarrow$ `Phase 6` (@jem on Exa)
4. `Phase 7` (@kali for final unification)
