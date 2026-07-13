#!/usr/bin/env python3
"""
John Carmack Entity Deepening - Ingestion Pipeline
Executes the 6-pass extraction over primary sources.
"""
import anyio
import json
import re
import uuid
import os
import logging
from pathlib import Path
from datetime import datetime, timezone

logging.basicConfig(level=logging.DEBUG)

# Omega Engine imports
from omega.oracle.model_gateway import ModelGateway

# Configuration
ENTITY_NAME = "john_carmack"
MODEL_NAME = "qwen3-1.7b"  # System default — native-gguf loads Qwen3-1.7B-Q6_K.gguf
BASE_DIR = Path("data/entities/john_carmack")
TIMEOUT_SECONDS = 300  # 5 minutes for local inference on 1.7B
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
TRAINING_DIR = Path("data/training/entities/john_carmack")
STUDIES_DIR = BASE_DIR / "workspace/carmack_studies"

SYSTEM_PROMPT = """You are the Omega Engine Ingestion Pipeline.
Your task is to analyze primary source text from John Carmack and extract data across multiple dimensions.
You must return ONLY valid JSON matching the following schema, with no markdown formatting or extra text.

{
  "technical_facts": ["fact 1", "fact 2"],
  "personality_patterns": ["pattern 1", "pattern 2"],
  "gnosis_principles": [
    {"principle": "Name", "description": "Details"}
  ],
  "heritage_patterns": ["pattern 1"],
  "dpo_pairs": [
    {"prompt": "A question about the text", "chosen": "Carmack's authentic answer based on the text", "rejected": "A generic or incorrect answer"}
  ]
}
"""

async def process_file(gateway: ModelGateway, file_path: Path):
    print(f"Processing {file_path.name}...")
    content = await anyio.Path(file_path).read_text()
    
    # Strip frontmatter for the LLM
    text_content = re.sub(r'^---.*?---\n', '', content, flags=re.DOTALL)
    
    user_query = f"/no_think\nExtract the 5 dimensions from the following text:\n\n{text_content[:12000]}"
    
    trace_id = f"ingest-{uuid.uuid4().hex[:8]}"
    
    try:
        result = await gateway.generate(
            model_name=MODEL_NAME,
            system_prompt=SYSTEM_PROMPT,
            user_query=user_query,
            temperature=0.3,
            max_tokens=4096,
            trace_id=trace_id,
            entity_name=ENTITY_NAME
        )
    except Exception as e:
        print(f"Gateway generation failed: {e}")
        return None
    
    try:
        # Strip thinking tokens if present
        raw = result.text.strip()
        # Remove <think>...</think> blocks
        raw = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL)
        raw = raw.strip()
        
        # Clean markdown JSON blocks if present
        if raw.startswith("```json"):
            raw = raw[7:-3].strip()
        elif raw.startswith("```"):
            raw = raw[3:-3].strip()
        
        # Try direct parse first
        try:
            data = json.loads(raw)
            return data
        except json.JSONDecodeError:
            pass
        
        # Fallback: find first { ... } block (handles extra text after JSON)
        brace_start = raw.find('{')
        if brace_start >= 0:
            depth = 0
            for i in range(brace_start, len(raw)):
                if raw[i] == '{':
                    depth += 1
                elif raw[i] == '}':
                    depth -= 1
                    if depth == 0:
                        try:
                            data = json.loads(raw[brace_start:i+1])
                            return data
                        except json.JSONDecodeError:
                            break
        
        print(f"Failed to parse JSON for {file_path.name}")
        print(f"Raw output: {raw[:300]}...")
        return None
    except Exception as e:
        print(f"Parse error for {file_path.name}: {e}")
        return None

async def main():
    gateway = ModelGateway()
    
    # Ensure output dirs exist
    await anyio.Path(TRAINING_DIR).mkdir(parents=True, exist_ok=True)
    await anyio.Path(STUDIES_DIR / "gnosis").mkdir(parents=True, exist_ok=True)
    
    dpo_file = TRAINING_DIR / "dpo_pairs.jsonl"
    gnosis_file = STUDIES_DIR / "gnosis" / "extracted_principles.jsonl"
    
    sources = [
        KNOWLEDGE_DIR / "gdc/supplementary/2009_wolfenstein_iphone_letter.md",
        KNOWLEDGE_DIR / "gdc/supplementary/2011_carmack_on_rage_interview.md"
    ]
    
    total_dpo = 0
    total_gnosis = 0
    
    for source in sources:
        if not await anyio.Path(source).exists():
            print(f"Source not found: {source}")
            continue
            
        data = await process_file(gateway, source)
        if not data:
            continue
            
        # Write DPO pairs
        if "dpo_pairs" in data:
            async with await anyio.Path(dpo_file).open("a") as f:
                for pair in data["dpo_pairs"]:
                    pair["source"] = source.name
                    await f.write(json.dumps(pair) + "\n")
                    total_dpo += 1
                    
        # Write Gnosis
        if "gnosis_principles" in data:
            async with await anyio.Path(gnosis_file).open("a") as f:
                for principle in data["gnosis_principles"]:
                    principle["source"] = source.name
                    await f.write(json.dumps(principle) + "\n")
                    total_gnosis += 1
                    
        print(f"Successfully extracted {len(data.get('dpo_pairs', []))} DPO pairs and {len(data.get('gnosis_principles', []))} principles from {source.name}")

    print(f"\nIngestion complete. Total DPO pairs: {total_dpo}. Total Gnosis principles: {total_gnosis}.")

if __name__ == "__main__":
    anyio.run(main)
