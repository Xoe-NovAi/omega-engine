# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Omega Engine
# AP: AP-OMEGA-INIT-v1.0.0
# Seal: 🛡️

# Single source of truth: pyproject.toml [project] version (C3, CLINE_DISPATCH_20260822)
try:
    import importlib.metadata
    from importlib.metadata import PackageNotFoundError

    __version__ = importlib.metadata.version("omega")
except PackageNotFoundError:  # pragma: no cover - not installed as distribution
    __version__ = "1.2.0"

__omega_core__ = f"Omega v{__version__}"
