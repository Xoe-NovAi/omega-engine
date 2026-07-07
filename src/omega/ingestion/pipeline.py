# AP: AP-INGESTION-PIPELINE-v1.0.0
"""
Sovereign Ingestion Pipeline — Orchestrating entity deepening.
"""

# DocRef: docs/architecture/SOVEREIGN_DATA_FLOW.md
import json
import time
import uuid
import anyio
import logging
import pybreaker
from typing import List, Optional, AsyncGenerator, Dict, Any
from pathlib import Path
from datetime import datetime, timezone

from .ingestion_types import (
    IngestionConfig, IngestionResult, ExtractionSchema, 
    CircuitBreakerState, IngestionError, SovereigntyError, 
    ProviderServerError, TransportError, SchemaError,
    BudgetExceededError, SentryFailure
)
from .extractors import BaseExtractor, GoogleExtractor
from .persistence import IngestionPersistence
from .sources import FileSource
from .guards import SovereignSentry, BudgetGuard
from .scraper import SovereignScraper
from .worker import SovereignWorker
from .verifier import TriangulationVerifier
from src.omega.archive.cas import CASArchiver
from src.omega.library.curator import CurationPipeline
from src.omega.library.extractor import ExtractedContent
from src.omega.library.enrichment import EnrichmentEngine

logger = logging.getLogger(__name__)

class IngestionCircuitBreaker:
    """Sovereign Circuit Breaker for the Ingestion Pipeline."""
    def __init__(self, fail_max: int = 5, reset_timeout: int = 300):
        self.breaker = pybreaker.CircuitBreaker(fail_max=fail_max, reset_timeout=reset_timeout)
        self.consecutive_failures = 0

    def can_proceed(self) -> bool:
        return self.breaker.current_state != "open"

    def record_success(self):
        self.consecutive_failures = 0

    def record_failure(self, error: Exception):
        self.consecutive_failures += 1

    def call(self, func, *args, **kwargs):
        return self.breaker.call(func, *args, **kwargs)

class ResilienceContext:
    """
    Unified resilience stack for the Ingestion Pipeline.
    Injects Sentry + Budget + Guard + Verifier into both run_source and _process_job.
    
    This eliminates the "divergent resilience stacks" between the Pipeline and Worker.
    """
    def __init__(
        self,
        config: IngestionConfig,
        breaker: IngestionCircuitBreaker,
        sentry: SovereignSentry,
        budget: BudgetGuard,
        verifier: TriangulationVerifier,
        resource_guard=None
    ):
        self.config = config
        self.breaker = breaker
        self.sentry = sentry
        self.budget = budget
        self.verifier = verifier
        self.resource_guard = resource_guard

    async def pre_flight_check(self) -> bool:
        """Runs pre-flight checks before processing a source."""
        if not self.breaker.can_proceed():
            logger.warning("Circuit breaker open, skipping source")
            return False
        
        # Run sentry probe (can be skipped for worker jobs)
        if self.sentry:
            try:
                await self.sentry.probe()
            except SentryFailure as e:
                logger.error(f"Sentry probe failed: {e}")
                return False
        
        return True

    def check_budget(self, estimated_tokens: int) -> bool:
        """Checks if we have budget remaining."""
        if self.budget:
            return self.budget.check_budget(estimated_tokens)
        return True

    def update_spend(self, tokens: int):
        """Updates the budget spend."""
        if self.budget:
            self.budget.update_spend(tokens)

    async def verify_web_content(self, t1_result: Dict, t3_result: Dict, domain_key: Optional[str] = None):
        """Verifies web content using the Triangulation Verifier."""
        if self.verifier:
            return await self.verifier.verify(t1_result, t3_result, domain_key)
        return None

    async def acquire_resource(self):
        """Acquires the resource guard (if available)."""
        if self.resource_guard:
            return await self.resource_guard.acquire()
        return True

    async def release_resource(self):
        """Releases the resource guard (if available)."""
        if self.resource_guard:
            await self.resource_guard.release()

class IngestionPipeline:
    """
    Orchestrates the full ingestion flow:
    Sentry Probe -> Budget Check -> Guarded Extraction -> Triangulation -> Persistence
    """
    
    def __init__(self, config: IngestionConfig, extractor: BaseExtractor):
        self.config = config
        self.extractor = extractor
        self.persistence = IngestionPersistence(config.entity_name)
        self.breaker = IngestionCircuitBreaker()
        self.sentry = SovereignSentry(config)
        self.budget = BudgetGuard(config)
        self.verifier = TriangulationVerifier(EnrichmentEngine())
        self.curation = CurationPipeline()
        self.enrichment = EnrichmentEngine()
        self.cas = CASArchiver()
        self.scraper = SovereignScraper(cas_archiver=self.cas)
        
        # Unified Resilience Context
        self.resilience = ResilienceContext(
            config=config,
            breaker=self.breaker,
            sentry=self.sentry,
            budget=self.budget,
            verifier=self.verifier
        )


    async def run_source(self, source: Any) -> Optional[IngestionResult]:
        """Processes a single source through the resilience ladder."""
        # Use unified resilience context
        if not await self.resilience.pre_flight_check():
            return None

        # Handle both FileSource and URL strings
        if hasattr(source, 'read'):
            source_name, text = await source.read()
        else:
            source_name = source
            text = source # Assume it's a URL

        trace_id = f"ingest_{uuid.uuid4().hex[:12]}"
        
        print(f"\n🚀 Ingesting: {source_name} ({len(text) if isinstance(text, str) else 'URL'} chars)")
        print(f"Model: {self.config.model_name} | Budget: {self.budget.get_status()}")
        print("-" * 60)
        
        t0 = time.time()
        
        try:
            # 1. Web Ingestion Path (Sovereign-Sieve)
            if source_name.startswith(("http://", "https://")):
                # T1: Fast Scrape
                t1_res = await self.scraper.scrape(source_name, tier="fast")
                if not t1_res.success:
                    raise TransportError(f"T1 Fast Scrape failed: {t1_res.error}")
                
                # T3: Deep Scrape (Sovereign-Sieve)
                t3_res = await self.scraper.scrape(source_name, tier="deep")
                if not t3_res.success:
                    logger.warning(f"T3 Deep Scrape failed for {source_name}, falling back to T1")
                    t3_res = t1_res # Fallback to T1 for triangulation
                
                # Triangulation Verification using resilience context
                verification = await self.resilience.verify_web_content(
                    t1_result={"content": t1_res.content, "metadata": t1_res.metadata},
                    t3_result={"content": t3_res.content, "metadata": t3_res.metadata}
                )
                
                if verification and not verification.is_verified:
                    print(f"⚠️  Triangulation failed for {source_name}. Confidence: {verification.confidence_score:.2f}")
                    # In a full implementation, we would trigger T2 Surgical here.
                    if verification.confidence_score < 0.4:
                        return None

                # Store raw content in CAS (Sovereign Archiving)
                raw_content = t3_res.content.encode('utf-8')
                cid = await self.cas.store(raw_content)
                text = t3_res.content
                
            else:
                # Standard File Path
                # 1. Pre-Extraction Quality Gate (Right Approximation)
                temp_content = ExtractedContent(
                    source=source_name,
                    source_type="file",
                    title=source_name,
                    body=text
                )
                curated = await self.curation._curate(temp_content)
                quality_score = curated.quality_score
                domain = curated.domain
                
                if quality_score < 0.3:
                    print(f"⚠️  Low quality source ({quality_score:.2f} < 0.3). Skipping extraction.")
                    return None
                
                print(f"💎 Quality Score: {quality_score:.2f} | Domain: {domain}")

            # 2. Budget Guard (via resilience context)
            if not self.resilience.check_budget(estimated_tokens=len(text)//4 + 1000):
                raise BudgetExceededError(f"Hard budget limit of ${self.config.max_budget_usd} reached.")

            # 3. Guarded Extraction (via resilience context breaker)
            extraction = await self.resilience.breaker.call(self.extractor.extract, text, self.config)
            
            # 4. Validation Gate (Standard Quality Check)
            # We still use a basic validation to ensure the LLM didn't hallucinate a failure
            if not extraction.technical_facts and not extraction.personality_patterns:
                print(f"⚠️  Extraction empty for {source_name}. Marking as corrupt.")
                self.resilience.breaker.record_failure(SchemaError("Extraction empty"))
                return None
            
            latency = time.time() - t0
            
            # 5. Enrichment (Sovereign Library Layer)
            enrichment_meta = await self.enrichment.enrich(
                title=extraction.technical_facts[0] if extraction.technical_facts else source_name,
                authors=extraction.personality_patterns[0] if extraction.personality_patterns else None
            )
            
            # 6. Persistence
            session_id = await self.persistence.persist_extraction(
                source_name=source_name,
                model_name=self.config.model_name,
                extraction_data=extraction.to_dict(),
                latency_s=latency,
                trace_id=trace_id,
                quality_score=0.8, # Default for verified web content
                domain="web",
                enrichment=enrichment_meta.to_dict()
            )
            
            # Update budget based on actual usage (approximate)
            self.resilience.update_spend(tokens=len(text)//4 + 1000)
            self.resilience.breaker.record_success()
            
            print(f"✅ Persisted to session {session_id}")
            print(f"Items: {sum(len(v) if isinstance(v, list) else 0 for v in extraction.to_dict().values())}")
            print(f"Latency: {latency:.2f}s")
            
            return IngestionResult(
                source_name=source_name,
                model_name=self.config.model_name,
                extraction=extraction,
                latency_s=latency,
                input_chars=len(text),
                trace_id=trace_id,
                quality_score=0.8,
                domain="web"
            )
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Ingestion failed for {source_name}: {e}")
            return None
    async def run_batch(self, sources: List[FileSource]) -> List[IngestionResult]:
        """Processes a batch of sources with pre-flight sentry and circuit breaker."""
        # 1. Pre-flight Sentry Probe via resilience context
        if not await self.resilience.pre_flight_check():
            print("🛑 [SENTRY HALT] Pre-flight check failed")
            return []

        results = []
        for source in sources:
            if not self.resilience.breaker.can_proceed():
                print("\n🛑 [CIRCUIT BREAKER TRIPPED] Halting batch ingestion.")
                break
                
            res = await self.run_source(source)
            if res:
                results.append(res)
        return results

async def create_pipeline(config: IngestionConfig) -> IngestionPipeline:
    """Factory to create a pipeline based on the model."""
    if "google" in config.model_name or "gemma" in config.model_name:
        extractor = GoogleExtractor(config.api_key)
    else:
        raise NotImplementedError(f"No extractor implemented for model {config.model_name}")
        
    return IngestionPipeline(config, extractor)
