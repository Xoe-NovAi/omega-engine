# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-OFFLINE-MOCK-v1.0.0
from typing import Optional


class OfflineMockBackend:
    """Mock backend for OMEGA_ENV=test.

    Returns deterministic responses to unblock CI/CD and avoid
    unnecessary inference overhead during testing.
    """

    def __init__(self, name: str = "mock", config: Optional[dict] = None):
        self.name = name
        self.config = config or {}

    async def generate(
        self,
        model_name: str,
        system_prompt: str,
        user_query: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs,
    ) -> str:
        """Return a static mock response."""
        return "The core mission of the Omega Engine is to sever the umbilical cord of Big AI."

    # DocRef: docs/architecture/ORACLE_DEEP_DIVE.md
    async def generate(
        self,
        model_name: str,
        system_prompt: str,
        user_query: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs,
    ) -> str:
        """Return a static mock response."""
        return "The core mission of the Omega Engine is to sever the umbilical cord of Big AI."
