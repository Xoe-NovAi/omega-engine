# 🔱 PrivacyKernel — CPE Scoring & Local Privacy Enforcement (R19)
**AP Token**: `AP-API-PRIVACY-v1.0.0`
⬡ OMEGA ⬡ P3/P6 ⬡ privacy ⬡ API-REFERENCE
**Package**: `omega.privacy`

---

## Overview

The `omega.privacy` package implements **R19 Part 2 (CPE Scoring)** and **R19 Part 4 (Local Privacy Kernel)**. It provides:

1. **Cumulative PII Exposure (CPE) Scoring** — CAMP-inspired co-occurrence graph that tracks PII exposure across conversation turns
2. **Privacy Kernel** — Local model detection (Gemma 4 E2B / Qwen3-1.7B readiness), session vault, pre/post-LLM hooks, placeholder restoration

---

## Module 1: `omega.privacy.cpe_scorer`

### Exports

| Export | Type | Purpose |
|--------|------|---------|
| `CPEAction` | Enum | PASS/WARN/PSEUDONYMIZE/BLOCK action thresholds |
| `PIIEntity` | DataClass | Detected PII entity with value, type, turn, span |
| `CPEResult` | DataClass | Result of CPE processing: action, score, entities |
| `CPESession` | class | Session-scoped CPE tracker with co-occurrence graph |
| `create_cpe_session()` | factory | Create CPESession with default config |

### CPEAction Enum
| Member | Value | Threshold Trigger |
|--------|-------|-------------------|
| `PASS` | `"pass"` | CPE < `MODERATE` threshold |
| `WARN` | `"warn"` | CPE >= `MODERATE` — log but allow |
| `PSEUDONYMIZE` | `"pseudonymize"` | CPE >= `HIGH` — rewrite history |
| `BLOCK` | `"block"` | CPE >= `CRITICAL` — hard stop |

### CPESession
```python
class CPESession(session_id: str, config: Optional[dict] = None)
```

#### Key Methods

**`process_turn(text: str, turn_number: int) -> CPEResult`**
Process a conversation turn for PII exposure.

- Detects PII entities (emails, phones, addresses, API keys, names, etc.)
- Builds co-occurrence graph for entity relationships
- Computes cumulative CPE score
- Returns `CPEResult` with action recommendation

**`get_co_occurrence_graph() -> nx.Graph`**
Get the entity co-occurrence graph (NetworkX).

- Nodes: PII entities (value + type)
- Edges: Co-occurrence weight (count of shared turns)

**`get_exposure_summary() -> dict`**
Get summary of all PII exposures.

- Returns: `{entity_type: {value: count, turns: [...], ...}, ...}`

**`pseudonymize(text: str, entity_types: Optional[Set[str]] = None) -> str`**
Replace PII entities with pseudonyms using Faker.

- Requires `faker` package (optional dependency)
- Returns anonymized text

**`pseudonymize_audit_log(entries: list[dict]) -> list[dict]`**
Batch pseudonymize audit log entries.

---

## Module 2: `omega.privacy.kernel`

### Exports

| Export | Type | Purpose |
|--------|------|---------|
| `PrivacyKernel` | class | Local model detection, session vault, pre/post-LLM hooks |
| `PrivacyHooks` | class | Pre-LLM input scrubbing + post-LLM output restoration |
| `PrivacyVault` | class | Session-scoped PII vault for placeholder management |
| `DetectionResult` | DataClass | Detection result from local model |
| `create_privacy_kernel()` | factory | Create PrivacyKernel with EntityRegistry |
| `create_privacy_hooks()` | factory | Create PrivacyHooks |

### PrivacyKernel
```python
class PrivacyKernel(entity_registry: Optional[Any] = None, config: Optional[dict] = None)
```

#### Key Methods

**`get_local_detection() -> str`**
Get local detection capability status.

- Returns one of:
  - `"gemma4_e2b_ready"` — Gemma 4 E2B execution environment detected
  - `"qwen3_local_ready"` — Qwen3-1.7B local model available
  - `"no_local_model"` — No local model for privacy enforcement

**`create_session_vault(session_id: str) -> dict`**
Create a new session-scoped PII vault.

- Returns: `{"vault_id": str, "created_at": str}`

**`scrub_input(text: str, session_id: str) -> DetectionResult`**
Scrub PII from input text before LLM processing.

- Detects PII, replaces with placeholders (`{{PII:type:ID}}`)
- Stores original values in session vault
- Returns `DetectionResult` with redacted text

**`restore_output(redacted_text: str, session_id: str) -> str`**
Restore PII placeholders in LLM output.

- Replaces `{{PII:type:ID}}` placeholders with original values
- Returns restored text

**`apply_privacy_action(action: CPEAction, text: str) -> str`**
Apply CPE action to text.

- `PASS`: Return as-is
- `WARN`: Log warning, return as-is
- `PSEUDONYMIZE`: Replace with pseudonyms
- `BLOCK`: Return `"[PRIVACY BLOCKED]"`

### PrivacyHooks
```python
class PrivacyHooks(kernel: PrivacyKernel)
```

#### Key Methods

**`pre_llm_hook(input_text: str, session_id: str) -> tuple[str, DetectionResult]`**
Pre-LLM pipeline hook: scrub → detect → return.

- Returns `(redacted_text, detection_result)`

**`post_llm_hook(output_text: str, session_id: str) -> str`**
Post-LLM pipeline hook: restore placeholders → return.

### DetectionResult DataClass
```python
@dataclass
class DetectionResult:
    redacted_text: str
    pii_found: List[dict]
    placeholder_map: Dict[str, str]
    cpe_action: CPEAction
    cpe_score: float
```

---

## Usage Examples

### CPE Scoring
```python
from omega.privacy import create_cpe_session

session = create_cpe_session("ses_001")
result = session.process_turn(
    "My email is user@example.com and my phone is 555-0100",
    turn_number=1
)
print(result.action)  # CPEAction.WARN if moderate threshold reached
```

### Privacy Kernel with Hooks
```python
from omega.privacy import create_privacy_kernel, create_privacy_hooks

kernel = create_privacy_kernel()
hooks = create_privacy_hooks(kernel)

session_id = "ses_001"
kernel.create_session_vault(session_id)

# Pre-LLM: scrub PII
redacted_text, detect = hooks.pre_llm_hook(
    "Email me at user@example.com", session_id
)
# redacted_text: "Email me at {{PII:email:1}}"

# Send redacted_text to LLM...

# Post-LLM: restore PII
restored = hooks.post_llm_hook(
    "I will email {{PII:email:1}}", session_id
)
# restored: "I will email user@example.com"
```

---

## Default Thresholds
```python
DEFAULT_THRESHOLDS = {
    "moderate": 3,    # 3+ PII entities → WARN
    "high": 10,       # 10+ PII entities → PSEUDONYMIZE  
    "critical": 25,   # 25+ PII entities → BLOCK
}
```

Override via `config` parameter in `CPESession` or `PrivacyKernel`.

---

## Cross-Reference

| System | Relation |
|--------|----------|
| `omega.soul.loader` | PrivacyKernel accesses entity directives for privacy rules |
| `omega.vault.crypto` | VaultCrypto used for encrypting session vaults |
| `omega.config.loader` | ConfigLoader provides privacy thresholds |
| `docs/research/R_SOUL_PRIVACY_MODEL.md` | Full R19 spec |
| `SOVEREIGN_MANDATES.md` M11 | Soul Integrity |

---

*⬡ OMEGA ⬡ P3/P6 ⬡ privacy ⬡ v1.0.0*
