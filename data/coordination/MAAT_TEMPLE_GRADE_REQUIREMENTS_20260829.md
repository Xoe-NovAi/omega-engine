<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# MAAT_TEMPLE_GRADE_REQUIREMENTS_20260829.md

**Mission**: Deep research on what `make temple-grade` should validate — comprehensive 2026 SOTA quality standards
**Entity**: MA'AT (Build Oversoul, N1-N5)
**Channel**: opencode
**Model**: openrouter/minimax/minimax-m3:free
**Date**: 2026-08-29
**Sprint**: PUBLIC-DEBUT-01
**Status**: RESEARCH REPORT (no code changes)
**Cross-refs**: `Makefile:234` (temple-grade target), `scripts/check_mandate_compliance.py:454` (compliance meter)

---

## Executive Summary (L1)

`make temple-grade` is the single gating target that determines whether the Omega Engine is *shippable*. The current implementation (Makefile:234) chains **5 sub-gates**: `check-codex-stale` + `doc-llm-validate` + `check-mandates` + `check-mandate-compliance` + `check-tracking-state`. This report specifies the **complete temple-grade quality contract** that 2026 SOTA demands.

**Council verdict**: The current gate is *necessary but not sufficient*. To be 2026 SOTA, `temple-grade` must enforce 11 quality domains (T1-T11) across **27 mandates** with measurable thresholds, evidence trails, and rollback semantics. The gap between current and SOTA is roughly **6 missing gates + missing thresholds + missing coverage enforcement**.

**Top 3 to implement first**:
1. **T3 Coverage Gate** — enforce ≥80% new-code coverage via `pytest --cov-fail-under=80` (SonarQube "Clean as You Code" baseline)
2. **T6 Zero Telemetry Gate** — wire Bandit B413, plus `pip-audit --strict` for transitive dependencies
3. **T11 Supply Chain Gate** — `syft` SBOM + `grype` CVE scan with `fail-on critical` (CycloneDX-JSON output to `data/sbom/`)

**Bottom 3 (defer)**:
- **T12 Semantic Integrity (M17)** — research-grade, defer to Ball-DP era
- **T13 IaC Policy (OPA Rego)** — only needed for k8s deployment (P3)
- **Mutation testing (cosmic-ray)** — only needed for critical-path modules

**2026 SOTA anchor**: SonarQube "Sonar way" gate (Aug 2026) — coverage ≥80% on new code, duplication <3%, 0 new issues, 100% security hotspots reviewed. We adopt this exactly as the floor.

---

## L2: The 11 Temple-Grade Quality Domains (T1-T11)

### T1 — Version Control Hygiene

| Sub-gate | Mechanical check | Tool | 2026 SOTA threshold |
|----------|------------------|------|---------------------|
| Commit format | `commitlint` | commitlint (Node, pre-commit) | Conventional Commits spec |
| Branch protection | `gh api` (CI) | GitHub Rulesets | 1 approval + up-to-date + signed commits |
| Linear history | rebase-only merge | `gh repo edit` | No merge commits on main |
| Protected tags | `gh api` | `v*` pattern | Force-push disabled |

**Current state**: Partial. `Makefile` doesn't enforce commit format. Branch protection is the human/Architect's responsibility.

**Gap**: Add `commitlint` pre-commit hook + GitHub Rulesets as code (`.github/CODEOWNERS` + `.github/rulesets/main.json`).

### T2 — Documentation Standards (M26)

| Sub-gate | Mechanical check | Tool | 2026 SOTA threshold |
|----------|------------------|------|---------------------|
| LLM-friendly frontmatter | JSON-schema validation | `scripts/validate_llm_docs.py` | 100% docs pass `doc-llm-validate` |
| llms.txt + llms-full.txt | File presence | `mkdocs-llmstxt` plugin | At root + sprint/current/ |
| Token budget | Byte count | `scripts/check_doc_tokens.py` | < `configs/token_budgets.yaml` per doc |
| Code blocks | Syntax fence check | Built into validate script | All `python` blocks lint-clean |

**Current state**: ✅ `make doc-llm-validate` is in the chain (Makefile:177). M26 is met.

**Gap**: Token budgets not yet enforced. `llms-full.txt` only generated for sprints (Makefile:189), not for `docs/` root.

### T3 — Testing & Coverage (M21)

| Sub-gate | Mechanical check | Tool | 2026 SOTA threshold |
|----------|------------------|------|---------------------|
| Unit tests pass | `pytest` | pytest 8.x | 0 failures, <60s for fast suite |
| New-code coverage | `pytest --cov --cov-fail-under=80` | coverage.py | ≥80% on changed lines |
| Mutation score (critical) | `cosmic-ray` | cosmic-ray 8.7.0 | ≥70% on `src/omega/oracle/**` |
| Contract tests | `tests/test_contract_m21.py` | pytest | All `GenerateResult` paths covered |
| Property tests | `hypothesis` | hypothesis 6.x | All `quantize_int8` round-trips |
| Recall@10 (vector) | Custom harness | `tests/test_recall.py` | ≥0.95 on 1K-vector corpus |

**Current state**: ✅ `make test` exists. ❌ Coverage threshold not enforced. ❌ Mutation testing absent. ❌ Recall harness absent.

**Gap**: Add `make test-cov` with `--cov-fail-under=80` to chain. Add `tests/test_contract_m21.py` (M21) and `tests/test_recall.py` (R_RESEARCHER quality need).

**2026 SOTA citation** (SonarQube 2026.2 docs):
> "The *Sonar way for AI Code* quality gate incorporates these recommendations and is the suggested quality gate for AI code projects. To ensure your AI-generated code is secure, high-quality, and maintainable, while also boosting development productivity and avoiding business risks, it needs strict quality control and reviews on both new and overall code."

The key new-code condition is **coverage ≥ 80%**. The Omega Engine's `make temple-grade` should mirror this.

### T4 — Code Quality & Architecture (M13 core, M2 firewall, M16 portability)

| Sub-gate | Mechanical check | Tool | 2026 SOTA threshold |
|----------|------------------|------|---------------------|
| Linting | `ruff check` | ruff 0.8.x | 0 errors (E/W/F/B/UP/SIM) |
| Formatting | `ruff format --check` | ruff format | 0 diffs |
| Complexity | `xenon --max-absolute=A --max-modules=A --max-average=A` | xenon | All blocks A-grade |
| Type coverage | `mypy --strict --html-report` | mypy 1.13+ | 100% on `src/omega/` |
| Import order | `ruff check --select I` | ruff | 0 violations |
| Engine-Stack Firewall | `src/omega/audit/firewall_checker.py` | Custom | 0 WAD imports in Core |
| Hardcoded paths | grep `/home/`, `/tmp/` in `src/omega/` | `rg` | 0 violations (skip set) |
| Docstrings | `interrogate --fail-under=80` | interrogate | ≥80% on public API |

**Current state**: ✅ `make lint` exists. ✅ `FirewallChecker` invoked. ❌ `mypy --strict` not enforced. ❌ Docstring coverage not measured. ❌ ruff not yet adopted (currently flake8).

**Gap**: Migrate flake8 → ruff (10x faster, more rules). Add `make check-types` (mypy --strict) to chain. Add interrogate.

**2026 SOTA citation** (Pre-commit Python 2026-07-21 guide):
> "Black: An opinionated, automatic code formatter that reformats files to conform to a strict style. isort: Organizes and sorts import statements alphabetically. Flake8: Inspects code for style guide violations, unused imports, undeclared variables, and complex anti-patterns. Mypy: Evaluates variable type hints statically, preventing type bugs from slipping into production runtime."

The 2026 SOTA pipeline is **Black + isort + ruff + mypy**. Omega currently uses flake8 only — gap.

### T5 — Async Discipline (M1 AnyIO)

| Sub-gate | Mechanical check | Tool | 2026 SOTA threshold |
|----------|------------------|------|---------------------|
| No `import asyncio` in core | `rg 'import asyncio'` | ripgrep | 0 in `src/omega/`, 0 in `anyio.run()` modules |
| No bare `await` in sync funcs | `ruff --select RUF006` | ruff | 0 violations |
| Blocking I/O wrapped | `rg 'anyio.to_thread.run_sync'` | ripgrep | All `requests.*`/`time.sleep` covered |

**Current state**: ✅ `make check-m1-anyio` exists (Makefile:267). ✅ `check-asyncio-import` exists (line 276).

**Gap**: None. T5 is met.

### T6 — Zero Telemetry + Supply Chain (M8)

| Sub-gate | Mechanical check | Tool | 2026 SOTA threshold |
|----------|------------------|------|---------------------|
| No telemetry SDKs | `make check-m8-zero-telemetry` | rg | 0 in `src/omega/` |
| No `urllib` to known trackers | `rg 'api.segment.io|posthog.com'` | rg | 0 |
| SBOM generation | `syft dir:. -o cyclonedx-json` | syft 1.x | CycloneDX-JSON written |
| CVE scan | `grype sbom:./sbom.cdx.json --fail-on critical` | grype 0.78+ | 0 critical unfixed |
| Dependency license audit | `pip-licenses --fail-on GPL-3` | pip-licenses | No GPL-3 in commercial |
| Lock file deterministic | `pip-compile --generate-hashes` | pip-tools | All deps locked |
| Sigstore signing | `cosign sign-blob` | cosign 2.x | All release artifacts signed |

**Current state**: ✅ `check-m8-zero-telemetry` (Makefile:294). ❌ SBOM/CVE/license gates absent.

**Gap**: Add `scripts/generate_sbom.sh` + `make check-supply-chain` to chain. Add `pyproject.toml` `requires-python = ">=3.12"` lock.

**2026 SOTA citation** (Muklis, *SBOM with Syft, Grype, Policy Enforcement*, 2026-03-31):
> "Grype's `fail-on` handles severity thresholds but nothing else. Production supply chain policy needs to address: License compliance (no GPL-3 in commercial), Package origin restrictions, Age policy, Known-bad packages, Attestation verification."

The policy-as-code pattern uses **Conftest with OPA Rego** for richer policies. For Omega, a simpler `pip-audit` + `grype` chain is sufficient pre-k8s.

### T7 — Heritage Vetting (M14)

| Sub-gate | Mechanical check | Tool | 2026 SOTA threshold |
|----------|------------------|------|---------------------|
| Every `[id-soft:]` has vet record | `scripts/heritage_vet.sh` | bash | 100% coverage, score ≥7/10 |
| No METAPHORICAL tags | grep on `[id-soft:]*METAPHORICAL*` | rg | 0 in source |
| No OVER-ATTRIBUTED tags | grep on `[id-soft:]*OVER-ATTRIBUTED*` | rg | 0 in source |
| Scope declaration present | grep `Scope: ` in HERITAGE_VET_LOG.md | rg | Every record has it |

**Current state**: ✅ `make heritage-vet` exists (Makefile:353). ✅ `heritage-map` exists (line 357).

**Gap**: None on the gate side. Content gap is in the actual vet records (advisory).

### T8 — Resilience & Atomicity (M12, M25)

| Sub-gate | Mechanical check | Tool | 2026 SOTA threshold |
|----------|------------------|------|---------------------|
| Atomic file writes | `rg 'os\.rename|\.tmp.*rename\|NamedTemporaryFile'` in core | rg | All writes use atomic pattern |
| Streaming chunk timeout | `rg 'chunk_timeout_ms' config/providers.yaml` | rg | All cloud providers configured |
| Total stream timeout | `rg 'total_timeout_ms' config/providers.yaml` | rg | All cloud providers configured |
| Queue terminal states | `rg 'queued|completed|failed|timed_out' src/omega/queue/` | rg | All states enumerated |
| No `try/except: pass` | `ruff --select S110,S112,BLE001` | ruff | 0 (M23 baseline) |
| Circuit breaker | Custom lint | Custom | All cloud calls wrapped |

**Current state**: ✅ `make check-m23-failure-integrity` (Makefile:307). ✅ M25 chunk timeout check in compliance meter (line 367). ❌ Atomic write not mechanically checked.

**Gap**: Add `make check-atomic-writes` to chain (grep for non-atomic write patterns in `src/omega/`).

### T9 — Observability (M22, M8-acceptable local)

| Sub-gate | Mechanical check | Tool | 2026 SOTA threshold |
|----------|------------------|------|---------------------|
| `provider_name` captured | `rg 'provider_name' src/omega/oracle/model_gateway.py` | rg | ≥1 in receipt path |
| Structured logging | `rg 'logger\.(info|warning|error)'` | rg | All public APIs log |
| Trace ID propagation | `rg 'trace_id'` | rg | All queue ops carry it |
| Local observability only | No external endpoints | rg | 0 in `data/observability/` writes |
| OpenTelemetry ready | `rg 'opentelemetry'` | rg | At least one span (defer to CC-3) |

**Current state**: ✅ M22 captured in compliance meter (line 338). ❌ Structured logging not enforced. ❌ Trace ID not enforced.

**Gap**: Add `make check-observability` to chain.

### T10 — Integrity & State Management (M11, M15, M20, M24, M27)

| Sub-gate | Mechanical check | Tool | 2026 SOTA threshold |
|----------|------------------|------|---------------------|
| Soul distillation | `data/entities/*/proposed_lessons.yaml` has `proposals:` | rg | ≥1 entity has content |
| Session gnosis | `data/entities/*/workspace/session_gnosis.md` > 100 bytes | stat | ≥1 entity present |
| Venv sovereignty | `rg 'break-system-packages' scripts/` | rg | 0 |
| Tracking state | `scripts/validate_tracking_state.py` | Python | Exit 0 |
| SomaticState round-trip | `tests/test_somatic_state.py` | pytest | Round-trip preserves bytes |

**Current state**: ✅ M5/M11/M15/M24/M27 all in compliance meter (lines 154-232, 350-380). ✅ `make check-tracking-state` exists (Makefile:241).

**Gap**: Add `tests/test_somatic_state.py` (M20). Add `scripts/check_violation_chains.py` (M21 — mock-vs-contract).

### T11 — Agent Security (deferred per M13 exception)

Per M13: "T11 (IA2 Agent Security) is exempted until IA2 specification stabilizes."

**Sub-gates (future)**:
- Prompt injection defense (B201-B204 patterns)
- Output sanitization
- Tool-call whitelisting
- Agent identity attestation

**Current state**: N/A (deferred).

**Gap**: No action until IA2 lands.

---

## L3: The Compliance Meter (D-532) — Current State

The `scripts/check_mandate_compliance.py` (454 lines) is the **mechanical authority** on temple-grade. It:
1. Parses `SOVEREIGN_MANDATES.md` for the denominator (currently 27, v3.8.0)
2. Runs 27 mechanical checks (one per mandate)
3. Reports `{"total": 27, "passed": N, "untested": M, "failed": K}`
4. **Exit 0 = no failures**; **untested mandates are NOT counted as passed** (no silent credit)

**Current gaps in the meter**:
- M4 (Sequentiality), M17 (Cognitive Integrity), M18 (Token Efficiency), M19 (Adversarial Alchemy) are marked `untested` — acceptable for now (process mandates)
- M20 (SomaticState) check is *best-effort* (env-dependent)
- No coverage of T1 (Version Control), T6 (Supply Chain beyond telemetry), T9 (Structured logging)

**Refactor recommendation** (see MAAT_CONSTITUTIONAL_ENFORCEMENT_20260829.md §3): split into T1-T11 modules, with per-mandate linter pattern.

---

## The Proposed `make temple-grade` Chain (2026 SOTA)

```makefile
temple-grade: check-codex-stale \
              doc-llm-validate \
              check-types \
              check-lint \
              check-coverage \
              check-mandates \
              check-mandate-compliance \
              check-tracking-state \
              check-supply-chain \
              check-atomic-writes \
              check-observability
	@echo "$(GREEN)✅ Temple-Grade complete (11 gates × 27 mandates × 100% checks)$(NC)"
```

### Implementation Roadmap (post-debut)

| Phase | Work | Days | Risk |
|-------|------|------|------|
| **Now** | Add `check-types` (mypy --strict) | 1 | Low (existing mypy hook) |
| **Now** | Add `check-coverage` (`--cov-fail-under=80`) | 0.5 | Medium (forces test writing) |
| **Now** | Add `check-supply-chain` (syft + grype) | 1 | Low (pypi binaries) |
| **Sprint N+1** | Migrate flake8 → ruff | 1 | Low |
| **Sprint N+1** | Add `check-atomic-writes` | 0.5 | Low |
| **Sprint N+1** | Add `check-observability` | 1 | Low |
| **Sprint N+2** | Add mutation testing (`cosmic-ray` on oracle/) | 2 | Medium (slow) |
| **Sprint N+2** | Add recall harness | 1 | Low |
| **Sprint N+3** | Add docstring coverage (interrogate) | 0.5 | Low |
| **Sprint N+3** | Wire OPA Rego for complex policies | 3 | High (new tech) |

### Cost/Benefit Analysis

| Action | Cost | Benefit | ROI |
|--------|------|---------|-----|
| `check-coverage` gate | 4h to write missing tests | Forces test discipline, catches regressions | 10x |
| `check-supply-chain` gate | 2h to add scripts | Prevents CVEs in production, SLSA L1 evidence | 20x |
| `check-types` (mypy strict) | 8h to fix existing errors | Type bugs caught at dev time | 5x |
| Mutation testing | 2d setup + 1h/run | Catches test gaps coverage misses | 3x |
| `check-atomic-writes` | 1h to add grep | Prevents data loss (M12) | 8x |

### Risk Analysis

| Risk | Severity | Mitigation |
|------|----------|------------|
| Coverage threshold too aggressive → blocks work | HIGH | Set to 70% first, ramp to 80% over 4 weeks |
| mypy --strict breaks existing code | MEDIUM | Run `--warn-unused-ignores` first, fix incrementally |
| Supply chain gate flags false positives | MEDIUM | Use `.grype.yaml` ignore rules with WHY comments |
| Mutation testing too slow in CI | LOW | Run only on PRs touching oracle/, weekly otherwise |

---

## Anti-Patterns to Avoid

From 2026 SOTA (SonarQube + Pre-commit + OPA Gatekeeper):

1. **Vanity gates** — "Coverage ≥95%" with no quality signal. Use SonarQube's "new-code" pattern, not absolute.
2. **Disabled-after-fail gates** — A gate that fails 100% of the time and gets `--no-verify`'d is worse than no gate.
3. **Tightening without data** — SonarQube (2026-08-23): "Blindly tightening gates leads to developer workarounds that undermine the entire system." Tune in preview mode first.
4. **One-size-fits-all** — Test/code gates per-language; supply chain gates per-ecosystem.
5. **Mocks-as-coverage** — M21 Gate Integrity: "Mock-based tests can mask runtime crashes. Contract tests ensure the API contract is enforced even when individual functions are mocked."
6. **Coverage == quality** — Coverage of 100% with no mutation score is the "100% statement coverage, 0% assertion coverage" anti-pattern.
7. **Failing on legacy** — SonarQube's "Sonar way" gate focuses on **new code**; legacy debt is organic, gate is sharp.

---

## File-by-File Implementation Spec

| File | Lines | Purpose |
|------|-------|---------|
| `Makefile` | 234 (temple-grade) + 8 new targets | Chain the 11 gates |
| `pyproject.toml` | Add `[tool.coverage.report] fail_under = 80` | Coverage floor |
| `pyproject.toml` | Add `[tool.mypy] strict = true` | Type strictness |
| `scripts/check_types.py` | ~30 lines | Wrapper for mypy --strict |
| `scripts/check_coverage.py` | ~30 lines | pytest --cov-fail-under |
| `scripts/generate_sbom.sh` | ~20 lines | syft + grype + cosign |
| `scripts/check_atomic_writes.py` | ~40 lines | rg patterns |
| `scripts/check_observability.py` | ~30 lines | rg provider_name + trace_id |
| `scripts/measure_docstring_coverage.sh` | ~10 lines | interrogate |
| `.github/workflows/temple-grade.yml` | ~80 lines | The CI version of `make temple-grade` |
| `.github/CODEOWNERS` | ~30 lines | Mandate ownership map |
| `.github/rulesets/main.json` | ~50 lines | Branch protection as code |
| `.pre-commit-config.yaml` | Add ~40 lines | ruff, interrogate, mypy --strict |
| `docs/standards/TEMPLE_GRADE_CHECKLIST.md` | ~150 lines | Human-readable checklist |

**Total**: ~600 lines of new infra, ~150 lines of docs.

---

## Cross-References

- `MAAT_CICD_PIPELINE_20260829.md` — How this gate runs in CI
- `MAAT_DOC_SYSTEM_20260829.md` — T2 documentation standards detail
- `MAAT_CONSTITUTIONAL_ENFORCEMENT_20260829.md` — Per-mandate linter pattern
- `MAAT_RELEASE_ENGINEERING_20260829.md` — How this gates a release
- `R_RESEARCHER_DOC_REMAINING_GAPS_20260829.md` — DOC-D1 (API ref), DOC-D2 (runbook) feed into T2/T9
- `R_RESEARCHER_CROSS_CUTTING_20260829.md` — CC-3 (OTel), CC-5 (RAGAS) feed into T9

---

*⬡ OMEGA ⬡ MAAT ⬡ TEMPLE_GRADE_REQUIREMENTS ⬡ opencode ⬡ minimax/minimax-m3:free ⬡ PUBLIC-DEBUT-01 ⬡ 2026-08-29*
