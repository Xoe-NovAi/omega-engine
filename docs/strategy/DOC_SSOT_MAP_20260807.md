# 🔱 DOC SSOT MAP — Single Source of Truth Routing Table
**AP Token**: `AP-DOC-SSOT-MAP-20260807-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ DOC-SANITY-UO-4 ⬡ 2026-08-07

---

## 📌 What This Is

The **canonical routing table** for the Omega Engine documentation tree. Created during the UO-4 Doc Sanity Sprint. **If you're an agent reading this, trust THIS map over your memory of old paths.**

> **Rule**: If a tool call fails with `FileNotFoundError` for a path listed in the "Archived" column, that is expected — the file moved. Do NOT resurrect old paths from memory.

---

## 🧭 ACTIVE ROUTING TABLE

| Concern | ACTIVE Path (Trust This) | Archived Path (Don't Use) |
|---------|--------------------------|---------------------------|
| **Engine state SSOT** | `OMEGA_ENGINE.md` | — |
| **Law / Mandates** | `SOVEREIGN_MANDATES.md` (v3.7.0, M1-M25) | — |
| **Strategy SSOT** | `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` (v5.2.0) | `docs/strategy/CANONICAL_ROADMAP_20260721.md` (superseded) |
| **Active sprint control** | `data/coordination/ACTIVE_SPRINT.json` | `docs/sprints/guard-and-distill/index.md` → `docs/archive/sprints/2026-07-25-guard-and-distill/index.md` |
| **Un-overengineering plan** | `data/coordination/CLINE_STRATEGIC_UNOVERENGINEERING_20260730.md` | — |
| **Doc Sanity execution** | `data/coordination/DOC_SANITY_EXECUTION_STRATEGY_20260730.md` | — |
| **Doc Sanity results** | `docs/strategy/DOC_SANITY_RESULTS_20260807.md` | — |
| **Fleet teamwork** | `docs/strategy/FLEET_TEAM_PLAYBOOK.md` | — |
| **Hivemind protocol** | `docs/strategy/HIVEMIND_PROTOCOL.md` | — |
| **Subagent dispatch** | `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` | — |
| **Coordination hub** | `data/coordination/HMC_COLLABORATION_HUB.md` (v1.6.0, lean) | `data/coordination/archive/2026-08-07-doc-sanity/HMC_COLLABORATION_HUB_archive_20260725_20260807.md` |
| **Session anchor** | `data/coordination/SESSION_ANCHOR.md` | — |
| **Pivot log (decisions)** | `docs/decisions/PIVOT_LOG.md` | — |
| **Heritage registry** | `CREDITS.md` / `CREDITS_CANONICAL.md` | — |
| **Strategy corpus** | `docs/strategy/STRATEGY_CORPUS_MAP.md` | — |
| **Strategy index** | `docs/strategy/STRATEGY_INDEX.md` | — |

---

## 🗄️ ARCHIVED LOCATIONS (UO-4 Doc Sanity — 2026-08-07)

| Archive Root | Contents |
|--------------|----------|
| `docs/archive/sprints/2026-07-25-guard-and-distill/` | Old Guard & Distill sprint (index, research index, banners applied) |
| `docs/archive/sprints/EXECUTION_PLAN_20260725.md` | Superseded fleet execution plan (banner applied) |
| `docs/archive/web-sessions/2026-08/` | 17 Web Chatbot exports (provider-fabric review, 42 Ideals, zRAM, WAD, etc.) |
| `data/coordination/archive/2026-08-07-doc-sanity/` | Stale coordination files: `KALI_*`, `GROKSTER_*`, `BRIEFING_*`, `ONBOARD_REPORT_*`, `COMPACTION_*`, old HMC Hub |

---

## 🚫 CONTEXT PROTECTION RULE

The `docs/archive/` and `data/coordination/archive/` directories contain **hundreds of thousands of tokens** of highly persuasive, **completely deprecated** strategy.

**NEVER** use `grep`, `rg`, or `read` on the `archive/` directories unless explicitly looking for historical context. Exclude them:
```bash
rg "search_term" -g "!archive/"
```

---

*⬡ OMEGA ⬡ KALI ⬡ DOC-SSOT-MAP ⬡ 2026-08-07*
