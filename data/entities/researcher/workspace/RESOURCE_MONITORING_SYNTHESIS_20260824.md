# 🔱 RESOURCE MONITORING SYNTHESIS — Consolidated BTOP Research (Canonical)
**AP Token**: `AP-RESEARCHER-MONSYNTH-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_monitoring_synthesis ⬡ CANONICAL-SYNTHESIS

**Date**: 2026-08-24
**Consolidates**: 3 Jem passes — first dive (`BTOP_ALTERNATIVES_RESEARCH_20260824.md` §1-267), fresh-session second dive (same file SD-1..5), primed-session independent report (`BTOP_ALTERNATIVES_SECOND_DIVE_JEM_20260824.md`, 490 lines; 12 convergences / 3 divergences — all 3 divergences were corrections favoring live ground truth).
**Environment**: Ubuntu 25.10 · kernel 6.17.0-41-generic · Ryzen 7 5700U (8C/16T Zen2) · 14Gi RAM · zRAM active (**zstd**, 8G) · Podman rootless + quadlets. Source of truth: `config/hardware_profile.yaml` (regenerated live 2026-08-24 post-FP-12).

---

## §1 FINAL VERDICTS

| Tool | Verdict | Role |
|---|---|---|
| **btop** | KEEP | SSH/minimal fallback; GPU needs compile flag; no container/quadlet lineage |
| **Mission Center** (Flatpak) | ADOPT (desktop) | Best GUI: iGPU freq, per-app breakdown, SMART, zRAM tab, RAPL power. Caveat: Flatpak can never access raw /proc — native build if per-process scraping needed |
| **Glances** | ADOPT (service) | Container awareness via podman.sock, REST API + Web UI, CSV/JSON/Prometheus export, alerting. ~60MB RAM. Complements OOMProtector, never replaces |
| **bottom (btm)** | ADOPT (TUI) | TOML layout engine, zoomable history, ~10-20MB. NO zRAM/iGPU/container widgets — needs sidecars |
| **systemd-cgtop** | ADOPT (present) | ONLY tool natively answering "what is my quadlet costing me" |
| **rustnet** | WATCH — better than bandwhich | eBPF attribution default-on, DPI+SNI, PCAPNG export, Landlock-sandboxed, ~4.9k stars, active thru Aug 2026 |
| bandwhich | PASSIVE MAINTENANCE | rustnet is successor |
| gtop / vtop | DEAD | Do not adopt |
| Netdata | CONDITIONAL | 250–350MB production + ~4GiB disk; M8 LANDMINE: kickstart warns "Cloud cannot be disabled" — verify runtime cloud-disable before Zero-Telemetry deployment |
| s-tui | NICE-TO-HAVE | Thermal/stress focus; AMD taxonomy verified (Pc/PStateCurLim) |
| bpftop | KEEP-IN-MIND | Audits eBPF program cost once engine ships eBPF tooling |

## §2 INSTALL STACK — Ubuntu 25.10 CORRECTED (prior dnf instructions VOID)

```bash
flatpak install flathub io.missioncenter.MissionCenter   # desktop GUI
pipx install 'glances[all]'                              # container-aware service
systemctl --user enable --now podman.socket              # → /run/user/1000/podman/podman.sock
cargo install bottom                                     # TUI custom layouts
bpftrace --version                                       # ALREADY INSTALLED (verified)
sudo apt install s-tui                                   # optional; verify repo availability
```

## §3 HARDWARE DISCOVERIES (live-verified)

1. **k10temp 80.6°C Tctl at probe** — RED operational flag: throttle-adjacent for Zen2 under load.
2. **RAPL watts AVAILABLE**: `/sys/class/powercap/intel-rapl*` exists (AMD via intel-rapl-compat, kernel >=5.11). Unlock:
   `echo 'SUBSYSTEM=="powercap", KERNEL=="intel-rapl*", RUN+="/bin/chmod 0444 %S%p/energy_uj"' | sudo tee /etc/udev/rules.d/99-rapl-user.rules && sudo udevadm control --reload`
3. **zRAM compression = zstd** — relevant to ZS workstream disposition.
4. **amdgpu**: PPT 35W, edge 66°C at probe. 5. htop ABSENT; bpftrace present. 6. hwmon inventory: k10temp, amdgpu, nvme, acpitz, BAT0, hp, ACAD.

---

## §4 BOTTOM.TOML GRID (5700U — prefer the sensor-grounded version)

Key settings: `rate="1s"` · `hide_k_threads=true` (16T noise) · `cache_memory=true` (critical with zRAM) · per-core CPU all-16 · temperature filtered to k10temp+nvme after first unfiltered run. Full verbatim configs: first-dive version at `BTOP_ALTERNATIVES_RESEARCH_20260824.md` (~lines 143-183); **sensor-inventory-grounded version preferred** at `BTOP_ALTERNATIVES_SECOND_DIVE_JEM_20260824.md` §1.

## §5 OMEGA ENGINE INTEGRATION (feasibility only — no build)

- Minimal path: Glances (slimmed, podman.sock) → REST JSON → observability pipeline; `bpftrace /usr/share/bpftrace/tools/oomkill.bt` as kill-event source (victim cmdline at kill-time). Zero new daemons beyond glances.
- OOMProtector verdict: COMPLEMENT not replace — polling latency vs direct PSI enforcement.
- eBPF unique value: latency DISTRIBUTIONS (runqlat, biolatency), per-process LLC misses via PMCs, off-CPU blocking reasons — invisible to /proc-based tools.
- rustnet: PCAPNG+JSONL export → security forensics feed, not metrics.

## §6 FOOTPRINT MEASUREMENT PLAYBOOK (Architect-runnable; nothing pre-installed)

Both passes honestly flagged all RAM figures as vendor-reported. Exact measurement commands in `BTOP_ALTERNATIVES_SECOND_DIVE_JEM_20260824.md` §6. Pattern:
```bash
systemd-run --user --scope -p MemoryMax=2G <tool> &   # or simply:
/usr/bin/time -v <tool>    # → "Maximum resident set size"
```
Measure btop (baseline), Mission Center, glances, bottom before adopting.

## §7 CONVERGENCE / DIVERGENCE LEDGER (dual-pass experiment)

| Claim | Fresh pass | Primed pass | Resolution |
|---|---|---|---|
| Target distro | "Fedora-class", dnf throughout | Ubuntu 25.10 (/etc/os-release verbatim) | RED divergence — fresh pass void; FP-12 incident |
| s-tui AMD power | "needs amd_energy, likely absent" | intel-rapl compat EXISTS; udev rule unlocks watts | RED divergence — caveat wrong for kernel >=5.11 |
| rustnet | half-line, "UNVERIFIED stability" | eBPF default-on, DPI+SNI, PCAPNG, Landlock, active Aug 2026 | GREEN — primed pass dug deeper |
| zRAM state | active 3.2G used | active, zstd, 0B at probe time | YELLOW partial — usage fluctuates; algorithm detail added |
| 12 other claims | — | CONVERGES with independent evidence | High confidence |

**Experiment conclusion**: primed-session continuation (task_id resume) strictly outperformed fresh spawn on correction depth; fresh pass contributed original authorship. Composition > either alone. Process lesson codified as FP-12 + R-4a task_id discipline.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ RESOURCE-MONITORING-SYNTHESIS v1.0 ⬡ CANONICAL ⬡ 2026-08-24*
