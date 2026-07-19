#!/usr/bin/env python3
"""
Freshness Checker — Automated Model Registry Staleness Detection.

Monitors Hugging Face Hub (lastModified, sha, file changes) and 
Artificial Analysis (Intelligence Index version, evaluation dates)
to detect stale model registry entries.

Integrates with background_researcher loop or runs standalone via CLI.

Usage:
    # Run as module (for background_researcher integration)
    python -m src.omega.workers.freshness_checker --tier standard
    
    # Run as CLI script
    python scripts/check_model_freshness.py --tier critical --notify
    
    # Dry run
    python scripts/check_model_freshness.py --tier all --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

import httpx


# ============================================================================
# CONFIGURATION
# ============================================================================

DB_PATH = Path("config/model_registry/index.sqlite")
HF_API_BASE = "https://huggingface.co/api"
AA_API_BASE = "https://artificialanalysis.ai/api/v2/language"

# Staleness thresholds (days)
THRESHOLDS = {
    "capability": 90,      # AA Intelligence Index scores
    "parameter": 180,      # HF Hub parameter data
    "metadata": 30,        # HF Hub tags, pipeline_tag, description
    "validation": 7,       # Validation status
}

# Check frequency tiers
TIER_MODELS = {
    "critical": 10,   # Top 10 by usage/downloads
    "standard": 50,   # Next 40
    "low": 100,       # Rest
    "all": -1,        # All models
}

# Rate limiting
HF_REQUEST_DELAY = 0.1   # seconds between requests
AA_REQUEST_DELAY = 0.5   # seconds between requests


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class ModelFreshnessResult:
    """Result of freshness check for a single model."""
    model_id: str
    hf_model_id: Optional[str]
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # HF Hub signals
    hf_last_modified: Optional[datetime] = None
    hf_sha: Optional[str] = None
    hf_days_since_modified: Optional[int] = None
    hf_weight_files_changed: bool = False
    hf_pipeline_tag: Optional[str] = None
    hf_tags: list = field(default_factory=list)
    
    # AA signals
    aa_index_version: Optional[str] = None
    aa_intelligence_index: Optional[int] = None
    aa_last_evaluated: Optional[datetime] = None
    aa_days_since_eval: Optional[int] = None
    aa_model_in_leaderboard: bool = False
    
    # Staleness assessment
    capability_stale: bool = False
    parameter_stale: bool = False
    metadata_stale: bool = False
    overall_stale: bool = False
    staleness_reasons: list = field(default_factory=list)
    
    # Recommended actions
    needs_revalidation: bool = False
    needs_reenrichment: bool = False
    
    # Errors
    hf_error: Optional[str] = None
    aa_error: Optional[str] = None
    
    def to_dict(self) -> dict:
        d = asdict(self)
        # Convert datetime to ISO string
        for k, v in d.items():
            if isinstance(v, datetime):
                d[k] = v.isoformat()
        return d


@dataclass
class FreshnessReport:
    """Aggregate report for a freshness check run."""
    run_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    tier: str = "standard"
    models_checked: int = 0
    models_stale: int = 0
    models_errors: int = 0
    results: list = field(default_factory=list)
    
    @property
    def stale_rate(self) -> float:
        if self.models_checked == 0:
            return 0.0
        return self.models_stale / self.models_checked
    
    def to_dict(self) -> dict:
        d = asdict(self)
        for k, v in d.items():
            if isinstance(v, datetime):
                d[k] = v.isoformat()
        d["results"] = [r.to_dict() if isinstance(r, ModelFreshnessResult) else r for r in self.results]
        return d


# ============================================================================
# API CLIENTS
# ============================================================================

class HuggingFaceHubClient:
    """Minimal HF Hub API client for freshness signals."""
    
    def __init__(self, timeout: float = 30.0):
        self.client = httpx.Client(
            base_url=HF_API_BASE,
            timeout=timeout,
            headers={"User-Agent": "Omega-Engine-FreshnessChecker/1.0"}
        )
    
    def get_model_info(self, model_id: str) -> dict:
        """Fetch model info from HF Hub API."""
        resp = self.client.get(f"/models/{model_id}", follow_redirects=True)
        resp.raise_for_status()
        return resp.json()
    
    def parse_last_modified(self, data: dict) -> Optional[datetime]:
        """Parse lastModified string to datetime."""
        lm = data.get("lastModified")
        if not lm:
            return None
        try:
            return datetime.fromisoformat(lm.replace("Z", "+00:00"))
        except ValueError:
            return None
    
    def detect_weight_changes(self, data: dict, previous_sha: Optional[str]) -> bool:
        """Check if weight files (.safetensors, .bin) have changed."""
        if not previous_sha:
            return True
        current_sha = data.get("sha")
        return current_sha != previous_sha
    
    def close(self):
        self.client.close()


class ArtificialAnalysisClient:
    """Artificial Analysis API client for capability score freshness."""
    
    def __init__(self, api_key: Optional[str] = None, timeout: float = 30.0):
        self.api_key = api_key or os.getenv("AA_API_KEY")
        self.client = httpx.Client(
            base_url=AA_API_BASE,
            timeout=timeout,
            headers={
                "User-Agent": "Omega-Engine-FreshnessChecker/1.0",
                **({"x-api-key": self.api_key} if self.api_key else {})
            }
        )
    
    def get_leaderboard(self, free_tier: bool = True) -> list[dict]:
        """Fetch model leaderboard from AA."""
        endpoint = "/models/free" if free_tier else "/models"
        resp = self.client.get(endpoint)
        resp.raise_for_status()
        data = resp.json()
        return data.get("models", data) if isinstance(data, dict) else data
    
    def find_model(self, leaderboard: list[dict], model_id: str, hf_model_id: Optional[str]) -> Optional[dict]:
        """Find model in AA leaderboard by slug or HF URL."""
        model_id_lower = model_id.lower()
        
        for model in leaderboard:
            # Match by slug
            if model.get("slug", "").lower() == model_id_lower:
                return model
            
            # Match by HF URL
            if hf_model_id and model.get("huggingface_url"):
                if hf_model_id.lower() in model["huggingface_url"].lower():
                    return model
            
            # Fuzzy name match (last resort)
            if model_id_lower in model.get("name", "").lower():
                return model
        
        return None
    
    def parse_aa_model(self, model: dict) -> dict:
        """Extract freshness-relevant fields from AA model data."""
        return {
            "intelligence_index": model.get("intelligence_index"),
            "index_version": model.get("index_version", "v4.1"),
            "last_evaluated": model.get("last_evaluated"),
            "benchmarks": model.get("benchmarks", {}),
            "pricing": model.get("pricing", {}),
            "performance": model.get("performance", {}),
        }
    
    def close(self):
        self.client.close()


# ============================================================================
# FRESHNESS CHECKER CORE
# ============================================================================

class FreshnessChecker:
    """Main freshness checking logic."""
    
    def __init__(
        self,
        db_path: Path = DB_PATH,
        aa_api_key: Optional[str] = None,
        hf_client: Optional[HuggingFaceHubClient] = None,
        aa_client: Optional[ArtificialAnalysisClient] = None,
    ):
        self.db_path = db_path
        self.hf_client = hf_client or HuggingFaceHubClient()
        self.aa_client = aa_client or ArtificialAnalysisClient(api_key=aa_api_key)
        self._aa_leaderboard_cache: Optional[list] = None
    
    def get_models_to_check(self, tier: str) -> list[dict]:
        """Get models from DB for specified tier."""
        limit = TIER_MODELS.get(tier, 50)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if limit > 0:
                cursor = conn.execute(
                    """SELECT model_id, display_name, provider, platform, tier, status,
                              model_id as hf_model_id, hf_hub_last_modified, enrichment_last_run,
                              validation_status, last_validated,
                              cap_reasoning_score, cap_code_score, cap_knowledge_score,
                              cap_creative_score, cap_tool_use_score, cap_structured_score,
                              cap_multimodal_score,
                              benchmark_data_date, total_parameters, architecture
                       FROM models
                       WHERE status = 'active'
                       ORDER BY 
                           CASE tier WHEN 'T1' THEN 1 WHEN 'T2' THEN 2 WHEN 'T3' THEN 3 ELSE 4 END,
                           model_id
                       LIMIT ?""",
                    (limit,)
                )
            else:
                cursor = conn.execute(
                    """SELECT model_id, display_name, provider, platform, tier, status,
                              model_id as hf_model_id, hf_hub_last_modified, enrichment_last_run,
                              validation_status, last_validated,
                              cap_reasoning_score, cap_code_score, cap_knowledge_score,
                              cap_creative_score, cap_tool_use_score, cap_structured_score,
                              cap_multimodal_score,
                              benchmark_data_date, total_parameters, architecture
                       FROM models
                       WHERE status = 'active'
                       ORDER BY 
                           CASE tier WHEN 'T1' THEN 1 WHEN 'T2' THEN 2 WHEN 'T3' THEN 3 ELSE 4 END"""
                )
            rows = [dict(row) for row in cursor.fetchall()]
            
            # Map OpenRouter-style model IDs to HF model IDs
            for row in rows:
                row["hf_model_id"] = self._map_to_hf_model_id(row["model_id"], row["provider"])
            
            return rows
    
    def _map_to_hf_model_id(self, model_id: str, provider: str) -> Optional[str]:
        """Map OpenRouter/Omega model ID to HuggingFace model ID."""
        # Already a valid HF ID (contains / but not provider prefix like openrouter/)
        if "/" in model_id and not model_id.startswith(("openrouter/", "liquid/", "nvidia/", "google/", "anthropic/", "meta-llama/", "xai/", "qwen/", "minimax/", "nousresearch/", "arcee-ai/", "poolside/", "z-ai/", "cognitivecomputations/")):
            return model_id
        
        # Known mappings for local models
        local_mappings = {
            "gpt-oss-120b-local": "openai/gpt-oss-120b",
            "gpt-oss-20b-local": "openai/gpt-oss-20b",
            "nemotron-3-ultra-local": "nvidia/nemotron-3-ultra",
            "qwen-3.5-72b-local": "qwen/qwen-3.5-72b",
            "llama-4-scout-local": "meta-llama/llama-4-scout",
            "deepseek-v4-flash-local": "deepseek-ai/DeepSeek-V4-Flash",
        }
        
        if model_id in local_mappings:
            return local_mappings[model_id]
        
        # For cloud models, try to extract HF ID from provider
        if provider in ("openrouter", "opencode-zen", "cline", "google", "anthropic", "xai"):
            # These are cloud APIs, not HF models - skip HF check
            return None
        
        # Default: try the model_id as-is
        return model_id
    
    def get_aa_leaderboard(self) -> list[dict]:
        """Fetch and cache AA leaderboard."""
        if self._aa_leaderboard_cache is None:
            try:
                self._aa_leaderboard_cache = self.aa_client.get_leaderboard(free_tier=True)
            except Exception as e:
                print(f"⚠️  AA API error (using empty): {e}")
                self._aa_leaderboard_cache = []
        return self._aa_leaderboard_cache
    
    def check_model(self, model: dict) -> ModelFreshnessResult:
        """Run freshness check for a single model."""
        model_id = model["model_id"]
        hf_model_id = model.get("hf_model_id")
        result = ModelFreshnessResult(model_id=model_id, hf_model_id=hf_model_id)
        
        # --- HF Hub Check ---
        if hf_model_id:
            try:
                hf_data = self.hf_client.get_model_info(hf_model_id)
                
                result.hf_last_modified = self.hf_client.parse_last_modified(hf_data)
                result.hf_sha = hf_data.get("sha")
                result.hf_pipeline_tag = hf_data.get("pipeline_tag")
                result.hf_tags = hf_data.get("tags", [])
                
                if result.hf_last_modified:
                    result.hf_days_since_modified = (
                        result.checked_at - result.hf_last_modified
                    ).days
                
                # Check if weight files changed since last enrichment
                prev_sha = None  # Could store in DB for precise detection
                result.hf_weight_files_changed = self.hf_client.detect_weight_changes(
                    hf_data, prev_sha
                )
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    result.hf_error = f"Model not found on HF Hub: {hf_model_id}"
                elif e.response.status_code == 401:
                    result.hf_error = f"Gated model (auth required): {hf_model_id}"
                else:
                    result.hf_error = f"HF Hub API error: {e}"
            except Exception as e:
                result.hf_error = f"HF Hub check failed: {e}"
        
        # --- Artificial Analysis Check ---
        try:
            leaderboard = self.get_aa_leaderboard()
            if leaderboard:
                aa_model = self.aa_client.find_model(leaderboard, model_id, hf_model_id)
                if aa_model:
                    result.aa_model_in_leaderboard = True
                    parsed = self.aa_client.parse_aa_model(aa_model)
                    result.aa_intelligence_index = parsed["intelligence_index"]
                    result.aa_index_version = parsed["index_version"]
                    
                    le = parsed.get("last_evaluated")
                    if le:
                        try:
                            result.aa_last_evaluated = datetime.fromisoformat(
                                le.replace("Z", "+00:00")
                            )
                            result.aa_days_since_eval = (
                                result.checked_at - result.aa_last_evaluated
                            ).days
                        except ValueError:
                            pass
                else:
                    result.aa_error = "Model not found in AA leaderboard"
            else:
                result.aa_error = "AA leaderboard unavailable"
        except Exception as e:
            result.aa_error = f"AA check failed: {e}"
        
        # --- Staleness Assessment ---
        self._assess_staleness(result, model)
        
        return result
    
    def _assess_staleness(self, result: ModelFreshnessResult, model: dict) -> None:
        """Determine staleness based on thresholds."""
        now = result.checked_at
        
        # Capability scores stale?
        has_cap_scores = any([
            model.get("cap_reasoning_score"),
            model.get("cap_code_score"),
            model.get("cap_knowledge_score"),
            model.get("cap_creative_score"),
            model.get("cap_tool_use_score"),
            model.get("cap_structured_score"),
            model.get("cap_multimodal_score"),
        ])
        
        if has_cap_scores:
            # Check AA evaluation date
            if result.aa_days_since_eval is not None:
                if result.aa_days_since_eval > THRESHOLDS["capability"]:
                    result.capability_stale = True
                    result.staleness_reasons.append(
                        f"AA evaluation {result.aa_days_since_eval}d old (> {THRESHOLDS['capability']}d)"
                    )
            # Check benchmark_data_date
            elif model.get("benchmark_data_date"):
                try:
                    bdd = datetime.fromisoformat(model["benchmark_data_date"].replace("Z", "+00:00"))
                    days = (now - bdd).days
                    if days > THRESHOLDS["capability"]:
                        result.capability_stale = True
                        result.staleness_reasons.append(
                            f"Benchmark data {days}d old (> {THRESHOLDS['capability']}d)"
                        )
                except ValueError:
                    pass
            # Fallback: if in AA leaderboard but no eval date, assume stale after 90d
            elif result.aa_model_in_leaderboard and result.aa_days_since_eval is None:
                result.capability_stale = True
                result.staleness_reasons.append("AA model has no evaluation date")
        
        # Parameter data stale?
        if model.get("total_parameters"):
            if result.hf_days_since_modified is not None:
                if result.hf_days_since_modified > THRESHOLDS["parameter"]:
                    result.parameter_stale = True
                    result.staleness_reasons.append(
                        f"HF repo {result.hf_days_since_modified}d since modified (> {THRESHOLDS['parameter']}d)"
                    )
            # Also check enrichment_last_run
            elif model.get("enrichment_last_run"):
                try:
                    elr = datetime.fromisoformat(model["enrichment_last_run"].replace("Z", "+00:00"))
                    days = (now - elr).days
                    if days > THRESHOLDS["parameter"]:
                        result.parameter_stale = True
                        result.staleness_reasons.append(
                            f"Enrichment {days}d old (> {THRESHOLDS['parameter']}d)"
                        )
                except ValueError:
                    pass
        
        # Metadata stale?
        if result.hf_days_since_modified is not None:
            if result.hf_days_since_modified > THRESHOLDS["metadata"]:
                result.metadata_stale = True
                result.staleness_reasons.append(
                    f"HF metadata {result.hf_days_since_modified}d old (> {THRESHOLDS['metadata']}d)"
                )
        
        # Overall stale?
        result.overall_stale = (
            result.capability_stale or 
            result.parameter_stale or 
            result.metadata_stale
        )
        
        # Recommended actions
        result.needs_revalidation = result.overall_stale
        result.needs_reenrichment = result.capability_stale or result.parameter_stale
    
    def update_staleness(self, results: list[ModelFreshnessResult]) -> int:
        """Update validation_status in DB, return count of newly stale models."""
        newly_stale = 0
        
        with sqlite3.connect(self.db_path) as conn:
            for r in results:
                if not r.overall_stale:
                    continue
                
                # Check current status
                cursor = conn.execute(
                    "SELECT validation_status FROM models WHERE model_id = ?",
                    (r.model_id,)
                )
                row = cursor.fetchone()
                current_status = row[0] if row else None
                
                if current_status != "stale":
                    newly_stale += 1
                
                # Update
                conn.execute(
                    """UPDATE models SET 
                        validation_status = ?,
                        validation_errors = ?,
                        last_validated = ?,
                        hf_hub_last_modified = ?,
                        enrichment_last_run = datetime('now')
                       WHERE model_id = ?""",
                    (
                        "stale",
                        json.dumps(r.staleness_reasons),
                        r.checked_at.isoformat(),
                        r.hf_last_modified.isoformat() if r.hf_last_modified else None,
                        r.model_id
                    )
                )
            conn.commit()
        
        return newly_stale
    
    def send_hivemind_notification(self, report: FreshnessReport) -> Optional[str]:
        """Send Hivemind handoff for stale models."""
        stale_models = [r for r in report.results if r.overall_stale]
        if not stale_models:
            return None
        
        try:
            # Import here to avoid circular dependency
            from omega_hub import hivemind_submit_handoff
            
            packet_id = f"freshness_{report.run_id}"
            
            hivemind_submit_handoff(
                target_channel="opencode",
                target_entity="researcher",
                source_channel="scheduler",
                source_entity="kali",
                task=f"Re-validate {len(stale_models)} stale models: {', '.join(m.model_id for m in stale_models[:5])}{'...' if len(stale_models) > 5 else ''}",
                context=f"Freshness checker ({report.tier} tier) detected staleness in {len(stale_models)} models",
                priority=1 if report.tier == "critical" else 0,
                metadata={
                    "stale_models": [
                        {"model_id": m.model_id, "reasons": m.staleness_reasons}
                        for m in stale_models
                    ],
                    "check_run_at": report.started_at.isoformat(),
                    "tier": report.tier,
                    "packet_id": packet_id
                }
            )
            return packet_id
        except Exception as e:
            print(f"⚠️  Hivemind notification failed: {e}")
            return None
    
    def run_check(self, tier: str = "standard", notify: bool = False, dry_run: bool = False) -> FreshnessReport:
        """Run freshness check for specified tier."""
        run_id = f"{tier}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        report = FreshnessReport(
            run_id=run_id,
            started_at=datetime.now(timezone.utc),
            tier=tier
        )
        
        print(f"🔍 Freshness check: {tier} tier (run_id: {run_id})")
        
        models = self.get_models_to_check(tier)
        print(f"   Models to check: {len(models)}")
        
        for i, model in enumerate(models, 1):
            model_id = model["model_id"]
            print(f"   [{i}/{len(models)}] Checking {model_id}...", end=" ")
            
            result = self.check_model(model)
            report.results.append(result)
            report.models_checked += 1
            
            if result.overall_stale:
                report.models_stale += 1
                print(f"⚠️  STALE ({', '.join(result.staleness_reasons[:2])})")
            elif result.hf_error or result.aa_error:
                report.models_errors += 1
                print(f"⚠️  ERRORS (HF: {result.hf_error is not None}, AA: {result.aa_error is not None})")
            else:
                print("✅ fresh")
            
            # Rate limiting
            if model.get("hf_model_id"):
                time.sleep(HF_REQUEST_DELAY)
            time.sleep(AA_REQUEST_DELAY)
        
        report.completed_at = datetime.now(timezone.utc)
        
        if not dry_run:
            newly_stale = self.update_staleness(report.results)
            print(f"\n📊 Results: {report.models_checked} checked, {report.models_stale} stale ({newly_stale} newly stale), {report.models_errors} errors")
            
            if notify and newly_stale > 0:
                packet_id = self.send_hivemind_notification(report)
                if packet_id:
                    print(f"📬 Hivemind notification sent: {packet_id}")
        else:
            print(f"\n📊 DRY-RUN: {report.models_checked} checked, {report.models_stale} would be stale, {report.models_errors} errors")
        
        return report
    
    def close(self):
        """Close API clients."""
        self.hf_client.close()
        self.aa_client.close()


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(description="Model Registry Freshness Checker")
    parser.add_argument("--tier", choices=["critical", "standard", "low", "all"], 
                        default="standard", help="Check tier")
    parser.add_argument("--notify", action="store_true", 
                        help="Send Hivemind notification for stale models")
    parser.add_argument("--dry-run", action="store_true", 
                        help="Run checks without updating DB")
    parser.add_argument("--json", action="store_true", 
                        help="Output JSON report")
    parser.add_argument("--db", default=str(DB_PATH), 
                        help=f"Database path (default: {DB_PATH})")
    parser.add_argument("--aa-api-key", default=os.getenv("AA_API_KEY"),
                        help="Artificial Analysis API key (or set AA_API_KEY env)")
    
    args = parser.parse_args()
    
    if not Path(args.db).exists():
        print(f"❌ Database not found: {args.db}")
        return 1
    
    checker = FreshnessChecker(
        db_path=Path(args.db),
        aa_api_key=args.aa_api_key
    )
    
    try:
        report = checker.run_check(
            tier=args.tier,
            notify=args.notify,
            dry_run=args.dry_run
        )
        
        if args.json:
            print(json.dumps(report.to_dict(), indent=2))
        
        return 0 if report.models_errors == 0 else 1
    finally:
        checker.close()


if __name__ == "__main__":
    sys.exit(main())