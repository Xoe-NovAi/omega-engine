import sys
import os
import asyncio
import json
from pathlib import Path

# Set up paths to import omega core
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from omega.library.research import ResearchEngine

async def run_research(query, depth=2, domain=""):
    engine = ResearchEngine()
    print(f"Executing research: {query} (Depth: {depth}, Domain: {domain})")
    result = await engine.research(query, depth=depth, domain=domain if domain else None)
    return result.to_dict()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/research_bridge.py 'query' [depth] [domain]")
        sys.exit(1)
    
    query = sys.argv[1]
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    domain = sys.argv[3] if len(sys.argv) > 3 else ""
    
    output = asyncio.run(run_research(query, depth, domain))
    print(json.dumps(output, indent=2, default=str))
