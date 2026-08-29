# 🔱 ARCHITECT DECISIONS REQUIRED — 2026-07-23
**AP Token**: `AP-KALI-DECISIONS-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ DECISIONS-REQUIRED ⬡ 2026-07-23

---

Three decisions are blocking Phase D gate progression. Each has been researched to initial recommendation but requires **deeper web research** to finalize.

---

## DECISION 1: C-3 Privacy Model

**Question**: How should Restic backup handle data sensitivity?

**Context**: C-3 Restic 3-2-1 Backup is implemented (scripts, systemd timer, B2 Object Lock, Healthchecks.io). The backup covers `config/` (low sensitivity) and `data/entities/` (high sensitivity — soul data, credentials).

**Options**:
| Option | Description | Initial Research |
|--------|-------------|-----------------|
| **A: Tiered Sovereignty** | Multiple restic repos with separate encryption keys per sensitivity tier | 🟡 Ma'at found inaccuracies in initial report — `restic-server --append-only` doesn't exist, AES tiers impossible, NIST scheme not standard |
| **B: Single Repo (Recommended)** | One restic repo, unified backup strategy | 🟢 Community standard for single-user, simpler, no security benefit from tiered for single-tenant |

**Initial recommendation**: Option B (Single Repo)

**Deep web research needed**:
- Restic single vs multi-repo for personal/single-user setups (2026 best practices)
- B2 Object Lock + append-only keys configuration patterns
- Backup architecture for sovereign/local-first AI data
- Any new restic features in 2026 that change the calculus

---

## DECISION 2: G-1 Workhorse Continuity Path

**Question**: How to restore OpenCode workhorse capacity after free Gemma 4 31B 16k TPM enforcement?

**Context**: Free-tier Gemma 4 31B had 16k TPM enforced on Jul 15, 2026. It was the primary workhorse for Omega sessions. Roc Raccoon's forensic research found the death is definitive — not a config bug.

**Options**:
| Option | Description | Initial Research |
|--------|-------------|-----------------|
| **A: Antigravity OAuth (Recommended first)** | `opencode auth login` — browser login, works immediately | 🟢 5 min, no cost, no config |
| **B: AI Studio Tier 1 Billing** | $250/mo cap — but may NOT fix 16k TPM ceiling | 🟡 Community reports Tier 3 also has 16k ceiling for Gemma 4 specifically |
| **C: OpenRouter Paid** | `google/gemma-4-31b-it:free` routes through AI Studio — inherits limits | 🟡 Uncertain if paid tier differs |
| **D: OCZ+WARP** | Multi-IP rotation | 🔴 Won't fix — Google quota is per-project, not per-IP |

**Additional findings**:
- `opencode.json` "google" provider ID collision blocks startup — needs fix
- Gemma 4 thinking config bug unfixed upstream (#21746 closed)
- Pi PR #2903 has correct fix — Omega Engine already has it
- Google now requires restricted API keys (since Jun 19)

**Initial recommendation**: Option A first (Antigravity OAuth — works now, no cost)

**Deep web research needed**:
- Antigravity OAuth 2026: current status, provider support, model availability
- Google AI Studio billing tiers: does Tier 1/3 actually lift Gemma 4 TPM ceiling?
- OpenCode latest provider config patterns (2026 best practices for custom providers)
- Alternative models with comparable quality-to-cost ratio to Gemma 4 31B
- Verified working OpenCode + provider combinations as of July 2026

---

## DECISION 3: C-0.5 Session End Hook Registration

**Question**: Should the OpenCode session end hook be registered in `opencode.json`?

**Context**: Carmack completed the C-0.5 Soul Distillation Pipeline. The `distiller.py` and `session_end.py` hook exist and pass 76/76 tests. The hook is NOT yet registered in OpenCode's config — it needs explicit opt-in.

**The hook does**:
1. On session end, reads session exchanges from MemoryStore
2. Runs L1 (Narrative) → L2 (Insight) → L3 (Universal Principle) distillation
3. Atomically writes to `proposed_lessons.yaml` (blind staging, NOT directly to soul.yaml)
4. Captures `model_used` for M22 Response Provenance

**Options**:
| Option | Description |
|--------|-------------|
| **A: Register Hook (Recommended)** | Add `"hooks": {"session_end": ".opencode/hooks/session_end.py"}` to `.opencode/opencode.json` |
| **B: Keep Manual** | Keep the pipeline file but don't auto-trigger; run manually |

**Initial recommendation**: Option A (Register Hook)

**Deep web research needed**:
- OpenCode hook API documentation for 2026
- `session_end` hook behavior: when exactly does it fire? Error handling?
- Best practices for session end hooks in agent frameworks
- Any known issues with hook execution in current OpenCode version
- How other OpenCode users handle soul/lesson persistence

---

## 📋 DECISION RECORD

| ID | Decision | Status | Recommended | Research Needed |
|----|----------|--------|-------------|-----------------|
| D-C3 | Privacy Model | ⏳ PENDING | Option B (Single Repo) | Yes — restic patterns, B2, sovereignty |
| D-G1 | Workhorse Path | ⏳ PENDING | Option A (Antigravity OAuth) | Yes — tier limits, alternatives, provider config |
| D-C05 | Hook Registration | ⏳ PENDING | Option A (Register Hook) | Yes — OpenCode API, best practices, edge cases |

---

## ⏭️ AFTER RESEARCH

Once deep web research is complete for all 3 decisions:

1. Kali synthesizes findings into final recommendation
2. Architect (User) reviews and decides
3. Decision logged to PIVOT_LOG.md
4. Corresponding agents dispatched:
   - C-3 decision → Ma'at implements final privacy model config
   - G-1 decision → Carmack executes workhorse restoration
   - C-05 decision → Scribe registers hook (or proceeds manual)
5. Phase D gate re-evaluated

---

*⬡ OMEGA ⬡ KALI ⬡ DECISIONS-REQUIRED ⬡ 2026-07-23*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: DECISIONS-REQUIRED | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
