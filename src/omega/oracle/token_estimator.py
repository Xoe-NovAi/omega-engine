# AP: AP-ORACLE-TOKEN-ESTIMATOR-v1.0.0
# 🔱 Oracle Token Estimator — Accurate Token Counting for LLM Routing
# Provides precise token estimation using tiktoken with model-specific encoders
# and safety margins to prevent quota exceeded errors

"""
Token Estimator for Oracle Provider Fabric

Estimates token counts for prompts and responses using tiktoken with
model-specific encoders and configurable safety margins to prevent
quota exceeded errors during LLM routing decisions.

Features:
- Model-specific tiktoken encoders (cl100k_base for GPT-4, p50k_base for GPT-3, etc.)
- Fallback to o200k_base for Llama 3 and similar models
- 15% safety margin for Llama family variance (code/CJK divergence)
- LRU caching of encoder instances for performance
- Support for estimating both prompt and completion tokens
"""

from __future__ import annotations

import functools
import logging
from typing import Dict, Optional

try:
    import tiktoken
except ImportError:
    tiktoken = None  # type: ignore

logger = logging.getLogger("omega.token_estimator")


class TokenEstimatorError(RuntimeError):
    """Raised when token estimation fails."""
    pass


class TokenEstimator:
    """
    Estimates token counts for text using appropriate tiktoken encoders.
    
    Provides model-specific token estimation with safety margins to
    prevent quota exceeded errors during LLM routing.
    
    Supported model families:
    - OpenAI GPT-4 family: cl100k_base encoder
    - OpenAI GPT-3.5 family: cl100k_base encoder  
    - Llama family: o200k_base encoder + 15% safety margin
    - Mistral/Mixtral: cl100k_base encoder
    - Claude family: cl100k_base encoder (approximation)
    - Google Gemini: cl100k_base encoder (approximation)
    - Unknown models: o200k_base encoder + 20% safety margin
    """

    # Model to encoder mapping
    _ENCODER_MAP = {
        # OpenAI models
        "gpt-4": "cl100k_base",
        "gpt-4-turbo": "cl100k_base",
        "gpt-4-vision": "cl100k_base",
        "gpt-3.5-turbo": "cl100k_base",
        "gpt-3.5-turbo-16k": "cl100k_base",
        "text-davinci-003": "p50k_base",
        "text-davinci-002": "p50k_base",
        "davinci": "p50k_base",
        
        # Anthropic Claude (approximation)
        "claude-3": "cl100k_base",
        "claude-2": "cl100k_base",
        "claude-instant": "cl100k_base",
        
        # Google Gemini (approximation)
        "gemini": "cl100k_base",
        "gemini-pro": "cl100k_base",
        
        # Mistral/Mixtral (approximation)
        "mixtral": "cl100k_base",
        "mistral": "cl100k_base",
    }

    # Safety margins by model family (percentage to add to estimated count)
    _SAFETY_MARGINS = {
        "llama": 15,      # Llama family: +15% for code/CJK variance
        "codellama": 15,  # CodeLlama: +15% 
        "deepseek": 15,   # DeepSeek: +15%
        "phi": 10,        # Phi: +10%
        "gemma": 10,      # Gemma: +10%
        "default": 20,    # Unknown models: +20% safety margin
    }

    def __init__(self, default_safety_margin: int = 20):
        """
        Initialize the token estimator.
        
        Args:
            default_safety_margin: Default percentage to add to token estimates
                                 for unknown models (default: 20%)
        """
        if tiktoken is None:
            raise TokenEstimatorError(
                "tiktoken is not installed. Install with: pip install tiktoken>=0.7.0"
            )
        
        self._default_safety_margin = default_safety_margin
        self._encoder_cache: dict[str, tiktoken.Encoding] = {}
        self._log = logger

    def _get_encoder_for_model(self, model_name: str) -> tiktoken.Encoding:
        """
        Get the appropriate tiktoken encoder for a model.
        
        Uses LRU caching to avoid recreating encoders.
        """
        model_lower = model_name.lower()
        
        # Check for known model prefixes
        encoder_name = None
        for prefix, enc in self._ENCODER_MAP.items():
            if model_lower.startswith(prefix):
                encoder_name = enc
                break
        
        # Default to o200k_base for unknown models (Llama 3, etc.)
        if encoder_name is None:
            encoder_name = "o200k_base"
        
        # Get or create encoder from cache
        if encoder_name not in self._encoder_cache:
            try:
                self._encoder_cache[encoder_name] = tiktoken.get_encoding(encoder_name)
                self._log.debug(f"Loaded tiktoken encoder: {encoder_name}")
            except Exception as e:
                self._log.warning(f"Failed to load encoder {encoder_name}: {e}")
                # Fallback to cl100k_base
                if encoder_name != "cl100k_base":
                    self._encoder_cache[encoder_name] = tiktoken.get_encoding("cl100k_base")
                else:
                    raise TokenEstimatorError(f"Could not load any tokenizer encoder: {e}")
        
        return self._encoder_cache[encoder_name]

    def _get_safety_margin(self, model_name: str) -> int:
        """
        Get the safety margin percentage for a model.
        
        Returns the percentage to add to estimated token count to prevent
        quota exceeded errors.
        """
        model_lower = model_name.lower()
        
        # Check for known model families
        for family, margin in self._SAFETY_MARGINS.items():
            if model_lower.startswith(family):
                return margin
        
        return self._default_safety_margin

    def estimate_tokens(self, text: str, model_name: str = "unknown") -> int:
        """
        Estimate the number of tokens in a text string.
        
        Args:
            text: The text to tokenize
            model_name: The model name for encoder selection
            
        Returns:
            Estimated token count including safety margin
            
        Raises:
            TokenEstimatorError: If tokenization fails
        """
        if not text:
            return 0
        
        try:
            encoder = self._get_encoder_for_model(model_name)
            token_count = len(encoder.encode(text))
            
            # Apply safety margin
            safety_margin = self._get_safety_margin(model_name)
            if safety_margin > 0:
                token_count = int(token_count * (1 + safety_margin / 100))
            
            self._log.debug(
                f"Estimated {token_count} tokens for model {model_name} "
                f"(base: {len(encoder.encode(text))}, +{safety_margin}% margin)"
            )
            return token_count
            
        except Exception as e:
            self._log.error(f"Failed to estimate tokens for model {model_name}: {e}")
            raise TokenEstimatorError(f"Token estimation failed: {e}") from e

    def estimate_prompt_tokens(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        model_name: str = "unknown"
    ) -> int:
        """
        Estimate tokens for a complete prompt (system + user).
        
        Args:
            system_prompt: The system prompt
            user_prompt: The user prompt
            model_name: The model name for encoder selection
            
        Returns:
            Estimated token count for the combined prompt
        """
        # Combine prompts with typical chat formatting
        combined = f"{system_prompt}\n\n{user_prompt}" if system_prompt else user_prompt
        return self.estimate_tokens(combined, model_name)

    def estimate_completion_tokens(
        self, 
        prompt_tokens: int, 
        model_name: str = "unknown",
        max_output_tokens: Optional[int] = None
    ) -> int:
        """
        Estimate tokens for a completion based on prompt length and model characteristics.
        
        Args:
            prompt_tokens: Number of tokens in the prompt
            model_name: The model name
            max_output_tokens: Maximum tokens to generate (if known)
            
        Returns:
            Estimated completion token count
        """
        # Heuristic: completion is typically 10-50% of prompt length
        # but capped by max_output_tokens if specified
        base_estimate = int(prompt_tokens * 0.2)  # 20% of prompt length
        
        if max_output_tokens is not None:
            base_estimate = min(base_estimate, max_output_tokens)
        
        # Apply safety margin
        safety_margin = self._get_safety_margin(model_name)
        if safety_margin > 0:
            base_estimate = int(base_estimate * (1 + safety_margin / 100))
        
        return max(1, base_estimate)  # At least 1 token

    def clear_cache(self) -> None:
        """Clear the encoder cache."""
        self._encoder_cache.clear()
        self._log.debug("Token estimator cache cleared")


# Global token estimator instance
_token_estimator: Optional[TokenEstimator] = None


def get_token_estimator() -> TokenEstimator:
    """Get or create the global token estimator instance."""
    global _token_estimator
    if _token_estimator is None:
        _token_estimator = TokenEstimator()
    return _token_estimator