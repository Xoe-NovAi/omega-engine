#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""Enrich Model Registry with Live Data from Artificial Analysis + HuggingFace Hub.

Usage:
    # Enrich a single model
    python scripts/enrich_model_registry.py --model deepseek-v4-flash --hf-id deepseek-ai/DeepSeek-V4-Flash

    # Enrich all models in registry directory
    python scripts/enrich_model_registry.py --batch config/model_registry/models/

    # Dry run (no file writes)
    python scripts/enrich_model_registry.py --model gemma-4-31b --dry-run

    # Fetch full AA leaderboard snapshot
    python scripts/enrich_model_registry.py --snapshot --output data/aa_snapshot.json

Environment:
    AA_API_KEY   — Artificial Analysis API key (optional, free tier works without it)
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import anyio

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from omega.library.model_api_clients import (
    ArtificialAnalysisClient,
    HuggingFaceHubClient,
    ModelEnrichmentOrchestrator,
    ModelEnrichmentResult,
    AAModelScore,
    HFModelConfig,
)

logger = logging.getLogger("enrich_model_registry")


# ============================================================================
# YAML HELPERS (lightweight, no pyyaml dependency for script)
# ============================================================================

def _read_yaml_file(path: Path) -> Optional[str]:
    """Read a YAML file as text."""
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


def _inject_fields(base_yaml: str, new_fields: Dict[str, Any]) -> str:
    """Inject new YAML fields after the 'parameters:' block in a model card.

    This is a simple text-based injection, not a full YAML parser.
    It looks for existing keys and updates them, or appends new fields.
    """
    lines = base_yaml.split("\n")
    result = []
    injected = set()

    for line in lines:
        result.append(line)
        # Inject after parameters block or at end
        stripped = line.strip()
        if stripped.startswith("parameters:") and "total" not in injected:
            result.append(f"  # Enriched from Artificial Analysis + HF Hub")
            result.append(f"  enriched_at: \"{new_fields.get('enriched_at', '')}\"")
            if "total_b" in new_fields:
                result.append(f"  # total_b: {new_fields['total_b']}  # from AA API")
            injected.add("total")

    # Append any fields that weren't injected inline
    extra_fields = []
    for k, v in new_fields.items():
        if k not in injected:
            if isinstance(v, str):
                extra_fields.append(f"{k}: \"{v}\"")
            elif isinstance(v, bool):
                extra_fields.append(f"{k}: {'true' if v else 'false'}")
            elif v is not None:
                extra_fields.append(f"{k}: {v}")

    if extra_fields:
        result.append("")
        result.append("# ── Enrichment Data (auto-generated) ──")
        for field_line in extra_fields:
            result.append(field_line)

    return "\n".join(result)


# ============================================================================
# CORE ENRICHMENT LOGIC
# ============================================================================

def build_enrichment_fields(
    result: ModelEnrichmentResult,
) -> Dict[str, Any]:
    """Convert ModelEnrichmentResult to injectable fields."""
    fields: Dict[str, Any] = {}
    fields["enriched_at"] = datetime.now(timezone.utc).isoformat()

    if result.aa_score:
        aa = result.aa_score
        if aa.intelligence_index is not None:
            fields["aa_intelligence_index"] = aa.intelligence_index
        if aa.coding_index is not None:
            fields["aa_coding_index"] = aa.coding_index
        if aa.agentic_index is not None:
            fields["aa_agentic_index"] = aa.agentic_index
        if aa.price_input is not None:
            fields["aa_price_input_per_1m"] = aa.price_input
        if aa.price_output is not None:
            fields["aa_price_output_per_1m"] = aa.price_output
        if aa.cost_per_task is not None:
            fields["aa_cost_per_task"] = aa.cost_per_task
        if aa.median_output_tokens_per_second is not None:
            fields["aa_median_tps"] = aa.median_output_tokens_per_second
        if aa.median_ttft is not None:
            fields["aa_median_ttft"] = aa.median_ttft
        if aa.context_window_tokens is not None:
            fields["aa_context_window"] = aa.context_window_tokens
        if aa.is_open_weights is not None:
            fields["aa_open_weights"] = aa.is_open_weights
        if aa.huggingface_url:
            fields["aa_huggingface_url"] = aa.huggingface_url

        # Individual benchmarks (only if non-None)
        benchmarks = {}
        for attr in [
            "mmlu_pro", "gpqa_diamond", "hle", "livecodebench", "scicode",
            "math_500", "aime", "critpt", "aa_lcr", "gdpval_aa_elo",
            "tau_banking", "terminalbench_v2_1", "ifbench",
        ]:
            val = getattr(aa, attr, None)
            if val is not None:
                benchmarks[attr] = val
        if benchmarks:
            fields["aa_benchmarks"] = benchmarks

        fields["aa_source"] = f"artificial_analysis_v{aa.intelligence_index_version or '4.1'}"

    if result.hf_config:
        hf = result.hf_config
        if hf.total_parameters_b is not None:
            fields["hf_total_parameters_b"] = hf.total_parameters_b
        if hf.architectures:
            fields["hf_architectures"] = hf.architectures
        if hf.model_type:
            fields["hf_model_type"] = hf.model_type
        if hf.num_local_experts is not None:
            fields["hf_num_local_experts"] = hf.num_local_experts
        if hf.num_experts_per_tok is not None:
            fields["hf_num_experts_per_tok"] = hf.num_experts_per_tok
        if hf.pipeline_tag:
            fields["hf_pipeline_tag"] = hf.pipeline_tag
        if hf.downloads is not None:
            fields["hf_downloads"] = hf.downloads
        if hf.last_modified:
            fields["hf_last_modified"] = hf.last_modified

        fields["hf_source"] = f"huggingface_hub_{hf.model_id}"

    fields["match_confidence"] = round(result.match_confidence, 2)
    fields["match_method"] = result.match_method

    return fields


def build_enrichment_report(
    results: List[ModelEnrichmentResult],
) -> Dict[str, Any]:
    """Build a JSON report of enrichment results."""
    enriched = []
    skipped = []

    for r in results:
        entry = {
            "model_id": r.model_id,
            "match_confidence": round(r.match_confidence, 2),
            "match_method": r.match_method,
            "enrichment_fields": r.enrichment_fields,
        }
        if r.aa_score:
            entry["aa_intelligence_index"] = r.aa_score.intelligence_index
            entry["aa_creator"] = r.aa_score.creator
            entry["aa_price_input"] = r.aa_score.price_input
        if r.hf_config:
            entry["hf_model_id"] = r.hf_config.model_id
            entry["hf_params_b"] = r.hf_config.total_parameters_b
            entry["hf_architecture"] = r.hf_config.architectures

        if r.enrichment_fields:
            enriched.append(entry)
        else:
            skipped.append(entry)

    return {
        "enriched_at": datetime.now(timezone.utc).isoformat(),
        "total_processed": len(results),
        "enriched_count": len(enriched),
        "skipped_count": len(skipped),
        "enriched": enriched,
        "skipped": skipped,
    }


# ============================================================================
# SNAPSHOT MODE
# ============================================================================

async def fetch_aa_snapshot(
    api_key: Optional[str] = None,
    output_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Fetch full AA leaderboard snapshot."""
    client = ArtificialAnalysisClient(api_key=api_key, tier="free" if not api_key else "pro")

    logger.info("Fetching AA snapshot (all models, all pages)...")
    all_models = []

    import httpx2 as httpx
    url = f"{client.base_url}{client._get_endpoint()}"

    async with httpx.AsyncClient(timeout=60) as http:
        page = 1
        version = 4.1
        while True:
            try:
                resp = await http.get(
                    url,
                    headers=client._get_headers(),
                    params={"page": page},
                )
                if resp.status_code == 429:
                    retry = int(resp.headers.get("Retry-After", 60))
                    logger.warning(f"Rate limited, waiting {retry}s...")
                    await anyio.sleep(retry)
                    continue
                resp.raise_for_status()
                data = resp.json()
                version = data.get("intelligence_index_version", 4.1)

                for item in data.get("data", []):
                    model = client._parse_model(item, version)
                    all_models.append(model.to_dict())

                pagination = data.get("pagination", {})
                logger.info(f"  Page {page}/{pagination.get('total_pages', '?')} — "
                            f"{len(all_models)} models so far")

                if not pagination.get("has_more", False):
                    break
                page += 1
                if page > pagination.get("total_pages", 1):
                    break

            except Exception as e:
                logger.error(f"Snapshot error on page {page}: {e}")
                break

    snapshot = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "intelligence_index_version": version,
        "total_models": len(all_models),
        "models": all_models,
    }

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
        logger.info(f"Snapshot saved to {output_path} ({len(all_models)} models)")

    return snapshot


# ============================================================================
# MAIN
# ============================================================================

async def main_async(args: argparse.Namespace) -> int:
    """Main async entry point."""
    import os
    
    # Resolve AA_API_KEY from VaultCore
    api_key = None
    try:
        from omega.vault import VaultCore
        vault = VaultCore()
        vault._load_sync()
        cred = vault._credentials.get("artificial_analysis:api_key")
        api_key = cred.encrypted_blob if cred else None
    except Exception:
        api_key = None

    if args.snapshot:
        output = Path(args.output) if args.output else Path("data/aa_snapshot.json")
        snapshot = await fetch_aa_snapshot(api_key=api_key, output_path=output)
        print(f"\n✅ Snapshot: {snapshot['total_models']} models fetched")
        return 0

    orchestrator = ModelEnrichmentOrchestrator(
        aa_client=ArtificialAnalysisClient(api_key=api_key),
        hf_client=HuggingFaceHubClient(),
    )

    results: List[ModelEnrichmentResult] = []

    if args.model:
        # Single model enrichment
        logger.info(f"Enriching model: {args.model}")
        hf_id = args.hf_id or args.model

        # Try AA first, then HF
        result = await orchestrator.enrich_from_aa(args.model, hf_model_id=hf_id)
        if not result:
            result = await orchestrator.enrich_from_hf(hf_id)

        if result:
            results.append(result)
            fields = build_enrichment_fields(result)
            report = build_enrichment_report(results)

            if args.dry_run:
                print(json.dumps(report, indent=2))
            else:
                # Write enrichment data to stdout or file
                print(json.dumps(fields, indent=2))

            return 0
        else:
            logger.error(f"Could not enrich model: {args.model}")
            return 1

    elif args.batch:
        # Batch enrichment
        batch_dir = Path(args.batch)
        if not batch_dir.exists():
            logger.error(f"Batch directory not found: {batch_dir}")
            return 1

        model_files = list(batch_dir.rglob("*.yaml"))
        logger.info(f"Batch enriching {len(model_files)} models from {batch_dir}")

        for model_file in model_files:
            model_name = model_file.stem
            logger.info(f"  Processing: {model_name}")

            result = await orchestrator.enrich_from_aa(model_name)
            if not result:
                result = await orchestrator.enrich_from_hf(model_name)

            if result:
                results.append(result)
                if not args.dry_run:
                    fields = build_enrichment_fields(result)
                    existing = _read_yaml_file(model_file)
                    if existing:
                        enriched = _inject_fields(existing, fields)
                        model_file.write_text(enriched, encoding="utf-8")
                        logger.info(f"    ✅ Enriched: {model_file}")

        report = build_enrichment_report(results)
        report_path = Path(args.output) if args.output else Path("data/enrichment_report.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"\n✅ Batch enrichment complete: {report['enriched_count']} enriched, "
              f"{report['skipped_count']} skipped")
        print(f"   Report: {report_path}")
        return 0

    else:
        logger.error("Specify --model or --batch")
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Enrich Model Registry with live AA + HF Hub data",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--model", help="Enrich a single model (by AA slug or HF ID)")
    group.add_argument("--batch", help="Batch enrich all .yaml files in directory")
    group.add_argument("--snapshot", action="store_true", help="Fetch full AA leaderboard snapshot")

    parser.add_argument("--hf-id", help="HuggingFace model ID for cross-reference (org/name)")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be written")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    return anyio.run(main_async, args)


if __name__ == "__main__":
    sys.exit(main())
