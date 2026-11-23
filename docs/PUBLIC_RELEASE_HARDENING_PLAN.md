<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Public Release Hardening Plan — Curated Cut ↔ CI Contract

**AP Token**: `AP-PUBLIC-RELEASE-HARDENING-v1.0.0`
**Status**: PLANNED — awaiting Architect approval to execute
**Date**: 2026-11-23
**Research sources**: see §8 — RE-FETCH THESE post-compaction before execution.
**Related**: `docs/operations/DUAL_REMOTE_RELEASE_RUNBOOK.md`,
`docs/operations/RELEASE_PR_PUBLIC_STANDARDS.md`, `PUBLIC_ALLOWLIST.txt`,
`docs/strategy/PUBLIC_ALLOWLIST.txt`, `docs/HEADROOM_ENHANCEMENT_PLAN.md`

---

## 1. Executive Summary

The public repo is up to date at `v1.6.0a8` (cut `595d3b7b`, 946 files) and the source tree is
clean, but **the release pipeline is broken**: the curated cut removes scripts that the public
workflows and public `Makefile` invoke. Neither `v1.6.0a7` nor `v1.6.0a8` produced a GitHub
Release — consistent with `release.yml` failing before `gh release create`.

This plan restores the cut↔CI contract, makes the gate fail closed, resolves the duplicate-allowlist
split-brain, and completes artifact verification. Research strongly favors a **new patch version**
over force-moving the published tag (§3, Decision D1).

---

## 2. Evidence (local discovery, 2026-11-23)

### 2.1 Missing scripts in the public tree

`release.yml` invokes these; none exist in `debut/main`:

| Gate | Script | Status |
|------|--------|--------|
| G8 | `scripts/check_release_changelog.py` | MISSING |
| G9 | `scripts/check_version_consistency.py` | MISSING |
| G10 | `scripts/check_wheel_contents.py` | MISSING |
| G11 | `scripts/verify_artifact_clean_env.py` | MISSING |

Public `Makefile` also references missing `check_doc_facts.py`,
`check_workflow_trigger_coverage.py`, `validate_wad.py`. `release.yml` runs
`make temple-grade require_clean=1 HUB_IMPORT_MODE=pristine` as its first gate, so failure can
occur even before G8.

Neither script is in either allowlist. `gh release view` returns "release not found" for both
`v1.6.0a7` and `v1.6.0a8`.

### 2.2 Allowlist split-brain

- Ratified: `PUBLIC_ALLOWLIST.txt` (Status: APPROVED, 2026-10-09).
- Operative: `docs/strategy/PUBLIC_ALLOWLIST.txt` (Status: DRAFT) — this is what
  `scripts/apply_public_allowlist.sh:74` reads by default.
- They differ substantially. The Headroom configs had to be added to **both** to make the cut
  retain them. Nothing enforces parity.

### 2.3 Test suite is not hermetic

`make test` rewrites `config/wads/_omega_default/entities.yaml` (domain ordering), causing
`test_wad_sync` + `test_lint_wad_all` to fail on a second consecutive run unless the file is
restored from git. Observed four times this session.

### 2.4 PyPI trigger state

`publish.yml` originally had `on: release: types: [published]` + `workflow_dispatch`. Per Architect
decision (publisher not yet approved), the `release:` trigger was removed in `2805e181`; only
`workflow_dispatch` remains. That workflow uses OIDC Trusted Publishing (`environment: pypi`,
`id-token: write`), which requires a *registered trusted publisher* on pypi.org — approval is a
separate, outstanding item.

---

## 3. Research-Backed Decisions

### D1 — Do NOT force-move `v1.6.0a8`; cut `v1.6.0a9` instead
Published tags are promises. Git does not propagate tag moves on normal fetch, so a moved tag
splits consumers (some hold the old commit). The ACM REP '26 study found 10.2M tag alterations
across 328.4M repos, 626k moves, 68% content-changing, with real reproducible-build breakage
(Nixpkgs) and a supply-chain incident (tj-actions/changed-files tag retargeting).
GitHub "immutable releases" lock tags after publication; force-moving is only defensible
*immediately*, before any workflow/consumer used the tag. Here a workflow did run on the tag
(we just don't have a Release), so the safer path is a new patch version. Mark `v1.6.0a8`
superseded in `v1.6.0a9` release notes.

### D2 — Fail closed: workflow must verify its own prerequisites
Research pattern: "a gate that can't run must fail" — no `continue-on-error`, no `|| true`.
Add a pre-flight step that asserts every `scripts/*.py` referenced by `release.yml` and the public
`Makefile` exists in the cut tree, driven by one array (existence check and invocation from the
same source). A missing script then produces a loud, located failure — not a silent no-op or a
late G8 crash.

### D3 — Single source of truth for the allowlist
Make `scripts/apply_public_allowlist.sh` read the ratified root `PUBLIC_ALLOWLIST.txt` by default
(or make `docs/strategy/...` a symlink), and add a CI parity check that fails when the two differ.
Until then, any future entry added to only one file silently does nothing.

### D4 — PyPI stays manual until approved
Keep `workflow_dispatch` only. When approved: register the trusted publisher on pypi.org for
`Xoe-NovAi/omega-engine` + `publish.yml` + environment `pypi`, add required reviewers on that
environment, restrict publishing job to download+upload (two steps), and re-enable `release:`.
PEP 740 attestations are generated automatically by `pypa/gh-action-pypi-publish@release/v1`
(v1.11+), so no manual signing is needed.

### D5 — Artifact verification: SHA + attestation, not SHA alone
Record the wheel SHA256 in `docs/FACTS.yaml` after download from GitHub Releases (verify
byte-for-byte with `hashlib`), and additionally use `gh release verify` /
`gh release verify-asset` when the release is immutable. Research note: a checksum answers "same
bytes"; an attestation answers "published by the real pipeline"; rebuild-from-source answers
"contents match the repo". Only the first is in scope now.

### D6 — Hermetic test suite via `conftest.py` guard
Adopt the researched pattern: session-scoped `autouse` fixture that records `git status --porcelain`
before the suite, tracks write-mode opens under the repo, and fails if a previously-clean tracked
file was modified. Locate the specific test that writes `entities.yaml` (candidates found:
`tests/test_wad_loader.py`, `tests/test_entity_affinity.py`, `tests/conftest.py`) and redirect it to
`tmp_path` / `monkeypatch.chdir`. The guard prevents recurrence for *any* future test.

---

## 4. Execution Plan

### Phase 1 — Restore cut↔CI contract (P0)
1. Add the 7 missing scripts to **both** allowlists with `[CI-required]` annotations, mirroring the
   existing `heritage_vet.sh` precedent:
   `check_release_changelog.py`, `check_version_consistency.py`, `check_wheel_contents.py`,
   `verify_artifact_clean_env.py`, `check_doc_facts.py`, `check_workflow_trigger_coverage.py`,
   `validate_wad.py`.
2. Add a pre-flight script-existence step to `release.yml` (fail closed).
3. Re-cut public, assert every workflow/Makefile script reference resolves in the cut tree,
   removals = 0.

### Phase 2 — Version + publish (P0)
4. Atomically bump to `v1.6.0a9` (5 files per runbook §2); note `v1.6.0a8` superseded.
5. Annotated tag, push to `debut`. Keep `publish.yml` dispatch-only.
6. Verify GitHub Release appears and both `.whl`/`.tar.gz` assets attach; if not, debug workflow.

### Phase 3 — Artifact verification (P1)
7. Download the wheel, verify SHA256, record in `docs/FACTS.yaml`; run `gh release verify-asset`
   if supported by the repo's release settings.

### Phase 4 — Structural hardening (P1/P2)
8. D3: single allowlist source + parity gate.
9. D6: hermetic test guard + fix the specific WAD-mutating test.
10. Optional: enable GitHub immutable releases / tag protection ruleset on `v*` (D1 research).

---

## 5. Files to Modify

| File | Change |
|------|--------|
| `PUBLIC_ALLOWLIST.txt` + `docs/strategy/PUBLIC_ALLOWLIST.txt` | add 7 CI-required scripts |
| `.github/workflows/release.yml` | pre-flight script-existence gate (fail closed) |
| `pyproject.toml`, `CHANGELOG.md`, `README.md`, `ANNOUNCEMENT_v1.6.0-alpha.md`, `docs/FACTS.yaml` | atomic a9 bump |
| `scripts/apply_public_allowlist.sh` | default to ratified allowlist (D3) |
| `tests/conftest.py` | hermetic tracked-file guard (D6) |
| offending WAD-mutating test | redirect writes to tmp_path |
| `docs/PUBLIC_RELEASE_HARDENING_PLAN.md` | this document |

---

## 6. Success Criteria

- [ ] Every `scripts/*` referenced by public workflows/Makefile exists in the cut tree
- [ ] Pre-flight gate fails when a referenced script is absent (negative test)
- [ ] `v1.6.0a9` cut: removals = 0, annotated tag pushed, GitHub Release + wheel exist
- [ ] Wheel SHA256 verified and recorded in `docs/FACTS.yaml`
- [ ] Allowlist parity enforced by a gate; both files byte-identical
- [ ] `make test` leaves `git status --porcelain` unchanged (no tracked-file mutation)
- [ ] `publish.yml` remains dispatch-only; no PyPI egress without approval
- [ ] All existing gates still green (2757 tests, temple 53/53, M23/M1)

---

## 7. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Allowlisting more scripts widens public surface | each is SPDX-headered, CI-required, no secrets; precedent exists |
| New version instead of tag move confuses users | mark `v1.6.0a8` superseded in a9 notes + FACTS.yaml |
| Pre-flight gate too strict for `workflow_dispatch` | scope it to the release job only; negative-test both paths |
| Hermetic guard false-positives on legitimately dirty trees | compare before/after SETS, not absolute cleanliness |
| PyPI publisher registered before approval | keep `workflow_dispatch`; do not register trusted publisher yet |

---

## 8. Web Research Sources — RE-FETCH POST-COMPACTION

| # | Source | URL | What it answers |
|---|--------|-----|-----------------|
| 1 | **Release readiness gates** | https://adamblansett.com/blog/release-readiness-action-guide/ | "Manifest Script Integrity" as a release-readiness property; changelog/lockfile freshness. §2.1/Phase 1. |
| 2 | **Quality gates / fail closed** | https://aicodeops.dev/blog/quality-gate-configs | "A gate that can't run must fail"; keep floors in `.github/`; CODEOWNERS on gates. D2. |
| 3 | **CI gate lies** | https://codepulse.at/blog/ci-release-gate-lies-layered-defenses | Parallel gate theater, exclusion-list no-op, one-array source of truth, layered defenses. D2. |
| 4 | **PyPI trusted publishing (usage)** | https://docs.pypi.org/trusted-publishers/using-a-publisher/ | `environment: pypi`, `id-token: write`, official action. D4. |
| 5 | **PyPI security model** | https://docs.pypi.org/trusted-publishers/security-model/ | Treat Trusted Publisher as a credential; per-job perms, dedicated environment, tag protection, minimal publish job. D4. |
| 6 | **PyPA GH Actions guide** | https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/ | Separate build from publish jobs; publish job only downloads + uploads. D4. |
| 7 | **GitHub immutable releases** | https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases | Tags/assets locked after publication; attestation; tag cannot be reused. D1/D5. |
| 8 | **Moving or deleting a published tag** | https://www.git-automation.com/git-workflow-architecture-branching-strategies/release-tagging-versioning/moving-or-deleting-a-published-tag/ | Tags don't propagate; prefer a new version; immediate-only exceptions. D1. |
| 9 | **Tag alteration study (ACM REP '26)** | https://dl.acm.org/doi/full/10.1145/3820002.3828585 | 10.2M alterations; 626k moves; 68% content-changing; real build breakage. D1. |
| 10 | **PyPI package integrity** | https://docs.pypi.org/using-pypi/package-security/package-integrity/ | SHA256/BLAKE2b from JSON API; hashlib verification snippet. D5. |
| 11 | **Release verification (virtualenv)** | https://virtualenv.pypa.io/en/latest/how-to/verify-release.html | `gh release verify`, `gh release verify-asset`, PEP 740 attestation verification. D5. |
| 12 | **Hermetic pytest conftest pattern** | https://github.com/anthony-chaudhary/dos-kernel/blob/master/tests/conftest.py | session autouse chdir to tmp; env home override; write tracker + before/after `git status` guard. D6. |
| 13 | **gh release create docs** | https://cli.github.com/manual/gh_release_create | annotated tags, `--verify-tag`, `--notes-from-tag`, immutable release behavior. Phase 2. |

### Fast re-hydration (post-compaction)
```bash
cd /home/xnai/Documents/Projects/omega-engine
git fetch debut main -q
echo "public: $(git log --oneline -1 debut/main)"
echo "release: $(timeout 20 gh release view v1.6.0a9 --repo Xoe-NovAi/omega-engine --json tagName 2>&1 | head -2)"
for f in check_release_changelog.py check_version_consistency.py check_wheel_contents.py \
         verify_artifact_clean_env.py check_doc_facts.py check_workflow_trigger_coverage.py validate_wad.py; do
  git cat-file -e "debut/main:scripts/$f" 2>/dev/null && echo "PRESENT $f" || echo "MISSING $f"
done
diff -q PUBLIC_ALLOWLIST.txt docs/strategy/PUBLIC_ALLOWLIST.txt
```

---

## 9. Deferred (Out of Scope)

- PyPI publication and trusted publisher registration (awaiting approval).
- Reproducible-build verification (`SOURCE_DATE_EPOCH`, pinned build backend) — research available
  in source #11/#12 above but not required for the first repair.
- Full branch protection / CODEOWNERS enforcement on `.github/` (organizational change).

---

*⬡ OMEGA ⬡ MAKALI ⬡ RELEASE-HARDENING-PLAN ⬡ 2026-11-23 ⬡*
