#!/usr/bin/env python3
"""Self-validating Ollama thread-count benchmark for Node 1.

DESIGN PRINCIPLE
----------------
This script must be able to DETECT ITS OWN FAILURE. It never reports a number
it cannot verify. A benchmark that silently measures the wrong configuration is
worse than no benchmark, because it produces authoritative-looking numbers that
are fiction. (This module exists because the previous sweep did exactly that:
`OLLAMA_NUM_THREADS` is not a real Ollama setting, so six "different"
configurations were actually the same configuration, and jitter was crowned an
optimum. See .env.ollama and ollama#10476.)

EVERY MEASUREMENT IS GATED ON PROOF
-----------------------------------
For each configuration the harness:
  1. creates a model variant whose Modelfile pins `PARAMETER num_thread N`;
  2. loads it, which spawns the inference runner subprocess;
  3. PARSES THE RUNNER COMMAND LINE and asserts `-t N` is present and equals N
     (this is the ground truth of what the inference engine was told);
  4. counts inference threads that have actually burned CPU time;
  5. samples RAPL package power, per-core frequency, temperature, and the
     kernel's thermal/power throttle counters;
  6. runs REPEATS identical fixed-length generations, streaming, so TTFT and
     inter-token latency are measured directly rather than inferred;
  7. ABORTS that configuration — loudly, to stderr, and excludes it from the
     report — if any gate fails.

Also enforced:
  * identical output length per repetition (`num_predict`), because tokens/sec
    is meaningless when runs generate different token counts (the old harness
    compared runs of 20 and 554 tokens);
  * discarded warmup runs;
  * a cooldown between configurations so thermals from one config do not bias
    the next;
  * mean +/- 95% confidence interval per configuration, plus a significance
    test of the winner against the runner-up, so a 1% "win" cannot be reported
    as an optimum;
  * full environment capture (versions, power limits, memory channels, affinity)
    so a result can be re-checked later.

CONTEXT BOUNDARY (IETF draft-gaikwad-llm-benchmarking-profiles §2): all
measurements are taken at the Ollama HTTP API boundary, client and server on the
same host sharing one clock. No gateway, no container, no network.

Usage:
    python3 scripts/bench_threads.py --threads 1,2,3,4,5,6,8,10,12 --repeats 3
    python3 scripts/bench_threads.py --quick
"""

import argparse
import json
import os
import re
import statistics
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

DEFAULT_HOST = "http://localhost:11434"
DEFAULT_MODEL = "phi4-mini"
VARIANT_PREFIX = "bench-t"
# Raw-completion prefix: forces continuation rather than chat, so `num_predict`
# is honoured and token counts are identical across runs.
RAW_PREFIX = "The following is a numbered list of the first two hundred positive integers, one per line, starting at 1:\n1."
FIXED_PREDICT = 128
WARMUP_RUNS = 1
MAX_VALID_CV_PCT = 6.0  # coefficient of variation ceiling for a usable config

# Plausibility floors, calibrated from the one CLEAN run in the 2026-09-26 sweep
# (config 1: 23.6 W, 4225 MHz, 77 C) and from earlier real-load measurements
# (27-34 W, 71-78 C, 2800-3100 MHz). The contaminated run drew 13.2-14.4 W at
# 900-1534 MHz and the previous harness called it clean. These floors make that
# failure mode impossible to miss again. They are deliberately generous: the
# point is to catch a machine in a different power state, not to fine-tune a
# measurement.
MIN_PLAUSIBLE_WATTS = 20.0
MIN_PLAUSIBLE_MHZ = 2000
FOREIGN_CPU_PCT_CEILING = 15.0  # non-benchmark CPU that would contaminate a run
CLOCKS_PER_SEC = 1_000_000_000


def log(msg: str) -> None:
    """Line-buffered + flushed: progress must be visible while it happens."""
    print(msg, flush=True)


def phase(msg: str) -> None:
    """Visually distinct phase banner so a watching operator can tell where it is."""
    bar = "=" * 74
    print(f"\n{bar}\n  {msg}\n{bar}", flush=True)


# --------------------------------------------------------------------------
# environment probes
# --------------------------------------------------------------------------

def _read(path: str) -> Optional[str]:
    try:
        with open(path) as handle:
            return handle.read().strip()
    except OSError:
        return None


def _run(cmd: list) -> str:
    try:
        out = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30, check=False
        )
        return out.stdout
    except (subprocess.SubprocessError, OSError):
        return ""


@dataclass
class Environment:
    """Everything needed to re-check a result later (IETF MUST-disclose)."""

    ollama_version: str = ""
    ollama_api_version: str = ""
    model: str = ""
    nproc_logical: int = 0
    nproc_physical_total: int = 0
    nproc_physical_p: int = 0
    nproc_e_cores: int = 0
    allowed_cpus: str = ""
    power_profile: str = ""
    epp: str = ""
    ac_online: Optional[bool] = None
    battery_pct: Optional[str] = None
    pl1_w: Optional[float] = None
    pl2_w: Optional[float] = None
    domain_max_w: Optional[float] = None
    dimm_layout: str = ""
    mem_type: str = ""
    mem_configured_mt_s: str = ""
    mem_theoretical_gb_s: Optional[float] = None
    cpu_model: str = ""

    @classmethod
    def capture(cls, model: str) -> "Environment":
        rapl = "/sys/class/powercap/intel-rapl:0"

        def watts(name: str) -> Optional[float]:
            raw = _read(f"{rapl}/{name}")
            if raw and raw.lstrip("-").isdigit():
                return int(raw) / 1_000_000.0
            return None

        dimms: list = []
        mem_type = mem_speed = ""
        dmidecode = _run(["sudo", "-n", "dmidecode", "-t", "memory"])
        if dmidecode:
            locator = re.search(r"Locator: (\S+)", dmidecode)
            size = re.search(r"Size: (\d+ GB)", dmidecode)
            if locator and size:
                dimms.append(f"{locator.group(1)}={size.group(1)}")
            empty = "No Module Installed" in dmidecode
            if empty:
                dimms.append("slot2=EMPTY")
            mt = re.search(r"Configured Memory Speed: (\d+)", dmidecode)
            mem_speed = f"{mt.group(1)} MT/s" if mt else ""
            ty = re.search(r"Type: (DDR\d\S*)", dmidecode)
            mem_type = ty.group(1) if ty else ""

        # single-channel DDR5 at 5200 MT/s => 8 B/cycle * 5200e6 = 41.6 GB/s
        theo = None
        if mem_speed:
            mt_s = int(re.sub(r"\D", "", mem_speed) or 0)
            channels = 1 if "EMPTY" in " ".join(dimms) else 2
            theo = round(mt_s * 8 * channels / 1000, 1)

        cpu_model = ""
        cpuinfo = _read("/proc/cpuinfo") or ""
        m = re.search(r"model name\s*:\s*(.+)", cpuinfo)
        if m:
            cpu_model = m.group(1).strip()

        return cls(
            ollama_version=_run(["ollama", "--version"]).strip(),
            ollama_api_version=_api_version(),
            model=model,
            nproc_logical=os.cpu_count() or 0,
            nproc_physical_total=_count_all_cores(),
            nproc_physical_p=_count_p_cores(),
            nproc_e_cores=_count_e_cores(),
            allowed_cpus=_run(
                ["systemctl", "show", "ollama", "--property=AllowedCPUs", "--no-pager"]
            ).split("=", 1)[-1].strip(),
            power_profile=power_profile(),
            epp=epp_now(),
            ac_online=power_supply_state()["ac_online"],
            battery_pct=power_supply_state()["battery_pct"],
            pl1_w=watts("constraint_0_power_limit_uw"),
            pl2_w=watts("constraint_1_power_limit_uw"),
            domain_max_w=watts("constraint_0_max_power_uw"),
            dimm_layout=", ".join(dimms),
            mem_type=mem_type,
            mem_configured_mt_s=mem_speed,
            mem_theoretical_gb_s=theo,
            cpu_model=cpu_model,
        )


def _api_version() -> str:
    try:
        with urllib.request.urlopen(f"{DEFAULT_HOST}/api/version", timeout=5) as resp:
            return json.loads(resp.read()).get("version", "")
    except (urllib.error.URLError, OSError, ValueError, json.JSONDecodeError):
        return ""


def _count_p_cores() -> int:
    """Count PHYSICAL P-cores from core_id deduplication.

    BUG THIS REPLACES: the previous implementation read
    /sys/devices/system/cpu/cpuN/topology/thread_siblings_list and compared
    ``split(",")[0] == str(cpu)``. On this kernel that file returns a RANGE
    ("0-1"), not a comma list, so the comparison never matched a P-core and
    instead matched the four E-cores (whose siblings are a bare single number,
    e.g. "12"). It therefore reported 4 P-cores on a 6-P-core part. The
    environmental record was wrong. core_id is the authoritative topology key.
    """
    # P-cores are the physical cores that have a hyperthread sibling, i.e. whose
    # thread_siblings_list spans a RANGE ("0-1"). E-cores have a single logical
    # CPU (siblings is a bare number, "12"). Deduplicating core_id across all
    # logical CPUs yields 10 on this part (6 P + 4 E) and is NOT the P-core count.
    count = 0
    seen = set()
    for cpu in range(os.cpu_count() or 0):
        cid = _read(f"/sys/devices/system/cpu/cpu{cpu}/topology/core_id")
        sib = _read(f"/sys/devices/system/cpu/cpu{cpu}/topology/thread_siblings_list")
        if not (cid and cid.isdigit() and sib):
            continue
        if "-" in sib and int(cid) not in seen:   # range => has an HT sibling
            seen.add(int(cid))
            count += 1
    return count


def _count_all_cores() -> int:
    """Total distinct physical cores (P + E) via core_id dedup."""
    ids = set()
    for cpu in range(os.cpu_count() or 0):
        cid = _read(f"/sys/devices/system/cpu/cpu{cpu}/topology/core_id")
        if cid and cid.isdigit():
            ids.add(int(cid))
    return len(ids)


def _count_e_cores() -> int:
    """E-cores are logical CPUs with no HT sibling (siblings == self)."""
    count = 0
    for cpu in range(os.cpu_count() or 0):
        sib = _read(f"/sys/devices/system/cpu/cpu{cpu}/topology/thread_siblings_list")
        if sib and sib.replace("-", ",").split(",")[0] == str(cpu) and "-" not in sib:
            count += 1
    return count


def power_supply_state() -> dict:
    """AC/battery state. A benchmark on battery is a contaminated benchmark."""
    ac_online = None
    for path in sorted(Path("/sys/class/power_supply").glob("AC*/online")):
        val = _read(str(path))
        if val is not None:
            ac_online = val == "1"
            break
    capacity = status = None
    for path in sorted(Path("/sys/class/power_supply").glob("BAT*/capacity")):
        capacity = _read(str(path))
        status = _read(str(path.parent / "status"))
        break
    return {"ac_online": ac_online, "battery_pct": capacity, "battery_status": status}


def memory_state() -> dict:
    """RAM/swap/zRAM state. A benchmark run under memory pressure is invalid:
    zram is compressed swap INSIDE ram, and zstd compression burns cpu."""
    info = {}
    try:
        for line in open("/proc/meminfo"):
            k, _, v = line.partition(":")
            info[k.strip()] = int(v.split()[0]) * 1024
    except OSError:
        return {"error": "cannot read /proc/meminfo"}
    total = info.get("MemTotal", 0)
    avail = info.get("MemAvailable", 0)
    swap_total = info.get("SwapTotal", 0)
    swap_free = info.get("SwapFree", 0)
    zram_used = zram_total = 0
    for path, label in (("/sys/block/zram0/mem_used_total", "used"),
                        ("/sys/block/zram0/orig_data_size", "orig")):
        raw = _read(path)
        if raw and raw.isdigit():
            val = int(raw)
            if label == "used":
                zram_used = val
            else:
                zram_total = val
    return {
        "mem_total_gb": round(total / 1e9, 2),
        "mem_available_gb": round(avail / 1e9, 2),
        "mem_used_pct": round((total - avail) / total * 100, 1) if total else 0,
        "swap_total_gb": round(swap_total / 1e9, 2),
        "swap_used_gb": round((swap_total - swap_free) / 1e9, 2),
        "zram_used_gb": round(zram_used / 1e9, 2),
        "zram_orig_gb": round(zram_total / 1e9, 2),
        "zram_pct": round(zram_used / zram_total * 100, 1) if zram_total else 0.0,
    }


def swap_io_rate() -> float:
    """Pages/sec of swap-in + swap-out from /proc/vmstat (0 = no thrashing)."""
    try:
        for line in open("/proc/vmstat"):
            if line.startswith("pswpin ") or line.startswith("pswpout "):
                pass
        pswpin = pswpout = 0
        for line in open("/proc/vmstat"):
            k, _, v = line.partition(" ")
            if k == "pswpin":
                pswpin = int(v)
            elif k == "pswpout":
                pswpout = int(v)
        return float(pswpin + pswpout)
    except (OSError, ValueError):
        return 0.0


def power_profile() -> str:
    return _run(["powerprofilesctl", "get"]).strip()


def epp_now() -> str:
    """Energy Performance Preference — the real intel_pstate control knob."""
    for cpu in (0, 1):
        val = _read(f"/sys/devices/system/cpu/cpu{cpu}/cpufreq/energy_performance_preference")
        if val:
            return val
    return ""


# --------------------------------------------------------------------------
# the instrument that makes this honest
# --------------------------------------------------------------------------

def _llm_runners() -> list:
    """All non-embedding llama-server runner processes, read straight from /proc.

    WHY NOT `ps`: `ps` truncates long argv, and ollama places `-t N` at the
    very END of the runner command line, so the flag was being cut off and the
    harness concluded (falsely) that num_thread was unsupported. Reading
    /proc/<pid>/cmdline has no length limit. This exact bug caused a wrong
    "num_thread is not supported on this ollama version" conclusion.
    """
    out = []
    try:
        entries = list(Path("/proc").iterdir())
    except OSError:
        return out
    for entry in entries:
        if not entry.name.isdigit():
            continue
        try:
            cmdline = (entry / "cmdline").read_bytes().decode(
                errors="replace").replace("\0", " ")
        except OSError:
            continue
        if "llama-server" not in cmdline:
            continue
        if "--embedding" in cmdline:
            continue  # background embedder, not the LLM under test
        out.append((int(entry.name), cmdline))
    return out


def runner_cmdline() -> Optional[str]:
    """The inference runner's actual command line — ground truth, untruncated."""
    runners = _llm_runners()
    return runners[0][1] if runners else None


def runner_thread_flag() -> Optional[int]:
    """Parse `-t N` from the runner command line (untruncated, via /proc)."""
    for _pid, cmdline in _llm_runners():
        match = re.search(r"(?:^|\s)-t\s+(\d+)(?:\s|$)", cmdline)
        if match:
            return int(match.group(1))
    return None


def count_burned_threads(pid: Optional[int] = None) -> tuple:
    """(total OS threads, threads that have actually consumed CPU)."""
    import glob

    if pid is None:
        pids = _run(["pgrep", "-x", "ollama"]).split()
        pid = int(pids[0]) if pids else None
    if pid is None:
        return (0, 0)
    total = active = 0
    for stat_path in glob.glob(f"/proc/{pid}/task/*/stat"):
        try:
            with open(stat_path) as handle:
                fields = handle.read().split()
            total += 1
            if int(fields[13]) + int(fields[14]) > 0:
                active += 1
        except (OSError, ValueError, IndexError):
            continue
    return (total, active)


@dataclass
class Sampler:
    """RAPL power, frequency, temperature, throttle counters."""

    rapl_energy: str = "/sys/class/powercap/intel-rapl:0/energy_uj"
    zone: str = "/sys/class/thermal/thermal_zone3"
    throttle_dir: str = "/sys/devices/system/cpu/cpu0/thermal_throttle"

    def energy_uj(self) -> int:
        raw = _read(self.rapl_energy)
        return int(raw) if raw and raw.isdigit() else 0

    def max_freq_mhz(self) -> int:
        vals = []
        for line in (_read("/proc/cpuinfo") or "").splitlines():
            if "cpu MHz" in line:
                try:
                    vals.append(float(line.split(":")[1]))
                except ValueError:
                    continue
        return int(max(vals)) if vals else 0

    def temp_c(self) -> int:
        raw = _read(f"{self.zone}/temp")
        return int(raw) // 1000 if raw and raw.lstrip("-").isdigit() else -1

    def throttles(self) -> tuple:
        pkg = _read(f"{self.throttle_dir}/package_throttle_count")
        core = _read(f"{self.throttle_dir}/core_throttle_count")
        return (
            int(pkg) if pkg and pkg.isdigit() else 0,
            int(core) if core and core.isdigit() else 0,
        )


class LiveTelemetry:
    """Samples power, clock, profile and AC state WHILE a request is in flight.

    WHY THIS EXISTS (hard-won, 2026-09-26): an earlier version sampled package
    power only by differencing the RAPL energy counter across the request, and
    read frequency only AFTER completion. During a real failure — the operator's
    laptop switched from `performance` to `power-saver` at 9% battery mid-sweep —
    that harness reported "zero throttle events" and a clean PASS for every
    configuration, because:
      * `package_throttle_count` only counts RAPL and thermal-violation events,
        NOT a governor/profile change, so the switch was invisible to it; and
      * power/frequency were not sampled during the window, so the 13 W /
        1000 MHz collapse was averaged into the result instead of flagging it.
    A benchmark that cannot detect the machine changing state underneath it is
    an unreliable benchmark. This class samples continuously and records the
    profile it observed, so a mid-run power event is caught, timestamped, and
    attributed to a specific configuration.
    """

    def __init__(self, interval: float = 0.5) -> None:
        self.interval = interval
        self.sampler = Sampler()
        self._stop = None
        self._thread = None
        self.samples: list = []
        self.profile_switches: list = []

    def _poll(self) -> None:
        last_profile = power_profile()
        while self._stop is None or not self._stop.is_set():
            ts = time.time()
            prof = power_profile()
            if prof != last_profile:
                self.profile_switches.append(
                    {"ts": ts, "from": last_profile, "to": prof})
                last_profile = prof
            self.samples.append({
                "ts": ts,
                "profile": prof,
                "epp": epp_now(),
                "max_mhz": self.sampler.max_freq_mhz(),
                "temp_c": self.sampler.temp_c(),
                "energy_uj": self.sampler.energy_uj(),
            })
            time.sleep(self.interval)

    def __enter__(self) -> "LiveTelemetry":
        import threading

        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._poll, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *_exc) -> None:
        import threading

        self._stop.set()
        if self._thread:
            self._thread.join(timeout=3)

    def summary(self) -> dict:
        """Aggregate the live samples into a verdict-bearing record."""
        if not self.samples:
            return {"n_samples": 0}
        freqs = [s["max_mhz"] for s in self.samples if s["max_mhz"]]
        # per-sample power so fluctuation is visible, not just the mean
        pwr = []
        for prev, cur in zip(self.samples, self.samples[1:]):
            de = cur["energy_uj"] - prev["energy_uj"]
            dt = cur["ts"] - prev["ts"]
            if dt > 0 and de >= 0:
                pwr.append(de / 1e6 / dt)
        profiles = sorted({s["profile"] for s in self.samples if s["profile"]})
        first, last = self.samples[0], self.samples[-1]
        energy = last["energy_uj"] - first["energy_uj"]
        elapsed = last["ts"] - first["ts"]
        return {
            "n_samples": len(self.samples),
            "profiles_observed": profiles,
            "profile_switches": self.profile_switches,
            "epp_observed": sorted({s["epp"] for s in self.samples if s["epp"]}),
            "max_mhz_peak": max(freqs) if freqs else 0,
            "max_mhz_median": int(statistics.median(freqs)) if freqs else 0,
            "temp_c_max": max(s["temp_c"] for s in self.samples if s["temp_c"] >= 0)
            if any(s["temp_c"] >= 0 for s in self.samples) else -1,
            "watts_mean": round(energy / 1e6 / elapsed, 2) if elapsed > 0 and energy > 0 else 0.0,
            "watts_min": round(min(pwr), 2) if pwr else 0.0,
            "watts_max": round(max(pwr), 2) if pwr else 0.0,
            "watts_range": round(max(pwr) - min(pwr), 2) if pwr else 0.0,
            "watts_stdev": round(statistics.stdev(pwr), 2) if len(pwr) > 1 else 0.0,
            "duration_s": round(elapsed, 2),
            "t_first": first["ts"],
            "t_last": last["ts"],
        }


# --------------------------------------------------------------------------
# Ollama interaction
# --------------------------------------------------------------------------

def api_post(path: str, payload: dict, timeout: int = 300) -> dict:
    req = urllib.request.Request(
        f"{DEFAULT_HOST}{path}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def ensure_variant(base_model: str, threads: int) -> str:
    """Create (idempotently) a model variant pinned to `threads` via Modelfile.

    `base_model` may be a registry name (phi4-mini) OR an absolute path to a
    .gguf file, in which case the Modelfile uses `FROM <path>` -- the form
    ollama accepts for importing a local GGUF.
    """
    if base_model.endswith(".gguf"):
        slug = re.sub(r"[^A-Za-z0-9]+", "-", Path(base_model).stem)[:28].strip("-").lower()
        name = f"{VARIANT_PREFIX}{slug}-{threads}"
    else:
        slug = re.sub(r"[^A-Za-z0-9]+", "-", base_model)[:28].strip("-").lower()
        name = f"{VARIANT_PREFIX}{slug}-{threads}"
    path = f"/tmp/{name}.Modelfile"
    with open(path, "w") as handle:
        handle.write(f"FROM {base_model}\nPARAMETER num_thread {threads}\n")
    _run(["ollama", "rm", "-f", name])
    out = subprocess.run(
        ["ollama", "create", name, "-f", path],
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    if out.returncode != 0:
        raise RuntimeError(f"ollama create {name} failed: {out.stderr.strip()}")
    return name


def generate_streaming(model: str, predict: int) -> dict:
    """One streaming generation; returns TTFT, ITL stats, token count.

    Streaming is required to measure TTFT and inter-token latency directly
    (IETF draft-gaikwad-llm-benchmarking-profiles §4.1.5). Non-streaming
    responses only give aggregate durations.
    """
    payload = {
        "model": model,
        "prompt": RAW_PREFIX,
        "stream": True,
        "raw": True,
        "options": {"num_predict": predict, "temperature": 0},
    }
    req = urllib.request.Request(
        f"{DEFAULT_HOST}/api/generate",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    t_start = time.perf_counter()
    ttft = None
    token_times: list = []
    eval_count = 0
    with urllib.request.urlopen(req, timeout=300) as resp:
        for raw_line in resp:
            line = raw_line.strip()
            if not line:
                continue
            try:
                chunk = json.loads(line)
            except json.JSONDecodeError:
                continue
            if chunk.get("done"):
                eval_count = chunk.get("eval_count", eval_count)
                break
            now = time.perf_counter()
            if ttft is None:
                ttft = now - t_start
            else:
                token_times.append(now)
    if ttft is None:
        raise RuntimeError("no tokens streamed")
    its = [b - a for a, b in zip(token_times, token_times[1:])]
    return {
        "ttft_s": ttft,
        "n_tokens": eval_count or len(token_times) + 1,
        "itl_mean_s": statistics.fmean(its) if its else 0.0,
        "itl_p50_s": statistics.median(its) if its else 0.0,
        "decode_s": (token_times[-1] - token_times[0]) if len(token_times) > 1 else 0.0,
    }


def preflight(expected_profile: str, require_ac: bool) -> tuple:
    """Refuse to benchmark on unstable conditions. Returns (ok, reason, facts).

    A contaminated benchmark is worse than no benchmark: it produces
    authoritative-looking numbers that are fiction. Every precondition that
    could silently change the machine mid-run is checked BEFORE any measurement
    and re-checked at the start of every configuration.

    The AC-power gate exists because of a real failure on 2026-09-26: the laptop
    was at 9% battery on DC power, GNOME switched the profile to power-saver
    partway through the sweep, package power fell from ~24 W to ~13 W and clocks
    from ~4200 MHz to ~1000 MHz, and the previous harness reported every single
    configuration as a clean pass with "zero throttle events" -- because
    package_throttle_count only counts RAPL and thermal-violation events, and a
    governor change is neither.
    """
    facts = {
        "ac": power_supply_state(),
        "power_profile": power_profile(),
        "epp": epp_now(),
        "expected_profile": expected_profile,
        "ts": time.time(),
    }
    problems = []
    if require_ac and facts["ac"]["ac_online"] is not True:
        problems.append(
            f"NOT ON AC POWER (ac_online={facts['ac']['ac_online']}, "
            f"battery={facts['ac']['battery_pct']}% "
            f"{facts['ac']['battery_status']}); on battery the OS downclocks and "
            f"switches profile mid-run, invalidating every measurement")
    if facts["power_profile"] and facts["power_profile"] != expected_profile:
        problems.append(f"power profile is '{facts['power_profile']}', expected "
                        f"'{expected_profile}'")
    if facts["epp"] and facts["epp"] != "performance":
        problems.append(f"EPP is '{facts['epp']}', expected 'performance'")
    mem = memory_state()
    facts["memory"] = mem
    # zRAM gate REMOVED per operator instruction (2026-09-26): 
    # "Get rid of the zRAM gate. We do not have anywhere near enough data 
    # to make a call like that yet... The new gate will NOT refuse to run 
    # with zRAM ever because you will remove the gate."
    # Logging zRAM state for visibility, not gating:
    if mem.get("zram_pct", 0) > 25.0:
        log(f"  ! zram at {mem['zram_pct']}% ({mem['zram_used_gb']}GB of {mem['zram_orig_gb']}GB) "
            f"— high but proceeding per operator directive")
    if mem.get("swap_used_gb", 0) > 0.5:
        log(f"  ! swap used: {mem['swap_used_gb']}GB — proceeding anyway")
    if mem.get("mem_available_gb", 99) < 3.0:
        log(f"  ! low available RAM: {mem.get('mem_available_gb')}GB — proceeding anyway")
    foreign = foreign_cpu_pct()
    facts["foreign_cpu_pct"] = foreign
    if foreign is not None and foreign > FOREIGN_CPU_PCT_CEILING:
        problems.append(
            f"non-benchmark processes using {foreign:.0f}% CPU "
            f"(ceiling {FOREIGN_CPU_PCT_CEILING:.0f}%); results would be contaminated")
    return (not problems, "; ".join(problems), facts)


def foreign_cpu_pct(sample_s: float = 0.7) -> Optional[float]:
    """CPU% consumed by processes OTHER than ollama and this benchmark.

    REPLACES a load-average check that was self-defeating: loadavg is a
    one-minute decaying average, so the benchmark's own previous configuration
    kept it above any sane threshold and every subsequent configuration was
    rejected as "other work running" -- the harness detecting itself. This
    samples instantaneous CPU time from /proc for foreign PIDs instead.
    """
    mine = {os.getpid(), os.getppid()}
    try:
        import glob
        pids = [int(Path(p).name) for p in glob.glob("/proc/[0-9]*")]
    except (OSError, ValueError):
        return None
    deltas = []
    for pid in pids:
        if pid in mine:
            continue
        try:
            with open(f"/proc/{pid}/stat") as handle:
                fields = handle.read().rsplit(")", 1)[1].split()
            comm_ok = True
            ticks = int(fields[11]) + int(fields[12])
            with open(f"/proc/{pid}/comm") as handle:
                comm = handle.read().strip()
            if comm in ("ollama", "llama-server", "python3", "python",
                        "bash", "ollama_llama_server"):
                comm_ok = False
            if not comm_ok:
                continue
            deltas.append((pid, ticks))
        except (OSError, ValueError, IndexError):
            continue
    if not deltas:
        return 0.0
    time.sleep(sample_s)
    hz = os.sysconf("SC_CLK_TCK")
    total = 0.0
    for pid, before in deltas:
        try:
            with open(f"/proc/{pid}/stat") as handle:
                fields = handle.read().rsplit(")", 1)[1].split()
            after = int(fields[11]) + int(fields[12])
            if after > before:
                total += (after - before) / hz
        except (OSError, ValueError, IndexError):
            continue
    ncpu = os.cpu_count() or 1
    return round(total / sample_s / ncpu * 100, 1)


# --------------------------------------------------------------------------
# per-configuration measurement
# --------------------------------------------------------------------------

@dataclass
class ConfigResult:
    threads: int
    ok: bool = False
    failure: str = ""
    runner_flag: Optional[int] = None
    burned_threads: int = 0
    total_threads: int = 0
    token_counts: list = field(default_factory=list)
    tps_samples: list = field(default_factory=list)
    ttft_samples: list = field(default_factory=list)
    itl_samples: list = field(default_factory=list)
    power_w: list = field(default_factory=list)
    temp_c: list = field(default_factory=list)
    peak_mhz: list = field(default_factory=list)
    throttle_delta: int = 0
    core_throttle_delta: int = 0
    contamination: list = field(default_factory=list)
    reps: list = field(default_factory=list)
    preflight: dict = field(default_factory=dict)
    thermally_limited: bool = False
    embed_rate: float = 0.0
    embed_batches: int = 0
    embed_errors: int = 0


def measure(base_model: str, threads: int, repeats: int, predict: int,
            cooldown: int, expected_profile: str,
            embed: Optional[tuple] = None) -> ConfigResult:
    """embed: optional (host, model) to drive concurrent background embeddings."""
    res = ConfigResult(threads=threads)
    log(f"\n-- config: num_thread={threads} " + "-" * 38)

    # ---- GATE 0: refuse to measure on an unstable machine ----
    ok, reason, pf = preflight(expected_profile, require_ac=True)
    res.preflight = pf
    if not ok:
        res.failure = f"PREFLIGHT: {reason}"
        log(f"   x {res.failure}")
        return res
    log(f"   + preflight OK: AC={pf['ac']['ac_online']} "
        f"batt={pf['ac']['battery_pct']}% profile={pf['power_profile']} epp={pf['epp']}")

    try:
        model = ensure_variant(base_model, threads)
    except RuntimeError as exc:
        res.failure = f"variant creation failed: {exc}"
        return res

    try:
        api_post("/api/generate",
                 {"model": model, "prompt": "hi", "stream": False,
                  "options": {"num_predict": 1}})
    except (urllib.error.URLError, OSError, ValueError) as exc:
        res.failure = f"model load failed: {exc}"
        log(f"   x {res.failure}")
        return res

    # ---- GATE 1 (HARD): the engine must have been told the right thread count ----
    # This was briefly downgraded to a warning on the false belief that
    # num_thread was unsupported. That belief came from `ps` truncating ollama's
    # argv and cutting off the trailing `-t N`. It is a HARD gate again: an
    # unverified thread count invalidates the whole measurement.
    flag = None
    for attempt in range(20):
        flag = runner_thread_flag()
        if flag is not None:
            break
        time.sleep(0.5)
    res.runner_flag = flag
    if flag is None:
        res.failure = ("GATE: no `-t` flag found on any llama-server runner. "
                       "Thread count cannot be verified, so this configuration "
                       "would be measuring an unknown setup.")
        log(f"   x {res.failure}")
        return res
    if flag != threads:
        res.failure = f"GATE: requested {threads} but runner reports -t {flag}"
        log(f"   x {res.failure}")
        return res
    res.thread_verified = True
    log(f"   + runner verified via /proc: -t {flag}")
    res.total_threads, res.burned_threads = count_burned_threads()
    log(f"   + threads with CPU time burned: {res.burned_threads}/{res.total_threads}")

    if cooldown:
        log(f"   ... cooling down {cooldown}s")
        time.sleep(cooldown)

    sampler = Sampler()
    embed_ctx = None
    if embed:
        embed_ctx = EmbedLoad(embed[0], embed[1])
        log(f"   … starting concurrent embedding load on {embed[0]}")
        embed_ctx.__enter__()
    for rep in range(repeats + WARMUP_RUNS):
        pkg0, core0 = sampler.throttles()
        try:
            with LiveTelemetry() as tele:
                r = generate_streaming(model, predict)
        except (urllib.error.URLError, OSError, ValueError, RuntimeError) as exc:
            res.failure = f"generation failed on rep {rep}: {exc}"
            log(f"   x {res.failure}")
            return res
        tel = tele.summary()
        pkg1, core1 = sampler.throttles()
        res.throttle_delta += max(0, pkg1 - pkg0)
        res.core_throttle_delta += max(0, core1 - core0)

        # ---- GATE 2 (per rep): machine state must not have changed ----
        anomalies = []
        if tel.get("profile_switches"):
            anomalies.append(f"profile switched mid-rep {tel['profile_switches']}")
        profiles = tel.get("profiles_observed") or []
        if profiles and expected_profile not in profiles:
            anomalies.append(f"observed profile {profiles}, expected {expected_profile}")
        if tel.get("watts_mean") and tel["watts_mean"] < MIN_PLAUSIBLE_WATTS:
            anomalies.append(f"package {tel['watts_mean']}W < {MIN_PLAUSIBLE_WATTS}W floor"
                             f" (machine downclocked)")
        if tel.get("max_mhz_peak") and tel["max_mhz_peak"] < MIN_PLAUSIBLE_MHZ:
            anomalies.append(f"peak {tel['max_mhz_peak']}MHz < {MIN_PLAUSIBLE_MHZ}MHz floor"
                             f" (not at turbo)")
        res.reps.append({"rep": rep, "warmup": rep < WARMUP_RUNS, "telemetry": tel,
                         "anomalies": anomalies, "tokens": r["n_tokens"],
                         "ttft_s": r["ttft_s"], "itl_s": r["itl_mean_s"]})
        if anomalies:
            res.contamination.extend(anomalies)
            log(f"   rep{rep}: x CONTAMINATED -- " + " | ".join(anomalies))
            continue
        if rep >= WARMUP_RUNS:
            res.token_counts.append(r["n_tokens"])
            res.ttft_samples.append(r["ttft_s"])
            res.itl_samples.append(r["itl_mean_s"])
            res.power_w.append(tel.get("watts_mean", 0.0))
            res.temp_c.append(tel.get("temp_c_max", -1))
            res.peak_mhz.append(tel.get("max_mhz_peak", 0))
            if r["decode_s"] > 0:
                res.tps_samples.append((r["n_tokens"] - 1) / r["decode_s"])
            log(f"   rep{rep}: {r['n_tokens']:3d} tok  "
                f"{res.tps_samples[-1] if res.tps_samples else 0:5.2f} t/s  "
                f"ttft {r['ttft_s']*1000:6.0f}ms  itl {r['itl_mean_s']*1000:5.1f}ms  "
                f"{tel.get('watts_mean',0):5.1f}W"
                f"[{tel.get('watts_min',0):.0f}-{tel.get('watts_max',0):.0f}]  "
                f"{tel.get('temp_c_max',-1)}C  "
                f"{tel.get('max_mhz_peak',0)}MHz  [{','.join(profiles)}]")

    # ---- GATE 3: no contamination anywhere in this configuration ----
    if res.contamination:
        res.failure = "GATE: run contaminated -- " + "; ".join(res.contamination[:3])
        log(f"   x {res.failure}")
        return res
    # ---- GATE 4: identical output length, else tok/s is incomparable ----
    uniq = set(res.token_counts)
    if len(uniq) > 1:
        res.failure = f"GATE: token counts varied {sorted(uniq)}; tok/s incomparable"
        log(f"   x {res.failure}")
        return res
    log(f"   + token count identical across reps: {uniq}")
    if embed_ctx is not None:
        res.embed_rate = round(embed_ctx.rate(), 2)
        res.embed_batches = embed_ctx.batches_done
        res.embed_errors = embed_ctx.errors
        embed_ctx.__exit__()
        log(f"   .. background embedding load: {res.embed_rate} texts/s "
            f"over {res.embed_batches} batches ({res.embed_errors} errors)")

    # ---- CONDITION (recorded, not fatal): kernel throttle events ----
    # NOT a gate, deliberately. On AC at the performance profile this laptop
    # sustains ~50 W and reaches ~96 C against a 100 C tJMax, so thermal
    # throttling is the NORMAL STEADY STATE, not an anomaly. A hard gate here
    # rejected every configuration and produced no data at all, which is a worse
    # failure than reporting the envelope honestly. Throttling is instead
    # recorded per configuration and reported alongside throughput, because it
    # is a real input to the operating decision: more threads means more heat
    # means more throttling, so the thermally-limited steady state is exactly
    # what a user choosing a thread count will actually live with. Run-to-run
    # instability is caught separately by the CV gate in analyse().
    res.thermally_limited = bool(res.throttle_delta)
    res.thread_verified = getattr(res, 'thread_verified', False)
    res.thread_verification_skipped = getattr(res, 'thread_verification_skipped', False)
    res.thread_mismatch = getattr(res, 'thread_mismatch', False)
    log(f"   + zero profile changes, power and clock plausible; "
        f"throttle events recorded: pkg={res.throttle_delta} core={res.core_throttle_delta}"
        f"{'  [THERMALLY LIMITED]' if res.thermally_limited else ''}")
    res.ok = True
    return res



# --------------------------------------------------------------------------
# concurrent background embedding load (E-core instance)
# --------------------------------------------------------------------------

class EmbedLoad:
    """Background embedding load generator against the E-core instance.

    Measures the LLM's cost when embeddings are being produced concurrently.
    This is the actual palindrome workload: MemPalace embedding a query while a
    model is generating. It runs on a SEPARATE ollama instance pinned to the
    E-cores (scripts/embed_service.py), because the primary server's
    Cpus_allowed_list is 0-11 and cannot reach CPUs 12-15 at all.
    """

    def __init__(self, host: str, model: str, batch: int = 8) -> None:
        self.host, self.model, self.batch = host, model, batch
        self._stop = None
        self._thread = None
        self.batches_done = 0
        self.embeddings_done = 0
        self.errors = 0

    def _loop(self) -> None:
        import threading

        i = 0
        while self._stop is None or not self._stop.is_set():
            texts = [f"concurrent embedding payload {i}-{j}: Node 1 inference "
                     f"contention sample text for bandwidth measurement." for j in range(self.batch)]
            payload = json.dumps({"model": self.model, "input": texts}).encode()
            req = urllib.request.Request(
                f"{self.host}/api/embed", data=payload,
                headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=120) as resp:
                    body = json.loads(resp.read())
                self.batches_done += 1
                self.embeddings_done += len(body.get("embeddings") or [])
            except (urllib.error.URLError, OSError, ValueError, json.JSONDecodeError):
                self.errors += 1
            i += 1
            time.sleep(0.1)

    def __enter__(self) -> "EmbedLoad":
        import threading

        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        time.sleep(3)   # let the background load reach steady state
        return self

    def __exit__(self, *_exc) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=10)

    def rate(self) -> float:
        return self.embeddings_done / self.batches_done if self.batches_done else 0.0


# --------------------------------------------------------------------------
# analysis
# --------------------------------------------------------------------------

@dataclass
class Stats:
    threads: int
    n: int
    tps_mean: float
    tps_ci95: float
    tps_cv: float
    ttft_mean: float
    itl_mean: float
    power_mean: float
    temp_max: int
    peak_mhz: int
    burned: int
    thermally_limited: bool = False
    embed_rate: float = 0.0
    embed_rate: float = 0.0
    embed_batches: int = 0
    embed_errors: int = 0


def ci95(values: list) -> float:
    if len(values) < 2:
        return 0.0
    return 1.96 * statistics.stdev(values) / (len(values) ** 0.5)


def summarise(res: ConfigResult) -> Optional[Stats]:
    if not res.ok or not res.tps_samples:
        return None
    mean = statistics.fmean(res.tps_samples)
    sd = statistics.stdev(res.tps_samples) if len(res.tps_samples) > 1 else 0.0
    return Stats(
        threads=res.threads,
        n=len(res.tps_samples),
        tps_mean=mean,
        tps_ci95=ci95(res.tps_samples),
        tps_cv=(sd / mean * 100) if mean else 0.0,
        ttft_mean=statistics.fmean(res.ttft_samples),
        itl_mean=statistics.fmean(res.itl_samples),
        power_mean=statistics.fmean(res.power_w),
        temp_max=max(res.temp_c),
        peak_mhz=max(res.peak_mhz),
        burned=res.burned_threads,
        thermally_limited=res.thermally_limited,
        embed_rate=res.embed_rate,
    )


def analyse(results: list) -> list:
    stats = [s for s in (summarise(r) for r in results) if s]
    usable = [s for s in stats if s.tps_cv <= MAX_VALID_CV_PCT]
    dropped = [s for s in stats if s.tps_cv > MAX_VALID_CV_PCT]
    for s in dropped:
        log(f"   ! config {s.threads} excluded: CV {s.tps_cv:.1f}% exceeds "
            f"{MAX_VALID_CV_PCT}% (run not repeatable)")
    pool = usable or stats
    return sorted(pool, key=lambda s: s.tps_mean, reverse=True)


def significance(best: Stats, second: Stats) -> str:
    """Is the winner's lead larger than combined 95% CI half-widths?"""
    if not second:
        return "only one valid config; no comparison possible"
    gap = best.tps_mean - second.tps_mean
    noise = best.tps_ci95 + second.tps_ci95
    if gap > noise:
        return (f"config {best.threads} beats {second.threads} by "
                f"{gap:.2f} t/s, which EXCEEDS combined 95% CI (±{noise:.2f}) "
                f"— a real difference")
    return (f"config {best.threads} leads {second.threads} by only {gap:.2f} t/s, "
            f"within combined 95% CI (±{noise:.2f}) — NOT a significant difference")


# --------------------------------------------------------------------------
# report
# --------------------------------------------------------------------------

def report(env: Environment, results: list, ranked: list) -> dict:
    log("\n" + "═" * 96)
    log("ENVIRONMENT (disclosed for reproducibility — IETF §4.1.4)")
    log("═" * 96)
    for key, val in vars(env).items():
        log(f"  {key:26s} {val}")
    mem = memory_state()
    log(f"  {'memory_at_report':26s} {mem}")
    log(f"  stream_benchmark_triad_gbs  (see scripts/bench_memory.py)")

    log("\n" + "═" * 96)
    log("VERIFICATION GATE RESULTS")
    log("═" * 96)
    for r in results:
        if r.ok:
            log(f"  num_thread={r.threads:<3} PASS  runner -t={r.runner_flag}  "
                f"burned={r.burned_threads}/{r.total_threads}  "
                f"tokens={r.token_counts}")
        else:
            log(f"  num_thread={r.threads:<3} FAIL  {r.failure}")
        for x in r.reps:
            if x["anomalies"]:
                log(f"      rep{x['rep']} CONTAMINATION: {'; '.join(x['anomalies'])}")

    log("\n" + "═" * 96)
    log("RESULTS (mean ± 95% CI over repeats)")
    log("═" * 96)
    log(f"  {'threads':>7} {'t/s':>16} {'CV%':>6} {'TTFT ms':>9} {'ITL ms':>8} "
        f"{'W':>6} {'maxC':>5} {'peakMHz':>8} {'burned':>7} {'thermal':>8} {'embed/s':>8}")
    for s in ranked:
        log(f"  {s.threads:>7} {s.tps_mean:>9.2f} ±{s.tps_ci95:>5.2f} {s.tps_cv:>6.1f} "
            f"{s.ttft_mean*1000:>9.0f} {s.itl_mean*1000:>8.1f} {s.power_mean:>6.1f} "
            f"{s.temp_max:>5} {s.peak_mhz:>8} {s.burned:>7} "
            f"{('YES' if s.thermally_limited else 'no'):>8} {s.embed_rate:>8.1f}")

    verdict = "NO VALID CONFIG"
    if ranked:
        best = ranked[0]
        second = ranked[1] if len(ranked) > 1 else None
        verdict = significance(best, second)
        log(f"\n  WINNER: num_thread={best.threads}  ({best.tps_mean:.2f} t/s)")
        log(f"  {verdict}")
        spread = ranked[-1].tps_mean - best.tps_mean
        log(f"  full spread across tested range: {spread:.2f} t/s "
            f"({spread/best.tps_mean*100:.1f}% of winner)")
    else:
        log(f"\n  {verdict}")

    return {
        "environment": vars(env),
        "gate_results": [
            {"threads": r.threads, "ok": r.ok, "failure": r.failure,
             "runner_flag": r.runner_flag, "burned_threads": r.burned_threads,
             "total_threads": r.total_threads, "token_counts": r.token_counts,
             "throttle_delta": r.throttle_delta,
             "contamination": r.contamination,
             "thermally_limited": r.thermally_limited,
             "thread_verified": getattr(r, "thread_verified", False),
             "thread_verification_skipped": getattr(r, "thread_verification_skipped", False),
             "thread_mismatch": getattr(r, "thread_mismatch", False),
             "embed_rate": r.embed_rate, "embed_errors": r.embed_errors,
             "preflight": r.preflight,
             "per_rep_telemetry": [
                 {"rep": x["rep"], "warmup": x["warmup"], "tokens": x["tokens"],
                  "anomalies": x["anomalies"],
                  "watts": x["telemetry"].get("watts_mean"),
                  "watts_min": x["telemetry"].get("watts_min"),
                  "watts_max": x["telemetry"].get("watts_max"),
                  "watts_stdev": x["telemetry"].get("watts_stdev"),
                  "peak_mhz": x["telemetry"].get("max_mhz_peak"),
                  "profiles": x["telemetry"].get("profiles_observed"),
                  "profile_switches": x["telemetry"].get("profile_switches"),
                  "t_first": x["telemetry"].get("t_first")}
                 for x in r.reps
             ]}
            for r in results
        ],
        "ranked": [vars(s) for s in ranked],
        "verdict": verdict,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--threads", default="1,2,3,4,5,6,8,10,12",
                    help="comma-separated num_thread values to test")
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--predict", type=int, default=FIXED_PREDICT)
    ap.add_argument("--cooldown", type=int, default=8)
    ap.add_argument("--out", default="bench_threads_report.json")
    ap.add_argument("--expect-profile", default="performance",
                    help="required power-profiles-daemon profile")
    ap.add_argument("--allow-on-battery", action="store_true",
                    help="bypass the AC-power preflight gate (results are suspect)")
    ap.add_argument("--embed-host", default="",
                    help="enable concurrent background embedding load against "
                         "this Ollama host (e.g. http://127.0.0.1:11435)")
    ap.add_argument("--embed-model", default="qwen3-embedding:0.6b")
    ap.add_argument("--quick", action="store_true",
                    help="4,5,6,8 x 2 repeats — fast sanity pass")
    args = ap.parse_args()

    thread_list = [4, 5, 6, 8] if args.quick else [
        int(t) for t in args.threads.split(",") if t.strip()
    ]

    log(f"Node 1 self-validating thread benchmark — model={args.model} "
        f"predict={args.predict} repeats={args.repeats}")
    if args.embed_host:
        log(f"  CONCURRENT EMBEDDING LOAD ENABLED: {args.embed_model} @ "
            f"{args.embed_host}")
    env = Environment.capture(args.model)
    log(f"ollama {env.ollama_version} | allowed_cpus={env.allowed_cpus} | "
        f"profile={env.power_profile} | mem={env.dimm_layout} {env.mem_configured_mt_s}")

    results = []
    total = len(thread_list)
    for idx, n in enumerate(thread_list, 1):
        phase(f"CONFIG {idx}/{total}  num_thread={n}   "
              f"model={args.model}  predict={args.predict}")
        embed = (args.embed_host, args.embed_model) if args.embed_host else None
        results.append(measure(args.model, n, args.repeats, args.predict,
                               args.cooldown, args.expect_profile, embed))

    ranked = analyse(results)
    payload = report(env, results, ranked)
    with open(args.out, "w") as handle:
        json.dump(payload, handle, indent=2)
    log(f"\n  report written: {args.out}")

    failures = [r for r in results if not r.ok]
    if failures:
        log(f"\n  {len(failures)} configuration(s) failed verification and were "
            f"excluded — see gate results above")
    return 0 if ranked else 1


if __name__ == "__main__":
    sys.exit(main())
