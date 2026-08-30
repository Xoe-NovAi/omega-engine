#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
Weekly freshness checker for Model Registry
⬡ OMEGA ⬡ CLINE ⬡ FRESHNESS-CHECK ⬡ 2026-07-19

Queries APIs, finds stale cards (>30d), generates freshness report.
"""
import sys, json, yaml, requests
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

REGISTRY_DIR = Path("config/model_registry/models")
STALE_FILE = Path("data/stale_models.txt")
REPORT_FILE = Path("data/freshness_report.json")
MAX_AGE_DAYS = 30


def fetch_openrouter_models() -> dict:
    try:
        resp = requests.get("https://openrouter.ai/api/v1/models", timeout=30)
        return {m["id"]: m for m in resp.json().get("data", [])}
    except Exception as e:
        print(f"⚠️ OpenRouter fetch failed: {e}")
        return {}


def load_registry():
    models = {}
    for f in REGISTRY_DIR.rglob("*.yaml.md"):
        content = f.read_text()
        if content.startswith("---"):
            parts = content.split("---", 2)
            data = yaml.safe_load(parts[1])
            if data and "model_id" in data:
                models[data["model_id"]] = {"path": f, "data": data}
    return models


def days_since(date_str: str) -> int:
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - date).days
    except:
        return 999


def main():
    print("🔄 OMEGA FRESHNESS CHECK")
    print("=" * 72)
    
    print("\n📡 Querying OpenRouter API...")
    or_models = fetch_openrouter_models()
    print(f"   Fetched {len(or_models)} models")
    
    our_models = load_registry()
    print(f"   Checking {len(our_models)} registry cards\n")
    
    stale = []
    fresh = []
    unmatched = []
    
    for model_id, info in our_models.items():
        data = info["data"]
        
        # Check staleness
        las = data.get("live_api_state", {})
        last_verified = las.get("last_verified", data.get("updated_at", "2020-01-01"))
        age = days_since(last_verified)
        
        entry = {
            "model_id": model_id,
            "last_verified": last_verified,
            "age_days": age,
            "is_stale": age > MAX_AGE_DAYS,
        }
        
        if age > MAX_AGE_DAYS:
            stale.append(entry)
        
        fresh.append(entry)
    
    # Sort by age
    stale.sort(key=lambda x: x["age_days"], reverse=True)
    fresh.sort(key=lambda x: x["age_days"])
    
    print(f"📊 Results:")
    print(f"   Fresh (<{MAX_AGE_DAYS}d): {len(fresh) - len(stale)}")
    print(f"   Stale (>{MAX_AGE_DAYS}d): {len(stale)}")
    
    if stale:
        print(f"\n⚠️ STALE MODELS (need re-verification):\n")
        for s in stale[:10]:
            print(f"   {s['model_id']}: {s['age_days']} days old")
        if len(stale) > 10:
            print(f"   ... and {len(stale) - 10} more")
    
    # Write report
    report = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "stale_threshold_days": MAX_AGE_DAYS,
        "fresh_count": len(fresh) - len(stale),
        "stale_count": len(stale),
        "stale": stale,
        "all": fresh,
    }
    REPORT_FILE.write_text(json.dumps(report, indent=2))
    
    # Write stale list for CI
    if stale:
        STALE_FILE.write_text("\n".join(s["model_id"] for s in stale))
    else:
        STALE_FILE.unlink(missing_ok=True)
    
    print(f"\n📝 Written: {REPORT_FILE}")
    print(f"   {'🚨' if stale else '✅'} Freshness status: {'STALE DETECTED' if stale else 'ALL CLEAR'}\n")
    
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
