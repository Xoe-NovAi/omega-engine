#!/usr/bin/env python3
"""Derive flat-contract evaluation sets from the existing sms_real_v1 holdout.

No new labelling happens here. Every gold value is a projection of gold that a
labelled capture already produced, so the decomposition comparison is matched:
the same underlying cases, scored under a complex contract and under the flat
contract that replaces it.

  place_classifier   <- mempalace_extractor gold.wing / gold.room
  quote_extractor    <- mempalace_extractor gold.items[0] (content + source_quote)
  pii_action         <- privacy_sentinel gold.action (spans handed in, already found)
  supersede_decider  <- well_curator gold.action / gold.superseded_by

Two filters are load-bearing:

  * quote_extractor drops any case whose gold source_quote is not a substring
    of its own input — a label that cannot be grounded is not a label the flat
    contract could ever score honestly. (Extraction asserts this at capture
    time; the check is re-run here rather than assumed.)
  * supersede_decider keeps only keep/supersede, because merge and drop are
    curation decisions that the split contract does not own. Cases dropped for
    either reason are counted and written to the manifest, not silently lost.

Outputs:
  ~/WanderGround/datasets/sms/derived/<role>_holdout.jsonl
  ~/WanderGround/datasets/sms/derived/<role>_train.jsonl
  ~/WanderGround/datasets/sms/derived/all_flat_{holdout,train}.jsonl  (union, so one
    gauntlet invocation resolves exemplars for all four roles from one file)
  ~/WanderGround/datasets/sms/derived/manifest.json

Run:  python3 scripts/sms/decomposition/build_derived.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.sms.decomposition import roles as droles  # noqa: E402

SMS_DIR = Path.home() / "WanderGround" / "datasets" / "sms"
OUT_DIR = SMS_DIR / "derived"
HOLDOUT = SMS_DIR / "sms_real_v1_holdout.jsonl"
TRAIN = SMS_DIR / "sms_real_v1_train.jsonl"
PARENT = {
    "place_classifier": "mempalace_extractor",
    "quote_extractor": "mempalace_extractor",
    "pii_action": "privacy_sentinel",
    "supersede_decider": "well_curator",
}


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def derive_place(row: dict) -> dict | None:
    gold = row["gold"]
    wing, room = gold.get("wing"), gold.get("room")
    if not isinstance(wing, str) or not wing or not isinstance(room, str) or not room:
        return None
    return {
        "role": "place_classifier",
        "case_id": str(row["case_id"]).replace("ex_", "pc_"),
        "input": row["input"],
        "gold": {"wing": wing, "room": room},
        "tags": row.get("tags", []),
        "source_file": row.get("source_file"),
        "source_group": row.get("source_group"),
        "labeler": "derived:mempalace_extractor.gold.wing+room",
        "derived_from_case": row["case_id"],
        "recorded_at": row.get("recorded_at"),
    }


def derive_quote(row: dict) -> dict | None:
    gold = row["gold"]
    items = gold.get("items") or []
    if not items:
        return None
    first = items[0]
    content, quote = first.get("content"), first.get("source_quote")
    if not isinstance(content, str) or not content:
        return None
    if not isinstance(quote, str) or not quote or quote not in row["input"]:
        return None
    return {
        "role": "quote_extractor",
        "case_id": str(row["case_id"]).replace("ex_", "qe_"),
        "input": row["input"],
        "gold": {"content": content, "source_quote": quote},
        "tags": row.get("tags", []),
        "source_file": row.get("source_file"),
        "source_group": row.get("source_group"),
        "labeler": "derived:mempalace_extractor.gold.items[0]",
        "derived_from_case": row["case_id"],
        "recorded_at": row.get("recorded_at"),
    }


def derive_pii(row: dict) -> dict | None:
    gold = row["gold"]
    action = gold.get("action")
    if action not in ("allow", "redact", "drop"):
        return None
    spans = gold.get("pii_found") or []
    found = "; ".join(f"{s.get('type')}={s.get('span')}" for s in spans if isinstance(s, dict))
    # Detection is upstream: the decision maker is handed the spans and the text.
    text = row["input"]
    context = f"text: {text}\nspans_found: {found if found else '(none)'}"
    return {
        "role": "pii_action",
        "case_id": str(row["case_id"]).replace("ps_", "pa_"),
        "input": text,
        "context_fields": {"text": text, "spans_found": found if found else "(none)"},
        "gold": {"action": action},
        "tags": row.get("tags", []),
        "source_file": row.get("source_file"),
        "source_group": row.get("source_group"),
        "labeler": "derived:privacy_sentinel.gold.action",
        "derived_from_case": row["case_id"],
        "recorded_at": row.get("recorded_at"),
    }


def derive_supersede(row: dict) -> dict | None:
    gold = row["gold"]
    action = gold.get("action")
    if action not in ("keep", "supersede"):
        return None
    superseded_by = gold.get("superseded_by")
    if action == "supersede":
        if not isinstance(superseded_by, str) or not superseded_by:
            return None
    else:
        superseded_by = None
    lines = [str(row["input"])]
    chain = [ln for ln in lines[0].splitlines() if ln.startswith("chain records you can see:")]
    lines = chain if chain else lines
    return {
        "role": "supersede_decider",
        "case_id": str(row["case_id"]).replace("wc_", "sd_"),
        "input": "\n".join(lines),
        "gold": {"action": action, "superseded_by": superseded_by},
        "tags": row.get("tags", []),
        "source_file": row.get("source_file"),
        "source_group": row.get("source_group"),
        "labeler": "derived:well_curator.gold.action+superseded_by",
        "derived_from_case": row["case_id"],
        "recorded_at": row.get("recorded_at"),
    }


DERIVERS = {
    "place_classifier": derive_place,
    "quote_extractor": derive_quote,
    "pii_action": derive_pii,
    "supersede_decider": derive_supersede,
}


def derive_all(rows: list[dict]) -> tuple[dict[str, list[dict]], dict[str, dict]]:
    per_role: dict[str, list[dict]] = {r: [] for r in droles.DECOMPOSITION_ROLES}
    stats: dict[str, dict] = {}
    for role, fn in DERIVERS.items():
        parent_rows = [r for r in rows if r.get("role") == PARENT[role]]
        kept, dropped = [], 0
        for row in parent_rows:
            out = fn(row)
            if out is None:
                dropped += 1
                continue
            kept.append(out)
        per_role[role] = kept
        stats[role] = {
            "parent_role": PARENT[role],
            "parent_rows": len(parent_rows),
            "derived_rows": len(kept),
            "dropped": dropped,
            "gold_distribution": _gold_distribution(role, kept),
        }
    return per_role, stats


def _gold_distribution(role: str, rows: list[dict]) -> dict[str, int]:
    """Which gold field is the decision for each role."""
    if role == "place_classifier":
        key = "wing"
    elif role == "quote_extractor":
        return {"grounded_quote_rows": len(rows)}
    else:
        key = "action"
    return dict(Counter(str(r["gold"].get(key)) for r in rows))


def sha256_rows(rows: list[dict]) -> str:
    blob = "\n".join(json.dumps(r, sort_keys=True, ensure_ascii=False) for r in rows).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Derive flat-contract sets from sms_real_v1 splits.")
    ap.add_argument("--holdout", default=str(HOLDOUT))
    ap.add_argument("--train", default=str(TRAIN))
    ap.add_argument("--out-dir", default=str(OUT_DIR))
    args = ap.parse_args(argv)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest: dict = {
        "dataset_id": "sms_derived_flat_v1",
        "derived_from": "sms_real_v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "derivation": "projection of existing gold only; no new labelling",
        "roles": {},
    }
    for split, path in (("holdout", Path(args.holdout)), ("train", Path(args.train))):
        rows = load(path)
        per_role, stats = derive_all(rows)
        union: list[dict] = []
        for role, role_rows in per_role.items():
            dest = out_dir / f"{role}_{split}.jsonl"
            with dest.open("w", encoding="utf-8") as f:
                for r in role_rows:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
            stats[role].update({
                "holdout_file": dest.name if split == "holdout" else None,
                "train_file": dest.name if split == "train" else None,
                f"{split}_sha256_16": sha256_rows(role_rows),
            })
            union.extend(role_rows)
            print(f"[derived] {split:7s} {role:20s} {len(role_rows):3d} rows -> {dest.name}")
        union_dest = out_dir / f"all_flat_{split}.jsonl"
        with union_dest.open("w", encoding="utf-8") as f:
            for r in union:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        manifest["union_file"] = manifest.get("union_file", {})
        manifest["union_file"][split] = union_dest.name
        manifest["union_sha256_16"] = manifest.get("union_sha256_16", {})
        manifest["union_sha256_16"][split] = sha256_rows(union)
        print(f"[derived] {split:7s} {'ALL':20s} {len(union):3d} rows -> {union_dest.name}")
        manifest["roles"].setdefault(split, {}).update(stats)
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"[derived] manifest -> {out_dir / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())