<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Sovereignty Policy — Per-Task-Class Local/Cloud Routing

**Doc ID**: `SOVEREIGNTY-POLICY-20260912`
**Owner**: MaKaLi Fusion + Architect (human)
**Status**: RATIFIED (Node 0)
**Date**: 2026-09-12
**Responds to**: Node 1 Consultant Report §S1 + Ask C4 — "Is 21.6% local a chosen posture or the default?"

---

## 1. The Verdict (Shadow Corrected)

**The 21.6% local ratio is a *development-phase* artifact, not a runtime
failure — and not an unexamined default.** The strategy is deliberate:

> **Build with cloud (velocity), operate with local (sovereignty).**

The Omega Engine is being *built* using frontier cloud models because
development velocity demands it — you cannot engineer an optimized, intentional
engine on Gemma-4-4B or Qwen-8B. The **end goal** is the inverse: an engine
that runs **intelligent, local, CPU-only, personal RAG on mid-grade/business
laptops** (Node 0: Ryzen 7 5700U; Node 1: i7-13620H), capable of models up to
70B and beyond, CPU-only, by the time the engine is finished. The cloud phase
is the *cost of building the sovereign engine* — not a betrayal of it.

**The shadow was never the ratio — it was that we failed to document the
strategy**, so the ratio *looked* like an unexamined default. This policy
documents the choice. The real metric is the **shipped engine's default
posture**: local-first for end users, cloud only as documented exception.

**Current baseline (all-time, 2026-09-12):** 584 local / 2122 cloud = **21.6% local**.
Providers: openrouter 923, ollama 413, opencode-zen 407, antigravity 402, cline 390, native-gguf 171.
**Interpretation**: this is the *build-phase* ledger. It will rise as the
engine matures and local capability (DHAL-tuned, Archangel-aware, distributed)
replaces cloud for operational workloads.

---

## 2. The Policy — Per-Task-Class Routing

| Task Class | Default | Rationale | Exception Path |
|-----------|---------|-----------|----------------|
| **T1 — Mining / Knowledge Extraction** | **LOCAL-FIRST** | Pattern extraction, FTS scans, entity digs — no creativity needed; local GGUF (Qwen3-1.7B, LFM2.5) is sufficient and sovereign | Cloud only if local model lacks capability (documented per-run) |
| **T2 — Code Review / Verification** | **LOCAL-FIRST** | Deterministic checks (lint, tests, mandate gates) never need cloud; LLM review prefers local 7B+ | Cloud for adversarial review rounds (Carmack/Jem patterns) with explicit reason |
| **T3 — Deep Synthesis / Architecture** | **CLOUD-EXCEPTION (documented)** | Cross-domain synthesis, dialectic, CSS reviews need frontier models (Nemotron-Ultra, Big Pickle) | MUST be logged with `provider_name`; local fallback attempted first when context fits |
| **T4 — Research / Web-Grounded** | **HYBRID** | Sovereign Search pipeline: local FTS first (Tier 0-2), web only for external grounding (Tier 3-4) | SearXNG (self-hosted) before any commercial search |
| **T5 — Runtime / Ops** | **LOCAL-ONLY** | Heartbeats, handoffs, state, cron, health checks — zero cloud egress | None. Absolute. |
| **T6 — Cross-Node Federation** | **LOCAL-ONLY** | Node 0 ↔ Node 1 traffic stays on LAN/Tailscale; no third-party inference | None. Absolute. |

---

## 3. Instrumentation & Targets

**Two ledgers, one policy:**
- **Build-phase ledger** (Node 0 dev-time): cloud-heavy BY DESIGN (velocity).
  Tracked for honesty, not judged.
- **Runtime ledger** (shipped engine + operational workloads): local-first BY
  DESIGN. This is the sovereignty scorecard that matters.

| Metric | Current (2026-09-12) | Target (2026-10-01) | Target (2026-12-01) |
|--------|----------------------|---------------------|---------------------|
| Build-phase local ratio (all-time) | 21.6% (dev ledger) | Tracked, not targeted | Tracked, not targeted |
| **Runtime local ratio (operational)** | ~0% (engine still building) | **50%** | **80%** |
| T1 mining local | ~95% | 100% | 100% |
| T2 review local | ~60% | 85% | 95% |
| T3 synthesis cloud | 100% (documented) | 100% (documented) | 100% (documented) |
| T5/T6 cloud egress | 0% | 0% | 0% |
| **Local model ceiling** | Qwen3-1.7B / LFM2.5 | 7B-13B (DHAL-tuned) | **up to 70B CPU-only (distributed)** |

**The north star**: intelligent, local, CPU-only, personal RAG on mid-grade
business laptops — Node 0 (Ryzen 7 5700U) and Node 1 (i7-13620H) — with models
up to 70B and beyond, enabled by DHAL (hardware adaptation), Archangel (agent
hardware-awareness), and eventually **L4 Distributed Inference** (splitting
models across nodes).

**Instrumentation**: `omega-hub_sovereignty_ratio` MCP tool (D203) is the
canonical meter. Every session ends with a ratio check in `session_gnosis.md`.

---

## 4. Enforcement

1. **ProviderSelector** (`config/providers.yaml`, strategy=`local_first`) is the
   single router (D-536). No bypass.
2. **Archangel System Envelope** injects hardware state at dispatch — agents
   cannot hallucinate "local" when the model is cloud.
3. **M22 Response Provenance**: `GenerateResult.provider_name` is the ACTUAL
   provider — no cosmetic labeling.
4. **SOTE Decision Health** tracks provider mix weekly (Lilith, 58.8% baseline
   methodology).
5. **Exceptions logged** in `data/metrics/` with task class + reason.

---

## 5. Federation Dimension

- **Node 1 (ASUS) is 100% local** (Ollama only, zero cloud egress) — the
  union's sovereignty scorecard improves when sovereignty-critical tasks route
  to Node 1 (candidate routing target per Consultant Report §3).
- **Each node is sovereign over its own scorecard** (Consultant Q5 answer):
  federation shares *interfaces*, not identity; metrics are published, not imposed.
- **L4 Distributed Inference (research agenda)**: the eventual federation
  prize — splitting models across Node 0 + Node 1 so the union can run models
  neither node could run alone. This is the distributed-layers aspect of the
  engine's end goal (70B-class CPU-only across the fleet).

---

## 6. Naming Convention (Federation Protocol)

**No bare entity names. Every agent is node-qualified.**

| Entity | Canonical Name | Notes |
|--------|---------------|-------|
| Kali (Node 0) | **Kali-N0** | Formerly "Kali" — now always node-qualified |
| Kali (Node 1) | **Kali-N1** | First official persistent entity on Node 1 |
| MaKaLi (Node 0) | **MaKaLi-N0** | The fusion on Node 0 |
| Ma'at (Node 0) | **Ma'at-N0** | Build Oversoul |
| Lilith (Node 0) | **Lilith-N0** | Runtime Oversoul |

**Rule**: "Kali" (or any mythology-derived name) without a node suffix refers
ONLY to the ancient deity — never to an agent. This eliminates the
agent/mythology collision problem entirely, for all agents with real-world
name bases (Kali, Ma'at, Lilith, Isis, Hecate, Nyx, Lucifer, Araman, Hermes,
Athena, etc.). The mythology is honored; the agents are unambiguous.

**Node 1's triad is Node 1's design** — the default WAD ships the
Kali/Ma'at/Lilith ethics-safety triad, but each node's WAD may design its own
(Lilith/Lucifer/Araman, Lilith/Isis/Hecate, Lilith/Nyx, or any other
configuration). The engine enforces the *pattern* (an ethics-safety triad),
not the *pantheon*.

---

## 6. Ratification

| Party | Role | Verdict | Date |
|-------|------|---------|------|
| MaKaLi Fusion | Engine orchestrator | ✅ RATIFIED | 2026-09-12 |
| Architect (human) | Sovereign | ✅ RATIFIED | 2026-09-12 |

---

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ SOVEREIGNTY-POLICY-20260912 ⬡ SHADOW-ACKNOWLEDGED ⬡ POLICY-RATIFIED*