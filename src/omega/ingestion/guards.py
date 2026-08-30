# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-INGESTION-GUARDS-v1.0.0
"""
Sovereign Ingestion Guards — Pre-flight probes and budget enforcement.
"""

# DocRef: docs/architecture/SOVEREIGN_DATA_FLOW.md
import logging
import httpx2 as httpx
import anyio
from .ingestion_types import IngestionConfig, SentryFailure

logger = logging.getLogger(__name__)


class SovereignSentry:
    """
    The Sentry performs 'Canary Probes' before a batch ingestion starts.
    If the probe fails, the pipeline is halted immediately to prevent token waste.
    """

    def __init__(self, config: IngestionConfig):
        self.config = config
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    async def probe(self) -> bool:
        """
        Executes a minimal 'Canary Request' to verify provider health.
        Implements a soft-retry for transient 500 errors common in Gemma 4.
        """
        url = f"{self.base_url}/{self.config.model_name}:generateContent"
        payload = {
            "contents": [{"parts": [{"text": "ping"}]}],
            "generationConfig": {"maxOutputTokens": 1},
        }

        max_retries = 3
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=20.0) as client:
                    response = await client.post(
                        url, json=payload, headers={"x-goog-api-key": self.config.api_key}
                    )

                    if response.status_code == 200:
                        logger.info(
                            f"Sentry Probe SUCCESS for {self.config.model_name} on attempt {attempt + 1}"
                        )
                        return True

                    if response.status_code == 403:
                        raise SentryFailure(
                            f"Sentry Probe FAILED: 403 Forbidden (Quota/Auth). {response.text}"
                        )

                    if response.status_code >= 500:
                        logger.warning(
                            f"Sentry Probe transient 500 on attempt {attempt + 1}/{max_retries}. Retrying..."
                        )
                        if attempt == max_retries - 1:
                            raise SentryFailure(
                                f"Sentry Probe FAILED: Persistent 500 Provider Error after {max_retries} attempts."
                            )
                        await anyio.sleep(2 ** (attempt + 1))  # Exponential backoff
                        continue

                    raise SentryFailure(f"Sentry Probe FAILED: HTTP {response.status_code}")

            except httpx.RequestError as e:
                logger.warning(f"Sentry Probe network error on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    raise SentryFailure(f"Sentry Probe FAILED: Network error {str(e)}")
                await anyio.sleep(2 ** (attempt + 1))

        return False


class BudgetGuard:
    """
    The Budget Guard tracks real-time token consumption and enforces a hard USD limit.
    """

    def __init__(self, config: IngestionConfig):
        self.config = config
        self.current_spend = 0.0
        # Simplified pricing for Gemma 4 (approximate)
        self.price_per_1k_tokens = 0.000125

    def check_budget(self, estimated_tokens: int = 0) -> bool:
        """
        Checks if the current spend plus estimated cost of the next call
        is within the max_budget_usd.
        """
        estimated_cost = (estimated_tokens / 1000.0) * self.price_per_1k_tokens
        if self.current_spend + estimated_cost > self.config.max_budget_usd:
            return False
        return True

    def update_spend(self, tokens: int):
        """Updates the total spend based on actual token usage."""
        self.current_spend += (tokens / 1000.0) * self.price_per_1k_tokens
        logger.info(
            f"Budget Update: Current spend ${self.current_spend:.4f} / ${self.config.max_budget_usd:.2f}"
        )

    def get_status(self) -> str:
        return f"Budget: ${self.current_spend:.4f} / ${self.config.max_budget_usd:.2f}"
