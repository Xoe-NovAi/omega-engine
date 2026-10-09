#!/usr/bin/env python3
"""Compare the complex v1 contracts against the flat decomposed chain.

Reads two gauntlet runs over MATCHED holdout cases and answers one question per
pair: did the flat contract beat its complex parent on the primary metric, and
did it do so without collapsing into exemplar echo?

The prior check is the point. A 0.917 exact-match is worthless if the model
answers the same thing on every case and the gold happens to be skewed that way,
so every row reports two reference points:

  modal_prior_acc   accuracy of a CONSTANT predictor that emits the model's own
                    most common output on every case. If the model's real score
                    equals this, the score is the format, not the reasoning.
  majority_gold_acc accuracy of a CONSTANT predictor that emits the most common
                    GOLD answer — the trivial floor any classifier must clear.

Verdict rule (applied in code, not only in prose): a flat contract WINS only if
it beats its parent's primary metric AND copy_suspect is false. Anything else is
reported as-is, including losses.

Usage:
  python3 scripts/sms/decomposition/compare.py \
      --baseline runs/sms_p2_baseline_20261008 \
      --flat runs/sms_p2_flat_20261008 \
      --out runs/sms_p2_decomposition_20261008/comparison.md
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

#: parent role -> (primary metric key, flat role, flat primary metric key)
PAIRS = (
    ("mempalace_extractor", "wing_exact", "place_classifier", "wing_exact"),
    ("mempalace_extractor", "provenance_preserved", "quote_extractor", "quote_grounded"),
    ("privacy_sentinel", "action_exact", "pii_action", "action_exact"),
    ("well_curator", "action_exact", "supersede_decider", "action_exact"),
)


def load_run(run_dir: Path) -> tuple[dict, list[dict]]:
    scoring = json.loads((run_dir / "scoring.json").read_text(encoding="utf-8"))
    results = [json.loads(ln) for ln in (run_dir / "results.jsonl").read_text(encoding="utf-8").splitlines() if ln.strip()]
    return scoring, results


def key_for(scoring: dict, role: str) -> str | None:
    for key in scoring:
        if key.split("|", 1)[1] == role:
            return key
    return None


def modal_prior_acc(rows: list[dict], metric: str) -> float:
    """Accuracy of always emitting this run's most common raw output."""
    if not rows:
        return 0.0
    modal_raw = Counter(r["raw_output"] for r in rows).most_common(1)[0][0]
    modal_ids = {r["case_id"] for r in rows if r["raw_output"] == modal_raw}
    return round(sum(r["metrics"].get(metric, 0.0) or 0.0 for r in rows if r["case_id"] in modal_ids) / len(rows), 3)


def majority_gold_acc(dataset: Path, role: str, metric: str) -> float | None:
    """Accuracy of a constant predictor that always emits the most common GOLD.

    Scored with the role's own scorer, so it is the same metric the model is
    graded on. This is the trivial floor: any model that cannot beat it has not
    learned anything the class prior does not already give away.
    """
    if not dataset or not dataset.exists():
        return None
    scorer = flat_roles.score_case if role in flat_roles.DECOMPOSITION_ROLES else parent_roles.score_case
    rows = [json.loads(ln) for ln in dataset.read_text(encoding="utf-8").splitlines() if ln.strip()]
    rows = [r for r in rows if r.get("role") == role]
    if not rows:
        return None
    modal_gold = json.loads(Counter(json.dumps(r["gold"], sort_keys=True) for r in rows).most_common(1)[0][0])
    total = 0.0
    for r in rows:
        metrics = scorer(role, modal_gold, r["gold"], r)
        total += float(metrics.get(metric, 0.0) or 0.0)
    return round(total / len(rows), 3)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Complex vs decomposed contract comparison.")
    ap.add_argument("--baseline", required=True, help="run dir with the complex v1 contracts")
    ap.add_argument("--flat", required=True, help="run dir with the flat contracts")
    ap.add_argument("--baseline-dataset", default=None,
                    help="dataset behind the baseline run (for majority_gold_acc); "
                         "defaults to <baseline>/../ dataset inferred from results inputs")
    ap.add_argument("--flat-dataset", default=None, help="dataset behind the flat run")
    ap.add_argument("--out", default="", help="write markdown here (default: <flat>/comparison.md)")
    ap.add_argument("--json-out", default="", help="write the machine-readable comparison here")
    args = ap.parse_args(argv)

    base_dir, flat_dir = Path(args.baseline), Path(args.flat)
    b_score, b_rows = load_run(base_dir)
    f_score, f_rows = load_run(flat_dir)

    flat_dataset = Path(args.flat_dataset) if args.flat_dataset else None
    baseline_dataset = Path(args.baseline_dataset) if args.baseline_dataset else None

    comparisons = []
    for parent_role, parent_metric, flat_role, flat_metric in PAIRS:
        bk, fk = key_for(b_score, parent_role), key_for(f_score, flat_role)
        if not bk or not fk:
            print(f"[skip] {parent_role} / {flat_role}: missing from one run", file=sys.stderr)
            continue
        b, f = b_score[bk], f_score[fk]
        b_role_rows = [r for r in b_rows if r["role"] == parent_role]
        f_role_rows = [r for r in f_rows if r["role"] == flat_role]
        # Matched cases: only evaluate the parent's rows that the flat run also saw.
        flat_ids = {r["case_id"].replace("pc_", "ex_").replace("qe_", "ex_")
                    .replace("pa_", "ps_").replace("sd_", "wc_") for r in f_role_rows}
        matched_b = [r for r in b_role_rows if r["case_id"] in flat_ids] or b_role_rows
        b_pm = b.get("per_metric_mean", {})
        f_pm = f.get("per_metric_mean", {})
        f_em = echo.echo_metrics(r["raw_output"] for r in f_role_rows)
        comparisons.append({
            "parent_role": parent_role,
            "parent_metric": parent_metric,
            "flat_role": flat_role,
            "flat_metric": flat_metric,
            "parent": {
                "n": b["n"], "matched_n": len(matched_b),
                "schema_conformant_pct": b["schema_conformant_pct"],
                "primary": b_pm.get(parent_metric),
                "modal_prior_acc": modal_prior_acc(matched_b, parent_metric),
                "exact_match_mean": b["exact_match_mean"],
                "p50_s": b["latency"]["p50"], "p95_s": b["latency"]["p95"],
                "mean_output_tokens": b["mean_output_tokens"],
                "distinct_output_ratio": b["distinct_output_ratio"],
                "modal_output_share": b["modal_output_share"],
                "copy_suspect": b["copy_suspect"],
            },
            "flat": {
                "n": f["n"],
                "schema_conformant_pct": f["schema_conformant_pct"],
                "primary": f_pm.get(flat_metric),
                "modal_prior_acc": modal_prior_acc(f_role_rows, flat_metric),
                "exact_match_mean": f["exact_match_mean"],
                "p50_s": f["latency"]["p50"], "p95_s": f["latency"]["p95"],
                "mean_output_tokens": f["mean_output_tokens"],
                "distinct_output_ratio": f["distinct_output_ratio"],
                "modal_output_share": f["modal_output_share"],
                "copy_suspect": f["copy_suspect"],
                "modal_output": f_em and Counter(r["raw_output"] for r in f_role_rows).most_common(1)[0][0],
                "modal_output_count": f_em["copy_suspect_n"],
            },
        })

    # Prior checks need the gold distribution, which lives in the datasets.
    for c in comparisons:
        c["priors"] = {
            "flat_majority_gold_acc": majority_gold_acc(flat_dataset, c["flat_role"], c["flat_metric"]),
            "parent_majority_gold_acc": majority_gold_acc(baseline_dataset, c["parent_role"], c["parent_metric"]),
        }

    payload = {
        "baseline_run": str(base_dir), "flat_run": str(flat_dir),
        "flat_dataset": str(flat_dataset) if flat_dataset else None,
        "baseline_dataset": str(baseline_dataset) if baseline_dataset else None,
        "comparisons": comparisons,
        "verdicts": {f"{c['flat_role']}": verdict(c) for c in comparisons},
    }
    out_json = Path(args.json_out) if args.json_out else flat_dir / "comparison.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    out_md = Path(args.out) if args.out else flat_dir / "comparison.md"
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(render_markdown(payload) + "\n", encoding="utf-8")
    print(render_markdown(payload))
    print(f"[done] {out_md} · {out_json}")
    return 0


def verdict(c: dict) -> dict:
    """The rule: win requires beating the parent AND no echo collapse."""
    p, f = c["parent"]["primary"], c["flat"]["primary"]
    delta = None if (p is None or f is None) else round(f - p, 3)
    modal = c["flat"]["modal_prior_acc"] if "modal_prior_acc" in c else None
    beats = delta is not None and delta > 0
    echo_collapse = bool(c["flat"]["copy_suspect"]) or (
        c["flat"]["distinct_output_ratio"] < echo.ECHO_RATIO_THRESHOLD)
    if beats and not echo_collapse:
        label = "WIN"
    elif beats and echo_collapse:
        label = "PRIOR-DOMINATED (beat parent, but collapsed into echo)"
    else:
        label = "NO WIN"
    return {
        "label": label,
        "primary_delta": delta,
        "beats_parent": beats,
        "echo_collapse": echo_collapse,
        "token_ratio_parent_over_flat": round(
            c["parent"]["mean_output_tokens"] / max(1e-9, c["flat"]["mean_output_tokens"]), 2),
        "p95_delta_s": round(c["flat"]["p95_s"] - c["parent"]["p95_s"], 2),
        "schema_delta_pts": round(
            c["flat"]["schema_conformant_pct"] - c["parent"]["schema_conformant_pct"], 1),
        "modal_output_repeats": c["flat"].get("modal_output_count", 0),
        "flat_modal_prior_acc": c["flat"].get("modal_prior_acc"),
        "majority_gold_acc": (c.get("priors") or {}).get("flat_majority_gold_acc"),
        "parent_modal_prior_acc": c["parent"].get("modal_prior_acc"),
        "parent_majority_gold_acc": (c.get("priors") or {}).get("parent_majority_gold_acc"),
    }


def render_markdown(p: dict) -> str:
    lines = ["# Complex vs decomposed contracts — measured comparison", ""]
    lines.append(f"- baseline (complex v1 contracts): `{p['baseline_run']}`")
    lines.append(f"- flat (decomposed chain): `{p['flat_run']}`")
    lines.append("")
    lines.append("| pair | primary metric | complex | flat | delta | complex schema% | flat schema% | complex tok | flat tok | complex p95 | flat p95 | flat distinct_ratio | flat modal_share | copy_suspect | verdict |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:--:|---|")
    for c in p["comparisons"]:
        v = p["verdicts"][c["flat_role"]]
        lines.append(
            f"| {c['parent_role']} → {c['flat_role']} | {c['parent_metric']} / {c['flat_metric']} | "
            f"{c['parent']['primary']} | {c['flat']['primary']} | {v['primary_delta']} | "
            f"{c['parent']['schema_conformant_pct']} | {c['flat']['schema_conformant_pct']} | "
            f"{c['parent']['mean_output_tokens']} | {c['flat']['mean_output_tokens']} | "
            f"{c['parent']['p95_s']} | {c['flat']['p95_s']} | "
            f"{c['flat']['distinct_output_ratio']} | {c['flat']['modal_output_share']} | "
            f"{'YES' if c['flat']['copy_suspect'] else 'no'} | **{v['label']}** |"
        )
    lines.append("")
    lines.append("## Prior check — is the score anything but the class prior?")
    lines.append("")
    lines.append("| flat role | flat primary | flat modal_prior_acc | majority_gold_acc | reading |")
    lines.append("|---|---:|---:|---:|---|")
    for c in p["comparisons"]:
        v = p["verdicts"][c["flat_role"]]
        flat_prior, gold_prior = v["flat_modal_prior_acc"], v["majority_gold_acc"]
        if flat_prior is None or gold_prior is None:
            reading = "prior check unavailable (dataset not supplied)"
        elif abs((flat_prior or 0) - (c["flat"]["primary"] or 0)) < 0.02:
            reading = ("**model == its own modal constant** — the score is the output format, "
                       "not the reasoning")
        elif (c["flat"]["primary"] or 0) <= (gold_prior or 0):
            reading = "**at or below the majority-gold floor** — not distinguishable from the prior"
        else:
            reading = "clears the majority-gold floor"
        lines.append(f"| {c['flat_role']} | {c['flat']['primary']} | {flat_prior} | {gold_prior} | {reading} |")
    lines.append("")
    lines.append("## Modal output of each flat contract")
    lines.append("")
    for c in p["comparisons"]:
        f = c["flat"]
        lines.append(f"- `{c['flat_role']}`: modal output `{str(f.get('modal_output', ''))[:110]}` "
                     f"(x{f.get('modal_output_count', 0)}/{f['n']})")
    lines.append("")
    lines.append("## Verdict rule")
    lines.append("")
    lines.append("A flat contract wins only if it beats its complex parent on the primary metric "
                 "**and** does not collapse into exemplar echo "
                 f"(`distinct_output_ratio < {echo.ECHO_RATIO_THRESHOLD}`). "
                 "Trade-offs in latency or schema conformance are reported, never counted as accuracy.")
    lines.append("")
    wins = [k for k, v in p["verdicts"].items() if v["label"] == "WIN"]
    losses = [k for k, v in p["verdicts"].items() if v["label"] != "WIN"]
    lines.append(f"- wins: {', '.join(wins) if wins else '**none**'}")
    lines.append(f"- not wins: {', '.join(losses) if losses else 'none'}")
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())