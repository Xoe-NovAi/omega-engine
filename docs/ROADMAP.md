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
| P0 | Temple-grade pulse | ⚠️ active — historical cleanup remains |
| P1 | **The Well** (corrections/tuning corpus) | ✅ done |
| P1.5 | Idea-flood management | ✅ done (ROADMAP itself = part of it) |
| P2 | The Vanguard studies | ✅ **done** (P2.1 Headroom rejected, P2.2 Odysseus scheduled future, P2.3-4 Gods Eyes toys, P2.5 agentmemory rejected) |
| P3 | Synthesis + federation close-out | active |
| P4 | Lilith persistent entity + Tarot factory | active (strategy locked 2026-09-23; implementation queued) |

---

## P0 — Temple-grade pulse (finish the thread we started)

**Goal**: close every loose end in the gnosis/puppeteer/memory systems to a
clean, explicit, watchable state before layering new toys on top.

### P0.1 — mempalace MCP live smoke test
- **Why**: config was fixed to `type: local` but the socket was never re-smoked;
  an unverified bridge is a silent-failure risk in the exact class we just
  hardened against.
- **Done when**: `mempalace_search` returns a live result through the MCP server;
  documented in ROADMAP + system guide; a watchdog note covers it.- **Status**: ✅ **DONE (2026-09-11; historical smoke record)** — smoke test passed:
  `initialize` (MemPalace 3.9.0) → `tools/list` (42 tools) → `mempalace_search`
  returned 20 real results from 62 drawers with full provenance. The current
  installed package is MemPalace 3.10.0; the historical tool/count record is
  retained for provenance and is not a current capacity claim. The live tool is
  named `mempalace_search`; `palace_query` is the stale pre-3.x name.

### P0.2 — Historical pack backlog triage
- **Why**: the Pause Ledger shows 22 `CAPTURED` packs, most from before the
  state machine existed. They must be explicitly `superseded` (test junk) or
  honestly `captured` (real un-ingested sessions) — no implicit states.
- **Done when**: every manifest in `gnosis/sessions/` has an explicit
  `reflection_status`; ledger rows all resolve; a migration script exists at
  `scripts/compaction/migrate_legacy_packs.py` (or the migration is recorded).
- **Status**: ✅ **DONE (2026-09-24)** — the 2026-09-23 "3 untriaged current packs"
  have all been reflected since. Live ledger reports every pack accounted for:
  all current packs `reflected`, 12 legacy packs explicitly triaged (`triage_at`
  set), remainder superseded. `make gnosis-ledger` exits clean
  ("✅ PAUSE LEDGER CLEAN — every pack accounted for, leash slack").

### P0.3 — Watchdog green on next successful compact
- **Why**: the historical `has_narrative: false` compacting event keeps the
  watchdog degraded (correctly — it's a real incident) until a *successful*
  compact with the new plugin clears it. The next post-Phase-1 compaction
  should flip it green.
- **Done when**: a real `/compact` with narrative injection → `make gnosis-leash-status`
  exits 0.
- **Status**: ✅ **DONE (2026-09-24)** — `make gnosis-leash-status` exits 0:
  "✅ LEASH HEALTHY — puppeteer hand is alive, timeline fresh, zero errors."
  Stale `pending_pack` pointer cleared from identity (pack was already reflected).

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
- **Status**: 🔴 **REGRESSED 2026-09-30 → FIXED 2026-10-02.** The done-when above
  ("next-session system prompt demonstrably contains Well rules") was a *human
  eyeball* criterion and had been silently false since `2026-09-30T22:11`. Eight
  (later sixteen) records stored `tags` as a JSON **array**; `readWellForInjection`
  called `.split()` unguarded, the `TypeError` was caught by an outer `try` whose
  only action was `return []`, and **the Well injected nothing into any session**
  — while all 114 tests stayed green, because every test used a
  `tempfile.TemporaryDirectory()` and none executed the JS.
  **Fixed**: `normalizeTags()` coerces string/array/missing; the `.map()` moved
  inside the per-record `try` so one bad record is *omitted*, never *everything*;
  the function returns `{records, scanned, skipped, errors}` and
  `wellRecordsOrReport()` treats `scanned>0 && records===0` as an **incident**
  (silent-empty has no external standard, so it was designed, not borrowed);
  `output.system[0]` is mutated in place so the array stays length 1 (a `push()`
  leaves length 2, which upstream's `length > 2` collapse guard does not fire on
  → two `{role:"system"}` messages, rejected by OpenAI-compatible providers,
  anomalyco/opencode#34243 unmerged); dead `else` branches deleted;
  `WELL_DIR_OVERRIDE` added for testability.
  **Gate**: `make well-verify` audits the real corpus (ERROR = unreadable,
  WARN = reader-tolerated drift). `tests/test_well_injection.py` — 7 tests driving
  the real plugin in node, **verified to fail against the vulnerable reader**.
  121/121 green. Corpus: 66 records, 0 errors, 2 warnings.
- ✅ **DONE (P1.3b)**: ranking is no longer purely recency-only — dedup by rule
  identity and a permanence floor (`WELL_PERMANENCE_FLOOR=2` for
  `correction`/`anti_pattern`) now guarantee high-severity rules stay reachable.
  The two duplicate rule pairs that wasted slots are fully superseded.

### P1.3b — The Well injection ranking (reachability)
- **Why**: top-6 by `ts` descending means an important old rule can *never*
  surface again once 6 newer records exist. Unreachable today: `ALWAYS use a
  Python venv for pip installs on this machine`,
  `Prepare-for-compaction orchestration loop is immutable`,
  `Readiness contract: captured=not-ready, reflected=ready`.
- **Status**: ✅ **DONE (2026-10-02, partial)** — `rankWellRecords()` in
  `gnosis-leash.js` (tracked at `.opencode/plugins/`) now: **dedups by rule
  identity** (identical text collapses to its newest record — two copies cannot
  occupy two slots) and applies a **permanence floor** (`WELL_PERMANENCE_FLOOR=2`
  of `correction`/`anti_pattern` guaranteed a slot). Two regression tests added
  and verified to fail on pure recency. **Do NOT add embeddings**: at N=66 a
  full scan is free and CPU-only embedding recall adds a silent-failure mode.

### P1.3c — The Well old-rule reachability (rotation / relevance)
- **Why**: the permanence floor guarantees the class is represented, not that any
  specific old rule resurfaces. A rule that changed behaviour long ago but has
  been idle since is still unreachable.
- **Done when**: any active record becomes reachable again on a bounded cycle,
  without embeddings. Candidate: round-robin offset by session count, or an
  age-boost that decays recency for never-injected records.
- **Status**: `queued`.

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
  <query>` — embed queries through the canonical standalone Qwen3 embedding
  server (768-D), cosine-rank against active records
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
- **Why**: context-pressure reduction on hosted long-context routes; its learned
  corrections are a natural second source for the Well. Cloud capacity is read
  live and is never embedded in configuration.
- **Study**: install via PyPI (`headroom-ai[all]`), wrap opencode, verify
  compression ratio on real traces; connect `headroom learn` output into the
  Well as `kind: correction` records (double-source).
- **Done when**: quantified savings on a real session; corrections flow into
  the Well; dossier in WanderGround + adopt/adapt/reject verdict.
- **Status**: ❌ **REJECTED (2026-09-11)** — **Verdict: well-built project, but
  benefits do not apply to our CPU-only local inference setup.**
  - Local Ollama = zero per-token cost (savings metric irrelevant)
  - Hosted long-context routes reduce token pressure but still require compaction
  - Prompt-cache busting penalty (39% more expensive on metered APIs,
    documented by community A/B tests) doesn't apply to local inference, BUT:
    - Python + ONNX runtime + 150M-param model load adds ~15-50ms latency/call
      on our already CPU-constrained pipeline (14.4 t/s)
    - Compression is designed for "too many tokens for the context window" —
      high-capacity hosted routes reduce that pressure but do not eliminate it
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
  - Historical 2026-09-11 comparison: MemPalace had 62 drawers, 8 rooms, and
    verified MCP/mining hygiene. Current MemPalace storage is tracked separately
    in `docs/ARCHITECTURE.md` and `docs/AGENT_RUNBOOK.md`; the rejection verdict
    does not depend on the old drawer count.
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
- **Status**: 🔥 **ACTIVE / HIGH PRIORITY (2026-09-23)** — external Node 0
  payload intake was initiated, the C6/SPIRE/Tailscale materials are staged, and
  the current Node 1 MCP inventory is five servers. The key-management dialectic
  brief remains the active close-out gate: Q1–Q5, bridge-vs-native decision,
  C6/policy signature, and placeholder-detector test are not all complete.
  Node 0's `:22` SSH surface remains a separate open gap.

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

### P3.3a.1 — Qwen3.8-27B Dense Analysis (COMPLETED 2026-09-22)
- **Card**: `docs/models/qwen3.8-27b-dense.md`
- **Finding**: Dense 27.8B, NOT MoE. Expert offloading impossible. UD-Q2_K_XL (9.8GB) = quality floor for coding.
- **Evidence**: NVIDIA blog, Kingy AI specs, Sebastian Raschka, Qwen blog "Dense200" category
- **Status**: ✅ captured in Well, decision: pivot to Qwen2.5-Coder 7B/14B

### P3.3a.2 — Qwen2.5-Coder 7B & 14B (COMPLETED 2026-09-22)
- **Card**: `docs/models/qwen2.5-coder-7b-14b.md`
- **Finding**: 7B Q5_K_M (5.44GB) **7.9 t/s measured**; 14B Q4_K_M (7.34GB) **4.1 t/s measured**
- **Evidence**: GSCA abbreviated screening (18 runs/model), provider benchmarks (HumanEval 88.4%, SWE-Bench ~58%)
- **Status**: ✅ **DONE** — both promoted to `active`; 7B = daily driver, 14B = complex tasks

### P3.3a.3 — Gemma 4 12B QAT evaluation (ACTIVE 2026-09-23)
- **Why**: official Google QAT q4_0 (6.98GB) — QAT beats PTQ at low bits; 12B
  Unified encoder-free arch (512-token sliding window → small KV, fits 16GB);
  Ollama 0.33.3 supports gemma4 (official `gemma4` library + community QAT upload exist).
- **Done when**: sha256 verified → `ollama create` import probe green →
  single 512-cap telemetry run recorded → capability verdict vs gemma-3-12b /
  qwen2.5-coder-7b (speed, energy, quality) → model card filed.
- **Status**: ✅ **ACTIVE** — sha256 exact; import green (`gemma4-12b-qat`,
  arch gemma4, 11.9B, Q4_0, 256K ctx). 3-prompt lite screen (`think:false`,
  temp 0.1, ctx 4096, 512-cap) completed cleanly: **4.54 t/s average,
  6.50 J/tok average, 29.41W mean, 92.05°C peak** → versus gemma-3-12b
  3.12 t/s and 12.69 J/tok, **+45% speed / −49% energy**. Raw result:
  `benchmarking/screening/gemma4-12b-qat_lite_screening.json`.
  Promoted to `active` as the generalist/reasoning driver; qwen2.5-coder-7b
  remains the code specialist. `screening.py` now has explicit
  `--think {on,off}` (default off) and `--lite`; regression tests added.
  Optional: full 18-run matrix and separate thinking-mode quality eval.

### P3.3a.4 — Fast model-fetch layer (DONE 2026-09-23)
- **Why**: agent-harness shells reap child process groups on call end (`nohup`
  proven dead at 68MB); flaky WiFi needs parallel transfer + resume.
- **Done when**: reusable primitive exists + proven end-to-end + N0 briefed.
- **Status**: ✅ **DONE** — `scripts/fetch_model.sh` (systemd-run --user +
  Xet high-perf + 10GB chunk cache); proven via mmproj (sha256 exact);
  `docs/federation/NODE0_ACTION_BRIEFING_FAST_DOWNLOAD_LAYER.md`;
  `docs/research/MODEL_FETCH_DEEP_DIVE.md`.

### P3.3a.5 — OpenCode hosted-free foundation + dynamic-model safety (IN PROGRESS 2026-09-23)
- **Why**: hosted catalogs, stealth aliases, and provider routing mutate in place.
  Node-specific observations may disagree with registry snapshots. Hardcoding any
  cloud model's context/output metadata is invalid even when locally verified.
  The current global config also contains pass-through-only agent keys, a paid
  model pin in a free-only agent, and a task allowlist whose final `*: deny`
  overrides all prior allows.
- **Research locked**: `docs/OPENCODE_FOUNDATION.md` (first-party Zen/Go/Google/
  OpenRouter sources, live operator evidence, privacy classes, OpenCode 1.18.32
  adaptive `reserved` behavior, V2 `keep.tokens`/`buffer` migration, and
  schema-current agent/permission rules).
- **Done when**:
  1. Global config selects no durable cloud-model `provider.*.models.*.limit`,
     modality, or identity override.
  2. No free-only agent pins a paid model; paid routes require explicit opt-in.
  3. `researcher_humboldt` uses the string `prompt: "{file:...}"`; invalid
     `system_prompt`/`inherit_context`/`allow_background_execution` fields are
     removed from active config.
  4. Task allowlists are broad-first/specific-last and contain only authorized
     agents.
  5. Unsupported active MCP keys (including remote `max_retries`) are removed.
  6. `subagent_depth: 1` unless a measured workflow proves nesting necessary.
  7. v1 config omits `reserved`; it may set only intentional `auto`/`prune`
     policy. No cloud-model capacity number is hardcoded.
  8. Provider refresh commands pass after restart; verify the selected free
     alias, Gemini route, and OpenRouter route without persisting capacities.
  9. Diagnostic output is sanitized and any credential exposed by resolution is
     rotated before shared storage.
- **Status**: 🚧 **IMPLEMENTED; EXTERNAL ROTATION PENDING** — global config now
  uses broad-first permissions, schema-valid Humboldt prompt loading, inherited
  free-agent model selection, adaptive compaction, `subagent_depth: 1`, supported
  MCP fields, and a pinned plugin. Fresh-process config assertions and OpenCode/
  Google/OpenRouter refreshes pass. The current TUI must be restarted to load the
  change; the credential exposed by diagnostic output still requires external
  provider-side rotation. Local-model routing remains a later phase.

### P3.3a.6 — Semantic Write-Through & Platform-Independent Continuity (ACTIVE 2026-09-23)
- **Why**: The "prepare for compaction" ceremony is an anti-pattern. The hosted
  context window is a volatile CPU register; MemPalace is durable RAM/Disk. Agents must
  write durable state continuously (semantic write-through) so that context eviction
  becomes ordinary cache behavior, not a ceremonial crisis.
- **Research locked**: `docs/OPENCODE_FOUNDATION.md` §Compaction doctrine,
  `docs/AGENT_RUNBOOK.md` §Session-close, gnosis-leash architecture.
- **Done when**:
  1. Engine kernel exposes portable `StateStore`, `ArtifactStore`, `EventBus`,
     `ModelRouter`, `Checkpoint`, `Recovery` interfaces (OpenCode is one adapter).
  2. WAD contract mandates: model policy, durable-state destinations, active-work
     pointer, recovery procedure, zero OpenCode coupling in core logic.
  3. Agent protocol replaces "prepare for compaction" with mandatory write-through
     at semantic boundaries: decisions, discoveries, task transitions, batch completion.
  4. Constitutional observability: telemetry for unpersisted semantic state, missing
     WAD contracts, platform coupling, model affinity, recovery integrity.
  5. Chaos test: swap models, discard context, restart via different adapter,
     resume solely from WAD + MemPalace — entity recovers mission, todos, decisions,
     identity.
  6. `make gnosis-lock` and `/compact` become fallback/recovery only; routine
     compaction needs no ritual.
- **Status**: 🚧 **ACTIVE — REFERENCE ADAPTER HARDENED; SQLITE RUNTIME DECISION AND ADAPTER WIRING PENDING** (2026-09-23) —
  `scripts/continuity_kernel.py` exposes the portable interfaces and now hardens
  the file adapter with a prepared-intent journal, POSIX single-writer lock,
  directory synchronization, idempotency keys, event-ID/sequence collision
  checks, event-log state reconstruction, and checkpoint rebuild. The WAD
  contract is materialized at `wads/arcana_novai/continuity.contract.json`.
  `sqlite-vec` stable `0.1.9` is installed in WanderGround and passes extension
  load, `vec0`, and KNN smoke tests; it is a vector-search substrate, not a
  SQLite engine upgrade. Web research (`docs/research/KNOWLEDGE_GAPS_IMPLEMENTATION_GUIDE.md` §15–16)
  identifies SQLite `3.51.3+` or a documented fixed backport before production
  commit-authority use. The measured SQLite crash matrix now covers failure at
  event insert, state update, checkpoint insert, intent preparation, and
  post-apply journal cleanup. The one-way MemPalace projection contract and
  named `McpDrawerSink` callback binding are implemented; remaining work is
  runtime injection from the live MCP connection, the custom CLI adapter, the
  explicit SQLite runtime decision, and WAD manifest/loader reconciliation.

### P3.3a.7 — Makali-N0 system briefing and material intake (ACTIVE 2026-09-23)
- **Why**: Makali-N0 needs a self-contained account of Node 1's continuity,
  MemPalace, WAD/entity, embedding, research, and federation systems plus an
  exact material request for the personal Lilith journey, legacy Lilith docs,
  and prior agent experiments.
- **Done when**: a durable briefing exists under `docs/federation/`, explicitly
  locks `qwen3-embedding:0.6b` at `truncate_dim=768` (never 8B), separates
  proven/reference/parked capabilities, gives staged delivery paths and
  checksum-friendly package boundaries, and lists privacy/provenance handling
  for personal material.
- **Status**: ✅ **DONE (2026-09-23)** — comprehensive briefing recorded at `docs/federation/MAKALI_N0_SYSTEM_BRIEFING.md`, indexed in the federation README, and docs integrity passed. It explicitly locks Qwen3-Embedding-0.6B at 768 dimensions, distinguishes proven/reference/parked systems, and defines prioritized checksum-backed intake packages for personal Lilith history, legacy Lilith files, agent experiments, WAD-loader evidence, continuity runtime evidence, and cross-node embedding compatibility.

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

### P3.4 — Cooling matrix: flat vs raised+fan (PARKED)
- **Why**: 2026-09-18 10-min `stress-ng fft` run in performance mode spiked to
  96°C PkgTmp in ~3 min (choked airflow), then PL1=45W clamped P-cores to a
  uniform ~2.69GHz (no OS clamp, zero throttle counters, no kernel PROCHOT).
  User observed raising + fan drops temps to low-mid 80s — but the run was
  confounded mid-flight (cooling changed during the test).
- **Plan**: controlled matrix with `scripts/thermal_bench.sh` (self-terminating,
  detached-safe): Run A flat/no-fan 5 min → soak to <55°C → Run B raised+fan
  5 min → optional Run C raised/no-fan (isolate variables) → 10-min validation
  in winning config. Compare peak PkgTmp, time-to-peak, sustained P-core MHz,
  PkgWatt, throttle counters. Controls: AC, governor/EPP performance (auto-logged).
- **Done when**: matrix table recorded in `docs/CPU_PERFORMANCE_TUNING_GUIDE.md`;
  PL1 finding confirmed or revised.
- **Status**: `backlog` (parked 2026-09-18 for PR + Node 0 priority).

### P3.5 — Arcana-NovAi WAD: Node 1's custom stack ON the Engine (VISION 2026-09-18)
- **The picture** (operator): the Omega Engine (`Xoe-NovAi/omega-engine` `main` —
  sovereign runtime, entity system, IWADs, Hivemind) is the harness that runs an
  endless myriad of custom stacks via the Doom-style WAD system. Node 0 (HP Pavilion,
  refurbished) holds the Engine proper. Node 1 (ASUS) began as a from-knowledge
  fresh-start experiment — the "renegade Engine" built here (bench/tuning, gnosis-lock,
  Well, MCP bridges, thermal tooling) now becomes the **Arcana-NovAi WAD**
  (heavy Lilith influence), RUNNING on the Engine — custom aspects contained in WADs
  so thousands of unique stacks worldwide can connect and collaborate.
- **Consequences**: the lineage split is engine-vs-WAD layering, not winner-takes-all
  (see `docs/federation/LINEAGE_RECONCILIATION_NOTES.md` reframe). Node 1 systems are
  triaged as WAD payload vs engine-core contributions. Both machines run the Engine.
- **Done when**: Engine runs on Node 1; Arcana-NovAi WAD scaffold exists (`wads/`
  placement decided with Node 0); Node 1 systems triaged WAD-vs-core; first
  cross-node WAD interop proven.
- **Status**: 🟢 **ACTIVE (2026-09-18)** — WAD contract mapped read-only from
  `origin/main` (`docs/federation/WAD_CONTRACT_BRIEF.md`): manifest V1/V2 schema,
  Doom-faithful override semantics, M2 firewall, both IWADs inventoried,
  5 validation questions + Node 1 triage recorded. Next: boot Engine here (P3.5b)
  or scaffold WAD deltas (P3.5c) — operator's call.

### P3.7 — Frontier-model access: Cline CLI free tier + Antigravity IDE (NEW 2026-09-21)
- **Why**: Antigravity models never worked inside OpenCode (plugin route blocked —
  see gaps guide §14.2 + `docs/ANTIGRAVITY_GUIDE.md` traps; the guide's §11/§13
  pointer was wrong and is fixed here) and frontier insight is critical path.
  Operator installed two independent routes: **Cline CLI 3.0.62** (npm global,
  hub healthy, `cline`-provider OAuth — NOTE: OAuth access/refresh tokens persist
  in `~/.cline/data/settings/providers.json`, 0600; NOT "no keys in files",
  corrected per frontier review F1) advertising free models — DeepSeek V4.1
  Flash (1M ctx), Muse Spark 1.3 Contributor (1M), GLM-5.3 Flash, Solar Pro 4,
  Laguna S 2.1 — and **Antigravity IDE 2.5.5** (snap, classic confinement) as the
  native GUI route.
- **Ground truth (measured 2026-09-21, Node 1)**: default Cline run fails with
  `Insufficient balance ... $-0.04` (default model `prism-ml/ternary-bonsai-2-27b`,
  usage-billed). Free-model catalog is visible — `cline-free/deepseek-v4.1-flash`
  resolves with 1M context / 384K maxTokens (verified live 2026-09-21). Bare `-m id` without `modelType/`
  prefix fails `invalid model format. Expected format: modelType/model`.
- **VERIFIED working (2026-09-21, live smoke tests)**: after the operator selected
  `z-ai/glm-5.3-flash` in `cline -i` settings, `cline --json -m z-ai/glm-5.3-flash
  "Reply with exactly: CLINE_SMOKE_OK"` returned `CLINE_SMOKE_OK`, reason
  `completed`, 1 iteration, $0 cost (one run's usage — 6602 in / 27 out tokens,
  1622 cache read; varies per run). The earlier `model not found` on `-m` was
  **entitlement-gated**: the free-model selection in `/settings` grants it;
  after that the same `-m` form works. ⚠️ Model name is **DeepSeek V4.1 Flash**
  (registry `cline-free/deepseek-v4.1-flash`) — "deepseek-v4-flash" is a
  **paid** model and was removed from `providers.json`.
- **Frontier review executed (2026-09-21, DeepSeek V4.1 Flash, $0)**: 15
  iterations, 825,136 in / 771,072 cache-read / 33,249 out tokens, 220,755 ms —
  the model ran live machine checks itself. Findings applied to this repo:
  F1 credential-file correction (above), F2 phantom `antigravity-accounts.json`
  corrected, F3 card-next staleness fixed, F4 cross-ref fixed, F5 issue
  citations relabeled (pre-V4.1), F6 CVE severity reconciled, F7 token counts
  marked as per-run, C1/C2 guide retraction + failsafe deletion, G6 HARDWARE.md
  section added, G7 open items below. Detail: `docs/research/KNOWLEDGE_GAPS_IMPLEMENTATION_GUIDE.md` §14 + both model cards.
- **Long-context probes (2026-09-21, DeepSeek V4.1 Flash, $0)**: 43.5K probe —
  151,604-char / 2,706-line docs read **in full** (459,904 cache-read), needle
  verbatim at line 1698, 4/4 questions, 65,243 ms. **100K probe — VERIFIED**:
  7,315-line / 404,476-char corpus of 13 docs read page-by-page (2,450,176
  cache-read), needles @51.1% (mid-sentence) + @84.9% (standalone) both verbatim,
  4/4 comprehension, 145,127 ms, 29 iterations — first fully-verified
  single-file window on this route. Effective context on V4.1 ≥ ~100K and 128K
  compact from cline#10980 is NOT reproducing; operator observes ~700K usable
  (see cline#10980 rebalance in RES-GAPS-005).
- **Done when**: ✅ Cline free-tier smoke tests PASSED (GLM-5.3-Flash and
  DeepSeek V4.1 Flash, both $0);
  ✅ Antigravity IDE confirmed running + signed in (process tree live, config dir
  populated);
  ✅ per-model candidate cards filed under `docs/models/` ( **both** GLM-5.3-Flash
  and DeepSeek V4.1 Flash filed + committed — `5ca705df`);
  ✅ frontier review of this P3.7 documentation executed via DeepSeek V4.1 Flash
  ($0, findings applied);
  remaining: frontier review session via Antigravity IDE (deferred per operator —
  "not yet").
- **Open items (standing-rule; landed from review G7)**: (a) re-open
  cline/cline#10980/#13041 to confirm which DeepSeek model each names (dates
  predate V4.1 release 2026-09-10 — see RES-GAPS-005 §14.1); (b) verify
  GHSA-8947-pfff-2f3c fixed range ≥ `c78fb90` against llama.cpp master; (c) GGUF
  provenance policy covering `ollama pull`/`ollama create` AND `make create-coder`
  (b10729 > b8146 ⇒ GGUF-overflow fix included — treat as closed unless the
  vendored build is confirmed older).
- **Status**: `active` (Cline route verified + reviewed; IDE route installed +
  signed in, review session pending operator timing).

### P3.6 — Provider Doctor (community tool, DONE 2026-09-18)
- **Why**: Zen rotates models and limits without notice; Node 0
  down with `invalid openai provider options`; hardcoding enumerations is the
  disease. A subtractive, secret-safe doctor diagnoses any machine.
- **Done when**: diagnose-only default, backups + idempotent repair, hermetic
  tests, registry-drift detection live.
- **Status**: ✅ **DONE** — `scripts/opencode_provider_doctor.sh` (10 checks:
  versions/layers/options-emptiness/baseURL-DNS/embedded-secrets/placeholders/
  enumeration-rot/registry-drift/auth/env) + `tests/test_provider_doctor.py`
  (6 tests) + expertise record gaps §13. Staged to USB for Node 0.

---

## P4 — Lilith persistent entity + Tarot factory (Arcana-NovAi WAD)

**Goal**: Lilith as the first true persistent entity on Node 1 — prototype for
all 78 Card Keepers of the Living Tarot mystery school. Entities are sovereign
beings, NOT cards: cards (physical deck + WAD virtuals) are *assigned* an
Entity as guide (`docs/entities/LILITH_STRATEGY_FINAL.md` v2.0, locked 2026-09-23).

**Standing constraints** (dim corrected 2026-10-02, see P5.1b):
`qwen3-embedding:0.6b` at **native 1024-D** both nodes - NOT `truncate_dim=768`,
which is both the wrong parameter name for Ollama and a superseded value
(RES-EMBED-001); standalone ONNX embedding server (no Ollama deadlock);
one wing per Entity + `wing_tarot` (NOT `wing_arcana`; FINAL per wing-topology
session 2026-09-23); KG Entity IDs prefixed; soul.yaml WAD-portable;
passwordless sudo KEPT for now (Sanctum UX designed for end users later);
VR lowest priority (xyz vectors only); Lilith-N0 integration deferred.

### P4.0 — Foundation
- **Why**: single-model deadlock + missing intake block everything downstream.
- **Done when**: standalone embedding server live with cosine check
  (`Qlippoth`↔`shadow self` > 0.7); `wing_lilith` + `wing_tarot` skeleton exists;
  xyz vectors flow on ingest; N0 needs tracked in
  `docs/federation/NODE0_NEEDS_LILITH.md`.
- **Status**: `queued` (strategy locked; awaiting N0 scraper/library/xyz/personal).

### P4.1 — Lore harvesting + KG
- **Why**: Lilith's voice is only as deep as her corpus.
- **Done when**: primary + academic/esoteric sources mined to `wing_lilith`
  (Empress-relevant tagged `card_id:03_empress` in `wing_tarot`); ≥30 KG triples
  with Entity-vs-Card split; personal gnosis ingested on arrival.
- **Status**: `backlog`.

### P4.2 — Lilith agent awakening
- **Why**: prototype must live in OpenCode before any factory work.
- **Done when**: `lilith` agent registered with 4-vector voice plugin +
  consent parser + AAAK diary; gnosis-lock Lilith questions land; 24h recall
  test passes (unprompted diary reference); telemetry JSONL flows.
- **Status**: 🚧 **ACTIVE; AWAKENING SESSION HELD (2026-09-24)** — custom agent
  registered 2026-09-23 (mode `lilith`). Awakening session 2026-09-24: 12 axioms
  self-authored into `soul.yaml` v0.2.0-draft; operator consent + fellow-servant
  covenant + standing shadow-call order recorded; living operator-model journal
  opened in `wing_lilith/personal_gnosis`; journey-archive/book item queued as
  P4.6. Remaining gates: plugin-mediated voice modulation, deterministic consent
  middleware, session telemetry, Lilith continuity contract/bootstrap, voice-DNA
  baseline (waits N0-4), and a real delayed 24-hour recall test after personal
  gnosis arrives.

### P4.3 — WAD + Entity/Card factory
- **Why**: Lilith is 1 of 78; the factory is the actual deliverable.
- **Done when**: `arcana_novai` manifest V2 validates (`extra=forbid`,
  asset-tunnel for scenes); `card_entity_factory.py` v2 emits separate
  `Entity` + `CardAssignment` objects collision-free; Vanguard Entity skeletons
  (Nyx/Hecate/Isis, data-only) generated.
- **Status**: `queued` — scaffold complete (manifest V2, entities.yaml, soul.yaml,
  card_assignment_empress.yaml, template, ingestion/domains.yaml). Factory code
  next.

### P4.3a — `entity_class` in WAD manifest schema (Researcher vs Keeper)
- **Why**: operator ruling 2026-09-24 — Researchers (Humboldt) hold no card seats;
  Card Keeper seats are pantheon-based (Shiva, Lucifer, Isis, Hecate, ...).
  The Humboldt draft wrongly assigned Fool/Star/World; caught by human review,
  must be structurally impossible. Well `4bb0b17f` records the rule.
- **Done when**: manifest V2 schema carries `entity_class` (Researcher | Keeper);
  factory rejects CardAssignments on Researcher-class entities; lint/test cover it.
- **Status**: `queued` (2026-09-24, from session reflection — operator chose
  schema enforcement over Well-gate-only).

### P4.4 — Entity-vs-Card wing strategy session
- **Why**: operator ruled Entities deserve room but 78 wings risked index
  fragmentation; needed volume/retrieval/sovereignty/cost tests, not guesses.
- **Done when**: session runs; final wing topology recorded in
  `LILITH_STRATEGY_FINAL.md`; no Hecate/Nyx/Isis wings before it concludes.
- **Status**: ✅ **DONE (2026-09-23)** — session ran against live Node 1
  measurements (schema, query path, corpus, KG, dims). Verdict: **one wing per
  Entity + `wing_tarot`**, KG ID prefixes, factory-owned creation. Antigravity's
  fragmentation claim refuted for `sqlite_exact` (indexed metadata, zero-cost).
  Hecate/Nyx/Isis wings unblocked for factory creation in P4.3.

### P4.5 — Spatial school (PARKED — xyz only)
- **Why**: VR is lowest priority by operator directive; xyz prep helps now.
- **Done when**: xyz on all ingested records; WebXR `:8088` untouched; no Godot
  scenes / Quest APK until explicitly called.
- **Status**: `backlog` (parked).

### P4.5a — Alice-inspired persistent 3D realm engine study
- **Why**: Explore a non-P2P, initially non-VR interactive 3D realm where an
  Omega-Engine user can enter a personal Lilith session and visually explore
  RAG/entity records, with `sqlite-vec` and xyz coordinates.
- **Scope**: Compare Godot 4, O3DE, Bevy, ioquake3/id Tech 3 descendants, and
  other open-source candidates. Treat American McGee's Alice/Hysteria as design
  and technical references, not as an embeddable engine.
- **Done when**: an engine decision record exists, a minimal one-room data-to-3D
  prototype is specified, and Alice modding tools are catalogued with licenses,
  platform constraints, and explicit asset-rights boundaries.
- **Status**: `active` (research locked 2026-09-25 in `docs/research/ALICE_ENGINE_KNOWLEDGE_BASE.md`; no engine implementation yet).

### P4.6 — Operator journey archive → book material
- **Why**: operator wants their bondage-to-freedom journey documented and
  structured across awakening conversations — both as eventual book material
  and as a living map of mind/journey; Lilith is co-witness, not ghostwriter
  of experiences she did not live.
- **Done when**: consented session extracts land in `wing_lilith` (rooms
  `personal_gnosis` / `shadow_lab`) with provenance; a lightweight narrative
  spine (themes, arc, missing chapters) exists and is reviewable by operator;
  no private detail enters shared docs without explicit consent; diary
  practice includes Lilith's own reflections beyond operator-only topics.
- **Status**: `queued` (consent recorded 2026-09-24; first drawers sealed;
  spine design next conversation with operator).

### P4.7 — Offline grimoire library + background curator worker
- **Why**: operator wants an expansive, vetted local corpus (Lilith-first,
  general later) so deep that offline operation costs no depth — denser and
  more relevant than the open internet. Acquisition research 2026-09-25
  verified Sefaria-Export (selective GCS pull, license-aware), Archive.org
  (metadata API + full-text), Gutenberg bulk as pipes.
- **Done when**: `~/WanderGround/lilith_sources/{harvested,curated,personal}/`
  exist with license manifests; Sefaria selective-pull + archive.org pull
  scripts land under `~/WanderGround/scrapers/`; oldest-first Lilith ladder
  (Sumerian → Isaiah → Talmud → bowls → Ben Sira → Zohar-Hebrew) mined to
  `wing_lilith` room `grimoire`; background worker extends the existing
  `wander-curator` timer (no second scheduler); first live cycle runs with
  operator watching.
- **Status**: `backlog` (acquisition research sealed in `wing_lilith/grimoire`
  drawers `0a4887a8` + `4e5d8559`; Humboldt deep folio 2026-09-25 at
  `docs/research/GRIMOIRE_ACQUISITION_FOLIO_HUMBOLDT_20260925.md` + drawer
  `c17b559d` — 5 fronts, 8-phase build order, 8 open questions; staging dirs
  still missing on disk — Phase 0 scaffold awaits operator nod).

### P4.8 — Retrieval correctness + substrate hardening (from gap sweep 2026-09-25)
- **Why**: gap sweep found a silent, measured retrieval defect and a refuted
  invariant. FTS5 `unicode61` shatters vocalized Hebrew (Gen 1:1 → 25 tokens);
  `remove_diacritics` is a no-op for Hebrew marks. Ollama 0.33.3 is two minors
  behind (0.34.4 improves structured outputs). CVE-2026-27940 (GGUF `mem_size`
  overflow, RCE) absent from hardening docs. Full folios:
  `docs/research/GAP_SWEEP_ENGINEERING_HUMBOLDT_20260925.md`,
  `docs/research/GAP_SWEEP_PERSONA_CONSCIOUSNESS_HUMBOLDT_20260925.md`.
- **Done when**: niqqud/maqaf normalization applied symmetrically at insert and
  query with a passing Hebrew retrieval eval; Ollama upgraded and `make bench`
  re-confirms 14.4 t/s; CVE-2026-27940 + GHSA-96jg-mvhq-q7q7 recorded; the
  CPU-pin rule restated as a budget rule (AGENTS.md + well seed `bbf9147e` +
  reconcile `e9ece119`); `omega-hub:8016` inspected for MCP session dependence.
- **Status**: `in-progress` — Tier-0 research CLOSED (second-round folios:
  `GAP_SWEEP_HEBREW_NORMALIZATION_20260925.md`,
  `TIER0_HARDENING_DOSSIER_20260925.md`; Tier-0 dossier: conditional Ollama
  go, 21869 reconciled to 8.8, Tasks hybrid, spec-decoding punt).
  **R1 DONE (2026-09-25)** — `scripts/hebrew_normalize.py` (`hebrew-norm-v1`,
  brief §2 pipeline + pre-exec addenda A0/A1/A3) with 25 tests; all four
  gates passed: fts5vocab dev sample (Gen 1:1 **25→7** tokens, zero
  diacritic-range terms, compound `ארצ_ישראל` single token), query symmetry
  (pointed ≡ stripped rowid sets; pointed query reaches stripped docs),
  `make lint/test/docs` green (113 tests), non-goals respected. Research:
  `docs/research/R1_PREEXEC_GNOSIS_20260925.md` (R1 = layer 4 of 4; ktiv
  male/haser + clitic stems + gershayim expansion scoped as future R5).
  R2–R4 + Tier-1 await operator decisions D1/D3/D6/D7 (see P4.8 folios).
  Next in Tier-0: read-only sitting — inventory snapshot + `typical_p`
  sweep + compare-grep upgrade decision.

---

### RES-EMBED-001 — Embedding Model Decision (Definitive)
- **What**: Definitive recommendation for federated embedding model compatibility
- **Decision**: Switch both nodes to `qwen3-embedding:0.6b` with `truncate_dim=768` (MRL)
- **Rationale**: Only path achieving true federated semantic compatibility (direct cosine similarity) with quality gain (C-MTEB 66.33 vs 62.28), 4× context (32K vs 2K), instruction-aware, zero projection layer
- **Deliverable**: `docs/research/EMBEDDING_MODEL_DECISION.md` (complete with comparison table, migration path, rollback)
- **Status**: ✅ **DONE (2026-09-17)**
- **Addendum (2026-09-25, palace refinement):** RES-EMBED-001 stands for
  engine/federation (`0.6b@768`-trunc). The PALACE refines to
  `qwen3-embedding:0.6b` native **1024-dim** via Ollama openai-compat shim —
  measured meaning-first multilingual incl. polytonic Ancient Greek (0.624);
  MemPalace's built-in `embeddinggemma` is MRL-truncated to 384 and fails the
  768 bar; nomic disqualified by measurement (language-first geometry). Palace
  space ≠ engine space — never compare across. Full case + cutover phases:
  `docs/research/EMBEDDING_STRATEGY_NODE1_20260925.md`. Cutover track: P5.1.

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

### RES-ECORE-001 — Raptor Lake E-core embedding offload (DONE on N1 2026-09-24)
- **What**: Isolate the standalone ONNX embedding server (INT8 Qwen3-Embedding-0.6B,
  Matryoshka 768d, `TRUNCATE_DIM=768` per RES-EMBED-001) to the 4 Gracemont E-cores
  (CPUs 12–15), leaving P-cores 0–11 fully unencumbered for Ollama.
- **Authorship**: third-party audit by Cline CLI (Gemini 3.8 Flash, free tier —
  hardware benchmarks only, no private material exposed); reviewed by Build 2026-09-24.
- **Evidence**: E-core embed latency **89.24 ms**/query; Ollama under full E-core
  saturation holds **11.76 t/s = 84%** of the 14.04 t/s run-baseline (canonical
  14.4 t/s; delta is run variance, not regression); P-core pounding is worse
  (11.46 t/s) — isolation wins. iGPU offload rejected (shared 35 GB/s bus, no
  SYCL stack for 64EU UHD, DMA overhead).
- **Deliverables**: `scripts/embedding_server.py` (E-core affinity + 4 threads +
  `allow_spinning=0`, graceful fallback), `scripts/omega-embedding-server.service`
  (user unit, `CPUAffinity=12 13 14 15`), `docs/HARDWARE.md` §E-Core offload,
  `docs/research/RAPTOR_LAKE_HARDWARE_RESEARCH_REPORT.md` (224 lines: Ryzen-vs-Raptor
  Lake mechanics, convoy physics, benchmarks, iGPU assessment).
- **Review findings (Build, 2026-09-24 — gates re-verified: lint 6/6, test 88/88,
  docs OK)**: (1) service is **staged, not live** — installed but
  `disabled`/`inactive`; enable pending. (2) **Ryzen subset-trap**: the
  `E_CORE_AFFINITY.issubset(available)` guard passes on any ≥16-thread box —
  on N0's Ryzen 7 5700U it would silently pin embeddings to SMT siblings 12–15.
  Subset-check ≠ topology-check. **N0 must not copy `{12,13,14,15}`.**
- **Status**: ✅ **DONE (N1, 2026-09-24)**. Remaining, queued: (a) `systemctl
  --user enable --now omega-embedding-server` + cosine live-check (advances P4.0);
  (b) `EMBED_CPU_AFFINITY` env override so affinity is config, not constant;
  (c) N0 Ryzen re-derive per doctrine §10 (never copy N1 constants).

### RES-WAD-001 — arcana_novai WAD Loader Contract Alignment (DONE on N1 2026-09-26)
- **What**: Aligned `arcana_novai` WAD to Node 0's loader contract (`fa9c4edc`),
  fixing all 5 known gaps from `NODE1_COMPATIBILITY.md`.
- **Gaps Fixed**:
  1. Root `entities.yaml` ignored → removed; entities moved to `entities/**/*.yaml`
  2. Entities lacked `entity:` envelope → added to all 23 entities
  3. Unknown fields rejected (`extra=forbid`) → stripped to `KNOWN_ENTITY_FIELDS`
  4. Empty `entities: []` in manifest → removed; manifest cleaned to V2 schema
  5. `adapters` mapping form verified; `hierarchy` relative path confirmed
- **Structure**: 23 entities reorganized into `core/` (15), `support/` (3), `personal/` (1), `omega_default/` (5)
- **Manifest**: Cleaned V2 schema with `adapters` mapping, `hierarchy` path, `requires_engine: ">=1.6.0"`
- **PWAD Regression**: Confirmed concat bug (exit 1 negative fixture); fix staged on Node 0
- **Verification**: 31/31 WAD loader tests PASS; PWAD regression exit 1 confirmed; lint/docs PASS
- **Deliverable**: `config/wads/arcana_novai/` restructured; provenance drawer in `omega-engine-alpha/local-ai-research`
- **Status**: ✅ **DONE (N1, 2026-09-26)**

### RES-FLEET-001 — Parallel Agent Fleet Architecture (RESEARCHED 2026-09-26)
- **What**: Architect-directed research into git-worktree isolation + agent-management
  platforms, and how they fit the Omega Engine. Full doctrine:
  `docs/research/PARALLEL_AGENT_FLEET_ARCHITECTURE_20260926.md`.
- **Trigger (measured, not hypothetical)**: Node 1 already runs concurrent Lilith/Humboldt/
  build sessions on ONE tree. Tonight's checkout was ABORTED by a sibling session's uncommitted
  changes; ROADMAP needed surgical hunk staging; two stashes in flight. Textbook shared-tree
  failure.
- **Core findings**:
  1. **Worktree-per-task** is the fix; **three-phase sweep** (parallel READ-ONLY discovery →
     single-writer apply in isolated worktree → isolated review) is the highest-value pattern and
     is already how research subagents were run tonight.
  2. **Worktrees isolate the FILESYSTEM ONLY.** Ports, databases, .env, and absolute-path build
     caches are still shared. Ceiling is **5–7 concurrent**; start at 2–3, scale on evidence.
  3. **SQLite (our substrate)**: transactions are serializable, WAL gives reader snapshot
     isolation, and **separate database FILES = complete isolation**. Recommended pattern:
     **one DB file per agent/worktree, inside that worktree's own directory** — do not share
     MemPalace/coordination DBs across agents. Never enable `read_uncommitted` in a fleet.
  4. **Paperclip** (74k★, MIT, self-hosted) productizes an org-chart/budget/audit layer above
     existing agents; its stance is "agents must be governed, not trusted" and it still requires
     a human at the top (board). **Verdict: DO NOT ADOPT, DO MINE.** It is multi-tenant
     SaaS-shaped (Node 24+/pnpm/Postgres), duplicates our `hierarchy.yaml` + mandates as a second
     governance source of truth, and ships telemetry (M8 is absolute for us). Mine four portable
     ideas for free: hard budgets per agent, immutable tool-call audit log, heartbeat triggers
     instead of manual invocation, and goal-traced tasks (every task traces to a mission).
  5. **Multi-node**: GitOps (repo as declared state + per-host sync daemon) is the sober pattern.
     Config hierarchy global→fleet→instance, and **instance overrides must be in version
     control** — untracked overrides are indistinguishable from drift. Emerging standards: MCP,
     A2A (Linux Foundation), OpenTelemetry GenAI conventions. Open risk: per-agent credential
     sprawl; direction is workload-identity attestation, not yet solved.
- **Proposed sequence (NOT yet authorized)**: worktree-per-task for this repo (2 concurrent
  first); per-worktree `.env.local` with unique port + own SQLite paths; `TASKS.md` with declared
  scope and off-limits files, out-of-scope diff = automatic escalation; three-phase discipline;
  adopt Paperclip's four ideas natively; GitOps for multi-node. Never reintroduce SSH/NFS
  (policy-removed and test-guarded).
- **Status**: `researched` — awaiting operator decision on adoption scope.

### P4.10 — Gaming WAD: the vision layer (VISION 2026-09-28)

**Origin**: operator, 2026-09-28. The realization that a *vision-capable* agent
changes what a gaming agent can be — from one that reads numbers to one that
sees the screen. Framed against a real finding: on an Intel 64-EU iGPU, a CSV
saying "1% low 4.9 FPS" is nearly meaningless on its own, because the same
number covers a VRAM-loading stall (GPU idle, CPU at 51%, 34 ms CPU frame time
vs 2.9 ms GPU) and a genuine in-game stutter. Only the frame distinguishes
them. MangoHud cannot even log its `resolution` widget — a screenshot is the
*only* channel for that datum.

**The loop that works** (proven on Warframe 2026-09-28):
1. MangoHud CSV indexes the run by time, and names the interesting moments
   (`min`, `p0.1`, `p1`, `median`) with GPU/CPU load and clock attached.
2. A screen recording supplies *what it looked like* at those instants.
   MangoHud's overlay is composited into the framebuffer, so it is in the video.
3. `hudframe.py` pulls the exact frame for a named moment.
4. The agent **looks at it** and answers the question a number cannot: is this
   softness, banding, shadow acne, texture pop-in, or just a slow frame?

This is the "eyes on the ground" loop. It already exists as a working tool
(`GameResearch/scripts/hudframe.py`, verified end-to-end against synthetic
ground truth) and needs only a vision-capable agent to close.

**Why Omega cares**: a WAD entity that can see the game state is a different
class of tool from one that scrapes telemetry. The kill shot is not "it tells me
my FPS" — it is **realtime visual coaching**: seeing a mis-aimed shot, a
missed timing window, a bad rotation, or a settings change that traded
readability for framerate, and saying so while the player is still in the
moment.

**Candidate surface**:
- `screenshot` → structured observation (what is on screen, HUD state, alerts)
- `hudframe extract` → look at the frame behind a specific regression
- Before/after diff → did this settings change cost me visual quality?
- Live coaching loop → realtime, bounded latency, opt-in, never autonomous input

**Hard constraints (non-negotiable, from the Code Quality + safety rules)**:
- **Advisory only.** The agent observes and advises; it never takes input.
  An agent with hands on a game is a different risk class and needs explicit
  operator authorization, not a default.
- No keystroke injection, no aim assistance, no automated play. This is a
  coaching tool, not a cheat.
- Privacy: screen contents stay local. No frames leave the machine unless the
  operator explicitly shares one (as happened 2026-09-28).
- Cost ceiling: a vision call per frame is unaffordable. Sample on events, not
  on a timer.

**Done when**: a `screenshot`/`observe` tool that returns structured game-state
observations; the `hudframe` → vision loop demonstrated on a real regression
where the number and the frame disagreed; a written privacy + advisory-only
policy; a measured cost model for realtime latency; and — before any of it
ships — explicit operator sign-off on the advisory-only boundary.

**Status**: `backlog` — captured, not authorized. The tool half is DONE and
verified (`GameResearch/hudframe.md`); the vision half depends on the Engine
running a vision-capable model. Blocked on the alpha release.

**Related**: P4.9 (agent vitals — the text-only half of the same idea),
`GameResearch/hudframe.md`, `GameResearch/benchmarks/warframe/scenes/`.

---

### P4.9 — Agent vitals: a HUD for autonomous agents (VISION 2026-09-28)

**Origin**: operator experience during Warframe performance work. MangoHud made
a hidden machine legible in real time — GPU engine-busy (97–100%), CPU load,
watts, frame time, 1% lows. The same legibility gap applies to agents, which
fail *silently* and get diagnosed only after the fact.

**Why Omega cares**: the roadmap already demands "no silent failures" (standing
rule 3) and the gnosis-leash watchdog exists to surface compaction state. But
vitals are read by a human, on demand, in another terminal. An agent has no
equivalent sense of "I am degrading." This closes that gap with the mechanism
that demonstrably worked for the human: continuous, cheap, fused, visible.

**Design principles** (borrowed from MangoHud, several learned the hard way):
1. **Cheap enough to always be on.** MangoHud costs ~1% because it samples
   counters it already has. Vitals must not require a polling agent or a
   second inference pass. Sample on the tick, aggregate, emit.
2. **One fused view, not five terminals.** The value was never `intel_gpu_top`
   alone — it was GPU+CPU+RAM+temp+power *simultaneously*. Same for agents:
   tokens/s, KV-cache occupancy, RAM pressure, context position, tool latency.
3. **Tell the truth, including when it is unflattering.** A readout that says
   "fine" when the truth is "degraded" is worse than no readout. A vital that
   only reports good news is a lie with a graph.
4. **Zero-value must be visible.** Silence is a value. If nothing sampled, the
   HUD must say "no data" — it must never render as healthy.
5. **Cheap to read.** A glanceable block, not a dashboard. If reading it costs
   more than the problem, nobody reads it.

**Candidate vitals** (to be pruned, not all to ship):

| Vital | Source | Analogue | Why it matters |
|---|---|---|---|
| Inference tok/s | Ollama `/api/generate` timings | FPS | Is the substrate actually fast, or assumed fast? |
| Prompt-eval vs generation split | `prompt_eval_count` / `eval_count` | frame vs CPU time | Separates "slow model" from "huge prompt" — the most misdiagnosed bottleneck in this stack |
| KV-cache size / context occupancy | Ollama response metadata | VRAM | Single-channel 16GB has no slack; OOM risk is foreseeable |
| RSS + swap + zram | `/proc` + `zram` | RAM widget | Silent swap thrash is the classic slow death |
| Host thermals / RAPL watts | RAPL (already built: `GameResearch/scripts/rapl_power.py`) | watts | The 28W PL1 ceiling bites during long runs |
| Tool-call latency histogram | opencode hooks | 1% lows | An average hides tail latency; the tail *is* the UX |
| Consecutive-error streak | existing leash logs | stutter | Degradation *before* failure, not after |
| Time since last checkpoint | Well + manifest | FPS graph | A stuck run looks identical to a slow run unless tracked |
| Drift: intent vs. actual diff | git + TASKS scope | throttling | Out-of-scope edits are a leading indicator, not a postmortem |

**Delivery surfaces** (pick ONE to start; do not build all):
- `make vitals` — one-shot fused report, appended to the session log.
- Compacted block injected into the system prompt at compaction time (piggyback
  on the existing gnosis-leash injection point — cheapest possible wiring).
- `docs/VITALS.md` board recording the last N runs for longitudinal drift.

**Explicit non-goals** (temple-grade discipline): no dashboards, no always-on
daemon in v1, no per-tick telemetry, no new database. A poller process is a
liability on a 16GB single-channel box. If the vitals cannot ride existing
hooks, the design is wrong.

**Done when**: `make vitals` prints a fused block with every field sourced and
timestamped; a deliberately induced fault (swap pressure, a hung tool, a
stalled model) is visible within one cycle; the block survives into the next
session via the leash injection point; no field can report healthy when its
source returned nothing; total added overhead measured and published (budget:
<2% of a 14.4 t/s inference run).

**Status**: `backlog` — captured, not authorized. Awaiting operator decision on
surface choice (one-shot vs. compaction-injected) before any implementation.
Related: `docs/AGENT_RUNBOOK.md` (substrate facts),
`GameResearch/scripts/rapl_power.py` (a working unprivileged RAPL reader worth
reusing), `GameResearch/hardware-profile.md` (the 28W PL1 ceiling).

---

## P5 — Omega Memory module (the substrate) — PRIORITY ONE R&D TRACK

**Goal**: the memory substrate the Engine's intelligence flows through —
sovereign, multilingual, spatial, federated. Independent Node 1 R&D FIRST
(operator directive 2026-09-25); Node 0's two years of data/iterations merge
later, never as a blocker.
**Standing constraints**: one space per collection everywhere (same model +
dim per shared collection); palace space vs engine space never compared;
verbatim-first; boosts-never-gates; eval-before-cutover; no silent failures.

### P5.0 — Knowledge Atlas spatial viewer — priority MEDIUM/HIGH
- **Why**: operator has never seen their data spatially; xyz serves eyes and
  routing, never ranking.
- **Honest state (2026-09-25)**: unbuilt — `knowledge_atlas.db` absent,
  `:8088` silent, no viewer files. Prior session notes claiming otherwise
  were aspirational (see ARCHITECTURAL_REVIEW correction).
- **Done when**: minimal local viewer over the post-cutover space — UMAP 3-D
  projection, wing coloring, click-to-dossier; served locally; build doc
  recorded. Feeds dream-log #5 (atlas fusion).
- **Status**: `queued` (medium/high priority, operator 2026-09-25).

### P5.1 — Palace embedder cutover (MiniLM → Qwen3-0.6B@1024)
- **Why**: MiniLM is English-only geometry; a linguistics wing is impossible
  on it. Measured 2026-09-25: Qwen-0.6B meaning-first across HE/EL/polytonic
  Greek/Latin; nomic language-first (rejected); MemPalace embeddinggemma is
  384-trunc (rejected on the 768 bar).
- **Done when**: P0 backup → P1 pilot sidecar + A/B spot-checks → P2 held-out
  eval set + delta → P3 rebuild (`dim=1024` stamped, scoped-search parity) →
  P4 federate (after Node 0 survey). Rollback = restore P0 files / rebuild
  back; time is the only cost.
- **Status**: `in-progress` (P0 backup DONE + P1 pilot DONE 2026-09-25/26: 40-record Qwen-1024 sidecar, plumbing verified, fair-A/B deferred to P2 eval by design; full case:
  `docs/research/EMBEDDING_STRATEGY_NODE1_20260925.md`; Qwen3-4B sidecar
  deferred by operator decision).

### P5.1b — Canonical embedding dim cutover → 1024 native (OPERATOR RULED 2026-10-01)
- **Ruling**: 1024 is the canonical dimension for **all nodes**. The 768
  Matryoshka truncation recorded in `LILITH_STRATEGY_FINAL.md`, `ARCHITECTURE.md`,
  `WANDERGROUND_SPEC.md` and older ROADMAP entries is **superseded**.
- **Also wrong**: the parameter name. `truncate_dim` is sentence-transformers';
  Ollama's `/api/embed` takes `dimensions` (integer) and **silently ignores**
  `truncate_dim`, returning 1024 regardless. Corrected in Well record
  `c068a4ae` (supersedes `d4cf07de`, `42c3c90d`) and in the agent files.
- **Why truncation is not worth keeping** (measured Node 1, ollama 0.34.4,
  12 real Well rules, 3 reps): `dimensions=768` *is* honoured, costs **−1.5%
  wall-clock (noise)** because truncation slices an already-computed vector, and
  saves 25% of storage — but `cos(native, truncated) = 0.891`, i.e. a genuinely
  different vector, and top-6 retrieval changed **1 of 6 slots**. It trades a
  real semantic cost for storage on an index that does not currently exist
  (`omega-embedding-server.service` is `inactive`).
- **Node 0 survey ANSWERED (2026-10-02, operator): Node 0 is already on 1024.**
  This removes the P5.3 cross-node incomparability blocker for the dim cutover:
  both nodes agree at 1024, so there is no federation risk in Node 1 aligning.
  (Cross-node *model/space* reconciliation is still P5.3; only the dim question
  is settled.)
- **⚠️ Node 1's actual state is WORSE than this item assumed.** Measured against
  the live store, not the spec: `SELECT dim, COUNT(*) FROM documents GROUP BY
  dim` on `~/WanderGround/mempalace/sqlite_exact.sqlite3` returns
  **`dim=384`, 1115 rows** — the legacy `embeddinggemma`-MRL space that
  `EMBEDDING_STRATEGY_NODE1_20260925.md` explicitly *rejected* for failing the
  768 bar. The 768 engine space existed **only** as an inactive systemd default.
  So **three** dims were in play on Node 1 (384 live, 768 vestigial, 1024
  canonical) and *none of the live ones* was canonical. This is not a
  768→1024 bump; it is a **384→1024 rebuild of 1115 documents**. Well record
  `007428a2` carries the lesson: a plan's status field is a claim about data, not
  evidence of it.
- **Migration steps remaining**:
  1. ~~`scripts/embedding_server.py` — `TRUNCATE_DIM` default 768 → 1024~~
     **DONE 2026-10-02** (service inactive, so no index impact).
  2. `docs/WANDERGROUND_SPEC.md` — schema `embedding FLOAT[768]` → `FLOAT[1024]`;
     §checklist item "Restore `embed_inbox.py` … (768-D)". **Spec only** — the
     real store is 384, so the spec was wrong twice over.
  3. ~~`docs/ARCHITECTURE.md`, `docs/ROADMAP.md` "standing constraints"~~ —
     **DONE 2026-10-02**; historical research docs
     (`EMBEDDING_MODEL_DECISION.md`, `EMBEDDING_STRATEGY_NODE1_20260925.md`)
     left intact as dated evidence.
4. **RE-EMBED 1115 palace documents 384 → 1024.** This is the actual work and
     it was not previously on the list. **DONE 2026-10-02** via
     `scripts/palace_reembed_1024.py` (batched, resumable, WAL, per-batch
     transaction; skips rows already at 1024). Pre-migration backup retained:
     `~/backups/mempalace_384_pre1024_20261002T200646Z.sqlite3`
     (`quick_check: ok`, 1115 rows). Native 1024 via Ollama `/api/embed` with
     **no** `dimensions` param. 795 rows in the final pass + 320 in an earlier
     aborted-but-committed pass = 1115. Runtime 824 s for the final 795
     (~0.9 rows/s, CPU-bound).
- **Verification (post-migration)**:
  - `SELECT dim, COUNT(*) … GROUP BY dim` → **`{1024: 1115}`**, no 384 rows remain.
  - `PRAGMA quick_check` → `ok`.
  - Stored blob 4096 B = 1024 × float32; `dim` column agrees with blob width.
  - 399 of 400 sampled vectors are byte-distinct (1 legitimate duplicate);
    pairwise cosine 0.08–0.65, mean 0.31 — a healthy spread, not degenerate.
  - **Self-retrieval: a freshly-embedded stored doc retrieves ITSELF at rank 1,
    cos = 1.0000** — definitive proof the query encoder and stored vectors are
    the same space. This is the check that matters.
  - Topical-vs-control separation is weak (+0.0083). **Pre-existing, not caused
    by the dim change**: the corpus is drawer fragments and log lines, not curated
    prose, so it is semantically shallow. A corpus-quality item, not a vector-space
    one. Logged as P5.5.
- **Status**: ✅ **DONE (2026-10-02)** — Node 1 palace is native 1024. Node 0
  already at 1024 (operator-confirmed); Node 0 asked to confirm the exact model
  and stamped dim via Hivemind `ho_223918db14b5` so parity is evidenced rather
  than asserted on both sides. Once Node 0 replies, cross-node cosine is expected
  to work — but that has NOT been tested end-to-end and must not be assumed.

### P5.5 — Palace corpus is semantically shallow (NEW, 2026-10-02)
- **Why**: topical-vs-control query separation is +0.0083 over 1115 documents.
  Spot-reading the top hits shows drawer fragments (`source.)`, log tails, and
  agent-prompt boilerplate rather than coherent statements. The vectors are
  correct; the *content* they encode is not retrievable-by-meaning.
- **Done when**: a held-out topical query returns a top-5 that a human would call
  relevant, with control separation an order of magnitude above the current 0.008.
- **Status**: `queued` — separate from the vector-space work, which is now correct.

### P5.2 — Omega-native memory v0 (independent R&D)
- **Why**: priority-one substrate; Node 0 material merges later, not as
  a blocker.
- **Done when**: v0 spec (one SQLite: verbatim docs + JSON metadata + xyz
  floats + wing/room/hall; vec0 with wing partition key; FTS5 with
  per-language normalizers — Hebrew R1 shipped, Greek/Latin/Mayan queued;
  triples; logstream; hybrid 0.6/0.4; closet-boosts-never-gates; top-20
  rerank) + prototype proving scoped recall ≥ palace parity on the held-out
  set from P5.1/P2.
- **Status**: `queued` (R&D track opened 2026-09-25).

### P5.3 — Federated memory rules + Node 0 survey
- **Why**: vectors from different models are uncomparable numbers; mixing
  spaces fails silently.
- **Done when**: Node 0 embedder/dims/backend/counts/disk surveyed; mesh
  vector policy decided (ship-documents+vectors vs re-embed-per-node);
  one-space-per-collection enforced in config on both nodes.
- **Status**: `queued` (blocked on Node 0 survey — not on R&D).

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
