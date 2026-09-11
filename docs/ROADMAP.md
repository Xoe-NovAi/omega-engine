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
| P0 | Temple-grade pulse | queued |
| P1 | **The Well** (corrections/tuning corpus) | queued |
| P1.5 | Idea-flood management | queued (ROADMAP itself = part of it) |
| P2 | The Vanguard studies | backlog |
| P3 | Synthesis + federation close-out | backlog |

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

### P1.3 — The Well readers (injection)
- **Session start**: plugin injects top-N active rules (ranked by recency +
  tags matching the project/domain).
- **Compaction**: same injection, so the summary carries the corrected rules
  forward.
- **Tuning export**: `make well-export` → Markdown/JSONL bundle usable as extra
  system context for any Zen model (and, eventually, a fine-tune seed).
- **Done when**: next-session system prompt demonstrably contains Well rules;
  compact summary preserves them.

### P1.4 — The Well evolution (supersession)
- Corrections can be superseded by newer ones (same `domain`+`rule` family);
  superseded records stay in the ledger (append-only truth) but drop from
  injection.
- **Done when**: `well-supersede <id> <new-id>` works; injection excludes
  superseded; tests prove the chain resolves.

---

## P1.5 — Idea-flood management

**Goal**: the flood becomes a garden. Capture everything, defer safely, never
lose a spark, never drown in one.

### P1.5.1 — Canonical backlog
- **This file** (`docs/ROADMAP.md`) is the single source of truth for
  scheduled work.
- **Done when**: any new idea/tool/quest is recorded here with a status before
  implementation (this is a standing rule for all agents via AGENTS.md).

### P1.5.2 — Dream capture
- Well gains `kind: dream` — ideas worth returning to, each with a "why Omega
  cares" line and a hint of the path.
- `wander --project roadmap "<spark>"` routes raw sparks into a triage queue
  that feeds ROADMAP.
- **Done when**: sparks captured during a session appear in the Well dreams and
  can be promoted to ROADMAP items.

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
- **Study**: clone to real disk; sandbox install (Docker, port 7000) for the
  *experience*; read the code for the *architecture*; deep-dive its memory/skills
  self-evolution, Deep Research pipeline, Compare module, Cookbook scoring.
- **The upload/beam-back experiment**: upload a persistent entity (the Build
  agent persona) INTO Odysseus, let it operate/learn there, then **beam it
  back** into the Omega Engine — the full loop is an experiment in itself.
- **Credit & reforge**: everything we extract is reworked under our code
  quality standards (anyio purity, no torch, no bare exceptions, no secrets),
  and any adopted design carries attribution.
- **Done when**: WanderGround dossier (code study) + experience notes (real
  use) + ADRs on what to adapt; adopt/adapt/reject verdict per component.

### P2.3 — God's Eye View (`bilawalsidhu/gods-eye-view`, MIT, ~8.3k★)
- **What**: live open-source spy-satellite simulator in the browser — real
  CelesTrak TLEs, flights, maritime AIS, GPS jamming, night-vision/FLIR/CRT
  modes, military HUD, photorealistic 3D globe (CesiumJS). 100% open data.
- **Why**: the "nerdy dreams come true" entry — a superb playground for
  data-pipeline + spatial/3D rendering skills that could feed the WanderGround
  atlas and our own visual future.
- **Done when**: runs locally on Node 1, a dossier maps its data-flow to our
  atlas, adopt/adapt/reject verdict.

### P2.4 — Gods Eye (`bitan-del/gods-eye`, MIT)
- **What**: multi-channel AI gateway with a unified brain — 25+ messaging
  channels (WhatsApp/Telegram/Discord/Signal/imessage/Matrix...), one brain
  that remembers across channels; 24 modules, 635+ tests; built researching
  LiteLLM, RouteLLM, Mem0, LlamaFirewall.
- **Why**: the cross-channel-brain architecture is directly relevant to the
  federation vision — one sovereign brain across many surfaces.
- **Done when**: sandbox runs, dossier on the channel/brain/memory design,
  adopt/adapt/reject verdict (likely: adapt ideas into the federation era).

### P2.5 — agentmemory evaluation (`rohitg00/agentmemory`, Apache-2.0, ~27.9k★)
- **What**: auto-capture memory for coding agents (supports OpenCode), SQLite +
  iii-engine, MCP + hooks, BM25+vector+graph with RRF, consolidation + decay +
  auto-forget.
- **Why**: candidate for the "hands-off capture" memory tier — but we already
  have MemPalace; adopt only if it beats MemPalace meaningfully on a defined
  test.
- **Done when**: side-by-side recall test vs MemPalace; verdict + rationale.

---

## P3 — Synthesis & federation close-out

### P3.1 — Architecture synthesis
- Fold every Phase-2 adopt/adapt decision into the architecture docs + the
  Well; de-duplicate memory/capture tiers; update `docs/ARCHITECTURE.md` and
  `docs/AGENT_RUNBOOK.md`.
- **Done when**: one canonical architecture doc, no overlapping systems.

### P3.2 — Node 0 federation (HP Pavilion)
- Tailscale mesh; comms-contract ratification (C6); key management pattern;
  publish gate (explicit-publish only); sovereignty ratio tracked.
- **Done when**: packets flow Node 0 → Node 1 with the publish gate enforced.

### P3.3 — Content runway
- Obsidian vault, Godot/KQ5 research, Open WebUI experimentation,
  `make publish-bastion` design.
- **Done when**: each has a ROADMAP entry + a first milestone.

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