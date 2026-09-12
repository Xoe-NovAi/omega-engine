# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict

# Add src to sys.path
import sys
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "src"))

from omega.memory_store import MemoryStore, get_memory_store
from omega.library.library import Library
from omega.library.indexer import Indexer
from omega.memory.providers import FileStorageProvider

async def index_historical_memory():
    print("🏗️  Indexing Historical Memory into FTS and Vector Store...")
    
    # Use the real memory store
    memory_store = get_memory_store()
    
    entities_dir = Path("data/memory/entities")
    if not entities_dir.exists():
        print(f"❌ Entities directory not found: {entities_dir}")
        return

    entity_dirs = [d for d in entities_dir.iterdir() if d.is_dir()]
    print(f"Found {len(entity_dirs)} entity directories.")

    total_indexed = 0
    
    for ent_dir in entity_dirs:
        entity_name = ent_dir.name
        session_files = list(ent_dir.glob("*.json"))
        
        for sess_file in session_files:
            session_id = sess_file.stem
            
            try:
                with open(sess_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Session files are typically a list of exchanges or a dict with a list
                exchanges = []
                if isinstance(data, list):
                    exchanges = data
                elif isinstance(data, dict) and "exchanges" in data:
                    exchanges = data["exchanges"]
                elif isinstance(data, dict):
                    # Some sessions might store exchanges in a different key or as the root
                    # Let's try to find any list of dicts
                    for k, v in data.items():
                        if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                            exchanges = v
                            break
                
                if not exchanges:
                    continue
                
                for ex in exchanges:
                    # Normalize exchange format
                    user_msg = ex.get("user", ex.get("user_message", ""))
                    assistant_msg = ex.get("assistant", ex.get("assistant_message", ""))
                    
                    if user_msg or assistant_msg:
                        await memory_store.add_exchange(
                            entity_name=entity_name,
                            session_id=session_id,
                            user_message=user_msg,
                            response=assistant_msg,
                            metadata=ex.get("metadata", {})
                        )
                        total_indexed += 1
                        
            except Exception as e:
                print(f"⚠️ Failed to index {sess_file}: {e}")

    print(f"✅ Successfully indexed {total_indexed} exchanges.")

if __name__ == "__main__":
    asyncio.run(index_historical_memory())
