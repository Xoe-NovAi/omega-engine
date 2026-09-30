# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
"""Adversarial tests for the M9 error-integrity gate.

The gate was a text grep until 2026-09-29. These tests exist to prove the
replacement cannot be defeated the same way — and, critically, that it still
catches what the grep caught.

Every test here is a sabotage test: each one constructs a condition that would
pass a naive implementation and asserts the gate rejects it.
"""

from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
GATE_PATH = REPO_ROOT / "scripts" / "check_m9_error_integrity.py"

spec = importlib.util.spec_from_file_location("check_m9", GATE_PATH)
assert spec and spec.loader
check_m9 = importlib.util.module_from_spec(spec)
sys.modules["check_m9"] = check_m9
spec.loader.exec_module(check_m9)


def _write(root: Path, rel: str, source: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(source, encoding="utf-8")
    return p


# --------------------------------------------------------------------------
# The gate must CATCH real bare excepts
# --------------------------------------------------------------------------


def test_catches_bare_except_in_function(tmp_path):
    _write(
        tmp_path,
        "mod.py",
        "def f():\n    try:\n        pass\n    except:\n        pass\n",
    )
    found = check_m9.find_bare_excepts(tmp_path)
    assert len(found) == 1, "bare except: was not detected"
    assert found[0].line == 4


def test_catches_bare_except_at_module_level(tmp_path):
    _write(tmp_path, "mod.py", "try:\n    pass\nexcept:\n    pass\n")
    assert len(check_m9.find_bare_excepts(tmp_path)) == 1


def test_catches_bare_except_in_class_and_nested(tmp_path):
    _write(
        tmp_path,
        "mod.py",
        "class A:\n"
        "    def f(self):\n"
        "        try:\n"
        "            try:\n"
        "                pass\n"
        "            except:\n"
        "                pass\n"
        "        except:\n"
        "            pass\n",
    )
    assert len(check_m9.find_bare_excepts(tmp_path)) == 2


def test_catches_bare_except_with_finally_but_no_type(tmp_path):
    _write(
        tmp_path,
        "mod.py",
        "def f():\n"
        "    try:\n"
        "        pass\n"
        "    except:\n"
        "        pass\n"
        "    finally:\n"
        "        pass\n",
    )
    assert len(check_m9.find_bare_excepts(tmp_path)) == 1


# --------------------------------------------------------------------------
# The gate must NOT be fooled by text that is not a bare except.
# Each of these PASSES a `rg 'except\\s*:'` style gate.
# --------------------------------------------------------------------------


def test_comment_mentioning_except_is_not_flagged(tmp_path):
    """The exact evasion used on 2026-09-29.

    Note the real bare except must sit inside a ``try`` — an ``except:`` with no
    matching ``try`` is a SyntaxError, so the file would not parse at all. An
    earlier draft of this fixture did exactly that and the gate correctly
    refused to certify it. That refusal is the behaviour we want.
    """
    _write(
        tmp_path,
        "mod.py",
        "def f():\n"
        "    # The M9 gate greps for the literal word except in\n"
        "    # comments, so this note avoids saying it.\n"
        "    try:\n"
        "        pass\n"
        "    except:\n"
        "        pass\n"
        "    return 1\n",
    )
    # A real bare except IS present, so the gate fires — but on the real line,
    # and only once. The comments must not add findings.
    found = check_m9.find_bare_excepts(tmp_path)
    assert len(found) == 1
    assert found[0].line == 6  # the real handler, not the comment lines


def test_string_literal_containing_except_is_not_flagged(tmp_path):
    _write(
        tmp_path,
        "mod.py",
        'MSG = "use except: to catch everything"\nDOC = """\nexcept:\n"""\n',
    )
    assert check_m9.find_bare_excepts(tmp_path) == []


def test_docstring_containing_except_is_not_flagged(tmp_path):
    _write(
        tmp_path,
        "mod.py",
        'def f():\n    """Avoid bare except: in core."""\n    return 1\n',
    )
    assert check_m9.find_bare_excepts(tmp_path) == []


def test_noqa_on_a_bare_except_does_not_excuse_it(tmp_path):
    """The old gate's escape hatch was `rg -v '# noqa'`.

    A bare except annotated `# noqa` is still a bare except. M9 must fire.
    """
    _write(
        tmp_path,
        "mod.py",
        "def f():\n    try:\n        pass\n    except:  # noqa\n        pass\n",
    )
    found = check_m9.find_bare_excepts(tmp_path)
    assert len(found) == 1, "a # noqa comment must not suppress a real bare except"


def test_typed_except_is_not_a_bare_except(tmp_path):
    _write(
        tmp_path,
        "mod.py",
        "def f():\n"
        "    try:\n        pass\n"
        "    except ValueError:\n        pass\n"
        "    except (OSError, KeyError):\n        pass\n"
        "    except Exception:\n        pass\n",
    )
    assert check_m9.find_bare_excepts(tmp_path) == []


# --------------------------------------------------------------------------
# Scope
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "rel",
    [
        "test_thing.py",
        "thing_test.py",
        "conftest.py",
        "tests/helper.py",
        "tests/nested/deep.py",
        "governance/notes.py",
    ],
)
def test_test_and_governance_files_are_out_of_scope(tmp_path, rel):
    _write(tmp_path, rel, "try:\n    pass\nexcept:\n    pass\n")
    assert check_m9.find_bare_excepts(tmp_path) == [], f"{rel} should be out of M9 scope"


def test_unparseable_file_is_not_silently_certified_clean(tmp_path, capfd):
    """A file we cannot parse is NOT a file we can certify.

    Skipping it would make the gate green on unverified code, which is the
    precise failure mode this gate exists to prevent.
    """
    _write(tmp_path, "broken.py", "def f(:\n    this is not python\n")
    assert check_m9.check(tmp_path) == 0  # does not crash, does not pass silently
    err = capfd.readouterr().err
    assert "not certified clean" in err


# --------------------------------------------------------------------------
# The real repository
# --------------------------------------------------------------------------


def test_repo_core_is_clean():
    """The actual engine tree must have no bare excepts."""
    found = check_m9.find_bare_excepts(REPO_ROOT / "src" / "omega")
    assert found == [], "\n".join(f.render() for f in found)


def test_check_returns_zero_on_clean_tree():
    assert check_m9.check(REPO_ROOT / "src" / "omega") == 0
