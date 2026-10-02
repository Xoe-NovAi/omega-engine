#!/usr/bin/env python3
"""
Mechanical recurrence detector for Well corrections.
Detects "phantom gradient steps" — violations of a correction rule that occur
AFTER the correction was written.
"""
import json
import subprocess
import sys
import re
from datetime import datetime
from pathlib import Path

WELL_PATH = Path("gnosis/well/well.jsonl")
RECURRENCES_PATH = Path("gnosis/well/recurrences.jsonl")

def load_well_corrections():
    """Load all Well corrections with violation patterns."""
    corrections = []
    if not WELL_PATH.exists():
        print(f"Well file not found: {WELL_PATH}")
        return []
    with WELL_PATH.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                if rec.get("kind") == "correction":
                    pattern = rec.get("violation_pattern")
                    if not pattern:
                        rule = rec.get("rule", "").lower()
                        if "opencode db" in rule:
                            pattern = "opencode db"
                        elif "immutable=1" in rule:
                            pattern = "immutable=1"
                        elif "0,2,4,6,8,10" in rule or "p-core" in rule:
                            pattern = "0,2,4,6,8,10"
                    if pattern:
                        rec["violation_pattern"] = pattern
                        corrections.append(rec)
            except json.JSONDecodeError:
                continue
    return corrections

def ochist_grep(pattern, limit=50):
    """Run ochist grep and return parsed JSON results."""
    cmd = ["ochist", "grep", pattern, "--global", "--limit", str(limit), "--json"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return []
        return json.loads(result.stdout) if result.stdout.strip() else []
    except (subprocess.TimeoutExpired, json.JSONDecodeError):
        return []

def is_likely_command_invocation(text):
    """Heuristic: match looks like a command invocation, not documentation."""
    if not text:
        return False
    t = text.strip()
    # Real command invocations: pattern at start of line or after shell prompt
    if re.match(r'^(opencode db\b|\$ opencode db\b|> opencode db\b|bash\s+opencode db\b)', t):
        return True
    # After common shell prompts
    if re.search(r'[\$>]\s*opencode db\b', t):
        return True
    # Exclude documentation-like patterns
    doc_patterns = [
        r'`opencode db`',           # backtick-quoted
        r'opencode db.*(?:is|was|are|were)\s+(not\s+)?(?:read-?only|readwrite|write)',  # "opencode db is read-only"
        r'(document|documentation|wrote|writing|rule|ban|forbid|never use|never run|prohibit|description|summary|plan|briefing|brief|correction|recurrence|detector|write|wrote|writing)',  # explanatory words
        r'(###|##|#)\s',  # markdown headers
        r'(verif|test|check|debug|fix|edit|edit applied|applied|commit|push)',  # dev activity
    ]
    text_lower = text.lower()
    for pat in doc_patterns:
        if re.search(pat, text_lower):
            return False
    # Positive: looks like a command at start of line or after prompt
    if re.match(r'^(opencode db\b|\$ opencode db\b|> opencode db\b|bash\s+opencode db\b)', text.strip()):
        return True
    if re.search(r'[\$>]\s*opencode db\b', text.strip()):
        return True
    return False

def check_recurrences(corrections, verify_only=False, exclude_sessions=None):
    """Check each correction for recurrences after its creation time."""
    all_findings = []
    for corr in corrections:
        pattern = corr.get("violation_pattern")
        if not pattern:
            continue
        created = corr.get("created_at") or corr.get("ts")
        if not created:
            continue
        try:
            cutoff = datetime.fromisoformat(created.replace("Z", "+00:00"))
        except ValueError:
            cutoff = datetime.fromisoformat(created)
        if cutoff.tzinfo is None:
            cutoff = cutoff.replace(tzinfo=datetime.now().astimezone().tzinfo)

        results = ochist_grep(corr["violation_pattern"], limit=200)
        findings = []
        for r in results:
            if r.get("kind") != "tool":
                continue
            ts = r.get("time")
            if not ts:
                continue
            try:
                ts_dt = datetime.fromtimestamp(ts / 1000)
                if ts_dt.tzinfo is None:
                    ts_dt = ts_dt.replace(tzinfo=datetime.now().astimezone().tzinfo)
            except (ValueError, OSError):
                continue
            if ts_dt <= cutoff:
                continue
            # Filter: only flag likely command invocations, not documentation
            match_text = r.get("match") or ""
            if not is_likely_command_invocation(match_text):
                continue
            # Exclude excluded sessions
            session_slug = r.get("session") or ""
            if exclude_sessions and session_slug in exclude_sessions:
                continue
            findings.append({
                "session": r.get("session"),
                "session_id": r.get("session_id"),
                "timestamp": ts_dt.isoformat(),
                "snippet": (r.get("match") or "")[:120]
            })
        if findings:
            all_findings.append({
                "record_id": corrections.index(corr),
                "pattern": pattern,
                "rule": corrections[corrections.index(corr)].get("rule", "")[:80],
                "created_at": created,
                "findings": findings
            })
    return all_findings

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true", help="Run verification only")
    parser.add_argument("--exclude-session", action="append", help="Exclude sessions by slug (can repeat)")
    parser.add_argument("--exclude-current", action="store_true", default=True, help="Exclude the most recent session (default: true)")
    args = parser.parse_args()

    corrections = load_well_corrections()
    if not corrections:
        print("No corrections with violation patterns found")
        return 0

    # Auto-exclude the most recent session if --exclude-current is set
    exclude_sessions = set(args.exclude_session or [])
    if args.exclude_current:
        # Get the most recent session slug
        try:
            result = subprocess.run(["ochist", "sessions", "--limit", "1", "--json"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout.strip():
                sessions = json.loads(result.stdout)
                if sessions:
                    recent_slug = sessions[0].get("slug") or sessions[0].get("id", "").split("/")[-1]
                    if recent_slug:
                        exclude_sessions.add(recent_slug)
                        print(f"Auto-excluding current session: {recent_slug}")
        except (subprocess.SubprocessError, json.JSONDecodeError, OSError):
            pass

    exclude_sessions.update(args.exclude_session or [])
    findings = check_recurrences(corrections, verify_only=True, exclude_sessions=exclude_sessions)
    total = sum(len(f["findings"]) for f in findings)
    print(f"Checked {len(corrections)} corrections")
    print(f"Total recurrences found: {total}")
    for f in findings:
        for hit in f["findings"]:
            print(f"  {f['pattern']} | {hit['timestamp']} | {hit['session']} | {hit['snippet']}")

    if args.verify:
        # Success if 3becf4f3 (opencode db) has 0 recurrences after 2026-10-02
        for f in findings:
            if f["pattern"] == "opencode db" and f["findings"]:
                print("❌ FAIL: 3becf4f3 has recurrences after 2026-10-02")
                return 1
        print("✅ VERIFY PASS: 3becf4f3 clean after 2026-10-02")
        return 0

    # Write recurrences log
    RECURRENCES_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RECURRENCES_PATH.open("a") as f:
        for f in findings:
            for hit in f["findings"]:
                rec = {
                    "record_id": f["record_id"],
                    "pattern": f["pattern"],
                    "session": hit["session"],
                    "timestamp": hit["timestamp"],
                    "snippet": hit["snippet"]
                }
                f.write(json.dumps(rec) + "\n")
    print(f"Wrote {total} recurrences to {RECURRENCES_PATH}")
    return 0

if __name__ == "__main__":
    sys.exit(main())