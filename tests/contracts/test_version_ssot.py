# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Contract tests: pyproject.toml is the single source of truth for the version.

Before this contract, four surfaces disagreed:
- pyproject.toml          1.2.0
- omega.__version__       1.2.0  (hardcoded fallback literal)
- Hub /health             2.2.0  (hardcoded)
- MCP serverInfo          1.30.0 (the *mcp SDK* version leaking as the engine's)

A release that advertises four versions cannot be supported. These tests pin
one resolution path and forbid second copies of the number.
"""

import re
import tomllib
from pathlib import Path

import pytest

import omega
import mcp_servers.omega_hub.server as hub_server

REPO_ROOT = Path(__file__).resolve().parents[2]


def _pyproject_version() -> str:
    data = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return data["project"]["version"]


def test_pyproject_declares_a_valid_version():
    version = _pyproject_version()
    assert re.fullmatch(r"\d+\.\d+\.\d+([.-]?(a|b|rc|alpha|beta)\.?\d*)?", version), (
        f"pyproject version {version!r} is not a recognisable release version"
    )


def test_package_reports_the_pyproject_version():
    """Runtime __version__ must equal the SSOT, not an install-time snapshot."""
    assert omega.__version__ == _pyproject_version()


def test_version_from_pyproject_finds_the_repo_root():
    assert omega._version_from_pyproject() == _pyproject_version()


def test_hub_health_reports_the_engine_version():
    """The /health payload must not carry its own hardcoded version."""
    assert hub_server._ENGINE_VERSION == _pyproject_version()
    assert hub_server._ENGINE_VERSION == omega.__version__


def test_mcp_serverinfo_reports_the_engine_version():
    """serverInfo must not leak the mcp SDK version.

    FastMCP has no `version` kwarg, so an unset field makes the SDK report
    its own library version — clients then see "1.30.0" for the engine.
    """
    import importlib.metadata

    mcp_sdk_version = importlib.metadata.version("mcp")
    assert hub_server.mcp._mcp_server.version == _pyproject_version()
    assert hub_server.mcp._mcp_server.version != mcp_sdk_version or (
        _pyproject_version() == mcp_sdk_version
    )


@pytest.mark.parametrize(
    "path",
    [
        REPO_ROOT / "mcp_servers" / "omega_hub" / "server.py",
        REPO_ROOT / "src" / "omega" / "__init__.py",
    ],
)
def test_no_second_copy_of_the_version_literal(path):
    """No hardcoded version literal may survive in the version surfaces."""
    source = path.read_text(encoding="utf-8")
    offenders = [
        match
        for match in re.findall(r'"version"\s*:\s*"([0-9]+\.[0-9]+\.[0-9]+)"', source)
    ]
    offenders += re.findall(r'__version__\s*=\s*"([0-9]+\.[0-9]+\.[0-9]+)"', source)
    assert not offenders, (
        f"{path.name} hardcodes a version literal {offenders}; "
        "pyproject.toml is the SSOT"
    )
