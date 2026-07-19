#!/usr/bin/env python3
"""HuggingFace Leaderboard Scraper for Capability Scores."""
import requests
from typing import Optional

HF_BENCHMARKS = {
    "reasoning": "cais/hle",
    "knowledge": "HuggingFaceH4/MMLU",
    "code": "openai/gsm8k",
}

def fetch_leaderboard(dataset_id: str, limit: int = 200) -> list[dict]:
    try:
        resp = requests.get(
            f"https://huggingface.co/api/datasets/{dataset_id}/leaderboard",
            params={"limit": limit},
            timeout=15
        )
        return resp.json() if resp.status_code == 200 else []
    except Exception:
        return []

def normalize_score(value: float, max_score: float = 100.0) -> float:
    return min(1.0, max(0.0, value / max_score))

def score_model(model_id: str) -> dict:
    scores = {}
    for cap, dataset in HF_BENCHMARKS.items():
        entries = fetch_leaderboard(dataset)
        for entry in entries:
            if entry.get("modelId", "").lower() == model_id.lower():
                scores[cap] = normalize_score(entry.get("value", 0))
                break
    return scores
