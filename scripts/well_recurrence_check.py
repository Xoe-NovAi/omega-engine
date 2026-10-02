#!/usr/bin/env python3
"""
Mechanical recurrence detector for Well corrections.
Detects "phantom gradient steps" — violations of a correction rule that occur
AFTER the correction was written.

Exit codes (sysexits convention — never conflate "couldn't look" with "clean"):
  0  checked, no recurrences
  1  recurrences found (or --verify failed)
  66 couldn't look (well.jsonl missing / ochist unavailable) — EX_NOINPUT
  2  argparse usage error (owned by argparse)
"""
import json
import os
import subprocess
import sys
import re
from datetime import datetime
from pathlib import Path

# Repo-relative, never CWD-relative (Path.cwd() is caller-dependent and made
# this script exit 0 "No corrections" when run from /tmp). Env override
# follows the pattern in scripts/well_storage.py:36 and the pypa/click
# convention: environment variable takes precedence over the default.
_WELL_DIR = Path(
    os.environ.get(
        "WELL_DIR_OVERRIDE",
        str(Path(__file__).resolve().parents[1] / "gnosis" / "well"),
    )
)
WELL_PATH = _WELL_DIR / "well.jsonl"
RECURRENCES_PATH = _WELL_DIR / "recurrences.jsonl"

EXIT_OK = 0        # checked, clean
EXIT_FINDINGS = 1  # recurrences found
EXIT_NOINPUT = 66  # sysexits EX_NOINPUT: couldn't look

def load_well_corrections():
    """Load all Well corrections with violation patterns.

    Returns None when the well file is missing (caller must exit
    EXIT_NOINPUT) — distinct from [] which means "file read, no
    corrections with patterns".
    """
    corrections = []
    if not WELL_PATH.is_file():
        return None
    with WELL_PATH.open() as fh:
        for raw in fh:
            line = raw.strip()
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
    """Run ochist grep; return list of hits, or None if ochist failed.

    None (operational failure: missing binary / timeout / bad JSON) must
    propagate to EXIT_NOINPUT — silently returning [] here was the
    "confuse couldn't-look with no-match" bug (CODE_QUALITY §4.3).
    """
    cmd = ["ochist", "grep", pattern, "--global", "--limit", str(limit), "--json"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except (subprocess.TimeoutExpired, OSError) as exc:
        print(f"ERROR: ochist grep failed: {exc}", file=sys.stderr)
        return None
    if result.returncode != 0:
        print(
            f"ERROR: ochist grep rc={result.returncode}: {result.stderr.strip()}",
            file=sys.stderr,
        )
        return None
    if not result.stdout.strip():
        return []
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        print(f"ERROR: ochist grep returned invalid JSON: {exc}", file=sys.stderr)
        return None

def is_likely_command_invocation(text):
    """Heuristic: match looks like a command invocation, not documentation."""
    if not text:
        return False
    t = text.strip()
    # Exclude documentation-like patterns FIRST
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
    # Include: shell prompt patterns ($ > # bash)
    if re.match(r'^([$#>]|bash\s+)\s*opencode db\b', t):
        return True
    # Include: command at line start (no prompt)
    if re.match(r'^opencode db\b', t):
        return True
    # Include: after prompt anywhere in line
    if re.search(r'[\$#>]\s*opencode db\b', t):
        return True
    return False

def check_recurrences(corrections, exclude_sessions=None):
    """Check each correction for recurrences after its creation time.

    Returns (all_findings, error) — error is an ochist failure message or
    None; callers must treat error as EXIT_NOINPUT, not as zero findings.
    """
    all_findings = []
    for corr_idx, corr in enumerate(corrections):
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
        if results is None:
            return None, f"ochist grep failed for pattern {pattern!r}"
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
                "session_id": r.get("sessionId"),
                "timestamp": ts_dt.isoformat(),
                "snippet": (r.get("match") or "")[:120]
            })
        if findings:
            all_findings.append({
                "record_id": corr.get("id") or corr_idx,
                "pattern": pattern,
                "rule": corr.get("rule", "")[:80],
                "created_at": created,
                "findings": findings
            })
    return all_findings, None

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true", help="Run verification only")
    parser.add_argument("--exclude-session", action="append", help="Exclude sessions by slug (can repeat)")
    parser.add_argument(
        "--exclude-current",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Exclude the most recent session (default: true; disable with --no-exclude-current)",
    )
    args = parser.parse_args()

    corrections = load_well_corrections()
    if corrections is None:
        print(f"ERROR: well file not found: {WELL_PATH}", file=sys.stderr)
        print("ERROR: cannot check recurrences — set WELL_DIR_OVERRIDE if the Well lives elsewhere", file=sys.stderr)
        return EXIT_NOINPUT
    if not corrections:
        print("No corrections with violation patterns found")
        return EXIT_OK

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

    findings, err = check_recurrences(corrections, exclude_sessions=exclude_sessions)
    if err:
        print(f"ERROR: {err}", file=sys.stderr)
        return EXIT_NOINPUT
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
                return EXIT_FINDINGS
        print("✅ VERIFY PASS: 3becf4f3 clean after 2026-10-02")
        return EXIT_OK

    if not findings:
        print("No recurrences to write")
        return EXIT_OK

    # Write recurrences log — note: file handle must NOT share a name with
    # the loop variable (the old `as f:` / `for f in` shadowing raised
    # AttributeError exactly when there were findings to write).
    RECURRENCES_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RECURRENCES_PATH.open("a") as fh:
        for finding in findings:
            for hit in finding["findings"]:
                rec = {
                    "record_id": finding["record_id"],
                    "pattern": finding["pattern"],
                    "session": hit["session"],
                    "timestamp": hit["timestamp"],
                    "snippet": hit["snippet"]
                }
                fh.write(json.dumps(rec) + "\n")
    print(f"Wrote {total} recurrences to {RECURRENCES_PATH}")
    return EXIT_FINDINGS

if __name__ == "__main__":
    sys.exit(main())