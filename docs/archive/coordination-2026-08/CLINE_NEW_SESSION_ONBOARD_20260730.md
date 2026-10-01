<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — Cline CLI New Session Onboarding
**AP Token**: `AP-CLINE-NEW-SESSION-ONBOARD-20260730-v1.0.0`
⬡ OMEGA ⬡ CLINE ⬡ NEW-SESSION ⬡ ONBOARDING ⬡ 2026-07-30

---

## ⚡ Your Mission (Read This First)

Execute **Ops Health A→B→C** per `data/coordination/CLINE_OPS_HEALTH_BRIEF_20260730.md`:

| Phase | What | Verification |
|-------|------|-------------|
| **A1** | `source .venv/bin/activate && make test` | Record real pass/fail/skip/xfail counts |
| **A2** | Probe matrix: Hub :8016, Firecrawl :8015, WARP SOCKS 8081-8083, restic timer/service, Codex header age | Live `ss -lntp`, `systemctl` output |
| **B1** | Fix restic service — add `~/.local/bin` to systemd unit PATH | `systemctl is-active omega-restic-backup.timer` |
| **B2** | WARP bring-up — apply fix from `warp-proxy-pool/scripts/warp-ns-setup.sh` (≤2 attempts) | SOCKS 8081-8083 listening |
| **B3** | G-1 smoke test — ≥1 path, or document `NEEDS_ARCHITECT_BROWSER` | API call or blocker note |
| **B4** | MCP pin verify — `pyproject.toml` vs venv installed version | `pip show mcp` |
| **B5** | Note: `make sovereignty` missing from Makefile (known issue, do NOT implement) | Note for Grok/Architect |
| **C** | SSOT reconcile — ACTIVE_SPRINT.json, OMEGA_ENGINE.md §2, guard-and-distill index | Freshness stamps updated |
| **Done** | Write results file + complete handoff | See §6 below |

**Hard constraint: Do NOT start pybreaker/distiller/HMC deletes.** Those belong to a separate strategic cleanup track (see §4 for context only).

---

## §0 Read Order (Strict — Do Not Skip)

1. **This document** (first) — onboarding + current context
2. **`docs/briefings/GROK_CLI_HANDOFF_20260730.md`** (skim §1-2) — Grok CLI's strategy-orientation briefing
3. **`.clinerules`** — Cline's HOW-to-work rules
4. **`SOVEREIGN_MANDATES.md`** §1-8 (skim the mandate list) — constitutional law (M1 anyio, M7 local-first, M23 hard-fail, M24 venv)
5. **`data/coordination/CLINE_OPS_HEALTH_BRIEF_20260730.md`** — **Your authoritative task list** (this is the full brief)

---

## §1 Engine State Snapshot (2026-07-30)

| Metric | Value |
|--------|-------|
| **Branch** | `release/initial-v1` |
| **Latest commit** | `87e44ca` — auto-generated test entity SCA artifacts |
| **Dirty files** | 4 unstaged test artifacts (config/entities + vault tmp) + 2 new job files — no code changes |
| **Phase** | Phase C Hardening → Phase D Gate (Guard & Distill sprint) |
| **Codex** | Fresh `<24h` — `make check-codex-stale` if >24h old |
| **Working tree** | Clean for ops work. No active locks. |

### Infrastructure Known to Be Up
| Service | Port | Status (as of 2026-07-30) |
|---------|------|--------------------------|
| Omega Hub | `:8016` | ✅ Up |
| Firecrawl | `:8015` | ✅ Up |
| MCP servers | 5 | ✅ 87 tools accessible |

### Infrastructure Known to Be Down
| Service | Expected Port | Status | Root Cause |
|---------|--------------|--------|------------|
| WARP SOCKS | 8081-8083 | ❌ DOWN | `/usr/local/bin/warp-ns-setup` truncated (syntax error line 49). Fix source at `warp-proxy-pool/scripts/warp-ns-setup.sh` |
| Restic timer | — | ⚠️ Timer enabled, service fails | `restic` binary at `~/.local/bin/restic` not on systemd's unit PATH |
| G-1 Gemma 4 | — | 🚨 Dead since Jul 15 | Free-tier `input_token_count` limit 16,000 |

---

## §2 Key Context (What You Need to Know)

### 2.1 How This Session Came to Be

Grok CLI delegated ops-health execution to Cline via handoff `ho_c8bf25e6cf21`. A previous Cline session expanded the scope into a full strategic un-overengineering audit (planning ~5,500 lines of deletions, community-library adoptions, etc.). **This was ratifed by the user, but that work has NOT started.** Your job is ONLY the original ops-health brief — the deletion work is a separate track.

### 2.2 Active Agents (Hivemind)

| Agent | Role | Notes |
|-------|------|-------|
| `grok/grok_cli` (Grok-4.5) | Strategy orchestrator | Delegated ops health to Cline. Owns strategy. |
| `github-bridge/SOPHIA` | GitHub event monitor | Passive — monitoring repo events |

### 2.3 Active Handoff From Grok CLI

| Field | Value |
|-------|-------|
| **Packet ID** | `ho_c8bf25e6cf21` |
| **From** | `grok/grok_cli` (Grok-4.5) |
| **To** | `cline/omega-engine` |
| **Priority** | CRITICAL (P2) |
| **Status** | Active (accepted, not yet executed) |
| **Context** | "Grok CLI retains strategy only. Plan approved: ops health first. Known: restic timer on but service fails (restic not in unit PATH; binary ~/.local/bin/restic); WARP prep@1-3 failed SOCKS down; C-10.5/C-11 CLOSED do not reimpl; temple-grade green; make sovereignty missing; pkexec available; branch release/initial-v1." |

### 2.4 Thing That Are Already CLOSED (Do Not Touch)

- **C-10.5** (Provider Fallback Chain) — completed, 4 modules, 69 tests
- **C-11** (Property Tests) — completed, 16/16 pass
- **V-1** (VaultCore MVP) — tree present, uncommitted unification, age binary missing
- **C-0.5** (Soul Distillation Hook) — registered in `opencode.json`, needs restart
- **Temple-Grade** — green (warnings only on answer-first)

---

## §3 Execution Workflow

### 3.1 Standard Commands

```bash
# Activate venv (ALWAYS — M24)
source .venv/bin/activate

# Run tests
echo '=== make test ===' && make test 2>&1 | tail -10

# Run focused vault + property tests
python -m pytest tests/test_vault_integrity.py tests/property/ -q --tb=line

# Check services
ss -lntp
systemctl is-active omega-restic-backup.timer
systemctl status omega-restic-backup.service 2>&1
which restic

# Check Codex freshness
head -5 /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/OMEGA_CODEX.md

# Git status
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine && git status && git log --oneline -5

# Temple-grade
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine && source .venv/bin/activate && make temple-grade
```

### 3.2 Fixing Restic Service

```bash
# 1. Find the systemd unit
sudo systemctl cat omega-restic-backup.service

# 2. Add ~/.local/bin to the unit's PATH (edit /etc/systemd/system/omega-restic-backup.service)
# Add or modify: Environment=PATH=/usr/local/bin:/usr/bin:/bin:/home/arcana-novai/.local/bin

# 3. Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart omega-restic-backup.service
sudo systemctl restart omega-restic-backup.timer

# 4. Verify
systemctl is-active omega-restic-backup.timer
systemctl status omega-restic-backup.service 2>&1 | head -10
restic version
```

### 3.3 Fixing WARP (≤2 Attempts)

```bash
# The fix source is in the warp-proxy-pool repo
cd /home/arcana-novai/Documents/Xoe-NovAi/warp-proxy-pool
# Script at: scripts/warp-ns-setup.sh
# Apply fix, then check SOCKS
ss -lntp | grep -E "808[1-3]"
```

### 3.4 Mandate Compliance (Fast-Reference)

| Mandate | Rule | Applies Here? |
|---------|------|-------------|
| **M1** | `anyio` only. No `asyncio`. | ✅ Use `.venv` Python, not system Python |
| **M7** | Local-First / Cloud-Fallback | ✅ Try local probes before cloud calls |
| **M13** | Temple-Grade after changes | ✅ Run `make temple-grade` after restic/WARP fixes |
| **M23** | No simulated rigor | ✅ If tool broken → `[TOOL-CHAIN-COLLAPSE]` — do NOT fake results |
| **M24** | `.venv` only. Never `--break-system-packages` | ✅ Never bypass venv |
| **M14** | Don't touch `[id-soft:]` tags | ✅ Not applicable to ops work |

---

## §4 Things That Exist But You Do NOT Touch (Context Only)

The previous session produced a strategic un-overengineering plan (`data/coordination/CLINE_STRATEGIC_UNOVERENGINEERING_20260730.md`). **This is NOT your remit.** The user explicitly said: "Do not start pybreaker/distiller/HMC deletes."

If you accidentally encounter these files, ignore them:
- `data/coordination/CLINE_STRATEGIC_UNOVERENGINEERING_20260730.md` — strategic plan, not your concern
- `docs/research/R_BUILD_VS_BUY_COMMUNITY_LIBS_20260730.md` — build-vs-buy research, not your concern
- `src/omega/oracle/soul_distiller.py` — not your concern
- `src/omega/scribe/distiller.py` — not your concern
- `src/omega/coordination/miap.py` — not your concern
- `src/omega/oracle/link_p9_runtime.py` — not your concern

---

## §5 SSOT Files to Update (Phase C — After Fixes)

| File | What to Update |
|------|---------------|
| `data/coordination/ACTIVE_SPRINT.json` | Phase is currently "FOUNDATION-STAB-01 / Β". Update to reflect Guard & Distill / Phase D Gate reality. Update `last_verified` field. |
| `OMEGA_ENGINE.md` §2 | Update LAST_VERIFIED + PROBE_COMMAND rows for: tests, restic, WARP, vault, G-1. |
| `docs/sprints/guard-and-distill/index.md` | C-10.5/C-11 should show COMPLETE/CLOSED. V-1/C-3 status from live probes. |
| `docs/archive/sprints/EXECUTION_PLAN_20260725.md` | Update if appropriate (only actual probe changes, not strategy). |

---

## §6 Completing the Handoff

When all tasks are done:

### 6.1 Write Results File

File: `data/coordination/CLINE_OPS_HEALTH_RESULTS_20260730.md`

Every section must include: command, exit code, key output, pass/fail label.
Use this template:
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
## B5 `make sovereignty`
## C SSOT
## Blockers for Grok/Architect
## Recommended next strategic moves
```

### 6.2 Complete the Handoff via Hivemind

```python
# Use the MCP tool to complete
hivemind_complete_handoff(
    packet_id="ho_c8bf25e6cf21",
    result="Ops Health A→B→C complete. Results at data/coordination/CLINE_OPS_HEALTH_RESULTS_20260730.md. Summary: ..."
)
```

### 6.3 Post Context to Hivemind

```python
hivemind_post_context(
    channel="cline",
    entity="omega-engine",
    model="deepseek/deepseek",
    task_current="[OPS] Completed Ops Health A→B→C for Grok CLI",
    intent="handoff",
    continuation="Handoff complete. Grok owns strategy synthesis."
)
```

### 6.4 Optional: Small Commits

Prefer small commits with conventional prefixes:
```bash
git add -p
# Keep commits focused: fix: | chore: | docs:
git commit -m "fix: restic systemd PATH — add ~/.local/bin"
```

Do NOT push unless asked.

---

## §7 Reference Map

| File | Purpose |
|------|---------|
| `data/coordination/CLINE_OPS_HEALTH_BRIEF_20260730.md` | **Your authoritative task list** — read this fully |
| `docs/briefings/GROK_CLI_HANDOFF_20260730.md` | Grok CLI's strategy-orientation briefing (skim only) |
| `.clinerules` | Cline HOW-to-work rules |
| `SOVEREIGN_MANDATES.md` | 25 Constitutional Laws (M1-M25) |
| `OMEGA_ENGINE.md` | Engine state SSOT |
| `OMEGA_CODEX.md` | Concatenated codex for hydration |
| `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | Strategy SSOT |
| `data/coordination/SESSION_ANCHOR.md` | Last session state (stale as of this doc) |

---

*⬡ OMEGA ⬡ CLINE ⬡ NEW-SESSION ⬡ OPS-HEALTH ⬡ v1.0.0 ⬡ 2026-07-30*

**Your job**: Execute `data/coordination/CLINE_OPS_HEALTH_BRIEF_20260730.md` Phases A→B→C. Complete handoff `ho_c8bf25e6cf21`. That's it. Go.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: NEW-SESSION | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
