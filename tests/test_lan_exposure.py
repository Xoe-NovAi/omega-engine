# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
# ⬡ OMEGA ⬡ MAAT ⬡ TEST ⬡ v1.0.0
"""Suite-visible wrapper for the LAN exposure gate's negative tests.

WHY THIS FILE EXISTS
--------------------
`scripts/test_lan_exposure_audit.py` holds 22 hand-rolled negative assertions
that pin `lan_exposure_audit.classify()`. They were only ever run by
`make check-lan-exposure`, which invokes the script directly:

    $(PYTHON) scripts/test_lan_exposure_audit.py

Because the file lives in `scripts/`, which is outside `testpaths = ["tests"]`,
pytest collected **0 tests** from it. So:

  * `pytest tests/` never exercised any of the 22 assertions;
  * they appeared in no junit-xml, no json-report, and no coverage;
  * a green suite said nothing whatsoever about LAN exposure.

The gate itself was honest — it self-reports 22/22 and was observed red on live
hardware. It was simply invisible to the suite.

WHAT THIS DOES
--------------
Parametrises over the SAME `CASES` table the script uses. No case is duplicated
and no logic is reimplemented: the script remains the single source of truth, and
`make check-lan-exposure` still runs it. This module only makes the existing
assertions visible to a plain `pytest tests/`.

The cases are synthetic — they construct a `Listener` and assert the verdict. No
socket is opened and no host state is touched, so this is safe in any parallel
or serial run.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def _load(name: str):
    """Import a script by path. These are not an installed package."""
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS / f"{name}.py")
    assert spec and spec.loader, f"could not load {name}"
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# The audit module does `sys.path.insert` of its own directory at import time.
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

lan_audit = _load("lan_exposure_audit")
lan_cases = _load("test_lan_exposure_audit")

CASES = lan_cases.CASES
ALLOW = lan_cases.ALLOW


def test_case_table_is_not_empty():
    """M23: refuse to "pass" on an empty table.

    A parametrised set over an empty CASES list collects zero tests and the
    suite reports success. That is the same no-op gate this file exists to
    prevent, one level up.
    """
    assert len(CASES) >= 20, (
        f"LAN negative-case table has only {len(CASES)} cases — expected the "
        "full set. An empty/short table would collect nothing and pass vacuously."
    )


@pytest.mark.parametrize(
    "name,listener,expect_clean",
    CASES,
    ids=[c[0] for c in CASES],
)
def test_lan_classification(name, listener, expect_clean):
    """Each negative case: `classify()` must return the expected verdict."""
    verdict = lan_audit.classify(listener, ALLOW)
    is_clean = verdict is None
    assert is_clean == expect_clean, (
        f"{name}: expected {'clean' if expect_clean else 'FLAGGED'}, "
        f"got {'clean' if is_clean else f'flagged({verdict[0]})'}"
    )
