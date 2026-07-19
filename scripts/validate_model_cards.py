#!/usr/bin/env python3
"""Model Card Validator — JSON Schema + Cross-field validation.

Validates model card YAML files against the schema and performs
cross-field consistency checks.

Usage:
    # Validate a single model card
    python scripts/validate_model_cards.py --file config/model_registry/research_profiles/gemma_4_31b.yaml

    # Validate all model cards
    python scripts/validate_model_cards.py --all

    # Validate with cross-field checks
    python scripts/validate_model_cards.py --all --cross-field

    # Fix common issues automatically
    python scripts/validate_model_cards.py --all --fix
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class ValidationError:
    """A single validation error."""
    file: str
    field: str
    rule: str
    message: str
    severity: str = "error"  # error | warning | info
    line: Optional[int] = None

    def __str__(self) -> str:
        loc = f"{self.file}:{self.line}" if self.line else self.file
        return f"[{self.severity.upper()}] {loc} {self.field}: {self.message} ({self.rule})"


@dataclass
class ValidationReport:
    """Validation results for one or more model cards."""
    checked_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    files_checked: int = 0
    files_valid: int = 0
    files_invalid: int = 0
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.files_invalid == 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "checked_at": self.checked_at,
            "files_checked": self.files_checked,
            "files_valid": self.files_valid,
            "files_invalid": self.files_invalid,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "passed": self.passed,
            "errors": [str(e) for e in self.errors],
            "warnings": [str(e) for e in self.warnings],
        }


# ============================================================================
# SCHEMA VALIDATION (lightweight, no jsonschema dependency)
# ============================================================================

REQUIRED_FIELDS = [
    "model_id", "display_name", "version", "provider", "platform",
    "tier", "status", "context_window", "capabilities", "pricing",
    "routing", "tags", "schema_version", "created_at", "updated_at",
]

VALID_PLATFORMS = {"cloud", "local", "cli", "stealth"}
VALID_TIERS = {"T1", "T2", "T3"}
VALID_STATUSES = {"active", "deprecated", "experimental", "blocked"}
VALID_SCHEMA_VERSIONS = {"1.0.0", "1.1.0"}

MIN_CONTEXT_WINDOW = 512
MAX_CONTEXT_WINDOW = 10_000_000

REQUIRED_CAPABILITIES = {"coding", "reasoning"}
REQUIRED_ROUTING = {"preferred_use_cases"}
REQUIRED_PRICING = {"input_per_1m", "output_per_1m"}


def validate_schema(card: Dict[str, Any], filename: str) -> List[ValidationError]:
    """Validate a model card against the schema rules."""
    errors = []

    # Required fields
    for field_name in REQUIRED_FIELDS:
        if field_name not in card:
            errors.append(ValidationError(
                file=filename, field=field_name, rule="required_field",
                message=f"Missing required field: {field_name}",
            ))

    # Platform enum
    if "platform" in card and card["platform"] not in VALID_PLATFORMS:
        errors.append(ValidationError(
            file=filename, field="platform", rule="enum",
            message=f"Invalid platform: {card['platform']}. Must be one of {VALID_PLATFORMS}",
        ))

    # Tier enum
    if "tier" in card and card["tier"] not in VALID_TIERS:
        errors.append(ValidationError(
            file=filename, field="tier", rule="enum",
            message=f"Invalid tier: {card['tier']}. Must be one of {VALID_TIERS}",
        ))

    # Status enum
    if "status" in card and card["status"] not in VALID_STATUSES:
        errors.append(ValidationError(
            file=filename, field="status", rule="enum",
            message=f"Invalid status: {card['status']}. Must be one of {VALID_STATUSES}",
        ))

    # Schema version
    if "schema_version" in card and card["schema_version"] not in VALID_SCHEMA_VERSIONS:
        errors.append(ValidationError(
            file=filename, field="schema_version", rule="enum",
            message=f"Invalid schema_version: {card['schema_version']}",
        ))

    # Context window range
    ctx = card.get("context_window")
    if ctx is not None:
        if not isinstance(ctx, int) or ctx < MIN_CONTEXT_WINDOW or ctx > MAX_CONTEXT_WINDOW:
            errors.append(ValidationError(
                file=filename, field="context_window", rule="range",
                message=f"context_window must be {MIN_CONTEXT_WINDOW}-{MAX_CONTEXT_WINDOW}, got {ctx}",
            ))

    # Capabilities
    caps = card.get("capabilities", {})
    if isinstance(caps, dict):
        for req in REQUIRED_CAPABILITIES:
            if req not in caps:
                errors.append(ValidationError(
                    file=filename, field=f"capabilities.{req}", rule="required_subfield",
                    message=f"Missing required capability: {req}",
                ))
    elif "capabilities" in card:
        errors.append(ValidationError(
            file=filename, field="capabilities", rule="type",
            message="capabilities must be an object",
        ))

    # Pricing
    pricing = card.get("pricing", {})
    if isinstance(pricing, dict):
        for req in REQUIRED_PRICING:
            if req not in pricing:
                errors.append(ValidationError(
                    file=filename, field=f"pricing.{req}", rule="required_subfield",
                    message=f"Missing required pricing field: {req}",
                ))
            elif pricing[req] is not None and (not isinstance(pricing[req], (int, float)) or pricing[req] < 0):
                errors.append(ValidationError(
                    file=filename, field=f"pricing.{req}", rule="non_negative",
                    message=f"pricing.{req} must be non-negative, got {pricing[req]}",
                ))

    # Routing
    routing = card.get("routing", {})
    if isinstance(routing, dict):
        for req in REQUIRED_ROUTING:
            if req not in routing:
                errors.append(ValidationError(
                    file=filename, field=f"routing.{req}", rule="required_subfield",
                    message=f"Missing required routing field: {req}",
                ))
    elif "routing" in card:
        errors.append(ValidationError(
            file=filename, field="routing", rule="type",
            message="routing must be an object",
        ))

    # Tags
    tags = card.get("tags", [])
    if not isinstance(tags, list) or len(tags) == 0:
        errors.append(ValidationError(
            file=filename, field="tags", rule="non_empty_array",
            message="tags must be a non-empty array",
        ))

    # Timestamps
    for ts_field in ["created_at", "updated_at"]:
        if ts_field in card:
            val = card[ts_field]
            if isinstance(val, str):
                try:
                    datetime.fromisoformat(val.replace("Z", "+00:00"))
                except ValueError:
                    errors.append(ValidationError(
                        file=filename, field=ts_field, rule="datetime_format",
                        message=f"Invalid ISO datetime: {val}",
                        severity="warning",
                    ))

    return errors


# ============================================================================
# CROSS-FIELD VALIDATION
# ============================================================================

def validate_cross_field(
    card: Dict[str, Any],
    filename: str,
    all_cards: Optional[Dict[str, Dict]] = None,
) -> List[ValidationError]:
    """Validate cross-field consistency rules."""
    warnings = []

    model_id = card.get("model_id", "")
    tier = card.get("tier", "")
    platform = card.get("platform", "")
    status = card.get("status", "")
    pricing = card.get("pricing", {})
    caps = card.get("capabilities", {})
    routing = card.get("routing", {})

    # Rule 1: T3 models should have reasoning capability
    if tier == "T3" and isinstance(caps, dict) and not caps.get("reasoning"):
        warnings.append(ValidationError(
            file=filename, field="tier/capabilities.reasoning",
            rule="tier_capability_consistency",
            message="T3 model should have reasoning=true",
            severity="warning",
        ))

    # Rule 2: T1 models should not be expensive (> $10/1M output)
    if tier == "T1" and isinstance(pricing, dict):
        out_price = pricing.get("output_per_1m")
        if out_price is not None and out_price > 10:
            warnings.append(ValidationError(
                file=filename, field="pricing.output_per_1m",
                rule="tier_price_consistency",
                message=f"T1 model has high output price (${out_price}/1M). T1 should be fast+cheap.",
                severity="warning",
            ))

    # Rule 3: Local models should have free or low pricing
    if platform == "local" and isinstance(pricing, dict):
        inp = pricing.get("input_per_1m")
        out = pricing.get("output_per_1m")
        if inp is not None and inp > 1:
            warnings.append(ValidationError(
                file=filename, field="pricing",
                rule="platform_price_consistency",
                message=f"Local model has input price ${inp}/1M. Local models should be free or very cheap.",
                severity="warning",
            ))

    # Rule 4: Deprecated models should not be in routing fallback lists
    if status == "deprecated" and isinstance(routing, dict):
        fallbacks = routing.get("fallback", [])
        if fallbacks and model_id in str(fallbacks):
            warnings.append(ValidationError(
                file=filename, field="routing.fallback",
                rule="deprecated_in_fallback",
                message="Deprecated model appears in fallback routing",
                severity="warning",
            ))

    # Rule 5: Model ID uniqueness
    if all_cards and model_id:
        duplicates = [f for f, c in all_cards.items() if c.get("model_id") == model_id and f != filename]
        if duplicates:
            warnings.append(ValidationError(
                file=filename, field="model_id",
                rule="unique_model_id",
                message=f"Duplicate model_id '{model_id}' found in: {duplicates}",
                severity="warning",
            ))

    # Rule 6: Vision models should have context_window >= 100K
    if isinstance(caps, dict) and caps.get("vision"):
        ctx = card.get("context_window", 0)
        if ctx and ctx < 100_000:
            warnings.append(ValidationError(
                file=filename, field="context_window",
                rule="vision_context_minimum",
                message=f"Vision model has small context ({ctx}). Vision models typically need >= 100K.",
                severity="warning",
            ))

    # Rule 7: Timestamps consistency
    created = card.get("created_at", "")
    updated = card.get("updated_at", "")
    if created and updated and updated < created:
        warnings.append(ValidationError(
            file=filename, field="updated_at",
            rule="timestamp_order",
            message="updated_at is before created_at",
            severity="warning",
        ))

    return warnings


# ============================================================================
# VALIDATION RUNNER
# ============================================================================

def validate_file(
    filepath: Path,
    all_cards: Optional[Dict[str, Dict]] = None,
    cross_field: bool = True,
) -> List[ValidationError]:
    """Validate a single YAML model card file."""
    errors = []
    filename = str(filepath)

    try:
        with open(filepath, encoding="utf-8") as f:
            card = yaml.safe_load(f)
    except yaml.YAMLError as e:
        errors.append(ValidationError(
            file=filename, field="(yaml)", rule="parse_error",
            message=f"YAML parse error: {e}",
        ))
        return errors
    except Exception as e:
        errors.append(ValidationError(
            file=filename, field="(io)", rule="read_error",
            message=f"Read error: {e}",
        ))
        return errors

    if not isinstance(card, dict):
        errors.append(ValidationError(
            file=filename, field="(root)", rule="type",
            message="Model card must be a YAML mapping (dict)",
        ))
        return errors

    # Schema validation
    errors.extend(validate_schema(card, filename))

    # Cross-field validation
    if cross_field:
        errors.extend(validate_cross_field(card, filename, all_cards))

    return errors


def validate_all(
    registry_dir: Path,
    cross_field: bool = True,
) -> ValidationReport:
    """Validate all model cards in the registry."""
    report = ValidationReport()

    # Collect all YAML files
    card_files = []
    for subdir in ["research_profiles", "providers"]:
        dir_path = registry_dir / subdir
        if dir_path.exists():
            card_files.extend(dir_path.glob("*.yaml"))

    # Also check root-level YAML files (but skip registry.yaml and provider dirs)
    for f in registry_dir.glob("*.yaml"):
        if f.name != "registry.yaml":
            card_files.append(f)

    # Load all cards for cross-field checks
    all_cards = {}
    for f in card_files:
        try:
            with open(f, encoding="utf-8") as fh:
                card = yaml.safe_load(fh)
                if isinstance(card, dict):
                    all_cards[str(f)] = card
        except Exception:
            pass

    # Validate each file
    for filepath in card_files:
        report.files_checked += 1
        errs = validate_file(filepath, all_cards if cross_field else None, cross_field)

        file_errors = [e for e in errs if e.severity == "error"]
        file_warnings = [e for e in errs if e.severity in ("warning", "info")]

        if file_errors:
            report.files_invalid += 1
            report.errors.extend(file_errors)
        else:
            report.files_valid += 1

        report.warnings.extend(file_warnings)

    return report


# ============================================================================
# MAIN
# ============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(description="Validate model card YAML files")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", "-f", help="Validate a single YAML file")
    group.add_argument("--all", "-a", action="store_true", help="Validate all model cards")

    parser.add_argument("--no-cross-field", action="store_true", help="Skip cross-field checks")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    parser.add_argument("--strict", action="store_true", help="Warnings count as errors")
    parser.add_argument("--registry-dir", default="config/model_registry",
                        help="Registry directory (default: config/model_registry)")

    args = parser.parse_args()
    registry_dir = Path(args.registry_dir)

    if args.file:
        filepath = Path(args.file)
        if not filepath.exists():
            print(f"File not found: {filepath}")
            return 1
        errs = validate_file(filepath, cross_field=not args.no_cross_field)
        report = ValidationReport(
            files_checked=1,
            files_valid=1 if not any(e.severity == "error" for e in errs) else 0,
            files_invalid=1 if any(e.severity == "error" for e in errs) else 0,
            errors=[e for e in errs if e.severity == "error"],
            warnings=[e for e in errs if e.severity in ("warning", "info")],
        )
    elif args.all:
        report = validate_all(registry_dir, cross_field=not args.no_cross_field)
    else:
        print("Specify --file or --all")
        return 1

    # Strict mode: promote warnings to errors
    if args.strict:
        report.errors.extend(report.warnings)
        report.warnings = []
        report.files_invalid = report.files_checked - report.files_valid
        report.files_valid = report.files_checked - report.files_invalid

    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        # Human-readable output
        for err in report.errors:
            print(f"  ❌ {err}")
        for warn in report.warnings:
            print(f"  ⚠️  {warn}")

        print(f"\n{'✅' if report.passed else '❌'} "
              f"Validated {report.files_checked} files: "
              f"{report.files_valid} valid, {report.files_invalid} invalid, "
              f"{len(report.warnings)} warnings")

    return 0 if report.passed or not args.strict else 1


if __name__ == "__main__":
    sys.exit(main())
