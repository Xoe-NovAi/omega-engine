# 🗺️ Omega Engine — Node 1 Roadmap & Phased Timeline

> **Purpose**: The single ordered backlog for everything the Omega Engine is
> building. Every flood of ideas, every vanguard tool, every "remember when we
> parked this" landing here. If it isn't in this file, it isn't scheduled.
>
> **Owner**: Build agent (Node 1). **Update rule**: any new idea/tool/quest
> enters ROADMAP with a status **first**; implementation follows only after it
> is triaged here. This is the antidote to rabbit-hole whiplash.
>
> **Companion docs**: `docs/AGENT_RUNBOOK.md` (ops awareness), `docs/HARDWARE.md`
> (machine spec), `docs/WANDERGROUND_SPEC.md` (knowledge architecture).

---

## 0. How to read this roadmap

Every item has a **status**, a **why-Omega-cares** line, and a **finish gate**
(the definition of *temple-grade done* — not "that'll do"). Phases are ordered
by *closeness to completion*, not by excitement. We finish what we started
before we start what we dreamed.

Status vocabulary:

| Status | Meaning |
|---|---|
| `backlog` | Captured, not yet queued |
| `queued` | Scheduled, next up in its phase |
| `active` | Work in progress |
| `done` | Temple-grade finished (gate met) |
| `superseded` | Replaced by a better idea (linked) |
| `rejected` | Studied, decided against (rationale recorded) |

Current state at a glance:

| Phase | Name | State |
|---|---|---|
| P0 | Temple-grade pulse | ✅ done |
| P1 | **The Well** (corrections/tuning corpus) | ✅ done |
| P1.5 | Idea-flood management | ✅ done (ROADMAP itself = part of it) |
| P2 | The Vanguard studies | ✅ **done** (P2.1 Headroom rejected, P2.2 Odysseus scheduled future, P2.3-4 Gods Eyes toys, P2.5 agentmemory rejected) |
| P3 | Synthesis + federation close-out | active |

---

## P0 — Temple-grade pulse (finish the thread we started)

**Goal**: close every loose end in the gnosis/puppeteer/memory systems to a
clean, explicit, watchable state before layering new toys on top.

### P0.1 — mempalace MCP live smoke test
- **Why**: config was fixed to `type: local` but the socket was never re-smoked;
  an unverified bridge is a silent-failure risk in the exact class we just
  hardened against.
- **Done when**: `palace_query` returns a live result through the MCP server;
  documented in ROADMAP + system guide; a watchdog note covers it.
- **Status**: ✅ **DONE (2026-09-11)** — smoke test passed: `initialize` (MemPalace 3.9.0) →
  `tools/list` (42 tools) → `mempalace_search` returned 20 real results from 62
  drawers with full provenance. **Note**: the live tool is named `mempalace_search` —
  `palace_query` is stale (was the pre-3.x name); the same tool covers status,
  list, taxonomy, graph, diary, events, tasks, artifacts.

### P0.2 — Historical pack backlog triage
- **Why**: the Pause Ledger shows 22 `CAPTURED` packs, most from before the
  state machine existed. They must be explicitly `superseded` (test junk) or
  honestly `captured` (real un-ingested sessions) — no implicit states.
- **Done when**: every manifest in `gnosis/sessions/` has an explicit
  `reflection_status`; ledger rows all resolve; a migration script exists at
  `scripts/compaction/migrate_legacy_packs.py` (or the migration is recorded).
- **Status**: ✅ **DONE (2026-09-11)** — `scripts/compaction/migrate_legacy_packs.py`
  written + applied (`--apply`): 10 `superseded` (harness-test artifacts:
  fake ids + ritual self-verification reasons), 12 honestly `captured` (real
  un-ingested sessions with `triage_at` provenance), 3 already-explicit
  (`reflected`) untouched — the migrator never demotes an explicit state.
  `pause_ledger.py` learned to distinguish triaged captures (acknowledged) from
  loose ends (degraded) → **PAUSE LEDGER CLEAN**. 3 new tests
  (`TestLegacyPackMigration`): dry-run runs, no implicit states remain,
  reflected packs never demoted. 36/36 green.

### P0.3 — Watchdog green on next successful compact
- **Why**: the historical `has_narrative: false` compacting event keeps the
  watchdog degraded (correctly — it's a real incident) until a *successful*
  compact with the new plugin clears it. The next post-Phase-1 compaction
  should flip it green.
- **Done when**: a real `/compact` with narrative injection → `make gnosis-leash-status`
  exits 0.

### P0.4 — Ponytail install (first vanguard adoption)
- **Repo**: `DietrichGebert/ponytail` (MIT) — "the lazy senior dev" ruleset for
  OpenCode: `/ponytail-review` (diff over-engineering) + `/ponytail-audit`
  (repo bloat). ~54% less code, 100% safety kept.
- **Why**: directly attacks the cognitive-tax loop — stop over-checking, ship
  the minimum that holds; the codebase gets a second pair of sardonic eyes.
- **Steps**: clone to `~/Vanguard/ponytail/` (or `~/ollama-install/`-adjacent
  disk, NOT /tmp), review its hooks (two lifecycle hooks — hook-trust review),
  register in `~/.config/opencode/opencode.json`, verify coexistence with the
  gnosis-leash system-transform (both append context — must not fight).
- **Done when**: plugin loads, `/ponytail-help` responds, first `/ponytail-review`
  run on a real diff produces a delete-list, gnosis-leash watchdog still green.
- **Status**: ⏳ **PARTIAL (2026-09-11)** — cloned to `~/Vanguard/ponytail@356918e`
  (real disk); **hook-trust review PASSED** (the only two lifecycle hooks are
  `experimental.chat.system.transform` → append-only ruleset injection honoring
  `off` mode, and `command.execute.before` scoped to `/ponytail` mode writes;
  `config` registers commands + skills dir; no destructive/system hooks);
  registered in `opencode.json` (`plugin`: absolute-path `.mjs`); coexist
  verified statically (both transforms append to `output.system`, neither
  overwrites). **REMAINING (needs a session restart)**: live
  `/ponytail-help` + first `/ponytail-review` on a real diff + confirm
  watchdog still green with the plugin active.

---

## P1 — The Well (the signature feature)

**Goal**: a structured, queryable, self-aging corpus of **corrections, coding
tips, preferences, and anti-patterns** — the perpetually evolving training and
tuning set tuned to *your* unique insights. The feature that changes sessions
from "re-teach the agent every time" to "the agent already knows."

### P1.1 — The Well storage & schema
- **Storage**: `gnosis/well/well.jsonl` (append-only truth) + rendered
  `gnosis/well/WISDOM.md` (human view) — same jsonl+index pattern as the
  evolution log.
- **Record schema**: `record_id`, `ts`, `kind`
  (`correction|preference|tip|anti_pattern|insight|dream`), `source_pack`,
  `domain`, `trigger`, `rule`, `rationale`, `tags`, `status`
  (`active|superseded`), `superseded_by`.
- **Lifecycle**: `CAPTURED → ACTIVE → SUPERSEDED` (mirrors the pack lifecycle
  you designed).
- **Done when**: `make well-stats` shows counts by kind/status; `make well-list`
  renders; schema versioned; tests cover the four invariants (jsonl valid,
  no secrets, index matches, supersession links resolve).
- **Status**: ✅ **DONE (2026-09-11)** — `scripts/well_storage.py` implements
  schema + validation + CRUD + render; `make well-add|well-list|well-stats|
  well-supersede|well-export` targets wired; 7 `TestWellStorage` tests
  enforce: valid JSONL, secret rejection, supersession chain resolves,
  index/JSONL parity, UTF-8/line integrity, stats accuracy, Makefile targets.
  43/43 total tests green, lint+docs clean.

### P1.2 — The Well writers
- **Skill Step 4c**: during `/gnosis-lock` reflection, the agent extracts any
  corrections/tips from the session into the Well (plus the session's human
  answers).
- **Prepare-for-compaction "Well sweep"**: the orchestration scans the session
  for corrections and records them before compacting.
- **CLI**: `make well-add kind=correction "rule"` (+ `--domain`, `--tags`,
  `--source`, `--rationale`).
- **Done when**: a real session's corrections land in the Well and are
  attributable to their source pack.
- **Status**: ✅ **DONE (2026-09-11)** — `SKILL.md` Step 4c added (agent extracts
  actionable rules from the narrative + runs `make well-add` for each with
  `PACK="${SESSION_ID}"`); CLI targets exist and tested. Next session's
  `/gnosis-lock` will exercise the full flow.

### P1.3 — The Well readers (injection)
- **Session start**: plugin injects top-N active rules (ranked by recency +
  tags matching the project/domain).
- **Compaction**: same injection, so the summary carries the corrected rules
  forward.
- **Tuning export**: `make well-export` → Markdown/JSONL bundle usable as extra
  system context for any Zen model (and, eventually, a fine-tune seed).
- **Done when**: next-session system prompt demonstrably contains Well rules;
  compact summary preserves them.
- **Status**: ✅ **DONE (2026-09-11)** — `gnosis-leash.js` updated:
  `experimental.chat.system.transform` injects top-6 Well records (harness,
  local_ai domains) at session start; `experimental.session.compacting`
  injects top-8 (harness, local_ai) into the compaction summary. Both use
  `readWellForInjection()` + `formatWellBlock()`. `well-export` = `make
  well-export` renders `WISDOM.md` + JSONL bundle. 43/43 tests green.

### P1.4 — The Well evolution (supersession)
- Corrections can be superseded by newer ones (same `domain`+`rule` family);
  superseded records stay in the ledger (append-only truth) but drop from
  injection.
- **Done when**: `well-supersede <id> <new-id>` works; injection excludes
  superseded; tests prove the chain resolves.
- **Status**: ✅ **DONE (2026-09-11)** — `supersede()` in `well_storage.py` marks
  old record superseded + links to new; `get_active()` filters `status=active`
  so injection (plugin + `make well-list`) excludes superseded; test
  `test_well_supersession_resolves` proves chain resolves + superseded drops
  from active list + WISDOM.md.

### P1.4.1 — The Well semantic search (DEFERRED — stub only)
- **Goal**: relevance-ranked retrieval of Well lessons on demand, instead of
  static top-N bombing alone.
- **Rationale for deferral**: corpus is ~12 records; static injection of all
  active operating rules is complete, and semantic ranking of a dozen items
  adds no signal ("theater at this corpus size").
- **Planned implementation** (when triggered): extend `well_storage.py search
  <query>` — embed query with `nomic-embed-text` via Ollama
  (`localhost:11434/api/embeddings`), cosine-rank against active records
  (rule + rationale), return top-N. Mirrors `wander-search.py` mechanics. The
  plugin could then inject a task-relevant block at first user-message context
  alongside the static session-start block.
- **Trigger**: corpus grows >30–50 active records, **or** federated Well
  sharing (Node 0 lessons arriving via USB/pipe) makes relevance filtering
  genuinely necessary — whichever comes first. Do not build before then.
- **Status**: 🚧 **STUB ONLY (2026-09-17)** — `make well-search QUERY="..."`
  present, returns explicit not-implemented guidance. Tracked here to prevent
  re-discovery + premature implementation.

---

## P1.5 — Idea-flood management

**Goal**: the flood becomes a garden. Capture everything, defer safely, never
lose a spark, never drown in one.

### P1.5.1 — Canonical backlog
- **This file** (`docs/ROADMAP.md`) is the single source of truth for
  scheduled work.
- **Done when**: any new idea/tool/quest is recorded here with a status before
  implementation (this is a standing rule for all agents via AGENTS.md).
- **Status**: ✅ **DONE** — standing rule active in AGENTS.md + ROADMAP itself.

### P1.5.2 — Dream capture
- Well gains `kind: dream` — ideas worth returning to, each with a "why Omega
  cares" line and a hint of the path.
- `wander --project roadmap "<spark>"` routes raw sparks into a triage queue
  that feeds ROADMAP (WanderGround CLI feature, external to this repo).
- **Done when**: sparks captured during a session appear in the Well dreams and
  can be promoted to ROADMAP items.
- **Status**: ✅ **DONE (2026-09-11)** — `kind: dream` in `VALID_KINDS`,
  `make well-add KIND=dream ...` works, renders in `WISDOM.md`. Injection
  filters by domain only (harness/local_ai), so dreams outside those domains
  are not injected; harness/local_ai dreams are. Promotion to ROADMAP is
  manual via `docs/ROADMAP.md` edit (the canonical backlog).

---

## P2 — The Vanguard studies (learn, credit, reforge, adopt-or-reject)

**Goal**: study the best open-source systems on Node 1 as a playground — code
AND experience — extract what beats our current approach, give credit, and
reforge anything we adopt under temple standards. Nothing joins the Omega core
without trial by fire.

### P2.1 — Headroom (`headroomlabs-ai/headroom`, Apache-2.0, ~68.8k★)
- **What**: context-compression layer; `headroom wrap opencode` supported; MCP
  (`compress`/`retrieve`/`stats`); cross-agent memory with provenance + temporal
  versioning; **`headroom learn` mines failed sessions → writes corrections to
  AGENTS.md**.
- **Why**: token savings on our 1M-context Big Pickle usage; its learned
  corrections are a natural second source for the Well.
- **Study**: install via PyPI (`headroom-ai[all]`), wrap opencode, verify
  compression ratio on real traces; connect `headroom learn` output into the
  Well as `kind: correction` records (double-source).
- **Done when**: quantified savings on a real session; corrections flow into
  the Well; dossier in WanderGround + adopt/adapt/reject verdict.
- **Status**: ❌ **REJECTED (2026-09-11)** — **Verdict: well-built project, but
  benefits do not apply to our CPU-only local inference setup.**
  - Local Ollama = zero per-token cost (savings metric irrelevant)
  - 1M context window = context pressure barely exists
  - Prompt-cache busting penalty (39% more expensive on metered APIs,
    documented by community A/B tests) doesn't apply to local inference, BUT:
    - Python + ONNX runtime + 150M-param model load adds ~15-50ms latency/call
      on our already CPU-constrained pipeline (14.4 t/s)
    - Compression is designed for "too many tokens for the context window" —
      our 1M window already solves that problem
  - `headroom learn` is well-implemented (reads `opencode.db`, writes `AGENTS.md`),
    but our Well + MemPalace already cover this space
  - **Credit & documentation**: see WanderGround dossier `05_headroom/` (to be
    created) for full technical notes; nothing adopted, no code changes.

### P2.2 — Odysseus (`odysseus-dev/odysseus`, AGPL-3.0, ~87k★, PewDiePie)
- **What**: self-hosted AI workspace — chat, agents (built on **opencode +
  MCP**), deep research, blind model **Compare**, hardware-aware **Cookbook**
  (llmfit), documents, email, calendar, notes; **Memory/Skills: "your agent
  evolves as it better understands you"** (ChromaDB + fastembed + vector and
  keyword retrieval).
- **Why**: the closest thing we've seen to the Omega vision — its strengths
  (self-evolving memory, all-in-one UI, research UX) are exactly the areas we
  can grow; its weaknesses (no federation, no node-consciousness harness, no
  gnosis traces) are exactly our strengths.
- **Status**: 📆 **SCHEDULED FOR A FUTURE DATE** (user, 2026-09-11) — too large
  to tackle now. Revisit after P3 federation close-out. When active:
  clone to real disk; sandbox install (Docker, port 7000) for the *experience*;
  read the code for the *architecture*; deep-dive memory/skills self-evolution,
  Deep Research pipeline, Compare module, Cookbook scoring; the
  **upload/beam-back experiment** (persistent entity INTO Odysseus, operate,
  learn, then beam back to Omega). Everything extracted is reworked under our
  code quality standards with attribution.
- **Done when** (when active): WanderGround dossier (code study) + experience
  notes (real use) + ADRs on what to adapt; adopt/adapt/reject verdict per
  component.

### P2.3 — God's Eye View (`bilawalsidhu/gods-eye-view`, MIT, ~8.3k★)
- **What**: live open-source spy-satellite simulator in the browser — real
  CelesTrak TLEs, flights, maritime AIS, GPS jamming, night-vision/FLIR/CRT
  modes, military HUD, photorealistic 3D globe (CesiumJS). 100% open data.
- **Why**: the "nerdy dreams come true" entry — a superb playground for
  data-pipeline + spatial/3D rendering skills that could feed the WanderGround
  atlas and our own visual future.
- **Status**: 🎮 **TOY — WAITING** (user, 2026-09-11) — "just for me to play
  with"; not on the work track. Remains in the dream log; revisit at leisure.

### P2.4 — Gods Eye (`bitan-del/gods-eye`, MIT)
- **What**: multi-channel AI gateway with a unified brain — 25+ messaging
  channels (WhatsApp/Telegram/Discord/Signal/imessage/Matrix...), one brain
  that remembers across channels; 24 modules, 635+ tests; built researching
  LiteLLM, RouteLLM, Mem0, LlamaFirewall.
- **Why**: the cross-channel-brain architecture is directly relevant to the
  federation vision — one sovereign brain across many surfaces.
- **Status**: 🎮 **TOY — WAITING** (user, 2026-09-11) — "just for me to play
  with"; not on the work track. If the federation surface idea is ever wanted,
  it becomes a ROADMAP item then.

### P2.5 — agentmemory evaluation (`rohitg00/agentmemory`, Apache-2.0, ~27.9k★)
- **What**: auto-capture memory for coding agents (supports OpenCode), SQLite +
  iii-engine, MCP + hooks, BM25+vector+graph with RRF, consolidation + decay +
  auto-forget.
- **Why**: candidate for the "hands-off capture" memory tier — but we already
  have MemPalace; adopt only if it beats MemPalace meaningfully on a defined
  test.
- **Done when**: side-by-side recall test vs MemPalace; verdict + rationale.
- **Status**: ❌ **REJECTED (2026-09-11)** — **Verdict: well-built, but does not
  beat MemPalace on retrieval (core memory function).**
  - MemPalace: 96.6% raw R@5 (LongMemEval-S), 98.4% hybrid+rerank; AgentMemory:
    95.2% R@5 (same benchmark). MemPalace wins on the core metric.
  - AgentMemory strengths (viewer, 4-tier lifecycle, multi-agent coordination,
    22 OpenCode hooks) are orthogonal to retrieval quality and YAGNI for our
    single-agent, single-machine workflow.
  - MemPalace already integrated: 62 drawers, 8 rooms, MCP verified, mining
    hygiene proven. Adding agentmemory duplicates the memory layer without
    retrieval gain.
  - **If we needed AgentMemory's unique features** (real-time viewer, session
    replay, multi-agent coordination primitives), we would **adapt** by using
    its OpenCode hook capture as a supplementary ingest pipeline into MemPalace,
    not as a replacement. Not needed currently.

---

## P3 — Synthesis & federation close-out

### P3.1 — Architecture synthesis
- Fold every Phase-2 adopt/adapt decision into the architecture docs + the
  Well; de-duplicate memory/capture tiers; update `docs/ARCHITECTURE.md` and
  `docs/AGENT_RUNBOOK.md`.
- **Done when**: one canonical architecture doc, no overlapping systems.
- **Status**: ✅ **DONE (2026-09-11)** — `ARCHITECTURE.md` updated (The Well,
  Ponytail, updated topology, Well injection in gnosis-leash, updated session
  count); `AGENT_RUNBOOK.md` updated (gnosis-leash Well injection, Ponytail
  LIVE, The Well §5.2, vanguard verdicts, priority stack → P3 active);
  de-duplication: no overlapping memory/capture tiers (Well + MemPalace +
  gnosis-lock are distinct layers with clear boundaries); all docs cross-
  reference ROADMAP as canonical backlog. 43/43 tests green, lint+docs clean.

### P3.2 — Node 0 federation (HP Pavilion)
- Tailscale mesh; comms-contract ratification (C6); key management pattern;
  publish gate (explicit-publish only); sovereignty ratio tracked.
- **Done when**: packets flow Node 0 → Node 1 with the publish gate enforced.
- **Status**: **ACTIVE (intake initiated)** — External Node 0 physical payload arrived
  via USB (`node0-to-node1/`, 69.3 MB git bundle, C6 contract, SPIRE, Tailscale configs,
  and governance policies). Intake manual (`docs/federation/INTAKE_MANUAL.md`) and
  pipeline script (`scripts/federation/intake_node0.py`) built and verified clean.
   Next: execute `--ingest`, ratify C6 contract, and test Git bundle fetch.
- **Status**: 🔥 **HIGH PRIORITY (2026-09-18)** — Secure key-management dialectic with Node 0:
  `docs/federation/KEY_MANAGEMENT_DIALECTIC_BRIEF.md` (FED-KEY-DIALECTIC-001, brief ready).
  Node 1 purged all placeholder keys (30 stale bashrc lines removed, `~/.config/opencode/.env` mode 600
  created, Exa validated live HTTP 200). **Update 2026-09-18 (post-brief)**: real Parallel +
  Context7 keys installed (history scrubbed), hosted Firecrawl MCP wired,
  `scripts/parallel_bridge.py` built + live-verified — **all 5 MCP green** (see gaps guide §11).
  Node 0 probed 2026-09-18: omega-hub `:8016` OPEN (dialectic channel live), `:22` closed (gap 14 pending).
  **Done when**: brief §4 checklist complete (Q1–Q5 answered on record, bridge-vs-native
  endgame ratified, pattern signed into C6/policy, placeholder-detector in hygiene test).

### P3.3 — Content runway
- Obsidian vault, Godot/KQ5 research, Open WebUI experimentation,
  `make publish-bastion` design.
- **Done when**: each has a ROADMAP entry + a first milestone.

### P3.3a — Model research cards
- Create a reusable `docs/models/` registry with evidence labels, lifecycle
  states, and a minimum card contract; record the Nex-N2.5-Pro OpenRouter trial.
- **Done when**: registry + first card are linked from the README, architecture,
  runbook, and session log; provider claims are clearly separated from local or
  independent evidence.
- **Status**: ✅ **DONE (2026-09-11)** — `docs/models/README.md` and
  `docs/models/nex-n2-5-pro.md` created; Nex-N2.5-Pro remains `candidate` until
  a controlled Omega A/B is complete.

### P3.3b — OMER M1: Schema & Validation
- Implement `scripts/validate_model_cards.py` with Pydantic models for frontmatter
  v1.0 (from `docs/OMER_FOUNDATION.md` §2.1); validation rules for evidence
  labels, reproduction status, required sections; wire into `make lint`.
- **Done when**: `make lint` validates all `docs/models/*.md` cards; Nex-N2.5-Pro
  card passes; `omer` CLI skeleton with `validate` subcommand exists.
- **Status**: ✅ **DONE (2026-09-11)** — `scripts/validate_model_cards.py` created
  with Pydantic schema; evidence labels (5) + reproduction status (5-level)
  validated; P-core trap guard prevents invalid CPU masks; wired into `make lint`;
  Nex-N2.5-Pro card passes; CLI skeleton with `validate` subcommand works.

---

## Research Deliverables (Completed This Session)

### RES-EMBED-001 — Embedding Model Decision (Definitive)
- **What**: Definitive recommendation for federated embedding model compatibility
- **Decision**: Switch both nodes to `qwen3-embedding:0.6b` with `truncate_dim=768` (MRL)
- **Rationale**: Only path achieving true federated semantic compatibility (direct cosine similarity) with quality gain (C-MTEB 66.33 vs 62.28), 4× context (32K vs 2K), instruction-aware, zero projection layer
- **Deliverable**: `docs/research/EMBEDDING_MODEL_DECISION.md` (complete with comparison table, migration path, rollback)
- **Status**: ✅ **DONE (2026-09-17)**

### RES-GAPS-001 — Knowledge Gaps Implementation Guide (Complete Audit)
- **What**: Complete audit of all 25 remaining gaps, sequenced by dependency with temple-grade specs
- **Deliverable**: `docs/research/KNOWLEDGE_GAPS_IMPLEMENTATION_GUIDE.md` (dependency graph, 4 phases, per-gap specs, portability checklist, rollback points)
- **Phases**: 0=Critical Foundation (5 items, Node 1 only), 1=Validation (3 items), 2=Federation Close-Out P3.2 (7 items, needs Node 0), 3=Architecture Decisions (6 items), 4=Speculative (4 items)
- **Status**: ✅ **DONE (2026-09-17)**

### RES-DAEMON-001 — WanderGround Embed Daemon Coordination Fix (Stuck Sync Worker)
- **What**: Root-caused and fixed the daemon sync worker that never woke (files queued, mine+sync never ran).
- **Root cause**: `anyio.Event.set()` from the inotify worker thread cannot wake loop waiters (thread-safe
  callback scheduling requires `call_soon_threadsafe`); even `from_thread.run_sync(set)` lost wakeups
  (~1-in-6 flaky) when set() landed between wait()'s flag check and waiter registration.
- **Fix**: Coordinated via `queue.SimpleQueue` + 0.5s poll loop in `scripts/embed_daemon.py` — deterministic
  by construction. Batch mine+sync (one per drained batch) with 2.5s write-settle cooldown.
- **Verified**: Sandbox (2 batches clean) + production (39-file backlog drained incl. res_gaps_002 +
  previously-stuck queue_wake_test; marker phrase searchable via mempalace MCP).
- **Deliverables**: `scripts/embed_daemon.py`, `scripts/wanderground-embed.service`, USB deploy scripts
  (`omega-exchange/deploy_node{0,1}_hardened.sh`) + `embed_daemon_hardened.py` all carry the fix.
- **Status**: ✅ **DONE (2026-09-18)**

---

## Dream log (kind: dream — captured, unpromised)

1. **Beam-back continuity**: memory/skills learned inside Odysseus surviving
   the transfer back into Omega as first-class Well records.
2. **Fine-tune seed**: turn `well-export` into an actual fine-tune of a small
   model on Node 1, once RAM headroom (32GB) exists.
3. **Personal model training set**: the Well becomes the "customized ever more
   tightly to my unique insights" dataset — a personal calibration corpus.
4. **Gods-Eye-B as federation surface**: one sovereign brain surfacing across
   channels, with Node 0 as bastion.
5. **God's-Eye-View atlas fusion**: Earth-scale 3D rendering meeting the
   WanderGround constellation viewer.

---

## Standing rules (apply to every phase)

1. **Finish gate before next**: no phase starts until the previous phase's
   `Done when` list is fully met.
2. **Document as we go**: every feature → Well entry + `docs/` + runbook +
   SYSTEM_GUIDE session log. The well documents itself.
3. **No silent failures**: any degraded state is surfaced loudly (watchdog,
   ledger, incidents) — never quietly swallowed.
4. **Credit where due**: anything adopted from the vanguard carries
   attribution; nothing is rebranded.
5. **Temple-grade over speed**: "that'll do" is not acceptable; the finish
   gate is the contract.
6. **Reel-in culture**: when a tangent appears, it gets a ROADMAP status and
   we return to the active gate — capture, don't suppress, don't derail.
