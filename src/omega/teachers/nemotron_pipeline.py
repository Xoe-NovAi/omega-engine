"""Nemotron 3 Ultra Teacher Pipeline — DPO Pair Generation via Iterative Critique-Loop.

AP: AP-NEMOTON-TEACHER-v1.0.0
⬡ OMEGA ⬡ ROC_RACOON ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_teacher_pipeline ⬡ ACTIVE

This module implements an Iterative Critique-Loop for generating DPO training pairs:
1. Local Model generates initial response
2. Nemotron 3 Ultra critiques the response
3. Local Model generates improved response
4. Nemotron 3 Ultra makes final verdict
5. DPO pair (prompt, chosen, rejected) is captured

Usage:
    pipeline = NemotronTeacherPipeline()
    dpo_pair = await pipeline.generate_dpo_pair(
        prompt="Explain the Zone Memory allocator in Quake",
        local_model="gemma-4-31b-it"
    )
"""

import json
import logging
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any

import anyio

logger = logging.getLogger("omega.teachers.nemotron")


@dataclass
class DPOPair:
    """A single DPO training pair."""
    prompt: str
    chosen: str
    rejected: str
    metadata: Dict[str, Any]
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class CritiqueResult:
    """Result from Nemotron critique."""
    accepted: bool
    issues: List[str]
    suggestions: List[str]
    raw_response: str


class NemotronTeacherPipeline:
    """Sovereign Teacher Pipeline for DPO pair generation.
    
    Uses Nemotron 3 Ultra via OpenRouter as a teacher model to critique
    and improve responses from local models, generating DPO training pairs.
    """
    
    # Nemotron 3 Ultra model ID on OpenRouter
    NEMOTRON_MODEL = "nvidia/nemotron-3-ultra-550b-a55b"
    
    # Prompt templates
    CRITIQUE_PROMPT = """You are a expert teacher evaluating a response. Analyze the following response and identify any issues.

Original Query: {prompt}

Response to Critique: {response}

Provide your critique in the following format:
- ACCEPTED: [yes/no]
- ISSUES: [list any factual errors, logical flaws, or missing information]
- SUGGESTIONS: [list specific improvements]

Be concise and specific."""

    FINAL_VERDICT_PROMPT = """You are a expert teacher making a final verdict on an improved response.

Original Query: {prompt}
Initial Response (rejected): {initial_response}
Improved Response: {improved_response}

Did the improvement address the issues from the critique?
- ACCEPTED: [yes/no]
- REASON: [brief explanation]

Be concise and specific."""
    
    def __init__(
        self,
        openrouter_key: Optional[str] = None,
        dpo_storage_dir: str = "data/knowledge/dpo_pairs",
        max_iterations: int = 3,
    ):
        """Initialize the Nemotron Teacher Pipeline.
        
        Args:
            openrouter_key: OpenRouter API key. If None, uses vault.
            dpo_storage_dir: Directory to store DPO pairs.
            max_iterations: Maximum critique-fix iterations.
        """
        self.openrouter_key = openrouter_key or self._resolve_openrouter_key()
        self.dpo_storage_dir = Path(dpo_storage_dir)
        self.dpo_storage_dir.mkdir(parents=True, exist_ok=True)
        self.max_iterations = max_iterations
        
        # Stats
        self.stats = {
            "pairs_generated": 0,
            "pairs_accepted": 0,
            "pairs_rejected": 0,
            "total_iterations": 0,
        }
    
    def _resolve_openrouter_key(self) -> str:
        """Resolve OpenRouter API key from vault or environment."""
        try:
            from omega.vault.key_vault import KeyVault
            vault = KeyVault()
            return vault.resolve("openrouter")
        except Exception as e:
            logger.warning(f"Vault resolution failed, falling back to env: {e}")
            return os.environ.get("OPENROUTER_API_KEY", "placeholder")
    
    async def generate_dpo_pair(
        self,
        prompt: str,
        local_model: str = "gemma-4-31b-it",
        local_generate_fn: Optional[Any] = None,
    ) -> Optional[DPOPair]:
        """Generate a DPO pair using the iterative critique-loop.
        
        Args:
            prompt: The original query/prompt.
            local_model: The local model to use for generation.
            local_generate_fn: Async function to generate responses from local model.
                If None, uses a mock generator.
        
        Returns:
            DPOPair if successful, None if failed.
        """
        logger.info(f"Starting DPO pair generation for prompt: {prompt[:50]}...")
        
        # Step 1: Generate initial response from local model
        initial_response = await self._generate_local(
            prompt, local_model, local_generate_fn
        )
        if not initial_response:
            logger.error("Failed to generate initial response")
            return None
        
        # Iterative critique-loop
        current_response = initial_response
        chosen_response = None
        
        for iteration in range(self.max_iterations):
            logger.info(f"Iteration {iteration + 1}/{self.max_iterations}")
            
            # Step 2: Nemotron critiques the response
            critique = await self._nemotron_critique(prompt, current_response)
            if not critique:
                logger.error(f"Critique failed on iteration {iteration + 1}")
                break
            
            if critique.accepted:
                logger.info(f"Response accepted on iteration {iteration + 1}")
                chosen_response = current_response
                break
            
            # Step 3: Local model generates improved response
            improved_response = await self._generate_local(
                f"{prompt}\n\nPlease address these issues:\n" + 
                "\n".join(critique.issues) + 
                "\n\nSuggestions:\n" + 
                "\n".join(critique.suggestions),
                local_model,
                local_generate_fn,
            )
            
            if not improved_response:
                logger.error(f"Failed to generate improved response on iteration {iteration + 1}")
                break
            
            # Step 4: Nemotron makes final verdict
            verdict = await self._nemotron_verdict(
                prompt, current_response, improved_response
            )
            
            if verdict and verdict.accepted:
                logger.info(f"Improved response accepted on iteration {iteration + 1}")
                chosen_response = improved_response
                break
            
            # Continue with improved response for next iteration
            current_response = improved_response
            self.stats["total_iterations"] += 1
        
        # If no response was accepted, use the last one
        if chosen_response is None:
            logger.warning("No response accepted, using last response")
            chosen_response = current_response
        
        # Create DPO pair
        dpo_pair = DPOPair(
            prompt=prompt,
            chosen=chosen_response,
            rejected=initial_response,
            metadata={
                "local_model": local_model,
                "teacher_model": self.NEMOTRON_MODEL,
                "iterations": iteration + 1 if 'iteration' in dir() else 0,
                "accepted": chosen_response != initial_response,
            }
        )
        
        # Save DPO pair
        await self._save_dpo_pair(dpo_pair)
        
        self.stats["pairs_generated"] += 1
        if chosen_response != initial_response:
            self.stats["pairs_accepted"] += 1
        else:
            self.stats["pairs_rejected"] += 1
        
        logger.info(f"DPO pair generated: {dpo_pair.timestamp}")
        return dpo_pair
    
    async def _generate_local(
        self, 
        prompt: str, 
        model: str,
        generate_fn: Optional[Any] = None,
    ) -> Optional[str]:
        """Generate response from local model."""
        if generate_fn:
            try:
                return await generate_fn(prompt, model)
            except Exception as e:
                logger.error(f"Local generation failed: {e}")
                return None
        
        # Mock generator for testing
        logger.info(f"Mock local generation for model: {model}")
        return f"[Mock response from {model}] {prompt[:100]}..."
    
    async def _nemotron_critique(
        self, 
        prompt: str, 
        response: str,
    ) -> Optional[CritiqueResult]:
        """Get critique from Nemotron 3 Ultra."""
        critique_prompt = self.CRITIQUE_PROMPT.format(
            prompt=prompt, response=response
        )
        
        raw_response = await self._call_nemotron(critique_prompt)
        if not raw_response:
            return None
        
        return self._parse_critique(raw_response)
    
    async def _nemotron_verdict(
        self,
        prompt: str,
        initial_response: str,
        improved_response: str,
    ) -> Optional[CritiqueResult]:
        """Get final verdict from Nemotron 3 Ultra."""
        verdict_prompt = self.FINAL_VERDICT_PROMPT.format(
            prompt=prompt,
            initial_response=initial_response,
            improved_response=improved_response,
        )
        
        raw_response = await self._call_nemotron(verdict_prompt)
        if not raw_response:
            return None
        
        return self._parse_verdict(raw_response)
    
    async def _call_nemotron(self, prompt: str) -> Optional[str]:
        """Call Nemotron 3 Ultra via OpenRouter."""
        import httpx
        
        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://omega-engine.xoe-nov.ai",
            "X-Title": "Omega Engine Teacher Pipeline",
        }
        
        payload = {
            "model": self.NEMOTRON_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1024,
            "temperature": 0.3,
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.warning("Rate limited by OpenRouter, backing off...")
                await anyio.sleep(5.0)
                return await self._call_nemotron(prompt)  # Retry once
            logger.error(f"Nemotron API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Nemotron call failed: {e}")
            return None
    
    def _parse_critique(self, raw_response: str) -> CritiqueResult:
        """Parse Nemotron critique response."""
        lines = raw_response.strip().split("\n")
        
        accepted = False
        issues = []
        suggestions = []
        
        for line in lines:
            line = line.strip()
            if line.upper().startswith("- ACCEPTED:"):
                value = line.split(":", 1)[1].strip().lower()
                accepted = value in ("yes", "true", "1")
            elif line.upper().startswith("- ISSUES:"):
                issues_text = line.split(":", 1)[1].strip()
                issues = [i.strip() for i in issues_text.split(",") if i.strip()]
            elif line.upper().startswith("- SUGGESTIONS:"):
                suggestions_text = line.split(":", 1)[1].strip()
                suggestions = [s.strip() for s in suggestions_text.split(",") if s.strip()]
        
        return CritiqueResult(
            accepted=accepted,
            issues=issues,
            suggestions=suggestions,
            raw_response=raw_response,
        )
    
    def _parse_verdict(self, raw_response: str) -> CritiqueResult:
        """Parse Nemotron verdict response."""
        lines = raw_response.strip().split("\n")
        
        accepted = False
        reason = ""
        
        for line in lines:
            line = line.strip()
            if line.upper().startswith("- ACCEPTED:"):
                value = line.split(":", 1)[1].strip().lower()
                accepted = value in ("yes", "true", "1")
            elif line.upper().startswith("- REASON:"):
                reason = line.split(":", 1)[1].strip()
        
        return CritiqueResult(
            accepted=accepted,
            issues=[reason] if not accepted else [],
            suggestions=[],
            raw_response=raw_response,
        )
    
    async def _save_dpo_pair(self, pair: DPOPair) -> None:
        """Save DPO pair to JSONL file."""
        filename = f"dpo_pairs_{datetime.now(timezone.utc).strftime('%Y%m%d')}.jsonl"
        filepath = self.dpo_storage_dir / filename
        
        def _write():
            with open(filepath, "a") as f:
                f.write(json.dumps(asdict(pair)) + "\n")
        
        await anyio.to_thread.run_sync(_write)
        logger.info(f"DPO pair saved to {filepath}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        return self.stats.copy()
