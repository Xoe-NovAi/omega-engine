<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# CARMACK ALPHA LAUNCH VERDICT — 2026-08-28
**AP**: AP-JOHN_CARMACK-v1.0.0 · **Session**: ses_fc8dca39effe3nZJp3QHx81Fy3 · **For**: Architect (final gate) · **Sprint**: PUBLIC-DEBUT-01 · **Branch**: `release/debut` @ `1dee11aa`
**Reads**: `CLINE_FULL_REVIEW_ROLLUP_20260828.md` (306L) · `CLINE_TO_KALI_HARDENING_BRIEFING_V2_20260828.md` (240L) · `CARMACK_FULL_REPO_REVIEW_CHECKLIST_VALIDATED_20260828.md` (372L)
**Method**: Adjudicate contradictions between rollup v2 and hardening v2; provide architectural verdict where the corpus disagrees; right-approximation check on every P0 fix; honest assess of alpha bar.

---

## §1 EXECUTIVE VERDICT (3 sentences)

**GO on alpha launch** after the 4 P0s close (estimated 2-3 engineer-hours + 1 human GCP rotation + 1 filter-repo pass per the rollup's §4 spec), with the **additional Carmack architectural addendum** in §3 below. The Cathedral is launch-worthy: 6 hard gates pass, CLI works, fresh-venv install works, CI is real, the provider fabric is sound, and the remaining 22 findings (P1=10, P2=12) are tracked, spec'd, and post-debut burnable. The rollout is a *release* (alpha) not a *promise* (beta) — it ships with disclaimers, not with the work done.

**Confidence**: 9/10. P0 close-out is small; P1/P2 are tracked; 2 open questions (hardening v2 vs rollup v2 meter state, 7-ahead commit audit) need Architect sign-off before cut.

---

## §2 P0 REMEDIATION REVIEW (architectural adjudication)

### P0-1 [MAND] Compliance meter broken/decoupled — `python`→`sys.executable` fix is correct but insufficient
**Contradiction adjudication**:
- **My validation pass** (2026-08-28 ~17:50 UTC) showed `python` not found → M23/M27 FAIL → 20/27 = 74.1%
- **Cline Hardening v2** (~30 min later) shows 23/27 = 85.2%, "meter works"

**Most likely explanation**: my run hit the broken path, hardening v2 hit a fixed path — **the fix may have been applied in the interval**, OR the meter has path-dependent behavior I didn't characterize. Either way, the **fix spec is correct**: `sys.executable` is the right call (more robust than `python3` because it resolves against the actual interpreter).

**Architectural verdict on the fix**:
- ✅ `python` → `sys.executable` (or `python3`): correct, but `sys.executable` is the strictly-better choice (works under venv, pyenv, system pipx, etc.)
- ✅ M20 `llama_cpp` absent → SKIP/UNTESTED not FAILED: correct, env-dependence honesty
- ✅ Wire meter into `check-mandates` AND `temple-grade`: correct
- ⚠️ **ADD**: the meter's brittleness is the deeper finding. A mandate enforcement system that breaks because of `python` vs `python3` is a load-bearing tool with a hair-trigger. **Recommend**: add a self-test in the meter (`assert sys.executable != 'python' and Path(sys.executable).exists()`) and fail loud if the interpreter path is unresolvable. Future-proofs against the next "python4" / "python" symlink / missing venv.

**Acceptance**: PR-A spec is sound; +1 line for the interpreter self-test. **ACCEPT.**

### P0-3 [SEC] GOCSPX OAuth secret in 4 history commits + 12 disk files
**Architectural verdict**:
- ✅ **Rotation is the load-bearing fix** (Google Cloud Console → Regenerate). Once the old secret is dead, the literal in history is forensic, not exploitable. Hardening v2's reclassification (private repo, future exposure) is correct.
- ✅ **`git filter-repo` is the right tool**, NOT `git rebase`/`git filter-branch`. Rationale: filter-branch is deprecated by git itself (1.7+ years), unsafe on large repos, and slow; rebase can't reach into commit objects safely. `filter-repo` is GitHub's recommended tool (13.2k stars), preserves author metadata, supports dry-run, single-pass. The rollup's command is correct.
- ✅ **Order is correct**: rotate → redact working-tree → filter-repo → re-key gates. Cannot reorder: redaction before rotation means a `git push` of pre-rotation working tree ships the new rotation's literal before it's stable.
- ⚠️ **Gitleaks baseline requires WHY-rationale per entry** (K-8 in hardening v2): correct — the rollup says "add to `.gitleaksignore`" but doesn't require justification. The hardening v2 specifies Kali-ratified audit trail. **Add: per-entry `why:` comment in `.gitleaksignore`**.
- ⚠️ **7-ahead commits audit (hardening v2 §8.1.5)**: the rollup scopes filter-repo to the GOCSPX literal, but the 7-ahead commits may carry other unverified content. **ADD: `git log -p HEAD~7..HEAD` eyeball before re-key, for ANY other secrets/data**. This is 5 minutes, not optional.
- ⚠️ **Hardening v2 UNVERIFIED claim** (Google auto-revocation timing): the architectural risk is real (GitHub partner scanning notifies Google → auto-revoke), but the *timing* of auto-revocation matters. If it's "days", we have buffer. If "hours", rotation must be coordinated with the debut push. **Architect decision required**: which way?

**Acceptance**: Rollup's Wave 0 spec is sound. **ACCEPT with 2 additions** (per-entry `.gitleaksignore` rationale + 7-ahead commit eyeball).

### P0-4 [DEBR/ALLOWLIST] release/debut FAILS own allowlist gate — 4 files
**Architectural verdict**:
- ✅ `apply_public_allowlist.sh --confirm` is the right tool (already shipped, M23-exempt per rollup §2 PASS LEDGER)
- ✅ 4 files (`data/library`, `data/memory` empty dirs + 2 `R_AUTO_…md` files with malformed filenames) — trivial fix
- ✅ CI `allowlist-check.yml` will RED on debut push until fixed — correct, that's the gate working
- ✅ D-565 semantics (vault excluded, interface kept) — the rollup confirmed 0 vault files in release tree, so D-565 is intact; the failure is tooling drift, not policy violation. **My prior NEW-04 concern was MAND-06 was wrong baseline; this concern is DEBR drift and is real.**

**Acceptance**: PR-B spec is sound. **ACCEPT.**

### P0-5 [SEC/GATE] `make gate-secrets` exit 1 — two independent defects
**Architectural verdict**:
- ✅ Defect (a) GOCSPX literal in 4 history commits: real, requires filter-repo (P0-3 fix closes this)
- ✅ Defect (b) **PEM baseline path drift** — the gate excludes the WRONG files in its baseline. This is a **tooling bug independent of any secret**. The gate self-fails on false positives. **Architectural finding**: a gate that fails on its own config drift is **worse than a gate that doesn't exist** — it produces noise that trains the team to ignore red lights.
- ⚠️ **ADD: the gate needs a self-test** (`make gate-secrets` should run on a known-clean state and verify it exits 0; if not, the gate's baseline is misconfigured, not the repo).
- ⚠️ The PEM baseline in `config/` (or wherever it lives) needs a WHY-per-entry comment, parallel to `.gitleaksignore` hygiene.

**Acceptance**: PR-2 (re-key gates) is sound. **ACCEPT with self-test addition.**

---

## §3 P1 RISK ASSESSMENT (10 items, each: accept/fix/reject)

| ID | Finding | Verdict | Rationale |
|----|---------|---------|-----------|
| **P1-1** | `logger` NameError at import time (L80/85 vs L106) | **ACCEPT AS P1 (downgraded by hardening v2)** | Hardening v2 is correct: module-level `logger` defined L106, used inside a function body that only executes when called. No NameError possible at import. **Real P1 sub-finding remains**: duplicate `OmegaError` import at L98-101. Landmine is real, location is wrong. |
| **P1-2** | Provider contract test STALE vs providers.yaml SSOT (deepseek-v4-flash no longer on openrouter) | **FIX BEFORE LAUNCH** | Provider fabric is the **only user-facing runtime path**. A contract test that lies about which provider serves a model is worse than no test. Fix is small (update one test expectation, design choice: exact-match-first normalization in `_normalize_model`). D-536 SSOT is core. |
| **P1-3** | Soul contract test couples to live data (asserts staging==[]) | **ACCEPT** | Test runs against `data/entities/kali/proposed_lessons.yaml` which is continuously mutating. The right fix (PR-E) decouples via tmp fixture clone. This is test hygiene, not a runtime bug. Ship with tracked issue. |
| **P1-4** | M11 promotion backlog: 49 kali lessons un-promoted | **ACCEPT (or batch-promote)** | The lessons are in `proposed_lessons.yaml`, not approved; they are *staged*, not *live*. Hydration reads from `approved_lessons.yaml`. Stale staging ≠ broken system. If Architect wants the 49 promoted: `python3 scripts/promote_soul_lessons.py --entity kali` (post-vetting). Acceptable either way. |
| **P1-5** | `secret-scan.yml` C3 references `scripts/ci_secret_scan.py` (forge-only) | **FIX BEFORE LAUNCH** | This is a self-inflicted wound: a public-tree CI job that errors on a missing file. Either ship the script or guard the job. 15 minutes. |
| **P1-6** | 5 soul backups + 1 `.backup` tracked on release/debut | **FIX BEFORE LAUNCH** | `data/entities/*/soul.yaml.bak.*` aren't `.gitignore`d. The gitignore pattern needs to be tightened (`soul.yaml.bak*` not `*.bak`). One-line fix. |
| **P1-7** | `make firewall-check` documented but missing | **ACCEPT** | Documented-but-missing command is doc drift, not code defect. The actual check (firewall_checker.py) exists; just no Makefile target. Either add target (PR-H) or delete from docs. 5 minutes either way. |
| **P1-8** | Temple-grade gate is decorative (placeholder comment) | **ACCEPT (P1 becomes P0-1 sub-task)** | This is the same finding as P0-1. The rollup's PR-H closes both. Not a separate work item. |
| **P1-9** | Compliance meter decoupled from CI | **ACCEPT (P1 becomes P0-1 sub-task)** | Same as P1-8. Closed by PR-A/PR-H. |
| **P1-10** | pyflakes 174 findings (42 redefinitions, 62 unused imports, 43 unused locals) | **ACCEPT (post-debut burndown Q-1)** | 42 redefinitions are real shadowing risk, but each is a small fix and the burndown is 1-2 weeks of mechanical work. Not a launch blocker. **BUT**: include the 42 redefinition count in the launch README as a known-issues bullet. |

**Summary**: 6 ACCEPT, **3 FIX BEFORE LAUNCH (P1-2, P1-5, P1-6)**, 1 ACCEPT (P1-1 downgraded), 0 reject.

**Total pre-launch P0+P1 work**: 4 P0 fixes (PR-A, B, C, Wave 0) + 3 P1 fixes (PR-D provider SSOT, PR-F ci_secret_scan, PR-G gitignore backups). Estimated: 3-4 engineer-hours + 1 human GCP rotation.

---

## §4 P2 CATEGORIZATION (12 items)

| ID | Finding | Verdict | Note |
|----|---------|---------|------|
| **P2-1** | 11 modules >1000 lines (observability/__init__.py 1660 worst) | **ACCEPT (Q-2 post-debut)** | God-modules. Split one per PR. observability/__init__.py is the priority. |
| **P2-2** | 60 silent `except…: pass` sites | **ACCEPT (Q-3 post-debut)** | Ratchet burndown 60→0, ≤10/PR. |
| **P2-3** | `_normalize_model` strips `-local/-free/-thinking` → silent re-routes | **PROMOTE TO P1** | **This is a paid-model-routing risk.** A request for `qwen3-4b-local` silently routing to `qwen3-4b` (cloud) is a billing surprise AND a privacy violation. Exact-match-first should be a launch requirement. **FIX BEFORE LAUNCH** in PR-D. |
| **P2-4** | M1 loophole unratified (tty_agent.py + governance/ exempt, no D-number) | **ACCEPT (Q-4 post-debut)** OR **FIX (preferred)** | If M1 is load-bearing, refactor tty_agent to anyio. If M1 has accepted exceptions, ratify by D-number. The current state — silent exemption — is the worst option. **My recommendation**: refactor (use anyio.from_thread.run_sync or anyio.to_thread.run_sync), eliminate the exemption. Post-debut. |
| **P2-5** | M20 gate env-dependent (llama_cpp absent → FAIL not SKIP) | **ACCEPT (closed by P0-1 sub-task)** | The meter's SKIP/UNTESTED for env-dependent mandates is part of P0-1 fix. |
| **P2-6** | Full pytest suite stalls (OOM risk on 14Gi) | **ACCEPT (CI-only)** | Dev box not the right host for full suite. CI runs in fresh resources. Document in AGENTS.md. |
| **P2-7** | M11 substantive count 24/56 | **ACCEPT (Q-6 post-debut)** | Real gap but 56-entity refactor is a 1-month initiative. Track; don't block debut. |
| **P2-8** | OMEGA_ENGINE.md stale (claims 25 mandates v3.7.0, dates 07-30) | **ACCEPT (Q-5 post-debut)** OR **FIX (5 min)** | Doc refresh is 5 minutes if you know the new numbers. The launch README will supersede anyway. Post-debut. |
| **P2-9** | Malformed filenames + internal docs on public branch | **PROMOTE TO P0 (subsumed by P0-4)** | Already in PR-B. The 2 R_AUTO files are the 4-line PR-B. Closed. |
| **P2-10** | Duplicate `OmegaError` import pattern (42 sites repo-wide) | **ACCEPT (Q-1 sub-task)** | Mass-fix in pyflakes cleanup wave. |
| **P2-11** | 19 `ses_*` session IDs in WAKE_STATE.json + entity/workspace docs | **ACCEPT (post-debut)** | Internal identifiers. Need a policy (strip before ship?), but not launch-blocking. |
| **P2-12** | Fleet at cap (14 entries under .opencode/agents/) | **ACCEPT (tracked, not blocking)** | M10 cap is working as designed. No agent can be added without removing one. Conscious constraint. |

**Summary**: 9 ACCEPT, **1 PROMOTE TO P1 (P2-3)**, 1 PROMOTE TO P0 (subsumed by P0-4), 0 reject.

---

## §5 ALPHA-LAUNCH READINESS

### The alpha bar (right-approximation)
- **Alpha**: code installs cleanly (D-539 ✅), CLI smoke works (✅), core contract tests pass (✅), 6 hard gates green, no P0 open, no P1 silently broken. Known-issues documented. Early-adopter tolerance for UX rough edges is HIGH; tolerance for data loss / privacy leak / cloud-billed-when-local-claimed is ZERO.
- **Beta**: alpha + P1 closed + perf baselines established + soak test 7 days.
- **RC**: beta + 30 days in field + zero P1 incidents + UX pass.

**This code is worthy of an alpha tag**, not a beta. The remaining work is post-debut burnable, not launch-blocking.

### Minimal feature flag set (for alpha)
```
# In config/providers.yaml or env:
OMEGA_ALPHA_MODE=true          # enables verbose error messages
OMEGA_ALPHA_NO_TELEMETRY=true  # redundant w/ M8, but explicit
OMEGA_ALPHA_PAY_ROUTING=strict # exact-match-first in provider_registry
OMEGA_ALPHA_AUDIT_LOG=true     # write every CLAIM to truth_events.jsonl
```
**The OMEGA_ALPHA_PAY_ROUTING=strict flag is load-bearing** — it's the runtime expression of P2-3's fix. Without it, an early adopter asking for a `-local` model may silently get a cloud-routed one.

### README disclaimers (mandatory)
1. **"ALPHA — expect rough edges. File issues at [URL]. The team triages daily."**
2. **"Data sovereignty: this engine does NOT phone home. Verify with `omega audit trail` (M22/M8)."**
3. **"Provider billing: by default, local-only. Cloud providers require explicit `--allow-cloud` flag. See config/providers.yaml for the strategy."**
4. **"Secrets: the engine has no telemetry SDK. If you find one, it's a bug — open an issue."**
5. **"The 27 Sovereign Mandates are the project's constitution. README.md + SOVEREIGN_MANDATES.md are the spec; the Makefile is the test suite."**
6. **"Known issues: [link to P1+P2 list with expected close dates]"**

### Launch checklist (final 9-item gate, rollup §5 verbatim + 2 additions)
1. `git log -S GOCSPX- --all | wc -l` → 0
2. `make gate-secrets` → exit 0
3. `python3 scripts/check_mandate_compliance.py` → ≥24/27 (M17-M20 SKIP/UNTESTED acceptable) + `make check-mandates` → exit 0
4. `bash scripts/apply_public_allowlist.sh --summary` → `Removed: 0`
5. `make lint` → 0 findings
6. `python3 -m pytest tests/contract -q` → 0 failures
7. `make temple-grade` → exit 0 (≥8 real gates)
8. `python3 -m venv /tmp/go-venv && /tmp/go-venv/bin/pip install -e . && /tmp/go-venv/bin/python -c "import omega; import omega.cli.oracle_cli"` → exit 0
9. `omega --help && omega list-entities` → exit 0

**+ ADD**: 10. `git log -p HEAD~7..HEAD` eyeball for any non-GOCSPX sensitive content.
**+ ADD**: 11. `OMEGA_ALPHA_PAY_ROUTING=strict omega oracle route "qwen3-4b-local"` → resolves to local provider, not cloud.

---

## §6 V-1 PRIORITY LIST (TOP 10)

This is what the post-debut sprint should attack, in order. **The vault refactor question** (per Architect's prompt) gets an explicit answer.

| # | Item | Effort | Impact | Architect answer |
|---|------|--------|--------|------------------|
| **1** | **VAULT: delete, don't refactor** | 1 sprint | -3,300 LOC, removes a debloat anchor | **CHANGES PRIORITY**: D-565 already excludes vault from debut. The 3,300 LOC of vault code is dead-on-arrival for alpha. **Recommend DELETE entirely**, replace with a thin `src/omega/secrets.py` (~100 lines) that reads from env. The Path A' refactor assumes we'll keep the vault; if we won't, the refactor is wasted work. **Architect decision required**: are we keeping vault at all? |
| **2** | **M1 loophole: refactor `tty_agent.py` to anyio** | 0.5 sprint | Eliminates P2-4, strengthens M1 enforcement | Yes — silent exemptions erode the mandate. |
| **3** | **Compliance meter hardening (sys.executable + self-test)** | 0.5 day | Closes P0-1 brittleness | Yes — already in PR-A. |
| **4** | **Pyflakes 174 burndown** | 1-2 weeks | Removes 42 shadowing risks + unused imports | Yes — mechanical, low-risk. |
| **5** | **God-module split: observability/__init__.py (1660) → trace/BLEG/sovereignty** | 1 sprint | Removes worst file, improves testability | Yes — most-bang-per-line. |
| **6** | **M11 entity refinement: 24/56 → 56/56 substantive** | 1 month | Soul integrity actually enforced | Yes — but ship as separate campaign, not blocking. |
| **7** | **P2-2 silent swallow burndown (60→0)** | 1-2 weeks | M23 becomes verifiable | Yes — ratchet continues. |
| **8** | **SoTA standardization: threat-modeling for agent attribution** | 1 week | Adopt Ed25519 + open interoception schema | Yes — open-source the schema to lock in the standard. |
| **9** | **OMEGA_ENGINE.md refresh (27 mandates, current dates)** | 1 hour | Doc accuracy | Yes — trivially, do it now. |
| **10** | **Two-truth-sources elimination: one mandate gate, one exit code** | 0.5 day | Closes P1-9, kills "compliance: 74.1% AND all gates pass" contradiction | Yes — same PR as P0-1. |

**Architectural answer on the vault**:
- **D-565 excludes vault from debut** (no code changes for debut)
- **If vault is dead code post-debut** (likely, per D-565 framing), the **3,300+ LOC delete is V-1 priority #1**, and the **Path A' refactor is moot** — it's refactoring code we're deleting
- **If vault is alive** (some post-debut workflow needs it), then Path A' is V-1 priority #1, and the delete is premature
- **My recommendation**: delete. Sovereignty can be served by `secrets.py` + env. The vault's complexity is the problem it's supposed to solve.

**Recommendation to the Architect**: choose delete. Path A' is V-1 if and only if vault survives; deletion is V-1 unconditionally.

---

## §7 FINAL STATEMENT

**GO on alpha launch** after the P0 close-out (4 items, ~3-4 engineer-hours) + 3 P1 fixes (provider SSOT, ci_secret_scan self-containment, gitignore pattern) + 1 P1 promote (P2-3 pay-routing flag). Total wall-clock: half a focused day. The 6 hard gates that pass are load-bearing: M1 (AnyIO), M8 (zero telemetry), M9 (no bare except), M14 (heritage), M26 (LLM doc validate), D-539 (fresh-venv install). The CLI works, the provider fabric is sound, the local-inference path is verified (sprint gate "local_inference_end_to_end" COMPLETED). The Cathedral stands.

**What this verdict does NOT change**: the truth-alignment dataset (TA-001..TA-010), the 9 architectural decisions (D-526..D-593), the Pillar Keeper roster, the Orchestrator Charter (v1.0). The architecture is intact; the launch gate is the secret, the meter, the allowlist, and one provider-routing guard.

**What this verdict DOES add**:
1. The hardening v2's refutations of its own v1 claims are correct; P0-2 (oracle_cli broken) and P1-1 (logger landmine) are not P0/P1 in the original sense — but the duplicate `OmegaError` import is a real P1 in P1-1's place.
2. **P2-3 is promoted to P1** (pay-routing) — this is the only one I'd insist on pre-launch.
3. **The vault refactor question has a different answer than expected**: D-565 implies delete, not refactor. Recommend Architect choose delete.

**Confidence**: 9/10. The 1-point uncertainty is the 7-ahead commit content (unverified beyond GOCSPX) and the Google auto-revocation timing. Both are Architect-decisions, not Carmack-decisions.

**The Cathedral is launch-worthy. The architect's hands are on the wheel. Ox Alpha rides.**

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ x-preview-f-free ⬡ opencode ⬡ trc_audit ⬡ VERDICT-ISSUED · ALPHA-GO · P0=4 · P1=10 · P2=12 · GATES=6/6*
*Confidence: §1 verdict 9/10 · §2 P0 adjudication 9/10 (10/10 on rotation+filter-repo correctness, 7/10 on Google auto-revocation timing unverified) · §3 P1 risk 9/10 · §4 P2 categorization 9/10 · §5 alpha bar 10/10 · §6 V-1 8/10 (vault delete vs refactor is Architect call) · §7 final 9/10*
