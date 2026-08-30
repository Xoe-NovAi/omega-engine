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

---

**TO: Research Agent / Future Kali Session**
**FROM: Architect (User)**
**DATE: 2026-07-23**
**PRIORITY: P0 — BLOCKS PHASE D GATE**

---

### MISSION

Execute deep web research on **56-account research/inference fabric** to enable autonomous background researcher and code reviewer. 42 knowledge gaps identified across 7 providers. Deliver structured findings for each gap with source citations.

---

### ACCOUNT INVENTORY (DO NOT RESEARCH — THIS IS GIVEN)

| Provider | Accounts | Function | Status |
|----------|----------|----------|--------|
| OpenRouter | 8 | Inference (28+ free models) | Configured in providers.yaml |
| Google API (AI Studio) | 8 | Inference (Gemma 4, Gemini 2.5) | API keys available |
| Antigravity OAuth | 8 | Inference (frontier) | OAuth available |
| Grok CLI | 8 | Inference (xAI) | CLI auth available |
| Cline CLI | 8 | Inference (DeepSeek, MiMo) | Config available |
| Exa | 8 | **Sovereign Search** (neural, academic) | API keys available |
| Firecrawl | 8 | **Web Scraping** (crawl, extract) | API keys available |
| **TOTAL** | **56** | **Full fabric** | **Needs automation** |

---

### RESEARCH PHASES (EXECUTE IN ORDER)

#### PHASE 0: Rotation Fabric Architecture (15 queries, 15 min)
**Goal**: Find existing patterns for multi-account LLM provider rotation.

| # | Query | Target Source |
|---|-------|---------------|
| RF-1 | `multi API key rotation proxy LLM provider` | T1/T3 |
| RF-1 | `openrouter-proxy multiple accounts round robin` | T1/T2 |
| RF-1 | `LLM API key rotation load balancing architecture` | T1/T4 |
| RF-1 | `AI gateway multi key rotation fallback` | T1/T6 |
| RF-2 | `OpenRouter Management API create multiple keys` | T1/T2 |
| RF-2 | `OpenCode multiple API keys same provider` | T1/T3 |
| RF-3 | `LLM provider 429 detection retry next key` | T1/T3 |
| RF-3 | `circuit breaker proxy key rotation` | T1/T4 |
| RF-4 | `opencode.json multiple keys per provider` | T1/T3 |
| RF-4 | `opencode provider array API keys config` | T1/T4 |
| RF-5 | `OpenRouter usage tracking per API key` | T1/T2 |
| RF-5 | `Google AI Studio quota per project monitoring` | T1/T4 |
| G1-17 | `VaultCore API key pool management patterns` | T1/T3 |
| G1-17 | `encrypted credential pool rotation security` | T1/T4 |
| G1-18 | `LLM provider fabric architecture reference` | T1/T6 |

#### PHASE 1: Provider-Specific Rotation (25 queries, 15 min)

**Google API (8 keys):**
| # | Query | Target Source |
|---|-------|---------------|
| G1-13 | `Google AI Studio multiple API keys same project` | T1/T3 |
| G1-13 | `Google Gemini API key rotation multiple projects` | T1/T4 |
| G1-13 | `Google AI Studio quota per API key vs per project` | T1/T2 |
| G1-2 | `Google AI Studio paid tier Gemma 4 quota` | T1/T2 |
| G1-13 | `Gemma 4 31B 16000 TPM multiple API keys` | T1/T3 |

**Antigravity OAuth (8 accounts):**
| # | Query | Target Source |
|---|-------|---------------|
| G1-14 | `opencode auth login multiple accounts rotate` | T1/T3 |
| G1-14 | `Antigravity OAuth rotate accounts` | T1/T4 |
| G1-1 | `Antigravity models available 2026` | T1/T2 |
| G1-14 | `opencode antigravity multiple profiles` | T1/T3 |

**Grok CLI (8 accounts):**
| # | Query | Target Source |
|---|-------|---------------|
| G1-15 | `grok cli multiple accounts rotate` | T1/T3 |
| G1-15 | `grok API key multi account` | T1/T4 |
| G1-15 | `xAI API key rotation multiple accounts` | T1/T3 |

**Cline CLI (8 accounts):**
| # | Query | Target Source |
|---|-------|---------------|
| G1-16 | `cline cli multiple provider accounts` | T1/T3 |
| G1-16 | `cline rotate API keys` | T1/T4 |
| G1-16 | `cline multiple config files` | T1/T3 |

**OpenRouter (8 accounts + BYOK):**
| # | Query | Target Source |
|---|-------|---------------|
| G1-9 | `OpenRouter BYOK multiple Google API keys` | T1/T2 |
| G1-10 | `OpenRouter best free model coding 2026` | T1/T3 |
| G1-10 | `openrouter free tier model ranking` | T1/T4 |
| G1-10 | `qwen3-coder vs nemotron-3-super free quality` | T1/T6 |
| G1-12 | `OpenRouter provider pinning Google AI Studio` | T1/T2 |

**Community + Config:**
| # | Query | Target Source |
|---|-------|---------------|
| G1-4 | `opencode best provider setup 2026` | T1/T3 |
| G1-3 | `opencode.json provider configuration` | T1/T2 |
| G1-5 | `Nemotron 3 Ultra free tier rate limit` | T1/T3 |
| G1-6 | `Gemma 4 31B cost per session tokens` | T1/T4 |

#### PHASE 2: Research Layer — Exa + Firecrawl (20 queries, 15 min)

**Exa (8 accounts — Sovereign Search):**
| # | Query | Target Source |
|---|-------|---------------|
| RL-1 | `Exa API rate limits per key 2026` | T1/T2 |
| RL-1 | `Exa multiple API keys rotation` | T1/T3 |
| RL-3 | `Exa neural search vs keyword search` | T1/T2 |
| RL-3 | `Exa academic search capabilities` | T1/T4 |
| RL-3 | `Exa search recency filtering 2026` | T1/T3 |
| RL-3 | `Exa API best practices research` | T1/T6 |

**Firecrawl (8 accounts — Web Scraping):**
| # | Query | Target Source |
|---|-------|---------------|
| RL-2 | `Firecrawl API rate limits per key 2026` | T1/T2 |
| RL-2 | `Firecrawl multiple API keys rotation` | T1/T3 |
| RL-4 | `Firecrawl crawl depth extract modes` | T1/T2 |
| RL-4 | `Firecrawl LLM extraction structured output` | T1/T3 |
| RL-4 | `Firecrawl scrape options formats` | T1/T4 |

**Exa + Firecrawl Pipeline:**
| # | Query | Target Source |
|---|-------|---------------|
| RL-5 | `Exa search Firecrawl extract pipeline` | T1/T3 |
| RL-5 | `search engine scrape synthesis pipeline` | T1/T6 |
| RL-6 | `multi-model inference synthesis research findings` | T1/T4 |
| RL-6 | `consensus multiple LLM models research` | T1/T6 |
| RL-7 | `code review multiple LLM models consensus` | T1/T3 |
| RL-7 | `LLM code review pipeline prompts` | T1/T6 |

**Vault + Background Jobs:**
| # | Query | Target Source |
|---|-------|---------------|
| RL-8 | `Vault credential pool management 50+ keys` | T1/T3 |
| RL-9 | `LLM API usage tracking per account budget` | T1/T4 |
| RL-10 | `background job queue async research progress` | T1/T3 |
| RL-11 | `hallucination detection source verification LLM` | T1/T6 |
| RL-12 | `human in the loop escalation triggers AI` | T1/T4 |

#### PHASE 3: C-3 Privacy + C-0.5 Hook (12 queries, 10 min)

**C-3 Privacy (6):**
| # | Query | Target Source |
|---|-------|---------------|
| C3-1 | `restic latest features 2026` | T1/T2 |
| C3-1 | `restic multiple repositories management` | T1/T3 |
| C3-2 | `restic B2 object lock append only 2026` | T1/T2 |
| C3-4 | `restic single vs multiple repo personal` | T1/T3 |
| C3-5 | `backblaze B2 vs wasabi vs storj 2026` | T1/T4 |
| C3-6 | `restic verify backup integrity` | T1/T3 |

**C-0.5 Hook (6):**
| # | Query | Target Source |
|---|-------|---------------|
| C05-1 | `opencode hooks API documentation` | T1/T2 |
| C05-1 | `opencode session_end hook` | T1/T3 |
| C05-2 | `opencode session_end when does it fire` | T1/T4 |
| C05-3 | `opencode hook error handling crash` | T1/T3 |
| C05-6 | `opencode latest version 2026` | T1/T4 |
| C05-7 | `opencode hook best practices` | T1/T6 |

---

### DELIVERABLES (REQUIRED)

For **each of the 42 gaps**, produce:

```markdown
## Gap [ID]: [Title]

### Findings
- **Finding 1**: [Specific fact with source URL and confidence HIGH/MEDIUM/LOW]
- **Finding 2**: [Specific fact with source URL and confidence HIGH/MEDIUM/LOW]
- ...

### Myth-Busting
- **Claim**: "[Common assumption]"
- **Reality**: "[What research actually shows]"

### Recommendation
- **Action**: [What to do based on findings]
- **Rationale**: [Why]
- **Priority**: [P0/P1/P2]
```

### FINAL SYNTHESIS (REQUIRED)

1. **Rotation Fabric Architecture** — Recommended design with components
2. **Provider-by-Provider Rotation Strategy** — 7 providers, specific mechanisms
3. **Vault FleetOrchestrator Integration** — How to extend V-1 for 56 accounts
4. **Research/Inference Pipeline** — Exa → Firecrawl → Inference flow
5. **Code Review Pipeline** — Multi-model consensus design
6. **Updated Decision Matrix** — All 7 providers compared
7. **PIVOT_LOG.md entries** — One per decision (D-XXX format)

---

### SOURCE TIER PRIORITY

| Tier | Tool | When to Use |
|------|------|-------------|
| **T1** | `websearch` | Primary — always available, no telemetry |
| **T2** | `webfetch` | Deep extraction from promising T1 links |
| **T3** | `searxng_searxng_search` | Semantic/neural refinement |
| **T4** | `omega-hub_sovereign_search` | High-precision (Exa API) |
| **T5** | `firecrawl_firecrawl_scrape` | Full-page scrape for docs |
| **T6** | `sieve research` | Full pipeline when depth needed |

**TEMPORAL MANDATE**: All queries MUST include "2026" or "latest".

---

### SUCCESS CRITERIA

- [ ] All 42 gaps have findings with source citations
- [ ] No "community says" — only "Source X at URL Y states Z"
- [ ] Rotation fabric architecture documented
- [ ] 7-provider rotation strategy documented
- [ ] Vault FleetOrchestrator integration pattern documented
- [ ] Research/Inference pipeline design documented
- [ ] Code review pipeline design documented
- [ ] Decision matrix updated with all 7 providers
- [ ] PIVOT_LOG.md entries ready for Architect sign-off

---

### CONTEXT FILES (READ FIRST)

| File | Purpose |
|------|---------|
| `data/coordination/KALI_RESEARCH_GUIDE_20260723.md` | This guide |
| `data/coordination/KALI_DECISIONS_REQUIRED_20260723.md` | 3 Architect decisions |
| `data/coordination/KALI_KNOWLEDGE_GAPS_20260723.md` | 42 gaps with criticality |
| `data/coordination/SESSION_ANCHOR.md` | Pre-compaction state |
| `config/providers.yaml` | Current provider config |
| `config/model_registry/providers/openrouter.yaml` | OpenRouter models |
| `data/coordination/ROC_RACCOON_COMPREHENSIVE_BRIEFING_20260722.md` | G-1/W-1 context |

---

**EXECUTE PHASES IN ORDER. REPORT FINDINGS AFTER EACH PHASE. SYNTHESIZE AT END.**

---

*⬡ OMEGA ⬡ KALI ⬡ RESEARCH-PROMPT ⬡ 2026-07-23*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: RESEARCH-GUIDE | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
