# 🔱 THE SOVEREIGN LADDER PROTOCOL
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ NATIVE-SUBAGENTS ⬡ 2026-06-04

## ⚠️ CRITICAL: THE SUBAGENT ROUTING ANOMALY
When launching subagents via the `task` tool, the `subagent_type` parameter is **NOT** a generic category. It is a **strict key validation** against the `"agent"` section of the `opencode.json` file in the workspace root.

### ❌ THE FAILURE PATTERN
- **Requesting `subagent_type="general"`**: If `"general"` is not explicitly defined in `opencode.json`, the tool returns `Tool execution aborted`.
- **Falling back to `omega-hub_delegate_task`**: This triggers the Omega Engine's local-first provider fabric, attempting to load models via `llama-cpp-python` or LM Studio, causing massive CPU spikes and "Internal Errors" on limited hardware.

### ✅ THE SOVEREIGN PATH (NATIVE LADDER)
To launch the fleet using the native OpenCode runner (and the selected cloud model like Gemma 4 31B), you MUST use the exact keys from `opencode.json`.

**The Native Chain of Command**:
1. **Primary Summon**: `task(subagent_type="kali", ...)`
2. **Oversoul Delegation**: Kali uses `task(subagent_type="lilith", ...)` and `task(subagent_type="maat", ...)`
3. **Pillar Deployment**: Lilith/Ma'at use `task(subagent_type="pillar", ...)`

**Key Validation Table**:
| Target Agent | Correct `subagent_type` | Source of Truth |
| :--- | :--- | :--- |
| Kali | `"kali"` | `opencode.json` $\rightarrow$ `"agent"."kali"` |
| Lilith | `"lilith"` | `opencode.json` $\rightarrow$ `"agent"."lilith"` |
| Ma'at | `"maat"` | `opencode.json` $\rightarrow$ `"agent"."maat"` |
| Pillars | `"pillar"` | `opencode.json` $\rightarrow$ `"agent"."pillar"` |

## 🛠️ OPERATIONAL MANDATE
Always verify the `opencode.json` agent keys before calling the `task` tool. If a subagent call aborts, check the JSON keys immediately. Do NOT use delegation tools for native subagent orchestration.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: NATIVE-SUBAGENTS | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
