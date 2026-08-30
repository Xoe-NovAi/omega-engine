# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-INGESTION-EXTRACTORS-v1.0.0
"""
Sovereign Extractors — Model-specific extraction logic.
"""

# DocRef: docs/architecture/SOVEREIGN_DATA_FLOW.md
import json
from pydantic import ValidationError
import httpx2 as httpx
from typing import AsyncGenerator
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type
from json_repair import repair_json
from .ingestion_types import (
    ExtractionSchema,
    IngestionConfig,
    SovereigntyError,
    ProviderServerError,
    TransportError,
    SchemaError,
)

# The Standard Sovereign Extraction Schema
# This is the core of the Entity Deepening Protocol.
EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "technical_facts": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Technical facts, decisions, and implementation details from the text",
        },
        "personality_patterns": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Observable patterns in personality, habits, communication style",
        },
        "gnosis_principles": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "principle": {"type": "string", "description": "Name of the principle"},
                    "description": {"type": "string", "description": "Detailed explanation"},
                },
                "required": ["principle", "description"],
            },
            "description": "Universal engineering or life principles distilled from the text",
        },
        "heritage_patterns": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Patterns that could be ported to other systems (id Software heritage, etc)",
        },
        "dpo_pairs": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "A question about the text"},
                    "chosen": {
                        "type": "string",
                        "description": "Authentic answer based on the text",
                    },
                    "rejected": {"type": "string", "description": "Generic or incorrect answer"},
                },
                "required": ["prompt", "chosen", "rejected"],
            },
            "description": "Direct Preference Optimization training pairs",
        },
    },
    "required": [
        "technical_facts",
        "personality_patterns",
        "gnosis_principles",
        "heritage_patterns",
        "dpo_pairs",
    ],
}


class BaseExtractor:
    """Abstract base for all sovereign extractors."""

    async def extract_stream(self, text: str, config: IngestionConfig) -> AsyncGenerator[str, None]:
        raise NotImplementedError

    async def extract(self, text: str, config: IngestionConfig) -> ExtractionSchema:
        """Non-streaming wrapper for extract_stream with robust JSON repair."""
        full_text = ""
        async for chunk in self.extract_stream(text, config):
            full_text += chunk

        # Robust JSON repair and validation
        try:
            repaired_json = repair_json(full_text)
            data = json.loads(repaired_json)
            return ExtractionSchema.model_validate(data)
        except (json.JSONDecodeError, ValidationError, RuntimeError, OSError) as e:
            raise SchemaError(f"Failed to parse extraction result even after repair: {str(e)}")


class GoogleExtractor(BaseExtractor):
    """Google Gemini API extractor with SSE streaming and responseJsonSchema."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_random_exponential(multiplier=1, max=60),
        retry=retry_if_exception_type((ProviderServerError, TransportError)),
        reraise=True,
    )
    async def extract_stream(self, text: str, config: IngestionConfig) -> AsyncGenerator[str, None]:
        url = f"{self.base_url}/{config.model_name}:streamGenerateContent?alt=sse"

        prompt = f"Extract data about the entity from the source text below. Focus on technical decisions, personality traits, universal principles, reusable patterns, and training data.\n\n{text[:240000]}"

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": config.temperature,
                "maxOutputTokens": config.max_tokens,
                "responseMimeType": "application/json",
                "responseJsonSchema": EXTRACTION_SCHEMA,
            },
        }

        async with httpx.AsyncClient(timeout=180.0) as client:
            try:
                async with client.stream(
                    "POST", url, json=payload, headers={"x-goog-api-key": self.api_key}
                ) as response:
                    if response.status_code == 403:
                        raise SovereigntyError(
                            f"HTTP 403: API Key invalid or quota exceeded. {await response.aread()}"
                        )
                    if response.status_code >= 500:
                        raise ProviderServerError(
                            f"HTTP {response.status_code}: Provider internal error."
                        )
                    if response.status_code != 200:
                        raise TransportError(f"HTTP {response.status_code}: Unexpected response.")

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]
                            try:
                                data = json.loads(data_str)
                                parts = data["candidates"][0]["content"]["parts"]
                                for part in parts:
                                    if "text" in part:
                                        yield part["text"]
                            except (json.JSONDecodeError, KeyError, IndexError):
                                continue
            except httpx.RequestError as e:
                raise TransportError(f"Network error during extraction: {str(e)}")
