# AP: AP-PR-READINESS-v1.0.0
# ── Antigravity Configuration ──
# [Mandate 16: Modularization & Portability] — all paths configurable, no hardcoded defaults.
# Reads from environment variables or explicit constructor args.

"""Configurable paths for the Antigravity module.

All paths are resolved at call-time (D-kal-152), never frozen at module import.
Environment variables override constructor args. Constructor args override defaults.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# Environment variable names
_ENV_ACCOUNTS_PATH = "ANTIGRAVITY_ACCOUNTS_PATH"
_ENV_CLIENT_ID = "ANTIGRAVITY_CLIENT_ID"
_ENV_CLIENT_SECRET = "ANTIGRAVITY_CLIENT_SECRET"
_ENV_BASE_URL = "ANTIGRAVITY_BASE_URL"

# OAuth client credentials (public — embedded in plugin binary)
_DEFAULT_CLIENT_ID = "1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com"
_DEFAULT_CLIENT_SECRET = "***REMOVED***"
_DEFAULT_BASE_URL = "https://cloudcode-pa.googleapis.com"


@dataclass
class AntigravityConfig:
    """Configuration for the Antigravity module.

    All fields are overridable via environment variables or constructor args.
    Paths are resolved at call-time (Mandate 16: portability).

    Attributes:
        accounts_path: Path to antigravity-accounts.json.
        client_id: OAuth client ID for token refresh.
        client_secret: OAuth client secret for token refresh.
        base_url: Base URL for the Antigravity API.
    """

    accounts_path: Path = field(default_factory=lambda: Path("~/.config/opencode/antigravity-accounts.json").expanduser())
    client_id: str = ""
    client_secret: str = ""
    base_url: str = _DEFAULT_BASE_URL

    def __post_init__(self) -> None:
        """Resolve environment variable overrides."""
        env_path = os.environ.get(_ENV_ACCOUNTS_PATH)
        if env_path:
            self.accounts_path = Path(env_path)

        env_client_id = os.environ.get(_ENV_CLIENT_ID)
        if env_client_id:
            self.client_id = env_client_id
        elif not self.client_id:
            self.client_id = _DEFAULT_CLIENT_ID

        env_client_secret = os.environ.get(_ENV_CLIENT_SECRET)
        if env_client_secret:
            self.client_secret = env_client_secret
        elif not self.client_secret:
            self.client_secret = _DEFAULT_CLIENT_SECRET

        env_base_url = os.environ.get(_ENV_BASE_URL)
        if env_base_url:
            self.base_url = env_base_url

    @classmethod
    def from_env(cls) -> "AntigravityConfig":
        """Create config from environment variables only."""
        return cls()

    @classmethod
    def with_accounts_path(cls, path: str | Path) -> "AntigravityConfig":
        """Create config with explicit accounts path."""
        return cls(accounts_path=Path(path))
