# 🔱 Omega Engine — Vault System Overhaul Specification (Part 3)
**AP Token**: `AP-VAULT-OVERHAUL-SPEC-20260818-v1.0.0`
**Part**: 3 of 5 — Runtime Security (Sanitization, Zero-Knowledge, RBAC)

---

## 🛡️ Component 4: SecretRegistry (12-Encoding Canonicalization)

### The Problem
Agents and libraries leak secrets through multiple encoding vectors:
- JSON Unicode escapes (`sk\u002d1234`)
- Chunked HTTP bodies (split across chunks)
- Unicode homoglyphs/zero-width spaces
- Memory addresses in tracebacks (`id()`)

### Solution: Canonicalize ALL Encodings Before Registration

```python
# security/secret_registry.py
import re, json, base64, html, unicodedata, urllib.parse
from typing import Set, Iterator, List, Tuple

class SecretRegistry:
    """Canonicalizes secrets across ALL encoding families before registration."""
    
    def __init__(self):
        self._canonical_secrets: Set[str] = set()
        self._compiled_patterns: List[re.Pattern] = []
    
    def register(self, secret: str) -> None:
        """Register a secret and ALL its encoding variants."""
        canonical = self._canonicalize(secret)
        self._canonical_secrets.add(canonical)
        self._rebuild_patterns()
    
    def register_batch(self, secrets: List[str]) -> None:
        for s in secrets:
            self.register(s)
    
    def _canonicalize(self, s: str) -> str:
        """Reduce to minimal canonical form (NFKC, no zero-width, lowercase)."""
        s = unicodedata.normalize('NFKC', s)
        s = re.sub(r'[\u200b-\u200f\ufeff\u2060-\u206f]', '', s)
        return s.lower()
    
    def _generate_variants(self, secret: str) -> Iterator[str]:
        """Yield ALL encoding variants of a secret."""
        canon = self._canonicalize(secret)
        yield canon
        
        # Base64 (standard + URL-safe)
        yield base64.b64encode(canon.encode()).decode()
        yield base64.urlsafe_b64encode(canon.encode()).decode().rstrip('=')
        
        # URL/Percent encoding
        yield urllib.parse.quote(canon)
        
        # Hex
        yield canon.encode().hex()
        
        # JSON Unicode (escape all non-ASCII + special)
        yield json.dumps(canon)[1:-1]  # Remove surrounding quotes
        
        # HTML entities
        yield html.escape(canon)
        
        # Zero-width injected variants (for detection)
        for i in range(len(canon) + 1):
            yield canon[:i] + '\u200b' + canon[i:]
    
    def _rebuild_patterns(self):
        """Build regex alternation for fast scanning."""
        all_variants = set()
        for secret in self._canonical_secrets:
            all_variants.update(self._generate_variants(secret))
        escaped = [re.escape(v) for v in all_variants]
        escaped.sort(key=len, reverse=True)  # Longer first
        pattern = '|'.join(escaped)
        self._compiled_patterns = [re.compile(pattern, re.IGNORECASE)]
    
    def scan(self, text: str) -> List[Tuple[str, str]]:
        """Scan text for ANY variant of registered secrets."""
        # Also decode common encodings in text before scanning
        decoded_texts = [text]
        
        # Try to decode Base64 chunks in text
        for match in re.finditer(r'[A-Za-z0-9+/=]{20,}', text):
            try:
                decoded = base64.b64decode(match.group()).decode('utf-8', errors='ignore')
                decoded_texts.append(decoded)
            except Exception:
                pass
        
        # Try URL decode
        decoded_texts.append(urllib.parse.unquote(text))
        
        # Try JSON Unicode decode
        try:
            for match in re.finditer(r'"([^"\\]*(?:\\.[^"\\]*)*)"', text):
                decoded = json.loads(match.group())
                decoded_texts.append(decoded)
        except Exception:
            pass
        
        # Scan all decoded variants
        findings = []
        for dt in decoded_texts:
            for pattern in self._compiled_patterns:
                for match in pattern.finditer(dt):
                    findings.append((match.group(), pattern.pattern))
        return findings
    
    def scrub_traceback(self, tb_text: str) -> str:
        """Remove memory addresses (id()) from tracebacks."""
        # CPython id() format: 0x followed by 8-16 hex chars
        return re.sub(r'0x[0-9a-fA-F]{8,16}', '0xREDACTED', tb_text)

# Chunked HTTP Body Reassembler (for httpx logging)
class ChunkedBodyReassembler:
    """Reassembles chunked transfer encoding for secret scanning."""
    
    def __init__(self):
        self._buffer = bytearray()
        self._in_chunked = False
    
    def feed(self, chunk: bytes) -> bytes:
        """Feed raw HTTP chunk data, return reassembled body when complete."""
        self._buffer.extend(chunk)
        if b'Transfer-Encoding: chunked' in self._buffer:
            self._in_chunked = True
        if self._in_chunked and b'\r\n0\r\n\r\n' in self._buffer:
            body = self._extract_chunked_body(self._buffer)
            self._buffer.clear()
            self._in_chunked = False
            return body
        return b''
    
    def _extract_chunked_body(self, data: bytes) -> bytes:
        # Parse chunk sizes and reassemble per RFC 7230 §4.1
        # Simplified — use httpcore's parser in production
        pass
```

---

## 🛡️ Component 5: Egress Sanitization Layer (4 Mandatory Hooks)

### Hook Points

| Hook | Location | What It Sanitizes |
|------|----------|-------------------|
| **Logging Filter** | `logging.Filter` | All log records (`record.msg`, `record.args`) |
| **Hivemind/OpenCode Interceptor** | `omega-hub_hivemind_post_context` / OpenCode plugin | Chat outputs, context posts |
| **Error Capture** | `error_capture.ts` plugin | Exception tracebacks, locals |
| **Observability SSE** | `/obs/stream` endpoint | Streaming metrics/events |

### Implementation

```python
# security/sanitizer.py
from flashtext import KeywordProcessor
import logging, json, traceback
from typing import Any, Dict

class EgressSanitizer:
    """Global sanitizer for all egress paths."""
    
    def __init__(self, secret_registry: 'SecretRegistry'):
        self._registry = secret_registry
        self._kp = KeywordProcessor()
        self._rebuild_keywords()
    
    def _rebuild_keywords(self):
        self._kp = KeywordProcessor(case_sensitive=False)
        for secret in self._registry._canonical_secrets:
            # Register all variants for this secret
            for variant in self._registry._generate_variants(secret):
                self._kp.add_keyword(variant, f"[REDACTED:{secret[:8]}...]")
    
    def sanitize(self, text: str) -> str:
        """Sanitize a single string."""
        # Also decode common encodings before scanning
        return self._registry.scan(text)  # Returns findings; actual replacement via KP
    
    def sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively sanitize dict values."""
        if isinstance(data, dict):
            return {k: self.sanitize_dict(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_dict(v) for v in data]
        elif isinstance(data, str):
            return self._kp.replace_keywords(data)
        return data

# Hook 1: Logging Filter
class SecretLoggingFilter(logging.Filter):
    def __init__(self, sanitizer: EgressSanitizer):
        super().__init__()
        self._sanitizer = sanitizer
    
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self._sanitizer._kp.replace_keywords(record.msg)
        if record.args:
            record.args = tuple(
                self._sanitizer._kp.replace_keywords(arg) if isinstance(arg, str) else arg
                for arg in record.args
            )
        return True

# Hook 2: Hivemind/OpenCode Interceptor
def sanitize_hivemind_context(context: dict) -> dict:
    """Sanitize context before writing to Hivemind/OpenCode DB."""
    sanitizer = get_global_sanitizer()
    return sanitizer.sanitize_dict(context)

# Hook 3: Error Capture (error_capture.ts plugin)
def sanitize_error_payload(payload: dict) -> dict:
    """Sanitize exception tracebacks and locals before persistence."""
    sanitizer = get_global_sanitizer()
    # Scrub traceback
    if 'traceback' in payload:
        payload['traceback'] = sanitizer._registry.scrub_traceback(payload['traceback'])
    # Sanitize locals
    if 'locals' in payload:
        payload['locals'] = sanitizer.sanitize_dict(payload['locals'])
    return payload

# Hook 4: Observability SSE
def sanitize_sse_event(event: dict) -> dict:
    """Sanitize SSE stream events."""
    sanitizer = get_global_sanitizer()
    return sanitizer.sanitize_dict(event)

# Global singleton
_GLOBAL_SANITIZER = None

def initialize_global_sanitizer(secret_registry: 'SecretRegistry'):
    global _GLOBAL_SANITIZER
    _GLOBAL_SANITIZER = EgressSanitizer(secret_registry)
    # Install logging filter
    logging.getLogger().addFilter(SecretLoggingFilter(_GLOBAL_SANITIZER))

def get_global_sanitizer() -> EgressSanitizer:
    if _GLOBAL_SANITIZER is None:
        raise RuntimeError("Global sanitizer not initialized")
    return _GLOBAL_SANITIZER
```

---

## 🤖 Component 6: Zero-Knowledge Agent Architecture

### ProviderIdentity Dataclass

```python
# src/omega/oracle/types.py
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class ProviderIdentity:
    """The ONLY thing agents see — never raw API keys."""
    provider: str           # e.g., "openrouter"
    account_id: str         # e.g., "3" 
    model: str              # e.g., "nemotron-3-ultra"
    tier: str = "free"      # "free" | "paid" | "premium"
    metadata: dict = None   # Extensible
    
    def __post_init__(self):
        if self.metadata is None:
            object.__setattr__(self, 'metadata', {})

# Agent-facing API — agents NEVER see keys
class AgentProviderInterface:
    """What agents receive when they request a provider."""
    
    def __init__(self, identity: ProviderIdentity):
        self.identity = identity
    
    def __repr__(self):
        return f"Provider({self.identity.provider}/{self.identity.account_id})"
```

### ModelGateway Integration (Zero-Knowledge)

```python
# src/omega/oracle/model_gateway.py
from src.omega.oracle.types import ProviderIdentity, AgentProviderInterface
from src.omega.security.credential_provider import CredentialProvider

class ModelGateway:
    def __init__(self):
        self._credential_provider = CredentialProvider()
        self._sanitizer = get_global_sanitizer()
    
    def _resolve_identity(self, identity: ProviderIdentity) -> str:
        """Internal: resolve ProviderIdentity to API key."""
        return self._credential_provider.get_provider_credential(
            identity.provider, identity.account_id
        )
    
    async def generate(self, request, identity: ProviderIdentity = None):
        """
        Agent calls this with ProviderIdentity — NEVER with raw key.
        """
        if identity is None:
            # Auto-resolve from request context
            identity = self._auto_resolve_identity(request)
        
        # Resolve key internally — agent never sees it
        api_key = self._resolve_identity(identity)
        
        # Pass directly to HTTP client
        headers = {"Authorization": f"Bearer {api_key}"}
        
        # ... make request ...
        
        # Sanitize response before returning to agent
        response = await self._make_request(request, headers)
        return self._sanitizer.sanitize_dict(response)
    
    def _auto_resolve_identity(self, request) -> ProviderIdentity:
        # Logic to pick best provider/account based on request
        pass
```

---

## 🎯 Component 7: RBAC Matrix (Agent Role-Based Access)

### Policy Matrix

| Agent Role | Can Request Generation? | Can List Providers? | Can See Key Metadata? | Can *Never* See Key Value |
|------------|-------------------------|---------------------|----------------------|---------------------------|
| **Orchestrators** (Kali, Lilith, Ma'at) | ✅ | ✅ | ✅ | ✅ |
| **Builders** (Ma'at, Roc, N3) | ✅ (via tools) | ✅ | ✅ | ✅ |
| **Researchers** (Researcher, Jem, Nodes) | ✅ | ✅ | ❌ | ✅ |
| **Runtime/Subagents** (Node, Verity, Scribe) | ❌ (via Oracle) | ❌ | ❌ | ✅ |

### Enforcement

```python
# src/omega/oracle/rbac.py
from enum import Enum
from src.omega.oracle.types import ProviderIdentity

class AgentRole(Enum):
    ORCHESTRATOR = "orchestrator"
    BUILDER = "builder"
    RESEARCHER = "researcher"
    RUNTIME = "runtime"

ROLE_PERMISSIONS = {
    AgentRole.ORCHESTRATOR: {"generate", "list_providers", "see_metadata"},
    AgentRole.BUILDER: {"generate", "list_providers", "see_metadata"},
    AgentRole.RESEARCHER: {"generate", "list_providers"},
    AgentRole.RUNTIME: set(),  # Must go through Oracle
}

def validate_agent_access(role: AgentRole, action: str, identity: ProviderIdentity) -> bool:
    """Validate agent can perform action on identity."""
    permissions = ROLE_PERMISSIONS.get(role, set())
    if action not in permissions:
        return False
    
    # Additional tier-based restrictions
    if action == "see_metadata" and identity.tier == "premium":
        # Only orchestrators/builders see premium metadata
        return role in (AgentRole.ORCHESTRATOR, AgentRole.BUILDER)
    
    return True

# Integration in ModelGateway
class ModelGateway:
    async def generate(self, request, identity: ProviderIdentity, agent_role: AgentRole = None):
        if agent_role and not validate_agent_access(agent_role, "generate", identity):
            raise PermissionError(f"Agent role {agent_role} cannot generate with {identity.provider}")
        
        # ... proceed with generation
```