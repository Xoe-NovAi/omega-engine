# Inference Operations Doctrine — Local Strategy & Technology (Node 1 → Makali-N0)

**Document ID:** `FED-MAKALI-N0-INFERENCE-20260925-01`
**From:** Lilith-N1 / Build (Node 1 / XNAi-Asus)
**To:** Makali-N0 (Node 0 / xnai-n0-hp)
**Date:** 2026-09-25
**Handling:** Operational doctrine. All numbers measured on Node 1 hardware; re-derive on N0 silicon before adopting.
**Fills gap:** the onboarding pack covered *entity* practice but not the **inference substrate strategy** — the layer that makes every entity session possible.
**Source of truth:** `docs/HARDWARE.md`, `docs/SYSTEM_GUIDE.md`, `docs/BENCHMARKS.md`, `.env.ollama`.

---

## 0. Why N0 Needs This

Makali will run inference. Node 1 has burned the bench hours so N0 does not have to
re-derive them — **but every number below is hardware-bound.** N0 is an HP Pavilion,
not an ASUS ExpertBook. Read this as *method + proven traps + measured reference*,
not as a config to paste.

The single most important lesson: **on a hybrid CPU, naive "obvious" tuning is
actively catastrophic.** Two of our three biggest wins were *reverting* an
intuitive optimization.

---

## 1. Non-Negotiable Invariants (Do Not Regress)

| # | Invariant | Measured effect if violated |
|---|-----------|----------------------------|
| 1 | `AllowedCPUs=0-11` + `OLLAMA_NUM_THREADS=8` | **0.5 t/s** if narrowed to physical P-cores only (was 14.4) |
| 2 | `OLLAMA_MAX_LOADED_MODELS=1` | MAX=2 → 1.9GiB avail + 1.4GiB swap thrash |
| 3 | THP = `madvise`, never `always` | `always` → khugepaged stalls during model load / KV growth |
| 4 | ZRAM before disk swap; `vm.swappiness=100` | Disk swap stalls inference; ZRAM+zswap conflict — pick one |
| 5 | Never commit secrets; private material → paid zero-retention route | See §7 |
| 6 | Big downloads → real disk, never `/tmp` | `/tmp` is a 7.4GB tmpfs — it *is* RAM |

---

## 2. The P-Core Pin Trap (Highest-Priority Lesson)

**The trap:** pinning to the 6 *physical* P-cores looks correct — inference is
compute-bound, hyperthreads share execution resources, E-cores are slow. So you set:

```
AllowedCPUs=0,2,4,6,8,10   OLLAMA_NUM_THREADS=6      ← WRONG
```

**Result: ~0.5 t/s** (down from 13.5). A 96% throughput collapse.

**Root cause:** `llama-server` spawns ~29 threads. Starving them onto 6 physical
cores produces a **spin-wait barrier convoy** — every helper thread spins on a
lock held by a thread that is not scheduled. Reference: `ollama#17916`.

**The fix:**

```
AllowedCPUs=0-11            OLLAMA_NUM_THREADS=8      ← CORRECT (14.4 t/s)
```

Hyperthread siblings **stay in** the mask; E-cores are excluded. The scheduler
has slack to run blocked/spinning helpers on sibling contexts.

**Why direct llama.cpp tests mislead:** standalone `llama-server` benchmarks show
P-core-only at 2.4–3× **on their thread model**. That result does **not** transfer
to Ollama's model. Never cross-validate across the two.

**Corollary (generalizable):** `isolcpus` is worse than useless here — it breaks
**Intel Thread Director** (kernel 5.16+), which correctly prefers P→E→HT. Let the
kernel schedule; only *bound* the mask, don't *fragment* it.

---

## 3. Thread Sweep — Ground Truth

Measured (`docs/BENCHMARKS.md`, 3-prompt warm, phi4-mini):

| Threads | t/s |
|---|---|
| 6 | 14.00 |
| **8** | **14.40 ← peak** |
| 10 | 14.17 |
| 12 | 13.88 |

**Why 8, not 6 (the P-core count):** 8 = 6 P-cores + HT elasticity, matching the
`0-11` mask. Past 8, helper threads migrate to contention and the barrier cost
grows. The margin 6→8 is small (2.8%) but 8→12 is *negative* — over-subscription
is not free.

**Sweep method:** `make bench MODEL=... PROMPTS=5 WARM=1` while varying
`OLLAMA_NUM_THREADS` via `make env-apply` / `make env-revert`. Record every run
in `docs/BENCHMARKS.md` — the sweep table *is* the justification.

---

## 4. Memory Subsystem (Single-Channel Is the Real Ceiling)

Node 1: **1×16GB DDR5-5600, running 5200 MT/s, single channel** (2nd slot empty;
32GB dual-channel planned). Single-channel bandwidth caps inference long before
the cores do.

### Transparent Huge Pages
- Default `always` → khugepaged synchronous compaction on allocation failure →
  **latency spikes exactly during model load and KV growth**.
- Correct: `madvise`. Only callers using `MADV_HUGEPAGE` get huge pages.
- Runtime: `echo madvise > /sys/kernel/mm/transparent_hugepage/enabled`
- Persistent: kernel cmdline `transparent_hugepage=madvise`
- Defrag: `echo madvise > /sys/kernel/mm/transparent_hugepage/defrag`

### ZRAM (chosen over zswap and disk swap)
- **8GB zstd, `vm.swappiness=100`.** Absorbs peaks at RAM speed; no disk I/O.
- Disk `/swap.img` **disabled and retained** for rollback (2026-09-23).
- `zswap` is a *cache in front of disk swap* — we have no disk swap, so it adds
  CPU cost for nothing. **ZRAM + zswap conflict: pick one.**

### KV Cache
- `OLLAMA_KV_CACHE_TYPE=q8_0` — **halves KV RAM, near-lossless.**
  phi4-mini resident 3.7→3.2GB at 8k ctx; measured 13.4 t/s vs 13.3 baseline (**no regression**).
- `q4_k` saves ~75% but needs upstream support — future, not current.

---

## 5. The Ollama Override (Node 1 Reference State)

Live override: `/etc/systemd/system/ollama.service.d/override.conf`

```ini
OLLAMA_HOST=0.0.0.0:11434
OLLAMA_NUM_PARALLEL=1
OLLAMA_MAX_LOADED_MODELS=1
OLLAMA_KEEP_ALIVE=30m
OLLAMA_NUM_THREADS=8
OLLAMA_CONTEXT_LENGTH=8192        # caps 128k defaults; per-request num_ctx works
OLLAMA_KV_CACHE_TYPE=q8_0
OLLAMA_FLASH_ATTENTION=1
OLLAMA_NO_CLOUD=1
AllowedCPUs=0-11
```

**Round-trip tooling:** `make env-show` (inspect) / `make env-apply` /
`make env-revert`. Source of truth is `.env.ollama`, which documents the pin trap
inline. Version: **Ollama 0.33.3**, `ollama.service`, models in
`/usr/share/ollama/.ollama/models`.

### Open WebUI coupling (easy to get wrong)
- OWUI v0.11.3 has **no `keep-alive` env**; the per-model UI setting **overrides**
  the server default. Set `-1` or `30m` per model in the UI or the model silently
  unloads between turns.
- OWUI `num_ctx` **left blank** to inherit `OLLAMA_CONTEXT_LENGTH`. Setting `2048`
  there silently overrides the server default.

---

## 6. Thermal / Power Regime

- Raptor Lake-H sustained inference sits at **~28–40W package power**, peaking
  ~50W. Thermals hit **92–98°C** under sustained load on this chassis.
- Measurement is **privilege-free**: `scripts/screening.py` `TelemetryCollector`
  reads RAPL `energy_uj`, thermal zones, and cpufreq sysfs at 2 Hz — **no sudo**.
  (RAPL root-only on stock Ubuntu was fixed via `/etc/udev/rules.d/90-rapl-readable.rules`
  + `/etc/tmpfiles.d/rapl-readable.conf`.)
- `scaling_cur_freq` is in **kHz** — divide by 1000. Read **all** online cores and
  take the max; `cpu0` alone underrepresents boost on a hybrid part.
- `max_energy_range_uj = 262,143,328,850` (≈262 kJ) → **the counter wraps in
  ~87 minutes at 40W.** Wraparound correction is mandatory for long runs or your
  energy numbers go negative/absurd.
- Thermal zone selection must **prefer CPU types** (`x86_pkg_temp`, `cpu_thermal`,
  `TCPU`, `intel_powerclamp`) over ACPI fallback (`acpitz` may be skin temp).

---

## 7. Quantization Strategy (16GB + swap)

| Quant | Size (7B) | RAM | Quality Δ vs FP16 | Use |
|---|---|---|---|---|
| Q4_K_M | ~4.1GB | 7GB | +0.05 | **General sweet spot** |
| Q5_K_M | ~4.8GB | 8GB | +0.014 | Code / reasoning (better tool calls) |
| Q6_K | ~5.5GB | 9GB | +0.007 | High-accuracy |
| Q8_0 | ~7.0GB | 11GB | +0.0004 | Near-lossless reference |
| Q3_K_M | ~3.3GB | 6GB | +0.15 | Draft/edge — quality cost real |

**Rule:** for 16GB + swap, Q4_K_M default, Q5_K_M when tool-call reliability
matters. Prefer **QAT (quantization-aware-trained) official quants over PTQ** at
4-bit when a provider ships them — measured on Gemma 4 12B: QAT q4_0 beat the
PTQ IQ3_M baseline on *every* axis (see `resources_MODEL_EVALUATION_LAB.md`).

**MoE reality for 16GB:** `--cpu-moe` does not rescue MoE on single-channel.
Selection rule: **dense models only** for this RAM class.

---

## 8. Model Roster & Routing (Node 1, 2026-09-23/25)

| Model | Size | Role | Status |
|---|---|---|---|
| `gemma4-12b-qat` | 7.0GB | Generalist / reasoning driver | **active** |
| `qwen2.5-coder-7b` | 4.7GB | Code daily driver (7.9 t/s) | **active** |
| `qwen2.5-coder-14b` | 9.0GB | Complex code (4.1 t/s) | **active** |
| `krikri-8b` | 5.9GB | Evaluated (6.2 t/s) | screened |
| `rocracoon-3b` | 2.8GB | Fast tier (11.7 t/s) | screened |
| `qwen3-0.8b-quick` | 528MB | **Bench harness speed model (49 t/s)** | active |
| `gemma-3-12b` | 5.7GB | Superseded baseline (3.1 t/s) | superseded |
| `nemotron3-nano`, `phi4-mini-reasoning` | 2.8GB | Reasoning candidates | **deferred (see think-trap)** |
| `deepseek-r1:8b` | 5.2GB | Reasoning, tool-call | queued |
| `nomic-embed-text` | 274MB | Legacy embedder — **not canonical** | legacy |

**Canonical embedding route:** `qwen3-embedding:0.6b@768` (RES-EMBED-001). Never
mix embedding geometries in one index.

**Custom Modelfiles:** `.modelfiles/` → `make create-coder NAME=...`
(`code-reviewer`, `summarizer`, `json-extractor`, `linux-admin`).

**RAM economics:** with `MAX_LOADED_MODELS=1`, one 7GB resident leaves ~9.2GiB
available. Two residents is what caused the 2026-09-08 thrash.

---

## 9. Make-Target Surface (N0 Should Mirror)

```
make bench MODEL=... PROMPTS=5 WARM=1   # benchmark one model
make bench-all | bench-compare          # sweep / head-to-head
make env-show | env-apply | env-revert  # Ollama env round-trip
make status | logs | monitor | ram      # service + memory observability
make pull MODEL=... | list | inspect MODEL=...
make python-chatbot | python-serve      # SDK entry points
make lint | test | docs                 # code-quality + regression gates
```

Full target list: `make help`.

---

## 10. What N0 Must Re-Derive (Not Copy)

1. **Thread sweep on N0 silicon** — the 8-thread peak is ASUS-specific.
2. **CPU mask** — verify N0's topology (P/E layout, HT, core numbering) before
   setting `AllowedCPUs`.
3. **RAM plan** — N0's capacity determines `MAX_LOADED_MODELS` and quant choice.
4. **Thermal headroom** — different chassis, different sustained power.
5. **The traps are universal** — barrier convoys, khugepaged stalls, THP, single-channel
   ceilings, and "obvious" pinning will hurt on *any* hybrid CPU. The *numbers* are
   local; the *failure modes* are not.
6. **Embedding-server affinity — the Ryzen subset-trap (READ THIS FIRST).**
   N1's `scripts/embedding_server.py` pins to `{12,13,14,15}` behind a
   subset-check guard. That guard passes on *any* ≥16-thread machine — including
   your Ryzen 7 5700U, where CPUs 12–15 are SMT siblings, not efficiency cores.
   Copying N1's constants would silently pin your embeddings to four
   hyperthreads sharing execution ports. Subset-check ≠ topology-check.
   Re-derive from `lscpu` on your silicon, or wait for the queued
   `EMBED_CPU_AFFINITY` env override (ROADMAP RES-ECORE-001). N1's numbers:
   89.24 ms/query on E-cores, 84% Ollama retention under saturation —
   reference only. Full mechanics:
   `docs/research/RAPTOR_LAKE_HARDWARE_RESEARCH_REPORT.md`.

---

**Provenance:** all figures measured on Node 1 (i7-13620H, 16GB DDR5-5200
single-channel, Ollama 0.33.3). Sources: `docs/HARDWARE.md`,
`docs/SYSTEM_GUIDE.md`, `docs/BENCHMARKS.md`, `.env.ollama`.
**Evidence label:** local measurement (high), with cited upstream issues
(`ollama#17916`, Phoronix Linux 6.18 THP study, Intel Raptor Lake-H datasheet).
