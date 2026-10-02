## Recovery Briefing Review

Verified the two load-bearing claims against OpenCode's official docs before building anything on top of them. One is confirmed. The other check surfaces a **second, previously-undetected bug** that's been silently breaking the config across every version I've reviewed so far.

### Claim verification

| Claim | Verdict | Evidence |
|---|---|---|
| `opencode mcp call` doesn't exist | ✅ **Confirmed** | Official CLI reference (opencode.ai/docs/cli) lists exactly `add`, `list`/`ls`, `auth`, `logout`, `debug`, `models` under `mcp`. No `call`. Your briefing is right — every `verify_step` and daemon call built on `opencode mcp call mempalace ...` across v3.0/v3.1/v3.2 was dead on arrival. |
| MemPalace package identity (`author: milla-jovovich`, v3.9.0, 36 tools, exact dependency pins) | ⚠️ **Not verifiable — and this matters** | MemPalace is real, but there are at least **five** distinct "mempalace"-named projects in the wild right now (upstream `aywp222/mempalace`, a Docker wrapper, a `mempalace-code` fork, a `mempalace-sync` add-on, a `pi` extension) with *different* tool counts reported (29 vs 28 vs unstated) and no source I found names "milla-jovovich" as maintainer. The upstream project's own README carries an active warning: **"Beware of impostor sites... any other domain may distribute malware."** Don't install from the deep-research agent's specifics — pin the exact PyPI project URL and GitHub org yourselves before `pip install`. |

### New finding — the static `mempalace` config entry has always been silently invalid

```
An MCP server never starts → Check the entry shape. A local server needs `command`
as an array, not a string with a separate `args` field — a string command with args
is Claude Desktop's format, and opencode ignores it silently rather than erroring.
```
— OpenCode integration docs

Every config I've seen from you (v3.0 through today) writes:
```json
"mempalace": {
  "type": "local",
  "command": "/home/xnai/WanderGround/.venv/bin/mempalace-mcp",
  "args": ["--palace", "/home/xnai/WanderGround/mempalace"],
  "enabled": true
}
```
That's the Claude-Desktop shape, not OpenCode's. **OpenCode silently ignores this entry — no error, no log, nothing.** This is consistent with (and explains the mechanism behind) your team's own "Lesson Learned #1" that local servers in `config.json` get ignored and only the `opencode mcp add` CLI registration counts — it's not a version quirk, it's this exact schema mismatch. Fix, whether or not you keep the static entry:
```json
"mempalace": {
  "type": "local",
  "command": ["/home/xnai/WanderGround/.venv/bin/mempalace-mcp", "--palace", "/home/xnai/WanderGround/mempalace"],
  "enabled": true
}
```

---

### Answers to open questions

**Q1 — Daemon strategy: go with A, but narrow it to what's actually confirmed.**
Across every source I found, `mine`, `search`, `status`, `init` show up consistently as real CLI subcommands (mirrored 1:1 as MCP tools and as `/mempalace:*` slash commands in a third-party extension). **`checkpoint` and `sync` never appeared anywhere** — not in any CLI reference, tool list, or extension I found. That doesn't prove they don't exist, but it means the whole "fire `mempalace_checkpoint` then `mempalace_sync` after each file batch" design in your manual's Appendix B was never confirmed against a real tool surface — it may be carried-over assumption, not fact.

Recommended daemon body, once the palace exists:
```python
async def process_batch_cooldown():
    await anyio.sleep(2.5)
    try:
        await anyio.to_thread.run_sync(
            lambda: subprocess.run(
                ["/home/xnai/WanderGround/.venv/bin/mempalace", "mine",
                 os.path.expanduser("~/WanderGround/inbox")],
                check=True, capture_output=True, text=True
            )
        )
    except subprocess.CalledProcessError as err:
        print(f"[WanderGround] mine failed: {err.stderr}")
    finally:
        lock_event.set()
```
Before wiring this in, run `mempalace --help` and `mempalace mine --help` yourselves (Phase 1 of your own recovery path already does this — good instinct, don't skip it) and confirm `mine` re-indexes existing files idempotently (won't duplicate entries on repeated runs over the same inbox).

**Q2 — Config cleanup: yes, remove the duplicate `mcp.mempalace` sibling, and also apply the array-format fix above in the same pass.** Don't fix one and miss the other — the duplicate-key bug and the wrong-shape bug are both in the same block and both silently defeat it.

**Q3 — API keys:** Your plan (bashrc cleanup → `.env` → `{env:...}` interpolation, already correct in the JSON) is right in shape, but confirm the mechanism before trusting it: `{env:PARALLEL_API_KEY}` reads from the *process environment at the moment OpenCode starts*, not from a bespoke `.env` loader inside OpenCode. A `~/.config/opencode/.env` file does nothing unless something sources it into that environment first (shell profile for interactive TUI use, `EnvironmentFile=` for anything under systemd). Test it directly rather than assume:
```bash
env -i HOME="$HOME" PATH="$PATH" PARALLEL_API_KEY=probe123 opencode mcp debug parallel-search
```
If that fails to pick up `probe123`, the interpolation mechanism doesn't work the way the config assumes, and this is worth knowing before real keys go anywhere.

**Q4 — Tool grants:** The `"tools": { "parallel-search": true }` key is the *server* name, not a tool name — this almost certainly grants the whole server's tool surface (all of `parallel-search`'s tools) to that agent, matching your own Lesson #2 ("tools as simple boolean" is a per-server toggle, not per-tool). I don't have a citation confirming per-tool sub-selection syntax exists at all in OpenCode 1.18+ — if you need to scope an agent to only `web_search` and not `web_fetch`, confirm via `opencode mcp debug` output or the docs directly; don't assume it's possible.

**Q5 — Prioritization:** Agreed with your own instinct — Node 1 first. The Tailscale ACL admin-console step and staging the USB package are safe to do in parallel since they don't touch Node 1's live, currently-broken state. Don't start Node 0's deploy script until Node 1 clears the "Better" tier below, since Node 0 deploys the same broken config/daemon pattern.

**Q6 — Verification gate: use your "Better" tier, not "Minimum" or "Full," and treat them as two separate gates.**
- Gate 1 (prove the palace works at all): `mempalace init` → `mempalace mine <test-file>` → `mempalace search <term-from-test-file>` returns it, all via the CLI directly, no OpenCode involved. This isolates whether MemPalace itself works from whether OpenCode's MCP wiring works.
- Gate 2 (prove OpenCode sees it): agent conversation calls `mempalace_search` and gets the same result via MCP.
- Gate 3 (daemon automation) is a separate, later concern — don't let an unproven daemon block proving the first two.

**Q7 — Ponytail audit:** Worth running, cheap. But a static audit skill won't catch "this CLI subcommand doesn't exist" — that class of bug only surfaces by actually running `--help` against the installed binary, which is exactly what your own Phase 1 already does. Use both, don't substitute one for the other.

---

### Additional traps not yet on your list

| Trap | Why it matters |
|---|---|
| `python3 -m venv` with no Python version check | MemPalace reportedly needs `<3.14` (chromadb/Pydantic v1 constraint per your research). If system `python3` is already 3.14+, the venv will build fine and `pip install mempalace` will fail or partially install — confirm `python3 --version` before Phase 0's venv step, not after a failed install. |
| `chromadb` as a dependency on this hardware target | Heavyweight vector-DB dependency on a Ryzen 5700U/Iris Xe box you've otherwise been keeping deliberately lean (torch-free, ONNX/GGUF-only per [[omega-engine]]). Worth a standalone `pip install chromadb` smoke test before wiring the full palace around it, so a slow/failed native-wheel build doesn't surface for the first time in the middle of Phase 2. |
| Stale version-pin check | `verify_step "OpenCode version" "... grep -q '1\.1[89]'"` will now halt deployment if OpenCode itself has been updated past 1.19 during all this churn — confirm current `opencode --version` before re-running, or you'll get a fourth "mysterious Phase 0 failure" that's actually just this gate doing its job. |

The pattern across all three of these review rounds is the same: each "fix" has been narrowly correct but revealed a deeper assumption that was never checked against the real tool. Before the next deploy attempt, I'd treat "run `--help`/`debug` against every real binary and confirm its actual surface" as a mandatory Phase 0 step in its own right, not something folded into the deploy script's existing checks.
