"""
Sovereign Extractors — Model-specific extraction logic.
"""
import json
import time
import httpx
import anyio
from typing import AsyncGenerator, Optional, Dict, Any
from pathlib import Path
from .ingestion_types import ExtractionSchema, IngestionConfig

# The Standard Sovereign Extraction Schema
# This is the core of the Entity Deepening Protocol.
EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "technical_facts": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Technical facts, decisions, and implementation details from the text"
        },
        "personality_patterns": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Observable patterns in personality, habits, communication style"
        },
        "gnosis_principles": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "principle": {"type": "string", "description": "Name of the principle"},
                    "description": {"type": "string", "description": "Detailed explanation"}
                },
                "required": ["principle", "description"]
            },
            "description": "Universal engineering or life principles distilled from the text"
        },
        "heritage_patterns": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Patterns that could be ported to other systems (id Software heritage, etc)"
        },
        "dpo_pairs": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "A question about the text"},
                    "chosen": {"type": "string", "description": "Authentic answer based on the text"},
                    "rejected": {"type": "string", "description": "Generic or incorrect answer"}
                },
                "required": ["prompt", "chosen", "rejected"]
            },
            "description": "Direct Preference Optimization training pairs"
        }
    },
    "required": ["technical_facts", "personality_patterns", "gnosis_principles", "heritage_patterns", "dpo_pairs"]
}

class BaseExtractor:
    """Abstract base for all sovereign extractors."""
    async def extract_stream(self, text: str, config: IngestionConfig) -> AsyncGenerator[str, None]:
        raise NotImplementedError

    async def extract(self, text: str, config: IngestionConfig) -> Dict[str, Any]:
        """Non-streaming wrapper for extract_stream."""
        full_text = ""
        async for chunk in self.extract_stream(text, config):
            full_text += chunk
        return json.loads(full_text)

class GoogleExtractor(BaseExtractor):
    """Google Gemini API extractor with SSE streaming and responseJsonSchema."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

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
            async with client.stream("POST", url, json=payload, headers={"x-goog-api-key": self.api_key}) as response:
                if response.status_code != 200:
                    yield f"Error: HTTP {response.status_code} - {await response.aread()}"
                    return

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        try:
                            data = json.loads(data_str)
                            # Extract the text part from the candidate
                            parts = data["candidates"][0]["content"]["parts"]
                            for part in parts:
                                if "text" in part:
                                    yield part["text"]
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue
