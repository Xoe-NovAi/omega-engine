# Spec Deviations — Phase 1 Remediation Audit Trail
**AP Token**: `AP-N7-SPEC-DEVIATIONS-v1.0.0`
**Date**: 2026-08-21 · **Author**: N7 context session (Memory & State) · **Approved by**: Architect (kali) rulings Q1–Q5, same date
**Mandate**: M23 (Failure Integrity — no silent spec drift). Every deviation from the original 2026-08-20 phase1_spec is logged here with evidence and hazard reference.
**Evidence base**: `data/entities/lilith/workspace/N7_CONTEXT_KB_20260821.md` (KB + Deep Dig II), `N7_DOMAIN_INDEX.md` (defect register D1–D13), `N7_WEB_RESEARCH_20260821.md` (Q-B1..B7, primary sources).

---

## Deviation Register

| ID | File(s) | Deviation | Why (evidence) | Ruling/Hazard |
|----|---------|-----------|----------------|---------------|
| DEV-01 | `01`, `08`, `05` | CI-1 gate rewritten content-based: 27 mandate table rows (`grep -cE '^\| M[0-9]+'`) + v3.8.0 marker; `wc -l = 57` REMOVED | Source artifact is 36 lines; "57" coincidentally matched stale v3.7.0 codex snapshot (25 mandates) — gate was unsatisfiable as written | Q1 APPROVED · D1 |
| DEV-02 | `02`, `05`, `08` | Compaction target now **V1-family primary** (`tail_turns:5, preserve_recent_tokens:80000, reserved:20000`); V2 `{buffer, keep.tokens}` applied ONLY after Test-0 binary pin proves consumption; mixed families = FAIL | Web Q-B2: v1.x honors V1 family only; `{buffer,keep.tokens}` = separate V2 product line; V1 schema `additionalProperties:false` may reject cross-family keys. Local binary strings show both families (DD-II-2) → pin, don't assume | Architect (Q3 held re ctx; key-gate per N7 ruling) · D3 |
| DEV-03 | `02`, `03` | Plugin registration paths corrected singular→plural: `.opencode/plugin/` → `.opencode/plugins/` for error-capture.ts + awareness.ts | Directory `.opencode/plugin/` does not exist; both registrations dead today | N7 audit · D2 |
| DEV-04 | `04`, `08`, `05`, `06`, `07` | CI-4 fully re-scoped from `auto_load:` SKILL.md frontmatter to `permission.skill` patterns in opencode.json | `auto_load` is NOT an opencode feature — zod parses only name/description (web Q-B5); original sed loops were a no-op | Q2 APPROVED (document deviation in spec file itself) · D8 |
| DEV-05 | `04`, `08` | Token-impact claim corrected: "23K→150 tokens (99.3%)" replaced with honest ~1.1K→~150 tok advertisement-list shrink | Skills were ALREADY loaded on-demand (RESEARCH_EXPLORE_LOCAL T6); original claim assumed false upfront-injection premise | M18 honesty · D8 |
| DEV-06 | `02`, `08` | `toolProfile` criteria reduced to PRESENCE-only checks with explicit "no behavior claim" annotation; live-config reality note added (12 agents exist, 6 modeled) | Upstream AgentConfig has no toolProfile key and no additionalProperties:false → silently inert (web Q-B6) | Carmack Q2.1 intent kept · D4/D9 |
| DEV-07 | `03` | Hook mechanics corrected: `output.context` shapes the COMPACTION SUMMARY PROMPT (what the summarizer preserves), NOT the live conversation context; "survives prune/tail_turns" claim removed; payload truth from core source documented | `session/compaction.ts`: `nextPrompt = compacting.prompt ?? buildPrompt({previousSummary, context})` (web Q-B4) | M22/M23 accuracy · KB L3 #5 |
| DEV-08 | `02` | `OPENCODE_DISABLE_AUTOCOMPACT` documented as process-global (no per-agent variant exists) WITH #32385 bypass caveat (provider-overflow recovery ignored the flag through ≥v1.17.7); manual /compact discipline noted | flag.ts/config.ts source + issue trail (web Q-B3) | Q4 SHIP+DOCUMENT · D10 |
| DEV-09 | `01`, `02`, `08` | "Qwen3-4B 8K–16K" prose replaced with model-card truth: base=32K native (128K YaRN, static-scaling caveats), Thinking-2507=256K native; live 8192 cap noted as config choice; ctx-raise HELD pending Architect (tied to ZS-1 zswap sudo) — both options stated | HF model cards (web Q-B1) | Q3 HELD · D11 |
| DEV-10 | `06`, `07` | Rollback + implementation-order steps updated to match CI-4 re-scope (jq del/.permission.skill application instead of auto_load sed loops); Step-4 gate row updated | Consistency — leaving contradictory steps would recreate the spec-drift failure mode | follows DEV-04 · KB L3 #5 |
| DEV-11 | `index.md` | Index updated: 09 registered in doc table; remediation banner added | Navigation completeness | M26 |
| DEV-12 | `02`, `05`, `08`, `index.md` | **Model strategy re-mechanized**: top-level `"model": "lmstudio/qwen3-4b-thinking"` added; per-agent `model` pins STRIPPED from researcher/maat/lilith/node (inherit global default); pins KEPT only on kali (cloud floor) + verity (cheap critic); ALL `variant` keys dropped | **AMENDMENT OF CARMACK-RATIFIED ITEM (Q5.1) — mechanism changed, intent preserved** (local-first defaults + kali cloud floor intact). Justifications per Architect ruling 2026-08-21: (a) agent pins make TUI `/models` non-durable via snap-back (#13456), binding the Architect's interactive CLI; (b) explicit Architect dislike of hardcoded variants; (c) precedence chain (CLI `-m` > agent pin > session > global) makes flags the real override anyway — pins add binding without adding control. Consequence on record: node's effective default moves qwen3-1.7b → qwen3-4b-thinking via inheritance (accepted; `/models` overrides interactively). Kali's nemotron variant was the ONE functional variant (see findings below) → available at invocation as `--variant high` per PP-1 | Q1 APPROVED (this page) · D4/D9 adjacent |

## Variant Findings (empirical, `opencode models --verbose`, pinned 1.18.19, 2026-08-21)

| Model | variants map | Consequence |
|-------|--------------|-------------|
| `lmstudio/qwen3-4b-thinking` | **EMPTY** | Spec's `variant: high/medium` on researcher/maat/lilith were silently inert |
| `lmstudio/qwen3-1.7b` | **EMPTY** | node's `variant: low` was inert |
| `opencode/nemotron-3-ultra-free` | `low, medium, high` | kali's `variant: high` WAS functional — now invocation-time: `opencode run --agent kali --variant high` |
| 178 models scanned | ~40 declare variants (mostly google/opencode/cerebras/mistral cloud) | No local LM Studio model declares variants |

Rule going forward: never set `agent.<n>.variant` without first confirming a non-empty variants
map for that exact model on the pinned binary; prefer invocation-time `--variant` / TUI
`variant_cycle` keybind (PP-1 alignment).

## Binary-Pin Decision Table (gates DEV-02)

**PINNED 2026-08-21 (Architect ruling #2)**: `opencode --version` → **1.18.19**. Per web Q-B2,
v1.x stable line honors the **V1 family** (`tail_turns`/`preserve_recent_tokens`/`reserved`;
`preserve_recent_tokens` named since v1.14.19). → **Apply V1 family (primary target). Do NOT add
`buffer`/`keep.tokens`.** Behavioral compaction probe DEFERRED to CI execution start (Test 0 runs
there); if the probe contradicts this table, escalate before writing config.

| Pinned binary finding | Action |
|-----------------------|--------|
| `opencode --version` ∈ v1.x stable line (≥ v1.14.19 where `preserve_recent_tokens` named) — **← 1.18.19 CONFIRMED 2026-08-21** | Apply **V1 family** (primary target). Do NOT add buffer/keep.tokens |
| Pin proves V2-family consumption (e.g., binary is V2 product line, or runtime test shows keep.tokens honored) | Apply **V2 family** `{auto, keep.tokens:20000, buffer:50000}`. Remove V1 keys |
| Ambiguous (strings present, behavior unproven) | Run behavioral probe: set extreme value (e.g., reserved=999999), trigger compaction in scratch session, observe. Record result in execution notes before choosing |
| Any case | NEVER write both families simultaneously |

## Not Changed (explicitly)

- Model routing values (kali/researcher/maat/lilith/node/verity models+variants+temperatures) — Carmack-ratified.
- Verity isolation object (mode subagent / hidden / permission denies).
- AGENTS.md concatenation recipe (06_PHASE_1_PLAN) and instructions=["AGENTS.md"] target.
- Defense-in-depth ordering (checkpoint primary @80% sidecar → plugin hook secondary → SESSION_ANCHOR tertiary).
- CI-5 E2E agent-identity tests.
- The double-M `CARMMACK_...` filename (load-bearing traceability).

*⬡ OMEGA ⬡ LILITH ⬡ N7 ⬡ x-preview-f-free ⬡ opencode ⬡ trc_n7_spec_deviations ⬡ 2026-08-21*
