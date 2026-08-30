#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
q6_corruption_dryrun.py — Read-only structural schema probe over entity gnosis YAML.

Purpose (WAVE 0 step 3 / WAKE_STATE Q-6):
  Give the Architect an exact, line-anchored inventory of schema-flagged records so the
  real repair scope (schema normalization vs per-record triage) can be SIZED without any
  manual digging. This is a DRY-RUN SIZING tool: it has ZERO mutation capability.

  Context: ERRATA_AND_PROPAGATION.md Finding 2 — live S-2 probe counts ~29 flagged records
  across data/entities/lilith AND data/entities/maat (maat L44-52 newly discovered), while
  bare `yaml.safe_load` (gate G8) is green throughout (BS-1 window). G8-green is
  parseability truth, NOT schema truth.

Probe method (structural, sibling-consistency based):
  For every sequence-of-mappings in each scanned file:
    1. KEYSET DRIFT   — record key-set differs from the sibling MAJORITY key-set.
                        Healthy proposals cluster on {id,tier,category,narrative,
                        insight,principle,tags}-family shapes; variants such as
                        {lesson,source,trace_id,...} or split fragments are flagged.
    2. SPLIT RECORD   — ("id" in keys) != ("narrative" in keys): the record carries
                        identity without body or body without identity (the lilith
                        L374-380 shape).
    3. EMPTY REQUIRED — id/narrative/insight/principle present but null/empty.
    4. NON-MAPPING    — sequence item that is not a mapping at all.
  Files that fail to parse are reported as file-level PARSE_ERROR entries (honesty:
  never silently skipped).

Line numbers come from yaml.compose() node marks (no object construction needed).

STRICTLY READ-ONLY over scanned files: the script opens entity YAML read-only and
writes NOTHING except its JSON report to data/coordination/fle_study_20260825/
q6_inventory.json. There is no --apply flag by design.

Output: human-readable inventory to stdout + machine-readable JSON report.
Exit codes: 0 = scan completed (findings are expected, not errors)
            1 = with --fail-on-findings AND at least one finding
            2 = scan could not complete (missing dir / no files)

Run via the project venv (M24): .venv/bin/python scripts/q6_corruption_dryrun.py
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import yaml  # project venv dependency (already required by existing validators)

REPO_ROOT = Path(__file__).resolve().parent.parent
SCAN_GLOBS = [
    "data/entities/*/proposed_lessons.yaml",
    "data/entities/*/soul.yaml",
]
DEFAULT_REPORT = Path("data/coordination/fle_study_20260825/q6_inventory.json")

REQUIRED_KEYS = ("id", "narrative", "insight", "principle")

# Gnosis-record vocabulary: a sequence whose sibling-majority keyset intersects this
# set is treated as a gnosis-record container (full corruption rules apply). Sequences
# with NO overlap (config-ish subtrees like trait maps, provider lists) are reported
# as severity="info" observations — heterogeneous by design, NOT Q-6 corruption.
GNOSIS_VOCAB = {
    "id", "narrative", "insight", "principle", "tier", "category", "tags",
    "lesson", "l1", "l2", "l3",
    "l1_narrative", "l2_insight", "l3_principle", "l3_universal_principle",
}


def scalar_key_names(mapping_node: yaml.MappingNode) -> list[str]:
    """Extract scalar key names from a MappingNode (non-scalar keys → '<complex>')."""
    names = []
    for key_node, _ in mapping_node.value:
        if isinstance(key_node, yaml.ScalarNode):
            names.append(str(key_node.value))
        else:
            names.append("<complex>")
    return names


def scalar_value(node: yaml.Node) -> object:
    """Best-effort scalar extraction for reporting ids."""
    if isinstance(node, yaml.ScalarNode):
        return node.value
    return "<non-scalar>"


def iter_mapping_sequences(root_node: yaml.Node):
    """Yield (path, seq_node) for every sequence-of-mappings reachable in the tree."""
    stack = [("$root", root_node)]
    while stack:
        path, node = stack.pop()
        if isinstance(node, yaml.SequenceNode):
            mappings = [i for i in node.value if isinstance(i, yaml.MappingNode)]
            if mappings:
                yield path, node
            # still descend into non-mapping items for nested structures
            for idx, item in enumerate(node.value):
                if isinstance(item, (yaml.MappingNode, yaml.SequenceNode)):
                    stack.append((f"{path}[{idx}]", item))
        elif isinstance(node, yaml.MappingNode):
            for key_node, value_node in node.value:
                key = (
                    str(key_node.value)
                    if isinstance(key_node, yaml.ScalarNode)
                    else "<complex>"
                )
                if isinstance(value_node, (yaml.MappingNode, yaml.SequenceNode)):
                    stack.append((f"{path}.{key}", value_node))


def probe_sequence(path: str, seq_node: yaml.SequenceNode) -> list[dict]:
    """Sibling-consistency probe over one sequence of mappings."""
    findings: list[dict] = []
    records: list[tuple[int, yaml.MappingNode, list[str]]] = []

    for idx, item in enumerate(seq_node.value):
        if not isinstance(item, yaml.MappingNode):
            findings.append(
                {
                    "path": path,
                    "index": idx,
                    "line_start": item.start_mark.line + 1 if item.start_mark else None,
                    "line_end": item.end_mark.line + 1 if item.end_mark else None,
                    "record_id": None,
                    "keyset": None,
                    "reasons": ["NON_MAPPING_ITEM"],
                }
            )
            continue
        records.append((idx, item, scalar_key_names(item)))

    if not records:
        return findings

    # Sibling majority keyset (most common frozen keyset among mappings).
    keyset_counts = Counter(tuple(sorted(keys)) for _, _, keys in records)
    majority_keyset, _majority_n = keyset_counts.most_common(1)[0]

    # Container classification: gnosis-record container vs config-ish subtree.
    is_gnosis_container = bool(set(majority_keyset) & GNOSIS_VOCAB)
    majority_has_id_and_narrative = ("id" in majority_keyset) and ("narrative" in majority_keyset)

    for idx, node, keys in records:
        reasons: list[str] = []
        keyset_sorted = sorted(keys)
        if tuple(keyset_sorted) != majority_keyset:
            reasons.append("KEYSET_DRIFT_VS_SIBLINGS")
        key_set = set(keys)
        # Split-record: identity without body, or body without identity. Only meaningful
        # in containers whose healthy siblings carry BOTH id and narrative (e.g.
        # proposals[]). Directives/core_principles ({id,rule,rationale,...}) are a
        # different, legitimate schema family — never split-records by absence of
        # narrative alone.
        if (
            majority_has_id_and_narrative
            and (("id" in key_set) != ("narrative" in key_set))
            and (("id" in key_set) or ("narrative" in key_set))
        ):
            reasons.append("SPLIT_RECORD")
        # Empty required fields (present but null/empty).
        value_map = {}
        for key_node, value_node in node.value:
            if isinstance(key_node, yaml.ScalarNode):
                value_map[str(key_node.value)] = value_node
        for req in REQUIRED_KEYS:
            vn = value_map.get(req)
            if vn is not None and isinstance(vn, yaml.ScalarNode) and not str(vn.value or "").strip():
                reasons.append(f"EMPTY_REQUIRED:{req}")
        if not reasons:
            continue
        rid = None
        idn = value_map.get("id")
        if idn is not None and isinstance(idn, yaml.ScalarNode):
            rid = idn.value
        findings.append(
            {
                "path": path,
                "index": idx,
                "line_start": node.start_mark.line + 1,
                "line_end": node.end_mark.line + 1,
                "record_id": rid,
                "keyset": keyset_sorted,
                "sibling_majority_keyset": list(majority_keyset),
                "severity": "finding" if is_gnosis_container else "info",
                "reasons": reasons,
            }
        )
    return findings


def scan_file(fpath: Path) -> dict:
    entry: dict = {
        "file": str(fpath),
        "status": "OK",
        "flagged_records": [],
        "flagged_count": 0,
    }
    try:
        text = fpath.read_text(encoding="utf-8")
    except OSError as exc:
        entry["status"] = "READ_ERROR"
        entry["error"] = str(exc)
        return entry
    try:
        root_node = yaml.compose(text)
    except yaml.YAMLError as exc:
        entry["status"] = "PARSE_ERROR"
        entry["error"] = str(exc).splitlines()[0]
        return entry

    findings: list[dict] = []
    if root_node is not None:
        for path, seq_node in iter_mapping_sequences(root_node):
            findings.extend(probe_sequence(path, seq_node))

    entry["flagged_records"] = findings
    entry["flagged_count"] = sum(1 for f in findings if f.get("severity") == "finding")
    entry["info_count"] = sum(1 for f in findings if f.get("severity") == "info")
    return entry


def write_report_atomic(report_path: Path, payload: dict) -> None:
    """Atomic JSON report write (tmpfile + os.replace). Only artifact this tool writes."""
    report_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(report_path.parent), prefix=".q6_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_name, report_path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Read-only structural schema probe over data/entities/*/proposed_lessons.yaml "
            "+ soul.yaml. Dry-run sizing for Architect Q-6. Zero mutation capability."
        )
    )
    ap.add_argument("--root", type=Path, default=REPO_ROOT, help="Repo root.")
    ap.add_argument("--report", type=Path, default=None, help="JSON report path (default inside fle_study_20260825/).")
    ap.add_argument("--fail-on-findings", action="store_true", help="Exit 1 if any record is flagged.")
    args = ap.parse_args(argv)

    root: Path = args.root
    files: list[Path] = []
    for g in SCAN_GLOBS:
        files.extend(sorted(root.glob(g)))

    if not files:
        print("[Q-6 PROBE] FATAL: no entity YAML files matched under", root)
        return 2

    results = [scan_file(f) for f in files]

    total_flagged = sum(r["flagged_count"] for r in results)
    total_info = sum(r.get("info_count", 0) for r in results)
    per_file_summary = {
        r["file"]: {
            "status": r["status"],
            "flagged": r["flagged_count"],
            "info": r.get("info_count", 0),
        }
        for r in results
    }

    print("=" * 78)
    print("Q-6 CORRUPTION DRY-RUN — structural schema probe (STRICTLY READ-ONLY)")
    print("=" * 78)
    print(f"Scanned {len(files)} files:")
    for f in files:
        print(f"  · {f.relative_to(root)}")
    print()

    for r in results:
        rel = Path(r["file"]).relative_to(root)
        tag = r["status"]
        print(f"── {rel}  [{tag}]  flagged={r['flagged_count']} info={r.get('info_count', 0)}")
        if r["status"] != "OK":
            print(f"     error: {r.get('error', '')}")
            continue
        for rec in r["flagged_records"]:
            lines = (
                f"L{rec['line_start']}-{rec['line_end']}"
                if rec.get("line_start") and rec.get("line_end")
                else "L?"
            )
            rid = rec.get("record_id") or "<no-id>"
            keys = ",".join(rec["keyset"]) if rec.get("keyset") else "<non-mapping>"
            reasons = "+".join(rec["reasons"])
            sev = rec.get("severity", "finding")
            marker = "⚑" if sev == "finding" else "ℹ"
            print(f"     {marker} {lines:<14} idx={rec['index']:<3} id={rid!r:<45} [{keys}]")
            print(f"       └─ {reasons}  (path={rec['path']})")
        print()

    print("─" * 78)
    print("PER-FILE SUMMARY  (⚑ finding = Q-6 corruption · ℹ info = heterogeneous-by-design)")
    for fname, s in per_file_summary.items():
        print(f"  {s['flagged']:>4} flagged · {s.get('info', 0):>3} info · {s['status']:<12} {fname}")
    print(f"\nTOTAL FLAGGED RECORDS (Q-6 findings): {total_flagged}   (+{total_info} informational)")
    print(
        "NOTE: parseability (G8) being green says nothing about these findings —\n"
        "      this probe measures SCHEMA truth (BS-1 window). Repair itself remains\n"
        "      MaKaLi-single-writer scope (Art. IX) pending Architect Q-6 sizing."
    )

    report_path: Path = args.report or (root / DEFAULT_REPORT)
    payload = {
        "tool": "scripts/q6_corruption_dryrun.py",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "dry-run / strictly read-only",
        "scan_globs": SCAN_GLOBS,
        "files_scanned": len(files),
        "total_flagged_records": total_flagged,
        "per_file_summary": per_file_summary,
        "results": results,
    }
    write_report_atomic(report_path, payload)
    print(f"\nJSON report written: {report_path}")

    if args.fail_on_findings and total_flagged > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
