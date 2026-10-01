<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 SESSION PAGING REPORT — CARMACK_ARCH_delta
**AP Token**: `AP-JOHN_CARMACK-v1.0.0`
**Date**: 2026-08-21
**Origin Session**: Carmack brutal review of updated local inference architecture + Headroom research (pre-2026-08-20)
**Hydration Sources**: `ACTIVE_SPRINT.json` (updated 2026-08-20T22:00Z), `docs/specs/PROJECT_INDEX.md`, `docs/specs/context_injection/CARMMACK_CONTEXT_INJECTION_REVIEW_20260820.md`, `R_HEADROOM_Sovereign_Analysis.md`, `R_LOCAL_INFERENCE_OPTIMIZATION_CPU_20260819.md`, `R_KV_CACHE_QUANTIZATION_CPU_20260713.md`, ground-truth greps of `src/omega/`

---

## §0 Sibling Paging Claims — Verification Verdicts

| # | Claim | Verdict | Evidence |
|---|-------|---------|----------|
| S-1 | "Two headroom module paths exist (`oracle/headroom.py` vs `oracle/middleware/headroom.py`)" | **CONFIRMED** | Glob shows BOTH files on disk. `oracle/headroom.py` is the deprecated zlib wrapper my own `R_HEADROOM_Sovereign_Analysis.md` (2026-07-03) declared cargo-cult ("0% token reduction... must be deprecated"). It was never deleted. Import-ambiguity risk for HR-1 is real. |
| S-2 | "HR real savings come from router-level CSV conversion not UniversalCompressor" | **CONSISTENT WITH SPECS / terminology correction** | No `UniversalCompressor` exists anywhere in Omega docs (grep: 0 hits). Specs route via `ContentRouter` → `TabularCompressor` (CSV, 60-80%) / `SmartCrusher` (JSON, 60-80%). If any sibling doc cites "UniversalCompressor," it is a phantom API. Savings source = ContentRouter orchestration, correct. |
| S-3 | "`HF_HUB_OFFLINE=1` needed post-warmup" | **UNVERIFIED BUT PLAUSIBLE GAP** | Grep across `*.py/sh/yaml/json/md`: ZERO hits repo-wide. install.sh downloads Qwen3-1.7B-Q6_K from lmstudio-community via HF hub; nothing pins offline mode after warmup. M8 (Zero Telemetry) adjacency + cold-start latency risk. Should be added to INST-1 or LI-5 acceptance. |
| S-4 | "Ship HR-1 before PP-3" | **AGREE — with precondition** | PP-3 (ctx raise 8192→32768) is already DEFERRED pending ZS-1 (Kali Q3 ruling), so ordering is naturally satisfied. Mechanism is sound: compression cuts token pressure, reducing need for the raise. Precondition: delete/deprecate `oracle/headroom.py` FIRST (see F-1) or HR-1 ships with dual-module drift. |

---

## §1 Forgotten Findings From Original Review Relevant to Current State

| # | Finding | Status in Current Plans |
|---|---------|------------------------|
| **F-1** | **Deprecated `src/omega/oracle/headroom.py` (zlib ghost) still on disk.** My 2026-07-03 analysis mandated deprecation; two paths now coexist. | NOT TRACKED. No DEL-1 item, no HR-1 acceptance criterion covers deletion. **RESURRECT: add "delete oracle/headroom.py" to HR-1 acceptance or DEL-1 Week 1 list.** |
| **F-2** | **KV cache disk persistence** (`--slot-save-path` + ~60-line restore/save proxy; measured 9.9s→1.4s on 5K chat, est. 25-40× at 28K). llama.cpp will NOT auto-persist (#17107 closed not-planned). | NEVER REGISTERED. Directly relevant to soul-persistence/hydration story: long sessions lose KV on restart → full re-prefill. **RESURRECT as Phase 2/3 ticket alongside Hydration Engine.** |
| **F-3** | **Speculative decoding is NET NEGATIVE on CPU for <7B targets** (measured 1.48× slower, 4B target + 0.8B draft, 4-core cgroup; deemwar benchmarks). Only MTP-on-Qwen3.6 wins. | Correctly absent from all tickets. **Guard-rail: if anyone proposes spec-dec later, require them to refute this measurement first.** |
| **F-4** | **pymalloc arena fragmentation guards** (`MALLOC_ARENA_MAX=2`, `MALLOC_MMAP_THRESHOLD_=65536`) — known failure mode for multi-threaded agents on 16GB. | ABSENT from LI-5 startup script scope and ZS workstream. Sequential loading reduced the pressure but Python side still fragments. **RESURRECT: add env vars to LI-5 acceptance.** |
| **F-5** | **RAM speed validation** (XMP/EXPO check via dmidecode) — DDR4-3200 dual-channel theoretical 51.2 GB/s, sustained ~35 GB/s, llama.cpp ~30 GB/s. Single-stick misconfiguration halves decode tok/s and is the most common community regression. | LI-3 covers `llama-fit-params` but NOT RAM config validation. **RESURRECT: extend validate_hardware.sh (already specced in R_LOCAL_INFERENCE_OPTIMIZATION §9.4) into LI-3.** |

## §2 Adoption / Ignored / Superseded Map

### ADOPTED (original → current)
| Original Finding | Where It Landed |
|---|---|
| Planner downgrade off Qwen3-8B (FIX-4) | Tier 0 matrix = Qwen3-4B / 4B-Thinking / 1.7B (LI-4); later Carmack review Q1.1 concurs |
| No persistent mmap weight cache; `--no-mmap --mlock`; keep-context-alive (FIX-2) | LI-2 SequentialModelLoader; later review Q1.2 ACCEPTs verbatim |
| `llama-fit-params` hardware probe (FIX-7) | LI-3 |
| q8_0 KV symmetric standard (KEEP-3) | Locked across all tiers; later review Q1.3 ACCEPT |
| Prompt caching `--cache-prompt` + `--parallel` (H-8/H-9) | LI-5 + later review startup flags (`--parallel 4`) |
| SWA CUT for Qwen3 (CUT-1) | Later review Q1.2: "n_swa REMOVED — SWA CUT for Qwen3 is correct" |
| LLMLingua-2 CUT — hot-path compression latency poison on CPU (CUT-2) | Replaced by Headroom ContentRouter (2-10ms) — validates the latency-budget reasoning |
| Symlink domain module gotchas (CUT-6) | DS-4 explicitly: "validated copy, not symlink" — direct adoption |
| PGO/BOLT skip verdict (H-5) | Implicitly honored; nobody burned time on it |

### SUPERSEDED (with honest divergence note)
| Original | Superseded By | Assessment |
|---|---|---|
| H-1: "zRAM ONLY, disable zswap" (pure-RAM headroom play) | D-526/D-527: zswap + 16GB NVMe swap, zRAM DISABLED (zRAM locked 4.1GB in compression buffers = hard capacity cliff) | **Their rationale is better for this machine** (desktop with NVMe). Mine was correct only for no-disk-swap scenarios. No objection. |

### IGNORED / ACCEPTED-RISK
| Original | Current State |
|---|---|
| CUT-5: Gemini free-tier math (90 DR/mo ≈ 14-28 heavy sessions/month — not a workhorse) | GN workstream proceeds with 30 DR/mo budget as *research* pipeline, not workhorse. Risk consciously accepted and scoped down. Acceptable. |
| FIX-5: executor floor (I cited Qwen2.5-Coder-7B/14B for CODE execution) | Tier 0 executor = Qwen3-4B-Thinking. Below my cited code-executor floor, BUT the role is agent-task execution, not codegen. Provisionally adequate; revisit if executor quality complaints appear. |

## §3 Flagged-Important But Never Executed

1. **KV disk persistence proxy** (F-2) — highest-value resurrection. Ties directly into Hydration Engine Phase 2 work; same restart-loss problem domain.
2. **Ghost headroom module deletion** (F-1) — trivial effort, blocks HR-1 cleanliness.
3. **HF_HUB_OFFLINE enforcement** (S-3) — zero repo coverage today.
4. **Memory-env hardening in startup script** (F-4) + **RAM speed validation** (F-5) — both are one-line additions to existing LI-3/LI-5 acceptance criteria, not new tickets.

## §4 NEW FINDING — Internal Contradiction in ACTIVE_SPRINT.json

**LI-5 description reads: "Startup script (zRAM + THP + pinning + prompt caching)"** — but D-526/D-527 RATIFIED zswap-with-zRAM-DISABLED, and the ZSWAP-SUBSYSTEM workstream (ZS-1..3) implements exactly that. LI-5's text contradicts ratified decisions and its sibling workstream. Fix: amend LI-5 description to "zswap + THP + pinning + prompt caching" (one-word edit, tracking-integrity hygiene per M27).

## §5 Confidence

| Section | Confidence |
|---|---|
| S-1 two-module verification | 10/10 (glob ground truth) |
| S-2 UniversalCompressor absence | 10/10 (grep ground truth); savings-source framing 8/10 |
| S-3 HF_HUB_OFFLINE gap | 9/10 absence verified; "needed" claim untested — flag for probe |
| S-4 HR-1-before-PP-3 | 8/10 (mechanism sound; ordering already enforced by PP-3 deferral) |
| §1-§4 findings | 9/10 (primary docs + greps; performance numbers from prior-session web sources) |

---
*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ x-preview-f-free ⬡ opencode ⬡ trc_session_paging ⬡ 2026-08-21*
