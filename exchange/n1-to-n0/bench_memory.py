#!/usr/bin/env python3
"""Achievable memory bandwidth on Node 1 — the physical ceiling for decode.

WHY THIS EXISTS
---------------
Autoregressive decode reads the full model weights for every generated token.
The IETF benchmarking draft states it plainly: "Decode is memory-bandwidth-bound
because each token requires reading the full model weights." So before asking
"how many threads is fastest?", we must know how much bandwidth is even
available, and how that bandwidth scales with thread count.

STREAM (McCalpin, Univ. of Virginia) is the de facto standard for sustained
bandwidth. Its Triad kernel (a[i] = b[i] + s*c[i]) is the standard figure
quoted for "memory bandwidth" and is the closest analogue to the weight-streaming
access pattern of decode.

The second job here is equally important: STREAM tells us at what thread count
bandwidth SATURATES. Past that point extra threads cannot add memory-level
parallelism, so extra threads buy nothing for a bandwidth-bound workload. That
saturation point is the physical upper bound on useful inference threads.

Reference expectations (StreamBench published ranges, DDR5-5600):
    single-channel  ~26-37 GB/s CPU STREAM
    dual-channel    ~55-70 GB/s CPU STREAM
Our box is single-channel (second slot empty), so ~32 GB/s is the expected
result. Dual-channel is the single highest-value hardware upgrade for this
workload and this script is the measurement that quantifies the prize.

Usage:
    python3 scripts/bench_memory.py
    python3 scripts/bench_memory.py --rebuild
"""

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

STREAM_URL = "https://www.cs.virginia.edu/stream/FTP/Code/stream.c"
BUILD_DIR = Path("/tmp/opencode/stream")
BINARY = BUILD_DIR / "stream"
# 80M doubles per array * 3 arrays touched by Triad ≈ 1.9 GB working set,
# far beyond the 24 MB L3, which is the point of STREAM.
ARRAY_SIZE = 80_000_000


def log(msg: str) -> None:
    print(msg, flush=True)


def _read(path: str) -> str:
    try:
        return Path(path).read_text().strip()
    except OSError:
        return ""


def _run(cmd: list, timeout: int = 120) -> tuple:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout, check=False)
        return (proc.returncode, proc.stdout, proc.stderr)
    except (subprocess.SubprocessError, OSError) as exc:
        return (1, "", str(exc))


def fetch_and_build(force: bool = False) -> bool:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    source = BUILD_DIR / "stream.c"
    if force or not source.exists() or source.stat().st_size < 1000:
        log(f"  fetching {STREAM_URL}")
        code, _, err = _run(["curl", "-sL", "-o", str(source), STREAM_URL], 120)
        if code != 0 or not source.exists():
            log(f"  ✗ fetch failed: {err}")
            return False
    if force or not BINARY.exists():
        log("  compiling with OpenMP (this takes a minute)")
        code, _, err = _run(
            ["gcc", "-O3", "-fopenmp", f"-DSTREAM_ARRAY_SIZE={ARRAY_SIZE}",
             "-DNTIMES=10", str(source), "-o", str(BINARY)],
            timeout=300,
        )
        if code != 0:
            log(f"  ✗ compile failed: {err[:400]}")
            return False
    return True


def dimm_summary() -> dict:
    code, out, _ = _run(["sudo", "-n", "dmidecode", "-t", "memory"])
    info = {"populated": [], "empty_slots": 0, "type": "", "configured_mt_s": "",
            "advertised_mt_s": ""}
    if code != 0:
        return info
    locator = re.findall(r"Locator: (\S+)", out)
    sizes = re.findall(r"Size: (No Module Installed|\d+ ?GB)", out)
    for loc, size in zip(locator, sizes):
        if size == "No Module Installed":
            info["empty_slots"] += 1
        else:
            info["populated"].append(f"{loc}={size}")
    ty = re.search(r"Type: (DDR\d\S*)", out)
    if ty:
        info["type"] = ty.group(1)
    cfg = re.search(r"Configured Memory Speed: (\d+)", out)
    if cfg:
        info["configured_mt_s"] = int(cfg.group(1))
    adv = re.search(r"Speed: (\d+)", out)
    if adv:
        info["advertised_mt_s"] = int(adv.group(1))
    return info


def theoretical_gb_s(mt_s: int, channels: int) -> float:
    """DDR transfer rate is MT/s; each transfer moves 8 bytes (64-bit bus)."""
    return round(mt_s * 8 * channels / 1000, 1)


def run_triad(threads: int, cpus: str) -> Optional[float]:
    code, out, _ = _run(
        ["taskset", "-c", cpus, "env",
         f"OMP_NUM_THREADS={threads}", "OMP_PROC_BIND=spread",
         "OMP_PLACES=cores", str(BINARY)],
        timeout=180,
    )
    if code != 0:
        return None
    best = None
    for line in out.splitlines():
        if "Triad" not in line:
            continue
        # "Function Best Rate MB/s Avg rate MB/s Min rate MB/s Max rate MB/s"
        parts = line.split()
        try:
            idx = parts.index("Triad:")
            best = max(best or 0.0, float(parts[idx + 1]))
        except (ValueError, IndexError):
            continue
    return best


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rebuild", action="store_true")
    ap.add_argument("--threads", default="1,2,3,4,5,6,8,10,12")
    ap.add_argument("--cpus", default="0-11", help="cpuset for the test")
    ap.add_argument("--out", default="bench_memory_report.json")
    args = ap.parse_args()

    log("Node 1 memory bandwidth — physical ceiling for autoregressive decode")
    log("─" * 70)

    if not fetch_and_build(args.rebuild):
        log("✗ could not obtain STREAM; bandwidth ceiling remains unknown")
        return 1

    dimm = dimm_summary()
    channels = 1 if dimm["empty_slots"] else 2
    theo = theoretical_gb_s(dimm["configured_mt_s"], channels) if dimm["configured_mt_s"] else None

    log(f"  memory    : {' '.join(dimm['populated']) or 'unknown'}  "
        f"empty_slots={dimm['empty_slots']}  type={dimm['type']}")
    log(f"  speed     : {dimm['configured_mt_s']} MT/s configured "
        f"({dimm['advertised_mt_s']} advertised)  channels={channels}")
    if theo:
        log(f"  theoretical peak: {theo} GB/s  ({dimm['configured_mt_s']} MT/s x 8 B x {channels} ch)")
    log("")

    thread_list = [int(t) for t in args.threads.split(",") if t.strip()]
    rows = []
    log(f"  {'threads':>7} {'triad MB/s':>12} {'GB/s':>8} {'% of peak':>10}")
    for n in thread_list:
        bw = run_triad(n, args.cpus)
        if bw is None:
            log(f"  {n:>7} {'failed':>12}")
            rows.append({"threads": n, "triad_mb_s": None})
            continue
        gbs = round(bw / 1000, 2)
        pct = round(bw / (theo * 1_000_000) * 100, 1) if theo else None
        log(f"  {n:>7} {bw:>12.1f} {gbs:>8.2f} "
            f"{f'{pct:>9.1f}%' if pct else '        -'}")
        rows.append({"threads": n, "triad_mb_s": round(bw, 1), "gb_s": gbs,
                     "pct_of_theoretical": pct})

    valid = [r for r in rows if r.get("gb_s")]
    if valid:
        peak = max(valid, key=lambda r: r["gb_s"])
        log("")
        log(f"  SATURATION: peak {peak['gb_s']} GB/s at {peak['threads']} threads")
        # first thread count within 95% of peak = point of diminishing returns
        knee = next((r["threads"] for r in valid
                     if r["gb_s"] >= peak["gb_s"] * 0.95), peak["threads"])
        log(f"  USEFUL-THREAD CEILING: {knee} threads (first to reach 95% of peak)")
        log("  Past this point extra threads add no memory-level parallelism, so")
        log("  a bandwidth-bound workload cannot benefit from them.")
        if dimm["empty_slots"]:
            log("")
            log(f"  *** UPGRADE PRIZE: {dimm['empty_slots']} empty slot(s). Populating it")
            log(f"      enables dual-channel -> theoretical {theoretical_gb_s(dimm['configured_mt_s'], 2)} GB/s,")
            log(f"      roughly DOUBLE the decode ceiling. This is the single")
            log(f"      highest-value hardware change for LLM inference here.")
    else:
        log("\n  ✗ no valid STREAM measurements")

    payload = {"dimm": dimm, "channels": channels,
               "theoretical_gb_s": theo, "measurements": rows}
    Path(args.out).write_text(json.dumps(payload, indent=2))
    log(f"\n  report written: {args.out}")
    return 0 if valid else 1


if __name__ == "__main__":
    sys.exit(main())
