<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# N11 evaluator — Mining Brief (T2)
**AP**: AP-N11-MINING-v1.0.0 · **Date**: 2026-08-22 · **Curator**: Jem (N11 evaluator, Model Quality & Evals) · **Miner**: roc_racoon (fresh session, read-only except the two output paths)

## Mission
Build the foundational Knowledge Base for Node N11 (Model Quality & Evals): inventory and digest every eval/benchmark/experiment-harness asset in the Omega Engine repo, extract interfaces, wiring surfaces, constraints, and gaps, and record file:line evidence for every claim. Output feeds N11 charter ratification and future lm-eval/promptfoo adoption work.

## Output Contract
Miner writes EXACTLY TWO files, nothing else:
1. `data/entities/jem/workspace/N11_EVALUATOR_KB_20260822.md` — sections in order:
   - `## Source Inventory` (table: path / status / priority / one-line role)
   - `## Per-Source Digests` (one subsection per source; every claim cited `file:line`)
   - `## Gotchas` (numbered; each = surprise/drift/contradiction found during mining, with file:line)
   - `## Open Questions` (numbered; things needing Pager/Jem ruling)
   - `## L2/L3 Insights` (structured-gnosis format per SO-10a: each entry has `narrative:` (L1), `insight:` (L2), `principle:` (L3); tag `[N11]`)
2. Append nothing to this brief. No other writes. No code edits.

## Source Inventory
### P0 (must digest)
- `src/omega/eval/__init__.py`, `runner.py`, `check.py`, `calibrate.py` — module interfaces, entry points, public API, RAGAS vocabulary usage. NOTE: check.py:3 and calibrate.py:3 carry LILITH/S2 tags — record exact header of each module.
- `src/omega/research/sandboxes/*` — all sandbox modules; ml_training.py:3 self-tags `MA'AT ⬡ N6` (record all headers); identify scorecard/sediment pipeline references.
- `docs/decisions/PIVOT_LOG.md` D-585 entry (lines ~252–260) + any other eval-related decisions (grep for `eval|benchmark|RAGAS|lm-eval|promptfoo`).
- Eval-related tests: glob `tests/**/test_*eval*`, `tests/test_scorecard.py`, `tests/test_integration_new_systems.py` (runner usage at :48), any test importing `omega.eval`.
- `data/entities/researcher/workspace/NODE_GAP_WEB_RESEARCH_JEM_20260822.md` §W1.
- `data/entities/roc_racoon/workspace/NODE_GAP_LOCAL_DISCOVERY_ROC_20260822.md` §L8.

### P1 (digest if present)
- `config/roles.yaml` — check DR-7 staleness vs D-585 matrix (Qwen3-4B planner / Qwen3-4B-Thinking executor / Qwen3-1.7B critic).
- `pyproject.toml` — are `lm-eval`, `promptfoo`, `ragas` declared anywhere (deps/extras)?
- Provider fabric wiring surface for a local-completions→llama.cpp backend: `src/omega/oracle/model_gateway.py` (get_model_path/get_model_spec), `config/providers.yaml` native-gguf section (~lines 130–200), `config/models.yaml` (NOTE: no qwen3-4b-thinking entry as of validation — confirm).
- OOMProtector / admission control constraints relevant to benchmark runs: grep `OOMProtector|admission|semaphore` under `src/omega/oracle/`.
- Scorecard/sediment pipeline: `tests/test_scorecard.py`, grep `sediment` across src/.

### P2 (skim, cite only notable hits)
- Docs mentioning RAGAS/metrics/benchmarks: grep docs/ for `ragas|lm-eval|promptfoo|benchmark`.
- `data/coordination/ACTIVE_SPRINT.json` LI workstream entries touching eval/models.

## Extraction Questions (minimum set)
1. What are the public interfaces/entry points of `src/omega/eval/{runner,check,calibrate}.py`? Who imports them today?
2. What existing test coverage exercises eval modules?
3. What exactly does D-585 claim, and what is its implementation status across providers.yaml / opencode.json / models.yaml?
4. How would lm-eval `local-completions` wire to the current fabric (llama.cpp server surface, model paths, context budgets)?
5. What CPU/OOM/admission-control constraints bound a benchmark run (RAM ceilings, semaphore, MemoryMax)?
6. What IS the scorecard/sediment pipeline — where does it live, who consumes its outputs?
7. Who consumes eval outputs today (CLI, MCP hub tools, CI gates)?
8. Where do the LILITH/S2 tags on eval modules conflict with the "unowned" premise?

## Constraints
- READ-ONLY except the two output paths above.
- Every claim cites `file:line`. No uncited assertions. If a source is absent, say ABSENT with the glob/grep you ran.
- Freshness: tag the KB with `last_verified: 2026-08-22`.
- Token efficiency (M18) with sane-boundary: precision over brevity; do not omit edge cases.
- Do not resolve open questions — record them.
