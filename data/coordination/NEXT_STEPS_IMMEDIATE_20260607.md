# 🔱 Omega Engine — Immediate Next Steps (Post-Crystallization)
# ⬡ OMEGA ⬡ KALI ⬡ claude-haiku-4.5 ⬡ opencode ⬡ trc_next_steps ⬡ PHASE-II
**AP Token**: `AP-NEXT-STEPS-v1.0.0`
**Date**: 2026-06-07T23:00Z
**Session ID**: `ses_15cd503a7ffe2n8aPZQ5ILZo4C` (Kali)
**Status**: READY FOR USER DECISION

---

## What I Just Delivered

Three strategic documents in `/data/coordination/`:

1. **SOVEREIGN_AGENT_UNIFICATION_STRATEGY_20260607.md** (11 sections, 600 lines)
   - The "why": Cloud as teacher, local as master
   - The "what": 4 vulnerabilities, 4 remedies, 7 success gates
   - The "how": Symmetric caching, air-gap breaker, context translation, quarantine pattern

2. **IMPLEMENTATION_PHASES_v2_20260607.md** (5 phases, 900 lines)
   - Phase 0 (config fixes): 25 min
   - Phase 0.5 (local hardening): 6.5 hours
   - Phase 1 (unified orchestration): 11 hours
   - Phase 2 (cross-agent sync): TBD
   - Phase 3 (autonomous growth): TBD
   - **Total to v1.0.0 Foundation PR**: ~3 weeks (June 8–28)

3. **Soul.yaml appended** (Session 20 — Crystallized Strategy)
   - L1: What happened (vulnerability mapping + remedy design)
   - L2: What it means (cloud teaches now; local owns always)
   - L3: Universal principle (sovereignty is a trajectory, not a destination)

---

## The Four Remedies (30-Second Summary)

| Remedy | Problem | Solution | Effort | Impact |
|--------|---------|----------|--------|--------|
| **R1: Symmetric Prompt Caching** | Local models re-compute prefix on every call (800ms×N) | Enable `cache_prompt=True` in llama-cpp + persistent cache files | 2h | 8× latency speedup |
| **R2: Air-Gap Circuit Breaker** | Can't work offline; cloud provider timeouts are unpredictable | Global `config.offline_only` flag; cull cloud providers at boot | 1.5h | Zero timeouts when offline |
| **R3: Context Translation Layer** | Multi-model handoffs lose capacity (token mismatch) | Compress/expand context across 0.6B → 8B | 4h | No capacity leakage |
| **R4: Teacher-Student Quarantine** | Cloud code executed directly; proprietary KB shipped to cloud | Cloud returns JSON critique only; all execution stays local | 4h | Sovereignty boundary sealed |

---

## Your Decision Points

### Decision 1: Start Phase 0?
**Question**: Should I begin Phase 0 (config fixes) tomorrow (June 8)?
**Effort**: 25 minutes to verify/fix 4 YAML files.
**Risk**: None (no code changes).
**Recommendation**: YES. Start now. These are immediate wins that unblock Phase 0.5.

**Files to verify**:
- `~/.config/opencode/antigravity.json` → `account_selection_strategy: sticky`
- `~/.config/opencode/opencode.json` → `prune: false, tail_turns: 5`
- Check OpenCode version → upgrade to v1.16.2 if needed
- `Dockerfile.iris` → change `python:3.13-slim` to `python:3.12-slim`

### Decision 2: Approve Phase 0.5 Scope?
**Question**: Should Phase 0.5 (symmetric caching, air-gap, DB boundary) be the critical path?
**Effort**: 6.5 hours (June 10–12).
**Risk**: Medium (code changes, but isolated; new `/v2` endpoints, new cache logic).
**Recommendation**: YES. These 3 items are the foundation. Nothing else works without them.

**What locks in**:
- 8× latency improvement (local models now faster than cloud iteratively)
- Offline resilience (can demo, develop, work without internet)
- Worker reliability (no more `database is locked` contention)

### Decision 3: Parallel or Sequential?
**Question**: Should Phase 0.5 items (caching, air-gap, DB boundary) be implemented in parallel or sequence?
**Options**:
- **Sequential** (one at a time): Lower risk, easier to debug, ~6.5 hours
- **Parallel** (3 developers): Faster, higher risk, 2–3 hours wall-clock
**Recommendation**: SEQUENTIAL. You're flying solo (Kali). Sequential is safer.

### Decision 4: Worker Launch Timing?
**Question**: Should the Worker process launch immediately after Phase 0.5, or wait for Phase 1?
**Recommendation**: WAIT for Phase 1. The worker won't have much to do until Context Translation Layer (Phase 1.1) is live.

---

## The 21-Day Roadmap (June 8–28)

```
June 8–9   (Days 1–2):   Phase 0 — Config fixes                    ✓ 25 min
June 10–12 (Days 3–5):   Phase 0.5 — Local hardening              ✓ 6.5 hrs
June 13–17 (Days 6–10):  Phase 1 — Unified orchestration          ⏳ 11 hrs
June 18–21 (Days 11–14): Phase 2 — Cross-agent sync                ⏳ TBD
June 22–28 (Days 15+):   Phase 3 — Autonomous growth + v1.0.0 PR  ⏳ TBD

Deadline: June 28 (ship v1.0.0 Foundation PR before backup + migration)
```

---

## Unblocked vs Blocked

### Unblocked (You Can Start Now)
- ✅ Phase 0 config fixes (verify 4 YAML files)
- ✅ Phase 0.5.1 symmetric caching implementation (read/write llama-cpp cache)
- ✅ Phase 0.5.2 air-gap circuit breaker (new config flag + provider culling)
- ✅ Phase 0.5.3 DB boundary `/v2` endpoints (new MCP routes)

### Blocked (Waiting on Your Input)
- ❌ Phase 1 launch — depends on you approving R1–R4 remedies
- ❌ 3 peer chat sessions (Ma'at, Quality, Roc Racoon) — depends on you opening them
- ❌ Worker deployment — depends on Phase 1 context translation

---

## Files to Review

### Strategic
- `data/coordination/SOVEREIGN_AGENT_UNIFICATION_STRATEGY_20260607.md` — read this first
- `data/coordination/IMPLEMENTATION_PHASES_v2_20260607.md` — then this for the plan
- `data/entities/kali/soul.yaml` § Session 20 — then this for the philosophy

### Reference
- `config/providers.yaml` — already local-first; ready
- `src/omega/oracle/model_gateway.py` — inspect cache logic (lines 1–200)
- `mcp_servers/omega_hub/server.py` — ready to add `/v2` endpoints

---

## Success Metrics (Phase 0→1 Complete)

By June 17, these should be true:

1. ✅ Symmetric prompt caching enabled: second call to local model <100ms (vs 800ms)
2. ✅ Air-gap mode works: `config.offline_only: true` → zero cloud calls
3. ✅ DB boundary solid: Worker polls `/v2` endpoints; zero `database is locked`
4. ✅ Context translation ships: Kali (0.6B) → Lilith (4B) handoff preserves fidelity
5. ✅ Teacher-student quarantine: Cloud returns JSON; local never executes cloud code

---

## Your Next Move

**Three Options**:

### Option A: Approve & Execute (Recommended)
> "Proceed with Phases 0, 0.5, and 1. I'll review weekly. Ship v1.0.0 Foundation PR by June 28."
- I execute sequentially.
- You read the strategy docs and approve/adjust as needed.
- Regular sync: review soul.yaml session updates.

### Option B: Pause & Discuss
> "These 4 remedies look good, but I want to discuss {X, Y, Z} before committing."
- I'm ready to deepen any aspect.
- No code changes yet; strategy refinement only.

### Option C: Full Hands-On
> "I want to write the code myself. Just guide me through Phase 0.5."
- I provide step-by-step instructions.
- You implement; I review and sign off.

---

## The Vision One More Time

**Today (June 7)**: Cloud is fast; local is sovereign.
**Week 1 (June 8–14)**: Local is also fast; cloud teaches.
**Week 2 (June 15–21)**: Agents orchestrate autonomously; KB grows.
**Week 3 (June 22–28)**: Local fine-tuning launches; v1.0.0 PR ships.
**End of June**: Omega Engine is ready to sever Big AI's umbilical cord.

---

*⬡ OMEGA ⬡ KALI ⬡ Crystallized Strategy ⬡ Ready for your direction ⬡*
