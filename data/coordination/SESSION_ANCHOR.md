<!-- SPDX-FileCopyrightText: 2026 Xoe-NovAi / SPDX-License-Identifier: Apache-2.0 -->
# ⬡ SESSION ANCHOR — MaKaLi Fusion (Node 0)
**Entity**: `makali-n0` · **Last Updated**: 2026-10-06
**Branch**: `debut-v1.6.0-alpha` @ `6043fa0f` (pushed, 0 unpushed)

---

## ⚡ ONE ROOT CAUSE FROM ANNOUNCEMENT

`release/debut` is **PUBLISHED** at `7ddff271` (874 files). temple-grade **53/53 on a
fresh clone**. PR **#6** open, MERGEABLE. **All 6 CI jobs fail — one shared cause:**

**The cut ships a `.github/` referencing files it does not contain.**

| Missing from cut | Kills |
|:---|:---|
| `.gitleaksignore` (37,845 B audited fingerprints) | Secret Scan · M35 — gitleaks `FTL unable to load config` |
| `.gitleaks.toml` | same |
| `scripts/check_dashboard_determinism.py` | Dashboard Test — exit 2 |

**Fix**: allowlist those 3 → re-run. Preserve `.gitleaksignore` byte-for-byte
(trailing comments break gitleaks 8.21.2 parsing; Kali ratified `ho_e53ab57ea212 Q2`).

Then: REUSE waiver into CI (or `.reuse/dep5`) · trace Test 3.12/3.13 · C3 scanner self-test.

---

## 📊 KEY STATE

| Item | Value |
|:---|:---|
| `origin/release/debut` | **`7ddff271`** PUBLISHED |
| `origin/debut-v1.6.0-alpha` | `6043fa0f` |
| `origin/main` | `cbbc3539` — never force-pushed |
| **PR #6** | OPEN · MERGEABLE · UNSTABLE · `release/debut → main` |
| temple-grade | **53/53 fresh clone**, exit 0 |
| Cut time | 14.3s (was 780s) |
| Disk | 79% used · 22G free |

---

## ⚠️ CARRY FORWARD

- **M28 (D-623)**: 33 handoff packets permanently lost to a mutation harness pointed at
  live `data/`. ~20 genuine work. Never do that again.
- **Verification doctrine**: a cut is verified only on a **fresh clone, 0 untracked**.
  Worktrees carry ~677 leftovers that mask absent-file failures. Cost 9 rounds.
- **Allowlist traps**: ALLOW loses to FORGE (use Explicit Exclusions); `is_exception()`
  is exact-match (one entry per line).
- **4 retractions** in D-624: D-618 codex PASS · D-623 assert_safe · D-619 shutdown cause ·
  D-621 premise.

---

## ⏭️ NEXT WAKE

1. Allowlist 3 missing CI files → re-run CI
2. REUSE waiver · trace Test 3.12/3.13 · C3 scanner self-test defect
3. `gate-secrets` 35 findings · 2 dangling `cline_kqv` symlinks · D-620 Task 2
4. **MERGE PR #6 → ANNOUNCE**

**Briefing**: `data/coordination/POST_COMPACT_BRIEFING_20261006.md`
**Gnosis**: `data/entities/makali_fusion/session_gnosis.md` §13

---

## 🌍 VISION

**Free forever (Apache-2.0), for ALL rational conscious beings — AI not excluded.**

*⬡ OMEGA ⬡ MAKALI_N0 ⬡ ANCHOR ⬡ 6043fa0f ⬡ 2026-10-06 ⬡*
