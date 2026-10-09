#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
# SPDX-License-Identifier: Apache-2.0

"""
Semantic Search for Omega Engine Session Corpus — Torch-Free.

Uses ONNX Runtime with all-MiniLM-L6-v2 quantized model for embeddings.
Integrates with sqlite-vec for vector similarity search.
Pure local inference, M7-compliant.
"""

import json
import sqlite3
import sys
import os
from pathlib import Path
from typing import Any, List, Dict, Optional
import numpy as np

# Try to import ONNX runtime
try:
    import onnxruntime as ort
    ORT_AVAILABLE = True
except ImportError:
    ORT_AVAILABLE = False

# Try to import sqlite-vec
try:
    import sqlite_vec
    VEC_AVAILABLE = True
except ImportError:
    VEC_AVAILABLE = False


class TorchFreeEmbedder:
    """ONNX-based embedder for semantic search — no PyTorch required."""

    def __init__(self, model_path: Path):
        self.model_path = model_path
        self.session = None
        self.tokenizer = None
        self.max_length = 256
        self._load_model()

    def _load_model(self):
        """Load ONNX model and tokenizer."""
        if not ORT_AVAILABLE:
            raise RuntimeError("onnxruntime not available")

        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {self.model_path}")

        # Load ONNX session
        self.session = ort.InferenceSession(str(self.model_path))

        # Load tokenizer
        tokenizer_path = self.model_path.parent / "tokenizer.json"
        if tokenizer_path.exists():
            import tokenizers
            self.tokenizer = tokenizers.Tokenizer.from_file(str(tokenizer_path))
            self.tokenizer.enable_truncation(max_length=self.max_length)
            self.tokenizer.enable_padding(length=self.max_length)
        else:
            raise FileNotFoundError(f"Tokenizer not found: {tokenizer_path}")

    def encode(self, texts: List[str]) -> np.ndarray:
        """
        Encode texts to embeddings.
        Returns: numpy array of shape (len(texts), 384) for all-MiniLM-L6-v2
        """
        if self.session is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded")

        # Tokenize all texts
        encodings = self.tokenizer.encode_batch(texts)
        input_ids = np.array([e.ids for e in encodings], dtype=np.int64)
        attention_mask = np.array([e.attention_mask for e in encodings], dtype=np.int64)
        token_type_ids = np.array([e.type_ids for e in encodings], dtype=np.int64)

        # Run inference
        inputs = {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "token_type_ids": token_type_ids
        }
        outputs = self.session.run(None, inputs)

        # Mean pooling (same as sentence-transformers)
        token_embeddings = outputs[0]  # (batch, seq_len, hidden_dim)
        attention_mask = np.expand_dims(attention_mask, -1)
        sum_embeddings = np.sum(token_embeddings * attention_mask, axis=1)
        sum_mask = np.clip(np.sum(attention_mask, axis=1), a_min=1e-9, a_max=None)
        embeddings = sum_embeddings / sum_mask

        # Normalize
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = embeddings / np.clip(norms, a_min=1e-9, a_max=None)

        return embeddings.astype(np.float32)

    def encode_single(self, text: str) -> np.ndarray:
        """Encode single text to embedding."""
        return self.encode([text])[0]


class SessionSemanticSearch:
    """Semantic search over session corpus using sqlite-vec."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.db_path = repo_root / "data" / "search" / "session_semantic.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.embedder = None
        self._init_embedder()

    def _init_embedder(self):
        """Initialize embedder if available."""
        model_path = self.repo_root / "data" / "models" / "embeddings" / "all-MiniLM-L6-v2.onnx"
        
        # Download model if missing
        if not model_path.exists():
            self._download_model(model_path)
        
        if model_path.exists() and ORT_AVAILABLE:
            try:
                self.embedder = TorchFreeEmbedder(model_path)
            except Exception as e:
                print(f"[semantic] Embedder init failed: {e}", file=sys.stderr)

    def _download_model(self, model_path: Path):
        """Download ONNX model and tokenizer if missing."""
        import urllib.request
        
        model_path.parent.mkdir(parents=True, exist_ok=True)
        
        base_url = "https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/onnx/"
        
        files = {
            model_path.name: base_url + "model.onnx",
            "tokenizer.json": "https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/tokenizer.json",
            "config.json": "https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/config.json"
        }
        
        for filename, url in files.items():
            filepath = model_path.parent / filename
            if not filepath.exists():
                print(f"[semantic] Downloading {filename}...")
                try:
                    urllib.request.urlretrieve(url, filepath)
                    print(f"[semantic] Downloaded {filename}")
                except Exception as e:
                    print(f"[semantic] Failed to download {filename}: {e}", file=sys.stderr)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.enable_load_extension(True)
        if VEC_AVAILABLE:
            sqlite_vec.load(conn)
        conn.row_factory = sqlite3.Row
        return conn

    def build_index(self, force_rebuild: bool = False) -> dict:
        """
        Build semantic index from session corpus.
        Uses FTS5 index as source, adds vector embeddings.
        """
        if not VEC_AVAILABLE:
            return {"status": "error", "message": "sqlite-vec not available"}

        if self.embedder is None:
            return {"status": "error", "message": "Embedder not available (ONNX model missing?)"}

        conn = self._connect()
        cursor = conn.cursor()

        try:
            # Create tables
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS session_vec USING vec0(
                    embedding float[384]
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS session_meta (
                    rowid INTEGER PRIMARY KEY,
                    session_id TEXT,
                    entity TEXT,
                    agent_id TEXT,
                    channel TEXT,
                    model TEXT,
                    timestamp TEXT,
                    intent TEXT,
                    task_current TEXT,
                    focus_chain TEXT,
                    decisions TEXT,
                    continuation TEXT,
                    source TEXT,
                    gnosis_section TEXT
                )
            """)

            # Check if already built
            if not force_rebuild:
                cursor.execute("SELECT COUNT(*) FROM session_meta")
                count = cursor.fetchone()[0]
                if count > 0:
                    return {"status": "exists", "rows": count, "rebuilt": False}

            # Clear existing
            cursor.execute("DELETE FROM session_vec")
            cursor.execute("DELETE FROM session_meta")

            # Get texts from FTS5 index
            fts_db = self.repo_root / "data" / "search" / "session_fts5.db"
            if not fts_db.exists():
                return {"status": "error", "message": "FTS5 index not found. Run session_fts5.py --build first"}

            fts_conn = sqlite3.connect(f"file:{fts_db}?mode=ro", uri=True)
            fts_conn.row_factory = sqlite3.Row
            fts_cursor = fts_conn.cursor()

            fts_cursor.execute("""
                SELECT session_id, entity, agent_id, channel, model,
                       timestamp, intent, task_current, focus_chain,
                       decisions, continuation, source, gnosis_section
                FROM session_fts
                WHERE (decisions != '' OR continuation != '' OR task_current != '')
            """)
            rows = fts_cursor.fetchall()
            fts_conn.close()

            if not rows:
                return {"status": "error", "message": "No sessions with content in FTS5 index"}

            # Prepare texts for embedding
            texts = []
            metas = []
            for row in rows:
                # Combine searchable fields
                combined = " ".join(filter(None, [
                    row["task_current"] or "",
                    row["focus_chain"] or "",
                    row["decisions"] or "",
                    row["continuation"] or ""
                ]))
                if combined.strip():
                    texts.append(combined[:1000])  # Limit length
                    metas.append({
                        "session_id": row["session_id"],
                        "entity": row["entity"],
                        "agent_id": row["agent_id"],
                        "channel": row["channel"],
                        "model": row["model"],
                        "timestamp": row["timestamp"],
                        "intent": row["intent"],
                        "task_current": row["task_current"],
                        "focus_chain": row["focus_chain"],
                        "decisions": row["decisions"],
                        "continuation": row["continuation"],
                        "source": row["source"],
                        "gnosis_section": row["gnosis_section"]
                    })

            if not texts:
                return {"status": "error", "message": "No valid texts to embed"}

            # Generate embeddings in batches
            batch_size = 32
            all_embeddings = []

            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]
                embeddings = self.embedder.encode(batch)
                all_embeddings.append(embeddings)

            embeddings = np.vstack(all_embeddings)

            # Insert into sqlite-vec
            for i, (embedding, meta) in enumerate(zip(embeddings, metas)):
                # Insert metadata
                cursor.execute("""
                    INSERT INTO session_meta (
                        session_id, entity, agent_id, channel, model,
                        timestamp, intent, task_current, focus_chain,
                        decisions, continuation, source, gnosis_section
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    meta["session_id"], meta["entity"], meta["agent_id"],
                    meta["channel"], meta["model"], meta["timestamp"],
                    meta["intent"], meta["task_current"], meta["focus_chain"],
                    meta["decisions"], meta["continuation"], meta["source"],
                    meta["gnosis_section"]
                ))
                rowid = cursor.lastrowid

                # Insert vector (sqlite-vec uses rowid for linking)
                cursor.execute("INSERT INTO session_vec(rowid, embedding) VALUES (?, ?)",
                             (rowid, embedding.tobytes()))

            conn.commit()

            cursor.execute("SELECT COUNT(*) FROM session_meta")
            total = cursor.fetchone()[0]

            return {
                "status": "built",
                "total_rows": total,
                "embedding_dim": 384,
                "model": "all-MiniLM-L6-v2 (ONNX)",
                "rebuilt": True
            }

        finally:
            conn.close()

    def search(self, query: str, limit: int = 10, entity: str = None) -> list[dict]:
        """
        Semantic search using vector similarity.
        """
        if not VEC_AVAILABLE:
            return [{"error": "sqlite-vec not available"}]

        if self.embedder is None:
            return [{"error": "Embedder not available"}]

        conn = self._connect()
        cursor = conn.cursor()

        try:
            # Encode query
            query_embedding = self.embedder.encode_single(query)

            # Build SQL
            sql = """
                SELECT
                    m.session_id, m.entity, m.agent_id, m.channel, m.model,
                    m.timestamp, m.intent, m.task_current, m.focus_chain,
                    m.decisions, m.continuation, m.source, m.gnosis_section,
                    vec_distance_cosine(v.embedding, ?) as distance
                FROM session_vec v
                JOIN session_meta m ON v.rowid = m.rowid
            """
            params = [query_embedding.tobytes()]

            if entity:
                sql += " WHERE m.entity = ?"
                params.append(entity)

            sql += " ORDER BY distance ASC LIMIT ?"
            params.append(limit)

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            results = []
            for row in rows:
                # Convert distance to similarity (1 - distance for cosine)
                similarity = 1.0 - row["distance"]

                results.append({
                    "session_id": row["session_id"],
                    "entity": row["entity"],
                    "agent_id": row["agent_id"],
                    "channel": row["channel"],
                    "model": row["model"],
                    "timestamp": row["timestamp"],
                    "intent": row["intent"],
                    "task_current": row["task_current"][:200] if row["task_current"] else "",
                    "focus_chain": row["focus_chain"][:200] if row["focus_chain"] else "",
                    "decisions": row["decisions"][:200] if row["decisions"] else "",
                    "continuation": row["continuation"][:200] if row["continuation"] else "",
                    "source": row["source"],
                    "gnosis_section": row["gnosis_section"],
                    "similarity": round(similarity, 4),
                    "distance": round(row["distance"], 4)
                })

            return results

        finally:
            conn.close()

    def hybrid_search(self, query: str, limit: int = 10, entity: str = None, alpha: float = 0.5) -> list[dict]:
        """
        Hybrid search: RRF fusion of FTS5 (lexical) + vec0 (semantic).
        alpha: weight for semantic (0.5 = equal weight)
        """
        # Get lexical results
        from session_fts5 import SessionFTS5
        fts = SessionFTS5(self.repo_root)
        lexical_results = fts.search(query, limit=limit*2, entity=entity)

        # Get semantic results
        semantic_results = self.search(query, limit=limit*2, entity=entity)

        # Filter out error results
        lexical_results = [r for r in lexical_results if "session_id" in r]
        semantic_results = [r for r in semantic_results if "session_id" in r]

        # RRF fusion
        k = 60  # RRF constant
        scores = {}

        for rank, r in enumerate(lexical_results):
            sid = r["session_id"]
            scores[sid] = scores.get(sid, 0) + (1 - alpha) * (1.0 / (k + rank + 1))

        for rank, r in enumerate(semantic_results):
            sid = r["session_id"]
            scores[sid] = scores.get(sid, 0) + alpha * (1.0 / (k + rank + 1))

        # Sort by combined score
        sorted_sids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

        # Build combined results
        all_results = {r["session_id"]: r for r in lexical_results + semantic_results}
        combined = []
        for sid in sorted_sids[:limit]:
            if sid in all_results:
                r = all_results[sid].copy()
                r["rrf_score"] = round(scores[sid], 6)
                combined.append(r)

        return combined

    def get_stats(self) -> dict:
        """Get index statistics."""
        if not VEC_AVAILABLE:
            return {"status": "sqlite-vec not available"}

        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT COUNT(*) FROM session_meta")
            total = cursor.fetchone()[0]

            cursor.execute("SELECT entity, COUNT(*) FROM session_meta GROUP BY entity ORDER BY COUNT(*) DESC LIMIT 10")
            by_entity = dict(cursor.fetchall())

            return {
                "total_rows": total,
                "top_entities": by_entity,
                "db_path": str(self.db_path),
                "db_size_mb": round(self.db_path.stat().st_size / (1024 * 1024), 2) if self.db_path.exists() else 0,
                "embedding_dim": 384,
                "model": "all-MiniLM-L6-v2 (ONNX)"
            }
        finally:
            conn.close()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Session Semantic Search (Torch-Free)")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root")
    parser.add_argument("--build", action="store_true", help="Build/rebuild index")
    parser.add_argument("--force", action="store_true", help="Force rebuild")
    parser.add_argument("--search", type=str, help="Semantic search query")
    parser.add_argument("--hybrid", type=str, help="Hybrid search query (RRF)")
    parser.add_argument("--limit", type=int, default=10, help="Result limit")
    parser.add_argument("--entity", type=str, help="Filter by entity")
    parser.add_argument("--alpha", type=float, default=0.5, help="Hybrid weight for semantic (0-1)")
    parser.add_argument("--stats", action="store_true", help="Show index stats")

    args = parser.parse_args()

    if not VEC_AVAILABLE:
        print(json.dumps({"error": "sqlite-vec not available. Install with: pip install sqlite-vec"}))
        return

    if not ORT_AVAILABLE:
        print(json.dumps({"error": "onnxruntime not available. Install with: pip install onnxruntime"}))
        return

    semantic = SessionSemanticSearch(args.repo_root)

    if args.build or args.force:
        result = semantic.build_index(force_rebuild=args.force)
        print(json.dumps(result, indent=2))
        return

    if args.search:
        results = semantic.search(args.search, limit=args.limit, entity=args.entity)
        print(json.dumps(results, indent=2))
        return

    if args.hybrid:
        results = semantic.hybrid_search(args.hybrid, limit=args.limit, entity=args.entity, alpha=args.alpha)
        print(json.dumps(results, indent=2))
        return

    if args.stats:
        stats = semantic.get_stats()
        print(json.dumps(stats, indent=2))
        return

    parser.print_help()


if __name__ == "__main__":
    main()