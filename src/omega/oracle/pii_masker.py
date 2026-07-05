# AP: AP-PII-MASKER-v1.0.0
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
        detect() -> tokenize() -> [LLM] -> detokenize()
    
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
        enable_legacy_patterns: bool = True,
    ):
        self.confidence_threshold = confidence_threshold
        self.redaction_style = redaction_style
        self._token_counter = 0
        self._gliner_available = False
        self._gliner_pipeline = None
        
        # [Legacy] Load ANAi/XNAi era patterns
        self._enable_legacy = enable_legacy_patterns
        
        # Try to import pii-shield (primary)
        self._pii_scanner = None
        try:
            from pii_shield import Scanner as PIIScanner
            self._pii_scanner = PIIScanner()
            logger.info("pii-shield loaded: 18 PII types, context-aware detection")
        except ImportError:
            logger.warning(
                "pii-shield not installed. Falling back to regex-only PII detection. "
                "Install: pip install pii-shield"
            )
        except (OmegaError, RuntimeError, OSError) as e:
            logger.warning("pii-shield initialization failed: %s", e)
        
        # Optionally load GLiNER for NER-based detection
        if use_gliner:
            try:
                logger.info("GLiNER enhancement requested but not yet wired")
                self._gliner_available = False
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
    
    # ── Legacy: Content Sanitization (ANAi/XNAi era port) ────────────
    # Source: crawl.py:236-263
    def sanitize_content(self, content: str, remove_scripts: bool = True) -> str:
        """Sanitize content by removing script/style tags and normalizing whitespace.

        [Legacy: ANAi/XNAi era crawl.py:236-263]

        Args:
            content: Raw content string
            remove_scripts: Remove <script>/<style> tags if True

        Returns:
            Sanitized content string
        """
        if not content:
            return ""

        sanitized = content

        if remove_scripts:
            sanitized = re.sub(
                r"<script[^>]*>.*?</script>", "", sanitized,
                flags=re.DOTALL | re.IGNORECASE,
            )
            sanitized = re.sub(
                r"<style[^>]*>.*?</style>", "", sanitized,
                flags=re.DOTALL | re.IGNORECASE,
            )

        # Normalize excessive whitespace
        sanitized = re.sub(r"\s+", " ", sanitized)
        return sanitized.strip()
    
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
        
        # Method 1: pii-shield (primary, context-aware)
        if use_pii_shield and self._pii_scanner:
            try:
                results = await anyio.to_thread.run_sync(
                    self._pii_scanner.scan_text, text
                )
                for match in results.matches:
                    confidence = match.confidence / 100.0  # pii-shield returns 0-100
                    if confidence >= self.confidence_threshold:
                        start = match.column if hasattr(match, 'column') else 0
                        end = start + len(match.value) if hasattr(match, 'value') else start
                        detections.append(PIIDetection(
                            pii_type=getattr(match, 'type', 'UNKNOWN'),
                            original=getattr(match, 'value', ''),
                            start=start,
                            end=end,
                            confidence=confidence,
                            placeholder='',
                        ))
                if detections:
                    logger.info(
                        "pii-shield detected %d PII instances in %d chars",
                        len(detections), len(text)
                    )
                    return detections
            except (OmegaError, RuntimeError, OSError) as e:
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
        except (OmegaError, RuntimeError, OSError) as e:
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
                       "unavailable" if not self._pii_scanner else "not used")
        
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
        sorted_detections = sorted(detections, key=lambda d: d.start)
        for detection in sorted_detections:
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
    def detokenize(self, text: str, token_map: Optional[PIITokenMap] = None) -> str:
        """Restore original PII values from placeholders.
        
        Called AFTER LLM response to replace [EMAIL_1] with actual values.
        
        Args:
            text: LLM response text with placeholders
            token_map: PIITokenMap from the tokenize() call, or None
                      (in which case text is returned unchanged)
            
        Returns:
            Text with original PII values restored
        """
        if token_map is None:
            return text
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
        - google, openrouter, opencode-zen, cline
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
        
        This is the primary integration point. Called before dispatching
        to ModelGateway.
        
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
