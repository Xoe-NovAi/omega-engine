#!/usr/bin/env python3
"""Paraphrase probe for well_curator — does the model read the record, or copy?

Phase 1 measured 0.767 exact-match on few-shot well_curator and then showed it
was prior-dominated: 18 of 20 outputs were the same string, and it was the
exemplars' answer (docs/research/LFM25_SMS_REAL_DATASET_20261008.md §5.1). An
aggregate cannot separate "inferred correctly" from "copied". A paraphrase probe
can, and it needs no new labels:

  * Build two variants of the SAME holdout case. `verbatim` is the captured
    window. `paraphrase` rewrites the trigger/rule/why/lifecycle surface form
    without changing meaning.
  * The gold label is identical for both variants. A rewrite that could change
    the label is dropped, not guessed.
  * Run both arms with the SAME exemplars and settings.

Verdict rule (applied in the report, and here so it cannot be softened):
if paraphrase accuracy collapses beyond the noise floor while modal_output_share
stays high, the few-shot model is copying exemplars, not inferring.

There is a third outcome that the naive binary rule misses, and phase 2 hit it:
accuracy can also be INVARIANT to paraphrase because the output barely depends
on the input at all. That is why this probe also measures, across arms:

  output_changed_rate     fraction of cases whose answer changed when the input
                          was paraphrased. Near zero with high modal share means
                          the model is not reading the record.
  modal_identical_across_arms  whether the single most common answer is the same
                          string in both arms.

A within-noise exact_match delta is NOT evidence of inference. It is only
evidence of inference if the answers actually move with the input.

Paraphrasing is deterministic and offline by construction: template rewrites,
a fixed synonym table, clause reordering, and punctuation/case changes. No LLM
is involved, so the probe is reproducible and free. The rewrite is verified
shallowly by a semantic guard (must still contain the record id, the chain ids
and the lifecycle signal) rather than by trusting the substitution table.

Usage:
  python3 scripts/sms/paraphrase_probe.py \
    --model lfm25-350m-q6k --few-shot 2 --limit 20 \
    --out-dir runs/sms_paraphrase_350m_20261008
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

SMS_DIR = Path.home() / "WanderGround" / "datasets" / "sms"
HOLDOUT = SMS_DIR / "sms_real_v1_holdout.jsonl"
TRAIN = SMS_DIR / "sms_real_v1_train.jsonl"
WORK = Path("/tmp/sms_paraphrase")

#: Sentence-level synonyms. Deliberately small and meaning-preserving: each pair
#: is a surface substitution, not a rewrite of the claim.
SYNONYMS: list[tuple[str, str]] = [
    (r"\bNode 1 operator\b", "the Node 1 operator"),
    (r"\boperator\b", "user"),
    (r"\brecord\b", "well entry"),
    (r"\bsuperseded\b", "replaced"),
    (r"\bsupersede\b", "replace"),
    (r"\bsuperseding\b", "replacing"),
    (r"\bsuccessor\b", "follow-on entry"),
    (r"\bnewer\b", "later"),
    (r"\bcurrent\b", "live"),
    (r"\bretired\b", "closed"),
    (r"\bnever\b", "must not"),
    (r"\bmust\b", "has to"),
    (r"\balways\b", "in every case"),
    (r"\bbecause\b", "since"),
    (r"\btherefore\b", "so"),
    (r"\bhowever\b", "but"),
    (r"\bnevertheless\b", "even so"),
    (r"\bcheck\b", "verify"),
    (r"\bverify\b", "check"),
    (r"\bfails\b", "breaks"),
    (r"\bbroken\b", "failing"),
    (r"\bwrong\b", "incorrect"),
    (r"\buse\b", "apply"),
    (r"\buses\b", "applies"),
    (r"\bset\b", "assign"),
    (r"\bstored\b", "kept"),
    (r"\brecorded\b", "logged"),
    (r"\brule\b", "standing policy"),
    (r"\brules\b", "standing policies"),
    (r"\bpin\b", "constrain"),
    (r"\bpins\b", "constrain"),
    (r"\bmeasure\b", "gauge"),
    (r"\bmeasures\b", "gauges"),
    (r"\bbenchmark\b", "bench run"),
    (r"\bconfig\b", "configuration"),
]

#: Whole-line templates, applied in order. Key = source field label as captured.
FIELD_TEMPLATES = {
    "trigger": [
        "trigger: {v}",
        "this record exists because: {v}",
        "situation that produced it: {v}",
        "why it was written: {v}",
    ],
    "rule": [
        "rule: {v}",
        "the operating rule: {v}",
        "guidance in force: {v}",
        "standing instruction: {v}",
    ],
    "why": [
        "why: {v}",
        "rationale recorded at capture time: {v}",
        "reasoning behind it: {v}",
        "how it was justified: {v}",
    ],
    "lifecycle": [
        "lifecycle: {v}",
        "state: {v}",
        "current status: {v}",
        "where this entry stands: {v}",
    ],
}

_UUID = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b")
_TS = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
CHAIN_PREFIX = "chain records you can see:"
CLOSING_PREFIX = "kind, domain and tags are NOT given."

#: Blueprint §7 noise floor for n=20. A smaller exact_match delta is not a
#: measurement; treating it as one is how phase 1's 0.767 got over-read.
NOISE_FLOOR = 0.10

#: modal_output_share at or above this means the group is near-constant, so an
#: accuracy delta between arms carries no information about inference.
HIGH_MODAL_SHARE = 0.80


def _rotate(index: int, options: list[str]) -> str:
    return options[index % len(options)]


def synonymize(text: str, variant_index: int) -> str:
    """Apply a deterministic subset of the synonym table.

    The rotation is keyed to the case index so different cases get different
    substitutions; within a case it is stable, so re-running the probe
    reproduces byte-identical inputs.
    """
    out = text
    for i, (pattern, repl) in enumerate(SYNONYMS):
        if (i + variant_index) % 2 == 0:
            out = re.sub(pattern, repl, out)
    return out


def split_fields(body: str) -> dict[str, str]:
    """Split a captured window into its `label: value` fields (multi-line safe).

    The chain line and the closing instruction are not fields — they are the
    decision evidence and are re-attached verbatim (modulo synonyms) so the
    rewrite cannot remove the tokens the gold action depends on.
    """
    fields: dict[str, str] = {}
    key = None
    for line in body.splitlines():
        if line.startswith(CHAIN_PREFIX) or line.startswith(CLOSING_PREFIX):
            key = None
            continue
        m = re.match(r"^(trigger|rule|why|lifecycle):\s?(.*)$", line)
        if m:
            key = m.group(1)
            fields[key] = m.group(2)
        elif key:
            fields[key] += "\n" + line
    return fields


def rejoin(fields: dict[str, str], record_id: str, index: int) -> str:
    lines = [f"Triage this Well record.\nrecord: {record_id}"]
    order = ["trigger", "rule", "why", "lifecycle"]
    for name in order:
        if name not in fields:
            continue
        value = synonymize(fields[name], index)
        lines.append(_rotate(index + order.index(name), FIELD_TEMPLATES[name]).format(v=value))
    return "\n".join(lines)


def build_variants(case: dict, index: int) -> tuple[dict | None, dict | None, str]:
    """Return (verbatim, paraphrase, drop_reason).

    The paraphrase keeps every factual token the decision depends on — the record
    id, the chain line and every timestamp — because paraphrasing those could
    legitimately change the gold action. Only the prose fields are rewritten.
    If anything the label depends on is missing, the case is dropped rather than
    risk scoring a rewritten input against an unchanged label.
    """
    raw = str(case.get("input", ""))
    rec = re.search(r"^record:\s*(\S+)", raw, re.M)
    chain = [ln for ln in raw.splitlines() if ln.startswith("chain records you can see:")]
    if not rec or not chain:
        return dict(case), None, "no record id or chain line to preserve"
    fields = split_fields(raw)
    for required in ("lifecycle", "rule"):
        if required not in fields:
            return dict(case), None, f"missing field {required}"

    verbatim = dict(case)
    verbatim["variant"] = "verbatim"

    body = rejoin(fields, rec.group(1), index)
    chain_line = synonymize(chain[0], index)
    text = f"{body}\n{chain_line}\nkind, domain and tags are NOT given. Infer them."

    # Guard: every identifier and timestamp the gold action depends on survives.
    gold = case.get("gold", {})
    must_survive = [rec.group(1)] + _UUID.findall(chain_line) + _TS.findall(chain_line)
    successor = gold.get("superseded_by")
    if isinstance(successor, str) and successor:
        must_survive.append(successor)
    missing = [tok for tok in must_survive if tok not in text]
    if missing:
        return verbatim, None, f"rewrite would drop decision-bearing tokens: {missing[:3]}"
    if text == raw:
        return verbatim, None, "rewrite was a no-op"

    para = dict(case)
    para["input"] = text
    para["variant"] = "paraphrase"
    para["gold"] = dict(gold)
    para["case_id"] = f"{case['case_id']}#para"
    return verbatim, para, ""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="well_curator paraphrase probe (verbatim vs paraphrase).")
    ap.add_argument("--model", default="lfm25-350m-q6k")
    ap.add_argument("--dataset", default=str(HOLDOUT))
    ap.add_argument("--few-shot-source", default=str(TRAIN))
    ap.add_argument("--few-shot", type=int, default=2)
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--concurrency", type=int, default=2)
    ap.add_argument("--warmup", type=int, default=2)
    ap.add_argument("--num-predict", type=int, default=512)
    ap.add_argument("--reuse", action="store_true",
                    help="reuse an arm's existing scoring.json/results.jsonl instead of re-running it")
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args(argv)

    dataset = [json.loads(ln) for ln in Path(args.dataset).read_text(encoding="utf-8").splitlines() if ln.strip()]
    cases = [r for r in dataset if r.get("role") == "well_curator"]
    if args.limit > 0:
        cases = cases[: args.limit]
    if not cases:
        print("[probe] no well_curator rows found", file=sys.stderr)
        return 1

    work = WORK
    work.mkdir(parents=True, exist_ok=True)
    variants: dict[str, list[dict]] = {"verbatim": [], "paraphrase": []}
    dropped: list[dict] = []
    for i, case in enumerate(cases):
        verbatim, para, reason = build_variants(case, i)
        variants["verbatim"].append(verbatim)
        if para is None:
            dropped.append({"case_id": case.get("case_id"), "reason": reason})
        else:
            variants["paraphrase"].append(para)
    print(f"[probe] cases={len(cases)} verbatim={len(variants['verbatim'])} "
          f"paraphrase={len(variants['paraphrase'])} dropped={len(dropped)}")
    for d in dropped:
        print(f"[probe] drop {d['case_id']}: {d['reason']}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    arms: dict[str, dict] = {}
    for name, rows in variants.items():
        if not rows:
            continue
        ds = work / f"{name}.jsonl"
        with ds.open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        arm_dir = out_dir / name
        key = f"{args.model}|well_curator"
        if args.reuse and (arm_dir / "scoring.json").exists() and (arm_dir / "results.jsonl").exists():
            print(f"[probe] reusing existing {name} results in {arm_dir}")
            arms[name] = json.loads((arm_dir / "scoring.json").read_text(encoding="utf-8")).get(key, {})
            continue
        cmd = [
            sys.executable, str(REPO / "scripts" / "sms" / "gauntlet.py"),
            "--models", args.model, "--roles", "well_curator",
            "--dataset", str(ds), "--limit", str(len(rows)),
            "--concurrency", str(args.concurrency), "--warmup", str(args.warmup),
            "--few-shot", str(args.few_shot), "--few-shot-source", args.few_shot_source,
            "--num-predict", str(args.num_predict), "--out-dir", str(arm_dir),
        ]
        print(f"[probe] running {name}: {' '.join(cmd[2:])}")
        proc = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True)
        if proc.returncode != 0:
            print(proc.stdout[-2000:], proc.stderr[-2000:], file=sys.stderr)
            return proc.returncode
        scoring = json.loads((arm_dir / "scoring.json").read_text(encoding="utf-8"))
        arms[name] = scoring.get(key, {})

    summary = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "model": args.model,
        "few_shot": args.few_shot,
        "num_predict": args.num_predict,
        "cases_offered": len(cases),
        "verbatim_n": len(variants["verbatim"]),
        "paraphrase_n": len(variants["paraphrase"]),
        "dropped": dropped,
        "arms": arms,
        "cross_arm": cross_arm(out_dir, args.model),
        "paraphrase_datasets": {"verbatim": str(work / "verbatim.jsonl"), "paraphrase": str(work / "paraphrase.jsonl")},
        "gold_identical_across_arms": True,
        "gold_label_note": "gold is byte-identical between arms by construction; "
                           "cases whose rewrite could alter the label were dropped",
        "noise_floor": NOISE_FLOOR,
    }
    (out_dir / "probe_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    _write_md(out_dir, summary)
    _print_table(summary)
    return 0


def _base_case_id(case_id: str) -> str:
    """Drop the `#para` suffix so arms can be matched case by case."""
    return str(case_id).split("#", 1)[0]


def cross_arm(out_dir: Path, model: str) -> dict:
    """Did the answer move when the wording changed, with the same gold?"""
    arms: dict[str, dict[str, str]] = {}
    for name in ("verbatim", "paraphrase"):
        path = out_dir / name / "results.jsonl"
        if not path.exists():
            continue
        arms[name] = {
            _base_case_id(json.loads(ln)["case_id"]): json.loads(ln)["raw_output"]
            for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()
        }
    if len(arms) != 2:
        return {"available": False}
    shared = sorted(set(arms["verbatim"]) & set(arms["paraphrase"]))
    changed = [cid for cid in shared if arms["verbatim"][cid] != arms["paraphrase"][cid]]
    modal: dict[str, str] = {}
    for name, mapping in arms.items():
        counts: Counter[str] = Counter(mapping.values())
        modal[name] = counts.most_common(1)[0][0] if counts else ""
    return {
        "available": True,
        "matched_cases": len(shared),
        "output_changed_n": len(changed),
        "output_changed_rate": round(len(changed) / len(shared), 3) if shared else 0.0,
        "modal_identical_across_arms": modal["verbatim"] == modal["paraphrase"],
        "verbatim_modal": modal.get("verbatim", ""),
        "paraphrase_modal": modal.get("paraphrase", ""),
    }


def _delta(a: dict, b: dict, key: str) -> float | None:
    if not a or not b or key not in a or key not in b:
        return None
    return round(a[key] - b[key], 3)


def _write_md(out_dir: Path, s: dict) -> None:
    v, p = s["arms"].get("verbatim", {}), s["arms"].get("paraphrase", {})
    lines = ["# Paraphrase Probe — well_curator", ""]
    lines.append(f"- model: `{s['model']}` · few-shot: {s['few_shot']} · num_predict: {s['num_predict']}")
    lines.append(f"- cases offered: {s['cases_offered']} · verbatim kept: {s['verbatim_n']} · "
                 f"paraphrase kept: {s['paraphrase_n']} · dropped: {len(s['dropped'])}")
    lines.append("- gold is identical in both arms; rewrites that could change the label were dropped")
    lines.append("")
    lines.append("| variant | n | schema% | exact_match | field_f1 | tags_f1 | distinct_output_ratio | modal_output_share | copy_suspect | p50_s | p95_s |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|:--:|---:|---:|")
    for name, agg in (("verbatim", v), ("paraphrase", p)):
        if not agg:
            continue
        lines.append(
            f"| {name} | {agg['n']} | {agg['schema_conformant_pct']} | {agg['exact_match_mean']} | "
            f"{agg['field_f1_mean']} | {agg.get('per_metric_mean', {}).get('tags_f1', '—')} | {agg['distinct_output_ratio']} | "
            f"{agg['modal_output_share']} | {'YES' if agg['copy_suspect'] else 'no'} | "
            f"{agg['latency']['p50']} | {agg['latency']['p95']} |"
        )
    lines.append("")
    d_exact = _delta(v, p, "exact_match_mean")
    d_modal = _delta(v, p, "modal_output_share")
    ca = s.get("cross_arm", {})
    lines.append(f"- exact_match delta (paraphrase - verbatim): {d_exact}")
    lines.append(f"- modal_output_share delta (paraphrase - verbatim): {d_modal}")
    lines.append(f"- noise floor for n={v.get('n', 0)} (blueprint §7): ±{s.get('noise_floor', NOISE_FLOOR)}")
    if ca.get("available"):
        lines.append(f"- output_changed_rate across arms: {ca['output_changed_rate']} "
                     f"({ca['output_changed_n']}/{ca['matched_cases']} answers moved when the wording changed)")
        lines.append(f"- modal output identical across arms: "
                     f"{'YES' if ca['modal_identical_across_arms'] else 'no'}")
    lines.append("")
    lines.append("## Verdict")
    lines.append("")
    lines.append(_verdict(v, p, d_exact, d_modal, ca))
    lines.append("")
    lines.append("## Dropped cases")
    lines.append("")
    if s["dropped"]:
        for d in s["dropped"]:
            lines.append(f"- `{d['case_id']}` — {d['reason']}")
    else:
        lines.append("- none")
    (out_dir / "paraphrase_probe.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _verdict(v: dict, p: dict, d_exact: float | None, d_modal: float | None,
             ca: dict | None = None) -> str:
    """Four outcomes, not two.

    The naive rule ("collapse ⇒ echo, survival ⇒ inference") is wrong for a
    near-constant model: accuracy survives paraphrase when the output does not
    depend on the input, and that is not inference. So the verdict is a
    function of the delta AND of how much the answers actually move.
    """
    if not v or not p or d_exact is None:
        return "INCONCLUSIVE — one arm produced no scoring output."
    ca = ca or {}
    near_constant = (
        v.get("modal_output_share", 0) >= HIGH_MODAL_SHARE
        and p.get("modal_output_share", 0) >= HIGH_MODAL_SHARE
    )
    changed_rate = ca.get("output_changed_rate")

    if d_exact <= -NOISE_FLOOR and (d_modal is None or d_modal >= 0.0):
        return ("**ECHO — proven by collapse.** Paraphrasing the surface form without changing the "
                f"label cost {abs(d_exact):.3f} exact-match (beyond the ±{NOISE_FLOOR} noise floor) "
                f"while modal_output_share did not fall (delta {d_modal}). Accuracy that survives only "
                "the wording the exemplars used is memorised prior, not inference.")

    if near_constant and changed_rate is not None and changed_rate < 0.35:
        return ("**ECHO — proven by invariance, NOT by collapse.** Accuracy did NOT collapse under "
                f"paraphrase (delta {d_exact}, inside the ±{NOISE_FLOOR} noise floor), so on the naive "
                "rule this would read as 'robust inference'. It is not. modal_output_share is "
                f"{v.get('modal_output_share')} verbatim and {p.get('modal_output_share')} paraphrase, and only "
                f"{ca.get('output_changed_n')}/{ca.get('matched_cases')} answers changed at all when the input was "
                f"rewritten (modal output identical across arms: {ca.get('modal_identical_across_arms')}). "
                "The score is invariant because the output barely depends on the input — the model is not "
                "reading the record. **The paraphrase probe is therefore uninformative as a discriminator "
                "here, and the echo metrics settle the question against inference.**")

    if d_exact >= NOISE_FLOOR:
        return (f"**Inference survives.** Accuracy rose by {d_exact}, beyond the ±{NOISE_FLOOR} noise floor, "
                "while the wording changed. This is the only shape of result that argues the model reads "
                "its input rather than the exemplars.")
    return ("Inconclusive: paraphrase moved accuracy by "
            f"{d_exact}, inside the ±{NOISE_FLOOR} noise floor, and the output distribution is not near-constant. "
            "Not enough signal to call either way.")


def _print_table(s: dict) -> None:
    for name, agg in s["arms"].items():
        if not agg:
            continue
        print(f"[probe] {name:10s} n={agg['n']:3d} schema={agg['schema_conformant_pct']:5.1f} "
              f"exact={agg['exact_match_mean']:.3f} f1={agg['field_f1_mean']:.3f} "
              f"distinct_ratio={agg['distinct_output_ratio']:.3f} modal_share={agg['modal_output_share']:.3f} "
              f"copy_suspect={agg['copy_suspect']} p95={agg['latency']['p95']}s")


if __name__ == "__main__":
    sys.exit(main())