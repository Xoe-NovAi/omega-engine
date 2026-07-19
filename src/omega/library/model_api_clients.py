# AP: AP-MODEL-API-v1.0.0
# Omega Engine — Model Registry API Clients (Artificial Analysis + HuggingFace Hub)
#
# Purpose: Enrich model registry with live benchmark scores, pricing,
#          performance metrics, and architecture parameters.
#
# Artificial Analysis API:
#   - Free tier: 100 req/day — headline indices, pricing, median performance
#   - Auth: x-api-key header
#   - Base: https://artificialanalysis.ai/api/v2
#
# HuggingFace Hub API:
#   - Public, no auth required for public models
#   - Base: https://huggingface.co/api/models/{model_id}
#   - Provides: config.json (architecture, params), safetensors (param counts),
#               pipeline_tag, lastModified, siblings

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod

import anyio
import httpx2 as httpx

logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class AAModelScore:
    """Artificial Analysis benchmark scores for a single model."""
    slug: str
    name: str
    creator: str
    release_date: Optional[str] = None
    reasoning_model: bool = False

    # Intelligence Indices (0-100 scale)
    intelligence_index: Optional[float] = None
    coding_index: Optional[float] = None
    agentic_index: Optional[float] = None
    multilingual_index: Optional[float] = None
    openness_index: Optional[float] = None

    # Individual benchmark scores (0-1 or Elo)
    mmlu_pro: Optional[float] = None
    gpqa_diamond: Optional[float] = None
    hle: Optional[float] = None
    livecodebench: Optional[float] = None
    scicode: Optional[float] = None
    math_500: Optional[float] = None
    aime: Optional[float] = None
    critpt: Optional[float] = None
    aa_lcr: Optional[float] = None
    aa_omniscience_accuracy: Optional[float] = None
    aa_omniscience_non_hallucination_rate: Optional[float] = None
    gdpval_aa_elo: Optional[float] = None
    tau_banking: Optional[float] = None
    terminalbench_v2_1: Optional[float] = None
    ifbench: Optional[float] = None

    # Pricing (USD per 1M tokens)
    price_input: Optional[float] = None
    price_output: Optional[float] = None
    price_blended_3_to_1: Optional[float] = None
    price_cache_hit: Optional[float] = None
    cost_per_task: Optional[float] = None

    # Performance
    median_output_tokens_per_second: Optional[float] = None
    median_ttft: Optional[float] = None  # time to first token
    median_end_to_end_response: Optional[float] = None

    # Metadata
    context_window_tokens: Optional[int] = None
    parameters_total: Optional[int] = None  # in billions
    parameters_active: Optional[int] = None  # in billions (for MoE)
    is_open_weights: Optional[bool] = None
    huggingface_url: Optional[str] = None
    modalities_input: Dict[str, bool] = field(default_factory=dict)
    modalities_output: Dict[str, bool] = field(default_factory=dict)

    # Provenance
    intelligence_index_version: Optional[float] = None
    fetched_at: Optional[str] = None
    source: str = "artificial_analysis"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HFModelConfig:
    """HuggingFace Hub model configuration extracted from config.json."""
    model_id: str
    model_type: Optional[str] = None
    architectures: List[str] = field(default_factory=list)

    # Architecture params
    hidden_size: Optional[int] = None
    num_hidden_layers: Optional[int] = None
    num_attention_heads: Optional[int] = None
    intermediate_size: Optional[int] = None
    vocab_size: Optional[int] = None
    max_position_embeddings: Optional[int] = None

    # MoE params
    num_local_experts: Optional[int] = None
    num_experts_per_tok: Optional[int] = None

    # Total parameters
    total_parameters: Optional[int] = None  # raw count from safetensors
    total_parameters_b: Optional[float] = None  # in billions

    # Metadata
    pipeline_tag: Optional[str] = None
    library_name: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    last_modified: Optional[str] = None
    downloads: Optional[int] = None
    likes: Optional[int] = None
    gated: Optional[bool] = None

    # Provenance
    fetched_at: Optional[str] = None
    source: str = "huggingface_hub"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ModelEnrichmentResult:
    """Combined enrichment from AA + HF Hub for a single model."""
    model_id: str
    aa_score: Optional[AAModelScore] = None
    hf_config: Optional[HFModelConfig] = None
    match_confidence: float = 0.0
    match_method: str = "none"  # slug, name, hf_url, fuzzy
    enrichment_fields: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================================
# BASE CLIENT
# ============================================================================

class BaseModelClient(ABC):
    """Abstract base for model registry API clients."""

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
        rate_limit_calls: int = 10,
        rate_limit_period: int = 60,
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self._last_call_time = 0.0
        self._call_count = 0
        self._rate_limit_calls = rate_limit_calls
        self._rate_limit_period = rate_limit_period

    async def _rate_limit(self) -> None:
        """Enforce rate limiting."""
        now = time.monotonic()
        if now - self._last_call_time < self._rate_limit_period / self._rate_limit_calls:
            wait = self._rate_limit_period / self._rate_limit_calls - (now - self._last_call_time)
            if wait > 0:
                await anyio.sleep(wait)
        self._last_call_time = time.monotonic()

    @abstractmethod
    async def search(self, query: str, **kwargs) -> List[Any]:
        """Search for models matching query."""
        ...

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Optional[Any]:
        """Get a single model by slug/ID."""
        ...


# ============================================================================
# ARTIFICIAL ANALYSIS CLIENT
# ============================================================================

class ArtificialAnalysisClient(BaseModelClient):
    """Client for Artificial Analysis Data API (artificialanalysis.ai/api/v2).

    Free tier: 100 requests/day.
    Provides: Intelligence Index, coding/agentic/math indices, individual
    benchmark scores, pricing, performance metrics, context window, parameters.
    """

    FREE_ENDPOINT = "/language/models/free"
    PRO_ENDPOINT = "/language/models"
    DETAIL_ENDPOINT = "/language/models/{slug}"

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = 30,
        tier: str = "free",  # "free" | "pro" | "commercial"
    ):
        super().__init__(
            base_url="https://artificialanalysis.ai/api/v2",
            api_key=api_key,
            timeout=timeout,
            rate_limit_calls=100 if tier == "free" else 500,
            rate_limit_period=86400,  # daily
        )
        self.tier = tier

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

    def _get_endpoint(self, detail: bool = False) -> str:
        if detail:
            return self.DETAIL_ENDPOINT
        if self.tier == "free" or not self.api_key:
            return self.FREE_ENDPOINT
        return self.PRO_ENDPOINT

    def _parse_model(self, item: Dict[str, Any], version: float = 4.1) -> AAModelScore:
        """Parse a single AA API model response into AAModelScore."""
        evals = item.get("evaluations", {})
        pricing = item.get("pricing", {})
        perf = item.get("performance", {})
        cost = item.get("artificial_analysis_intelligence_index_cost", {})
        params = item.get("parameters", {})
        modal_in = item.get("modalities", {}).get("input", {})
        modal_out = item.get("modalities", {}).get("output", {})
        licensing = item.get("licensing", {})

        cost_per_task = None
        if cost:
            cpt = cost.get("cost_per_task", {})
            if isinstance(cpt, dict):
                cost_per_task = cpt.get("total_cost")
            elif isinstance(cpt, (int, float)):
                cost_per_task = cpt

        return AAModelScore(
            slug=item.get("slug", ""),
            name=item.get("name", ""),
            creator=item.get("model_creator", {}).get("name", ""),
            release_date=item.get("release_date"),
            reasoning_model=item.get("reasoning_model", False),

            intelligence_index=evals.get("artificial_analysis_intelligence_index"),
            coding_index=evals.get("artificial_analysis_coding_index"),
            agentic_index=evals.get("artificial_analysis_agentic_index"),
            multilingual_index=evals.get("artificial_analysis_multilingual_index"),
            openness_index=evals.get("artificial_analysis_openness_index"),

            mmlu_pro=evals.get("mmlu_pro"),
            gpqa_diamond=evals.get("gpqa_diamond"),
            hle=evals.get("hle"),
            livecodebench=evals.get("livecodebench"),
            scicode=evals.get("scicode"),
            math_500=evals.get("math_500"),
            aime=evals.get("aime"),
            critpt=evals.get("critpt"),
            aa_lcr=evals.get("aa_lcr"),
            aa_omniscience_accuracy=evals.get("aa_omniscience_accuracy"),
            aa_omniscience_non_hallucination_rate=evals.get("aa_omniscience_non_hallucination_rate"),
            gdpval_aa_elo=evals.get("gdpval_aa_elo"),
            tau_banking=evals.get("tau_banking"),
            terminalbench_v2_1=evals.get("terminalbench_v2_1"),
            ifbench=evals.get("ifbench"),

            price_input=pricing.get("price_1m_input_tokens"),
            price_output=pricing.get("price_1m_output_tokens"),
            price_blended_3_to_1=pricing.get("price_1m_blended_3_to_1"),
            price_cache_hit=pricing.get("price_1m_cache_hit_tokens"),
            cost_per_task=cost_per_task,

            median_output_tokens_per_second=perf.get("median_output_tokens_per_second"),
            median_ttft=perf.get("median_time_to_first_token_seconds"),
            median_end_to_end_response=perf.get("median_end_to_end_response_time_seconds"),

            context_window_tokens=item.get("context_window_tokens"),
            parameters_total=params.get("total"),
            parameters_active=params.get("active"),
            is_open_weights=licensing.get("is_open_weights"),
            huggingface_url=item.get("huggingface_url"),
            modalities_input={k: v for k, v in modal_in.items() if isinstance(v, bool)},
            modalities_output={k: v for k, v in modal_out.items() if isinstance(v, bool)},

            intelligence_index_version=version,
        )

    async def search(self, query: str, **kwargs) -> List[AAModelScore]:
        """Search AA API — paginated model list. Query is a name/creator filter."""
        await self._rate_limit()
        endpoint = self._get_endpoint()
        url = f"{self.base_url}{endpoint}"

        all_models: List[AAModelScore] = []
        page = 1
        version = 4.1

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            while True:
                try:
                    resp = await client.get(
                        url,
                        headers=self._get_headers(),
                        params={"page": page},
                    )
                    if resp.status_code == 401:
                        logger.warning("AA API: Invalid or missing API key")
                        break
                    if resp.status_code == 403:
                        logger.warning("AA API: Tier does not cover this endpoint")
                        break
                    if resp.status_code == 429:
                        retry_after = int(resp.headers.get("Retry-After", 60))
                        logger.warning(f"AA API: Rate limited, retry after {retry_after}s")
                        await anyio.sleep(retry_after)
                        continue
                    resp.raise_for_status()
                    data = resp.json()
                    version = data.get("intelligence_index_version", 4.1)

                    for item in data.get("data", []):
                        model = self._parse_model(item, version)
                        # Filter by query (name or creator contains query)
                        q_lower = query.lower()
                        if (q_lower in model.name.lower()
                                or q_lower in model.creator.lower()
                                or q_lower in model.slug.lower()):
                            all_models.append(model)

                    pagination = data.get("pagination", {})
                    if not pagination.get("has_more", False):
                        break
                    page += 1
                    if page > pagination.get("total_pages", 1):
                        break

                except httpx.HTTPStatusError as e:
                    logger.error(f"AA API HTTP error: {e.response.status_code}")
                    break
                except httpx.RequestError as e:
                    logger.error(f"AA API request error: {e}")
                    break

        return all_models

    async def get_by_slug(self, slug: str) -> Optional[AAModelScore]:
        """Get a single model by AA slug."""
        await self._rate_limit()
        url = f"{self.base_url}{self.DETAIL_ENDPOINT.format(slug=slug)}"

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            try:
                resp = await client.get(url, headers=self._get_headers())
                if resp.status_code == 404:
                    logger.warning(f"AA API: Model '{slug}' not found")
                    return None
                resp.raise_for_status()
                data = resp.json()
                version = data.get("intelligence_index_version", 4.1)
                return self._parse_model(data.get("data", {}), version)
            except Exception as e:
                logger.error(f"AA API error fetching '{slug}': {e}")
                return None


# ============================================================================
# HUGGINGFACE HUB CLIENT
# ============================================================================

class HuggingFaceHubClient(BaseModelClient):
    """Client for HuggingFace Hub REST API (huggingface.co/api/models).

    Public models: No auth required.
    Provides: config.json (architecture, params), safetensors (param counts),
              pipeline_tag, lastModified, tags, downloads, likes.
    """

    BASE_URL = "https://huggingface.co/api/models"

    def __init__(self, timeout: int = 30):
        super().__init__(
            base_url=self.BASE_URL,
            timeout=timeout,
            rate_limit_calls=30,
            rate_limit_period=60,
        )

    def _parse_model(self, data: Dict[str, Any]) -> HFModelConfig:
        """Parse HF Hub API response into HFModelConfig."""
        config = data.get("config", {})
        safetensors = data.get("safetensors", {})

        # Extract total parameters from safetensors
        total_params = None
        total_params_b = None
        if safetensors:
            total_params = safetensors.get("total")
            if total_params:
                total_params_b = round(total_params / 1e9, 1)

        # Extract MoE params from config
        num_local_experts = config.get("num_local_experts")
        num_experts_per_tok = config.get("num_experts_per_tok")

        return HFModelConfig(
            model_id=data.get("modelId") or data.get("id", ""),
            model_type=config.get("model_type"),
            architectures=config.get("architectures", []),
            hidden_size=config.get("hidden_size"),
            num_hidden_layers=config.get("num_hidden_layers"),
            num_attention_heads=config.get("num_attention_heads"),
            intermediate_size=config.get("intermediate_size"),
            vocab_size=config.get("vocab_size"),
            max_position_embeddings=config.get("max_position_embeddings"),
            num_local_experts=num_local_experts,
            num_experts_per_tok=num_experts_per_tok,
            total_parameters=total_params,
            total_parameters_b=total_params_b,
            pipeline_tag=data.get("pipeline_tag"),
            library_name=data.get("library_name"),
            tags=data.get("tags", []),
            last_modified=data.get("lastModified"),
            downloads=data.get("downloads"),
            likes=data.get("likes"),
            gated=data.get("gated"),
        )

    async def search(self, query: str, **kwargs) -> List[HFModelConfig]:
        """Search HF Hub models — returns list of matching models."""
        await self._rate_limit()
        limit = kwargs.get("limit", 10)

        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
        ) as client:
            try:
                resp = await client.get(
                    self.base_url,
                    params={"search": query, "limit": limit, "sort": "downloads", "direction": "-1"},
                )
                resp.raise_for_status()
                models = resp.json()
                return [self._parse_model(m) for m in models[:limit]]
            except Exception as e:
                logger.error(f"HF Hub search error: {e}")
                return []

    async def get_by_slug(self, slug: str) -> Optional[HFModelConfig]:
        """Get a single model by HF model ID (org/name format).

        Handles 307 redirects (case sensitivity) automatically.
        """
        await self._rate_limit()

        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            max_redirects=5,
        ) as client:
            try:
                resp = await client.get(f"{self.base_url}/{slug}")
                if resp.status_code == 404:
                    logger.warning(f"HF Hub: Model '{slug}' not found")
                    return None
                if resp.status_code == 401:
                    logger.warning(f"HF Hub: Model '{slug}' requires authentication (gated)")
                    return None
                resp.raise_for_status()
                return self._parse_model(resp.json())
            except Exception as e:
                logger.error(f"HF Hub error fetching '{slug}': {e}")
                return None


# ============================================================================
# MODEL ENRICHMENT ORCHESTRATOR
# ============================================================================

class ModelEnrichmentOrchestrator:
    """Coordinates AA API + HF Hub to produce ModelEnrichmentResult.

    Matching strategy:
      1. AA slug ↔ HF model_id (exact)
      2. AA huggingface_url contains HF model_id
      3. Name/creator fuzzy match
    """

    def __init__(
        self,
        aa_client: Optional[ArtificialAnalysisClient] = None,
        hf_client: Optional[HuggingFaceHubClient] = None,
    ):
        self.aa = aa_client or ArtificialAnalysisClient()
        self.hf = hf_client or HuggingFaceHubClient()

    def _match_models(
        self,
        aa_score: AAModelScore,
        hf_models: List[HFModelConfig],
    ) -> tuple[Optional[HFModelConfig], float, str]:
        """Match AA model to HF model. Returns (config, confidence, method)."""
        # Strategy 1: Exact slug match
        for hf in hf_models:
            if aa_score.huggingface_url and hf.model_id in aa_score.huggingface_url:
                return hf, 0.95, "hf_url"

        # Strategy 2: Name/creator match
        for hf in hf_models:
            hf_name = hf.model_id.split("/")[-1].lower()
            aa_name = aa_score.name.lower().replace(" ", "-")
            if hf_name in aa_name or aa_name in hf_name:
                return hf, 0.8, "name_fuzzy"

        # Strategy 3: Slug match (AA slug vs HF model_id last part)
        for hf in hf_models:
            hf_name = hf.model_id.split("/")[-1].lower()
            if aa_score.slug.lower() == hf_name:
                return hf, 0.9, "slug"

        return None, 0.0, "none"

    async def enrich_from_aa(
        self,
        query: str,
        hf_model_id: Optional[str] = None,
    ) -> Optional[ModelEnrichmentResult]:
        """Enrich a model starting from AA search, optionally cross-referencing HF."""
        aa_models = await self.aa.search(query)
        if not aa_models:
            return None

        # Take best match
        aa_score = aa_models[0]

        # Cross-reference with HF
        hf_config = None
        match_confidence = 0.0
        match_method = "aa_only"

        if hf_model_id:
            hf_config = await self.hf.get_by_slug(hf_model_id)
            if hf_config:
                match_confidence = 0.95
                match_method = "direct_hf_id"
        else:
            # Search HF for cross-reference
            hf_results = await self.hf.search(query, limit=5)
            if hf_results:
                hf_config, match_confidence, match_method = self._match_models(
                    aa_score, hf_results
                )

        # Build enrichment fields list
        fields = []
        if aa_score.intelligence_index is not None:
            fields.append("intelligence_index")
        if aa_score.price_input is not None:
            fields.append("pricing")
        if aa_score.median_output_tokens_per_second is not None:
            fields.append("performance")
        if hf_config and hf_config.total_parameters:
            fields.append("parameters")
        if hf_config and hf_config.architectures:
            fields.append("architecture")

        return ModelEnrichmentResult(
            model_id=aa_score.slug,
            aa_score=aa_score,
            hf_config=hf_config,
            match_confidence=match_confidence,
            match_method=match_method,
            enrichment_fields=fields,
        )

    async def enrich_from_hf(
        self,
        hf_model_id: str,
    ) -> Optional[ModelEnrichmentResult]:
        """Enrich a model starting from HF Hub, optionally cross-referencing AA."""
        hf_config = await self.hf.get_by_slug(hf_model_id)
        if not hf_config:
            return None

        # Try to find on AA by name
        aa_score = None
        model_name = hf_config.model_id.split("/")[-1]
        aa_results = await self.aa.search(model_name)
        if aa_results:
            aa_score = aa_results[0]

        return ModelEnrichmentResult(
            model_id=hf_model_id,
            aa_score=aa_score,
            hf_config=hf_config,
            match_confidence=0.9 if aa_score else 0.0,
            match_method="aa_cross_ref" if aa_score else "hf_only",
            enrichment_fields=["architecture", "parameters", "downloads", "likes"],
        )
