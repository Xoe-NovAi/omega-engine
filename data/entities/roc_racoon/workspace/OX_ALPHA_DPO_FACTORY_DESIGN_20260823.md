<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# Ox Alpha DPO Pair Factory — Design Spec
**AP Token**: `AP-ROC_RACOON-OX_ALPHA_DPO_FACTORY-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ x-preview-f-free ⬡ opencode ⬡ trc_dpo_factory_design ⬡ ANALYSIS

**Date**: 2026-08-23
**Requested by**: researcher (ses_fd81c19dcffe1nkbPqFg5kRt2v)
**Status**: Analysis/design only — no implementation in this pass
**Window**: ~5 days (Ox Alpha free tier expires ~2026-08-27/28)

**Ground truth correction absorbed**: Ox Alpha is NOT an external API. It is
`x-preview-f-free` on OpenCode Zen — the substrate our own sessions run on.
The critic lives IN-SESSION. No HTTP hop, no key, no rate limit. This changes
the pipeline from a *network service* into a *session discipline*.

---

## §1 Retarget Spec: `nemotron_pipeline.py` → In-Session Pair Factory

Source: `src/omega/teachers/nemotron_pipeline.py` (386 lines). The skeleton is
sound; the transport layer is what dies.

### 1.1 What STAYS (verbatim or near-verbatim)

| Component | Lines | Why it survives |
|---|---|---|
| `DPOPair` dataclass | 33–45 | Canonical pair shape; extend metadata only |
| `CritiqueResult` dataclass | 48–55 | Same parse contract |
| Iterative critique-loop structure | 159–207 | generate → critique → improve → verdict is teacher-agnostic |
| `CRITIQUE_PROMPT` / `FINAL_VERDICT_PROMPT` templates | 69–92 | Format works; tighten parsing (see gate) |
| `_parse_critique()` / `_parse_verdict()` | 323–370 | Line-format parsers still valid |
| JSONL daily-file storage (`_save_dpo_pair`) | 372–382 | Keep, but move target to omega_library (§4) |
| Stats dict | 112–118 | Add `gate_rejected`, `dedupe_skipped` counters |

### 1.2 What CHANGES

| Old (Nemotron remote) | New (Ox Alpha in-session) |
|---|---|
| `_call_nemotron()` — httpx POST to OpenRouter, Bearer key, 429 backoff (L284–321) | **DELETED ENTIRELY.** Critique happens because *I* (roc_racoon on Ox Alpha) write it in-conversation. No client, no retry logic, no vault lookup (`_resolve_openrouter_key`, L120–132 → delete). M7 note: this makes the factory *more* local-first compliant, not less — the cloud spend is the free window we're converting to durable artifacts. |
| Teacher = `nvidia/nemotron-3-ultra-550b-a55b` endpoint | Teacher = **in-session Ox Alpha critique passes**, tagged `teacher_model: "ox-alpha/x-preview-f-free"` + thinking level used |
| Student generator = mock / injected fn (L233–249) | Student generator = **`spawn_local_worker`** against Qwen3 GGUFs on omega_library partition (Tier 0 models, already on disk), OR Ox Alpha itself drafting deliberately-varied candidates for contrastive pairing |
| One pair per explicit call | **Batch discipline**: pair-generation blocks appended to mining sessions (§3) |

### 1.3 New execution modes (replacing the single API path)

- **Mode A — Refinery (primary)**: mined raw material → prompt derived →
  local student (spawn_local_worker, Qwen3-4B-Thinking) generates rejected
  draft → Ox Alpha critiques in-session → improved chosen written by Ox Alpha
  → verdict pass → pair committed. This is the original loop with the network
  edge amputated.
- **Mode B — Self-contrast**: for domains where the local student is too weak
  to produce a useful rejected draft (long-context analysis, heritage vetting),
  Ox Alpha produces two candidate responses at different thinking levels
  (Low vs High); the weaker becomes `rejected`. Cheaper, slightly riskier for
  preference fidelity — cap at ~30% of total volume.
- **Mode C — Replay-grade**: Grok export responses that are already excellent
  become `chosen`; a fresh Ox Alpha "degraded" rewrite becomes `rejected`.
  Highest authenticity, lowest cost per pair. Good for bootstrapping volume.

### 1.4 Pair Schema (extends `DPOPair.metadata`)

```json
{
  "prompt": "...",
  "chosen": "...",
  "rejected": "...",
  "timestamp": "2026-08-23T...Z",
  "metadata": {
    "schema": "ox-alpha-dpo-v1",
    "mode": "A|B|C",
    "teacher_model": "ox-alpha/x-preview-f-free",
    "teacher_thinking": "low|high|max",
    "student_model": "Qwen3-4B-Thinking-2507-Q4_K_M|null",
    "source_corpus": "grok-export:arcana.novai/<convo>|mnemosyne:<sphere>|synthetic",
    "source_ref": "<file:line or convo id>",
    "domain": "mining|infra|heritage|strategy|code",
    "iterations": 1,
    "critique_issues_count": 0,
    "verdict_reason": "..."
  }
}
```

### 1.5 Quality Gate (new — replaces implicit acceptance)

A pair is COMMITTED only if ALL pass:
1. **G1 Distinctness**: normalized chosen ≠ rejected (current code already
   counts this; make it a hard gate, not a stat).
2. **G2 Verdict-verified**: final verdict ACCEPTED=yes with non-empty reason.
   Pairs failing after `max_iterations=3` are discarded, not force-saved
   (fixes L204–206 "use last response" fallback — that pollutes training data).
3. **G3 Parse strictness**: critique must yield ≥1 concrete issue when
   rejecting; empty-parse = discard pair (silent parser failure today).
4. **G4 Dedup**: SHA256(prompt) index across all daily files; skip duplicates.
5. **G5 Length floor**: chosen ≥ 200 chars, prompt ≥ 20 chars.
6. **G6 Provenance**: `source_ref` mandatory for Mode A/C (auditable lineage,
   M22 spirit applied to training data).

### 1.6 Volume estimate (~5 days, opportunistic)

Constraint is NOT tokens (100T/day ceiling is unreachable) — it is **session
attention**. Realistic cadence:

| Mode | Per session | Sessions/day | Raw/day |
|---|---|---|---|
| A Refinery | 15–25 pairs | 2–3 | 30–75 |
| C Replay-grade | 10–20 pairs | 2–3 | 20–60 |
| B Self-contrast | 5–10 pairs | 1–2 | 5–20 |

Raw total over 5 days: **~275–775**. After G1–G6 attrition (~30–40%):
**≈ 200–500 committed pairs**, central estimate **~350**.

That is enough for a first-pass DPO/LoRA run on a 4B student (typical
preference sets start paying off around 300–1000 pairs). Not SOTA — but it
survives the cliff, which is the entire point.

---

## §2 Student Selection (LI workstream constraints)

Constraints (D-526 / ACTIVE_SPRINT LI): sequential loading, one model at a
time (Semaphore(1)), Tier 0 = 16GB CPU class, q8_0 KV, Tier matrix names
Qwen3-4B / Qwen3-4B-Thinking / Qwen3-1.7B. Live inventory check confirms both
winners are ALREADY on disk at `omega_library/models/gguf/`.

### Pick 1 (primary): **Qwen3-4B-Thinking-2507-Q4_K_M** (2.33 GB, present)
- Named in the Tier 0 matrix — zero friction with LI-4.
- Reasoning-native: DPO pairs generated from critique-loops teach exactly the
  skill this model exercises (self-correction, issue resolution).
- Small enough to train LoRA on Tier 0 hardware post-cliff.

### Pick 2 (secondary): **Qwen3-4B-Instruct-2507-UD-Q4_K_XL** (2.37 GB, present)
- Same base family/tokenizer as Pick 1 → adapter cross-pollination, shared
  eval harness, one data format.
- Covers the fast/non-thinking executor role; pairs where "concise correct"
  beats "verbose reasoning" train this one.

### Explicitly REJECTED as students
- **GLM-5.2 GGUF (my Aug 22 presets)**: those presets were for *running* Ox
  Alpha locally as a workhorse, not for training. A 744B/40B-active MoE cannot
  be fine-tuned on Tier 0 hardware, and even Q4_K_M is 24GB — it would hog the
  sequential loader and starve everything else. Teacher's family ≠ student.
- **RocRacoon-3b**: exists on disk, tempting for persona tuning, but payoff is
  niche. Revisit AFTER the Qwen3 pair proves the pipeline end-to-end.
- **Qwen3-1.7B**: keep as critic/utility per existing Tier 0 plan; too small
  to absorb 350 pairs meaningfully.

**Post-cliff sequence**: collect pairs now (window) → train LoRA on
Qwen3-4B-Thinking after weights open ~Aug 28 (no GPU contention during the
collection sprint either way — training is a post-window activity).

---

## §3 Mining Synergy: Feed, Don't Compete

**Verdict: the mining queue IS the pair factory's supply chain.** They compete
only for session attention inside the same 5-day window — and the resolution
is interleaving, not sequencing.

### The feed chain
```
P0 mining queue                    Pair Factory
───────────────                    ────────────
Grok exports                       Mode C: excellent historical answers → chosen;
(274 convos, 6565 responses)       Ox Alpha degraded rewrite → rejected
        │
        ├─ question-style turns ─→ Mode A prompts: real questions from the
        │                            archive → student draft → critique loop
        │
Mnemosyne (13 spheres) ──────────→ Domain pairs: memory-schema reasoning,
                                    Kabbalah↔soul.yaml mapping explanations
        │
Mining reports themselves ───────→ Meta-pairs: "summarize/extract pattern"
                                    tasks with my own report excerpts as gold
```

### Why this beats running them separately
1. Mining without distillation already violates the spirit of M11 — raw
   extraction that never becomes structured gnosis is half-wasted window.
   Pair conversion IS a distillation form (L1 narrative → training artifact).
2. Every mining session already loads the corpus context; deriving 15–25
   prompts from material just read costs near-zero extra context.
3. Mode C is nearly free: the Grok exports contain thousands of high-quality
   responses that need only a degraded twin to become pairs.

### Budget rule (per mining session)
**70% mining/extraction · 30% pair conversion.** End every mining session
with a fixed pair-generation block. If a day forces a choice, prioritize
Mode C (cheapest pairs, uses material already mined) over new mining.

---

## §4 Needs From Researcher

1. **Corpus prep (blocking for Mode A/C)**: from Grok exports, extract
   deduplicated question-style user turns as JSONL:
   `{prompt_id, source_ref, prompt_text, domain, quality_hint}`.
   Target: 500–800 candidates so the factory can filter down. Mnemosyne
   spheres: same shape, tagged `domain: memory`.
2. **Prompt template ratification**: I will reuse the pipeline's
   CRITIQUE/FINAL_VERDICT formats with stricter parsing (§1.5 G3). If
   researcher has a preferred rubric (e.g., scoring dimensions beyond
   accept/issues/suggestions), send BEFORE Day 1 — changing the schema
   mid-window corrupts pair consistency.
3. **Storage layout under omega_library** (proposed — confirm or amend):
   ```
   /media/arcana-novai/omega_library/training/
   ├── dpo_pairs/
   │   ├── raw/          # daily JSONL as generated (dpo_pairs_YYYYMMDD.jsonl)
   │   ├── gated/        # post G1–G6, canonical training set
   │   ├── rejected/     # failed pairs, kept for audit (never deleted)
   │   └── manifest.jsonl
   ```
   Mirrors the intake/mining_queue convention; keeps heavy artifacts off the
   engine repo. Engine-side pointer doc only.
4. **Post-cliff training owner**: who runs the actual DPO/LoRA job on
   Qwen3-4B-Thinking after ~Aug 28 (unsloth? llama.cpp finetune? external)?
   Factory output format above is trainer-agnostic but I need the target
   format (e.g., TRL preference rows) to emit directly if known.
5. **Token-budget coordination**: confirm no other fleet workstream plans
   bulk Ox Alpha consumption that would collide with daily pair blocks.

---

## Cross-references
- `src/omega/teachers/nemotron_pipeline.py` — retarget source
- `OX_ALPHA_QUANTIZATION_PRESETS.json` — GLM-5.2 presets (workhorse, NOT student)
- `OX_ALPHA_LEGACY_MINING_20260822.md` — Ox Alpha identity forensics
- `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md` — LI workstream (D-526)
- `data/entities/jem/workspace/N11_EVALUATOR_KB_20260822.md` — Semaphore(1)/admission constraints

*⬡ OMEGA ⬡ ROC_RACOON ⬡ OX_ALPHA_DPO_FACTORY ⬡ DESIGN-v1.0.0 ⬡ 2026-08-23*
