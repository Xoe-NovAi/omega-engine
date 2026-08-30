<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Cline Execution Brief — Ops Health Grunt Work
**AP Token**: `AP-CLINE-OPS-HEALTH-20260730-v1.0.0`  
**From**: `@grok_cli` (Grok Build CLI — strategy only)  
**To**: Cline CLI · **Model**: `deepseek/deepseek-v4-flash` (1M context)  
**Channel**: `cline` · **cwd**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine`  
**Priority**: CRITICAL (P0 ops)  
**Date**: 2026-07-30

---

## Role Split (NON-NEGOTIABLE)

| Actor | Owns |
|-------|------|
| **Grok CLI** | Strategy, prioritization, Architect decisions, synthesis, Phase D readiness judgment |
| **Cline CLI** | All token-heavy execution: tests, probes, service fixes, WARP bring-up, SSOT file updates, gate scripts, reports |

You are the **execution arm**. Do the work. Write results. Do **not** redesign strategy or re-open CLOSED research.

Read first (skim only):
1. This brief (authoritative task list)
2. `.clinerules` + `SOVEREIGN_MANDATES.md` (M1 AnyIO, M7, M13, M23, M24)
3. `docs/archive/sprints/EXECUTION_PLAN_20260725.md` §0 (better status than handoff)
4. Optional orientation: `docs/briefings/GROK_CLI_HANDOFF_20260730.md` (status cells **stale**)

**Truth hierarchy**: machine probes > git status > EXECUTION_PLAN §0 > Ark §4 > handoff prose > HMC.

---

## Already Known (do not re-research)

| Fact | Evidence |
|------|----------|
| Branch `release/initial-v1` clean at handoff start | `git status` |
| Omega Hub `:8016` up, Firecrawl `:8015` up | `ss -lntp` |
| Vault crypto tests 3/3 pass | `pytest tests/test_vault_integrity.py` |
| C-10.5 + C-11 **CLOSED** — do not re-implement | Ark + Execution Plan |
| Restic **timer enabled** but **service failed** | `restic` not on systemd PATH; binary at `~/.local/bin/restic` |
| WARP ns-setup script **identical** to fix source; prep@1-3 **failed**; no SOCKS 8081-8083 | systemctl + ss |
| `pkexec` available for elevation | Architect owner |
| `make temple-grade` green (warnings only on answer-first) | Grok ran 2026-07-30 |
| `make sovereignty` target **missing** | Makefile has no rule |
| `ACTIVE_SPRINT.json` still FOUNDATION-STAB Phase Β (stale) | file content |
| HMC Hub ~1928 lines | entropy; do not full-rewrite |

---

## Mission

Execute **Ops Health First** phases **A → B → C** (then residual D if time). Produce a single results file:

**`data/coordination/CLINE_OPS_HEALTH_RESULTS_20260730.md`**

Every section must include: command, exit code, key output, pass/fail label.

---

## Phase A — Baseline (token-heavy; you own fully)

### A1. Tests
```bash
source .venv/bin/activate
# If a prior `make test` is still running, wait for it OR kill only if hung >20min with no progress
make test
```
Record **real** pass/fail/skip/xfail/error counts. No vanity.

Also run focused:
```bash
pytest tests/test_vault_integrity.py tests/property/ -q --tb=line
```

### A2. Probe matrix
Fill a table with live results for:
- Hub 8016, Firecrawl 8015
- WARP SOCKS 8081-8083 (expect fail pre-B2)
- `systemctl is-active omega-restic-backup.timer`
- `systemctl status omega-restic-backup.service` (expect failed pre-B1)
- `which restic` / version
- `hivemind_get_awareness` + pending handoffs (via MCP if configured)
- Codex header age (`head -3 OMEGA_CODEX.md`)

### A3. Stop condition
If core honest test suite is red for reasons other than known quarantine, **fix blockers first** or document [TOOL-CHAIN-COLLAPSE] honestly (M23). Do not fake green.

---

## Phase B — Real ops fixes

### B1. Restic backup (C-3) — HIGHEST LEVERAGE 🔴
**Root cause**: systemd unit cannot find `restic` (user install at `/home/arcana-novai/.local/bin/restic`).

Do:
1. Read `/etc/systemd/system/omega-restic-backup.service` and `scripts/backup_restic.sh`
2. Fix PATH (prefer script-side absolute/hardened PATH **and/or** unit `Environment=PATH=...`)
3. Ensure `ProtectHome` / `ReadWritePaths` allow restic repo + cache (inspect `.env.backup` for repo path — **do not print secrets/passwords**)
4. `pkexec systemctl daemon-reload` if unit changed
5. Run oneshot: `pkexec systemctl start omega-restic-backup.service`
6. Accept: service exit 0 + new snapshot exists (`restic snapshots` with env loaded, no password in logs)

If `.env.backup` missing or repo uninitialized, initialize per script docs and report blockers clearly.

### B2. WARP pool (W-1) 🔴
```bash
bash scripts/fix_warp_ns_setup_and_restart.sh
```
Use `pkexec` where sudo is required. If script assumes interactive sudo, adapt safely.

Accept:
- prep@1-3 not failed
- node@1-3 active
- SOCKS on 8081-8083
- ideally 3 distinct exit IPs
- Python: `import warp_proxy_pool` healthy path if available

On failure: capture `journalctl -u 'warp-ns-prep@1' -n 80 --no-pager` and stop thrashing after 2 fix attempts; report root cause.

**Do not** treat W-1 as free-Gemma quota fix.

### B3. G-1 workhorse smokes (non-interactive first)
Run what you can without browser:
```bash
# Interim free / local
opencode run -m opencode/mimo-v2.5-free "Reply PONG" 2>&1 | tail -20
# Antigravity / Gemma only if already authed — do not hang on login UI
opencode run -m google/antigravity-gemini-3-flash "Reply PONG" 2>&1 | tail -30 || true
```
Document which paths work. If OAuth required, mark **NEEDS_ARCHITECT_BROWSER** — do not block other phases.

### B4. MCP pin hygiene (cheap)
Align mcp version story:
- `pyproject.toml` pin `mcp>=1.27,<2`
- venv installed version
- requirements*.txt if present  
Single source preferred: pyproject. Do not mass-upgrade ecosystem.

---

## Phase C — SSOT reconciliation (stop agent thrash)

Update **only** status surfaces to match probes (no strategy rewrites):

1. `data/coordination/ACTIVE_SPRINT.json` — current = Guard & Distill / Phase D Gate ops-health; not FOUNDATION-STAB Β as active
2. `data/coordination/SESSION_ANCHOR.md` — Grok strategist + Cline executor; probe summary; next actions
3. `OMEGA_ENGINE.md` §2 rows for: tests, restic, WARP, vault, G-1 (LAST_VERIFIED + PROBE_COMMAND)
4. `docs/sprints/guard-and-distill/index.md` — C-10.5/C-11 CLOSED; V-1/C-3 from live probes
5. Optional thin: `data/coordination/sprint_status.yaml` machine-readable sibling

**Do not** rewrite entire HMC hub (1928 lines). Optional: append one short Discussion note pointing to results file.

Hivemind (if MCP works):
```
hivemind_post_context(
  channel="cline", entity="omega-engine",
  model="deepseek/deepseek-v4-flash",
  task_current="Ops health A-B-C execution",
  intent="status",
  ...
)
```

---

## Phase D — Residual (only if A–C green / time remains)

1. `python scripts/verify_phase_d_gate.py` — honest FAIL list
2. V-1 residual: broader vault tests if exist; do not invent 8-account fabric
3. Confirm `.opencode/plugins/soul_distiller.js` present (runtime fire may need OpenCode restart — note only)

---

## Deliverables (mandatory)

| Path | Content |
|------|---------|
| `data/coordination/CLINE_OPS_HEALTH_RESULTS_20260730.md` | Full probe/fix report with real counts |
| Updated SSOTs listed in Phase C | Match probes |
| Git commits | Prefer small commits: `fix:`, `chore:`, `docs:` — do **not** push unless asked |
| Hivemind complete handoff | When done, complete packet with summary |

### Results file template
```markdown
# Cline Ops Health Results 2026-07-30
## Summary (answer first)
| Item | Status | Evidence |
## A1 Tests
## A2 Probes
## B1 Restic
## B2 WARP
## B3 G-1
## B4 MCP pin
## C SSOT
## D Gate (if run)
## Blockers for Grok/Architect
## Recommended next strategic moves
```

---

## Hard constraints

- **M1**: no new `asyncio` — use `anyio`
- **M23**: no simulated rigor; if tool broken, say so
- **M24**: use `.venv`; never `--break-system-packages`
- Do not print vault passwords, API keys, or `.env.backup` secrets
- Do not re-implement C-10.5 / C-11 / free-tier provider shopping
- Do not cap context to "fix" free Gemma
- Prefer `pkexec` for system changes; capture failures cleanly

---

## Success criteria

| Metric | Target |
|--------|--------|
| Honest test report | Real counts recorded |
| Restic | Timer active **and** successful oneshot (or clear blocker) |
| WARP | 8081-8083 up **or** journal-backed root cause after ≤2 attempts |
| G-1 | ≥1 smoke path documented (or NEEDS_ARCHITECT_BROWSER) |
| SSOT | ACTIVE_SPRINT + OMEGA_ENGINE + SESSION_ANCHOR match probes |
| Results file | Written and complete |

---

## When finished

1. Write results file  
2. `hivemind_complete_handoff` / post_context with continuation for `@grok_cli`  
3. Leave working tree in a reviewable state (commits OK; no force-push)  

**Grok will** synthesize strategy, decide Phase D readiness, and only touch high-leverage decisions.

---

*⬡ OMEGA ⬡ GROK_CLI → CLINE ⬡ OPS-HEALTH ⬡ 2026-07-30*
