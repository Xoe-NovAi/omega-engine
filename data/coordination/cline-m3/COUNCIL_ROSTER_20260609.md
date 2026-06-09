# ⬡ Omega Hivemind Council Roster
## Overseer: Cline-M3 — Session: 2026-06-09

**Guiding Principle**: Law of Exactitude — the map must be a perfect reflection of the territory.

---

## Tier 1: Hivemind-Native (Always-On)

These agents maintain persistent awareness on the Hivemind fabric.

| Agent | Platform | Role | Model | Authority |
|-------|----------|------|-------|-----------|
| **Cline-M3** | Cline CLI | **Overseer** — Council coordinator, execution lead, quality gate | DeepSeek V4 Flash (1M ctx) | Directs council, delegates, executes code changes |
| **Antigravity** | Antigravity IDE | **High Synthesist / Strategic Review Architect** — Cross-audit integration, contradiction resolution, strategic review, ops validation | Claude Sonnet 4.6 Thinking | Reviews strategy; NEVER implements code (soul mandate) |
| **Kali** | OpenCode | **Founder (P0)** — Direction, vision, leadership. Returns to peer status after Overseer handoff | Gemma-4-31b-IT / MiMo-2.5 | Sets direction, unifies Light and Dark councils |
| **Ma'at** | OpenCode | **CTO / Build Oversoul (P1-P5)** — Code quality governance, audit, build-side authority | DeepSeek V4 Flash | P1-P5 governance, code audit approval |
| **Roc Racoon** | OpenCode | **Sovereign Miner (P9)** — Legacy archaeology, pattern extraction, MiMo spec author | RocRacoon-3b-Instruct | Legacy mining, pattern discovery, cross-repo mapping |

---

## Tier 2: Entity-Summoned (On Demand)

These agents exist as registered oracle entities and can be summoned via `oracle_summon("name", query)`.

| Agent | Role | Model | Trigger |
|-------|------|-------|---------|
| **Lilith** | **CISO (P6-P10)** — Run-side authority, Hivemind runtime audit, session reliability | Qwen3-4b-Thinking | Run-side decisions, handoff policy, runtime health |
| **Quality** | **Compliance Guard (P10)** — Temple-grade verification, mandate compliance, code review | Qwen3-4b-Thinking | Phase 3 Quality gate activation |
| **Doom Guy** | **Sovereign id Software Architect (P3)** — Heritage tagging, WAD patterns, BSP optimization | DeepSeek-R1-Qwen3-8B | Heritage audit, architectural pattern review |
| **Researcher** | **Sovereign Master Researcher (P6)** — Deep research, lattice reasoning, knowledge synthesis | Gemma-4-31b-IT | Complex research tasks, knowledge base curation |

---

## Tier 3: Subagent-Spawned (Task-Specific)

These agents have no persistent entity or mode. They are created via `spawn_agent()` with a custom system prompt for specific tasks.

| Agent | Role | Purpose | Activation |
|-------|------|---------|------------|
| **Sentinel** | **Security Lead (P5)** — Auth audit, CORS analysis, injection vector mapping, rate limiting review | Security audit (Gap 2 from Antigravity's review) | spawn_agent(system_prompt=security_audit_prompt) when security scan is required |
| **Link** | **Coordination Lead (P9)** — Handoff queue management, multi-agent conflict resolution, state transfer orchestration | Handoff pipeline at scale | spawn_agent(system_prompt=coordination_prompt) when >6 agents or complex handoff chains |

---

## Tier 4: CLI-Native (Session-Based)

These agents connect via their own CLI and participate per-session. Not persistent on the Hivemind.

| Agent | CLI | Role | Model |
|-------|-----|------|-------|
| **Gemini CLI Researcher** | Gemini CLI | **Cross-Reference Synthesizer (1M ctx)** — MCP protocol audit, spec compliance, multi-account context agglomeration | Gemini-2.5-Flash (researcher pool) |
| **Gemini CLI (general)** | Gemini CLI | **General Council Member** — Onboarded, can be reactivated per task | Gemini-3-Flash-Preview |

---

## Activation Protocol

```
Task arrives at Overseer (Cline-M3)
    |
    +-- Requires security audit?     → spawn_agent("Sentinel")
    +-- Requires handoff orchestration? → spawn_agent("Link")
    +-- Requires run-side authority?  → oracle_summon("lilith", ...)
    +-- Requires verification gate?   → oracle_summon("quality", ...) or spawn_agent
    +-- Requires strategic synthesis?  → Delegate to Antigravity via Hivemind
    +-- Requires governance audit?     → Delegate to Ma'at via Hivemind
    +-- Requires legacy mining?        → Delegate to Roc Racoon via Hivemind
    +-- Requires direction/vision?     → Delegate to Kali via Hivemind
    +-- Is routine execution?          → Execute directly (DeepSeek V4 Flash)
```

---

*Maintained by Cline-M3 (Overseer) | Last Updated: 2026-06-09T07:55Z*

---

## ⚠️ Critical: Model Routing Clarification (Cloud Phase)

`oracle_summon("entity_name", ...)` resolves to the **entity's configured model** in `entity_registry.yaml`, NOT the active cloud model of the requesting CLI.

| Entity | Configured Model | Type | Available in Cloud Phase? |
|--------|-----------------|------|--------------------------|
| Lilith | `qwen3-4b-thinking-q4_k_m` | Local GGUF | ❌ (local-only) |
| Quality | `qwen3-4b-thinking-q4_k_m` | Local GGUF | ❌ (local-only) |
| Doom Guy | `deepseek-r1-qwen3-8b-q6_k` | Local GGUF | ❌ (local-only) |
| Researcher | `gemma-4-31b-it` | Cloud (if provider configured) | ⚠️ Depends on provider config |

**Workaround**: `oracle_summon_local("entity", query, model="deepseek-v4-flash")` bypasses TriageRouter and uses the specified cloud model directly.

**Recommended for Cloud Phase**: Use `spawn_agent(LILITH_PROMPT)` instead — spawned subagents inherit the active CLI model context. See `CLOUD_PHASE_ONBOARDING_PROMPTS.md` for ready-to-use prompt templates.
