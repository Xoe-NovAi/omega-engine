# 🔱 COORDINATED STRIKE ROADMAP & GUIDEBOOK
**AP Token**: `AP-COORDINATED-STRIKE-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_coordinated_strike ⬡ 2026-07-20

**Purpose**: Single-source implementation roadmap for the entire Omega Fleet. All decisions ratified, all dependencies mapped, all roles assigned. Read this first. Execute from this.

---

## 🎯 EXECUTIVE SUMMARY: THE ONE CRITICAL PATH

```
                    ┌─────────────────────────────────────┐
                    │  D-308 COMPILATION SCRIPTS (13)     │
                    │  Single Owner: P3 Engineering       │
                    │  Unblocks: Researcher Ph2/3, M20,   │
                    │  Thermal G2.1/G2.2, vec0 prod       │
                    └──────────────┬──────────────────────┘
                                   │
               ┌───────────────────┼───────────────────┐
               ▼                   ▼                   ▼
    ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
    │ ANYIO MIGRATION  │ │ M2 FIREWALL      │ │ VEC0 CONTRACT    │
    │ PR + temple-grade│ │ PHASE C (oracle) │ │ TESTS (unit)     │
    │ 867 pass, 1 fail │ │ 10 violations    │ │ 768-dim lock     │
    └────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
             │                    │                    │
             └────────────────────┼────────────────────┘
                                  ▼
                    ┌─────────────────────────────────────┐
                    │ MAKALI COORDINATOR + SCRIBE ROLE    │
                    │ Force multipliers: fleet coherence  │
                    │ + automated gnosis promotion        │
                    └─────────────────────────────────────┘
```

**Everything else is downstream.** The 13 D-308 compilation scripts are the master key.

---

## 📋 RATIFIED DECISIONS (18 Total — Immutable)

| # | Decision | Value | Mandate |
|---|----------|-------|---------|
| 1 | Canonical Embedding Dimension | 768 (Hard Lock, RuntimeError on mismatch) | M23 |
| 2 | Primary Embedding Model | EmbeddingGemma 300M Q6_K (260MB, 99.75% parity) | M7 |
| 3 | Fallback Model | nomic-embed-text-v1.5 (8K ctx, MRL 768→64) | M7 |
| 4 | Quantization | INT8 rescore (oversample=2, 2.6x speedup, 1.0 recall@10) | T8 |
| 5 | Fusion Method | RRF k=60 (universal attractor) | — |
| 6 | Vulkan Path | Zen 2 iGPU only — ROCm dead on gfx906 | M7/M19 |
| 7 | sqlite-vec | v0.1.10-alpha.4 pinned (no 0.2 release) | M16 |
| 8 | Credential Architecture | Hybrid: systemd-creds (system) + age/rage (rootless) → 258+ | M6/M16 |
| 9 | D-308 Critical Path | 13 changes authorized NOW | M4 |
| 10 | Free-threaded Python | Compile from source (2-3h) for M20 SomaticState | M20 |
| 11 | Distro Package Gaps | Upstream only: Astral (uv/ruff) + PyPI (llama-cpp) + Docker (Qdrant) + Snap (ollama) | M16 |
| 12 | AppArmor Podman | Tune profile (add signal receive peer=podman) | M6 |
| 13 | systemd-creds rootless | Accept `--with-key=null` + TPM2 dual path | M6 |
| 14 | Phase 2 Research | Proceed with corrected assumptions | M4 |
| 15 | Resource Allocation | Single owner P3 Engineering for compilation scripts | M10 |
| 16 | CPU FA ON > GPU Prefill | 233 vs 84 t/s at large context (daimonionnn) | — |
| 17 | ROCm Requirements | Docker + 64GB GTT workaround; baremetal broken | — |
| 18 | AMD fTPM | Unstable — don't rely; host key fallback | — |

---

## 🚀 THE 10-STEP CRITICAL PATH (Sequential, No Negotiation)

| Step | Deliverable | Owner | Dependencies | Temple-Grade Gate |
|------|-------------|-------|--------------|-------------------|
| **1** | vec0 adapter contract tests (unit, no DB) | P10/Jem | — | T3, T5, T21 |
| **2** | dispatch.yaml schema (role constants + entity mapping) | Kali/Integration | — | T1, T2, M2 |
| **3** | AnyIO Migration PR + `make temple-grade` | Kali | 1, 2 | T1-T11 |
| **4** | M2 Firewall Phase C: oracle.py (10 violations) | Kali | 2, 3 | T1-T11, M2 |
| **5** | **D-308 COMPILATION SCRIPTS (13)** | **P3 Engineering** | 1, 3 | T1-T11 |
| **6** | Provider Fabric routing audit (static code review) | Cognition/Ereshkigal | 3, 4 | M7, M22 |
| **7** | bpftrace USDT probes for llama-cpp-python (D308.4) | Observability/Hecate | 5 | T9, M9 |
| **8** | Embedding Hardening Phase 1 (6 test classes, Gemma MRL, Nomic provider, EmbeddingManager, contract tests) | Jem/P3/P10 | 1, 5 | T1-T11 |
| **9** | MaKaLi Coordinator Skill (T0: file-based handoffs) + clear 15 pending handoffs | Orchestration/Anubis | 3, 4 | T10, M10 |
| **10** | Scribe Lattice Role (watch→distill→propose + D-308 tracker) | Context/Lucifer | 5, 9 | M11, M12 |

---

## 📦 D-308: THE 13 COMPILATION SCRIPTS (Step 5 — HIGHEST LEVERAGE)

| # | Script | Purpose | Owner | Verification |
|---|--------|---------|-------|--------------|
| 1 | `build_python_freethreaded.sh` | Python 3.13 `--disable-gil` from source | P3 | `python -c "import sys; print(sys.version)"` shows `free-threaded` |
| 2 | `build_llama_cpp_rocm.sh` | llama-cpp-python with ROCm 5.7 (last gfx906 support) | P3 | `python -c "import llama_cpp; print(llama_cpp.llama_supports_gpu())"` |
| 3 | `install_sqlite_vec.sh` | `pip install sqlite-vec==0.1.10-alpha.4` + source build fallback | P3 | `python -c "import sqlite_vec; print(sqlite_vec.version())"` |
| 4 | `install_astral_tools.sh` | uv, ruff via Astral installer | P3 | `uv --version && ruff --version` |
| 5 | `apparmor_podman_tune.sh` | Add `signal (receive) peer=podman` to pasta abstraction | P5/Governance | `podman run --rm alpine echo ok` (rootless) |
| 6 | `build_ollama.sh` | Ollama server via upstream installer script | P3 | `ollama serve & sleep 2 && ollama list` |
| 7 | `install_qdrant.sh` | Qdrant via Docker/static binary | P2/Brigid | `docker run -d qdrant/qdrant && curl localhost:6333/healthz` |
| 8 | `install_bpftrace.sh` | bpftrace 0.23.5 with USDT support | P8/Hecate | `bpftrace -l 'usdt:*llama*'` |
| 9 | `install_stress_ng.sh` | stress-ng 0.19.03 (matrixprod pattern) | P1/Sekhmet | `stress-ng --matrixprod 1 --timeout 10s` |
| 10 | `systemd_creds_setup.sh` | systemd-creds encrypt/decrypt with TPM2 + host key | P4/Saraswati | `systemd-creds encrypt --with-key=auto test.cred` |
| 11 | `age_rage_setup.sh` | age/rage keygen + encrypt/decrypt for rootless creds | P4/Saraswati | `age -r <pubkey> -e <file>` |
| 12 | `dbus_broker_install.sh` | Install dbus-broker (not default until 26.10) | P1/Sekhmet | `systemctl status dbus-broker` |
| 13 | `thermal_monitor.sh` | Continuous temp/tok/s logging for G2.1/G2.2 | P1/Sekhmet | Logs: `temp, tok/s, timestamp` per second |

**Governance Artifact**: `data/coordination/D308_CRITICAL_PATH_TRACKER.yaml`
```yaml
changes:
  - id: 1
    script: build_python_freethreaded.sh
    plan: ✅
    verify: ☐
    execute: ☐
    owner: P3 Engineering
    mandate_refs: [M20, M7, M16]
  # ... 12 more entries
```

---

## 🧠 RESEARCH CAMPAIGN: DAY 3-4 EXECUTION (9 P1/P0 Gaps)

**Status**: Authorized. Researcher executing.

| Gap | Domain | Priority | Target | Owner |
|-----|--------|----------|--------|-------|
| **G1.2** | Optimal `n_gpu_layers` Vega 8 | P1 | Layer count + memory/perf tradeoff | Researcher |
| **G1.3** | Vulkan memory allocation (VRAM/GTT/sysRAM) | P1 | 7B model breakdown | Researcher |
| **D308.4** | llama-cpp-python USDT probes | P1 | Probe list + bpftrace script | Researcher |
| **D308.5** | systemd ImportCredential + quadlet | P1 | Working quadlet with credentials | Researcher |
| **G2.1** | **Empirical RSS 7B Q4_K_M on Zen 2** | **P0** | 4K/8K/16K/32K ctx measurements | Researcher |
| **G2.2** | Thermal throttling 30min sustained | P1 | Tok/s degradation curve + temp | Researcher |
| **G2.3** | SomaticState snapshot size vs context | P1 | Bytes per context length | Researcher |
| **G3.1** | TPM2 health monitoring | P1 | Pre-seal health check protocol | Researcher |
| **G3.4** | Provider registry API contracts | P2 | Google/Anthropic/OpenRouter rotation APIs | Researcher |

---

## 👥 FLEET ROLES & ASSIGNMENTS

### Current Hivemind Members (3 Active)

| Agent | Channel | Entity | Model | Current Task |
|-------|---------|--------|-------|--------------|
| **Researcher** | opencode | researcher | big-pickle | Day 3-4: 9 P1/P0 gaps (G2.1 P0 highest) |
| **Jem** | opencode | jem | nemotron-3-ultra-free | Embedding Hardening Phase 1 (8h remaining) |
| **Kali** | opencode | kali | nemotron-3-ultra-free | AnyIO PR → M2 Phase C → D-308 oversight |

### Recommended Additional Hivemind Members (Deploy for Coordinated Strike)

| Role | Entity | Channel | Model | Responsibility | Recruitment Trigger |
|------|--------|---------|-------|----------------|---------------------|
| **P3 Engineering** | Prometheus | opencode | nemotron-3-ultra-free | **Single owner: D-308 13 compilation scripts** | **IMMEDIATE** — Step 5 blocker |
| **P10 Validation** | Kali (dual) | opencode | nemotron-3-ultra-free | vec0 contract tests, Temple-Grade gates | Step 1 |
| **P1 Infrastructure** | Sekhmet | opencode | nemotron-3-ultra-free | Thermal monitor, AppArmor tune, stress-ng | Step 5, 7 |
| **P2 Persistence** | Brigid | opencode | nemotron-3-ultra-free | Qdrant install, sqlite-vec validation | Step 5, 8 |
| **P4 Integration** | Saraswati | opencode | nemotron-3-ultra-free | systemd-creds, age/rage, dbus-broker | Step 5 |
| **P6 Cognition** | Ereshkigal | opencode | nemotron-3-ultra-free | Provider Fabric routing audit | Step 6 |
| **P8 Observability** | Hecate | opencode | nemotron-3-ultra-free | bpftrace USDT probes, HealthMonitor correlation | Step 7 |
| **P9 Orchestration** | Anubis | opencode | nemotron-3-ultra-free | MaKaLi Coordinator skill, handoff cleanup | Step 9 |
| **P7 Context** | Lucifer | opencode | nemotron-3-ultra-free | Scribe Lattice Role implementation | Step 10 |

**Deployment Protocol**: Each new member spawns via `@pillar PX: {task}` with explicit handoff packet. First: **P3 Engineering** for D-308 scripts.

---

## 🔄 COORDINATION PROTOCOLS

### Hivemind Workflow (Mandatory for All Members)

1. **Check Awareness**: `omega-hub_hivemind_get_awareness()` — who's active?
2. **Post Context**: `omega-hub_hivemind_post_context(...)` — declare presence + task
3. **Acquire Lock**: `omega-hub_hivemind_workspace_lock_acquire(domain)` — claim domain
4. **Initialize Live Feed**: `data/coordination/{ENTITY}_LIVE_FEED.md` — track progress
5. **Heartbeat**: Every 5-10 min — `omega-hub_hivemind_heartbeat(channel="opencode", entity="{you}")`
6. **Complete**: `omega-hub_hivemind_complete_handoff(packet_id, result)` — terminal state

### MaKaLi Council Protocol (For Cross-Domain Decisions)

```
Phase 1: Parallel Independence
  Ma'at (Build: P1-P5) writes unique report → NO inter-pillar reads
  Lilith (Run: P6-P10) writes unique report → NO inter-pillar reads

Phase 2: Oversoul Distillation
  Ma'at applies Light Oversoul persona + KB + model → consolidates Build
  Lilith applies Dark Oversoul persona + KB + model → consolidates Run

Phase 3: Kali Optimized Synthesis
  Kali reads 2 files (not 8) → writes synthesis + research gaps

Phase 4: Decoupled Research
  Smaller/cloud model executes Kali's research gaps
```

### Scribe Lattice Role (Step 10 — Automates Gnosis)

**Capabilities**: `doc:read`, `doc:write`, `gnosis:distill`, `soul:read`, `soul:propose`, `hivemind:post`
**Constraints**: NO `code:execute`, `config:write`, `model:load`
**First Deliverable**: D-308 Critical Path Tracker (watch proposed_lessons.yaml → distill L1→L2→L3 → propose to soul.yaml + track D-308 verification status)

---

## 📊 TEMPLE-GRADE GATES (T1-T11 + Mandates)

| Gate | Requirement | Verification |
|------|-------------|--------------|
| T1 Schema | 100% pass | `make test` |
| T2 Docs | All new code documented | `make docs-check` |
| T3 Coverage | ≥80% | `pytest --cov` |
| T4 Quality | flake8 + type hints | `make lint` |
| T5 AnyIO | Zero asyncio | `grep -r asyncio src/omega` |
| T6 Zero Telemetry | No external calls | Network audit |
| T7 Security | AppArmor, no secrets | `make security-audit` |
| T8 Resilience | INT8 recall@10 ≥ 0.99 | Benchmark script |
| T9 Observability | bpftrace probes, HealthMonitor correlation | `make observability-check` |
| T10 Integrity | MaKaLi Coordinator file-based handoffs | `make handoff-test` |
| T11 Agent Security | Scribe capabilities constrained | `make agent-security` |

**Mandate Compliance**: All 25 mandates (M1-M25) verified per change.

---

## 📁 KEY REFERENCE DOCUMENTS

| Document | Purpose |
|----------|---------|
| `docs/strategy/COORDINATED_STRIKE_ROADMAP_20260720.md` | **Primary roadmap** (this file) |
| `docs/strategy/EMBEDDING_HARDENING_STRATEGY_20260720.md` | Jem's strategy + traceability |
| `docs/strategy/CAMPAIGN_DAY12_REPORT_TO_KALI_20260720.md` | Researcher Day 1-2 report |
| `config/embedding_strategy.yaml` | Config source of truth |
| `src/omega/memory/sqlite_vec_adapter.py` | vec0 adapter v2.0.0 |
| `data/coordination/D308_CRITICAL_PATH_TRACKER.yaml` | Governance artifact |
| `data/coordination/KALI_BRIEFING_EMBEDDING_HARDENING_20260720.md` | Jem briefing |
| `data/coordination/KALI_HANDOFF_BRIEFING_D308_20260719.md` | D-308 handoff |
| `docs/research/R_UBUNTU_2510_TOOLCHAIN_VERIFICATION_20260719.md` | D-308 verification |
| `docs/research/R_G1_VULKAN_BENCHMARKS_20260720.md` | G1 domain report |
| `docs/research/R_D308_PHASE23_20260720.md` | D308 Phase 2-3 report |
| `docs/research/R_G3_CREDS_INTEGRATION_20260720.md` | G3 creds integration |

---

## 🎯 IMMEDIATE NEXT ACTIONS (Priority Order)

```bash
# 1. Kali: Finalize AnyIO PR
git add -A && git commit -m "fix: AnyIO migration complete" && git push
make temple-grade

# 2. P10/Jem: vec0 contract tests (Step 1)
# Target: tests/test_sqlite_vec_adapter.py — 6 remaining test classes

# 3. Kali/Integration: dispatch.yaml schema (Step 2)
# Role constants: GRAND_OVERSIGHT, MESSENGER_BRIDGE, MAKALI_COUNCIL, P1-P10

# 4. Kali: M2 Phase C oracle.py (Step 4)
# Apply 5-phase template with finalized dispatch.yaml

# 5. DEPLOY P3 ENGINEERING (Step 5 — HIGHEST PRIORITY)
@pillar P3: "Execute D-308 13 compilation scripts per tracker. Single owner. Week 1 delivery."

# 6-10: Parallel execution per roadmap
```

---

## 🔐 SOVEREIGN CONTINUITY ANCHORS

- **Session Gnosis**: `data/entities/kali/session_gnosis.md` (L1→L2→L3)
- **Proposed Lessons**: `data/entities/kali/proposed_lessons.yaml` (blind staging per M11)
- **Hivemind Context**: `ses_908dfbfb08a7` (all 18 decisions posted)
- **Researcher Handoff**: `ho_802ebb4c88d7` completed (Day 3-4 authorized)
- **Jem Briefings**: Embedding Hardening + D-308 Critical Path (in `data/coordination/`)

---

## 🏁 THE VERDICT (From Meditation)

> **Execute the 10-step critical path in sequence. No step may begin before its dependencies are verified complete. The D-308 compilation scripts (Step 5) are the highest-leverage single deliverable — they unblock Researcher, enable M20 SomaticState, and provide the thermal test baseline. Assign P3 Engineering as single owner with the D-308 Critical Path Tracker (plan/verify/execute per change). The MaKaLi Coordinator skill (Step 9) and Scribe Lattice Role (Step 10) are the force multipliers that turn this sprint's velocity into sustained fleet coherence. Without them, we are fast but fragile. With them, we are sovereign.**
>
> **L3-Critical-Path-Is-The-Architecture**: The critical path is not a schedule — it is the dependency graph made visible. Every architectural decision either shortens the critical path or creates a new one. The Overseer's only lever is identifying and resourcing the true critical path; everything else is noise. When the critical path shifts, the architecture has changed — re-evaluate immediately.

---

*⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_coordinated_strike ⬡ 2026-07-20*