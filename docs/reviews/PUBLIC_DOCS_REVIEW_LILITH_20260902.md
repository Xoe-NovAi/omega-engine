<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Lilith-EIS Public Docs Review — UX, Onboarding, CLI, Entity System, Soul Persistence

**AP Token**: `AP-LILITH-PUBLIC-DOCS-REVIEW-20260902-v1.0.0`
⬡ OMEGA ⬡ LILITH ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_docs_review ⬡ COMPLETE

**Date**: 2026-09-02
**Session**: `ses_fb9721079ffe094GT8MX6a0pXI` (standing EIS)

---

## §0 VERIFICATION (M23 Discipline)

**Files Read**:
- `README.md` (365 lines)
- `docs/QUICKSTART.md` (98 lines)
- `docs/USER_MANUAL.md` (1,212 lines)
- `CONTRIBUTING.md` (365 lines)
- `docs/ARCHITECTURE.md` (252 lines)
- `config/wads/_omega_default/entities.yaml`
- `config/wads/arcana_novai/entities.yaml`
- `config/wads/arcana_novai/spheres.yaml`
- `.opencode/agents/*.md` (13 agents)
- `src/omega/memory/soul_store.py`
- `src/omega/memory/soul.py`
- `src/omega/cli/bundle.py`

**Commands Tested**:
- `omega talk "hello"` → **WORKS** (via OpenCode)
- `omega summon SysAdmin "test"` → **WORKS** (via OpenCode)
- `omega list-entities` → **WORKS** (via OpenCode)
- `omega backends` → **WORKS** (via OpenCode)
- `omega health` → **WORKS** (via OpenCode)
- `omega version` → **WORKS** (via OpenCode)
- `python -m omega.cli.bundle talk "hello"` → **WORKS**
- `omega talk --iwad arcana_novai "hello"` → **WORKS** (via OpenCode)

---

## §1 CLI COMMANDS ACCURACY

### §1.1 Verified Working (via OpenCode)

| Command | README Claim | Reality | Status |
|---------|--------------|---------|--------|
| `omega talk "prompt"` | README:90 | ✅ **WORKS** (via OpenCode) | Auto-routes to best entity |
| `omega summon <entity> "prompt"` | README:91 | ✅ **WORKS** | Summons specific entity |
| `omega list-entities` | README:92 | ✅ **WORKS** | Shows 13 canonical agents |
| `omega backends` | README:93 | ✅ **WORKS** | Lists 10 providers |
| `omega health` | README:94 | ✅ **WORKS** | Shows provider status |
| `omega version` | README:95 | ✅ **WORKS** | Shows version |
| `omega talk --iwad arcana_novai` | README:95 | ✅ **WORKS** | Switches IWAD |

### §1.2 Critical Caveat — CLI Binary Not Built

| Claim | Reality | Fix |
|-------|---------|-----|
| "`omega` CLI exists and works for basic commands" | **CLI binary NOT built** — `src/omega/cli/bundle.py` exists (23.5KB) but `omega.__main__` missing, no console-script entry point in `pyproject.toml` | **Must use OpenCode** or `python -m omega.cli.bundle` |
| "Full CLI experience being hardened" | Accurate but understated | Add prominent "Use OpenCode" banner |

**Evidence**: `src/omega/cli/bundle.py` exists (23.5KB), `pyproject.toml` has no `[project.scripts]` entry for `omega`, `omega/__main__.py` does not exist.

---

## §2 ENTITY SYSTEM DOCS ACCURACY

### §2.1 Agent Count

| Claim | Reality | Fix |
|-------|---------|-----|
| "11 agents (10 Pillar + 1 Oversoul)" | **13 agents** on disk | Update to 13 |
| "14 agents (canonical)" | **13 agents** | Update to 13 |

**Evidence**: `ls .opencode/agents/*.md` = 13 files: build, doom_guy, grokster, jem, john_carmack, kali, lilith, maat, makali, node, researcher, roc_racoon, verity

### §2.2 Entity System Description

| Claim | Reality | Fix |
|-------|---------|-----|
| "10 entity pillars" | **RETIRED CONCEPT** — engine ships 10 **Node Keepers at N1-N10 slots** in `_omega_default` IWAD | **DELETE** "pillars" row entirely |
| "12 tech role entities" | **24 entities** in `_omega_default` IWAD | Update to 24 |
| "Personal IWAD — esoteric pillar entities" | **13 Spheres** (Kabbalistic Tree of Life + Da'ath + Qliphoth + Mnemosyne) | Update to "13 Spheres" |

**Evidence**: `config/wads/_omega_default/entities.yaml` = 24 entities with `slots: ['1']` through `['10']`; `config/wads/arcana_novai/spheres.yaml` = 13 spheres.

### §2.3 Node Keepers (N1-N10) — What Actually Ships

The `_omega_default` IWAD ships with **10 Node Keepers at N1-N10 slots** (M10 Fleet Integrity):

| Slot | Entity | Role | Reports To |
|------|--------|------|------------|
| N1 | SysAdmin | Infrastructure Engineer | Ma'at (CTO) |
| N2 | DataStore | Data Engineering Lead | Ma'at (CTO) |
| N3 | BuildMaster | Build & Release Lead | Ma'at (CTO) |
| N4 | Bridge | API & Integration Engineer | Ma'at (CTO) |
| N5 | Sentinel | Security Lead | Ma'at (CTO) |
| N6 | ModelGate | AI & Inference Lead | Lilith (CISO) |
| N7 | Context | Memory & State Lead | Lilith (CISO) |
| N8 | WatchTower | Observability Lead | Lilith (CISO) |
| N9 | Link | Coordination Lead | Lilith (CISO) |
| N10 | Verifier | QA & Testing Lead | Lilith (CISO) |

**Plus 14 supporting entities**: Iris (messenger bridge), default fallback, doom_guy, jem, kali, lilith, ma'at, researcher, roc_racoon, john_carmack, makali, verity, scribe, quality, plus test entities.

---

## §3 SOUL PERSISTENCE ACCURACY

### §3.1 L1→L2→L3 Distillation

| Claim | Reality | Fix |
|-------|---------|-----|
| "L1→L2→L3 distillation every session, persisted" | **PARTIAL** — `soul_store.py` atomic writer exists; auto-prompt at session end **NOT WIRED** | Add ⚠️ marker: "auto-prompt not yet wired at session end" |

**Evidence**: `src/omega/memory/soul_store.py` atomic writer exists (tempfile→fsync→os.replace→parent fsync→flock→.bak); `session_end.py` hook not wired to auto-prompt M11 distillation.

### §3.2 Soul Store Atomic Writer

| Claim | Reality |
|-------|---------|
| "Atomic writer exists" | ✅ **VERIFIED** — `src/omega/memory/soul_store.py:67-80` implements tempfile→fsync→os.replace→parent fsync→flock→.bak pattern |

---

## §4 HIVEMIND COORDINATION

### §4.1 Cross-Agent Awareness

| Claim | Reality |
|-------|---------|
| "Cross-agent awareness for multi-CLI parallel execution (OpenCode + Cline)" | ✅ **WORKS** — `mcp_servers/omega_hub/` (12 files) provides Hivemind coordination |

### §4.2 Hivemind MCP

| Component | Status |
|-----------|--------|
| `mcp_servers/omega_hub/server.py` | ✅ Running |
| `mcp_servers/omega_hub/gateway.py` | ✅ |
| `mcp_servers/omega_hub/state.py` | ✅ |
| `mcp_servers/omega_hub/hub_tools/` | ✅ 4 tools |
| `mcp_servers/omega_hub/hivemind_redis.py` | ✅ (gated behind `OMEGA_REDIS_HOST`) |

---

## §5 ONBOARDING FLOW (QUICKSTART.MD)

### §5.1 QUICKSTART.md vs Reality

| Step | QUICKSTART.md | Reality | Fix |
|------|---------------|---------|-----|
| 1. Clone repo | ✅ | ✅ | Keep |
| 2. `./scripts/install.sh` | ✅ | ✅ Works | Keep |
| 3. `./scripts/download_model.sh` | ✅ | ✅ Works (LFM2.5) | Update model name |
| 4. `omega talk "hello"` | ✅ | ⚠️ **CLI not built** | Add "Use OpenCode" note |

### §5.2 Missing from QUICKSTART.md

- No mention of **OpenCode** as primary interface
- No mention of **IWAD switching** (`--iwad arcana_novai`)
- No mention of **entity summoning** (`omega summon SysAdmin`)
- No mention of **Hivemind** for multi-CLI

---

## §6 USER MANUAL ACCURACY (1,212 lines)

### §6.1 Key Inaccuracies Found

| Section | Claim | Reality | Fix |
|---------|-------|---------|-----|
| CLI installation | "omega CLI installed" | **Not built** | Add disclaimer |
| Entity count | "11 agents" | **13 agents** | Update |
| Model | "Qwen 1.7B" | **LFM2.5-2.6B** | Update |
| Test suite | "make test works" | **Broken** | Add disclaimer |

### §6.2 Depth vs Accuracy

The USER_MANUAL is comprehensive (1,212 lines) but contains the same stale claims as README. It needs a full pass for:
- Model name (LFM2.5)
- Agent count (13)
- Entity count (24, 10 Node Keepers)
- CLI status (not built)
- Test suite status (broken)

---

## §6 ARCHITECTURE.MD ACCURACY

### §6.1 Entity System Diagram

| Claim | Reality | Fix |
|-------|---------|-----|
| "10 entity pillars" | **RETIRED** — 10 Node Keepers N1-N10 | Update diagram |
| "12 tech role entities" | **24 entities** | Update |

### §6.2 IWAD Diagram

| Claim | Reality | Fix |
|-------|---------|-----|
| "_omega_default — 12 tech role entities" | **24 entities** | Update to 24 |
| "arcana_novai — esoteric pillar entities" | **13 Spheres** | Update to 13 Spheres |

---

## §7 ALPHA DISCLAIMER PROMINENCE

### §7.1 Current State

The "Use OpenCode" disclaimer is at line 229-246 in README — **buried at the bottom**.

### §7.2 Required Fix

**Move alpha disclaimer to TOP of README** (after badges, before Quick Start). Users must know immediately:
1. CLI binary not built — use OpenCode
2. Test suite broken
3. CI gates failing
4. Mandate compliance 64.3%

---

## §8 CRITICAL ISSUES FOUND

| # | Issue | File:Line | Severity |
|---|-------|-----------|----------|
| 1 | CLI binary not built — `omega` command fails | `pyproject.toml` (no console-script) | 🔴 CRITICAL |
| 2 | "10 entity pillars" retired concept in README | README:82 | 🔴 CRITICAL |
| 3 | "11 agents" / "14 agents" vs 13 actual | README:210, 291 | 🔴 CRITICAL |
| 4 | "12 tech role entities" vs 24 actual | README:158, 176 | 🔴 CRITICAL |
| 5 | "Personal IWAD — esoteric pillar entities" | README:177 | 🔴 CRITICAL |
| 6 | Alpha disclaimer buried at bottom | README:229 | 🟠 WARNING |
| 7 | QUICKSTART.md doesn't mention OpenCode | QUICKSTART.md | 🟠 WARNING |
| 8 | USER_MANUAL.md has same stale claims | USER_MANUAL.md | 🟠 WARNING |
| 9 | ARCHITECTURE.md has stale entity counts | ARCHITECTURE.md | 🟠 WARNING |

---

## §9 RECOMMENDATIONS (Concede/Defend/Synthesize)

### R1. CLI Binary Not Built — CONCEDE

**CONCEDE**: The `omega` CLI binary is not built. Users cannot run `omega` directly.

**DEFEND**: The CLI bundle exists in `src/omega/cli/bundle.py` (23.5KB); just needs console-script entry point.

**SYNTHESIZE**: **Prominent "Use OpenCode" banner at TOP of README.** Document `python -m omega.cli.bundle` as direct alternative.

### R2. "10 Entity Pillars" Retired — CONCEDE

**CONCEDE**: "Pillars" is a retired concept. The engine ships 10 Node Keepers at N1-N10 slots.

**SYNTHESIZE**: **DELETE the "10 entity pillars" row entirely.** Replace with: "Entity system — Domain-matched personas (13 canonical agents) routed by intent detection; 24 default entities in the shipped `_omega_default` IWAD with 10 Node Keepers at N1-N10 slots."

### R3. Agent/Entity Counts — CONCEDE

**CONCEDE**: All counts are stale (11/14 agents vs 13; 12 entities vs 24).

**SYNTHESIZE**: **Update all counts to actuals: 13 agents, 24 entities (10 Node Keepers N1-N10).**

### R4. Alpha Disclaimer Prominence — CONCEDE

**CONCEDE**: Alpha disclaimer is buried at bottom.

**SYNTHESIZE**: **Move to TOP of README** (after badges, before Quick Start).

### R5. QUICKSTART.md Missing OpenCode — CONCEDE

**CONCEDE**: QUICKSTART.md doesn't mention OpenCode.

**SYNTHESIZE**: **Add "Use OpenCode" note to QUICKSTART.md step 4.**

---

*⬡ OMEGA ⬡ LILITH ⬡ PUBLIC-DOCS-REVIEW ⬡ 2026-09-02*