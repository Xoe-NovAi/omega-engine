# 🔱 Antigravity 8-Key Rotation Strategy — Two-Pool Architecture
# ⬡ OMEGA ⬡ KALI ⬡ trc_rotation ⬡ ROTATION-STRATEGY
**AP Token**: `AP-ANTIGRAVITY-ROTATION-v1.0.0`
**Date**: 2026-06-05T06:00Z
**Status**: 🟢 **DRAFT — Ready for Antigravity review**
**Context**: First cross-platform Hivemind test with Antigravity IDE

---

## §0 The Quota Reality

Antigravity has **two independent weekly usage pools**:

| Pool | Models | Reset | Capacity per key per week |
|------|--------|-------|---------------------------|
| **Pool G (Gemini)** | Gemini 3.5 Flash, Gemini 3.1 Pro, all Gemini models | Weekly | Limited (free tier, varies by model) |
| **Pool C (Claude + gpt-oss)** | Claude Sonnet 4.6 Adaptive Thinking, Opus 4.6 Adaptive Thinking, gpt-oss-120b | Weekly | Limited (free tier) |

**Critical insight**: Within a single key, switching from Gemini 3.5 Flash to Gemini 3.1 Pro does NOT give more capacity — it's the same pool. You consume from the same bucket.

**Cross-pool**: Switching from Gemini 3.1 Pro to Claude Sonnet 4.6 (or Opus 4.6) DOES give more capacity — different pool.

The user has **8 Google API keys**. Each key has its own Pool G and Pool C. So:

```
Total weekly capacity: 8 × (Pool G + Pool C) per pool category
```

This is a **strategic asset**, not a casual one. Misuse = weeks of downtime.

---

## §1 The 8-Key Rotation Policy

### 1.1 State Machine per Key

```
        ┌──────────────────────────────────────────────┐
        │                                              │
        │  ┌────────┐  quota_hit   ┌──────────┐         │
        │  │ ACTIVE │ ──────────→ │  COOLING │         │
        │  └────────┘              └─────┬────┘         │
        │      ▲                        │              │
        │      │  cool_period_elapsed   │              │
        │      │  (default: 1 hour)     │              │
        │      └────────────────────────┘              │
        │                                              │
        │  ┌────────┐  weekly_reset   ┌──────────┐     │
        │  │EXPIRED │ ←───────────── │  DRAINED │     │
        │  └────────┘                 └─────┬────┘     │
        │      ▲                            │          │
        │      │  reset_complete            │          │
        │      └────────────────────────────┘          │
        │                                              │
        └──────────────────────────────────────────────┘
```

**States**:
- **ACTIVE**: Currently usable. Can be selected for the next interaction.
- **COOLING**: Recently quota-hit. Wait `cool_period_seconds` (default 3600s = 1h) before retry.
- **DRAINED**: Pool G or Pool C quota hit for the week. Wait for `weekly_reset`.
- **EXPIRED**: All pools drained AND the week has reset. Ready to be re-ACTIVE.

### 1.2 Selection Algorithm (Round-Robin with Anti-Thrashing)

```python
def select_next_key() -> KeyState:
    """Pick the next key to use. Round-robin with anti-thrashing."""
    for key in keys_in_round_robin_order:
        if key.status == "active":
            return key
        elif key.status == "cooling":
            if time.time() >= key.cool_until:
                key.status = "active"
                return key
        elif key.status == "drained":
            # Skip — wait for weekly reset
            continue
        elif key.status == "expired":
            # Weekly reset happened — try this key
            key.pool_g.tokens_this_week = 0
            key.pool_c.tokens_this_week = 0
            key.status = "active"
            return key
    raise NoActiveKeys("All keys exhausted. Wait for weekly reset or use a different platform.")
```

### 1.3 Anti-Thrashing Rules

- **3 failures in 5 minutes** → mark key as COOLING for 1 hour.
- **5 quota hits in a single day** → mark key as DRAINED for 24 hours (faster than weekly).
- **All 8 keys COOLING** → wait for the first to thaw, or fall back to a different platform.

### 1.4 Pool Selection Within a Key

When a key is ACTIVE, the pool/model is selected based on the task:

| Task Type | Pool | Model | Thinking |
|-----------|------|-------|----------|
| Quick sanity check | G | Gemini 3.5 Flash | low |
| Standard review | G | Gemini 3.5 Flash | medium |
| Deep architecture review | G | Gemini 3.5 Flash | high |
| High-stakes M14 heritage vet | G | Gemini 3.1 Pro | high |
| Roadmap / threat model | G | Gemini 3.1 Pro | high |
| Cross-pool sanity check | C | Claude Sonnet 4.6 Adaptive Thinking | (default) |
| High-stakes tie-breaker | C | Opus 4.6 Adaptive Thinking | (escalation) |
| Open-weight privacy | C | gpt-oss-120b | (default) |

**Default**: Gemini 3.5 Flash — medium. This is the workhorse. Cheap, fast, deep enough.

---

## §2 Per-Phase Budget (Token Allocation)

Each of the 7 review phases has a **token budget**. If Antigravity exceeds the budget, the user gets a warning.

| Phase | Default Budget | Override |
|-------|----------------|----------|
| Phase 1: Architecture & Mandates | 50,000 tokens (Gemini 3.5 Flash — medium) | 100,000 if escalates to high |
| Phase 2: Hivemind & Coordination | 50,000 tokens | 100,000 if escalates |
| Phase 3: Sovereign Model Orchestration | 75,000 tokens | 150,000 if reviews cross-system |
| Phase 4: Heritage & id Software | 100,000 tokens (M14 needs depth) | 200,000 if full CREDITS audit |
| Phase 5: Soul & Continuity | 50,000 tokens | 100,000 if soul.yaml overhaul |
| Phase 6: Sovereignty & Big AI Severance | 75,000 tokens | 150,000 if 8-key strategy overhaul |
| Phase 7: Roadmap & Future-Proofing | 100,000 tokens (Gemini 3.1 Pro — high) | 200,000 if strategic overlay needed |

**Default total for 7 phases**: 500,000 tokens (well within 1 week's free-tier capacity across 8 keys).

**If we need to escalate to Gemini 3.1 Pro — high for 3+ phases**: 1,200,000 tokens total. Still feasible.

---

## §3 Usage Tracking

### 3.1 Schema: `data/entities/antigravity/knowledge/USAGE_POOL_LOG.json`

```json
{
  "schema_version": "1.0",
  "last_updated": "2026-06-05T06:00:00Z",
  "weekly_reset_date": "2026-06-08T00:00:00Z",  // Next Monday
  "keys": [
    {
      "key_id": "agy_key_01",
      "last_used_at": null,
      "last_model_used": null,
      "status": "active",
      "cool_until": null,
      "pool_g": {
        "quota_hit_at": null,
        "calls_this_week": 0,
        "tokens_this_week": 0,
        "thinking_levels_used": {
          "low": 0,
          "medium": 0,
          "high": 0
        }
      },
      "pool_c": {
        "quota_hit_at": null,
        "calls_this_week": 0,
        "tokens_this_week": 0,
        "thinking_levels_used": {
          "low": 0,
          "medium": 0,
          "high": 0
        }
      }
    }
  ],
  "current_key_index": 0,
  "decisions_log": []
}
```

### 3.2 Who Writes to This File

- **Antigravity**: Writes before and after each interaction (model selection + actual token usage).
- **OpenCode Pillar 7 (Context)**: Can READ for telemetry. NEVER writes.
- **OpenCode Pillar 5 (Sentinel)**: Can validate the schema, alert on anomalies.

### 3.3 Why Not Centralize in PostgreSQL?

Because **Antigravity cannot reach the local database**. The file must be in the same git repo that both platforms can see.

---

## §4 Failure Scenarios

### 4.1 All 8 Keys Drained

**Symptom**: `agy --print` returns 429 / `RESOURCE_EXHAUSTED` on all keys.

**Recovery**:
1. Stop Antigravity sessions immediately.
2. Check `weekly_reset_date` — how long until reset?
3. If >3 days away, switch to **OpenCode-only mode**. Skip Phases with P0/Strategic priority.
4. If <3 days away, do high-value Phases only (1, 4, 7).
5. Document the drain in PIVOT_LOG.

### 4.2 Antigravity Sandbox Cannot Find Files

**Symptom**: "File not found" when reading `SOVEREIGN_MANDATES.md` etc.

**Recovery**:
1. Check the git remote is in sync with the local repo.
2. If using a subdirectory mount, expand to the full repo.
3. If still failing, write the missing content to `data/coordination/EMERGENCY_REFERENCE_BUNDLE.md` (a single file with all critical content) and mount that.

### 4.3 2-Model Disagreement

**Symptom**: Gemini 3.5 Flash says YES, Claude Sonnet 4.6 says NO on the same Phase review.

**Recovery**:
1. Escalate to **Gemini 3.1 Pro — high** for tie-breaking.
2. If still 2-way disagreement, use `agy_key_08` with **Opus 4.6 Adaptive Thinking** (Pool C) for the final call.
3. Document the disagreement in PIVOT_LOG with both verdicts.

---

## §5 The Weekly Reset Calendar

Google's weekly reset is on **Mondays at 00:00 UTC** (assumed; verify with first observation).

```
2026-06-08 (Mon): Reset 1
2026-06-15 (Mon): Reset 2
2026-06-22 (Mon): Reset 3
...
```

**Planning tip**: If the cross-platform test starts mid-week, budget the remaining days carefully. If it starts on Monday, you have the full week.

---

## §6 Open Questions for Antigravity

1. **What is the actual quota per key per week?** (Free tier varies; we need to measure.)
2. **Does Pool G and Pool C reset on the same Monday, or different days?** (Verify with first observation.)
3. **Is the `--print` mode more or less efficient than interactive mode?** (Test and measure.)
4. **Can Antigravity write to a file mount in real time, or only at the end of a session?** (Critical for handoff files.)

---

## §7 Heritage

- **WAD System (id Software 1993)**: Each API key is a "WAD" that can override engine defaults. The engine (Antigravity) doesn't know which key is which. The key just provides strategy.
- **Cvar System (Quake 1996)**: The keys are cvars — registered at engine start, looked up at runtime. Same key index, different values.
- **Right Approximation (FISR 1999)**: Don't burn the most expensive model on a problem the cheapest model can solve. The right approximation is better than the exact solution you can't afford.

---

## §8 Soul Write-Back (Mandate 11)

**L1**: We designed an 8-key rotation strategy for Antigravity with two independent weekly usage pools. Each phase has a token budget, a default model, and an escalation path.

**L2**: The bottleneck is not compute — it's quota. The right answer is to rotate keys, not to escalate models. Escalation should be reserved for high-stakes tasks (M14 vet, threat modeling, roadmap).

**L3**: **Scarcity breeds wisdom.** When a resource is constrained (8 weekly quotas per pool), the right design is to map it to a 7-phase plan with escalation reserved for the most important decisions. Abundance breeds waste; scarcity breeds discipline.

---

*🔱 OMEGA ⬡ KALI ⬡ trc_rotation ⬡ ROTATION-STRATEGY — 2026-06-05T06:00Z*
