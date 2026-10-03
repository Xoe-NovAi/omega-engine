## Deepening Review — v3.1 Verification

Read all 6 updated files against the 10 claimed fixes. **9 of 10 are genuinely fixed. One (#1, the daemon) is only half-fixed — the process/thread swap was correct, but it exposed a second, more serious bug that was masked by the original crash.**

### Fix verification

| # | Fix | Verdict | Notes |
|---|-----|---------|-------|
| 1 | `to_process` → `to_thread` | ⚠️ **CONCERN — see below** | Correct primitive, wrong call site. Daemon will run but never fire checkpoints. |
| 2 | MemPalace verify_step `\|\| true` removed | ✅ PASS | Confirmed gone from both scripts (line 32 in each). Will now correctly halt deployment under `set -e` if MemPalace is down. |
| 3 | Node 0 Tailscale check → `.Peer[]` for `xnai-n1-asus` | ✅ PASS | Symmetric with Node 1 now. |
| 4 | Duplicate `mempalace` key in node1 JSON | ✅ PASS | Single definition under `mcp.servers.mempalace`, no sibling. |
| 5 | Bashrc marker-guarded idempotency | ✅ PASS (with edge case) | See Q2 below — markers work for the common case. |
| 6 | Backup guard `[ -f ... ] && cp ...` | ⚠️ **CONCERN — see below** | Fixes the first-deploy crash, but introduces a silent-failure mode. |
| 7 | `library_web_search.py` bare `except:` → `except Exception:` | ✅ PASS | Confirmed line 147, node0 script. |
| 8 | Domain routing `06_general` fallback | ✅ PASS | Confirmed line 177 — every query now lands in a real bucket. |
| 9 | Systemd circuit breaker | ⚠️ **CONCERN — see below** | Values are reasonable but placed in the wrong section. |
| 10 | API key placeholder warnings | Not verifiable | Manual/README weren't in this upload batch — flag to confirm separately. |

---

### New finding — daemon still won't fire checkpoints (blocks #1)

```python
async with anyio.create_task_group() as tg:
    await anyio.to_thread.run_sync(run_inotify, send_stream)   # <-- awaited directly
    async for filename in receive_stream:                      # <-- never reached
        ...
```

`run_inotify` runs `inotifywait -m` — a monitor-mode process that never exits under normal operation, so `for line in proc.stdout:` inside it never returns. Because that call is `await`ed directly rather than handed to the task group, **control never falls through to the `async for filename in receive_stream:` loop.** The watcher thread will happily call `ch.send()` into an infinite-buffer stream forever, but nothing is ever consuming it — `process_batch_cooldown` (and therefore `mempalace_checkpoint` / `mempalace_sync`) never runs. The daemon will show `systemctl --user is-active` = `active` and *look* healthy indefinitely while silently doing nothing.

This bug existed in v3.0 too, but was masked — the `to_process` pickling failure crashed the daemon before this sequencing mattered. Fixing the primitive surfaced the real bug underneath it.

**Fix:**
```python
async with anyio.create_task_group() as tg:
    tg.start_soon(anyio.to_thread.run_sync, run_inotify, send_stream)
    async for filename in receive_stream:
        if filename.endswith(".md") and lock_event.is_set():
            lock_event = anyio.Event()
            lock_event.clear()
            tg.start_soon(process_batch_cooldown)
```

**Verification once patched** — don't trust `systemctl is-active` alone; it will say "active" either way. Confirm the consumer loop is actually running:
```bash
touch ~/WanderGround/inbox/test_probe.md
sleep 4
journalctl --user -u wanderground-embed -n 20 --no-pager | grep -q "Firing atomic database checkpoint" \
  && echo "PASS: consumer loop live" || echo "FAIL: daemon accepting events but not processing them"
rm ~/WanderGround/inbox/test_probe.md
```

---

### Systemd: `StartLimit*` in the wrong section

```ini
[Service]
Restart=always
RestartSec=5
StartLimitIntervalSec=60   # <- belongs in [Unit]
StartLimitBurst=3          # <- belongs in [Unit]
```

`StartLimitIntervalSec=` / `StartLimitBurst=` are `[Unit]`-section directives per `systemd.unit(5)`. Recent systemd versions tolerate the old `[Service]` placement for backward compatibility with a deprecation warning, but that's version-dependent — don't rely on it silently working. Move them:

```ini
[Unit]
Description=WanderGround Async Embedding Daemon (anyio Hardened)
After=default.target
StartLimitIntervalSec=60
StartLimitBurst=3

[Service]
Type=simple
WorkingDirectory=%h/WanderGround/daemon
ExecStart=%h/WanderGround/.venv/bin/python3 %h/WanderGround/daemon/embed_daemon.py
Restart=always
RestartSec=5
```

Confirm it's actually being honored: `systemctl --user show wanderground-embed.service -p StartLimitIntervalUSec -p StartLimitBurst` — if either comes back empty/default, the directive was ignored.

---

### Backup guard: `&&`/`||` masks real failures

```bash
[ -f ~/.config/opencode/opencode.json ] && cp ... || log_warn "No existing opencode.json to backup (first deploy)"
```

If the file exists but `cp` genuinely fails (disk full, permission denied), the `||` branch still fires — you get "first deploy" logged when it's actually a **backup failure on a redeploy**, and `set -e` won't catch it because the compound statement's final exit status is `log_warn`'s (0). Phase 1 then overwrites the live config with zero real backup. Use explicit `if`:

```bash
if [ -f ~/.config/opencode/opencode.json ]; then
    cp ~/.config/opencode/opencode.json ~/.config/opencode/opencode.json.bak.${BACKUP_SUFFIX} \
        || { log_error "Backup failed on existing config"; exit 1; }
else
    log_warn "No existing opencode.json to backup (first deploy)"
fi
```

---

### Answers to open questions

**Architecture & design**
1. Threading model is correct in principle (`to_thread` + portal via `from_thread.run`) — see the `tg.start_soon` fix above for the remaining defect. Lock re-instantiation itself is race-free: the `async for` loop is single-consumer, cooperative, with no `await` between the `is_set()` check and reassignment, so debounce/coalescing is sound once the consumer actually runs.
2. Marker guard handles the common case but not partial corruption — if the script is killed mid-write between `# OMEGA_ENGINE_API_KEYS` and `# END ...`, the start marker alone will cause future runs to skip re-appending a broken block. Safer: delete-and-reinsert the whole marked region each run (`sed -i '/# OMEGA_ENGINE_API_KEYS/,/# END OMEGA_ENGINE_API_KEYS/d' ~/.bashrc` then append fresh) — fully idempotent and self-healing regardless of prior state.
3. Prefer a `.env` file over `.bashrc` for this — see the dedicated section below (Q3 + Q11 combined, since they're the same underlying issue).
4. `StartLimitIntervalSec=60` / `StartLimitBurst=3` is reasonable for a long-running daemon — 3 crashes in 60s before backing off is neither too twitchy (normal restarts from e.g. a laptop suspend/resume won't trip it) nor too lenient. Fine as-is once moved to `[Unit]`.
5. Tailscale ACLs aren't something `tailscale set` manages client-side — that's peer-level settings (SSH, exit-node), not network ACLs, which live in the tailnet policy file. Automate via the [Tailscale API](https://tailscale.com/api) (`PATCH /api/v2/tailnet/{tailnet}/acl`) with an API key, or manage the policy file in source control and push it with `tailscale`'s admin API — idempotent because you're pushing a full desired-state document, not a diff.

**Deployment & operations**
6. See the `&&`/`||` masking fix above — don't skip the backup silently, distinguish "no file" from "cp failed."
7. Yes, verify registration immediately after `opencode mcp add`, don't wait for Phase 9:
   ```bash
   opencode mcp add mempalace -- ... 2>/dev/null || true
   opencode mcp list --verbose 2>&1 | grep -q mempalace || { log_error "mempalace registration did not take"; exit 1; }
   ```
8. `import inotify` will fail — the package `inotify-simple` exposes the module as `inotify_simple`, not `inotify`. This check is currently silently wrong (it'll always re-run `pip install`, which is harmless but means the guard does nothing). Fix: `import inotify_simple`. Also add a binary check: `command -v mempalace-mcp >/dev/null || log_warn "mempalace-mcp binary not found on PATH"`.
9. Being stricter on `401`/`403` than `405` is reasonable — 405 genuinely means "wrong HTTP method, endpoint is alive," while 401/403 could mean your API key is bad (which you want to know about explicitly, not lump into "reachable"). Split the check:
   ```bash
   CODE=$(curl -s -o /dev/null -w '%{http_code}' https://search.parallel.ai/mcp)
   case "$CODE" in
     200|405) log_success "Endpoint reachable ($CODE)" ;;
     401|403) log_warn "Endpoint reachable but auth rejected ($CODE) — check PARALLEL_API_KEY" ;;
     *) log_error "Unexpected response ($CODE)"; exit 1 ;;
   esac
   ```
10. End-to-end federation test should cover the full chain, not just connectivity: `@kali` issues a `web_search` → confirm a file lands in `~/WanderGround/inbox/kali_*.md` with valid frontmatter → confirm a line appended to `search_log.jsonl` → confirm `mempalace_checkpoint`/`mempalace_sync` actually ran (per the daemon-verification command above) → confirm `mempalace_search` returns the newly ingested content. Anything short of that last step doesn't prove the loop actually closed.

**Security & hardening**
11 + 3. Combined: move off `.bashrc`. Real API keys in a world-readable, `source`d-by-every-shell dotfile is bad practice independent of the placeholder issue. Use `~/.config/opencode/.env` (mode 600) and load it explicitly at daemon/script start rather than relying on interactive-shell sourcing:
    ```bash
    install -m 600 /dev/null ~/.config/opencode/.env
    cat >> ~/.config/opencode/.env << 'EOF'
    PARALLEL_API_KEY=<real key here>
    EOF
    ```
    ```python
    from dotenv import load_dotenv
    load_dotenv(os.path.expanduser("~/.config/opencode/.env"))
    ```
    Check whether OpenCode's `{env:PARALLEL_API_KEY}` header substitution reads from `os.environ` at process launch — if so, the systemd unit should `EnvironmentFile=%h/.config/opencode/.env` rather than relying on `.bashrc` being sourced at all (a systemd user service does **not** source `.bashrc` by default — this is worth checking directly, since right now `PARALLEL_API_KEY` may not even be visible to the daemon process as deployed).
12. Passwordless sudo is a real assumption to surface, not paper over. Fail explicit and early rather than hanging on a password prompt inside a script meant to run unattended:
    ```bash
    sudo -n true 2>/dev/null || { log_error "Passwordless sudo required for inotify-tools install — run 'sudo -v' first or add a sudoers rule"; exit 1; }
    ```
13. Worth checking `direct: true` if you're latency-sensitive on the federation calls, but Tailscale falls back to DERP relay transparently — the mesh check as written proves reachability, not performance. Add a diagnostic (not a blocker): `tailscale ping --timeout 3s xnai-n1-asus.tail51f14a.ts.net` and log whether it reports `via DERP` vs a direct path, for troubleshooting rather than gating deployment.

**Code quality & maintenance**
14. Silent catch-and-print in `process_batch_cooldown` is acceptable for now given `Restart=always`/backoff will recover the daemon itself, but the checkpoint/sync failure itself is currently unobservable outside `journalctl`. At minimum, write a sentinel file or last-failure timestamp somewhere `opencode mcp list`/a status subagent can surface, so a silent sync failure doesn't go unnoticed for days.
15. Yes — add `StandardOutput=journal` and `SyslogIdentifier=wanderground-embed` explicitly. It's the systemd default for `Type=simple` already, but making it explicit avoids surprises if the unit is ever templated or inherited.
16. Pin versions. `pip install anyio inotify-simple` with no version spec means a future `anyio` major bump (you already had one breaking change — `abandon_on_cancel`) can silently reintroduce a break on next redeploy. Pin: `pip install 'anyio>=4.0,<5.0' 'inotify-simple==1.3.5'`.

**Documentation & handoff**
17. Rollback via `sed` between markers will silently no-op if markers are missing (manual edit removed them) — same root issue as Q2. Have rollback check for marker presence first and fail loud if absent, rather than assuming success.
18. Yes — pull the fixes table into a standalone `CHANGELOG.md`. Embedding it in a 39KB manual means it'll get stale or buried; a changelog is the thing people actually diff between versions.
19. Add at minimum: a unit test asserting `tg.start_soon` (not bare `await`) wraps the blocking call in the daemon (this exact class of bug will keep recurring in async code without a test that fails on it), and an integration test that touches a file in `inbox/` and asserts a checkpoint call fires within N seconds (the probe command above, scripted).
20. Given what's outstanding — the daemon consumer-loop bug is the most severe remaining item (it silently defeats the entire ingestion pipeline's purpose). After that: confirm the `.bashrc`/systemd env-visibility question in Q11, since a broken API key path makes everything downstream moot regardless of daemon health. Node 0 SSH/deployment and ZRAM/thermal work are lower priority until the core daemon loop is proven to actually fire under load.
