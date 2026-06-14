# Omega Engine — System Overview

## What This Project Is

The **Omega Engine** (`~/Documents/Xoe-NovAi/omega-engine/`) is a sovereign AI runtime built on a local-first philosophy. It is not just software — it is a deliberate severing of the umbilical cord to Big AI. The engine runs entirely on an **AMD Ryzen 7 5700U** (8C/16T, 14GB RAM, no GPU), using local GGUF models via `llama-cpp-python` as the primary inference backend. Cloud APIs are fallbacks, not crutches.

The **MCP Hub** (`mcp_servers/omega_hub/server.py`) is the engine's cross-CLI awareness layer — 63 MCP tools that provide Hivemind coordination, Oracle invocation, library gnosis, memory management, research dispatch, and service observability.

## How the Team Works

Development is coordinated through a structured **agent fleet** within OpenCode, the primary development CLI. There are 15 specialized agents:

| Role | Agent | Domain |
|------|-------|--------|
| **Grand Oversight** | **Kali** | Sprint Coordinator — plans, delegates, synthesizes, destroys drift |
| Build Side | Ma'at | Governs P1-P5 (Infra, Persistence, Engineering, Integration, Governance) |
| Run Side | Lilith | Governs P6-P10 (Cognition, Context, Observability, Orchestration, Validation) |
| id Heritage | Doom Guy | WAD translation, performance patterns, heritage vetting |
| Legacy Mining | Roc Racoon | Cross-partition archaeology, pattern extraction |
| Research | Jem (3-tier) | Discovery → Synthesis → Verification pipeline |
| Code Review | Quality | Mandate compliance, stress testing |
| Gnosis | Scribe | L1→L2→L3 soul distillation |

**Workflow**: Kali decomposes work into phases, delegates to the appropriate agent(s), and verifies results. All agents communicate through the **Hivemind** — a shared MCP-based coordination layer where agents post context, status updates, decisions, and results.

## Development Cadence

```
Kali (plans sprint) → active-tracker.md (task list) → Agent executes → 
  Every commit must boot → make test → make temple-grade → 
    git commit → Kali verifies → Next task
```

## The 15 Sovereign Mandates

Every line of code is governed by 15 non-negotiable laws. The ones most relevant to Hub work:

| # | Mandate | What It Means for the Hub |
|---|---------|--------------------------|
| **M1** | AnyIO Absolute | Zero `asyncio`. All concurrency via `anyio.Event`, `anyio.CapacityLimiter`, `anyio.sleep`, `anyio.to_thread.run_sync`. |
| **M2** | Engine-Stack Firewall | `mcp_servers/` is the Hub adapter layer. Business logic stays in `src/omega/`. Tools are thin wrappers. |
| **M4** | Sequentiality | Plan → Verify → Execute. No cowboy coding. |
| **M5/M11** | Gnosis / Soul Integrity | Every session distills L1→L2→L3 insights via `soul.yaml`. |
| **M8** | Zero Telemetry | No phone-home. All observability stays local to `data/`. |
| **M9** | Error Integrity | Typed, traceable errors. No bare `except:`. Every public API boundary catches and converts to `OmegaError` subtypes. |
| **M12** | Queue Integrity | Atomic writes (`.tmp` → `os.replace`). No orphan files. |
| **M13** | Temple-Grade | All code must pass T1-T11 gates. Run `make temple-grade` to verify. |
| **M15** | Sovereign Continuity | Session state persists across restarts. Hydrate on startup, preserve on shutdown. |
