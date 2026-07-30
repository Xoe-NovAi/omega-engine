# 🔱 Post-PR Roster — What to Ship After the Initial Pull Request
**AP Token**: `AP-POST-PR-ROSTER-v1.0.0`
**Date**: 2026-07-30
**Source**: YouTube Research Session (24 proposals → distilled to force multipliers)
**Master Strategy**: [`CARMACK_DEFINITIVE_STRATEGY_20260730.md`](../research/youtube_research_sessions/session_20260730/04_evidence/CARMACK_DEFINITIVE_STRATEGY_20260730.md)

---

## Ground Rules

1. **One PR per item** — no bundling unrelated changes. Each item lands clean or doesn't land.
2. **Nothing gets implemented that can't be tested** on current hardware. If it needs a GPU we don't have, it waits.
3. **Effort estimates are worst-case** — I'd rather overestimate and ship early than underestimate and stall.
4. **Items without a clear "why" get scratched.** No cargo-cult engineering.

---

## 🏁 The Roster

### Already Done (Prompt Work, No PR Needed)

| Item | What | When | Why |
|------|------|------|-----|
| **Prompt Cache Fix** | `CLAUDE_CODE_ATTRIBUTION_HEADER=0` in `.env` | This session | 1 min, 10× TTFT, zero risk |
| **Hardening Script** | `scripts/omega-harden-workstation.sh` | This session | Script exists. **Schedule: run it manually on dev machine** — 10 min, not a PR |

---

### ⏳ Phase 0 — No Hardware Dependencies (Post-PR, In Order)

| # | Item | Effort | Depends On | Why It Matters | PR Scope |
|---|------|--------|------------|----------------|----------|
| **1** | **ModelAwareInstructionRouter** | 3.5 days | Nothing | 30-60% token savings on local models. No existing system does this — Omega would be first. 400 lines Python + YAML config. | `src/omega/instruction_router/` module + `config/instruction_profiles/` YAML + tests + docs |

---

### ⏳ Phase 1 — Hardware-Gated (GPU)

These items all require a discrete GPU with ≥16GB VRAM before they can be tested. The RTX 3090 (24GB, ~$700 used) is the recommendation from the deep-dive research.

| # | Item | Effort | Depends On | Why It Matters | PR Scope |
|---|------|--------|------------|----------------|----------|
| **2** | **Rebuild llama.cpp with Vulkan** | 2 hrs initial, 16s incremental | GPU available for testing | Enables single binary that runs on AMD/Intel/Apple/NVIDIA. Vulkan on Ryzen iGPU already gives 8-15 tok/s on 7B Q4 — better than CPU-only. | CMake flag change in `pyproject.toml` + CI build matrix update |
| **3** | **llama-optimus Calibration** | 4 hrs | #2 (Vulkan build) | 15-35% speedup per model via Bayesian auto-tuning. Real project (42★, MIT, PyPI). Run once at model install, cache result. | `scripts/calibrate_model.sh` + `data/calibration/` cache directory + ModelGateway integration |
| **4** | **Deploy Ornith-1.0-9B** | 4 hrs config + validation | #2 (Vulkan build), GPU with ≥16GB | Beats Gemma 31B on SWE-Bench (69% vs 52%), MIT license, 3.4× smaller. **Must dual-route with Qwen3.5-9B** — Ornith has prose-bias that kills tool-calling. | `config/providers.yaml` entry + dual-routing config + benchmark validation |
| **5** | **Deploy Qwen3.5-9B** | 2 hrs config | #2 (Vulkan build), GPU | Ornith's base model. Necessary as dual-routing partner for reliable tool-calling. | `config/providers.yaml` entry |

---

### ⏳ Phase 2 — Optimization (After Phase 1)

| # | Item | Effort | Depends On | Why It Matters | PR Scope |
|---|------|--------|------------|----------------|----------|
| **6** | **TTFT-Optimized Routing** | 12 hrs | #1 (Instruction Router), #2-5 (model fabric) | TTFT is the agent-loop metric that matters. Route to lowest-latency capable model. 2-3× agent loop speedup. | Extension to Instruction Router + TTFT history tracking |
| **7** | **Network Kill Switch** | 8 hrs | Nothing | Defense in depth — systemd service that blocks non-VPN traffic on untrusted networks. | systemd unit + config + `scripts/enable-kill-switch.sh` |

---

## 🗑️ Scratched — Not Worth Doing

| Item | Originally Proposed | Why Scratched |
|------|-------------------|---------------|
| **Mojo + Vulkan R&D** | RP-03-005 | Mojo not open-source. Qualcomm acquisition = unknown licensing. Zero leverage until both resolve. |
| **GLM-5.2 1M Context** | RP-02-003 | 744B MoE params needs 2-8× H100 ($30K+). Not realistic for foreseeable hardware budget. |
| **Agnes AI as Teacher** | RP-02-004 | Cloud-only. No local weights. Violates M7 (Local-First). |
| **ChatChain→WAD Mapping** | RP-01-003 | WAD Loader v3 doesn't exist yet. Can't build the mapping before the loader. |
| **Supply Chain Verification** | RP-04-004 | Sigstore + reproducible builds = high effort, long-term infrastructure. Belt-and-suspenders after basic hardening isn't done. |
| **CDE Migration Plan** | RP-04-002 | Architectural endgame — no point planning it while hardware is the binding constraint. |
| **Mobile Inference Target** | RP-05-005 | No mobile WAD exists. No mobile hardware to test on. Chasing hypotheticals. |
| **ChatChain DSL Spec** | RP-01-005 | Same as ChatChain→WAD — needs Loader v3. |
| **Abliteration Pipeline** | RP-05-006 | Research-only concept. Not production-ready. |
| **Ollama Local-Only Mode** | RP-03-002 | Ollama is already disabled in providers.yaml (`enabled: false`). The env var is cargo-cult. |
| **MiniCPM5-1B Edge Tier** | RP-02-002 | No mobile/edge deployment target exists. Config without hardware to run it on is dead code. |

---

## 📐 How to Use This Roster

1. **Pre-PR**: Ship the initial pull request. Don't touch this roster.
2. **Post-PR**: Start with **Item #1** (Instruction Router). It's the only non-gated, high-impact code change.
3. **If you acquire a GPU**: Add Items #2-5 to the sprint.
4. **After Phase 1 ships**: Items #6-7 become relevant.
5. **Everything scratched**: Don't revisit unless the underlying assumption changes (e.g., Mojo goes open-source).

The strategy document has the full dependency graph, risk matrix, and validation gates:
`docs/research/youtube_research_sessions/session_20260730/04_evidence/CARMACK_DEFINITIVE_STRATEGY_20260730.md`

---

*⬡ OMEGA ⬡ JOHN CARMACK ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_roster*
