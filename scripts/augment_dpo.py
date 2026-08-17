#!/usr/bin/env python3
"""
DPO Dataset Augmentation Script

Reads 14 DPO pairs from data/training/dpo_dataset.jsonl,
generates 8 semantic variations per pair using local qwen3-1.7b model,
and writes ~150 total pairs to data/training/dpo_dataset_augmented.jsonl.

Usage:
    python scripts/augment_dpo.py
"""

import json
import logging
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import anyio

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from omega.oracle.model_gateway import ModelGateway

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
INPUT_FILE = Path("data/training/dpo_dataset.jsonl")
OUTPUT_FILE = Path("data/training/dpo_dataset_augmented.jsonl")
MODEL_NAME = "qwen3-1.7b"
VARIATIONS_PER_PAIR = 8
TARGET_TOTAL = 150  # ~14 original + 136 variations


def load_dpo_dataset(filepath: Path) -> List[Dict[str, Any]]:
    """Load DPO dataset from JSONL file."""
    pairs = []
    with open(filepath, "r") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                pair = json.loads(line)
                pairs.append(pair)
            except json.JSONDecodeError as e:
                logger.error(f"Line {line_num}: Failed to parse JSON: {e}")
    logger.info(f"Loaded {len(pairs)} DPO pairs from {filepath}")
    return pairs


def extract_situation(prompt: str) -> str:
    """Extract the situation description from the prompt."""
    prefix = "Fix this situation: "
    if prompt.startswith(prefix):
        return prompt[len(prefix):].strip()
    return prompt


def build_variation_prompt(situation: str, num_variations: int = 8) -> str:
    """Build the prompt for generating variations."""
    return f"""Generate {num_variations} semantic variations of this coding problem situation. Each variation must describe the SAME underlying issue with different phrasing, terminology, or framing.

Original situation: {situation}

Requirements:
- Each variation must be a complete sentence or two describing the same problem
- Use different vocabulary, sentence structure, or perspective
- Keep the core technical issue identical
- Return ONLY the variations, one per line, no numbering, no extra text
- Do not include the "Fix this situation:" prefix - just the situation description

Variations:"""


async def generate_variations(
    gateway: ModelGateway,
    situation: str,
    num_variations: int = VARIATIONS_PER_PAIR
) -> List[str]:
    """Generate semantic variations using the local model."""
    prompt = build_variation_prompt(situation, num_variations)
    
    try:
        result = await gateway.generate(
            model_name=MODEL_NAME,
            system_prompt="You are a precise technical writer. Generate only the requested variations, one per line.",
            user_query=prompt,
            temperature=0.7,
            max_tokens=512,
        )
        
        # Parse variations from response
        variations = []
        for line in result.text.strip().split("\n"):
            line = line.strip()
            # Remove common prefixes like "1.", "- ", "* ", etc.
            line = line.lstrip("0123456789.-* ").strip()
            if line and len(line) > 10:  # Filter out empty/short lines
                variations.append(line)
        
        # Ensure we have the right number
        variations = variations[:num_variations]
        
        if len(variations) < num_variations:
            logger.warning(f"Only generated {len(variations)} variations, expected {num_variations}")
        
        return variations
        
    except Exception as e:
        logger.error(f"Failed to generate variations: {e}")
        return []


def create_augmented_pair(
    original: Dict[str, Any],
    variation: str,
    variation_index: int
) -> Dict[str, Any]:
    """Create an augmented DPO pair from original and variation."""
    # Generate a lineage ID if not present
    source_lineage = original.get("metadata", {}).get("lineage_id", str(uuid.uuid4())[:8])
    
    augmented = {
        "prompt": f"Fix this situation: {variation}",
        "chosen": original["chosen"],
        "rejected": original["rejected"],
        "metadata": {
            **original.get("metadata", {}),
            "augmented": True,
            "source_lineage": source_lineage,
            "variation_index": variation_index,
        }
    }
    
    # Preserve lineage_id if it exists in original
    if "lineage_id" in original.get("metadata", {}):
        augmented["metadata"]["lineage_id"] = original["metadata"]["lineage_id"]
    
    return augmented


async def augment_dataset() -> None:
    """Main augmentation pipeline."""
    logger.info("=" * 60)
    logger.info("Starting DPO Dataset Augmentation")
    logger.info("=" * 60)
    
    # Load original dataset
    original_pairs = load_dpo_dataset(INPUT_FILE)
    
    if not original_pairs:
        logger.error("No pairs loaded. Exiting.")
        return
    
    # Initialize ModelGateway
    logger.info(f"Initializing ModelGateway with model: {MODEL_NAME}")
    gateway = ModelGateway()
    
    # Verify model is available
    models = gateway.list_models()
    model_names = [m["name"] for m in models]
    if MODEL_NAME not in model_names:
        logger.error(f"Model {MODEL_NAME} not found in available models: {model_names}")
        return
    
    logger.info(f"Model {MODEL_NAME} confirmed available")
    
    # Process each pair
    all_pairs = []  # Will contain original + augmented
    total_variations_generated = 0
    
    for pair_idx, original in enumerate(original_pairs, 1):
        logger.info(f"Processing pair {pair_idx}/{len(original_pairs)}")
        
        # Add original pair to output
        all_pairs.append(original)
        
        # Extract situation
        situation = extract_situation(original["prompt"])
        logger.debug(f"  Situation: {situation[:100]}...")
        
        # Generate variations
        variations = await generate_variations(gateway, situation)
        
        if not variations:
            logger.warning(f"  No variations generated for pair {pair_idx}, skipping augmentation")
            continue
        
        # Create augmented pairs
        for var_idx, variation in enumerate(variations, 1):
            augmented = create_augmented_pair(original, variation, var_idx)
            all_pairs.append(augmented)
            total_variations_generated += 1
        
        logger.info(f"  Generated {len(variations)} variations")
        
        # Progress log every 10 pairs
        if pair_idx % 10 == 0:
            logger.info(f"Progress: {pair_idx}/{len(original_pairs)} pairs processed, "
                       f"{total_variations_generated} variations generated so far")
    
    # Write output
    logger.info(f"Writing {len(all_pairs)} total pairs to {OUTPUT_FILE}")
    with open(OUTPUT_FILE, "w") as f:
        for pair in all_pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")
    
    # Verify
    original_count = len(original_pairs)
    augmented_count = len(all_pairs) - original_count
    
    logger.info("=" * 60)
    logger.info("AUGMENTATION COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Original pairs: {original_count}")
    logger.info(f"Augmented pairs: {augmented_count}")
    logger.info(f"Total pairs: {len(all_pairs)}")
    logger.info(f"Target: ~{TARGET_TOTAL}")
    logger.info(f"Output file: {OUTPUT_FILE}")
    
    # Verify all originals preserved
    verify_originals_preserved(original_pairs, all_pairs)
    
    # Cleanup
    gateway.shutdown()


def verify_originals_preserved(originals: List[Dict], augmented: List[Dict]) -> None:
    """Verify all original pairs are present in augmented dataset."""
    original_prompts = {p["prompt"] for p in originals}
    augmented_prompts = {p["prompt"] for p in augmented}
    
    missing = original_prompts - augmented_prompts
    if missing:
        logger.error(f"MISSING ORIGINALS: {len(missing)} prompts not found in output!")
        for m in missing:
            logger.error(f"  Missing: {m[:80]}...")
    else:
        logger.info("✓ All original pairs preserved in output")
    
    # Check metadata preservation
    for orig in originals:
        for aug in augmented:
            if aug["prompt"] == orig["prompt"] and not aug["metadata"].get("augmented", False):
                # This is an original pair - verify metadata
                orig_meta = orig.get("metadata", {})
                aug_meta = aug.get("metadata", {})
                for key in orig_meta:
                    if key not in aug_meta:
                        logger.warning(f"Metadata key '{key}' not preserved for prompt: {orig['prompt'][:60]}...")
                break


async def main():
    """Entry point."""
    try:
        await augment_dataset()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    anyio.run(main)