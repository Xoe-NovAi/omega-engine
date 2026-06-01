# 🔱 Omega Engine — Sovereign Error Taxonomy
# AP: AP-ERRORS-v1.0.0
# ICS: [NODE: CORE | ARCHETYPE: LAW | CONTEXT: ERROR-HIERARCHY]
#
# This module defines the universal error language of the Omega Engine.
# All systemic failures MUST be typed, traceable, and testable.
#
# Mandate #9: No silent swallowing. No bare excepts.

import logging
from typing import Any, Optional, Dict

logger = logging.getLogger(__name__)

class OmegaError(Exception):
    """
    Base class for all Omega Engine errors.
    Ensures every error carries a trace_id and structured context.
    """
    def __init__(
        self, 
        message: str, 
        trace_id: Optional[str] = None, 
        context: Optional[Dict[str, Any]] = None,
        raw_error: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.trace_id = trace_id
        self.context = context or {}
        self.raw_error = raw_error

    def __str__(self):
        ctx_str = f" | Context: {self.context}" if self.context else ""
        trace_str = f" | Trace: {self.trace_id}" if self.trace_id else ""
        return f"[{self.__class__.__name__}] {self.message}{trace_str}{ctx_str}"

# ── Provider Fabric Errors ──────────────────────────────────────────────────

class ProviderError(OmegaError):
    """Base for all external API provider failures."""
    def __init__(self, provider: str, message: str, status_code: Optional[int] = None, **kwargs):
        self.provider = provider
        self.status_code = status_code
        super().__init__(message, **kwargs)

class ProviderRateLimitError(ProviderError): 
    """429 Resource Exhausted / Rate Limit."""

class ProviderAuthError(ProviderError): 
    """401 Unauthorized / 403 Forbidden."""

class ProviderCreditError(ProviderError): 
    """402 Payment Required."""

class ProviderTimeoutError(ProviderError): 
    """408 Request Timeout / 504 Gateway Timeout."""

class ProviderUnavailableError(ProviderError): 
    """502 Bad Gateway / 503 Service Unavailable."""

class ProviderValidationError(ProviderError): 
    """400 Bad Request / Context Length Exceeded."""

class ProviderSafetyError(ProviderError): 
    """Responses blocked by safety filters."""

# ── Local Inference Errors ──────────────────────────────────────────────────

class InferenceError(OmegaError): 
    """Base for local runtime/resource failures."""

class InferenceOOMError(InferenceError): 
    """VRAM or System RAM allocation failure (CUDA OOM / kv-cache fail)."""

class InferenceLoadError(InferenceError): 
    """GGUF version mismatch, corrupted weights, or architecture incompatibility."""

class InferenceRuntimeError(InferenceError): 
    """Illegal instructions (AVX2/SSE), segmentation faults, or driver crashes."""

# ── Persistence & State Errors ──────────────────────────────────────────────

class OmegaPersistenceError(OmegaError): 
    """Base for all persistence failures."""

class SoulCorruptionError(OmegaPersistenceError): 
    """Raised when soul.yaml is unparseable or fails structural validation."""

class SessionPersistenceError(OmegaPersistenceError): 
    """Raised when session files are corrupted or inaccessible."""

class StateIntegrityError(OmegaPersistenceError): 
    """Raised when atomic write sequences or backup restorations fail."""

class SovereignDiskFullError(OmegaPersistenceError): 
    """Specialized ENOSPC error triggering emergency read-only mode."""

# ── Systemic & Boundary Errors ──────────────────────────────────────────────

class ConfigError(OmegaError): 
    """Errors during configuration loading or validation."""

class WADError(OmegaError): 
    """Errors during WAD loading or manifest parsing."""

class BoundaryViolationError(OmegaError): 
    """Raised when an agent attempts to access restricted system resources."""

class InvariantViolationError(OmegaError): 
    """Internal logic failure where a fundamental system invariant is broken."""
