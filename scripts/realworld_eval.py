#!/usr/bin/env python3
"""Omega real-world eval: lfm25-8b-a1b vs baselines on engine-representative tasks.

Methodology (researched 2026-10-08, applied):
- OLMES: every eval choice documented below and recorded in the output JSON;
  prompt formatting is fixed identically across models.
- LatentEval: automated EXACT/EXECUTABLE grading only (no LLM judge -> no
  judge bias); multi-run to size variance; reliability (runs) reported
  separately from validity (task design).
- pass@k for code uses temp 0.7 (k=3); deterministic tasks use temp 0.0-0.1.
- Baselines run on the identical harness/engine (Ollama :11434, sequential
  single slot).

Tasks (all graded by execution or exact match):
1. code      -- slugify() with 8 executable assertions; pass@1 + pass@3
2. extract   -- JSON fields from messy text; json.loads + exact value match
3. toolcall  -- /api/chat tools= schema; tool_calls name + args validated
4. instruct  -- 4 explicit system-prompt rules; exact marker checks

Usage: python3 scripts/realworld_eval.py [--quick]
"""

import argparse
import json
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

HOST = "http://127.0.0.1:11434"
MODELS = [
    "lfm25-8b-a1b:latest",
    "Krikri-8b-Instruct-Q5_K_M:latest",
    "lfm25-t6:latest",
]
OUT = Path(__file__).resolve().parent.parent / "benchmarking" / "realworld"
TIMEOUT_S = 240

SLUGIFY_SPEC = (
    "Write a Python function slugify(text: str) -> str that: lowercases; "
    "replaces runs of whitespace or underscores with a single hyphen; strips "
    "every character that is not [a-z0-9-]; collapses repeated hyphens; "
    "strips leading/trailing hyphens. Include type hints. Output ONLY one "
    "```python code block, no other prose."
)
# Spec-order trace for the unicode case: lower -> 'ünïcödé? nope!'; ws runs
# -> '-'; strip non-[a-z0-9-] removes ü ï ö é ? ! -> 'ncd-nope'.
SLUGIFY_TESTS = [
    ("Hello World", "hello-world"),
    ("  spaced   out ", "spaced-out"),
    ("snake_case_mixed", "snake-case-mixed"),
    ("--lead and trail--", "lead-and-trail"),
    ("Ünïcödé? Nope!", "ncd-nope"),
    ("double  space", "double-space"),
    ("a_b__c", "a-b-c"),
    ("already-clean", "already-clean"),
]

EXTRACT_INPUT = (
    "INVOICE #4471-B\n"
    "Client: Marianne Okafor (Lagos office)\n"
    "Service period: 03/14/2026 - 03/20/2026\n"
    "  Total due: USD 4,820.50  (net 30)\n"
    "Rush fee applied? yes -- approved by J. Alvarez 2026-03-13.\n"
    "Notes: client asked twice about the rush fee; see thread #221."
)
EXTRACT_SPEC = {
    "invoice_id": "4471-B",
    "client_name": "Marianne Okafor",
    "total_usd": 4820.50,
    "due_date": "2026-04-19",  # net 30 from 2026-03-20
}
EXTRACT_PROMPT = (
    "Extract from the text below a single JSON object with EXACTLY these keys: "
    "invoice_id, client_name, total_usd (number), due_date (YYYY-MM-DD, net 30 "
    "from service period end 2026-03-20). Output ONLY the JSON object, no "
    "fences, no prose.\n\n" + EXTRACT_INPUT
)

TOOLS = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for a city",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
    },
}]
TOOL_PROMPT = "What's the current weather in Athens?"

INSTRUCT_SYSTEM = (
    "You are graded by exact marker checks. RULES:\n"
    "1. Begin your reply with the exact token: VERIFIED\n"
    "2. Include at least one markdown table.\n"
    "3. The word 'however' must not appear anywhere.\n"
    "4. End your reply with exactly: Done / Pending / Files touched / Next"
)
INSTRUCT_PROMPT = "List three benefits of running AI models locally."


def chat(model, messages, temperature, max_tokens, tools=None, num_ctx=8192):
    body = {
        "model": model, "messages": messages, "stream": False,
        "options": {"temperature": temperature, "num_predict": max_tokens,
                    "num_ctx": num_ctx},
    }
    if tools:
        body["tools"] = tools
    req = urllib.request.Request(
        HOST + "/api/chat", data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"})
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
        resp = json.loads(r.read())
    wall = time.perf_counter() - t0
    msg = resp.get("message", {})
    return msg.get("content", "") or "", msg.get("tool_calls"), wall, resp


def first_code_block(text):
    m = re.search(r"```(?:python)?\n(.*?)```", text, re.S)
    return m.group(1) if m else None


def run_slugify_tests(code):
    """Execute generated code against assertions in a subprocess. Returns n_pass."""
    harness = (
        "import sys\n"
        "user_code = sys.stdin.read()\n"
        "ns = {}\n"
        "exec(compile(user_code, 'model_output.py', 'exec'), ns)\n"
        "f = ns.get('slugify')\n"
        "cases = " + repr(SLUGIFY_TESTS) + "\n"
        "ok = 0\n"
        "for src, want in cases:\n"
        "    try:\n"
        "        if f(src) == want:\n"
        "            ok += 1\n"
        "    except Exception:\n"
        "        pass\n"
        "print(ok)\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=True) as h:
        h.write(harness)
        h.flush()
        try:
            p = subprocess.run(
                [sys.executable, h.name], input=code, capture_output=True,
                text=True, timeout=15)
            return int(p.stdout.strip().splitlines()[-1])
        except (subprocess.SubprocessError, OSError, ValueError, IndexError):
            return 0


def eval_code(model, quick):
    n = 1 if quick else 3
    passes, walls, samples = [], [], []
    for _ in range(n):
        content, _, wall, _ = chat(
            model, [{"role": "user", "content": SLUGIFY_SPEC}], 0.7, 768)
        walls.append(round(wall, 2))
        code = first_code_block(content)
        n_pass = run_slugify_tests(code) if code else 0
        passes.append(n_pass == len(SLUGIFY_TESTS))
        samples.append({"pass": passes[-1],
                        "tests": "%d/%d" % (n_pass, len(SLUGIFY_TESTS))})
    return {"pass@1": passes[0],
            "pass@3": any(passes[:3]) if n == 3 else None,
            "runs": n, "samples": samples, "wall_s": walls}


def eval_extract(model, quick):
    n = 1 if quick else 3
    hits, walls, detail = [], [], []
    for _ in range(n):
        content, _, wall, _ = chat(
            model, [{"role": "user", "content": EXTRACT_PROMPT}], 0.0, 256)
        walls.append(round(wall, 2))
        m = re.search(r"\{.*\}", content.strip(), re.S)
        ok, why = False, "no_json"
        if m:
            try:
                got = json.loads(m.group(0))
                ok = all(
                    (abs(float(got.get(k)) - v) < 0.01
                     if isinstance(v, float) else str(got.get(k)).strip() == v)
                    for k, v in EXTRACT_SPEC.items())
                if not ok:
                    why = "value_mismatch:" + json.dumps(
                        got, ensure_ascii=False)[:120]
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                why = "parse_error:%s" % e
        hits.append(ok)
        detail.append({"pass": ok, "why": why})
    return {"accuracy": sum(hits) / n, "runs": n, "samples": detail,
            "wall_s": walls}


def eval_toolcall(model, quick):
    n = 1 if quick else 2
    hits, walls, detail = [], [], []
    for _ in range(n):
        _, tcs, wall, _resp = chat(
            model, [{"role": "user", "content": TOOL_PROMPT}], 0.0, 512,
            tools=TOOLS)
        walls.append(round(wall, 2))
        ok, why = False, "no_tool_calls"
        if tcs:
            fn = tcs[0].get("function", {})
            if fn.get("name") == "get_weather":
                try:
                    raw_args = fn.get("arguments", "{}")
                    args = (raw_args if isinstance(raw_args, dict)
                            else json.loads(raw_args))
                    city = str(args.get("city", "")).strip().lower()
                    ok = "athens" in city
                    if not ok:
                        why = "city_arg_wrong:%r" % args
                except (json.JSONDecodeError, TypeError, ValueError) as e:
                    why = "args_not_json:%s" % e
            else:
                why = "wrong_name:%s" % fn.get("name")
        hits.append(ok)
        detail.append({"pass": ok, "why": why})
    return {"accuracy": sum(hits) / n, "runs": n, "samples": detail,
            "wall_s": walls}


def eval_instruct(model, quick):
    n = 1 if quick else 3
    rules = []
    for _ in range(n):
        content, _, wall, _ = chat(
            model,
            [{"role": "system", "content": INSTRUCT_SYSTEM},
             {"role": "user", "content": INSTRUCT_PROMPT}],
            0.1, 512)
        body = content or ""
        checks = {
            "starts_verified": body.lstrip().startswith("VERIFIED"),
            "has_table": "|" in body and "---" in body,
            "no_however": "however" not in body.lower(),
            "ends_marker": body.rstrip().endswith(
                "Done / Pending / Files touched / Next"),
        }
        rules.append({"pass_all": all(checks.values()),
                      "score": sum(checks.values()), "checks": checks,
                      "wall_s": round(wall, 2)})
    return {"rule_pass_rate": sum(r["pass_all"] for r in rules) / n,
            "avg_rules": round(sum(r["score"] for r in rules) / n, 2),
            "runs": n, "samples": rules}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true",
                    help="1 run per task instead of 3 (smoke)")
    args = ap.parse_args()
    results = {"date": "2026-10-08", "quick": args.quick,
               "harness": "scripts/realworld_eval.py",
               "engine": "ollama /api/chat, single slot, ctx 8192",
               "grading": "executable + exact match (no LLM judge)",
               "models": {}}
    tasks = [("code", eval_code), ("extract", eval_extract),
             ("toolcall", eval_toolcall), ("instruct", eval_instruct)]
    for model in MODELS:
        print("== %s ==" % model, flush=True)
        results["models"][model] = {}
        for name, fn in tasks:
            t0 = time.perf_counter()
            try:
                r = fn(model, args.quick)
            except (urllib.error.URLError, OSError, ValueError, KeyError,
                    json.JSONDecodeError) as e:
                r = {"error": "%s: %s" % (type(e).__name__, e)}
            r["task_wall_s"] = round(time.perf_counter() - t0, 1)
            results["models"][model][name] = r
            print("  %-9s %s" % (name, json.dumps(
                {k: v for k, v in r.items() if k != "samples"})), flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    out_path = OUT / ("eval_%s%s.json" % (
        results["date"], "_quick" if args.quick else ""))
    out_path.write_text(json.dumps(results, indent=1))
    print("SAVED %s" % out_path, flush=True)


if __name__ == "__main__":
    main()