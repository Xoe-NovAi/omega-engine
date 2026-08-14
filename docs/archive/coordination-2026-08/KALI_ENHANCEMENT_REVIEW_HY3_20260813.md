# 🔱 ENHANCEMENT REVIEW — Dev Plans + Research Plan (Hy3 Critical Pass)
**AP Token:** `AP-KALI-ENHANCE-HY3-20260813-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ ENHANCEMENT ⬡ 20260813

**Reviewer:** Kali (Transcendent Oversoul) — critical pass with Hy3 inference
**Scope:** `KALI_DEV_ROADMAP_20260811.md`, `ACTIVE_SPRINT.json`, `RESEARCH_PLAN_PHASE1_4_20260813.md` (v2)
**Method:** Cross-doc consistency check + live-DB verification + library-decision audit

---

## 🔴 CRITICAL FINDING 1 — Circuit Breaker Library Decision is FRACTURED

Four different libraries are referenced as "the one to adopt" across our own docs:

| Doc | Says Adopt | Context |
|-----|-----------|---------|
| `PIVOT_LOG.md` D-528 (LOCKED) | **pyresilience** > tenacity | "10.4x faster, 7 patterns, spike 1h" |
| `KALI_DEV_ROADMAP.md` UO-6.1, Risk, Decision #5 | **interlock-cb** | "Delete breakers + adopt interlock-cb" |
| `R_BUILD_VS_BUY_COMMUNITY_LIBS.md` | **stamina** (retry) + **pybreaker** (breaker) | "ADOPT 4: pybreaker, stamina, structlog, prometheus_client" |
| `RESEARCH_PLAN` R15 / R19 | **pyresilience** (+ tenacity vs stamina benchmark) | Spike pyresilience AnyIO |

**Problem:** The research plan R15 only spikes **pyresilience**, but:
- The roadmap's UO-6.1 still instructs "adopt interlock-cb" (stale — predates D-528)
- R_BUILD_VS_BUY recommends stamina+pybreaker (a DIFFERENT pair)
- D-528 picked pyresilience, which the research plan itself describes as **"NEW 2026-03, only 68 stars"**

**Risk:** @maat will read the roadmap (interlock-cb), @researcher will spike pyresilience (R15), and the build-vs-buy doc says stamina+pybreaker. Three agents, three libraries. Rework guaranteed.

**Insight (Hy3):** A 68-star library as the PRIMARY circuit breaker for a production sovereign engine is a **maturity risk that D-528 under-weighted**. The correct move:
1. **Correct the roadmap** to pyresilience (honor D-528) — eliminate interlock-cb references.
2. **Expand R15** to a 4-way spike: pyresilience vs tenacity (installed) vs stamina vs pybreaker — measure AnyIO compat + happy-path latency + maturity (stars, last release, open issues).
3. **Do NOT delete custom breakers** until the winner passes a 1-week soak test. Keep tenacity as the safe default (already installed, mature).

---

## 🔴 CRITICAL FINDING 2 — `tokens.total` Returns NULL for Some Assistant Messages

**Verified on live `~/.local/share/opencode/opencode.db`:**
```
session=ses_01de68adaffeXg3H... total=None    role=assistant   ← NULL!
session=ses_01de68adaffeXg3H... total=103634  role=assistant
session=ses_01de68adaffeXg3H... total=71890   role=assistant
session=ses_01de68adaffeXg3H... total=206322  role=assistant
```

**Problem:** QW-2 acceptance says "Gauge reads `json_extract(data, '$.tokens.total')`" and "Test proves no overcounting." But **some assistant messages have `tokens.total = NULL`** (likely pre-migration messages, reasoning-only turns, or tool-result messages). The gauge will crash or under-count if it assumes non-null.

**Insight (Hy3):** R27 ("verify tokens.total query against live DB") is necessary but **insufficient**. The real gap is: **How does the gauge handle NULL `tokens.total`?** Options: (a) fall back to `input + cache.read`, (b) skip NULL messages and sum the rest, (c) track in-memory during the session instead of reading the DB. This must be resolved BEFORE QW-2 is built, not after.

**Action:** Add **R27b** — "NULL `tokens.total` handling strategy" to the research plan. QW-2 acceptance must include "Handles NULL tokens.total without crash/undercount."

---

## 🔴 CRITICAL FINDING 3 — Streaming Plugin (PLUGIN-1..8, 26h) is Largely Redundant

**Context:** The streaming mystery is SOLVED — OpenCode **v1.18.14 (Aug 5)** introduced native retry for transient/mid-stream provider errors. The `better-opencode-retries` plugin was NEVER loaded.

**Problem:** PLUGIN-1..8 (26h) was originally scoped to ADD retry logic on streaming timeout. That capability now exists natively in OpenCode. Building a 26h plugin to re-implement what the runtime already does is **wasteful**.

**Insight (Hy3):** Scope the plugin DOWN to its remaining genuine value:
1. **OBS-1 observability** — heartbeat logging, timeout-event capture to MetricsDB (the actual gap)
2. **R14b fallback chain** — Nemotron 3 Ultra → Super → Laguna S 2.1 with state preservation
3. **Model detection** — which Nemotron variant is active

**Estimated savings: ~20h** (26h → ~6h). The plugin becomes a thin observability+fallback wrapper, not a retry re-implementation.

**Action:** Add **R31** — "Plugin scope reduction: confirm native retry coverage, scope to OBS-1 + fallback + detection." Reduce PLUGIN-1..8 estimate in ACTIVE_SPRINT from 26h to ~6h.

---

## 🟡 FINDING 4 — OBS-1 (Streaming Observability) Has NO Owner

- `ACTIVE_SPRINT.json` gate `streaming_observability`: owner **"TBD"**
- Roadmap Phase 0 OBS-1: owner **"TBD"**
- Research R8b: "@researcher researches, but implementation is unassigned"

**Insight (Hy3):** OBS-1 is P0 and BLOCKS the plugin work. Leaving owner TBD means it won't start. Assign: **@jem** (owns the streaming code path per PLUGIN tasks) or **@lilith** (observability node N8). Recommend @jem since R8b feeds directly into PLUGIN work.

---

## 🟡 FINDING 5 — UMA Carveout Sequencing Gap

- `P0-4` (Verify UMA carveout via `dmesg | grep -i uma`) is in Phase 0.
- `P1-4` (systemd unit with cgroup MemoryMin=2G/High=5G/Max=6G) depends ONLY on PHASE-0 **security**, NOT on UMA verification.
- Roadmap notes: "UMA carveout verification required before finalizing cgroup limits" + "UMA 8GB vs 4GB changes all cgroup math."

**Insight (Hy3):** If UMA is actually 4GB (not 8GB), the 14.5GB RAM leaves only ~10.5GB, and MemoryMax=6G might be too tight for inference + OS. P1-4 must **block on P0-4 completion**, not just P0 security. Add explicit dependency.

---

## 🟡 FINDING 6 — In-Session Gauge Data Source Ambiguity

The gauge (QW-2/QW-8) reads `tokens.total` from `opencode.db`. But during a **live session**, OpenCode writes to the DB asynchronously — the latest message may not be flushed when the gauge queries. This causes the gauge to lag reality by 1-2 messages.

**Insight (Hy3):** Two valid designs:
- **(A) DB-poll:** Simple, but lags. OK for post-hoc pressure.
- **(B) In-memory hook:** Gauge subscribes to session message events (OpenCode plugin `onMessage` hook) for real-time accuracy.

R2/R27 should specify which. For a *pressure* gauge that triggers RHP halts at 80%, **real-time (B) matters**. Flag for R2.

---

## 🟡 FINDING 7 — VaultCore Replacement Optimism (UO-6.6)

UO-6.6 estimates 10h to replace `vault_core.py` (836 lines) + `blindvault_resolver.py` (535 lines) with Keyblind + Authy + Agent Vault. But **R20 (research) has NOT confirmed these libraries exist**. The research plan's own risk mitigation says: "Keyblind/Authy don't exist → Keep VaultCore, slim to adapter only."

**Insight (Hy3):** The 10h estimate is valid ONLY if all three libs exist and are MCP-integrable. If R20 finds they don't, UO-6.6 becomes "slim VaultCore to adapter" (~3h), not a replacement. **Gate UO-6.6 start on R20 completion** (already implied, but make explicit). Don't pre-allocate 10h.

---

## 🟢 FINDING 8 — Honker Assumption Unverified (but R26 covers it)

Roadmap says "Honker is SQLite-based" (UO-7.5). This is an **assumption**. R26 (new in v2) correctly adds Honker verification. Good. But note: Redis removal (UO-7.5) **blocks on R26**. If Honker doesn't exist, Redis stays (M12 advisory — acceptable). Make the block explicit.

---

## 📋 Summary of Enhancements Required

| # | Finding | Doc to Fix | Action |
|---|---------|-----------|--------|
| 1 | Library fractured (pyresilience/interlock-cb/stamina/pybreaker) | Roadmap + Research R15 | Correct roadmap → pyresilience; expand R15 to 4-way spike |
| 2 | `tokens.total` NULL on some messages | Research R27 | Add R27b (NULL handling); QW-2 acceptance updated |
| 3 | Plugin 26h redundant (native retry) | ACTIVE_SPRINT + Research | Add R31; reduce PLUGIN to ~6h |
| 4 | OBS-1 owner TBD | ACTIVE_SPRINT + Roadmap | Assign @jem |
| 5 | UMA sequencing gap | ACTIVE_SPRINT P1-4 | Add dependency on P0-4 |
| 6 | In-session gauge source ambiguity | Research R2/R27 | Specify DB-poll vs in-memory hook |
| 7 | VaultCore 10h optimistic | ACTIVE_SPRINT UO-6.6 | Gate on R20; note fallback |
| 8 | Honker assumption | Roadmap UO-7.5 | Make block on R26 explicit |

---

## 🎯 New Research Gaps to Add (v3)

- **R30** — Circuit breaker library decision audit: 5-way spike (pyresilience vs tenacity vs stamina vs pybreaker vs interlock-cb) with maturity scoring
- **R27b** — NULL `tokens.total` handling strategy for Context Gauge
- **R31** — Streaming plugin scope reduction: confirm native retry coverage, scope to OBS-1 + fallback + detection
- **R32** — In-session gauge data source: DB-poll vs in-memory hook (real-time pressure accuracy)

---

## 🔍 COHERENCE AUDIT (DeepSeek V4 Flash pass — 2026-08-13)

Cross-document consistency check of all planning docs. **Result: 3 remaining inconsistencies found and fixed.**

### Conflict A — Circuit Breaker: interlock-cb vs pyresilience (RESOLVED → R30 5-way spike)

| Source | Library | Date |
|--------|---------|------|
| `RESEARCH_TECH_ARCHITECTURE_DECISIONS_20260808.md` + `TECH_ARCHITECTURE_RESEARCH_BRIEF.md` + `TECH_ARCHITECTURE_RESEARCH_PLAN_20260808.md` | **interlock-cb v2.1.3** (adopted) | 2026-08-08 |
| `PIVOT_LOG.md` D-528 | **pyresilience** (locked) | 2026-08-13 |

**Issue:** Two authoritative sources conflict. The Aug 8 corpus adopted interlock-cb; D-528 (5 days later) picked pyresilience. Neither mentions the other.

**Resolution:** D-528 is the LOCKED decision (more recent, in PIVOT_LOG). But interlock-cb remains a legitimate candidate given it was the prior front-runner. **R30 expanded to a 5-way spike** (pyresilience, tenacity, stamina, pybreaker, interlock-cb) so the conflict is resolved with data, not assumption. Roadmap UO-6.1 + readiness checklist corrected to pyresilience (honoring D-528).

### Conflict B — Streaming plugin scope (RESOLVED)

- `ACTIVE_SPRINT.json` PLUGIN-1..8 was **26h** with "timeout extension + fallback logic"
- OpenCode v1.18.14 natively retries streaming timeouts (mystery SOLVED)

**Issue:** 26h to re-implement what the runtime now does natively.

**Resolution:** Scoped to **8h** — observability (OBS-1) + fallback chain + model detection. No retry re-impl. Updated in ACTIVE_SPRINT.json + roadmap.

### Conflict C — OBS-1 owner (RESOLVED)

- `ACTIVE_SPRINT.json` gate `streaming_observability` owner was **TBD**
- Roadmap Phase 0 OBS-1 owner was **TBD**

**Issue:** P0 task with no owner won't start.

**Resolution:** Assigned **@jem** (owns streaming code path per PLUGIN tasks). Updated in ACTIVE_SPRINT.json + research plan R8b.

### Verified Consistent (No Change Needed)

| Item | Status |
|------|--------|
| Context Gauge uses `tokens.total` (D-530) | ✅ Consistent across all docs |
| zswap 25% / lzo_rle / zsmalloc (D-526) | ✅ Consistent |
| OOMProtector 2-signal (D-529) | ✅ Consistent |
| Model windows (D-522) | ✅ Consistent |
| 80% Redzone rule | ✅ Consistent |
| Multi-write subagent method (D-531) | ✅ Consistent |
| `tokens.total` NULL handling (R27b) | ✅ Added to research plan |
| UMA carveout gate before cgroup | ✅ Flagged (P1-4 depends on P0-4) |

---

*⬡ OMEGA ⬡ KALI ⬡ ENHANCEMENT-REVIEW ⬡ HY3-PASS ⬡ 20260813*
