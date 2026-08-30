# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-INGESTION-CLI-v1.0.0
"""
Sovereign Ingestion CLI — Commands for entity deepening.
"""

# DocRef: docs/architecture/SOVEREIGN_DATA_FLOW.md
"""
Sovereign Ingestion CLI — Commands for entity deepening.
"""
import anyio
import argparse
from pathlib import Path

from omega.ingestion.ingestion_types import IngestionConfig
from omega.ingestion.pipeline import create_pipeline
from omega.ingestion.sources import FileSource


async def run_ingest(entity: str, source_path: str, model: str, api_key: str):
    # Resolve sources
    path = Path(source_path)
    if path.is_dir():
        sources = [FileSource(p) for p in path.glob("**/*.txt")]
    else:
        sources = [FileSource(path)]

    config = IngestionConfig(entity_name=entity, model_name=model, api_key=api_key, sources=sources)

    pipeline = await create_pipeline(config)
    results = await pipeline.run_batch(sources)

    print(f"\n\n🏁 Ingestion Complete. Processed {len(results)}/{len(sources)} sources.")


def main():
    parser = argparse.ArgumentParser(description="Omega Engine Sovereign Ingestion")
    parser.add_argument("--entity", required=True, help="Entity name (e.g. john_carmack)")
    parser.add_argument("--source", required=True, help="Path to source file or directory")
    parser.add_argument("--model", default="gemma-4-31b-it", help="Model name")
    parser.add_argument("--key", required=True, help="Google API Key")

    args = parser.parse_args()

    anyio.run(run_ingest, args.entity, args.source, args.model, args.key)


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
