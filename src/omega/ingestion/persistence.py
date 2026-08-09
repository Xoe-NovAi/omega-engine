# AP: AP-INGESTION-PERSISTENCE-v1.0.0
"""
Sovereign Persistence — Wiring ingestion results into Engine systems.
"""

# DocRef: docs/architecture/SOVEREIGN_DATA_FLOW.md
import json
import os
import hashlib
import uuid
import shutil
import re
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

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
        
        # Tri-Anchor Storage
        self.knowledge_dir = Path(f"data/entities/{entity_name}/knowledge")
        self.raw_dir = self.knowledge_dir / "raw"
        self.quarantine_dir = self.knowledge_dir / "quarantine"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)

    async def persist_raw_anchor(self, source_name: str, content: bytes, quarantine: bool = True) -> str:
        """
        Stage 1: The Raw Anchor (Immutable Ground Truth).
        Stores raw content and a .hash file for immutability.
        By default, stores in quarantine until promoted.
        """
        # Generate a stable source ID
        source_id = hashlib.sha256(source_name.encode()).hexdigest()[:16]
        base_dir = self.quarantine_dir if quarantine else self.raw_dir
        source_path = base_dir / source_id
        source_path.mkdir(parents=True, exist_ok=True)
        
        # Store raw content
        content_file = source_path / "content.bin"
        async with await anyio.open_file(content_file, "wb") as f:
            await f.write(content)
            
        # Store hash for immutability
        content_hash = hashlib.sha256(content).hexdigest()
        hash_file = source_path / ".hash"
        async with await anyio.open_file(hash_file, "w") as f:
            await f.write(content_hash)
            
        return source_id

    async def promote_to_soul(self, source_id: str):
        """
        Omnidroid Migration: Promotes a source from quarantine to the active raw anchor store.
        """
        q_path = self.quarantine_dir / source_id
        r_path = self.raw_dir / source_id
        
        if not await anyio.Path(q_path).exists():
            raise FileNotFoundError(f"Source {source_id} not found in quarantine.")
            
        # Remove existing raw anchor if it exists to avoid 'Directory not empty'
        if await anyio.Path(r_path).exists():
            import shutil as _shutil
            await anyio.to_thread.run_sync(_shutil.rmtree, r_path)
        
        # Move the entire directory
        await anyio.to_thread.run_sync(shutil.move, str(q_path), str(r_path))
        logger.info(f"Source {source_id} promoted to soul.")

    async def persist_sca(self, source_id: str, metadata: Dict[str, Any], quarantine: bool = True):
        """
        Stage 2: The Sovereign Continuity Anchor (SCA).
        Captures intent, voice, and context of ingestion.
        """
        base_dir = self.quarantine_dir if quarantine else self.raw_dir
        sca_path = base_dir / source_id / "sca.json"
        async with await anyio.open_file(sca_path, "w") as f:
            await f.write(json.dumps(metadata, indent=2))

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize source name for use as a filename."""
        return re.sub(r'[^a-zA-Z0-9_\-]', '_', name)

    async def persist_extraction(
        self, 
        source_id: str,
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
        await self.obs.log_event(
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
        safe_name = self._sanitize_filename(source_name)
        backup_path = self.training_dir / f"{safe_name}_{int(datetime.now().timestamp())}.json"
        async with await anyio.Path(backup_path).open("w") as f:
            await f.write(json.dumps({
                "source": source_name,
                "model": model_name,
                "extraction": extraction_data,
                "metadata": metadata,
                "trace_id": trace_id
            }, indent=2))
            
        return session_id
