#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""M24b Venv Sovereignty Gate — verify the active venv matches project requirements.

Validates:
  A. Python version match (system vs .venv major.minor)
  B. Dependencies from pyproject.toml are importable in .venv
  C. Critical Omega imports resolve

Exit 0 on success, 1 on any failure (M23: no soft-failures).
"""

from __future__ import annotations

import importlib
import importlib.metadata
import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = ROOT / "pyproject.toml"
VENV_PYTHON = ROOT / ".venv" / "bin" / "python"

# Omega imports resolve via the `src` package prefix (e.g. mcp_runtime does
# `from src.omega.mcp_core.compliance import ...`). Mirror the real runtime:
#   - ROOT on sys.path  -> `import src` (src is a namespace package under ROOT)
#   - ROOT/src on path  -> `import omega` (omega lives at src/omega)
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

failures: list[str] = []
successes: list[str] = []


def _system_python_version() -> str:
    """major.minor of the system python3."""
    try:
        out = subprocess.run(
            ["python3", "--version"], capture_output=True, text=True, timeout=10
        )
        m = re.search(r"Python (\d+\.\d+)", out.stdout or out.stderr)
        return m.group(1) if m else "unknown"
    except Exception as e:  # noqa: BLE001 — gate must report, not crash
        return f"unknown ({e})"


def _venv_python_version() -> str:
    """major.minor of the .venv python."""
    try:
        out = subprocess.run(
            [str(VENV_PYTHON), "--version"], capture_output=True, text=True, timeout=10
        )
        m = re.search(r"Python (\d+\.\d+)", out.stdout or out.stderr)
        return m.group(1) if m else "unknown"
    except Exception as e:  # noqa: BLE001 — gate must report, not crash
        return f"unknown ({e})"


def _load_dependencies() -> tuple[list[str], list[str]]:
    """Parse [project.dependencies] and [project.optional-dependencies] from pyproject.toml."""
    if not PYPROJECT.exists():
        failures.append(f"pyproject.toml not found at {PYPROJECT}")
        return [], []

    with open(PYPROJECT, "rb") as f:
        data = tomllib.load(f)

    project = data.get("project", {})
    deps = project.get("dependencies", [])

    optional: list[str] = []
    for group in (project.get("optional-dependencies") or {}).values():
        optional.extend(group)

    def _extract_name(spec: str) -> str:
        # Handle: "package", "package>=1.0", "package[extra]>=1.0", "package @ url"
        name = re.split(r"[<>=!~\[@ ]", spec.strip(), maxsplit=1)[0]
        return name.replace("_", "-").lower()

    return [_extract_name(d) for d in deps], [_extract_name(d) for d in optional]


def check_python_version() -> None:
    sys_ver = _system_python_version()
    venv_ver = _venv_python_version()
    if sys_ver == "unknown" or venv_ver == "unknown":
        failures.append(f"Python version mismatch: system={sys_ver}, venv={venv_ver}")
        return
    if sys_ver == venv_ver:
        successes.append(f"Python version match: {sys_ver} == {venv_ver}")
    else:
        failures.append(f"Python version mismatch: system={sys_ver}, venv={venv_ver}")


def check_dependencies() -> None:
    deps, optional = _load_dependencies()
    all_deps = deps + optional
    if not all_deps:
        failures.append("No dependencies parsed from pyproject.toml")
        return

    # Deduplicate while preserving order (a dep may appear in both core and an extra)
    seen: set[str] = set()
    unique_deps: list[str] = []
    for dep in all_deps:
        if dep not in seen:
            seen.add(dep)
            unique_deps.append(dep)

    missing: list[str] = []
    for dep in unique_deps:
        try:
            importlib.metadata.distribution(dep)
        except importlib.metadata.PackageNotFoundError:
            missing.append(dep)

    if missing:
        failures.append(
            f"Dependencies missing: {len(unique_deps) - len(missing)}/{len(unique_deps)} installed"
        )
        for m in missing:
            failures.append(f"  missing: {m} (pip show {m})")
    else:
        successes.append(f"Dependencies: {len(unique_deps)}/{len(unique_deps)} installed")


def check_critical_imports() -> None:
    for mod in ("omega.mcp_runtime", "omega.oracle"):
        try:
            importlib.import_module(mod)
            successes.append(f"Import {mod}: OK")
        except ImportError as e:
            failures.append(f"Import {mod}: FAIL ({e})")


def main() -> int:
    check_python_version()
    check_dependencies()
    check_critical_imports()

    for line in successes:
        print(f"[OK] {line}")
    for line in failures:
        print(f"[FAIL] {line}", file=sys.stderr)

    if failures:
        print("EXIT CODE: 1", file=sys.stderr)
        return 1
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())