#!/usr/bin/env python3
"""
Abbreviated Screening — GSCA Protocol
Temperature sweep: 0.1, 0.5, 0.7
Context sweep: 4096, 8192
3 prompts × 3 temps × 2 contexts = 18 runs/model

Features:
- Incremental save after EACH run (no data loss on interrupt)
- Auto-resume from existing results file
- Clear progress tracking
- TelemetryCollector: privilege-free power/thermal/freq sampling per run
  (RAPL powercap + thermal zone + cpufreq sysfs; no sudo, no external deps)
  Reference: docs/TELEMETRY_PLAN.md
"""

import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

SCREENING_PROMPTS = [
    "Write a Python function to parse JSON with error handling.",
    "Explain the difference between async and threading in Python.",
    "Write a recursive function to flatten a nested dictionary.",
]

TEMPERATURES = [0.1, 0.5, 0.7]
CONTEXTS = [4096, 8192]

REQUEST_TIMEOUT = 300

_CPU_ZONE_TYPES = ("x86_pkg_temp", "cpu_thermal", "TCPU", "intel_powerclamp")
_FALLBACK_ZONE_TYPES = ("acpitz",)


class TelemetryCollector:
    """Background telemetry sampler for LLM inference runs.

    Privilege-free: reads RAPL powercap, thermal zone, and cpufreq sysfs.
    Handles RAPL counter wraparound via max_energy_range_uj. ~2ms/tick at
    2 Hz (<0.5% CPU). Aggregated stats returned on stop().
    """

    def __init__(self, sample_interval=0.5):
        self.interval = sample_interval
        self.samples = []
        self._thread = None
        self._stop = threading.Event()
        self._rapl_path = None
        self._rapl_max = None
        self._thermal_path = None
        self._prev_energy = None
        self._prev_time = None

    @staticmethod
    def _find_rapl_pkg():
        """Return (energy_uj_path, max_energy_range_uj) for the PKG domain."""
        base = "/sys/class/powercap/intel-rapl"
        if not os.path.isdir(base):
            return None, None
        for d in sorted(os.listdir(base)):
            if not d.startswith("intel-rapl:"):
                continue
            dom = os.path.join(base, d)
            try:
                with open(os.path.join(dom, "name")) as f:
                    name = f.read().strip()
                if "package" in name:
                    energy_path = os.path.join(dom, "energy_uj")
                    with open(os.path.join(dom, "max_energy_range_uj")) as f:
                        rapl_max = int(f.read().strip())
                    if not rapl_max:
                        rapl_max = 1 << 64
                    return energy_path, rapl_max
            except OSError:
                continue
        return None, None

    @staticmethod
    def _find_cpu_thermal_zone():
        """Return path to CPU package temp file, or None.

        Priority: CPU-type zones (x86_pkg_temp/cpu_thermal/TCPU/
        intel_powerclamp) over ACPI fallback (acpitz may be skin temp).
        """
        found_fallback = None
        try:
            zones = sorted(os.listdir("/sys/class/thermal"))
        except OSError:
            return None
        for zone in zones:
            if not zone.startswith("thermal_zone"):
                continue
            try:
                with open(f"/sys/class/thermal/{zone}/type") as f:
                    zone_type = f.read().strip()
            except OSError:
                continue
            if zone_type in _CPU_ZONE_TYPES:
                return f"/sys/class/thermal/{zone}/temp"
            if zone_type in _FALLBACK_ZONE_TYPES and found_fallback is None:
                found_fallback = f"/sys/class/thermal/{zone}/temp"
        return found_fallback

    def _read_energy(self):
        if not self._rapl_path:
            return None
        try:
            with open(self._rapl_path) as f:
                return int(f.read().strip())
        except (OSError, ValueError):
            return None

    def _read_temp(self):
        if not self._thermal_path:
            return None
        try:
            with open(self._thermal_path) as f:
                return int(f.read().strip()) / 1000.0
        except (OSError, ValueError):
            return None

    @staticmethod
    def _read_max_freq():
        """Return max current CPU frequency (MHz) across all online cores.

        scaling_cur_freq is in kHz; cpu0 alone underrepresents boost on
        hybrid parts. Reads each online cpuN and returns the max.
        """
        freqs = []
        try:
            cpus = sorted(os.listdir("/sys/devices/system/cpu"),
                          key=lambda s: int(s[3:]) if s.startswith("cpu") and s[3:].isdigit() else -1)
        except OSError:
            return None
        for cpu in cpus:
            if not cpu.startswith("cpu") or not cpu[3:].isdigit():
                continue
            try:
                with open(f"/sys/devices/system/cpu/{cpu}/cpufreq/scaling_cur_freq") as f:
                    freqs.append(int(f.read().strip()) // 1000)
            except OSError:
                continue
        return max(freqs) if freqs else None

    def start(self):
        """Begin sampling. Call before inference begins."""
        self._rapl_path, self._rapl_max = self._find_rapl_pkg()
        # energy_uj may be root-only (r--------) on some distros; degrade
        # gracefully: power metrics omitted, thermal/freq still captured.
        self._rapl_available = self._rapl_path is not None and self._read_energy() is not None
        if not self._rapl_available:
            self._rapl_path = None
        self._thermal_path = self._find_cpu_thermal_zone()
        self._prev_energy = self._read_energy()
        self._prev_time = time.monotonic()
        self.samples.clear()
        self._stop.clear()
        self._thread = threading.Thread(target=self._sample_loop, daemon=True)
        self._thread.start()

    def _sample_loop(self):
        first = True
        while not self._stop.is_set():
            now = time.monotonic()
            energy = self._read_energy()
            if not first and energy is not None and self._prev_energy is not None:
                sample = {"ts": now}
                delta_e = energy - self._prev_energy
                if delta_e < 0:  # RAPL counter wrapped
                    delta_e += self._rapl_max
                dt = now - self._prev_time
                if dt > 0:
                    sample["pkg_power_w"] = (delta_e / 1_000_000) / dt
            else:
                sample = {"ts": now}
            self._prev_energy = energy
            self._prev_time = now
            first = False
            temp = self._read_temp()
            if temp is not None:
                sample["pkg_temp_c"] = temp
            freq = self._read_max_freq()
            if freq is not None:
                sample["freq_mhz"] = freq
            self.samples.append(sample)
            time.sleep(self.interval)

    def stop(self, tokens=None):
        """Stop sampling. Returns aggregated telemetry dict on success."""
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2.0)
        return self._aggregate(tokens=tokens)

    def _aggregate(self, tokens=None):
        if not self.samples:
            return {}
        powers = [s["pkg_power_w"] for s in self.samples if "pkg_power_w" in s]
        temps = [s["pkg_temp_c"] for s in self.samples if "pkg_temp_c" in s]
        freqs = [s["freq_mhz"] for s in self.samples if "freq_mhz" in s]

        telemetry = {
            "samples": len(self.samples),
            "sampling_hz": round(
                len(self.samples)
                / max(self.samples[-1]["ts"] - self.samples[0]["ts"], 1e-6),
                2,
            ),
        }
        if powers:
            telemetry["pkg_power_w"] = self._stats(powers)
            total_energy_j = sum(
                (s.get("pkg_power_w", 0.0) or 0.0)
                * (self.samples[i + 1]["ts"] - s["ts"] if i + 1 < len(self.samples) else 0.0)
                for i, s in enumerate(self.samples)
                if "pkg_power_w" in s
            )
            if tokens:
                telemetry["energy_per_token_j"] = round(total_energy_j / tokens, 6)
                telemetry["tokens_per_joule"] = round(tokens / total_energy_j, 2) if total_energy_j > 0 else None
        if temps:
            telemetry["pkg_temp_c"] = self._stats(temps)
            telemetry["max_temp_c"] = max(temps)
        if freqs:
            telemetry["freq_mhz"] = self._stats(freqs)
        return telemetry

    @staticmethod
    def _stats(vals):
        if not vals:
            return None
        n = len(vals)
        mean = sum(vals) / n
        sv = sorted(vals)
        return {
            "mean": round(mean, 2),
            "min": round(sv[0], 2),
            "max": round(sv[-1], 2),
            "p50": round(sv[n // 2], 2),
            "p95": round(sv[min(int(n * 0.95) - 1, n - 1)], 2),
        }


def log(msg):
    print(msg, flush=True)


def generate(host, model, prompt, temperature=0.1, num_ctx=4096, num_predict=512, timeout=REQUEST_TIMEOUT):
    data = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_ctx": num_ctx,
            "num_predict": num_predict,
            "num_thread": 8,
            "num_gpu": 0
        }
    }).encode()
    req = urllib.request.Request(
        f"{host}/api/generate",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:500]
        raise RuntimeError(f"HTTP {e.code} :: {body}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"connection error: {e.reason}") from e
    except TimeoutError:
        raise RuntimeError(f"request timed out after {timeout}s")
    return json.loads(raw)


def load_existing_results(output_file):
    """Load existing results if file exists, return (results, completed_runs_set)."""
    if not output_file.exists():
        return [], set()
    try:
        data = json.loads(output_file.read_text())
        results = data.get("results", [])
        completed = {(r["context"], r["temperature"], r["prompt_idx"]) for r in results if r.get("tps") is not None}
        log(f"[RESUME] Found {len(completed)}/18 runs already completed")
        return results, completed
    except Exception as e:
        log(f"[WARN] Could not load existing results: {e}")
        return [], set()


def save_results(output_file, model, results):
    """Save results atomically (write to temp, then rename)."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    temp_file = output_file.with_suffix(".tmp")
    data = {
        "model": model,
        "protocol": "GSCA abbreviated screening",
        "num_predict": num_predict if "num_predict" in dir() else 512,
        "prompts": SCREENING_PROMPTS,
        "temperatures": TEMPERATURES,
        "contexts": CONTEXTS,
        "results": results,
        "timestamp": time.time()
    }
    temp_file.write_text(json.dumps(data, indent=2))
    temp_file.replace(output_file)


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Abbreviated screening per GSCA protocol")
    ap.add_argument("--model", required=True)
    ap.add_argument("--host", default="http://localhost:11434")
    ap.add_argument("--num-predict", type=int, default=512,
                    help="max output tokens per run (default 512; bounds reasoning-model"
                         " chains that never emit EOS — e.g. Qwen3 think loops)")
    args = ap.parse_args()
    num_predict = args.num_predict

    log(f"=== ABBREVIATED SCREENING: {args.model} ===")
    log(f"Prompts: {len(SCREENING_PROMPTS)} | Temps: {TEMPERATURES} | Contexts: {CONTEXTS}")
    log(f"Total runs: {len(SCREENING_PROMPTS) * len(TEMPERATURES) * len(CONTEXTS)}")
    log("")

    # Output file path
    output_dir = Path("benchmarking") / "screening"
    output_file = output_dir / f"{args.model.replace(':', '-')}_screening.json"

    # Load existing results
    results, completed = load_existing_results(output_file)

    run_id = 0
    for ctx in CONTEXTS:
        for temp in TEMPERATURES:
            for i, prompt in enumerate(SCREENING_PROMPTS, 1):
                run_id += 1
                key = (ctx, temp, i)

                # Skip if already completed
                if key in completed:
                    existing = next(r for r in results if (r["context"], r["temperature"], r["prompt_idx"]) == key)
                    log(f"[Run {run_id:2d}/18] ctx={ctx:5d} temp={temp:.1f} prompt={i} — SKIPPED (already done: {existing['tps']:.2f} t/s)")
                    continue

                log(f"[Run {run_id:2d}/18] ctx={ctx:5d} temp={temp:.1f} prompt={i}")
                log(f"  Prompt: {prompt!r}")

                collector = TelemetryCollector()
                collector.start()
                t0 = time.time()
                try:
                    resp = generate(args.host, args.model, prompt, temperature=temp, num_ctx=ctx, num_predict=num_predict)
                except Exception as exc:
                    dt = time.time() - t0
                    telemetry = collector.stop()
                    log(f"  ERROR: {exc}")
                    results.append({
                        "run": run_id, "context": ctx, "temperature": temp, "prompt_idx": i,
                        "error": str(exc), "time_s": None, "tokens": None, "tps": None,
                        "telemetry": telemetry or None
                    })
                    # Save immediately on error too
                    save_results(output_file, args.model, results)
                    continue

                dt = time.time() - t0
                tok = resp.get("eval_count", 0)
                tps = tok / dt if dt > 0 else 0
                telemetry = collector.stop(tokens=tok)

                result = {
                    "run": run_id, "context": ctx, "temperature": temp, "prompt_idx": i,
                    "time_s": round(dt, 2), "tokens": tok, "tps": round(tps, 2),
                    "telemetry": telemetry or None
                }
                results.append(result)

                # INCREMENTAL SAVE AFTER EACH RUN
                save_results(output_file, args.model, results)

                log(f"  {dt:.1f}s | {tok} tokens | {tps:.2f} t/s  ✓ SAVED")
                if telemetry:
                    pw = telemetry.get("pkg_power_w", {})
                    pt = telemetry.get("pkg_temp_c", {})
                    ep = telemetry.get("energy_per_token_j")
                    log(f"  ℹ pkg_power mean={pw.get('mean')}W "
                        f"| pkg_temp mean={pt.get('mean')}°C max={pt.get('max')}°C "
                        f"| energy/token={ep}J"
                        + (f" | max_energy_range={collector._rapl_max}" if False else ""))
                log("")

    # Summary
    log("=== SCREENING SUMMARY ===")
    valid = [r for r in results if r["tps"] is not None]
    if valid:
        for ctx in CONTEXTS:
            for temp in TEMPERATURES:
                subset = [r for r in valid if r["context"] == ctx and r["temperature"] == temp]
                if subset:
                    avg_tps = sum(r["tps"] for r in subset) / len(subset)
                    avg_tok = sum(r["tokens"] for r in subset) / len(subset)
                    log(f"  ctx={ctx:5d} temp={temp:.1f} → avg {avg_tps:.2f} t/s | {avg_tok:.0f} tokens")

    log(f"\nFinal results saved to {output_file}")

    # Telemetry summary
    with_telemetry = [r for r in results if r.get("telemetry")]
    if with_telemetry:
        log("=== TELEMETRY SUMMARY ===")
        powers = [r["telemetry"]["pkg_power_w"]["mean"] for r in with_telemetry if r["telemetry"].get("pkg_power_w")]
        temps = [r["telemetry"]["max_temp_c"] for r in with_telemetry if r["telemetry"].get("max_temp_c")]
        eps = [r["telemetry"]["energy_per_token_j"] for r in with_telemetry if r["telemetry"].get("energy_per_token_j")]
        if powers:
            log(f"  avg_pkg_power_w={sum(powers)/len(powers):.2f}")
        if temps:
            log(f"  peak_pkg_temp_c={max(temps):.1f}")
        if eps:
            log(f"  avg_energy_per_token_mj={sum(eps)/len(eps)*1000:.2f}")


if __name__ == "__main__":
    main()