<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 README Improvement Review — Omega Engine Public Debut

**AP Token**: `AP-RESEARCHER-README-REVIEW-20260902-v1.0.0`
**Date**: 2026-09-02
**Session**: `ses_fd81c19dcffe1nkbPqFg5kRt2v` (Researcher — standing EIS)
**Model**: `minimax/minimax-m3:free`
**Inputs**:
- `README.md` (314 lines) — the public face Kali created
- `data/entities/roc_racoon/workspace/mining_reports/ENGINE_VISION_TECH_DIG_20260902.md` (216 lines) — Roc-EIS forensic dig

---

## §0 Executive Summary

The README is **structurally strong but factually stale and strategically mis-positioned for a public debut.** It has an excellent hook ("Prometheus' Fire"), a clean 3-command quick start, and a compelling vision. But it makes **6 materially false claims** (verified against disk) that would be **instantly caught and punished** by the Hacker News / r/LocalLLaMA audiences I recommended in `COMMUNITY_LAUNCH_VENUES_20260902.md`. A public debut with a README that says "tests passing" when `make test` collects 0 tests, or "all 27 mandates enforced" when the meter reads 67.9%, is a **self-inflicted credibility wound**.

**The core problem**: The README reads like a **finished product** ("Production-ready" × 12, "All 27 enforced") when the engine is a **PROTOTYPE** (per Roc-EIS §0). For a debut, the README must either (a) be made **true** (fix the blockers first), or (b) be **honest about maturity** (say "alpha, here's what works, here's what's next"). Option (b) is the only launch-ready path today.

**Top 5 improvements** (in priority order):
1. **Fix or remove the false claims** (agents=11→13, mandates=22→27/28, model=Qwen→LFM2.5, tags=113→216, entities=12→24, "8-backend"→13 providers, "11 Temple-Grade gates"→actual target)
2. **Add a prominent, honest maturity/status banner** at the top (not buried at line 229)
3. **Lead with a concrete "what you can do in 5 minutes" demo** (a real terminal transcript, not just the 3 commands)
4. **Fix the Quick Start to match reality** (default model is now LFM2.5, not Qwen 1.7B)
5. **Restructure the "Why Omega Is Different" to be evidence-first** (show the gates, not just claim them)

---

## §1 Verified Factual Errors (Must Fix Before Debut)

All verified against disk 2026-09-02. These are **false statements** that a technical reviewer would catch within minutes.

| # | README Claim | Line | Disk Truth | Severity |
|---|--------------|------|-----------|----------|
| 1 | "11 agents (10 Pillar + 1 Oversoul)" | :210 | **13** agent files in `.opencode/agents/` | 🔴 CRITICAL |
| 2 | "All 22 enforced" (mandates) | :209 | **27/28** mandates; meter reads **67.9% (19/28)** | 🔴 CRITICAL |
| 3 | Default model "Qwen 1.7B GGUF, ~1.6GB" | :22, :93 | **LFM2.5-2.6B** (Q4_K_M, 1.67GB) per `providers.yaml:150-175` | 🔴 CRITICAL |
| 4 | "113 `[id-soft:]` tags across 39 files" | :214 | **216** tags across src/omega/ | 🟠 HIGH |
| 5 | "_omega_default — 12 tech role entities" | :158 | **24** entity YAMLs in `config/wads/_omega_default/entities/` | 🟠 HIGH |
| 6 | "Provider Fabric (8-backend fallback chain)" | :192 | **13** provider entries in `providers.yaml` | 🟠 HIGH |
| 7 | "Verify all 11 Temple-Grade gates" | :79 | `temple-grade` target runs 6 checks, not 11 | 🟠 HIGH |
| 8 | "Test Suite ... ✅" (implied passing) | :207-208 | `make test` **collects 0 tests** (`ModuleNotFoundError: omega.library`) | 🔴 CRITICAL |
| 9 | "All 27 enforced" / "All 27 Sovereign Mandates verified" | :290, :209 | 4 failures (M13, M16, M23, M27) | 🔴 CRITICAL |
| 10 | "10 entity pillars" | :63 | 13-agent fleet; pillar taxonomy unreconciled | 🟡 MEDIUM |

**Root cause**: The README was written against an **older snapshot** of the codebase (Qwen 1.7B era, 11 agents, 113 tags) and never updated as the engine evolved (LFM2.5 default, 13 agents, 216 tags, 24 entities). This is exactly the "manual index regen guarantees drift" anti-pattern (F4) — the README is a **hand-maintained artifact** that has drifted from disk truth.

**Recommended fix**: Add a **CI gate** that verifies README claims against disk (agent count, mandate count, model default, tag count). This is the README analog of `check_mandate_compliance.py`. Until then, every claim is a liability.

---

## §2 Strategic Positioning Issues

### 2.1 The Maturity Banner Is Buried (Line 229)

The README's most important honest disclosure — "⚠️ Current Status: Alpha via OpenCode" — is at **line 229**, after the Omegaverse section. A reader skimming the top sees "Production-ready" × 12 and "All 27 enforced" before ever reaching the honest caveat.

**Fix**: Move a **prominent, honest status banner to the very top** (after the title, before Quick Start):

```markdown
> ## ⚠️ Status: Alpha — Under Active Development
> Omega Engine is a **working prototype**, not a finished product. The core
> local-inference path, memory, and entity system work. The full CLI, installer,
> and CI gates are still being hardened. Expect rough edges. Feedback welcome.
```

This **pre-empts** the "this is vaporware" criticism by owning it. HN respects honest alpha announcements far more than overclaimed "production-ready" ones.

### 2.2 "Production-Ready" × 12 Is Overclaiming for a Prototype

The Verification table (lines 284-295) marks 12 features "✅ Production-ready" and claims "Temple-Grade (T1-T11) ✅ VERIFIED" and "All 27 enforced." Per Roc-EIS, the test suite is broken, mandate compliance is 67.9%, and CI fails. **A single "Production-ready" claim that's false poisons the whole table.**

**Fix**: Split into two honest columns:
- **"Working today"** (verified): local GGUF inference, sqlite-vec memory, soul persistence, Hivemind MCP, entity routing
- **"In progress / alpha"**: full CLI, installer robustness, CI gates, Temple-Grade, full mandate enforcement

### 2.3 The "Why Omega Is Different" Is Claim-First, Not Evidence-First

The table (lines 56-63) lists mandates as claims ("M8 Zero Telemetry — No phone-home, ever"). For a technical audience, **claims without evidence are marketing**. HN will ask "prove it."

**Fix**: For each mandate, show the **verifiable gate** and ideally a **one-line proof**:
- M8: "No phone-home, ever" → `make check-m8-zero-telemetry` → "grep for outbound HTTP in core returns 0"
- M1: "Zero `import asyncio`" → `make check-m1-anyio` → "0 asyncio imports in src/omega/"
- M23: "No soft failures" → `make check-m23-failure-integrity`

**But critically**: only claim the gates that **actually pass**. If `make test` is broken, don't put a passing badge on it.

---

## §3 Structure & Flow Improvements

### 3.1 Lead With a Real Demo, Not Just Commands

The Quick Start (lines 16-34) gives 3 commands but no **output**. A technical reader wants to see what actually happens. Add a **real terminal transcript**:

```markdown
$ ./scripts/install.sh
✓ Python 3.12 detected
✓ venv created at .venv/
✓ core deps installed (native, cli)
✓ local model LFM2.5-2.6B ready (1.67GB)
✓ Omega Engine v1.2.0 installed

$ omega talk "hello"
🦝 [native-gguf] Hello! I'm your sovereign local AI. 
   Running entirely on your CPU. No cloud. No telemetry.
```

A real transcript (verified to actually produce that output) is worth more than 10 marketing claims.

### 3.2 Reorder: Demo → Why → Architecture → Status → Extras

Current order: Quick Start → Why Different → What Is → Commands → Providers → Architecture → Dialectic → Omegaverse → **Status (buried)** → Requirements → v1.6.0 → License.

**Recommended order**:
1. Title + **Status banner** (new, top)
2. Quick Start + **real demo transcript**
3. What Omega Is (the pitch)
4. Why Different (evidence-first)
5. Architecture (keep, it's good)
6. Provider Setup (keep)
7. **Status / Maturity** (moved up, honest)
8. Dialectic System (keep)
9. Omegaverse (keep, clearly marked 🔮 Future)
10. Requirements, Roadmap, License

### 3.3 The Omegaverse Needs a Clear "Not Shipped" Label

The Omegaverse section (lines 203-226) is compelling but reads like it's real. Roc-EIS confirms the Godot bridge is a **standalone script with no runtime callers** (`godot_spatial_bridge.py` has 0 imports in `src/omega/`). 

**Fix**: Add a prominent label at the top of the section:
```markdown
> 🔮 **Vision / Phase 4 (2028)** — Not yet shipped. The Godot bridge and spatial
> index are foundational experiments; the VR renderer and P2P soul exchange
> are future work.
```

This prevents the "you claim VR but it doesn't work" criticism.

### 3.4 The "10 entity pillars" vs "13 agents" Confusion

Line 63 says "10 entity pillars" and line 82 says "10 entity pillars" again, but there are **13 agents** on disk and the pillar taxonomy is unreconciled (Roc-EIS I3). This confuses the reader about the actual fleet size.

**Fix**: Reconcile the taxonomy. Either (a) list the actual 13 agents, or (b) explain the relationship between "pillars" (conceptual domains) and "agents" (runtime personas). Don't leave both numbers floating.

---

## §4 Content Gaps (What's Missing)

| Gap | Why It Matters | Recommendation |
|-----|----------------|----------------|
| **No real demo/screenshot** | Technical audiences want to see it work | Add a terminal transcript or GIF |
| **No "what it's NOT" section** | Sets expectations; prevents "why not Ollama" | Add "Omega is not a chatbot, not an API wrapper, not a SaaS" |
| **No comparison table** | HN will ask "vs Ollama/LM Studio/AnythingLLM?" | Add a short honest comparison |
| **No security section** | Self-hosted agents raise security questions | Add "how we handle secrets, permissions, the M2 firewall" |
| **No contribution guide link** | Debut should invite contribution | Link CONTRIBUTING.md, good-first-issues |
| **No community/contact** | Where do people ask questions? | Add GitHub Discussions link |
| **No license explanation** | Apache 2.0 is good; explain what it means | "Free. Sovereign. Yours." is good, add one line on commercial use |
| **No install troubleshooting** | First-run failures kill adoption | Add a "Troubleshooting" section (C compiler, llama-cpp-python) |

---

## §5 Security Disclosure (Critical, Pre-Debut)

Roc-EIS found a **real Google OAuth client secret committed** to the repo (`OAuth-failure-incident-session-ses_fe8c.md:57`, `GOCSPX-***REDACTED-ROTATED***`), tracked across 10+ commits, **un-allowlisted**, and `check_secrets.py` exits 1 with 11 violations. This is **not a README problem** — it's a **launch blocker** that must be fixed before any public announcement.

**This is out of scope for the README review but must be flagged**: the README cannot be "improved" into launch-readiness while a real secret is exposed and the secret-scan CI gate fails. The README review assumes these blockers are fixed first.

---

## §6 Recommended README Rewrite (Target Structure)

Here is the recommended top-to-bottom structure for the debut README:

```markdown
# 🔱 Omega Engine — Sovereign AI Runtime
[badges: tests (only if passing), license, python, local-first, zero-telemetry]

> ⚠️ **Status: Alpha** — working prototype, under active development. [NEW]

## Quick Start — 3 Commands, No Cloud Key
[3 commands + REAL terminal transcript] [FIX model name → LFM2.5]

## What Omega Is
[the pitch: sovereign local-first AI runtime, models as infrastructure]

## Why Omega Is Different
[evidence-first mandate table: claim → gate → proof] [FIX counts]

## Architecture
[keep the good diagram; fix "12 tech role entities" → 24]

## Provider Setup
[keep; fix "8-backend" → 13 providers]

## The Dialectic System
[keep — this is a genuine differentiator]

## The Omegaverse (🔮 Phase 4 / 2028)
[keep, add prominent "not shipped" label]

## Current Status: Alpha
[moved UP; honest "what works / what's being hardened"]

## System Requirements
[keep]

## Roadmap
[keep]

## Contributing
[NEW — link CONTRIBUTING.md, good-first-issues, GitHub Discussions]

## License
[keep]
```

---

## §7 Priority Matrix

| Priority | Action | Effort | Blocker? |
|----------|--------|-------:|----------|
| **P0** | Fix 6 false claims (agents, mandates, model, tags, entities, providers) | 1h | ✅ Yes — credibility |
| **P0** | Add honest status banner to top | 0.5h | ✅ Yes — positioning |
| **P0** | Fix Quick Start model name (Qwen→LFM2.5) | 0.1h | ✅ Yes — correctness |
| **P1** | Add real demo transcript | 1h | No |
| **P1** | Reorder sections (status up top) | 0.5h | No |
| **P1** | Add "what it's NOT" + comparison | 1h | No |
| **P1** | Add security section | 1h | No |
| **P2** | Add contributing/community links | 0.5h | No |
| **P2** | Add troubleshooting section | 1h | No |
| **P2** | Add README-claims CI gate | 4h | No (but recommended) |

**Total**: ~10h of README work. **But the P0 items are blocked by the underlying launch blockers** (broken tests, committed secret, 67.9% compliance) — the README can be made honest now, but it cannot be made "production-ready" until the engine actually is.

---

## §8 Verdict

**The README is a strong draft with a fatal flaw: it overclaims.** For a public debut, honesty is the highest-value asset. The single most important change is to **replace every unverifiable "Production-ready / All enforced" claim with an honest, evidence-first status** — and to move that honest status to the top where readers see it first.

**Recommended next step**: Fix the P0 factual errors now (1h), add the status banner (0.5h), and **do not launch until the underlying blockers (C1 test suite, C2 secret, C3 compliance) are resolved**. A README that says "alpha, here's what works, here's what's next" will earn more trust from the HN/r/LocalLLaMA audience than a README that falsely claims production-readiness and gets caught.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ README-REVIEW ⬡ 2026-09-02 ⬡ 6 FALSE CLAIMS ⬡ 10 IMPROVEMENTS ⬡ 10h EFFORT*
