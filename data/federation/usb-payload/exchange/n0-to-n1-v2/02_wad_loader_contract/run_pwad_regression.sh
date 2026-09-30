#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
#
# NOTE: on media that do not persist the executable bit (e.g. FAT/vfat USB), invoke this
# wrapper via `sh <path>` — direct invocation may fail with exit 126 (permission denied).
#
# PWAD negative-regression wrapper.
#
# This wrapper exists because 02_wad_loader_contract/test_pwad_override.py is a
# NEGATIVE REGRESSION FIXTURE that INTENTIONALLY EXITS 1 at sealed checkout
# fa9c4edc while the personality-concatenation bug exists. Raw `python
# test_pwad_override.py` therefore reports a non-zero status on the sealed
# checkout, which is easy to misread as failure. This wrapper translates the
# fixture's intentional exit 1 into shell exit 0 (PASS) so automation and
# operators get an unambiguous signal.
#
# Exit codes: fixture 1 -> wrapper 0 (PASS: bug reproduced, fixture healthy);
#             anything else -> wrapper 1 (FAIL: fixture did not reproduce the sealed-checkout bug).
#
# POSIX-safe: set -u only; deliberately NO `set -e` around the fixture invocation,
# because set -e would abort on the fixture's intentional exit 1 before it could
# be classified.

set -u

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
FIXTURE="$SCRIPT_DIR/test_pwad_override.py"

if [ ! -f "$FIXTURE" ]; then
    echo "PWAD REGRESSION FIXTURE: FAIL (fixture not found: $FIXTURE)"
    exit 1
fi

# Walk up until pyproject.toml marks the Omega Engine checkout (if present).
REPO_ROOT=""
d="$SCRIPT_DIR"
while [ "$d" != "/" ]; do
    if [ -f "$d/pyproject.toml" ]; then
        REPO_ROOT="$d"
        break
    fi
    d=$(dirname -- "$d")
done

PY="${PYTHON:-python3}"
if [ -n "$REPO_ROOT" ] && [ -x "$REPO_ROOT/.venv/bin/python" ]; then
    PY="$REPO_ROOT/.venv/bin/python"
fi
if [ -n "$REPO_ROOT" ] && [ -d "$REPO_ROOT/src" ]; then
    PYTHONPATH="${PYTHONPATH:-}:$REPO_ROOT/src"
    export PYTHONPATH
fi

"$PY" "$FIXTURE"
rc=$?

if [ "$rc" -eq 1 ]; then
    echo "PWAD NEGATIVE REGRESSION FIXTURE: PASS (expected exit 1 — bug reproduced; NOT a compatibility pass)"
    exit 0
fi

echo "PWAD NEGATIVE REGRESSION FIXTURE: FAIL (unexpected exit $rc — expected 1 at sealed checkout fa9c4edc)"
exit 1
