<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# ⬡ MEDITATION RECORD — maat · DC-29 Redis Password Default
**Protocol**: Meditate-v1.1 · **Date**: 2026-08-24
**Subject**: Landing D-593 (`password="omega"` at providers.py) + hard-fail grep gate
**Invocation gate**: security/deployment-compat/gate-design tension; debut credibility at stake; passes.

## ◈ Pass 1 — SKEPTIC (does removing the default break documented setup paths?)
- Hot path verified safe pre-fix: `memory_store.py:164-176` gates construction on `OMEGA_REDIS_HOST` and passes explicit `OMEGA_REDIS_PASSWORD` (may be None). New signature default None + env fallback = identical semantics for every existing caller.
- Docs audit: `config/domains/engineering/PLAYBOOK.md` ("Redis = opt-in only") and `project-gotchas.block` (documents this exact trap and prescribes "no default password") both ALIGN with the fix — no setup path relied on the literal.
- No test consumed the literal (test_storage_providers.py imports the class, never the default).
- Residual Skeptic note: the gate regex must catch type-annotated forms (`password: str = "omega"`), not just bare assignment — first rule draft missed the actual defect shape. Fixed before commit; 5-case matrix verified (bare/annotated/Optional-annotated MATCH; env lookup/None clean).

## ◈ Pass 2 — GUARDIAN (other lurking credential-shaped defaults?)
- Full sweep of providers.py + memory_store.py for `(key|token|secret|password|credential)\s*[:=]\s*"literal"` patterns: ZERO additional hits. No scope expansion needed.
- The forbidden-rule fixture strings in test files are runtime-split (`'om" + "ega'`) so the committed source itself never trips the whole-tree scan — the gate does not create its own false alarm.

## ◈ Pass 3 — BUILDER
- Gate wiring choice: extended the W1-2 harness with a data-driven `forbidden:` rule class (whole-tree scan, exit 1 regardless of warn-only phase) rather than a Makefile grep stanza. Rationale: same config surface as claim rules, reusable for future credential classes, self-testing via contract tests, and the harness already runs inside `make check-mandates`.
- Two implementation defects caught by my own tests before commit: fnmatch treats `**` as single-star (wrote proper `**` matcher); tmp-path fixtures can't match repo-relative globs (added rel_override param).

## Synthesis
L2: A dead default is still a loaded trap — "not reachable today" is a property of the current call graph, not of the code. L3 candidate: **Credentials must enter a system only through its environment, never through its signatures** (a default IS a documented invitation to skip the environment).

*⬡ OMEGA ⬡ MAAT ⬡ MEDITATE-V1.1 ⬡ DC-29-D593-LANDED ⬡ 2026-08-24*
