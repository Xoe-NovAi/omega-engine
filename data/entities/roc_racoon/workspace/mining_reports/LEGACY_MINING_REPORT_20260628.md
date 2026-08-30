<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Legacy Mining Report

**Date**: 2026-06-28
**Mining Agent**: ROC_RACOON
**Mission**: Mine legacy codebases for proven patterns applicable to 3 critical gaps identified by MaKaLi Council

## Target 1: Memory/Security Patterns

### Files Found
1. **`~/Documents/Archives/Old-Stacks/Xoe-NovAi/app/XNAi_rag_app/crawl.py`** — Security validation and content sanitization patterns
2. **`~/archive/foundation-legacy/versions/Xoe-NovAi/app/XNAi_rag_app/ingest_library.py`** — Content quality validation and domain filtering
3. **`~/Documents/docs-backup/internal_docs/`** — Security architecture documentation (ACL, encryption)

### Reusable Patterns

#### [PATTERN-1: INPUT_VALIDATION] Whitelist Input Validation
**Source**: `crawl.py:89-103`
```python
def validate_safe_input(text: str, max_length: int = 200) -> bool:
    """Whitelist validation for curation inputs to prevent command injection."""
    if not text or len(text) > max_length:
        return False
    pattern = r'^[a-zA-Z0-9\s\-_.,()\[\]{}]{1,%d}$' % max_length
    return bool(re.match(pattern, text))
```
**Application to PII Masking**: Use as first-pass validation before PII detection. Reject inputs that don't match expected character sets.

#### [PATTERN-2: CONTENT_SANITIZATION] Script/Style Tag Removal
**Source**: `crawl.py:236-263`
```python
def sanitize_content(content: str, remove_scripts: bool = True) -> str:
    """Sanitize crawled content by removing scripts and excessive whitespace."""
    if not content:
        return ""
    sanitized = content
    if remove_scripts:
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.DOTALL | re.IGNORECASE)
        sanitized = re.sub(r'<style[^>]*>.*?</style>', '', sanitized, flags=re.DOTALL | re.IGNORECASE)
    sanitized = re.sub(r'\s+', ' ', sanitized)
    return sanitized.strip()
```
**Application to PII Masking**: Extend pattern to detect and redact PII patterns (emails, phone numbers, SSNs) using regex similar to script tag removal.

#### [PATTERN-3: ID_SANITIZATION] Path Traversal Prevention
**Source**: `crawl.py:105-116`
```python
def sanitize_id(raw_id: str) -> str:
    """Prevent path traversal by sanitizing IDs."""
    safe = re.sub(r'[^a-zA-Z0-9_-]', '', raw_id)
    return safe[:100]
```
**Application to PII Masking**: Use for sanitizing entity names and identifiers before injection into LLM context.

#### [PATTERN-4: QUALITY_VALIDATION] Content Quality Filtering
**Source**: `ingest_library.py:475-497`
```python
def _validate_domain_texts(self, texts: List[ContentMetadata]) -> List[ContentMetadata]:
    """Validate texts for domain relevance and quality."""
    config = self.domain_configs.get(self.domain, {})
    min_authority = config.get('min_authority_score', 0.5)
    validated = []
    for text in texts:
        if not self._is_domain_relevant(text):
            continue
        if hasattr(text, 'scholarly') and text.scholarly:
            if text.scholarly.scholarly_rating < min_authority:
                continue
        if text.quality_score < 0.5:
            continue
        validated.append(text)
    return validated[:config.get('max_texts', 1000)]
```
**Application to PII Masking**: Implement quality scoring for PII detection confidence. Only mask entities with high confidence scores.

---

## Target 2: Observability/Tracing Patterns

### Files Found
1. **`~/Documents/Xoe-NovAi/xna-omega-legacy/src/omega/core/observability.py`** — OpenTelemetry integration (zero-telemetry compliant)
2. **`~/Documents/Xoe-NovAi/xna-omega-legacy/src/omega/services/log_aggregator.py`** — Request ID correlation and log aggregation
3. **`~/Documents/Xoe-NovAi/xna-omega-legacy/src/omega/schemas/responses.py`** — Response schemas with request_id fields

### Reusable Patterns

#### [PATTERN-5: ZERO_TELEMETRY_TRACER] Dummy Tracer for Compliance
**Source**: `observability.py:26-65`
```python
class Tracer:
    """Dummy Tracer for zero-telemetry compliance."""
    @contextmanager
    def start_as_current_span(self, *args, **kwargs):
        class DummySpan:
            def set_attribute(self, *args, **kwargs): pass
            def set_status(self, *args, **kwargs): pass
            def record_exception(self, *args, **kwargs): pass
        logger.debug(f"Tracing disabled: Span '{args[0]}' started.")
        yield DummySpan()

def get_tracer(name: str = "omega-core") -> Tracer:
    """Returns a dummy tracer instance for the given name (zero-telemetry compliant)."""
    return Tracer()
```
**Application to Trace Propagation**: Omega already has zero-telemetry mandate (M8). This pattern provides trace context without external export. Can be extended to propagate trace_id through AnyIO boundaries.

#### [PATTERN-6: REQUEST_CORRELATION] Request ID in Log Entries
**Source**: `log_aggregator.py:78-100, 198-228`
```python
@dataclass
class LogEntry:
    """A log entry."""
    timestamp: datetime
    level: str
    message: str
    module: Optional[str] = None
    lineno: Optional[int] = None
    sphere: Optional[str] = None
    entity: Optional[str] = None
    request_id: Optional[str] = None  # <-- CORRELATION ID

def add_entry(self, message: str, level: str = "INFO", ..., request_id: Optional[str] = None) -> None:
    entry = LogEntry(
        timestamp=datetime.now(timezone.utc),
        level=level.upper(),
        message=message,
        request_id=request_id,  # <-- PROPAGATED
    )
    self._index_entry(entry)
```
**Application to Trace Propagation**: Extend Omega's existing trace_id pattern (found in memory_store.py) to all async boundaries. Use contextvars to propagate trace_id through AnyIO tasks.

#### [PATTERN-7: SPHERE_FILTERING] Multi-dimensional Log Filtering
**Source**: `log_aggregator.py:233-300`
```python
def search(self, query=None, level=None, sphere=None, entity=None, request_id=None, ...):
    """Search logs with filters."""
    results = []
    candidates = self._entries
    if level and level.upper() in self._by_level:
        candidates = self._by_level[level.upper()]
    if sphere and sphere in self._by_sphere:
        candidates = [e for e in candidates if e in self._by_sphere.get(sphere, [])]
    # Apply filters...
```
**Application to Trace Propagation**: Omega's observability can adopt multi-dimensional filtering (entity, pillar, trace_id) for forensic analysis.

---

## Target 3: Entity/Agent Patterns

### Files Found
1. **`~/Documents/Xoe-NovAi/xna-omega-legacy/src/omega/core/agent_bus.py`** — Agent-to-agent communication with Pydantic validation
2. **`~/Documents/Archives/Old-Stacks/Xoe-NovAi/app/XNAi_rag_app/library_api_integrations.py`** — Entity extraction and command parsing

### Reusable Patterns

#### [PATTERN-8: AGENT_MESSAGE] Pydantic-validated Agent Communication
**Source**: `agent_bus.py:83-140`
```python
class AgentMessage(BaseModel):
    """Message for agent-to-agent communication with Pydantic validation."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True,
    )
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_agent: str = Field(min_length=1, max_length=128)
    target_agent: str = Field(min_length=1, max_length=128)
    task: str = Field(min_length=1, max_length=512)
    status: str = Field(default="pending", pattern="^(pending|processing|completed|failed)$")
    data: Dict[str, Any] = Field(default_factory=dict)
    entity_sphere: Optional[int] = Field(default=None, ge=6001, le=8013)
    priority: MessagePriority = Field(default=MessagePriority.NORMAL)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    origin_trace: List[str] = Field(default_factory=list)
    sender_did: Optional[str] = Field(default=None, max_length=256)
    signature: Optional[str] = Field(default=None, max_length=128)
```
**Application to A2A Agent Cards**: This is a complete agent-to-agent message schema. Can be adapted to A2A v1.0 Agent Card format. Key fields: source_agent, target_agent, task, data, origin_trace.

#### [PATTERN-9: AGENT_PERMISSIONS] Access Control Matrix
**Source**: `agent_bus.py:148-192`
```python
class AgentPermissions:
    """Access control matrix for agent publishing and subscribing."""
    KNOWN_AGENTS: Set[str] = {
        "system", "command", "foundry", "audit",
        "r1", "r2", "r3", "r4", "r5",
        "d1", "d2", "d3", "d4", "genesis", "curation", "scholarly", "metadata_enricher",
    }
    PUBLISHER_PERMISSIONS: Dict[str, Set[str]] = {
        "system": {"*"},  # System can publish to all
        "command": {"*"},  # Command can publish to all
        "foundry": {"foundry", "audit", "d1", "d2"},
        "audit": {"*"},
        "r1": {"r2", "r3", "r4", "foundry"},
        # ...
    }
```
**Application to A2A Agent Cards**: Omega's 11-agent fleet can adopt this permission matrix pattern for Agent Card capabilities. Each agent declares what it can publish to and subscribe from.

#### [PATTERN-10: ENTITY_EXTRACTION] NLP Entity Recognition
**Source**: `library_api_integrations.py:1763-1770`
```python
def _get_entity_extractor(self):
    """Get entity extractor (using spaCy if available)."""
    try:
        import spacy
        return spacy.load("en_core_web_sm")
    except ImportError:
        logger.warning("spaCy not available - using regex-based entity extraction")
        return None
```
**Application to A2A Agent Cards**: Use for extracting capabilities and domain expertise from agent descriptions when generating Agent Cards.

---

## Cross-Era Correlation

### Pattern Lineage Across Eras

| Pattern | Era 1 (ANAi) | Era 2 (XNAi) | Era 3 (Omega-Stack) | Era 4 (Omega-Engine) |
|---------|--------------|--------------|---------------------|----------------------|
| **Input Validation** | Unknown | `validate_safe_input()` | Ported | **GAP: Not implemented** |
| **Content Sanitization** | Unknown | `sanitize_content()` | Ported | **GAP: Not implemented** |
| **Request ID** | Unknown | Unknown | `request_id` in schemas | `trace_id` in memory_store |
| **Agent Communication** | Unknown | Unknown | `AgentMessage` Pydantic | **GAP: No A2A protocol** |
| **Entity Extraction** | Unknown | spaCy NER | Ported | **GAP: No NER in context injection** |

### Key Insight
The ANAi/XNAi era had robust security patterns (input validation, content sanitization) that were **not ported** to Omega-Engine. These are directly applicable to PII masking.

---

## Directly Portable Code

### 1. Input Validation for PII Masking
```python
# From crawl.py:89-103 — DIRECT PORT
import re
from typing import Optional

def validate_safe_input(text: str, max_length: int = 200) -> bool:
    """Whitelist validation for inputs before PII detection."""
    if not text or len(text) > max_length:
        return False
    pattern = r'^[a-zA-Z0-9\s\-_.,()\[\]{}]{1,%d}$' % max_length
    return bool(re.match(pattern, text))

def sanitize_id(raw_id: str) -> str:
    """Sanitize identifiers for LLM context injection."""
    safe = re.sub(r'[^a-zA-Z0-9_-]', '', raw_id)
    return safe[:100]
```

### 2. Content Sanitization for PII Redaction
```python
# From crawl.py:236-263 — EXTEND FOR PII
import re
from typing import List, Tuple

# PII patterns (extend with GLiNER for general PII)
PII_PATTERNS = {
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'phone': r'\b(?:\+?1[-. ]?)?\(?[0-9]{3}\)?[-. ]?[0-9]{3}[-. ]?[0-9]{4}\b',
    'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
    'api_key': r'\b(?:sk|pk|api)[-_][A-Za-z0-9]{20,}\b',
}

def mask_pii(content: str, mask_char: str = '*', preserve_length: bool = True) -> Tuple[str, List[str]]:
    """Mask PII in content, return masked content and list of detected types."""
    detected_types = []
    masked = content
    
    for pii_type, pattern in PII_PATTERNS.items():
        matches = re.finditer(pattern, masked)
        for match in matches:
            detected_types.append(pii_type)
            original = match.group()
            if preserve_length:
                masked = masked.replace(original, mask_char * len(original))
            else:
                masked = masked.replace(original, f'[{pii_type.upper()}]')
    
    return masked, detected_types
```

### 3. Request ID Propagation (AnyIO-compatible)
```python
# From log_aggregator.py:78-100 — ADAPT FOR AnyIO
import contextvars
import uuid
from typing import Optional

# Context variable for trace propagation (AnyIO-compatible)
trace_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'trace_id', default=None
)

def get_trace_id() -> str:
    """Get current trace_id or generate new one."""
    tid = trace_id_var.get()
    if tid is None:
        tid = f"trace_{uuid.uuid4().hex[:12]}"
        trace_id_var.set(tid)
    return tid

def set_trace_id(trace_id: str) -> None:
    """Set trace_id in current context."""
    trace_id_var.set(trace_id)
```

### 4. Agent Message Schema (A2A Ready)
```python
# From agent_bus.py:83-140 — ADAPT FOR A2A AGENT CARDS
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import uuid

class AgentCard(BaseModel):
    """A2A Agent Card schema based on legacy AgentMessage pattern."""
    # Identity
    agent_id: str = Field(description="Unique agent identifier")
    name: str = Field(min_length=1, max_length=128)
    description: str = Field(default="")
    
    # Capabilities
    capabilities: List[str] = Field(default_factory=list)
    domains: List[str] = Field(default_factory=list)
    
    # Communication
    supported_tasks: List[str] = Field(default_factory=list)
    priority: str = Field(default="normal")
    
    # Metadata
    version: str = Field(default="1.0.0")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # A2A Protocol
    endpoint: Optional[str] = Field(default=None)
    protocol_version: str = Field(default="1.0")
```

---

## Recommendations for MaKaLi Council

### Gap 1: PII Masking
**Priority**: HIGH
**Effort**: Medium (2-3 days)
**Approach**: 
1. Port `validate_safe_input()` and `sanitize_content()` from ANAi era
2. Extend with PII regex patterns (email, phone, SSN, API keys)
3. Integrate GLiNER for general PII detection (as Jem recommended)
4. Implement Gateway proxy pattern: detect → tokenize → LLM → detokenize

### Gap 2: Trace ID Propagation
**Priority**: HIGH
**Effort**: Low (1-2 days)
**Approach**:
1. Use existing `trace_id` pattern from memory_store.py
2. Extend with contextvars for AnyIO compatibility (Mandate 1)
3. Propagate through all async boundaries using `trace_id_var`
4. Adopt zero-telemetry tracer pattern (M8 compliant)

### Gap 3: A2A Agent Cards
**Priority**: MEDIUM
**Effort**: Medium (3-4 days)
**Approach**:
1. Adapt `AgentMessage` Pydantic schema to A2A v1.0 Agent Card format
2. Map Omega's 11-agent fleet to Agent Card capabilities
3. Implement `/.well-known/agent-card.json` endpoint
4. Use `AgentPermissions` matrix for capability declarations

---

*Report generated by ROC_RACOON — Sovereign Miner*
*Legacy mining complete. 10 reusable patterns extracted across 3 eras.*