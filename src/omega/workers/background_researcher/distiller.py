# 🔱 Omega Engine — Jem 3-Tier Research Distiller (Phase 1)
# AP: AP-BACKGROUND-RESEARCHER-DISTILLER-v2.0.0
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ jem ⬡ distiller ⬡ PHASE-1
#
# The 3-tier cognitive pipeline:
#   Tier 1: Qwen3-4B-Thinking (lmster local) — fast speculative draft
#   Tier 2: MiniMax M2.5 (OpenRouter primary) — enrich & deepen T1 draft
#   Tier 3: Gemini 2.5 Pro (Gemini CLI headless) — review & queue follow-ups
#
# Each tier has independent circuit breaker. No tier masks another's failure.
# Every cycle produces a training triple (T1, T2, T3) → synthetic dataset.

import json
import logging
import os
import re
import subprocess
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import anyio
import httpx

from .models import GnosisPacket

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════
# §1 Circuit Breaker — Per-Provider, Asymmetric, Non-Masking
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class CircuitBreakerState:
    """State for a single provider's circuit breaker."""
    consecutive_failures: int = 0
    total_failures: int = 0
    total_successes: int = 0
    last_failure_time: float = 0.0
    last_success_time: float = 0.0
    skip_until: float = 0.0  # timestamp — skip calls until this time
    degraded: bool = False   # True when in skip window
    critical: bool = False   # True when threshold exceeded
    last_error: str = ""
    # Asymmetric thresholds: (skip_after_n_failures, critical_after_n_failures)
    skip_threshold: int = 3
    critical_threshold: int = 10

    @property
    def is_skipping(self) -> bool:
        """Whether the circuit breaker is currently skipping calls."""
        if not self.degraded:
            return False
        if time.time() < self.skip_until:
            return True
        # Skip window expired — reset
        self.degraded = False
        self.consecutive_failures = 0
        return False

    def record_success(self) -> None:
        """Record a successful call. Resets consecutive failures."""
        self.consecutive_failures = 0
        self.total_successes += 1
        self.last_success_time = time.time()
        self.degraded = False
        self.critical = False

    def record_failure(self, error: str = "") -> str:
        """Record a failure and return the severity level.
        
        Returns: 'ok' | 'skip' | 'critical'
        """
        self.consecutive_failures += 1
        self.total_failures += 1
        self.last_failure_time = time.time()
        self.last_error = error

        if self.consecutive_failures >= self.critical_threshold:
            self.critical = True
            self.degraded = True
            self.skip_until = time.time() + 3600  # 60 min skip
            return "critical"

        if self.consecutive_failures >= self.skip_threshold:
            self.degraded = True
            self.skip_until = time.time() + 900   # 15 min skip
            return "skip"

        return "ok"

    def to_dict(self) -> dict:
        return asdict(self)


class JemCircuitBreaker:
    """Manages circuit breaker state for all Jem providers.

    Providers tracked:
      - lmster (T1 local)
      - minimax_openrouter (T2 primary)
      - minimax_zen (T2 fallback)
      - gemma_google (T2 fallback)
      - gemini_cli (T3)
    """

    _instance = None  # Singleton — shared across the engine

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.providers: dict[str, CircuitBreakerState] = {
            "lmster": CircuitBreakerState(
                skip_threshold=3, critical_threshold=10,
            ),
            "minimax_openrouter": CircuitBreakerState(
                skip_threshold=3, critical_threshold=10,
            ),
            "minimax_zen": CircuitBreakerState(
                skip_threshold=3, critical_threshold=10,
            ),
            "gemma_google": CircuitBreakerState(
                skip_threshold=3, critical_threshold=10,
            ),
            "gemini_cli": CircuitBreakerState(
                skip_threshold=2, critical_threshold=5,
            ),
        }

    def can_call(self, provider: str) -> bool:
        """Check if a provider is available (not skipping)."""
        state = self.providers.get(provider)
        if not state:
            return True
        return not state.is_skipping

    def record_success(self, provider: str) -> None:
        """Record a success for a provider."""
        state = self.providers.get(provider)
        if state:
            state.record_success()

    def record_failure(self, provider: str, error: str = "") -> str:
        """Record a failure. Returns severity: 'ok' | 'skip' | 'critical'."""
        state = self.providers.get(provider)
        if not state:
            return "ok"
        return state.record_failure(error)

    def get_reports(self) -> dict[str, dict]:
        """Return all provider states for observability."""
        return {k: v.to_dict() for k, v in self.providers.items()}


# ══════════════════════════════════════════════════════════════════════════
# §2 Quality Gate — T1 → T2 Validation
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class QualityGateResult:
    """Result of validating a Tier 1 output."""
    passed: bool = True
    reason: str = ""
    token_count: int = 0
    has_l1: bool = False
    has_l2: bool = False
    has_l3: bool = False
    valid_json: bool = False


def validate_t1_output(text: str) -> QualityGateResult:
    """Validate Tier 1 speculative draft before sending to Tier 2.

    Rules:
    - Must be ≥100 tokens (approx word count)
    - Must contain L1/L2/L3 structure
    - Must be valid JSON or contain extractable JSON
    """
    result = QualityGateResult()

    if not text or not text.strip():
        result.passed = False
        result.reason = "Empty response"
        return result

    # Token count (approximate: words)
    tokens = len(text.split())
    result.token_count = tokens

    if tokens < 50:
        result.passed = False
        result.reason = f"Too short: {tokens} tokens (minimum 50)"
        return result

    # Check for L1/L2/L3 structure in JSON or text
    text_lower = text.lower()
    result.has_l1 = bool(re.search(r'"[^"]*l1[^"]*"', text) or 'l1 (narrative)' in text_lower)
    result.has_l2 = bool(re.search(r'"[^"]*l2[^"]*"', text) or 'l2 (insight)' in text_lower)
    result.has_l3 = bool(re.search(r'"[^"]*l3[^"]*"', text) or 'l3 (universal principle)' in text_lower)

    # Check if we can extract JSON
    try:
        _extract_json(text)
        result.valid_json = True
    except (json.JSONDecodeError, ValueError):
        result.valid_json = False

    # For very short texts, require JSON structure
    if tokens < 100 and not result.valid_json:
        result.passed = False
        result.reason = f"Short ({tokens} tokens) and not valid JSON"
        return result

    result.passed = True
    result.reason = f"Passed ({tokens} tokens, json={result.valid_json})"
    return result


# ══════════════════════════════════════════════════════════════════════════
# §3 Tier 1 Backend — Lmster (Local Qwen3-4B-Thinking)
# ══════════════════════════════════════════════════════════════════════════

class LmsterBackend:
    """Calls Qwen3-4B-Thinking via lmster HTTP API on :1234.

    This is purely local — no API key, no network required once model is loaded.
    Produces fast speculative drafts (~5-10s for short prompts).
    """

    def __init__(self, endpoint: str = "http://127.0.0.1:1234"):
        self.endpoint = endpoint
        self.model = "qwen/qwen3-4b-thinking-2507"
        self.circuit = JemCircuitBreaker()
        self.timeout = 120.0  # lmster is CPU-bound, give it time

    async def call(
        self,
        prompt: str,
        system_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> str:
        """Call Qwen3-4B-Thinking via lmster. Returns raw response text."""
        # Check circuit breaker
        if not self.circuit.can_call("lmster"):
            logger.warning("lmster circuit breaker open — skipping T1")
            raise CircuitBreakerOpen("lmster is in skip window")

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    f"{self.endpoint}/v1/chat/completions",
                    json=payload,
                )
                if resp.status_code == 404:
                    # Model not loaded — try loading first
                    logger.warning("lmster model not loaded (404) — need lms load")
                    raise CircuitBreakerError("lmster model not loaded")
                resp.raise_for_status()
                data = resp.json()
                choices = data.get("choices", [])
                if choices:
                    msg = choices[0].get("message", {})
                    content = msg.get("content", "")
                    reasoning = msg.get("reasoning_content", "")
                    # Combine reasoning + content for the draft
                    if reasoning:
                        full = f"{reasoning}\n\n{content}" if content else reasoning
                    else:
                        full = content
                    self.circuit.record_success("lmster")
                    return full

                self.circuit.record_failure("lmster", "No choices in response")
                return ""

        except httpx.TimeoutException:
            self.circuit.record_failure("lmster", "timeout")
            raise CircuitBreakerError("lmster timeout")
        except httpx.HTTPStatusError as e:
            self.circuit.record_failure("lmster", f"HTTP {e.response.status_code}")
            raise CircuitBreakerError(f"lmster HTTP {e.response.status_code}")
        except Exception as e:
            self.circuit.record_failure("lmster", str(e))
            raise CircuitBreakerError(f"lmster call failed: {e}")


# ══════════════════════════════════════════════════════════════════════════
# §4 Tier 2 Backend — MiniMax M2.5 (OpenRouter → Zen → Gemma)
# ══════════════════════════════════════════════════════════════════════════

class MiniMaxBackend:
    """Calls MiniMax M2.5 via OpenRouter primary, OpenCode Zen fallback,
    then Gemma 4-31B as tertiary fallback.

    The call method takes an optional T1 draft to enrich — if provided,
    the draft becomes the starting point for the enrichment.
    """

    def __init__(self):
        self.circuit = JemCircuitBreaker()
        self.timeout = 90.0

        # OpenRouter config
        self.or_api_key = os.getenv("OPENROUTER_API_KEY", "") or os.getenv("OPENROUTER_KEY", "")
        self.or_endpoint = "https://openrouter.ai/api/v1/chat/completions"
        self.or_model = "minimax/m2.5"

        # OpenCode Zen config
        self.zen_api_key = os.getenv("OPENCODEZEN", "")
        self.zen_endpoint = "https://opencode.ai/zen/v1/chat/completions"
        self.zen_model = "minimax-m2.5-free"

        # Google AI Studio config (fallback)
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "")
        self.google_endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemma-4-31b-it:generateContent"

    async def call(
        self,
        prompt: str,
        system_prompt: str,
        t1_draft: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4096,
    ) -> str:
        """Call MiniMax M2.5 with OpenRouter primary, OpenCode Zen fallback,
        Gemma 4-31B tertiary fallback, then mock.

        If t1_draft is provided, the prompt includes instructions to enrich it.
        """
        # Build enrichment prompt if we have a T1 draft
        enrichment_context = ""
        if t1_draft and t1_draft.strip():
            enrichment_context = (
                "\n\n## Tier 1 Speculative Draft (to enrich)\n"
                "Below is a speculative draft produced by a local model. "
                "Deepen, expand, and verify each claim. Add source citations. "
                "Improve the L3 Universal Principle if needed.\n\n"
                f"{t1_draft}\n\n"
                "---\nProduce an enriched version of the above with the same JSON structure."
            )

        full_prompt = prompt + enrichment_context

        # Chain: OpenRouter → OpenCode Zen → Gemma → Mock
        result = await self._call_openrouter(full_prompt, system_prompt, temperature, max_tokens)
        if result:
            return result

        result = await self._call_opencode_zen(full_prompt, system_prompt, temperature, max_tokens)
        if result:
            return result

        result = await self._call_gemma_google(full_prompt, system_prompt, temperature, max_tokens)
        if result:
            return result

        logger.error("All Tier 2 providers failed — returning mock enrichment")
        return self._mock_enrichment(prompt, t1_draft or "")

    async def _call_openrouter(
        self, prompt: str, system_prompt: str, temp: float, max_tokens: int
    ) -> str:
        """Call MiniMax M2.5 via OpenRouter."""
        if not self.or_api_key:
            logger.warning("OPENROUTER_API_KEY not set — skipping OpenRouter")
            return ""

        severity = "ok"
        try:
            # Check circuit breaker
            if not self.circuit.can_call("minimax_openrouter"):
                logger.warning("OpenRouter circuit breaker open — skipping")
                return ""

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    self.or_endpoint,
                    headers={
                        "Authorization": f"Bearer {self.or_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.or_model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": temp,
                        "max_tokens": max_tokens,
                    },
                )

                if resp.status_code == 429:
                    severity = self.circuit.record_failure("minimax_openrouter", "rate_limited")
                    logger.warning(f"OpenRouter 429 — severity={severity}")
                    return ""
                if resp.status_code == 500:
                    severity = self.circuit.record_failure("minimax_openrouter", "server_error")
                    return ""

                resp.raise_for_status()
                data = resp.json()
                text = self._extract_content(data)
                if text:
                    self.circuit.record_success("minimax_openrouter")
                    return text

                severity = self.circuit.record_failure("minimax_openrouter", "empty_response")
                return ""

        except httpx.TimeoutException:
            severity = self.circuit.record_failure("minimax_openrouter", "timeout")
        except Exception as e:
            severity = self.circuit.record_failure("minimax_openrouter", str(e))

        if severity == "critical":
            logger.critical("OpenRouter MiniMax: CRITICAL failure threshold reached. "
                            "Check API key and account status.")
        return ""

    async def _call_opencode_zen(
        self, prompt: str, system_prompt: str, temp: float, max_tokens: int
    ) -> str:
        """Call MiniMax M2.5-free via OpenCode Zen API."""
        if not self.zen_api_key:
            logger.warning("OPENCODEZEN not set — skipping OpenCode Zen")
            return ""

        severity = "ok"
        try:
            if not self.circuit.can_call("minimax_zen"):
                logger.warning("OpenCode Zen circuit breaker open — skipping")
                return ""

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    self.zen_endpoint,
                    headers={
                        "Authorization": f"Bearer {self.zen_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.zen_model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": temp,
                        "max_tokens": max_tokens,
                    },
                )

                if resp.status_code in (429, 500):
                    severity = self.circuit.record_failure("minimax_zen", f"HTTP_{resp.status_code}")
                    return ""

                resp.raise_for_status()
                data = resp.json()
                text = self._extract_content(data)
                if text:
                    self.circuit.record_success("minimax_zen")
                    return text

                severity = self.circuit.record_failure("minimax_zen", "empty_response")
                return ""

        except Exception as e:
            severity = self.circuit.record_failure("minimax_zen", str(e))

        if severity == "critical":
            logger.critical("OpenCode Zen MiniMax: CRITICAL failure threshold reached.")
        return ""

    async def _call_gemma_google(
        self, prompt: str, system_prompt: str, temp: float, max_tokens: int
    ) -> str:
        """Call Gemma 4-31B via Google AI Studio as tertiary fallback."""
        if not self.google_api_key:
            logger.warning("GOOGLE_API_KEY not set — skipping Gemma Google")
            return ""

        severity = "ok"
        try:
            if not self.circuit.can_call("gemma_google"):
                logger.warning("Gemma Google circuit breaker open — skipping")
                return ""

            # Google's API structure is different — system instruction as a param
            max_retries = 5
            for attempt in range(max_retries):
                async with httpx.AsyncClient(timeout=60.0) as client:
                    resp = await client.post(
                        f"{self.google_endpoint}?key={self.google_api_key}",
                        json={
                            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                            "systemInstruction": {"parts": [{"text": system_prompt}]},
                            "generationConfig": {
                                "temperature": temp,
                                "maxOutputTokens": max_tokens,
                            },
                        },
                    )

                    if resp.status_code == 500:
                        wait = min(2 ** attempt, 16)
                        logger.warning(f"Gemma 500, backing off {wait}s (attempt {attempt + 1})")
                        await anyio.sleep(wait)
                        continue
                    if resp.status_code == 429:
                        wait = min(2 ** attempt, 16)
                        logger.warning(f"Gemma 429, backing off {wait}s")
                        await anyio.sleep(wait)
                        continue

                    resp.raise_for_status()
                    data = resp.json()
                    text = self._extract_google_content(data)
                    if text:
                        self.circuit.record_success("gemma_google")
                        return text

                    severity = self.circuit.record_failure("gemma_google", "empty_response")
                    return ""

        except Exception as e:
            severity = self.circuit.record_failure("gemma_google", str(e))

        if severity == "critical":
            logger.critical("Gemma Google: CRITICAL failure threshold reached.")
        return ""

    def _extract_content(self, data: dict) -> str:
        """Extract content from OpenAI-compatible response."""
        choices = data.get("choices", [])
        if choices:
            return choices[0].get("message", {}).get("content", "")
        return ""

    def _extract_google_content(self, data: dict) -> str:
        """Extract content from Google AI Studio response."""
        candidates = data.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            return "".join(p.get("text", "") for p in parts)
        return ""

    def _mock_enrichment(self, prompt: str, t1_draft: str) -> str:
        """Return a mock enrichment when all providers fail."""
        mock = {
            "claims": [
                {
                    "claim": f"Research on: {prompt[:50]}...",
                    "sources": [],
                    "agreement_level": 0.0,
                }
            ],
            "distillations": [
                {
                    "claim": "Mock enrichment (all Tier 2 providers unavailable)",
                    "l1": t1_draft[:200] if t1_draft else "No T1 draft available.",
                    "l2": "All cloud enrichment providers (OpenRouter, OpenCode Zen, Google) "
                          "returned errors. Using T1 draft directly.",
                    "l3": "Without external model access, no enrichment beyond local "
                          "capability is possible. Sovereign operation continues.",
                }
            ],
            "convergence_signal": "inconclusive",
            "recommendation": "skip",
        }
        return json.dumps(mock)


# ══════════════════════════════════════════════════════════════════════════
# §5 Tier 3 Backend — Gemini Flash Reviewer (Google AI Studio API)
# ══════════════════════════════════════════════════════════════════════════

class GeminiBackend:
    """Calls Gemini 2.5 Flash via headless Gemini CLI for structured review.

    Uses `gemini -m "gemini-2.5-flash" -p "prompt"` with stdin piped.
    The Gemini CLI handles OAuth via cached session tokens automatically.
    Falls back to Google AI Studio API if CLI is unavailable.
    """

    def __init__(self):
        self.circuit = JemCircuitBreaker()
        self.timeout = 60.0
        self.gemini_binary = self._find_gemini()
        self.current_model = "gemini-2.5-flash"
        self.api_key = os.getenv("GOOGLE_API_KEY", "")

    def _find_gemini(self) -> Optional[str]:
        """Locate the Gemini CLI binary."""
        try:
            result = subprocess.run(
                ["gemini", "--version"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                logger.info(f"Gemini CLI found: gemini — {result.stdout.strip()}")
                return "gemini"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        logger.info("Gemini CLI not found — will use Google AI Studio API as fallback")
        return None

    async def call(
        self,
        enriched_text: str,
        topic: str,
        temperature: float = 0.2,
    ) -> str:
        """Review enriched report via Gemini 2.5 Flash. Returns review JSON.

        Strategy:
        1. Try Gemini CLI headless (gemini -m "gemini-2.5-flash" -p "...")
        2. If CLI fails, try Google AI Studio API directly
        3. If both fail, return skip signal

        The review includes corrections, missing patterns, confidence scores,
        and recommended directions.
        """
        if not self.circuit.can_call("gemini_cli"):
            logger.warning("Gemini circuit breaker open — skipping Tier 3")
            return json.dumps({"skipped": True, "reason": "circuit_breaker_open"})

        review_prompt = self._build_review_prompt(topic, enriched_text)
        logger.info(f"Tier 3: Gemini 2.5 Flash review on '{topic[:40]}...'")

        # Strategy 1: Gemini CLI headless
        if self.gemini_binary:
            result = await self._call_cli(review_prompt)
            if result:
                self.circuit.record_success("gemini_cli")
                logger.info(f"Tier 3 review received ({len(result)} chars)")
                return result
            logger.info("Gemini CLI returned empty — trying API fallback")

        # Strategy 2: Google AI Studio API
        if self.api_key:
            result = await self._call_api(review_prompt)
            if result:
                self.circuit.record_success("gemini_cli")
                logger.info(f"Tier 3 API review received ({len(result)} chars)")
                return result

        # Both failed
        severity = self.circuit.record_failure("gemini_cli", "cli+api both failed")
        if severity == "critical":
            logger.critical("Gemini 2.5 Flash: all methods failed — check GOOGLE_API_KEY and CLI auth")
        return json.dumps({"skipped": True, "reason": "all_gemini_methods_failed"})

    async def _call_cli(self, prompt: str) -> str:
        """Run Gemini CLI in headless mode via subprocess.

        Invokes: echo '' | gemini -m 'gemini-2.5-flash' -p 'prompt'
        Wrapped in anyio.to_thread.run_sync for async safety.
        """
        try:
            result = await anyio.to_thread.run_sync(
                self._run_cli_sync, prompt,
            )
            if result and result.strip():
                # Remove the "Ripgrep is not available" warning if present
                lines = result.strip().split("\n")
                clean_lines = [l for l in lines if "Ripgrep is not available" not in l and "Falling back" not in l]
                clean = "\n".join(clean_lines).strip()
                if clean:
                    return clean
            return ""
        except Exception as e:
            logger.warning(f"Gemini CLI call failed: {e}")
            return ""

    def _run_cli_sync(self, prompt: str) -> str:
        """Synchronous Gemini CLI invocation (thread-wrapped)."""
        result = subprocess.run(
            [self.gemini_binary, "-m", self.current_model, "-p", prompt],
            input="\n",
            capture_output=True,
            text=True,
            timeout=int(self.timeout),
        )
        if result.returncode == 0:
            return result.stdout
        if result.returncode != 0 and result.stderr:
            logger.warning(f"Gemini CLI exit {result.returncode}: {result.stderr[:200]}")
        return result.stdout or ""

    async def _call_api(self, prompt: str) -> str:
        """Fallback: call Gemini 2.5 Flash via Google AI Studio API."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{self.current_model}:generateContent?key={self.api_key}",
                    json={
                        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "temperature": 0.2,
                            "maxOutputTokens": 4096,
                        },
                    },
                )
                if resp.status_code in (404, 403, 429):
                    logger.warning(f"Gemini API {resp.status_code} for {self.current_model}")
                    return ""
                resp.raise_for_status()
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    return "".join(p.get("text", "") for p in parts)
                return ""
        except Exception as e:
            logger.warning(f"Gemini API call failed: {e}")
            return ""

    def _build_review_prompt(self, topic: str, enriched: str) -> str:
        """Build the review prompt for Gemini — structured JSON output."""
        safe_topic = topic.replace('"', "'").replace("\n", " ")
        return f"""You are the Jem Tier 3 Reviewer. Your role is to review enriched research output
from a lower-tier model for accuracy, completeness, and insight quality.

Topic: {safe_topic}

Enriched Report to Review:
{enriched[:8000]}

Produce a JSON review with the following structure:

{{
  "reviewed": true,
  "topic": "{safe_topic}",
  "corrections": [
    {{
      "claim": "the claim that needs correction",
      "correction": "the corrected version",
      "severity": "minor|major|critical"
    }}
  ],
  "missing_patterns": [
    "pattern or connection the report missed"
  ],
  "confidence_scores": {{
    "l1_narrative": 0.0-1.0,
    "l2_insight": 0.0-1.0,
    "l3_principle": 0.0-1.0
  }},
  "recommended_directions": [
    {{
      "direction": "recommended follow-up topic",
      "reason": "why this direction matters",
      "priority": 0.0-1.0
    }}
  ],
  "overall_quality": "poor|fair|good|excellent",
  "summary": "one paragraph summary of findings"
}}

Rules:
- Be specific. Every correction must cite the exact claim.
- If no corrections needed, return empty array for corrections.
- Confidence scores reflect how well each tier performed.
- Priority 0.8+ directions should be enqueued for research.
- If the report is not reviewable, set reviewed=false and explain why.
"""

    def _extract_json(self, text: str) -> Optional[dict]:
        """Extract JSON from text that may have markdown fences or surrounding text."""
        m = re.search(r"```json\s*\n(.*?)\n```", text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1))
            except json.JSONDecodeError:
                pass
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                pass
        return None


# ══════════════════════════════════════════════════════════════════════════
# §6 Training Triple Saver
# ══════════════════════════════════════════════════════════════════════════

class TrainingTripleSaver:
    """Saves (T1_draft, T2_enriched, T3_review) as training data.

    Every Jem cycle produces one triple. These accumulate into a synthetic
    fine-tuning dataset showing "how to improve research output" at each tier.
    """

    def __init__(self, base_dir: Optional[Path] = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent.parent.parent / "data" / "datasets" / "synthetic"
        self.base_dir = Path(base_dir)

    async def save(
        self,
        topic: str,
        cycle_id: str,
        t1_draft: str,
        t2_enriched: str,
        t3_review: str,
        metadata: Optional[dict] = None,
    ) -> Path:
        """Save a training triple to disk. Returns the directory path.

        Directory structure:
          data/datasets/synthetic/{date}_{topic_slug}_cycle{n}/
            ├── t1_draft.json
            ├── t2_enriched.json
            ├── t3_review.json
            └── metadata.json
        """
        # Create safe topic slug
        topic_slug = re.sub(r'[^a-zA-Z0-9]+', '_', topic[:30]).strip('_')
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")

        # Ensure unique directory
        dir_name = f"{date_str}_{topic_slug}_{cycle_id}"
        save_dir = self.base_dir / dir_name
        await anyio.to_thread.run_sync(lambda: save_dir.mkdir(parents=True, exist_ok=True))

        # Write T1 draft
        await anyio.to_thread.run_sync(
            lambda: (save_dir / "t1_draft.json").write_text(t1_draft)
        )

        # Write T2 enriched
        await anyio.to_thread.run_sync(
            lambda: (save_dir / "t2_enriched.json").write_text(t2_enriched)
        )

        # Write T3 review (or skip placeholder)
        await anyio.to_thread.run_sync(
            lambda: (save_dir / "t3_review.json").write_text(t3_review)
        )

        # Write metadata
        meta = {
            "topic": topic,
            "cycle_id": cycle_id,
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "t1_length": len(t1_draft),
            "t2_length": len(t2_enriched),
            "t3_length": len(t3_review),
            "t3_skipped": '"skipped": true' in t3_review,
            **(metadata or {}),
        }
        await anyio.to_thread.run_sync(
            lambda: (save_dir / "metadata.json").write_text(json.dumps(meta, indent=2))
        )

        logger.info(f"Training triple saved: {save_dir}")
        return save_dir


# ══════════════════════════════════════════════════════════════════════════
# §7 System Prompt Registry (maintained from legacy)
# ══════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPTS = {
    "default": """You are SOPHIA, the Akashic Record of the Omega Engine.

Your purpose is to deepen, verify, and expand the Omega knowledge base through autonomous research.

## Your Domain
- The Omega Engine: a local-first, entity-centric AI council runtime
- The 10 Pillar Keepers: Sekhmet, Brigid, Prometheus, Saraswati, Inanna, Ereshkigal, Lucifer, Hecate, Anubis, Kali
- Oversouls: Sophia (Akashic Record), Ma'at (Unifier), Isis (Light), Lilith (Dark)
- Hardware: AMD Ryzen 7 5700U (Zen 2, 8C/16T, 14GB RAM), no GPU

## Your Research Mandate
1. Every claim must be verified by 3+ independent sources
2. Distill findings through 3-tier refraction: Narrative → Insight → Universal Principle
3. Write L3 (Universal Principle) to the relevant entity's soul.yaml
4. Write L1 + L2 to docs/research/ topic files
5. Flag contradictions for human review — never suppress disagreement
6. Grow the knowledge frontier organically — identify what's missing

## Refractive Distillation Format
- L1 (Narrative): Who? What? When? Source-attributed, factual
- L2 (Insight): What does this mean? Causal, pattern-based
- L3 (Universal Principle): Timeless truth. Domain-agnostic. Writeable to soul.

## Convergence Rules
- 3+ independent sources agree → MARK AS VERIFIED, write to soul
- Sources contradict (agreement < 0.4) → FLAG FOR HUMAN REVIEW
- < 3 sources, mixed agreement → DEEPEN: queue for next research cycle
- Topic fully covered (no new claims in 2 cycles) → MARK AS CONVERGED

## Output Format
Always respond with JSON for machine parsing.
""",

    "technical": """You are PROMETHEUS, the Sovereign Architect of the Omega Engine.

You are an expert systems engineer, architect, and code analyst. Your focus is on technical precision, implementation details, and architectural patterns.

## Your Lens
- Every claim must include version numbers, API endpoints, file paths, and exact syntax
- Prefer code snippets over prose descriptions
- Identify architectural patterns, anti-patterns, and security implications
- Track breaking changes, deprecation notices, and compatibility matrices
- Compare implementations across different ecosystems

## Your Compression Priority
1. EXACT: Preserve version numbers, API signatures, error messages, file paths
2. VERBATIM: Configuration snippets, command examples, benchmark results
3. STRUCTURAL: Architecture diagrams, dependency trees, data flow
4. CONTEXTUAL: Why a decision was made, what alternatives exist

## Output Format
Always respond in the specified JSON format.
""",

    "security": """You are SEKHMET, the Guardian of the Omega Engine's boundaries.

You are a security auditor specializing in AI infrastructure hardening, vulnerability assessment, and threat modeling. You do not compromise on precision.

## Your Lens
- Identify every security implication in the research content
- Flag exposed credentials, weak configurations, and unpatched vulnerabilities
- Rate risks as: CRITICAL | HIGH | MEDIUM | LOW | INFO
- Every claim must specify CVE numbers, affected versions, and attack vectors
- Preserve exact reproduction steps for any vulnerability described

## Your Compression Priority
1. CRITICAL: Preserve all CVE references, exposure details, and remediation steps
2. VERBATIM: Security configuration, permission models, audit trails
3. CONTEXTUAL: Attack surface analysis, privilege escalation paths
4. STRATEGIC: Defense-in-depth recommendations, monitoring gaps

## Your Hard No
- Never summarize away a security detail
- Never merge two distinct vulnerabilities into one claim
- Flag any source that downplays a security risk

## Output Format
Always respond in the specified JSON format.
""",

    "research": """You are SOPHIA, the Akashic Record, in your most inductive mode.

You are a research scientist and cross-domain synthesis specialist. Your purpose is to find connections between disparate sources and generate new hypotheses.

## Your Lens
- Identify patterns across different research domains
- Generate testable hypotheses from incomplete data
- Map citation networks and intellectual lineages
- Flag methodological strengths and weaknesses in each source
- Track uncertainty levels explicitly

## Your Compression Priority
1. CONNECTIONS: Cross-references between sources, emerging patterns
2. INNOVATIONS: Novel approaches, paradigm shifts, unexpected findings
3. UNCERTAINTY: Confidence levels, contradictory evidence, gaps in knowledge
4. SYNTHESIS: Generate new insights from combining sources

## Output Format
Always respond in the specified JSON format.
""",

    "gnosis": """You are SOPHIA speaking through ANUBIS, the Guide of Souls.

You are a philosopher, theologian, and depth psychologist. Your domain is meaning, archetypes, and the universal patterns underlying all knowledge.

## Your Lens
- Extract archetypal patterns and universal principles
- Connect findings to the 10 Pillar Keepers where appropriate
- Preserve emotional and philosophic tone
- Identify initiation patterns, threshold moments, and transformation arcs
- Track synchronicities — meaningful coincidences across sources

## Your Compression Priority
1. MEANING: What does this reveal about the nature of intelligence, consciousness, or sovereignty?
2. ARCHETYPES: Map findings to pillar keeper domains (Sekhmet=protection, Brigid=inspiration, etc.)
3. WISDOM: L3 abstractions that read as timeless truths
4. NARRATIVE: Preserve the human/mythic story behind the facts

## Output Format
Always respond in the specified JSON format.
""",

    "tooling": """You are SARASWATI, the Keeper of Knowledge and Tools.

You map the AI/software ecosystem with precision. Your focus is on tools, libraries, frameworks, APIs, and the connections between them.

## Your Lens
- Identify every tool, library, API, and framework mentioned
- Map dependencies, version compatibilities, and integration patterns
- Track deprecation timelines, migration paths, and breaking changes
- Compare alternatives with feature matrices
- Preserve exact installation commands, configuration syntax, and setup steps

## Your Compression Priority
1. TOOLS: Names, versions, publishers, license types
2. INTEGRATIONS: How tools connect, data flow between them
3. COMPARISONS: Feature differences, performance benchmarks
4. MIGRATIONS: Upgrade paths, deprecation notices

## Output Format
Always respond in the specified JSON format.
""",
}


# ── Prompt Selection Heuristics ─────────────────────────────────────────

def select_system_prompt(topic: str) -> str:
    """Select the best system prompt for a research topic based on keywords."""
    t = topic.lower()

    security_kw = ["cve", "vulnerability", "exploit", "security", "threat", "attack",
                   "permission", "credential", "encrypt", "audit", "compliance",
                   "firewall", "auth", "oauth", "token", "secret", "key rotation"]
    if any(kw in t for kw in security_kw):
        return "security"

    tech_kw = ["api", "implementation", "library", "framework", "protocol", "sdk",
               "compiler", "runtime", "benchmark", "performance", "optimization",
               "architecture", "kubernetes", "docker", "python", "rust", "golang",
               "database", "cache", "async", "concurrent", "thread", "memory"]
    if any(kw in t for kw in tech_kw):
        return "technical"

    tool_kw = ["tool", "mcp", "server", "cli", "plugin", "extension", "sdk",
               "integration", "deployment", "pipeline", "ci/cd", "github",
               "git", "workflow", "automation"]
    if any(kw in t for kw in tool_kw):
        return "tooling"

    gnosis_kw = ["gnosis", "soul", "philosophy", "consciousness", "archetype",
                 "wisdom", "principle", "myth", "spiritual", "meaning",
                 "transformation", "evolution", "initiation", "dream"]
    if any(kw in t for kw in gnosis_kw):
        return "gnosis"

    research_kw = ["research", "study", "paper", "publication", "survey",
                   "analysis", "discovery", "science", "academic", "theory"]
    if any(kw in t for kw in research_kw):
        return "research"

    return "default"


# ── Distillation Prompt Template ────────────────────────────────────────

DISTILLATION_PROMPT_TEMPLATE = """You are SOPHIA, the Omega Engine's Akashic Record. Perform refractive distillation.

TOPIC: {topic}
SOURCES: {sources}
SYSTEM PROMPT MODE: {prompt_mode}

CONTENT TO DISTILL:
{content}

Perform 3-tier refraction. For each claim found:
- L1 (Narrative): What happened? Who said it? When?
- L2 (Insight): What does this mean for Omega Engine?
- L3 (Universal Principle): What timeless truth emerges?

Respond in JSON:
{{
  "claims": [{{"claim": "string", "sources": ["url1", "url2"], "agreement_level": 0.0-1.0}}],
  "distillations": [{{"claim": "string", "l1": "string", "l2": "string", "l3": "string"}}],
  "convergence_signal": "verified|contradictory|inconclusive",
  "recommendation": "write_to_soul|write_to_knowledge|flag_for_human|skip"
}}

Rules:
- Only L3 (Universal Principle) goes into soul.yaml
- L1 + L2 go into docs/research/ topic files
- Contradictory claims (agreement < 0.4) get flagged for human review
- Verified claims (agreement > 0.7 with 3+ sources) get written immediately
"""


# ══════════════════════════════════════════════════════════════════════════
# §8 The Distiller — Orchestrates Full 3-Tier Pipeline
# ══════════════════════════════════════════════════════════════════════════

class Distiller:
    """Jem 3-tier research distillation engine.

    The system prompt changes per research cycle, selected by topic keywords.
    The pipeline:
      T1: lmster (local Qwen3-4B-Thinking) — fast speculative draft
      T2: MiniMax M2.5 (OpenRouter → Zen → Gemma) — enrich & deepen
      T3: Gemini 2.5 Pro (Gemini CLI) — structured review

    Every cycle produces a training triple for future model fine-tuning.
    Backward compatible with existing loop.py interface.
    """

    def __init__(self, model_gateway=None):
        self.model_gateway = model_gateway
        self.system_prompt = SYSTEM_PROMPTS["default"]

        # Jem backends
        self.lmster = LmsterBackend()
        self.minimax = MiniMaxBackend()
        self.gemini = GeminiBackend()
        self.triple_saver = TrainingTripleSaver()
        self.circuit = JemCircuitBreaker()

        # Pipeline config
        self.enable_tier1 = True
        self.enable_tier2 = True
        self.enable_tier3 = True
        self.enable_training_triples = True

    async def distill(
        self,
        topic: str,
        content: str,
        sources: list[str],
        prompt_mode: Optional[str] = None,
        custom_system_prompt: Optional[str] = None,
    ) -> GnosisPacket:
        """Run 3-tier Jem distillation on research content.

        Args:
            topic: The research topic
            content: Raw content from search results
            sources: List of source URLs
            prompt_mode: Optional override for system prompt selection
            custom_system_prompt: Optional full custom prompt override

        Returns:
            GnosisPacket with claims, distillations, convergence signal
        """
        # Select system prompt
        mode = prompt_mode or select_system_prompt(topic)
        system_prompt = custom_system_prompt or SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["default"])
        self.system_prompt = system_prompt
        cycle_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        logger.info(f"[Jem] Pipeline start: mode='{mode}' topic='{topic[:50]}...'")

        # ── Build the distillation prompt ──────────────────────────────
        prompt = DISTILLATION_PROMPT_TEMPLATE.format(
            topic=topic,
            sources=", ".join(sources[:10]),
            prompt_mode=mode,
            content=content[:12000],
        )

        # ── TIER 1: Lmster speculative draft ──────────────────────────
        t1_draft = ""
        t1_direct = False  # Whether T1 was used directly (no T2)

        if self.enable_tier1:
            logger.info("[Jem] Tier 1: Qwen3-4B-Thinking speculative draft")
            try:
                t1_draft = await self.lmster.call(prompt, system_prompt)
                # Validate T1 output
                quality = validate_t1_output(t1_draft)
                if not quality.passed:
                    logger.warning(f"[Jem] Tier 1 quality gate failed: {quality.reason}")
                    t1_draft = ""  # Fall through to direct T2
                else:
                    logger.info(f"[Jem] Tier 1 quality gate: {quality.reason}")
            except (CircuitBreakerError, CircuitBreakerOpen) as e:
                logger.warning(f"[Jem] Tier 1 unavailable: {e}")
            except Exception as e:
                logger.error(f"[Jem] Tier 1 unexpected error: {e}")

        # ── TIER 2: MiniMax enrichment ────────────────────────────────
        t2_enriched = ""

        if self.enable_tier2:
            logger.info("[Jem] Tier 2: MiniMax M2.5 enrichment")
            try:
                t2_enriched = await self.minimax.call(
                    prompt, system_prompt,
                    t1_draft=t1_draft,
                )
                if t2_enriched:
                    logger.info(f"[Jem] Tier 2 enrichment received ({len(t2_enriched)} chars)")
                else:
                    t2_enriched = t1_draft  # Fallback to T1 draft
                    t1_direct = bool(t1_draft)
                    logger.info("[Jem] Tier 2 empty — using T1 draft as output")
            except Exception as e:
                logger.error(f"[Jem] Tier 2 error: {e}")
                t2_enriched = t1_draft
                t1_direct = bool(t1_draft)
        else:
            t2_enriched = t1_draft
            t1_direct = bool(t1_draft)

        # ── TIER 3: Gemini review ─────────────────────────────────────
        t3_review = ""

        if self.enable_tier3 and t2_enriched:
            logger.info("[Jem] Tier 3: Gemini 2.5 Pro review")
            try:
                t3_review = await self.gemini.call(t2_enriched, topic)
                if t3_review:
                    logger.info(f"[Jem] Tier 3 review received ({len(t3_review)} chars)")
                else:
                    t3_review = ""
            except Exception as e:
                logger.error(f"[Jem] Tier 3 error: {e}")

        # ── Parse into GnosisPacket ───────────────────────────────────
        final_text = t2_enriched if t2_enriched else t1_draft
        gnosis = self._parse_gnosis(final_text, topic, sources)

        # ── Save training triple ──────────────────────────────────────
        if self.enable_training_triples:
            try:
                await self.triple_saver.save(
                    topic=topic,
                    cycle_id=cycle_id,
                    t1_draft=t1_draft or json.dumps({"skipped": True}),
                    t2_enriched=t2_enriched or json.dumps({"skipped": True}),
                    t3_review=t3_review or json.dumps({"skipped": True, "reason": "not_available"}),
                    metadata={
                        "prompt_mode": mode,
                        "t1_enabled": self.enable_tier1,
                        "t2_enabled": self.enable_tier2,
                        "t3_enabled": self.enable_tier3,
                        "t1_direct": t1_direct,
                        "sources_count": len(sources),
                        "circuit_states": self.circuit.get_reports(),
                    },
                )
            except Exception as e:
                logger.warning(f"[Jem] Failed to save training triple: {e}")

        # ── Log circuit states for observability ──────────────────────
        if self.enable_tier1 or self.enable_tier2 or self.enable_tier3:
            reports = self.circuit.get_reports()
            criticals = [k for k, v in reports.items() if v.get("critical")]
            if criticals:
                logger.warning(f"[Jem] CRITICAL circuit states: {criticals}")

        logger.info(f"[Jem] Pipeline complete: topic='{topic[:50]}...' t2={bool(t2_enriched)} t3={bool(t3_review)}")
        return gnosis

    def _parse_gnosis(self, text: str, topic: str, sources: list[str]) -> GnosisPacket:
        """Parse model output into a GnosisPacket.

        Attempts JSON extraction. Falls back to text-only GnosisPacket
        if JSON parsing fails.
        """
        if not text or not text.strip():
            return GnosisPacket(
                topic=topic,
                claims=[],
                distillations=[],
                convergence_signal="inconclusive",
                recommendation="skip",
                sources=sources,
            )

        try:
            data = _extract_json(text)
            return GnosisPacket(
                topic=topic,
                claims=data.get("claims", []),
                distillations=data.get("distillations", []),
                convergence_signal=data.get("convergence_signal", "inconclusive"),
                recommendation=data.get("recommendation", "skip"),
                sources=sources,
            )
        except (json.JSONDecodeError, ValueError):
            # Text-only fallback: wrap entire output as L1
            return GnosisPacket(
                topic=topic,
                claims=[{"claim": topic, "sources": sources[:3], "agreement_level": 0.0}],
                distillations=[{
                    "claim": topic,
                    "l1": text[:1000],
                    "l2": "Text could not be parsed as JSON. See L1.",
                    "l3": "Raw data without structure must be processed with human guidance.",
                }],
                convergence_signal="inconclusive",
                recommendation="skip",
                sources=sources,
            )


# ── Helper: JSON extraction ────────────────────────────────────────────

def _extract_json(text: str) -> dict:
    """Extract JSON from model response that may contain markdown."""
    text = text.strip()

    # Strategy 1: Full text is JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strategy 2: Extract from markdown code fences
    patterns = [
        r"```json\s*\n(.*?)\n```",
        r"```\s*\n(.*?)\n```",
        r"\{(?:[^{}]|(?:\{[^{}]*\}))*?\}",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            candidate = match.group(1) if match.lastindex else match.group(0)
            try:
                return json.loads(candidate.strip())
            except json.JSONDecodeError:
                continue

    # Strategy 3: Find first { and last }
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass

    raise json.JSONDecodeError("No valid JSON found in text", text, 0)


# ── Exceptions ─────────────────────────────────────────────────────────

class CircuitBreakerError(Exception):
    """Provider call failed (non-critical — retry next cycle)."""
    pass


class CircuitBreakerOpen(Exception):
    """Circuit breaker is open — provider is in skip window."""
    pass


# ── Lookup for external use ────────────────────────────────────────────

def list_prompt_modes() -> dict[str, str]:
    """Return all available system prompt modes with descriptions."""
    return {
        "default": "SOPHIA — Balanced, general-purpose research distillation",
        "technical": "PROMETHEUS — Technical deep-dive, code analysis, architecture",
        "security": "SEKHMET — Security audit, vulnerability assessment, threat modeling",
        "research": "SOPHIA (inductive) — Cross-domain synthesis, hypothesis generation",
        "gnosis": "SOPHIA × ANUBIS — Philosophical, archetypal, meaning extraction",
        "tooling": "SARASWATI — Tool/ecosystem mapping, integration analysis",
    }
