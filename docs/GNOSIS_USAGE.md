# Gnosis Lock Protocol — Usage Guide

> **Purpose**: Before you compact (or lose) an OpenCode session, this locks all
> session gnosis to disk so context is never lost.
>
> **TL;DR**: From any terminal tab, while OpenCode is still open, type:
> ```bash
> gnosis-lock "what I was doing"
> ```
> then go back to OpenCode and run `/compact`.

---

## 1. Why this exists

OpenCode context windows fill up. When you `/compact` (or an auto-compaction
fires), the model's working memory is summarized away. The **Gnosis Lock
Protocol** captures the full session state *before* compaction so nothing is
lost:

1. Git state (commit, dirty files, recent commits)
2. OpenCode config snapshot
3. MCP server status
4. System state (RAM, CPU, swap, load)
5. Session narrative (template to fill in)
6. Evolution delta (what changed vs last session)
7. Persistent identity update
8. Session manifest (index of all artifacts)

Everything is written to `gnosis/sessions/`, `gnosis/evolution/`, and
`gnosis/identity/` inside the project.

**Important**:
- OpenCode (v1.18.x) does **not** support hooks / lifecycle events (yet), so the
  ritual cannot fire automatically on `/compact`.
- **There is no CLI command to compact a running OpenCode session.** Verified
  2026-09-09: `opencode compact` is not a real subcommand — it treats "compact"
  as a project path. Compaction can only be triggered from **inside** the TUI by
  typing `/compact` (or via auto-compaction when context fills).
- Therefore the terminal workflow is exactly **two steps**:
  1. `gnosis-lock "reason"` — lock gnosis to disk
  2. Switch to OpenCode and type `/compact` (inside the session)

---

## 2. Setup

The shell functions live in `~/.bash_aliases` (auto-loaded by `~/.bashrc`).

**Already done** (by the Build agent):
- `~/.bash_aliases` created with `gnosis-lock`, `gnosis-stats`, and `oc` alias
- `Makefile` gained `gnosis-lock` and `gnosis-stats` targets

**If you ever need to re-enable** (e.g. after a fresh shell config):
```bash
# Option A: load the functions in the current shell
source ~/.bashrc

# Option B: verify the file exists and is loaded
ls -la ~/.bash_aliases
type gnosis-lock        # should print a function definition
```

> If `type gnosis-lock` prints nothing, run `source ~/.bashrc` or open a new
> terminal tab.

---

## 3. Commands (exact usage)

### 3.1 `gnosis-lock` — run the pre-compaction ritual (THE command)

```bash
# Simple — runs ritual with a default reason
gnosis-lock

# With a reason (recommended — it lands in the evolution log)
gnosis-lock "finished implementing bench-compare"

# Multiple words are fine; everything is treated as one reason
gnosis-lock "before adding ZRAM config + rewrites"
```

**Output**: the full 8-step ritual, then a friendly reminder:
```
✅ PRE-COMPACTION RITUAL COMPLETE — Session <id> fully captured.
✅ Gnosis locked. Complete the compact INSIDE OpenCode:
   Switch to your session and type:  /compact <reason>
```

**Notes**:
- Runs from **any directory** (paths are absolute inside the script).
- Creates `gnosis/sessions/<session-id>_*.json|.md` artifacts.
- Updates `gnosis/evolution/` and `gnosis/identity/`.
- Takes ~5–15 seconds (MCP capture is time-boxed to 5s).
- **It does NOT compact anything.** It only locks gnosis. The `/compact` is
  always typed inside the running OpenCode session.

### 3.2 After locking — compact inside OpenCode

There is no `oc compact` / CLI compaction. After `gnosis-lock` succeeds:

1. Switch to your **running OpenCode session** (the TUI).
2. Type `/compact <reason>` (or just `/compact`).
3. Done — now the post-compaction session can recover all context from
   `docs/` + `gnosis/` if needed.

`oc` is just a shorthand alias for `opencode` (e.g. `oc --version`).

### 3.3 `gnosis-stats` — check the evolution log

```bash
# Stats + last 5 timeline events
gnosis-stats

# Stats + last 10 timeline events
gnosis-stats 10
```

**Output**: evolution-log statistics (event counts, identity, current session)
plus a recent timeline.

---

## 4. Make targets (equivalent)

Same functionality via `make` (run from the project root):

| Command | Purpose |
|---------|---------|
| `make gnosis-lock REASON="why"` | Run the pre-compaction ritual |
| `make gnosis-lock` | Same, default reason |
| `make gnosis-stats LIMIT=10` | Show stats + last 10 timeline events |

Example:
```bash
cd ~/Documents/Projects/omega-engine-alpha
make gnosis-lock REASON="about to run /compact"
```

**Note:** There is deliberately **no** `compact-gnosis` target — a target
cannot trigger `/compact` inside a running session, so it would be fake.

---

## 5. Manual fallback (raw script)

If both shell functions and make fail (weird shell, minimal env):

```bash
bash ~/Documents/Projects/omega-engine-alpha/scripts/compaction/pre_compaction_ritual.sh \
  "session-$(date -u +%Y-%m-%dT%H-%M-%SZ)" \
  "reason here"
```

---

## 6. Recommended workflow

1. **Work** in OpenCode as normal.
2. When context feels heavy or you're about to `/compact`:
   - Open a **new terminal tab** (or use an existing one).
   - Run `gnosis-lock "worked on X, next is Y"`.
   - See the ✅ banner.
3. **Switch back** to OpenCode and run `/compact "reason"` (in the TUI — this
   is the **only** place compaction can be triggered; there is no CLI command).
4. After compaction, the new session can read `docs/` + `gnosis/` to recover
   full context if needed.

---

## 7. What gets captured (references)

- `gnosis/SESSION_STATE_FORMAT.md` — artifact spec (8 files per session)
- `gnosis/OPENCODE_HOOKS.md` — hook integration guide (notes the current
  "hooks unsupported in v1.18" limitation)
- `gnosis/GNOSIS_LOCK_PROTOCOL.md` — full protocol spec
- `scripts/compaction/evolution_log.py` — evolution-log CLI:
  ```bash
  python3 scripts/compaction/evolution_log.py log DECISION "msg" --tags a,b
  python3 scripts/compaction/evolution_log.py stats
  python3 scripts/compaction/evolution_log.py timeline --limit 10
  python3 scripts/compaction/evolution_log.py export
  python3 scripts/compaction/evolution_log.py query --tag BENCHMARK
  ```

---

## 8. Troubleshooting

| Symptom | Fix |
|---------|-----|
| `gnosis-lock: command not found` | `source ~/.bashrc` or open a new terminal tab |
| Ritual hangs at Step 3 (MCP) | Timeout already added (5s) — wait, it will continue |
| `make gnosis-lock` not found | Run from project root (where `Makefile` lives) |
| Evolution log says 0 events | Events are logged by ritual + manual `log` calls; check `timeline` |
| Want to see a session after compact | `ls gnosis/sessions/`, then read the manifest for that session |

---

## 9. Files involved

```
~/.bash_aliases                                      # shell functions
~/Documents/Projects/omega-engine-alpha/Makefile     # make targets
~/Documents/Projects/omega-engine-alpha/scripts/compaction/pre_compaction_ritual.sh
~/Documents/Projects/omega-engine-alpha/scripts/compaction/evolution_log.py
~/Documents/Projects/omega-engine-alpha/scripts/compaction/opencode_hooks.py
~/Documents/Projects/omega-engine-alpha/gnosis/      # session/evolution/identity stores
~/Documents/Projects/omega-engine-alpha/docs/GNOSIS_USAGE.md   # this file
```