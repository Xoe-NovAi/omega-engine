import anyio
import os
import logging
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List
from src.omega.ingestion.pipeline import create_pipeline
from src.omega.ingestion.ingestion_types import IngestionConfig
from src.omega.ingestion.sources import FileSource
from omega.errors import OmegaError

async def setup_logging(entity_name: str):
    """Sets up standardized logging for the ingestion process."""
    log_dir = Path(f"data/logs/ingestion/{entity_name}")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"ingest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("SovereignIngest")

async def load_state(entity_name: str) -> set:
    """Load the set of already successfully ingested sources for a specific entity."""
    state_file = Path(f"data/logs/ingestion/{entity_name}/state.json")
    if state_file.exists():
        try:
            with open(state_file, "r") as f:
                return set(json.load(f))
        except Exception as e:
            logging.warning(f"Failed to load state file for {entity_name}: {e}. Starting fresh.")
    return set()

async def save_state(entity_name: str, completed_sources: set):
    """Persist the set of successfully ingested sources for a specific entity."""
    state_file = Path(f"data/logs/ingestion/{entity_name}/state.json")
    try:
        with open(state_file, "w") as f:
            json.dump(list(completed_sources), f)
    except Exception as e:
        logging.error(f"Failed to save state file for {entity_name}: {e}")

async def main():
    parser = argparse.ArgumentParser(description="Sovereign Ingestion Utility")
    parser.add_argument("--entity", required=True, help="Target entity name (e.g., john_carmack)")
    parser.add_argument("--model", default="gemma-4-31b-it", help="Model to use for extraction")
    parser.add_argument("--sources", nargs="+", required=True, help="List of source files to ingest")
    parser.add_argument("--budget", type=float, default=10.0, help="Max budget in USD")
    
    args = parser.parse_args()
    logger = await setup_logging(args.entity)
    
    logger.info(f"Initializing Sovereign Ingestion for entity: {args.entity}")
    
    # Resolve Google API key from VaultCore
    google_key = None
    try:
        from omega.vault import VaultCore
        vault = VaultCore()
        vault._load_sync()
        cred = vault._credentials.get("google:api_key")
        google_key = cred.encrypted_blob if cred else None
    except Exception:
        google_key = None
    
    config = IngestionConfig(
        entity_name=args.entity,
        model_name=args.model,
        api_key=google_key,
        sources=[Path(s) for s in args.sources],
        max_budget_usd=args.budget
    )
    
    try:
        pipeline = await create_pipeline(config)
        completed = await load_state(args.entity)
        
        pending_paths = [p for p in config.sources if str(p) not in completed]
        
        if not pending_paths:
            logger.info(f"All provided sources for {args.entity} already ingested.")
            return

        logger.info(f"Processing {len(pending_paths)} pending sources...")
        sources = [FileSource(p) for p in pending_paths]
        
        results = await pipeline.run_batch(sources)
        
        for res in results:
            completed.add(str(res.source_name))
        
        await save_state(args.entity, completed)
        
        success_count = len(results)
        logger.info(f"Batch Complete. Successfully ingested {success_count}/{len(pending_paths)} sources.")

    except OmegaError as e:
        logger.critical(f"Sovereign Pipeline Error: {e}", exc_info=True)
    except Exception as e:
        logger.critical(f"Unexpected System Failure: {e}", exc_info=True)

if __name__ == "__main__":
    try:
        anyio.run(main)
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
