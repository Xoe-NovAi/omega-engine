import sqlite3
import os

DB_PATH = "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/workbench/workbench.db"

def update_workbench():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Create Project
    cursor.execute(
        "INSERT OR IGNORE INTO projects (name, status, priority, description) VALUES (?, ?, ?, ?)",
        ("Sovereign Ingestion Hardening", "active", "P0", "Implementation of the stripped S3 Ingestion Pipeline (T1-T9)")
    )
    
    cursor.execute("SELECT id FROM projects WHERE name=?", ("Sovereign Ingestion Hardening",))
    project_id = cursor.fetchone()[0]

    # 2. Add Work Items
    tasks = [
        ("T1: Double-Fsync", "P0", "backlog", "Engineering"),
        ("T2: IngestionWorker", "P0", "backlog", "Engineering"),
        ("T3: WebScraper", "P0", "backlog", "Engineering"),
        ("T4: TriangulationVerifier", "P1", "backlog", "Integration"),
        ("T5: QualityScorer", "P1", "backlog", "Validation"),
        ("T6: Greek Normalize", "P2", "backlog", "Linguistics"),
        ("T7: Branding Purge", "P1", "backlog", "Governance"),
        ("T8: PLO Deferral", "P3", "backlog", "Governance"),
        ("T9: Blueprint Sync", "P1", "backlog", "Governance"),
    ]

    for title, priority, status, workstream in tasks:
        cursor.execute(
            "INSERT INTO work_items (project_id, title, priority, status, workstream) VALUES (?, ?, ?, ?, ?)",
            (project_id, title, priority, status, workstream)
        )

    conn.commit()
    conn.close()
    print("Workbench DB updated successfully.")

if __name__ == "__main__":
    update_workbench()
