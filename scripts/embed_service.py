#!/usr/bin/env python3
"""E-core Ollama instance for background embedding work.

WHY A SECOND SERVER
-------------------
The primary `ollama.service` is started with `AllowedCPUs=0-11`, which is the
correct P-core-only pin for latency-sensitive generation on this hybrid part
(see AGENTS.md: do NOT narrow it further, or llama.cpp's spin-wait barrier
convoy collapses throughput — ollama#17916). The consequence, verified live on
2026-09-26, is that the primary server's `Cpus_allowed_list` is `0-11` and the
four E-cores (CPUs 12-15) are PHYSICALLY UNREACHABLE to it. A single Ollama
process therefore cannot place embeddings on E-cores and generation on P-cores.

So we run a second, purpose-built instance:

  primary  ollama.service   AllowedCPUs=0-11  (P-cores)  LLM / interactive
  embed    ollama-embed     AllowedCPUs=12-15 (E-cores)  background embeddings

Two processes, two thread pools, two independent load generators. That is real
isolation. The alternative — widening the primary server to 0-15 and hoping the
scheduler sorts it out — would re-expose the P-core convoy trap and would depend
on Linux's energy-aware scheduler placing a latency-critical pool on P-cores and
a background pool on E-cores. Intel Thread Director is NOT available to do this
for us on Linux: per unix.stackexchange (2026-06) the kernel forwards HFI events
to a userspace daemon and *"patches to enable ITD at hardware level ... do not
seem that any of those have been merged."* So explicit pinning is the correct
mechanism, not a workaround.

WHAT THIS DOES *NOT* SOLVE
-------------------------
E-cores do not have a private power or memory budget. Per Intel's own OpenEdge
guidance, heterogeneous cores share the package power budget, and a warning
worth repeating verbatim: "GPU/NPU power starvation when CPU cores consume the
bulk of the power budget." On this machine the LLM already draws ~40 W of a
45 W package budget and reaches 94-98 C against a 100 C tJMax. E-cores will
still contend for that package power AND for memory bandwidth, which STREAM
measured as saturating at ~32.6 GB/s on 4-5 threads. Isolating the cores is
necessary; it is not sufficient. The harness measures the residual contention
rather than assuming it away.

Usage:
    python3 scripts/embed_service.py install     # write + start the unit
    python3 scripts/embed_service.py status
    python3 scripts/embed_service.py uninstall
    python3 scripts/embed_service.py embed --threads 2 --batches 50
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

EMBED_PORT = 11435
EMBED_HOST = f"http://127.0.0.1:{EMBED_PORT}"
EMBED_MODEL = "qwen3-embedding:0.6b"
ECORE_CPUS = "12-15"
UNIT_NAME = "ollama-embed.service"
UNIT_PATH = Path(f"/etc/systemd/system/{UNIT_NAME}")

UNIT_TEMPLATE = """[Unit]
Description=Ollama embedding instance pinned to E-cores (background work)
After=network.target
# Deliberately NOT After=ollama.service: these are independent workloads.

[Service]
Type=simple
# Identity MUST mirror the stock unit. Without User= and an explicit HOME,
# ollama aborts at startup with `panic: $HOME is not defined`
# (envconfig.Models() -> config.go:120) and systemd restarts it forever. The
# first install of this unit failed exactly that way.
User=ollama
Group=ollama
Environment=HOME=/usr/share/ollama
WorkingDirectory=/usr/share/ollama
Environment=OLLAMA_HOST=127.0.0.1:11435
Environment=OLLAMA_MAX_LOADED_MODELS=1
Environment=OLLAMA_NUM_PARALLEL=1
Environment=OLLAMA_KEEP_ALIVE=30m
Environment=OLLAMA_CONTEXT_LENGTH=8192
Environment=OLLAMA_KV_CACHE_TYPE=q8_0
Environment=OLLAMA_FLASH_ATTENTION=1
Environment=OLLAMA_NO_CLOUD=1
Environment=OMP_NUM_THREADS={threads}
AllowedCPUs={ecores}
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""


def log(msg: str) -> None:
    print(msg, flush=True)


def run(cmd: list, timeout: int = 60) -> tuple:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout, check=False)
        return (proc.returncode, proc.stdout, proc.stderr)
    except (subprocess.SubprocessError, OSError) as exc:
        return (1, "", str(exc))


def sudo_run(cmd: list, timeout: int = 60) -> tuple:
    return run(["sudo", "-n", *cmd], timeout)


def run_env(env: dict, cmd: list, timeout: int = 60) -> tuple:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, env=env,
                              timeout=timeout, check=False)
        return (proc.returncode, proc.stdout, proc.stderr)
    except (subprocess.SubprocessError, OSError) as exc:
        return (1, "", str(exc))


def embed_server_pid() -> Optional[int]:
    """PID of the ollama serve process whose OLLAMA_HOST is the embed port."""
    out = run(["ps", "-eo", "pid,args"])[1]
    for line in out.splitlines():
        if "ollama serve" not in line or "grep" in line:
            continue
        pid = int(line.split()[0])
        try:
            env = Path(f"/proc/{pid}/environ").read_bytes().decode(
                errors="replace").split("\0")
        except OSError:
            continue
        if any(e == f"OLLAMA_HOST=127.0.0.1:{EMBED_PORT}" for e in env):
            return pid
    return None


def _processes() -> list:
    """(pid, ppid, args) for every process, read straight from /proc."""
    rows = []
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            stat = (entry / "stat").read_text()
            tail = stat.rsplit(")", 1)[1].split()
            ppid = int(tail[1])
            args = (entry / "cmdline").read_bytes().decode(
                errors="replace").replace("\0", " ").strip()
        except (OSError, ValueError, IndexError):
            continue
        rows.append((int(entry.name), ppid, args))
    return rows


def install(threads: int, ecores: str) -> int:
    unit = UNIT_TEMPLATE.format(threads=threads, ecores=ecores)
    tmp = Path("/tmp") / UNIT_NAME
    tmp.write_text(unit)
    code, _, err = sudo_run(["cp", str(tmp), str(UNIT_PATH)])
    if code != 0:
        log(f"x could not install unit: {err}")
        return 1
    log(f"  wrote {UNIT_PATH} with AllowedCPUs={ecores} OMP_NUM_THREADS={threads}")
    sudo_run(["systemctl", "daemon-reload"])
    sudo_run(["systemctl", "enable", "--now", UNIT_NAME], timeout=120)
    for _ in range(30):
        code, _, _ = run(["systemctl", "is-active", UNIT_NAME])
        if code == 0:
            break
        time.sleep(1)
    status()
    return 0


def uninstall() -> int:
    sudo_run(["systemctl", "disable", "--now", UNIT_NAME], timeout=120)
    code, _, err = sudo_run(["rm", "-f", str(UNIT_PATH)])
    sudo_run(["systemctl", "daemon-reload"])
    log(f"  removed {UNIT_NAME}" if code == 0 else f"  rm failed: {err}")
    return 0 if code == 0 else 1


def status() -> int:
    code, out, _ = run(["systemctl", "is-active", UNIT_NAME])
    active = "active" if code == 0 else out.strip() or "inactive"
    log(f"  unit: {active}")
    pids = run(["pgrep", "-f", "ollama serve"])[1].split()
    log(f"  ollama serve processes: {len(pids)} {pids}")
    for pid in pids:
        st = Path(f"/proc/{pid}/status")
        if st.exists():
            for line in st.read_text().splitlines():
                if line.startswith("Cpus_allowed_list"):
                    log(f"    pid {pid}: {line.split()[1]}")
    try:
        with urllib.request.urlopen(f"{EMBED_HOST}/api/version", timeout=5) as resp:
            ver = json.loads(resp.read()).get("version")
        log(f"  embed endpoint {EMBED_HOST}: responding, ollama {ver}")
        return 0
    except (urllib.error.URLError, OSError, ValueError, json.JSONDecodeError):
        log(f"  embed endpoint {EMBED_HOST}: NOT responding")
        return 1


def embed_batch(texts: list, timeout: int = 120) -> dict:
    payload = {"model": EMBED_MODEL, "input": texts}
    req = urllib.request.Request(
        f"{EMBED_HOST}/api/embed",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = json.loads(resp.read())
    dt = time.perf_counter() - t0
    emb = body.get("embeddings") or []
    dim = len(emb[0]) if emb else 0
    return {"n": len(texts), "dim": dim, "elapsed_s": dt,
            "texts_per_s": len(texts) / dt if dt else 0.0}


def sweep(threads_list: list, batches: int, batch_size: int) -> list:
    """Sweep the embedding model's thread count on the E-core instance."""
    env = {**os.environ, "OLLAMA_HOST": EMBED_HOST}
    results = []
    self_pid = embed_server_pid()
    log(f"  embed server pid: {self_pid}")

    # PHASE 1: create all variants up front, with a short per-create timeout.
    # Creating inside the per-config loop let one stalled create burn the entire
    # time budget (4 x 240s = 16 min observed) and silently produced no data.
    created = {}
    for n in threads_list:
        name = f"emb-t{n}"
        path = Path("/tmp") / f"{name}.Modelfile"
        path.write_text(f"FROM {EMBED_MODEL}\nPARAMETER num_thread {n}\n")
        subprocess.run(["ollama", "rm", "-f", name], capture_output=True,
                       text=True, timeout=30, env=env, check=False)
        t_create = time.perf_counter()
        code, _, err = run_env(env, ["ollama", "create", name, "-f", str(path)],
                               timeout=90)
        dt_create = time.perf_counter() - t_create
        if code != 0:
            log(f"  x threads={n}: create FAILED in {dt_create:.0f}s: "
                f"{err.strip()[:110]}")
            results.append({"threads": n, "ok": False, "error": err.strip()[:200]})
            continue
        created[n] = name
        log(f"  + created {name} in {dt_create:.0f}s")

    # PHASE 2: measure each created variant
    for n in threads_list:
        if n not in created:
            continue
        name = created[n]
        # warm
        try:
            embed_batch(["warmup"])
        except (urllib.error.URLError, OSError, ValueError) as exc:
            log(f"  x threads={n}: warmup failed: {exc}")
            results.append({"threads": n, "ok": False, "error": str(exc)})
            continue
        # Verify the runner really got -t n. The runner binds a RANDOM port, so
        # the embed server's port never appears in its argv; identify the runner
        # by parent PID instead. Matching on the port string silently found
        # nothing and would have marked every config UNVERIFIED.
        flag = None
        for pid, ppid, args in _processes():
            if "llama-server" in args and ppid == self_pid:
                m = re.search(r"(?:^|\s)-t\s+(\d+)(?:\s|$)", args)
                if m:
                    flag = int(m.group(1))
                break
        samples = []
        for b in range(batches):
            texts = [f"Node 1 benchmark sentence number {b}-{i}: the quick brown fox "
                     f"jumps over the lazy dog while inference proceeds." for i in range(batch_size)]
            try:
                r = embed_batch(texts)
                samples.append(r)
            except (urllib.error.URLError, OSError, ValueError) as exc:
                log(f"    batch {b} failed: {exc}")
        if not samples:
            results.append({"threads": n, "ok": False, "error": "no samples"})
            continue
        tps = [s["texts_per_s"] for s in samples]
        mean_tps = sum(tps) / len(tps)
        results.append({
            "threads": n, "ok": True, "runner_flag": flag,
            "flag_verified": flag == n,
            "dim": samples[0]["dim"],
            "batch_size": batch_size, "batches": batches,
            "texts_per_s_mean": round(mean_tps, 2),
            "texts_per_s_best": round(max(tps), 2),
            "latency_ms_mean": round(1000 * sum(s["elapsed_s"] for s in samples) / len(samples), 1),
        })
        log(f"  threads={n:<2} runner -t={flag} "
            f"{'VERIFIED' if flag == n else 'UNVERIFIED'}  "
            f"dim={samples[0]['dim']}  {mean_tps:.2f} texts/s  "
            f"latency {results[-1]['latency_ms_mean']}ms")
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["install", "status", "uninstall", "embed"])
    ap.add_argument("--threads", default="1,2,3,4",
                    help="for install: OMP_NUM_THREADS; for embed: sweep list")
    ap.add_argument("--batches", type=int, default=10)
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--ecores", default=ECORE_CPUS)
    ap.add_argument("--out", default="bench_embed_report.json")
    args = ap.parse_args()

    if args.action == "install":
        return install(int(args.threads.split(",")[0]), args.ecores)
    if args.action == "status":
        return status()
    if args.action == "uninstall":
        return uninstall()

    log("E-core embedding sweep (qwen3-embedding:0.6b on CPUs 12-15)")
    log("─" * 70)
    ok = status() == 0   # status() returns 0 when healthy (systemd convention)
    if not ok:
        log("x embed instance is not up; run: python3 scripts/embed_service.py install")
        return 1
    results = sweep([int(t) for t in args.threads.split(",") if t.strip()],
                    args.batches, args.batch_size)
    valid = [r for r in results if r.get("ok")]
    if valid:
        best = max(valid, key=lambda r: r["texts_per_s_mean"])
        log("")
        log(f"  peak: {best['texts_per_s_mean']} texts/s at {best['threads']} threads")
        unverified = [r for r in valid if not r.get("flag_verified")]
        if unverified:
            log(f"  WARNING: {len(unverified)} config(s) had unverified runner flags "
                f"and should not be trusted")
    Path(args.out).write_text(json.dumps({"results": results}, indent=2))
    log(f"\n  report written: {args.out}")
    return 0 if valid else 1


if __name__ == "__main__":
    sys.exit(main())
