import sqlite3
import shutil
from pathlib import Path

DB_PATH = Path("data/workbench/workbench.db")
BACKUP_PATH = Path("data/workbench/workbench.db.bak")

def migrate():
    print("🛡️ Backing up database...")
    shutil.copy(DB_PATH, BACKUP_PATH)

    try:
        print("🚀 Executing migration...")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Add domain column
        cursor.execute("ALTER TABLE projects ADD COLUMN domain TEXT NOT NULL DEFAULT 'omega_engine';")
        
        # Update schema version (assuming schema_version table exists)
        try:
            cursor.execute("INSERT INTO schema_version (version, description) VALUES (2, 'Add domain column to projects table');")
        except sqlite3.OperationalError:
            # Create table if it doesn't exist
            cursor.execute("CREATE TABLE schema_version (version INTEGER PRIMARY KEY, description TEXT);")
            cursor.execute("INSERT INTO schema_version (version, description) VALUES (2, 'Add domain column to projects table');")
            
        conn.commit()
        conn.close()
        print("✅ Migration successful.")

        # Seed test data
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE projects SET domain = 'foundation_community' WHERE id = 'prj_community_tool';")
        cursor.execute("UPDATE projects SET domain = 'custom_stack' WHERE id = 'prj_arcana_nova';")
        conn.commit()
        conn.close()
        print("🌱 Seeding test domains complete.")

        # Validation
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, domain FROM projects;")
        print("\n📊 Validation Report:")
        for row in cursor.fetchall():
            print(row)
        conn.close()

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("🔄 Rolling back...")
        shutil.move(BACKUP_PATH, DB_PATH)
        exit(1)

if __name__ == "__main__":
    migrate()
