# 🔱 Sovereign Handoff: Jem Phase 2 Implementation
**From**: OpenCode Builder (DeepSeek V4 Flash)
**To**: Antigravity Gemini 3.1 Pro
**Date**: 2026-05-19
**Trace**: trc_jem_ph2_handoff
**Status**: ⚠️ **Implementation 90% Complete — Testing Blocker**

---

## 🎯 Objective
Complete the implementation of **Jem Phase 2: Scheduling & Rotation** for the background researcher.

## ✅ What Has Been Achieved
The following components have been implemented and integrated into `src/omega/workers/background_researcher/`:

1. **`EnhancedPriorityQueue` (`models.py`)**:
   - Implements a two-tier queue (High/Normal).
   - Designed for **Weighted Fair Scheduling (2:1 ratio)** to prevent starvation of normal tasks while prioritizing user-requested/high-priority research.

2. **`TopicScheduler` (`scheduler.py`)**:
   - Implements round-robin rotation of scheduled topics from `config/research_topics.yaml`.
   - Handles **Aging** (priority decay per cycle) and **Deepening** (priority boost for iterative research).
   - Feeds the `EnhancedPriorityQueue` without replacing it.

3. **`ReviewQueue` (`review_queue.py`)**:
   - A 3-tier filesystem-based queue (`data/research/review_queue/{high,normal,low}`).
   - Implements **TTL-based sweeping** (7d/5d/2d) and a **hard cap of 100 items**.
   - Uses atomic `mkdir` locks for crash-safe processing.

4. **`ResearchMetrics` (`metrics.py`)**:
   - Logs per-cycle performance data to `data/research/metrics/cycle_metrics.jsonl`.
   - Tracks T1/T2/T3 latency, success rates, and circuit breaker transitions.

5. **`loop.py` Integration**:
   - Rewritten to use the new `TopicScheduler`, `ReviewQueue`, and `ResearchMetrics`.
   - Added a **crash-safe cycle lock** at `/tmp/omega/research.lock`.
   - Implemented **Discovery-First Local Scan**: Performs a local `glob+grep` for topic patterns before initiating cloud-based research.

6. **Test Suite (`tests/test_background_researcher.py`)**:
   - Comprehensive tests for queue fairness, scheduler rotation, review queue locking, and metrics logging.

---

## 🛑 The Blocker: Weighted Fair Scheduling
The only remaining item is a failure in `tests/test_background_researcher.py::test_enhanced_priority_queue_weighted_fair`.

**The Symptom**:
- Expected sequence for 5 High and 5 Normal tasks (2:1 ratio): `H, H, N, H, H, N, H, H, N, N, N`
- Actual sequence produced: `H, H, N, H, H, H, ...`
- The test fails at `results[5]`, where it expects "normal" but receives "high".

**The Root Cause**:
The `dequeue` logic in `models.py` is failing to correctly reset the `_current_weight_count` or switch the `_current_queue` state after the first "normal" task is served. It appears to be "forgetting" the weight limit for the high queue or skipping the switch back to normal.

**Current State of `dequeue`**:
I have attempted several iterations (including a `while True` loop and `if/elif` structures), but the state transition at the boundary of the weight limit is still slightly off.

---

## 🛠️ Recommended Next Steps for Gemini 3.1 Pro
1. **Fix `EnhancedPriorityQueue.dequeue()`**:
   - Review the state transitions of `_current_queue` and `_current_weight_count`.
   - Ensure that after `normal_weight` is reached, the state resets to `high` and `count=0`.
   - Ensure that after `high_weight` is reached, the state resets to `normal` and `count=0`.
   - Verify that the "fallback" logic (when one queue is empty) does not corrupt the weight counters for the other queue.

2. **Verify with Tests**:
   - Run `pytest tests/test_background_researcher.py::test_enhanced_priority_queue_weighted_fair`.
   - Once green, run the full suite: `pytest tests/test_background_researcher.py`.

3. **Final Integration Check**:
   - Run a manual cycle of the background researcher loop to ensure `TopicScheduler` and `ReviewQueue` are behaving as expected in a live environment.

## 📂 Relevant Files
- `src/omega/workers/background_researcher/models.py` (The Blocker)
- `src/omega/workers/background_researcher/scheduler.py`
- `src/omega/workers/background_researcher/review_queue.py`
- `src/omega/workers/background_researcher/loop.py`
- `tests/test_background_researcher.py`
- `docs/research/R_PHASE2_SCHEDULING_RESEARCH.md` (The Spec)

---
**Handoff Complete. The fire is yours.**
