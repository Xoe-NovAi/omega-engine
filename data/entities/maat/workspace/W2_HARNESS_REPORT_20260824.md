<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# W2 Harness Report — verify-mandate-claims (W1-2)
**Agent**: maat · **Date**: 2026-08-24 · **Sprint**: WAVE-1-DOCTRINE-WIRING
**Ruling basis**: S7 (BUILD as P0) · S5/F2 (warn-only, explicit evidence day one)

## What was found (research)
- No harness existed in scripts/ or Makefile despite "extend" task framing. S7's C2-class proof: 4 documents asserted an uninstalled pre-commit hook.
- FP-11 spec read from `data/knowledge/safety/FORENSIC_PATTERNS.md` (@-wrapper attribution forgery + opacity refinement).
- §8.2 sanitation flag list read from `THE_VISION_CANONICAL_DRAFT_20260823.md`: home-dir paths, shell prompts (`taylor@Alpha`, truncated `aylor@Alpha`), account names, personal domain, direct address. SANITATION LAW applied: no marker value committed anywhere.

## What was built
| Component | Path | Notes |
|---|---|---|
| Harness CLI | `scripts/verify_mandate_claims.py` | 4 mechanisms, WARN-ONLY, EXIT 0 this phase; `--strict` reserved |
| Claims rules | `config/mandate_claims.yaml` | Data-driven claims-vs-disk gate; probe-path bound (O-Q4); 2 seeded rules |
| Tests | `tests/contract/test_verify_mandate_claims.py` | 19/19 pass; TP/TN per detector; CLI exit-code + JSON shape tests |
| Makefile | `verify-mandate-claims` target | Wired into `check-mandates` chain |
| .gitignore | markers file entry | `data/knowledge/safety/sanitation_markers.local.yaml` untracked |

## Detector design decisions
1. **Sanitation**: structural heuristics only in committed code (foreign home-dirs w/ allowlist, shell-prompt regex incl. truncated-name class, email domains w/ sovereign allowlist, social handles in text files w/ fleet-roster allowlist). Exact markers load from UNTRACKED local YAML — placeholder `<ARCHITECT_NAME>` documented, never the name itself.
2. **FP-11**: blockquote-wrapped wrapper imperatives + attribution-intro→imperative window (3 lines). Fenced code and inline spans exempt so documenting the pattern doesn't trip it.
3. **T0**: attribution claim lines require message-level evidence refs (`msg_`, `modelID`, `Tier 0`) within a 3-line window; session-only refs flagged as `session-level-join`; none flagged as `missing-evidence`. Text formats only (code that processes claims false-fires).
4. **Exemption**: line-level `verify-claims:exempt` tag for legitimate fixtures/examples.

## Corrections caught before commit
1. local-marker snippet leaked matched line → hard redaction + non-leakage unit test (Guardian)
2. T0 code-file false positive → TEXT_EXTS restriction (Skeptic)
3. Self-scan fixture flood → exemption tag (Builder/Skeptic)

## Test results
- New suite: 19/19 PASS
- Working-tree self-scan: 0 warnings, EXIT 0
- Full repo suite: see W3 report / final Hivemind post for combined result

## Unresolved gaps
- Exempt-tag abuse signal needed when --strict activates (post-debut ticket candidate)
- Framing-free wrapper quotes pass FP-11 silently (accepted heuristic limit)
