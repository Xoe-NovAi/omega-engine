#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""M23 gate: no workflow may fail *invisibly*.

The `sote.yml` incident (G24/G25) is the reference case. That workflow runs on
`schedule: cron` + `workflow_dispatch` only. It failed on `pip install -r
requirements.txt` — a file this repo has never had — on **every weekly run
since it was created**, and nobody saw it, because nothing that runs on a push
ever executed it. A scheduled-only workflow is a red status light in a room
nobody enters.

This check makes that class of failure impossible to add by accident:

1. Every workflow under `.github/workflows/` must trigger on at least one of
   push / pull_request — i.e. it must run in response to a change.
2. A workflow that is genuinely scheduled-only must be declared in
   SCHEDULED_ONLY_ALLOWLIST below, with the reason it is allowed to be
   invisible, and a reviewer-visible note is emitted for each one so the debt
   stays on the record rather than being rediscovered months later.

It is a *structural* check, not a status check: it cannot tell you a scheduled
run is red today, only that a workflow is capable of being red invisibly.

M23 Failure Integrity: a broken gate reported is governance. A broken gate
nobody can see is the failure mode this file exists to prevent.

AP: AP-WORKFLOW-TRIGGER-COVERAGE-v1.0.0
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

WORKFLOW_DIR = Path(".github/workflows")

# Workflows deliberately restricted to cron / manual dispatch, and why.
# Adding an entry is a deliberate act: if the reason is no longer true, the
# entry must be removed and the workflow given a change-trigger.
SCHEDULED_ONLY_ALLOWLIST: dict[str, str] = {
    "sote.yml": (
        "Weekly SOTE index/digest regeneration. Runs a full pipeline that "
        "pushes generated content; running it on every push would be wrong. "
        "ACCEPTED RISK: can fail invisibly. Mitigation: manual dispatch is "
        "available and its red status is checked before the next release "
        "(see docs/operations/RELEASE_PR_PUBLIC_STANDARDS.md G25)."
    ),
    "codex-refresh.yml": (
        "Daily OMEGA_CODEX.md staleness refresh. Running daily on a cron is the "
        "whole point — the content-hash check has its own cadence and is NOT a "
        "release gate (Makefile:506-512 removed it from temple-grade for "
        "exactly this reason). "
        "ACCEPTED RISK: can fail invisibly. Realised: this workflow had a "
        "missing `fi` in its shell block and failed every day since creation "
        "with nobody seeing it — the direct evidence for this check. Mitigation: "
        "manual dispatch plus a status review before releases."
    ),
}


def _trigger_keys(raw: object) -> set[str]:
    """Return the set of trigger event names for a workflow.

    PyYAML parses the bare key `on:` as boolean True (YAML 1.1), so accept both.
    """
    if not isinstance(raw, dict):
        return set()
    for key in (True, "on", "On", "ON"):
        if key in raw:
            val = raw[key]
            if isinstance(val, list):
                return {str(v) for v in val}
            if isinstance(val, dict):
                return {str(v) for v in val}
            return {str(val)}
    return set()


def main() -> int:
    if not WORKFLOW_DIR.is_dir():
        print(f"FAIL: {WORKFLOW_DIR} not found — run from the repo root")
        return 2

    files = sorted(
        p for p in WORKFLOW_DIR.iterdir()
        if p.suffix in (".yml", ".yaml") and p.is_file()
    )
    if not files:
        print(f"FAIL: no workflow files found under {WORKFLOW_DIR}")
        return 2

    violations: list[tuple[str, set[str]]] = []
    for wf in files:
        try:
            data = yaml.safe_load(wf.read_text(encoding="utf-8"))
        except (yaml.YAMLError, UnicodeDecodeError) as exc:
            print(f"FAIL: {wf.name}: cannot parse ({exc})")
            return 2

        triggers = _trigger_keys(data)
        change_triggers = triggers & {"push", "pull_request", "pull_request_target"}
        if change_triggers:
            continue
        if wf.name in SCHEDULED_ONLY_ALLOWLIST:
            print(f"  [scheduled-only, declared] {wf.name} — triggers: {sorted(triggers) or ['none']}")
            continue
        violations.append((wf.name, triggers))

    for name in sorted(SCHEDULED_ONLY_ALLOWLIST):
        if not (WORKFLOW_DIR / name).exists():
            print(f"  [note] allowlist entry '{name}' no longer exists — remove it")

    if violations:
        print("\nM23 FAIL: workflow(s) that can only fail INVISIBLY (no push/PR trigger):\n")
        for name, triggers in violations:
            shown = ", ".join(sorted(triggers)) if triggers else "NONE"
            print(f"  {name}: triggers = {shown}")
        print(
            "\nA workflow with no push/pull_request trigger never runs when code\n"
            "changes, so a failure in it is invisible until someone remembers to\n"
            "look (the sote.yml requirements.txt failure ran red every Monday for\n"
            "weeks unnoticed).\n\n"
            "Fix: add a push or pull_request trigger, OR declare the workflow in\n"
            f"    {Path(__file__).name}: SCHEDULED_ONLY_ALLOWLIST\n"
            "with the reason it is allowed to be invisible."
        )
        return 1

    print("M23 passed: every workflow is triggered by a change (push/PR) or explicitly declared scheduled-only.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
