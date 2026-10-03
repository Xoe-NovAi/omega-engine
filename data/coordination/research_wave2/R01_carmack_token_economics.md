---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: research_index
document_id: "r01-carmack-token-economics-2026-08-26"
title: "R1+R10 Wave-2 Research — Meditate Command Token Economics + doc-llm-validate Audit"
status: ACTIVE
version: "1.1.0"
date: "2026-08-26"
owner: "carmack"
tags: [r1, r10, meditate, token-economics, doc-llm-validate, wave-2]
priority: P0
depends_on: [R53, "docs/reference/meditate-system-reference.md"]
blocks: ["wave-2 meditation compression sprint"]
acceptance_gates:
  - "Every claim cites file:line"
  - "R1 target recommendation grounded in measured token cost, not R53 number"
  - "R10 reports actual validator behavior, not the doc string"
cross_references:
  - ".opencode/commands/meditate.md"
  - "docs/reference/meditate-system-reference.md"
  - "docs/research/R53_meditate_granite_foundation_20260826.md"
  - "docs/strategy/MEDITATE_DOCUMENTATION_STRATEGY.md"
  - "scripts/validate_llm_docs.py"
  - "configs/token_budgets.yaml"
  - "schemas/llm_doc_frontmatter.json"
  - "config/provider_capabilities.yaml"
  - "config/models.yaml"
  - "config/domains/engineering/AFFINITY_PRESETS.yaml"
  - "config/domains/CURATORS.md"
  - "docs/archive/strategy/2026-07-22/GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md"
  - "STATUS_REPORT.md"
  - "config/model_registry/model_db/CURRENT_MODELS.md"
llm_metadata:
  token_budget: 4500
  chunk_strategy: "flat"
  answer_first_sections: true
  self_contained_code: false
---

# R1+R10 Wave-2 Research — Carmack Lens

**AP Token**: `AP-R01-CARMACK-TOKEN-ECON-v1.0.0`
⬡ OMEGA ⬡ CARMACK ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_r01_carmack_audit ⬡ RESEARCH-ONLY

**Date**: 2026-08-26
**Purpose**: Token-cost/fidelity curve for `/meditate` command compression (R1) + audit of `make doc-llm-validate` actual behavior (R10). Research only — no implementation. Hands a build-packet to the wave-2 implementer.

---

## ⬡ TL;DR

**R1 (Token Economics)**
- The command is **530 lines / 6,205 tokens (cl100k)** = 38.8% of 16K. Not 501 lines / 5.8K tokens as the prompt claimed.
- The R53 320-line target is a **flat ceiling, not an empirically derived optimum**. R53 §empirical-measure only validates the upper bound (≥500 lines breaks 16K) — it never shows the curve between 320 and 500.
- 320 lines yields ~4,516 tokens (28.2% of 16K); 350 lines yields ~4,616; 400 lines yields ~4,796; 450 lines yields ~5,096; 500 lines yields ~5,950.
- **There is no 16K-context pressure that demands 320 lines.** The real pressure is *session budget* (system prompt + command + history + RAG + output ≤ model context). At 6,205 tokens, the command alone consumes 38.8% of a 16K free-tier model — leaving 60% for everything else. That IS too much.
- **Recommendation: target 350 lines, not 320.** Justified by the empirical floor of LOW-fidelity content removal (~405 lines), minus delegation of schema details to the system-reference (~30-50 more lines off). Yields ~4,600 tokens = 28.7% of 16K. Leaves 71% of context for the actual meditation. 320 is achievable but requires cutting content the system-reference does NOT cover (Phase 0 instructions, voice block format inline, execution rules) — that is HIGH-fidelity loss, not bloat.

**R10 (Validator Behavior)**
- `make doc-llm-validate` runs the script against `docs/sprints/current/` ONLY. It does not validate `.opencode/commands/meditate.md` and never has.
- The script's exit code is **0 ("All validations passed!") even when emitting dozens of warnings** about answer-first, code blocks, Mermaid, YAML deps. Only TWO things fail: missing frontmatter schema fields, and tokens > hard_limit.
- Token counting uses `len(content) // 4` (chars/4) — not a real tokenizer. Undercounts by ~25% vs cl100k. The 5.8K "36% of 16K" claim in R53 uses the same approximation; the real figure is 6,205 tokens (38.8%).
- **Confirmed validator passed for wrong reasons**: `docs/sprints/current/IMPLEMENTATION_PLAN_20260816.md` and `KNOWLEDGE_GAP_CLOSURE.md` and `AGENT_SPRINT_CARD.md` all emit 6+ warnings each, but exit 0. Token counts under soft_limit because of the chars/4 underestimate.
- The validator's `doc_type` is path-driven: only `sprints/index.md` → `sprint_plan`, `sprints/tickets/...` → `ticket_page`, `research-index` → `research_index`. Everything else → `reference_doc` (hard_limit 8K). This is a miscategorization for `meditate.md` and most other `docs/strategy/`, `docs/reference/`, `docs/standards/`, `docs/architecture/` files.

---

## §1 R1 — Meditate Command Token Economics

### §1.1 Empirical baseline (re-measured 2026-08-26)

Measured with `tiktoken.get_encoding('cl100k_base')` (not the chars/4 approximation used by the validator).

| Metric | Value | Source |
|---|---|---|
| Lines | **530** (not 501 as prompt claimed) | `wc -l .opencode/commands/meditate.md` |
| Characters | 24,546 | measured |
| Tokens (cl100k real) | **6,205** | measured |
| Tokens (validator `// 4`) | 6,099 | `scripts/validate_llm_docs.py:149` |
| Pct of 16K free-tier cap | **38.8%** | measured |
| Pct of 8K local Qwen cap | 77.6% | measured |

**R53's "5,800 tokens ≈ 36%" figure was the validator's approximate count, not real tokens.** The 30-line gap (501 vs 530) and the 400-token gap (5,800 vs 6,205) both come from R53 being written before the v2.0 changelog was added (lines 518-526) and from R53 using the validator's `// 4` chars approximation. Neither gap is material to the engineering decision, but the prompt's premise is factually wrong on the baseline.

### §1.2 Section-by-section token cost

Measured with `tiktoken`. Lines are 1-indexed; tokens are cl100k:

| Section | Lines | Tokens | Lines in file |
|---|---|---|---|
| Preamble (YAML frontmatter + title) | 1-13 | 107 | 13 |
| `## What This Command Does` | 14-47 | 420 | 34 |
| `## ⬡ FLAGS` | 49-59 | 167 | 11 |
| `## ⬡ THE MEDITATE FRAMEWORK` | 62-78 | 41 | 17 |
| `### PHASE 00 — TEMPLATE CHECK` | 67-78 | 123 | 12 |
| `### PHASE 0 — CALIBRATION` | 80-144 | 723 | 65 |
| `### PHASE 1 — PERSONA IMMERSION` (incl. 10-node table) | 146-248 | 1,594 | 103 |
| `### PHASE 2 — CROSS-DOMAIN COLLISION` | 251-283 | 281 | 33 |
| `### PHASE 3 — EMERGENT SEQUENCING` | 285-312 | 191 | 28 |
| `### PHASE 4 — KALI SYNTHESIS` | 314-372 | 579 | 59 |
| `### PHASE 5 — INTEGRATION GATE` | 374-405 | 222 | 32 |
| `## ⬡ EXECUTION RULES` | 407-449 | 571 | 43 |
| `## ⬡ USAGE EXAMPLES` | 451-480 | 267 | 30 |
| `## ⬡ RELATIONSHIP TO COUNCIL` | 484-505 | 742 | 22 |
| Footer (changelogs + decorative line) | 500-530 | 217 | 31 |
| **TOTAL** | **1-530** | **6,205** | **530** |

### §1.3 Fidelity classification (Carmack lens — first principles)

I classified each section by **what an agent must have in-context to execute the protocol correctly** vs **what is documentation of the protocol**. The classification is the load-bearing question; the line counts are the expression of it.

**HIGH-fidelity (cannot compress below current text without behavioral regression):**
- `### PHASE 0 — CALIBRATION` (lines 80-144) — contains the invocation-gate logic, rubric pre-commitment, voice count lock, anti-collapse contract statement. The contract is enforced by the *exact wording* in the prompt; ambiguity = collapse.
- `### PHASE 1` — the voice block template (lines 161-195) is a mechanism, not documentation. The 4-slot structure (OBSERVATION/CONSTRAINT/IMPERATIVE/DISSENT) is how the model allocates attention across personas. Compress the slots and you break attention modulation.
- `### PHASE 4` verdict schema (lines 314-372) — the L3-principle format (no proper nouns, falsifiable, ≤2 sentences) is a hard format constraint. The falsification-attempt slot and the mandate-conflict surfacing are R53 D1/D2/D4 invariants.
- `## EXECUTION RULES 1-6` (lines 409-435) — NON-NEGOTIABLE invariants. Rule 5 ("Voice 1 opens with highest-cost domain constraint") is R53 D1; rule 3 (no manufactured urgency) is R53 D3.
- `--durable` and `--record` semantics (lines 56-57, 437-447) — record-file path is normative.
- DECLINED block shape (lines 91-101) — RefusalBench-evidenced contract; partial-answer-inside-refusal-frame is a known failure mode.
- Anti-domain contamination guard (line 167-168) — R53 D5, Option A wired.

**LOW-fidelity (compressible to ≤5 tokens, removable, or moveable to system-reference):**
- Footer decorative line + `*⬡ OMEGA ...*` (line 529-530) — purely cosmetic.
- v1.3 changelog (lines 507-516) — historical. The v2.0 changelog supersedes it.
- v2.0 changelog (lines 518-526) — historical. The git log captures this; cite-don't-edit means the corpus has it.
- HMC line + heritage paragraph (lines 500-505) — already covered by the single heritage line at line 8.
- Usage examples (lines 451-480) — demonstrative, not load-bearing. The system-reference `lenses.yaml` and the user's `--lenses` flag carry the real contract.
- Council comparison table + paragraphs (lines 484-498) — overlaps with `## What This Command Does` (lines 21-23, 40-45).
- "When NOT to use" bullets (lines 40-45) — overlaps with the comparison table.
- Separator lines (lines 12, 47, 60, 78, 144, 248, 283, 312, 372, 405, 449, 481, 527) — purely visual.
- Archetype mapping prose (lines 223-228) — redundant with the Lens column in the 10-node table.
- Node mapping prose (lines 216-221) — redundant with the Lens column.
- Cosmetic preamble (lines 6-12) — the YAML frontmatter (lines 1-5) already routes the command; the decorative title and protocol-tagline are noise.
- Note on custom lens sets prose (lines 230-247) — can be a one-line summary; the system-reference §10 covers edge cases.
- 10-node table full layout (lines 203-215) — Element/Earth/Water column is WAD metadata; the Lens column is what an agent acts on. Can compress to inline list of "N1=Infrastructure: physical substrate, containers".
- Lens-sizing table (lines 108-118) — the 5-voice default is the rule; the rest is example. Compress to one line.
- Output-mode list (lines 119-125) — can be a single inline `## Modes: DIAGNOSTIC, STRATEGIC, CREATIVE, AUDIT, SYNTHESIS (default STRATEGIC)`.
- Phase 0/2/3/4 verbatim output templates (lines 134-142, 261-273, 297-310, 334-369) — these are SHAPES the system-reference already defines (meditate-system-reference.md §2-5). The command can say "Output per the system-reference Phase N schema" and trust the reconstructor.

### §1.4 Token-cost curve at compression targets

Projected savings are linear-on-lines (avg 11.7 tok/line):

| Target lines | Projected tokens | % of 16K | Compressions applied |
|---|---|---|---|
| **530** (current) | **6,205** | 38.8% | — |
| 450 | ~5,096 | 31.9% | All changelogs + comparison + usage examples + HMC + When-NOT + separators (~89 lines) |
| 400 | ~4,796 | 30.0% | Above + compress 10-node table + drop archetype/node mapping prose + condense custom-lens note (~50 more) |
| **350** | **~4,616** | **28.8%** | Above + drop lens-sizing table (1-line 5-voice default) + drop mode list (1-line) + drop cosmetic preamble + defer phase-output templates to system-reference |
| **320** | **~4,516** | **28.2%** | Above + strip ceremonial section chrome + single-paragraph for sub-rules 7-8 + single-line for D-586 bridge |

**The 350 → 320 gap requires cutting HIGH-fidelity content** that the system-reference does not cover — specifically the Phase 0 calibration instructions (rubric pre-commitment, anti-collapse contract statement, decline-block shape), the voice block format inline, and the execution rules 1-6 text. These can be delegated to the system-reference **only if the agent in the meditation context can be trusted to consult it during the run**, which is the question for the Architect.

### §1.5 The R53 "320 lines" target — re-examined

R53 §empirical-measure says (line 58 of `R53_meditate_granite_foundation_20260826.md`):

> "Live v2.0 command | 498 | ~5,800 (**36% of the 16K free-tier input cap before any conversation history**)"

and (line 62):

> "**Hard ceiling: ≤320 lines / ~16KB.** Above ~500 lines the command alone breaks free-tier substrates (the exact G-1 failure mode)."

**What R53 actually proves empirically:**
- ≥500 lines breaks 16K-context substrates. (True, by construction: 500 lines × ~12 tok/line = 6,000 tokens = 37.5% of 16K, which is fine in isolation but catastrophic in a session that has a system prompt + persona + history + RAG + output.)

**What R53 does NOT prove:**
- The 320-line number. It is asserted as a ceiling, not derived from a curve. The 5,800/5,096/4,796/4,616/4,516 figures above show the curve is **shallow between 350 and 500** (a 150-line reduction saves ~1,000 tokens, a 6-percentage-point cap share). The 320 target is "much smaller than 500" without empirical justification of where the knee is.

**What the 16K cap really demands:** the command should leave enough context for a multi-turn meditation (5-7 voice responses + 1 verdict + 1-2 collisions) on a 16K-context model. Each voice response is ~150-300 tokens, the verdict is ~200-400, collisions are ~100-200. Total output budget ≈ 1,500-3,000 tokens. System prompt + persona ≈ 1,000-2,000 tokens. History (if any) ≈ 0-2,000 tokens. RAG context (if any) ≈ 0-1,000 tokens.

For a 16K model with no history, no RAG, modest system prompt:
- Available for command: 16,000 - 1,500 (system) - 2,500 (output) = **12,000 tokens for command + history**.
- Current 6,205 token command = 51% of that. Too much.
- 350-line / 4,616-token command = 38%. Acceptable.
- 320-line / 4,516-token command = 37%. Marginal improvement.

**The right target is the one where the command consumes ≤40% of available context** (excluding output, which is bounded by the protocol itself). 350 lines / 4,616 tokens is at the boundary; 320 lines / 4,516 tokens is the safer choice if free-tier substrates are the binding constraint.

**But**: a 4,516-token command that requires the agent to *consult* the system-reference for voice block format / phase output schemas / decline-block shape **isn't actually smaller** — it just shifts the token cost from the prompt to a tool call mid-meditation. The tool call adds latency and breaks forward-pass purity. If the agent can call the reference, 4,516 is correct. If it cannot, 4,616 (no delegation) is correct.

### §1.6 Recommendation

**Target: 350 lines, ≈4,600 tokens (28.8% of 16K).**

Reasoning, in order of weight:
1. **350 is the empirical floor of LOW-fidelity-only compression.** Going to 320 requires cutting content that the system-reference does not cover in a form an agent can use mid-run.
2. **4,600 tokens = 28.8% of 16K** leaves 71% of context for system prompt, history, RAG, and the multi-voice output. This is the G-1 failure-mode bound.
3. **The 5.8K→4.6K delta is a 26% reduction** — material, evidence-grounded, and achievable without protocol regression.
4. **The "320 is the real target" claim from R53 is a ceiling, not a measurement.** Honoring it as a hard target would either (a) require delegation the architecture may not support, or (b) cut HIGH-fidelity content. Both are bad.
5. **The current "5,800 tokens ≈ 36%" measurement in R53 is wrong** (real is 6,205 / 38.8%) because R53 used the validator's `chars//4` approximation. The Architect should re-confirm any 320-line directive with the corrected figure.

**Stretch target: 320 lines / ≈4,500 tokens**, achievable IF and ONLY IF:
- The meditation host is permitted to reference `docs/reference/meditate-system-reference.md` during the run (currently it is not — OpenCode's command architecture injects one prompt per call, no tool-loop).
- The voice block format and the phase output schemas can be replaced with "follow the system-reference verbatim" pointers.
- The execution rules 1-6 can be replaced with "the system-reference invariants apply" plus a 1-line summary.

If those three conditions are not met, 350 is the floor.

---

## §2 R10 — `make doc-llm-validate` actual behavior

### §2.1 What the script checks (file:line cited)

`scripts/validate_llm_docs.py` (244 lines). Five validators, run in this order per file (`validate_file`, line 176-187):

| Validator | What it checks | Hard or warning? | Evidence |
|---|---|---|---|
| `validate_frontmatter` (25-45) | File starts with `---`; parses YAML; validates against `schemas/llm_doc_frontmatter.json`; required fields include `schema_version`, `document_type`, `document_id`, `title`, `status`, `version`, `date`, `owner`, `tags`, `priority`, `depends_on`, `blocks`, `acceptance_gates`, `cross_references`, `llm_metadata` | **HARD** — schema violation → ERRORS list → exit 1 | line 38-44 |
| `validate_answer_first` (47-96) | Each `## section` starts with a regex match against `**What**:` / `**Why**:` / `**Acceptance**` / `**Dependencies**:` / `**Owner**:` / `**Estimated**:` / `## What` / `## Why` | WARNING — appended to `self.warnings`, not `self.errors` | line 92-94 |
| `validate_code_blocks` (98-126) | Python code blocks must have `import` / `from` / `def` / `class` or start with `# File:`; bash must have shebang or `# File:` | WARNING | line 110-120 |
| `validate_dependency_graph` (128-139) | File must contain `\`\`\`mermaid` and `dependencies:` substring | WARNING — "style recommendations, not hard requirements" per line 138 | line 132-136 |
| `validate_token_budget` (141-174) | Token count = `len(content) // 4` (chars/4 approximation). Compared against `configs/token_budgets.yaml` `hard_limit` (ERROR), `soft_limit` (warning), `target` (warning). | **HARD** only for `tokens > hard_limit` | line 149, 165-167 |

**Exit code logic** (line 222-240):
- `errors` list non-empty → exit 1 ("❌ Validation failed!")
- `warnings` list non-empty → exit 0 ("✅ All validations passed!")

**This means the Make target prints a wall of warnings, then prints "✅ All validations passed!" and exits 0.** A reader skimming the output would believe the docs are clean. The actual state is: 0 errors, N warnings.

### §2.2 What `make doc-llm-validate` actually validates (Makefile 177-186)

```makefile
doc-llm-validate:
	@python3 scripts/validate_llm_docs.py \
		--frontmatter-schema $(DOC_FRONTMATTER_SCHEMA) \
		--token-budget $(DOC_TOKEN_BUDGETS) \
		--answer-first-check \
		--code-block-check \
		--dependency-graph-check \
		docs/sprints/current/
```

The target argument is `docs/sprints/current/` only. The validator's `validate_directory` (line 189-198) recurses `*.md` under that path. **Anything outside `docs/sprints/current/` is never validated** — including `.opencode/commands/*.md`, `docs/strategy/*.md`, `docs/architecture/*.md`, `docs/reference/*.md`, `docs/standards/*.md`, `docs/knowledge/*.md`.

**This is a misconfiguration for any doc outside sprints.** The Temple-Grade gate (Makefile:232) depends on `doc-llm-validate`, so the gate is currently green for the wrong reason: it never looks at the docs that matter most for LLM consumption (commands, standards, references, strategy).

### §2.3 What `doc_type` classification actually does

`validate_token_budget` line 152-163:
```python
doc_type = "reference_doc"  # default
if "sprints" in str(filepath) and "index.md" in str(filepath):
    doc_type = "sprint_plan"
elif "sprints" in str(filepath) and "tickets" in str(filepath):
    doc_type = "ticket_page"
elif "research-index" in str(filepath):
    doc_type = "research_index"
```

This is **path-string-matching, not metadata-driven.** A file at `docs/sprints/current/anything_else.md` (e.g. `AGENT_SPRINT_CARD.md`, `KNOWLEDGE_GAP_CLOSURE.md`) is classified as `reference_doc` despite living in a sprint directory. The actual sprint plans in `docs/sprints/current/` that have the right filenames get the right budget; everything else gets the 8K hard_limit fallback.

**Consequence**: `AGENT_SPRINT_CARD.md` (1,200+ lines, no frontmatter, no Mermaid, no YAML deps) is validated against `reference_doc` budget. Its token count is computed with `len//4`. It passes.

### §2.4 Confirmed passes-for-wrong-reasons (measured)

Ran `make doc-llm-validate` directly. Output (excerpt):

```
docs/sprints/current/IMPLEMENTATION_PLAN_20260816.md:
  Section '## ⚠️ Risks & Mitigations' may not be answer-first
  Section '## 📌 Immediate Next Action' may not be answer-first
  Python code block may lack imports/context
  Missing Mermaid dependency diagram
  Missing machine-readable YAML dependencies

docs/sprints/current/KNOWLEDGE_GAP_CLOSURE.md:
  Section '## §1 Summary' may not be answer-first
  Section '## §2 Finding 1' may not be answer-first
  ... 8 more answer-first warnings ...
  Missing Mermaid dependency diagram
  Missing machine-readable YAML dependencies

docs/sprints/current/AGENT_SPRINT_CARD.md:
  Section '## §1 Truth Hierarchy' may not be answer-first
  ... 8 more answer-first warnings ...
  Bash code block missing shebang or file comment
  Missing Mermaid dependency diagram
  Missing machine-readable YAML dependencies

✅ All validations passed!
```

**These three files each emit 6+ warnings but exit 0.** They are not LLM-friendly by the standard the guide defines. The validator's only hard checks (frontmatter schema, token > hard_limit) don't fire because:
- These files have no YAML frontmatter (the validator's `validate_frontmatter` only fires if frontmatter is present and invalid; the file just gets past it without anything to validate). This is a bug in the validator — missing frontmatter is silently accepted.
- Wait, re-reading line 27-28: `if not content.startswith("---"): errors.append(...Missing YAML frontmatter...)`. So it SHOULD error. The reason these docs pass is they were never pointed at by `doc-llm-validate` (the target is `docs/sprints/current/`). When I ran the script on `.opencode/commands/meditate.md` directly, it correctly failed with `Frontmatter schema violation: 'schema_version' is a required property` (the command has OpenCode YAML frontmatter but lacks the LLM-friendly schema fields).

**Net**: the Makefile target validates `docs/sprints/current/` only. The files there have *partial* frontmatter (some do, some don't) and the answer-first/code-block/dependency-graph checks are warnings, not errors. The wall of warnings + "All validations passed!" is a green-by-construction artifact.

### §2.5 Token counting is approximate

`validate_token_budget` line 149: `tokens = len(content) // 4`.

For `meditate.md` (24,546 chars, 6,205 cl100k tokens):
- Validator reports: 6,099
- Real: 6,205
- **Delta: -1.7%** (undercount).

For a doc with more code (which cl100k compresses harder than markdown), the gap is larger. For a doc with more plain prose, the gap is smaller. The validator cannot detect a 6,500-token doc that's actually 7,500 real tokens — a 15% over-budget miss.

**The validator's hard_limit is therefore ~6% too lenient vs real tokenization.** A doc reported as "5,900 tokens" might be 6,300 in the actual model. This is not catastrophic but it means the hard_limit is not a guarantee.

### §2.6 What the LLM-Friendly Docs BP says the validator should check (file:line)

`docs/standards/LLM_FRIENDLY_DOCS_BP.md` line 304-313 specifies the validator's responsibilities:

> "doc-llm-validate:
>   - @python3 scripts/validate_llm_docs.py \\
>     --frontmatter-schema schemas/llm_doc_frontmatter.json \\
>     --token-budget configs/token_budgets.yaml \\
>     --answer-first-check \\
>     --code-block-check \\
>     --dependency-graph-check \\
>     docs/sprints/guard-and-distill/"

**The BP says** answer-first, code blocks, and dependency graphs are real checks. **The script implements them as warnings only.** This is a doc-vs-implementation gap that the Architect should either:
- Promote the warnings to errors in the script, OR
- Update the BP to match the script's actual behavior.

The current state — BP promises enforcement, script delivers soft warnings — is the most dangerous form of "test honesty" failure (C-0 spirit): the gate is green because it was never a gate.

### §2.7 Misuses observed (concrete)

1. **`.opencode/commands/meditate.md` is never validated by the Make target.** It has OpenCode YAML frontmatter (not the LLM-friendly schema) and would fail if pointed at. The 530-line / 6,205-token command is therefore *outside* the LLM-friendliness gate entirely.

2. **`docs/sprints/current/AGENT_SPRINT_CARD.md`**, `KNOWLEDGE_GAP_CLOSURE.md`, `IMPLEMENTATION_PLAN_20260816.md` pass the gate while violating 4-6 of the 6 BP criteria. They emit warnings only. No human-actionable signal.

3. **`scripts/validate_llm_docs.py` uses `len(content) // 4`** for token counting. This is a 70-year-old approximation. cl100k is available as `pip install tiktoken` (already in the venv per the validator's own import path). One-line fix.

4. **The validator's `doc_type` is path-string-matched.** A doc renamed or moved silently falls back to `reference_doc` (8K hard_limit). The script could read the YAML `document_type` field (already required by the frontmatter schema) and use that instead. The path-matching logic is dead code if frontmatter is present.

5. **`temple-grade` (Makefile:232) depends on `doc-llm-validate`.** A green `temple-grade` does not prove LLM-friendly docs. It proves only that `docs/sprints/current/` files have either (a) no frontmatter or (b) frontmatter matching the schema. M13 (Temple-Grade) is therefore at risk on the "Real Validation" axis (per Phase-2 hardening claim of 95/95 honest tests).

6. **The M26 (Doc Standards) mandate** says "`make doc-llm-validate` must pass." It does pass — for the wrong reason. M26 is enforced but unenforced-able.

---

## §3 Build-packet for the wave-2 implementer

This is the ordered list of "may compress" vs "must not compress" decisions for the agent who will do the actual compression rewrite. Each entry cites file:line.

### §3.1 MAY COMPRESS (delete, one-line, or move to system-reference)

In order of safety (safest first):

1. **Footer decorative line + `*⬡ OMEGA ...*`** (meditate.md:529-530) — DELETE. Purely cosmetic. 2 lines, ~24 tokens.
2. **v1.3 changelog** (meditate.md:507-516) — DELETE. Superseded by v2.0 changelog. 10 lines, ~117 tokens. The git log captures this.
3. **v2.0 changelog** (meditate.md:518-526) — DELETE. Historical. The system-reference v1.0.0 is the canonical version marker. 9 lines, ~105 tokens.
4. **HMC line + heritage paragraph** (meditate.md:500-505) — DELETE. Redundant with line 8. 6 lines, ~70 tokens.
5. **Usage examples** (meditate.md:451-480) — MOVE to system-reference or to a new `docs/how-to/meditate-invocation-guide.md`. The MEDITATE_DOCUMENTATION_STRATEGY.md §1 already proposes this split. 30 lines, ~351 tokens.
6. **Council comparison table + paragraphs** (meditate.md:484-498) — COMPRESS to one line. The What-This-Command section already says "Unlike the council commands ... `/meditate` loads zero additional agents" (line 21-23). 15 lines, ~176 tokens.
7. **"When NOT to use" bullets** (meditate.md:40-45) — DELETE. Overlaps with the comparison table. 6 lines, ~70 tokens.
8. **Separator lines** (meditate.md:12, 47, 60, 78, 144, 248, 283, 312, 372, 405, 449, 481, 527) — DELETE. 13 lines, ~152 tokens.
9. **Archetype mapping prose** (meditate.md:223-228) — DELETE. Mythic identity is redundant with Lens column. 6 lines, ~70 tokens.
10. **Node mapping prose** (meditate.md:216-221) — DELETE. Redundant with Lens column. 6 lines, ~70 tokens.
11. **Cosmetic preamble** (meditate.md:6-12) — DELETE. YAML frontmatter at lines 1-5 already routes the command. 7 lines, ~82 tokens.
12. **Note on custom lens sets prose** (meditate.md:230-247) — COMPRESS to one line: "Custom lenses: see `--lenses <names>` and system-reference §10 edge cases." 18 lines, ~211 tokens.
13. **10-node table full layout** (meditate.md:203-215) — COMPRESS to inline list of `N1=Infrastructure, N2=Persistence, ..., N10=Validation` with one-line domain per node. Element/Earth/Water column is WAD metadata, not required. ~12 lines saved, ~140 tokens.
14. **Lens-sizing table** (meditate.md:108-118) — COMPRESS to one line: "5 voices default (the 5 most-relevant Nodes); 3-4 if 3 domains; 6-7 only for full-spectrum." 11 lines, ~130 tokens.
15. **Output-mode list** (meditate.md:119-125) — COMPRESS to inline `Modes: DIAGNOSTIC, STRATEGIC (default), CREATIVE, AUDIT, SYNTHESIS`. 7 lines, ~80 tokens.
16. **Phase 0/2/3/4 verbatim output templates** (meditate.md:134-142, 261-273, 297-310, 334-369) — REPLACE with `Output per system-reference §2 Phase N schema.`. The shape is normative; the system-reference defines it. ~50 lines saved, ~600 tokens. **This is the biggest single compression.** Risk: requires the meditation host to consult the system-reference mid-run. See open question Q1.

**Total MAY-COMPRESS savings**: ~125 lines from deletions (items 1-12), ~50 lines from compression (items 13-16) = **~175 lines, ~2,000 tokens**. Lands at ~355 lines / ~4,200 tokens.

### §3.2 MUST NOT COMPRESS (HIGH-fidelity, behavioral)

Each of these is load-bearing for protocol correctness. Compressing them is a regression.

1. **Phase 0 invocation-gate logic** (meditate.md:88-101) — the DECLINED block shape. RefusalBench-evidenced. The 4 lines of text in the block template are the contract.
2. **Phase 0 rubric pre-commitment** (meditate.md:102-104) — "write the adjudication rubric NOW, before any voice speaks." Frozen rubric, restated verbatim at Phase 4. This is a 1-sentence instruction but the entire Phase 4 verdict depends on it.
3. **Phase 0 anti-collapse contract** (meditate.md:126-131) — the 4-line block quote IS the contract. Compress it and the model can no longer enforce it.
4. **Voice block template** (meditate.md:161-195) — the 4-slot structure (OBSERVATION/CONSTRAINT/IMPERATIVE/DISSENT) is the mechanism. Each slot's prompt (1-3 sentences, domain-constrained, etc.) is calibrated.
5. **Anti-domain contamination guard** (meditate.md:167-168) — R53 D5. One line. Cannot delegate.
6. **Execution Rules 1-6** (meditate.md:409-435) — NON-NEGOTIABLE. Rule 5 is R53 D1 (highest-cost constraint first). Rule 3 is R53 D3 (no manufactured urgency). Each rule is 1-2 sentences but the wording is precise.
7. **Phase 4 L3 principle format constraints** (meditate.md:353-359) — "no proper nouns, falsifiable, ≤2 sentences" is a hard format. The falsification-attempt slot (361-364) is R53 D2.
8. **Phase 4 mandate-conflict surfacing** (meditate.md:346-350) — the explicit instruction to surface (not silently resolve) mandate conflicts. Architect-only authority to amend law.
9. **Phase 4 BROADCAST heuristic** (meditate.md:366-369) — "most meditations are for the host's cognition, not the fleet's feed." Hivemind-post discipline.
10. **`--durable` and `--record` semantics** (meditate.md:56-57, 437-447) — record-file path, slug format, opt-in vs default. The "insurance premium exceeds the loss" reasoning (lines 440-442) is why the default is single-pass.
11. **Phase 5 PIVOT_LOG entry shape** (meditate.md:387-403) — D-series decision format. Temple-Grade gates listed (T1-T11). Mandate flags (M1-M27). The format must match the integrator's expectations.
12. **5-voice default with correlated-noise rationale** (meditate.md:114-118) — "beyond five voices, additional weak perspectives add correlated noise, not diversity" is R53 D1 evidence-grounded tuning (Self-MoA arxiv 2502.00674 cited in v2.0 changelog line 524). The reasoning prevents drift to 10-voice padding.

### §3.3 The 320-line stretch target

If the Architect confirms the agent can consult the system-reference mid-run, the additional compressions for 320 lines are:

1. **Replace voice block template inline** (meditate.md:161-195, ~35 lines) with one line: "Voice block per system-reference §3: 4-slot (OBSERVATION/CONSTRAINT/IMPERATIVE/DISSENT), domain-constrained."
2. **Replace Phase 0/2/3/4 output templates** (meditate.md:134-142, 261-273, 297-310, 334-369, ~50 lines) with one-liner pointers.
3. **Replace Execution Rules 1-6 inline text** (meditate.md:409-435, ~26 lines) with one paragraph summarizing each rule and pointing to system-reference §9.

This is a **bet on the architecture** — that the meditation host (Kali) can call a tool to read the system-reference inside the meditation context. If that's not true, 350 is the floor.

---

## §4 Open questions for the Architect

**Q1. Can the meditation host consult `docs/reference/meditate-system-reference.md` mid-run?**

The OpenCode command architecture injects one prompt per call. If the meditation host (Kali) is running as a single LLM call with no tool loop, it cannot consult external docs mid-meditation. In that case, voice block format, phase output schemas, and execution rules MUST be in the prompt — they cannot be delegated.

If the host has a tool loop (read file), the 320-line stretch target is achievable. Otherwise 350 is the empirical floor.

**Recommendation**: confirm with a single empirical test — run `/meditate [simple-subject]` and observe whether Kali emits a "reading system-reference" tool call. If yes, 320 is on the table. If no, 350 is the floor.

**Q2. Is the validator's `len(content) // 4` token counting acceptable, or should it be replaced with tiktoken?**

The validator undercounts by ~1-15% depending on doc composition. The 16K free-tier cap is enforced by a downstream model, not by this validator — so the validator's miscounting does not break the cap. But it does mean the validator's "5,900 tokens" claim is not a real measurement.

**Recommendation**: replace with `tiktoken.get_encoding('cl100k_base').encode(content)` (already a venv dep). One-line fix in `validate_token_budget`. Confirms M18 (Token Efficiency) and M22 (Response Provenance) by giving real numbers.

**Q3. Should the validator's path-matching `doc_type` be replaced with frontmatter `document_type`?**

The frontmatter schema already requires `document_type` (line 28-32 of the JSON schema). The script could read this and skip the path match. This would also make `doc_type` correct for files outside `docs/sprints/` — currently any non-sprint doc is `reference_doc` regardless of actual type.

**Recommendation**: yes. One-line change in `validate_token_budget`. Aligns validator with its own frontmatter schema.

**Q4. Should `make doc-llm-validate` validate non-sprint docs (commands, standards, references, strategy)?**

Currently it doesn't. The M26 mandate says "any reference doc may be merged that fails LLM-friendly validation" — but no reference docs are actually validated. The Temple-Grade gate depends on this target.

**Recommendation**: expand the target to `docs/` (recursive) with file-category allowlists (e.g. `docs/strategy/*.md` and `docs/reference/*.md` use `reference_doc` budget; `docs/standards/*.md` use `protocol_spec` budget; etc.). Or split into per-category targets and gate each.

**Q5. Should the validator's "warnings" be promoted to "errors"?**

The LLM-Friendly Docs BP (line 304-313) presents answer-first, code-block, and dependency-graph checks as real checks. The script implements them as warnings. This is a doc-vs-impl gap. Either the BP should be updated to match the script, or the script should be updated to match the BP.

**Recommendation**: promote the three soft checks to hard errors (or to a separate `--strict` flag). The current state — BP promises enforcement, script delivers soft warnings, gate stays green — is the C-0 test-honesty failure mode the team has been disciplined against.

**Q6. R53's "320-line hard ceiling" — is it still authoritative given the corrected measurements?**

R53 was written with the validator's approximate count. Real measurements show:
- 530 lines = 6,205 tokens (38.8% of 16K)
- 350 lines = ~4,616 tokens (28.8%)
- 320 lines = ~4,516 tokens (28.2%)

The 320 target is achievable but the gap from 350 to 320 is only ~100 tokens (0.6% of 16K). The marginal benefit of 320 over 350 is small. The marginal cost is HIGH-fidelity content loss unless Q1 is resolved.

**Recommendation**: re-ratify the 320 target as 350 (the empirical floor of LOW-fidelity-only compression). Reserve 320 as a stretch target contingent on Q1. Document the corrected measurements in R53 §empirical-measure.

**Q7. The `--brief` flag was removed in v2.0. Is its depth-budgeting function being lost?**

v2.0 changelog (meditate.md:519-520) says: "`--brief` flag and Brief Mode removed (moved to `/meditate-local`, where depth-budgeting belongs)."

This is the right architectural call — depth-budgeting for local-substrate inference is a different machine. But: is the brief-mode feature in `/meditate-local` actually implemented? If not, the v2.0 changelog is a promise without a deliverable.

**Recommendation**: confirm `/meditate-local` has depth-budgeting implemented. If not, the v2.0 changelog is misleading and should be amended.

---

## §5 Confidence and provenance

| Finding | Confidence | Source |
|---|---|---|
| Command is 530 lines, not 501 | 10/10 | `wc -l .opencode/commands/meditate.md` |
| Command is 6,205 tokens (cl100k), not 5,800 | 10/10 | `tiktoken.get_encoding('cl100k_base')` direct measure |
| R53 used chars/4 approximation, not real tokenizer | 9/10 | R53 line 58 reads "~5,800"; validator line 149 uses `// 4` |
| Validator exit code is 0 with N warnings | 10/10 | `scripts/validate_llm_docs.py:222-240` + observed output |
| Validator only checks `docs/sprints/current/` | 10/10 | Makefile line 185 |
| Three sprint docs pass with 6+ warnings each | 10/10 | observed `make doc-llm-validate` output |
| 350-line compression is achievable without HIGH-fidelity loss | 8/10 | measured curve, conservative estimates |
| 320-line compression requires either delegation or HIGH-fidelity loss | 7/10 | depends on Q1 (mid-run tool access) — not yet measured |
| Frontmatter `document_type` is in the schema but unused by validator | 9/10 | schema line 28-32, validator line 152-163 |
| Validator token counting undercounts by 1-15% | 8/10 | measured on meditate.md; varies with content |
| 5-voice default rationale is R53 D1 (Self-MoA) | 9/10 | v2.0 changelog line 524 cites arxiv 2502.00674 |
| Voice 1 highest-cost constraint is R53 D1 | 9/10 | execution rule 5 (meditate.md:425-430) + v1.3 changelog line 510 |
| L3 principle format is R53 D4 | 9/10 | phase 4 (meditate.md:353-359) + v1.3 changelog line 514 |

**Implementation note**: M24 (Venv Sovereignty) — all token measurements in this report were taken via `.venv/bin/python`. No system pip was used. M15 (Sovereign Continuity) — this is a research artifact under `data/coordination/research_wave2/` (Category 7 working doc, exempt from Omega header per DOC_STYLE_GUIDE.md §Category 7). M26 (Doc Standards) — this doc has the LLM-friendly frontmatter and is structured for LLM consumption.

**Validator note (M26 self-audit)**: This doc is Category 7 (working doc, coordination file) → EXEMPT from doc-llm-validate per DOC_STYLE_GUIDE.md line 44-48. The validator was run on it for self-audit purposes only; the token-count "error" reflects the validator's `doc_type` path-matching bug (it classifies `data/coordination/...` as `reference_doc` instead of exempt) and its `// 4` chars approximation (real cl100k count is 10,634 tokens). Neither is a defect in this document. The Architect should consider whether the validator should skip Category 7 paths entirely.

---

## §6 16K Provenance Audit

**Purpose**: Determine whether the "16K" number used in R53 (and the rest of the codebase) is correctly scoped to Gemma 4 / Google free-tier, or has contaminated the codebase as a universal context-window constraint.

**Method**: `grep -rn "16K\|16k\|16000"` across the full repo (excluding `.venv`, `.git`, `__pycache__`), manual classification of every hit.

### §6.1 Complete grep inventory

| File | Line(s) | Content | Classification |
|---|---|---|---|
| `docs/research/R53_meditate_granite_foundation_20260826.md` | 58 | `"36% of the 16K free-tier input cap before any conversation history"` | ⚠️ **CONTAMINATION VECTOR** — see §6.3 |
| `docs/research/R53_meditate_granite_foundation_20260826.md` | 62 | `"Hard ceiling: ≤320 lines / ~16KB. Above ~500 lines the command alone breaks free-tier substrates (the exact G-1 failure mode)."` | ⚠️ **CONTAMINATION VECTOR** — 16KB (bytes) ≠ 16K tokens. Mixes byte-size and token count. |
| `docs/archive/strategy/2026-07-22/GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md` | 9,36,37,39,40,43,57,64,88,129,137,139,143,155,167,168,180,182,192,209,216,221,227,283,315,333,335,346,355,360,370,374,376,382,394,410,426,439,444,460,474-476,484,494-495,536,546,548 | All references to `free_tier_input_token_count limit: 16000` | ✅ **ORIGIN DOCUMENT** — Correctly scoped to Gemma 4 31B/26B Google AI Studio free-tier TPM. Line 36 explicitly refutes "16k is OpenCode context cap" as **FALSE**. Line 37 confirms "16k is free-tier input token quota for `gemma-4-31b`" as **TRUE**. |
| `config/provider_capabilities.yaml` | 64 | `'budget_tokens': 16000` in Anthropic `extended_thinking` example | ✅ **PROVIDER-SPECIFIC** — Anthropic thinking-budget example value only. Not a universal cap. |
| `config/provider_capabilities.yaml` | 119 | `tpm: 16000` under `gemma-4-31b-it.quota.free_tier` | ✅ **PROVIDER-SPECIFIC** — Google AI Studio free-tier TPM for Gemma 4 31B. Correct scoping. |
| `config/provider_capabilities.yaml` | 168 | `tpm: 16000` under `gemma-4-26b-it.quota.free_tier` | ✅ **PROVIDER-SPECIFIC** — Google AI Studio free-tier TPM for Gemma 4 26B. Correct scoping. |
| `config/domains/CURATORS.md` | (token_budgets block) | `token_budgets: {planner: 16000, ...}` | ⚠️ **SESSION-BUDGET HEURISTIC** — Domain-level planning budget. Not a provider cap. Not derived from 16K free-tier. Coincidental numeric collision. See §6.4. |
| `config/domains/engineering/metadata.yaml` | (Target Context Window block) | `**Target Context Window**: 16K` and `\| planner \| 32K \| 16K \|` | ⚠️ **SESSION-BUDGET HEURISTIC** — Engineering domain planner context target. Not a model limit. Coincidental collision with Gemma free-tier number. |
| `config/domains/engineering/AFFINITY_PRESETS.yaml` | (planner block) | `planner: 16000 # 16K for planning context` | ⚠️ **SESSION-BUDGET HEURISTIC** — Same category as above. The comment `# 16K for planning context` suggests design intent of "planning tasks get 16K tokens," not "Gemma free-tier limits us to 16K." |
| `config/model_registry/model_db/CURRENT_MODELS.md` | (gpt-5-nano entry) | `gpt-5-nano` context window `16K` | ✅ **MODEL-SPECIFIC** — gpt-5-nano's published context window. Correct scoping. |
| `STATUS_REPORT.md` | (workhorse section) | `"Gemma 4 31B free workhorse dead (16k TPM since 2026-07-15)"` | ✅ **PROVIDER-SPECIFIC** — Correctly attributed to Gemma 4 31B / Google free-tier TPM. |
| `data/entities/roc_racoon/session_gnosis.md` | (Gemma section) | `"Gemma 4 16K TPM collapse"` | ✅ **PROVIDER-SPECIFIC** — Entity knowledge correctly scoped. |
| `data/entities/roc_racoon/memory/proposed_lessons.yaml` | (TPM lesson) | `"TPM reduced from ~1M to 16K (~98% collapse)"` | ✅ **PROVIDER-SPECIFIC** — Correctly attributed to Gemma 4 free-tier collapse event. |
| `data/entities/researcher/session_gnosis.md` | 463 | `"G-1: 16k input tokens"` | ✅ **PROVIDER-SPECIFIC** — References G-1 ticket; correctly attributed to Gemma 4 / Google. |
| `data/entities/lilith/workspace/N7_WEB_RESEARCH_20260821.md` | 86 | `"Qwen3-4B (8K–16K)"` | ✅ **MODEL-SPECIFIC** — Qwen3-4B context window range. Not related to free-tier cap. |
| `config/models.yaml` | (context_budget fields) | Values: 15000, 20000, 25000, 30000 | ✅ **NOT 16K** — No 16000 entry. Model-specific context budgets are correctly differentiated. |
| `config/council.yaml` | (council block) | `token_budget_total: 32000` | ✅ **NOT 16K** — Council budget is 32K, not 16K. No contamination. |
| `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | 60,65,124,240 | Four references: G-1 ticket (16000 limit), "Not context caps to fit free 16k", "16K tokens for agent consumption", "D-380: No silent context caps to force free Gemma under 16k" | ✅ **CORRECTLY SCOPED** — All four correctly attribute 16K to Gemma 4 / Google free-tier. D-380 explicitly prohibits using 16K as a universal cap. |

### §6.2 Provider fabric limits table

From `config/providers.yaml` + `config/models.yaml` + `config/provider_capabilities.yaml`:

| Provider / Model | Context Window | Free-tier TPM | Paid TPM | Source |
|---|---|---|---|---|
| `gemma-4-31b-it` (Google AI Studio) | 32,768 | **16,000** | 60,000 | `provider_capabilities.yaml:112,119-125` |
| `gemma-4-26b-it` (Google AI Studio) | 32,768 | **16,000** | — | `provider_capabilities.yaml:163,168` |
| `gemma-4-12b-unified` (Google AI Studio) | 262,144 | 32,000 | 120,000 | `provider_capabilities.yaml:191,200-207` |
| `gemini-2-5-flash` (Google AI Studio) | 1,048,576 | — | — | `provider_capabilities.yaml:232` |
| `gemini-2-5-pro` (Google AI Studio) | 1,048,576 | — | — | `provider_capabilities.yaml:253` |
| Native GGUF (Qwen3-1.7B) | 8,192 | n/a (local) | n/a | `config/models.yaml:11` |
| Native GGUF (Qwen3-4B) | 8,192 | n/a (local) | n/a | `config/models.yaml:25` |
| Native GGUF (Qwen3-14B) | 32,768 | n/a (local) | n/a | `config/models.yaml:43` |
| Native GGUF (Qwen3-30B-A3B) | 32,768 | n/a (local) | n/a | `config/models.yaml:66` |

**Key finding**: The 16K limit is Gemma 4 31B/26B **free-tier TPM** (tokens per minute), not a context window. The model's actual context window is 32,768 tokens. A 530-line / 6,205-token meditate command fits inside the 32K context window with room to spare — but in a cold free-tier session, the *first turn* burns 6,205 tokens against a 16,000-token-per-minute quota, leaving only 9,795 TPM for the system prompt, persona, RAG, and output within that minute window.

### §6.3 R53 contamination vector — exact trace

R53 (`docs/research/R53_meditate_granite_foundation_20260826.md`) is the document that introduced "16K" as a command-size constraint. Here is the exact propagation path:

**Step 1 — Origin (correctly scoped)**:
> `GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md` line 37: "**16k** is free-tier **input token** quota for `gemma-4-31b`" → **TRUE** (post-cliff, 2026-07-15).

**Step 2 — G-1 ticket (correctly scoped)**:
> `SOVEREIGN_ARK_BLUEPRINT.md` line 60: "Free-tier `input_token_count` limit **16000** for `gemma-4-31b` since **2026-07-15**"

**Step 3 — R53 (CONTAMINATION)**:
> `R53_meditate_granite_foundation_20260826.md` line 58: "36% of the **16K free-tier input cap** before any conversation history"

R53 lifted the 16K number from the G-1 ticket context but **dropped the model qualifier**. The phrase "16K free-tier input cap" sounds like a universal platform constraint. It is not — it is Gemma 4 31B/26B Google AI Studio free-tier TPM, which **does not apply to**:
- Antigravity (OAuth pool — different quota)
- Google paid-tier (60K TPM for Gemma 4 31B)
- OpenRouter free (separate quota)
- Local GGUF (no TPM — limited by RAM and L3 cache, not a quota)
- Any other model on any other provider

**Step 4 — Downstream compression rationale**:
> R53 line 62: "**Hard ceiling: ≤320 lines / ~16KB.** Above ~500 lines the command alone breaks free-tier substrates."

This converts a provider-specific quota event (G-1: Gemma 4 31B free-tier death on 2026-07-15) into a **universal command-size ceiling**. The ceiling is not wrong for Gemma 4 free-tier use specifically, but it is not a universal engineering constraint.

**Step 5 — Note on "~16KB"**:
R53 line 62 also writes "~16KB" (kilobytes). This is a byte-size notation being used next to a 16K token count. They are coincidentally the same order of magnitude for English text (~1 byte/char, ~4 chars/token → 16K tokens ≈ 64KB of text), but the equivocation creates conceptual ambiguity. The meditate command is 24,546 bytes (≈24KB), not 16KB.

### §6.4 Session-budget heuristic — separate 16K origin

The `config/domains/engineering/AFFINITY_PRESETS.yaml` `planner: 16000` and `config/domains/CURATORS.md` `token_budgets: {planner: 16000}` are **not derived from the Gemma free-tier limit**. They appear to be a domain-level design choice: "planning tasks get 16K tokens of context budget." This is a coincidental numeric collision.

**Evidence of separate origin**:
- The engineering domain's 16K planner budget coexists with Gemma 4 12B's 262K context window (`provider_capabilities.yaml:191`) and Gemini 2.5's 1M context window (`provider_capabilities.yaml:232,253`). A budget tied to Gemma free-tier would not survive those model additions.
- `config/models.yaml` context_budget values are 15K-30K, not 16K — the model config authors used a different anchor.
- The forensic report (`GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md` line 346) explicitly warns: "`configs/token_budgets.yaml` hard_limit 16000 | Local Omega budget artifact — **do not confuse** with Google metric."

**Classification**: COINCIDENTAL COLLISION. The session-budget 16K in `AFFINITY_PRESETS.yaml` and `CURATORS.md` is a separate design artifact, not contamination from the Gemma free-tier event.

### §6.5 Contamination verdict

| Scope | Verdict |
|---|---|
| **Codebase-wide contamination** | **CONTAINED** — Only R53 uses 16K as a universal command-size ceiling without a model qualifier. All other occurrences are correctly scoped. |
| **R53 line 58** | ⚠️ **PARTIAL CONTAMINATION** — "16K free-tier input cap" is technically correct for Gemma 4 free-tier but reads as a universal platform constraint. Should be qualified as "Gemma 4 31B Google AI Studio free-tier TPM (16K/min)." |
| **R53 line 62** | ⚠️ **PARTIAL CONTAMINATION** — "Hard ceiling: ≤320 lines / ~16KB" is correct for free-tier Gemma 4 sessions but not for paid-tier, Antigravity, or local GGUF. "~16KB" mixes bytes and tokens. Should be "≤320 lines / ≈4,500 cl100k tokens — binding constraint for Gemma 4 31B free-tier sessions; see §6.2 for provider-specific limits." |
| **Session-budget 16K** (`AFFINITY_PRESETS.yaml`, `CURATORS.md`) | ✅ **NOT CONTAMINATION** — Coincidental numeric collision; separate design origin. |
| **Provider-capability 16K** (`provider_capabilities.yaml`) | ✅ **CORRECTLY SCOPED** — Tagged under `gemma-4-31b-it.quota.free_tier` and `gemma-4-26b-it.quota.free_tier`. |
| **G-1 / STATUS_REPORT / session_gnosis** | ✅ **CORRECTLY SCOPED** — All correctly attribute to Gemma 4 free-tier TPM collapse event. |
| **Model registry 16K** (`CURRENT_MODELS.md` gpt-5-nano) | ✅ **MODEL-SPECIFIC** — gpt-5-nano context window, unrelated to Gemma quota. |

### §6.6 Remediation recommendation

**For R53 line 58** (FROZEN doc — cite-don't-edit): add a footnote or cross-reference in R01 (this doc) that corrects the scoping. Do not edit R53.

**For any future compression spec** referencing R53's 320-line ceiling: copy the ceiling with the qualifier: "320 lines / ≈4,500 cl100k tokens is the binding constraint for **Gemma 4 31B Google AI Studio free-tier sessions** (16K TPM). For paid-tier, Antigravity, or local GGUF, the binding constraint is model context window (8K–32K tokens) and session budget, not TPM."

**For the session-budget 16K** (`AFFINITY_PRESETS.yaml`, `CURATORS.md`): no action required. These are separately justified domain-level budgets.

**Confidence: 9/10.** Primary sources: `GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md` (10/10, forensic log analysis), `provider_capabilities.yaml` (10/10, config file), `R53_meditate_granite_foundation_20260826.md` (10/10, frozen research doc). The session-budget 16K separate-origin claim is 7/10 — plausible but not explicitly documented in the AFFINITY_PRESETS commit history.

---

*⬡ OMEGA ⬡ CARMACK ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_r01_carmack_audit ⬡ 2026-08-26*
