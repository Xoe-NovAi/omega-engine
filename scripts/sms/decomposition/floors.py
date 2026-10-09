#!/usr/bin/env python3
"""Trivial-prior floors for one dataset + one or more gauntlet runs.

Phase 2 established that a score only means something next to two constants:

  constant_string_floor  accuracy of emitting ONE fixed output on every case,
                         scored with the role's own scorer. It is a property of
                         the run (the model chose that string) so it needs the
                         run's rows.
  majority_gold_floor    accuracy of emitting the most common GOLD on every
                         case. It is a property of the dataset alone and needs
                         no model.

Both are computed by calling the role's real scorer, never by arithmetic on a
headline number, so a floor can never drift from the metric it bounds.

Usage:
  python3 scripts/sms/decomposition/floors.py \
      --dataset ~/WanderGround/datasets/sms/p3/all_p3_holdout.jsonl \
      --runs runs/sms_p3_zs_20261008 runs/sms_p3_fs2even_20261008 \
      --roles supersede_decider well_curator \
      --metric action_exact \
      --out runs/sms_p3_zs_20261008/floors.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.sms import roles as parent_roles  # noqa: E402
from scripts.sms.decomposition import roles as flat_roles  # noqa: E402
from scripts.sms.scoring import echo  # noqa: E402

#: Primary metric per role. Mirrors decomposition.compare.PAIRS plus the two
#: roles phase 3 measures directly.
DEFAULT_METRIC = {
    "well_curator": "action_exact",
    "supersede_decider": "action_exact",
    "mempalace_extractor": "wing_exact",
    "place_classifier": "wing_exact",
    "quote_extractor": "quote_grounded",
    "privacy_sentinel": "action_exact",
    "pii_action": "action_exact",
    "tool_router": "tool_exact",
    "failure_classifier": "class_exact",
}


def scorer_for(role: str):
    return flat_roles.score_case if role in flat_roles.DECOMPOSITION_ROLES else parent_roles.score_case


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def majority_gold_floor(dataset_rows: list[dict], role: str, metric: str) -> dict:
    """Always answer the most common gold. A dataset-only constant."""
    rows = [r for r in dataset_rows if r.get("role") == role]
    if not rows:
        return {"n": 0, "accuracy": None, "answer": None, "gold_distribution": {}}
    blobs = Counter(json.dumps(r["gold"], sort_keys=True, ensure_ascii=False) for r in rows)
    modal_blob, modal_n = blobs.most_common(1)[0]
    modal_gold = json.loads(modal_blob)
    scorer = scorer_for(role)
    total = sum(float(scorer(role, modal_gold, r["gold"], r).get(metric, 0.0) or 0.0) for r in rows)
    return {
        "n": len(rows),
        "accuracy": round(total / len(rows), 3),
        "answer": modal_gold,
        "modal_gold_share": round(modal_n / len(rows), 3),
        "gold_distribution": {k: v for k, v in Counter(str(r["gold"].get("action") or r["gold"].get("class")
                                                                   or r["gold"].get("tool")
                                                                   or r["gold"].get("wing"))
                                                  for r in rows).items()},
    }


def constant_string_floor(run_rows: list[dict], role: str, metric: str, dataset: list[dict]) -> dict:
    """Always emit the string this run emitted most often. Needs the run.

    The SAME string is scored against every case's gold — that is the whole
    definition of the constant predictor. (Scoring each row's own output here
    would just return the model's accuracy under a floor-shaped name.)
    """
    rows = [r for r in run_rows if r["role"] == role]
    if not rows:
        return {"n": 0, "scored": 0, "accuracy": None, "answer": None, "modal_repeats": 0}
    scorer = scorer_for(role)
    by_id = {str(r["case_id"]): r for r in dataset if r.get("role") == role}
    modal_raw = Counter(r["raw_output"] for r in rows).most_common(1)[0][0]
    modal_obj = _parse(modal_raw)
    total, scored = 0.0, 0
    for r in rows:
        case = by_id.get(str(r["case_id"]))
        if case is None:
            continue
        if modal_obj is None:
            # A non-JSON answer scores 0 under the harness rule (metrics are only
            # computed for conformant dicts), so count it as a miss, not a skip.
            total += 0.0
            scored += 1
            continue
        total += float(scorer(role, modal_obj, case["gold"], case).get(metric, 0.0) or 0.0)
        scored += 1
    em = echo.echo_metrics(r["raw_output"] for r in rows)
    return {
        "n": len(rows),
        "scored": scored,
        "accuracy": round(total / scored, 3) if scored else None,
        "answer": modal_raw,
        "modal_repeats": em["copy_suspect_n"],
    }


def _parse(raw: str):
    try:
        obj = json.loads(raw)
    except (json.JSONDecodeError, TypeError, ValueError):
        return None
    return obj if isinstance(obj, dict) else None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Constant-string and majority-gold floors.")
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--roles", nargs="+", required=True)
    ap.add_argument("--metric", default=None, help="override the primary metric for every role")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    dataset = load_jsonl(Path(args.dataset))
    payload = {
        "dataset": str(Path(args.dataset)),
        "echo_ratio_threshold": echo.ECHO_RATIO_THRESHOLD,
        "echo_min_n": echo.ECHO_MIN_N,
        "roles": {},
        "runs": {},
    }
    for role in args.roles:
        metric = args.metric or DEFAULT_METRIC[role]
        payload["roles"][role] = {
            "metric": metric,
            "majority_gold_floor": majority_gold_floor(dataset, role, metric),
        }
        print(f"[floor] {role:20s} metric={metric:14s} majority_gold="
              f"{payload['roles'][role]['majority_gold_floor']['accuracy']}")

    for run in args.runs:
        run_dir = Path(run)
        rows = load_jsonl(run_dir / "results.jsonl")
        entry: dict = {}
        for role in args.roles:
            metric = args.metric or DEFAULT_METRIC[role]
            csf = constant_string_floor(rows, role, metric, dataset)
            entry[role] = {"metric": metric, "constant_string_floor": csf}
            print(f"[floor] {run_dir.name:26s} {role:20s} constant_string={csf['accuracy']}")
        payload["runs"][run_dir.name] = entry

    out = Path(args.out) if args.out else Path(args.runs[0]) / "floors.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"[floor] -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())