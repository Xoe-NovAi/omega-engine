# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-PR-READINESS-v1.0.0
# AP: AP-SKEPTICAL-VERIFIER-v1.0.0
# 🔱 Skeptical Verifier — NLI and the Two-Source Rule
# [id-soft: vet-015] ZONEID Pattern — verification of claim integrity
# ⬡ OMEGA ⬡ MAAT ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_skeptical_verifier ⬡ H3-C2


# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from omega.oracle.model_gateway import ModelGateway
from omega.errors import OmegaError

logger = logging.getLogger(__name__)


@dataclass
class VerificationSource:
    """A single piece of evidence used for verification."""

    content: str
    source_id: str
    timestamp: Optional[datetime] = None
    authority_score: float = 0.5  # 0.0 to 1.0
    nli_result: str = "NEUTRAL"  # ENTAIL, CONTRADICT, NEUTRAL


@dataclass
class VerificationResult:
    """The final outcome of the skeptical verification process."""

    status: str  # VERIFIED, CONTRADICTED, UNVERIFIED
    claim: str
    evidence: List[VerificationSource] = field(default_factory=list)
    reasoning: str = ""
    verified_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SkepticalVerifier:
    """
    Implements the Two-Source Rule (TSR) and Natural Language Inference (NLI)
    to move from probabilistic generation to deterministic verification.

    [H3-C2] Sovereign Verification Pipeline.
    """

    def __init__(self, model_gateway: ModelGateway, nli_model: str = "qwen3-4b-think"):
        self.model_gateway = model_gateway
        self.nli_model = nli_model

    async def verify(
        self, claim: str, evidence_list: List[Dict[str, Any]], trace_id: Optional[str] = None
    ) -> VerificationResult:
        """
        Verify a claim against a list of evidence snippets using the Two-Source Rule.

        Args:
            claim: The hypothesis to verify.
            evidence_list: List of evidence dicts containing 'content', 'source_id', etc.
            trace_id: Current trace ID for observability propagation.
        """
        self._trace_id = trace_id  # Store for sub-calls
        sources = []
        entailments = []
        contradictions = []

        for item in evidence_list:
            content = item.get("content", "")
            source_id = item.get("source_id", "unknown")
            timestamp = item.get("timestamp")
            authority = item.get("authority_score", 0.5)

            # Perform NLI check
            result = await self._nli_check(content, claim)

            source = VerificationSource(
                content=content,
                source_id=source_id,
                timestamp=timestamp,
                authority_score=authority,
                nli_result=result,
            )
            sources.append(source)

            if result == "ENTAIL":
                entailments.append(source)
            elif result == "CONTRADICT":
                contradictions.append(source)

        # Apply Two-Source Rule (TSR)
        # 1. Check for contradictions first
        if contradictions:
            resolution = await self._resolve_contradiction(claim, contradictions, entailments)
            if resolution["status"] == "CONTRADICTED":
                return VerificationResult(
                    status="CONTRADICTED",
                    claim=claim,
                    evidence=sources,
                    reasoning=resolution["reasoning"],
                )
            # If resolved to verified, continue to TSR check

        # 2. Check for >= 2 independent entailments
        if len(entailments) >= 2:
            return VerificationResult(
                status="VERIFIED",
                claim=claim,
                evidence=sources,
                reasoning=f"Claim verified by {len(entailments)} independent sources.",
            )

        # 3. Default to unverified
        return VerificationResult(
            status="UNVERIFIED",
            claim=claim,
            evidence=sources,
            reasoning="Insufficient evidence to verify claim (less than 2 entailments).",
        )

    async def _nli_check(self, premise: str, hypothesis: str) -> str:
        """
        Perform NLI using the reasoning model as a classifier.
        Returns: ENTAIL, CONTRADICT, or NEUTRAL.
        """
        prompt = (
            f"Task: Natural Language Inference (NLI)\n"
            f"Premise: {premise}\n"
            f"Hypothesis: {hypothesis}\n\n"
            f"Determine the relationship between the premise and the hypothesis.\n"
            f"Output ONLY one of the following tags: [ENTAIL], [CONTRADICT], or [NEUTRAL].\n"
            f"Rules:\n"
            f"- [ENTAIL]: The premise logically implies the hypothesis is true.\n"
            f"- [CONTRADICT]: The premise logically implies the hypothesis is false.\n"
            f"- [NEUTRAL]: The premise does not provide enough information."
        )

        try:
            res = await self.model_gateway.generate(
                model_name=self.nli_model,
                system_prompt="You are a high-precision NLI classifier. Output only the requested tag.",
                user_query=prompt,
                temperature=0.0,
                max_tokens=10,
                trace_id=self._trace_id,  # [M22] Propagate trace context
            )

            response = res.text.strip().upper()
            if "[ENTAIL]" in response or "ENTAIL" in response:
                return "ENTAIL"
            if "[CONTRADICT]" in response or "CONTRADICT" in response:
                return "CONTRADICT"
            return "NEUTRAL"

        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"NLI check failed: {e}")
            return "NEUTRAL"

    async def _resolve_contradiction(
        self,
        claim: str,
        contradictions: List[VerificationSource],
        entailments: List[VerificationSource],
    ) -> Dict[str, Any]:
        """
        Resolve contradictions using recency, authority, and divergence analysis.
        """
        # If no entailments, it's a straight contradiction
        if not entailments:
            return {
                "status": "CONTRADICTED",
                "reasoning": f"Claim explicitly contradicted by {len(contradictions)} source(s).",
            }

        # Use reasoning model to analyze the divergence
        divergence_prompt = (
            f"Claim: {claim}\n\n"
            f"Supporting Evidence:\n"
            + "\n".join([f"- {s.content} (Auth: {s.authority_score})" for s in entailments])
            + f"\n\nContradicting Evidence:\n"
            + "\n".join([f"- {s.content} (Auth: {s.authority_score})" for s in contradictions])
            + f"\n\nAnalyze the divergence. Determine if the contradiction is due to versioning, context, or a factual error. "
            f"Decide if the claim is still VERIFIED or remains CONTRADICTED. "
            f"Output your verdict as 'VERDICT: VERIFIED' or 'VERDICT: CONTRADICTED' followed by your reasoning."
        )

        try:
            res = await self.model_gateway.generate(
                model_name=self.nli_model,
                system_prompt="You are a Sovereign Resolution Engine. Resolve factual contradictions with extreme skepticism.",
                user_query=divergence_prompt,
                temperature=0.2,
                trace_id=self._trace_id,  # [M22] Propagate trace context
            )

            response = res.text
            if "VERDICT: VERIFIED" in response:
                return {"status": "VERIFIED", "reasoning": response}
            return {"status": "CONTRADICTED", "reasoning": response}

        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Contradiction resolution failed: {e}")
            return {
                "status": "CONTRADICTED",
                "reasoning": "Contradiction detected and resolution failed.",
            }
