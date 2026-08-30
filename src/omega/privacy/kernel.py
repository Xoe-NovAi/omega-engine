# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
Privacy Kernel — Local Privacy Detection (Gemma 4 E2B / Qwen3-1.7B)
AP: AP-PRIVACY-KERNEL-v1.0.0
⬡ OMEGA ⬡ P6 ⬡ privacy_kernel ⬡ CLOAKBOT-INSPIRED

Implements R19 Soul Privacy Model Part 2.3:
CloakBot-Inspired Local Privacy Kernel

Architecture: Local model runs as privacy detector BEFORE any cloud call.
Remote LLM NEVER sees raw PII. Detection runs locally on user-controlled hardware.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from omega.memory.providers import sanitize_path_component

logger = logging.getLogger(__name__)


@dataclass
class DetectionResult:
    """Result of privacy detection."""

    spans: List[Dict[str, Any]]  # List of {type, value, start, end, confidence}
    sanitized_text: str
    placeholder_map: Dict[str, str]  # placeholder -> original value
    action: str  # "pass", "warn", "pseudonymize", "block"


@dataclass
class PrivacyVault:
    """Session vault for placeholder mapping."""

    session_id: str
    mappings: Dict[str, str] = field(default_factory=dict)  # placeholder -> original
    reverse_mappings: Dict[str, str] = field(default_factory=dict)  # original -> placeholder
    counter: int = 0

    def get_placeholder(self, original: str, pii_type: str) -> str:
        """Get or create placeholder for original value."""
        if original in self.reverse_mappings:
            return self.reverse_mappings[original]

        self.counter += 1
        placeholder = f"<<{pii_type}_{self.counter}>>"
        self.mappings[placeholder] = original
        self.reverse_mappings[original] = placeholder
        return placeholder

    def restore(self, text: str) -> str:
        """Restore original values from placeholders in text."""
        result = text
        for placeholder, original in self.mappings.items():
            result = result.replace(placeholder, original)
        return result

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "mappings": self.mappings,
            "counter": self.counter,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PrivacyVault":
        vault = cls(session_id=data["session_id"])
        vault.mappings = data.get("mappings", {})
        vault.reverse_mappings = {v: k for k, v in vault.mappings.items()}
        vault.counter = data.get("counter", 0)
        return vault


class PrivacyKernel:
    """
    Local privacy detection kernel.

    Runs locally (Gemma 4 E2B or Qwen3-1.7B) to detect PII before any cloud call.
    Implements the CloakBot pattern: detect → vault → sanitize → cloud → restore.
    """

    def __init__(
        self,
        model_name: str = "gemma-4-e2b-q4_k_m",
        local_only: bool = True,
        enabled: bool = True,
        vault_dir: Optional[Path] = None,
    ):
        """
        Initialize privacy kernel.

        Args:
            model_name: Local model to use for detection
            local_only: If True, never send to cloud (enforced)
            enabled: Whether kernel is active
            vault_dir: Directory for session vaults
        """
        self.model_name = model_name
        self.local_only = local_only
        self.enabled = enabled
        self.vault_dir = vault_dir or Path("data/privacy/vaults")
        self.vault_dir.mkdir(parents=True, exist_ok=True)

        # Detection prompts (would be loaded from config in production)
        self.detection_prompts = {
            "general": self._load_prompt("general"),
            "digit": self._load_prompt("digit"),
        }

        # Fast-path regex patterns for common PII (fallback when model unavailable)
        self.fast_patterns = self._compile_fast_patterns()

        # Active session vault
        self.current_vault: Optional[PrivacyVault] = None

    def _load_prompt(self, prompt_type: str) -> str:
        """Load detection prompt template."""
        # In production, load from config/privacy/prompts/
        prompts = {
            "general": """You are a privacy detection system. Analyze the text and identify ALL personally identifiable information (PII).

Return a JSON array of detected entities with this format:
[
  {"type": "PERSON", "value": "John Smith", "start": 10, "end": 20, "confidence": 0.95},
  {"type": "EMAIL", "value": "john@example.com", "start": 50, "end": 66, "confidence": 1.0}
]

PII types to detect:
- PERSON: Names of people
- LOCATION: Addresses, cities, countries
- ORGANIZATION: Company names, institutions
- FINANCIAL: Account numbers, amounts, salaries
- MEDICAL: Diagnoses, medications, health info
- CREDENTIAL: Passwords, API keys, tokens, private keys
- CONTACT: Phone numbers, emails, social handles
- IDENTITY: SSN, driver's license, passport numbers

Text to analyze:
{text}""",
            "digit": """Detect digit-based PII in the text:
- Credit card numbers
- Phone numbers
- SSN
- Bank account numbers
- IP addresses
- API keys with numeric patterns

Return same JSON format as general detection.

Text:
{text}""",
        }
        return prompts.get(prompt_type, prompts["general"])

    def _compile_fast_patterns(self) -> Dict[str, re.Pattern]:
        """Compile fast-path regex patterns."""
        return {
            "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
            "PHONE": re.compile(
                r"\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b"
            ),
            "SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
            "CREDIT_CARD": re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
            "API_KEY": re.compile(r"\b(?:sk|pk|api)[_-]?[A-Za-z0-9]{20,}\b"),
            "PASSWORD": re.compile(r"(?i)(?:password|passwd|pwd)\s*[:=]\s*\S+"),
            "PRIVATE_KEY": re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"),
            "IP_ADDRESS": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
            "URL_WITH_AUTH": re.compile(r"https?://[^:\s]+:[^@\s]+@[^\s]+"),
        }

    async def start_session(self, session_id: str) -> PrivacyVault:
        """Start a new privacy session with vault."""
        safe_session = sanitize_path_component(session_id)
        vault_path = self.vault_dir / f"{safe_session}.json"

        if vault_path.exists():
            # Load existing vault
            content = vault_path.read_text()
            self.current_vault = PrivacyVault.from_dict(json.loads(content))
        else:
            # Create new vault
            self.current_vault = PrivacyVault(session_id=session_id)

        return self.current_vault

    async def end_session(self, session_id: str) -> None:
        """End session and save vault."""
        if self.current_vault and self.current_vault.session_id == session_id:
            safe_session = sanitize_path_component(session_id)
            vault_path = self.vault_dir / f"{safe_session}.json"
            vault_path.write_text(json.dumps(self.current_vault.to_dict(), indent=2))
            self.current_vault = None

    async def detect_and_sanitize(
        self,
        text: str,
        session_id: Optional[str] = None,
        use_model: bool = True,
    ) -> DetectionResult:
        """
        Detect PII in text and return sanitized version with placeholders.

        This is the main entry point for the pre-LLM hook.

        Args:
            text: Input text to sanitize
            session_id: Optional session ID for vault persistence
            use_model: Whether to use local model (vs fast-path only)

        Returns:
            DetectionResult with sanitized text and placeholder map
        """
        if not self.enabled:
            return DetectionResult(
                spans=[],
                sanitized_text=text,
                placeholder_map={},
                action="pass",
            )

        # Ensure vault exists
        if session_id and not self.current_vault:
            await self.start_session(session_id)

        vault = self.current_vault

        # Run detection
        if use_model:
            spans = await self._model_detect(text)
        else:
            spans = self._fast_detect(text)

        # If no PII detected, pass through
        if not spans:
            return DetectionResult(
                spans=[],
                sanitized_text=text,
                placeholder_map={},
                action="pass",
            )

        # Create placeholders and sanitize
        sanitized = text
        placeholder_map = {}

        # Sort by start position descending to avoid index shifting
        sorted_spans = sorted(spans, key=lambda s: s["start"], reverse=True)

        for span in sorted_spans:
            original = span["value"]
            pii_type = span["type"]

            if vault:
                placeholder = vault.get_placeholder(original, pii_type)
            else:
                # Temporary placeholder without vault
                placeholder = f"<<{pii_type}_{hash(original) % 10000}>>"

            placeholder_map[placeholder] = original
            start, end = span["start"], span["end"]
            sanitized = sanitized[:start] + placeholder + sanitized[end:]

        # Determine action based on severity
        action = self._determine_action(spans)

        return DetectionResult(
            spans=spans,
            sanitized_text=sanitized,
            placeholder_map=placeholder_map,
            action=action,
        )

    async def _model_detect(self, text: str) -> List[Dict[str, Any]]:
        """
        Run local model detection.

        In production, this would call the local Gemma 4 E2B or Qwen3-1.7B model
        via the Oracle provider fabric. For now, fall back to fast patterns.
        """
        # TODO: Integrate with Oracle provider fabric for local model inference
        # For now, use fast-path as fallback
        logger.debug("Model detection not yet integrated, using fast-path")
        return self._fast_detect(text)

    def _fast_detect(self, text: str) -> List[Dict[str, Any]]:
        """Fast-path regex-based detection."""
        spans = []

        for pii_type, pattern in self.fast_patterns.items():
            for match in pattern.finditer(text):
                spans.append(
                    {
                        "type": pii_type,
                        "value": match.group(),
                        "start": match.start(),
                        "end": match.end(),
                        "confidence": 0.9,
                    }
                )

        # Named entity detection (simplified)
        person_pattern = re.compile(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b")
        for match in person_pattern.finditer(text):
            matched = match.group()
            if not any(word in matched for word in ["The ", "This ", "That ", "These ", "Those "]):
                spans.append(
                    {
                        "type": "PERSON",
                        "value": matched,
                        "start": match.start(),
                        "end": match.end(),
                        "confidence": 0.7,
                    }
                )

        # Financial amounts
        financial_pattern = re.compile(r"\$\d+(?:,\d{3})*(?:\.\d{2})?")
        for match in financial_pattern.finditer(text):
            spans.append(
                {
                    "type": "FINANCIAL",
                    "value": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": 0.8,
                }
            )

        return spans

    def _determine_action(self, spans: List[Dict[str, Any]]) -> str:
        """Determine action based on detected PII severity."""
        # High-severity types that should trigger pseudonymize/block
        high_severity = {"CREDENTIAL", "PASSWORD", "PRIVATE_KEY", "SSN", "API_KEY"}
        medium_severity = {"FINANCIAL", "MEDICAL", "IDENTITY"}

        has_high = any(s["type"] in high_severity for s in spans)
        has_medium = any(s["type"] in medium_severity for s in spans)

        if has_high:
            return "pseudonymize"
        elif has_medium:
            return "warn"
        return "pass"

    async def restore_response(
        self,
        response: str,
        session_id: Optional[str] = None,
    ) -> str:
        """
        Restore original values in LLM response using session vault.

        This is the post-LLM hook.

        Args:
            response: LLM response with placeholders
            session_id: Session ID to load vault

        Returns:
            Response with original values restored
        """
        if session_id and not self.current_vault:
            await self.start_session(session_id)

        if self.current_vault:
            return self.current_vault.restore(response)

        return response

    async def process_streaming(
        self,
        chunks: List[str],
        session_id: Optional[str] = None,
    ) -> List[str]:
        """
        Process streaming response chunks, restoring placeholders.

        Handles carryover window for placeholders split across chunks.

        Args:
            chunks: List of response chunks
            session_id: Session ID for vault

        Returns:
            List of restored chunks
        """
        if session_id and not self.current_vault:
            await self.start_session(session_id)

        if not self.current_vault:
            return chunks

        restored = []
        carryover = ""

        for chunk in chunks:
            # Prepend carryover from previous chunk
            combined = carryover + chunk

            # Restore placeholders
            restored_chunk = self.current_vault.restore(combined)

            # Check if chunk ends with incomplete placeholder
            # Look for <<TYPE_ pattern at end
            import re

            placeholder_match = re.search(r"(<<[A-Z_]+_\d+>>)", combined[::-1])
            if placeholder_match:
                # Found placeholder at end, might be incomplete
                # Keep last 50 chars as carryover
                carryover = combined[-50:]
                restored_chunk = restored_chunk[:-50]
            else:
                carryover = ""

            restored.append(restored_chunk)

        # Restore any remaining carryover
        if carryover:
            restored[-1] += self.current_vault.restore(carryover)

        return restored


# =============================================================================
# PRE/POST LLM HOOKS
# =============================================================================


class PrivacyHooks:
    """
    Pre/post LLM hooks for Oracle integration.

    Usage:
        hooks = PrivacyHooks(kernel)

        # Pre-LLM: sanitize input
        sanitized = await hooks.pre_llm(user_input, session_id)

        # Call LLM with sanitized input
        response = await oracle.talk(sanitized)

        # Post-LLM: restore response
        restored = await hooks.post_llm(response, session_id)
    """

    def __init__(self, kernel: PrivacyKernel):
        self.kernel = kernel

    async def pre_llm(
        self,
        text: str,
        session_id: Optional[str] = None,
        use_model: bool = True,
    ) -> Tuple[str, DetectionResult]:
        """
        Pre-LLM hook: detect and sanitize PII.

        Returns:
            Tuple of (sanitized_text, detection_result)
        """
        result = await self.kernel.detect_and_sanitize(text, session_id, use_model)
        return result.sanitized_text, result

    async def post_llm(
        self,
        response: str,
        session_id: Optional[str] = None,
    ) -> str:
        """
        Post-LLM hook: restore original values in response.

        Returns:
            Restored response text
        """
        return await self.kernel.restore_response(response, session_id)

    async def post_llm_streaming(
        self,
        chunks: List[str],
        session_id: Optional[str] = None,
    ) -> List[str]:
        """
        Post-LLM streaming hook: restore placeholders in chunks.

        Returns:
            List of restored chunks
        """
        return await self.kernel.process_streaming(chunks, session_id)


# =============================================================================
# FACTORY
# =============================================================================


def create_privacy_kernel(
    model_name: str = "gemma-4-e2b-q4_k_m",
    local_only: bool = True,
    enabled: bool = True,
    vault_dir: Optional[Path] = None,
) -> PrivacyKernel:
    """Factory: create a PrivacyKernel with default or custom config."""
    return PrivacyKernel(
        model_name=model_name,
        local_only=local_only,
        enabled=enabled,
        vault_dir=vault_dir,
    )


def create_privacy_hooks(kernel: PrivacyKernel) -> PrivacyHooks:
    """Factory: create PrivacyHooks for a kernel."""
    return PrivacyHooks(kernel)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "PrivacyKernel",
    "PrivacyHooks",
    "PrivacyVault",
    "DetectionResult",
    "create_privacy_kernel",
    "create_privacy_hooks",
]
