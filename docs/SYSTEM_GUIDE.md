# SYSTEM_GUIDE.md — Definitive Living Guide for ASUS ExpertBook P1503CVA (i7-13620H) Local AI Inference

**Machine:** ASUS ExpertBook P1503CVA | **CPU:** i7-13620H (6P+4E, 10C/16T) | **RAM:** 1×16GB DDR5-5600 @ 5200 MT/s (single-channel) | **GPU:** Intel UHD Graphics 64EU / Raptor Lake-P, PCI ID 8086:a7a8 (shared) | **OS:** Ubuntu 26.04 LTS, Linux 7.0 | **BIOS:** P1503CVA.337 (2026-05-29)

**Purpose:** Single authoritative source for all system tunings, decisions, rationale, and future evolution. Updated every session. No re-discovery.

---

## 1. CORE PRINCIPLES

| Principle | Rationale |
|-----------|-----------|
| **Measure, don't guess** | Every tuning has bench evidence or citation |
| **Document the trap** | P-core pinning (0,2,4,6,8,10) = 0.5 t/s disaster (ollama #17916) |
| **Single-channel reality** | 41.6 GB/s theoretical → ~35 GB/s actual; bandwidth is the bottleneck |
| **Hybrid CPU respect** | Thread Director exists; don't fight it with `isolcpus`/`nohz_full` |
| **Living document** | This guide grows; stale entries get tagged `[STALE]` and re-verified |

---

## 2. CURRENT OPTIMAL CONFIG (Verified 2026-09-23)

### Ollama (systemd override: `/etc/systemd/system/ollama.service.d/override.conf`)
```ini
[Service]
Environment=OLLAMA_HOST=0.0.0.0:11434
Environment=OLLAMA_NUM_PARALLEL=1
Environment=OLLAMA_MAX_LOADED_MODELS=1
Environment=OLLAMA_KEEP_ALIVE=30m
Environment=OLLAMA_NUM_THREADS=8
Environment=OLLAMA_CONTEXT_LENGTH=8192
Environment=OLLAMA_KV_CACHE_TYPE=q8_0
Environment=OLLAMA_FLASH_ATTENTION=1
Environment=OLLAMA_NO_CLOUD=1
AllowedCPUs=0-11
```

### Open WebUI (Docker, pinned v0.11.3)
- `docker-compose.yml`: `image: ghcr.io/open-webui/open-webui:v0.11.3`
- `OLLAMA_BASE_URL=http://host.docker.internal:11434`
- **UI setting required:** Workspace → Models → (each) → Advanced → Keep Alive = `-1` (or `30m`)
- **num_ctx:** Leave UNSET (inherits 8192 from Ollama)

### CPU Affinity & Threading
- **AllowedCPUs=0-11** (P-cores + HT siblings, E-cores excluded)
- **OLLAMA_NUM_THREADS=8** (6 P-cores + 2 HT elasticity)
- **Runner verified:** `llama-server --flash-attn on -c 8192 --cache-type-k q8_0 --cache-type-v q8_0`

### Performance Baseline (phi4-mini, Q4_K_M, 8k ctx, warm)
| Metric | Value |
|--------|-------|
| Throughput | **13.4 t/s** (3-prompt avg) |
| Resident RAM | **3.2 GB** (down from 3.7 GB f16 KV) |
| Swap pressure | **~0 during the 2026-09-08 benchmark**; current zRAM usage is runtime-dependent |
| Available RAM | **9.2 GiB** |

---

## 3. STRATEGIC DECISIONS (With Rationale)

### 3.1 ZRAM vs ZSWAP → **ZRAM 8GB zstd, swappiness 100**

| Factor | Decision | Why |
|--------|----------|-----|
| **Technology** | ZRAM | Compressed RAM block device; no disk I/O |
| **Size** | 8GB (50% RAM) | Absorbs model-load peaks (3-6GB each) |
| **Algorithm** | zstd | 40% better compression than lz4, minimal speed penalty |
| **Swappiness** | 100 | Pushes cold pages to fast ZRAM aggressively |
| **Conflict** | Never ZRAM+ZSWAP | They fight for pages |

**Implementation (persistent, current):**
```ini
# /etc/systemd/zram-generator.conf.d/99-llm.conf
[zram0]
zram-size = min(ram / 2, 8192)
compression-algorithm = zstd
```
```ini
# /etc/sysctl.d/99-llm-inference.conf
vm.swappiness=100
```
The generated `/dev/zram0` is the only active swap device. The NVMe-backed
`/swap.img` is retained for rollback but disabled in `/etc/fstab`.

**Sources:** zram-tuning (reapercanuk39), ChromeOS/Android strategies, Ariadne HPCA 2025.

### 3.2 THP (Transparent Huge Pages) → **madvise**

| Setting | Value | Why |
|---------|-------|-----|
| `/sys/kernel/mm/transparent_hugepage/enabled` | `madvise` | Only apps calling `madvise(MADV_HUGEPAGE)` get THP; avoids khugepaged stalls |
| `/sys/kernel/mm/transparent_hugepage/defrag` | `madvise` | Same rationale |
| Kernel cmdline | `transparent_hugepage=madvise` | Persistent across reboots |

**Impact:** Phoronix Linux 6.18 + AMD ZenDNN + Red Hat all confirm `madvise` optimal for LLM inference — eliminates synchronous compaction latency spikes during model load/KV growth.

### 3.3 MAX_LOADED_MODELS → **1 (not 2)**

| Config | Resident | Available | Swap | phi4-mini t/s |
|--------|----------|-----------|------|---------------|
| MAX=2 | 11.3 GB (2 models) | 1.9 GiB | 1.4 GiB (thrash) | 13.5 (with cold dips to 3.2-6.5) |
| **MAX=1** | **3.2 GB (1 model)** | **9.2 GiB** | **~0** | **13.4 (steady)** |

**Decision:** Single-channel 16GB cannot hold 2 residents + OS headroom. Swap thrash under MAX=2 causes cold-load t/s dips. Model-switch reload cost of MAX=1 is acceptable (~2-5s).

### 3.4 KV Cache Quantization → **q8_0 (now), q4_k (future)**

| KV Type | Resident Delta | Throughput | Quality (ppl Δ) | Status |
|---------|----------------|------------|-----------------|--------|
| f16 (default) | baseline 3.7 GB | 13.3 t/s | baseline | baseline |
| **q8_0** | **-0.5 GB → 3.2 GB** | **13.4 t/s** | **~0** | **DEPLOYED** |
| q4_k | ~-1 GB est. | TBD | <0.1 | Awaits upstream (KVQuant/VecInfer per-channel pre-RoPE) |

**Note:** q8_0 halves KV RAM with near-lossless quality. q4_k saves another ~0.4GB but needs per-channel quantization not yet in llama.cpp mainline.

### 3.5 Model Quantization → **Q4_K_M for all (sweet spot)**

| Model | Current Quant | Size | RAM | Notes |
|-------|---------------|------|-----|-------|
| phi4-mini | Q4_K_M | 2.5 GB | 7 GB | Primary fast model |
| qwen2.5-coder:7b | Q4_K_M | 4.7 GB | 7 GB | Code tasks |
| deepseek-r1:8b | Q4_K_M | 5.2 GB | 8 GB | Reasoning; **candidate for Q5_K_M** if tool-calls matter |
| Custom (code-reviewer, etc.) | Q4_K_M | 2.5-4.7 GB | 7-8 GB | FROM base models |

**Upgrade path:** deepseek-r1:8b → Q5_K_M (better tool-call reliability for agentic coding) if RAM allows.

---

## 4. BIOS CONFIGURATION (Verify on Next Reboot)

**Path:** Advanced → CPU Configuration / Power Management Control

| Setting | Target Value | Rationale |
|---------|--------------|-----------|
| Hyper-Threading | **Enabled** | Required for 8-thread config |
| Intel SpeedStep (EIST) | **Enabled** | Required for HWP |
| **Intel Speed Shift (HWP)** | **Enabled** | **Critical** — per-core P-states, hardware P-state selection |
| Turbo Mode | **Enabled** | Allows PL2 burst (115W, 28-56s) |
| C-States (C3/C6) | **Enabled** | Power savings at idle |
| Package C-State Limit | **Enabled (C6/C8/C10)** | Deep idle |
| Energy Performance Bias | **Performance** | Hardware default for EPP=performance |
| AVX Offset | **0** | Negative offset reduces AVX freq; keep 0 for inference |
| PL1 / PL2 | **View only** (usually locked) | PL1=45W, PL2=115W stock; if adjustable, don't exceed cooling |

**Fan Profile:** Already set to **Performance** in BIOS (user confirmed). MyASUS "Full Speed" mode also available.

**Note:** i7-13620H is 6P+4E (10C/16T), NOT i7-13700H (14C/20T). Previous gaming-expert agent had wrong CPU.

---

## 5. LINUX KERNEL / SYSCTL TUNINGS

### Applied / To Apply

| Parameter | Current | Target | Method |
|-----------|---------|--------|--------|
| `transparent_hugepage` | madvise | **madvise** | Runtime + `grub` cmdline |
| `thp defrag` | madvise | **madvise** | Runtime |
| CPU governor | powersave + EPP=balance_performance | **Keep** | Current desktop state; performance profile is an explicit benchmark mode |
| `vm.swappiness` | 100 | **100 (with ZRAM)** | High swappiness = push cold to fast ZRAM |
| ZRAM | 7.4 GiB zstd, priority 100 | **8GB class, zstd, priority 100** | `systemd-zram-generator` + sysctl |
| NVMe `/swap.img` | disabled; retained for rollback | **Disabled** | zRAM is the only active swap device |
| `nohz_full` / `isolcpus` | none | **Don't** | Breaks Thread Director on hybrid |

### Grub Cmdline Addition
```bash
# /etc/default/grub
GRUB_CMDLINE_LINUX_DEFAULT="... transparent_hugepage=madvise"
# Then: sudo update-grub
```

### Runtime Verification Commands
```bash
# THP
cat /sys/kernel/mm/transparent_hugepage/enabled
cat /sys/kernel/mm/transparent_hugepage/defrag

# ZRAM
zramctl
swapon -s

# CPU
cat /sys/devices/system/cpu/cpu*/cpufreq/energy_performance_preference
turbostat --Summary --show PkgWatt,CoreTmp,Avg_MHz,Busy% -i 2   # needs CAP_SYS_RAWIO (sudo)

# Memory
free -h
```

> **Privilege-free alternative (2026-09-23)**: `scripts/screening.py` now embeds a
> `TelemetryCollector` that reads power/thermal/freq directly from sysfs
> (`/sys/class/powercap/intel-rapl/*`, `/sys/class/thermal/thermal_zone*`,
> `/sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq`) — **no sudo**.
> Use that for automated screening; `turbostat` above remains for manual/forensic
> runs only. See `docs/TELEMETRY_PLAN.md`.

---

## 6. THERMAL / POWER MANAGEMENT

### Raptor Lake-H Specs (Intel Datasheet)
- **PL1 (sustained):** 45W (Base Power / TDP)
- **PL2 (burst):** 115W (Max Turbo Power)
- **Tau:** 28-56s (PL2 duration)
- **Tj max:** 100°C

### Current State
- `intel_pstate` + `powersave` governor + **EPP=performance** ✓
- `thermald` active (adaptive; watch for PL1=0 bug #550)
- Idle: ~63°C @ 400 MHz (normal for laptop silent mode)

### Validation Protocol (10-min Sustained)
```bash
# Terminal 1: Run continuous inference
while true; do curl -s http://localhost:11434/api/generate -d '{"model":"phi4-mini","prompt":"Continue the story:","stream":false}' >/dev/null; done

# Terminal 2: Log thermals (turbostat needs sudo; privilege-free variant below)
turbostat --Summary --show PkgWatt,CoreTmp,Avg_MHz,Busy% -i 2 > thermals.log
# Also: watch -n 2 sensors
```

**Privilege-free thermal logging:** use `scripts/screening.py --model <m>`
with its embedded TelemetryCollector (reads RAPL/thermal/freq sysfs, no sudo).
Reference: `docs/TELEMETRY_PLAN.md`.

**Pass criteria:** Avg P-core freq ≥ 3.5 GHz sustained, no throttle to < 3.0 GHz, pkg temp < 90°C.

### Optional Tools (If Thermal Headroom Exists)
- `intel-undervolt` — per-core/uncore undervolt (MSR writes, **caution**)
- `throttled` (erpalma) — restores PL1/PL2 if firmware resets them
- **BIOS PL1/PL2 unlock** — rarely available on laptops

---

## 7. OPEN WEBUI + OLLAMA INTEGRATION RULES

| Issue | Resolution |
|-------|------------|
| **Keep-alive override** | OWUI sends per-request `keep_alive` → overrides server. Set in UI per-model to `-1` or `30m`. |
| **Task model reload** | Title/tag generation uses different keep_alive → reloads model. Workaround: match OWUI = Ollama = same value. |
| **num_ctx trap** | OWUI pre-fills 2048. **Leave blank** to inherit `OLLAMA_CONTEXT_LENGTH=8192`. |
| **Connection pooling** | Random LB across multiple Ollama URLs. Single host = no benefit. |
| **Timeout** | Default 10s. Lower if multi-host for faster failover. |

---

## 8. BENCHMARK HISTORY & REGRESSION GUARDS

### Thread Sweep (Ground Truth)
| Threads | AllowedCPUs | phi4-mini t/s | Notes |
|---------|-------------|---------------|-------|
| 6 | 0-11 | 14.0 | Physical P-cores only |
| **8** | **0-11** | **14.4** | **PEAK** |
| 10 | 0-11 | 14.17 | +2 E-core threads |
| 12 | 0-11 | 13.88 | All HT |
| 6 | 0,2,4,6,8,10 | **~0.5** | **TRAP — spin-wait convoy** |

### Model Comparison (2026-09-08, 2 prompts, warm)
| Model | Avg t/s | Note |
|-------|---------|------|
| **phi4-mini** | **13.5** | Fastest, smallest |
| qwen2.5-coder:7b | 7.1 | Prompt 1 cold: 3.2 t/s |
| deepseek-r1:8b | 6.8 | Reasoning tokens; prompt 1: 6.5 t/s |

### Regression Tests (Run Before Any Config Change)
- [ ] `make bench MODEL=phi4-mini PROMPTS=3 WARM=1` → expect ~13.4 t/s
- [ ] `ollama ps` → resident ~3.2 GB, TTL ~29 min
- [ ] `free -h` → available > 8 GiB, swap ~0
- [ ] `cat /proc/<llama-pid>/cmdline` → verify `--cache-type-k q8_0 --flash-attn on -c 8192`

---

## 9. UPGRADE ROADMAP (Prioritized)

| # | Upgrade | Effort | Expected Gain | Prerequisites |
|---|---------|--------|---------------|---------------|
| 1 | **THP madvise** (sysctl + grub) | Low | Eliminate khugepaged stalls | None |
| 2 | **ZRAM 8GB zstd** (systemd + sysctl) | Low | Absorb peaks, zero swap I/O | None |
| 3 | **OWUI Keep Alive = -1** (UI) | Low (manual) | Fix 10-min TTL, prevent reloads | OWUI accessible |
| 4 | **BIOS verify** (Speed Shift, Turbo, EPP) | Low | Sustained turbo | Reboot |
| 5 | **10-min thermal bench** | Medium | Validate no throttle | turbostat |
| 6 | **Q5_K_M for deepseek-r1** | Low | Better tool calls | Pull model |
| 7 | **32GB DDR5-5600 dual-channel** | High ($$) | **+52-58% token gen** → ~20-22 t/s | Buy matched stick |
| 8 | **KV q4_k** (when upstream) | Medium | Save ~0.4 GB more KV | llama.cpp merge |

---

## 10. FILES & LOCATIONS (Source of Truth)

| File | Purpose | Updated |
|------|---------|---------|
| `docs/HARDWARE.md` | Canonical machine spec | 2026-09-08 |
| `docs/BENCHMARKS.md` | All benchmark data | 2026-09-08 |
| `docs/SYSTEM_GUIDE.md` | **This file — living guide** | 2026-09-08 |
| `.env.ollama` | Ollama env source of truth | 2026-09-08 |
| `/etc/systemd/system/ollama.service.d/override.conf` | Live Ollama config | 2026-09-08 |
| `docker-compose.yml` | OWUI stack (pinned v0.11.3) | 2026-09-08 |
| `Makefile` | Harness targets | 2026-09-08 |
| `docs/GNOSIS_USAGE.md` | Gnosis Lock usage (shell funcs + make) | 2026-09-09 |
| `docs/models/` | Model research registry + model cards | 2026-09-11 |
| `~/.bash_aliases` | Funcs: `gnosis-lock`, `gnosis-stats`; alias `oc` | 2026-09-09 |
| `~/.config/opencode/opencode.jsonc` | OpenCode config (with MCP) | 2026-09-08 |
| `~/.config/opencode/agent/gaming-expert.md` | Sibling agent (CPU fixed) | 2026-09-08 |

---

## 11. KNOWN TRAPS (DO NOT REGRESS)

| Trap | Symptom | Root Cause | Prevention |
|------|---------|------------|------------|
| **P-core-only pin** | 0.5 t/s | llama-server 29 threads on 6 cores → spin-wait barrier convoy | Keep HT siblings (0-11) |
| **MAX_LOADED_MODELS=2** | Swap thrash, cold dips | 11.3 GB resident > 16GB single-channel headroom | Keep = 1 |
| **OWUI num_ctx=2048** | Silent truncation, tool-call failures | Overrides server 8192 | Leave unset in UI |
| **OWUI keep-alive default** | 10-min TTL despite server 30m | OWUI per-request override | Set per-model in UI |
| **ZRAM + ZSWAP together** | Memory pressure, conflicts | Both fight for pages | Pick ONE |
| **isolcpus/nohz_full** | Breaks Thread Director | Hybrid CPU needs HW-guided scheduling | Don't use |

---

## 12. SESSION LOG (Append-Only)

> Entries in this section are historical records captured on their stated dates.
> They intentionally preserve old package versions, tool counts, and benchmark
> observations; current machine state and policy are maintained in §§1–5 and
> `docs/HARDWARE.md`.

| Date | Session | Changes | Verified |
|------|---------|---------|----------|
| 2026-09-08 | Initial deep research + config | HARDWARE.md, BENCHMARKS.md, SYSTEM_GUIDE.md created; Ollama KV q8_0 + flash-attn applied; MAX_LOADED_MODELS=1; OWUI pinned v0.11.3; cold backup taken | Bench: 13.4 t/s, 3.2 GB resident, 9.2 GiB avail |
| 2026-09-08 | Exa research integration | MCP servers configured (websearch=Exa, context7, grep_app); BIOS/PL1/PL2/zram/THP deep research completed | Pending: THP/ZRAM apply, OWUI keep-alive UI, thermal bench |
| 2026-09-09 | Gnosis Lock Protocol v1.0 | 8-step ritual + evolution log + identity + hooks-handler built & tested; **`hooks` config key confirmed ABSENT in OpenCode v1.18 — but PLUGIN EVENTS are the correct hook mechanism (CORRECTED 2026-09-10: `session.*`, `experimental.session.compacting`, etc. — see WANDERGROUND_SPEC §10.1)**; **no CLI compaction exists — `/compact` is TUI-only**; shipped `~/.bash_aliases` (`gnosis-lock`, `gnosis-stats`, `oc` alias) + Makefile targets (`gnosis-lock`, `gnosis-stats`) + `docs/GNOSIS_USAGE.md`; stale `hooks` config and fake `oc compact`/`compact-gnosis` removed | Verified: ritual 8/8, funcs load in interactive shell, make targets run |
| 2026-09-09 | **Review fixes P0+P1** (system audit) | `git init` (git_state captures real data); ritual **Step 4 system_state rebuilt in Python + JSON-validated**, **new Step 9 logs SESSION_END** → ritual now **9-step**; `scripts/backup_harness.sh` + daily cron; instruction-stack de-dup (HARDWARE loaded once per project); SSOT sync (`api.exa.ai`, Big Pickle 1M block in HARDWARE/AGENTS); gnosis docs consolidated (STATE_FORMAT → Protocol Appendix A, OPENCODE_HOOKS → stub) | Verified: SESSION_END in stats (2→3 events), backup secret-clean, cron installed, 2 git commits |
| 2026-09-10 | **Federation LIVE — first contact** | omega-hub at `192.168.10.168:8016` connected from ASUS; full probe pass: HP stats, 28 entities, 10 GGUF models, hivemind history; **first-contact handoff completed by roc_racoon**; sovereignty ratio measured (21.6% local); outside-consultant report shipped (`11_CONSULTANT_REPORT.md` — 8 flaws incl. sovereignty contradiction, 45 stale handoffs, broken tool surfaces); comms contract v0.9 (`12_COMMUNICATION_PROTOCOLS.md`); client tool curation config; USB packet updated (identity 17) | Verified: probe battery all live; packet 14 docs/161 files; secrets clean |
| 2026-09-10 | **🧭 The WanderGround launches (Node 1 = exploration node)** | `docs/WANDERGROUND_SPEC.md` v1.0 (architecture, 5-domain registry, model-assignment matrix: local = light tasks only, cloud frontier via OpenCode Zen = synthesis); `~/WanderGround/` scaffolded + git repo `97de8bf`/`2a45792`; **`wander` CLI** (frictionless capture, `-d <domain>`, auto-triggers curator) + PATH wiring; **Knowledge Atlas** (`sqlite-vec` vec0 768-dim, `nomic-embed-text` embeddings verified, cosine search); **3D pipeline** (`project_umap_3d.py` — UMAP N≥8 / PCA fallback, KMeans, 100-sphere; graceful guard for scipy `k>=N` edge case); **offline Three.js constellation viewer** (`:8088`, vendored assets, click-to-open dossier); **background curator** (systemd user service + 30-min timer, verified exit 0 @ 223.8MB peak); MkDocs encyclopedia mirror (wiki-sync, 2.8M site builds clean); env decision: NO local deep-synthesis models — heavy work stays on OpenCode Zen (Nemotron 3 Ultra / MiMo V2.5 / Muse Spark / Big Pickle) | Verified: ingest → embed → archive → sqlite-vec → 3D → viewer JSON end-to-end with 3 live concepts; timer armed; site 200s served; secrets clean |
| 2026-09-10 | **Native TUI Gnosis Lock — temple-grade reflection** | **REJECTED `!` shell-interp + sentinel-error hacks** (zero-throw, zero-bloat, zero fake errors, CODE_QUALITY §2); shipped **`/gnosis-lock` command + `gnosis-lock` skill** (global `~/.config/opencode/`): runs ritual via `bash` tool, then **dynamic reflection via native `question` tool** (3 core: Decision/Pattern/Gnosis + unlimited session-specific, no cap), writes `narrative.md`, commits `gnosis/`; **hardened `gnosis-leash.js`** → `readLatestNarrative()` injects YOUR reflection into compaction prompt, logs `has_narrative`; `make gnosis-leash-status` watchdog verifies plugin + skill + command + runbook; committed `4f7ecde` | Verified: skill+command registered, 24/24 tests green, `make lint` clean, watchdog exit 0 |
| 2026-09-10 | **Agent awareness audit — runbook + instruction surfaces** | **`docs/AGENT_RUNBOOK.md`** created (canonical Node 1 ops: gnosis-lock flow, `/compact` standalone rule, prepare-for-compaction orchestration, WanderGround, Zen privacy, quality gates, architecture, source-of-truth ladder); **`~/.config/opencode/AGENTS.md`** + project **`AGENTS.md`** + **`prompts/build.md`** updated with gnosis-lock/leash/runbook awareness; **`opencode.json` instructions** += `AGENT_RUNBOOK.md` + `CODE_QUALITY.md`; **`WanderGround/INDEX.md`** (injected every session by plugin) now points at runbook; **`docs/GNOSIS_USAGE.md`** clarified `/gnosis-lock` (primitive) vs "prepare for compaction" (orchestration) vs `/compact` (standalone, tested); fixed SKILL.md Step 6 `/compact <reason>` bug; README docs index += AGENT_RUNBOOK + GNOSIS_USAGE; watchdog + tests aware of runbook (25 tests green) | Verified: `make lint` ✓, 25/25 tests ✓, `make docs` ✓, `make gnosis-leash-status` exit 0 (runbook OK) |
| 2026-09-11 | **Narrative fallback + NO-SILENT-FAILURES** | Hydration test after compaction exposed a real gap: the ritual's `current_session` stamps a fresh TODO template moments before `/compact`, so the plugin skipped it with NO fallback → `has_narrative: false` silently. Fix: `readLatestNarrative()` inserts a loud `⚠️ GNOSIS-LOCK INCIDENT` block INTO the compaction prompt when no narrative exists + structured diagnostic to `gnosis-errors.jsonl`; timeline gains `narrative_source`/`narrative_reason`; watchdog exits 1 on missed narrative; ritual now carries `entity`/`channel`/`phase` + auto-fills CLI narrative (Step 6.5) | Commits `766a84b` + `f49d0ca`; 31 tests green |
| 2026-09-11 | **The Pack lifecycle — state machine + leash check** | User's insight: the blank TODO is a *signal*, not garbage — track ingestion state explicitly. Implemented: **pack lifecycle** `CAPTURED → REFLECTED → COMPACTED` with `manifest.reflection_status` + `identity.pending_pack` (the leash); **ritual Step 0 leash check** refuses a second pack while one is un-reflected (`FORCE_PACK=1` override); **skill Step 4b** flips pack to reflected + clears leash; **plugin** prefers REFLECTED packs via `packStatus()` + `findLatestReflectedNarrative()`; **`make gnosis-ledger`** (pause_ledger.py) prints full pack states + timestamps; identity now *preserves* achievements/open_quests (Python mutator — the "living document" stops being hardcoded); `ready_for_compaction` now honest (false until reflected) | Verified suite 33 tests green; leash block + force + reflect cycle tested live; ledger degraded-consistent (22 historical CAPTURED packs are true signals) |
| 2026-09-11 | **Priority stack + Ponytail/Headroom** | Added runbook §9 priority stack: **Ponytail** (`DietrichGebert/ponytail` — lazy-senior-dev OpenCode plugin, ~54% less code, /ponytail-review + /ponytail-audit) to attack the over-engineering/cognitive-tax loop; **Headroom hook-in** (omega-hub `headroom_retrieve` exists, nothing local consumes it yet); mempalace re-verify; Node 0 federation; sudo revert; content runway | — |
| 2026-09-11 | **🗺️ Roadmap — the single ordered backlog** | **`docs/ROADMAP.md`** created (P0 pulse, P1 **The Well** corrections/tuning corpus, P1.5 idea-flood, P2 Vanguard studies — Headroom, Odysseus upload/beam-back, God's Eye View, Gods Eye, agentmemory — P3 synthesis + federation); standing rule: ideas enter ROADMAP with a status BEFORE implementation; wired into README docs index, `make docs` gate, `test_repo_hygiene` EXPECTED_DOCS, project + global AGENTS.md, runbook §9 now points at ROADMAP; vanguard research confirmed: **Odysseus = PewDiePie** (87k★, AGPL, opencode+MCP, ChromaDB/fastembed memory+skills), **God's Eye View** = Bilawal Sidhu spy-sat sim (8.3k★, MIT), **Gods Eye** = bitan-del multi-channel AI gateway (MIT), **Headroom** = context compression + `headroom learn` corrections (68.8k★, Apache-2.0) | Commit `183916e`; 33 tests green, docs/lint clean |
| 2026-09-11 | **🔱 Prepare-for-Compaction R1 — roadmap-first ratified** | Full orchestration: ritual capture (`session-…05-04-58Z`, identity #24) → dynamic human reflection via question tool (**roadmap-first is ALWAYS right**, **one continuous thread**, **capture, don't suppress**) → narrative → pack REFLECTED + leash cleared → gates green → commit `11aa2f2`; test caught `ready_for_compaction` still false after reflection → **SKILL Step 4b fixed** to flip `reflection_status` + `reflected_at` + `ready_for_compaction = true` together (readiness contract: captured=not-ready, reflected=ready) | 33 tests green; pack #24 reflected+ready |
| 2026-09-11 | **🔱 Prepare-for-Compaction R2 — the full loop, always** | User caught TWO skips in R1: docs step was not updated, and a second work round deserved its own gnosis capture. Lesson codified in runbook §1.4: **the full loop, always** — capture → reflect → docs → lint → test → commit, in order, no skipped steps; "discipline is enforced, not assumed". R2 executed completely: fresh capture (`session-…05-13-41Z`, identity #25) → reflection (**orchestration discipline matters**, **discipline is enforced**, **the full loop always**) → narrative → pack REFLECTED+ready → **docs actually updated** (GNOSIS_USAGE lifecycle readiness, runbook §1.4 full-loop + §1.6 readiness contract, SYSTEM_GUIDE rows) → gates → commit | 33 tests green; packs #24+#25 reflected+ready; tree clean |
| 2026-09-11 | **✅ P0.1 mempalace MCP smoke test PASSED** | Hydration after compact #1: watchdog **HEALTHY** (P0.3 effectively met — narrative injected this compact). MCP bridge verified live end-to-end: `initialize` (3.9.0) → `tools/list` = **42 tools** → `mempalace_search` returned 20 real results (62 drawers, full provenance). **Tool-name drift documented**: the query tool is `mempalace_search`, not `palace_query` (pre-3.x name). | P0.1 gate met; next: P0.2 pack triage |
| 2026-09-11 | **✅ P0.2 legacy pack triage DONE** | `scripts/compaction/migrate_legacy_packs.py` (dry-run by default, `--apply` to write): rewrites legacy manifests lacking `reflection_status` — 10 `superseded` (harness-test artifacts: fake ids `--session-id`/`test-session-002`/`hook-test-002`/`real-compact-test` + ritual self-verification reasons), 12 honestly `captured` with `triage_at` provenance, 3 already-explicit never demoted. `pause_ledger.py` now distinguishes triaged captures (acknowledged, printed as `note:`) from untriaged loose ends (degraded) → **PAUSE LEDGER CLEAN**. 3 new `TestLegacyPackMigration` tests (dry-run runs, no implicit states, reflected never demoted). | commit `2abca7e`; 36/36 tests; all P0 except Ponytail |
| 2026-09-11 | **⏳ P0.4 Ponytail install PARTIAL (needs restart)** | Cloned `~/Vanguard/ponytail@356918e`; **hook-trust review PASSED** — only 2 lifecycle hooks: `experimental.chat.system.transform` (append-only ruleset, honors `off`) + `command.execute.before` (scoped `/ponytail` mode writes); benign. Registered absolute-path `.mjs` in `opencode.json` `plugin`; coexist verified statically (both gnosis-leash + ponytail transforms append to `output.system`). **Remaining**: live `/ponytail-help`, first `/ponytail-review`, watchdog-still-green check — after next opencode launch. | P0.4 gate partially met; runbook §5.1 documents |
| 2026-09-11 | **✅ P1.1 The Well storage & schema DONE** | `scripts/well_storage.py` (schema: record_id, ts, kind, source_pack, domain, trigger, rule, rationale, tags, status, superseded_by); lifecycle CAPTURED→ACTIVE→SUPERSEDED; append-only `gnosis/well/well.jsonl` + rendered `WISDOM.md`; CLI + Makefile targets: `well-add|well-list|well-stats|well-supersede|well-export`; 7 tests (valid JSONL, secret rejection, supersession chain, index parity, UTF-8, stats, Make targets); 43/43 tests green. | commit + ROADMAP P1.1 done |
| 2026-09-11 | **✅ P1.2 The Well writers DONE** | `SKILL.md` Step 4c added (agent extracts actionable rules from narrative + runs `make well-add` with `PACK="${SESSION_ID}"`); CLI targets exist and tested. | commit `8b7e8fa` |
| 2026-09-11 | **✅ P1.3 The Well readers DONE** | `gnosis-leash.js` updated: `experimental.chat.system.transform` injects top-6 Well records (harness, local_ai) at session start; `experimental.session.compacting` injects top-8 (harness, local_ai) into compaction summary. Both use `readWellForInjection()` + `formatWellBlock()`. `well-export` = `make well-export` renders `WISDOM.md` + JSONL bundle. 43/43 tests green. | commit `7fa1556` |
| 2026-09-11 | **✅ P1.4 The Well evolution (supersession) DONE** | `supersede()` marks old record superseded + links to new; `get_active()` filters `status=active` so injection (plugin + `make well-list`) excludes superseded; test `test_well_supersession_resolves` proves chain resolves + superseded drops from active list + WISDOM.md. | commit `ad76b33` |
| 2026-09-11 | **✅ P1.5 Idea-flood management DONE** | `kind:dream` in Well works, renders in `WISDOM.md`, excluded from injection (only harness/local_ai domains injected). Promotion to ROADMAP is manual via `docs/ROADMAP.md` edit (the canonical backlog). | P1.5 gate met; all P1 done |
| 2026-09-11 | **❌ P2.1 Headroom REJECTED** | Well-built, but benefits don't apply to local inference: zero token cost (local Ollama), 1M context = no pressure, CPU-constrained pipeline (14.4 t/s) would add latency tax. Prompt-cache busting penalty (39% more expensive on metered APIs) doesn't apply locally but doesn't help either. | Verdict: REJECTED; dossier for credit only |
| 2026-09-11 | **❌ P2.5 agentmemory REJECTED** | Does NOT beat MemPalace on retrieval (95.2% vs 96.6% R@5 LongMemEval-S). MemPalace already integrated (62 drawers, 8 rooms, MCP verified). AgentMemory's viewer/4-tier lifecycle/multi-agent coordination are YAGNI for single-machine workflow. | Verdict: REJECTED; MemPalace remains primary |
| 2026-09-11 | **✅ P2 complete** | All vanguard tools evaluated with documented verdicts: Headroom REJECTED, agentmemory REJECTED, Odysseus scheduled future, God's Eye View + Gods Eye toys. Phase table updated (P2 ✅ done). | ROADMAP phase table updated |
| 2026-09-11 | **✅ P3.1 Architecture synthesis DONE** | `ARCHITECTURE.md` + `AGENT_RUNBOOK.md` updated: The Well + Ponytail + Well injection in gnosis-leash + Ponytail LIVE + The Well §5.2 spec + vanguard verdicts + priority stack → P3 active. De-duplication: no overlapping tiers (Well corrections + MemPalace knowledge + gnosis-lock packs = distinct layers). All docs cross-reference ROADMAP as canonical backlog. | 43/43 tests, lint+docs clean; commit `546dc03` |
| 2026-09-11 | **✅ Model research registry + Nex-N2.5-Pro card** | Added `docs/models/README.md` (lifecycle, evidence labels, card contract, template) and `docs/models/nex-n2-5-pro.md` (metadata, strengths, quirks, provider-benchmark caveats, Omega verdict, OpenRouter recipe, validation plan). Linked from README, architecture, runbook, ROADMAP, and session log; `test_repo_hygiene` now requires the registry. | Registry/card docs pass link checks; Nex remains `candidate` pending local A/B |
| 2026-09-11 | **🔄 P3.2 Node 0 federation ACTIVE (blocked)** | Tailscale not installed on either node; C6 comms-contract not ratified; key-management pattern + publish gate design incomplete. HP `omega-hub` reachable via LAN; Redis Pub/Sub designed but not live. | Next: Tailscale install + C6 ratification |

---

## 13. NEXT ACTIONS (Immediate)

Status verified 2026-09-23:
- ✅ **THP madvise** — runtime is `[madvise]`; GRUB persistence is configured.
- ✅ **ZRAM 8GB class zstd** — `/dev/zram0` is active at priority 100; `vm.swappiness=100`.
- ✅ **NVMe swap disabled** — `/swap.img` remains on disk for rollback but is not active or in `/etc/fstab`.
- ⏳ **OWUI Keep Alive = -1** per model (UI manual step) — still pending.
- ⏳ **10-min thermal bench** with turbostat logging — still pending.
- ⏳ **BIOS settings verify** — still pending (next reboot).

New priority queue (federation era):
6. **HP response awaited** — `RESPONSE_FROM_HP.md` (F1–F7 in `10_ACTIONS_FOR_HP.md`); then ratify `12_COMMUNICATION_PROTOCOLS.md` with the council
7. **Apply client-side tool curation** on next session start (`ASUS-build-curated-tools.json` → `opencode.json` `tools` block) — cuts ~90 → ~50 hub tools
8. **Fix/flag the 3 broken hub surfaces** (HP-side, C1): `oracle_list_pillar_keepers`, library gemma_768 default, continuation lookup
9. **Sovereignty policy write-up** (per consultant S1/C4) — set per-task-class local/cloud targets; ASUS is 100% local exemplar
10. **Package refresh cadence** — after every meaningful session, re-sync USB packet evidence (identity/evolution/sessions)

---

---

## 14. MCP SERVER USAGE GUIDE (Exa, Context7, Grep.app)

### 14.1 Architecture Overview

OpenCode includes **three built-in remote MCP servers** (no config needed, always on):

| MCP Server | Based On | Purpose | Invocation |
|------------|----------|---------|------------|
| `websearch` | **Exa** | Neural web search — current info, code examples, company intel, people lookup | `use websearch` or automatic |
| `context7` | **Context7** | Official library docs — version-specific, hallucination-free | `use context7` |
| `grep_app` | **Grep.app (Vercel)** | GitHub code search — real production patterns across public repos | `use grep_app` or `use gh_grep` |

**Key insight:** These are HTTP remote MCPs. They add tools to the agent's context. For token budget management, only invoke when needed.

---

### 14.2 Exa Web Search — MCP REMOVED 2026-09-18, direct API live

> **Status change**: the `websearch` MCP (old URL `https://api.exa.ai/mcp` → 404;
> correct endpoint `https://mcp.exa.ai/mcp`) was **removed from both
> `opencode.json` and `opencode.jsonc`** per operator directive. There is no
> native Exa/search tool in OpenCode (verified CLI + docs) — web research now
> flows through the replacements below. `EXA_API_KEY` is live (validated
> `/search` HTTP 200) and consumed by `scripts/exa_search.py`.

**Replacement 1 — `scripts/exa_search.py` (committed, no MCP needed):**
```bash
python3 scripts/exa_search.py search "query" [--num 5]
python3 scripts/exa_search.py fetch <url> [--chars 6000]
```
Reads `EXA_API_KEY` from env / `~/.config/opencode/.env`. Key never printed.

**Replacement 2 — `parallel-search` MCP** (via `scripts/parallel_bridge.py`,
connected): `web_search` + `web_fetch` tools in-session.

**Replacement 3 — `firecrawl` MCP** (`https://mcp.firecrawl.dev/v2/mcp`,
connected): `firecrawl_search` / `scrape` / `parse`.

**Legacy configuration (REMOVED — kept for archaeology):**
```json
{
  "mcp": {
    "websearch": {
      "type": "remote",
      "url": "https://api.exa.ai/mcp",
      "enabled": true,
      "headers": {
        "Authorization": "Bearer {env:EXA_API_KEY}"
      }
    }
  }
}
```

**Environment variable (optional, for higher rate limits):**
```bash
export EXA_API_KEY="your_key_from_dashboard_exa_ai"
# Or in shell profile: echo 'export EXA_API_KEY=...' >> ~/.bashrc
```

**Available Tools:**
| Tool | Description | Best For |
|------|-------------|----------|
| `web_search_exa` | General web search, clean LLM-ready content | Current info, news, facts, broad discovery |
| `web_fetch_exa` | Full page content as clean markdown from known URL | Deep reading specific pages |
| `web_search_advanced_exa` | Advanced: domains, date ranges, categories, highlights | Precision research, source filtering |
| `agent_run` | Multi-step Exa Agent (async research, list-building) | Complex multi-query tasks |

**Prompt Patterns:**
```text
# Basic search
Search for the latest Ubuntu 26.04 kernel version. use websearch

# Code/API lookup
Find official llama.cpp KV cache quantization docs. use websearch

# Company/people research
Research Exa AI company and team. use websearch

# Advanced: constrain to domain
Search site:github.com/ggml-org/llama.cpp for "flash attention" implementation. use websearch

# With context7 combo
How to configure Cloudflare Workers KV? use context7
```

**Exa Search Types (via `type` param):**
| Type | Speed | Best For |
|------|-------|----------|
| `auto` | ~1s | Default, balanced |
| `instant` | ~250ms | Real-time apps |
| `fast` | ~450ms | Speed with quality |
| `deep-lite` | ~4s | Lightweight synthesis |
| `deep` | 4-15s | Multi-step reasoning |
| `deep-reasoning` | 12-40s | Hard research tasks |

**Rate Limits:** Free tier generous; `EXA_API_KEY` raises limits for production.

---

### 14.3 Context7 (`context7`)

**Configuration:**
```json
{
  "mcp": {
    "context7": {
      "type": "remote",
      "url": "https://mcp.context7.com/mcp",
      "enabled": true
    }
  }
}
```
*(Optional: add `CONTEXT7_API_KEY` header for higher rate limits / private repos)*

**Purpose:** Fetches **version-specific, official documentation** directly into context. Eliminates hallucinated APIs and outdated examples.

**Invocation:**
```text
Create a Next.js middleware that checks for a valid JWT in cookies and redirects unauthenticated users to /login. use context7

Configure a Cloudflare Worker script to cache JSON API responses for five minutes. use context7

How to use drizzle-orm transactions with PostgreSQL? use context7

Show me the latest TanStack Query v5 migration guide. use context7
```

**Workflow:**
1. Write prompt naturally
2. Add `use context7`
3. Get working code with current APIs

**When to use:** Any library/framework question — React, Next.js, Cloudflare, Drizzle, TanStack, etc.

---

### 14.4 Grep.app (`grep_app` / `gh_grep`)

**Configuration:**
```json
{
  "mcp": {
    "grep_app": {
      "type": "remote",
      "url": "https://mcp.grep.app",
      "enabled": true
    }
  }
}
```
*(Naming it `gh_grep` allows `use gh_grep` in prompts)*

**Purpose:** Literal/regex code search across **millions of public GitHub repos**. Find real production patterns, not tutorials.

**Invocation:**
```text
# Pattern search
use gh_grep to search for "useTransition" usage in React 19 codebases. Find the 3 most common patterns.

# Library usage in production
search github via gh_grep for examples of "drizzle-orm" with "transaction" — show me how production codebases structure transactions.

# Framework patterns
use gh_grep to find how big public Tailwind v4 projects organize their theme tokens. Pull 3 examples I can browse.

# Compare patterns
use gh_grep to count occurrences of useFormState vs useActionState in production React codebases (Next.js 15+). Report the ratio and top 5 examples for each.

# Specific repo
use gh_grep to search for "createContext" in facebook/react repo.

# Authentication patterns
use gh_grep to find production NextAuth.js v5 implementations with credentials provider. Filter by TypeScript.
```

**Search Parameters (exposed via tool):**
| Parameter | Description |
|-----------|-------------|
| `query` | **Required** — literal code pattern (e.g., `useState(`, `export function`) |
| `language` | Comma-separated: `TypeScript,TSX`, `Python`, `Rust` |
| `repo` | Filter by repo: `facebook/react`, `vercel/next.js` |
| `path` | Filter by file path: `src/components/` |
| `match_case` | Case-sensitive (default: false) |
| `match_whole_words` | Whole words only (default: false) |
| `use_regexp` | Interpret query as regex (default: false) |

**Gotchas:**
- **Public only** — private repos invisible
- **Quality varies** — half GitHub is side projects; filter by popular repos
- **Literal/regex only** — not semantic "code that does X"; be precise
- **Intermittent availability** — `mcp.grep.app` sometimes unreachable; retry

**Best Queries:** Actual code syntax (`useEffect(() =>`, `async function`, `getServerSession(`) — NOT keywords (`react tutorial`, `best practices`, `how to use`).

---

### 14.5 MCP Management Commands

```bash
# List configured MCPs and auth status
opencode mcp list

# Authenticate OAuth-based MCPs (e.g., Sentry)
opencode mcp auth sentry

# Debug connection issues
opencode mcp debug <server-name>

# Remove stored credentials
opencode mcp logout <server-name>

# Add MCP interactively (wizard)
opencode mcp add
```

---

### 14.6 Token Budget Management

**Critical:** MCP servers add significant context tokens. From Scott Spence's optimization:

| Scenario | MCP Tools Tokens | Free Space |
|----------|------------------|------------|
| All MCPs enabled (empty convo) | 82k (41%) | 12k (5.8%) |
| Only `mcp-omnisearch` (consolidated) | 5.7k (2.8%) | 88k (44%) |

**Instruction stack cost (what we load every session, pre-MCP, measured
2026-09-09):** `AGENTS.md` (global+project) + `HARDWARE.md` + `SYSTEM_GUIDE.md`
+ `BENCHMARKS.md` ≈ **13.5K tokens** (~52KB). Its share of usable context depends
on the selected model's live metadata, so keep the stack lean across every cloud
model. HARDWARE.md is loaded once per project (de-duplicated 2026-09-09; the
global config no longer also loads it).

**Best Practices:**
1. **Disable unused MCP servers** in `opencode.json`:
   ```json
   "mcp": { "example": { "enabled": false } }
   ```
2. **Use per-agent permission rules** for tool access (never the deprecated
   `tools` block):
   ```json
   "permission": { "websearch": "deny" },
   "agent": {
     "my-research-agent": {
       "permission": { "websearch": "allow" }
     }
   }
   ```
3. **Invoke explicitly in prompt** (`use context7`) rather than relying on auto-invocation
4. **Consolidate similar tools** — one search tool with provider param vs multiple
5. **Semantic write-through over context hoarding.** The context window is a volatile
   CPU register; MemPalace is durable RAM. After every decision, discovery, or batch
   completion, persist state to MemPalace/Event Log. Compaction becomes ordinary
   cache eviction — no ceremony, no `prepare for compaction` ritual.

---

### 14.7 Skill-Embedded MCPs (Advanced)

Skills can embed their own MCPs that **spin up on-demand** and **disappear when done**:

| Skill | Embedded MCP | Purpose |
|-------|--------------|---------|
| `playwright` | Browser automation | Screenshots, E2E tests, scraping |
| `git-master` | Git operations | Atomic commits, rebase surgery |

**Custom skills** at:
- Project: `.opencode/skills/*/SKILL.md`
- User: `~/.config/opencode/skills/*/SKILL.md`

Each skill defines its own MCP server definition + scoped permissions.

---

### 14.8 Current Config (Verified 2026-09-23 — 5 connected)

> Discovery 2026-09-18: opencode merges **`opencode.json` + `opencode.jsonc`**
> (both in `~/.config/opencode/`). A stale `websearch` entry survived in
> `opencode.jsonc` after removal from `opencode.json` — always check both.

// ~/.config/opencode/opencode.json
{
  "mcp": {
    "parallel-search": { "type": "local", "command": ["<repo>/scripts/parallel_bridge.py"], "enabled": true },
    "mempalace": { "type": "local", "command": [".../mempalace-mcp", "--palace", "..."], "enabled": true },
    "firecrawl": { "type": "remote", "url": "https://mcp.firecrawl.dev/v2/mcp", "enabled": true,
                   "headers": { "Authorization": "Bearer {env:FIRECRAWL_API_KEY}" } }
  },
  "tools": { "mempalace_*": true, "parallel-search_*": true, "firecrawl_*": true }
}
// ~/.config/opencode/opencode.jsonc
{
  "mcp": {
    "context7": { "type": "remote", "url": "https://mcp.context7.com/mcp", "enabled": true },
    "grep_app": { "type": "remote", "url": "https://mcp.grep.app", "enabled": true }
  }
}
```

**Current MCP inventory:** `parallel-search`, `mempalace`, `firecrawl`,
`context7`, and `grep_app` are connected. Exa is not currently configured as
an MCP server; use the direct Exa script only if that route is explicitly
reintroduced.

**Test commands:**
```bash
opencode mcp list          # Should show 5 connected servers
opencode run "Search for latest Rust 1.81 features. use context7"
opencode run "How to use Axum extractors? use context7"
opencode run "Find production Axum middleware examples. use grep_app"
```

---

## 15. P2P OMEGAVERSE FEDERATION (Node 0 ↔ Node 1)

### 15.1 Architecture Overview

| Node | Role | Hardware | Key Service |
|------|------|----------|-------------|
| **Node 0 (HP)** | Archival Bastion & Nexus | AMD Ryzen 7 5700U, 16GB DDR4-3200 dual-channel, Ubuntu 25.10 | `omega-hub` (FastMCP, 55 tools live 2026-10-07, Streamable HTTP on `:8016`) |
| **Node 1 (ASUS)** | Compute Vanguard | Intel i7-13620H, 16GB DDR5-5200 single-channel, Ubuntu 26.04 | Bare-metal Ollama, Open WebUI, OpenCode client |

### 15.2 Wire Protocols

| Layer | Transport | Binding | Status |
|-------|-----------|---------|--------|
| **1. Local LAN** | Streamable HTTP (`POST /mcp`) | `192.168.10.168:8016/mcp` | Phase 0 — Immediate |
| **2. Tailscale Mesh** | WireGuard via MagicDNS | `hp.tailnet:8016`, `asus.tailnet` | Phase 1 — Planned |
| **3. Redis Pub/Sub** | High-frequency heartbeats | Ephemeral event bus | Phase 2 — Future |

### 15.3 Hivemind Channel Partitioning

| Node | Agent Persona | Channel | Function |
|------|---------------|---------|----------|
| HP (Node 0) | `@roc_racoon` | `opencode` | Legacy mining, DHAL, hardware forensics |
| HP (Node 0) | `@kali` / `@makali` | `opencode` | Council synthesis, debut release, law |
| HP (Node 0) | `@grokster` | `grokster` | OpenCode CLI internals, cross-platform KB |
| ASUS (Node 1) | `asus_build` | `opencode-asus` | Bare-metal compile, Ollama benchmarking |
| ASUS (Node 1) | `asus_plan` | `opencode-asus` | Hardware profiling, local workload planning |

### 15.4 4-Way Handoff Contract

```
[ASUS: asus_build]                            [HP: roc_racoon]
        │                                             │
        │ 1. hivemind_post_context(channel, intent)   │
        ├────────────────────────────────────────────►│ (Context stored in HALL_OF_RECORDS)
        │ 2. hivemind_submit_handoff(target="roc")    │
        ├────────────────────────────────────────────►│ (Packet written to data/handoff/pending/)
        │                                             │
        │                                             │ 3. hivemind_accept_handoff()
        │                                             │    (Packet moves to data/handoff/active/)
        │                                             │
        │                                             │ 4. hivemind_complete_handoff(result)
        │◄────────────────────────────────────────────┤    (Packet moves to data/handoff/completed/)
```

### 15.5 ASUS OpenCode Config for Federation

Federation MCP configuration is independent of model selection:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "omega-hub": {
      "type": "remote",
      "url": "http://192.168.10.168:8016/mcp",
      "enabled": true
    }
  }
}
```

Do not add `provider.opencode.models.big-pickle.limit` overrides. Big Pickle
and Space Bunny are rotating stealth aliases; their context and output limits
are mutable and node/time-dependent. See `docs/OPENCODE_FOUNDATION.md`.

### 15.6 Connectivity Verification

```bash
# Test LAN connectivity
~/test_connection.sh

# Ceremonial first contact
python3 ~/hivemind_first_contact.py

# Expected: Health check + MCP handshake + latest tool count (93 in the 2026-09-18 verification) + SSE stream
```

### 15.7 Migration Status

| Component | HP (Node 0) | ASUS (Node 1) | Status |
|-----------|-------------|---------------|--------|
| `omega-hub` | ✅ Running (55 tools live 2026-10-07) | — | Recheck live after Node 0 changes |
| OpenCode | ✅ Custom agents, skills | ✅ Fresh + USB config | Connected |
| MCP Servers | 5 (Exa, Firecrawl, omega-hub, SearXNG, parallel-search) | 7 (Exa, Context7, Grep.app, omega-hub, SearXNG, Firecrawl*) | Synced |
| Git Repo | ✅ SSOT | ⏳ Pending clone | Phase 0 |

*Firecrawl disabled on ASUS; Exa `agent_run` covers deep scraping.

---

*This guide is the single source of truth. Every tuning decision traces to a benchmark, a kernel doc, an Intel datasheet, or a ggml issue. When in doubt, re-bench.*| 2026-09-10 | **Deep research pass — definitive corrections (WanderGround)** | **OpenCode hooks CORRECTED:** plugin event system IS the hook mechanism (`session.created/idle/compacted`, full `session.next.*`, `experimental.session.compacting`) — verified in local 1.18.30 types; shipped `~/.config/opencode/plugins/gnosis-leash.js` (timeline + compaction/system-prompt injection; loads clean); **MemPalace v3.9.0 online**: `sqlite_exact` backend + hermetic `minilm` ONNX (SHA256-verified pre-seed, flaky-link safe) — 20 files → 62 drawers, hybrid search verified; `mempalace` stdio MCP wired into opencode.json; mining hygiene via `.gitignore` (SKIP_DIRS + vendor/site/docs/mempalace exclusions); **Zen privacy tier** documented (free tiers collect data — `big-pickle`, `mimo-v2.5-free`, `nemotron-3-ultra-free`, `muse-spark-*-contributor-free`; paid = zero-retention); **sqlite-vec corrected** (`distance_metric=cosine` + `k = ?` KNN syntax); **systemd linger enabled** (timer survives logout); **anyio code-quality standard** added (`docs/CODE_QUALITY.md` — absolute anyio async wiring, no bare asyncio/trio, no torch); **eyes-on-machine tooling** (`ey`, `withey` pre/post snapshots) | Verified: mine exit 0 in ~2s (62 drawers/7 rooms); MemPalace search returns correct rooms; `opencode serve` starts with plugin clean; Linger=yes; model tarball SHA256 OK |

---

## 16. HARDENED DEPLOYMENT LESSONS (2026-09-17 — SONNET 5 HARDENED v3.1)

### 16.1 Battle-Tested Fixes Catalog (Including Sonnet 5 Review)

| Failure | Root Cause | Hardening Applied |
|---------|------------|-------------------|
| **MCP server ignored** | Local servers need CLI registration | `opencode mcp add mempalace -- <cmd> <args>` after config |
| **Tools config validation error** | Object format instead of boolean | `"tools": { "parallel-search": true }` NOT `{ "enabled": true, "max_results": 15 }` |
| **Parallel.ai returns 405** | Endpoint expects POST, not GET/HEAD | Accept 405 in validation: `grep -E '200|401|405'` |
| **Venv path wrong** | Hardcoded `/home/xnai/.local/share/ov/env/` | Use `/home/xnai/WanderGround/.venv/bin/python3` |
| **Systemd "Bad message"** | Semicolons in service file | Use newlines: `Restart=always` + `RestartSec=5` (not `;`) |
| **anyio 4.x TypeError** | `abandon_on_cancel` removed | Remove parameter: `run_sync(fn, stream)` |
| **inotifywait missing** | Package not installed | `sudo apt-get install -y inotify-tools` in Phase 0 |
| **MemPalace check failed** | Checked for `mempalace.yaml` | Check `sqlite_exact.sqlite3` instead |
| **Venv path hardcoded** | Old path `/home/xnai/.local/share/ov/env/` | Use `/home/xnai/WanderGround/.venv/bin/python3` |
| **Systemd semicolons** | `Restart=always; RestartSec=5` | Use newlines: `Restart=always` + `RestartSec=5` |
| **anyio abandon_on_cancel** | Parameter removed in 4.x | Remove: `run_sync(fn, stream)` |
| **MemPalace not in mcp list** | Not registered via CLI | `opencode mcp add mempalace -- <cmd> <args>` |
| **TUI shows only mempalace, CLI shows all green** | TUI snapshots MCP state at startup; network was down then | Restart TUI — `opencode mcp list` (fresh probe) is source of truth, not the sidebar |
| **Sonnet 5 #1: Daemon to_process** | `anyio.to_process.run_sync()` for inotify — MemoryObjectStream not picklable | **FIXED: `anyio.to_thread.run_sync()`** |
| **Sonnet 5 #2: Fake verify_step** | `|| true` baked into MemPalace check command | Removed `|| true` from command strings |
| **Sonnet 5 #3: Node 0 Tailscale** | Checked Self.DNSName instead of Peer[] | Fixed to check `.Peer[]` for `xnai-n1-asus` |
| **Sonnet 5 #4: Duplicate config** | Duplicate `mempalace` key in Node 1 config | Removed duplicate `mcp.mempalace` block |
| **Sonnet 5 #5: Bashrc duplicates** | Unconditional append on every re-run | Marker guards (`# OMEGA_ENGINE_API_KEYS`) + `grep -q` |
| **Sonnet 5 #6: Backup fail** | First deploy fails (no existing config) | Guarded with `[ -f ... ] &&` |
| **Sonnet 5 #7: Bare except** | `except: pass` swallowed signals | Changed to `except Exception:` |
| **Sonnet 5 #8: No domain fallback** | Unrecognized queries filed under kernel | Added `06_general` catch-all domain |
| **Sonnet 5 #9: No circuit breaker** | Daemon crash-loop restarted forever | Added `StartLimitIntervalSec=60`, `StartLimitBurst=3` |
| **Sonnet 5 #10: Fake API keys** | Date placeholders documented as real | **Documented: placeholders must be replaced** |

### 16.2 Key Hardening Principles

1. **Never trust config-only for local MCP servers** — always register via CLI
2. **OpenCode 1.18+ tool format is boolean** — not object with nested config
3. **Accept 405 from parallel.ai** — MCP endpoint uses POST, not GET/HEAD
4. **Venv is at `~/WanderGround/.venv/`** — not `/home/xnai/.local/share/ov/env/`
5. **Systemd files need proper newlines** — no semicolons in service files
6. **anyio 4.x removed `abandon_on_cancel`** — remove parameter
7. **inotify-tools is required** — install via apt in Phase 0
8. **MemPalace palace is `sqlite_exact.sqlite3`** — not `mempalace.yaml`
9. **TUI MCP sidebar is a startup snapshot** — `opencode mcp list` is the source of truth; restart TUI after any network blip (see FL-005)

### 16.3 Deployment Validation Checklist

```bash
# Pre-deployment
opencode --version | grep -q '1\.1[89]'
opencode mcp list
tailscale status --json | jq -r '.Peer[] | .DNSName' | grep -q 'omega-hub.tail51f14a.ts.net'
curl -s -o /dev/null -w '%{http_code}' https://search.parallel.ai/mcp | grep -E -q '200|401|405'

# Post-deployment validation
opencode mcp list
systemctl --user is-active wanderground-embed.service | grep -q active
opencode run "Use the parallel-search web_search tool for a test query"
```

### 16.4 Rollback Procedures

```bash
# Config rollback
cp ~/.config/opencode/opencode.json.bak.* ~/.config/opencode/opencode.json

# Service rollback
systemctl --user stop wanderground-embed.service
systemctl --user disable wanderground-embed.service
rm ~/.config/systemd/user/wanderground-embed.service
systemctl --user daemon-reload

# Env rollback (marker-guarded cleanup)
sed -i '/# OMEGA_ENGINE_API_KEYS/,/# END OMEGA_ENGINE_API_KEYS/d' ~/.bashrc
source ~/.bashrc

# MCP server removal
opencode mcp logout mempalace 2>/dev/null || true
```

### 16.5 Deployment Scripts (Canonical)

- **Node 1:** `/home/xnai/deploy_node1.sh` — complete atomic deployment
- **Node 0:** `/home/xnai/deploy_node0.sh` — complete atomic deployment

Both scripts include:
- Phase 0: Validation + backup + venv bootstrap + inotify-tools
- Phase 1: Config with mempalace + parallel-search + CLI registration
- Phase 2: Env vars with scoped API keys
- Phase 3: System prompts with `{include:...}` syntax
- Phase 4: WanderGround directories + enhanced frontmatter
- Phase 5: Omega-hub wrapper with `CapacityLimiter(2)` + dynamic frontmatter (Node 0)
- Phase 6: anyio sidecar daemon (SimpleQueue + 0.5s poll coordination, no Event wake races) + systemd service
- Phase 7: Tailscale ACL documentation
- Phase 8: Offline cache pre-population
- Phase 9: Pre-flight validation with exit-on-failure gates

### 16.6 Post-Deployment Verification

```bash
# Full validation suite
opencode mcp list
systemctl --user is-active wanderground-embed.service
opencode run "Use mempalace_search for a test query"
opencode run "Use parallel-search web_search for a test query"

# TUI test
opencode  # select Nemotron 3 Ultra -> @asus_plan "test query"
```

### 16.7 Known Remaining Gaps (Track in ROADMAP)

- [ ] Node 0 SSH access (needs `sudo systemctl enable --now ssh` on HP)
- [ ] Tailscale ACL rule application (manual in admin console)
- [x] USB drive packet update with hardened configs (COMPLETED v3.1)
- [ ] Cross-node federation test: `@kali` on Node 0 via omega-hub
- [ ] Full thermal bench (10-min sustained) with turbostat logging
