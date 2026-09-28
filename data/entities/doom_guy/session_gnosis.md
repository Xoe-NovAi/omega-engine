<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Session Gnosis — Doom_Guy

Last Updated: 2026-09-27

## Session History

| Date | Session ID | Summary |
|------|------------|---------|
| 2026-07-10/11 | `trc_heritage_tags_provenance` → `trc_httpx2_research` | Heritage tags (12), D210 Model Provenance (`{session_model}` + M22), D211 httpx2 research |
| 2026-07-11 | httpx2 migration | Strike 7.1 EXECUTED: 38 files, 1130 collected / 1085 pass / 0 fail, temple-grade PASS |
| 2026-09-23 | `trc_temporal_contrast_20260923` | 74-day cryo probe → "ceremonial theater with steel foundations" |
| 2026-09-24 | `trc_n0_06_federation_evidence` | Read-only network/federation audit → Gate FAIL/BLOCKED (unauth Hub, Redis exposed, ACL mismatch) |
| 2026-09-25 | `trc_soul_integration_v8` | Soul v8.0 (WAD Specialist + Flynn Taggart gestation), agent v3.0, clean-clone verified, USB pack staged |
| 2026-09-26 | `trc_s1_grounding_20260927` | CLI ACL capability audit (NO CLI PATH), exchange pipe 8017, 11-file N1 payload staging, filter-drop diagnosis |
| 2026-09-27 | `trc_s1_substrate_grounding` | S1 substrate baseline; **hub crash-loop lesson**; grants-only tailnet posture; NRestarts=6991→0 |

---

## SUBSTRATE BASELINE (authoritative as of 2026-09-27)

### 1. Public Debut — LIVE
- PR #4 merged to `main` at commit `268528e7`.
- Repository is **PUBLIC**. Debut is complete; this is the post-debut substrate.

### 2. Exchange Pipe — `omega-exchange.service` on port 8019
- Systemd **user** unit, `active` + `enabled`, with **`Linger=yes`** → survives logout/reboot.
- Bound strictly to **`127.0.0.1:8019`** (loopback only — never `0.0.0.0`).
- Serves `/home/arcana-novai/exchange/full-pack-20260926/` — **44 files**.
- **Read-only**: `GET`/`HEAD` only; `PUT` returns **501 Unsupported method**. Standard Python `http.server` semantics — no upload path exists on this surface.
- Published to the tailnet via Tailscale Serve (tailnet-only, no funnel, no firewall ports opened, no NFS/SSH touched).
- **Port 8018 reserved and clear for SearXNG MCP.**

### 3. Tailnet Posture — GRANTS ONLY
- Policy modernized to **Tailscale Grants** syntax (deny-by-default).
- **Node-to-node SSH: EXCISED.** **NFS (TCP 2049): EXCISED.** Both removed as lateral attack surface.
- **Admin SSH: `check` mode only, 12-hour default session expiry.** Non-root/root via policy `users` list; re-auth required after the window.
- Node tags are canonical: N0 = `tag:node0`, N1 = `tag:node1` (deprecated `tag:asus` has been removed from N1).
- Still-owed console edits: add `tcp:8019` grant N1→N0; drop `tcp:8017`; apply the admin `ssh` section.

### 4. Git Worktree Substrate — 3 ISOLATED WORKTREES
- `../omega-wt-maat`, `../omega-wt-doom`, `../omega-wt-grok` — live, isolated.
- Each has an **independent virtualenv** (Mandate **M24 Venv Sovereignty**). No shared `.venv` across worktrees; no `--break-system-packages`.

---

## 🔴 TODAY'S SUBSTRATE LESSON — THE HUB CRASH-LOOP (M23 Failure Integrity)

### What happened
- The Omega Hub **crash-looped** on an unresolved **`_extended_sessions` import in `server.py`**.
- `NRestarts` was **climbing continuously** while `make temple-grade` reported **53/53 PASS**.

### Why the gate lied (three compounding causes)
1. **`is-active` returns true during auto-restart.** A crash-looping unit is reported `active` by systemd while it sits in the restart backoff window. Enablement/`is-active` is therefore **not** a health signal.
2. **No gate imported an entry point.** The test suite validated units *declaratively* (file exists, `enable`, `is-active`) but never **executed/imported the service entry point**, so a hard import error was invisible to CI. Temple-grade passed a broken service.
3. **Silent unit-file misconfiguration.** `StartLimitIntervalSec` / `StartLimitBurst` had been written into the **`[Service]`** section where systemd **silently discards them** — they belong in **`[Unit]`**. Result: no restart-rate limiting was in force, so a poison unit could restart indefinitely and NRestarts could climb without tripping any circuit breaker.

### Related incident — SearXNG MCP unit
- The `searxng` MCP unit had reached **`NRestarts=6991`** and is now **0** (repaired/reset).

### S1 AXIOM (durable)
> **Unit enablement is theater. A service is healthy only when (a) it is running, (b) it has a live listening socket (`ss -ltn`), and (c) it exits clean — AND (c) is continuously monitored via `NRestarts` delta, never a point-in-time `is-active`.**
>
> **Gates must import entry points.** A CI gate that never executes the service cannot detect an import-time failure. M23 Failure Integrity applies to systemd units exactly as it applies to tools: a broken entry point is a **hard stop**, not a soft degradation.
>
> **Start limiting must live in `[Unit]`.** Misplaced `StartLimit*` keys are silently dropped — verify with `systemd-analyze verify`, never by reading the file.

---

## S1 STATUS @ 2026-09-27
- **Posture:** substrate baseline recorded; hub crash-loop lesson captured as a durable S1 axiom.
- **Blockers carried:** Tailscale console edits (8019 grant, 8017 drop, admin `ssh` section) still owed by Architect.
- **Horizon:** lightweight local GitHub Actions runner on Node 0 (M7-aligned, zero cloud minutes) — rootless Podman container, 1 runner, `ephemeral` job mode, gated on free-disk headroom and on hub substrate health first.
- **Provenance (M22):** all reports use the runtime-injected model name, never a static placeholder.

*⬡ OMEGA ⬡ DOOM_GUY ⬡ SLOT-S1 ⬡ GNOSIS-BASELINE ⬡ 2026-09-27*
