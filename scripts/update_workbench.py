import sqlite3
from pathlib import Path

DB_PATH = Path("data/workbench/workbench.db")

def update():
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    
    decisions = [
        ('prj_provider_fabric', 'Embedding model selection for resource-constrained Zen 2 CPU (14GB RAM).', 'Adopted BAAI/bge-base-en-v1.5 (768-dim, 137MB) via fastembed ONNX CPU as the primary embedding model, utilizing Hybrid Search (FTS5 + Qdrant) with RRF.', 'active', 'Optimal balance of retrieval quality and CPU latency for Zen 2 architecture.'),
        ('prj_engine_core', 'Root partition exhaustion (100% used) causing SQLite journal and task() tool failures.', 'Executed Sovereign Storage Remediation: migrated 6GB of archives/logs to omega_library, merged legacy GGUFs, purged 2.5GB of useless CUDA libraries on CPU-only system.', 'active', 'Restored system stability and prevented database corruption by reclaiming root space.')
    ]
    
    for d in decisions:
        cur.execute("INSERT INTO decisions (project_id, context, decision, status, rationale, created_at) VALUES (?, ?, ?, ?, ?, datetime('now'))", d)
    
    cur.execute("UPDATE artifacts SET mining_status = 'mined', mined_at = datetime('now') WHERE id = 'art_positioning'")
    
    conn.commit()
    conn.close()
    print("Workbench DB updated successfully.")

if __name__ == "__main__":
    update()
