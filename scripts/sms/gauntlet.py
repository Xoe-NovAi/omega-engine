#!/usr/bin/env python3
"""SMS gauntlet runner — LFM2.5 specialist modules evaluation.

Usage:
  python3 scripts/sms/gauntlet.py \
    --models lfm25-230m-q6k,lfm25-350m-q6k \
    --roles mempalace_extractor,well_curator,tool_router,privacy_sentinel,failure_classifier \
    --limit 10 --concurrency 1 --out-dir runs/sms_smoke --warmup 1

Behavior:
  * Loads the smoke dataset (scripts/sms/datasets/sms_smoke_dataset.jsonl) —
    synthetic, sanitized rows with gold labels per role.
  * For each case: POST to Ollama /api/chat with format:"json",
    temperature 0.1, num_thread 6 (--num-thread), num_predict 512 (--num-predict).
  * Scores each output: JSON validity, schema conformance (JSON Schema
    Draft 2020-12), role-specific exact match / F1 approximations,
    provenance preservation, wall latency, output token count.
  * Writes results.jsonl (per-case raw output + scores), scoring.json
    (aggregates), report.md and failure_examples.md (top 5 per failure class)
    into --out-dir.

Privacy: the smoke dataset is synthetic. Never point --dataset at raw
private transcripts; sanitize per docs/research/P7_SMS_GAUNTLET_BLUEPRINT_20261008.md
§1.2 before use. Raw model outputs are written locally under --out-dir;
commit only scoring.json / report.md (redacted) per §10.3.
"""

from __future__ import annotations

import argparse
import concurrent.futures as futures
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.sms import roles  # noqa: E402
from scripts.sms.decomposition import roles as decomposition_roles  # noqa: E402
from scripts.sms.scoring import echo, json_schema, latency  # noqa: E402

DEFAULT_DATASET = REPO / "scripts" / "sms" / "datasets" / "sms_smoke_dataset.jsonl"
SCHEMA_DIR = REPO / "scripts" / "sms" / "schemas"
DECOMPOSITION_SCHEMA_DIR = REPO / "scripts" / "sms" / "decomposition" / "schemas"

#: Roles dispatched to the flat-contract module in scripts/sms/decomposition/.
#: Their prompts, schemas and scorers live there; everything else stays on roles.py.
DECOMPOSITION_ROLE_SET = set(decomposition_roles.DECOMPOSITION_ROLES)

#: Default generation cap. The phase-1 extractor emitted 260-324 tokens for a
#: flat-ish answer, so this is a sweepable knob, not a fixed contract — pass
#: --num-predict to measure. No context or output limit is hardcoded elsewhere.
DEFAULT_NUM_PREDICT = 512

#: llama.cpp generation threads per request. Swept with --num-thread; the Node 1
#: profile runs Ollama on CPUs 0-11, so this is measured, not assumed.
DEFAULT_NUM_THREAD = 6
OLLAMA_HOST = "http://localhost:11434"
REQUEST_TIMEOUT = 300
_MESSAGE_ROLES = ("system", "user", "assistant")


def log(msg: str) -> None:
    print(msg, flush=True)


def load_dataset(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_schema(role: str) -> dict:
    return json.loads((schema_path(role)).read_text())


def schema_path(role: str):
    """Flat-contract roles resolve to the decomposition schema dir, not the v1 one."""
    base = DECOMPOSITION_SCHEMA_DIR if role in DECOMPOSITION_ROLE_SET else SCHEMA_DIR
    return base / f"{role}.schema.json"


def role_prompt(role: str) -> str:
    return decomposition_roles.SYSTEM[role] if role in DECOMPOSITION_ROLE_SET else roles.SYSTEM[role]


def build_user(role: str, case: dict) -> str:
    return decomposition_roles.build_user(role, case) if role in DECOMPOSITION_ROLE_SET \
        else roles.build_user(role, case)


def score_role_case(role: str, pred, gold: dict, case: dict) -> dict:
    return decomposition_roles.score_case(role, pred, gold, case) if role in DECOMPOSITION_ROLE_SET \
        else roles.score_case(role, pred, gold, case)


def resolve_few_shot_source(explicit: str | None, dataset_path: Path) -> Path:
    """Exemplars come from an explicit --few-shot-source, else the train split
    beside the dataset, else the smoke dataset. The holdout is never used as an
    exemplar source: a sibling `_holdout.jsonl` resolves to `_train.jsonl`."""
    if explicit:
        path = Path(explicit)
        if not path.exists():
            raise FileNotFoundError(f"--few-shot-source not found: {path}")
        return path
    sibling = dataset_path.with_name(dataset_path.name.replace("_holdout.jsonl", "_train.jsonl"))
    if sibling.exists() and sibling.resolve() != dataset_path.resolve():
        return sibling
    return DEFAULT_DATASET


def chat_json(host: str, model: str, system: str, user: str, num_predict: int = DEFAULT_NUM_PREDICT,
              num_thread: int = DEFAULT_NUM_THREAD) -> dict:
    return chat_messages(host, model, [system, user], num_predict, num_thread=num_thread)


def chat_messages(host: str, model: str, contents: list[str], num_predict: int = DEFAULT_NUM_PREDICT,
                  timeout: float = REQUEST_TIMEOUT, num_thread: int = DEFAULT_NUM_THREAD) -> dict:
    """Single Ollama /api/chat call.

    `contents` is an alternating [system, user, assistant, user, ...] list; a
    one-shot call is just [system, user]. Few-shot runs interleave exemplar
    user/assistant pairs before the real user turn.

    `timeout` is passed straight to urlopen. The latency-probe injection lowers
    it to force a real client-side timeout rather than simulating one.
    `num_thread` is a llama.cpp generation parameter, not an Ollama server
    setting — it is per-request and is swept with --num-thread.
    """
    messages = [{"role": _MESSAGE_ROLES[i] if i < len(_MESSAGE_ROLES) else "user", "content": c}
                for i, c in enumerate(contents)]
    payload = {
        "model": model,
        "stream": False,
        "format": "json",
        "messages": messages,
        "options": {
            "temperature": 0.1,
            "num_thread": num_thread,
            "num_predict": num_predict,
        },
    }
    req = urllib.request.Request(
        f"{host}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")[:400]
        raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
    except TimeoutError as exc:
        raise RuntimeError(f"request timed out after {timeout}s") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"connection error: {exc.reason}") from exc


def failure_class_for(valid: bool, conformant: bool, timed_out: bool) -> str:
    if timed_out:
        return "latency_spike"
    if not valid:
        return "parse_failure"
    if not conformant:
        return "schema_violation"
    return "ok"


#: Deliberate runner faults, for capturing failure_classifier gold that a real
#: trace cannot produce on demand. Phase 1's gold had only `ok` and
#: `schema_violation` because nothing ever produced a bad output.
#:   truncate        — cut the output mid-string (a real generation cutoff)
#:   malformed_json  — emit JSON-shaped prose that json.loads rejects
#:   timeout         — force a genuine client-side HTTP timeout (latency_spike)
#:   schema_violation— drop a required key
#: `auto` rotates these deterministically so ONE probe run yields every class.
INJECTION_MODES = ("none", "truncate", "malformed_json", "timeout", "schema_violation")
AUTO_INJECTION_CYCLE = ("none", "truncate", "malformed_json", "timeout", "schema_violation")
MALFORMED_SAMPLES = (
    'Sure! {"class": "ok", "confidence": 0.9, "evidence": "looks fine"',
    "{'class': 'ok', 'confidence': 0.9, 'evidence': 'single quotes are not JSON'}",
    '{"class": "ok", "confidence": 0.9, "evidence": "ok",}',
    '<class>ok</class> confidence=0.9 evidence=none',
)


def injection_for(mode: str, index: int) -> str:
    """Resolve `--inject-failure` for one case. Deterministic, no RNG."""
    if mode == "auto":
        return AUTO_INJECTION_CYCLE[index % len(AUTO_INJECTION_CYCLE)]
    return mode if mode in INJECTION_MODES else "none"


def apply_injection(mode: str, raw: str, schema: dict, index: int) -> tuple[str, str]:
    """Corrupt a real model output into a targeted failure. Returns (raw, note).

    The output is a genuine model response that has been perturbed in one
    specific way, so the downstream validity/conformance/failure_class is
    computed from the perturbed artifact exactly as it would be in production.
    """
    if mode in ("none", "timeout") or not raw:
        return raw, ""
    if mode == "truncate":
        cut = max(1, len(raw) // 2)
        return raw[:cut], "truncated mid-output by --inject-failure"
    if mode == "malformed_json":
        return MALFORMED_SAMPLES[index % len(MALFORMED_SAMPLES)], "malformed JSON injected"
    if mode == "schema_violation":
        obj, ok = json_schema.parse_json(raw)
        if ok and isinstance(obj, dict):
            required = [k for k in schema.get("required", []) if k in obj]
            if required:
                trimmed = {k: v for k, v in obj.items() if k != required[0]}
                return json.dumps(trimmed, ensure_ascii=False), f"dropped required key {required[0]!r}"
            trimmed = dict(obj)
            trimmed["unexpected_extra_key"] = "injected"
            return json.dumps(trimmed, ensure_ascii=False), "added key outside schema"
        return raw + '" trailing', "could not parse before schema perturbation"
    return raw, ""


def run_case(host: str, model: str, role: str, schema: dict, case: dict,
             exemplars: list[dict] | None = None, num_predict: int = DEFAULT_NUM_PREDICT,
             inject_failure: str = "none", case_index: int = 0,
             injected_timeout_s: float = 0.05, num_thread: int = DEFAULT_NUM_THREAD) -> dict:
    system = role_prompt(role)
    user = build_user(role, case)
    contents = [system]
    for ex in exemplars or []:
        contents.append(ex["user"])
        contents.append(ex["assistant"])
    contents.append(user)
    injection = injection_for(inject_failure, case_index)
    started = time.monotonic()
    timed_out = False
    raw_output = ""
    tokens_out = 0
    error = ""
    injection_note = ""
    try:
        timeout = injected_timeout_s if injection == "timeout" else REQUEST_TIMEOUT
        resp = chat_messages(host, model, contents, num_predict, timeout, num_thread)
        raw_output = resp.get("message", {}).get("content", "")
        tokens_out = int(resp.get("eval_count", 0) or 0)
        raw_output, injection_note = apply_injection(injection, raw_output, schema, case_index)
        if injection == "timeout":
            error = f"request timed out after {timeout}s"
    except RuntimeError as exc:
        error = str(exc)
        timed_out = "timed out" in error.lower() or "timeout" in error.lower()
        if injection == "timeout":
            injection_note = f"forced client timeout at {injected_timeout_s}s"
    wall = time.monotonic() - started

    obj, valid = json_schema.parse_json(raw_output)
    if valid and obj is not None:
        conformant, errs = json_schema.validate_schema(obj, schema)
    else:
        conformant, errs = False, []
    fclass = failure_class_for(valid, conformant, timed_out) if not error else ("latency_spike" if timed_out else "parse_failure")
    gold = case.get("gold", {})
    metrics = score_role_case(role, obj, gold, case) if valid and conformant and isinstance(obj, dict) \
        else {"exact_match": 0.0, "field_f1": 0.0}
    return {
        "case_id": case.get("case_id"),
        "role": role,
        "model": model,
        "tags": case.get("tags", []),
        "few_shot": len(exemplars or []),
        "input_sha256": hashlib.sha256(json.dumps(case.get("input", ""), sort_keys=True, default=str).encode()).hexdigest()[:16],
        "raw_output": raw_output,
        "num_predict": num_predict,
        "num_thread": num_thread,
        "injected_failure": injection,
        "injection_note": injection_note,
        "tokens_out": tokens_out,
        "latency_s": round(wall, 3),
        "json_valid": valid,
        "schema_conformant": conformant,
        "schema_errors": errs,
        "metrics": metrics,
        "failure_class": fclass,
        "error": error,
    }


def signature(role: str, gold: dict) -> set[tuple[str, str]]:
    """The diversity signature of one candidate exemplar.

    Diversity is measured over the fields a few-shot collapse actually happens
    on — the categorical decision fields and the tag set — not over case ids.
    Two `well_curator` exemplars with different case ids but the same
    (kind=correction, domain=harness, action=keep, same five tags) are the same
    exemplar as far as echo is concerned, and phase 2 measured exactly that:
    `well_curator` emitted 34/36 copies of one exemplar's answer.
    """
    if not isinstance(gold, dict):
        return {("gold", str(gold))}
    out: set[tuple[str, str]] = set()
    for field in ("kind", "domain", "action", "class", "tool", "fallback", "wing", "room"):
        if field in gold and not isinstance(gold[field], (list, dict)):
            out.add((field, str(gold[field])))
    tags = gold.get("tags")
    if isinstance(tags, list):
        for t in tags:
            out.add(("tag", str(t)))
    if not out:
        for k in sorted(gold):
            if isinstance(gold[k], (list, dict)):
                out.add((k, json.dumps(gold[k], sort_keys=True, ensure_ascii=False)))
            else:
                out.add((k, str(gold[k])))
    return out


def select_exemplars(role: str, rows: list[dict], n: int, exclude_ids: set[str] | None = None,
                     strategy: str = "even") -> list[dict]:
    """Deterministically pick n gold cases for `role` as few-shot exemplars.

    Only rows from the exemplar source are eligible (callers pass the TRAIN
    split; the holdout is never a source). Two strategies:

      even    even spacing over sorted case ids. Cheap, and — as phase 2 showed —
              blind to content: the curator's two exemplars were both harness
              corrections, and the modal output was 34/36 copies of one of them.

      diverse greedy max-coverage over `signature()`, so the exemplars span
              kinds, domains, actions and tags rather than ids. Selection is a
              deterministic greedy pass with a stable tie-break on case id, so
              the same pool always yields the same exemplars.

    Returns the rendered user turn plus the canonical gold JSON answer.
    """
    blocked = exclude_ids or set()
    eligible = sorted(
        (r for r in rows if r.get("role") == role and str(r.get("case_id")) not in blocked),
        key=lambda r: str(r.get("case_id")),
    )
    if not eligible or n <= 0:
        return []
    if len(eligible) <= n:
        picked = eligible
    elif strategy == "diverse":
        picked = []
        covered: set[tuple[str, str]] = set()
        remaining = list(eligible)
        while remaining and len(picked) < n:
            best = max(remaining, key=lambda r: (len(signature(role, r.get("gold", {})) - covered),
                                                 -eligible.index(r)))
            picked.append(best)
            covered |= signature(role, best.get("gold", {}))
            remaining.remove(best)
    else:
        picked = [eligible[(i * len(eligible)) // n] for i in range(n)]
        seen: set[str] = set()
        deduped = []
        for row in picked:
            cid = str(row.get("case_id"))
            if cid not in seen:
                seen.add(cid)
                deduped.append(row)
        picked = deduped
    exemplars = []
    for row in picked:
        gold = row.get("gold", {})
        exemplars.append(
            {
                "case_id": row.get("case_id"),
                "user": build_user(role, row),
                "assistant": json.dumps(gold, ensure_ascii=False),
            }
        )
    return exemplars


def aggregate(results: list[dict]) -> dict:
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in results:
        groups[(r["model"], r["role"])].append(r)
    out = {}
    for (model, role), rows in sorted(groups.items()):
        n = len(rows)
        em = echo.echo_metrics(r["raw_output"] for r in rows)
        metric_keys = sorted({k for r in rows for k in r["metrics"]})
        per_metric = {
            k: round(sum(float(r["metrics"].get(k, 0.0) or 0.0) for r in rows) / n, 3)
            for k in metric_keys
        }
        out[f"{model}|{role}"] = {
            "n": n,
            "json_valid_pct": round(100 * sum(r["json_valid"] for r in rows) / n, 1),
            "schema_conformant_pct": round(100 * sum(r["schema_conformant"] for r in rows) / n, 1),
            "exact_match_mean": round(sum(r["metrics"].get("exact_match", 0.0) for r in rows) / n, 3),
            "field_f1_mean": round(sum(r["metrics"].get("field_f1", 0.0) for r in rows) / n, 3),
            "latency": latency.summarize(r["latency_s"] for r in rows),
            "tokens_out_mean": round(sum(r["tokens_out"] for r in rows) / n, 1),
            "mean_output_tokens": round(sum(r["tokens_out"] for r in rows) / n, 1),
            "num_predict": rows[0].get("num_predict", DEFAULT_NUM_PREDICT),
            "num_thread": rows[0].get("num_thread", DEFAULT_NUM_THREAD),
            "distinct_outputs": em["distinct_outputs"],
            "distinct_output_ratio": em["distinct_output_ratio"],
            "modal_output_share": em["modal_output_share"],
            "copy_suspect_n": em["copy_suspect_n"],
            "copy_suspect": em["copy_suspect"],
            "per_metric_mean": per_metric,
            "failure_classes": {c: sum(1 for r in rows if r["failure_class"] == c) for c in {r["failure_class"] for r in rows}},
        }
    return out


def few_shot_verdicts(scoring: dict, few_shot: int, select_strategy: str) -> dict:
    """ACCEPT/REJECT per role, gated on `copy_suspect`.

    A few-shot configuration is only ACCEPTED for a role when the group did NOT
    trip the echo alarm. Anything else is REJECTED regardless of how good the
    exact-match looks — that is the whole lesson of phase 2, where
    `well_curator` scored 0.852 while a constant string scored 0.898. The gate is
    stated in the report so a future run cannot quietly drop it.
    """
    out: dict[str, dict] = {}
    for key, agg in scoring.items():
        model, role = key.split("|", 1)
        if few_shot <= 0:
            verdict, reason = "N/A", "no exemplars in this arm; the gate applies to few-shot configs only"
        elif agg["copy_suspect"] or agg["distinct_output_ratio"] < echo.ECHO_RATIO_THRESHOLD:
            verdict = "REJECT"
            reason = (f"distinct_output_ratio {agg['distinct_output_ratio']} < "
                      f"{echo.ECHO_RATIO_THRESHOLD} at n={agg['n']}: exemplar echo")
        else:
            verdict, reason = "ACCEPT", f"distinct_output_ratio {agg['distinct_output_ratio']} clears the echo gate"
        out[role] = {
            "model": model,
            "n": agg["n"],
            "few_shot": few_shot,
            "select_strategy": select_strategy,
            "distinct_output_ratio": agg["distinct_output_ratio"],
            "modal_output_share": agg["modal_output_share"],
            "copy_suspect": agg["copy_suspect"],
            "exact_match_mean": agg["exact_match_mean"],
            "verdict": verdict,
            "reason": reason,
        }
    return out


def write_report(out_dir: Path, scoring: dict, results: list[dict], verdicts: dict | None = None) -> None:
    lines = ["# SMS Gauntlet Run Report", ""]
    lines.append(f"- cases: {len(results)}")
    models = sorted({r['model'] for r in results})
    roles_seen = sorted({r['role'] for r in results})
    lines.append(f"- models: {', '.join(models)}")
    lines.append(f"- roles: {', '.join(roles_seen)}")
    injections = sorted({r.get("injected_failure", "none") for r in results if r.get("injected_failure")})
    if injections and injections != ["none"]:
        lines.append(f"- injected_failure: {', '.join(injections)}")
    lines.append("")
    num_predicts = sorted({a.get("num_predict") for a in scoring.values() if a.get("num_predict")})
    if num_predicts:
        lines.append(f"- num_predict: {', '.join(str(x) for x in num_predicts)}")
    threads = sorted({a.get("num_thread") for a in scoring.values() if a.get("num_thread")})
    if threads:
        lines.append(f"- num_thread: {', '.join(str(x) for x in threads)}")
    lines.append("")
    lines.append("## Accuracy and latency")
    lines.append("")
    lines.append("| model | role | n | json_valid% | schema% | exact_match | field_f1 | p50_s | p95_s | mean_output_tokens |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for key, agg in scoring.items():
        model, role = key.split("|", 1)
        lines.append(
            f"| {model} | {role} | {agg['n']} | {agg['json_valid_pct']} | {agg['schema_conformant_pct']} | "
            f"{agg['exact_match_mean']} | {agg['field_f1_mean']} | {agg['latency']['p50']} | {agg['latency']['p95']} | {agg['mean_output_tokens']} |"
        )
    lines.append("")
    lines.append("## Exemplar-echo metrics")
    lines.append("")
    lines.append(f"`copy_suspect` is true when distinct_output_ratio < {echo.ECHO_RATIO_THRESHOLD} "
                 f"and n >= {echo.ECHO_MIN_N}. A high exact_match with copy_suspect true is "
                 "prior-dominated, not capability.")
    lines.append("")
    lines.append("| model | role | n | distinct_outputs | distinct_output_ratio | modal_output_share | copy_suspect_n | copy_suspect |")
    lines.append("|---|---|---:|---:|---:|---:|---:|:--:|")
    for key, agg in scoring.items():
        model, role = key.split("|", 1)
        lines.append(
            f"| {model} | {role} | {agg['n']} | {agg['distinct_outputs']} | {agg['distinct_output_ratio']} | "
            f"{agg['modal_output_share']} | {agg['copy_suspect_n']} | {'YES' if agg['copy_suspect'] else 'no'} |"
        )
    if verdicts:
        lines.append("")
        lines.append("## Few-shot ACCEPT/REJECT gate")
        lines.append("")
        lines.append("A few-shot configuration is ACCEPTED for a role only when `copy_suspect` is false. "
                     "A REJECT is not a tuning note: the arm's accuracy is not evidence of capability.")
        lines.append("")
        lines.append("| role | few_shot | select | distinct_ratio | modal_share | copy_suspect | exact_match | verdict | reason |")
        lines.append("|---|---:|---|---:|---:|:--:|---:|:--:|---|")
        for role, v in verdicts.items():
            lines.append(
                f"| {role} | {v['few_shot']} | {v['select_strategy']} | {v['distinct_output_ratio']} | "
                f"{v['modal_output_share']} | {'YES' if v['copy_suspect'] else 'no'} | "
                f"{v['exact_match_mean']} | **{v['verdict']}** | {v['reason']} |"
            )
    (out_dir / "report.md").write_text("\n".join(lines) + "\n")

    by_class: dict[str, list[dict]] = defaultdict(list)
    for r in results:
        if r["failure_class"] != "ok":
            by_class[r["failure_class"]].append(r)
    ex = ["# Failure Examples (top 5 per class)", ""]
    for cls, rows in sorted(by_class.items()):
        ex.append(f"## {cls} (n={len(rows)})")
        for r in rows[:5]:
            ex.append(f"- **{r['model']} / {r['role']} / {r['case_id']}**")
            ex.append(f"  - raw: `{r['raw_output'][:200]!r}`")
            if r["schema_errors"]:
                ex.append(f"  - schema_errors: `{r['schema_errors'][0][:160]}`")
            if r["error"]:
                ex.append(f"  - error: `{r['error'][:160]}`")
        ex.append("")
    (out_dir / "failure_examples.md").write_text("\n".join(ex) + "\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="SMS gauntlet runner (Ollama, LFM2.5 specialists).")
    ap.add_argument("--models", required=True, help="comma-separated Ollama model names")
    ap.add_argument("--roles", required=True, help="comma-separated role names")
    ap.add_argument("--dataset", default=str(DEFAULT_DATASET))
    ap.add_argument("--limit", type=int, default=0, help="max cases per role (0 = all)")
    ap.add_argument("--concurrency", type=int, default=1)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--warmup", type=int, default=1, help="warmup cases per model before timing")
    ap.add_argument("--host", default=OLLAMA_HOST)
    ap.add_argument("--few-shot", type=int, default=0,
                    help="exemplar pairs per role prepended to the chat (0 = zero-shot, default)")
    ap.add_argument("--few-shot-source", default=None,
                    help="dataset JSONL exemplars are drawn from; defaults to the train split "
                         "alongside --dataset (falling back to the smoke dataset)")
    ap.add_argument("--few-shot-select", default="even", choices=("even", "diverse"),
                    help="exemplar selection: 'even' spaces over sorted case ids (phase-2 default, "
                         "blind to content) or 'diverse' greedily maximises coverage of "
                         "(kind, domain, action, tag-set)")
    ap.add_argument("--num-predict", type=int, default=DEFAULT_NUM_PREDICT,
                    help=f"generation cap per case, forwarded to Ollama (default {DEFAULT_NUM_PREDICT})")
    ap.add_argument("--inject-failure", default="none", choices=("none", "auto", *INJECTION_MODES[1:]),
                    help="deliberately perturb each output to capture failure_classifier gold; "
                         "'auto' rotates all modes deterministically")
    ap.add_argument("--injected-timeout-s", type=float, default=0.05,
                    help="client timeout used by the 'timeout' injection (real HTTP timeout)")
    ap.add_argument("--num-thread", type=int, default=DEFAULT_NUM_THREAD,
                    help=f"llama.cpp generation threads per request (default {DEFAULT_NUM_THREAD})")
    args = ap.parse_args(argv)

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    role_list = [r.strip() for r in args.roles.split(",") if r.strip()]
    dataset = load_dataset(Path(args.dataset))
    by_role: dict[str, list[dict]] = defaultdict(list)
    for row in dataset:
        by_role[row["role"]].append(row)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Warmup: throwaway calls per model (excluded from scoring).
    for model in models:
        for _ in range(max(0, args.warmup)):
            try:
                chat_json(args.host, model, "Reply with JSON: {\"ok\": true}", "warmup",
                          num_predict=32, num_thread=args.num_thread)
                log(f"[warmup] {model} ok")
            except RuntimeError as exc:
                log(f"[warmup] {model} failed: {exc}")

    exemplars_by_role: dict[str, list[dict]] = {}
    if args.few_shot > 0:
        source_path = resolve_few_shot_source(args.few_shot_source, Path(args.dataset))
        pool_rows = load_dataset(source_path)
        evaluated_ids = {str(r.get("case_id")) for r in dataset}
        for role in role_list:
            chosen = select_exemplars(role, pool_rows, args.few_shot, evaluated_ids, args.few_shot_select)
            exemplars_by_role[role] = chosen
            log(f"[few-shot] {role}: {len(chosen)} exemplars ({args.few_shot_select}) from {source_path.name} "
                f"({[e['case_id'] for e in chosen]})")
        log(f"[few-shot] exemplar source: {source_path}")

    tasks: list[tuple[str, str, dict, dict]] = []
    for model in models:
        for role in role_list:
            try:
                schema = load_schema(role)
            except FileNotFoundError:
                log(f"[skip] no schema for role {role}")
                continue
            cases = by_role.get(role, [])
            if args.limit > 0:
                cases = cases[: args.limit]
            for case in cases:
                tasks.append((model, role, schema, case))

    log(f"[run] {len(tasks)} cases, concurrency={args.concurrency}, few_shot={args.few_shot}, "
        f"few_shot_select={args.few_shot_select}, "
        f"num_predict={args.num_predict}, num_thread={args.num_thread}, "
        f"inject_failure={args.inject_failure}")
    results: list[dict] = []
    if args.concurrency <= 1:
        for idx, (model, role, schema, case) in enumerate(tasks):
            r = run_case(args.host, model, role, schema, case, exemplars_by_role.get(role),
                         args.num_predict, args.inject_failure, idx, args.injected_timeout_s,
                         args.num_thread)
            results.append(r)
            log(f"  {model} {role} {case.get('case_id')} valid={r['json_valid']} conformant={r['schema_conformant']} f1={r['metrics'].get('field_f1', 0):.2f} {r['latency_s']}s")
    else:
        def _run(t: tuple, idx: int) -> dict:
            model, role, schema, case = t
            return run_case(args.host, model, role, schema, case, exemplars_by_role.get(role),
                            args.num_predict, args.inject_failure, idx, args.injected_timeout_s,
                            args.num_thread)

        with futures.ThreadPoolExecutor(max_workers=args.concurrency) as pool:
            for r in pool.map(_run, tasks, range(len(tasks))):
                results.append(r)
                log(f"  {r['model']} {r['role']} {r['case_id']} valid={r['json_valid']} conformant={r['schema_conformant']} {r['latency_s']}s")

    with (out_dir / "results.jsonl").open("w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    scoring = aggregate(results)
    (out_dir / "scoring.json").write_text(json.dumps(scoring, indent=2) + "\n")
    verdicts = few_shot_verdicts(scoring, args.few_shot, args.few_shot_select)
    (out_dir / "verdicts.json").write_text(json.dumps(verdicts, indent=2) + "\n")
    write_report(out_dir, scoring, results, verdicts)
    log("")
    log("=== few-shot ACCEPT/REJECT gate ===")
    log(f"  rule: a few-shot config is ACCEPTED for a role only if copy_suspect == false")
    for role, v in verdicts.items():
        log(f"  {v['verdict']:6s} {role:22s} n={v['n']:3d} select={v['select_strategy']:8s} "
            f"distinct={v['distinct_output_ratio']} modal={v['modal_output_share']} "
            f"exact={v['exact_match_mean']}  ({v['reason']})")
    log(f"[done] wrote {out_dir}/results.jsonl, scoring.json, verdicts.json, report.md, failure_examples.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
