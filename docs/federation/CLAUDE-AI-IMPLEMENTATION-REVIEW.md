## Omega Engine — Hardened Federation Review

Reviewed all 6 files against the stated goals in `CLAUDE_AI_REVIEW_PROMPT.md`. One finding below is deployment-blocking; the rest are hardening gaps that contradict the "battle-tested" framing.

### Critical — will fail at runtime

| # | Location | Issue |
|---|----------|-------|
| 1 | `embed_daemon_hardened.py` (both nodes, `watch_and_checkpoint()`) | `run_inotify` is dispatched via `anyio.to_process.run_sync(run_inotify, send_stream)`. `to_process` spawns a **separate OS process**, not a thread. `send_stream` is a `MemoryObjectSendStream` — it isn't picklable, so this will raise on startup (or silently produce a broken channel if some anyio version tolerates it). Even if it were picklable, `anyio.from_thread.run()` inside `run_inotify` requires a *thread portal* back to the parent event loop — that portal doesn't exist across a process boundary. **This should be `anyio.to_thread.run_sync`, not `to_process`.** As written, the sidecar daemon that both deploy scripts install as a `systemd --user` service with `Restart=always` will crash-loop indefinitely (masked by the restart policy, so it'll look "up" in `systemctl is-active` between crashes if timed right, but will never actually process a file). |

This single bug undermines the "hardened, battle-tested" claim for the daemon — it's the component both manuals present as fully fixed.

### High — false verification / broken checks

| # | Location | Issue |
|---|----------|-------|
| 2 | Both deploy scripts, Phase 0 | `verify_step "MemPalace MCP responding" "opencode mcp call ... >/dev/null 2>&1 \|\| true"` — the `\|\| true` is baked into the *command string itself*, so `eval` always returns 0. `verify_step` will print `[SUCCESS] ... passed` unconditionally regardless of whether MemPalace actually responds. This check verifies nothing. |
| 3 | `deploy_node0_hardened.sh` vs `deploy_node1_hardened.sh`, Tailscale check | Node 1 checks `.Peer[] | .DNSName` for `omega-hub` — a real connectivity/peer-visibility check. Node 0 checks `.Self.DNSName` for `omega-hub` — this only confirms Node 0 knows its **own** hostname, not that it can see Node 1. It will pass even if the mesh is fully broken. Should mirror Node 1's pattern: grep `.Peer[]` for `xnai-n1-asus`. |
| 4 | `opencode_node1_hardened.json`, top-level `mcp` object | `mempalace` is defined **twice** — once correctly inside `mcp.servers.mempalace` (string command + args + enabled), and again as a sibling key `mcp.mempalace` with a different, non-matching schema (`command` as an array, no `enabled` field). This second block is dead/conflicting JSON that doesn't exist in the Node 0 config — it's an artifact of a bad merge, not intentional redundancy. Delete it; it invites confusion for a future maintainer diffing the two node configs. |

### Medium — idempotency / practice gaps

| # | Location | Issue |
|---|----------|-------|
| 5 | Both scripts, Phase 2 | `cat >> ~/.bashrc << 'BASHRC_EOF'` appends unconditionally. Re-running either "idempotent" deploy script (explicitly encouraged in the manual for rollback/redeploy cycles) will duplicate the `export PARALLEL_API_KEY...` block on every run, growing `.bashrc` and eventually causing var-shadowing confusion. Guard with a marker comment + `grep -q` check before appending, or write a separate sourced file (`~/.config/opencode/env.sh`) and source it once. |
| 6 | Both scripts, Phase 0 backup | `cp ~/.config/opencode/opencode.json ... || exit 1` — under `set -euo pipefail`, a first-time deploy where `opencode.json` doesn't exist yet will hard-fail before any config is written. Fine for the "already deployed, redeploying" case the manual describes, but the scripts are also pitched as the Node 0 first-deploy path — add a `[ -f ... ] &&` guard. |
| 7 | `library_web_search.py`, cache lookup | `except: pass` — bare except swallows everything including cancellation/shutdown signals from anyio. Narrow it to the specific exception you expect from `ctx.call_tool`, or at minimum `except Exception:`. |
| 8 | `library_web_search.py`, `domain` routing | The keyword chain has a real fallback for `room` (`General_Research`) but **no generic fallback for `domain`** — any query that doesn't match kernel/opencode/consciousness/classical/psychology/game keywords silently files under `01_local_ai/kernel`. A query like "circus website redesign color palette" (plausible given your freelance work mixing into the same tool) would get archived into the kernel domain. Add a `06_general` (or similar) catch-all. |
| 9 | `wanderground-embed.service` | No `StartLimitIntervalSec` / `StartLimitBurst`. Combined with bug #1, once the daemon starts crash-looping, systemd will restart it every 5s forever with no circuit breaker. |

### Answers to your key questions

- **Config architecture**: Mostly sound (boolean tool flags, explicit deny-by-default permission matrix are correct for OpenCode 1.18+). Node 1's config has the duplicate-key defect (#4) — fix before treating it as canonical.
- **Parallel-search wrapper**: Pattern (cache-check → search → bounded concurrent fetch → archive+audit) is architecturally reasonable. The bare `except` (#7) and missing domain fallback (#8) are the actual edge cases, not the concurrency model.
- **anyio daemon**: Not safe as written — see #1. This needs to be fixed and re-tested before Node 0 deployment, not just documented as hardened.
- **MCP registration (config + CLI add)**: The dual-path (declare in JSON, then `opencode mcp add`) matches your own documented lesson (#1 in the manual) that config-only entries are ignored for local servers — so the JSON entries are effectively inert documentation, and the CLI call is what matters. Not a race condition since it's idempotent and sequential in the script, but the `2>/dev/null || true` on the `add` call means a genuine registration failure (bad path, missing binary) is silently swallowed with no downstream check for it.
- **Documentation completeness**: The manual is thorough on *narrative* (lessons learned, phase-by-phase), but doesn't currently reflect bug #1, so a future maintainer following it will deploy a broken daemon believing it's fixed.
- **Security posture**: `PARALLEL_API_KEY="pk_hp_$(date +%Y%m)"` / `pk_asus_$(date +%Y%m)` — these aren't real credentials, they're date-derived placeholder strings. If this is literally what ships in `.bashrc`, `parallel-search` auth will 401 on every call. Confirm whether the real key gets substituted elsewhere (a `.env` overlay, secrets manager) before deployment — as written in these files, it's a fake key.
- **Operational readiness for Node 0**: Two things worth verifying before you trust this package as "battle-tested on Node 1": your own [[asus-node1-provisioning]] notes had Node 1 blocked on a Secure Boot/GRUB failure as of Sept 7 — worth confirming that's resolved and Node 1 is actually the "PRODUCTION — Deployed & Verified" state the manual claims before using it as the reference implementation for Node 0. Separately, the omega-hub FastMCP server that Node 0's wrapper (`library_web_search.py`) will run inside had an open audit with flagged issues (disabled start backoff, a mocked proxy handler, disabled `RequestSizeLimitMiddleware`, a lazy-init race) — if that audit hasn't closed those out, they compound with bug #1 above once Node 0 goes live.

### Priority fix order
1. Daemon threading bug (#1) — blocking.
2. Fake/placeholder API key (security) — blocking for any real `parallel-search` calls.
3. Broken verify_step + asymmetric Tailscale check (#2, #3) — these are actively lying to you about deployment health.
4. Duplicate JSON key, bashrc idempotency, bare except, domain fallback (#4–8) — cleanup before calling this "hardened v3.0."
