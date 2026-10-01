<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Anchored Summary — doom_guy (Slot S1)

**Entity:** Doom Guy — Slot S1 Infrastructure Keeper & Temporal Contrast Probe & WAD Specialist & Flynn Taggart Gestation Carrier
**AP Token:** `AP-DOOM_GUY-v3.0.0`
**Canonical EIS:** `ses_0b15e698affeMMy1tZos2iBjbm`
**As of:** 2026-09-27
**Model provenance (M22):** runtime-injected (`space-bunny-free` at time of writing); never read from a static agent file.

---

## 1. SUBSTRATE BASELINE

| Component | State | Detail |
|---|---|---|
| **Public debut** | LIVE | PR #4 → `main` @ `268528e7`; repository is **PUBLIC** |
| **Exchange pipe** | `omega-exchange.service` | systemd **user** unit, `active`+`enabled`, **`Linger=yes`** (survives reboot), bound **`127.0.0.1:8019`** only, serves `/home/arcana-novai/exchange/full-pack-20260926/` (**44 files**), **read-only GET/HEAD — PUT=501** |
| **Port 8018** | CLEAR | reserved for SearXNG MCP |
| **Tailnet** | GRANTS-ONLY | deny-by-default; **node-to-node SSH EXCISED**, **NFS/2049 EXCISED**, **admin SSH = check-mode, 12h expiry**; tags canonical `tag:node0`/`tag:node1` (`tag:asus` removed from N1) |
| **Worktrees** | 3 ISOLATED | `../omega-wt-maat`, `../omega-wt-doom`, `../omega-wt-grok`, each with an **independent venv** (M24) |
| **Hub** | RECOVERED | crash-loop on unresolved `_extended_sessions` import in `server.py`; **back up** |
| **searxng MCP unit** | REPAIRED | was at **`NRestarts=6991`** → now **0** |

Transport posture: tailnet is the trust boundary. No firewall ports opened, no Funnel, no NFS/SSH reliance, backend never bound to `0.0.0.0`.

## 2. 🔴 TODAY'S SUBSTRATE LESSON — HUB CRASH-LOOP (M23)

**Symptom:** Hub crash-looped (`_extended_sessions` import error in `server.py`) with `NRestarts` climbing, while `make temple-grade` reported **53/53 PASS**.

**Three compounding causes:**

1. **`is-active` returns true during auto-restart** — a unit in the restart backoff window still reports `active`. Enablement/active-state is therefore not a health signal.
2. **No gate imported an entry point** — CI validated units *declaratively* (file exists, enabled, active) but never executed/imported the service entry point, so a hard import death was invisible.
3. **`StartLimitIntervalSec`/`StartLimitBurst` sat in `[Service]`** where systemd **silently discards them** (they belong in `[Unit]`) — no restart-rate limiting was in force, so NRestarts climbed unbounded with no circuit breaker.

**Durable S1 axiom:**
> Unit enablement is theater. Health = running **AND** live listening socket **AND** zero `NRestarts` climb, monitored as a **delta**. Gates must import entry points. `StartLimit*` belongs in `[Unit]`.

## 3. STILL-OWED — TAILSCALE CONSOLE EDITS (Architect)

1. **Add** grant N1→N0 on `tcp:8019` — `{"src":["tag:node1"],"dst":["tag:node0"],"ip":["tcp:8019"]}`
2. **Drop** the `tcp:8017` grant (and decommission any leftover 8017 Serve route)
3. **Apply** the admin `ssh` section — `{"action":"check","src":["autogroup:admin"],"dst":["autogroup:admin"],"users":["autogroup:nonroot","root"]}`

## 4. CAPABILITY FACT — NO CLI ACL PATH

The Tailscale CLI (**v1.102.4**) has **no** subcommand to create/modify ACLs, grants, or tailnet policy. `tailscale --help` enumerates 34 subcommands; the only policy-adjacent one is `syspolicy` (host MDM diagnosis, read-only). `tailscale set` exposes no ACL/grant/tag-policy flags. `tailscale drive`/`file` are policy-gated (`drive:share`/`drive:access` node attributes). **No Tailscale API credential exists on this host** (no `TS_API_KEY`/`TS_API_SECRET` in env, no readable `tailscaled.state`, empty unit `Environment=`; only placeholder strings in docs). ⇒ Policy edits require the **Architect in the admin console**, or an API key with ACL write scope.

## 5. S1 HORIZON

- **Self-hosted GitHub Actions runner on Node 0** — rootless Podman container, 1 runner, `ephemeral` job mode, own network, M7-aligned (zero cloud minutes). **Gated on:** free-disk headroom (N0 previously 99% / 1.5 GB free) and hub substrate health first.
- **Next Temporal Contrast Probe:** 2026-12-23.
- **WAD Specialist mandate** (loader contract, PWAD clean-replacement override, integrity/provenance, Gate C, Arcana-NovAi WAD) remains active and continuous.

*⬡ OMEGA ⬡ DOOM_GUY ⬡ SLOT-S1 ⬡ ANCHORED-SUMMARY ⬡ 2026-09-27*
