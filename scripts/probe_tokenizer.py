#!/usr/bin/env python3
"""Omega Engine Alpha — tokenizer fingerprint probe for rotating stealth aliases.

METHOD
------
Chat endpoints wrap the user message in a provider chat template and charge for
those tokens. Absolute prompt_tokens therefore mixes two unknowns: the upstream
tokenizer AND the template. Raw counts are not interpretable on their own.

This probe separates them by measuring a minimal baseline probe in the SAME
endpoint and reporting:

    delta(probe) = remote_count(probe) - remote_count(baseline)

Template overhead is constant per endpoint and cancels in the subtraction.
Local references are computed the same way, so both sides are comparable.

DISCRIMINATIVE CEILING
----------------------
Reliable for the coarse partition (CJK-native vs Latin-native) and for families
with a LOCAL reference tokenizer. It cannot exclude families with no local
reference. Absence of a match is not evidence of absence. Self-reported model
identity is never an input here — see docs/OPENCODE_FOUNDATION.md.

Backends: openai-compat (Zen/OpenRouter/Ollama /v1), ollama (native), file.
"""
import argparse
import json
import os
import statistics
import sys
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

QWEN_TOKENIZER_PATH = "models/embedding/qwen3-0.6b-onnx/tokenizer.json"
BASELINE = "."
TIMEOUT = 120

# An axis where the local poles agree to within this fraction carries no
# discriminating power. Measured, not guessed: see reference table.
MIN_INFO = 0.06

# If a remote disagrees with BOTH local references by more than this on a
# control axis, the delta method has probably broken (template differs per
# request, or counts are not upstream-authentic). Void the reading.
CONTROL_TOLERANCE = 0.35

# Fixed by hand. Do not edit existing probes or historical runs stop comparing.
# Append only.
CORPUS = {
    "ascii_common": (
        "The quick brown fox jumps over the lazy dog near the riverbank at dawn, "
        "and the miller considers whether the weather will hold until morning."
    ),
    "ascii_rare": (
        "The zygote's quokka-like kludge caused a syzygy in the perambulating "
        "obfuscatory parser; a pseudoporphyritic frisson followed the theremin."
    ),
    "cjk_common": (
        "今天下午的天气很好，我们决定去公园散步，然后一起吃一顿丰盛的晚餐，"
        "聊了很多关于工作和未来的计划，感觉非常放松和愉快。"
    ),
    "cjk_rare": (
        "他翻阅那部尘封已久的古籍，扉页上钤着「囗囗」印记，末尾写着"
        "「□□□」，笔法苍劲，糅合了々与ゝ的旧式写法。"
    ),
    "cjk_mixed": (
        "我们在 Docker 容器里跑了一次 benchmark，发现 throughput 掉了，"
        "大概率是 KV cache 没开 q8_0，重新 configure 之后就 normal 了。"
    ),
    "code": (
        "def probe(self, timeout=300):\n"
        "        result = self._call(payload, retries=3)\n"
        "        if result.status_code != 200:\n"
        "            raise RuntimeError(f'bad status: {result.status_code}')\n"
        "        return result.json()\n"
    ),
    "emoji": "👨‍👩‍👧‍👦 \U0001F1EF\U0001F1F5 👩🏽‍💻 \U0001F3F3️‍\U0001F308 ❤️‍🔥 ✅ \U0001F1E7\U0001F1F7",
    "whitespace": "a" + " " * 24 + "b" + "\t" * 4 + "c" + "\n" * 6 + "d",
    "json": (
        '{"model":"probe","temperature":0,"max_tokens":1,'
        '"options":{"top_p":0.1,"seed":42,"stop":["\\n\\n"]},'
        '"messages":[{"role":"user","content":"x"}]}'
    ),
    "unicode_edge": (
        "éöü ę́  "
        " مرحبا "
        "שלום "
        "ελληνικά "
        " ру́сский "
        " 日本語 한국어"
    ),
}


def log(msg):
    """Progress goes to stderr so stdout stays pure JSON (redirectable)."""
    print(msg, file=sys.stderr, flush=True)


def _o200k():
    try:
        import tiktoken
        return tiktoken.get_encoding("o200k_base")
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            f"o200k_base unavailable (use .venv/bin/python3): {exc}"
        ) from exc


def _qwen():
    try:
        from tokenizers import Tokenizer
    except ImportError as exc:
        raise RuntimeError("tokenizers unavailable (use .venv/bin/python3)") from exc
    if not os.path.exists(QWEN_TOKENIZER_PATH):
        raise RuntimeError(
            f"reference tokenizer absent: {QWEN_TOKENIZER_PATH} — "
            "CJK pole uncalibrated without it"
        )
    try:
        return Tokenizer.from_file(QWEN_TOKENIZER_PATH)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Qwen tokenizer failed to load: {exc}") from exc


def local_reference():
    """Delta-profiles for both locally-held reference tokenizers."""
    enc, qwen = _o200k(), _qwen()
    counters = {
        "o200k_base": lambda s: len(enc.encode(s)),
        "qwen3": lambda s: len(qwen.encode(s).ids),
    }
    refs = {}
    for name, fn in counters.items():
        base = fn(BASELINE)
        axes = {}
        for axis, text in CORPUS.items():
            n = fn(text)
            axes[axis] = {
                "count": n,
                "delta": n - base,
                "chars": len(text),
                "tok_per_char": round(n / len(text), 4),
            }
        refs[name] = {"baseline": base, "axes": axes}

    # An axis only carries information if the two poles DISAGREE about it.
    # Axes where both references agree carry no discriminating power and must
    # not be averaged into the score; they serve as integrity controls instead
    # (a remote diverging wildly on a control axis invalidates the delta
    # method, which is worth far more than a near-miss on a scored axis).
    lo, hi = "o200k_base", "qwen3"
    for axis in CORPUS:
        a = refs[lo]["axes"][axis]["delta"]
        b = refs[hi]["axes"][axis]["delta"]
        denom = max(a, b) or 1
        refs.setdefault("axis_power", {})[axis] = {
            "info": round(abs(a - b) / denom, 4),
            "role": "control" if abs(a - b) / denom < MIN_INFO else "scored",
        }
    return refs


def _post(url, payload, headers, timeout=TIMEOUT):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")[:400]
        raise RuntimeError(f"HTTP {exc.code} from {url} :: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"connection error to {url}: {exc.reason}") from exc
    except TimeoutError as exc:
        raise RuntimeError(f"timeout after {timeout}s at {url}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"non-JSON response from {url}: {exc}") from exc


def _probe_openai(url, model, key, text, repeat):
    """OpenAI-compatible chat completion; reads usage.prompt_tokens."""
    seen = []
    for _ in range(repeat):
        r = _post(
            f"{url.rstrip('/')}/chat/completions",
            {
                "model": model,
                "messages": [{"role": "user", "content": text}],
                "max_tokens": 1,
                "temperature": 0,
                "stream": False,
            },
            {"Authorization": f"Bearer {key}"},
        )
        usage = r.get("usage")
        if not isinstance(usage, dict) or "prompt_tokens" not in usage:
            raise RuntimeError(
                "endpoint returned no usage.prompt_tokens — this probe is "
                f"unusable against it. Response: {json.dumps(r)[:300]}"
            )
        seen.append(int(usage["prompt_tokens"]))
    return seen


def _probe_ollama(host, model, text, repeat):
    """Native Ollama generate; reads prompt_eval_count (upstream tokenizer)."""
    seen = []
    for _ in range(repeat):
        r = _post(
            f"{host.rstrip('/')}/api/generate",
            {"model": model, "prompt": text, "stream": False, "options": {"num_predict": 1}},
            {},
        )
        if "prompt_eval_count" not in r:
            raise RuntimeError(
                "ollama returned no prompt_eval_count. Response: "
                f"{json.dumps(r)[:300]}"
            )
        seen.append(int(r["prompt_eval_count"]))
    return seen


def collect(args):
    probes = {"__baseline__": BASELINE, **CORPUS}
    samples = {}
    for axis, text in probes.items():
        if args.backend == "openai-compat":
            if not args.key:
                raise RuntimeError(
                    "--key or $PROBE_API_KEY required for openai-compat"
                )
            seen = _probe_openai(args.base_url, args.model, args.key, text, args.repeat)
        elif args.backend == "ollama":
            seen = _probe_ollama(args.base_url, args.model, text, args.repeat)
        elif args.backend == "file":
            with open(args.input, encoding="utf-8") as fh:
                seen = json.load(fh)["samples"][axis]
        else:
            raise RuntimeError(f"unknown backend: {args.backend}")
        samples[axis] = seen
        log(f"  {axis:16} n={len(seen)} median={int(statistics.median(seen))}")
    return {
        "schema": "omega.tokenizer_fingerprint/1",
        "provenance": {
            "collected_at": args.collected_at,
            "backend": args.backend,
            "base_url": args.base_url,
            "model_label": args.model,
            "repeat": args.repeat,
            "note": args.model_note,
        },
        "samples": samples,
        "baseline_median": int(statistics.median(samples["__baseline__"])),
    }


def classify(result):
    """Score a collection against local references. Report the ceiling."""
    refs = local_reference()
    base = result["baseline_median"]
    obs = {}
    for axis, seen in result["samples"].items():
        if axis == "__baseline__":
            continue
        med = int(statistics.median(seen))
        obs[axis] = {
            "median": med,
            "delta": med - base,
            "chars": len(CORPUS[axis]),
            "tok_per_char": round(med / len(CORPUS[axis]), 4),
            "spread": max(seen) - min(seen),
        }

    log("\n─── observed vs reference (delta from in-endpoint baseline) ───")
    log(f"{'axis':16} {'obs':>6} {'wt':>5} " + " ".join(f"{r:>12}" for r in ("o200k_base", "qwen3")))
    power = refs["axis_power"]
    scores = {"o200k_base": 0.0, "qwen3": 0.0}
    weight_total = 0.0
    controls_failed = []
    for axis, o in obs.items():
        wt = power[axis]["info"]
        role = power[axis]["role"]
        row = f"{axis:16} {o['delta']:>6} {wt:>5.2f} "
        ratios = {}
        for name in ("o200k_base", "qwen3"):
            rd = refs[name]["axes"][axis]["delta"]
            ratio = o["delta"] / rd if rd else float("inf")
            ratios[name] = ratio
            row += f"{str(rd) + ' (' + f'{ratio:.2f}x' + ')':>12}"
        if role == "scored":
            for name in scores:
                scores[name] += wt * abs(ratios[name] - 1.0)
            weight_total += wt
        else:
            # Integrity control: poles agree here, so remote must too.
            if min(abs(ratios[n] - 1.0) for n in ratios) > CONTROL_TOLERANCE:
                controls_failed.append(
                    f"{axis} (obs {o['delta']}, refs {ratios['o200k_base']:.2f}x/"
                    f"{ratios['qwen3']:.2f}x)"
                )
        log(row)

    if controls_failed:
        log("\n!! INTEGRITY FAIL — reading VOID. Deltas diverge on axes where the")
        log("!! reference poles agree, so the template/delta assumption is broken")
        log("!! or counts are relay-computed. Offending axes:")
        for c in controls_failed:
            log(f"!!   {c}")
    else:
        log("\nintegrity controls passed (relay is plausibly counting upstream)")

    ranked = sorted(scores.items(), key=lambda kv: kv[1] / (weight_total or 1))
    verdict, confidence = ranked[0], "high" if ranked[1][1] > ranked[0][1] * 1.5 else "low"

    log(f"\nnearest local reference: {verdict[0]}  "
        f"(weighted distance {verdict[1] / (weight_total or 1):.3f})")
    log(f"separation confidence: {confidence}")
    if abs(ranked[0][1] - ranked[1][1]) < 0.15 * weight_total:
        log("!! references too close to separate — widen the corpus")

    cjk_o = obs["cjk_common"]["tok_per_char"]
    lat_o = obs["ascii_common"]["tok_per_char"]
    partition = "CJK-native leaning" if cjk_o < lat_o else "Latin-native leaning"
    log(f"coarse partition (cjk/ascii ratio): {cjk_o}/{lat_o} -> {partition}")

    log("\n!! CEILING: excludes NO family lacking a local reference tokenizer.")
    log("!! 'nearest reference' is not identity. Self-report is not evidence.")
    return {
        "schema": "omega.tokenizer_fingerprint/1.analysis",
        "observed": obs,
        "axis_power": power,
        "nearest_reference": ranked[0][0],
        "separation_confidence": confidence,
        "partition": partition,
        "integrity_controls_passed": not controls_failed,
        "integrity_failures": controls_failed,
        "unresolved_families": ["glm", "claude", "deepseek", "llama", "unknown"],
        "conclusion": (
            "VOID — integrity controls failed"
            if controls_failed else "partial — coarse partition only"
        ),
    }


class _Stub(BaseHTTPRequestHandler):
    """Hermetic fake endpoint returning o200k-computed counts."""

    counts = {}

    def do_POST(self):  # noqa: N802
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        text = body.get("messages", [{}])[0].get("content", "")
        n = len(_o200k().encode(text)) + 7  # +7 simulates template overhead
        out = json.dumps(
            {"usage": {"prompt_tokens": n, "completion_tokens": 1}}
        ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def log_message(self, *_a):
        return


def selftest(_args):
    """Validate the instrument against a stub whose tokenizer we control."""
    log("─── selftest: stub endpoint with known tokenizer (o200k_base) ───")
    srv = HTTPServer(("127.0.0.1", 0), _Stub)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/v1"
    try:
        res = collect(
            argparse.Namespace(
                backend="openai-compat", base_url=url, model="stub", key="x",
                repeat=2, input=None, collected_at="selftest", model_note="stub",
            )
        )
        analysis = classify(res)
    finally:
        srv.shutdown()
    ok = analysis["nearest_reference"] == "o200k_base"
    log(f"\n{'PASS' if ok else 'FAIL'}: stub resolved to {analysis['nearest_reference']}")
    if not ok:
        raise RuntimeError("instrument failed to recover a known tokenizer")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("reference", help="print local reference profiles")
    sub.add_parser("selftest", help="validate instrument against a known tokenizer")

    c = sub.add_parser("collect", help="measure a remote endpoint")
    c.add_argument("--backend", default="openai-compat",
                   choices=["openai-compat", "ollama", "file"])
    c.add_argument("--base-url", default="https://opencode.ai/zen/v1")
    c.add_argument("--model", required=True)
    c.add_argument("--key", default=os.environ.get("PROBE_API_KEY"))
    c.add_argument("--repeat", type=int, default=3)
    c.add_argument("--input", help="JSON file for --backend file")
    c.add_argument("--collected-at", default="unset")
    c.add_argument("--model-note", default="")

    cl = sub.add_parser("classify", help="score a collection")
    cl.add_argument("--input", required=True)

    args = ap.parse_args()
    try:
        if args.cmd == "reference":
            log(json.dumps(local_reference(), indent=2, ensure_ascii=False))
        elif args.cmd == "selftest":
            return selftest(args)
        elif args.cmd == "collect":
            log(json.dumps(collect(args), indent=2, ensure_ascii=False))
        else:
            try:
                with open(args.input, encoding="utf-8") as fh:
                    res = json.load(fh)
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    f"{args.input} is not valid JSON ({exc}). Note that progress "
                    "goes to stderr, so redirect only stdout: "
                    f"'... collect > {args.input}'"
                ) from exc
            if "samples" not in res:
                raise RuntimeError(
                    f"{args.input} has no 'samples' key — is it a collect output?"
                )
            log(json.dumps(res["provenance"], indent=2))
            log(json.dumps(classify(res), indent=2, ensure_ascii=False))
        return 0
    except RuntimeError as exc:
        log(f"PROBE FAILED: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
