import sqlite3
from pathlib import Path

DB_PATH = Path.home() / ".local/share/opencode/opencode.db"

def analyze():
    if not DB_PATH.exists():
        print(f"Error: DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    print("═══ OPENCODE DB FORENSICS ═══")
    
    try:
        print("\n--- Table Schema: sessions ---")
        cur.execute("PRAGMA table_info(sessions)")
        for col in cur.fetchall(): print(col)

        print("\n--- Table Schema: tasks ---")
        cur.execute("PRAGMA table_info(tasks)")
        for col in cur.fetchall(): print(col)

        print("\n--- Last 5 Sessions ---")
        cur.execute("SELECT id, created_at, status FROM sessions ORDER BY created_at DESC LIMIT 5")
        for row in cur.fetchall(): print(row)

        print("\n--- Last 5 Tasks ---")
        cur.execute("SELECT id, session_id, created_at FROM tasks ORDER BY created_at DESC LIMIT 5")
        for row in cur.fetchall(): print(row)

        print("\n--- Checking for Orphaned Tasks ---")
        cur.execute("SELECT COUNT(*) FROM tasks WHERE session_id NOT IN (SELECT id FROM sessions)")
        print(f"Orphaned Tasks: {cur.fetchone()[0]}")

    except sqlite3.OperationalError as e:
        print(f"DB Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    analyze()
