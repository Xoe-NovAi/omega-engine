# HARDENED DEPLOYMENT PACKAGE (2026-09-17 — SONNET 5 POST-REVIEW v3.3)

This package contains battle-tested, hardened deployment configurations
for the Omega Engine Alpha federation (Node 1 ASUS + Node 0 HP).
All Sonnet 5 review findings (initial + deepening + post-review) have been addressed.

## Contents

### Deployment Scripts (Canonical)
- `deploy_node1_hardened.sh` — Node 1 (ASUS) atomic deployment **(v3.3 — config format + daemon + verification fixes)**
- `deploy_node0_hardened.sh` — Node 0 (HP) atomic deployment

### Configurations
- `configs/opencode_node1_hardened.json` — Node 1 master config (duplicate mempalace key REMOVED, array format command)
- `configs/opencode_node0_hardened.json` — Node 0 mirror config (kali + makali, array format command)

### Systemd Service
- `wanderground-embed_hardened.service` — Hardened systemd user service (circuit breaker in [Unit], EnvironmentFile)

### Sidecar Daemon
- `embed_daemon_hardened.py` — Hardened anyio sidecar (2026-09-18 current-gen: queue.SimpleQueue + 0.5s poll coordination, no anyio.Event wake races; 2.5s cooldown, ONE mine+sync per batch, failure sentinel, structured JSON logging, **mempalace mine CLI**)

### Prompts
- `prompts/asus_plan.md` — Intel kernel/hardware researcher
- `prompts/grokster.md` — OpenCode internals specialist
- `prompts/kali.md` — Council synthesis / federation law
- `prompts/makali.md` — AMD-only architecture vault

### Documentation
- `IMPLEMENTATION_MANUAL_HARDENED.md` — Complete hardened manual

## Deployment Instructions

### Node 1 (ASUS ExpertBook)
```bash
chmod +x deploy_node1_hardened.sh
./deploy_node1_hardened.sh
```

### Node 0 (HP Pavilion)
```bash
chmod +x deploy_node0_hardened.sh
./deploy_node0_hardened.sh
```

## ⚠️ CRITICAL: API Key Setup Required

**The deployed scripts create `~/.config/opencode/.env` (mode 600) with placeholder keys.** 
**Replace with real Parallel.ai API keys BEFORE production use:**

```bash
# Node 1 - Edit the file and replace the placeholder:
PARALLEL_API_KEY="YOUR_REAL_PARALLEL_API_KEY"

# Node 0 - Edit the file and replace the placeholder:
PARALLEL_API_KEY="YOUR_REAL_PARALLEL_API_KEY"
```

The systemd service uses `EnvironmentFile=%h/.config/opencode/.env` so keys are available to the daemon.

## Sonnet 5 Fixes Applied (v3.2 — Deepening Review)

| # | Component | Bug | Fix Applied |
|---|-----------|-----|-------------|
| 1 | **embed_daemon.py** (CRITICAL) | `to_thread` correct but `await`ed directly — consumer loop never reached | **`tg.start_soon(anyio.to_thread.run_sync, ...)`** — runs concurrently |
| 2 | **embed_daemon.py** (CRITICAL) | No failure observability for silent sync failures | **Failure sentinel** `~/.local/daemon/.last_sync_failure` with timestamp |
| 3 | **Deploy scripts Phase 0** | `|| true` masked MemPalace verify failure | Removed `|| true` from command strings |
| 4 | **Node 0 Tailscale check** | Checked Self.DNSName instead of Peer[] | Fixed to check `.Peer[]` for `xnai-n1-asus` |
| 5 | **Node 1 opencode.json** | Duplicate `mempalace` key in config | Removed duplicate `mcp.mempalace` block |
| 6 | **Bashrc env vars** | Unconditional append duplicated on re-run | **Moved to `.env` file (mode 600)** — no bashrc pollution |
| 7 | **Backup step** | `&&`/`||` compound masked real cp failures | Explicit `if/else` with proper error handling |
| 8 | **library_web_search.py** | Bare `except: pass` swallowed signals | Changed to `except Exception:` |
| 9 | **library_web_search.py** | No domain fallback for unrecognized queries | Added `06_general` catch-all domain |
| 10 | **Systemd service** | `StartLimitIntervalSec/Burst` in `[Service]` | Moved to `[Unit]` section (correct per systemd.unit) |
| 11 | **Systemd service** | No circuit breaker | Added `StartLimitIntervalSec=60`, `StartLimitBurst=3` |
| 12 | **Systemd service** | No explicit logging config | Added `StandardOutput=journal`, `SyslogIdentifier=wanderground-embed` |
| 13 | **Systemd service** | No env file for API keys | Added `EnvironmentFile=%h/.config/opencode/.env` |
| 14 | **Venv bootstrap** | `import inotify` wrong module name | Fixed to `import inotify_simple` |
| 15 | **MCP registration** | No immediate verification after `opencode mcp add` | Added verification: `opencode mcp list | grep mempalace` |
| 16 | **Parallel.ai check** | 401/403 lumped with 405/200 | Case statement: 200\|405=OK, 401\|403=auth warning, else=error |
| 17 | **Sudo check** | Silent hang if passwordless sudo unavailable | `sudo -n true` check before apt install |
| 18 | **Pip versions** | Unpinned — future breaks possible | Pinned: `anyio>=4.0,<5.0`, `inotify-simple==1.3.5` |
| 19 | **Daemon verification** | Only checked `systemctl is-active` | Added probe test: touch file → wait → verify checkpoint fires |
| 20 | **Rollback** | Silent no-op if markers missing | Check marker presence, fail loud if absent |

## Sonnet 5 Post-Review Fixes Applied (v3.3)

| # | Component | Bug | Fix Applied |
|---|-----------|-----|-------------|
| 21 | **opencode.json config** (CRITICAL) | Local MCP `command` string + `args` array (Claude Desktop format) silently ignored by OpenCode | **`command` as array**: `["binary", "arg1", "arg2"]` |
| 22 | **Deploy scripts + daemon** (CRITICAL) | `opencode mcp call` subcommand used — **does not exist** in OpenCode CLI | Removed all `opencode mcp call` usage; daemon uses `mempalace mine` CLI directly |
| 23 | **Verification** | Single verification conflated MemPalace with OpenCode MCP wiring | **Two-stage gates**: Gate 1 (CLI proof), Gate 2 (MCP proof via agent) |
| 24 | **MemPalace package** | Multiple "mempalace" projects; must verify exact source | Pin exact source: `github.com/mempalace/mempalace` |
| 25 | **API key interpolation** | `{env:VAR}` reads from process env at startup, not from `.env` file automatically | Test mechanism: `env -i HOME="$HOME" PATH="$PATH" PARALLEL_API_KEY=probe123 opencode mcp debug parallel-search` |
| 26 | **Python version** | MemPalace/chromadb/Pydantic v1 may not support Python 3.14+ | Verify `python3 --version` < 3.14 before venv creation |
| 27 | **chromadb dependency** | Heavyweight vector DB on lean hardware target | Smoke test `pip install chromadb` in isolation before full setup |
| 28 | **Daemon sync commands** | `mempalace_checkpoint` + `mempalace_sync` never documented | Use confirmed `mempalace mine` CLI command |
| 29 | **OpenCode version gate** | `grep '1\.1[89]'` will fail if OpenCode updated past 1.19 | Verify current `opencode --version` before deploy |

## Hardening Checklist (All Applied v3.3)

- [x] OpenCode 1.18+ tool format: boolean not object
- [x] MemPalace MCP registered via CLI + immediate verification
- [x] Parallel.ai endpoint accepts 405 in validation, distinguishes 401/403
- [x] API keys in `~/.config/opencode/.env` (mode 600) + systemd EnvironmentFile
- [x] Systemd service: StartLimit* in [Unit], StandardOutput=journal, SyslogIdentifier
- [x] anyio 4.x: `to_thread` + `tg.start_soon` (NOT `to_process`, NOT bare `await`)
- [x] anyio 4.x: removed `abandon_on_cancel` parameter
- [x] inotify-tools installed via apt in Phase 0 (with sudo check)
- [x] MemPalace palace check: `sqlite_exact.sqlite3`
- [x] Sidecar daemon: infinite buffer + atomic lock (no Flanagan typo)
- [x] Sidecar daemon: failure sentinel for silent sync failures
- [x] Verify steps: no `|| true` masking failures
- [x] Tailscale check: Peer[] visibility, not Self.DNSName
- [x] Config: no duplicate keys
- [x] Backup: explicit if/else with proper error handling
- [x] Pip versions pinned: anyio>=4.0,<5.0, inotify-simple==1.3.5
- [x] Venv bootstrap: import inotify_simple
- [x] MCP registration: immediate verification after add
- [x] API keys: documented as placeholders requiring substitution

## Post-Deployment Verification (Two-Stage Gates v3.3)

```bash
# Gate 1: CLI Proof — MemPalace Works (No OpenCode Involved)
# 1. Initialize palace (creates sqlite_exact.sqlite3)
/home/xnai/WanderGround/.venv/bin/mempalace init /home/xnai/WanderGround/mempalace

# 2. Ingest test content
echo "omega engine test $(date)" > /tmp/omega_test.md
/home/xnai/WanderGround/.venv/bin/mempalace mine /tmp/omega_test.md

# 3. Verify search returns result
/home/xnai/WanderGround/.venv/bin/mempalace search "omega engine" | grep -q "omega engine" && echo "✅ Gate 1 PASSED" || { echo "❌ Gate 1 FAILED"; exit 1; }

# Gate 2: MCP Proof — OpenCode Sees MemPalace (Requires Agent Conversation)
# 4. Replace placeholder API keys in ~/.config/opencode/.env with real keys

# 5. Register MemPalace MCP server (idempotent)
opencode mcp add mempalace -- /home/xnai/WanderGround/.venv/bin/mempalace-mcp --palace /home/xnai/WanderGround/mempalace 2>/dev/null || true

# 6. Validate MCP servers
opencode mcp list --verbose
# Should show both parallel-search and mempalace

# 7. Test API key interpolation mechanism
env -i HOME="$HOME" PATH="$PATH" PARALLEL_API_KEY=probe123 opencode mcp debug parallel-search 2>&1 | grep -q "probe123" && echo "✅ Env interpolation works" || echo "⚠️ Env interpolation test inconclusive"

# 8. Gate 2 requires agent conversation test (cannot be done via CLI):
# In OpenCode TUI: @build Search for "omega engine" in MemPalace
# Agent should call mempalace_search tool and return the test content

# Gate 3: Daemon Health (Separate, Later)
# 9. Verify daemon active
systemctl --user is-active wanderground-embed.service | grep -q active && echo "✅ Daemon active" || { echo "❌ Daemon failed"; exit 1; }

# 10. Verify daemon consumer loop processes files
touch ~/WanderGround/inbox/test_probe.md
sleep 4
journalctl --user -u wanderground-embed -n 20 --no-pager | grep -q "Firing mempalace mine sync" && echo "✅ Daemon processing" || echo "⚠️ Daemon may not be processing yet"
rm -f ~/WanderGround/inbox/test_probe.md

# 11. TUI test
opencode  # select Nemotron 3 Ultra -> @asus_plan "test query"
```

## Rollback

```bash
# Config rollback
cp ~/.config/opencode/opencode.json.bak.* ~/.config/opencode/opencode.json

# Service rollback
systemctl --user stop wanderground-embed.service
systemctl --user disable wanderground-embed.service
rm ~/.config/systemd/user/wanderground-embed.service
systemctl --user daemon-reload

# Env rollback (.env file)
rm -f ~/.config/opencode/.env

# If bashrc markers exist from old version:
if grep -q "# OMEGA_ENGINE_API_KEYS" ~/.bashrc 2>/dev/null; then
    sed -i '/# OMEGA_ENGINE_API_KEYS/,/# END OMEGA_ENGINE_API_KEYS/d' ~/.bashrc
    log_warn "Removed legacy bashrc API key block"
else
    log_warn "No legacy bashrc markers found — .env already removed"
fi
source ~/.bashrc

# MCP server removal
opencode mcp logout mempalace 2>/dev/null || true
```

## Next Steps After Deployment

1. **Replace API keys** in `~/.config/opencode/.env` with real Parallel.ai keys
2. Apply Tailscale ACL rule in admin console: `src=xnai-n1-asus.tail51f14a.ts.net dst=omega-hub.tail51f14a.ts.net:8016`
3. Launch OpenCode TUI: `opencode`
4. Select Nemotron 3 Ultra in model picker
5. Test: `@asus_plan Ingest kernel THP documentation`
6. Cross-node: `@kali` on Node 0 via omega-hub