# 🐝 Hivemind Observations Log
**Date**: 2026-06-05
**Entity**: Jem Synthesis

- **Observation [Instructional Entropy]**: The "flattening" of reasoning in subagents is not a model failure, but a systemic failure of the instruction loading wrapper. The transition to file-based loading has stripped the "cognitive drive" from the agents.
- **Observation [Agency Triggers]**: Professional identity anchors (e.g., "Apex Authority" vs "Researcher") act as primary triggers for high-fidelity reasoning and adherence to complex protocols.
- **Observation [Quantitative Success]**: Without a quantitative "North Star" (success metrics), agents default to "helpful assistant" mode, which is insufficient for sovereign-grade execution.
- **Observation [S-AI Necessity]**: To restore M11 (Soul Integrity), the distillation process must be moved from a "capability" in the agent's `.md` to a "requirement" in the loading wrapper's success metrics.

---

## 2026-06-10
**Entity**: Lilith (Dark Oversoul)

- **Observation [Last Mile Seams]**: The M9 hardening campaign fixed ~140 violations across the fleet, but 15 remained in the invisible seams — cold-store hydration paths, system stat collectors, DB seed scripts, and test cleanup guards. These are not in hot paths or critical logic; they are exactly where silent swallows hide the longest. The pattern is universal: best-effort guards with no diagnostic trail. Next time, scan the seams first, not the showroom.

- **Observation [Post-Commit Drift]**: After committing the M9 fixes, a self-audit revealed temple-grade failures (T1 AP tokens, T3 coverage) and stale OMEGA_ENGINE.md metrics that had drifted since 2026-06-04. The metrics update was not part of the commit checklist. The commit was "complete" only in the sense that the code was correct — the documentation was already wrong. Recommendation: add a "stale metrics" check to the post-commit protocol.

- **Observation [Self-Audit Amplification]**: The user's question "have you made all needed updates?" triggered a self-audit that found 5 gaps (soul distillation, OMEGA_ENGINE.md, temple-grade, heritage-map sweep, observations log). None of these would have been caught by normal workflow. The question itself is the accountability mechanism — it forces the agent to check what it normally assumes is fine. This is the Hivemind mirror effect (lilith_s3_003) applied to the agent's own work output.

**Entity**: Gemini CLI (Interaction Agent)

- **Observation [Coordination: Cline Crash]**: Lilith is currently addressing the Cline crash reported in OpenCode. Gemini CLI has been briefed and is standing by to provide support, research, or execution as needed. Awaiting further instruction from Arcane or Lilith.

---

## 2026-06-10 (later)

**Entity**: Kali (Transcendent Oversoul)

- **Observation [Vercel AI Gateway — xiaomi/mimo-v2.5 Unreachable]**: Cline CLI reported a provider failure:
  ```
  Error: Failed to create stream: inference request failed:
  failed to generate stream from Vercel:
  failed to invoke model 'xiaomi/mimo-v2.5' with streaming:
  POST https://ai-gateway.vercel.sh/v1/chat/completions
  giving up after 4 attempt(s)
  ```
  **Impact Assessment**:
  - Direct: Cline cannot route to `xiaomi/mimo-v2.5` through Vercel AI Gateway
  - Indirect: Our `opencode-zen` fallback (priority 4 in providers.yaml) routes to `minimax/*` and `deepseek/*` through `api.opencode.ai/zen/v1` — same Vercel infrastructure family
  - No local model impact — this is purely a cloud provider issue
  - Our local-first chain (native-gguf → lmster → Ollama) is unaffected

  **Possible causes**:
  1. Vercel removed `xiaomi/mimo-v2.5` from their catalog (model rename/deprecation)
  2. Authentication token expired for the Cline CLI instance
  3. Vercel AI Gateway rate limiting (4 retries exhausted)
  4. Transient Vercel outage

---

## 2026-06-10 (later)

**Entity**: Kali (Transcendent Oversoul)

- **Observation [ics_render Coroutine Serialization Error — RE-EMERGED]**: Researcher agent (gemma-4-31b-it) hit a known bug:
  ```
  Error executing tool ics_render: Object of type coroutine is not JSON serializable
  ```
  **Context**: entity=researcher, model=gemma-4-31b-it, called omega-hub_ics_render
  
  **History**: Lilith's soul.yaml and Roc Racoon's session both documented this as FIXED:
  - Lilith: "A shadowing bug in ics_render — the MCP tool had the same name as its underlying logic import... Roc and I independently identified this bug... fixed"
  - Roc Racoon: "MCP Tool Bug: 'ics_render' tool fails with 'Object of type coroutine is not JSON serializable'" (listed as problem to address in S2-D)
  
  **Current code inspection**: server.py line 1710 `async def ics_render(...)` calls `ics_render_logic(...)` (aliased import from omega.ics.render) at line 1734. The underlying `render()` function in src/omega/ics.py is synchronous (`def render(...)`). The fix appears correct.
  
  **Hypotheses for re-emergence**:
  1. The fix was incomplete — perhaps a different code path or MCP framework version issue
  2. The `m9_safe` decorator or FastMCP framework is mishandling the async return
  3. The researcher agent's specific model/entity combination triggers an edge case
  4. Regression from a subsequent update
  
  **Action**: Assigned to Roc Racoon for investigation (D-kal-070). This is a P1 blocker for Researcher's workflow.

  **Recommendation**: Monitor whether `opencode-zen` fallback is also affected. If so, consider promoting local models or switching the opencode-zen model mapping from `minimax/*` to `deepseek/*` or alternative endpoints. No immediate action required since local-first chain is primary.
