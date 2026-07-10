# 🔱 Omega Engine — Sovereignty Ratio Query (D203)
# ⬡ OMEGA ⬡ RESEARCHER ⬡ hy3-free ⬡ opencode ⬡ trc_research
#
# Queries MetricsDB performance table for local vs cloud inference ratio.
# The `is_cloud` field is set per-response by the ModelGateway (M22 provenance).
# Local=0, Cloud=1.
#
# [id-soft: quake3-1999] cvar — sovereignty ratio as a cvar-table metric

import logging
import sqlite3
from pathlib import Path
from typing import Dict, Any
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Default MetricsDB location (matches MetricsDB class default)
METRICS_DB_PATH = Path("data/observability/metrics.db")


def get_sovereignty_ratio(
    db_path: str | Path = METRICS_DB_PATH,
    since_days: int | None = None,
) -> Dict[str, Any]:
    """
    Query the local vs cloud inference ratio from MetricsDB.

    Args:
        db_path: Path to the MetricsDB SQLite database.
        since_days: Optional — only count inferences from last N days.

    Returns:
        Dict with keys: local_count, cloud_count, total, ratio_local,
        ratio_cloud, provider_breakdown, since, generated_at.
        Returns empty counts if DB doesn't exist or has no data.
    """
    db = Path(db_path)
    if not db.exists():
        logger.warning(f"MetricsDB not found at {db_path}")
        return {
            "local_count": 0,
            "cloud_count": 0,
            "total": 0,
            "ratio_local": 0.0,
            "ratio_cloud": 0.0,
            "provider_breakdown": {},
            "since": "no_data",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    try:
        conn = sqlite3.connect(str(db))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Check if performance table exists
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='performance'"
        )
        if not cur.fetchone():
            conn.close()
            return {
                "local_count": 0,
                "cloud_count": 0,
                "total": 0,
                "ratio_local": 0.0,
                "ratio_cloud": 0.0,
                "provider_breakdown": {},
                "since": "no_table",
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }

        # Time filter
        since_ts = None
        if since_days:
            since_ts = (
                datetime.now(timezone.utc).timestamp() - since_days * 86400
            )

        # Aggregate counts
        if since_ts:
            cur.execute(
                """
                SELECT 
                    SUM(CASE WHEN is_cloud = 0 THEN 1 ELSE 0 END) as local_count,
                    SUM(CASE WHEN is_cloud = 1 THEN 1 ELSE 0 END) as cloud_count,
                    COUNT(*) as total
                FROM performance
                WHERE ts >= ?
                """,
                (since_ts,),
            )
        else:
            cur.execute(
                """
                SELECT 
                    SUM(CASE WHEN is_cloud = 0 THEN 1 ELSE 0 END) as local_count,
                    SUM(CASE WHEN is_cloud = 1 THEN 1 ELSE 0 END) as cloud_count,
                    COUNT(*) as total
                FROM performance
                """
            )

        row = cur.fetchone()
        local_count = row["local_count"] or 0
        cloud_count = row["cloud_count"] or 0
        total = row["total"] or 0

        # Provider breakdown
        if since_ts:
            cur.execute(
                """
                SELECT provider, is_cloud, COUNT(*) as cnt
                FROM performance
                WHERE ts >= ?
                GROUP BY provider, is_cloud
                ORDER BY cnt DESC
                """,
                (since_ts,),
            )
        else:
            cur.execute(
                """
                SELECT provider, is_cloud, COUNT(*) as cnt
                FROM performance
                GROUP BY provider, is_cloud
                ORDER BY cnt DESC
                """
            )

        provider_breakdown = {}
        for prow in cur.fetchall():
            provider_breakdown[prow["provider"]] = {
                "count": prow["cnt"],
                "is_cloud": bool(prow["is_cloud"]),
            }

        conn.close()

        ratio_local = local_count / max(total, 1)
        ratio_cloud = cloud_count / max(total, 1)

        return {
            "local_count": local_count,
            "cloud_count": cloud_count,
            "total": total,
            "ratio_local": round(ratio_local, 4),
            "ratio_cloud": round(ratio_cloud, 4),
            "provider_breakdown": provider_breakdown,
            "since": f"last_{since_days}_days" if since_days else "all_time",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    except sqlite3.Error as e:
        logger.error(f"MetricsDB query failed: {e}")
        return {
            "local_count": 0,
            "cloud_count": 0,
            "total": 0,
            "ratio_local": 0.0,
            "ratio_cloud": 0.0,
            "provider_breakdown": {},
            "error": str(e),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
