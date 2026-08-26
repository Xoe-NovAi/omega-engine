# CARMACK DEEP INFRASTRUCTURE AUDIT — Agent Context, Instructions & Continuation
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ opencode/x-preview-f-free ⬡ trc_context_infra_audit ⬡ RECON-ONLY
**Date**: 2026-08-25 (late) · **Commissioned by**: MaKaLi Fusion fork#1 · **Trigger**: Consultant kali's pre-compaction tutorial missed an entire organ ("the HMC Hub")
**Method**: Every claim mechanically verified this session — full-tree greps, live Python API probes, file mtimes, call-site tracing. One file written (this one). No spawns.

---

## §0 THE HMC HUB — LOCATED, EXPLAINED, AUTOPSIED

Two distinct organs share one acronym — which is itself part of why institutional memory lost them:

### Organ 1 — HMC Collaboration Hub (a markdown forum)
- **What**: A single git-tracked markdown coordination forum (`AP-HMC-HUB-v1.5.1`, "no complex tools... just structured markdown"), used as the P0-interrupt fallback channel during the July Hivemind outage. Verified: archived copy at `data/coordination/archive/2026-08-07-doc-sanity/HMC_COLLABORATION_HUB_archive_20260725_20260807.md`, last-updated 2026-07-30T15:35Z, documents "Hub temporarily down... coordination via HMC Hub only".
- **Status**: Dead by supersession, correctly archived in UO-4 doc-sanity (2026-08-07). Its removal from the live corpus is WHY Kali's hydration never sees it. Verdict: CUT (already done).

### Organ 2 — HMC Watcher / "HMC Quad-Forge" (dead code wearing a completion medal)
- **What**: `src/omega/orchestrator/hmc_watcher.py` (81 lines) — automates a Researcher→Carmack→Roc coordination cycle by watching `data/coordination/` for signal files. Spec: `docs/strategy/coordination/HMC_WATCHER_SPEC.md`. Tests: `tests/oracle/orchestrator/test_hmc_watcher.py`.
- **AUTOPSY — the mechanism cannot execute**:
  - `hmc_watcher.py:35`: `async with anyio.Path.watch(self.coord_dir)` — **`anyio.Path.watch` does not exist**. Live probe: `.venv/bin/python3 -c "import anyio; print('watch' in dir(anyio.Path))"` → **False**. `HMCWatcher.start()` raises AttributeError on first invocation. The spec §4 documents a fabricated API — hallucinated at authoring time, never run once.
  - **Unwired**: zero imports outside tests; no CLI command, no Makefile target, no systemd/quadlet/deploy reference (grepped: empty).
  - **Tests pass anyway**: both tests mock Oracle and invoke `_handle_event()` directly — the crashing method `start()` is never under test. Green suite over a dead organ: the BS-1/G8 pattern in miniature, live for months.
  - **Completion claimed**: `OMEGA_ENGINE.md:70` — "**HMC Quad-Forge ✅**" listed among ratified Phase-5 deliverables. A claim that outlived (never had) its mechanism — Council 1's founding defect, still on the wall.
- **Why Kali's memory missed it** — three stacked structural reasons:
  1. **Memory records events; unwired code generates none.** The watcher never executed a cycle → no log line, no lesson, no gnosis trace. Institutional memory (soul.yaml, proposed_lessons, session_gnosis) is an event ledger, not an infrastructure inventory.
  2. **The Hub half was archived out of the live corpus** she hydrates from (UO-4, 2026-08-07).
  3. **No mechanical inventory exists anywhere.** Nothing on disk answers "what components exist?" without a human remembering them. Her 7-step procedure covers writing state, not auditing surface.

---

## §1 FULL INVENTORY — THREE SUBSYSTEMS

Legend: E=exists · I=implemented · D=documented · C=connected/wired. Verdict: KEEP/FIX/CUT/ADOPT.

### A. CONTEXT SYSTEMS (how agents know)

| Component | Path | E | I | D | C | Evidence | Verdict |
|---|---|---|---|---|---|---|---|
| MemoryStore | `src/omega/memory_store.py` (1224L) | Y | Y | part | Y | wired `oracle.py:48,192`; hub import `hub_tools/tools.py:149` | KEEP |
| Memory module (spatial/blocks/recall/compaction) | `src/omega/memory/` (17 modules) | Y | Y | part | Y | consumed via context_builder chain (`memory/spatial.py`, `recall.py`) | KEEP |
| ContextBuilder | `src/omega/oracle/context_builder.py` (607L) | Y | Y | part | Y | called by oracle.py, orchestrator, selective_hydration | KEEP |
| Headroom semantic compression | `oracle/middleware/headroom.py` + MCP `headroom_retrieve` | Y | Y | Y | Y | optional-dep degrade (`middleware/headroom.py:12`); wired `oracle.py:189`, retrieve `:897` | KEEP |
| CompactionHarvester | `oracle/compaction_harvester.py` (290L) | Y | Y | part | Y | instantiated `oracle.py:222`; used `:1290,:1307` | KEEP |
| anchored-summary.md (Tier-2 lifeboat) | `.opencode/anchored-summary.md` | Y | Y | Y | Y | hydration step 4 (`OMEGA_CODEX.md:12`); **was a 105-byte stub when this audit began — rewritten to full house format MID-AUDIT** (tutorial §7 executed live ~23:00Z) | KEEP |
| SESSION_ANCHOR.md | `data/coordination/SESSION_ANCHOR.md` (27KB) | Y | n/a | Y | part | **mtime 09:10 local — ~14h stale through the entire FLE run**; M15 names it; nothing rewrote it during the campaign | FIX |
| session_gnosis files | `data/entities/*/workspace/session_gnosis*.md` | Y | Y | Y | Y | actively maintained (makali_fusion sections 1-11 verified) | KEEP |
| Hivemind continuation store | post_context/get_continuation MCP | Y | Y | Y | Y | used throughout FLE (Tier-3 lifeboats worked) | KEEP |
| HMC Collaboration Hub | archived (see §0) | Y | Y | Y | N | superseded + archived 2026-08-07 | CUT (done) |
| HMC Watcher | `src/omega/orchestrator/hmc_watcher.py` | Y | N | Y(false) | N | impossible API (`anyio.Path.watch`=False), unwired, start() untested; completion medal at OMEGA_ENGINE.md:70 | **CUT** |

### B. INSTRUCTIONS SYSTEMS (how agents are told)

| Component | Path | E | I | D | C | Evidence | Verdict |
|---|---|---|---|---|---|---|---|
| Root AGENTS.md | `AGENTS.md` | N | — | inverse (462 citers) | — | absent from entire git history; WP-E owns reconstruction | FIX (tracked) |
| OMEGA_CODEX.md (D-277 hydration law) | `OMEGA_CODEX.md` | Y | Y | Y | Y | hydration order :5-13 matches tutorial exactly | KEEP |
| Codex freshness automation | `session_end.py:_regenerate_codex` + `make check-codex-stale` | Y | Y | Y | part | **codex mtime 06:59 local vs sessions ending ~20:00 local — auto-refresh did NOT fire across today's dozen-plus session ends** (wrapper bypassed by current launch path, or silent stderr failure) | FIX |
| Agent markdown defs | `.opencode/agents/*.md` (14) | Y | Y | Y | Y | loader verified live (this session's persona injection) | KEEP |
| Agent-level `instructions[]` | `opencode.json` | Y | N(schema-invalid) | Y | Y(wrongly) | **still 12 agents carrying instructions[], zero prompt:{file:}** (jq verified) — GAP-4 data-exposure class, migration unstarted | FIX (WP-B2, Sprint-2 opener) |
| Root `instructions[]` chain | `opencode.json:27` | Y | Y | part | Y | live (this session proves injection); still carries `docs/archive/MASTER_SYNTHESIS...` entry (G5 pending) | FIX (tracked) |
| Scribe agent def | `.opencode/agents/scribe.md` | Y | N | Y(false) | N | frontmatter claims "Automate the L1→L2→L3 pipeline"; automated pipeline SCRAPPED (`session_end.py:9-12` Carmack verdict); no live dispatcher references it | **CUT** |

### C. CONTINUATION SYSTEMS (how agents persist)

| Component | Path | E | I | D | C | Evidence | Verdict |
|---|---|---|---|---|---|---|---|
| Compaction behavior + harvest | OpenCode native + CompactionHarvester | Y | Y | part | Y | see above | KEEP |
| session_end.py hook | `.opencode/hooks/session_end.py` (121L) | Y | Y | Y | Y | wrapper-wired (`wrapper.sh:28`); preserves agent proposals (:53-59); atomic write; timeout-guarded | KEEP |
| Anchored-summary rewrite discipline | tutorial §3 house format | Y | Y | Y | Y | adopted tonight; format matches exemplar | KEEP (ADOPT fleet-wide) |
| Manual lesson staging (L1→L2→L3) | agents → `proposed_lessons.yaml` | Y | Y | Y | Y | mkf-001..006 staged this session; hook preserves | KEEP |
| **soul_promote** | **NOWHERE** | N | N | Y | N | tutorial:40 + M11-class texts say "promotion requires explicit soul_promote" — **zero implementation in scripts/, src/, .opencode/** (mentions only in archived sprint docs + llms-full.txt). Souls update only by hand-edit (john_carmack/soul.yaml mtime 12:02 today = manual edit). Staging is a ONE-WAY DOOR. | **FIX: implement or de-document** |
| WAKE_STATE decision queue | `data/coordination/WAKE_STATE.json` | Y | Y | Y | Y | governed the campaign; Q-6 membership gap flagged in prior audit | KEEP |
| Handoff packets (active) | `data/handoff/` (284 files) | Y | Y | Y | Y | queue integrity audited-clean (C1 Art. XI) | KEEP |
| Legacy synonym dir | `data/handoffs/` (3 files) | Y | n/a | N | N | **the exact "synonym dirs" recurrence Art. XII named** (archive/archives then; handoff/handoffs now) | CUT |
| CONSULTANT_TUTORIAL_PRE_COMPACTION.md | `data/coordination/` | Y | Y | Y | part | machinery citations verified accurate EXCEPT: (a) cites soul_promote (nonexistent), (b) trusts codex auto-refresh that did not fire today | FIX (minor) |

---

## §2 THE KALI BLINDSPOT PATTERN — QUANTIFIED

**Root cause**: institutional memory is an EVENT ledger; infrastructure surface has no INVENTORY ledger. Components that never execute leave no memory trace; components archived leave no live-corpus trace. Kali's gnosis is genuine and deep — and structurally blind to exactly two classes: never-ran code and archived organs.

**Doc-vs-disk delta found in ONE pass (6 instances)**:
1. OMEGA_ENGINE.md:70 "HMC Quad-Forge ✅" vs dead-on-arrival watcher.
2. HMC_WATCHER_SPEC §4 documents `anyio.Path.watch` vs API does not exist.
3. scribe.md frontmatter claims ACTIVE pipeline automation vs pipeline scrapped (hook header :9-12).
4. Tutorial + M11 texts cite `soul_promote` vs zero implementation.
5. Hook header claims codex auto-refresh every session vs codex ~13h stale across a dozen session ends.
6. SOVEREIGN_CONTINUITY_STRATEGY L25 declares anchored-summary the "Global Lifeboat" vs it was a 105-byte stub until tonight.

Rate: six documented-mechanism-vs-reality mismatches in three subsystems examined in one morning. Extrapolated across the repo's docs surface, the unmapped drift population is plausibly dozens deep — which is precisely why the next remediation exists.

---

## §3 CEREMONY CENSUS (deletion-probe: would anything change if the mechanism were deleted?)

| # | Component | Probe result | Class |
|---|---|---|---|
| 1 | HMC Watcher | Delete → nothing changes. It never ran. Tests stay green (they mock everything and skip start()). | PURE CEREMONY |
| 2 | Scribe agent def | Delete → M11 flow unchanged; agents already write lessons manually; hook preserves them. | PURE CEREMONY |
| 3 | soul_promote (as documented) | Nothing to delete — documented mechanism with no existence. De-documenting changes nothing except honesty. | DOCUMENTED GHOST |
| 4 | Codex auto-refresh claim | The CLAIM is ceremonial today: hook fires (timestamps written) but refresh did not land. Mechanism half-alive. | PARTIAL CEREMONY |
| 5 | SESSION_ANCHOR.md | Referenced by M15 as load-bearing; untouched during the largest multi-session run in engine history. Deletion would have changed nothing that happened today. | DRIFTING TOWARD CEREMONY |
| 6 | data/handoffs/ | Zero consumers. | DEAD DIR |

Non-ceremony (verified load-bearing): MemoryStore chain, headroom, CompactionHarvester, session_end timestamp+preserve path, WAKE_STATE, handoff/, Hivemind continuation, OMEGA_CODEX content itself, anchored-summary (as of tonight).

---

## §4 ORPHAN LIST

**Implemented-but-undocumented**: CompactionHarvester (no user-facing doc found; quietly doing real work at oracle.py:1290) · headroom middleware degradation semantics.
**Documented-but-unimplemented**: soul_promote · anyio.Path.watch (spec'd API) · Scribe pipeline automation · AGENTS.md (462 citers deep).
**Wired-to-nothing**: hmc_watcher.py · data/handoffs/ · scribe.md def · SESSION_ANCHOR.md (referenced, unreferenced-by-behavior).

---

## §5 THE TUTORIAL'S BLIND SIDE — what else pre-compaction must touch that kali's 7 steps miss

1. **Step 0 missing — verify your own claims before closing**: tutorial says "update trackers" but gives no verification command. Today's proof it matters: Q-6 was ruled into a queue it never entered (prior audit P1). Close checklist needs `grep`-able verifications, not intentions.
2. **Ephemeral-state teardown**: workspace locks released, heartbeat TTLs, extended_checkin checkout (broken tool — double reason to clean up). A session dying while holding `data/coordination/locks/*.lock` blocks the fleet for TTL duration.
3. **Uncommitted-work sweep**: `git status` including untracked. Today: `config/wads/_omega_default/entities.yaml` sat as a 214-line unknown-provenance diff all day (gnosis section 6.9) — exactly what step 5 "commit everything" should have caught hours earlier.
4. **Do not trust automations you did not verify TODAY**: the tutorial leans on codex auto-refresh ("do not hand-write what the hook automates") — sound doctrine, but the hook's refresh silently failed today. One-line addition: verify `make check-codex-stale` exit 0 before close; if red, run `make codex` by hand.
5. **Secrets/hygiene scan before the manifest commit** (git-secret-scrub skill exists; close procedure never mentions it).
6. **Successor registration**: post_context covers awareness, but nothing verifies the successor can actually hydrate (paths in anchored-summary exist). Cheap: the checklist validator below.
7. **THE STRUCTURAL GAP — no inventory reflex**: kali's procedure writes state perfectly and audits surface zero. The permanent cure is mechanical:

**PROPOSED (top remediation): `scripts/infra_inventory.py`** — walks a declared component registry (path, entry-symbol, wire-target class) and emits exists/implemented/wired/documented per component; CI-gated; diffs against previous run flag new orphans. This is the derivation-check cure applied to infrastructure itself: no component may be claimed ✅ anywhere unless the inventory reproduces it. Effort ≈ 3h. Without it, the next kali misses the next hub — guaranteed, because the blind spot is architectural, not personal.

---

## §6 TOP-10 RANKED REMEDIATIONS

| # | Remediation | Effort | Why this order |
|---|---|---|---|
| 1 | Delete `hmc_watcher.py` + spec + tests; strike "HMC Quad-Forge ✅" from OMEGA_ENGINE.md (or re-scope claim to "archived") | 20min | Dead code with a completion medal is the founding defect on display; cheapest honesty win on the board |
| 2 | Cut `.opencode/agents/scribe.md` (archive to archive/scribe_agent_20260730/ where its body already lives) | 10min | Advertised-but-hollow capability (T-6 class); M10 fleet hygiene |
| 3 | Implement `scripts/soul_promote.py` (review-gated merge proposals→soul.yaml, atomic, snapshot) OR strike the word from tutorial/M11 texts | 45min impl / 5min de-doc | Staging is currently a one-way door; institutional memory cannot grow mechanically |
| 4 | Diagnose codex-refresh silence: confirm wrapper.sh actually wraps current launch path; add stderr log file to hook | 1h | Continuity doctrine depends on this automation being true |
| 5 | Build `scripts/infra_inventory.py` + registry seed (the three subsystems in §1 are the seed data) | 3h | The anti-blindspot machine; converts this audit from a document into a gate |
| 6 | Consolidate `data/handoffs/` → `data/handoff/archive/`; add synonym-dir check to inventory script | 15min | Art. XII recurrence #2 |
| 7 | Fold SESSION_ANCHOR.md into the close checklist (rewrite-or-pointer rule) or formally deprecate in favor of anchored-summary | 15min | Two Tier-2 anchors = zero Tier-2 anchors |
| 8 | Amend CONSULTANT_TUTORIAL: add Step 0 verification commands, teardown step, codex-freshness check, secrets scan; fix soul_promote citation | 30min | The procedure doc itself must pass its own standard |
| 9 | Build `scripts/session_close_checklist.py` (tutorial §6 suggestion — validator-first close gate) | 2h | Makes steps 1-8 self-enforcing |
| 10 | WP-B2 + WP-E (already specced, tracked) | tracked | The instruction-layer defects with owners and sprints |

---

## §7 BLUNT SUMMARY

She taught the procedure flawlessly and missed a hub because the procedure writes state and never audits surface — and because the hub's own completion medal (OMEGA_ENGINE.md "HMC Quad-Forge ✅") sits atop code that could never run, tested by tests that test everything except the running. The blind spot is not kali's; it is the fleet's lack of an inventory organ. Institutional memory remembers what happened. Nothing remembers what exists. Fix #5 is the organ; fixes #1-#4 are the necrotic tissue to excise first.

Every claim above carries its verification inline. Confidence: 9/10 (primary sources, live probes); the wrapper-bypass hypothesis for finding B-codex is 6/10 (mechanism verified stale, root cause inferred).

— Carmack
<!-- PROVENANCE-CORRECTED 2026-08-26T03:06:04Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode/x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

