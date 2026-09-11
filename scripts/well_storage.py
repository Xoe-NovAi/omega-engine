#!/usr/bin/env python3
"""The Well — structured, queryable, self-aging corpus of corrections,
coding tips, preferences, and anti-patterns.

Storage: gnosis/well/well.jsonl (append-only truth) + rendered
gnosis/well/WISDOM.md (human view).

Record schema:
  record_id: UUID
  ts: ISO-8601 UTC
  kind: correction|preference|tip|anti_pattern|insight|dream
  source_pack: gnosis session id that produced this
  domain: local_ai|consciousness|psychology|classical|games|harness|other
  trigger: what prompted the rule (brief)
  rule: the actual rule/insight (actionable, single sentence preferred)
  rationale: why it matters
  tags: comma-separated tags
  status: active|superseded
  superseded_by: record_id of the replacement (if status=superseded)

Lifecycle: CAPTURED → ACTIVE → SUPERSEDED (mirrors pack lifecycle)
"""

from __future__ import annotations

import json
import os
import uuid
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Literal
import sys

_DEFAULT_WELL_DIR = Path(__file__).resolve().parents[1] / "gnosis" / "well"
WELL_DIR = Path(os.environ.get("WELL_DIR_OVERRIDE", str(_DEFAULT_WELL_DIR)))
WELL_JSONL = WELL_DIR / "well.jsonl"
WELL_MD = WELL_DIR / "WISDOM.md"

VALID_KINDS = frozenset({
    "correction", "preference", "tip", "anti_pattern", "insight", "dream"
})
VALID_STATUSES = frozenset({"active", "superseded"})
VALID_DOMAINS = frozenset({
    "local_ai", "consciousness", "psychology", "classical", "games", "harness", "other"
})

UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


@dataclass(slots=True)
class WellRecord:
    record_id: str
    ts: str
    kind: str
    source_pack: str
    domain: str
    trigger: str
    rule: str
    rationale: str
    tags: str
    status: str = "active"
    superseded_by: str = ""

    def to_jsonl(self) -> str:
        return json.dumps(asdict(self), separators=(",", ":"), ensure_ascii=False)

    @classmethod
    def from_jsonl(cls, line: str) -> "WellRecord":
        data = json.loads(line)
        return cls(**data)

    def validate(self) -> list[str]:
        """Return list of validation errors (empty = valid)."""
        errors = []
        if not UUID_RE.match(self.record_id):
            errors.append(f"record_id must be UUIDv4, got {self.record_id!r}")
        if not ISO_RE.match(self.ts):
            errors.append(f"ts must be ISO-8601 UTC ending in Z, got {self.ts!r}")
        if self.kind not in VALID_KINDS:
            errors.append(f"kind must be one of {sorted(VALID_KINDS)}, got {self.kind!r}")
        if self.domain not in VALID_DOMAINS:
            errors.append(f"domain must be one of {sorted(VALID_DOMAINS)}, got {self.domain!r}")
        if self.status not in VALID_STATUSES:
            errors.append(f"status must be one of {sorted(VALID_STATUSES)}, got {self.status!r}")
        if self.status == "superseded" and not self.superseded_by:
            errors.append("superseded record must have superseded_by")
        if self.superseded_by and not UUID_RE.match(self.superseded_by):
            errors.append(f"superseded_by must be UUIDv4, got {self.superseded_by!r}")
        if not self.rule or not self.rule.strip():
            errors.append("rule must be non-empty")
        if not self.trigger or not self.trigger.strip():
            errors.append("trigger must be non-empty")
        # No secrets check: basic pattern matching
        secret_patterns = [
            r"api[_-]?key\s*[:=]\s*\S+",
            r"password\s*[:=]\s*\S+",
            r"secret\s*[:=]\s*\S+",
            r"token\s*[:=]\s*\S+",
            r"sk-[a-zA-Z0-9]{20,}",
            r"ghp_[a-zA-Z0-9]{30,}",
        ]
        for field_name in ("rule", "rationale", "trigger", "tags"):
            val = getattr(self, field_name, "")
            for pat in secret_patterns:
                if re.search(pat, val, re.IGNORECASE):
                    errors.append(f"{field_name} contains potential secret pattern")
        return errors


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def create_record(
    kind: str,
    source_pack: str,
    domain: str,
    trigger: str,
    rule: str,
    rationale: str,
    tags: str = "",
    status: Literal["active", "superseded"] = "active",
    superseded_by: str = "",
) -> WellRecord:
    """Factory that validates before returning."""
    rec = WellRecord(
        record_id=str(uuid.uuid4()),
        ts=now_iso(),
        kind=kind,
        source_pack=source_pack,
        domain=domain,
        trigger=trigger,
        rule=rule,
        rationale=rationale,
        tags=tags,
        status=status,
        superseded_by=superseded_by,
    )
    errs = rec.validate()
    if errs:
        raise ValueError("; ".join(errs))
    return rec


def append_record(rec: WellRecord) -> None:
    WELL_DIR.mkdir(parents=True, exist_ok=True)
    with WELL_JSONL.open("a", encoding="utf-8") as f:
        f.write(rec.to_jsonl() + "\n")


def load_all() -> list[WellRecord]:
    if not WELL_JSONL.is_file():
        return []
    records = []
    with WELL_JSONL.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = WellRecord.from_jsonl(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"well.jsonl line {i}: invalid JSON: {e}")
            records.append(rec)
    return records


def get_active() -> list[WellRecord]:
    return [r for r in load_all() if r.status == "active"]


def get_by_kind(kind: str) -> list[WellRecord]:
    return [r for r in load_all() if r.kind == kind]


def get_by_domain(domain: str) -> list[WellRecord]:
    return [r for r in load_all() if r.domain == domain]


def supersede(record_id: str, new_record_id: str) -> bool:
    """Mark record_id as superseded by new_record_id. Returns True if found."""
    records = load_all()
    found = False
    for rec in records:
        if rec.record_id == record_id:
            rec.status = "superseded"
            rec.superseded_by = new_record_id
            found = True
    if found:
        # Rewrite the whole file (append-only truth means we rewrite atomically)
        tmp = WELL_JSONL.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            for rec in records:
                f.write(rec.to_jsonl() + "\n")
        tmp.replace(WELL_JSONL)
    return found


def render_wisdom_md() -> str:
    """Generate human-readable WISDOM.md from active records."""
    active = get_active()
    if not active:
        return "# The Well\n\n*(empty — no active records)*\n"

    # Group by kind
    by_kind = {}
    for rec in active:
        by_kind.setdefault(rec.kind, []).append(rec)

    kind_order = ["correction", "preference", "tip", "anti_pattern", "insight", "dream"]
    lines = ["# The Well — Active Records", "", f"Generated: {now_iso()}", "", f"Total active: {len(active)}", ""]

    for kind in kind_order:
        if kind not in by_kind:
            continue
        lines.append(f"## {kind.capitalize()} ({len(by_kind[kind])})")
        lines.append("")
        for rec in sorted(by_kind[kind], key=lambda r: r.ts, reverse=True):
            tags = f" [{rec.tags}]" if rec.tags else ""
            lines.append(f"- **{rec.rule}**{tags}")
            if rec.rationale:
                lines.append(f"  *{rec.rationale}*")
            lines.append(f"  — pack: {rec.source_pack} | domain: {rec.domain} | id: {rec.record_id[:8]}")
            lines.append("")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def write_wisdom_md() -> None:
    WELL_MD.write_text(render_wisdom_md(), encoding="utf-8")


def stats() -> dict:
    all_recs = load_all()
    return {
        "total": len(all_recs),
        "active": len([r for r in all_recs if r.status == "active"]),
        "superseded": len([r for r in all_recs if r.status == "superseded"]),
        "by_kind": {k: len([r for r in all_recs if r.kind == k]) for k in VALID_KINDS},
        "by_domain": {d: len([r for r in all_recs if r.domain == d]) for d in VALID_DOMAINS},
        "by_status": {s: len([r for r in all_recs if r.status == s]) for s in VALID_STATUSES},
    }


def main():
    """CLI entry: `python3 scripts/well_storage.py <cmd> [args]`"""
    if len(sys.argv) < 2:
        print("Usage: well_storage.py <cmd> [args]")
        print("Commands:")
        print("  add <kind> <domain> <trigger> <rule> <rationale> [--tags TAGS] [--pack PACK]")
        print("  list [--kind KIND] [--domain DOMAIN] [--status active|all]")
        print("  stats")
        print("  supersede <old_id> <new_id>")
        print("  render-md")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "add":
        if len(sys.argv) < 7:
            print("Usage: add <kind> <domain> <trigger> <rule> <rationale> [--tags TAGS] [--pack PACK]")
            sys.exit(1)
        kind, domain, trigger, rule, rationale = sys.argv[2:7]
        tags = ""
        pack = "manual"
        for i, arg in enumerate(sys.argv[7:], 7):
            if arg == "--tags" and i + 1 < len(sys.argv):
                tags = sys.argv[i + 1]
            elif arg == "--pack" and i + 1 < len(sys.argv):
                pack = sys.argv[i + 1]
        try:
            rec = create_record(kind, pack, domain, trigger, rule, rationale, tags)
            append_record(rec)
            write_wisdom_md()
            print(f"Added {rec.record_id} ({rec.kind})")
        except ValueError as e:
            print(f"Validation error: {e}", file=sys.stderr)
            sys.exit(1)

    elif cmd == "list":
        kind = domain = None
        status = "active"
        for i, arg in enumerate(sys.argv[2:], 2):
            if arg == "--kind" and i + 1 < len(sys.argv):
                kind = sys.argv[i + 1]
            elif arg == "--domain" and i + 1 < len(sys.argv):
                domain = sys.argv[i + 1]
            elif arg == "--status" and i + 1 < len(sys.argv):
                status = sys.argv[i + 1]
        recs = load_all()
        if kind:
            recs = [r for r in recs if r.kind == kind]
        if domain:
            recs = [r for r in recs if r.domain == domain]
        if status == "active":
            recs = [r for r in recs if r.status == "active"]
        for r in recs:
            tag = f" [{r.tags}]" if r.tags else ""
            sup = f" → superseded by {r.superseded_by[:8]}" if r.status == "superseded" else ""
            print(f"{r.record_id[:8]} | {r.ts} | {r.kind:14s} | {r.domain:12s} | {r.rule[:60]}{tag}{sup}")

    elif cmd == "stats":
        s = stats()
        print(json.dumps(s, indent=2))

    elif cmd == "supersede":
        if len(sys.argv) < 4:
            print("Usage: supersede <old_id> <new_id>")
            sys.exit(1)
        if supersede(sys.argv[2], sys.argv[3]):
            write_wisdom_md()
            print(f"Superseded {sys.argv[2]} → {sys.argv[3]}")
        else:
            print(f"Record {sys.argv[2]} not found", file=sys.stderr)
            sys.exit(1)

    elif cmd == "render-md":
        write_wisdom_md()
        print(f"Rendered {WELL_MD}")

    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()