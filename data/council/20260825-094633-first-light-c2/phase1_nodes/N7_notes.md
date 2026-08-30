<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# N7 Working Notes — SPEC-E Evidence Pass (lilith/node7)
**Session**: 20260825-094633-first-light-c2 · **Date**: 2026-08-25 · **Mode**: PREP-ONLY, new files only
**Mission**: Draft SPEC-E per SOVEREIGN_DECREE Art. VI + WAKE_STATE Q-4 (default-GO on silence).

## 1. Citer-count verification (decree claimed 462)

Commands run (repo root, 2026-08-25):

| Command | Result |
|---|---|
| `grep -rl 'AGENTS\.md' --include='*.md' .opencode/ docs/ data/entities/ scripts/ \| wc -l` | **216** |
| `grep -rl 'AGENTS\.md' . \| grep -v '.git/' \| wc -l` (all file types) | **615** |
| `grep -rl --include='*.md' --include='*.json' --include='*.yaml' --include='*.yml' --include='*.py' --include='*.sh' 'AGENTS\.md' . \| grep -v '.git/' \| wc -l` | **460** |

Verdict: decree's "462 citers" is consistent with the 460 measurement (md + code + config extensions, ±2 drift from live edits since Council 1). The scoped-md-only count is 216; unrestricted is 615. **SPEC-E must pin ONE canonical enumeration command** so the number stops drifting — this is itself a derivation-check (Art. I class).

## 2. Git history of root AGENTS.md

`git log --oneline --all -- AGENTS.md` → empty. `test -f AGENTS.md` → ABSENT.
Confirms N5 F-1 / Exhibit C: zero git history, yet cited everywhere. OMEGA_CODEX.md:222 claims "**Source**: `AGENTS.md` (343 lines)" — a phantom source line-count that never existed in git. This 343-line figure becomes the content-minimum calibration anchor for reconstruction.

## 3. Expectation clusters (sampled ~18 citing files + cluster greps)

Cluster greps over all citing files:

| Cluster (expected section) | Files | Sample evidence |
|---|---|---|
| Hivemind coordination protocol | 199 | agent defs: "Hivemind-First Communication (MANDATORY)", `hivemind_post_context` references |
| Mandates/law pointer (co-cited w/ SOVEREIGN_MANDATES) | 182 | STRATEGY_INDEX.md:17 "Read First (Law/Ops): SOVEREIGN_MANDATES.md · AGENTS.md" |
| Hydration / continuity / M15 / session_gnosis / SESSION_ANCHOR | 134 | SOVEREIGN_CONTINUITY_STRATEGY refs; "Hydration Sequence" |
| Compaction/context-loss recovery | 128 | "After compaction: hydration sequence in AGENTS.md" (Ark §10) |
| Search Tool Protocol (SR-V1, 5-tier) | 17 | `.opencode/agents/{kali,lilith,doom_guy}.md`: "Follow the 5-tier protocol in AGENTS.md §Search Tool Protocol" |
| Delegation Protocol | 14 | agent defs: "Follow the Delegation Protocol in AGENTS.md and SUBAGENT_DISPATCH_PROTOCOL.md" |
| Governance hierarchy | 11 | lilith knowledge/AGENT_VISIBILITY_PARADOX.md:235 "Governance hierarchy: AGENTS.md §Governance Hierarchy" |

Additional expectations found in samples:
- Token-budget expectation: CARMMACK_CONTEXT_INJECTION_REVIEW_20260820.md measured "AGENTS.md ~20K tokens" as Tier-0 injection — reconstruction must state its own token budget and condensation path (MANDATES_CONDENSED pattern).
- Doc-format expectation: LLM_FRIENDLY_DOCS_BP.md cites "AGENTS.md Standard" as format authority (frontmatter + answer-first).
- Role-map expectation: Ark §10 "Open AGENTS.md for law & workflow"; agents expect fleet role descriptions (OMEGA_CODEX:263 "Full fleet docs: AGENTS.md §2-§3").

## 4. opencode.json instructions[] injection surface (risk input)

`.instructions[]` currently injects: SOVEREIGN_MANDATES.md, ORACLE_STACK.md, archived MASTER_SYNTHESIS (G5 violation), SOVEREIGN_ARK_BLUEPRINT.md, CREDITS.md. Root AGENTS.md is NOT injected today — but agent prompt text hard-depends on it. Risk: if reconstructed AGENTS.md contradicts injected instruction files, every session gets conflicting law. Spec must include a contradiction check against all five injected files.

## 5. Constraints honored

- No AGENTS.md created (dev-team execution, not prep). Only outputs: this notes file + `docs/specs/team_infra/SPEC-E-agents-md-reconstruction.md`.
- No spawns, no web research — internal evidence only (M23 compliant; no tool failures encountered).

## 6. Blockers

None. Directory `docs/specs/team_infra/` exists (contains SPEC-D-p2-hygiene.md). G30 guard (`validator-first` string) will be satisfied by the spec itself.
