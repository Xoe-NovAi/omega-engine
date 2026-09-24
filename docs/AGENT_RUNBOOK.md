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
make test                        # current regression suite (88 tests at 2026-09-24 audit)
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
  - the watchdog prints `LEASH TAUT (in-flight)` and exits **0** (healthy
    advisory note) if captured within the 24-hour TTL; it exits **1** (degraded)
    only if stale (>24h without reflection) or if a compaction ran without a
    human narrative;
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

### 1.4 The "prepare for compaction" Fallback/Recovery Procedure

**Primary mode is Semantic Write-Through (continuous, no ceremony).** The "prepare for compaction" orchestration is now a **fallback/recovery procedure** used only when:
- A compaction ran without a populated narrative (Gnosis incident)
- Context was evicted unexpectedly and the active-work pointer was lost
- Model swap or adapter restart requires manual state reconciliation
- The user explicitly requests a full session-close audit

When invoked as a session-close instruction (NOT the bare command):

- [ ] `/gnosis-lock` capture + reflection (see §1.3) — run only if a semantic
      boundary was crossed without a prior write-through
- [ ] Update documentation: `docs/` + `README.md` + `SYSTEM_GUIDE.md` as relevant
      — **docs are part of the artifact, not an afterthought**
- [ ] `make lint` green (anyio purity, no bare exceptions, no torch)
- [ ] `make test` green (or `python3 -m unittest discover -s tests`)
- [ ] Commit all work with descriptive message
- [ ] Confirm: "🔱 Gnosis locked, docs updated, gates green. Safe to /compact."

**The full loop is now the exception, not the rule.** Primary workflow:
`Observe → reason in context → classify durable state → write through → continue.`
Compaction becomes ordinary cache eviction. `gnosis-lock` and `/compact` are
fallback/recovery only.

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

## 3. Semantic Write-Through & Platform-Independent Continuity

**The hosted context window is a volatile CPU register. SQLite continuity state is the durable authority; MemPalace is a one-way searchable projection.** Compaction is cache eviction, not a ceremonial crisis.

> **Current implementation status (2026-09-23):** semantic write-through is the
> normative target architecture, not yet a live end-to-end runtime path. The
> portable file kernel and SQLite reference adapter are implemented and tested;
> the SQLite production runtime decision, live MemPalace MCP injection, custom
> CLI recovery, and WAD loader reconciliation remain open gates.

### 3.1 The Register / RAM / Disk Model

| Layer | Role | Technology | Volatility |
|-------|------|------------|------------|
| **Context (Register)** | Immediate computation | OpenCode context window | Lossy, 4K summary bottleneck |
| **SQLite Continuity Store (RAM/Disk)** | Authoritative state and event log | Local SQLite `StateStore`/`EventBus` | Durable; production runtime-gated |
| **MemPalace Projection** | Searchable knowledge surface | MCP drawer sink | Rebuildable; never the write authority |
| **Artifacts / Well (Disk)** | Canonical records | JSONL, patches, gnosis narrative | Immutable |

### 3.2 Operational Doctrine

1. **Semantic write-through is mandatory.** After every decision, discovery, task transition, or completed batch, persist state to the local SQLite continuity authority before continuing. Project to MemPalace only after the SQLite commit succeeds.
2. **Compaction is ordinary cache eviction.** No ceremony. `gnosis-lock` and `/compact` are fallback/recovery only.
3. **The active-work pointer lives in SQLite.** MemPalace is a one-way searchable projection and is not the recovery source of truth.
4. **Model swap = register swap.** Swapping models (Gemini ↔ Space Bunny ↔ Big Pickle) changes provenance, not entity identity; recovery reads the SQLite event/state history.
5. **Chaos recovery is the acceptance test.** Kill the model, discard context, restart via a different adapter, and resume from WAD + SQLite continuity state. The entity must recover mission, todos, decisions, and identity; MemPalace projection may be rebuilt afterward.

### 3.3 Agent Protocol (replaces "prepare for compaction")

```
Observe → reason in context → classify durable state → write through → continue
```

The "prepare for compaction" orchestration (§1.4) is now a **fallback/recovery procedure** used only when semantic write-through was missed or a Gnosis incident occurred.

---

### 3.4 Layout (`~/WanderGround/`, own git repo)
- `inbox/` → raw sparks via `wander -d <domain> "thought"`
- `archive/` → ingested notes moved here
- `domains/` (01_local_ai … 05_video_games)
- `dossiers/` → curated synthesis per domain (template in `dossiers/_template_dossier.md`)
- `mempalace/` → MemPalace `3.10.0` palace (`sqlite_exact`; 5,047 document
  rows, all currently 384-D, measured 2026-09-23)
- `spatial/knowledge_atlas.db` → target sqlite-vec atlas with Qwen3 768-D
  embeddings + 3D projection; currently absent on Node 1
- `site/` → MkDocs encyclopedia (wiki-sync via `make wiki-sync`)

### 3.5 Commands
```bash
wander -d consciousness "new spark..."    # capture (auto-triggers curator)
make -C ~/WanderGround status            # current atlas/domain state
make -C ~/WanderGround search q="..."    # search the atlas
make -C ~/WanderGround 3d-serve          # target offline Three.js constellation viewer :8088 (not currently deployed)
```

### 3.6 Background curator
- systemd user timer `wander-curator.timer` (every 30 min) → ingest, embed, UMAP, wiki
- Linger enabled — survives logout (see docs/HARDWARE.md / SYSTEM_GUIDE)

### 3.7 MemPalace MCP (in OpenCode)
- MCP server `mempalace` (type: local) exposes the live MemPalace tool surface;
  current operations use names such as `mempalace_search` and
  `mempalace_add_drawer`. Do not assume the historical `palace_query` name.
- Palace path: `/home/xnai/WanderGround/mempalace`
- The continuity adapter reaches this boundary through an injected
  `McpDrawerSink`; it never mutates the palace SQLite database directly.

---

## 4. OpenCode hosted-free model foundation

- **Canonical guide**: `docs/OPENCODE_FOUNDATION.md`.
- `big-pickle`, `space-bunny-free`, and other stealth aliases are dynamic
  endpoints. Their underlying checkpoints and limits may change in place and
  differ by node/time. Never hardcode their context, output, modality, or
  identity; use the alias ID and refresh the live registry.
- Big Pickle is always a free stealth alias despite lacking a `-free` suffix.
  Space Bunny is an anonymous free alias; it is **not** confirmed to be
  DeepSeek V4.1 Flash.
- Google free API models include Gemini 3.8/3.7/3.6/3.5 Flash and Gemini 3.5
  Flash-Lite. Prefer 3.8 for current public research; use 3.5 Flash-Lite for
  high-volume work. Free Google API data may be used to improve Google products.
- **Privacy rule**: Space Bunny is currently described as a hosted free
  zero-retention route, but the global policy is conservative: private material
  uses paid zero-retention models only. Big Pickle, MiMo, Ling, NVIDIA trial,
  and Muse contributor free tiers have explicit training/retention caveats.
  Free routes remain for public/non-sensitive work until policy is revalidated.
- Local inference remains CPU-only and is deferred from this hosted foundation.
- Drift detection before model claims: `opencode models <provider> --verbose --refresh`.

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
- Current suite count is discovered by `make test`; the 2026-09-23 audit
   observed 88 passing tests. Lint and documentation gates are green.

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

### 5.4 Frontier Gnosis & Epistemic Principles (Hard-Won Invariants)
- **1. Intent is the Contract**: Code comments, docstrings, and architectural
  specifications define the normative system contract. If an automated
  watchdog or test contradicts stated intent, the test/watchdog is the defect—
  not the intent. Reframe from *"what is the code doing?"* to *"what SHOULD
  the system do?"* (Well record `013c6037`).
- **2. Invariants Over Transient States**: Test state consistency across
  transitions (e.g., `reflection_status == "reflected" <=> ready_for_compaction == true`),
  never assert absolute terminal readiness on an active, in-flight, mid-pipeline
  session pack (Well record `a254a505`).
- **3. Multi-Model Verification Over Authority**: In a multi-model harness,
  models will propose conflicting theories (e.g. ACL drops, package managers,
  file ownership). Never accept confident assertions from any model without
  empirical verification: probe the port, parse the configuration with
  deterministic scripts, and consult canonical specs (`HARDWARE.md`).
- **4. The Tailscale ACL Replacement Trap**: Custom Tailscale policies replace
  default rules rather than merging. Saving a tag-only policy while nodes are
  untagged instantly severs all mesh communication. Always execute Phase A
  (preserving the allow-all rule `src:["*"] dst:["*:*"]`; never
  `autogroup:member` in `dst`), tag both nodes, and only then enforce
  Phase B lockdown.
- **5. The Network SQLite WAL Breakdown**: SQLite WAL mode requires POSIX shared
  memory (`-shm`) across processes on the *same kernel*. Over network filesystems
  (NFS/SMB), locks silently fail. Never run WAL mode on `/mnt/node-drive`.

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
- Connected MCP (verified 2026-09-18, all green): mempalace (local),
  parallel-search (local via `scripts/parallel_bridge.py`), firecrawl (remote),
  context7 (remote), grep_app (remote). omega-hub: **Omega Core Hub v1.28.1
  HEALTHY on Node 0 :8016** (live handshake + 93 tools incl. `task_registry_*`
  verified 2026-09-18) but NOT wired on Node 1 — absent from all config
  layers/backups (was TUI-visible historically; removal predates the backup
  window; wiring deferred to Node 0 strategic window). searxng (:8018) DOWN
  (connection refused 2026-09-18) — Node 0 to (re)start.

---

## 6.5. CPU Performance Tuning (i7-13620H, intel_pstate + HWP)

> The commands in this section are a deliberate performance-mode benchmark
> procedure, not the current desktop state. Current live state (2026-09-23):
> governor `powersave`, EPP `balance_performance`, power profile `balanced`,
> kernel command line `intel_pstate=performance`.

### The Three-Layer Problem
| Layer | Component | Default | Fix |
|-------|-----------|---------|-----|
| 1 | Kernel (`intel_pstate` active + HWP) | `powersave` pseudo-governor | `echo performance > scaling_governor` |
| 2 | Daemon (`power-profiles-daemon`) | Platform profile set, but **does not force pseudo-governor** | `powerprofilesctl set performance` |
| 3 | GUI (GNOME power menu) | Synced to daemon via `powerprofilesctl` | Click "Performance" → runs daemon |

### Immediate Fix (run once)
```bash
# 1. Set governor to performance (immediate)
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# 2. Set power profile (persists via daemon)
powerprofilesctl set performance

# 3. Kernel cmdline fallback (highest priority, survives reboot)
sudo sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="/GRUB_CMDLINE_LINUX_DEFAULT="intel_pstate=performance /' /etc/default/grub
sudo update-grub
```

### Verification (performance-mode target)
```bash
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor   # target: performance
cat /sys/devices/system/cpu/cpu*/cpufreq/energy_performance_preference  # target: performance
powerprofilesctl  # target: * performance:
grep intel_pstate /proc/cmdline  # → intel_pstate=performance (after reboot)
```

### Expected Results (controlled performance-mode runs)
| Metric | `powersave` governor | `performance` governor |
|--------|---------------------|------------------------|
| Avg MHz (sustained load) | 2023-2758 MHz | **3600+ MHz** |
| Peak Temp | 92°C brief | 81-82°C stabilized |
| Throttle <3000 MHz | Never | Never |

### BIOS Settings (ExpertBook P1503CVA)
| Setting | Location | Value |
|---------|----------|-------|
| Fan Profile | Advanced → Fan Control | **Performance** |
| Turbo Boost | Advanced → CPU Configuration | **Enabled** |
| Intel Speed Shift (HWP) | Advanced → CPU Configuration | **Enabled** |
| SpeedStep | Advanced → CPU Configuration | **Enabled** |
| C-States | Advanced → CPU Power Management | **Enabled** |
| AVX Offset | Advanced → CPU Configuration | **0** |

**NOT in BIOS** (firmware-locked): PL1, PL2, Tau, IccMax — managed by firmware/thermald.

### Why GUI Setting Was Ignored
1. GUI → `powerprofilesctl` → daemon sets platform profile (ACPI hint)
2. `intel_pstate` (HWP active) reads hint but **chooses own pseudo-governor** based on kernel default (`powersave`)
3. Result: Platform=Performance, Governor=powersave → frequency scales with load

### Persistence
| Method | Survives Reboot | Priority |
|--------|-----------------|----------|
| `powerprofilesctl set performance` | ✅ (daemon enabled) | Medium |
| `intel_pstate=performance` kernel param | ✅ (GRUB) | **Highest** |
| Sysfs write | ❌ | Immediate only |

**Full guide**: `docs/CPU_PERFORMANCE_TUNING_GUIDE.md`

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
7. `docs/OPENCODE_FOUNDATION.md` — hosted-free aliases, dynamic-model safety, schema-current agents, and v1 compaction

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
     inference (zero token cost, dynamic hosted context, CPU-constrained pipeline).
   - **Odysseus**: SCHEDULED FOR A FUTURE DATE (after P3) — too large for now.
   - **God's Eye View + Gods Eye**: TOY — WAITING (user: "just for me to play
     with"; not on the work track).
   - **agentmemory**: REJECTED — does NOT beat MemPalace on retrieval
     (95.2% vs 96.6% R@5 LongMemEval-S); MemPalace already integrated.
   All verdicts documented in ROADMAP + WanderGround dossiers (to be created).
5. **P3 — Synthesis + Federation Close-out** — **ACTIVE**:
   - P3.1 Architecture synthesis (folded P0-P2 decisions into `ARCHITECTURE.md`).
   - P3.2 Node 0 federation:
     - Hostname schema ratified (`xnai-n1-asus`, `xnai-n0-hp`).
     - Pure NFSv4.2 server live on Node 1 bound strictly to `100.89.40.17:2049` (`all_squash` -> `1000:1000`).
     - Two-phase ACL migration policy ratified (Phase A allow-all rule -> Phase B tag lockdown; NFS+MCP+SSH verified live 2026-09-21).
     - Node 0 Action Briefing (`NODE0_ACTION_BRIEFING_NFS_L2.md`) delivered on USB.
     - **Next physical action**: Mount `/mnt/node-drive` on Node 0 via USB briefing and enable `tailscale set --ssh`.
   - P3.3 Content runway (Obsidian, Godot/KQ5, Open WebUI, `make publish-bastion`).
   - P3.3a Model research cards — registry live; Nex-N2.5-Pro is a candidate.

Old open items folded into ROADMAP: sudo revert (standing infra — outside
ROADMAP, see `~/.config/opencode/AGENTS.md`), content runway (P3.3).
---

## 10. Hardened Deployment Procedures (v3.1 — Sonnet 5 Review Hardened)

### 10.1 The Hardening Philosophy
Every failure in the setup process is converted into a hardening measure. This section documents the battle-tested deployment procedures that survived real-world execution **and Sonnet 5 review**.

### 10.2 Pre-Deployment Validation (Non-Negotiable)
```bash
# 1. OpenCode version (must be 1.18+)
opencode --version | grep -q '1\.1[89]'

# 2. MCP inventory — OpenCode has no `mcp call` subcommand
opencode mcp list
opencode run "Use mempalace_search for a test query"

# 3. Tailscale mesh connectivity (Node 1 checks Peer[] for omega-hub)
tailscale status --json | jq -r '.Peer[] | .DNSName' | grep -q 'omega-hub.tail51f14a.ts.net'

# 4. Parallel.ai endpoint (accept 405 as "reachable")
curl -s -o /dev/null -w '%{http_code}' https://search.parallel.ai/mcp | grep -E -q '200|401|405'

# 5. Backup existing config — guard for first deploy
BACKUP_SUFFIX=$(date +%Y%m%d_%H%M%S)
[ -f ~/.config/opencode/opencode.json ] && cp ~/.config/opencode/opencode.json ~/.config/opencode/opencode.json.bak.${BACKUP_SUFFIX} || true

# 6. Venv dependency lock
if ! /home/xnai/WanderGround/.venv/bin/python3 -c "import anyio; import inotify" 2>/dev/null; then
    /home/xnai/WanderGround/.venv/bin/pip install anyio inotify-simple --quiet || exit 1
fi

# 7. System dependency: inotify-tools
sudo apt-get update && sudo apt-get install -y inotify-tools || exit 1
```

### 10.3 Master Configuration (schema-current principles)

The live `https://opencode.ai/config.json` schema is authoritative. Do not
copy historical templates that contain removed or pass-through-only fields.

Current rules:

- Agent prompt file: `"prompt": "{file:~/.config/opencode/prompts/<agent>.md}"`.
- `inherit_context`, `allow_background_execution`, and `system_prompt` are not
  current top-level agent controls; unknown fields become provider options.
- Task permission rules are last-match-wins: put `*: deny` **before** explicit
  allows.
- `subagent_depth: 1` is the safe default for primary-to-specialist work.
- Do not manually duplicate the live model catalog or hardcode stealth-alias
  limits. See `docs/OPENCODE_FOUNDATION.md`.
- Current v1 compaction is adaptive. Omit `reserved`; it derives from live model
  input/output metadata. Hardcode only intentional policy such as
  `compaction: { "auto": true, "prune": true }`. In future V2 config, omit
  `buffer`; OpenCode applies its default against live model metadata.
- MCP config keys are top-level server names, not an `mcp.servers` wrapper.
  Local servers use `command: [absolute executable, ...args]`; remote servers use
  `type`, `url`, and `headers`. Unsupported keys such as remote `max_retries`
  must not be carried in active templates.

Validate after every active config change:

```bash
opencode debug config  # sanitize output; it resolves env substitutions
opencode models opencode --verbose --refresh
```

### 10.4 Venv Path Resolution (Hardened)
```bash
# WRONG (old hardcoded path):
/home/xnai/.local/share/ov/env/bin/python3

# CORRECT (actual venv location):
/home/xnai/WanderGround/.venv/bin/python3
/home/xnai/WanderGround/.venv/bin/pip
```

### 10.5 Systemd Service (Hardened Format — With Circuit Breaker)
```ini
# ~/.config/systemd/user/wanderground-embed.service
[Unit]
Description=WanderGround Async Embedding Daemon (anyio Hardened)
After=default.target

[Service]
Type=simple
WorkingDirectory=%h/WanderGround/daemon
ExecStart=%h/WanderGround/.venv/bin/python3 %h/WanderGround/daemon/embed_daemon.py
Restart=always
RestartSec=5
StartLimitIntervalSec=60
StartLimitBurst=3

[Install]
WantedBy=default.target
```

**CRITICAL FORMAT RULES:**
- Use newlines, NOT semicolons: `Restart=always` + newline + `RestartSec=5`
- `[Install]` on its own line, `WantedBy=default.target` on next line
- `ExecStart` points to correct venv: `%h/WanderGround/.venv/bin/python3`
- **Circuit breaker**: `StartLimitIntervalSec=60` + `StartLimitBurst=3` prevents infinite crash-loops

### 10.6 anyio 4.x API Compliance
```python
# WRONG (anyio 4.x removed this parameter):
await anyio.to_process.run_sync(fn, stream, abandon_on_cancel=True)

# CORRECT (to_thread for thread workers, not to_process):
await anyio.to_thread.run_sync(fn, stream)
```

### 10.6 Sidecar Daemon (Hardened — to_thread Fixed)
```python
# CURRENT GENERATION (2026-09-18): queue.SimpleQueue + poll — NO anyio.Event
#
# Why not Event.set() from the inotify thread?
#  - Direct set() from a worker thread sets the flag but CANNOT wake loop waiters
#    (misses call_soon_threadsafe scheduling) — sync worker stays stuck forever.
#  - from_thread.run_sync(set) fixes that, but a set() landing between wait()'s
#    flag check and waiter registration is SILENTLY LOST (flaky stuck worker,
#    reproduced ~1-in-6 in sandbox trials).
#
# Deterministic alternative used by scripts/embed_daemon.py:
pending_queue = queue.SimpleQueue()          # GIL-safe, cannot lose items
POLL_INTERVAL_SECONDS = 0.5
# inotify thread:
pending_queue.put(filename)                  # NO thread signaling at all
# sync worker (async task):
while True:
    files = []
    while True:
        try:
            files.append(pending_queue.get_nowait())
        except queue.Empty:
            break
    if not files:
        await anyio.sleep(POLL_INTERVAL_SECONDS)
        continue
    # cooldown + ONE mine+sync per batch (see scripts/embed_daemon.py)
```

### 10.7 Parallel.ai Endpoint Behavior
```bash
# Endpoint returns 405 (Method Not Allowed) for GET/HEAD
# This is EXPECTED - MCP endpoint expects POST
# Validation must accept 405:
curl -s -o /dev/null -w '%{http_code}' https://search.parallel.ai/mcp | grep -E -q '200|401|405'
```

### 10.8 Parallel-search Response Schema
```python
# Defensive parsing with fallback:
try:
    data = json.loads(search_payload) if isinstance(search_payload, str) else search_payload
    urls = data.get("canonical_urls", [])[:5]
except Exception:
    urls = []
```

### 10.9 MemPalace Palace Check
```bash
# Check for sqlite_exact.sqlite3 (NOT mempalace.yaml)
verify_step "MemPalace palace" "[ -f ~/WanderGround/mempalace/sqlite_exact.sqlite3 ]"
```

### 10.10 Complete Deployment Scripts
See `/home/xnai/deploy_node1.sh` and `/home/xnai/deploy_node0.sh` for complete atomic deployment scripts with all hardening applied (including Sonnet 5 fixes).

### 10.11 Sonnet 5 Review Fixes (v3.1 — All Critical Bugs Fixed)
The following critical bugs were identified by Sonnet 5 review and fixed in the deployed scripts:

| # | Component | Bug | Fix |
|---|-----------|-----|-----|
| 1 | **embed_daemon.py** (CRITICAL) | `to_process` used for inotify worker — MemoryObjectStream not picklable | Changed to `anyio.to_thread.run_sync()` |
| 2 | **Deploy scripts Phase 0** | `|| true` masked MemPalace verify failure | Removed `|| true` from command strings |
| 3 | **Node 0 Tailscale check** | Checked Self.DNSName instead of Peer[] | Fixed to check `.Peer[]` for `xnai-n1-asus` |
| 4 | **Node 1 opencode.json** | Duplicate `mempalace` key in config | Removed duplicate `mcp.mempalace` block |
| 5 | **Bashrc env vars** | Unconditional append duplicated on re-run | Marker guards (`# OMEGA_ENGINE_API_KEYS`) with `grep -q` |
| 6 | **Backup step** | Failed on first deploy (no existing config) | Guarded with `[ -f ... ] &&` |
| 7 | **library_web_search.py** | Bare `except: pass` swallowed signals | Changed to `except Exception:` |
| 8 | **library_web_search.py** | No domain fallback for unrecognized queries | Added `06_general` catch-all domain |
| 9 | **embed_daemon.py** (CRITICAL) | Sync worker never woke — `Event.set()` from thread can't wake loop waiters; `from_thread.run_sync(set)` still has lost-wakeup race | Rewrote to `queue.SimpleQueue` + 0.5s poll; verified end-to-end 2026-09-18 |
| 10 | **Systemd service** | No circuit breaker for crash-loops | Added `StartLimitIntervalSec=60`, `StartLimitBurst=3` |
| 11 | **API Keys** | Date-derived placeholders documented as real | Added explicit warnings: must replace with real keys |

---

## 11. Quick Reference: Hardened Commands

**Credential boundary:** live API credentials are stored outside the repository
in the canonical runtime locations. Never print, copy, or commit them; verify
authentication with the configured MCP client rather than placeholder probes.

```bash
# Deploy Node 1
chmod +x /home/xnai/deploy_node1.sh && /home/xnai/deploy_node1.sh

# Deploy Node 0 (via USB or SSH)
scp /home/xnai/deploy_node0.sh xnai@100.123.51.67:~/ && ssh xnai@100.123.51.67 'chmod +x deploy_node0.sh && ./deploy_node0.sh'

# Validate MCP servers
opencode mcp list
opencode run "Use parallel-search web_search for a test query"
opencode run "Use mempalace_search for a test query"

# Verify daemon
systemctl --user status wanderground-embed.service

# Rollback
cp ~/.config/opencode/opencode.json.bak.* ~/.config/opencode/opencode.json
systemctl --user stop wanderground-embed.service && systemctl --user disable wanderground-embed.service
rm ~/.config/systemd/user/wanderground-embed.service
systemctl --user daemon-reload
# Remove API key block (between markers)
sed -i '/# OMEGA_ENGINE_API_KEYS/,/# END OMEGA_ENGINE_API_KEYS/d' ~/.bashrc
source ~/.bashrc
```
