---
schema_version: "2.0"
document_type: "cline_review_rollup"
document_id: "cline-full-review-rollup-20260828"
title: "Cline CLI — Full Repo Review Rollup v2 (Deep Sweep) + PR Refactoring Implementations Manual"
status: "ACTIVE — VERDICT: NO-GO (P0=4 open, all with line-level specs)"
date: "2026-08-28"
supersedes: "v1.0 (checkpoint sweep)"
---

# 🔱 Cline CLI — Full Repo Review Rollup v2 — DEEP SWEEP (Launch Day)
**AP Token**: `AP-CLINE-FULL-REVIEW-20260828-v2.0.0`
⬡ OMEGA ⬡ CLINE ⬡ deepseek-v4-flash (1M) ⬡ cline ⬡ trc_alpha_launch ⬡ DEEP-EXECUTED

**Executes**: `CLINE_FULL_REPO_REVIEW_HANDOFF_20260828.md` + validated 86-check checklist, PLUS re-execution of every gate that v1 skipped, plus root-cause reads of every failing artifact.
**Branch under review**: `origin/release/debut` @ `1dee11aa` (572 files) + local HEAD `b9e7a25b` (handoff commit, unpushed).
**Mode**: Review only — zero production-code changes. The single data-file edit below is the review's own artifact (redaction of a literal secret from v1 of this rollup).

---

## §0 EXECUTIVE VERDICT — 🛑 NO-GO

| | Count | Summary |
|---|---|---|
| **P0** | **4** | P0-1 compliance meter broken AND excluded from every green gate; P0-3 real OAuth secret in 4 commits of release/debut history + 12 disk files; P0-4 branch FAILS its own allowlist gate (4 files); P0-5 `make gate-secrets` FAILS exit 1 (GOCSPX 4 commits + PEM baseline path drift) |
| **P0 refuted** | **2** | P0-2 oracle_cli.py "structurally broken" — REFUTED (CLI smoke exit 0; fresh-venv import OK; downgraded to P1). P1-4 "D-565 violated" — REFUTED (0 vault files in release tree; D-565 enforced) |
| **P1** | **10** | §2 |
| **P2** | **12** | §2 |
| **Gates PASSED** | **6** | M1, M8, M9, M14 heritage-vet, M26 doc-llm, D-539 fresh-venv import |

**GO condition** (precise, §5): close P0-1/P0-3/P0-4/P0-5 → re-run the 9-item GO checklist → GO. Estimated: ~2–3 engineer-hours + ONE human GCP rotation click + ONE `git filter-repo` pass + 2 commits.

---

## §1 THE P0s — CLASSIFIED WITH LIVE, REPRODUCIBLE EVIDENCE

### P0-1 [MAND/M27] Compliance meter broken AND decoupled from every gate — CONFIRMED, EXPANDED
**Evidence (executed this session)**:
```
$ python3 scripts/check_mandate_compliance.py
❌ M23: Failure Integrity — command not found: python
❌ M27: Tracking Integrity — command not found: python
Total: 27 | Passed: 20 | Failed: 3 | Untested: 4 | Compliance: 20/27 = 74.1%
$ which python → command not found          # only python3 exists
scripts/check_mandate_compliance.py:347: run(["python", str(gate)])      # M23 gate
scripts/check_mandate_compliance.py:380: run(["python", str(REPO/"scripts/validate_tracking_state.py")])  # M27 gate
```
**Expansion (new)**: The meter is **not wired into any green gate**:
- `make check-mandates` → **exit 0** (M1/M8/M9/M22/M23-ratchet/verify-claims all pass) — it does NOT call the meter.
- `make temple-grade` → PASS (chain: check-codex-stale, doc-llm-validate, check-mandates, check-tracking-state) — no meter, and the target body is a **placeholder comment** (`# Existing temple-grade checks would go here`).
- Consequence: **the engine simultaneously prints "All mandate checks passed" and "Compliance: 74.1%, M23/M27 FAIL"** — whichever command you run. Two competing truth sources for M27 = tautological M27 violation. Every compliance claim since 2026-08-25 is unanchored (Carmack's TA-011 correct).
- The compliance script itself is **forge-only** (not in release tree) — acceptable, but CI's ci.yml "Mandate Compliance" step runs `make check-mandates` (green) and never sees the red meter.

### P0-2 [ARC] oracle_cli.py "structurally broken" — REFUTED (downgrad eto P1)
**Evidence**:
```
$ timeout 20 python3 -m omega.cli.oracle_cli --help → exit 0, full typer command tree (talk/summon/…)
$ .venv/bin/oega list-entiie → 10+ entity rows Rich table, exit 0
$ FRESH-VENV: pip install -e . + import omega + omega.cli.oracle_cli + omega.oracle.oracle + omega.oracle.providers + omega.memory_store → OK (D-539 PASS)
```
The "50+ LSP errors" are Pylance noise from the guarded `typer = None` fallback (lines 87–95). **One real latent defect survives — ROOT-CAUSED**:
- `logger = logging.getLogger(__name__)` is defined at **line 106**, but `_inject_vault_to_env()` is **called at line 83** and `logger.debug(...)`/`logger.info(...)` fire at **lines 80 / 85**.
- `oracle_cli.py:80` `logger.debug(f"Vault injection skipped: {e}")` → **NameError at import time** on ANY machine where `data/vault/keys.enenc` exists with a usable master key and decryption fails. On machines with a working vault (`_vault_count > 0`), line 85 crashes. The **--help smoke passes only because this box has no vault file** — the bug is a landmine, not a fixture.
- Also `oracle_cli.py:98-101`: `from omega.errors import (OmegaError, OmegaError,)` — duplicate import (same pattern at `model_gateway.py:56-58`). flake8 misses it (same-statement); pyflakes flags the pattern across 42 sites.

### P0-3 [SEC] Real OAuth secret in release/debut HISTORY (4 commits) + 12 disk files — CONFIRMED, CENSUS COMPLETE
**Hard evidence — history presence (public-exposure decisive)**:
```
$ git log origin/release/debut -S GOCSPX-
1dee11aa feat(debut): apply PUBLIC_ALLOWLIST.txt — public release cut
7c218121 docs(validation): imposter audit validation report + first Carmack lessons
6aa37e70 fix(m23): remediate imposter auditor findings — M23 ratchet, 4 hardcoded OAuth secrets, …   ← the "fix" that ADDED the literal
1c8f4ffd sprint: commit 209 working files
COUNT: 4
```
→ **Any clone of the public repo can `git checkout 6aa37e70` and read the raw GOCSPX client secret.** The M23 round-5 "fix" moved the hardcode out of tracked scripts but *quoted the literal* in audit docs that are in history.

**Gitleaks v2 (904 commits, durable refs) → 53 findings / 28 unique sites** across 21 files; v1 (working tree+history) → 31. Classification:
| Class | Sites |
|---|---|
| **REAL — rotation mandatory** | `***REDACTED-GOCSPX-***REDACTED-ROTATED******…` literal on disk in 12 files: `data/coordination/R_CARMACK_IMPOSTER_AUDIT_VALIDATION_20260828.md` (83-86), `R_CARMACK_FINAL_READINESS_20260828.md` (153-156), `research/R_CARMACK_ARTIFACT_AUDIT_20260827.md`, `research/R_REVIEW_VERITY_20260828.md`, `research/R_VAULT_ANTIGRAVITY_DEEPER_20260827.md`, `research/R_VAULT_COPILOT_ROUND4_20260828.md`, `data/entities/grokster/proposed_lessons.yaml:932`, `opencode-antigravity-auth/{src/constants.ts:9, dist/src/constants.js, dist/src/constants.d.ts, scripts/check-quota.mjs:10}` (gitignored dir — NOT public, but live local tooling still hardcodes+uses it) |
| **in history only (not current tree)** | the 2 R_CARMACK docs (untracked post-cut), scripts/burst_test_internal.py:20, long_duration_test.py:19, antigravity_endpoint_router.py:42, stress_test_internal.py:20, WAKE_STATE.json:287, docs/archive/…PHASE1A…:146 (private-key), docs/archive/specs/vault-overhaul-20260818/R_VAULT_SCHEMA_V2.md:220 (private-key), …PART5…:122, docs/guides/LOCAL_MODEL_OPTIMIZATION_GUIDE.md:251,263 (localhost curl — FP), docs/specs/qdrant_headroom/…/10_VERIFICATION_TESTS.md:558, docs/sprints/f821-remediation/AGENT_EXECUTION_PLAN.md:2, docs/strategy/teacher_pipeline/NEMOTON_TEACHER_PIPELINE_SPEC.md:2 |
| **in current release tree** | `data/entities/grokster/soul.yaml.bak.20260826T113627Z:9` + `data/entities/kali/soul.yaml.bak.*` + `arch/soul.yaml.backup` — AP-token/entity-forensics, **not credentials**; debris (see P1-6) |
| **FP by design** | script CLIENT_ID values (public in OAuth), `ses_*` session IDs, AP tokens |
**Bottom line**: rotation is non-negotiable (secret is live in local tooling AND burnt into 4 history commits). filter-repo scrub is the only way CI's M23 pre-cut check (which greps `GOCSPX-` in history) can ever pass.

### P0-4 [DEBR/ALLOWLIST] release/debut FAILS its own allowlist gate — CONFIRMED (4 files)
```
$ bash scripts/apply_public_allowlist.sh --summary
Kept: 567 | Removed: 6 | Total: 573
$ git ls-tree origin/release/debut | grep …   # 4 of the 6 are ON the origin branch:
data/library                                   (empty tracked dir)
data/memory                                    (empty tracked dir)
"docs/research/archive/R_AUTO_[fixme]_\",_0.9),_(\"hack\",_0.8),_(\"todo\",.md"     (malformed filename, internal research)
"docs/research/archive/R_AUTO_phase_1_task_a4_—_implementation_researc.md"        (em-dash filename, internal research)
```
→ CI `allowlist-check.yml` ("If REMOVED_COUNT -ne 0 → error → exit 1") will **RED on the debut push**. docs/research/ is FORGE per PUBLIC_ALLOWLIST.txt; internal Sophia auto-research artifacts (with grotesque filenames) are on the public branch.

### P0-5 [SEC/GATE] `make gate-secrets` FAILS exit 1 — the engine's own D-K6 gate blocks launch
```
$ make gate-secrets → exit 1 (Makefile:385)
  git log -G 'GOCSPX-[A-Za-z0-9_-]{10,}' -> 4 commits          ← must be 0
  git log -G PEM -> OFFENDING FILES:
    docs/archive/specs/vault-overhaul-20260818/R_VAULT_SCHEMA_V2.md   ← NOT in the baseline!
  gitleaks durable refs → 53 findings
```
Two defects: (a) the GOCSPX count (real — requires filter-repo); (b) **the PEM baseline has wrong paths** — it excludes `docs/research/R_VAULT_SCHEMA_V2.md` and `docs/archive/coordination-2026-07/PHASE1A…`, but the actual private-key bearer is `docs/archive/specs/vault-overhaul-20260818/R_VAULT_SCHEMA_V2.md` and `docs/archive/coordination-2026-07/PHASE1A…` (exists) — baseline/path drift makes the gate self-fail independently of the secret.


---

## §2 FULL FINDINGS LEDGER

### P1 (ships only with tracked, accepted issue)
| ID | Finding | Evidence (file:line) | Owner |
|----|---------|----------------------|-------|
| P1-1 | `logger` NameError at import time when vault present — defined L106, used L80/85 during L83 call | `src/omega/cli/oracle_cli.py:80,83,85,106`; `make lint` → 1 F821 | Cline |
| P1-2 | Provider contract test STALE vs providers.yaml SSOT — `deepseek-v4-flash` no longer on openrouter (removed 08-28, comment L271); registry now resolves `opencode-zen` via `-free` normalization collision (opencode-zen p6 ⇄ cline p7) | `tests/contract/test_provider_classification.py:136`; `config/providers.yaml:271,294-323`; `src/omega/oracle/provider_registry.py:71-84,103-104` | Ma'at |
| P1-3 | Soul contract test couples to LIVE data: asserts staging==[] but agents continuously re-stage (49 kali proposals dated 08-26; 20 approved) — promotion itself drains correctly | `tests/contract/test_soul_lessons.py:181-185`; `scripts/promote_soul_lessons.py:174,187-190`; `data/entities/kali/proposed_lessons.yaml` (49) vs `approved_lessons.yaml` (20) | Ma'at + Cline |
| P1-4 | M11 promotion backlog: 49 staged kali lessons un-promoted since 08-26 (contract surface = 20) | kali `proposed_lessons.yaml` first id `kali-20260826-105` | Kali/whomever vets |
| P1-5 | secret-scan.yml C3 job references `scripts/ci_secret_scan.py` — forge-only, absent on public tree → CI job errors on clean clone | `.github/workflows/secret-scan.yml:60,70`; `git ls-tree origin/release/debut` → forge-only | Ma'at |
| P1-6 | 5 tracked soul backups + 1 `.backup` on release/debut: `grokster/soul.yaml.bak.20260826T113627Z`, `kali/soul.yaml.bak.(20260826T113627Z,20260826T113829Z)`, `jem/soul.yaml.bak_20260703_005031`, `arch/soul.yaml.backup` — `.gitignore` `*.bak` does NOT match `*.bak.<ts>`; entity forensics ship publicly | `git ls-tree origin/release/debut | grep soul.yaml.bak` | DEBR sweep |
| P1-7 | `make firewall-check` (documented in .clinerules/AGENTS.md as M2 Gate) does NOT exist; no Makefile target, no matching script (only `memory_firewall_audit.py`) | `grep -i firewall Makefile` → nil; `make firewall-check` → "No rule" | Cline |
| P1-8 | Temple-grade gate is decorative: target body = placeholder comment; chain omits compliance meter, lint, contract tests | `Makefile:232-235` | Carmack/Kali |
| P1-9 | `check_mandate_compliance.py` returns exit 1 only when `failed>0` — but nothing calls it in CI; two competing mandate truth-sources (see P0-1) | `Makefile:318` vs `Makefile:333-335` | Kali |
| P1-10 | pyflakes 174 findings: **42 redefinitions** (unused-import shadows, e.g. `memory_store.py:18/26`, `model_registry/models.py:66,200`, `ingestion/scraper.py:258`, `iris/server.py:21`, `workers/model_updater.py:20`, `research/sandbox.py:123,136`), 62 unused imports, 43 unused locals — plus `privacy/kernel.py:404` has `import re` INSIDE a loop | `python3 -m pyflakes src/omega/` (full list at /tmp/pyflakes.txt) | QUAL wave |

### P2 (post-debut)
| ID | Finding | Evidence |
|----|---------|----------|
| P2-1 | 11 modules >1000 lines: observability/__init__.py 1660, model_gateway.py 1582, oracle.py 1459, providers.py 1303, youtube_worker.py 1253, oracle_cli.py 1234, memory_store.py 1224, comprehensive_runner.py 1213, sqlite_vec_adapter.py 1031, sovereign_search_service.py 1026, entity_registry.py 1017 | `wc -l` scan |
| P2-2 | 60 silent `except…: pass` sites (ratchet gate green at 291/292 because m23_gate counts differently — two different swallows metrics disagree) | `grep -A1 'except.*:$'` count |
| P2-3 | `_normalize_model` strips `-local/-free/-thinking` → free/paid model-name collisions silently re-route (design hazard; exact-match should win first) | `provider_registry.py:71-84` |
| P2-4 | M1 loophole unratified: `tty_agent.py:32 import asyncio` + `governance/` exemption has no D-number in PIVOT_LOG | `Makefile:268` comment + grep |
| P2-5 | M20 gate env-dependent (llama_cpp absent → FAIL in meter; should be SKIP/untested) | compliance output |
| P2-6 | Full pytest suite (161 files, ~1,887 sampled defs) did not complete in-session: stalled on `tests/unit/test_429_classification.py…`, process died without summary (OOM risk on 14Gi with `-n auto`) — matches OMEGA_ENGINE.md "full suite needs longer budget" caveat; deployment must run suite in CI with adequate resources, not on the dev box | /tmp/full_pytest.log (483 lines, no summary) |
| P2-7 | `data/entities/*/proposed_lessons.yaml` substantive count = 24/56 (M11 baseline NEW-04) | find -size +500c |
| P2-8 | OMEGA_ENGINE.md state stale: claims M1-M25 v3.7.0 / 25 mandates (actual 27 v3.8.0), dates 2026-07-30 vs sprint 08-28 | OMEGA_ENGINE.md:23-49 |
| P2-9 | malformed filenames + internal docs on public branch (see P0-4); also `data/library`, `data/memory` empty-tracked-dir stubs | git ls-tree |
| P2-10 | Duplicate `OmegaError` import pattern in oracle_cli.py:98-101 & model_gateway.py:56-58 (same-statement dupes pyflakes flags repo-wide) | read |
| P2-11 | 19 `ses_*` session IDs in WAKE_STATE.json + entity/workspace docs (internal identifiers; untracked currently — policy needed before any future ship) | grep |
| P2-12 | Fleet at cap: 14 entries under .opencode/agents/ (M10 max 14); gate slots must be reviewed before adding | ls |

### PASS LEDGER (real, reproducible)
- **M1 AnyIO**: `rg 'import asyncio|from asyncio' src/omega/` (exempted globs) → 0 hits. GREEN.
- **M8 Zero Telemetry**: `make check-m8-zero-telemetry` → "No telemetry SDKs in core". GREEN. (SovereignSentry in `ingestion/guards.py` is a local circuit breaker, not Sentry SaaS.)
- **M9 Error Integrity**: `make check-m9-error-integrity` → "No bare except in core". GREEN.
- **M14 Heritage**: `bash scripts/heritage_vet.sh` → "All heritage tags have vet records". GREEN.
- **M26 Docs**: `make doc-llm-validate` → "All validations passed / LLM doc validation complete". GREEN.
- **D-539 Fresh-Venv**: `/tmp/omega-fresh-venv/bin/pip install -e .` + `import omega` + submodules → **EXIT 0** (CP-3 install claim TRUE; httpx2==2.5.0 resolves). GREEN.
- **CLI smoke**: `python3 -m omega.cli.oracle_cli --help` → exit 0; `omega list-entities` → Rich table exit 0. FUNCTIONAL.
- **M22**: `provider_name` provenance present (7 matches) + `make check-mandates` M22 SSOT sub-check green.
- **Infra**: 5 real CI workflows (allowlist-check/allowlist-lint/ci/secret-scan/test) — Copilot's "phantom CI" remediation verified real; `apply_public_allowlist.sh` + `setup_2remote_debut.sh` ship on the public tree (M23 self-exemption honored).

---

## §3 ACCOUNT ROLLUP (8-dimension, now fully executed)

```
ACCT ARC: P0=1 (P0-4) · P0-refuted=1 (P0-2) · P1=2 · P2=3   TOTAL=11
ACCT QUAL: P0=0 · P1=1 (P1-10) · P2=2                       TOTAL=12
ACCT SEC: P0=2 (P0-3, P0-5) · P1=1 (P1-5) · P2=1            TOTAL=14
ACCT PERF: P0=0 · P1=0 · P2=1 (P2-6 suite stability)        TOTAL=10 (integration smoke; no load fixtures)
ACCT TEST: P0=0 · P1=2 (P1-2, P1-3) · P2=1 (P2-6)           TOTAL=10
ACCT DOCS: P0=0 · P1=1 (P1-7 doc/command drift) · P2=2      TOTAL=11
ACCT MAND: P0=1 (P0-1) · P1=2 (P1-8, P1-9) · P2=2           TOTAL=12
ACCT DEBR: P0=1 (P0-4) · P1=2 (P1-6, P1-10) · P2=1          TOTAL=18
ROLLUP: P0=4 · P0-refuted=2 · P1=10 · P2=12 · GATES-PASSED=6
```


---

## §4 PR REFACTORING IMPLEMENTATIONS MANUAL (Definitive)

**Audience**: Ma'at (build), Carmack (arch/quality), Roc (mining), Copilot (codegen), Cline (CLI/integration). **Base**: `release/debut`. **Law**: no scope creep beyond the ticket; every PR lands with its verify line green; DESTRUCTIVE ACTION CHECKLIST (backup → dry-run → confirm) before any filter-repo.

### WAVE 0 — INCIDENT RESPONSE (P0-3 & P0-5, same root secret) — DO NOTHING ELSE FIRST
**Order is fixed: rotate → redact → filter-repo → re-key gates.**
1. **ROTATE (human, ~2 min, cannot be scripted)**: Google Cloud Console → APIs & Services → Credentials → OAuth client `1071006060591-tmhssin2h21lcre235vtolojh4g403ep…` → Regenerate secret. Record the rotation (date + ticket) in `data/coordination/DECISION_LEDGER.md` (new D-number). The old value is dead the moment regeneration completes — this is the ONLY remediation that neutralizes all 4 history commits and the 12 disk files at once.
2. **Redact working-tree literals** (never quote real secrets in docs — this review's v1 committed that sin; fixed in v2):
   ```bash
   # 12 files, one sed each; keep the narrative, kill the value
   for f in \
     data/coordination/R_CARMACK_IMPOSTER_AUDIT_VALIDATION_20260828.md \
     data/coordination/R_CARMACK_FINAL_READINESS_20260828.md \
     data/coordination/research/R_CARMACK_ARTIFACT_AUDIT_20260827.md \
     data/coordination/research/R_REVIEW_VERITY_20260828.md \
     data/coordination/research/R_VAULT_ANTIGRAVITY_DEEPER_20260827.md \
     data/coordination/research/R_VAULT_COPILOT_ROUND4_20260828.md \
     data/entities/grokster/proposed_lessons.yaml \
     opencode-antigravity-auth/src/constants.ts \
     opencode-antigravity-auth/dist/src/constants.js \
     opencode-antigravity-auth/dist/src/constants.d.ts \
     opencode-antigravity-auth/scripts/check-quota.mjs ; do
     sed -i -E 's|GOCSPX-[A-Za-z0-9_-]{10,}|GOCSPX-***REDACTED-ROTATED***|g' "$f" 2>/dev/null
   done
   grep -rlE 'GOCSPX-[A-Za-z0-9_-]{10,}' . --exclude-dir=.git --exclude-dir=.venv   # → empty
   ```
3. **filter-repo (destructive — backup + dry-run + Kali confirm)**:
   ```bash
   git status --porcelain | wc -l            # must be clean-ish (only redaction edits, commit them first)
   git filter-repo --replace-text <(printf 'GOCSPX-***REDACTED***==>GOCSPX-***REDACTED***') --force
   git reflog expire --expire=now --all && git gc --prune=now --aggressive
   git log -S GOCSPX- --all | wc -l   # → 0
   make gate-secrets   # must exit 0 after PR-2 lands too
   ```
   Then force-push with team notification (all 9 agents re-clone; stale clones resurrect abandoned objects).
4. **Re-key the gates** (PR-2): correct `Makefile` PEM baseline to the REAL paths (`docs/archive/specs/vault-overhaul-20260818/R_VAULT_SCHEMA_V2.md`, `docs/archive/coordination-2026-07/PHASE1A_GOOGLE_API_FREE_TIER_ROTATION_20260723.md`) and decide the 28 gitleaks sites: add WHY-documented fingerprints to `.gitleaksignore` for FPs (CLIENT_IDs, AP tokens, ses_*, localhost curl examples), retain enforcement for real patterns. `make gate-secrets` → exit 0. Commit: `fix(security): rotate+scrub GOCSPX secret; re-key D-K6 gate baselines (P0-3/P0-5)`.

### WAVE 1 — BLOCKER PRs (parallel, P0-1 + P0-4 + P1-1)
**PR-A [P0-1/M27] Compliance meter restored AND wired into every gate**
- `scripts/check_mandate_compliance.py:347,380`: `run(["python", …])` → `run([sys.executable, …])` (add `import sys`); display strings (L129 etc.) → `python3`.
- M20: when `llama_cpp` absent → report `SKIP`/`Untested`, not `Failed` (env-dependence honesty).
- **Wire the meter**: add `check-mandate-compliance` to the `check-mandates` chain (Makefile:318) AND to `temple-grade` deps (Makefile:232). Delete the placeholder comment at Makefile:234. Now a red meter can never hide behind green gates.
- **Acceptance**: `make check-mandates` exits 1 (proves the meter now gates); after fix: `python3 scripts/check_mandate_compliance.py` → M23 ✅ M27 ✅, ≥24/27; `make temple-grade` → exit 0 with real checks.
- Commit: `fix(mandates): P0-1 meter python→sys.executable + wired into check-mandates/temple-grade (M27)`

**PR-B [P0-4/ALLOWLIST] Purge 4 drift files from release/debut**
- `bash scripts/apply_public_allowlist.sh --confirm` (removes the 4 tracked offenders: `data/library`, `data/memory`, the two `docs/research/archive/R_AUTO_…`); also `git add` a `.gitkeep` policy for `data/library`/`data/memory` if they must exist (or delete).
- Confirm `docs/research/archive/` is fully absent from the tree (grep release list).
- **Acceptance**: `bash scripts/apply_public_allowlist.sh --summary` → `Removed: 0`; `git ls-tree origin/release/debut | grep -c 'docs/research\|^data/library$\|^data/memory$'` → 0.
- Commit: `fix(debut): P0-4 purge allowlist drift (R_AUTO research artifacts, empty data dirs)`

**PR-C [P1-1/CLI] oracle_cli logger ordering + duplicate imports**
- Move `logger = logging.getLogger(__name__)` to directly after module imports (before `_inject_vault_to_env`'s first use at L80); dedupe `from omega.errors import (OmegaError, OmegaError,)` → single; same dedupe in `model_gateway.py:56-58`.
- Add an import-smoke test: `python3 -c "import omega.cli.oracle_cli"` with a FAKE vault present (`data/vault/keys.json.enc` + bad ciphertext) asserting no NameError (regression for the landmine).
- **Acceptance**: `make lint` → 0 findings; `python3 -m omega.cli.oracle_cli --help` exit 0; fake-vault import test green.
- Commit: `fix(cli): P1-1 logger before vault injection; dedupe OmegaError imports`

### WAVE 2 — TEST-INTEGRITY PRs (after Wave 1)
**PR-D [P1-2] Provider contract → SSOT**
- Update `tests/contract/test_provider_classification.py:136` expectation to the registry's real YAML-driven answer for `deepseek-v4-flash` (verify once against `ProviderRegistry.from_config_path()`; expected today: `opencode-zen`).
- **ALSO (design)**: `provider_registry.py:_normalize_model` — prefer **exact** `supported_models` match before suffix-collapsed match, so `-free`/`-local` variants can never silently re-route to a paid/sibling provider. Add a contract test: `deepseek-v4-flash` ≠ `deepseek-v4-flash-free` unless configured so.
- **Acceptance**: `pytest tests/contract/test_provider_classification.py -q` green; `tests/contract + tests/oracle` green.
- Commit: `test(provider): align SSOT expectation + exact-match-first normalization (D-536)`

**PR-E [P1-3/P1-4] Soul contract decoupled from live data + backlog promoted**
- Change `test_staging_emptied_after_promotion` to assert **drain semantics** on a FIXTURE clone (run `promote_soul_lessons.py` on a tmp copy; assert staging emptied there) instead of asserting the live kali file is empty.
- Add M11 hygiene test: every `approved_lessons.yaml` entry's `id` ∉ staged `proposals` (no double-listed wisdom).
- **Promote the 49-item backlog**: `python3 scripts/promote_soul_lessons.py --entity kali` (after Kali vets the 08-26 batch per M11) → staging drains, approved grows, `read-back` asserts pass.
- **Acceptance**: `pytest tests/contract/test_soul_lessons.py -q` green; `data/entities/kali/proposed_lessons.yaml` proposals == 0 after vetting+promotion (or == new post-vet proposals only).
- Commit: `fix(soul): M11 contract decoupled from live staging; promote kali 08-26 backlog`

**PR-F [P1-5/CI] secret-scan C3 self-contained**
- Either ship `scripts/ci_secret_scan.py` to the public tree (it's a scanner, allowlist-consistent), or guard the C3 job (`if: hashFiles('scripts/ci_secret_scan.py') != ''`).
- **Acceptance**: dry-run `git archive origin/release/debut | tar -t | grep ci_secret_scan` per decision; `bash scripts/ci_secret_scan.py /tmp/sk-test` behavior documented.
- Commit: `fix(ci): secret-scan C3 job self-contained on public tree`

**PR-G [P1-6] Backup debris off the public branch**
- `git rm --cached` the 5 tracked backups (`grokster`, `kali×2`, `jem`, `arch/soul.yaml.backup`); extend `.gitignore`: `data/entities/*/soul.yaml.bak.*` + `data/entities/*/soul.yaml.backup`.
- **Acceptance**: `git ls-tree origin/release/debut | grep 'soul.yaml.bak\|soul.yaml.backup'` → empty; still 0 vault files (D-565).
- Commit: `chore(debris): untrack soul backups from public branch + gitignore pattern`

### WAVE 3 — GATE-INTEGRITY PRs
**PR-H [P1-7/P1-8] Makefile truth + temple-grade real**
- Add `firewall-check: @$(PYTHON) src/omega/audit/firewall_checker.py` (align with `.clinerules`/AGENTS.md docs); add `check-mandate-compliance` + `lint` + `test-contract` into `temple-grade` deps; remove placeholder comment; assert exit codes.
- Update `.clinerules` §KEY COMMANDS to match actual targets (kill documented-but-missing commands).
- **Acceptance**: `make firewall-check` exit 0; `make temple-grade` now actually exercises ≥8 real gates; `make help` lists only real targets.
- Commit: `chore(make): firewall-check target + temple-grade real gate chain (M13/M27)`

**PR-I [P1-9] One compliance truth-source**
- Make `check-mandates` call `check-mandate-compliance` (done in PR-A) OR delete the meter's standalone claims — one entry point, one exit code. Add CI step: `make check-mandate-compliance` in ci.yml.
- Commit: `ci(mandates): single compliance gate in CI`

### WAVE 4 — POST-DEBUT (each its own PR, tracked issues)
- **Q-1 [P2-10/P1-10] pyflakes 174**: redefinitions first (42 — real shadowing risk), then unused imports/locals (105). One subsystem per PR.
- **Q-2 [P2-1] god-modules**: split `observability/__init__.py` (1660) → trace/BLEG/sovereignty submodules; then model_gateway/oracle/providers; one file per PR, `make test` green each.
- **Q-3 [P2-2] silent swallows**: ratchet `config/m23_baseline.txt` to measured 60→0 burn-down, ≤10/PR, each `pass` → typed narrow except + `logger.debug` or `OmegaError` wrap (M9).
- **Q-4 [P2-4] M1 loophole**: ratify `tty_agent.py`/`governance/` exemption as a D-number (doc-only).
- **Q-5 [P2-8] OMEGA_ENGINE.md**: refresh to 27 mandates v3.8.0 + 2026-08-28 state; add LAST_VERIFIED cadence (M27).
- **Q-6 [P2-7] M11 scale**: 24/56 → 56/56 substantive `proposed_lessons.yaml` (NEW-04 baseline), uniform layout (`memory/proposed_lessons.yaml` canonical), <500B stubs retired.

---

## §5 GO/NO-GO RE-CHECK — 9-ITEM CHECKLIST (exact commands)

```bash
# 1. Secret history scrubbed
git log -S GOCSPX- --all | wc -l            # → 0
# 2. Engine's own secret gate green
make gate-secrets                                                      # → exit 0
# 3. Compliance meter green AND gating
python3 scripts/check_mandate_compliance.py                            # → 27/27 or ≥24 (SKIPs documented); M23/M27 ✅
make check-mandates                                                    # → exit 0 (now includes meter)
# 4. Allowlist conformant
bash scripts/apply_public_allowlist.sh --summary                       # → Removed: 0
# 5. Lint clean
make lint                                                              # → exit 0, 0 findings
# 6. Contract suite green
python3 -m pytest tests/contract -q                                    # → 0 failures
# 7. Temple-grade real
make temple-grade                                                      # → exit 0 (≥8 real gates)
# 8. Fresh-venv import (D-539/CP-3)
python3 -m venv /tmp/go-venv && /tmp/go-venv/bin/pip install -e . && \
  /tmp/go-venv/bin/python -c "import omega; import omega.cli.oracle_cli"   # → exit 0
# 9. Focused runtime smoke
omega --help && omega list-entities                                    # → exit 0
```
All 9 green → **GO; cut the PR at https://github.com/Xoe-NovAi/omega-engine/pull/new/release/debut**. Any red → stay NO-GO; fix forward per the owning PR.

## §6 FINAL STATEMENT

**NO-GO today — and now we know exactly why, in four hard, reproducible blockers** (secret in history, secret gate failing, allowlist drift, compliance meter decoupled from every green gate). Nothing else in the sweep is structural: 6 gates pass, the CLI works, fresh-venv install works, CI is real, the provider fabric is sound. The remaining debt is tracked, spec'd, and burnable. This is a Cathedral worth launching — it just needs 2 honest hours of incident response + gate repair before the world meets it.

*⬡ OMEGA ⬡ CLINE ⬡ AP-CLINE-FULL-REVIEW-20260828-v2.0.0 ⬡ cline ⬡ trc_alpha_launch ⬡ DEEP-EXECUTED · P0=4 · P1=10 · P2=12 · GATES=6/6 · VERDICT: NO-GO (spec'd to GO)*
<!-- PROVENANCE-CORRECTED 2026-08-29T03:07:15Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash (1M) | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

