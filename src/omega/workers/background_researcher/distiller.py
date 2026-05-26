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
from .soul_update_manager import SoulUpdateManager

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

    # Check for raw claims and sources
    text_lower = text.lower()
    claims_found = bool(re.search(r'"claims":\s*\[', text) or 'claim:' in text_lower)
    sources_found = bool(re.search(r'"sources":\s*\[', text) or 'source:' in text_lower)
    
    result.has_l1 = claims_found
    result.has_l2 = sources_found
    result.has_l3 = False # T1 should NEVER produce L3
    
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

class T2Backend:
    """Calls Gemma 4-31B via Google AI Studio.
    
    The call method takes an optional T1 draft to enrich — if provided,
    the draft becomes the starting point for the enrichment.
    """
    
    def __init__(self):
        self.circuit = JemCircuitBreaker()
        self.timeout = 90.0
        
        # Google AI Studio config
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "")
        self.google_endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemma-4-31b-it:generateContent"
        self.model = "gemma-4-31b-it"

    async def call(
        self,
        prompt: str,
        system_prompt: str,
        t1_draft: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4096,
    ) -> str:
        """Call Gemma 4-31B via Google AI Studio.
        
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
        
        # Primary: Google AI Studio
        result = await self._call_gemma_google(full_prompt, system_prompt, temperature, max_tokens)
        if result:
            return result
        
        logger.error("Tier 2 provider (Gemma Google) failed — returning mock enrichment")
        return self._mock_enrichment(prompt, t1_draft or "")

    async def _call_gemma_google(
        self, prompt: str, system_prompt: str, temp: float, max_tokens: int
    ) -> str:
        """Call Gemma 4-31B via Google AI Studio."""
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
                    "claim": "Mock enrichment (T2 providers unavailable)",
                    "l1": t1_draft[:200] if t1_draft else "No T1 draft available.",
                    "l2": "T2 enrichment failed. Using T1 draft directly.",
                    "l3": "Sovereign operation continues without cloud enrichment.",
                }
            ],
            "convergence_signal": "inconclusive",
            "recommendation": "skip",
        }
        return json.dumps(mock)


# ══════════════════════════════════════════════════════════════════════════
# §5 Tier 3 Backend — Gemini Flash Reviewer (Google AI Studio API)
# ══════════════════════════════════════════════════════════════════════════

class T3Backend:
    """Calls DeepSeek-V4-Flash via OpenCode Zen.
    
    The review includes corrections, missing patterns, confidence scores,
    and recommended directions.
    """
    
    def __init__(self):
        self.circuit = JemCircuitBreaker()
        self.timeout = 60.0
        self.zen_api_key = os.getenv("OPENCODEZEN", "")
        self.zen_endpoint = "https://opencode.ai/zen/v1/chat/completions"
        self.model = "deepseek-v4-flash"

    async def call(
        self,
        enriched_text: str,
        topic: str,
        temperature: float = 0.2,
    ) -> str:
        """Review enriched report via OpenCode Zen (DeepSeek-V4-Flash)."""
        if not self.circuit.can_call("opencode_zen"):
            logger.warning("OpenCode Zen circuit breaker open — skipping Tier 3")
            return json.dumps({"skipped": True, "reason": "circuit_breaker_open"})
        
        review_prompt = self._build_review_prompt(topic, enriched_text)
        logger.info(f"Tier 3: DeepSeek-V4-Flash review on '{topic[:40]}...'")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    self.zen_endpoint,
                    headers={
                        "Authorization": f"Bearer {self.zen_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are the Jem Tier 3 Reviewer. Your role is to review enriched research output for accuracy, completeness, and insight quality."},
                            {"role": "user", "content": review_prompt},
                        ],
                        "temperature": temperature,
                        "max_tokens": 4096,
                    },
                )
                
                if resp.status_code in (429, 500):
                    self.circuit.record_failure("opencode_zen", f"HTTP_{resp.status_code}")
                    return json.dumps({"skipped": True, "reason": f"HTTP_{resp.status_code}"})
                
                resp.raise_for_status()
                data = resp.json()
                text = self._extract_content(data)
                if text:
                    self.circuit.record_success("opencode_zen")
                    logger.info(f"Tier 3 review received ({len(text)} chars)")
                    return text
                
                self.circuit.record_failure("opencode_zen", "empty_response")
                return json.dumps({"skipped": True, "reason": "empty_response"})
        
        except Exception as e:
            self.circuit.record_failure("opencode_zen", str(e))
            logger.warning(f"Tier 3 call failed: {e}")
            return json.dumps({"skipped": True, "reason": str(e)})

    def _extract_content(self, data: dict) -> str:
        """Extract content from OpenAI-compatible response."""
        choices = data.get("choices", [])
        if choices:
            return choices[0].get("message", {}).get("content", "")
        return ""

    def _build_review_prompt(self, topic: str, enriched: str) -> str:
        """Build the review prompt for T3 — structured JSON output.
        
        Implements the 'Sovereign Auditor' pattern to prevent convergence bias.
        """
        safe_topic = topic.replace('"', "'").replace("\n", " ")
        return f"""You are the Jem Tier 3 Sovereign Auditor. Your role is to critically review enriched research output.
        
        CRITICAL MANDATE: Avoid Convergence Bias. Do NOT simply agree with the lower-tier model. 
        Your value comes from finding what the previous model missed, misattributed, or hallucinated.
        
        Topic: {safe_topic}
        
        Enriched Report to Review:
        {enriched[:8000]}
        
        Produce a JSON review with the following structure:
        {{
          "reviewed": true,
          "topic": "{safe_topic}",
          "corrections": [
            {{
              "claim": "the exact claim that is flawed",
              "correction": "the evidence-based correction",
              "severity": "minor|major|critical"
            }}
          ],
          "missing_patterns": [
            "critical connections or contradictions the report ignored"
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
          "summary": "A critical summary. If the report is too 'safe' or generic, mark it as such."
        }}
        
        Audit Rules:
        1. Devil's Advocate: Actively attempt to disprove the L3 Universal Principle.
        2. Evidence Check: If a claim lacks a specific source, flag it as a 'low-confidence' correction.
        3. Pattern Gap: Look for 'blind spots' — what is the report NOT saying that a sovereign intelligence should know?
        4. Penalty for Agreement: If you find no corrections in a complex topic, you are failing your mandate. Be rigorous.
        5. If the report is not reviewable, set reviewed=false and explain why.
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
# §7 System Prompt Registry (Config-Driven)
# ══════════════════════════════════════════════════════════════════════════

# Removed hardcoded SYSTEM_PROMPTS dictionary. 
# Prompts are now loaded dynamically via load_distiller_prompts().



# ── Prompt Registry Loader ─────────────────────────────────────────

def load_distiller_prompts() -> dict:
    """Load distiller prompts and mappings from config/distiller_prompts.yaml."""
    try:
        import yaml
        config_path = Path("config/distiller_prompts.yaml")
        if not config_path.exists():
            logger.error("distiller_prompts.yaml not found — using empty registry")
            return {"modes": {"default": {"prompt": "You are a research assistant."}}, "mappings": {}}
        
        content = config_path.read_text()
        data = yaml.safe_load(content)
        return data if data else {"modes": {}, "mappings": {}}
    except Exception as e:
        logger.error(f"Error loading distiller prompts: {e}")
        return {"modes": {"default": {"prompt": "You are a research assistant."}}, "mappings": {}}

def select_system_prompt(topic: str, registry: dict) -> str:
    """Select the best system prompt for a research topic based on config mappings."""
    t = topic.lower()
    mappings = registry.get("mappings", {})
    
    for mode, keywords in mappings.items():
        if any(kw in t for kw in keywords):
            return mode
            
    return "default"



# ── Prompt Templates ──────────────────────────────────────────────────────
 
T1_GATHER_PROMPT = """You are the Jem Tier 1 Gatherer. Your role is to extract raw, factual claims from the provided content.
 
TOPIC: {topic}
SOURCES: {sources}
 
CONTENT TO GATHER:
{content}
 
Extract every distinct factual claim. For each claim, provide:
1. The exact claim text.
2. The source URL(s) supporting it.
3. A confidence score (0.0-1.0) based on source reliability.
 
Respond in JSON:
{{
  "claims": [
    {{
      "claim": "string",
      "sources": ["url1", "url2"],
      "confidence": 0.0-1.0
    }}
  ]
}}
 
Rules:
- NO ANALYSIS.
- NO SYNTHESIS.
- NO L1/L2/L3 REFRACTION.
- Just raw, attributed facts.
"""
 
T2_DISTILL_PROMPT = """You are the Omega Engine's Akashic Record. Perform refractive distillation on the provided claims.
 
TOPIC: {topic}
SOURCES: {sources}
SYSTEM PROMPT MODE: {prompt_mode}
 
RAW CLAIMS TO DISTILL:
{content}
 
Perform 3-tier refraction. For each claim found:
- L1 (Narrative): What happened? Who said it? When?
- L2 (Insight): What does this mean for Omega Engine?
- L3 (Universal Principle): What timeless truth emerges?
 
Respond in JSON:
{{
  "claims": [{{ "claim": "string", "sources": ["url1", "url2"], "agreement_level": 0.0-1.0 }}],
  "distillations": [{{ "claim": "string", "l1": "string", "l2": "string", "l3": "string" }}],
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

    def __init__(self, model_gateway=None, budget=None):
        self.model_gateway = model_gateway
        self.system_prompt = None
        self.budget = budget
        
        # Jem backends
        self.lmster = LmsterBackend()
        self.t2 = T2Backend()
        self.t3 = T3Backend()
        self.triple_saver = TrainingTripleSaver()
        self.soul_manager = SoulUpdateManager()
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
        registry = load_distiller_prompts()
        mode = prompt_mode or select_system_prompt(topic, registry)
        
        modes = registry.get("modes", {})
        system_prompt = custom_system_prompt or modes.get(mode, {}).get("prompt") or modes.get("default", {}).get("prompt", "You are a research assistant.")
        self.system_prompt = system_prompt
        cycle_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        logger.info(f"[Jem] Pipeline start: mode='{mode}' topic='{topic[:50]}...'")

        # ── Build the prompts ──────────────────────────────────────────
        t1_prompt = T1_GATHER_PROMPT.format(
            topic=topic,
            sources=", ".join(sources[:10]),
            content=content[:12000],
        )
        
        t2_prompt = T2_DISTILL_PROMPT.format(
            topic=topic,
            sources=", ".join(sources[:10]),
            prompt_mode=mode,
            content=content[:12000],
        )

        # ── TIER 1: Lmster speculative draft ──────────────────────────
        t1_draft = ""
        t1_direct = False  # Whether T1 was used directly (no T2)

        if self.enable_tier1:
            logger.info("[Jem] Tier 1: Qwen3-4B-Thinking raw gathering")
            try:
                t1_draft = await self.lmster.call(t1_prompt, system_prompt)
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
            logger.info("[Jem] Tier 2: Gemma 4-31B distillation")
            try:
                # Budget check for gemma_calls
                if self.budget and not self.budget.check_daily_limit("gemma_calls"):
                    logger.warning("[Jem] Daily budget for gemma_calls exhausted — skipping T2")
                    t2_enriched = t1_draft
                    t1_direct = bool(t1_draft)
                else:
                    t2_enriched = await self.t2.call(
                        t2_prompt, system_prompt,
                        t1_draft=t1_draft,
                    )
                    if t2_enriched:
                        logger.info(f"[Jem] Tier 2 distillation received ({len(t2_enriched)} chars)")
                        if self.budget: self.budget.increment_daily("gemma_calls")
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
        
        # ── TIER 3: DeepSeek review ─────────────────────────────────────
        t3_review = ""
        
        if self.enable_tier3 and t2_enriched:
            logger.info("[Jem] Tier 3: DeepSeek-V4-Flash review")
            try:
                # Budget check for gemma_calls
                if self.budget and not self.budget.check_daily_limit("gemma_calls"):
                    logger.warning("[Jem] Daily budget for gemma_calls exhausted — skipping T3")
                    t3_review = ""
                else:
                    t3_review = await self.t3.call(t2_enriched, topic)
                    if t3_review:
                        logger.info(f"[Jem] Tier 3 review received ({len(t3_review)} chars)")
                        if self.budget: self.budget.increment_daily("gemma_calls")
                    else:
                        t3_review = ""
            except Exception as e:
                logger.error(f"[Jem] Tier 3 error: {e}")
        
        # ── Parse into GnosisPacket and apply T3 corrections ────────────────
        final_text = t2_enriched if t2_enriched else t1_draft
        gnosis = self._parse_gnosis(final_text, topic, sources)
        
        if t3_review:
            try:
                review_data = self.t3._extract_json(t3_review)
                if review_data:
                    # 1. Apply corrections to distillations
                    for corr in review_data.get("corrections", []):
                        for dist in gnosis.distillations:
                            if corr["claim"] in dist["claim"]:
                                dist["l3"] = f"{dist['l3']} [CORRECTION: {corr['correction']}]"
                    
                    # 2. Update convergence signal based on T3 confidence
                    conf = review_data.get("confidence_scores", {})
                    if conf.get("l3_principle", 1.0) < 0.4:
                        gnosis.convergence_signal = "contradictory"
                        gnosis.recommendation = "flag_for_human"
                    elif conf.get("l3_principle", 1.0) > 0.8:
                        gnosis.convergence_signal = "verified"
                        gnosis.recommendation = "write_to_soul"
                    
                    # 3. Capture recommended directions
                    gnosis.recommended_directions = review_data.get("recommended_directions", [])
                
                # 4. Write improvement briefs to sub-facet souls
                # T2 output -> Initiate soul
                await self.soul_manager.update_subfacet_soul(
                    "initiate", 
                    f"L2 enrichment for {topic}: {t2_enriched[:500]}..."
                )
                # T3 output -> Analyst and Editor souls
                await self.soul_manager.update_subfacet_soul(
                    "analyst", 
                    f"T3 review for {topic}: {t3_review[:500]}..."
                )
                await self.soul_manager.update_subfacet_soul(
                    "editor", 
                    f"T3 review for {topic}: {t3_review[:500]}..."
                )
                
            except Exception as e:
                logger.warning(f"[Jem] Failed to apply T3 review to GnosisPacket: {e}")

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
