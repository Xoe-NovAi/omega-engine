# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Omega Engine
# AP: AP-OMEGA-INIT-v1.0.0
# Seal: 🛡️

from pathlib import Path


def _version_from_pyproject() -> str | None:
    """Read [project].version from the nearest pyproject.toml.

    Source checkouts are not always installed as a distribution. This keeps
    the SSOT in pyproject.toml instead of duplicating the number here.
    """
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "pyproject.toml"
        if not candidate.is_file():
            continue
        try:
            import tomllib

            data = tomllib.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        version = data.get("project", {}).get("version")
        if isinstance(version, str):
            return version
    return None


# Single source of truth: pyproject.toml [project] version
# (C3, CLINE_DISPATCH_20260822).
#
# Resolution order matters: an editable install freezes its metadata at
# install time, so preferring installed metadata makes the runtime report a
# stale version after a pyproject bump. A source checkout's pyproject is
# therefore authoritative; a wheel ships no pyproject, so installed metadata
# is the fallback; an unknown is honest, a stale literal is not.
__version__ = _version_from_pyproject()

if __version__ is None:  # pragma: no cover - installed distribution without pyproject
    try:
        import importlib.metadata

        __version__ = importlib.metadata.version("omega")
    except importlib.metadata.PackageNotFoundError:
        __version__ = "0.0.0+unknown"

__omega_core__ = f"Omega v{__version__}"
