"""
Sovereign Ingestion Pipeline — Orchestrating entity deepening.
"""
import json
import time
import uuid
import anyio
import logging
from typing import List, Optional, AsyncGenerator
from pathlib import Path
from datetime import datetime, timezone

from .ingestion_types import IngestionConfig, IngestionResult, ExtractionSchema
from .extractors import BaseExtractor, GoogleExtractor
from .persistence import IngestionPersistence
from .sources import FileSource

logger = logging.getLogger(__name__)

class IngestionPipeline:
    """
    Orchestrates the full ingestion flow:
    Source Loading -> Streaming Extraction -> Quality Scoring -> Persistence
    """
    
    def __init__(self, config: IngestionConfig, extractor: BaseExtractor):
        self.config = config
        self.extractor = extractor
        self.persistence = IngestionPersistence(config.entity_name)

    async def run_source(self, source: FileSource) -> Optional[IngestionResult]:
        """Processes a single source through the pipeline."""
        source_name, text = await source.read()
        
        # Create a unique trace for this extraction
        trace_id = f"ingest_{uuid.uuid4().hex[:12]}"
        
        print(f"\n🚀 Ingesting: {source_name} ({len(text):,} chars)")
        print(f"Model: {self.config.model_name} | Key: {self.config.api_key[:8]}...")
        print("-" * 60)
        
        t0 = time.time()
        full_response = ""
        
        try:
            # 1. Streaming Extraction
            print("Streaming extraction: ", end="", flush=True)
            async for chunk in self.extractor.extract_stream(text, self.config):
                print(chunk, end="", flush=True)
                full_response += chunk
            print("\n" + "-" * 60)
            
            # 2. Parse Result
            try:
                extraction_dict = json.loads(full_response)
                extraction = ExtractionSchema(**extraction_dict)
            except json.JSONDecodeError:
                print(f"❌ JSON Parse Error for {source_name}")
                return None
            
            latency = time.time() - t0
            
            # 3. Persistence (MemoryStore, Qdrant, Observability)
            session_id = await self.persistence.persist_extraction(
                source_name=source_name,
                model_name=self.config.model_name,
                extraction_data=extraction.to_dict(),
                latency_s=latency,
                trace_id=trace_id
            )
            
            print(f"✅ Persisted to session {session_id}")
            print(f"Items: {sum(len(v) if isinstance(v, list) else 0 for v in extraction.to_dict().values())}")
            print(f"Latency: {latency:.2f}s")
            
            return IngestionResult(
                source_name=source_name,
                model_name=self.config.model_name,
                extraction=extraction,
                latency_s=latency,
                input_chars=len(text),
                trace_id=trace_id
            )
            
        except Exception as e:
            print(f"❌ Pipeline failure for {source_name}: {e}")
            return None

    async def run_batch(self, sources: List[FileSource]) -> List[IngestionResult]:
        """Processes a batch of sources."""
        results = []
        for source in sources:
            res = await self.run_source(source)
            if res:
                results.append(res)
        return results

async def create_pipeline(config: IngestionConfig) -> IngestionPipeline:
    """Factory to create a pipeline based on the model."""
    if "google" in config.model_name or "gemma" in config.model_name:
        extractor = GoogleExtractor(config.api_key)
    else:
        raise NotImplementedError(f"No extractor implemented for model {config.model_name}")
        
    return IngestionPipeline(config, extractor)
