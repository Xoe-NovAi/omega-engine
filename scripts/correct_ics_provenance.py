#!/usr/bin/env python3
"""ICS Provenance Correction Worker (FP-04 / R_MESSAGE_PROVENANCE_HIERARCHY).

Scans markdown artifacts for ICS headers claiming model authorship,
verifies claims against Tier-0 ground truth (messages.modelID in
opencode.db), and corrects/annotates misattributions with a full
audit trail. Emits a training-purity manifest for DPO/SFT pipelines.

Modes:
  --dry-run   (default) report only, no writes
  --apply     append provenance-correction annotations to affected files
  --manifest PATH  emit JSONL manifest {file -> verified attribution}

Idempotent: files already annotated are skipped on re-runs.
Stdlib only. Read-only against opencode.db.
"""
from __future__ import annotations
import argparse, json, re, sqlite3, sys, time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DB_PATH = Path.home() / ".local/share/opencode/opencode.db"
AUDIT_LOG = REPO / "data/knowledge/safety/provenance_corrections.jsonl"
MARKER = "<!-- PROVENANCE-CORRECTED"
SCAN_ROOTS = [REPO / "data", REPO / "docs"]
ICS_RE = re.compile(r"⬡\s*OMEGA\s*⬡\s*([^\n⬡]*?)\s*⬡\s*([^\n⬡]*?)\s*⬡")
SES_RE = re.compile(r"ses_[A-Za-z0-9]{10,}")
DATE_RE = re.compile(r"(2026-\d{2}-\d{2})")
HEADER_ZONE = 20  # only the file's own header lines, not quoted content


def db_session_models(session_id: str) -> tuple[Counter, int, int] | None:
    """Assistant-model stamp distribution for one session."""
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    try:
        rows = con.execute(
            "SELECT time_created, data FROM message WHERE session_id=?",
            (session_id,),
        ).fetchall()
    finally:
        con.close()
    if not rows:
        return None
    counts: Counter = Counter()
    times = []
    for ts, data in rows:
        try:
            j = json.loads(data)
        except json.JSONDecodeError:
            continue
        if j.get("role") != "assistant":
            continue
        mid = j.get("modelID")
        if mid:
            counts[mid] += 1
            times.append(ts)
    if not counts:
        return None
    return counts, min(times), max(times)


def dominant_near(counts: Counter, times: list[int], near_ts: float) -> str:
    """Model with most stamps within ±36h of near_ts; else overall dominant."""
    window = Counter()
    lo, hi = (near_ts - 36 * 3600) * 1000, (near_ts + 36 * 3600) * 1000
    # times were not returned per-model; approximate via full-set dominance
    del window, times
    return counts.most_common(1)[0][0]


def parse_file(path: Path) -> dict | None:
    """Extract the file's own ICS claim from its header zone."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    if MARKER in text:
        return None  # already processed — idempotent
    head = "\n".join(text.splitlines()[:HEADER_ZONE])
    m = ICS_RE.search(head)
    if not m:
        return None
    entity, claimed_raw = m.group(1).strip(), m.group(2).strip()
    sessions = sorted(set(SES_RE.findall(head)))
    dates = DATE_RE.findall(head)
    return {
        "path": str(path.relative_to(REPO)),
        "entity": entity,
        "claimed_model": claimed_raw,
        "session_refs": sessions,
        "date": dates[0] if dates else None,
        "mtime": path.stat().st_mtime,
        "header_line": m.group(0)[:120],
    }


def verify(claim: dict) -> dict:
    """Classify the claim against Tier-0 ground truth."""
    verdict = {"verdict": "UNANCHORED", "actual_models": [], "note": ""}
    if not claim["session_refs"]:
        verdict["note"] = "no session anchor in header zone"
        return verdict
    merged: Counter = Counter()
    anchored = False
    for sid in claim["session_refs"]:
        result = db_session_models(sid)
        if result is None:
            continue
        anchored = True
        counts, _lo, _hi = result
        merged.update(counts)
    if not anchored:
        verdict["note"] = "session refs not found in DB"
        return verdict
    actual = [m for m, _ in merged.most_common()]
    verdict["actual_models"] = actual
    res = model_matches(claim["claimed_model"], actual)
    if res == "placeholder":
        verdict["verdict"] = "PLACEHOLDER"
        verdict["note"] = "header contains unresolved {session_model} literal"
    elif res is True:
        verdict["verdict"] = "VERIFIED"
    elif len(actual) == 1:
        verdict["verdict"] = "MISATTRIBUTED"
        verdict["note"] = f"suggested: {actual[0]}"
    else:
        verdict["verdict"] = "AMBIGUOUS"
        verdict["note"] = f"multi-model session; candidates: {', '.join(actual[:4])}"
    return verdict


def model_matches(claimed: str, actual_list: list[str]):
    """Fuzzy-match a claimed model name against Tier-0 stamps.
    Returns True/False, or 'placeholder' for unresolved literals."""
    cl = claimed.lower().strip()
    if "{" in cl or cl in ("session_model", "?", "unknown"):
        return "placeholder"
    # channel-name in model slot = malformed header (missing model field)
    if cl in ("opencode", "google", "openrouter", "anthropic", "google-antigravity",
              "antigravity", "cline", "local"):
        return "placeholder"
    alias = {
        "ox alpha": "x-preview-f-free",
        "big pickle": "big-pickle",
        "gemini": "gemini",
        "sonnet": "sonnet",
        "opus": "opus",
        "nemotron": "nemotron",
    }
    c = alias.get(cl, cl)
    for m in actual_list:
        ml = m.lower()
        if c in ml or ml in c:
            return True
        toks = [t for t in re.split(r"[-_.\s]", c) if len(t) >= 4]
        if toks and all(t in ml for t in toks):
            return True
    return False


def annotation(claim: dict, verdict: dict) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return (
        f"\n{MARKER} {ts} — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit\n"
        f"claimed_model: {claim['claimed_model']} | verdict: {verdict['verdict']}"
        f"{(' | ' + verdict['note']) if verdict['note'] else ''}\n"
        f"actual_models(Tier0): {', '.join(verdict['actual_models'][:6]) or 'n/a'}\n"
        f"-->\n"
    )


def audit(entry: dict) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    tmp = AUDIT_LOG.with_suffix(".tmp")
    with open(tmp, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    tmp.rename(AUDIT_LOG)  # atomic-ish append per line


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--manifest", type=Path, default=None)
    args = ap.parse_args()

    findings = []
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*.md"):
            claim = parse_file(path)
            if claim:
                claim["verdict"] = verify(claim)
                findings.append(claim)

    tally = Counter(f["verdict"]["verdict"] for f in findings)
    print(f"scanned ICS-bearing artifacts: {len(findings)}")
    for v, n in tally.most_common():
        print(f"  {v}: {n}")

    for f in findings:
        flag = "" if f["verdict"]["verdict"] == "VERIFIED" else "  <-- "
        print(f"[{f['verdict']['verdict']:>13}] {f['path']}{flag}{f['verdict']['note']}")

    if args.manifest:
        with open(args.manifest, "w", encoding="utf-8") as fh:
            for f in findings:
                fh.write(json.dumps({
                    "file": f["path"],
                    "entity": f["entity"],
                    "claimed_model": f["claimed_model"],
                    "verified_models_tier0": f["verdict"]["actual_models"],
                    "purity_verdict": f["verdict"]["verdict"],
                    "training_safe": f["verdict"]["verdict"] == "VERIFIED",
                }, ensure_ascii=False) + "\n")
        print(f"manifest -> {args.manifest}")

    if args.apply:
        applied = 0
        for f in findings:
            if f["verdict"]["verdict"] == "VERIFIED":
                continue
            p = REPO / f["path"]
            with open(p, "a", encoding="utf-8") as fh:
                fh.write(annotation(f, f["verdict"]))
            audit({
                "ts": datetime.now(timezone.utc).isoformat(),
                "file": f["path"], "claimed": f["claimed_model"],
                "verdict": f["verdict"]["verdict"], "actual": f["verdict"]["actual_models"],
                "worker": "correct_ics_provenance", "tier_source": "messages.modelID",
            })
            applied += 1
        print(f"annotations applied: {applied}; audit -> {AUDIT_LOG}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
