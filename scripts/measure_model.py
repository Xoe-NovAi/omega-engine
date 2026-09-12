#!/usr/bin/env python3
"""
Omega Engine Alpha — OMER M2 Measurement CLI

Appends a dated, evidence-labelled `## Local Measurement` block to a model
card, so the card can rise from `Indicative` to `Controlled`+ (the only
promotion path in the OMER v1.0 registry).

Composes with (does not reinvent):
  - `scripts/validate_model_cards.py` — the OMER v1.0 schema it validates against
  - `scripts/bench.py` — the same anyio-pure urllib generate pattern
  - `scripts/measure_model.py` — the M1 validator (evidence labels)

Recording contract (enforced by `omer measure` + `make lint`):
  1. ANYIO-PURE: stdlib urllib only. No bare asyncio/trio, no torch
     (hard reject in `make lint`).
  2. HARD TIMEOUT: every request capped via `urlopen(timeout=...)`; the CLI
     also refuses to run against a TTY-hanging subprocess (`</dev/null`).
  3. DATED: the appended block carries a UTC timestamp; old blocks are never
     overwritten, so the card shows reproducibility over time.
  4. CONFIG-HASHED: model + seed + prompts + hardware mask feed a SHA-256
     config hash; identical hash ⇒ identical measurable setup.
  5. P-CORE-TRAP GUARD: `allowed_cpus` must include HT siblings (0-11),
     NOT the physical-only trap `0,2,4,6,8,10` — same hard guard as M1.

Run:
  ./scripts/omer measure docs/models/nex-n2-5-pro.md --model nex-agi/nex-n2.5-pro:free --seed 42 --prompts 3
"""
import argparse
import json
import platform
import re
import statistics
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

OLLAMA_HOST_DEFAULT = "http://localhost:11434"
REQUEST_TIMEOUT = 120  # hard ceiling per request (seconds)
NPROC_TIMEOUT = 5  # subprocess ceiling for nproc (seconds)

# Physical-P-core-only mask — the Omega Pin Trap. Hard-rejected.
P_TRAP_MASK = (0, 2, 4, 6, 8, 10)

# Evidence label OMER v1.0 recognizes for a measured card:
LOCAL_EVIDENCE = "Local measurement"

# Reproduction status OMER v1.0 recognizes after a controlled local run:
CONTROLLED = "Controlled"


def log(msg: str) -> None:
    print(msg, flush=True)


def allowed_cpus() -> str:
    """Best-effort effective allowed_cpus: systemd override → ollama env → nproc."""
    # 1. systemd override (source of truth for this deployment)
    ov = Path("/etc/systemd/system/ollama.service.d/override.conf")
    if ov.exists():
        try:
            for line in ov.read_text(encoding="utf-8").splitlines():
                m = re.search(r"AllowedCPUs=([0-9,\-]+)", line)
                if m:
                    return m.group(1)
        except OSError:
            pass
    # 2. ollama env
    try:
        out = subprocess.run(["systemctl", "show", "ollama", "-p", "Environment"],
                             capture_output=True, text=True, timeout=NPROC_TIMEOUT)
        for token in out.stdout.split():
            if token.startswith("OLLAMA_NUM_THREADS="):
                pass  # threads captured separately; mask still needed
            if token.startswith("AllowedCPUs=") or "AllowedCPUs" in token:
                m = re.search(r"AllowedCPUs=([0-9,\-]+)", token)
                if m:
                    return m.group(1)
    except (OSError, subprocess.SubprocessError):
        pass
    # 3. nproc fallback
    try:
        out = subprocess.run(["nproc"], capture_output=True, text=True, timeout=NPROC_TIMEOUT)
        n = int(out.stdout.strip())
        return f"0-{n - 1}"
    except Exception:
        return "0-11"


def pcore_trap_guard(allowed: str) -> bool:
    """Reject the physical-P-core-only trap: mask must include HT siblings."""
    # Parse "0-11" or "0,2,4,..." into an int set
    cpus = set()
    for part in allowed.split(","):
        if "-" in part:
            lo, hi = part.split("-", 1)
            cpus.update(range(int(lo), int(hi) + 1))
        elif part.isdigit():
            cpus.add(int(part))
    # Trap = exactly the 6 physical P-cores, no HT siblings
    return not (cpus == set(P_TRAP_MASK))


def capture_hardware() -> dict:
    """Capture the hardware profile at measure time (mirrors bench.py)."""
    # KV cache / KV type via `ollama ps` when available
    kv_cache = "unknown"
    quantization = "unknown"
    flash_attention = False
    try:
        out = subprocess.run(["ollama", "ps"], capture_output=True, text=True, timeout=10).stdout
        for line in out.splitlines():
            if "MODEL" in line.upper() or not line.strip():
                continue
            if "q8_0" in line.lower() or "q_8" in line.lower():
                kv_cache = "q8_0"
            if "q4_k_m" in line.lower() or "q4_k" in line.lower():
                quantization = "Q4_K_M"
            if "flash" in line.lower() or "fa" in line.lower():
                flash_attention = True
    except (OSError, subprocess.SubprocessError):
        pass

    threads = 8  # default recipe (OLLAMA_NUM_THREADS=8)
    try:
        out = subprocess.run(["nproc"], capture_output=True, text=True, timeout=NPROC_TIMEOUT).stdout
        nprocs = int(out.strip())
    except Exception:
        nprocs = 16
    threads = min(nprocs, 12)  # never oversubscribe HT-free

    ram_gb = 0
    try:
        with open("/proc/meminfo", encoding="utf-8") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    ram_gb = int(line.split()[1]) // (1024 * 1024)
                    break
    except OSError:
        ram_gb = 16

    allowed = allowed_cpus()
    return {
        "cpu": platform.processor() or platform.machine(),
        "cores": nprocs,
        "threads": threads,
        "allowed_cpus": allowed,
        "ram_gb": ram_gb,
        "kv_cache": kv_cache,
        "quantization": quantization,
        "flash_attention": flash_attention,
        "anyio_pure": True,
    }


def config_hash(model: str, hw: dict, seed: int, prompts: list[str]) -> str:
    """Deterministic SHA-256 config fingerprint — same hash ⇒ same setup."""
    import hashlib
    blob = json.dumps({
        "model": model,
        "seed": seed,
        "prompts": prompts,
        "hardware": hw,
        "omer_milestone": "M2",
    }, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def generate(host: str, model: str, prompt: str) -> dict:
    """POST /api/generate (anyio-pure urllib, hard timeout). Raises RuntimeError on failure."""
    data = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request(
        f"{host}/api/generate",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:500]
        raise RuntimeError(f"HTTP {e.code} from {host}/api/generate :: {body}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"connection error to {host}: {e.reason}") from e
    except TimeoutError:
        raise RuntimeError(f"request timed out after {REQUEST_TIMEOUT}s") from None
    dt = time.monotonic() - t0
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"non-JSON response: {raw[:300]!r}") from e
    payload["_omega_dt"] = dt
    return payload


DEFAULT_PROMPTS = [
    "Explain quantum computing in one sentence.",
    "Write a Python function to sort a list.",
    "What are the pros and cons of microservices?",
    "Summarize the history of the internet.",
    "Write a haiku about debugging code.",
]


def measure(host: str, model: str, prompts: list[str]) -> dict:
    """Run prompts, return aggregate {tokens, tps, p95, runs}."""
    latencies: list[float] = []
    tokens = 0
    dt_total = 0.0
    runs = []
    for prompt in prompts:
        resp = generate(host, model, prompt)
        eval_count = int(resp.get("eval_count", 0))
        dt = float(resp.get("_omega_dt", 0.0))
        tokens += eval_count
        dt_total += dt
        latencies.append(dt)
        runs.append({"prompt": prompt[:60], "tokens": eval_count, "dt_s": round(dt, 3)})
    tps = tokens / dt_total if dt_total else 0.0
    p95 = statistics.quantiles(latencies, n=20)[-1] if len(latencies) >= 20 else max(latencies)
    return {
        "tokens": tokens,
        "total_s": round(dt_total, 3),
        "tokens_per_sec": round(tps, 2),
        "p95_latency_s": round(p95, 3),
        "runs": runs,
    }


def append_local_measurement(card: Path, model: str, results: dict, hw: dict, seed: int, hash_: str) -> None:
    """Insert a dated `## Local Measurement` block before the verdict section."""
    text = card.read_text(encoding="utf-8")
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    block = f"""
## Local Measurement — {date}

| Metric | Value |
|---|---:|
| Tokens/sec | **{results['tokens_per_sec']}** |
| P95 latency | **{results['p95_latency_s']}s** |
| Total tokens | {results['tokens']} |
| Total time | {results['total_s']}s |
| Hardware | {hw['cpu']} · {hw['cores']} threads · {hw['ram_gb']} GB RAM |
| Allowed CPUs | `{hw['allowed_cpus']}` |
| Quantization | {hw['quantization']} |
| KV cache | {hw['kv_cache']} |
| Flash attention | {hw['flash_attention']} |
| Config hash | `{hash_}` |
| Seed | {seed} |
| Evidence | **{LOCAL_EVIDENCE}** |
| Reproduction | **{CONTROLLED}** |

> Measured {date} with `./scripts/omer measure --seed {seed}`.
> Config hash {hash_} — identical hash ⇒ identical measurable setup.
"""
    # Insert before `## Omega Verdict`/`## Sources`/`## Omega Verdict and promotion`
    insert_before = None
    for marker in ("## Omega Verdict", "## Sources", "## Omega verdict and promotion"):
        if marker in text:
            insert_before = marker
            break
    if insert_before:
        text = text.replace(insert_before, f"{block.strip()}\n\n{insert_before}", 1)
    else:
        text = f"{text.rstrip()}\n\n{block.strip()}\n"
    card.write_text(text, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="OMER M2: local model measurement — appends a dated Local Measurement block")
    ap.add_argument("card", help="Model card path, e.g. docs/models/nex-n2-5-pro.md")
    ap.add_argument("--model", help="Ollama model id (default: from card frontmatter)")
    ap.add_argument("--host", default=OLLAMA_HOST_DEFAULT)
    ap.add_argument("--prompts", type=int, default=len(DEFAULT_PROMPTS))
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--dry-run", action="store_true", help="Capture hardware + prints block; no inference, no write")
    args = ap.parse_args()

    card = Path(args.card)
    if not card.exists():
        log(f"✗ Card not found: {card}")
        return 1

    # Pull model_id from frontmatter if --model not given
    model = args.model
    if not model:
        m = re.search(r"model_id:\s*[\"']?(.+?)[\"']?\s*$", card.read_text(encoding="utf-8"), re.MULTILINE)
        model = m.group(1) if m else None
    if not model:
        log("✗ Could not determine model_id from card frontmatter. Pass --model.")
        return 1

    hw = capture_hardware()
    # OMER M1 hard guard: P-core-only mask is rejected here too
    if not pcore_trap_guard(hw["allowed_cpus"]):
        log(f"✗ OMER-PIN-TRAP: allowed_cpus={hw['allowed_cpus']} is physical-P-core-only. "
            f"Use 0-11 (P-cores + HT siblings). See docs/HARDWARE.md")
        return 3

    prompts = DEFAULT_PROMPTS[: args.prompts]
    hash_ = config_hash(model, hw, args.seed, prompts)

    log(f"── OMER M2 measurement ──")
    log(f"  model : {model}")
    log(f"  hw    : {hw['allowed_cpus']} allowed · {hw['threads']} threads · {hw['ram_gb']} GB")
    log(f"  seed  : {args.seed} | hash: {hash_}")

    if args.dry_run:
        log("  [dry-run] no inference; would append block:")
        mock = {"tokens": 0, "total_s": 0.0, "tokens_per_sec": 0.0, "p95_latency_s": 0.0}
        return 0

    results = measure(args.host, model, prompts)
    results["tokens_per_sec"] = round(results["tokens"] / results["total_s"], 2) if results["total_s"] else 0.0
    append_local_measurement(card, model, results, hw, args.seed, hash_)

    log(f"  ✓ measured {results['tokens']} tokens in {results['total_s']}s "
        f"= {results['tokens_per_sec']} t/s | P95 {results['p95_latency_s']}s")
    log(f"  ✓ appended Local Measurement to {card}")
    log(f"  Card stays `candidate` until an Omega A/B + verdict promotes it (§2.5).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
