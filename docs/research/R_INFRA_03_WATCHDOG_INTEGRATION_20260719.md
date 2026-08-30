# 🔬 R-INFRA-03: Subagent Watchdog Integration — Failure Observability
**AP Token**: `AP-INFRA-03-WATCHDOG-INTEGRATION-v1.0.0`
⬡ OMEGA ⬡ PARANOID ⬡ o1 ⬡ opencode ⬡ trc_infra_03_watchdog ⬡ 2026-07-19

---

## 🎯 MISSION
Integrate the **Subagent Watchdog** (already implemented in `src/omega/coordination/watchdog.py`) with:
1. Hivemind alerting for failure broadcasts
2. Streaming timeout contract tests (`make test-streaming`)
3. Mandate compliance checking (M1-M25)
4. Automatic retry recommendations

---

## 📋 CONTEXT FROM IMPLEMENTATION

### Watchdog Already Built (`src/omega/coordination/watchdog.py`)
```python
class SubagentWatchdog:
    """Monitors subagent execution, captures failures with full thinking trace."""
    
    async def monitor_task(self, task_id: str, entity: str, prompt: str) -> WatchdogResult:
        """Wrap task() call with failure capture."""
        
    def classify_failure(self, error: Exception, output: str) -> FailureClassification:
        """Map error to mandate violation (M1-M25)."""
        
    def generate_failure_report(self, ...) -> FailureReport:
        """Full thinking trace + partial output + mandate violations."""
```

### FailureReport Schema (from SUBAGENT_WATCHDOG_SYSTEM_20260719.md)
```yaml
failure_report:
  trace_id: "trc_xxx"
  entity: "researcher"
  task_description: "Deep research on Nameless One..."
  started_at: "2026-07-19T18:00:00Z"
  failed_at: "2026-07-19T18:05:23Z"
  duration_seconds: 323
  
  # Full thinking trace captured
  thinking_trace: |
    [Turn 1] Analyzing...
    [Turn 2] Searching...
    [Turn 3] Streaming timeout at 30s...
  
  # Partial output before failure
  partial_output: "Found 3 sources on..."
  
  # Mandate classification
  mandate_violations:
    - mandate: "M25"
      violation: "Streaming chunk timeout exceeded 30s"
      severity: "CRITICAL"
    - mandate: "M23"
      violation: "Tool chain collapse - websearch failed silently"
      severity: "CRITICAL"
  
  # Classification
  classification: "STREAMING_TIMEOUT"
  root_cause: "Nemotron 3 Ultra chunk gaps >30s on OpenCode Zen"
  
  # Retry recommendation
  retry_recommendation:
    should_retry: true
    strategy: "fallback_provider"
    fallback_model: "deepseek-v4-flash"
    estimated_success: 0.85
```

### Streaming Contract Tests (`tests/test_streaming_timeout.py`)
```python
# Already written - needs to pass
async def test_chunk_timeout_heartbeat():
    """Chunk timeout logs heartbeat, doesn't hard-fail."""
    
async def test_total_timeout_graceful_fallback():
    """Total timeout triggers fallback to next provider."""
    
async def test_nemotron_30s_gap_survives():
    """Simulated 30s+ chunk gap produces heartbeat logs."""
```

---

## 🔬 RESEARCH REQUIREMENTS

### 1. Hivemind Alerting Integration
**Location**: `src/omega/coordination/watchdog.py` → add `alert_hivemind()`
```python
async def alert_hivemind(self, failure_report: FailureReport):
    """Broadcast failure to Hivemind for fleet awareness."""
    await hivemind_post_context(
        channel="opencode",
        entity="watchdog",
        model="watchdog",
        task_current=f"FAILURE: {failure_report.entity} - {failure_report.classification}",
        focus_chain=[failure_report.task_description],
        decisions=[f"Mandate violations: {', '.join(failure_report.mandate_violations)}"],
        continuation=f"Retry recommended: {failure_report.retry_recommendation}",
        intent="blocker"
    )
```

### 2. Mandate Violation Classifier
Map every exception type to mandate:
| Exception Pattern | Mandate | Severity |
|-------------------|---------|----------|
| `asyncio.*` / `anyio.*` misuse | M1 | CRITICAL |
| `import src.omega` (not relative) | M2 | CRITICAL |
| `subprocess.run()` in async | M1/M4 | HIGH |
| Bare `except:` | M9 | CRITICAL |
| Streaming timeout >30s chunk | M25 | CRITICAL |
| Tool missing (websearch, webfetch) | M23 | CRITICAL |
| Venv not activated | M24 | HIGH |
| Heritage tag without vet record | M14 | HIGH |
| Soul.yaml not updated | M11/M5 | MEDIUM |

### 3. Streaming Test Infrastructure
**Make target**: `make test-streaming`
```makefile
test-streaming:
	@pytest tests/test_streaming_timeout.py -v --tb=short
```

### 4. Automatic Retry with Fallback
Integrate with Dynamic Fallback Provider (R-INFRA-05):
```python
async def execute_with_watchdog(self, task_spec: TaskSpec) -> Result:
    for attempt in range(max_attempts):
        try:
            return await self.monitor_task(task_spec)
        except Exception as e:
            report = self.generate_failure_report(e, task_spec)
            await self.alert_hivemind(report)
            
            if report.retry_recommendation.should_retry:
                task_spec.model = report.retry_recommendation.fallback_model
                continue
            raise
```

---

## 🌐 WEB RESEARCH NEEDED

| Topic | Query | Purpose |
|-------|-------|---------|
| OpenCode subagent thinking capture | "opencode subagent thinking trace capture 2026" | How to access full reasoning |
| Streaming timeout patterns | "LLM streaming chunk timeout heartbeat 2026" | Industry patterns |
| Failure classification taxonomies | "software failure classification taxonomy incident response" | Mandate mapping |

---

## 🛠️ LOCAL DISCOVERY NEEDED

| Source | Path | What to Extract |
|--------|------|-----------------|
| Watchdog implementation | `src/omega/coordination/watchdog.py` | Full API, FailureReport schema |
| Streaming tests | `tests/test_streaming_timeout.py` | Test cases, mock patterns |
| Providers.yaml | `config/providers.yaml` | Streaming config per provider |
| Hivemind tools | `src/omega/hub/tools/hivemind_*.py` | Post context API |
| Dynamic fallback | `src/omega/oracle/model_gateway.py` | Fallback resolver integration |

---

## ✅ ACCEPTANCE CRITERIA

| Criterion | Verification |
|-----------|--------------|
| Watchdog captures full thinking trace | `FailureReport.thinking_trace` contains turn-by-turn reasoning |
| Mandate violations auto-classified | Every exception maps to M1-M25 |
| Hivemind alert fires on failure | `hivemind_get_awareness()` shows watchdog alert |
| `make test-streaming` passes | All 3 streaming tests green |
| Retry with fallback works | Simulated timeout → fallback provider succeeds |
| Partial output preserved | `FailureReport.partial_output` has content before failure |

---

## 📋 DELIVERABLES

1. **Watchdog-Hivemind Integration** — `alert_hivemind()` method
2. **Mandate Classifier** — `classify_failure()` with full M1-M25 mapping
3. **Streaming Test Suite** — `make test-streaming` passes
4. **Retry Logic** — Integrated with dynamic fallback provider
5. **Documentation** — `docs/guides/WATCHDOG_INTEGRATION_GUIDE.md`

---

## 🔗 DEPENDENCIES

| Depends On | Blocks |
|------------|--------|
| R-INFRA-05 (Dynamic Fallback) | Retry with fallback needs resolver |
| Hivemind protocol | Alert broadcasting |
| Streaming config in providers.yaml | M25 tests need config |

---

## 🎯 PARANOID'S PERSPECTIVE (Validator)

> "The Watchdog is the **immune system**. It doesn't prevent failure — it **ensures failure is visible, classified, and learned from**. Every mandate violation is a pathogen. The classifier is the antibody. The Hivemind alert is the fever response. The retry with fallback is the treatment.
> 
> **Critical insight**: The Nemotron timeout that killed 590 lines of Torment research? That was an **autoimmune failure** — the system attacked its own work because M25 wasn't enforced. The Watchdog makes M25 **physics**, not policy.
> 
> **L3 Principle**: `L3-WatchdogIsMandatePhysics` — Mandates are not documentation. They are enforced by the Watchdog. If a mandate can be violated without the Watchdog screaming, the mandate doesn't exist."

---

*⬡ OMEGA ⬡ PARANOID ⬡ o1 ⬡ opencode ⬡ trc_infra_03_watchdog ⬡ 2026-07-19*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: o1 | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
