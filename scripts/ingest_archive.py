#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
Omega Engine — Archive Ingestion using Existing Infrastructure
Ingests coordination archives, ChatGPT exports, legacy mining, session artifacts
using the existing MemoryStore + SQLiteVecAdapter pipeline.
Adds XYZ coordinate tracking for spatial-temporal-quality queries.
"""
import json
import logging
import sqlite3
import zipfile
import hashlib
import sqlite_vec
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import anyio
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.omega.memory_store import get_memory_store
from src.omega.ingestion.persistence import IngestionPersistence

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# XYZ Coordinate Schema:
# X = Spatial (domain/area): 0=coordination, 1=chatgpt, 2=legacy, 3=session, 4=research
# Y = Temporal (time): Unix timestamp normalized to 0-1 range for 2026
# Z = Quality (relevance): 0.0-1.0 (source authority, recency, density)

DOMAIN_MAP = {
    "coordination": 0.0,
    "chatgpt": 1.0,
    "legacy": 2.0,
    "session": 3.0,
    "research": 4.0,
}

TIME_MIN = datetime(2026, 1, 1, tzinfo=timezone.utc).timestamp()
TIME_MAX = datetime(2026, 12, 31, tzinfo=timezone.utc).timestamp()

class XYZIngestionPipeline:
    """Ingestion pipeline with XYZ coordinate tracking using existing MemoryStore."""
    
    def __init__(self, entity_name: str = "kali"):
        self.entity_name = entity_name
        self.memory_store = get_memory_store()
        self.persistence = IngestionPersistence(entity_name)
        self.db_path = Path("data/workbench/workbench.db")
        
    def init_xyz_schema(self):
        """Initialize XYZ coordinate tracking table in workbench.db."""
        conn = sqlite3.connect(self.db_path)
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS xyz_coordinates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id TEXT UNIQUE NOT NULL,
                entity_name TEXT NOT NULL,
                domain TEXT NOT NULL,
                x_coord REAL NOT NULL,
                y_coord REAL NOT NULL,
                z_coord REAL NOT NULL,
                source_path TEXT,
                archive_path TEXT,
                title TEXT,
                word_count INTEGER,
                char_count INTEGER,
                content_hash TEXT,
                metadata_json TEXT,
                ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("CREATE INDEX IF NOT EXISTS idx_xyz_domain ON xyz_coordinates(domain)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_xyz_coords ON xyz_coordinates(x_coord, y_coord, z_coord)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_xyz_entity ON xyz_coordinates(entity_name)")
        
        conn.commit()
        conn.close()
        logger.info("XYZ coordinate schema initialized")
    
    def normalize_time(self, timestamp: float) -> float:
        """Normalize timestamp to 0-1 range for 2026."""
        if timestamp < TIME_MIN:
            return 0.0
        if timestamp > TIME_MAX:
            return 1.0
        return (timestamp - TIME_MIN) / (TIME_MAX - TIME_MIN)
    
    def compute_quality(self, domain: str, content: str, metadata: Dict) -> float:
        """Compute quality score Z (0.0-1.0)."""
        base_scores = {
            "coordination": 0.7,
            "chatgpt": 0.8,
            "legacy": 0.6,
            "session": 0.75,
            "research": 0.9,
        }
        base = base_scores.get(domain, 0.5)
        
        word_count = len(content.split())
        if word_count > 5000:
            base += 0.1
        elif word_count > 1000:
            base += 0.05
        
        if metadata.get("authority_score", 0) > 7:
            base += 0.1
        
        return min(1.0, max(0.0, base))
    
    def extract_timestamp(self, file_path: Path) -> float:
        """Extract timestamp from filename or use file mtime."""
        import re
        match = re.search(r'2026(\d{4})', file_path.name)
        if match:
            try:
                dt = datetime.strptime(match.group(0), "%Y%m%d")
                return dt.replace(tzinfo=timezone.utc).timestamp()
            except (ValueError, TypeError):  # M9: typed errors only
                pass
        return file_path.stat().st_mtime
    
    def compute_xyz(self, domain: str, timestamp: float, quality: float) -> tuple:
        """Compute xyz coordinates."""
        x = DOMAIN_MAP.get(domain, 2.0)
        y = self.normalize_time(timestamp)
        z = quality
        return (x, y, z)
    
    async def ingest_file(self, file_path: Path, domain: str, archive_path: str = None, metadata: Dict = None) -> bool:
        """Ingest a single file using existing MemoryStore + XYZ tracking."""
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return False
        
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                content = file_path.read_text(encoding="latin-1")
            except Exception as e:
                logger.error(f"Failed to read {file_path}: {e}")
                return False
        
        if not content.strip():
            logger.warning(f"Empty file: {file_path}")
            return False
        
        # Compute identifiers
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:32]
        doc_id = f"{domain}_{content_hash}"
        timestamp = self.extract_timestamp(file_path)
        quality = self.compute_quality(domain, content, metadata or {})
        x, y, z = self.compute_xyz(domain, timestamp, quality)
        
        # Prepare metadata
        meta = metadata or {}
        meta.update({
            "original_path": str(file_path),
            "file_size": file_path.stat().st_size,
            "extracted_timestamp": timestamp,
            "domain": domain,
            "xyz": {"x": x, "y": y, "z": z},
        })
        
        # 1. Store in MemoryStore (existing infrastructure)
        session_id = f"ingest_{file_path.stem}_{int(datetime.now().timestamp())}"
        user_msg = f"Archive Ingestion: {file_path.name} from {domain}"
        assistant_res = content
        
        try:
            await self.memory_store.add_exchange(
                entity_name=self.entity_name,
                session_id=session_id,
                user_message=user_msg,
                response=assistant_res,
                metadata=meta,
                trace_id=f"ingest_{doc_id}"
            )
        except Exception as e:
            logger.error(f"MemoryStore ingestion failed for {file_path}: {e}")
            return False
        
        # 2. Track XYZ coordinates in workbench.db
        conn = sqlite3.connect(self.db_path)
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)
        
        try:
            conn.execute("""
                INSERT OR REPLACE INTO xyz_coordinates 
                (doc_id, entity_name, domain, x_coord, y_coord, z_coord,
                 source_path, archive_path, title, word_count, char_count, content_hash, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc_id, self.entity_name, domain, x, y, z,
                str(file_path), archive_path, file_path.stem,
                len(content.split()), len(content), content_hash,
                json.dumps(meta)
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"XYZ tracking failed for {file_path}: {e}")
            conn.close()
            return False
        finally:
            conn.close()
        
        logger.info(f"Ingested: {file_path.name} (domain={domain}, xyz=({x:.1f},{y:.3f},{z:.2f}))")
        return True
    
    async def ingest_directory(self, dir_path: Path, domain: str, pattern: str = "*.md") -> int:
        """Ingest all matching files in a directory."""
        count = 0
        for file_path in dir_path.rglob(pattern):
            if file_path.is_file():
                if await self.ingest_file(file_path, domain):
                    count += 1
        return count
    
    async def ingest_chatgpt_export(self, zip_path: Path) -> int:
        """Extract and ingest ChatGPT export zip."""
        count = 0
        extract_dir = Path("data/ingestion/processing") / f"chatgpt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(extract_dir)
            
            # Extract timestamp from zip filename
            import re
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', zip_path.name)
            if date_match:
                base_timestamp = datetime.fromisoformat(date_match.group(1)).replace(tzinfo=timezone.utc).timestamp()
            else:
                base_timestamp = datetime.now(timezone.utc).timestamp()
            
            for file_path in extract_dir.rglob("*"):
                if file_path.is_file() and file_path.suffix in ['.json', '.md', '.txt', '.html']:
                    # Override timestamp for chatgpt files
                    meta = {"base_timestamp": base_timestamp, "zip_source": zip_path.name}
                    if await self.ingest_file(file_path, "chatgpt", archive_path=str(zip_path), metadata=meta):
                        count += 1
            
            logger.info(f"ChatGPT export ingested: {count} files from {zip_path.name}")
        except Exception as e:
            logger.error(f"Failed to process ChatGPT export: {e}")
        finally:
            import shutil
            shutil.rmtree(extract_dir, ignore_errors=True)
        
        return count
    
    def query_xyz(self, x_min: float = 0, x_max: float = 4, 
                  y_min: float = 0, y_max: float = 1,
                  z_min: float = 0, z_max: float = 1,
                  limit: int = 50) -> List[Dict]:
        """Query documents by xyz coordinate ranges."""
        conn = sqlite3.connect(self.db_path)
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)
        
        try:
            cursor = conn.execute("""
                SELECT doc_id, domain, x_coord, y_coord, z_coord, title, 
                       word_count, char_count, ingested_at, metadata_json
                FROM xyz_coordinates
                WHERE x_coord BETWEEN ? AND ?
                  AND y_coord BETWEEN ? AND ?
                  AND z_coord BETWEEN ? AND ?
                ORDER BY z_coord DESC, y_coord DESC
                LIMIT ?
            """, (x_min, x_max, y_min, y_max, z_min, z_max, limit))
            
            columns = [d[0] for d in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_stats(self) -> Dict:
        """Get ingestion statistics."""
        conn = sqlite3.connect(self.db_path)
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)
        
        try:
            stats = {}
            cursor = conn.execute("SELECT COUNT(*) FROM xyz_coordinates")
            stats['total_documents'] = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT domain, COUNT(*) FROM xyz_coordinates GROUP BY domain")
            stats['by_domain'] = dict(cursor.fetchall())
            
            cursor = conn.execute("SELECT AVG(z_coord) FROM xyz_coordinates")
            stats['avg_quality'] = cursor.fetchone()[0] or 0
            
            cursor = conn.execute("SELECT MIN(y_coord), MAX(y_coord) FROM xyz_coordinates")
            y_range = cursor.fetchone()
            stats['time_range'] = {'min': y_range[0], 'max': y_range[1]} if y_range[0] else None
            
            return stats
        finally:
            conn.close()


async def main():
    pipeline = XYZIngestionPipeline("kali")
    pipeline.init_xyz_schema()
    
    print("=" * 60)
    print("OMEGA ENGINE — ARCHIVE INGESTION (XYZ COORDINATES)")
    print("=" * 60)
    
    # 1. Ingest coordination archive
    print("\n[1/4] Ingesting coordination archive (July 4-14)...")
    coord_dir = Path("data/archive/coordination/2026-07-04-to-2026-07-14")
    if coord_dir.exists():
        count = await pipeline.ingest_directory(coord_dir, "coordination", "*.md")
        print(f"  Ingested {count} coordination files")
    else:
        print(f"  Archive not found: {coord_dir}")
    
    # 2. Ingest current coordination files
    print("\n[2/4] Ingesting current coordination files...")
    current_dir = Path("data/coordination")
    if current_dir.exists():
        count = await pipeline.ingest_directory(current_dir, "coordination", "*.md")
        print(f"  Ingested {count} current coordination files")
    
    # 3. Ingest ChatGPT export
    print("\n[3/4] Ingesting ChatGPT export...")
    chatgpt_zip = Path("data/archive/chatgpt-exports/8e93b1f249c5ae750605b8609264bb55d4e4bb0fff46f7e2e1a10515bdad0e49-2026-07-16-02-03-17-a48e6f282eb44dfaba96bcaa462b5edd.zip")
    if chatgpt_zip.exists():
        count = await pipeline.ingest_chatgpt_export(chatgpt_zip)
        print(f"  Ingested {count} files from ChatGPT export")
    else:
        print(f"  ChatGPT export not found: {chatgpt_zip}")
    
    # 4. Ingest research docs
    print("\n[4/4] Ingesting research documents...")
    research_dir = Path("docs/research")
    if research_dir.exists():
        count = await pipeline.ingest_directory(research_dir, "research", "*.md")
        print(f"  Ingested {count} research files")
    
    # Print stats
    print("\n" + "=" * 60)
    print("INGESTION STATISTICS")
    print("=" * 60)
    stats = pipeline.get_stats()
    print(f"Total documents: {stats['total_documents']}")
    print(f"By domain: {stats['by_domain']}")
    print(f"Average quality: {stats['avg_quality']:.2f}")
    print(f"Time range: {stats['time_range']}")
    
    # Test xyz query
    print("\n" + "=" * 60)
    print("TEST XYZ QUERY: High-quality coordination docs (z > 0.7)")
    print("=" * 60)
    results = pipeline.query_xyz(x_min=0, x_max=0, z_min=0.7, limit=10)
    for r in results:
        print(f"  [{r['z_coord']:.2f}] {r['title']} ({r['word_count']} words)")


if __name__ == "__main__":
    anyio.run(main)