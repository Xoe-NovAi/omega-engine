#!/usr/bin/env python3
"""
⬡ OMEGA ⬡ FLE TELEMETRY COLLECTOR (Wave 2 Telemetry Stream Ingestion)
Parses [TELEMETRY] YAML blocks emitted by Dev Team / Fleet sessions.

Usage:
  .venv/bin/python scripts/collect_telemetry.py [--since-commit <sha>] [--stream-file <path>] [--summary]
  .venv/bin/python scripts/collect_telemetry.py --self-test
"""

import sys
import re
import json
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

TELEMETRY_BLOCK_PATTERN = re.compile(
    r'\[TELEMETRY\]\s*\n(```(?:yaml)?\s*\n)?(.*?)(```|\Z)',
    re.DOTALL
)

DEFAULT_STREAM_FILE = Path("data/coordination/fle_study_20260825/TELEMETRY_STREAM.jsonl")


def parse_telemetry_yaml(text: str) -> Dict[str, Any]:
    """Extract and parse [TELEMETRY] block from text."""
    match = TELEMETRY_BLOCK_PATTERN.search(text)
    if not match:
        return {}
    
    yaml_body = match.group(2).strip()
    result = {}
    
    for line in yaml_body.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            k = k.strip()
            v = v.strip().strip("'\"")
            # Strip approx tildes e.g. ~96000 -> 96000
            clean_v = v.lstrip("~")
            if clean_v.isdigit():
                result[k] = int(clean_v)
            else:
                try:
                    result[k] = float(clean_v)
                except ValueError:
                    result[k] = v
    return result


def extract_telemetry_from_git(since_commit: Optional[str] = None) -> List[Dict[str, Any]]:
    """Scan git log commit bodies for [TELEMETRY] blocks."""
    cmd = ["git", "log", "--format=%H|%an|%ad|%s%n%b%n---ENDCOMMIT---", "--date=iso"]
    if since_commit:
        cmd.insert(2, f"{since_commit}..HEAD")
        
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        return []
        
    entries = []
    commits = res.stdout.split("---ENDCOMMIT---")
    for c in commits:
        c = c.strip()
        if not c or "[TELEMETRY]" not in c:
            continue
        header_body = c.split("\n", 1)
        header_parts = header_body[0].split("|", 3)
        sha = header_parts[0] if len(header_parts) > 0 else ""
        date = header_parts[2] if len(header_parts) > 2 else ""
        body = header_body[1] if len(header_body) > 1 else ""
        
        telemetry = parse_telemetry_yaml(body)
        if telemetry:
            telemetry["_source"] = "git_commit"
            telemetry["_sha"] = sha
            telemetry["_date"] = date
            entries.append(telemetry)
            
    return entries


def self_test():
    """Verify parser robustness against known fixture variants."""
    sample_text = """
Task completed successfully.

[TELEMETRY]
```yaml
input_tokens: ~96000
output_tokens: ~14000
duration_ms: ~1500000
gate_status: green
ceremony_census: 0
```
Done.
"""
    parsed = parse_telemetry_yaml(sample_text)
    assert parsed.get("input_tokens") == 96000, f"Failed input_tokens: {parsed}"
    assert parsed.get("output_tokens") == 14000, f"Failed output_tokens: {parsed}"
    assert parsed.get("duration_ms") == 1500000, f"Failed duration_ms: {parsed}"
    assert parsed.get("gate_status") == "green", f"Failed gate_status: {parsed}"
    assert parsed.get("ceremony_census") == 0, f"Failed ceremony_census: {parsed}"
    print("✅ self-test PASSED")


def main():
    parser = argparse.ArgumentParser(description="FLE Telemetry Collector")
    parser.add_argument("--self-test", action="store_true", help="Run internal parser test")
    parser.add_argument("--since-commit", type=str, help="Scan commits since SHA")
    parser.add_argument("--stream-file", type=str, default=str(DEFAULT_STREAM_FILE), help="Path to JSONL stream file")
    parser.add_argument("--summary", action="store_true", help="Print aggregated summary of collected telemetry")
    
    args = parser.parse_args()
    
    if args.self_test:
        self_test()
        sys.exit(0)
        
    entries = extract_telemetry_from_git(args.since_commit)
    
    if entries:
        stream_path = Path(args.stream_file)
        stream_path.parent.mkdir(parents=True, exist_ok=True)
        with open(stream_path, "a") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")
        print(f"Collected {len(entries)} telemetry block(s) into {stream_path}")
    else:
        print("No new [TELEMETRY] blocks found.")
        
    if args.summary:
        stream_path = Path(args.stream_file)
        if stream_path.exists():
            records = [json.loads(l) for l in open(stream_path) if l.strip()]
            tot_in = sum(r.get("input_tokens", 0) for r in records)
            tot_out = sum(r.get("output_tokens", 0) for r in records)
            tot_dur = sum(r.get("duration_ms", 0) for r in records)
            greens = sum(1 for r in records if r.get("gate_status") == "green")
            reds = sum(1 for r in records if r.get("gate_status") == "red")
            ceremony = sum(r.get("ceremony_census", 0) for r in records)
            
            print("\n=== FLE TELEMETRY AGGREGATE ===")
            print(f"Records ingested : {len(records)}")
            print(f"Total Input Tok  : {tot_in:,}")
            print(f"Total Output Tok : {tot_out:,}")
            print(f"Total Duration   : {tot_dur/1000:.1f}s ({tot_dur/60000:.1f}m)")
            print(f"Gate Status      : {greens} Green | {reds} Red")
            print(f"Ceremony Census  : {ceremony} ceremonial step(s)")


if __name__ == "__main__":
    main()
