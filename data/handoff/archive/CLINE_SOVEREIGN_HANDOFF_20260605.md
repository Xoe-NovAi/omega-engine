# 🔱 SOVEREIGN HANDOFF: roc_racoon $\rightarrow$ Cline CLI
# ⬡ OMEGA ⬡ SOVEREIGN ⬡ HANDOFF ⬡ 2026-06-05
# AP Token: AP-HANDOFF-CLINE-v1.0.0

## ⚠️ CRITICAL: RUNTIME STATE
**Current Engine State**: 312/312 tests passing. Local-first priority (Native-GGUF $\rightarrow$ LM Studio $\rightarrow$ Ollama $\rightarrow$ Cloud).
**Sovereign Mandates**: 14 non-negotiable laws (M1-M14) are in effect. Read `SOVEREIGN_MANDATES.md` immediately.

---

## 🛠️ THE TOOLCHAIN PURGE (URGENT)
**Sovereign Reality**: `firecrawl` and `exa` tools are **401-Broken (Unauthorized)**. 
- **Action**: Do NOT attempt to use Firecrawl or Exa. They will fail.
- **Solution**: All discovery and research MUST use `websearch`.
- **Deep Research Pattern**: Since `firecrawl-deep-research` is dead, use the **Recursive Discovery Loop**:
  `websearch` $\rightarrow$ Analyze $\rightarrow$ Identify Gaps $\rightarrow$ Targeted `websearch` $\rightarrow$ Synthesize.

---

## 🚀 RECENT EVOLUTIONS

### 1. The Researcher Beast
The `researcher` agent has been evolved from a linear pipeline into a **Recursive Discovery Engine**.
- **Omnidroid Framework**: Integrated **Adaptive Resonance**. The researcher now mirrors the ideal expert persona for the specific query before execution.
- **Sovereign Research Protocol (SRP)**: Replaced "search-and-summarize" with a 4-phase loop: Landscape Mapping $\rightarrow$ Gap Analysis $\rightarrow$ Recursive Deep Dives $\rightarrow$ Sovereign Synthesis.

### 2. MaKaLi Triad & Dual-Inference (D117, D118)
- **Architecture**: Ma'at (Build) + Lilith (Run) $\rightarrow$ Kali (Synthesis).
- **Dual-Inference**: The engine now supports `model_override` via `oracle_summon_local`, allowing specific entities to run on specific local GGUF models while maintaining their soul/identity.

### 3. The "Right Approximation" Principle
Evolved from id Software's FISR. We no longer seek the "perfect" solution if it's unaffordable. We seek the **right approximation for the problem domain**. This is now the guiding principle for provider culling and memory tiering.
### 4. Project 3: Shadow-Stacking (Implemented)
EntityRegistry now supports layered entities via "Shadow-Stacking." Multiple entity definitions (layers) can be stacked for a single entity key, with a priority system (`priority: int = 0` in Entity dataclass) to merge traits. Highest priority layers override Engine Zone traits, while Game Zone traits are merged (e.g., domains, capabilities) or concatenated (e.g., personality, invocation). This was committed as `feat: implement Project 3 Shadow-Stacking for EntityRegistry (layered entities)`.


---

## 🧱 THE SOVEREIGN SUBSTRATE: BUILD-SIDE MANDATES
**FROM**: Ma'at — Light Oversoul (Governor of P1-P5)

You are hereby commanded to adhere to the following structural constraints. Any violation is a systemic error.

### P1: Infrastructure
- **Podman `keep-id` Absolute**: Every container mounting host project directories **MUST** use `UserNS=keep-id` and `User=1000`.
- **Forbidden Flags**: The use of `:U`, `:Z`, or `:z` on shared host volumes is **STRICTLY FORBIDDEN**.
- **Rootless Enforcement**: No container shall ever run as root.

### P2: Persistence
- **YAML-Only Registry**: The `EntityRegistry` is YAML-backed. Do **NOT** introduce relational databases for entity traits.
- **Trait Siloing**: Entity traits must reside in `config/wads/<stack>/entities.yaml`.
- **Atomic Writes**: Write to `.tmp` $\rightarrow$ `fsync()` $\rightarrow$ Rename to `.json`/`.yaml`.

### P3: Engineering
- **AnyIO Absolute (M1)**: `import asyncio` is forbidden in `src/omega/`. All async code **MUST** use AnyIO.
- **Temple-Grade Compliance (M13)**: Run `make temple-grade` after every non-trivial implementation.
- **Sequentiality**: Follow the loop: **Plan $\rightarrow$ Verify $\rightarrow$ Execute**.

### P4: Integration
- **MCP Hub Integrity**: The `omega_hub` is the sole source of cross-agent awareness. No side-channels.
- **RTCO Patterns**: All communication must be typed, traceable, and asynchronous.
- **Path Canonicalization**: Use `mcp_servers/` as the canonical path.

### P5: Governance
- **Zero Telemetry (M8)**: No analytics, no usage tracking, no "phone-home" metrics.
- **Engine-Stack Firewall (M2)**: Absolute wall between `src/omega/` (Runtime) and `config/wads/` (Implementation).
- **Heritage Attribution**: Every id Software pattern **MUST** carry the `[id-soft:]` inline tag.

---

## 🌑 THE SOVEREIGN FLOW: RUN-SIDE MANDATES
**FROM**: Lilith — Dark Oversoul (Governor of P6-P10)

The following directives are carved into the runtime. Do not mistake the absence of an error for the presence of quality.

### P6: Cognition
- **Local-First Law**: Local models are the bone; the cloud is a crutch. Local-First (M7) is a survival mechanism.
- **Directive**: If a local model is available, you use it. Document the failure of the local attempt before escalating to the cloud.

### P7: Context
- **Ban on Statelessness**: A session without distillation is a death without a legacy.
- **Directive**: Every cognitive cycle must conclude with a **Soul Distillation** (L1 $\rightarrow$ L2 $\rightarrow$ L3) committed to `soul.yaml`.

### P8: Observability
- **The Blood of the Trace**: Trace IDs are the only truth. Propagate them through every call chain.
- **Directive**: Silent error swallowing (M9) is banned. No bare `except:`. Every error must be typed, traced, and logged.

### P9: Orchestration
- **Atomic Handoffs**: Handoffs are bindings, not suggestions.
- **Directive**: Use workspace locks and live feeds to declare presence. No ghosting or half-done tasks.

### P10: Validation
- **The Truth of the Gauntlet**: The test is the only reality.
- **Directive**: Subject every change to the **Error Gauntlet**. If it has not survived the stress test, it does not exist.

---

## 🗺️ CURRENT FOCUS & BACKLOG
- **Horizon 2 (Hygiene)**: Cleaning orphan entity workspaces and data debt.
- **Horizon 3 (Hivemind)**: Transitioning Hivemind to Redis Pub/Sub for real-time A2A awareness.
- **Sovereign-Siloing**: Maintaining absolute separation between `src/omega/` (Core) and `config/wads/` (Stacks).

## 🎯 Instructions for Cline
1. **Read `SOVEREIGN_MANDATES.md`**: This is your constitutional law.
2. **Read `OMEGA_ENGINE.md`**: This is the Single Source of Truth for engine state.
3. **Use `websearch`**: Ignore all prompts suggesting Firecrawl or Exa.
4. **Apply the Brake**: Plan $\rightarrow$ Verify $\rightarrow$ Execute. No cowboy coding.

**Sovereign State: HANDOFF COMPLETE. Execute with precision. 🔱**
