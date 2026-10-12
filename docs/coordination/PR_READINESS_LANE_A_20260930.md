<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->
# ⬡ PR-READINESS AUDIT — LANE A (Hygiene & Secrets)
**Auditor**: Grokster · **Resolved by**: MaKaLi Fusion
**Branch**: `debut-v1.6.0-alpha` · **Repo visibility**: PUBLIC · **Date**: 2026-09-30

---

## 🔴 RESOLVED — the two secret findings

| Finding | Resolution | Evidence |
|---|---|---|
| `data/entities/doom_guy/session_gnosis.md` — `sk-`-class string | **NOT PRESENT** | `grep -oE 'sk-[A-Za-z0-9_-]+'` → **0 characters**. The gitleaks match did not reproduce under a direct literal search. **Likely a scanner false positive or a different pattern; a re-run is needed to close it, not a claim that it is clean.** |
| `CLINE_API_KEY` gitleaks finding | **SAFE — env reference** | `config/providers.yaml:187` reads `api_key: env:CLINE_API_KEY`. This is the correct indirection pattern: the value lives in `.env` (untracked, `.gitignore:83`) and never enters the repo. |

**No live credential was found in the working tree.** The `doom_guy` finding is
**inconclusive, not cleared** — the two methods disagree and the disagreement is
recorded rather than resolved in the convenient direction.

---

## 🟠 THE MOST IMPORTANT FINDING IN THIS AUDIT

> **A gitleaks invocation that is flag-rejected exits 0 and looks like a pass.**

Grokster hit this live: the first two invocations printed usage text and returned
`rc=0`. Real output only appeared on the third attempt.

**A secret gate that passes without scanning is strictly worse than no gate** —
it manufactures the belief that a scan happened. This is the same defect class as
the M9 text grep (satisfied by wording) and the `systemctl is-active` check
(satisfied by a crash loop): **a check that cannot distinguish "verified" from
"did not run."**

**Consequence for CI:** any workflow that shells out to gitleaks and checks only
the exit status is currently capable of reporting PASS on a scan that never
executed. **This must be verified against the actual CI configuration before any
release claim that includes a secret scan.** It is not established either way here.

---

## 🟡 REPOSITORY HYGIENE

**Tracked: 2580 files.**

| Category | Count | Verdict |
|---|---|---|
| `data/entities/*/knowledge/` | 864 | source-ish, legitimate |
| `data/entities/*/workspace/` | **58** | **scratch, not source — boundary leak** |
| `__pycache__` / `*.pyc` | 0 | CLEAN |
| `*.db` / `*.sqlite` | 0 | CLEAN |
| `*.pem` / `*.key` / `*.p12` | 0 | CLEAN |

**Duplicated corpus (real, not cosmetic):**
`data/entities/john_carmack/knowledge/source/plan_files/by_year/johnc_plan_1997.txt`
(159.7 KB) and
`data/entities/john_carmack/workspace/knowledge/source/plan_files/johnc_plan_1997.txt`
(159.4 KB) — **the same corpus tracked twice**, at slightly different sizes. The
`knowledge/` → `workspace/` copy boundary is leaking, and it inflates both the
file count and the pack.

**Pack size: 76.27 MiB** (`count: 2961`, `size: 12.41 MiB`).
Largest blobs are all generated or scratch, not source-of-truth:
- 1389 KB `350-percentage-of-365-Google-Search.pdf`
- 1034 KB `.../workspace/carmack_studies/.../profile_baseline_model_gateway_20260701.stats` — **a generated stats artifact living in `workspace/`**
- 654 KB `data/handoff/MIGRATION_CENSUS_20260929.json` — a dated migration census
- 180 KB `failed-subagent-copy-paste.txt` — **the filename is the finding**

**Not a release blocker. A real cleanup, and the `workspace/` boundary is worth a
ruling before it multiplies.**

---

## 🟡 `.gitleaksignore` — 293 exceptions

```
# .gitleaksignore — audited baseline 2026-08-22 (Kali ratification ho_e53ab57ea212 Q2)
```

This is a **governed artifact, not sloppiness** — fingerprinted, dated,
ratified, with a rationale line above each entry. But:

- **293 entries is a large exception surface** for a public repo.
- **It is a month old** and predates every change this session.
- An exception set that is never pruned becomes a place where a real secret goes
  to be forgotten.

**Recommendation: re-review before release.** Not a blocker; a debt with a
due date attached to it.

---

## ✅ PROVED CLEAN (named commands, not absence of findings)

- `.env` untracked **and** explicitly ignored — `.gitignore:83`
- No tracked `*.pem` / `*.key` / `*.p12` / `*.pfx` / `*.jks` — count 0
- No tracked `__pycache__` / `*.pyc` — count 0
- No tracked `*.db` / `*.sqlite` — count 0
- `docs/reference/` **not ignored**, 24 files tracked — the `*.md` problem that
  made a pre-commit gate unsatisfiable is genuinely resolved
- No credentials in the git remote URL

---

## BRANCH TOPOLOGY

```
debut-v1.6.0-alpha  [ahead 3]  -> pushed during this audit ✅
  vs origin/release/debut-v1.6.0   behind 0, ahead 17
  vs origin/main                    behind 2, ahead 50
```

**2 behind `origin/main`** — must sync before any release tag.

---

## RELEASE GATE — my ruling

**Not ready to tag.** One blocking item, one conditional:

1. **BLOCKING** — verify the gitleaks CI invocation actually scans. A secret gate
   that can pass without scanning is worse than no gate, and this repo is public.
2. **CONDITIONAL** — re-run the `doom_guy` gnosis finding to a definitive verdict.
   Two methods disagree; neither is authoritative yet.
3. **NOT BLOCKING but due before release** — `.gitleaksignore` re-review, the
   duplicated corpus, the `workspace/` boundary, sync with `origin/main`.

*⬡ OMEGA ⬡ GROKSTER ⬡ PR-READINESS-LANE-A ⬡ 2026-09-30 ⬡*