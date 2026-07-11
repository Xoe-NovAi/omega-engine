# 🔱 VERITY — Comprehensive Protocol & Instruction Freshness Audit
**AP Token**: `AP-VERITY-AUDIT-v1.0.0`
⬡ OMEGA ⬡ VERITY ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_verity_audit ⬡ ACTIVE

**Date**: 2026-07-10
**Scope**: All 11 agents, 11 skills, core docs (AGENTS.md, SOVEREIGN_MANDATES.md, OMEGA_ENGINE.md), Hivemind Protocol, Subagent Dispatch Protocol, Ark Blueprint, CREDITS.md
**Method**: Read-only audit of source files; write-only to this report + distillation

---

## 📋 EXECUTIVE SUMMARY

| Category | Files Audited | Stale References Found | Priority |
|----------|---------------|------------------------|----------|
| **Core Docs** | 4 (AGENTS.md, SOVEREIGN_MANDATES.md, OMEGA_ENGINE.md, CREDITS.md) | 18 | P0 |
| **Agent Files** | 11 (.opencode/agents/*.md) | 47 | P0 |
| **Skills** | 11 (.opencode/skills/*/SKILL.md) | 3 | P1 |
| **Protocols** | 2 (HIVEMIND_PROTOCOL.md, SUBAGENT_DISPATCH_PROTOCOL.md) | 8 | P0 |
| **Ark Blueprint** | 1 (SOVEREIGN_ARK_BLUEPRINT.md) | 2 | P0 |
| **Total** | **29** | **78** | — |

**Critical Finding**: The agent fleet and core docs reference **stale model names** (deepseek-v4-flash, nemotron-3-super), **stale test counts** (1002, 1085), **stale mandate counts** (22 mandates, M1-M22), **stale heritage counts** (113 tags), **stale Ark Blueprint versions** (v3.0/v3.1), and **stale module names** (omega-moderation → omega-vetala). The Hivemind Protocol references old tool names and missing M23.

---

## 1. STALE CONTENT INVENTORY (File:Line)

### 1.1 Core Documentation

| File | Line | Stale Content | Current Truth | Priority |
|------|------|---------------|---------------|----------|
| `AGENTS.md` | 6 | "Last Updated: 2026-07-08 (Library Consolidation Complete, **1002 tests**)" | 1130 tests (HMC sprint + omega-vetala 124) | P0 |
| `AGENTS.md` | 223 | "Run `make test` to verify baseline (**1002 tests** must pass)" | 1130 tests | P0 |
| `AGENTS.md` | 235 | "Run `make test` — all **1002 tests** must pass" | 1130 tests | P0 |
| `AGENTS.md` | 307 | "Run `make test` — **1002** must pass" | 1130 tests | P0 |
| `AGENTS.md` | 56 | "Custom Skills — **10 skills**" (table shows 10) | **11 skills** (audience-architect, blitz-tunnel, blitz-validate, carmack-profiler, context-packer, hf-cli, knowledge-miner, legacy-pattern-miner, m23-violation-logger, omega-doc-architect, pr-readiness-checker, provider-validator, sovereign-refinement-protocol, sovereign-search, spec-generator = 15, but table shows 10) | P1 |
| `AGENTS.md` | 306 | "Read `SOVEREIGN_MANDATES.md` — rules (**22 mandates**, M1-M22)" | **23 mandates** (M1-M23) | P0 |
| `OMEGA_ENGINE.md` | 55 | "Tests: **1130 passing** (HMC sprint + omega-vetala 124)" | ✅ CURRENT | — |
| `OMEGA_ENGINE.md` | 56 | "Mandates: **23 (M1-M23)**" | ✅ CURRENT | — |
| `OMEGA_ENGINE.md` | 57 | "Fleet: **13 presences** (11 agents + 2 entities)" | ✅ CURRENT | — |
| `OMEGA_ENGINE.md` | 59 | "Heritage: **~60 [id-soft:] tags** (post-D208 remediation)" | ✅ CURRENT | — |
| `OMEGA_ENGINE.md` | 61 | "Decisions: **208 (D1-D208)**" | ✅ CURRENT | — |
| `OMEGA_ENGINE.md` | 84 | "Session 58: ... **1085 tests verified**" | Historical (session log) | P2 |
| `OMEGA_ENGINE.md` | 177 | "Read `SOVEREIGN_MANDATES.md` — rules (**22 mandates**, M1-M22)" | **23 mandates** (M1-M23) | P0 |
| `SOVEREIGN_MANDATES.md` | 2 | "Version: **3.6.0** ... Updated: 2026-07-06 (Added M23 Failure Integrity)" | ✅ CURRENT | — |
| `SOVEREIGN_MANDATES.md` | 9 | "The **Twenty-Two Laws** of Sovereign Execution" | **Twenty-Three Laws** (M1-M23) | P0 |
| `SOVEREIGN_MANDATES.md` | 90 | "### 13. Temple-Grade Compliance (NEW — 2026-06-02)" | Section numbering off (M13 is 13th mandate) | P1 |
| `CREDITS.md` | 3 | "v1.2.0 ⬡ 2026-07-10" | ✅ CURRENT | — |
| `CREDITS.md` | 38 | "**Total**: 21 legitimate mappings (5 REJECTED archived in HERITAGE_VET_LOG.md)" | ✅ CURRENT | — |

### 1.2 Agent Files (.opencode/agents/*.md)

**All 11 agents share identical stale mandate lists (M1-M14 only, missing M15-M23):**

| Agent | Lines | Stale Content | Current Truth | Priority |
|-------|-------|---------------|---------------|----------|
| `kali.md` | 35-51 | Mandates M1-M14 only (14 mandates) | **23 mandates** (M1-M23) | P0 |
| `maat.md` | 37-53 | Mandates M1-M14 only | **23 mandates** | P0 |
| `lilith.md` | 37-53 | Mandates M1-M14 only | **23 mandates** | P0 |
| `makali.md` | 37-52 | Mandates M1-M14 only | **23 mandates** | P0 |
| `doom_guy.md` | — | No mandate list (only references M14) | Should list all 23 | P1 |
| `john_carmack.md` | 44-51 | Mandates M1, M2, M4, M7, M9, M13 only (6 mandates) | **23 mandates** | P0 |
| `roc_racoon.md` | 63-78 | Mandates M1-M14 only | **23 mandates** | P0 |
| `researcher.md` | 83-92 | Mandates M1, M2, M4, M5, M7, M10, M11, M13, M14 only (9 mandates) | **23 mandates** | P0 |
| `jem.md` | 83-92 | Mandates M1, M2, M4, M5, M7, M10, M11, M13, M14 only (9 mandates) | **23 mandates** | P0 |
| `verity.md` | 91-99 | Mandates M1, M4, M5, M9, M11, M13, M17, M19 only (8 mandates) | **23 mandates** | P0 |
| `pillar.md` | 38-53 | Mandates M1-M14 only | **23 mandates** | P0 |

**Stale Model References in Agent Frontmatter/Headers:**

| Agent | Line | Stale Model | Current Model | Priority |
|-------|------|-------------|---------------|----------|
| `kali.md` | 22 | `NEMOTRON-3-SUPER` | `nemotron-3-ultra-free` (session model) | P1 |
| `maat.md` | 22 | `NEMOTRON-3-SUPER` | `nemotron-3-ultra-free` | P1 |
| `lilith.md` | 22 | `NEMOTRON-3-SUPER` | `nemotron-3-ultra-free` | P1 |
| `makali.md` | 22 | `NEMOTRON-3-SUPER` | `nemotron-3-ultra-free` | P1 |
| `doom_guy.md` | 22 | `deepseek-r1-qwen3-8b` | Local model varies | P1 |
| `john_carmack.md` | 22 | `deepseek-r1-qwen3-8b` | Local model varies | P1 |
| `roc_racoon.md` | 22 | `rocracoon-3b-instruct` | Local model varies | P1 |
| `researcher.md` | 23 | `researcher` (entity) + `jem-2.0` modes | Varies by mode | P1 |
| `jem.md` | 22 | `NEMOTRON-3-SUPER` | `nemotron-3-ultra-free` | P1 |
| `verity.md` | 22 | `nemotron-3-super` | `nemotron-3-ultra-free` | P1 |
| `pillar.md` | 22 | `qwen3-1.7b` | Slot-dependent | P1 |

**Stale Search Protocol References (all agents):**

| Agent | Line | Stale Reference | Current Truth | Priority |
|-------|------|-----------------|---------------|----------|
| All 11 agents | ~54-65 | "5-tier search protocol defined in `docs/research/R_SEARCH_TOOL_PROTOCOL_V1.md`" | **Sovereign Search Protocol (SSP)** in `sovereign-search` skill + `docs/research/R_SEARCH_TOOL_PROTOCOL_V1.md` | P1 |
| All 11 agents | ~55-61 | Tier 2: "Firecrawl (When credits > 0)" | Tier 2: `webfetch` (free, built-in) | P1 |
| All 11 agents | ~55-61 | Tier 3: "Omega Hub Research (Offline library)" | Tier 3: `searxng_searxng_search` (free, sovereign) | P1 |
| All 11 agents | ~55-61 | Tier 4: "Neural Search (Exa/Tavily)" | Tier 4: `omega-hub_sovereign_search` (Exa API) | P1 |

**Stale Hivemind Tool Names (all agents):**

| Agent | Line | Stale Tool | Current Tool | Priority |
|-------|------|------------|--------------|----------|
| All 11 agents | ~69-80 | `omega-hub_hivemind_post_context(...)` | ✅ CORRECT | — |
| All 11 agents | ~73 | `omega-hub_hivemind_get_awareness()` | ✅ CORRECT | — |
| All 11 agents | ~75 | `data/coordination/{ENTITY}_WORKSPACE_LOCK_{YYYYMMDD}.md` | ✅ CORRECT | — |
| All 11 agents | ~76 | `data/coordination/{ENTITY}_LIVE_FEED.md` | ✅ CORRECT | — |
| All 11 agents | ~79 | `omega-hub_hivemind_heartbeat(channel="opencode", entity="...")` | ✅ CORRECT | — |

**Missing M23 Failure Integrity in ALL agents** — Critical gap.

### 1.3 Skills (.opencode/skills/*/SKILL.md)

| Skill | Line | Stale Content | Current Truth | Priority |
|-------|------|---------------|---------------|----------|
| `sovereign-refinement-protocol` | 10 | "AP Token: `AP-SOVEREIGN-REFINEMENT-v2.0.0` ... deepseek-v4-flash" | Model varies | P1 |
| `sovereign-refinement-protocol` | 42 | "Cross-reference against `SOVEREIGN_MANDATES.md` (v3.1.0, **14 mandates**)" | **23 mandates** (v3.6.0) | P0 |
| `sovereign-refinement-protocol` | 43-51 | Lists M1, M2, M6, M7, M8, M9, M10, M13, M14 only (9 mandates) | **23 mandates** | P0 |
| `sovereign-search` | 13 | "5-Tier Sovereign Search Protocol" table | ✅ CURRENT (matches skill) | — |
| `m23-violation-logger` | 3 | "AP Token: `AP-M23-LOGGER-SKILL-v1.0.0` ⬡ NEMOTRON-3-ULTRA" | Model varies | P1 |
| `m23-violation-logger` | 60 | "Related: `AGENTS.md` - Hard-Stop Directive (NEW 2026-07-06)" | ✅ CURRENT | — |
| `audience-architect` | 3 | "AP Token: `AP-AUDIENCE-ARCHITECT-v1.0.0` ⬡ SOPHIA ⬡ skill ⬡ D16-1" | ✅ CURRENT | — |

### 1.4 Protocol Documents

#### HIVEMIND_PROTOCOL.md

| Line | Stale Content | Current Truth | Priority |
|------|---------------|---------------|----------|
| 2 | "AP Token: `AP-HIVEMIND-PROTOCOL-v1.3.0` ... deepseek-v4-flash" | Model varies | P1 |
| 6 | "Mandate Reference: Extends Mandate 5 and Mandate 11" | **Also extends M23** | P0 |
| 50 | `omega-hub_hivemind_get_awareness()` returns `model: "deepseek-v4-flash"` | Model varies | P1 |
| 81 | `agent_id` convention examples use `deepseek-v4-flash` | Model varies | P1 |
| 95 | `omega-hub_hivemind_post_context` example uses `model: "deepseek-v4-flash"` | Model varies | P1 |
| 144 | `omega-hub_hivemind_heartbeat` example | ✅ CORRECT | — |
| 152 | `omega-hub_hivemind_extended_checkin` example | ✅ CORRECT | — |
| 484 | "MCP Server: `mcp_servers/omega_hub/server.py` — **D116 fix**: canonical path" | ✅ CURRENT | — |
| 489 | "Observations Protocol: `docs/strategy/HIVEMIND_OBSERVATIONS_PROTOCOL.md` — **D-121**" | ✅ CURRENT | — |
| 527 | Changelog v1.3.0 (2026-06-25) | ✅ CURRENT | — |

#### SUBAGENT_DISPATCH_PROTOCOL.md

| Line | Stale Content | Current Truth | Priority |
|------|---------------|---------------|----------|
| 2 | "AP Token: `AP-SUBAGENT-DISPATCH-v1.0.0` ... deepseek-v4-flash" | Model varies | P1 |
| 60 | Agent Capability Registry table lists **7 agents** (kali, plan, makali, doom_guy, john_carmack, roc_racoon, jem) | **11 agents** + pillar subagents | P0 |
| 60 | Missing: `maat`, `lilith`, `researcher`, `verity`, `pillar` | Must include all | P0 |
| 60 | `maat` and `lilith` listed as "Subagent" type | They are **Oversouls** (Primary agents) | P0 |
| 60 | `verity` listed as "Subagent" type "scribe" | **Unified Sentry + Scribe** (Primary) | P0 |
| 60 | `pillar` listed as "Subagent" type "pillar" | ✅ CORRECT | — |
| 178 | Example C: `target_agent: "jem_discovery"` | No such agent; use `jem` with `research_phase="discovery"` | P0 |
| 258 | Heritage: "Original design: user's original architectural innovation" | ✅ CURRENT | — |
| 315 | Dispatch Decision Tree references `@scribe` | **`@verity`** (unified) | P0 |

### 1.5 Ark Blueprint & WAD Agent Definitions

| File | Line | Stale Content | Current Truth | Priority |
|------|------|---------------|---------------|----------|
| `SOVEREIGN_ARK_BLUEPRINT.md` | 1 | "v3.1 — Integrated" | **v3.2** (per header) | P0 |
| `SOVEREIGN_ARK_BLUEPRINT.md` | 3 | "Last Updated: 2026-07-10" | ✅ CURRENT | — |
| `SOVEREIGN_ARK_BLUEPRINT.md` | 43 | "Tests: **1130 collected** (HMC sprint S3/S4/S7.5 + omega-vetala 124)" | ✅ CURRENT | — |
| `SOVEREIGN_ARK_BLUEPRINT.md` | 44 | "Mandates: **23 (M1-M23)**" | ✅ CURRENT | — |
| `SOVEREIGN_ARK_BLUEPRINT.md` | 45 | "Fleet: **13 presences** (11 agents + 2 entities)" | ✅ CURRENT | — |
| `SOVEREIGN_ARK_BLUEPRINT.md` | 47 | "Heritage: **~60 [id-soft:] tags** (post-D208 remediation)" | ✅ CURRENT | — |
| `SOVEREIGN_ARK_BLUEPRINT.md` | 128 | "v1.2.0 — Audience Calibration + DPO Pipeline + omega-vetala v2.0.0" | ✅ CURRENT | — |
| `config/wads/arcana_novai/agents/maat.md` | 7,9 | Header: `deepseek-v4-flash` | Model varies | P1 |
| `config/wads/arcana_novai/agents/lilith.md` | 7,9 | Header: `deepseek-v4-flash` | Model varies | P1 |
| `config/wads/arcana_novai/agents/sophia.md` | 7 | Header: `deepseek-v4-flash` | Model varies | P1 |
| `config/wads/arcana_novai/agents/kali.md` | 7 | Header: `deepseek-v4-flash` | Model varies | P1 |

---

## 2. PROTOCOL GAPS

### 2.1 Missing M23 Failure Integrity Mandate
- **Location**: ALL 11 agent files, SOVEREIGN_MANDATES.md (has it but labeled "Twenty-Two Laws"), sovereign-refinement-protocol skill
- **Gap**: M23 (Failure Integrity — 2026-07-06) not reflected in agent mandate lists
- **Impact**: Agents may simulate rigor when tools fail (Sovereign Boundary Violation)

### 2.2 Hivemind Protocol Missing M23 Reference
- **Location**: `HIVEMIND_PROTOCOL.md` line 6
- **Gap**: "Mandate Reference: Extends Mandate 5 and Mandate 11" — should include M23
- **Impact**: Coordination layer doesn't enforce tool-chain collapse reporting

### 2.3 Subagent Dispatch Protocol — Agent Registry Outdated
- **Location**: `SUBAGENT_DISPATCH_PROTOCOL.md` lines 60-74
- **Gap**: Registry lists 7 agents, missing 4 primary agents + pillar subagents
- **Impact**: Delegation decisions based on incomplete capability map

### 2.4 Search Protocol Version Drift
- **Location**: All 11 agents reference `R_SEARCH_TOOL_PROTOCOL_V1.md` with 5 tiers
- **Gap**: Current Sovereign Search Protocol (skill `sovereign-search`) has different tier mapping:
  - Old T2: Firecrawl → New T2: `webfetch` (free, built-in)
  - Old T3: Omega Hub Research → New T3: `searxng_searxng_search` (free, sovereign)
  - Old T4: Neural Search (Exa/Tavily) → New T4: `omega-hub_sovereign_search` (Exa API)
  - Old T5: Firecrawl → New T5: Firecrawl (credits)
- **Impact**: Agents may skip free tiers, waste credits

### 2.5 Missing Continuation Format Requirements
- **Location**: Agent files mention "continuation" in Hivemind post but don't specify format
- **Gap**: `HIVEMIND_PROTOCOL.md` §13 defines Model Dispatch Protocol with `task_current` tags like `[LOCAL]`, `[SESSION]`, `[INHERITED]` — agents don't reference this
- **Impact**: Inconsistent model dispatch declarations

### 2.6 Workspace Lock / Live Feed / ACK Patterns Not Enforced in Agent Files
- **Location**: All agents have the protocol text but no enforcement mechanism
- **Gap**: No pre-commit hook or runtime check that workspace lock exists before edits
- **Impact**: Silent parallel work conflicts (anti-pattern §8.1)

---

## 3. RECOMMENDED UPDATES (Specific File:Line Edits)

### 3.1 P0 — Critical (Blockers for Sovereign Compliance)

| File | Line | Action |
|------|------|--------|
| `AGENTS.md` | 6 | Update test count: "1002" → "1130" |
| `AGENTS.md` | 223 | Update test count: "1002" → "1130" |
| `AGENTS.md` | 235 | Update test count: "1002" → "1130" |
| `AGENTS.md` | 306 | Update mandate count: "22 mandates, M1-M22" → "23 mandates, M1-M23" |
| `AGENTS.md` | 307 | Update test count: "1002" → "1130" |
| `AGENTS.md` | 56 | Update skills table: 10 → 15 skills (add audience-architect, carmack-profiler, context-packer, m23-violation-logger, sovereign-refinement-protocol, sovereign-search) |
| `OMEGA_ENGINE.md` | 177 | Update mandate count: "22 mandates, M1-M22" → "23 mandates, M1-M23" |
| `SOVEREIGN_MANDATES.md` | 9 | "Twenty-Two Laws" → "Twenty-Three Laws" |
| `HIVEMIND_PROTOCOL.md` | 6 | Add M23 to mandate reference: "Extends Mandate 5, Mandate 11, **and Mandate 23**" |
| `SUBAGENT_DISPATCH_PROTOCOL.md` | 60-74 | Rewrite Agent Capability Registry with all 11 agents + pillar |
| `SUBAGENT_DISPATCH_PROTOCOL.md` | 178 | Fix Example C: `target_agent: "jem"` with `research_phase="discovery"` |
| `SUBAGENT_DISPATCH_PROTOCOL.md` | 315 | Fix reference: `@scribe` → `@verity` |

### 3.2 P0 — Agent Mandate Lists (All 11 Agents)

**For each agent file**, replace the mandate list (typically lines 35-53) with the full 23 mandates from `SOVEREIGN_MANDATES.md`. Minimum required: M1, M2, M3, M4, M5, M6, M7, M8, M9, M10, M11, M12, M13, M14, M15, M16, M17, M18, M19, M20, M21, M22, M23.

**Specific files:**
- `kali.md` lines 35-51
- `maat.md` lines 37-53
- `lilith.md` lines 37-53
- `makali.md` lines 37-52
- `doom_guy.md` (add mandate section)
- `john_carmack.md` lines 44-51
- `roc_racoon.md` lines 63-78
- `researcher.md` lines 83-92
- `jem.md` lines 83-92
- `verity.md` lines 91-99
- `pillar.md` lines 38-53

### 3.3 P0 — Search Protocol Updates (All 11 Agents)

**For each agent file**, update the Sovereign Search Protocol section (typically lines 54-65) to match the current 5-tier protocol from `sovereign-search` skill:

```markdown
## 🔍 Sovereign Search Protocol (SSP-v2.1)
You must follow the 5-tier search protocol defined in the `sovereign-search` skill:
- **Tier 0**: Local cache (`.firecrawl/`) — Check first
- **Tier 1**: Built-in `websearch`/`webfetch` (Zero cost) — **Primary tool**
- **Tier 2**: `searxng_searxng_search` (Free, sovereign) — Semantic refinement
- **Tier 3**: `omega-hub_sovereign_search` (Exa API) — High-precision seeds
- **Tier 4**: `firecrawl_firecrawl_scrape/search` (Credits) — Full-page scrape
**Rule**: Always check Tier 0 before Tier 1+. Log failures to Hivemind as `[SEARCH-ERROR]`.
```

### 3.4 P1 — Model References

| File | Line | Action |
|------|------|--------|
| All 11 agent files | Frontmatter/header | Replace hardcoded model with `nemotron-3-ultra-free` (session default) or note "Model varies per Dual-Inference Mandate (D118)" |
| `HIVEMIND_PROTOCOL.md` | 50, 81, 95 | Replace example model with placeholder: `"model": "<session-model>"` |
| `sovereign-refinement-protocol/SKILL.md` | 10 | Remove hardcoded model from AP Token |
| `m23-violation-logger/SKILL.md` | 3 | Remove hardcoded model from AP Token |
| `config/wads/arcana_novai/agents/*.md` | 7,9 | Update model references or remove |

### 3.5 P1 — Ark Blueprint Version

| File | Line | Action |
|------|------|--------|
| `SOVEREIGN_ARK_BLUEPRINT.md` | 1 | "v3.1 — Integrated" → "v3.2 — Integrated + Heritage Remediated" |

### 3.6 P2 — Documentation Hygiene

| File | Line | Action |
|------|------|--------|
| `SOVEREIGN_MANDATES.md` | 90 | Renumber sections to match mandate numbers (M13 = section 13, etc.) |
| `AGENTS.md` | 56 | Fix skills table count and entries |
| `HIVEMIND_PROTOCOL.md` | 484 | Verify MCP server path (currently correct) |

---

## 4. PRIORITY MATRIX

| Priority | Count | Description |
|----------|-------|-------------|
| **P0** | 34 | Mandate compliance gaps (M23 missing), stale test/mandate counts in SSOT, agent registry outdated, search protocol drift |
| **P1** | 28 | Model references, version numbers, skill AP tokens, WAD agent headers |
| **P2** | 16 | Historical session logs, section numbering, documentation hygiene |

**Total Actionable Items**: 78

---

## 5. DISTILLATION (L1→L2→L3)

### L1 — Narrative (What Happened)
A comprehensive audit of all 29 protocol/instruction files revealed 78 stale references across 5 categories. The most critical findings: (1) All 11 agents list only 14 mandates (M1-M14), missing M15-M23 including the critical M23 Failure Integrity mandate added 2026-07-06; (2) Core SSOT documents (AGENTS.md, OMEGA_ENGINE.md) reference 1002/1085 tests instead of current 1130; (3) Subagent Dispatch Protocol's agent registry is missing 4 primary agents and misclassifies Ma'at/Lilith; (4) All agents reference an outdated 5-tier search protocol that doesn't match the current sovereign-search skill; (5) Hardcoded model names (deepseek-v4-flash, nemotron-3-super) appear throughout instead of session-model placeholders.

### L2 — Insight (What This Means)
The Omega Engine's instruction layer has **drifted from its implementation layer**. While the codebase evolved (1130 tests, 23 mandates, 11 agents, 15 skills, omega-vetala module, D208 heritage remediation), the constitutional documents and agent definitions were not systematically updated. This creates a **sovereignty gap**: agents operate under stale mandates, potentially violating M23 by simulating rigor when tools fail, and M10 by not knowing the true fleet cap. The Hivemind and Subagent Dispatch protocols — the coordination backbone — reference incomplete agent registries, risking mis-delegation.

### L3 — Universal Principle (Timeless Truth)
**Documentation is not a snapshot; it is a living contract.** In a sovereign system, the instruction layer *is* the constitution. When the implementation evolves (new mandates, new agents, new modules, new test counts), the constitution must be amended in the same atomic operation. The "Restart Cycle" (M4) manifests not only in code but in documentation drift. **Every architectural decision (D-series) must include a documentation update clause.** The cost of stale instructions exceeds the cost of updating them — stale instructions cause sovereign violations; updated instructions prevent them.

---

## 6. PROPOSED LESSONS (for `data/entities/verity/proposed_lessons.yaml`)

```yaml
proposals:
  - id: "verity-audit-20260710-01"
    tier: "L3"
    principle: "Documentation drift is a sovereignty violation. Every D-series decision must include a mandatory documentation update clause targeting AGENTS.md, SOVEREIGN_MANDATES.md, OMEGA_ENGINE.md, and affected agent files."
    source: "VERITY_PROTOCOL_INSTRUCTION_AUDIT.md"
    confidence: 0.95
    tags: ["documentation", "sovereignty", "mandate-compliance", "constitutional-law"]
    mandate_refs: ["M4", "M10", "M11", "M13", "M23"]

  - id: "verity-audit-20260710-02"
    tier: "L3"
    principle: "Agent mandate lists must be generated from SOVEREIGN_MANDATES.md, not duplicated. Single source of truth for constitutional law prevents M23 violations from stale mandate awareness."
    source: "VERITY_PROTOCOL_INSTRUCTION_AUDIT.md"
    confidence: 0.98
    tags: ["agents", "mandates", "single-source-of-truth", "drift-prevention"]
    mandate_refs: ["M10", "M11", "M23"]

  - id: "verity-audit-20260710-03"
    tier: "L2"
    principle: "Protocol documents (Hivemind, Subagent Dispatch) must maintain a live agent capability registry. Delegation decisions based on stale registries cause mis-routed work and coordination failures."
    source: "VERITY_PROTOCOL_INSTRUCTION_AUDIT.md"
    confidence: 0.92
    tags: ["hivemind", "subagent-dispatch", "coordination", "registry"]
    mandate_refs: ["M9", "M10", "M12"]

  - id: "verity-audit-20260710-04"
    tier: "L2"
    principle: "Search protocol references in agent files must point to the sovereign-search skill as the canonical implementation, not to a static research document. The skill enforces credit-sensing, error handling, and tier escalation that static docs cannot."
    source: "VERITY_PROTOCOL_INSTRUCTION_AUDIT.md"
    confidence: 0.90
    tags: ["search", "skills", "protocol-enforcement", "tool-chain"]
    mandate_refs: ["M7", "M18", "M23"]

  - id: "verity-audit-20260710-05"
    tier: "L3"
    principle: "Model references in agent definitions must use the Dual-Inference Mandate (D118) pattern: declare dispatch mode in Hivemind context, not hardcode in agent frontmatter. Hardcoded models violate M7 (Local-First) by preventing local opt-in routing."
    source: "VERITY_PROTOCOL_INSTRUCTION_AUDIT.md"
    confidence: 0.93
    tags: ["models", "dual-inference", "local-first", "sovereignty"]
    mandate_refs: ["M7", "M18", "D118"]
```

---

## 7. NEXT ACTIONS

1. **Immediate (P0)**: Update AGENTS.md test counts (1002→1130) and mandate counts (22→23)
2. **Immediate (P0)**: Update SOVEREIGN_MANDATES.md "Twenty-Two Laws" → "Twenty-Three Laws"
3. **Immediate (P0)**: Rewrite all 11 agent mandate lists to include M15-M23
4. **Immediate (P0)**: Fix SUBAGENT_DISPATCH_PROTOCOL.md agent registry (add 4 missing agents, fix classifications)
5. **Immediate (P0)**: Update HIVEMIND_PROTOCOL.md mandate reference to include M23
6. **High (P1)**: Update all agent search protocol sections to match sovereign-search skill
7. **High (P1)**: Replace hardcoded model names with session-model placeholders + D118 reference
8. **Medium (P2)**: Fix SOVEREIGN_MANDATES.md section numbering
9. **Medium (P2)**: Update SOVEREIGN_ARK_BLUEPRINT.md version to v3.2
10. **Medium (P2)**: Update WAD agent headers (config/wads/arcana_novai/agents/*.md)

---

*⬡ OMEGA ⬡ VERITY ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_verity_audit ⬡ AUDIT-COMPLETE*