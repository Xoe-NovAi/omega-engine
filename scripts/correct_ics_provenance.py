#!/usr/bin/env python3
"""ICS Provenance Correction Worker (FP-04 / R_MESSAGE_PROVENANCE_HIERARCHY).

Scans markdown artifacts for ICS headers claiming model authorship,
verifies claims against Tier-0 ground truth (messages.modelID in
opencode.db), and corrects/annotates misattributions with a full
audit trail. Emits a training-purity manifest for DPO/SFT pipelines.

Modes:
  --dry-run   (default) report only, no writes
  --apply     append provenance-correction annotations to affected files
              AND emit one ledger line per annotated file.
              FAIL-CLOSED (DC-01): if opencode.db is unreachable, --apply
              aborts with exit 2 and zero writes — a db outage must never
              degrade stored Tier-0 verdicts into n/a rewrites.
  --manifest PATH  emit JSONL manifest {file -> verified attribution}

W1-4 enhancements (2026-08-24):
  - Tier-0 db resolver: session IDs resolved via indexed lookup +
    json_extract(data,'$.modelID') on ONE read-only (mode=ro) connection;
    graceful fallback to n/a when unresolvable or db unavailable.
  - Anchor recall: session refs collected from an 80-line anchor zone
    (ICS claim still comes from the strict 20-line header zone).
  - Ledger completeness root-cause fix: the old audit() renamed a
    per-call tmp file OVER the ledger, clobbering all prior entries
    (1,440 sweeps -> 1 surviving line). Now direct O_APPEND + fsync.
  - Idempotent re-runs: already-annotated files are re-verified and
    their annotation UPDATED IN PLACE (original audit timestamp
    preserved as first_audit:) only when the semantic verdict changed.

Stdlib only. READ-ONLY against opencode.db (mode=ro; no writes,
no VACUUM, no ATTACH ever).
"""
from __future__ import annotations
import argparse, json, os, re, sqlite3, sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.environ.get("OPENCODE_DB_PATH", str(Path.home() / ".local/share/opencode/opencode.db")))
AUDIT_LOG = REPO / "data/knowledge/safety/provenance_corrections.jsonl"
MARKER = "<!-- PROVENANCE-CORRECTED"
SCAN_ROOTS = [REPO / "data", REPO / "docs"]
ICS_RE = re.compile(r"⬡\s*OMEGA\s*⬡\s*([^\n⬡]*?)\s*⬡\s*([^\n⬡]*?)\s*⬡")
SES_RE = re.compile(r"ses_[A-Za-z0-9]{10,}")
DATE_RE = re.compile(r"(2026-\d{2}-\d{2})")
HEADER_ZONE = 20   # strict zone for the file's OWN ICS claim
ANCHOR_ZONE = 80   # widened zone for session-id anchors (GAP-1 recall fix)
DB_QUERY_LIMIT = 5000  # hard cap per session; parameterized, indexed plan


def open_db_ro() -> sqlite3.Connection | None:
    """Open opencode.db strictly read-only. Returns None if unavailable."""
    try:
        return sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True, timeout=5.0)
    except sqlite3.Error as e:
        print(f"[warn] db unavailable ({e}); resolver disabled -> n/a", file=sys.stderr)
        return None


def db_session_models(con: sqlite3.Connection | None, session_id: str):
    """Assistant-model stamp distribution for one session (Tier-0).

    Uses the covering index message_session_time_created_id_idx; json_extract
    projects only role/modelID so large message bodies never cross the wire.
    Returns (Counter,) or None when session absent / no stamps / db down.
    """
    if con is None:
        return None
    try:
        rows = con.execute(
            "SELECT json_extract(data,'$.role'), json_extract(data,'$.modelID') "
            f"FROM message WHERE session_id=? LIMIT {int(DB_QUERY_LIMIT)}",
            (session_id,),
        ).fetchall()
    except sqlite3.Error as e:
        print(f"[warn] db query failed for {session_id}: {e}", file=sys.stderr)
        return None
    counts: Counter = Counter()
    for role, mid in rows:
        if role == "assistant" and mid:
            counts[mid] += 1
    return counts or None


def parse_file(path: Path) -> dict | None:
    """Extract the file's own ICS claim + session anchors.

    Files carrying an existing annotation are returned with
    existing_annotation metadata so re-runs can upgrade in place.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    head = "\n".join(text.splitlines()[:HEADER_ZONE])
    m = ICS_RE.search(head)
    if not m:
        return None
    anchor_head = "\n".join(text.splitlines()[:ANCHOR_ZONE])
    sessions = sorted(set(SES_RE.findall(anchor_head)) | set(SES_RE.findall(head)))
    dates = DATE_RE.findall(head)
    existing = _existing_annotation(text)
    return {
        "path": str(path.relative_to(REPO)),
        "entity": m.group(1).strip(),
        "claimed_model": m.group(2).strip(),
        "session_refs": sessions,
        "date": dates[0] if dates else None,
        "mtime": path.stat().st_mtime,
        "header_line": m.group(0)[:120],
        "existing_annotation": existing,  # None | dict(ts, claimed, verdict, note, models)
    }


ANN_TS_RE = re.compile(re.escape(MARKER) + r"\s+(\S+)")
ANN_MODELS_RE = re.compile(r"^actual_models\(Tier0\):\s*(.*)$", re.M)
ANN_BLOCK_RE = re.compile(
    re.escape(MARKER) + r"[^\n]*\n(?:(?!-->).*\n)*-->\n?", re.M
)


def _existing_annotation(text: str) -> dict | None:
    """Parse an existing annotation block into comparable semantic fields."""
    if MARKER not in text:
        return None
    m = ANN_BLOCK_RE.search(text)
    if not m:
        # marker present but malformed block; treat as annotated-unparseable
        return {"ts": None, "claimed": None, "verdict": None, "note": "", "models": []}
    block = m.group(0)
    lines = block.splitlines()
    ts_m = ANN_TS_RE.search(lines[0])
    info_line = next((l for l in lines if l.startswith("claimed_model:")), "")
    parts = [p.strip() for p in info_line.split("|")]
    claimed = parts[0].replace("claimed_model:", "").strip() if parts else None
    verdict, note = None, ""
    for p in parts[1:]:
        if p.startswith("verdict:"):
            verdict = p.replace("verdict:", "").strip()
        elif p.startswith("note:"):
            note = p.replace("note:", "").strip()
        elif verdict is not None and not note:
            # legacy format: bare trailing text after verdict IS the note
            note = p.strip()
    md_m = ANN_MODELS_RE.search(block)
    models = ([x.strip() for x in md_m.group(1).split(",")]
              if md_m and md_m.group(1).strip() != "n/a" else [])
    return {
        "ts": ts_m.group(1) if ts_m else None,
        "claimed": claimed,
        "verdict": verdict,
        "note": note,
        "models": models,
    }


def verify(claim: dict, con) -> dict:
    """Classify the claim against Tier-0 ground truth."""
    verdict = {"verdict": "UNANCHORED", "actual_models": [], "note": ""}
    if not claim["session_refs"]:
        verdict["note"] = "no session anchor in header zone"
        return verdict
    merged: Counter = Counter()
    anchored = False
    for sid in claim["session_refs"]:
        result = db_session_models(con, sid)
        if result is None:
            continue
        anchored = True
        merged.update(result)
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


def annotation(claim: dict, verdict: dict, first_audit: str | None = None) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        f"\n{MARKER} {ts} — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit",
        f"claimed_model: {claim['claimed_model']} | verdict: {verdict['verdict']}"
        f"{(' | ' + verdict['note']) if verdict['note'] else ''}",
        f"actual_models(Tier0): {', '.join(verdict['actual_models'][:6]) or 'n/a'}",
    ]
    if first_audit:
        lines.append(f"first_audit: {first_audit} | updated: {ts}")
    lines.append("-->\n")
    return "\n".join(lines) + "\n"


def semantics(verdict: dict) -> tuple:
    """Comparable semantic fingerprint of a verdict (timestamp-excluded)."""
    return (verdict["verdict"], verdict.get("note", ""), tuple(verdict["actual_models"][:6]))


def needs_update(claim: dict, verdict: dict) -> bool:
    ex = claim.get("existing_annotation")
    if not ex:
        return True
    ex_sem = (ex.get("verdict"), ex.get("note") or "", tuple(ex.get("models") or []))
    return ex_sem != semantics(verdict)


def apply_annotation(path: Path, claim: dict, verdict: dict) -> str:
    """Append or update-in-place the annotation block. Atomic via tmp+replace."""
    text = path.read_text(encoding="utf-8", errors="replace")
    action = "annotated"
    if claim.get("existing_annotation"):
        action = "updated"
        first_ts = claim["existing_annotation"].get("ts")
        m = ANN_BLOCK_RE.search(text)
        new_block = annotation(claim, verdict, first_audit=first_ts)
        if m:
            text = text[:m.start()] + new_block.lstrip("\n") + text[m.end():]
        else:
            text = text.rstrip("\n") + "\n" + new_block.lstrip("\n")
    else:
        text = text.rstrip("\n") + "\n" + annotation(claim, verdict).lstrip("\n")
    tmp = path.with_suffix(path.suffix + ".pvn.tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(text)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)
    return action


def audit(entry: dict) -> None:
    """Append one ledger line. ROOT-CAUSE FIX (W1-4): the previous
    implementation wrote a per-call .tmp then renamed it OVER the ledger,
    destroying all prior entries (mass sweep -> exactly 1 survivor).
    Direct O_APPEND + fsync keeps every line; single-writer timer context."""
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_LOG, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--manifest", type=Path, default=None)
    args = ap.parse_args(argv)

    con = open_db_ro()
    if con is None and args.apply:
        # DC-01 (fail-closed): a db outage must NEVER reach the write path.
        # With the resolver down, every session-anchored claim degrades to
        # UNANCHORED/n/a and idempotency machinery would rewrite real
        # Tier-0 verdicts into misleading n/a annotations (exit 0, no
        # signal — M23 anti-pattern). Dry-run KEEPS graceful degradation.
        print(
            "[TOOL-CHAIN-COLLAPSE] --apply aborted: opencode.db unreachable "
            f"at {DB_PATH} — refusing to overwrite Tier-0 verdicts with "
            "n/a. Restore db access, or re-run without --apply (dry-run).",
            file=sys.stderr,
        )
        return 2
    findings = []
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*.md"):
            claim = parse_file(path)
            if claim:
                claim["verdict"] = verify(claim, con)
                findings.append(claim)
    if con is not None:
        con.close()

    tally = Counter(f["verdict"]["verdict"] for f in findings)
    resolved = sum(1 for f in findings if f["verdict"]["actual_models"])
    print(f"scanned ICS-bearing artifacts: {len(findings)}")
    for v, n in tally.most_common():
        print(f"  {v}: {n}")
    print(f"tier0-resolved: {resolved}/{len(findings)}")

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
        applied = updated = backfilled = skipped_current = 0
        # Ledger-membership set: an annotated file with NO ledger line is a
        # GAP-2 violation (claim-on-disk without audit trail). Backfill once;
        # subsequent runs skip (idempotent, no daily bloat).
        logged_files: set[str] = set()
        if AUDIT_LOG.exists():
            with open(AUDIT_LOG, encoding="utf-8") as fh:
                for line in fh:
                    try:
                        logged_files.add(json.loads(line).get("file", ""))
                    except json.JSONDecodeError:
                        continue
        for f in findings:
            has_ann = bool(f["existing_annotation"])
            if f["verdict"]["verdict"] == "VERIFIED" and not has_ann:
                continue  # honest header needs no annotation
            changed = needs_update(f, f["verdict"])
            p = REPO / f["path"]
            if has_ann and not changed and f["path"] in logged_files:
                skipped_current += 1
                continue  # annotation current + ledger-backed — no churn
            if has_ann and not changed:
                action = "backfill"  # ledger-only line; file untouched
            else:
                action = apply_annotation(p, f, f["verdict"])  # annotated|updated
            if action == "updated":
                updated += 1
            elif action == "annotated":
                applied += 1
            elif action == "backfill":
                backfilled += 1
            audit({
                "ts": datetime.now(timezone.utc).isoformat(),
                "file": f["path"], "claimed": f["claimed_model"],
                "verdict": f["verdict"]["verdict"], "actual": f["verdict"]["actual_models"],
                "action": action,
                "worker": "correct_ics_provenance", "tier_source": "messages.modelID",
            })
        print(f"annotations applied: {applied}; updated in place: {updated}; "
              f"ledger backfilled: {backfilled}; already-current: {skipped_current}; "
              f"ledger -> {AUDIT_LOG}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
