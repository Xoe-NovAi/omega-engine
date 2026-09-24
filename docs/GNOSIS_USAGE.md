# Gnosis Lock Protocol — Usage Guide

> **Purpose**: Before you compact (or lose) an OpenCode session, this locks all
> session gnosis to disk and captures dynamic human reflection so context is never lost.
>
> **TL;DR (Native OpenCode TUI — Recommended)**:
> Inside OpenCode, type:
> ```
> /gnosis-lock "what I was doing"
> ```
> (or simply say *"prepare for compaction"*).
> Answer the dynamic interactive reflection questions in the TUI, then type `/compact` **on its own line**.
> 
> **⚠️ Important**: In OpenCode, `/compact` MUST be typed alone on its own line. Any additional text (like `/compact "reason"`) is treated as a regular prompt, NOT a compaction trigger. This differs from Gemini CLI — in OpenCode, compaction takes no arguments.
>
> **Alternative (Terminal CLI — Fully Supported)**:
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

## The Pack lifecycle (state machine)

Each lock creates a **pack** that moves through an explicit lifecycle. The
empty TODO narrative is a *signal* (pack captured, not ingested), never a bug:

```
CAPTURED ──▶ REFLECTED ──▶ COMPACTED
```

- **CAPTURED**: ritual ran. `manifest.reflection_status = "captured"`,
  `manifest.ready_for_compaction = false`, `identity.pending_pack = <session>`.
  The narrative is TODO **by intent** — the pack is captured but NOT read to compact.
- **REFLECTED**: the skill answered reflection questions, wrote the narrative,
  flipped `reflection_status = "reflected"` + `reflected_at` +
  `ready_for_compaction = true`, cleared `pending_pack`. **A pack is only
  ready to compact once reflected** (readiness contract: captured = not-ready,
  reflected = ready — enforced by the congruence test).
- **COMPACTED**: the plugin injected the narrative into a `/compact`.

The **leash check** (ritual Step 0) refuses to create a new pack while
`pending_pack` is un-reflected: `LEASH CHECK FAILED` + exit 1, unless
`FORCE_PACK=1`. This makes the original "second lock shadows good narrative"
bug impossible by default.

Visibility: `make gnosis-ledger` prints every pack + state + timestamps.
`make gnosis-leash-status` surfaces a taut leash as degraded.

**Important**:
- **OpenCode Plugin Hook & Leash**: The `gnosis-leash.js` plugin listens to
  `experimental.session.compacting`. When you run `/compact`, it automatically
  reads the latest populated narrative from `gnosis/sessions/` and injects YOUR
  exact reflections into the compaction prompt alongside the WanderGround rules.
- **Native TUI vs CLI Workflow**:
  - **Native TUI**: Type `/gnosis-lock "reason"`. The `gnosis-lock` skill runs
    state capture, prompts you with dynamic questions via OpenCode's native
    `question` tool, populates `narrative.md`, commits the session gnosis, and
    signals when it's safe to `/compact`.
  - **CLI Workflow**: Running `gnosis-lock` in terminal runs the capture script
    directly (still 100% supported). CLI locks record `entity`, `channel`,
    `phase` (env `ENTITY`/`CHANNEL`/`PHASE`) and **auto-fill** the narrative's
    Session Summary + Code Changes from captured git/evolution state (Step 6.5),
    so even a CLI-only session is a continuity record.
- Compaction itself can only be triggered from **inside** the TUI by typing
  `/compact` (or via auto-compaction when context fills).
- **⚠️ `/gnosis-lock` vs "Prepare for compaction"**:
  - **`/gnosis-lock` (command/skill)**: Single-purpose primitive. Runs capture + dynamic reflection + narrative commit. **Does NOT** update documentation, run lint/tests, or perform general session-close hygiene.
  - **"Prepare for compaction" (natural-language instruction)**: A broader orchestration task. When you tell your agent this, it composes: `/gnosis-lock` + documentation updates (`docs/`, `README`, `SYSTEM_GUIDE`, `CHANGELOG`) + `make lint` + `make test` + full commit. This is the **temple-grade session-close practice** that prevents data loss and accumulates quality over time.
  - **Auto-compact / bare `/compact`**: No gnosis capture, no reflection, no doc updates. Context is summarized by the model alone — high risk of insight loss.

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

**Output**: the full 9-step ritual, then an explicit readiness reminder:
```
📦 PRE-COMPACTION RITUAL COMPLETE — Session <id> captured.
📦 Captured, not ready for /compact. Run /gnosis-lock reflection first.
```
*(Note: `/compact` takes NO arguments in OpenCode. Type it alone on its line.)*

**Notes**:
- Runs from **any directory** (paths are absolute inside the script).
- Creates `gnosis/sessions/<session-id>_*.json|.md` artifacts.
- Updates `gnosis/evolution/` and `gnosis/identity/`.
- Takes ~5–15 seconds (MCP capture is time-boxed to 5s).
- **It does NOT compact anything.** It only locks gnosis. The `/compact` is
  always typed inside the running OpenCode session.

### 3.2 After capture and reflection — compact inside OpenCode

There is no `oc compact` / CLI compaction. Capture creates a `CAPTURED` pack;
the `/gnosis-lock` reflection step must mark it `REFLECTED` first. After that:

1. Switch to your **running OpenCode session** (the TUI).
2. Type `/compact` **on its own line** (no arguments — OpenCode ignores any text after `/compact`).
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
make gnosis-lock REASON="about to run /compact (standalone command)"
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
3. **Switch back** to OpenCode and run `/compact` **on its own line** (in the TUI — this
   is the **only** place compaction can be triggered; there is no CLI command; `/compact` takes no arguments).
4. After compaction, the new session can read `docs/` + `gnosis/` to recover
   full context if needed.

---

## 6b. Temple-Grade Session-Close Practice (The Orchestration Layer)

The `/gnosis-lock` command is a **single-purpose primitive** — it does one thing exceptionally well. For a production-grade session close that prevents data loss and accumulates quality over time, compose it into a broader orchestration:

**When you say "Prepare for compaction" to your agent, it should:**
1. **Run `/gnosis-lock`** — capture state, dynamic reflection, commit gnosis
2. **Update documentation** — `docs/`, `README.md`, `SYSTEM_GUIDE.md`, `CHANGELOG.md`, `BENCHMARKS.md` as relevant
3. **Run quality gates** — `make lint` (anyio purity, bare exceptions, torch ban) + `make test`
4. **Commit everything** — clean repo with descriptive message linking gnosis + code changes
5. **Signal ready** — "🔱 Gnosis locked, docs updated, gates green. Safe to `/compact`."

**Why this matters:**
- Most users just `/compact` (or let auto-compact fire) and lose the human insight layer
- The gnosis-lock captures *what you learned*; the doc updates capture *what you built*
- Together they create a compounding knowledge asset that survives compaction
- Quality gates ensure the codebase stays temple-grade as it grows

**Anti-patterns to avoid:**
- ❌ Just typing `/compact` — model-only summary, human gnosis lost
- ❌ Running `/gnosis-lock` but skipping doc updates — insights trapped in narrative
- ❌ Skipping lint/tests — technical debt compounds silently
- ❌ Auto-compact without any prep — highest risk of insight loss

---

## 7. What gets captured (references)

- `gnosis/GNOSIS_LOCK_PROTOCOL.md` › Appendix A — artifact spec (8 files per session)
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