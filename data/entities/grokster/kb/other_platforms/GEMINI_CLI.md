<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Gemini CLI — Dormant / Transitioning

**KB Entry**: grokster/platforms/other/GEMINI_CLI
**last_verified**: 2026-08-26 · **rot_class**: fast
**Sources**: `docs/research/GEMINI_CLI_QUICK_REF.md` (STALE-flagged), `docs/research/R_GAP_CLOSURE_SWEEP_20260826.md`, provider fabric docs

---

## Status

Repo reference is STALE-flagged (pre-June 2026). Classic Gemini CLI **replaced by Antigravity CLI for unpaid tiers since Jun 18 2026** — guidance premised on classic CLI needs this banner.

## Durable Nuggets Only

- Config hierarchy: `/etc/gemini-cli/system-defaults.json` → `~/.gemini/settings.json` → `.gemini/settings.json` (+ overrides); project context via GEMINI.md/CONTEXT.md.
- Key settings: `context.fileName`, `context.includeDirectories`, `model.maxSessionTurns`, `general.plan.enabled` (read-only plan mode), `general.checkpointing.enabled` (session recovery).
- Flags: `--yolo`/`--approval-mode=yolo` (auto-approve all — dangerous), `--headless`.
- Memory flow: auto-distillation back into GEMINI.md.
- **AGENTS.md support RESOLVED (2026-08-26 sweep)**: default = GEMINI.md only; AGENTS.md opt-in via `context.fileName` array.

## Verdict

Keep as shallow reference; no active mileage. Research targets: settings.json current schema, MCP support, quota model.

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ KB v2.1.3 ⬡ 2026-08-26*