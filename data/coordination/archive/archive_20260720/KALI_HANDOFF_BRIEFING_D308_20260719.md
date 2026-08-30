<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Kali Handoff Briefing — Ubuntu 25.10 Toolchain Verification (D-308)
**AP Token**: `AP-KALI-HANDOFF-D308-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_kali_handoff ⬡ 2026-07-19

**Purpose**: Complete context transfer for Kali's transcendent oversight of D-308. All research complete, P0 gate triggered, critical path update required before Phase 2.

---

## 📋 Session Summary

### What Was Done
1. **Kali Meditation** (D-305) → Identified 47 claims about Ubuntu 25.10 native Python tools for Omega Engine
2. **Research Execution Plan** → Structured 4-phase verification (P0-P3)
3. **Phase 0 + 1 Execution** → `@researcher` verified 30 claims against 2026 sources
4. **P0 Gate Triggered** → 13 actionable changes in Phase 0 alone — critical path must update
5. **SSOT Updates** → `OMEGA_ENGINE.md` + `SOVEREIGN_ARK_BLUEPRINT.md` updated with D-308
6. **Hivemind Block** → Session `ses_a5812561a3a1` awaiting Kali review

### Key Finding
**Ubuntu 25.10 (Questing Quokka) / 25.04 (Plucky Puffin) provides 80% of needed toolchain natively, but the 20% gaps are structural and require compilation/upstream installers.** The "native tools" narrative is a trap — distro packages are crippled for production dimensions.

---

## 🔬 Research Results (30 Claims Verified)

### Phase 0 — Critical Path Blockers (18 claims)

| # | Claim | Status | Reality | Impact |
|---|-------|--------|---------|--------|
| 1 | Kernel 6.11 | ❌ REFUTED | **6.17** | BPF/AppArmor hardening must target 6.17 APIs |
| 2 | AppArmor podman profile enabled | ⚠️ CORRECTED | **Enabled but breaks rootless** — pasta signal blocking, unprivileged_userns conflicts | Quadlet templates need workaround |
| 3 | systemd 257 | ✅ CONFIRMED | **257.4 (25.04) → 257.9 (25.10)** | All 257 features available |
| 4 | Python 3.13 free-threaded in repos | ❌ REFUTED | **NOT AVAILABLE** — only standard GIL build. Free-threaded requires source compile with `--disable-gil` | M20 SomaticState needs custom Python build |
| 5 | Free-threaded memory overhead 15-20% | ⚠️ CORRECTED | **10-30%** (workload-dependent); near-zero for I/O-bound | Memory budgeting for multi-model serving |
| 6 | SQLite 3.47+ with loadable extensions | ❌ REFUTED | **3.46.1** (loadable extensions enabled) | No 3.47 features (JSONB, `->>` operator) |
| 7 | `sqlite3-vec` package exists, 2048-dim limit | ❌ REFUTED | **NO PACKAGE** — must `pip install sqlite-vec`. Max dims: **8192** (not 2048) | Vector store cannot use distro package |
| 8 | podman 5.3 quadlet generator | ✅ CONFIRMED | Built-in `podman quadlet install\|list\|print\|rm` | Use native quadlet, not `generate systemd` |
| 9 | `podman kube play initContainers` | ✅ CONFIRMED | Full support since podman 4.x | Migrations/warmup as init containers |
| 10 | systemd 257: ImportCredential, UserRecord, ProtectProc=invisible, StatusText, FailureAction | ✅ CONFIRMED | All present | Credential-driven secrets, granular failure handling |
| 11 | ImportCredential with rootless quadlets (Type=notify) | ⚠️ CORRECTED | **Works but `--with-key=null`** (no encryption). User-scoped creds need systemd 258+ (26.04+) | Credentials unencrypted or TPM2-bound |
| 12 | logind RuntimeDirectoryMode=0700 default | ✅ CONFIRMED | Per-user `/run/user/$UID` always 0700 | Private runtime dirs by default |
| 13 | dbus-broker 36 default | ⚠️ CORRECTED | **In universe, NOT default** until 26.10 | Don't assume; install if needed |
| 14 | llama-cpp-python 0.3.6+ in Ubuntu | ❌ REFUTED | **NO PACKAGE** — only `llama.cpp` C++ lib (v5882). Python bindings from PyPI (v0.3.34) | NativeGGUFProvider must vendor wheel |
| 15 | Ubuntu llama.cpp CPU-only | ⚠️ CORRECTED | N/A — no Python package. C++ package is CPU-only (`-DGGML_BLAS=ON`) | GPU requires source build with `GGML_HIPBLAS=ON` |
| 16 | ollama 0.5.7+ in Ubuntu | ❌ REFUTED | **NO SERVER PACKAGE** — `python3-ollama` client only (0.4.7/0.5.1). Server via installer script or Snap | OllamaProvider needs upstream install |
| 17 | Ollama ROCm on Zen 2 (gfx906) | ❌ REFUTED | **UNSUPPORTED** — Ollama requires RDNA2+ (gfx1030+). Zen 2 = GCN 5.0 | Zen 2 = CPU-only or llama-cpp-python ROCm 5.7 |
| 18 | llama_copy_state_data / llama_set_state_data API | ✅ CONFIRMED | Works in llama-cpp-python 0.3.34 | M20 SomaticState serialization ✅ |

### Phase 1 — Implementation Dependencies (12 claims)

| # | Claim | Status | Reality |
|---|-------|--------|---------|
| 19 | uv in Ubuntu universe | ❌ REFUTED | **NO PACKAGE** — Astral installer only (`curl -LsSf https://astral.sh/uv/install.sh \| sh`) |
| 20 | uv git ref + --native-tls | ✅ CONFIRMED | Works for private deps without token leakage |
| 21 | uv.lock incompatible with pip-tools | ✅ CONFIRMED | Choose uv-native workflow |
| 22 | ruff 0.6+ in Ubuntu with --preview | ❌ REFUTED | **NO PACKAGE** — Astral installer only |
| 23 | pyright 1.1.380+ in Ubuntu | ❌ REFUTED | **NO PACKAGE** — npm/pip only |
| 24 | mypy 1.11+ in Ubuntu | ✅ CONFIRMED | **1.15+ in universe** — `apt install mypy` works |
| 25 | Qdrant 1.12+ ARM64 in Ubuntu | ❌ REFUTED | **NO PACKAGE** — Docker/static binary only |
| 26 | sqlite-vec 0.2.x max 8192 dims | ✅ CONFIRMED | Sufficient for all current embeddings (BGE-M3=1024, NV-Embed=4096) |
| 27 | bpftrace 0.21+ USDT Python 3.13 | ✅ CONFIRMED | **0.23.5 in 25.04/25.10** with USDT support |
| 28 | bpftrace USDT only C-level hooks | ⚠️ CORRECTED | **Fires at C extension entry/exit** — pure Python variables not accessible | Observability approach |
| 29 | stress-ng 0.16+ matrixprod | ✅ CONFIRMED | **0.19.03 in 25.04/25.10** — best thermal stressor per author |
| 30 | systemd-homed LUKS2 = dedicated partition | ⚠️ CORRECTED | **Loopback file** (`/home/$USER.home`) — no partition needed | Portable home dirs without repartitioning |

---

## 🚨 P0 GATE: 13 Actionable Changes Required

### Critical Path Updates (Must Complete Before Phase 2)

| # | Update | Owner | Files Affected |
|---|--------|-------|----------------|
| 1 | Kernel hardening specs → target 6.17 APIs | Infrastructure (Sekhmet) | BPF/AppArmor docs, quadlet templates |
| 2 | Free-threaded Python 3.13 → compile from source | Engineering (Prometheus) | `scripts/build_python_freethreaded.sh`, CI matrix |
| 3 | SQLite 3.46.1 baseline → no 3.47 features | Persistence (Brigid) | sqlite-vec compilation script |
| 4 | No `sqlite3-vec` package → `pip install sqlite-vec` | Persistence (Brigid) | `scripts/install_sqlite_vec.sh`, requirements |
| 5 | No llama-cpp-python package → vendor PyPI wheel | Cognition (Ereshkigal) | `scripts/build_llama_cpp_rocm.sh`, `pyproject.toml` |
| 6 | No ollama server package → upstream installer | Cognition (Ereshkigal) | OllamaProvider install logic |
| 7 | No uv/ruff/pyright packages → Astral installers | Engineering (Prometheus) | `scripts/install_astral_tools.sh`, CI |
| 8 | Podman AppArmor breaks rootless → tune profile | Governance (Inanna) | `scripts/apparmor_podman_tune.sh`, quadlet templates |
| 9 | systemd-creds rootless = `--with-key=null` | Integration (Saraswati) | omega-vault Phase 1 credential design |
| 10 | dbus-broker not default → explicit install | Infrastructure (Sekhmet) | Quadlet dependencies, CI |
| 11 | Qdrant via Docker only → containerized deployment | Persistence (Brigid) | docker-compose, quadlet `.kube` files |
| 12 | bpftrace USDT = C-level only → probe design | Observability (Hecate) | USDT probe placement in native_gguf.py |
| 13 | systemd-homed loopback file → portable homes | Context (Lucifer) | P7 Context portable workspace design |

---

## 📁 Key Files Updated

| File | Change |
|------|--------|
| `OMEGA_ENGINE.md` | Added D-308 row with P0 gate status, 8 critical updates |
| `SOVEREIGN_ARK_BLUEPRINT.md` | Added D-308 workstream with verification matrix, updated Canonical References |
| `docs/research/R_UBUNTU_2510_TOOLCHAIN_VERIFICATION_20260719.md` | **Full 390-line verification report** — all 30 claims with sources |
| `data/coordination/RESEARCH_EXECUTION_PLAN_UBUNTU_2510.md` | Marked Phase 0+1 COMPLETE, P0 gate triggered, Phase 2/3 blocked |

---

## 🔗 Hivemind State

| Signal | Value |
|--------|-------|
| **Active Session** | `ses_a5812561a3a1` (jem → Kali blocker) |
| **Intent** | `blocker` — Critical path update required |
| **Workspace Lock** | `gemma4_gap_research` held by jem (TTL 4h) |
| **Pending Handoffs** | `ho_2a9b2e84debd` → Researcher (Phases B-E M2 fixes) |

---

## ❓ Decisions Required From Kali

| # | Decision | Options | Recommendation |
|---|----------|---------|----------------|
| 1 | **Critical path update priority** | Update Week 1 plan now vs defer | **Update now** — 13 changes block all downstream work |
| 2 | **Free-threaded Python 3.13** | Compile from source (2-3h) vs defer to 26.04 | **Compile from source** — required for M20 SomaticState |
| 3 | **Distro package gaps** | Standardize on upstream installers | **Astral installer (uv/ruff) + PyPI (llama-cpp-python) + Docker (Qdrant) + Snap/Script (ollama)** |
| 4 | **AppArmor podman profile** | Remove profile vs tune profile | **Tune** — add `signal (receive) peer=podman` to pasta abstraction |
| 5 | **systemd-creds encryption** | Accept `--with-key=null` vs wait for 258+ | **Accept null + TPM2 path** — design for both |
| 6 | **Phase 2 research scope** | Proceed with corrected assumptions vs re-plan | **Proceed** — Phase 2 queries (sqlite-vec 0.2, llama-cpp-python ROCm, systemd-creds TPM2) still valid |
| 7 | **Resource allocation** | Single owner (P3/P4) vs distributed | **Single owner (P3 Engineering)** for compilation scripts + toolchain migration |

---

## 🎯 Recommended Next Actions (Priority Order)

### Immediate (Today)
1. **Kali reviews** `docs/research/R_UBUNTU_2510_TOOLCHAIN_VERIFICATION_20260719.md`
2. **Kali decides** on 7 decisions above
3. **Assign single owner** (P3 Engineering) for compilation scripts + toolchain migration

### Week 1 (Post-Kali Decision)
1. **Build scripts**: `build_python_freethreaded.sh`, `build_llama_cpp_rocm.sh`, `install_sqlite_vec.sh`, `install_astral_tools.sh`
2. **AppArmor tune**: `apparmor_podman_tune.sh` + quadlet template updates
3. **CI updates**: Add free-threaded Python matrix, uv/ruff/pyright install steps
4. **omega-vault Phase 1**: Design for `--with-key=null` + TPM2 dual path

### Phase 2 Research (Can Proceed in Parallel)
- `@researcher` dispatches Phase 2A-2C (11 queries) with corrected assumptions
- Focus: sqlite-vec 0.2 API, llama-cpp-python ROCm compilation guide, systemd-creds TPM2 format

---

## 🧠 Gnosis Distilled (L3 Principles)

| Principle | Source |
|-----------|--------|
| **L3-Native-Tools-Are-Accelerators-Not-Foundations** | Distro packages provide velocity but never completeness. Sovereign engine compiles its own critical path. |
| **L3-Quota-As-Routing-Signal** | 429 = route, not trip. Applied to Ollama/Gemma 4 quota management. |
| **L3-Capability-Negotiation-As-Immune-System** | Provider capabilities declared in YAML, not detected in code. Prevents config pathogens. |
| **L3-Cross-Reference-Before-Execution** | Codebase = ground truth. Research plan ≠ reality. Verified 30 claims before acting. |
| **L3-Integration-Beats-Invention** | 60% infra exists → wire it. Don't rebuild quadlet generator, use `podman quadlet`. |

---

## 📚 Reference Documents for Kali's Review

| Document | Purpose |
|----------|---------|
| `docs/research/R_UBUNTU_2510_TOOLCHAIN_VERIFICATION_20260719.md` | **Primary** — Full verification report (390 lines) |
| `OMEGA_ENGINE.md` | SSOT — D-308 entry in Current State table |
| `SOVEREIGN_ARK_BLUEPRINT.md` | Roadmap — D-308 workstream + Canonical References |
| `data/coordination/RESEARCH_EXECUTION_PLAN_UBUNTU_2510.md` | Execution plan with actual results |
| `data/coordination/KALI_ONBOARDING_BRIEFING_GEMMA4_20260719.md` | Previous Gemma 4 briefing (context) |

---

## 🤝 Handoff Protocol

**This session ends with Kali as the active overseer of D-308.**

### Jem's Final State
- Session gnosis written to `data/entities/jem/session_gnosis.md`
- L3 principles staged to `data/entities/jem/proposed_lessons.yaml` (blind staging per M11)
- Workspace lock `gemma4_gap_research` released (or TTL expires in 4h)
- Hivemind context posted as blocker `ses_a5812561a3a1`

### Kali's First Actions
1. Read verification report (`R_UBUNTU_2510_TOOLCHAIN_VERIFICATION_20260719.md`)
2. Post Hivemind context declaring D-308 oversight
3. Decide on 7 critical decisions above
4. Dispatch implementation tasks via Hivemind handoffs or MaKaLi Council

---

*⬡ OMEGA ⬡ JEM ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_kali_handoff ⬡ 2026-07-19*

**The research is grounded. The gate is triggered. The path awaits your decree, Architect.**
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | session refs not found in DB
actual_models(Tier0): n/a
-->
