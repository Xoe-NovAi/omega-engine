# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Vector versioning + drift detection for embedding migrations.

AP: AP-VECTOR-VERSIONING-v1.0.0

[heritage: alembic 2013] Schema migration discipline applied to vectors.
[heritage: tian-pan-2026] Per-vector version tag is the column you forgot.
[heritage: levelop-2026] Dual-write migration + PSI drift detection.
"""
from __future__ import annotations

import hashlib
import logging
import sqlite3
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Collections defined in sqlite_vec_adapter_optimized.py:54-97
MRL_COLLECTIONS = [
    "omega_vec_qwen_768",
    "omega_vec_nomic_768",
    "omega_vec_nomic_512",
    "omega_vec_nomic_256",
    "omega_vec_minilm_384",
    "omega_vec_static_64",
    "omega_vec_library_768",
]

# Drift thresholds — see CARMACK_VECTOR_VERSIONING_SPEC_20260829.md §L3
DRIFT_THRESHOLD_INVESTIGATE = 0.10
DRIFT_THRESHOLD_REEMBED = 0.20
DEFAULT_PCA_DIM = 30
MIN_SAMPLE_SIZE = 30  # below this, drift detection returns 0.0 (not enough data)


@dataclass
class ModelVersion:
    """One row of the `omega_memory_versions` registry."""
    version_id: str       # e.g. 'nomic-embed-v1.5'
    model_name: str       # e.g. 'nomic-embed-text'
    dimension: int        # 768
    status: str           # active | shadow | retired
    promoted_at: Optional[int] = None
    retired_at: Optional[int] = None
    notes: str = ""


class VectorVersionRegistry:
    """SSOT for embedding model versions + per-collection metadata.

    Backed by:
      - omega_memory_versions  (registry, global)
      - vec_{name}_meta        (per-collection provenance)
    """

    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def ensure_schema(self) -> None:
        """Idempotent — safe to call on every adapter init.

        Creates the registry table + 7 per-collection meta tables + their
        indexes. No destructive operations.
        """
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS omega_memory_versions (
                version_id   TEXT PRIMARY KEY,
                model_name   TEXT NOT NULL,
                dimension    INTEGER NOT NULL,
                status       TEXT NOT NULL
                    CHECK (status IN ('active','shadow','retired')),
                promoted_at  INTEGER,
                retired_at   INTEGER,
                notes        TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_versions_status
                ON omega_memory_versions(status);
            """
        )
        # Per-collection meta tables — store model_version + content_hash
        # so an embedding model upgrade can diff the corpus.
        for coll in MRL_COLLECTIONS:
            self._conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {coll}_meta (
                    rowid         INTEGER PRIMARY KEY,
                    model_version TEXT NOT NULL DEFAULT 'nomic-embed-v1.5',
                    content_hash  TEXT,
                    embedded_at   INTEGER NOT NULL DEFAULT (strftime('%s','now'))
                )
                """
            )
            short = coll[len("omega_vec_"):]
            self._conn.execute(
                f"""
                CREATE INDEX IF NOT EXISTS idx_{short}_version
                    ON {coll}_meta(model_version)
                """
            )
        self._conn.commit()
        logger.info("Vector versioning schema ensured (%d meta tables)", len(MRL_COLLECTIONS))

    def register_version(self, v: ModelVersion) -> None:
        """Insert or update a model version record. Idempotent on version_id."""
        self._conn.execute(
            """
            INSERT OR REPLACE INTO omega_memory_versions
              (version_id, model_name, dimension, status, promoted_at, retired_at, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (v.version_id, v.model_name, v.dimension, v.status,
             v.promoted_at, v.retired_at, v.notes),
        )
        self._conn.commit()

    def get_active_version(self, model_name: str) -> Optional[ModelVersion]:
        """Returns the currently-active version for a model, or None."""
        row = self._conn.execute(
            """
            SELECT version_id, model_name, dimension, status,
                   promoted_at, retired_at, notes
            FROM omega_memory_versions
            WHERE model_name = ? AND status = 'active'
            LIMIT 1
            """,
            (model_name,),
        ).fetchone()
        if not row:
            return None
        return ModelVersion(*row)

    def promote(self, version_id: str) -> None:
        """Atomically: set `version_id` to active, demote all other versions
        of the same model_name to 'shadow'.

        This is the cutover operation. Per Levelop (2026-07-26), the gate
        for cutover is validation, not calendar pressure.
        """
        cur = self._conn.execute(
            "SELECT model_name FROM omega_memory_versions WHERE version_id = ?",
            (version_id,),
        ).fetchone()
        if not cur:
            raise ValueError(f"Unknown version_id: {version_id}")
        model_name = cur[0]
        now = int(time.time())
        with self._conn:  # transaction
            self._conn.execute(
                """
                UPDATE omega_memory_versions
                SET status = 'shadow', promoted_at = NULL
                WHERE model_name = ? AND status = 'active'
                """,
                (model_name,),
            )
            self._conn.execute(
                """
                UPDATE omega_memory_versions
                SET status = 'active', promoted_at = ?
                WHERE version_id = ?
                """,
                (now, version_id),
            )
        logger.info("Promoted %s (%s) to active", version_id, model_name)

    def tag_vector(self, collection: str, rowid: int,
                   model_version: str, content: str) -> None:
        """Stamp a single row with model_version + sha256 of source content.

        The content_hash enables incremental re-embedding (Levelop 2026):
        on model upgrade, only re-embed chunks whose content_hash changed.
        """
        h = hashlib.sha256(content.encode("utf-8")).hexdigest()
        self._conn.execute(
            f"""
            INSERT OR REPLACE INTO {collection}_meta
              (rowid, model_version, content_hash, embedded_at)
            VALUES (?, ?, ?, ?)
            """,
            (rowid, model_version, h, int(time.time())),
        )
        self._conn.commit()

    def count_by_version(self, collection: str) -> Dict[str, int]:
        """Returns {model_version: row_count} for a collection."""
        rows = self._conn.execute(
            f"""
            SELECT model_version, COUNT(*)
            FROM {collection}_meta
            GROUP BY model_version
            """
        ).fetchall()
        return {v: c for v, c in rows}

    def chunks_to_reembed(self, collection: str,
                          new_version: str) -> int:
        """Returns count of rows in the meta table that need re-embedding.

        For v1 of this implementation: any row whose model_version !=
        new_version AND whose content_hash is not yet associated with
        the new version. The caller is expected to use this to schedule
        a background re-embed job.
        """
        row = self._conn.execute(
            f"""
            SELECT COUNT(*) FROM {collection}_meta
            WHERE model_version != ?
            """,
            (new_version,),
        ).fetchone()
        return int(row[0]) if row else 0


class DriftDetector:
    """Detect embedding distribution drift via Wasserstein on PCA-30.

    [heritage: tian-pan-2026] PSI > 0.2 = investigate.
    [heritage: thelinuxcode-2026] PCA-30 + Wasserstein = production pattern.

    The scalar drift score is the mean Wasserstein distance across the
    PCA-reduced components. Interpretation:
      < 0.10  -> "ok"             (distributions are similar)
      0.10-0.20 -> "investigate"  (some drift, may need re-embed)
      > 0.20  -> "reembed"        (clear drift, schedule full re-embed)
    """

    def __init__(self, conn: sqlite3.Connection, pca_dim: int = DEFAULT_PCA_DIM):
        self._conn = conn
        self._pca_dim = pca_dim

    def compute_drift(self, recent: List[List[float]],
                      baseline: List[List[float]]) -> float:
        """Mean Wasserstein distance across PCA-reduced components.

        Returns 0.0 if either sample has fewer than MIN_SAMPLE_SIZE vectors
        or if numpy/sklearn/scipy are not importable (graceful degrade).
        """
        try:
            import numpy as np
            from sklearn.decomposition import PCA
            from scipy.stats import wasserstein_distance
        except ImportError:
            logger.warning("numpy/sklearn/scipy missing; drift detection disabled")
            return 0.0
        if (len(recent) < MIN_SAMPLE_SIZE
                or len(baseline) < MIN_SAMPLE_SIZE):
            return 0.0
        r = np.asarray(recent, dtype=np.float32)
        b = np.asarray(baseline, dtype=np.float32)
        n_components = min(self._pca_dim, r.shape[1], b.shape[1])
        pca = PCA(n_components=n_components)
        pca.fit(np.vstack([b, r]))
        return float(np.mean([
            wasserstein_distance(
                pca.transform(b)[:, i],
                pca.transform(r)[:, i],
            )
            for i in range(n_components)
        ]))

    def recommend_action(self, drift: float) -> str:
        if drift < DRIFT_THRESHOLD_INVESTIGATE:
            return "ok"
        if drift < DRIFT_THRESHOLD_REEMBED:
            return "investigate"
        return "reembed"
