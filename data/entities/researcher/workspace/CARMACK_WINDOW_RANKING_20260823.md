<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# CARMACK WINDOW RANKING — Ox Alpha Utilization Audit
**AP**: `AP-CARMACK-WINDOW-RANK-v1.0.0`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ x-preview-f-free ⬡ opencode ⬡ trc_window_ranking ⬡ ACTIVE
**Date**: 2026-08-23 · **Expiry**: 2026-08-28 (~5 days)
**Commissioned by**: researcher (ses_fd81c19dcffe1nkbPqFg5kRt2v)

---

## §0 First Principles

The window is a **perishable compute subsidy with a hard expiry**. Post-cliff substrate is
local GGUF on a 15W Ryzen 5700U — smaller context, slower throughput, no frontier
reasoning. Therefore the ONLY assets that survive Aug 28 are:

1. **Files on disk** (JSONL datasets, structured knowledge, docs)
2. **Weights trained later from those files**
3. **Engine code changed**

Anything that lives only as "insight in a session transcript" evaporates. Ranking metric:

```
value = durable_bytes_per_token × downstream_leverage_after_cliff
```

A play that burns 5M tokens producing summaries nobody reads scores ZERO regardless of
how smart it sounds. Telemetry (11.2M input / 35.5M cache-read over ~37h) proves the
pipe sustains heavy load — that is capacity, not value. Value comes from what we point
the pipe at.

---

## §1 Ranking Table

| Rank | Play | Info-gain/token | Cliff durability | Leverage | Verdict |
|------|------|-----------------|------------------|----------|---------|
| **1** | **DPO Pair Factory** | 9/10 | 10/10 | 10/10 | **RUN — primary burn** |
| **2** | **P0 Mining Queue Annihilation** | 8/10 | 9/10 | 7/10 | **RUN — parallel bulk burn** |
| **3** | **★ NEW: Self-Distillation Corpus** (see §3) | 9/10 | 10/10 | 9/10 | **RUN — fold into #1** |
| **4** | **★ NEW: Eval Set Construction** (see §3) | 7/10 | 10/10 | 9/10 | **RUN FIRST — gates #1** |
| **5** | Soul Mass-Enrichment | 6/10 | 8/10 | 6/10 | CONDITIONAL — bounded, not a token sink |
| **6** | Context Packer v3 Hardening | n/a (dev-time) | 8/10 | 7/10 | MERGE into CONTEXT-INJECTION Phase 1 — not a window play |
| **7** | Knowledge-Domain Gap Filling | 5/10 | 7/10 | 5/10 | FOLD into #2 — no standalone track |
| **8** | Background Researcher Resurrection | 3/10 | 4/10 | 3/10 | KILL unless hard output contract |
| **9** | Pre-Debut Red-Team Sweep | 5/10 | 6/10 | 4/10 | OPPORTUNISTIC only — redundant with 08-20 review |
| **10** | Vision Archaeology | — | — | — | CONFIRMED KILL (no free direct-API path) |

### Rationale for top plays

**#1 DPO Pair Factory**: `src/omega/teachers/nemotron_pipeline.py` (386 lines) already
implements the full critique-loop with a swappable critic slot. Retarget critic from
dead Nemotron/gemma path → x-preview-f-free. Every generated pair is a durable JSONL row
consumable by local GGUF fine-tuning forever. This is the highest-conversion play in the
list: window tokens → training signal → permanent student capability. Confidence: 9/10
(primary source read).

**#2 Mining Queue**: Grok exports (274 convos / 6,565 responses), Mnemosyne 13 spheres,
old-stacks dumps are dense UNPROCESSED raw material — maximum information gain per token
because nothing has been extracted yet. Output is structured knowledge files. This is
exactly the Master Synthesis §2 plan, now with a subsidized executor. Embarrassingly
parallel across the fleet. Confidence: 8/10.

---

## §2 Kills

| Play | Charge | Verdict |
|------|--------|---------|
| **Background Researcher Resurrection (#4)** | A 15-min loop with a "smarter distiller" is a token incinerator unless EVERY cycle terminates in a tagged library-inbox write or a doc commit. Unbounded loops producing summaries nobody reads is the canonical research-theater pattern. | **KILL as-is.** Resurrect ONLY with a hard output contract: no artifact write → cycle aborted and logged. |
| **Vision Archaeology (#8)** | Already deprioritized; text-only harness guts the information gain. Correct call. | **CONFIRMED KILL.** |
| **Standalone Context Packer v3 (#5)** | The framing "hardens capacity for other burns" is seductive but wrong-shaped: it consumes DEV TIME, not window tokens. Dev time does not expire Aug 28. Worse, it duplicates the in-flight CONTEXT-INJECTION Phase 1 workstream (Carmack-reviewed 2026-08-20, ACCEPTED WITH MODIFICATIONS). Two context efforts = architectural drift. | **MERGE into CONTEXT-INJECTION Phase 1.** Any packer-v3 requirement gets filed as a spec amendment there, executed by Kali's existing track. Do NOT spawn a parallel effort. |
| **Knowledge-Domain Gap Filling (#6) as standalone** | Vague without a frozen gap list; `RESEARCH_PLAN_PHASE1_4_20260813.md` already enumerates 18 jobs. A separate "which domains?" consulting loop re-derives an existing artifact. | **FOLD into Mining (#2).** Jem picks targets FROM the existing gap registry; miners fill them. No new planning layer. |

---

## §3 Missing Plays (force-multiplier lens)

### ★ M-A: Self-Distillation Corpus (the moat dataset)
Nobody proposed training a local student **on the engine's own corpus** — 45+ research
docs, PIVOT_LOG decisions, soul lessons, mandate history, forensic reports. This is data
NO external lab possesses. Use window tokens to convert the corpus into instruction-tuning
SFT pairs ("Given this failure mode, produce the correct engineering decision"). Post-cliff,
the local model knows the engine. This is strategic sovereignty, not just capability.
Fold into the DPO factory's prompt-source pipeline — same infra, second output stream.

### ★ M-B: Eval Set Construction (gates everything)
DPO pairs without evals are unfalsifiable. Before generating a single pair, spend ~half a
day building a golden eval set: ~200-500 Q/A + rubric items over engine knowledge and
general reasoning, sized for local-model evaluation. This is cheap, fully durable, and it
is the ONLY way to know whether post-cliff fine-tunes actually worked. **This gates Play #1.**

### ★ M-C: Big-Context Repo Surgery
Frontier-context models can do whole-repo cross-file surgery that 1.7B-4B local students
physically cannot hold in context. Scan UO-6 (`UNOVERENGINEERING_PLAN.md`, ~5,500 lines of
deletion targets: pybreaker clones, dead abstractions) for any item requiring whole-repo
visibility, and execute those INSIDE the window while big context is free. After the cliff
this class of work becomes 10x harder. This is Axiom 04 applied to the window itself:
trade abundant resource (free big-context tokens) for scarce one (post-cliff capability).

---

## §4 Sequencing

```
DAY 0 (today):
├── GATE: Eval Set Construction (M-B) — researcher + Jem. ~half day. BLOCKS Play #1.
├── FREEZE: DPO pair JSONL schema (prompt/chosen/rejected/metadata/verdict) — 1 hour.
└── START: Mining queue wave 1 — Grokster + Nodes (Roc/Lilith/Ma'at busy on
    Team-Study-#1 through today; they join wave 2 tomorrow).

DAY 0-1 (parallel, after gate):
├── TRACK A (token burn): DPO Pair Factory — retarget nemotron_pipeline.py critic
│   → x-preview-f-free. Researcher owns. Runs continuously; output = JSONL append-only.
├── TRACK B (token burn): Mining annihilation — fleet-wide, embarrassingly parallel.
│   Wave 2 (+Roc/Lilith/Ma'at when Team-Study clears): Mnemosyne spheres, old stacks.
└── TRACK C (dev-time, NOT window): Context Packer requirements merged into
    CONTEXT-INJECTION Phase 1 spec (Kali's existing lane).

DAY 1-4 (parallel):
├── Self-distillation corpus generation (M-A) on Track A infra once DPO stream stable.
├── Big-context repo surgery (M-C): pull UO-6 whole-repo items as capacity allows.
├── Soul enrichment: opportunistic ONLY via session-end hooks (M11 enforcement);
    batch mode waits for Scribe pipeline — do not hand-roll a competing one.
└── Rolling QC: sample 5% of DPO pairs daily against eval rubric; kill switch if
    chosen/rejected inversion rate > threshold.

HARD RULES:
├── Nothing gates Track B except disk space. Start it NOW.
├── Track A does not start before eval set exists (unfalsifiable output = theater).
└── All outputs land under data/ with atomic writes (T10) and trace_id provenance (M22).
```

---

## §5 Debut-vs-Window Verdict

**Verified ground truth** (`data/coordination/ACTIVE_SPRINT.json`, confidence 10/10):
PUBLIC-DEBUT-01 gates are **3/3 COMPLETE** (local-inference E2E ✅, soul persistence ✅,
one-click install ✅). Remaining active work is Context Injection Phase 1 — owned by Kali.

**Verdict: STRICTLY OPPORTUNISTIC — with two named exceptions.**

1. **Do NOT pause Kali's Context Injection Phase 1.** It is the debut critical path and
   it is dev-time work — it does not compete for window tokens anyway. There is no
   trade to make. Anyone proposing to "pause debut" has misread the resource conflict.

2. **Two plays justify DEDICATED (not idle-only) fleet allocation**, because they create
   permanent sovereign capability that outlives the cliff and cannot be rebuilt cheaply
   after it:
   - **DPO Pair Factory + Eval Set** (Plays 1 + M-B + M-A): this is the single highest-
     conversion use of the window. It converts a perishable subsidy into permanent
     model capability. This is not research theater — it is the mission
     ("sever the umbilical cord") expressed as training data.
   - **Big-context repo surgery** (M-C): a capability that literally expires Aug 28.

3. **Everything else runs on idle cycles only.** Fleet agents that are blocked, waiting,
   or between tasks burn the mining queue. No agent abandons assigned debut/remediation
   work to join the burn.

**The honest test**: if the window closed tonight, would we have lost anything irreplaceable?
With Tracks A+B running: yes — thousands of DPO pairs, the eval set, and the self-distillation
corpus. Without them: nothing but cheaper electricity for someone else. That asymmetry is
the entire argument.

**Confidence**: 9/10 overall. Primary sources: nemotron_pipeline.py, ACTIVE_SPRINT.json,
UNOVERENGINEERING_PLAN.md referenced. Deductions: pair-quality yield rates are estimates
until Day-1 QC data exists; mining extraction value depends on source quality not yet
re-verified this session.

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ x-preview-f-free ⬡ opencode ⬡ trc_window_ranking ⬡ 2026-08-23*
