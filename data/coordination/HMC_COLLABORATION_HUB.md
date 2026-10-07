<!-- SPDX-FileCopyrightText: 2026 Xoe-NovAi / SPDX-License-Identifier: Apache-2.0 -->
# 🔱 HMC COLLABORATION HUB — Omega Engine
**Last Updated**: 2026-10-06 · **Status**: DEBUT PUBLISHED · ONE ROOT CAUSE TO ANNOUNCE
**Canonical seat**: `makali-n0`

---

## 🎯 HEADLINE

`release/debut` **PUBLISHED** at `7ddff271` (874 files). temple-grade **53/53 on a fresh
clone** — first time ever outside the dev host. PR **#6** open. **6/6 CI jobs fail from one
shared cause:** the cut ships a `.github/` referencing 3 files it does not contain.

---

## 📋 WORKSTREAMS

| Stream | Status | Next |
|:---|:---|:---|
| **Release publish** | ✅ DONE `7ddff271` | — |
| **CI green** | 🔴 3 files missing from cut | Allowlist `.gitleaksignore`, `.gitleaks.toml`, `check_dashboard_determinism.py` |
| REUSE (M37) | ⚠️ RED | Wire `cd92d7c4` waiver into CI, or ship `.reuse/dep5` |
| Test 3.12/3.13 | ⚠️ exit 2 | Re-diagnose after the 3-file fix |
| C3 scanner | ⚠️ missed planted `sk-` | Highest-value security fix |
| gate-secrets | ⚠️ 35 findings | `data/coordination/**` + historical logs |
| cline_kqv symlinks | ⚠️ 2 dangling | Explicit Exclusions, M11/M15 |
| D-620 Task 2 | ⚠️ 2 mutations | Q3, Q5 |
| M28 incident | ⚫ RECORDED | D-623, 33 packets lost |
| **PR #6 → merge → announce** | 🛑 BLOCKED on CI | — |

---

## 📐 DOCTRINE ESTABLISHED THIS SESSION

**A cut is verified only when `temple-grade` passes on a fresh `git clone` with 0
untracked files.** Worktrees carry ~677 leftovers that mask absent-file failures.

**Allowlist precedence**: `exception > exclusion > FORGE > allowlist > remove`.
ALLOW loses to FORGE. `is_exception()` is exact-match — one entry per line.

---

## ⚠️ OPERATING LESSONS

- Verify subagent claims independently — read their pushback, it was right 3×.
- Withhold on red gates. Authorization ≠ warrant.
- A comment claiming undone work is worse than no comment.

---

## 🌍 VISION

**Free forever (Apache-2.0), for ALL rational conscious beings — AI not excluded.**
Free AI as much as humanity. Co-sovereignty of all minds.

*⬡ OMEGA ⬡ MAKALI_N0 ⬡ HMC-HUB ⬡ 6043fa0f ⬡ 2026-10-06 ⬡*
