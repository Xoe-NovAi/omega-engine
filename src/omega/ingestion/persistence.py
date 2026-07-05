# AP: AP-INGESTION-PERSISTENCE-v1.0.0
"""
Sovereign Persistence — Wiring ingestion results into Engine systems.
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime, timezone

import anyio
from omega.memory_store import get_memory_store
from omega.observability import get_engine as get_observability_engine, new_trace_id

class IngestionPersistence:
    """Handles the persistence of extracted knowledge into the Omega Engine."""
    
    def __init__(self, entity_name: str):
        self.entity_name = entity_name
        self.memory_store = get_memory_store()
        self.obs = get_observability_engine()
        self.training_dir = Path(f"data/training/entities/{entity_name}")
        self.training_dir.mkdir(parents=True, exist_ok=True)

    async def persist_extraction(
        self, 
        source_name: str, 
        model_name: str, 
        extraction_data: Dict[str, Any], 
        latency_s: float, 
        trace_id: str,
        quality_score: float,
        domain: str,
        enrichment: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Persists an extraction result through the full Engine stack:
        1. MemoryStore (Hot/Warm/FTS5/Qdrant)
        2. Observability (Events/Traces)
        3. Raw JSON Backup (Training dir)
        """
        # 1. MemoryStore Persistence
        # We create a unique session for this specific source extraction
        session_id = f"ingest_{source_name}_{int(datetime.now().timestamp())}"
        
        user_msg = f"Sovereign Ingestion: Extract from {source_name} using {model_name}"
        assistant_res = json.dumps(extraction_data, indent=2)
        
        metadata = {
            "source": source_name,
            "model": model_name,
            "latency_s": latency_s,
            "category": "ingestion_extraction",
            "quality_score": quality_score,
            "domain": domain,
            "enrichment": enrichment,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # This call handles:
        # - Hot cache update
        # - Warm file storage (gzip JSON)
        # - FTS5 SQLite indexing (searchable via MemoryStore.search())
        # - Qdrant vector upsert (semantic search via IVectorStoreAdapter)
        # - Vault update
        await self.memory_store.add_exchange(
            entity_name=self.entity_name,
            session_id=session_id,
            user_message=user_msg,
            response=assistant_res,
            metadata=metadata,
            trace_id=trace_id
        )
        
        # 2. Observability Event
        self.obs.log_event(
            event_type="ingestion_complete",
            trace_id=trace_id,
            data={
                "entity": self.entity_name,
                "source": source_name,
                "model": model_name,
                "items_extracted": sum(
                    len(v) if isinstance(v, list) else 0 
                    for v in extraction_data.values()
                ),
                "latency_s": latency_s
            }
        )
        
        # 3. Raw JSON Backup for DPO training
        backup_path = self.training_dir / f"{source_name}_{int(datetime.now().timestamp())}.json"
        async with await anyio.Path(backup_path).open("w") as f:
            await f.write(json.dumps({
                "source": source_name,
                "model": model_name,
                "extraction": extraction_data,
                "metadata": metadata,
                "trace_id": trace_id
            }, indent=2))
            
        return session_id
