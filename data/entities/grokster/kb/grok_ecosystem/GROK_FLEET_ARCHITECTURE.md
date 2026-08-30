<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Grok Fleet Architecture & Ecosystem
**KB Entry**: grokster/grok_ecosystem/GROK_FLEET_ARCHITECTURE
**last_verified**: 2026-08-26 · **rot_class**: medium
**Sources**: `docs/research/R_OPENCODE_CONFIG_POLLUTION_FORENSICS_20260826.md` v3.0, `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` §7, `docs/coordination/BRIEFING_KALI_GROKSTER_RESPONSE_20260721.md`, `docs/research/R_GAP_CLOSURE_SWEEP_20260826.md`, provider fabric docs

---

## 1. The Phantom Supercomputer: Grok CLI Fleet

The Omega Engine possesses 8 Grok CLI accounts — a massive, untapped parallel inference resource.

**Architecture:**
- **8 Headless Instances**: Running via the Agent Client Protocol (ACP) over stdio.
- **Capabilities**: Each instance has 500K context (Grok 4.5), built-in `web_search`, `x_search`, `code_interpreter`.
- **Status**: **Blocked on V-1 Omega-Vault MVP** (GAP-08 → D-360′: vault → ACP smoke test → pool; not 4h fantasy). Credentials (browser cookies, 24–48h expiry) require automated rotation.

**Recommendation**: V-1 vault MVP first, then single ACP smoke test, then pool. Solves MaKaLi Council OOM pressure (routing 2 voices to cloud) and provides free parallel search.

---

## 2. xAI API Ecosystem & Pricing (Verified 2026-08-26)

**Model Selection Matrix (Canonical — Architect ruling):**

| Task | Primary Model | Fallback | Context | Pricing (input/output per 1M) |
|------|---------------|----------|---------|-------------------------------|
| Deep Research | Grok 4.5 (DeepSearch) | Web Grok-Research | 500K | $3/$15 |
| Long-Context Synthesis | Grok 4.3 | Grok 4.5 | 1M | $1.25/$2.50 |
| Code Implementation | Grok Build 0.1 | Grok 4.5 | 500K | $2/$10 |
| Reasoning/Think | Grok 4.5 (Think) | Web Grok-Reason | 500K | $3/$15 |
| Real-Time Pulse | Web Grok-Pulse | Grok 4.5 (X Search) | 500K | N/A (Web) |
| Cost-Optimized | Grok 4.3 | Grok 4.20 | 1M | $1.25/$2.50 |

**Key Verified Findings:**
- **Long-Context Penalty**: ≥200K tokens triggers 2x pricing across all models.
- **Server-Side Tools**: `web_search`, `x_search`, `code_execution` = **$5.00 per 1k calls** (not free).
- **Responses API**: Future of xAI interaction — `previous_response_id` for efficient multi-turn, replacing legacy Chat Completions.
- **Prompt Caching**: $0.20–$0.30/1M (keep system prompts/prefixes stable).
- **Batch API**: 20% discount for non-real-time synthesis.
- **Chunking**: Stay under 200K token penalty threshold.

---

## 3. Web Grok Persona Fleet

8 distinct personas configured as Web Grok Projects (`grok.com/project`). **No public API** — requires browser automation (Playwright) for provisioning.

| Persona | Specialization |
|---------|----------------|
| Research | DeepSearch, citation discipline |
| Reason | Think Mode, adversarial critique |
| Pulse | X real-time signal detection |
| Code | Security-first, perf-aware |
| Arch | Trade-off analysis, ADR generation |
| Creative | Imagine/Video, asset generation |
| Strategic | Risk-weighted scenario planning |
| Wildcard | Chaos agent, stress tests |

---

## 4. Grokster's Insights & Recommendations

- **Sovereignty Honesty**: We claim to "sever Big AI's umbilical cord," yet provider fabric (Ark §7) shows: local-first (native-gguf → lmster → Ollama) then cloud (Antigravity → Google → OCZ → OpenRouter). **We are cloud-assisted with a local fallback** — honest framing is a mandate (M7).
- **Grok Build Open Source** (Jul 15, 2026): Inspectable 8-way parallel subagent orchestrator (isolated Git worktrees, conflict resolution hooks) — replicable architecture for Omega complex coding tasks.
- **Self-Search Reflex (M26)**: My defining instinct — Epistemic Closure Reflex. Gap detected (confidence <0.7, factual claim, recency requirement) → autonomous search before responding. xAI server-side tools (`web_search`, `x_search`) are ideal engines at $5/1k cost.
- **ACP Bridge**: Grok Build ACP stdio → Omega Hivemind handoff packets (bidirectional). Session persistence: JSONL → MIAP execution log.

---

*⬡ OMEGA ⬡ GROKSTER ⬡ KB v2.1.3 ⬡ 2026-08-26*