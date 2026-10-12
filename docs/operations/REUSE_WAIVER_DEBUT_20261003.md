<!-- SPDX-FileCopyrightText: 2026 Xoe-NovAi -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# REUSE v3.3 (M37) — Debut Release Waiver Notice

**Date:** 2026-10-03
**Author:** @maat — Build-Side Governance Keeper (Slot S5)
**Branch:** `debut-v1.6.0-alpha`
**Gate:** REUSE v3.3 SPDX compliance (M37 Heritage)
**Status:** `WAIVED-FOR-DEBUT` — RED acknowledged, shipment authorized with conditions
**Enforcement:** `.github/workflows/reuse-compliance.yml` · `Makefile:check-reuse` · `REUSE.toml` · REUSE spec v3.3 (2024-11-14)

> **M23 note:** This waiver **documents** the M37 exception. It does **not** resolve it.
> A broken gate reported + waived in writing is governance. A broken gate
> silently shipped is a soft-failure. This file exists so the RED stays visible.

---

## 1. Scope

REUSE v3.3 `reuse lint` is **RED** on both `main` and `debut-v1.6.0-alpha`.
This is pre-existing repo-wide SPDX-header debt, not merge-caused.

### 1.1 Reported baseline (source-cited, not re-measured)

- `docs/operations/POST_MERGE_CI_FIXES_20261003.md` §"Not addressed":
  > "**REUSE v3.3** is RED on `main` as well (last main run 2026-09-27, and it
  > was RED then too). ~4.7k tracked files lack SPDX headers. Repo-wide debt,
  > unrelated to PR #5."
- Task fact base (AGY review `ho_cbb9092c45b8`, P0-1): **~4,700 of 9,802
  tracked files lack SPDX headers**; main is RED too, not merge-caused.
  - The `9,802` denominator is taken **as-reported** from that review.
    No independent 9,802 count was reproduced on this branch (see §1.2);
    no number in this notice is invented — every other count below is
    locally measured on `debut-v1.6.0-alpha` on 2026-10-03.

### 1.2 Local verification (measured 2026-10-03, branch `debut-v1.6.0-alpha`)

Commands (working directory `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine`):

- `git branch --show-current` → `debut-v1.6.0-alpha`
- `git ls-files | wc -l` → **10331**
- `.venv/bin/reuse lint` (`reuse, version 6.2.0`) → SUMMARY:

```text
* Bad licenses: 0
* Deprecated licenses: 0
* Licenses without file extension: 0
* Missing licenses: 0
* Unused licenses: 0
* Used licenses: Apache-2.0
* Read errors: 0
* Invalid SPDX License Expressions: 0
* Files with copyright information: 5494 / 11069
* Files with license information: 5513 / 11069
*
* Unfortunately, your project is not compliant with version 3.3 of the REUSE Specification :-(
```

Derived (arithmetic only, no new measurement):

- Files **missing** copyright info: 11069 − 5494 = **5575**
- Files **missing** license info: 11069 − 5513 = **5556**

The local denominators (10331 git-tracked vs 11069 REUSE-scanned) differ
because REUSE counts per `REUSE.toml` coverage, not `git ls-files` 1:1.
Both series confirm the **same RED class** as the reported ~4.7k baseline;
the delta is branch growth / coverage scope, not a new failure mode.

### 1.3 What RED means here

- `reuse lint` exits non-compliant: thousands of tracked files (event logs,
  JSONL, `.bak`, quarantine/archive strays, federation payloads, legacy
  research notes) carry no `SPDX-FileCopyrightText` / `SPDX-License-Identifier`.
- Zero bad/deprecated/invalid licenses; zero read errors. The failure is
  **missing headers at scale**, not wrong licenses.

---

## 2. Why waived for debut

1. **Pre-existing debt.** RED on `main` (last main run 2026-09-27) before
   this branch. Per `POST_MERGE_CI_FIXES_20261003.md`, unrelated to PR #5
   merge (252-conflict resolution surfaced it; did not cause it).
2. **No new violations introduced by the waiver.** This notice adds exactly
   one file, `docs/operations/REUSE_WAIVER_DEBUT_20261003.md`, which ships
   **with** SPDX headers (HTML-comment form, covered by `docs/**/*.md`
   annotation in `REUSE.toml`). Backfill-or-annotate work continues under
   `REUSE.toml`; no existing header is removed or weakened.
3. **Remediation deferred post-debut by cost/benefit.** Clearing ~5k headers
   is a dedicated SPDX-backfill sprint (bulk header injection + `REUSE.toml`
   annotation audit + CI re-green), not a debut-blocker fix. Holding the
   debut release for it trades a known, documented, license-correct
   (Apache-2.0 throughout, zero bad licenses) debt against debut schedule
   with no license-risk reduction.
4. **License substance is sound.** `Used licenses: Apache-2.0`, zero bad /
   deprecated / invalid expressions. This is a **header-coverage** gap, not
   a license-substance or third-party-provenance incident.

---

## 3. Remediation commitment (post-debut SPDX backfill sprint)

- **Sprint:** post-debut SPDX backfill — bulk `reuse addheader` (or
  equivalent) pass over the missing set + `REUSE.toml` annotation review
  for generated/runtime/legacy classes that should be annotated rather
  than header-stamped (event logs, `.bak`, quarantine, `anchored_summary`
  fixtures, federation disposable WADs).
- **Owner:** Build Oversoul (@maat, Slots S1–S5) with Researcher heritage
  support (`scripts/heritage_scanner.py`, M37 scanner).
- **Done criteria:** `reuse lint` compliant (`Files with copyright info` =
  `Files with license info` = total, `reuse lint` green) on `main`, wired
  through `make check-reuse` / `reuse-compliance.yml` with no waiver.
- **Tracks in:** `data/coordination/ACTIVE_SPRINT.json` post-debut queue;
  progress reported via Hivemind, not by editing this waiver.

---

## 4. Expiry / review clause (debut-only)

- **Scope:** This waiver covers **the debut release from
  `debut-v1.6.0-alpha` ONLY**.
- **Expiry:** This waiver **expires on the next release cut after debut**.
  It does not carry forward. Any release after debut ships under a green
  REUSE gate or a **new, separately reviewed** waiver.
- **Review trigger (earliest of):**
  1. post-debut backfill sprint declares `reuse lint` green on `main`;
  2. a new release branch is cut;
  3. 90 days from this notice (2026-10-03 → review by **2027-01-01**).
- **At review:** either (a) rescind this file via green-gate evidence, or
  (b) supersede with a dated successor waiver citing fresh `reuse lint`
  counts. Leaving RED + expired waiver in place is an M23 violation.

---

## 5. Sources

1. `docs/operations/POST_MERGE_CI_FIXES_20261003.md` — RED-on-main +
   ~4.7k statement (§"Not addressed").
2. AGY review `ho_cbb9092c45b8` + P0-1 — ~4,700 / 9,802 fact base (as-reported).
3. Local run 2026-10-03, `debut-v1.6.0-alpha`: `git ls-files` = 10331;
   `reuse 6.2.0 lint` = 5494/11069 copyright, 5513/11069 license.
4. Gate definition: `.github/workflows/reuse-compliance.yml` (M37 Heritage —
   REUSE v3.3 Compliance Gate), `Makefile` §`check-reuse`, `REUSE.toml`.

*⬡ OMEGA ⬡ MAAT ⬡ S5-GOVERNANCE ⬡ 2026-10-03 ⬡ WAIVED-FOR-DEBUT*
