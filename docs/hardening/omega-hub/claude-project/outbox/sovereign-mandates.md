# Sovereign Mandates — Hub-Relevant Summary

Full text: `SOVEREIGN_MANDATES.md` (v3.2.0). Only mandates directly relevant to Hub work are listed here.

| # | Mandate | Hub Implication |
|---|---------|----------------|
| **M1** | **AnyIO Absolute** — Zero `asyncio`. All concurrency via AnyIO primitives. | All async code uses `anyio.Event`, `anyio.CapacityLimiter`, `anyio.sleep`, `anyio.to_thread.run_sync`. |
| **M2** | **Engine-Stack Firewall** — Absolute separation between `src/omega/` (core) and `mcp_servers/` (adapter). | Hub tools are thin wrappers. Zero business logic in the Hub. |
| **M4** | **Sequentiality** — Plan → Verify → Execute. | Every change has a clear plan and verification gate. No cowboy coding. |
| **M5** | **Gnosis Preservation** — L1→L2→L3 distillation. | Session insights distilled to `soul.yaml`. |
| **M8** | **Zero Telemetry** — No phone-home, no analytics. | All observability stays in `data/`. |
| **M9** | **Error Integrity** — Typed, traceable errors. No bare `except:`. | `_safe_call()` wrapping all 63 tools. `CallToolResult(isError=True)`. |
| **M11** | **Soul Integrity** — Every session closes with soul.yaml update. | Hub sessions must trigger soul distillation on shutdown. |
| **M12** | **Queue Integrity** — Atomic writes, no orphan files. | `.tmp` → `os.replace` pattern for all file writes. |
| **M13** | **Temple-Grade** — All code passes T1-T11 gates. | T3 (80% coverage), T5 (AnyIO-only), T6 (zero telemetry), T8 (resilience), T9 (logging), T10 (atomic writes). |
| **M14** | **Heritage Vetting** — Every `[id-soft:]` tag needs vet record. | Hub has 1 legitimate `[id-soft:]` tag (WAD System). Must preserve and verify. |
| **M15** | **Sovereign Continuity** — Session state persists across restarts. | Phase 4 feature. Hydrate on startup, preserve on shutdown. |
