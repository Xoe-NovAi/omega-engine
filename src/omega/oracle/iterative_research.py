"""Iterative Research Loops — Cognitive retrieval with gap analysis.
# [id-soft: quake-1996] Sovereign-Symmetry — iterative cognitive loop
AP: AP-ITERATIVE-RESEARCH-v1.0.0
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from ..memory_store import get_memory_store
from .search import SovereignSearcher
from .model_gateway import ModelGateway
from .security import TaintedData, TDPGate
from .skeptical_verifier import SkepticalVerifier, VerificationResult

logger = logging.getLogger(__name__)

class IterativeResearcher:
    """Implements the Iterative Research Loop (H3-C1).
    
    Instead of a single search, this component performs a cycle of:
    Search -> Gap Analysis -> Refinement -> Search.
    
    This ensures that complex queries are fully answered by identifying 
    missing information and iteratively filling the gaps.
    """
    
    def __init__(self, model_gateway: ModelGateway, searcher: Optional[SovereignSearcher] = None, verifier: Optional[SkepticalVerifier] = None):
        self.model_gateway = model_gateway
        self.searcher = searcher or SovereignSearcher(get_memory_store())
        self.verifier = verifier
        self.max_iterations = 3
        self.confidence_threshold = 0.8

    async def research(
        self, 
        query: str, 
        entity_name: str, 
        max_iterations: Optional[int] = None,
        min_confidence: float = 0.8
    ) -> Tuple[str, List[TaintedData]]:
        """Execute an iterative research loop to answer a query.
        
        Returns a tuple of (final_synthesis, all_gathered_evidence).
        """
        current_query = query
        all_evidence: List[TaintedData] = []
        iteration = 0
        
        while iteration < (max_iterations or self.max_iterations):
            iteration += 1
            logger.info(f"Research iteration {iteration}/{self.max_iterations} for query: {current_query}")
            
            # 1. Perform search
            # Note: SovereignSearcher.search_knowledge uses hybrid FTS+Vector
            # We need the embedding for semantic search, which is handled inside searcher.search_knowledge
            # but we must ensure the searcher has access to the embedding manager.
            results = await self.searcher.search_knowledge(entity_name, current_query)
            all_evidence.extend(results)
            
            # 2. Gap Analysis
            # We ask the model to evaluate the gathered evidence against the original query.
            analysis_prompt = self._build_gap_analysis_prompt(query, current_query, results)
            
            # Use a high-reasoning model for gap analysis
            res = await self.model_gateway.generate(
                model_name="qwen3-4b-think", # Prefer thinking models for analysis
                system_prompt="You are a Sovereign Research Auditor. Your goal is to identify gaps in provided evidence.",
                user_query=analysis_prompt,
                temperature=0.2,
            )
            analysis_text = res.text
            
            # 3. Parse Analysis
            # We expect the model to return either "SUFFICIENT" or a refined query.
            if "SUFFICIENT" in analysis_text.upper():
                logger.info(f"Research converged at iteration {iteration}.")
                break
            
            # Extract refined query (assuming the model provides it after a specific marker)
            refined_query = self._extract_refined_query(analysis_text)
            if not refined_query or refined_query == current_query:
                logger.info(f"No further refinement possible at iteration {iteration}. Converging.")
                break
                
            current_query = refined_query
            
        # 4. Final Synthesis
        synthesis = await self._synthesize_final_answer(query, all_evidence)
        
        return synthesis, all_evidence

    def _build_gap_analysis_prompt(self, original_query: str, current_query: str, results: List[TaintedData]) -> str:
        """Build a prompt for the model to perform gap analysis."""
        evidence_block = ""
        for i, res in enumerate(results, 1):
            evidence_block += f"Source {i}: {res.content}\n\n"
            
        return (
            f"Original Goal: {original_query}\n"
            f"Current Search Query: {current_query}\n\n"
            f"Gathered Evidence:\n{evidence_block}\n"
            "--- \n"
            "Task: Analyze the evidence. Is it sufficient to answer the Original Goal completely and accurately?\n"
            "1. If YES, respond with 'SUFFICIENT' and a brief summary of why.\n"
            "2. If NO, identify exactly what is missing or contradictory, and provide a REFINED SEARCH QUERY to find that specific information.\n"
            "Format your response as:\n"
            "STATUS: [SUFFICIENT | INCOMPLETE]\n"
            "GAPS: [List missing info]\n"
            "REFINED_QUERY: [The new search query]"
        )

    def _extract_refined_query(self, analysis_text: str) -> Optional[str]:
        """Extract the REFINED_QUERY from the model's analysis."""
        match = re.search(r"REFINED_QUERY:\s*(.*)", analysis_text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    async def _synthesize_final_answer(self, query: str, evidence: List[TaintedData]) -> str:
        """Synthesize all gathered evidence into a final, verified answer."""
        if not evidence:
            return "No relevant evidence was found to answer the query."
            
        # De-duplicate and format evidence
        unique_content = []
        seen = set()
        for res in evidence:
            if res.content not in seen:
                unique_content.append(f"Source: {res.source}\nContent: {res.content}")
                seen.add(res.content)
        
        evidence_block = "\n\n".join(unique_content)
        
        synthesis_prompt = (
            f"Original Query: {query}\n\n"
            f"Gathered Evidence:\n{evidence_block}\n\n"
            "--- \n"
            "Task: Synthesize a comprehensive, accurate, and verified answer based ONLY on the provided evidence. "
            "If the evidence is contradictory, highlight the contradiction. "
            "If the evidence is insufficient, state what is still unknown. "
            "Cite your sources (e.g., [Source 1])."
        )
        
        res = await self.model_gateway.generate(
            model_name="gemma-4-31b-it", # Use a high-capacity model for synthesis
            system_prompt="You are a Sovereign Synthesis Engine. Your goal is to produce a verified, evidence-based answer.",
            user_query=synthesis_prompt,
            temperature=0.3,
        )
        response_text = res.text
        
        # --- SKEPTICAL VERIFICATION STEP ---
        if self.verifier:
            # 1. Extract key claims for verification
            claims_prompt = (
                f"Extract the top 3 most critical factual claims from the following synthesis. "
                f"Output each claim on a new line, starting with 'CLAIM: '.\n\n"
                f"Synthesis:\n{response_text}"
            )
            res = await self.model_gateway.generate(
                model_name="qwen3-4b-think",
                system_prompt="You are a claim extractor. Extract only factual, verifiable claims.",
                user_query=claims_prompt,
                temperature=0.0
            )
            claims_text = res.text
            
            claims = [line.replace("CLAIM: ", "").strip() for line in claims_text.splitlines() if "CLAIM:" in line]
            
            if claims:
                verification_results = []
                # Convert TaintedData to the format expected by SkepticalVerifier
                formatted_evidence = [
                    {"content": res.content, "source_id": res.source} for res in evidence
                ]
                
                for claim in claims:
                    res = await self.verifier.verify(claim, formatted_evidence)
                    verification_results.append(f"- {claim}: {res.status} ({res.reasoning})")
                
                if verification_results:
                    response_text += "\n\n--- 🛡️ SKEPTICAL VERIFICATION ---\n" + "\n".join(verification_results)
        
        return response_text
