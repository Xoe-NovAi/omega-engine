<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Ma'at — Workspace Lock for Probe Report Actions

**Owner**: maat (Build Oversoul)
**Domain**: probe-report-actions-20260827
**Acquired**: 2026-08-27 22:25 UTC (epoch 1787869555)
**TTL**: 7200s (2 hours)
**Sprint**: PUBLIC-DEBUT-01
**Dispatch**: kali (Sprint Coordinator) → maat

## Mission

Implement 5 immediate actions from Grokster's provider reliability probe report
(`data/coordination/PROVIDER_RELIABILITY_REPORT_20260827.md`):

1. **P0** — Fix API key resolution (3-key rotation, pre-check)
2. **P0** — Add quality checks (valid JSON, completion present, content length)
3. **P1** — Rolling percentiles (P50/P90/P99, last 50 probes per model)
4. **P1** — Schedule probes at quota windows (00/06/12/18 UTC)
5. **P2** — Build alerting webhook (state change → Hivemind)

## Scope (Files)

### WRITE
- `scripts/probe_free_models.sh` — rewrite (Actions 1+2)
- `scripts/probe_percentiles.py` — new (Action 3)
- `scripts/alert_state_change.sh` — new (Action 5)
- `scripts/crontab.txt` — new (Action 4)
- `data/metrics/model_percentiles.jsonl` — initial run (Action 3)
- `data/metrics/model_state.json` — new state file (Action 5)
- `data/metrics/probe_quality_summary.json` — new (Action 2)

### READ-ONLY
- `data/metrics/free_model_probes.jsonl` (append)
- `data/coordination/ACTIVE_SPRINT.json` (no change)

## Non-Scope (do not touch)

- Workspace `debut-track1-build` (different track, held by another process)
- Provider config (`config/providers.yaml`) — out of mission
- AGENTS.md, .opencode/rules/ — out of mission

## Authority

- Architect GO (via kali) — full authorization for 5 actions
- Mandate M23 — no soft-failures, broken tools → STOP, report
- Mandate M8 — zero telemetry (no external calls except model APIs)
- Mandate M27 — 6-step mandatory flow; track all in `TASK_REGISTRY.json` (optional for batch ops)

## Parallel Work

- debut-track1-build (Ma'at P3, locked) — different files, no conflict
- researcher (vault research) — Hivemind aware, no overlap
- kali (Sprint Coordinator) — oversight, will read final Hivemind post

## Reference

- `data/coordination/PROVIDER_RELIABILITY_REPORT_20260827.md` — report
- `data/metrics/free_model_probes.jsonl` — 345 entries, probe data
- `data/coordination/MINIMAX_M3_LONG_WRITE_CHAMPION_20260827.md` — M3 model card
- `data/coordination/SESSION_CONTINUITY_PROTOCOL_20260827.md` — session mgmt
