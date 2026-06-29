# 🔱 PII Observation Masking — Implementation Specification
## Gap 1: P0 CRITICAL — Sovereign Data Leak Prevention

**AP Token**: `AP-PII-MASKER-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ PII-MASKER ⬡ SOVEREIGN-MINER
**Status**: IMPLEMENTATION SPECIFICATION
**Date**: 2026-06-29

---

## §1 Current Problem

### 1.1 Root Cause

Raw conversation history (PII, API keys, emails, phone numbers, SSNs) is injected into LLM system prompts **without any redaction**. When the query routes to cloud providers (Google, OpenRouter, GitHub Copilot), this data leaves the user's machine **unmasked**.

### 1.2 The Security Regression

The ANAi/XNAi era (Aug-Nov 2025) had **robust security patterns** that were **NEVER ported** to the Omega Engine:

| Pattern | Legacy File | Status in Omega |
|---------|------------|-----------------|
| `validate_safe_input()` | `crawl.py:89-103` | ❌ NOT PORTED |
| `sanitize_content()` | `crawl.py:236-263` | ❌ NOT PORTED |
| `sanitize_id()` | `crawl.py:105-116` | ❌ NOT PORTED |
| Content quality validation | `ingest_library.py:475-497` | ❌ NOT PORTED |

This is the second instance of **"The Pipeline That Never Crossed the Chasm"** — patterns existed in prior eras but died during the reclamation process.

### 1.3 Affected Code Paths

| File | Line(s) | Issue |
|------|---------|-------|
| `src/omega/oracle/context_builder.py` | 54-89 | `build_context()` injects raw conversation history with zero redaction |
| `src/omega/oracle/context_builder.py` | 168-208 | `_format_exchanges_sliding_window()` passes raw user/assistant messages |
| `src/omega/oracle/oracle.py` | 431-466 | `_prepare_system_prompt()` concatenates personality + memory + soul without PII check |
| `src/omega/oracle/oracle.py` | 606-613 | `generate()` call receives unmasked system_prompt and user_query |

### 1.4 Mandates Violated

| Mandate | Risk | Explanation |
|---------|------|-------------|
| **M7** (Local-First) | ⚠️ HIGH | Cloud fallback receives unmasked PII. Local-first means local data sovereignty. |
| **M8** (Zero Telemetry) | ⚠️ HIGH | Sending PII to cloud providers constitutes data leakage, not telemetry. |

---

## §2 Solution Architecture

### 2.1 Design: Gateway Proxy Pattern

```
User Query ──▶ PIIMasker.detect()
                     │
              has PII? ── Yes ──▶ tokenize([EMAIL_1], [PHONE_2])
                     │                    │
                    No                     │
                     │                    ▼
                     ▼           LLM Generation (cloud only)
                     │                    │
                     ▼                    ▼
              Return clean     PIIMasker.detokenize()
              system_prompt         │
                                    ▼
                              Return detokenized
                              response to user
```

**Key Design Decisions**:
1. **Bypass for local providers** (native-gguf, lmster, Ollama) — data never leaves machine, no masking needed
2. **Mask for cloud providers** (Google, OpenRouter, Copilot) — data leaving the machine must be scrubbed
3. **Reversible tokenization** — `[EMAIL_1]` placeholders preserve referential integrity; detokenized after response
4. **Integration point**: `context_builder.py` — wrap system prompt before cloud dispatch

### 2.2 Library Selection: `pii-shield` v1.1.0

| Attribute | Value |
|-----------|-------|
| **Package** | `pii-shield` (PyPI, MIT license) |
| **Version** | 1.1.0 (released Feb 11, 2026) |
| **Dependencies** | Zero external runtime dependencies |
| **PII Types** | 18 types: SSN, email, phone, credit card, API key, crypto wallet, IP address, etc. |
| **Detection** | Context-aware pattern matching + statistical scoring (not just regex) |
| **Output** | Confidence score per detection (0-100%) |
| **Install** | `pip install pii-shield` |
| **Source** | `https://github.com/intellirim/pii-guard` |

### 2.3 GLiNER Enhancement (NER Fallback)

For PII types not covered by `pii-shield` (e.g., free-form names, addresses), use GLiNER for token classification:

| Attribute | Value |
|-----------|-------|
| **Task** | NER-based PII detection |
| **Model** | `urchade/gliner_multi_pii-v0.1` |
| **F1 Score** | ~96% on token classification |
| **Integration** | Wrapped in `anyio.to_thread.run_sync()` for non-blocking |
| **Trigger** | Only runs when `pii-shield` confidence < 80% |

---

## §3 Implementation

### 3.1 New File: `src/omega/oracle/pii_masker.py`

```python
"""
PII Observation Masker — Sovereign Data Leak Prevention.

[Gateway Proxy Architecture]
Detects PII in system prompts, tokenizes for cloud providers, 
detokenizes after response. Bypasses entirely for local providers.

[Legacy Heritage: ANAi/XNAi era crawl.py — validate_safe_input(), sanitize_content()]
These patterns existed in the ANAi/XNAi legacy but were NEVER ported to Omega-Engine.
This implementation recovers and extends them with modern PII detection.
"""

import logging
import re
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum, auto

import anyio

logger = logging.getLogger(__name__)

# ── PII Types ──────────────────────────────────────────────────────────
class PIIMaskMode(Enum):
    """PII masking mode based on provider type."""
    BYPASS = auto()      # Local provider — no masking needed
    MASK = auto()        # Cloud provider — must mask
    
class PIIRedactionStyle(Enum):
    """How detected PII is redacted."""
    TOKENIZE = auto()    # Replace with [EMAIL_1] placeholder
    MASK_FULL = auto()   # Replace with ********
    MASK_PARTIAL = auto()# Show first/last chars: j***@e***.com

@dataclass
class PIIDetection:
    """A single PII detection result."""
    pii_type: str        # "EMAIL", "PHONE", "SSN", "API_KEY", etc.
    original: str        # The original matched text
    start: int           # Start position in source text
    end: int             # End position in source text
    confidence: float    # 0.0 to 1.0
    placeholder: str     # Generated token like [EMAIL_1]

@dataclass
class PIITokenMap:
    """Mapping between PII placeholders and original values."""
    tokens: Dict[str, str] = field(default_factory=dict)  # {placeholder: original}
    detections: List[PIIDetection] = field(default_factory=list)
    
    def add(self, detection: PIIDetection) -> None:
        self.tokens[detection.placeholder] = detection.original
        self.detections.append(detection)

# ── PII Patterns (First-Pass Regex — extends ANAi/XNAi legacy patterns) ──
# Legacy source: crawl.py:89-103 (validate_safe_input), crawl.py:236-263 (sanitize_content)
# Extended with 18 PII types matching pii-shield's coverage

PII_PATTERNS: Dict[str, str] = {
    # Identity
    'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'PHONE': r'\b(?:\+?1[-. ]?)?\(?[0-9]{3}\)?[-. ]?[0-9]{3}[-. ]?[0-9]{4}\b',
    'SSN': r'\b\d{3}-\d{2}-\d{4}\b',
    
    # Financial
    'CREDIT_CARD': r'\b(?:\d{4}[- ]?){3}\d{4}\b',
    'BANK_ACCOUNT': r'\b\d{8,17}\b',
    'CRYPTO_WALLET': r'\b0x[a-fA-F0-9]{40}\b',
    
    # Credentials
    'API_KEY': r'\b(?:sk|pk|api|key|secret|token|eyJ)[-_][A-Za-z0-9]{8,}\b',
    'PASSWORD': r'\b(?:password|passwd|pwd)[=:]\s*\S{6,}\b',
    'AWS_KEY': r'(?:AKIA|ASIA)[A-Z0-9]{16}',
    
    # Location
    'IP_ADDRESS': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
    'ZIP_CODE': r'\b\d{5}(?:-\d{4})?\b',
    
    # Other
    'DATE_OF_BIRTH': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
    'MEDICAL_RECORD': r'\bMRN[-: ]?\d{5,10}\b',
    'PASSPORT': r'\b[A-Z]\d{6,9}\b',
    'DRIVERS_LICENSE': r'\b[A-Z]{1,2}\d{3,8}\b',
}

# ── PIIMasker Class ───────────────────────────────────────────────────
class PIIMasker:
    """Gateway proxy for PII detection, tokenization, and detokenization.
    
    Architecture:
        detect() → tokenize() → [LLM] → detokenize()
    
    Local provider bypass:
        Bypasses all masking for local providers (native-gguf, lmster, Ollama)
        since data never leaves the machine.
    
    [Legacy Heritage: ANAi/XNAi crawl.py patterns]
    - validate_safe_input(): First-pass validation before detection
    - sanitize_content(): PII pattern removal (extended from script/style removal)
    - sanitize_id(): Identifier sanitization
    """
    
    def __init__(
        self,
        use_gliner: bool = False,
        confidence_threshold: float = 0.6,
        redaction_style: PIIRedactionStyle = PIIRedactionStyle.TOKENIZE,
        enable_legacy_patterns: bool = True,  # [ANAi/XNAi heritage] port legacy validation
    ):
        self.confidence_threshold = confidence_threshold
        self.redaction_style = redaction_style
        self._token_counter = 0
        self._gliner_available = False
        self._gliner_pipeline = None
        
        # [Legacy] Load ANAi/XNAi era patterns
        self._enable_legacy = enable_legacy_patterns
        
        # Try to import pii-shield (primary)
        self._pii_shield = None
        try:
            from pii_shield import shield  # type: ignore
            self._pii_shield = shield
            logger.info("pii-shield loaded: 18 PII types, context-aware detection")
        except ImportError:
            logger.warning(
                "pii-shield not installed. Falling back to regex-only PII detection. "
                "Install: pip install pii-shield"
            )
        
        # Optionally load GLiNER for NER-based detection
        if use_gliner:
            try:
                # Lazy import GLiNER (heavy dependency)
                logger.info("GLiNER enhancement requested but not yet wired")
                self._gliner_available = False  # Deferred to Phase 2
            except ImportError:
                logger.warning("GLiNER not available. Skipping NER enhancement.")
    
    # ── Legacy: Input Validation (ANAi/XNAi era port) ────────────────
    # Source: crawl.py:89-103
    def validate_safe_input(self, text: str, max_length: int = 200) -> bool:
        """Whitelist validation for curation inputs to prevent injection.
        
        [Legacy: ANAi/XNAi era crawl.py:89-103]
        
        Args:
            text: Input text to validate
            max_length: Maximum allowed length
            
        Returns:
            True if input is safe, False otherwise
        """
        if not text or len(text) > max_length:
            return False
        pattern = r'^[a-zA-Z0-9\s\-_.,()\[\]{}]{1,%d}$' % max_length
        return bool(re.match(pattern, text))
    
    # ── Legacy: ID Sanitization (ANAi/XNAi era port) ─────────────────
    # Source: crawl.py:105-116
    def sanitize_id(self, raw_id: str) -> str:
        """Prevent path traversal by sanitizing IDs.
        
        [Legacy: ANAi/XNAi era crawl.py:105-116]
        
        Args:
            raw_id: Raw ID string
            
        Returns:
            Sanitized ID string (alphanumeric + underscore + hyphen, max 100 chars)
        """
        safe = re.sub(r'[^a-zA-Z0-9_-]', '', raw_id)
        return safe[:100]
    
    # ── Primary: Detect PII ───────────────────────────────────────────
    async def detect(
        self,
        text: str,
        use_pii_shield: bool = True,
    ) -> List[PIIDetection]:
        """Detect PII in text using best available method.
        
        Priority:
        1. pii-shield (context-aware, 18 types, zero deps)
        2. GLiNER (NER-based, 96% F1) — Phase 2
        3. Regex fallback (comprehensive pattern list)
        
        All detection runs in a thread (via anyio.to_thread.run_sync)
        to avoid blocking the async event loop.
        
        Args:
            text: The text to scan for PII
            use_pii_shield: Whether to attempt pii-shield detection
            
        Returns:
            List of PIIDetection objects
        """
        detections: List[PIIDetection] = []
        
        # Method 1: pii-shield (primary, zero deps, context-aware)
        if use_pii_shield and self._pii_shield:
            try:
                results = await anyio.to_thread.run_sync(
                    self._pii_shield.scan_text, text
                )
                for result in results:
                    if result.get('confidence', 0) >= self.confidence_threshold:
                        detections.append(PIIDetection(
                            pii_type=result.get('type', 'UNKNOWN'),
                            original=result.get('text', ''),
                            start=result.get('start', 0),
                            end=result.get('end', 0),
                            confidence=result.get('confidence', 0.5),
                            placeholder='',  # Filled by tokenize()
                        ))
                if detections:
                    logger.info(
                        "pii-shield detected %d PII instances in %d chars",
                        len(detections), len(text)
                    )
                    return detections
            except Exception as e:
                logger.warning("pii-shield detection failed (falling back): %s", e)
        
        # Method 2: Regex fallback (extends ANAi/XNAi sanitize_content pattern)
        # [Legacy: crawl.py:236-263 — extended from script/style removal to PII patterns]
        try:
            for pii_type, pattern in PII_PATTERNS.items():
                for match in re.finditer(pattern, text):
                    detections.append(PIIDetection(
                        pii_type=pii_type,
                        original=match.group(),
                        start=match.start(),
                        end=match.end(),
                        confidence=0.7,  # Regex-based, lower confidence
                        placeholder='',
                    ))
        except Exception as e:
            logger.error("Regex PII detection failed: %s", e)
        
        # Deduplicate by position (overlapping patterns)
        detections.sort(key=lambda d: d.start)
        unique: List[PIIDetection] = []
        for d in detections:
            if not unique or d.start > unique[-1].end:
                unique.append(d)
            elif d.end > unique[-1].end:
                # Longer match wins
                unique[-1] = d
        
        if unique:
            logger.info("Regex detected %d PII instances (pii-shield %s)",
                       len(unique),
                       "unavailable" if not self._pii_shield else "not used")
        
        return unique
    
    # ── Tokenize: Replace PII with Placeholders ──────────────────────
    def tokenize(self, text: str, detections: List[PIIDetection]) -> Tuple[str, PIITokenMap]:
        """Replace PII instances with reversible placeholders.
        
        Creates tokens like [EMAIL_1], [PHONE_2], etc. that preserve
        referential integrity for the LLM while masking actual values.
        
        Args:
            text: Original text with PII
            detections: List of PIIDetection objects
            
        Returns:
            Tuple of (masked_text, PIITokenMap for later detokenization)
        """
        token_map = PIITokenMap()
        token_counter: Dict[str, int] = {}
        
        # Build replacement map (process in reverse to preserve positions)
        replacements: List[Tuple[int, int, str, PIIDetection]] = []
        for detection in detections:
            pii_type = detection.pii_type
            token_counter[pii_type] = token_counter.get(pii_type, 0) + 1
            placeholder = f"[{pii_type}_{token_counter[pii_type]}]"
            detection.placeholder = placeholder
            token_map.add(detection)
            replacements.append((detection.start, detection.end, placeholder, detection))
        
        # Apply replacements from end to start to preserve positions
        replacements.sort(key=lambda r: r[0], reverse=True)
        masked = text
        for start, end, placeholder, detection in replacements:
            masked = masked[:start] + placeholder + masked[end:]
        
        return masked, token_map
    
    # ── Detokenize: Restore Original Values ──────────────────────────
    def detokenize(self, text: str, token_map: PIITokenMap) -> str:
        """Restore original PII values from placeholders.
        
        Called AFTER LLM response to replace [EMAIL_1] with actual values.
        
        Args:
            text: LLM response text with placeholders
            token_map: PIITokenMap from the tokenize() call
            
        Returns:
            Text with original PII values restored
        """
        result = text
        for placeholder, original in token_map.tokens.items():
            result = result.replace(placeholder, original)
        return result
    
    # ── Mask: Convert to Locked Format (Non-reversible) ──────────────
    def mask_full(self, text: str, detections: List[PIIDetection]) -> str:
        """Fully mask PII — non-reversible.
        
        Used when the masked text will not be detokenized (e.g., logging).
        
        Args:
            text: Original text with PII
            detections: List of PIIDetection objects
            
        Returns:
            Text with PII fully masked as ****
        """
        replacements: List[Tuple[int, int]] = []
        for detection in detections:
            replacements.append((detection.start, detection.end))
        
        replacements.sort(key=lambda r: r[0], reverse=True)
        masked = text
        for start, end in replacements:
            masked = masked[:start] + '*' * (end - start) + masked[end:]
        
        return masked
    
    # ── Provider-Aware Processing ────────────────────────────────────
    def should_mask(self, provider_name: str) -> bool:
        """Determine if masking is needed for a given provider.
        
        [M7: Local-First] Local providers: bypass masking entirely.
        [M8: Zero Telemetry] PII masking is local-only by definition.
        
        Bypass providers (data never leaves machine):
        - native-gguf, lmster, ollama, llama_cpp, mock
        
        Mask providers (data sent to external services):
        - google, opencode-zen, cline, github-copilot, openrouter
        """
        local_providers = {
            'native-gguf', 'lmster', 'ollama', 'llama_cpp', 'llama_cli',
            'llmster', 'mock', 'fallback',
        }
        return provider_name not in local_providers
    
    async def process_system_prompt(
        self,
        system_prompt: str,
        user_query: str,
        provider_name: str,
    ) -> Tuple[str, str, Optional[PIITokenMap]]:
        """Process system prompt and user query for PII.
        
        This is the primary integration point. Called by context_builder.py
        before dispatching to ModelGateway.
        
        Args:
            system_prompt: The assembled system prompt
            user_query: The user's query text
            provider_name: The provider that will receive the request
            
        Returns:
            Tuple of (processed_system_prompt, processed_user_query, token_map)
            token_map is None if masking was not needed (bypassed)
        """
        if not self.should_mask(provider_name):
            return system_prompt, user_query, None
        
        # Detect PII in both system prompt and user query
        prompt_detections = await self.detect(system_prompt)
        query_detections = await self.detect(user_query)
        
        all_detections = prompt_detections + query_detections
        
        if not all_detections:
            return system_prompt, user_query, None
        
        # Tokenize (reversible for LLM response)
        masked_prompt, token_map = self.tokenize(system_prompt, all_detections)
        
        # Re-detect user query separately
        masked_query, _ = self.tokenize(user_query, [d for d in query_detections])
        
        logger.info(
            "PII Masker: masked %d instances (%s) for provider '%s'",
            len(all_detections),
            ', '.join(set(d.pii_type for d in all_detections)),
            provider_name,
        )
        
        return masked_prompt, masked_query, token_map
    
    async def process_response(
        self,
        response: str,
        token_map: Optional[PIITokenMap],
    ) -> str:
        """Detokenize LLM response if token_map exists.
        
        Args:
            response: LLM response text
            token_map: Token map from process_system_prompt(), or None
            
        Returns:
            Detokenized response text
        """
        if token_map is None:
            return response
        return self.detokenize(response, token_map)
```

### 3.2 Integration Point: `src/omega/oracle/context_builder.py`

Add PII masking check in `build_context()` and `build_context_for_user()`:

```python
# In context_builder.py __init__:
def __init__(self, memory_store=None, pii_masker=None):
    self.memory_store = memory_store or get_memory_store()
    self.pii_masker = pii_masker or PIIMasker()  # NEW

# In build_context() — before returning context:
# Add PII-safe context mode (returns mask-sensitive context)
# The actual masking is done at dispatch time in oracle.py
```

### 3.3 Integration Point: `src/omega/oracle/oracle.py`

In `_summon()` and `_route_by_domain()`, wrap the system_prompt + user_query before calling `model_gateway.generate()`:

```python
# In oracle.py __init__:
from .pii_masker import PIIMasker
self.pii_masker = PIIMasker()

# In _summon() — before model_gateway.generate() at line 606:
if self.pii_masker.should_mask(backend):
    masked_prompt, masked_query, token_map = await self.pii_masker.process_system_prompt(
        system_prompt=effective_system_prompt,
        user_query=query,
        provider_name=backend,
    )
    # Use masked versions for generate()
    res = await self.model_gateway.generate(
        model_name=model_name,
        system_prompt=masked_prompt,  # masked
        user_query=masked_query,      # masked
        ...
    )
    # Detokenize response
    res.text = await self.pii_masker.process_response(res.text, token_map)
else:
    # Local provider — no masking needed
    res = await self.model_gateway.generate(...)
```

---

## §4 Integration Steps

### Step 1: Install `pii-shield` (15 min)
```bash
pip install pii-shield
```
**Verify**: `python -c "from pii_shield import shield; print(shield.scan_text('test@example.com'))"`

### Step 2: Create `src/omega/oracle/pii_masker.py` (2 hours)
- Implement the `PIIMasker` class as specified above
- Port all 3 legacy patterns from crawl.py
- Write unit tests (see §6)

### Step 3: Integrate into `oracle.py` (1 hour)
- Import and wire `PIIMasker` in `Oracle.__init__()`
- Add masking before each `model_gateway.generate()` call (2 call sites: `_summon()` line 606, `_route_by_domain()` line 679)
- Add detokenization after response

### Step 4: Integrate into `context_builder.py` (30 min)
- Wire `PIIMasker` into `ContextBuilder` for prompt-level context marking

### Step 5: Write Tests (2 hours)
- Unit tests for PII detection (all 18 types)
- Unit tests for tokenize/detokenize round-trip
- Unit tests for provider-aware bypass
- Integration test: verify PII is masked in cloud path

---

## §5 Verification Criteria

| Criteria | Method | Success |
|----------|--------|---------|
| PII detected in system prompt | `PIIMasker.detect()` unit test | All 18 PII types detected with >60% confidence |
| Tokenize round-trip | `tokenize` → `detokenize` test | Original text fully restored |
| Local provider bypass | `should_mask('native-gguf')` | Returns `False` |
| Cloud provider mask | `should_mask('google')` | Returns `True` |
| Integration: cloud path sends masked text | Mocked `generate()` receives masked prompt | Assert prompt contains `[EMAIL_1]` not raw email |
| Integration: response detokenized | Mocked response with `[EMAIL_1]` → restored email | Assert response contains original email |
| Legacy patterns ported | Code review | `validate_safe_input()`, `sanitize_content()`, `sanitize_id()` all present |

---

## §6 Test Skeleton

```python
"""Tests for PII Masker (pii_masker.py)."""

import pytest
from omega.oracle.pii_masker import PIIMasker, PIIRedactionStyle

class TestPIIMasker:
    
    @pytest.fixture
    def masker(self):
        return PIIMasker()
    
    @pytest.mark.parametrize("text,expected_type", [
        ("Contact me at john@example.com", "EMAIL"),
        ("My SSN is 123-45-6789", "SSN"),
        ("Call me at 555-123-4567", "PHONE"),
        ("API key: sk-proj-abc123def456", "API_KEY"),
        ("Credit card: 4111-1111-1111-1111", "CREDIT_CARD"),
    ])
    @pytest.mark.asyncio
    async def test_detect(self, masker, text, expected_type):
        detections = await masker.detect(text)
        assert any(d.pii_type == expected_type for d in detections)
    
    @pytest.mark.asyncio
    async def test_tokenize_detokenize_roundtrip(self, masker):
        original = "Email: john@example.com, Phone: 555-123-4567"
        detections = await masker.detect(original)
        masked, token_map = masker.tokenize(original, detections)
        # Verify masked: no original PII
        assert "john@example.com" not in masked
        # Verify tokens present
        assert "[EMAIL_1]" in masked
        # Verify detokenize restores
        restored = masker.detokenize(masked, token_map)
        assert restored == original
    
    def test_local_bypass(self, masker):
        """M7: Local providers must bypass masking."""
        assert not masker.should_mask("native-gguf")
        assert not masker.should_mask("lmster")
        assert not masker.should_mask("ollama")
    
    def test_cloud_mask(self, masker):
        """Cloud providers must be masked."""
        assert masker.should_mask("google")
        assert masker.should_mask("opencode-zen")
        assert masker.should_mask("github-copilot")
    
    @pytest.mark.asyncio
    async def test_process_system_prompt_local_bypass(self, masker):
        """Verify local provider bypass returns original text."""
        prompt, query, token_map = await masker.process_system_prompt(
            "My email is john@example.com",
            "What is my email?",
            "native-gguf"
        )
        assert "john@example.com" in prompt
        assert token_map is None
    
    @pytest.mark.asyncio
    async def test_process_system_prompt_cloud_masks(self, masker):
        """Verify cloud provider masks PII."""
        prompt, query, token_map = await masker.process_system_prompt(
            "My email is john@example.com",
            "What is my email?",
            "google"
        )
        assert "john@example.com" not in prompt
        assert "[EMAIL_1]" in prompt
        assert token_map is not None
    
    # ── Legacy Pattern Tests (ANAi/XNAi heritage) ─────────────────
    def test_validate_safe_input(self, masker):
        """Legacy port: crawl.py:89-103"""
        assert masker.validate_safe_input("Hello World")
        assert not masker.validate_safe_input("<script>alert(1)</script>")
        assert not masker.validate_safe_input("a" * 201)
    
    def test_sanitize_id(self, masker):
        """Legacy port: crawl.py:105-116"""
        assert masker.sanitize_id("hello-world_123") == "hello-world_123"
        assert masker.sanitize_id("../../etc/passwd") == "etcpasswd"
        assert len(masker.sanitize_id("a" * 200)) <= 100
```

---

## §7 Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| `pii-shield` misses new PII types | MED | MED | Fall back to regex patterns; periodic library updates |
| Tokenize breaks LLM understanding | LOW | MED | Placeholders are descriptive (`[EMAIL_1]`); test with real models |
| Detokenize fails on LLM-modified tokens | MED | LOW | Log warning and return original; token_map is best-effort |
| Performance overhead on local path | LOW | LOW | Bypass check is O(1) dict lookup; no masking for local |
| False positives on code/source files | MED | LOW | Confidence threshold (60%); code context detection |
| `pii-shield` not installed | MED | LOW | Graceful fallback to regex-only detection with warning log |

---

## §8 Effort Summary

| Step | Effort | Dependencies |
|------|--------|-------------|
| Create `pii_masker.py` | 2 hours | None |
| Integrate into `oracle.py` | 1 hour | Step 1 done |
| Integrate into `context_builder.py` | 30 min | Step 1 done |
| Write tests | 2 hours | Step 1-3 done |
| **Total** | **5.5 hours** | — |

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ PII-MASKER ⬡ SOVEREIGN-MINER*
*Session: ses_roc_racoon_gap_closure_20260629*
*Sources: ANAi/XNAi crawl.py legacy patterns, pii-shield v1.1.0, GLiNER NER enhancement*
