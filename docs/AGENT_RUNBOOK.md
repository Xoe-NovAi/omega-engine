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

### 1.5 Entity & phase attribution (who locked what)

Every gnosis-lock record (manifest, narrative, git_state, evolution event)
carries `entity`, `channel`, and `phase` fields. Pass them via env:

```bash
ENTITY=build CHANNEL=opencode PHASE=phase-3 make gnosis-lock REASON="..."
```

- `identity.json` keeps a per-entity map (`entities.<entity>.session_count`,
  `last_session`, `last_phase`) so each agent's continuity is a query over one
  flat store — no folder-per-agent needed.
- CLI locks (`make gnosis-lock`) **auto-fill** the narrative's Session Summary +
  Code Changes from captured git/evolution state (Step 6.5), so even a CLI-only
  session is a useful continuity record. The human-reflection fields
  (Decisions/Gnosis) remain TODO until the skill runs.

### 1.6 The Pack lifecycle (state machine — NO silent states)

A gnosis-lock creates a **pack** (all artifacts + narrative + manifest) that
moves through an explicit lifecycle. The blank `TODO` narrative is NOT garbage
— it is a *signal* that the pack is captured but not yet ingested:

```
CAPTURED ──(skill answers reflection questions)──▶ REFLECTED ──(plugin injects)──▶ COMPACTED
  (ritual ran,          every artifact + narrative   (the leash verifies it landed
   TODO by intent)      written, manifest flipped)    in a /compact session)
```

- **`reflection_status`** in the manifest is the authoritative signal:
  `captured` | `reflected`.
- **`identity.pending_pack`** points at the current un-reflected pack — the
  **leash**. While it is set and the pack is not reflected:
  - the ritual **refuses** to create a new pack (`LEASH CHECK FAILED`),
    unless `FORCE_PACK=1` explicitly acknowledges the override;
  - the watchdog prints `LEASH TAUT` and exits degraded;
  - the pause ledger shows the pack as `captured`.
- Reflection (the skill) flips the manifest to `reflected`, stamps
  `reflected_at`, sets `ready_for_compaction = true`, and clears
  `pending_pack`. This is the ONLY valid path from captured → reflected.
  **Readiness contract**: captured = not-ready, reflected = ready — a pack is
  only `ready_for_compaction` once reflected (enforced by the congruence test).
- Visibility: `make gnosis-ledger` prints every pack's state, entity, phase,
  and capture/reflect timestamps in chronological order — no questions, only
  answers.

> The original bug — a second gnosis-lock stamping a new CAPTURED template over
> a populated narrative — is now impossible by default: the leash check blocks
> the second lock before any capture happens.

### 1.4 The "prepare for compaction" orchestration checklist

When the user phrases it as a session-close instruction (NOT the bare command):

- [ ] `/gnosis-lock` capture + reflection (see §1.3) — **run it even if a pack
      was already captured earlier in the session**; each new round of work
      deserves its own pack record
- [ ] Update documentation: `docs/` + `README.md` + `SYSTEM_GUIDE.md` as relevant
      — **docs are part of the artifact, not an afterthought; do them BEFORE
      committing**
- [ ] `make lint` green (anyio purity, no bare exceptions, no torch)
- [ ] `make test` green (or `python3 -m unittest discover -s tests`)
- [ ] Commit all work with descriptive message
- [ ] Confirm: "🔱 Gnosis locked, docs updated, gates green. Safe to /compact."

**The full loop, always.** Order: capture → reflect → docs → lint → test →
commit. Skipping any step breaks the whole. Discipline is enforced, not assumed
(by the checklist, the test suite, and the user).

---

## 2. Gnosis-Leash Plugin (the "unseen puppeteer hand")

### 2.1 What it does (automatically, in the background)
- `~/.config/opencode/plugins/gnosis-leash.js`
- Wires: `session.created`, `session.idle`, `session.compacted` events → gnosis timeline
- On `/compact`: injects WanderGround INDEX rules **+ The Well active rules (top-N by recency + domain)** **+ your captured narrative** into
  the compaction prompt via `experimental.session.compacting`
- Appends WanderGround operating rules + The Well active rules (top-N, harness/local_ai domains) to every session system prompt via
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

### 2.4 NO SILENT FAILURES contract
A compaction that runs with **no populated human narrative** is a first-class
incident — it is never quietly ignored:

- The plugin injects `⚠️ GNOSIS-LOCK INCIDENT: NO HUMAN NARRATIVE AVAILABLE`
  into the compaction context, so the model cannot unknowingly produce a
  lower-fidelity summary.
- A structured diagnostic (`compaction_without_narrative`) is written to
  `gnosis-errors.jsonl`.
- The timeline event records `narrative_source` + `narrative_reason` (provenance).
- `make gnosis-leash-status` **exits 1 (degraded)** while the last compacting
  event has `has_narrative: false`, printing the reason. The leash returns to
  healthy after the next compaction that injects a narrative.

Fallback chain (in order): current session → most recent *populated* session on
disk. This is why a second ritual mid-session cannot shadow a good narrative:
the plugin deliberately ignores unedited `TODO: Fill in` templates in favor of
the last real reflection.

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

### 5.1 Ponytail (lazy senior dev — P0.4, **LIVE**)
- Checkout: `~/Vanguard/ponytail` (registered as absolute-path plugin in
  `~/.config/opencode/opencode.json`). Live after the opencode restart.
- The ruleset (inject-on-every-turn, modes `lite|full|ultra|off`) composes
  with the gnosis-leash system-transform: BOTH append to the system prompt,
  neither overwrites. `/ponytail off` silences it.
- Commands: `/ponytail`, `/ponytail-review`, `/ponytail-audit`,
  `/ponytail-debt`, `/ponytail-gain`, `/ponytail-help`.
- Watchdog note: `make gnosis-leash-status` stays green with the
  plugin active.

### 5.2 The Well (corrections/tuning corpus — P1, **LIVE**)
- **Full-depth reference**: `docs/WELL_SYSTEM.md` (schema, validation,
  injection mechanics, lifecycle, CLI, closed-loop).
- Storage: `gnosis/well/well.jsonl` (append-only) + `gnosis/well/WISDOM.md` (human view).
- Schema: `record_id`, `ts`, `kind` (correction|preference|tip|anti_pattern|insight|dream),
  `source_pack`, `domain`, `trigger`, `rule`, `rationale`, `tags`, `status` (active|superseded),
  `superseded_by`.
- Lifecycle: `CAPTURED → ACTIVE → SUPERSEDED` (mirrors pack lifecycle).
- **Writers**: Skill Step 4c (during `/gnosis-lock` reflection, agent extracts
  corrections → `make well-add`), Prepare-for-compaction "Well sweep",
  CLI `make well-add`, immediate capture of sharp lessons (see GNOSIS-LEARN-001).
- **Readers**: gnosis-leash plugin injects top-6 (harness/local_ai) at session
  start + top-8 at compaction; `make well-export` → `WISDOM.md` + JSONL bundle.
- **Evolution**: `make well-supersede OLD=<id> NEW=<id>`; injection excludes
  superseded. **Injection filters by status+domain only — NOT by kind**
  (a `dream` in harness/local_ai IS injected; verified against plugin source
  2026-09-17).
- CLI: `make well-add|well-list|well-stats|well-supersede|well-export`.
- Tests: 7 `TestWellStorage` tests (JSONL validity, secret rejection,
  supersession chain, index parity, UTF-8 integrity, stats accuracy, Make targets).
- 43/43 total tests green, lint+docs clean.

### 5.3 OMER — Model Card Registry (P3.3a/b, **LIVE**)
- **What**: git-native model evaluation registry. A card is a **decision record**
  (verdict + promotion checklist), not a marketing summary.
- **Docs**: registry contract → `docs/models/README.md`; full design +
  M1–M6 milestones → `docs/OMER_FOUNDATION.md`.
- **Cards**: `docs/models/<provider>-<model>-<variant>.md` with required YAML
  frontmatter (v1.0) + `## Provider Claims`, `## Local Measurement`,
  `## Omega Verdict` sections.
- **When to create a card**: any model researched/trialled/deployed/rejected.
  New models are `candidate` until a real Omega task validates them.
- **Evidence labels (enforced, exact)**: `Provider claim`, `Community benchmark`,
  `Independent eval`, `Reproduced`, `Local measurement`.
- **Reproduction status (enforced, exact)**: `Indicative` → `Reported` →
  `Controlled` → `Verified` → `Independent`. Provider claims default to
  `Indicative`; only `Controlled`+ local measurements promote a card.
- **Validation**: `./scripts/omer validate docs/models` (wired into `make lint`).
  Validator is `scripts/validate_model_cards.py` (Pydantic v1.0 schema); hard
  P-core-trap guard rejects `allowed_cpus: 0,2,4,6,8,10`.
- **Rule**: never present provider benchmarks as independent validation; keep
  rejected/retired cards for future comparisons.

---

## 6. Architecture cheat-sheet

- Project: `/home/xnai/Documents/Projects/omega-engine-alpha` (make-driven)
- Docs: `docs/` — HARDWARE, SYSTEM_GUIDE, CODE_QUALITY, GNOSIS_USAGE,
  WANDERGROUND_SPEC, GETTING_STARTED, ARCHITECTURE, DEVELOPER_GUIDE,
  PLUGIN_DEVELOPMENT, AGENT_RUNBOOK (this file), and `docs/models/` (model cards)
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

---

## 9. Priority stack (next to seize)

> ⚠️ **Authoritative backlog moved**: this quick stack is a pointer. The full,
> ordered, phased roadmap with finish gates lives in
> **`docs/ROADMAP.md`** — the single source of truth. Any new idea/tool/quest
> is recorded there with a status BEFORE implementation (standing rule).

Quick orientation (current phase = **P3 Synthesis + Federation Close-out**):

1. **P0.1–P0.4** — ✅ **DONE**: mempalace smoke test, historical pack triage,
   watchdog green on next compact, **Ponytail install** (`DietrichGebert/ponytail`, MIT, LIVE).
2. **P1 — The Well** — ✅ **DONE**: `gnosis/well/well.jsonl` + `WISDOM.md`;
   writers (skill Step 4c + compaction sweep + `make well-add`); readers
   (plugin inject at session start + compaction); `make well-export` bundle.
3. **P1.5** — ✅ **DONE**: `docs/ROADMAP.md` backlog + `kind:dream` capture.
4. **P2 — Vanguard studies** — ✅ **DONE** (all evaluated, documented):
   - **Headroom**: REJECTED — well-built, but benefits don't apply to local
     inference (zero token cost, 1M context, CPU-constrained pipeline).
   - **Odysseus**: SCHEDULED FOR A FUTURE DATE (after P3) — too large for now.
   - **God's Eye View + Gods Eye**: TOY — WAITING (user: "just for me to play
     with"; not on the work track).
   - **agentmemory**: REJECTED — does NOT beat MemPalace on retrieval
     (95.2% vs 96.6% R@5 LongMemEval-S); MemPalace already integrated.
   All verdicts documented in ROADMAP + WanderGround dossiers (to be created).
5. **P3 — Synthesis + Federation Close-out** — **ACTIVE**:
   - P3.1 Architecture synthesis (fold all P0-P2 decisions into docs, de-duplicate).
   - P3.2 Node 0 federation (Tailscale, C6 comms-contract, publish gate).
   - P3.3 Content runway (Obsidian, Godot/KQ5, Open WebUI, `make publish-bastion`).
   - P3.3a Model research cards — registry live; Nex-N2.5-Pro is a candidate.

Old open items folded into ROADMAP: sudo revert (standing infra — outside
ROADMAP, see `~/.config/opencode/AGENTS.md`), content runway (P3.3).