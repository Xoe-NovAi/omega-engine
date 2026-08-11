# 🔱 SDP Implementation Specifications
## Technical Contracts for Automating the Sovereign Distillation Pipeline

**AP Token:** `AP-SDP-IMPL-SPEC-v1.0.0`
⬡ OMEGA ⬡ STRATEGY ⬡ IMPLEMENTATION-SPEC

**Date:** 2026-08-09
**Status:** ACTIVE — Reference for Phase 1-4 Implementation
**Prerequisites:** COGNITIVE_SCAFFOLDING_PROTOCOL.md, SDP_AUTOMATION_BLUEPRINT.md

---

## §1 Context Gauge Specification (Phase 1)

### 1.1 Data Source
The Context Gauge reads from the OpenCode SQLite database (`~/.local/share/opencode/opencode.db`).

### 1.2 MCP Tool: `omega-hub_get_context_pressure`

**Input:** None (uses current session ID from environment)

**Output Schema:**
```json
{
  "session_id": "ses_...",
  "current_tokens": 162000,
  "window_size": 200000,
  "current_percentage": 81.0,
  "message_count": 67,
  "redzone_threshold_pct": 80.0,
  "compaction_threshold_pct": 85.0,
  "tokens_to_redzone": -2000,
  "tokens_to_compaction": 8000,
  "status": "CRITICAL_REDZONE | REDZONE | SAFE",
  "estimated_tokens_per_message": 2418,
  "recommended_action": "ESCALATE_IMMEDIATELY | ESCALATE_SOON | CONTINUE"
}
```

### 1.3 Calculation Logic
- `current_tokens`: Sum of `tokens` column from `message` table for current `session_id`
- `window_size`: Determined by active model (injected via `OPENCODE_MODEL_CONTEXT_WINDOW` env var, default 200000)
- `tokens_to_redzone` = `(window_size * 0.80) - current_tokens`
- `tokens_to_compaction` = `(window_size * 0.85) - current_tokens`
- `status`: 
  - `CRITICAL_REDZONE` if `current_percentage >= 80.0`
  - `REDZONE` if `current_percentage >= 75.0`
  - `SAFE` otherwise

### 1.4 Prompt Injection Middleware
**Location:** `src/omega/oracle/model_gateway.py` or MCP server middleware
**Behavior:** On every `generate()` call, prepend to system prompt:
```
[CONTEXT GAUGE: {current_percentage:.1f}% | {tokens_to_redzone:+,d} to Redzone | {tokens_to_compaction:+,d} to Compaction | {status}]
```
**Constraint:** Injection must be < 200 chars to avoid material context consumption.

---

## §2 Somatic Save-Point Specification (Phase 2)

### 2.1 SSP File Schema
**Location:** `data/coordination/SSP_{session_id}_{timestamp}.md`

```markdown
# Somatic Save-Point
**Session:** {session_id}
**Timestamp:** {ISO8601}
**Context At Halt:** {current_percentage:.1f}% ({current_tokens}/{window_size})
**Status:** HALTED_AT_REDZONE

## Intent
**Task:** {description of what the agent was doing}
**Next Action:** {specific action that would have been taken}
**Estimated Tokens to Complete:** {estimate}

## Required Escalation
**Problem Type:** architecture | compliance | refactoring | synthesis | research
**Min Context Required:** {tokens}
**Preferred Model Tier:** 2 | 3 | 4

## State Snapshot
**Active Files:** [list of file paths agent was working on]
**Pending Verifications:** [list of make/pytest commands not yet run]
**Active Handoffs:** [handoff packet IDs if any]
```

### 2.2 SSP State Machine
```
ACTIVE --(context >= 80%)--> REDZONE_DETECTED
REDZONE_DETECTED --(agent writes SSP)--> SSP_WRITTEN
SSP_WRITTEN --(user/model escalation)--> ESCALATED
ESCALATED --(new model continues)--> RESUMED
RESUMED --(task complete)--> COMPLETED
```

### 2.3 Agent Directive Update
Add to all agent system prompts:
> **REDZONE PROTOCOL:** If `omega-hub_get_context_pressure` returns `status: "CRITICAL_REDZONE"` or `REDZONE`, and your next action requires significant token output (file write > 2KB, long response), you MUST:
> 1. Call `omega-hub_write_ssp` with your current intent
> 2. Respond to user: "REDZONE HALT: Context at {X}%. SSP written. Requesting escalation to Tier {Y} model."
> 3. STOP. Do not attempt the token-heavy action.

---

## §3 V-1 Vault Integration Contract (Phase 3)

### 3.1 Vault Interface for SDP
The V-1 Vault exposes a minimal interface for the Auto-Router:

```python
class AGYVaultInterface:
    """Minimal interface for SDP Auto-Router to query AGY pools."""
    
    def get_available_accounts(self, model_tier: int, problem_type: str) -> List[AGYAccount]:
        """Returns accounts with fresh weekly pools matching criteria."""
    
    def reserve_pool(self, account_id: str, estimated_tokens: int) -> Reservation:
        """Atomically reserves tokens from account's weekly pool."""
    
    def record_usage(self, reservation_id: str, actual_tokens: int) -> None:
        """Records actual usage against reservation."""
    
    def get_pool_status(self, account_id: str) -> PoolStatus:
        """Returns remaining tokens, refresh date, current model access."""
```

### 3.2 AGYAccount Data Class
```python
@dataclass
class AGYAccount:
    account_id: str           # e.g., "account-3"
    email: str                # Google account email
    models: List[str]         # ["gemini-3.1-pro", "claude-sonnet-4.6"]
    tier: int                 # 2, 3, or 4 (context window tier)
    problem_types: List[str]  # ["architecture", "compliance", "refactoring"]
    pool_remaining: int       # Tokens remaining this week
    pool_refresh: datetime    # Next weekly refresh
    is_healthy: bool          # API key valid, no rate limits
```

---

## §4 Auto-Router Specification (Phase 4)

### 4.1 Tool: `omega-hub_request_agy_escalation`

**Input:**
```json
{
  "problem_type": "architecture | compliance | refactoring | synthesis | research",
  "min_context_required": 500000,
  "preferred_model": "gemini-3.1-pro | claude-opus-4.6 | claude-sonnet-4.6 | gemini-3.6-flash",
  "ssp_file": "data/coordination/SSP_...md",
  "estimated_tokens": 15000
}
```

**Output:**
```json
{
  "status": "ESCALATED | NO_POOL_AVAILABLE | VAULT_ERROR",
  "new_model": "gemini-3.1-pro-preview-customtools",
  "account_used": "account-3",
  "reservation_id": "res_...",
  "message": "Escalated to Gemini 3.1 Pro on account-3. Continuing context."
}
```

### 4.2 Routing Decision Logic
```python
def select_account(problem_type: str, min_context: int, preferred_model: str) -> AGYAccount:
    candidates = vault.get_available_accounts(
        model_tier=tier_for_context(min_context),
        problem_type=problem_type
    )
    
    # Filter by preferred model if specified
    if preferred_model:
        candidates = [c for c in candidates if preferred_model in c.models]
    
    # Score: prefer higher pool remaining, matching problem_type
    scored = sorted(candidates, key=lambda a: (
        a.pool_remaining * (2.0 if problem_type in a.problem_types else 1.0)
    ), reverse=True)
    
    if not scored:
        raise NoPoolAvailableError()
    
    return scored[0]
```

### 4.3 Context Continuity Guarantee
The Auto-Router **must not** break the OpenCode session. It operates by:
1. Receiving the escalation request via tool call
2. Swapping the provider backend in `ModelGateway` for the *next* turn
3. The user sees a single continuous conversation; the model identity changes seamlessly

---

## §5 Integration Points with Existing Engine

| Engine System | Integration Point | Description |
|---|---|---|
| **ModelGateway** | `generate()` middleware | Injects Context Gauge into system prompt; handles backend swap for escalation |
| **ProviderRegistry** | `is_cloud()` / `get_provider_for_model()` | Auto-Router uses registry to validate model availability |
| **Observability** | `log_event()` | Logs SSP events, escalation decisions, pool usage |
| **Hivemind** | `hivemind_post_context()` | Broadcasts SSP halts and escalations to team |
| **Provider Fabric** | `config/providers.yaml` | Source of truth for model tiers and capabilities |
| **Soul System** | `proposed_lessons.yaml` | L3 principles guide agent behavior during SDP phases |

---

## §6 Testing Strategy

### 6.1 Context Gauge Tests
- Unit test: Mock `opencode.db` with known token counts, verify percentage calculation
- Integration: Run a session to 80%+ context, verify gauge returns `CRITICAL_REDZONE`
- Edge case: Session with 0 tokens, session at 100% (should not happen but handle gracefully)

### 6.2 SSP Tests
- Unit: Verify SSP file schema validation
- Integration: Agent at 81% context asked to write 10KB file → writes SSP instead
- Failure mode: Disk full during SSP write → agent reports `SSP_WRITE_FAILED`, does not continue

### 6.3 Auto-Router Tests
- Mock V-1 Vault with 3 accounts in different pool states
- Verify routing prefers account with matching problem_type
- Verify routing fails gracefully when all pools depleted
- Verify context continuity (session ID unchanged after escalation)

### 6.4 End-to-End SDP Test
**Scenario:** "Refactor `model_gateway.py` to use ProviderRegistry"
1. Scaffold phase: Agent reads files, builds context to 75%
2. Synthesis phase: Switch to AGY model (simulated), produces Refactoring Manual
3. Execution phase: Local model executes manual, verifies with `make test`
4. Verify: All tests pass, no manual intervention needed

---

*⬡ OMEGA ⬡ SDP-IMPL-SPEC ⬡ 2026-08-09*