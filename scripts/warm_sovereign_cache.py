#!/usr/bin/env python3
"""
SovereignCache Warmer — Populates cache from URL Registry.

Uses config/research/url_registry.yaml to warm caches for:
- Tier 1: Official API responses (HF Hub, AA, OpenCode Zen, etc.)
- Tier 2: Firecrawl scrapes of documentation pages
- Tier 4: webfetch of known good URLs

Integrates with background_researcher loop or runs standalone.

Usage:
    # Warm all priority 1 entries
    python scripts/warm_sovereign_cache.py --priority 1

    # Warm specific domain
    python scripts/warm_sovereign_cache.py --domain ai_model_evaluation

    # Dry run
    python scripts/warm_sovereign_cache.py --dry-run --priority 1

    # Force refresh (ignore cache freshness)
    python scripts/warm_sovereign_cache.py --priority 1 --force
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import sqlite3
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

import httpx
import yaml


# ============================================================================
# CONFIGURATION
# ============================================================================

REGISTRY_PATH = Path("config/research/url_registry.yaml")
CACHE_DB_PATH = Path("data/cache/sovereign_cache.sqlite")
CACHE_DIR = Path("data/cache/sovereign")

# Rate limiting (seconds between requests per tier)
TIER_DELAYS = {
    1: 0.5,   # Official APIs - be respectful
    2: 2.0,   # Firecrawl - slower, JS rendering
    3: 1.0,   # SearXNG
    4: 0.3,   # webfetch - fast static content
}

MAX_RETRIES = 3
REQUEST_TIMEOUT = 60.0
FIRECRAWL_TIMEOUT = 120.0


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class RegistryEntry:
    url: str
    domain: str
    tier: int
    auth: str
    rate_limit: str
    selectors: Optional[str]
    freshness: str
    priority: int
    tags: list[str]
    last_verified: str

    @classmethod
    def from_dict(cls, d: dict) -> "RegistryEntry":
        return cls(
            url=d["url"],
            domain=d["domain"],
            tier=d["tier"],
            auth=d["auth"],
            rate_limit=d["rate_limit"],
            selectors=d.get("selectors"),
            freshness=d["freshness"],
            priority=d["priority"],
            tags=d.get("tags", []),
            last_verified=d.get("last_verified", ""),
        )


@dataclass
class CacheEntry:
    url: str
    domain: str
    tier: int
    content: str
    content_hash: str
    fetched_at: datetime
    expires_at: datetime
    status_code: int
    headers: dict
    metadata: dict


# ============================================================================
# CACHE DATABASE
# ============================================================================

def init_cache_db() -> None:
    """Initialize SovereignCache SQLite database."""
    CACHE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    with sqlite3.connect(CACHE_DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cache_entries (
                url TEXT PRIMARY KEY,
                domain TEXT NOT NULL,
                tier INTEGER NOT NULL,
                content TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                fetched_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                status_code INTEGER NOT NULL,
                headers TEXT NOT NULL,
                metadata TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_cache_domain 
            ON cache_entries(domain)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_cache_expires 
            ON cache_entries(expires_at)
        """)


def get_freshness_ttl(freshness: str) -> int:
    """Convert freshness string to TTL in seconds."""
    mapping = {
        "real_time": 300,        # 5 min
        "continuous": 3600,      # 1 hour
        "daily": 86400,          # 24 hours
        "weekly": 604800,        # 7 days
        "per_version": 2592000,  # 30 days
        "per_release": 2592000,  # 30 days
        "monthly": 2592000,      # 30 days
    }
    return mapping.get(freshness, 86400)


def is_cache_fresh(conn: sqlite3.Connection, url: str) -> bool:
    """Check if cached entry is still fresh."""
    cursor = conn.execute(
        "SELECT expires_at FROM cache_entries WHERE url = ?", (url,)
    )
    row = cursor.fetchone()
    if not row:
        return False
    expires_at = datetime.fromisoformat(row[0].replace("Z", "+00:00"))
    return datetime.now(timezone.utc) < expires_at


def store_cache_entry(conn: sqlite3.Connection, entry: CacheEntry) -> None:
    """Store or update cache entry."""
    conn.execute("""
        INSERT OR REPLACE INTO cache_entries 
        (url, domain, tier, content, content_hash, fetched_at, expires_at, 
         status_code, headers, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        entry.url,
        entry.domain,
        entry.tier,
        entry.content,
        entry.content_hash,
        entry.fetched_at.isoformat(),
        entry.expires_at.isoformat(),
        entry.status_code,
        json.dumps(entry.headers),
        json.dumps(entry.metadata),
    ))
    conn.commit()


# ============================================================================
# FETCHERS
# ============================================================================

class Tier1Fetcher:
    """Fetch from Official APIs (Tier 1)."""
    
    def __init__(self):
        self.client = httpx.Client(timeout=REQUEST_TIMEOUT)
    
    def _get_headers(self, entry: RegistryEntry) -> dict:
        headers = {"User-Agent": "Omega-Engine-CacheWarmer/1.0"}
        
        if entry.auth == "token":
            token = os.getenv("HF_TOKEN")
            if token:
                headers["Authorization"] = f"Bearer {token}"
        elif entry.auth == "api_key":
            # Try common env vars
            for key in ["AA_API_KEY", "EXA_API_KEY", "OPENROUTER_API_KEY", "GH_TOKEN", "SEMANTIC_SCHOLAR_API_KEY"]:
                token = os.getenv(key)
                if token:
                    if "artificialanalysis" in entry.url:
                        headers["x-api-key"] = token
                    elif "exa.ai" in entry.url:
                        headers["x-api-key"] = token
                    elif "openrouter" in entry.url:
                        headers["Authorization"] = f"Bearer {token}"
                    elif "github" in entry.url:
                        headers["Authorization"] = f"Bearer {token}"
                    elif "semanticscholar" in entry.url:
                        headers["x-api-key"] = token
                    break
        elif entry.auth == "zen_auth":
            # OpenCode Zen auth - would need specific handling
            pass
        
        return headers
    
    def fetch(self, entry: RegistryEntry) -> Optional[CacheEntry]:
        headers = self._get_headers(entry)
        
        for attempt in range(MAX_RETRIES):
            try:
                resp = self.client.get(entry.url, headers=headers, follow_redirects=True)
                
                if resp.status_code == 429:
                    # Rate limited - wait and retry
                    retry_after = int(resp.headers.get("Retry-After", "60"))
                    print(f"  ⏳ Rate limited, waiting {retry_after}s...")
                    time.sleep(retry_after)
                    continue
                
                resp.raise_for_status()
                
                content = resp.text
                content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
                
                ttl = get_freshness_ttl(entry.freshness)
                now = datetime.now(timezone.utc)
                
                return CacheEntry(
                    url=entry.url,
                    domain=entry.domain,
                    tier=entry.tier,
                    content=content,
                    content_hash=content_hash,
                    fetched_at=now,
                    expires_at=now + timedelta(seconds=ttl),
                    status_code=resp.status_code,
                    headers=dict(resp.headers),
                    metadata={
                        "tags": entry.tags,
                        "priority": entry.priority,
                        "auth_type": entry.auth,
                    }
                )
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500 and attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
                    continue
                print(f"  ❌ HTTP {e.response.status_code}: {e}")
                return None
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
                    continue
                print(f"  ❌ Error: {e}")
                return None
        
        return None
    
    def close(self):
        self.client.close()


class Tier2Fetcher:
    """Fetch via Firecrawl Direct (Tier 2)."""
    
    def __init__(self):
        self.api_key = os.getenv("FIRECRAWL_API_KEY")
        if not self.api_key:
            print("  ⚠️  FIRECRAWL_API_KEY not set - Tier 2 fetches will fail")
        self.client = httpx.Client(timeout=FIRECRAWL_TIMEOUT)
    
    def fetch(self, entry: RegistryEntry) -> Optional[CacheEntry]:
        if not self.api_key:
            return None
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "url": entry.url,
            "max_chars": 0,  # NO TRUNCATION - critical!
            "timeout": 60000,
        }
        
        if entry.selectors:
            payload["selectors"] = entry.selectors
        
        for attempt in range(MAX_RETRIES):
            try:
                resp = self.client.post(
                    "https://api.firecrawl.dev/v1/scrape",
                    headers=headers,
                    json=payload,
                )
                
                if resp.status_code == 429:
                    retry_after = int(resp.headers.get("Retry-After", "60"))
                    print(f"  ⏳ Firecrawl rate limited, waiting {retry_after}s...")
                    time.sleep(retry_after)
                    continue
                
                resp.raise_for_status()
                data = resp.json()
                
                if not data.get("success"):
                    print(f"  ❌ Firecrawl failed: {data.get('error')}")
                    return None
                
                content = data.get("data", {}).get("markdown", "")
                if not content:
                    content = data.get("data", {}).get("content", "")
                
                content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
                ttl = get_freshness_ttl(entry.freshness)
                now = datetime.now(timezone.utc)
                
                return CacheEntry(
                    url=entry.url,
                    domain=entry.domain,
                    tier=entry.tier,
                    content=content,
                    content_hash=content_hash,
                    fetched_at=now,
                    expires_at=now + timedelta(seconds=ttl),
                    status_code=200,
                    headers={},
                    metadata={
                        "tags": entry.tags,
                        "priority": entry.priority,
                        "source": "firecrawl",
                        "selectors_used": entry.selectors,
                    }
                )
                
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
                    continue
                print(f"  ❌ Firecrawl error: {e}")
                return None
        
        return None
    
    def close(self):
        self.client.close()


class Tier4Fetcher:
    """Fetch via webfetch (Tier 4) - direct HTTP for known good URLs."""
    
    def __init__(self):
        self.client = httpx.Client(timeout=REQUEST_TIMEOUT)
    
    def fetch(self, entry: RegistryEntry) -> Optional[CacheEntry]:
        headers = {"User-Agent": "Omega-Engine-CacheWarmer/1.0"}
        
        for attempt in range(MAX_RETRIES):
            try:
                resp = self.client.get(entry.url, headers=headers, follow_redirects=True)
                
                if resp.status_code == 429:
                    retry_after = int(resp.headers.get("Retry-After", "60"))
                    print(f"  ⏳ Rate limited, waiting {retry_after}s...")
                    time.sleep(retry_after)
                    continue
                
                resp.raise_for_status()
                
                content = resp.text
                content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
                ttl = get_freshness_ttl(entry.freshness)
                now = datetime.now(timezone.utc)
                
                return CacheEntry(
                    url=entry.url,
                    domain=entry.domain,
                    tier=entry.tier,
                    content=content,
                    content_hash=content_hash,
                    fetched_at=now,
                    expires_at=now + timedelta(seconds=ttl),
                    status_code=resp.status_code,
                    headers=dict(resp.headers),
                    metadata={
                        "tags": entry.tags,
                        "priority": entry.priority,
                        "source": "webfetch",
                    }
                )
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500 and attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
                    continue
                print(f"  ❌ HTTP {e.response.status_code}: {e}")
                return None
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
                    continue
                print(f"  ❌ Error: {e}")
                return None
        
        return None
    
    def close(self):
        self.client.close()


# ============================================================================
# MAIN WARMER
# ============================================================================

class CacheWarmer:
    def __init__(self, dry_run: bool = False, force: bool = False):
        self.dry_run = dry_run
        self.force = force
        self.tier1 = Tier1Fetcher()
        self.tier2 = Tier2Fetcher()
        self.tier4 = Tier4Fetcher()
        self.stats = {
            "checked": 0,
            "fetched": 0,
            "skipped_fresh": 0,
            "skipped_no_auth": 0,
            "errors": 0,
        }
    
    def load_entries(self, domain: Optional[str] = None, priority: Optional[int] = None) -> list[RegistryEntry]:
        with open(REGISTRY_PATH) as f:
            data = yaml.safe_load(f)
        
        entries = [RegistryEntry.from_dict(e) for e in data.get("entries", [])]
        
        if domain:
            entries = [e for e in entries if e.domain == domain]
        if priority:
            entries = [e for e in entries if e.priority <= priority]
        
        # Sort by priority, then tier
        entries.sort(key=lambda e: (e.priority, e.tier))
        return entries
    
    def warm(self, entries: list[RegistryEntry]) -> dict:
        if not self.dry_run:
            init_cache_db()
        
        conn = sqlite3.connect(CACHE_DB_PATH) if not self.dry_run else None
        
        try:
            for entry in entries:
                self.stats["checked"] += 1
                
                print(f"\n[{self.stats['checked']}/{len(entries)}] {entry.url}")
                print(f"  Domain: {entry.domain} | Tier: {entry.tier} | Priority: {entry.priority} | Freshness: {entry.freshness}")
                
                # Check cache freshness
                if not self.force and not self.dry_run and is_cache_fresh(conn, entry.url):
                    print(f"  ⏭️  SKIP: Cache fresh")
                    self.stats["skipped_fresh"] += 1
                    continue
                
                # Check auth availability
                if entry.auth in ("token", "api_key", "zen_auth"):
                    env_var = {
                        "token": "HF_TOKEN",
                        "api_key": "AA_API_KEY/EXA_API_KEY/OPENROUTER_API_KEY/GH_TOKEN",
                        "zen_auth": "ZEN_AUTH",
                    }.get(entry.auth, entry.auth)
                    if not os.getenv(env_var.split("/")[0]):
                        print(f"  ⚠️  SKIP: Missing auth ({env_var})")
                        self.stats["skipped_no_auth"] += 1
                        continue
                
                if self.dry_run:
                    print(f"  📝 DRY-RUN: Would fetch (Tier {entry.tier})")
                    continue
                
                # Fetch based on tier
                fetcher = {1: self.tier1, 2: self.tier2, 4: self.tier4}.get(entry.tier)
                if not fetcher:
                    print(f"  ⚠️  SKIP: No fetcher for Tier {entry.tier}")
                    continue
                
                print(f"  🔄 Fetching...")
                result = fetcher.fetch(entry)
                
                if result:
                    store_cache_entry(conn, result)
                    self.stats["fetched"] += 1
                    print(f"  ✅ Cached ({len(result.content)} chars, hash: {result.content_hash})")
                else:
                    self.stats["errors"] += 1
                    print(f"  ❌ Failed")
                
                # Rate limiting
                delay = TIER_DELAYS.get(entry.tier, 1.0)
                time.sleep(delay)
        
        finally:
            if conn:
                conn.close()
        
        return self.stats
    
    def close(self):
        self.tier1.close()
        self.tier2.close()
        self.tier4.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="SovereignCache Warmer")
    parser.add_argument("--domain", "-d", help="Filter by domain")
    parser.add_argument("--priority", "-p", type=int, choices=[1, 2, 3], 
                        help="Max priority to fetch (1=critical, 2=standard, 3=all)")
    parser.add_argument("--dry-run", "-n", action="store_true", 
                        help="Show what would be fetched without fetching")
    parser.add_argument("--force", "-f", action="store_true",
                        help="Force refresh even if cache is fresh")
    parser.add_argument("--list-domains", action="store_true",
                        help="List available domains and exit")
    
    args = parser.parse_args()
    
    if args.list_domains:
        with open(REGISTRY_PATH) as f:
            data = yaml.safe_load(f)
        domains = {}
        for e in data.get("entries", []):
            d = e["domain"]
            domains[d] = domains.get(d, 0) + 1
        for d, c in sorted(domains.items()):
            print(f"  {d}: {c} entries")
        return 0
    
    warmer = CacheWarmer(dry_run=args.dry_run, force=args.force)
    
    try:
        entries = warmer.load_entries(domain=args.domain, priority=args.priority)
        print(f"📋 Loaded {len(entries)} entries from registry")
        
        if not entries:
            print("No entries match filters")
            return 0
        
        stats = warmer.warm(entries)
        
        print(f"\n{'='*50}")
        print(f"CACHE WARMER SUMMARY")
        print(f"{'='*50}")
        print(f"  Checked:      {stats['checked']}")
        print(f"  Fetched:      {stats['fetched']}")
        print(f"  Skipped fresh:{stats['skipped_fresh']}")
        print(f"  Skipped auth: {stats['skipped_no_auth']}")
        print(f"  Errors:       {stats['errors']}")
        
        return 0 if stats["errors"] == 0 else 1
        
    finally:
        warmer.close()


if __name__ == "__main__":
    sys.exit(main())