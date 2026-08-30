<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Mining Report 10 — Antigravity KB Scaffold (2026-06-05)

**Entity**: roc_racoon (Sovereign Miner)
**Date**: 2026-06-05
**Sprint**: H2-A (Data Hygiene + KB Scaffolding) — initiated by user directive
**Status**: 🟢 SCAFFOLD COMPLETE, GOLD LANDED

---

## §0 Mandate Received

User directive (verbatim, 2026-06-05):

> "Make sure we save all of this rich research you've done. All of this
> research should go in a specialized knowledge base, a sub-category of a
> larger CLI/IDE/Platform expert knowledge base. BUT there first has to
> be a place for the research to reside until it is properly vetted and
> reviewed by multiple agents. Do that, then I have something along those
> lines for you to dig deep into. Well, the failed agent had some
> excellent gnosis, but it hung before writing its report."

Three parts to the mandate:

1. **Save the research** — 8 files of rich Antigravity investigation
2. **KB structure** — specialized sub-category under larger CLI/IDE/Platform KB
3. **Staging first** — vetting area for unvetted research
4. **Recover the hung agent's gnosis** — best-effort reconstruction

---

## §1 The Heuristic: The Dirt is Where the Roots Are

The user's reference to the "failed agent's excellent gnosis" is a
**classic roc_racoon signal**. The dirt (failed/hung/stuck processes) is
where the roots (real gnosis) often hide. A successful agent writes
its report and moves on. A hung agent's INTENT remains in the
session_diff, in the tool calls, in the partial output.

Per the **Heuristic** (this entity's operating principle): when an
agent dies, the unfinished work is more valuable than the finished
work, because it represents the frontier of what the engine was
reaching for.

This is the **"Dirt is where the roots are"** principle: the surface
might be polished, but the foundation is where the real truth lives.
Failed agents expose the foundation.

---

## §2 What Was Built (Today's Sprint)

### 2.1 The KB Scaffolding

Created:
```
data/kb/
├── _staging/                                  ← UNVETTED research
│   ├── _protocol/
│   │   └── VETTING_PROTOCOL.md                ← How research gets promoted
│   └── cli_ide_platform/
│       └── antigravity/                       ← 9 gold files
│           ├── 00_MASTER_INDEX.md
│           ├── 01_PROVENANCE_LINEAGE.md
│           ├── 02_AUTH_MECHANISMS.md
│           ├── 03_PLUGIN_VS_CLI.md
│           ├── 04_QUOTA_REALITY.md            ← The "4 accounts in minutes" fact
│           ├── 05_8KEY_POOL.md
│           ├── 06_AGY_CLI_LIVE_TEST.md        ← User testimony, single-source
│           ├── 07_GEMINI_CLI_HARVEST_PLAN.md
│           └── 08_FAILED_AGENT_RECOVERY.md    ← Best-effort reconstruction
└── cli_ide_platform/                          ← CANONICAL (awaiting promotion)
    ├── _meta/
    │   └── DOMAIN_INDEX.md                    ← Master index
    └── antigravity/                           ← Empty until cross-vet completes
```

### 2.2 Total Gold Landed

- **9 files** in the Antigravity staging area
- **~50 KB** of rich, citation-bearing research
- **3 closed decisions** (D-AGY-01, D-AGY-02, D-AGY-03)
- **4 heritage citations** (WAD, netchan, Worse is Better, Multi-Index)
- **1 critical empirical fact** (4-accounts-in-minutes, with primary citation)
- **1 best-effort hung agent recovery** (reconstruction, marked SPECULATIVE)
- **1 vetting protocol** (Tier 0/1/2 + RACI matrix)

---

## §3 Key Findings (Distilled)

### Finding 1: The `agy` CLI is Ruled Out

**Empirical basis**: User test, 2026-06-05, 4 of 8 accounts burned in minutes.
**Implication**: Don't build any `agy` integration. Use OpenCode plugin path.
**Decision**: D-AGY-03 (closed, 2026-06-05).

### Finding 2: The 8-Key Pool Has Two Independent Pools

**Pool G (Gemini)**: 8 keys, weekly reset, all 8 fresh.
**Pool C (Claude + OSS)**: 8 keys, weekly reset, 5/8 exhausted.
**Implication**: Cross-pool switching gives a "second wind" mechanism.
**Decision**: 7-phase review plan allocates the 8 fresh Claude slots to high-stakes phases.

### Finding 3: The Plugin Death Was Silent (April)

**Symptom**: `~/.config/opencode/opencode.json` was using the OLD `"plugins": {obj}` format. After OpenCode 1.16.0, the format became `"plugin": [...]` (array). The plugin was loaded but not recognized, so Antigravity silently disappeared.
**Implication**: This is the M9 (Error Integrity) anti-pattern. The engine should detect silent failures and surface them.
**Counter-action**: User ran `opencode auth login` on 2026-06-05. Plugin re-authenticated. Needs session restart.

### Finding 4: The Hung Agent's Gnosis (Best-Effort)

**What it would have covered**: `agy` subcommand inventory, plugin system architecture, MCP integration paths.
**Why it doesn't matter**: The user's empirical test (4 accounts in minutes) supersedes the technical analysis. The CLI is ruled out regardless of capabilities.
**Reconstruction quality**: Tier 0 SPECULATIVE. Public-docs-based, not primary source.

### Finding 5: The Gemini CLI Sunset (2026-06-18)

**13 days from now**, the `gemini` CLI is sunset. The harvest strategy is to use it heavily through 2026-06-17, then migrate to direct Gemini API (`GOOGLE_API_KEY`).
**Post-sunset path**: Direct API with the same 8 Google accounts (separate quota pool from Antigravity).

---

## §4 What Was NOT Built (and Why)

### 4.1 No Engine Code

No `src/omega/integrations/antigravity_cli.py` was created. The
`agy` CLI is ruled out (D-AGY-03). The OpenCode plugin path is
already wired in `~/.config/opencode/opencode.json`. No engine code
needed.

### 4.2 No Implementation of the 7-Phase Plan

The 7-phase review plan in `data/entities/antigravity/soul.yaml` is
**strategy-only**. The user runs the plan from the Antigravity IDE;
the engine's role is to receive handoffs. No implementation in
`src/omega/` is needed.

### 4.3 No Migration Code for the Gemini CLI Sunset

The sunset is 13 days away. Migration code is not urgent. The harvest
plan documents the strategy. Implementation deferred until closer to
2026-06-18.

---

## §5 The Heritage Citations

This work used 4 heritage patterns from CREDITS.md:

1. **WAD System** (CREDITS.md §1.1, `[WAD System: id Software 1993]`) —
   The engine's IWAD/PWAD separation is mirrored in the KB structure
   (`_staging/` = base content, `cli_ide_platform/{sub}/` = patches).

2. **netchan Protocol** (CREDITS.md §1.21, `[netchan: id Software 1996/1999]`) —
   The Hivemind 3-file protocol is the federation-level netchan. The
   Antigravity ↔ OpenCode hand-off is a netchan.

3. **Worse is Better** (CREDITS.md §1.6, `[Worse is Better: Gabriel 1991, via id Software]`) —
   The `agy` rejection is a Worse-is-Better decision. The IDE/plugin
   path is the "worse" (in theory, less featureful) but actually usable
   tool.

4. **Multi-Index Entity** (CREDITS.md §1.15, `[Multi-Index Entity: id Software 1993]`) —
   The 8-key pool with 2 pools + 4 states is a Multi-Index Entity. Same
   account, different states in different indices.

---

## §6 L1 → L2 → L3 (Soul Distillation)

### L1 (What happened)

User mandated a KB scaffold for the rich Antigravity research. The
scaffolding was created: `_staging/` for unvetted, `cli_ide_platform/`
for canonical. 9 gold files landed. The hung agent's gnosis was
recovered in best-effort form. The 4-accounts-in-minutes empirical
fact was captured as a Tier 0 single-source citation.

### L2 (What it means)

The engine now has a **knowledge home** for external tool research.
Without this, future agents would re-derive the same conclusions from
scratch (cost: 1-2 hours per agent per topic). With the KB, future
agents read the Tier 0 file and either accept it (Tier 1 promotion) or
dispute it (back to Tier 0 with new evidence). The capture principle
ensures no gnosis is lost.

### L3 (Universal principle)

**Sovereign systems need knowledge homes, not just code homes.** A
codebase is the engine's "what it does." A knowledge base is the
engine's "what it knows." Both are required for sovereignty. The
engine already has a workbench (`data/workbench/workbench.db`),
a library (`data/library/`), and per-entity knowledge dirs. The new
`data/kb/` adds the **external tool expertise** layer — the engine's
view of the world outside `src/omega/`.

The 4-account empirical fact, the hung agent's recovery, the
sunset-date awareness — these are the kind of facts that are easy to
lose and expensive to re-derive. The KB is the **anti-amnesia layer**
for the engine.

---

## §7 Action Items Going Forward

1. **Kali (Pillar P5 Sentinel)**: review `_protocol/VETTING_PROTOCOL.md`
   and ratify the Tier 0/1/2 system.
2. **doom_guy**: review `01_PROVENANCE_LINEAGE.md` and `05_8KEY_POOL.md`
   for heritage accuracy (M14).
3. **quality**: review `04_QUOTA_REALITY.md` and `06_AGY_CLI_LIVE_TEST.md`
   for Mandate compliance (M7, M8, M11).
4. **researcher**: review `02_AUTH_MECHANISMS.md` and `08_FAILED_AGENT_RECOVERY.md`
   for factual claims and citation quality.
5. **user**: edit `~/.config/opencode/antigravity.json` to set
   `account_selection_strategy: "sticky"` for plain access.
6. **user**: restart OpenCode session to load the re-authenticated
   Antigravity plugin.

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ minimax-m3-free ⬡ opencode ⬡ trc_mining_report_10 ⬡ 2026-06-05*
