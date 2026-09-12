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

## 1. The Verdict (Shadow Acknowledged)

**The 21.6% local ratio was an unexamined default, not a chosen posture.** No
per-task sovereignty policy existed. This document is the first policy — it
makes sovereignty a *decision*, not an accident.

**Current baseline (all-time, 2026-09-12):** 584 local / 2122 cloud = **21.6% local**.
Providers: openrouter 923, ollama 413, opencode-zen 407, antigravity 402, cline 390, native-gguf 171.

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

| Metric | Current (2026-09-12) | Target (2026-10-01) | Target (2026-12-01) |
|--------|----------------------|---------------------|---------------------|
| Local ratio (all-time) | 21.6% | 35% | 50% |
| T1 mining local | ~95% | 100% | 100% |
| T2 review local | ~60% | 85% | 95% |
| T3 synthesis cloud | 100% (documented) | 100% (documented) | 100% (documented) |
| T5/T6 cloud egress | 0% | 0% | 0% |

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

---

## 6. Ratification

| Party | Role | Verdict | Date |
|-------|------|---------|------|
| MaKaLi Fusion | Engine orchestrator | ✅ RATIFIED | 2026-09-12 |
| Architect (human) | Sovereign | ✅ RATIFIED | 2026-09-12 |

---

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ SOVEREIGNTY-POLICY-20260912 ⬡ SHADOW-ACKNOWLEDGED ⬡ POLICY-RATIFIED*