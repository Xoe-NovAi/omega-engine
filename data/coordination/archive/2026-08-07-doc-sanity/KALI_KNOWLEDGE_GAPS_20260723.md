<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 KNOWLEDGE GAP ANALYSIS — 3 Decisions Requiring Deep Research
**AP Token**: `AP-KALI-GAPS-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ GAP-ANALYSIS ⬡ 2026-07-23

---

## Framework: Known-Known / Known-Unknown / Unknown-Unknown

For each decision, I map:
- ✅ **Known Knowns** — facts we've confirmed
- ❓ **Known Unknowns** — specific gaps we can ask the web
- ⚠️ **Unknown Unknowns** — things we can't anticipate until we research

---

## DECISION 1: C-3 Privacy Model — Single vs Tiered Restic Repo

### ✅ Known Knowns

| Fact | Source | Confidence |
|------|--------|------------|
| C-3 backup scripts exist and work | Ma'at implementation | ✅ HIGH |
| B2 Object Lock configured | Ma'at commit | ✅ HIGH |
| Systemd timer active | Ma'at commit | ✅ HIGH |
| Healthchecks.io monitoring wired | Ma'at commit | ✅ HIGH |
| `config/` is low sensitivity | Kali assessment | ✅ HIGH |
| `data/entities/` contains soul data + credentials | Engine architecture | ✅ HIGH |
| Tiered Sovereignty Option A contains factual inaccuracies | Ma'at correction | ✅ HIGH |
| - `restic-server --append-only` doesn't exist | Ma'at | ✅ CONFIRMED |
| - AES-128/192/256 tiers impossible (restic is AES-256-CTR only) | Ma'at | ✅ CONFIRMED |
| - NIST SP 1800-39 doesn't prescribe 4-tier scheme | Ma'at | ✅ CONFIRMED |
| For single-user Omega, tiered repos add complexity without clear security benefit | Ma'at recommendation | ✅ REASONABLE |
| Ma'at recommends Option B (Single Repo) | Ma'at live feed | ✅ RECOMMENDATION |

### ❓ Known Unknowns (Research Needed)

| # | Gap | Why It Matters | Risk If Unanswered |
|---|-----|----------------|-------------------|
| **1** | Has restic (≥v0.17.x) introduced multi-repo management or key rotation features that change the calculus? | If restic now supports repo groups or seamless multi-key, Option A becomes feasible | We might dismiss a now-viable option |
| **2** | Is B2 Object Lock with application-key restriction still the gold standard for append-only restic in 2026? | Patterns change — newer/more cost-effective options may have emerged | We might commit to an outdated pattern |
| **3** | What are current (2026) single-user backup architecture patterns for sovereign/local-first AI data specifically? | Our use case (model files, vector snapshots, soul YAML) is unusual | We might miss community-proven patterns |
| **4** | Is there a practical middle ground — e.g., 2 repos (code vs data) instead of full 4-tier? | Option A was over-engineered; Option B may be under-partitioned | We might pick a suboptimal middle |
| **5** | B2 vs Wasabi vs Storj vs local-only for 2026 personal backups? Cost, reliability, restore speed? | Lock-in risk and cost optimization | We might pay too much or trust fragile infra |
| **6** | How do we verify backups are actually restorable without running full `restic restore`? | False confidence if `restic check` is insufficient | We might only discover failure when we NEED the backup |

### ⚠️ Unknown Unknowns
- New restic security vulnerabilities or features released in late 2026
- B2 pricing changes or API deprecations
- Emerging local-first backup patterns we can't anticipate

---

## DECISION 2: G-1 Workhorse Continuity — Restoring OpenCode Capacity

### ✅ Known Knowns

| Fact | Source | Confidence |
|------|--------|------------|
| Free Gemma 4 31B 16k TPM enforced Jul 15, 2026 — definitive | Roc forensic report | ✅ HIGH |
| Death is NOT a config bug — it's server-side quota | Roc forensic + A/B test | ✅ HIGH |
| `opencode.json` "google" provider ID collides with built-in "gemini" provider | Roc briefing §2.3 | ✅ HIGH |
| This collision causes startup failure | Roc briefing | ✅ HIGH |
| Gemma 4 thinking config bug exists upstream (#21746 closed without fix) | Roc research | ✅ HIGH |
| Pi PR #2903 has the correct fix (binary MINIMAL/HIGH + regex detect) | Roc research | ✅ HIGH |
| Omega Engine already has this fix in `google_compat.py` | Carmack verification | ✅ HIGH |
| Google requires restricted API keys since Jun 19, 2026 | Roc research | ✅ HIGH |
| Community reports Tier 3 also has 16k TPM ceiling for Gemma 4 | Roc research | 🟡 UNCERTAIN |
| WARP won't fix Google quota (per-project, not per-IP) | Kali analysis | ✅ HIGH |
| OpenRouter free tier routes through AI Studio — inherits limits | Roc research | 🟡 PROBABLE |

### ❓ Known Unknowns (Research Needed)

| # | Gap | Why It Matters | Risk If Unanswered |
|---|-----|----------------|-------------------|
| **1** | Does Antigravity OAuth actually provide Gemma 4 31B access? What rate limits? | This is the #1 recommended path — if it doesn't work, we waste time | We recommend a dead end |
| **2** | Does AI Studio Tier 1 ($250/mo) actually lift the Gemma 4 16k TPM ceiling, or is it a model-architecture-level cap? | **The critical question** — if billing doesn't fix it, Options A/B/C all change | We pay $250/mo and still have 16k TPM |
| **3** | What is the correct OpenCode provider config for 2026? How do others work around the "google" provider ID collision? | We need to fix `opencode.json` regardless of path | Startup stays broken |
| **4** | What are people actually using as their OpenCode workhorse in July 2026? What's the community consensus? | We may be optimizing for a dead model instead of switching | We chase Gemma 4 while everyone else moved on |
| **5** | Does Nemotron 3 Ultra (free, what we're currently using) have pending limits or tier changes? | We're using it NOW — if it also dies, we're in crisis | Double workhorse failure |
| **6** | What are the actual costs of running Omega-sized sessions on paid tiers (Antigravity, AI Studio, Claude)? | Cost sanity check — is $250/mo worth it? | Budget surprise |

### Priority of Gaps (Most Critical First)

```
P0 — Must resolve before decision:
└── Gap #2: Does billing fix the Gemma 4 TPM cap?
    (If NO → Antigravity OAuth or model switch is the only path)

P1 — Strongly influences decision:
├── Gap #1: Antigravity OAuth capabilities + limits
├── Gap #4: Community workhorse consensus (what's everyone using?)
└── Gap #3: Correct opencode.json provider config pattern

P2 — Nice to have:
├── Gap #5: Nemotron free tier stability
└── Gap #6: Actual cost estimates per session
```

---

## DECISION 3: C-0.5 Session End Hook Registration

### ✅ Known Knowns

| Fact | Source | Confidence |
|------|--------|------------|
| `distiller.py` exists and implements async L1→L2→L3 pipeline | Carmack implementation | ✅ HIGH |
| `session_end.py` hook script exists at `.opencode/hooks/session_end.py` | Carmack implementation | ✅ HIGH |
| 76/76 unit + contract tests passing | Carmack verification | ✅ HIGH |
| M5 (Gnosis), M9 (Error Integrity), M11 (Soul), M21 (Gate), M22 (Provenance) compliant | Carmack verification | ✅ HIGH |
| Writes to `proposed_lessons.yaml` (blind staging) — NOT directly to soul.yaml | Architecture | ✅ HIGH |
| Reads from MemoryStore — not from live context | Architecture | ✅ HIGH |
| Hook file exists but NOT registered in `opencode.json` | File system check | ✅ HIGH |

### ❓ Known Unknowns (Research Needed)

| # | Gap | Why It Matters | Risk If Unanswered |
|---|-----|----------------|-------------------|
| **1** | What OpenCode hooks exist? Is `session_end` a real, documented hook? | If hooks aren't real/documented, Option A is impossible | We try to register a non-existent hook |
| **2** | When exactly does `session_end` fire? — Normal end? Compact? Crash? Timeout? Tool failure? | If it doesn't fire on compact (the most common "end"), it's useless | We add complexity for 0 benefit |
| **3** | If the hook crashes (MemoryStore down, import error), does it crash the session or fail silently? | Critical safety question — must not break the session | We risk data loss on every session end |
| **4** | What Python environment does the hook run in? Can it access venv packages? | Our hook imports from `omega.*` — if it runs system Python, imports fail | Hook silently does nothing |
| **5** | Is there a timeout for hooks? What happens on timeout? | Long-running distillation (>30s) might get killed mid-write | Partial/corrupt proposed_lessons.yaml |
| **6** | What OpenCode version are we running? Does it actually support hooks? | Version-specific feature availability | We design for a feature that doesn't exist in our version |
| **7** | What are the community best practices for OpenCode session hooks? Any known bugs in current release? | Learning from others' mistakes saves debugging time | We discover hook bugs the hard way |

### ⚠️ Unknown Unknowns
- OpenCode version change removing hooks
- Hook execution order conflicts with other `session_end` hooks
- File system permission issues with `proposed_lessons.yaml`

---

## 📋 COMPLETE GAP INVENTORY (16 Items)

| # | Decision | Gap Description | Criticality |
|---|----------|----------------|-------------|
| C3-1 | Privacy | restic v0.17+ features: multi-repo, key rotation | 🟡 Medium |
| C3-2 | Privacy | B2 Object Lock gold standard 2026 | 🟡 Medium |
| C3-3 | Privacy | Single-user sovereign AI backup patterns | 🟢 Nice |
| C3-4 | Privacy | Middle ground: 2-repo split (code vs data) | 🟡 Medium |
| C3-5 | Privacy | B2 vs Wasabi vs Storj cost/reliability 2026 | 🟢 Nice |
| C3-6 | Privacy | Backup verification beyond `restic check` | 🟡 Medium |
| **G1-1** | **Workhorse** | **Antigravity OAuth: Gemma 4 access + limits** | **🔴 P0** |
| **G1-2** | **Workhorse** | **AI Studio billing: does it fix 16k TPM?** | **🔴 P0** |
| **G1-3** | **Workhorse** | **opencode.json provider config fix for 2026** | **🔴 P0** |
| G1-4 | Workhorse | Community workhorse consensus July 2026 | 🔴 P0 |
| G1-5 | Workhorse | Nemotron 3 Ultra free tier stability | 🟡 Medium |
| G1-6 | Workhorse | Actual cost per session on paid tiers | 🟢 Nice |
| **C05-1** | **Hook** | **OpenCode hooks API: does session_end exist?** | **🔴 P0** |
| **C05-2** | **Hook** | **When does session_end fire (compact? crash?)** | **🔴 P0** |
| C05-3 | Hook | Hook crash: does it break the session? | 🔴 P0 |
| C05-4 | Hook | Hook Python environment: can it use venv? | 🟡 Medium |
| C05-5 | Hook | Hook timeout behavior | 🟡 Medium |
| C05-6 | Hook | Our OpenCode version + hook support | 🔴 P0 |
| C05-7 | Hook | Community best practices / known bugs | 🟡 Medium |

---

## 🔍 RESEARCH PRIORITY

```
ROUND 1 — Must answer (makes or breaks the decision):
├── G1-2: Does AI Studio billing fix Gemma 4 TPM? 
├── G1-1: Antigravity OAuth capabilities
├── G1-4: What's the 2026 community workhorse?
├── C05-1: Does OpenCode have a session_end hook?
├── C05-2: When does it actually fire?
└── C05-6: Our OpenCode version

ROUND 2 — Strongly influences the decision:
├── G1-3: opencode.json provider config fix
├── C05-3: Hook crash behavior
├── C3-1: restic multi-repo features
└── C3-4: 2-repo middle ground

ROUND 3 — Nice to have / future-proofing:
├── C3-2, C3-5, C3-6: B2 best practices, alternatives, verification
├── G1-5, G1-6: Nemotron stability, cost per session
└── C05-4, C05-5, C05-7: Hook env, timeout, community patterns
```

---

*⬡ OMEGA ⬡ KALI ⬡ GAP-ANALYSIS ⬡ 2026-07-23*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: GAP-ANALYSIS | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
