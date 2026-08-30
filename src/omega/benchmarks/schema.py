# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# ⬡ OMEGA ⬡ BENCHMARK SCHEMA ⬡ v1.0
# SQLite schema and helpers for benchmark_runs table.
# Single source of truth for data model.

import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

DB_PATH = Path("data/benchmarks/benchmark_runs.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS benchmark_runs (
    run_id TEXT PRIMARY KEY,
    timestamp INTEGER NOT NULL,
    model_id TEXT NOT NULL,
    model_hash TEXT NOT NULL,
    provider TEXT,
    task_category TEXT NOT NULL,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    latency_ms INTEGER,
    ttft_ms INTEGER,
    quality_score REAL,
    cost_usd REAL,
    energy_j REAL,
    thermal_state TEXT,
    privacy_tag INTEGER DEFAULT 0,
    success INTEGER DEFAULT 1,
    error_type TEXT
);

CREATE INDEX IF NOT EXISTS idx_runs_task_quality ON benchmark_runs(task_category, quality_score);
CREATE INDEX IF NOT EXISTS idx_runs_model ON benchmark_runs(model_id);
CREATE INDEX IF NOT EXISTS idx_runs_thermal ON benchmark_runs(thermal_state);
CREATE INDEX IF NOT EXISTS idx_runs_provider ON benchmark_runs(provider);
CREATE INDEX IF NOT EXISTS idx_runs_timestamp ON benchmark_runs(timestamp);
"""

# ── Schema Version ────────────────────────────────────────────────────
SCHEMA_VERSION = 1

MIGRATIONS = {
    1: SCHEMA,
    # Future migrations go here:
    # 2: "ALTER TABLE benchmark_runs ADD COLUMN new_column TEXT;",
}


def init_db(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Initialize database with schema and migrations."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Check current version
    cursor = conn.execute("PRAGMA user_version")
    current_version = cursor.fetchone()[0]

    if current_version == 0:
        # Fresh database
        conn.executescript(SCHEMA)
        conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
    elif current_version < SCHEMA_VERSION:
        # Run migrations
        for v in range(current_version + 1, SCHEMA_VERSION + 1):
            if v in MIGRATIONS:
                conn.executescript(MIGRATIONS[v])
        conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")

    conn.commit()
    return conn


@contextmanager
def get_db(db_path: Path = DB_PATH):
    """Context manager for database connections."""
    conn = init_db(db_path)
    try:
        yield conn
    finally:
        conn.close()


# ── Query Helpers ─────────────────────────────────────────────────────
def insert_run(conn: sqlite3.Connection, run: Dict[str, Any]) -> None:
    """Insert a benchmark run. Expects dict with all schema columns."""
    columns = ", ".join(run.keys())
    placeholders = ", ".join(["?"] * len(run))
    conn.execute(
        f"INSERT INTO benchmark_runs ({columns}) VALUES ({placeholders})", tuple(run.values())
    )
    conn.commit()


def query_runs(
    db_path: Path = DB_PATH,
    task_category: Optional[str] = None,
    model_id: Optional[str] = None,
    provider: Optional[str] = None,
    thermal_state: Optional[str] = None,
    min_quality: Optional[float] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """Query benchmark runs with filters."""
    with get_db(db_path) as conn:
        conditions = []
        params = []

        if task_category:
            conditions.append("task_category = ?")
            params.append(task_category)
        if model_id:
            conditions.append("model_id = ?")
            params.append(model_id)
        if provider:
            conditions.append("provider = ?")
            params.append(provider)
        if thermal_state:
            conditions.append("thermal_state = ?")
            params.append(thermal_state)
        if min_quality is not None:
            conditions.append("quality_score >= ?")
            params.append(min_quality)

        where = "WHERE " + " AND ".join(conditions) if conditions else ""
        params.append(limit)

        query = f"""
            SELECT * FROM benchmark_runs
            {where}
            ORDER BY timestamp DESC
            LIMIT ?
        """
        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def get_pareto_frontier(
    db_path: Path = DB_PATH,
    execution_mode: str = "local",  # "local" or "cloud"
    task_category: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Get Pareto frontier for routing decisions."""
    with get_db(db_path) as conn:
        provider_filter = (
            "provider IS NULL" if execution_mode == "local" else "provider IS NOT NULL"
        )
        task_filter = f"AND task_category = '{task_category}'" if task_category else ""

        query = f"""
            SELECT
                model_id,
                AVG(quality_score) as avg_quality,
                AVG(latency_ms) as avg_latency,
                AVG(energy_j) as avg_energy,
                AVG(cost_usd) as avg_cost,
                COUNT(*) as n_runs
            FROM benchmark_runs
            WHERE {provider_filter} {task_filter}
            GROUP BY model_id
            HAVING n_runs >= 3
        """
        cursor = conn.execute(query)
        return [dict(row) for row in cursor.fetchall()]


# ── Export Helpers ────────────────────────────────────────────────────
def export_csv(db_path: Path = DB_PATH, output_path: Path = Path("benchmarks_export.csv")):
    """Export all runs to CSV."""
    with get_db(db_path) as conn:
        cursor = conn.execute("SELECT * FROM benchmark_runs ORDER BY timestamp")
        rows = cursor.fetchall()

        if rows:
            import csv

            with open(output_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(rows[0].keys())
                writer.writerows(rows)
            print(f"Exported {len(rows)} runs to {output_path}")


def export_json(db_path: Path = DB_PATH, output_path: Path = Path("benchmarks_export.json")):
    """Export all runs to JSON."""
    with get_db(db_path) as conn:
        cursor = conn.execute("SELECT * FROM benchmark_runs ORDER BY timestamp")
        rows = [dict(row) for row in cursor.fetchall()]

        import json

        with open(output_path, "w") as f:
            json.dump(rows, f, indent=2)
        print(f"Exported {len(rows)} runs to {output_path}")


# ── CLI ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m src.omega.benchmarks.schema <command>")
        print("Commands: init, export-csv, export-json, pareto-local, pareto-cloud")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "init":
        init_db()
        print(f"Database initialized at {DB_PATH}")
    elif cmd == "export-csv":
        export_csv()
    elif cmd == "export-json":
        export_json()
    elif cmd == "pareto-local":
        results = get_pareto_frontier(execution_mode="local")
        for r in results:
            print(
                f"{r['model_id']}: qual={r['avg_quality']:.2f}, lat={r['avg_latency']:.0f}ms, energy={r['avg_energy']:.2f}J, n={r['n_runs']}"
            )
    elif cmd == "pareto-cloud":
        results = get_pareto_frontier(execution_mode="cloud")
        for r in results:
            print(
                f"{r['model_id']}: qual={r['avg_quality']:.2f}, lat={r['avg_latency']:.0f}ms, cost=${r['avg_cost']:.4f}, n={r['n_runs']}"
            )
    else:
        print(f"Unknown command: {cmd}")
