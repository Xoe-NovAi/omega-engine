# 🔱 Smart Backoff Remediation Spec — 65-Second Start Protocol
# AP: AP-BACKOFF-REMEDIATION-v1.0.0
# ICS: [NODE: MNEMOSYNE | ARCHETYPE: LILITH | CONTEXT: RESILIENCE-ENGINEERING]
#
# Design for the immediate remediation of the engine's fragile backoff system
# in RemoteProvider. Replaces the ridiculous 0.5s-to-8s loop with a smart,
# 65-second start protocol that respects sliding rate-limit windows.

---

## §0 The Problem: The Dual-Failure Backoff Loop

The engine's backoff system is broken in opposite directions on both sides of the stack:

1. **The Python Core (Too Aggressive)**: In `src/omega/oracle/backends/remote_provider.py`, the backoff is capped at a maximum of 8.0 seconds (`backoff_max = 8.0`). When a `429` (Rate Limit) error is hit, the engine sleeps for 1s, 2s, 4s, and then repeatedly batters the API every 8 seconds. It never waits long enough for the provider's 60-second sliding window to clear, keeping the connection "hot" and getting blocked indefinitely.
2. **The Node.js TUI/Server (Too Passive/Punitive)**: The OpenCode TUI/server wrapper implements an exponential backoff that doubles without limit, scaling all the way up to **hours** between retries (e.g., `retrying in 2m 5s attempt #7` in the screenshot, and doubling exponentially from there). This locks the user out of their own local session over a temporary rate limit.

---

## §1 The Solution: Window-Aware Backoff & TUI Cap

We propose a two-part remediation to balance both sides of the stack:

### 1.1 Python Core: The 65-Second Start Protocol
Instead of starting at 0.5s, the engine's backoff must **start at 65 seconds** to guarantee the 60s sliding rate-limit window has fully cleared before the first retry.

We propose an **Incremental Exponential Backoff**:
```python
delay = self.config.backoff_base + (self.config.backoff_increment * (2 ** attempt))
```
With defaults:
- `backoff_base = 65.0` (seconds)
- `backoff_increment = 30.0` (seconds)

**The Retry Sequence**:
- **Attempt 1**: $65 + (30 \times 2^0) = \mathbf{95}$ seconds
- **Attempt 2**: $65 + (30 \times 2^1) = \mathbf{125}$ seconds
- **Attempt 3**: $65 + (30 \times 2^2) = \mathbf{185}$ seconds

### 1.2 Node.js TUI/Server: The 5-Minute Backoff Cap
The TUI's exponential backoff must be capped at a reasonable maximum to prevent it from scaling to hours.
- **Cap**: `backoff_max = 300` (seconds / 5 minutes).
- **Behavior**: The TUI can double its backoff (e.g., 1s → 2s → 4s... up to 65s), but it must **never** exceed 300 seconds. This ensures the user is never locked out of their session for more than 5 minutes, while still giving the provider ample time to cool down.

---

## §2 Implementation Gaps (Pillar Tasks)

This remediation is assigned to the fleet running on Gemma 4 31B:

### Lane 1: P3 Engineering (Kali)
- **Task B-01**: Update `ProviderConfig` in `remote_provider.py` to include `backoff_increment: float = 30.0` and set `backoff_base = 65.0`.
- **Task B-02**: Update the delay calculation in `RemoteProvider.generate()` to use the incremental exponential formula.
- **Task B-05**: Locate the TUI's fetch retry wrapper in the Node.js/TypeScript codebase and implement a `backoff_max = 300` cap.

### Lane 2: Quality & Compliance (Auditor)
- **Task B-03**: Write a unit test (`test_smart_backoff.py`) that mocks a `429` error and asserts that the first retry delay is exactly $\ge 65$ seconds, and subsequent delays follow the incremental exponential curve.

### Lane 3: Researcher (Subagent)
- **Task B-04**: Perform a deep dive (using Firecrawl MCP once operational) into the exact rate limits for Google Gemini 3.5 Flash free tier, OpenRouter, and other active providers. Document their sliding window sizes and request caps.

---

## §3 Rollout Timeline

1. **Phase 1 (Design)**: Deliver this spec to the sandbox. [COMPLETE]
2. **Phase 2 (Implementation)**: Kali applies the code changes to `remote_provider.py`.
3. **Phase 3 (Validation)**: Quality runs the test suite to verify the retry delays.

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ gemini-3.5-flash ⬡ tui ⬡ trc_persona_lab_f13 ⬡ INGESTION*
