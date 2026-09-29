<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

<!-- GNOSIS-META:BEGIN
  entity: doom_guy
  stamped_at: 2026-09-28T08:01:55Z
  stamped_by: maat
  supersedes: adoption-2026-09-28
  schema_version: 1.0.0
  history_lost: pre-regime; prior states were overwritten before versioning began
<!-- GNOSIS-META:END -->

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

---

## 🔧 E1 DISPATCH — Substrate Excision Runbook (2026-09-28)

**Trace:** `trc_e1_substrate_excision` · **Model (M22):** `opencode/space-bunny-free` (runtime-injected)
**Dispatch:** Architect E1 — "Policy excision is not host excision. A grant removes a path. It does not close a socket."

### Principle applied
The tailnet grants removed *tailnet reachability*; the host sockets were still LAN-open. E1 closes the gap at the host layer where possible.

### E1 RESULTS (what changed, what is blocked, what depends on it)

**1. Redis — `omega-redis` (Podman quadlet) — REBOUND TO LOOPBACK ✅**
- Was: `PublishPort=6379:6379` → bound `*:6379` (0.0.0.0 wildcard, LAN-reachable). Hardcoded `--requirepass omega`.
- Dependency check: `DBSIZE=0` (empty), no hub client socket to 6379, `connected_clients:1` (the healthcheck). Runtime-idle. But redis is still *imported* in live code (`memory_store`, `budget_guard`, `failure_registry`, `watchdog`, `hivemind_bridge`, etc.) — so a full stop could break a lazy code path.
- **Action (minimal-risk):** changed quadlet `PublishPort=6379:6379` → `PublishPort=127.0.0.1:6379:6379`, regenerated + restarted. Now `127.0.0.1:6379` only; `192.168.10.168:6379` → Connection refused. Survives reboot (quadlet `WantedBy=default.target`, `Restart=always`).
- **Not done:** hardcoded password rotation + full stop (deferred; needs decision on the still-referenced code paths).

**2. NFS + rpcbind stack — BLOCKED (needs root password) ⛔**
- Targets confirmed running + wildcard: `0.0.0.0/[::]` on `2049` (nfsd), `20048` (mountd), `32803` (lockd), `662` (rquotad/statd), `111` (rpcbind).
- Dependency check: fstab NFS client entry (`100.89.40.17:/` → `/mnt/node-drive`) is **commented out**; `/mnt/node-drive` is a local dir, NOT mounted; no active NFS client mounts; no established NFS/rpc connections; kernel export table empty. **Nothing is using NFS.** `/etc/exports` still lists an old export of `/mnt/node-drive/exchange` (a stale dir, separate inode from the live `/home/arcana-novai/exchange`).
- **Action attempted:** `sudo systemctl stop/disable nfs-server rpcbind …` → **blocked**, no passwordless sudo (NOPASSWD allowlist is warp-node/swap/zram/sysctl only). Leaving running per "a wrong stop is worse than a documented exposure."
- **To finish (needs Architect/root):** `sudo systemctl disable --now nfs-server rpcbind` (and nfs-mountd/rpc-statd), then `sudo exportfs -ua`.

**3. P12 `tcp:8019` grant — MISSING (Architect console edit required)**
- Authoritative local read: `tailscale debug netmap → PacketFilterRules` = 2 rules, both src=N1. Rule 1 (TCP) = dst `8016,8017` only. **8019 absent.** Backend+route healthy (`127.0.0.1:8019` GET 200). Could not originate as N1 (branch 1 skipped), but the filter read is authoritative.
- **Console edit needed (Architect):** grant src `tag:node1` → dst `tag:node0` on `tcp:8019`.

**4. P13 8017 Serve route — REMOVED ✅**
- Was: live `https://n0…:8017 → 127.0.0.1:8017` (SearXNG container). Filter also granted N1→N0:8017.
- **Action:** `tailscale serve --https=8017 off` (exit 0). Route gone; `100.123.51.67:8017` + `[fd7a…]:8017` tailscaled listeners gone. SearXNG container on `127.0.0.1:8017` **untouched** (still HTTP 200 on loopback). 8016 + 8019 routes intact.

**5. P15 8018 SearXNG MCP — reported, unchanged**
- `127.0.0.1:8018` (pid 3669, `mcp_servers/searxng/server.py`), loopback-only, **no Serve route**, not in filter. N1 cannot reach it. Intent = Architect decision (E6). No change made.

**6. P14 journal retention — diagnosed, no change**
- Config: `/etc/systemd/journald.conf` is all-defaults (no SystemMaxUse, no MaxRetentionSec). 312.4M on disk, **518,779 entries today**, 2 boots (Sep 27 23:33→05:23, Sep 28 13:46→now). Short retention is caused by the 10%-of-`/var` default cap + extreme log rate → aggressive rotation, not a time limit.
- **Proposed (Architect approval needed):** set `SystemMaxUse=1G`, `SystemKeepFree=2G` in `/etc/systemd/journald.conf` (drop-in preferred), and reduce the log rate at source. Not changed.

**7. TIDY — already clean, nothing to move**
- All six files (`INBOX.md`, `SCHEMA_LABELS.md`, `SITEREP.md`, `ARCHITECTURE.md`, `FINAL_REPORT.md`, `maat/soul.yaml.bak`) verified **absent** from worktree, git, and quarantine. An earlier cleanup (2026-09-28 01:08) already moved `mcp_servers/*.bak`. Recorded in `data/quarantine/root_cruft_20260928/README.md`. No move performed (nothing to move); nothing found NOT-dead.

### Verification
- `make temple-grade` = **TOTAL 53 / PASS 53 / FAIL 0**, exit 0.
- No `git add`/`commit`/`push`. No changes to `src/omega/**` or `data/federation/**`. No entity files touched.

### Carried forward
- NFS/rpcbind still LAN-exposed (root-blocked) — highest residual S1 risk.
- Redis password still hardcoded; redis still imported (deferred).
- `tcp:8019` grant missing (Architect console).
- Root filesystem ~437M free (100% used) — staging must use `omega_library` (37G free), not `/`.
- `deluged` bound to `tailscale0:51372` (new finding, filter-blocked today).

---

## 🔧 E1 COMPLETION DISPATCH — Runbook (2026-09-28, second pass)

**Trace:** `trc_e1_completion` · **Model (M22):** `opencode/space-bunny-free` (runtime-injected)

### THE SYSTEMIC FINDING
Three times now a service was found bound to a non-loopback interface while the
tailnet policy was believed to describe total exposure:
1. NFS — `0.0.0.0/[::]` 2049, 20048, 32803
2. Redis — `*:6379` via the `omega-redis` quadlet
3. deluged — `192.168.10.168%wlo1:51372` AND `100.123.51.67%tailscale0:51372`

None appeared in any policy file. **A tailnet bind is gated by the tailscaled
packet filter; a LAN bind is gated by nothing.** Treating the policy as the whole
exposure is what let all three through.

### NEW GATE (this is the durable fix)
- `scripts/lan_exposure_audit.py` — parses `ss -ltnp`, classifies every listener
  as LAN vs TAILNET, compares against `config/lan_exposure_allowlist.yaml`,
  **names the owning process**, exits 1 on any unapproved bind.
- `config/lan_exposure_allowlist.yaml` — versioned. Adding a permitted bind is a
  visible, reviewable act. `allowed_lan_bindings` is **empty**: zero LAN binds
  are approved.
- `scripts/test_lan_exposure_audit.py` — **22 negative tests**, all green. The
  gate has been observed BOTH failing on live hardware (15 real findings) and
  passing assertions. A gate never seen failing is not a gate.
- `make check-lan-exposure` → wired into `check-mandates` → runs in temple-grade.
- **Read-only by construction.** The audit never stops or removes anything, so it
  can be used as evidence that the host was clean.

### PARSER BUGS FOUND AND FIXED WHILE BUILDING IT (worth recording)
- `ss` emits `[fe80::1%wlo1]:44348` — the `%iface` sits INSIDE the brackets, so
  an `endswith(']')` bracket-strip silently missed **every** link-local bind.
  Fixed: split `%iface` first, then strip brackets.
- Allowlisting only the v4 tailnet address left the v6 `fd7a::` twin reported on
  every run. A gate that cries wolf gets ignored. Both twins are now listed.
- An allowlist entry requiring a `process` match is **unsatisfiable** for
  sockets `ss` cannot attribute (tailscaled, kernel threads, foreign netns).
  Address+port is the identity; process only *narrows* it.

### REMOVED THIS PASS
- **Redis: gone.** Container + quadlet + generated unit removed. `6379` clear.
  Hardcoded password `omega` was plaintext in the quadlet (`--requirepass omega`
  and `redis-cli -a omega ping`) — treat as compromised, it is in git history.
  Record: `data/quarantine/redis_20260928/`.
- **Deluge: config quarantined, binaries pending root.** 4.0 MB of config copied
  to `data/quarantine/deluge_20260928/config/` (45 torrent state files, daemon
  password in `auth` — do not commit publicly).
  **9.3 GB of downloaded media remains at `omega_library/Movies/`** — reported,
  not deleted, pending Architect decision. No downloads in progress (newest
  mtime 7 days prior).

### STILL BLOCKED ON ROOT
- `rpcbind.socket` active → 111 persists; `rpc-statd.service` → 662 persists.
- deluged unit/binaries/packages.
- journald retention drop-in.

### RESIDUAL RISK
The new gate is RED and **temple-grade will fail** until the Architect removes
deluged + rpcbind/statd. That is the gate working, not a regression. 15 findings
remain: rpcbind 111/662 (v4+v6), deluged ×5, rygel ×7 (DLNA media server on LAN
+ docker bridges — **previously unknown, not yet reviewed**).

### ARCHIVE STAGING (confirmed)
`/media/arcana-novai/omega_library/archive_staging` — `/dev/nvme0n1p3`, ext4,
36.9 G free, internal NVMe. **Never stage on `/`** (100% full, 807 M free).

---

## ✅ E1 CLOSEOUT — Gate GREEN, temple-grade 53/53 (2026-09-28)

**Trace:** `trc_e1_closeout` · **Model (M22):** `opencode/space-bunny-free` (runtime-injected)
**Root escalation:** `pkexec` authorised by Architect and confirmed working (`uid=0(root)`).

### Removed (all with proof)
| Item | Action | Proof |
|---|---|---|
| **Deluge** | `apt-get purge deluged deluge-common deluge-console`; system + user units deleted; binary gone; `~/.config/deluge` removed; PPA repo removed; unit masked; orphaned pid 2628 SIGTERM'd | 0 sockets on 51372; `ls /usr/bin/deluged` → no such file |
| **rygel (DLNA)** | `apt-get purge rygel`, unit masked, `/var/lib/rygel` removed | 0 sockets on 34994; binary gone |
| **rpcbind / statd** | `disable --now` + `mask` on `rpcbind.socket`, `rpcbind.service`, `rpc-statd.service`; `fsidd`/`nfs-blkmap` stopped | 0 sockets on 111/662 |
| **Redis** | container + quadlet + generated unit removed (E1 pass 2) | 0 sockets on 6379 |
| **Stale redis test** | `tests/test_hivemind_redis.py` quarantined to `data/quarantine/redis_tests_20260928/` | pytest went **0 tests → 1190 collected** |

### Two bugs I had missed, both now closed
1. **`apt-get purge` leaves the process running.** The unit was unmasked-then-removed
   before the stop landed, so `deluged` survived the purge still holding **6
   sockets**. Purge removes files; it does not kill a running daemon. Caught only
   because I re-ran `ss` after the batch instead of trusting the package manager.
2. **A PPA is a reinstall vector.** `/etc/apt/sources.list.d/deluge-team-*.sources`
   remained — `apt install deluged` would have silently restored the LAN bind with
   no review. Removed. Purging a package is not the same as excising it.

### LAN AUDIT: 15 findings → 0
```
RESULT: PASS — no unapproved non-loopback binds.      (20 listeners, 6 non-loopback)
RESULT: PASS — 22/22 negative tests green.
```
Last entry added: `100.123.51.67:43961` = **tailscaled peer/telemetry**, confirmed
by a root-side `ss -ltnp` (pid 2280, fd=22). Infrastructure, tailnet-scoped, not
a user service.

### JOURNALD RETENTION APPLIED
`/etc/systemd/journald.conf.d/10-retention.conf` → `SystemMaxUse=1G`,
`SystemKeepFree=2G`. Drop-in carries the root-cause comment: the old window was
volume-truncated (10%-of-/var default, 518K entries/day), not time-truncated.

### temple-grade: TOTAL 53 / PASS 53 / FAIL 0, exit 0 — with `check-lan-exposure` in the chain.

### REMAINING, NOT MINE
- `tests/test_hivemind_integration.py` — 2 errors: `state` module has no
  attribute `EXTENDED_SESSIONS_FILE`. This is the **same `_extended_sessions`
  seam** that crash-looped the hub on 2026-09-27. Carmack's file.
- `tests/unit/test_circuit_breaker.py::test_health_report_exposes_state` — 3 fails.
- `tests/test_hub_health.py` — 55 registered vs 54 served: the hub process started
  13:46 and is running pre-consolidation code. **A restart is required**; the
  Architect's call.
- `tcp:8019` grant still missing (admin console).
- `tcp:8017` grant still in the filter; Serve route already down.
- Redis podman volume + `pyproject.toml`/`.env.example`/`config/*` redis refs.

### DISCIPLINE NOTE
I did not touch the OpenCode DB, per explicit standing order. All verification
was filesystem, `ss`, `systemctl`, `journalctl`, and the live MCP HTTP endpoint.

---

## 🔒 ROOT CLEANUP DISPATCH — Closeout (2026-09-28, third pass)

**Trace:** `trc_root_cleanup` · **Model (M22):** `opencode/space-bunny-free` (runtime-injected)
**Escalation:** `pkexec` authorised. One batch, one auth dialog.

### 🔴 THE FINDING THAT MATTERED MOST: I STAGED SECRETS IN A PUBLIC REPO
`data/quarantine/deluge_20260928/config/auth` (deluged daemon password) and
`data/quarantine/redis_20260928/omega-redis.container.removed` (quadlet with
`--requirepass <literal>`) were inside the working tree of a **public** repo
(`Xoe-NovAi/omega-engine`, public since `268528e7`). My earlier dispatch said
"quarantine, do not delete" and I executed that faithfully — while never asking
whether the quarantine *location itself* was safe. Quarantining a secret into a
public repo is not quarantine.

Both moved to `/home/arcana-novai/quarantine/` (outside the repo and outside git
tracking). `data/quarantine/README.md` is now a stub that states the rule:
**this directory is public; sanitised summaries only.** The deluge password is
preserved at `~/quarantine/deluge_20260928/config/auth` (mode 0600, not tracked).

Durable lesson: *a quarantine is only as safe as its location. Check the
containment boundary before moving something into it, not after.*

### Executed this pass
- **`librygel-*` (4 packages) purged.** `rygel` itself was gone last pass, but
  `librygel-{core,db,renderer,server}-2.8-0` remained — the resurrection vector
  the Architect flagged. No rygel packages now.
- **`redis-tools` purged**, `/usr/bin/redis-benchmark` gone.
- **`/etc/redis`, `/var/lib/redis`, `/var/log/redis` removed.**
- **Podman redis volume removed.** `dump.rdb` was **88 bytes** (an empty RDB
  header) plus `appendonlydir/`, 12 K total, owned by subuid 100998.
- No `redis.service` unit file anywhere; no redis cron; no redis binaries.

### ALREADY DONE in the prior pass (verified, not re-run)
rpcbind.socket / rpcbind.service / rpc-statd.service — all `masked` + `inactive`.
deluged — purged, binary gone, unit `masked`, PPA removed, `~/.config/deluge`
gone, orphaned pid 2628 SIGTERM'd. journald drop-in in place.

### Unresolved, deliberate
- `nfs-client.target` is still `active`+`enabled`, and `fsidd.service` /
  `nfs-blkmap.service` are `enabled`+`inactive`. **Not masked** — they are
  client-side targets, hold no listening socket, and the LAN audit confirms
  `111/662` are clear. Left alone: masking a client target could break a future
  intentional NFS mount. Re-raise if the Architect wants them masked.
- `omega_library/Movies` — **not touched.** Architect deleted it (4.0 K remains).

### Gate + temple-grade
```
make check-lan-exposure : 22/22 negative tests PASS
                          RESULT: PASS — no unapproved non-loopback binds (exit 0)
make temple-grade        : TOTAL 53 / PASS 53 / FAIL 0, exit 0
journalctl --verify     : PASS on every journal file
```

### Team
`grokster` completed the Redis reference purge outside `src/omega/**` and
**corrected my test baseline**: `pyproject.toml` `addopts` contains `-x`, so a
plain `pytest` aborts at the first failure. True full-suite state is
**errors=26, failures=4** (not the 2 I reported). Grokster proved via JUnit-XML
test-by-test diffing that it introduced **0 new failures**. The `EXTENDED_SESSIONS_FILE`
cluster is dispatched to `john_carmack` — it is the same `_extended_sessions`
seam that crash-looped the hub on 2026-09-27.

---

## 🔧 REDIS DEPLOY SURFACE + STALE-PATH CLASS (2026-09-28, fourth pass)

**Trace:** `trc_deploy_sweep` · **Model (M22):** `opencode/space-bunny-free` (runtime-injected)

### The last live redis: `deploy/infra/docker-compose.yml`
Carmack's code sweep was cosmetic because the **deploy surface** still defined
`omega-redis` with `restart: unless-stopped` and the hardcoded default secret
`${REDIS_PASSWORD:-omega}`. One `podman-compose up` would have resurrected it.

Removed:
- the entire `redis:` service block (image, ports, command, healthcheck, volume, deploy limits)
- **2** redis-only `depends_on:` blocks (iris, firecrawl)
- **1** `redis:` key from a MIXED block (firecrawl#2) — `playwright` preserved
- **3** `REDIS_URL=redis://:${REDIS_PASSWORD:-omega}@omega-redis:6379` injections
- all 4 occurrences of the hardcoded default secret

Validated: YAML parses; `podman-compose config` exits 0 from the correct CWD;
**0 redis occurrences in the RENDERED config**; services = qdrant, postgres,
caddy, iris, firecrawl, playwright.

⚠️ **Queue consumers flagged, not repointed:** `iris` and `firecrawl` (×2) were
`depends_on: redis: service_healthy`. Removing the dependency stops them being
blocked; it does NOT give them a queue. If they need one, that is an
Architect-level design decision. I did not silently repoint them at anything.

### Allowlist audit — Carmack's concern did NOT apply
He warned the allowlist might contain 6379. **It does not.** I read all 115 lines
and verified every entry against live state:
- `allowed_lan_bindings: []` — EMPTY. Zero LAN binds approved. No 6379 anywhere.
- 8 `allowed_tailnet_bindings` (8016/8019/40656/43961 × v4+v6) — all `tailscaled`,
  all still live, all justified. 43961 root-confirmed as tailscaled pid 2280.
- Nothing removed. **A hole needs a service behind it; redis is gone, so there
  was no hole to close.** The gate is honest because nothing was ever added.

### Stale-path class — the systemic sweep
| Surface | Finding |
|---|---|
| `pyproject.toml` `--ignore=.../odysseus-dev` | **Already removed by Carmack**, documented in-place. Path still absent from disk. Comment-only reference remains. |
| `pyproject.toml` `addopts` | `-x` present → plain `pytest` aborts at first failure, reporting a misleadingly small count. Noted, not changed (Carmack's call). |
| `Makefile` — 54 file refs scanned | 6 flagged by regex, **all 6 verified inert**: 3 in `#` comments, 2 self-avoiding grep baselines in a PEM gate, 1 an `echo` string in `sprint-plan-llms-txt`, 1 a `cd` to an EXTERNAL godot dir that exists. |
| `mcp_servers/omega_hub/server.py` `_PASSTHROUGH_TOOLS` | 6 names — **all 6 verified** as real defs in `hub_tools/tools.py`. No phantom symbols. |
| `pytest.ini` / `tox.ini` / `setup.cfg` / `.githooks/commit-msg` | Do not exist. |

**Zero live stale filters found.** The class was already excised; I verified
rather than assumed, because "there are none" is the hardest claim to trust.

### 🔴 CONFTEST — the suppression was worse than reported, and the real cause was not `sep_title`
Carmack said `tests/conftest.py:75` set `tr.sep_title = None`. True, but that was
not the main cause. **`pytest-tldr` (a declared dependency) hijacks the terminal
reporter entirely** and prints a bare `OK` / `Ran N tests` instead of pytest's
summary. With it active, `pytest tests/ --collect-only -q` printed **no test
count at all** — 2410 collected, terminal silent.

Fixed: removed `sep_title = None` and added an explicit, always-printed line:
```
═══ OMEGA TEST RESULT: PASS|FAIL | collected=… passed=… failed=… errors=… skipped=… xfailed=… ═══
```
Counts read from the reporter, with a guard that derives `collected` from
executed tests so a run can **never print a false zero**. Wrapped in try/except so
reporting can never break a test run.

**Honest limitation:** under tldr, the per-category sub-counts
(passed/failed/skipped) are still unreliable — tldr keys outcomes "x"/"f"/"E".
`collected` and the PASS/FAIL verdict are correct. JSON sub-counts remain
authoritative (`--json-report`). Reporting a wrong number would be worse than
reporting a coarse one.

Collection count **unchanged: 2410 before, 2410 after** (asserted).

### Hub restart
`omega-hub.service` restarted per order. `ActiveState=active`, `SubState=running`,
`NRestarts=0`, new start 22:11:11, `:8016/health` 200. **Tool count 54 → 54.**

**The 55-vs-54 discrepancy was NOT a stale process.** `tests/test_hub_health.py`
**passes now, before any restart** — the in-process registry reports 54, matching
the live hub. The 55 was observed mid-run while Carmack's consolidation edits
were still landing. Restarting a correct process fixed nothing; it was a no-op.

### Ordering-hazard check (Architect's explicit warning) — I checked
Three full-suite runs, identical code:
```
pre-restart   passed=2293 failed=35 error=26 collected=2410
post-restart  passed=2283 failed=45 error=26 collected=2410
re-run        passed=2299 failed=29 error=26 collected=2410
```
**Errors pinned at exactly 26 across all three** → not restart-induced.
Failures oscillate 35/45/29 → **flaky**. 13 named tests failed post-restart and
**pass in isolation** (`test_orchestrator::test_dispatch_timeout`,
`test_oracle::test_talk_mention_at_start` → OK). Reported, not assumed.

### Remaining failures, attributed
- **26 errors — Carmack.** `state` has no attribute `EXTENDED_SESSIONS_FILE`
  (the 09-27 `_extended_sessions` seam). Plus `BudgetGuard.__init__() got an
  unexpected keyword argument 'enable_redis'` ×10 — redis-removal fallout in his layer.
- **22 failures — environmental.** `InferenceOOMError: available RAM below 1.0 GB
  safety threshold`. Root FS is 100% full; this host cannot hold an inference model.
- **~29–45 — flaky pool**, oscillating per run.

### Gates
`make check-lan-exposure` → 22/22 + no unapproved binds, **exit 0**
`make temple-grade` → **TOTAL 53 / PASS 53 / FAIL 0, exit 0**
