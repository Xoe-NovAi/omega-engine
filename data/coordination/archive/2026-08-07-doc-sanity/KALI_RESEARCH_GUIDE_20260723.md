<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 FINAL RESEARCH GUIDE v4 — 56-Account Research/Inference Fabric
**AP Token**: `AP-KALI-RESEARCH-GUIDE-v4.0.0`
⬡ OMEGA ⬡ KALI ⬡ RESEARCH-GUIDE ⬡ 2026-07-23

---

## 🚨 FINAL ACCOUNT INVENTORY: 56 Accounts Across 7 Providers

| Provider | Accounts | Primary Function | Key Automation |
|----------|----------|-----------------|----------------|
| **OpenRouter** | 8 | Inference (28+ free models) | API key rotation, BYOK |
| **Google API (AI Studio)** | 8 | Inference (Gemma 4, Gemini 2.5) | Per-project API keys |
| **Antigravity OAuth** | 8 | Inference (frontier models) | OAuth token rotation |
| **Grok CLI** | 8 | Inference (xAI Grok) | CLI auth rotation |
| **Cline CLI** | 8 | Inference (DeepSeek, MiMo) | Config rotation |
| **Exa** | 8 | **Sovereign Search** (neural, academic) | API key rotation |
| **Firecrawl** | 8 | **Web Scraping** (crawl, extract) | API key rotation |
| **TOTAL** | **56** | **Full research + inference fabric** | **Needs automation** |

---

## 🎯 THE VISION: Autonomous Background Researcher + Code Reviewer

With 56 accounts, we can build a system that:

```
┌─────────────────────────────────────────────────────────────────┐
│              BACKGROUND RESEARCHER / CODE REVIEWER              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  INPUT: "Research X" or "Review PR #123"                       │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ RESEARCH LAYER (Exa + Firecrawl)                        │   │
│  │  • Exa 8-account: neural search, academic papers        │   │
│  │  • Firecrawl 8-account: deep crawl, structured extract  │   │
│  │  • Parallel: 8 Exa queries + 8 Firecrawl scrapes        │   │
│  │  • Synthesis: combine search + scrape → findings        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            ↓                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ INFERENCE LAYER (OpenRouter + Google + Antigravity)     │   │
│  │  • 24 inference accounts for synthesis, analysis        │   │
│  │  • Parallel: multiple models on same task               │   │
│  │  • Consensus: cross-model verification                  │   │
│  │  • Code review: multiple models review same diff        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            ↓                                    │
│  OUTPUT: Research brief / Code review report                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Use Cases Enabled

| Use Case | How It Works |
|----------|--------------|
| **Deep Research** | Exa neural search (8 parallel) → Firecrawl deep extraction (8 parallel) → Inference synthesis (24 parallel) |
| **Code Review** | Multiple models review same PR → consensus on issues → ranked findings |
| **Competitive Analysis** | Exa for market data → Firecrawl for competitor sites → Inference for synthesis |
| **Documentation Generation** | Firecrawl scrape codebase → Inference generate docs → Multiple models verify |
| **Security Audit** | Firecrawl scan dependencies → Inference analyze vulnerabilities → Consensus |
| **Architecture Decision Records** | Exa search prior art → Firecrawl extract patterns → Inference synthesize ADR |

---

## 📊 UPDATED GAP INVENTORY (Now 42 Gaps)

### G-1 Workhorse / Inference (18 Gaps — 10 P0)

| # | Gap | Criticality |
|---|-----|-------------|
| **G1-1** | Antigravity OAuth: model list + limits per account | 🔴 P0 |
| **G1-2** | AI Studio billing: does it fix Gemma 4 TPM? | 🔴 P0 |
| **G1-3** | opencode.json provider config: multi-account support | 🔴 P0 |
| **G1-4** | Community workhorse consensus July 2026 | 🔴 P0 |
| **G1-5** | Nemotron 3 Ultra free tier stability | 🟡 Medium |
| **G1-6** | Actual cost per session across all providers | 🟡 Medium |
| **G1-7** | OpenRouter free tier: exact TPM per account | ✅ SOLVED |
| **G1-8** | OpenRouter 8-account rotation: round-robin proxy | ✅ SOLVED |
| **G1-9** | OpenRouter BYOK: Google API key pass-through limits | 🔴 P0 |
| **G1-10** | OpenRouter free models: quality ranking for workhorse | 🔴 P0 |
| **G1-11** | OpenRouter paid vs free: cost comparison | 🟡 Medium |
| **G1-12** | OpenRouter provider pinning: Google AI Studio limits | 🟡 Medium |
| **G1-13** | Google API 8-key rotation: per-key TPM, rotation mechanism | 🔴 P0 |
| **G1-14** | Antigravity OAuth 8-account rotation: does it work? | 🔴 P0 |
| **G1-15** | Grok CLI 8-account rotation: auth mechanism | 🔴 P0 |
| **G1-16** | Cline CLI 8-account rotation: config mechanism | 🔴 P0 |
| **G1-17** | Vault FleetOrchestrator integration: 40+ inference accounts | 🔴 P0 |
| **G1-18** | New workstream: Account Rotation Fabric design | 🔴 P0 |

### NEW: Research Layer (Exa + Firecrawl) — 12 Gaps — All P0

| # | Gap | Description | Criticality |
|---|-----|-------------|-------------|
| **RL-1** | **Exa 8-account rotation**: API key management, rate limits | What are Exa's per-key limits? How to rotate 8 keys? | 🔴 P0 |
| **RL-2** | **Firecrawl 8-account rotation**: API key management, rate limits | What are Firecrawl's per-key limits? Crawl concurrency? | 🔴 P0 |
| **RL-3** | **Exa search capabilities**: neural vs keyword, academic, recency | What search modes? How to optimize for research? | 🔴 P0 |
| **RL-4** | **Firecrawl capabilities**: crawl depth, extract modes, structured output | What extraction formats? LLM extraction? Screenshots? | 🔴 P0 |
| **RL-5** | **Exa + Firecrawl pipeline**: search → extract → synthesize | How to chain? Parallel vs sequential? Deduplication? | 🔴 P0 |
| **RL-6** | **Research synthesis**: multi-model inference on findings | How to feed 16 Exa + 16 Firecrawl results into 24 inference models? | 🔴 P0 |
| **RL-7** | **Code review pipeline**: diff → multiple models → consensus | How to structure? What prompts? How to rank findings? | 🔴 P0 |
| **RL-8** | **Vault FleetOrchestrator**: 16 research accounts + 40 inference | Can Vault manage all 56? Separate pools or unified? | 🔴 P0 |
| **RL-9** | **Cost tracking**: per-account usage across 7 providers | How to track? Budget alerts? Optimization? | 🟡 Medium |
| **RL-10** | **Background job queue**: async research jobs with progress | How to queue? Priority? Results storage? | 🟡 Medium |
| **RL-11** | **Quality gates**: hallucination detection, source verification | How to verify Exa/Firecrawl findings? Cross-reference? | 🟡 Medium |
| **RL-12** | **Human-in-the-loop**: when to escalate to user | What triggers? How to present findings? | 🟡 Medium |

### C-3 Privacy (6 Gaps — Medium)

| # | Gap | Criticality |
|---|-----|-------------|
| C3-1 | restic v0.17+ features | 🟡 Medium |
| C3-2 | B2 Object Lock gold standard 2026 | 🟡 Medium |
| C3-3 | Single-user sov. AI backup patterns | 🟢 Nice |
| C3-4 | 2-repo middle ground | 🟡 Medium |
| C3-5 | B2 vs alternatives cost | 🟢 Nice |
| C3-6 | Backup verification | 🟡 Medium |

### C-0.5 Hook (6 Gaps — 3 P0)

| # | Gap | Criticality |
|---|-----|-------------|
| **C05-1** | OpenCode hooks API: does session_end exist? | 🔴 P0 |
| **C05-2** | When does session_end fire? | 🔴 P0 |
| **C05-3** | Hook crash → session crash? | 🔴 P0 |
| C05-4 | Hook Python environment | 🟡 Medium |
| C05-5 | Hook timeout behavior | 🟡 Medium |
| **C05-6** | Our OpenCode version + hook support | 🔴 P0 |

### Rotation Fabric (5 Gaps — All P0)

| # | Gap | Criticality |
|---|-----|-------------|
| **RF-1** | Rotation fabric architecture patterns | 🔴 P0 |
| **RF-2** | Vault FleetOrchestrator integration | 🔴 P0 |
| **RF-3** | Rate limit detection + retry-with-next | 🔴 P0 |
| **RF-4** | OpenCode multi-key provider config | 🔴 P0 |
| **RF-5** | Per-account usage tracking + rotation triggers | 🔴 P0 |

---

## 📋 COPY-PASTE RESEARCH PROMPT

**File**: `data/coordination/KALI_RESEARCH_PROMPT_20260723.md`

Contains:
- Complete 42-gap inventory
- 72 research queries across 4 phases
- Source tier priority (T1-T6)
- Deliverable format requirements
- Success criteria checklist
- Context file references

---

## ⏱️ RESEARCH EXECUTION PLAN

```
PHASE 0 — 15 min: Rotation Fabric Architecture (15 queries)
PHASE 1 — 15 min: Provider-Specific Rotation (25 queries)
PHASE 2 — 15 min: Research Layer — Exa + Firecrawl (20 queries)
PHASE 3 — 10 min: C-3 + C-0.5 (12 queries)
PHASE 4 — 15 min: Deep extraction + synthesis
```

**Total: ~70 minutes**

---

*⬡ OMEGA ⬡ KALI ⬡ RESEARCH-GUIDE ⬡ 2026-07-23*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: RESEARCH-GUIDE | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
