# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""CLI import-smoke gate [N1/dc-cli-dead 2026-08-24].

The omega CLI was DEAD on main: a stacked click decorator raised TypeError
at vault import, then a click.Group mounted via typer.add_typer raised
AttributeError lazily inside app(). Neither failure is caught by importing
the module — typer validates registrations LAZILY at invocation time.

This gate exercises the REAL console-script entry point and asserts the
full help tree renders. It runs in the default suite, so any commit that
kills the CLI fails CI within seconds.
"""

import subprocess
import sys

import pytest

from omega.cli.oracle_cli import TYPER_AVAILABLE


def test_omega_console_script_help_renders() -> None:
    """The installed `omega` entry point must render --help with exit 0."""
    result = subprocess.run(
        ["omega", "--help"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        f"omega CLI is broken (exit {result.returncode}).\n"
        f"stdout tail: {result.stdout[-800:]}\nstderr tail: {result.stderr[-800:]}"
    )
    assert "Traceback" not in result.stderr, f"CLI traceback on --help:\n{result.stderr[-1500:]}"
    assert "Usage:" in result.stdout, "help text missing Usage header"


def test_every_cli_module_imports_cleanly() -> None:
    """Each cli module must import without raising (catches decorator-time explosions)."""
    from pathlib import Path

    cli_dir = Path(__file__).resolve().parents[1] / "src" / "omega" / "cli"
    failures = []
    for py in sorted(cli_dir.glob("*.py")):
        mod = f"omega.cli.{py.stem}"
        probe = subprocess.run(
            [sys.executable, "-c", f"import {mod}"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if probe.returncode != 0:
            failures.append(f"{mod}: {probe.stderr[-300:]}")
    assert not failures, "CLI modules failing at import:\n" + "\n".join(failures)


@pytest.mark.skipif(not TYPER_AVAILABLE, reason="typer not installed")
def test_typer_app_builds_click_tree() -> None:
    """typer validates registrations lazily — force the build explicitly.

    This is the assertion that would have caught the click.Group-mounted-
    via-add_typer defect even without subprocess: building the click tree
    raises AttributeError on a bad mount.
    """
    import typer.main

    from omega.cli.oracle_cli import app

    group = typer.main.get_group(app)
    names = {c.name for c in getattr(group, "commands", {}).values()}
    assert "talk" in names, f"talk subcommand missing from built tree: {sorted(names)}"
