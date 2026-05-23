#!/usr/bin/env python3
"""
Omega Research Metadata Database — Initialization & Sync Script
===============================================================
Creates and maintains the SQLite database for tracking all research artifacts.
Includes FTS5 full-text search, schema versioning, and automated sync from docs.

Usage:
    python3 scripts/init-research-db.py              # Initialize database
    python3 scripts/init-research-db.py --seed       # Initialize + seed from current docs
    python3 scripts/init-research-db.py --sync       # Sync existing DB with current docs
    python3 scripts/init-research-db.py --query TAG  # Query by tag
    python3 scripts/init-research-db.py --stale      # List stale documents
    python3 scripts/init-research-db.py --stats      # Show database statistics
"""

import sqlite3
import os
import sys
import re
import glob
import json
from datetime import datetime

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "docs", "research", "internal-discovery", "DB", "research.db"
)
RESEARCH_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "docs", "research"
)

SCHEMA_VERSION = 3

SCHEMA_SQL = f"""
-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT DEFAULT (datetime('now')),
    description TEXT
);

INSERT OR IGNORE INTO schema_version (version, description)
VALUES ({SCHEMA_VERSION}, 'Schema v3: Added work_items table for unified task tracking, migration support');

-- Research documents registry (enhanced)
CREATE TABLE IF NOT EXISTS research_documents (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    status TEXT CHECK(status IN ('complete','in_progress','pending','blocked','draft','in_review','superseded','archived')),
    urgency TEXT CHECK(urgency IN ('critical','high','strategic','low')),
    domain TEXT,
    file_path TEXT UNIQUE NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT,
    author TEXT DEFAULT 'Sovereign Master Researcher',
    confidence INTEGER CHECK(confidence BETWEEN 1 AND 10),
    sovereignty_score INTEGER CHECK(sovereignty_score BETWEEN 1 AND 10),
    ram_mb INTEGER DEFAULT 0,
    cpu_cores REAL DEFAULT 0,
    latency_ms INTEGER DEFAULT 0,
    superseded_by TEXT,
    word_count INTEGER DEFAULT 0
);

-- Tags for filtering and graph analysis
CREATE TABLE IF NOT EXISTS tags (
    document_id TEXT REFERENCES research_documents(id) ON DELETE CASCADE,
    tag TEXT NOT NULL,
    PRIMARY KEY (document_id, tag)
);

-- Cross-document links (bidirectional)
CREATE TABLE IF NOT EXISTS related_documents (
    source_id TEXT REFERENCES research_documents(id) ON DELETE CASCADE,
    target_id TEXT REFERENCES research_documents(id) ON DELETE CASCADE,
    relationship TEXT DEFAULT 'related',
    PRIMARY KEY (source_id, target_id)
);

-- Source provenance (URLs, legacy paths, papers)
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id TEXT REFERENCES research_documents(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    source_type TEXT DEFAULT 'web' CHECK(source_type IN ('web','legacy_file','paper','api_doc','other')),
    accessed_at TEXT DEFAULT (datetime('now'))
);

-- Internal discovery tracking
CREATE TABLE IF NOT EXISTS discoveries (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    status TEXT CHECK(status IN ('complete','in_progress','pending','blocked')),
    lead TEXT,
    file_path TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT
);

-- Work items for unified task tracking (Phase 1 — Systems Discovery)
CREATE TABLE IF NOT EXISTS work_items (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'backlog'
        CHECK(status IN ('backlog','ready','in_progress','review','done','archived','blocked')),
    priority TEXT NOT NULL DEFAULT 'P3'
        CHECK(priority IN ('P0','P1','P2','P3','P4')),
    source_entity TEXT,
    source_document TEXT REFERENCES research_documents(id),
    depends_on TEXT,
    tags TEXT,
    trace_id TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_work_items_status ON work_items(status);
CREATE INDEX IF NOT EXISTS idx_work_items_priority ON work_items(priority);
CREATE INDEX IF NOT EXISTS idx_work_items_entity ON work_items(source_entity);

-- Document lifecycle events
CREATE TABLE IF NOT EXISTS lifecycle_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id TEXT REFERENCES research_documents(id) ON DELETE CASCADE,
    event_type TEXT CHECK(event_type IN ('created','reviewed','completed','superseded','archived','stale_flagged')),
    timestamp TEXT DEFAULT (datetime('now')),
    notes TEXT
);

-- Full-Text Search (FTS5) for content indexing
CREATE VIRTUAL TABLE IF NOT EXISTS research_fts USING fts5(
    id,
    title,
    content,
    tags,
    domain,
    content='research_documents',
    content_rowid='rowid'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS research_documents_ai AFTER INSERT ON research_documents BEGIN
    INSERT INTO research_fts(rowid, id, title, content, tags, domain)
    SELECT new.rowid, new.id, new.title, '', '', new.domain FROM research_documents WHERE rowid = new.rowid;
END;

CREATE TRIGGER IF NOT EXISTS research_documents_ad AFTER DELETE ON research_documents BEGIN
    INSERT INTO research_fts(research_fts, rowid, id, title, content, tags, domain)
    VALUES('delete', old.rowid, old.id, old.title, '', '', old.domain);
END;

CREATE TRIGGER IF NOT EXISTS research_documents_au AFTER UPDATE ON research_documents BEGIN
    INSERT INTO research_fts(research_fts, rowid, id, title, content, tags, domain)
    VALUES('delete', old.rowid, old.id, old.title, '', '', old.domain);
    INSERT INTO research_fts(rowid, id, title, content, tags, domain)
    SELECT new.rowid, new.id, new.title, '', '', new.domain FROM research_documents WHERE rowid = new.rowid;
END;

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_documents_status ON research_documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_urgency ON research_documents(urgency);
CREATE INDEX IF NOT EXISTS idx_documents_domain ON research_documents(domain);
CREATE INDEX IF NOT EXISTS idx_documents_confidence ON research_documents(confidence);
CREATE INDEX IF NOT EXISTS idx_tags_document ON tags(document_id);
CREATE INDEX IF NOT EXISTS idx_tags_tag ON tags(tag);
CREATE INDEX IF NOT EXISTS idx_related_source ON related_documents(source_id);
CREATE INDEX IF NOT EXISTS idx_related_target ON related_documents(target_id);

-- View: Documents with their tags aggregated
CREATE VIEW IF NOT EXISTS v_document_tags AS
SELECT d.id, d.title, d.status, d.urgency, d.domain,
       GROUP_CONCAT(t.tag, ', ') AS tags
FROM research_documents d
LEFT JOIN tags t ON d.id = t.document_id
GROUP BY d.id;

-- View: Cross-document link graph
CREATE VIEW IF NOT EXISTS v_document_graph AS
SELECT r.source_id, r.target_id, r.relationship,
       d1.title AS source_title, d2.title AS target_title
FROM related_documents r
JOIN research_documents d1 ON r.source_id = d1.id
JOIN research_documents d2 ON r.target_id = d2.id;

-- View: Stale documents (no update in 90+ days)
CREATE VIEW IF NOT EXISTS v_stale_documents AS
SELECT id, title, status, updated_at,
       julianday('now') - julianday(updated_at) AS days_since_update
FROM research_documents
WHERE updated_at IS NOT NULL
  AND julianday('now') - julianday(updated_at) > 90
  AND status NOT IN ('archived', 'superseded');

-- View: Low confidence documents (confidence < 6)
CREATE VIEW IF NOT EXISTS v_low_confidence_documents AS
SELECT id, title, confidence, status
FROM research_documents
WHERE confidence IS NOT NULL AND confidence < 6
  AND status NOT IN ('archived', 'superseded');

-- View: Research velocity (documents per domain per month)
CREATE VIEW IF NOT EXISTS v_research_velocity AS
SELECT
    domain,
    strftime('%Y-%m', created_at) AS month,
    COUNT(*) AS documents_created,
    SUM(CASE WHEN status = 'complete' THEN 1 ELSE 0 END) AS documents_completed
FROM research_documents
GROUP BY domain, month
ORDER BY month DESC, domain;

-- View: Sovereignty score distribution
CREATE VIEW IF NOT EXISTS v_sovereignty_distribution AS
SELECT
    CASE
        WHEN sovereignty_score >= 9 THEN '🟢 Sovereign (9-10)'
        WHEN sovereignty_score >= 7 THEN '🟡 Partial (7-8)'
        WHEN sovereignty_score >= 5 THEN '🟠 Compromised (5-6)'
        ELSE '🔴 Cloud-Dependent (1-4)'
    END AS sovereignty_tier,
    COUNT(*) AS document_count
FROM research_documents
WHERE sovereignty_score IS NOT NULL
GROUP BY sovereignty_tier
ORDER BY sovereignty_tier;
"""


def init_database():
    """Create the database and schema."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()
    print(f"✅ Database initialized: {DB_PATH}")
    print(f"   Schema version: {SCHEMA_VERSION}")


def extract_yaml_frontmatter(filepath):
    """Extract YAML frontmatter from a markdown file as a dict."""
    result = {}
    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"   ⚠ Cannot read {filepath}: {e}")
        return result

    # Match YAML frontmatter between --- markers
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return result

    yaml_text = match.group(1)
    for line in yaml_text.split('\n'):
        line = line.strip()
        if ':' in line:
            key, _, value = line.partition(':')
            key = key.strip().lower()
            value = value.strip()
            if key in ('id', 'title', 'status', 'urgency', 'domain', 'author', 'superseded_by'):
                result[key] = value
            elif key in ('created', 'updated'):
                result[key] = value
            elif key in ('confidence', 'sovereignty_score', 'word_count'):
                try:
                    result[key] = int(value)
                except ValueError:
                    pass
            elif key == 'ram_mb':
                try:
                    result[key] = int(value)
                except ValueError:
                    pass
            elif key == 'cpu_cores':
                try:
                    result[key] = float(value)
                except ValueError:
                    pass
            elif key == 'latency_ms':
                try:
                    result[key] = int(value)
                except ValueError:
                    pass
            elif key == 'tags':
                tags_match = re.findall(r'[\w-]+', value)
                if tags_match:
                    result['tags'] = tags_match
            elif key == 'related':
                tags_match = re.findall(r'[\w-]+', value)
                if tags_match:
                    result['related'] = tags_match
            elif key == 'sources':
                result[key] = value
            elif key == 'hardware_impact':
                # Parse nested hardware_impact block
                pass  # Handled separately if needed

    return result


def seed_from_docs():
    """Seed the database from existing research documents."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Scan all R-*.md files in docs/research/
    pattern = os.path.join(RESEARCH_DIR, "R*.md")
    files = glob.glob(pattern)
    print(f"🔍 Scanning {len(files)} research documents...")

    for filepath in sorted(files):
        filename = os.path.basename(filepath)
        rel_path = os.path.relpath(filepath, RESEARCH_DIR)
        doc_id = filename.replace('.md', '')
        metadata = extract_yaml_frontmatter(filepath)

        title = metadata.get('title', filename)
        status = metadata.get('status', 'in_progress').strip('✅🔄🔲🔴🟡🟢 ').lower()
        status_map = {
            'complete': 'complete', 'done': 'complete', 'ready': 'complete',
            'in_progress': 'in_progress', 'pending': 'pending',
            'blocked': 'blocked', 'draft': 'draft', 'in_review': 'in_review',
            'superseded': 'superseded', 'archived': 'archived'
        }
        normalized_status = status_map.get(status, 'in_progress')

        urgency = metadata.get('urgency', 'strategic').strip('🔴🟡🟢 ')
        urgency_map = {'critical': 'critical', 'high': 'high', 'strategic': 'strategic', 'low': 'low'}
        normalized_urgency = urgency_map.get(urgency, 'strategic')

        created = metadata.get('created', datetime.now().isoformat()[:10])
        updated = metadata.get('updated', created)
        domain = metadata.get('domain', 'general')
        author = metadata.get('author', 'Sovereign Master Researcher')
        confidence = metadata.get('confidence', None)
        sovereignty_score = metadata.get('sovereignty_score', None)
        ram_mb = metadata.get('ram_mb', 0)
        cpu_cores = metadata.get('cpu_cores', 0)
        latency_ms = metadata.get('latency_ms', 0)
        superseded_by = metadata.get('superseded_by', None)
        word_count = metadata.get('word_count', 0)

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO research_documents
                (id, title, status, urgency, domain, file_path, created_at, updated_at, author,
                 confidence, sovereignty_score, ram_mb, cpu_cores, latency_ms, superseded_by, word_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (doc_id, title, normalized_status, normalized_urgency, domain,
                  rel_path, created, updated, author,
                  confidence, sovereignty_score, ram_mb, cpu_cores, latency_ms, superseded_by, word_count))
        except Exception as e:
            print(f"   ⚠ Error inserting {doc_id}: {e}")
            continue

        # Insert tags
        tags = metadata.get('tags', [])
        for tag in tags:
            try:
                cursor.execute("INSERT OR IGNORE INTO tags (document_id, tag) VALUES (?, ?)",
                            (doc_id, tag.lower()))
            except Exception:
                pass

        # Insert related documents
        related = metadata.get('related', [])
        for rel_id in related:
            try:
                cursor.execute("INSERT OR IGNORE INTO related_documents (source_id, target_id) VALUES (?, ?)",
                            (doc_id, rel_id))
            except Exception:
                pass

        # Insert sources
        sources = metadata.get('sources', [])
        if isinstance(sources, str):
            sources = [sources]
        for source in sources:
            if source.startswith('http'):
                try:
                    cursor.execute("INSERT INTO sources (document_id, url, source_type) VALUES (?, ?, 'web')",
                                (doc_id, source))
                except Exception:
                    pass

        print(f"   ✓ {doc_id}: {title[:50]}")

    conn.commit()
    conn.close()
    print(f"\n✅ Database seeded from {len(files)} documents.")


def sync_database():
    """Sync existing database with current documents."""
    print("🔄 Syncing database with current documents...")
    # This would compare file timestamps with DB timestamps and update accordingly
    seed_from_docs()


def query_by_tag(tag):
    """Query documents by tag."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.id, d.title, d.status, d.urgency, d.domain
        FROM research_documents d
        JOIN tags t ON d.id = t.document_id
        WHERE t.tag = ?
        ORDER BY d.updated_at DESC
    """, (tag.lower(),))
    results = cursor.fetchall()
    conn.close()
    if results:
        print(f"\n📄 Documents tagged '{tag}':")
        for row in results:
            print(f"  ✓ {row[0]}: {row[1]} [{row[2]}] ({row[3]})")
    else:
        print(f"\n🔍 No documents found with tag '{tag}'")


def list_stale():
    """List stale documents."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, days_since_update FROM v_stale_documents ORDER BY days_since_update DESC")
    results = cursor.fetchall()
    conn.close()
    if results:
        print(f"\n🟡 Stale documents ({len(results)} total):")
        for row in results:
            print(f"  ⚠ {row[0]}: {row[1]} ({row[2]:.0f} days old)")
    else:
        print("\n✅ No stale documents found")


def show_stats():
    """Display database statistics."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM research_documents")
    doc_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tags")
    tag_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM related_documents")
    link_count = cursor.fetchone()[0]

    cursor.execute("SELECT status, COUNT(*) FROM research_documents GROUP BY status")
    status_counts = cursor.fetchall()

    cursor.execute("SELECT urgency, COUNT(*) FROM research_documents GROUP BY urgency")
    urgency_counts = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM v_stale_documents")
    stale_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM v_low_confidence_documents")
    low_conf_count = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM v_sovereignty_distribution")
    sov_dist = cursor.fetchall()

    conn.close()

    print(f"\n📊 Research Database Statistics:")
    print(f"   Documents: {doc_count}")
    print(f"   Tags: {tag_count}")
    print(f"   Cross-document links: {link_count}")
    print(f"   Stale documents: {stale_count}")
    print(f"   Low confidence documents: {low_conf_count}")
    print(f"\n   By Status:")
    for status, count in status_counts:
        print(f"     {status}: {count}")
    print(f"\n   By Urgency:")
    for urgency, count in urgency_counts:
        print(f"     {urgency}: {count}")
    if sov_dist:
        print(f"\n   Sovereignty Distribution:")
        for tier, count in sov_dist:
            print(f"     {tier}: {count}")


def list_work_items():
    """List work items from the work_items table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, status, priority, source_entity, created_at
        FROM work_items
        ORDER BY
            CASE priority
                WHEN 'P0' THEN 0 WHEN 'P1' THEN 1
                WHEN 'P2' THEN 2 WHEN 'P3' THEN 3
                WHEN 'P4' THEN 4
            END,
            created_at DESC
    """)
    results = cursor.fetchall()
    conn.close()
    if results:
        print(f"\n📋 Work Items ({len(results)} total):")
        status_icons = {
            'backlog': '📥', 'ready': '🎯', 'in_progress': '🔄',
            'review': '👁️', 'done': '✅', 'archived': '🗄️', 'blocked': '🚫'
        }
        for row in results:
            icon = status_icons.get(row[2], '📄')
            print(f"  {icon} {row[0]}: {row[1]} [{row[2]}] ({row[3]})")
    else:
        print("\n📋 No work items found")
    conn.close()


if __name__ == "__main__":
    init_database()

    if "--seed" in sys.argv:
        seed_from_docs()
    elif "--sync" in sys.argv:
        sync_database()
    elif "--query" in sys.argv:
        idx = sys.argv.index("--query")
        if idx + 1 < len(sys.argv):
            query_by_tag(sys.argv[idx + 1])
        else:
            print("Usage: --query <tag>")
    elif "--stale" in sys.argv:
        list_stale()
    elif "--work-items" in sys.argv:
        list_work_items()
    elif "--stats" in sys.argv:
        show_stats()
    else:
        show_stats()

    print(f"\n💡 Usage: sqlite3 '{DB_PATH}'")
    print("   Example: sqlite3 \"$DB_PATH\" \"SELECT * FROM v_stale_documents;\"")
    print("   Example: python3 scripts/init-research-db.py --query podman")
