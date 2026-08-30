#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
Gemma Model Comparison — 31B vs 26B via Google API
Uses DIFFERENT API keys per model to avoid rate limits.

Key discovery: Gemma 4 requires BOTH responseMimeType AND responseJsonSchema
to suppress thinking and force clean JSON output. Without the schema, the
model ignores the mime type and outputs reasoning text.
"""
import json
import os
import sys
import time
import uuid
import httpx
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

def load_env():
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key, val)

load_env()

MODELS = {
    "gemma4_31b": {
        "model": "gemma-4-31b-it",
        "env_key": "GOOGLE_API_KEY_1",
    },
    "gemma4_26b": {
        "model": "gemma-4-26b-a4b-it",
        "env_key": "GOOGLE_API_KEY_2",
    },
}

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
            "description": "Observable patterns in Carmack's personality, habits, communication style"
        },
        "gnosis_principles": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "principle": {"type": "string", "description": "Name of the principle"},
                    "description": {"description": "Detailed explanation of the principle", "type": "string"}
                },
                "required": ["principle", "description"]
            },
            "description": "Universal engineering or life principles distilled from the text"
        },
        "heritage_patterns": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Patterns that could be ported to other systems (id Software heritage, design patterns)"
        },
        "dpo_pairs": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "A question about the text"},
                    "chosen": {"type": "string", "description": "Carmack's authentic answer based on the text"},
                    "rejected": {"type": "string", "description": "A generic or incorrect answer that sounds plausible"}
                },
                "required": ["prompt", "chosen", "rejected"]
            },
            "description": "Direct Preference Optimization training pairs for fine-tuning"
        }
    },
    "required": ["technical_facts", "personality_patterns", "gnosis_principles", "heritage_patterns", "dpo_pairs"]
}

EXTRACTION_PROMPT = """Extract data about John Carmack from the source text below. Focus on technical decisions, personality traits, universal principles, reusable patterns, and training data."""

SOURCES = [
    {
        "name": "masters_of_doom",
        "path": Path("data/entities/john_carmack/knowledge/source/masters_of_doom_excerpts.md"),
        "label": "Masters of Doom (4.2K words)",
    },
    {
        "name": "plan_1996",
        "path": Path("data/entities/john_carmack/knowledge/source/plan_files/by_year/johnc_plan_1996.txt"),
        "label": ".plan 1996 (24K words)",
    },
]


async def google_generate(text: str, model: str, api_key: str) -> tuple[Optional[dict], float, int]:
    """Call Google Gemini API. Uses responseMimeType + responseJsonSchema for clean JSON."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    truncated = text[:240000]

    payload = {
        "contents": [{"parts": [{"text": f"{EXTRACTION_PROMPT}\n\n{truncated}"}]}],
        "generationConfig": {
            "temperature": 0.6,
            "maxOutputTokens": 8192,
            "responseMimeType": "application/json",
            "responseJsonSchema": EXTRACTION_SCHEMA,
        },
    }
    t0 = time.time()
    async with httpx.AsyncClient(timeout=180.0) as client:
        resp = await client.post(url, json=payload, headers={"x-goog-api-key": api_key})
        elapsed = time.time() - t0
        if resp.status_code != 200:
            return {"error": f"HTTP {resp.status_code}: {resp.text[:300]}"}, elapsed, len(truncated)
        data = resp.json()
        if "candidates" not in data or not data["candidates"]:
            return {"error": "no candidates", "raw": json.dumps(data)[:300]}, elapsed, len(truncated)
        parts = data["candidates"][0]["content"]["parts"]
        text_out = None
        for part in parts:
            if not part.get("thought", False):
                text_out = part["text"]
                break
        if text_out is None:
            text_out = parts[0]["text"] if parts else ""
        try:
            return json.loads(text_out), elapsed, len(truncated)
        except json.JSONDecodeError:
            return {"raw_text": text_out[:500], "parse_error": "json failed"}, elapsed, len(truncated)


def score_result(data: dict) -> dict:
    if "error" in data or "parse_error" in data:
        return {"total": 0, "details": {"error": data.get("error", data.get("parse_error", "unknown"))}}
    scores = {}
    for key in ("technical_facts", "personality_patterns", "gnosis_principles", "heritage_patterns", "dpo_pairs"):
        val = data.get(key, [])
        if isinstance(val, list):
            scores[key] = len(val)
        elif isinstance(val, dict):
            scores[key] = len(val.keys())
        else:
            scores[key] = 0
    scores["total"] = sum(scores.values())
    return {"total": scores.pop("total"), "details": scores}


async def main():
    run_id = f"gemma_{uuid.uuid4().hex[:6]}"
    timestamp = datetime.now(timezone.utc).isoformat()
    results = []

    # Load separate keys per model
    model_keys = {}
    for model_key, info in MODELS.items():
        api_key = os.environ.get(info["env_key"], "")
        if not api_key:
            print(f"⚠️  {info['env_key']} not set — skipping {info['model']}")
            continue
        model_keys[model_key] = api_key

    if not model_keys:
        print("ERROR: No API keys configured")
        return

    print(f"🔱 Gemma Comparison — run_id={run_id}")
    print(f"   Models: {', '.join(info['model'] for info in MODELS.values() if info['env_key'] in model_keys)}")
    print(f"   JSON mode: responseMimeType + responseJsonSchema")
    print(f"   Keys: separate per model (no rate limit collision)")
    print()

    for src in SOURCES:
        if not src["path"].exists():
            print(f"❌ Missing: {src['path']}")
            continue

        text = src["path"].read_text(encoding="utf-8")
        print(f"\n{'='*60}")
        print(f"📄 {src['label']} — {len(text):,} chars")
        print(f"{'='*60}")

        for model_key, api_key in model_keys.items():
            info = MODELS[model_key]
            model_name = info["model"]
            print(f"\n  ── {model_name} ──")
            try:
                data, elapsed, chars = await google_generate(text, model_name, api_key)
            except httpx.ReadTimeout:
                data, elapsed, chars = {"error": "timeout (180s)"}, 180.0, len(text[:240000])
            quality = score_result(data)

            status = "✅" if quality["total"] > 0 else "⚠️"
            print(f"  {status} {elapsed:.1f}s | {chars:,} chars")
            print(f"  Extraction: {quality['total']} items — {quality['details']}")

            if data.get("raw_text"):
                print(f"  Raw (first 200): {data['raw_text'][:200]}...")
            if data.get("error"):
                print(f"  Error: {str(data['error'])[:200]}")

            results.append({
                "run_id": run_id,
                "timestamp": timestamp,
                "source": src["name"],
                "model": model_name,
                "model_key": model_key,
                "api_key_used": info["env_key"],
                "latency_s": round(elapsed, 2),
                "input_chars": chars,
                "quality": quality,
                "result": data,
            })

    # Summary
    print(f"\n{'='*60}")
    print("📊 COMPARISON SUMMARY")
    print(f"{'='*60}")
    print(f"{'Source':<25} {'Model':<20} {'Latency':>8} {'Items':>6}")
    print("-" * 62)
    for r in results:
        print(f"{r['source']:<25} {r['model']:<20} {r['latency_s']:>7.1f}s {r['quality']['total']:>5}")

    # Save
    out_dir = Path("data/training/entities/john_carmack/ab_tests")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{run_id}.json"
    out_path.write_text(json.dumps(results, indent=2, default=str))
    print(f"\n💾 {out_path}")


if __name__ == "__main__":
    import anyio
    anyio.run(main)
