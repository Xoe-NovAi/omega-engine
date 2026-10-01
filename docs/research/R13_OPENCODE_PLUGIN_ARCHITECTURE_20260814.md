<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Gap R13: OpenCode Plugin Architecture

**AP Token:** `AP-RESEARCH-PHASE1-4-20260813-v3.2.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ 2026-08-14
**Dependent task:** PLUGIN-1..8 (Fleet Health Dashboard plugin)
**Status:** ✅ RESOLVED

## Summary
OpenCode plugins are TypeScript modules that export an async `Plugin` factory. They are loaded via the `plugin` array in `opencode.json` (npm name, `file://` path, or directory name) and run inside the Bun runtime. They can register lifecycle **hooks** (e.g. `session.start`, `session.end`, `message.updated`, `session.error`), custom tools, and commands. Model attribution is available via `modelID` in event properties. This unblocks PHASE-2 (Fleet Health Dashboard plugin build).

## Authoritative Sources
| Source | URL / Path | Date | Relevance |
|--------|-----------|------|-----------|
| OpenCode Plugins docs | https://opencode.ai/docs/plugins/ | 2026 | Canonical plugin API, load order, npm install via Bun |
| Local: `.opencode/plugins/awareness.ts` | repo | 2026 | Real plugin using `@opencode-ai/plugin` types + hooks |
| Local: `.opencode/plugins/error-capture.ts` | repo | 2026 | Same pattern; `session.error` handler |
| Local: `.opencode/opencode.json` | repo | 2026 | `plugin` array with `file://` entries |
| Local: `opencode.json` (project) | repo | 2026 | `plugin` array with npm + dir entries |

## Findings
1. **Plugin signature** (verified locally + docs):
   ```ts
   import type { Plugin } from "@opencode-ai/plugin";
   export const FleetHealthPlugin: Plugin = async ({ project, client, $, directory, worktree }) => {
     return {
       hooks: {
         "session.end": async (event) => { /* ... */ },
       },
     };
   };
   ```
2. **Loading**: `opencode.json` → `"plugin": ["@scope/name@latest", "file:///abs/path/plugin.ts", "dir-name"]`. npm plugins are auto-installed by Bun at startup and cached in `~/.cache/opencode/node_modules`. Load order: global → project → global plugin dir → project plugin dir.
3. **Local grounding**: Both `awareness.ts` and `error-capture.ts` use `@opencode-ai/plugin` types, register hooks, and run under Bun (no Node-only APIs). `error-capture.ts` already handles `session.error` — the exact event the Nemotron streaming-fix needs.
4. **Model detection**: event properties carry `modelID` (e.g. `nemotron-3-ultra`), enabling per-model attribution in the dashboard.
5. **No retry re-impl**: OpenCode v1.18.14 has native streaming retry (confirmed in R8 research), so PLUGIN-1..8 scope is observability + fallback + detection only (R31 scope reduction).

## Recommendation
Build the Fleet Health Dashboard as `.opencode/plugins/fleet-health.ts` exporting a `Plugin` that registers a `session.end` hook. The hook queries `data/observability/metrics.db` (MetricsDB), computes per-entity health, and writes:
- `data/coordination/metrics.json` (structured snapshot), and
- a Prometheus textfile `data/observability/fleet_health.prom` (see R18) for node-exporter scraping.
Load it via the `plugin` array using the `file://` path. Use `modelID` from event props for model attribution. Keep it Bun-compatible (no Node-only imports). This satisfies PLUGIN-1..8 without re-implementing retry.

## Confidence
**HIGH** — conclusions drawn from the repo's own plugin source plus the official OpenCode plugin documentation.

## Remaining Unknowns
- Exact `session.end` payload shape (verify against `@opencode-ai/plugin` types at implementation time).
- Whether the dashboard needs a live HTTP endpoint or file-based polling is sufficient (file-based recommended for M7 local-first).
