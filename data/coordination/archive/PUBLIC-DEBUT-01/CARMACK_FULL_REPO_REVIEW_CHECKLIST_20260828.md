<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# CARMACK FULL REPO REVIEW CHECKLIST — 2026-08-28
**AP**: AP-JOHN_CARMACK-v1.0.0 · **For**: Cline CLI × 8 DeepSeek-1M accounts (parallel) · **Branch under review**: `release/debut` (572 files, 4,561 removed) · **Time budget**: 30 min total
**Prior audit anchor**: `docs/strategy/CARMACK_FULL_SCOPE_AUDIT_20260825.md` — this checklist operationalizes the P0–P5 items into mechanical checks. Items flagged **(re-verify)** were audit findings whose remediation is unconfirmed.

---

## §0 HOW TO USE THIS

### Partition strategy (8 accounts)
**Dimension-major, not file-major.** Each account gets one coherent domain; outputs are comparable; no two accounts re-derive the same signal.

| Acct | Dimension(s) | Symbol |
|------|--------------|--------|
| 1 | Architecture & Design | `ARC` |
| 2 | Code Quality (M1/M23/M7/types/size) | `QUAL` |
| 3 | Security & Secrets (M8/M24/vault/auth) | `SEC` |
| 4 | Performance & Concurrency | `PERF` |
| 5 | Testing & M13 Temple-Grade | `TEST` |
| 6 | Docs, Heritage (M14), M26, M27 | `DOCS` |
| 7 | Sovereign Mandates deep-dive (27-row) | `MAND` |
| 8 | Debris/Tech Debt + API/CLI + Build/Release | `DEBR` |

### Output format (every check)
```
[DIM-NN] PASS|FAIL|SKIP  file:line  evidence  remediation_hint
```
- One line per check. No prose. Skip if not applicable with one-word reason.
- Append a final per-account summary: `ACCT X: P0=… P1=… P2=… SKIP=…  TOTAL=…`

### Priority semantics
- **P0**: blocks debut. Secret leak, crash, data loss, hard mandate violation, unverifiable claim about a built artifact.
- **P1**: ships-to-early-adopter, but a tracked issue accepted in writing by Architect.
- **P2**: nice-to-fix, post-debut.

### Common anti-patterns to REJECT as findings
- "This could be more Pythonic." (aesthetic)
- "Why not use library X?" (without measuring it's better on the 5700U floor)
- "I would have designed this differently." (not a defect)
- Any item not backed by a `file:line` or command output

---

## §1 ARC — Architecture & Design (Account 1)

| ID | Check | Pass criterion | Fail criterion | Evidence | Pri |
|----|-------|----------------|----------------|----------|-----|
| ARC-01 | `find src/omega/ -name "*.py" \| xargs grep -l "import asyncio"` (M1) | Zero hits | Any hit | file:line of offending import | P0 |
| ARC-02 | Confirm `python3 scripts/check_mandate_compliance.py` exits 0 (re-verify P0-3) | exit 0 | exit ≠ 0 | full stderr | P0 |
| ARC-03 | Confirm `make temple-grade` exits 0 (re-verify P0-1) | exit 0 | exit ≠ 0 | stderr from failing step | P0 |
| ARC-04 | Engine-Stack Firewall: `python3 scripts/check_mandate_compliance.py --json` reports 0 stack-logic violations in `src/omega/` | violations=0 | violations>0 | file:line per violation | P0 |
| ARC-05 | No circular imports: `python3 -c "import omega; import omega.llm; import omega.router; import omega.vault; import omega.oracle"` (or run the public entry points) | import succeeds | ImportError | full traceback | P0 |
| ARC-06 | Layering: `src/omega/` (Core) MUST NOT import from `config/wads/` (Stack) | zero hits | any hit | `grep -rn "from config.wads" src/omega/ or grep -rn "import config.wads" src/omega/` | P0 |
| ARC-07 | Reverse: Stack files may import from Core (expected). Confirm: no `wads/*.py` reaches back into other stacks | zero hits | any hit | file:line | P1 |
| ARC-08 | Interface contracts: any function with `-> Any` return type, or `dict`/`object` untyped, in public API surface | zero hits in `src/omega/` public modules | any hit | file:line | P1 |
| ARC-09 | Module size: any `.py` file >800 lines in `src/omega/` | ≤800 | >800 | `wc -l` output | P1 |
| ARC-10 | "God modules": any module exporting >25 public symbols | ≤25 | >25 | `grep -E '^(def\|class\|async def) [a-z_]' file.py \| wc -l` per file | P2 |

---

## §2 QUAL — Code Quality (Account 2)

| ID | Check | Pass criterion | Fail criterion | Evidence | Pri |
|----|-------|----------------|----------------|----------|-----|
| QUAL-01 | M1 AnyIO: see ARC-01 (do not duplicate; reference result) | zero `import asyncio` in `src/omega/` | any | — | P0 |
| QUAL-02 | M23 Failure Integrity: `grep -rn "except Exception" src/omega/` with bare or `: pass` body | zero hits with silent swallow | any silent pass / `# noqa` only | file:line + 3 lines of context | P0 |
| QUAL-03 | M23: `grep -rn "return None" src/omega/ \| grep -E "(error\|fail)"` for error paths returning None silently | zero hits | any hit | file:line | P0 |
| QUAL-04 | M7 Local-First: `grep -n "strategy: local_first" config/providers.yaml` | line present, exactly | missing | file:line | P0 |
| QUAL-05 | M7: confirm ProviderSelector reads `config/providers.yaml` as SSOT (no second source of truth) | exactly one `open(config/providers.yaml)` | >1 | file:line per access | P1 |
| QUAL-06 | Type leaks: `grep -rn "from typing import.*Any" src/omega/` outside tests | zero hits in public API | any hit | file:line | P1 |
| QUAL-07 | Type leaks: `grep -rn ": Any\b" src/omega/` | zero hits in public API | any hit | file:line | P1 |
| QUAL-08 | Dead code: `vulture src/omega/ --min-confidence 80` (install if needed) or `pyflakes src/omega/` | zero high-confidence dead code | any | file:line | P2 |
| QUAL-09 | Stale TODO/FIXME/XXX: `grep -rEn "TODO\|FIXME\|XXX" src/omega/ \| wc -l`; spot-check top 20 oldest (by file mtime) | ≤30, each with ticket ref | any without ticket | full list | P2 |
| QUAL-10 | Function size: any `def` or `async def` with body >100 lines | none | any | file:line per offender | P2 |
| QUAL-11 | Naming: `grep -rEn "class [A-Z][a-z]+_[A-Z]" src/omega/` (PascalCase mandated for classes) | zero hits | any | file:line | P3 |

---

## §3 SEC — Security & Secrets (Account 3)

| ID | Check | Pass criterion | Fail criterion | Evidence | Pri |
|----|-------|----------------|----------------|----------|-----|
| SEC-01 | `gitleaks detect --no-banner --redact` (or `make secrets-scan` if exists) | zero hits | any | full report | P0 |
| SEC-02 | Confirm D-590 remediation: `grep -rn "hardcoded.*secret\|fallback.*key" src/omega/` | zero hits outside test fixtures | any production hit | file:line | P0 |
| SEC-03 | M24 Venv: `grep -rn "break-system-packages" --include="*.md" --include="*.sh" --include="Makefile" --include="*.py" .` | zero active uses (comments exempt; flag intent) | any active use | file:line | P0 |
| SEC-04 | M8 Zero Telemetry: `grep -rn "import segment\|import sentry\|import datadog\|import mixpanel\|import posthog" src/` | zero hits | any | file:line | P0 |
| SEC-05 | Vault integration: `grep -rn "vault\." src/omega/ \| grep -v "test_\|conftest"`; every read goes through vault abstraction, no direct `os.environ["*SECRET*"]` | zero direct secret env reads in prod code | any | file:line | P0 |
| SEC-06 | Hardcoded path safety: `grep -rEn "/home/[a-z]+/\|/Users/[A-Za-z]+/\|C:\\\\Users" src/ omega_*.py mcp_servers/` | zero hits | any | file:line | P0 |
| SEC-07 | Input validation at boundaries: every public API entry function (`def main\|def run\|def handle_\|def process_`) has input validation within first 10 lines | all validate | any unguarded | file:line | P1 |
| SEC-08 | Dependency CVE: `pip-audit -r requirements.txt -r requirements-dev.txt` (run if installed) | zero high/critical | any high/crit | report excerpt | P1 |
| SEC-09 | Auth/session: `grep -rn "session_id\|api_key\|bearer" src/omega/` for any plain-text logging | zero plain-text logged credentials | any | file:line | P0 |
| SEC-10 | `.gitignore` covers: `data/entities/*/knowledge/quarantine/`, `.env*`, `*.key`, `*.pem`, `data/handoff/active/` | all covered | any missing | diff against expected list | P1 |

---

## §4 PERF — Performance & Concurrency (Account 4)

| ID | Check | Pass criterion | Fail criterion | Evidence | Pri |
|----|-------|----------------|----------------|----------|-----|
| PERF-01 | Hot path: `python3 -c "import cProfile, pstats; ..."` over the router/oracle/vault entry point under a synthetic load (10 calls). Report top-5 cumulative time. | documented | undocumented | cProfile output | P1 |
| PERF-02 | `await` discipline: any `asyncio.sleep` in production path? | zero in `src/omega/router`, `oracle`, `vault` | any | file:line | P1 |
| PERF-03 | Concurrency: every shared-mutable-state read/write goes through `anyio.Lock` or `anyio.Semaphore` (M1-aligned) | all guarded | any unguarded | file:line | P0 |
| PERF-04 | Memory: any module-level mutable singleton >1MB | none | any | file:line + size | P1 |
| PERF-05 | I/O: `grep -rn "open(" src/omega/ \| grep -v "encoding="` (text mode without explicit encoding) | all explicit | any implicit | file:line | P2 |
| PERF-06 | Caching: ProviderSelector + model registry have an invalidation story? | explicit TTL or trigger | implicit/never | file:line | P1 |
| PERF-07 | 15W floor: any `multiprocessing.Pool` or `ProcessPoolExecutor` (CPU-heavy path on APU) | justified or absent | unjustified | file:line | P1 |
| PERF-08 | `MALLOC_ARENA_MAX` and `MALLOC_MMAP_THRESHOLD_` are set in startup (per prior audit finding) | set in `.env`, Makefile, or entry script | missing | file:line | P1 |
| PERF-09 | Hot path zero-allocation: top 5 hot functions allocate per call (list/dict comprehensions building transient structures) | measured allocations, report baseline | undocumented | call graph excerpt | P2 |
| PERF-10 | Iris / speculative decode budget: confirm sequential model loading discipline in any oracle startup | sequential, gated | parallel without admission control | file:line | P1 |

---

## §5 TEST — Testing & M13 Temple-Grade (Account 5)

| ID | Check | Pass criterion | Fail criterion | Evidence | Pri |
|----|-------|----------------|----------------|----------|-----|
| TEST-01 | `make temple-grade` exits 0 (re-verify; do not duplicate ARC-03) | exit 0 | exit ≠ 0 | — | P0 |
| TEST-02 | `python3 -m pytest tests/ -q` | all pass | any fail | tail of pytest output | P0 |
| TEST-03 | Coverage on `src/omega/`: `python3 -m coverage run -m pytest && python3 -m coverage report --include="src/omega/*"` | ≥80% lines | <80% | coverage report | P1 |
| TEST-04 | No quarantined tests: `find tests/ -name "*.py" \| xargs grep -l "@pytest.mark.skip\|@pytest.mark.xfail" \| wc -l` ≤ N (declare N based on count, require ticket ref per skip) | justified | unjustified | list | P1 |
| TEST-05 | Contract tests: `tests/test_contract_*.py` exist for every mandate tagged with a test contract | 1:1 | any missing | file inventory vs mandate list | P1 |
| TEST-06 | Integration tests: at least one happy-path E2E (CLI invocation → response) per public entry point | all covered | any missing | inventory | P1 |
| TEST-07 | Test data realism: any test using `MagicMock()` in production path coverage? | justified in comment | unjustified | file:line | P2 |
| TEST-08 | Flake rate: re-run `pytest tests/ -q --count 3` if `pytest-repeat` available, else run 3x manually | zero flakes in 3 runs | any flake | run log | P1 |
| TEST-09 | M21 Gate Integrity contract: `tests/test_contract_m21.py` exists and passes | passes | missing/fails | file + output | P1 |
| TEST-10 | M20 SomaticState round-trip: `tests/test_somatic_roundtrip.py` exists and passes (re-verify from audit) | passes | missing/fails | file + output | P1 |

---

## §6 DOCS — Docs, Heritage, M26, M27 (Account 6)

| ID | Check | Pass criterion | Fail criterion | Evidence | Pri |
|----|-------|----------------|----------------|----------|-----|
| DOCS-01 | M26: `make doc-llm-validate` exits 0 | exit 0 | exit ≠ 0 | full output | P0 |
| DOCS-02 | Decision log: `docs/decisions/PIVOT_LOG.md` contains D-526..D-593 each with all 8 required fields (date/title/decision/rationale/scope/supersedes/approved-by/verdict-tier) | all present, all complete | any missing field | per-D check | P0 |
| DOCS-03 | PIVOT_LOG numbers cited in code match disk: spot-check 5 random D-numbers referenced in src/ | 5/5 match | any mismatch | diff per spot | P1 |
| DOCS-04 | M14 Heritage: `scripts/heritage_audit.py` exits 0; every `[id-soft:]` tag in repo has a vet record ≥7/10 | all vetted | any unvetted | full report | P0 |
| DOCS-05 | M27: `python3 scripts/validate_tracking_state.py` exits 0 (re-verify P0-4) | exit 0 | exit ≠ 0 | stderr | P0 |
| DOCS-06 | `data/coordination/ACTIVE_SPRINT.json` parses, has `next_free_id`, `gaps`, `rules` | parses, complete | any missing | jq output | P0 |
| DOCS-07 | `data/coordination/GAP_REGISTRY.json` parses, gaps have owner + due | parses, complete | any missing | jq output | P0 |
| DOCS-08 | Spec/code alignment: every spec in `docs/specs/` references a file in `src/` that still exists | all referenced code present | any dead reference | per-spec check | P1 |
| DOCS-09 | Entity docs: every entity under `data/entities/*/soul.yaml` has matching `data/entities/*/proposed_lessons.yaml` with non-empty `lessons` (M11 re-verify) | 51/51 entities | <51 | inventory | P1 |
| DOCS-10 | Stale docs: any `docs/**/*.md` referencing files removed in the 4,561-file diff (use `git log --diff-filter=D` or `git show release/debut^ --stat \| grep docs/`) | zero | any | per-doc check | P2 |

---

## §7 MAND — Sovereign Mandates Deep-Dive (Account 7)

Re-classify every mandate against the current branch. Update the table from
`docs/strategy/CARMACK_FULL_SCOPE_AUDIT_20260825.md` §1 (28-row table from verity's audit).

| ID | Check | Pass criterion | Fail criterion | Evidence | Pri |
|----|-------|----------------|----------------|----------|-----|
| MAND-01 | Re-run compliance meter: `python3 scripts/check_mandate_compliance.py --json` | 27/27 = 100% | <27 | full JSON | P0 |
| MAND-02 | All P0 items from prior audit (ARC-01, ARC-03, ARC-04, M8 regex, pre-commit install, python3 fix, validate_tracking_state) are PASS | all 6 PASS | any FAIL | per-item evidence | P0 |
| MAND-03 | Pre-commit framework installed: `ls .git/hooks/pre-commit` and verify it invokes the framework, not custom bash | framework present | custom bash only | file dump | P0 |
| MAND-04 | Dyadic equilibrium: compliance_history.jsonl exists and has ≥1 entry from a recent run (re-verify P1-7/8) | exists + populated | missing or empty | ls + head | P1 |
| MAND-05 | Feather Gate as code (re-verify P2-9): a `scripts/feather_gate.py` or equivalent exists, is wired into dispatch path | exists + wired | missing | file:line | P1 |
| MAND-06 | M11: count entities with non-empty `proposed_lessons.yaml` (re-verify) | 51/51 | <51 | `find data/entities -name proposed_lessons.yaml -size +500c \| wc -l` | P1 |
| MAND-07 | M22: `grep -n "provider_name" src/omega/oracle/model_gateway.py` exists, is consumed by ≥3 callers | ≥3 consumers | <3 | grep results | P0 |
| MAND-08 | M25: `tests/test_streaming_timeout.py` exists + passes; `config/providers.yaml` has `chunk_timeout_ms: 45000` | both present | either missing | file + value | P1 |
| MAND-09 | D-series currency: any D-number referenced in code is in PIVOT_LOG | 100% match | any D-N not in log | grep | P1 |
| MAND-10 | Any mandate text changes since v3.8.0 require a version bump in the file header? | bumped if changed | not bumped | git diff on `SOVEREIGN_MANDATES.md` | P1 |

---

## §8 DEBR — Debris, API/CLI, Build/Release (Account 8)

### Debris / tech debt
| ID | Check | Pass criterion | Fail criterion | Evidence | Pri |
|----|-------|----------------|----------------|----------|-----|
| DEBR-01 | No untracked junk in repo root: `git status --short \| grep "^??" \| grep -vE "\.lock$" \| head` | only intentional | orphans | file list | P1 |
| DEBR-02 | No `.pyc` / `__pycache__` committed: `git ls-files \| grep -E "\.pyc$\|__pycache__"` | zero | any | file list | P0 |
| DEBR-03 | `.gitignore` covers all build/cache artifacts (`__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `node_modules`, `dist`, `build`) | all covered | any missing | diff | P0 |
| DEBR-04 | Stale PDF/binary orphans at repo root (re-verify P0-5: the 350-percentage PDF) | moved or .gitignore'd | present | ls | P1 |
| DEBR-05 | Vestigial paths: `grep -rn "src/omega_youtube_research\|src/omega_stack" src/omega/` (the old monolithic apps) | only documented re-exports | any internal import | file:line | P2 |
| DEBR-06 | Half-executed campaigns: search for `TODO: PHASE 2`, `WIP`, `partial` comments in src | ≤10, all with ticket ref | unjustified | list | P2 |
| DEBR-07 | Orphaned branches: `git branch --merged release/debut` to find features-to-delete | documented | undoc'd | branch list | P3 |

### API & CLI
| ID | Check | Pass criterion | Fail criterion | Evidence | Pri |
|----|-------|----------------|----------------|----------|-----|
| DEBR-08 | `omega --help` exits 0; every subcommand has a one-line description | all documented | any missing | output | P0 |
| DEBR-09 | CLI flag consistency: `--json` works on every list/show command | all | any | per-command check | P2 |
| DEBR-10 | Error messages: every CLI error path includes a remediation hint (`try: omega X --help`) | all | any | spot-check 10 errors | P2 |
| DEBR-11 | Public API stability: any `__all__` in `src/omega/__init__.py`? If so, list it; verify nothing in `__all__` is deprecated | consistent | contradictions | diff | P1 |

### Build & Release
| ID | Check | Pass criterion | Fail criterion | Evidence | Pri |
|----|-------|----------------|----------------|----------|-----|
| DEBR-12 | `make help` lists all public targets; every target has a one-line `#` comment | complete | any undocumented | `make -p` summary | P1 |
| DEBR-13 | CI workflows: `.github/workflows/*.yml` reference `make temple-grade` and `make secrets-scan` | both | either missing | file:line | P0 |
| DEBR-14 | `requirements.txt` + `requirements-dev.txt` parse, versions pinned (== or ~=) | pinned | unpinned | cat + audit | P0 |
| DEBR-15 | `pyproject.toml` (or setup.py) version matches `__version__` in `src/omega/__init__.py` | match | mismatch | diff | P0 |
| DEBR-16 | `make clean` actually removes all build artifacts (verify against `git clean -ndX`) | all | misses | dry-run diff | P2 |
| DEBR-17 | `.github/dependabot.yml` or equivalent (Renovate) configured | configured | missing | file | P2 |

---

## §9 KNOWN-ANCHOR RE-VERIFICATION (any account, whichever finishes first)

These were P0 items from `CARMACK_FULL_SCOPE_AUDIT_20260825.md`. **All must be PASS
before debut**, not merely TRACKED. Distribute across accounts by ID:

| Anchor | Was | Now | Evidence | Pri |
|--------|-----|-----|----------|-----|
| P0-1 M8 regex FP on ics.py:197 | RED | PASS | ARC-03 (temple-grade green) | P0 |
| P0-2 pre-commit install | NOT INSTALLED | INSTALLED | MAND-03 | P0 |
| P0-3 compliance meter python→python3 | BROKEN | FIXED | ARC-02 | P0 |
| P0-4 validate_tracking_state | exits 1 | exits 0 | MAND-03 / DOCS-05 | P0 |
| P0-5 stray 350-percentage PDF in repo root | present | relocated | DEBR-04 | P1 |
| P1-7 compliance_history.jsonl | absent | present + populated | MAND-04 | P1 |
| P1-8 verify_mandate_claims structured output | warn-only | structured | MAND-04 | P1 |
| P2-9 P12 Feather Gate as code | prose | code | MAND-05 | P1 |

---

## §10 SCORING RUBRIC (applies to all 8 accounts)

```
PASS  = check met, evidence in hand
FAIL  = check not met, file:line + remediation hint recorded
SKIP  = check N/A in this branch, one-word reason given

Per-account summary:  P0_FAIL = 0 → green
                      P0_FAIL ≥ 1 → RED, blocks debut
                      P1_FAIL ≤ 5  → yellow, Architect sign-off required
                      P2_FAIL any  → log, post-debut cleanup

Cross-account rollup: P0_FAIL_total = 0 → debut go
                      P0_FAIL_total ≥ 1 (any account) → debut hold, remediation cycle
```

### Final report format (one file per account, plus a rollup)

Each account writes to `data/coordination/REVIEW_{SYMBOL}_20260828.md`. The orchestrator
(kali) writes the rollup to `data/coordination/REVIEW_ROLLUP_20260828.md` containing:
- 8-row table: account × P0/P1/P2 fail counts
- Cross-cutting findings (items that fail in 3+ accounts = systemic)
- Top 5 P0 remediations ordered by cost-to-fix
- Debut GO/HOLD verdict + required conditions for GO

---

## §11 WHAT THIS CHECKLIST WILL NOT CATCH (be honest)

- **Architectural drift** (e.g., did MaKaLi cutover actually happen as designed?) — needs
  orchestrator-level meta-review, not file forensics.
- **User experience** — flag obvious errors in CLI messages (DEBR-10) but actual UX
  requires running the binary.
- **Model behavior** — covered by E-FRONTIER, not this checklist.
- **Long-running load behavior** — needs actual soak testing, out of scope for 30min.
- **Realism of synthetic test data** — TEST-07 is a heuristic; will miss well-faked mocks.

If any of these is debut-critical, flag in the rollup as "out-of-scope, requires follow-up."

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ x-preview-f-free ⬡ opencode ⬡ trc_audit ⬡ CHECKLIST-ISSUED*
*Items: 76 (ARC 10, QUAL 11, SEC 10, PERF 10, TEST 10, DOCS 10, MAND 10, DEBR 15) · plus 8 re-verification anchors*
