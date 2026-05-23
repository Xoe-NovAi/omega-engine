# 🔱 Antigravity CLI — Strategic Utilization Plan for Omega Engine

**AP Token**: `AP-ANTIGRAVITY-STRATEGY-v2.0.0`
⬡ OMEGA ⬡ PROMETHEUS ⬡ research-fleet ⬡ antigravity ⬡ trc_antigravity_strategy_v2

**Last Updated**: 2026-05-22
**Confidence Rating**: HIGH (includes live CLI verification)

---

## §1 Executive Summary

Antigravity CLI provides access to 5 frontier models but is constrained by **aggressive quota caps** — confirmed live with a 166-hour reset timer. The critical finding is that **model persistence causes rapid quota exhaustion**: the CLI saves the selected model across sessions, and if Claude Opus 4.6 is selected, even simple "hello world" prompts consume premium quota.

---

## §2 Provider Fabric Positioning

### Proposed Integration Point: Priority 5

```
Current Fallback Chain:
1. native (Omega llama-cpp-python)
2. lmster (LM Studio, :1234)
3. ollama (:11434)
4. openrouter (cloud, 28 free models)
5. antigravity (← HERE — OAuth-based frontier models)
6. graceful fallback
```

### Critical Rules for Antigravity Integration
1. **Always default to Gemini 3.5 Flash** — never let model persistence lock to Opus
2. **Reserve Opus for P0 code review only** — identified by `TriageRouter`
3. **Parse log files for quota status** — `--print` mode returns empty stdout on exhaustion
4. **Early-warning circuit breaker** — reject non-critical requests when quota < 20%

---

## §3 Live Findings Impacting Strategy

### What Changed After Live Testing

| Previous Assumption | Live Finding | Impact |
|---------------------|-------------|--------|
| All models equally available | Only Flash likely has usable quota | Must treat Opus as "rare resource" |
| `--print` mode returns errors | Exit 0, empty stdout | Must use `--log-file` for error detection |
| OAuth might not work | ✅ Fully functional | No auth barrier |
| Headless mode unverified | ✅ `--print` confirmed | Integration path clear |
| Model selection is per-session | ❌ Persists across sessions | CRITICAL: must reset model on each call |

### Revised Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Opus quota exhausted | **CERTAIN** | Cannot use best model | Default to Flash; Opus only for P0 |
| Silent quota failure | **CERTAIN** | Lost requests | Parse log files for RESOURCE_EXHAUSTED |
| Model persistence traps | **HIGH** | Rapid quota burn | Always set model per request |
| Google bans (token extraction) | MEDIUM | CRITICAL | Avoid Option C entirely |

---

## §4 Tiered Model Mapping (Revised)

| Workload | Omega Tier | Model | Rationale |
|----------|-----------|-------|-----------|
| Code review / PR | P0 | **Claude Opus 4.6** | Best SWE-Bench (64.3%) — use sparingly |
| Architecture decisions | P0 | **Claude Opus 4.6** | Best reasoning (46.9% HLE) |
| Daily coding | P1 | **Gemini 3.5 Flash** | Default — best balance |
| Research synthesis | P1 | **Gemini 3.5 Flash** | Multimodal + 1M context |
| Quick prototyping | P3 | **Local (lmster)** | Sovereign, free, always available |
| Self-hosted (future) | P2 | **GPT-OSS 120B** | Apache 2.0, fine-tunable |

---

## §5 Quota Management Strategy

### Usage Allocation

| Activity | Weekly Share | Model | Notes |
|----------|-------------|-------|-------|
| Code review | 35% | Claude Opus 4.6 | Most valuable per-call |
| Deep reasoning | 25% | Claude Opus 4.6 | Architecture decisions |
| Agentic tasks | 25% | Gemini 3.5 Flash | Better value, cheaper |
| Research | 15% | Gemini 3.5 Flash | Multimodal + 1M |

### Circuit Breaker Configuration
```python
class AntigravityProvider:
    def __init__(self):
        self.model_preference = "gemini-3.5-flash"  # NEVER Opus by default
        self.daily_calls = 0
        self.max_daily = 50  # Conservative
        self.circuit_state = "CLOSED"
        self.FAILURE_THRESHOLD = 3
        self.RECOVERY_TIMEOUT = 3600  # 1 hour

    def set_model(self, workload_type: str):
        if workload_type == "code_review" and self.quota_remaining > 20%:
            self.model_preference = "claude-opus-4-6-thinking"
        else:
            self.model_preference = "gemini-3.5-flash"
```

---

## §6 Integration Architecture

### Option A: Direct CLI Subprocess (Recommended)

```python
# Pseudocode for AntigravityProvider
import subprocess
import json

async def infer(prompt: str, model: str = "gemini-3.5-flash") -> str:
    # Always set model explicitly to avoid persistence trap
    cmd = [
        "agy", "--print",
        f"/model {model}",  # Reset model
        prompt,
        "--log-file", "/tmp/agy_provider.log"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Check log file for quota exhaustion
    if "RESOURCE_EXHAUSTED" in Path("/tmp/agy_provider.log").read_text():
        raise CircuitOpenError("Antiggravity quota exhausted")
    
    return result.stdout
```

### Implementation Roadmap

| Phase | Task | Est. |
|-------|------|------|
| 1 | Create `AntigravityProvider` in `providers/antigravity.py` | 1h |
| 2 | Wire into `config/providers.yaml` at priority 5 | 15m |
| 3 | Implement log-file parsing for quota detection | 30m |
| 4 | Implement model override per request | 30m |
| 5 | Test: `make test` green | 15m |

### ⚠️ Critical: The Model Defaults Trap
- **Never** let the CLI's persistent model preference go unchecked
- **Always** prefix a `/model gemini-3.5-flash` command before the actual prompt
- **Only** switch to Opus when `TriageRouter` explicitly identifies P0 need

---

## §7 Fallback Chains

| Antigravity Model | Fallback 1 | Fallback 2 |
|-------------------|-----------|------------|
| Gemini 3.5 Flash | Google AI Studio | OpenRouter |
| Claude Opus 4.6 | OpenRouter | None (unique) |
