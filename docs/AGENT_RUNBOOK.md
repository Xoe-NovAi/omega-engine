# Node 1 Agent Runbook — Omega Engine OpenCode Team

> **Purpose**: One dense, authoritative reference so EVERY agent on this machine
> (primary agents, subagents, future harness instances) has full awareness of the
> tools, protocols, and systems available on Node 1.
>
> **Audience**: Any agent operating in an OpenCode session on the ASUS ExpertBook
> P1503CVA. Read this when: entering a session, asked to "prepare for compaction",
> invoked as `/gnosis-lock`, asked about knowledge capture, or before any quality gate.

---

## 0. TL;DR — the commands that matter

```text
/gnosis-lock "reason"            # TUI: capture + dynamic reflection (question tool)
/compact                         # TUI: MUST be standalone line, NO arguments
"prepare for compaction"         # natural language → agent runs full orchestration
make gnosis-lock REASON="..."    # CLI capture (equivalent to the skill's Step 1)
make gnosis-leash-status         # watchdog: is the puppeteer hand alive?
make lint                        # anyio purity + no bare exceptions + no torch
make test                        # 24+ regression tests (also python3 -m unittest)
wander -d <domain> "spark"       # capture a thought into the WanderGround
```

---

## 1. Session-Close & Compaction Protocols (CRITICAL)

### 1.1 The two different things

| Trigger | What it does | Does NOT do |
|---|---|---|
| `/gnosis-lock` (command/skill) | Runs state capture + **dynamic human reflection** via the `question` tool + writes `narrative.md` + commits gnosis | Does **NOT** update docs, run lint/tests, or general hygiene |
| **"Prepare for compaction"** (natural language) | **Orchestration**: runs `/gnosis-lock` **AND** updates docs (`docs/`, `README`), runs `make lint` + `make test`, commits everything clean | — |
| `/compact` (bare, standalone line) | Triggers context compaction; `gnosis-leash.js` injects your narrative + INDEX rules | Takes **NO arguments** — text after `/compact` turns it into a normal prompt |
| Auto-compaction (context overflow) | Model-only summary | Highest data-loss risk — human gnosis not captured |

### 1.2 `/compact` syntax rule (hard fact, tested 2026-09-10)

- `/compact` **must be typed alone on its own line**.
- Any extra text (`/compact my reason`) is treated as a **regular prompt**, NOT compaction.
- Different from Gemini CLI — do not port that habit here.

### 1.3 The gnosis-lock skill flow (what an agent should do)

When `/gnosis-lock` fires or the user asks to lock gnosis:

1. Run the ritual:
   `bash ~/Documents/Projects/omega-engine-alpha/scripts/compaction/pre_compaction_ritual.sh "$REASON"`
   (REASON defaults to "End of session")
2. Read `gnosis/identity/identity.json` → `current_session` (the SESSION_ID).
3. **Dynamic reflection** (the human aspect — non-negotiable):
   - Always: Decision, Pattern, Gnosis (3 core categories).
   - Additionally: generate as many session-specific questions as warranted (0–10+).
     Light session → few; architecture/release session → deep multi-question set.
   - Use the **`question` tool** (built-in) with `header`,`question`,`options`,
     `multiple` fields. Always offer a "type your own" escape.
4. Write answers into `gnosis/sessions/${SESSION_ID}_narrative.md` — replace the
   template TODOs under `## Session Summary`, `## Key Decisions`, `## Code Changes`,
   `## Gnosis Gained`, `## Next Session Priorities`.
5. Commit the gnosis record:
   `git -C ~/Documents/Projects/omega-engine-alpha add gnosis/`
   `git -C ~/Documents/Projects/omega-engine-alpha commit -m "gnosis: session ${SESSION_ID} locked (${REASON})"`
6. Confirm to the user: "🔱 Gnosis locked to disk. Ready to run /compact."

### 1.4 The "prepare for compaction" orchestration checklist

When the user phrases it as a session-close instruction (NOT the bare command):

- [ ] `/gnosis-lock` capture + reflection (see §1.3)
- [ ] Update documentation: `docs/` + `README.md` + `SYSTEM_GUIDE.md` as relevant
- [ ] `make lint` green (anyio purity, no bare exceptions, no torch)
- [ ] `make test` green (or `python3 -m unittest discover -s tests`)
- [ ] Commit all work with descriptive message
- [ ] Confirm: "🔱 Gnosis locked, docs updated, gates green. Safe to /compact."

---

## 2. Gnosis-Leash Plugin (the "unseen puppeteer hand")

### 2.1 What it does (automatically, in the background)
- `~/.config/opencode/plugins/gnosis-leash.js`
- Wires: `session.created`, `session.idle`, `session.compacted` events → gnosis timeline
- On `/compact`: injects WanderGround INDEX rules **+ your captured narrative** into
  the compaction prompt via `experimental.session.compacting`
- Appends WanderGround operating rules to every session system prompt via
  `experimental.chat.system.transform`
- Logs to `~/.config/opencode/plugins/state/gnosis-events.jsonl` (and errors to
  `gnosis-errors.jsonl`)

### 2.2 Watchdog
```bash
make gnosis-leash-status        # exit 0 = healthy, 1 = degraded, 2 = FAIL
```
Checks: plugin source + hooks, timeline freshness, event-kind coverage, error log,
INDEX.md payload, skill+command registration.

### 2.3 Why agents should care
Because the narrative you write in Step 1.3 is **read by the plugin and injected
into the compaction summary**. A populated narrative = your exact insight survives.
An empty/template narrative = the model summarizes alone.

---

## 3. WanderGround & Knowledge Capture

### 3.1 Layout (`~/WanderGround/`, own git repo)
- `inbox/` → raw sparks via `wander -d <domain> "thought"`
- `archive/` → ingested notes moved here
- `domains/` (01_local_ai … 05_video_games)
- `dossiers/` → curated synthesis per domain (template in `dossiers/_template_dossier.md`)
- `mempalace/` → MemPalace palace (sqlite_exact + minilm), 62+ drawers
- `spatial/knowledge_atlas.db` → sqlite-vec 768-dim embeddings + 3D projection
- `site/` → MkDocs encyclopedia (wiki-sync via `make wiki-sync`)

### 3.2 Commands
```bash
wander -d consciousness "new spark..."    # capture (auto-triggers curator)
make -C ~/WanderGround status            # current atlas/domain state
make -C ~/WanderGround search q="..."    # search the atlas
make -C ~/WanderGround 3d-serve          # offline Three.js constellation viewer :8088
```

### 3.3 Background curator
- systemd user timer `wander-curator.timer` (every 30 min) → ingest, embed, UMAP, wiki
- Linger enabled — survives logout (see docs/HARDWARE.md / SYSTEM_GUIDE)

### 3.4 MemPalace MCP (in OpenCode)
- MCP server `mempalace` (type: local) exposes `palace_query`, `palace_exec`, etc.
- Palace path: `/home/xnai/WanderGround/mempalace`

---

## 4. OpenCode Zen / Model guidance

- Local inference is CPU-only (i7-13620H). NO local model for deep/long synthesis.
- Use OpenCode Zen cloud models (Big Pickle 1M verified, Nemotron 3 Ultra, MiMo V2.5,
  Muse Spark) for deep synthesis/long content.
- **Privacy tier (hard rule)**: Free Zen tiers collect prompt data
  (`big-pickle` free period, `mimo-v2.5-free`, `nemotron-*-free`,
  `muse-spark-*-contributor-free`, `ling-3.0-flash-fin-free`).
  Private explorations NEVER cross free tiers. Paid = zero-retention
  (`muse-spark-1.3`, `minimax-m3`, `glm-5.3-flash`, ...).
- max 1M context Big Pickle limit configured in `opencode.json`.

---

## 5. Code-quality gates (absolute standards)

| Gate | Where | Rule |
|---|---|---|
| anyio purity | `make lint` | NO bare `asyncio`/`trio` imports in first-party scripts |
| exceptions | `make lint` | NO bare `except:` / `except Exception: pass` — typed, logged or re-raise |
| torch ban | `make lint` | NO first-party `torch`/`torchvision` imports (CPU-only) |
| secrets | `make test` | No literal credentials in tracked files |
| docs | `make docs` | README + doc links valid |

Full spec: `docs/CODE_QUALITY.md`. Enforce before committing.

---

## 6. Architecture cheat-sheet

- Project: `/home/xnai/Documents/Projects/omega-engine-alpha` (make-driven)
- Docs: `docs/` — HARDWARE, SYSTEM_GUIDE, CODE_QUALITY, GNOSIS_USAGE,
  WANDERGROUND_SPEC, GETTING_STARTED, ARCHITECTURE, DEVELOPER_GUIDE,
  PLUGIN_DEVELOPMENT, AGENT_RUNBOOK (this file)
- Evolution log: `scripts/compaction/evolution_log.py` (log/stats/timeline/export)
- Sessions: `gnosis/sessions/` (manifest + git/system/config/mcp/narrative/evolution)
- Identity: `gnosis/identity/identity.json`
- Plugins: `~/.config/opencode/plugins/` (gnosis-leash.js)
- Skills: `~/.config/opencode/skills/gnosis-lock/SKILL.md`
- Commands: `~/.config/opencode/commands/gnosis-lock.md`
- Connected MCP: omega-hub (remote :8016), searxng (:8018), websearch (Exa),
  context7, grep_app, mempalace (local)

---

## 7. For agents running in sub-projects (WanderGround, future)

Same global rules apply. If `wander`/`mempalace` are referenced, they live in
`~/WanderGround/.venv/bin/` and `~/.local/bin/`. Keep anything private out of free
Zen tiers. Prefer the same CODE_QUALITY §1–5 standards for new Python code.

---

## 8. Source of truth ladder

1. `docs/AGENT_RUNBOOK.md` (this file) — quick operational awareness
2. `docs/GNOSIS_USAGE.md` — protocol deep-dive & exact command reference
3. `docs/SYSTEM_GUIDE.md` — the living machine/decision record
4. `docs/HARDWARE.md` — canonical hardware spec
5. `docs/CODE_QUALITY.md` — invariants & how to enforce
6. `docs/WANDERGROUND_SPEC.md` — exploration-node architecture & research corrections