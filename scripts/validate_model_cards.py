#!/usr/bin/env python3
"""
OMER M1: Model Card Schema Validation

Validates model card frontmatter (YAML) against the OMER v1.0 schema.
Wired into `make lint` for continuous validation.
"""

import sys
import re
from pathlib import Path
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, field_validator, model_validator
import yaml


# =============================================================================
# ENUMS & CONSTANTS (from OMER Foundation §2.1, §2.3, §2.4)
# =============================================================================

VALID_RESEARCH_STATUS = Literal["candidate", "active", "rejected", "retired"]
VALID_DEPLOYMENT = Literal["hosted_trial", "local", "hybrid", "not_deployed"]
VALID_EVIDENCE_LABELS = Literal[
    "Provider claim",      # marketing, blog post, model card from provider
    "Community benchmark", # leaderboard score (LMSYS, OpenLLM, etc.)
    "Independent eval",    # third-party controlled study
    "Local measurement",   # our own controlled run on our hardware
    "Reproduced"           # independently reproduced by external party
]
VALID_REPRODUCTION_STATUS = Literal[
    "Indicative",          # informal, not gated; quick sanity check
    "Reported",            # described in paper/blog; public materials exist
    "Controlled",          # ran through full validation methodology chain
    "Verified",            # Controlled + results replicated by independent team
    "Independent"          # Verified + multiple independent reproductions
]


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class LocalHardwareProfile(BaseModel):
    """MLPerf-style hardware profile for local deployments (§2.1)"""
    cpu: str
    cpu_cores: int = Field(ge=1)
    cpu_threads: int = Field(ge=1)
    allowed_cpus: str
    threads: int = Field(ge=1)
    ram_gb: int = Field(ge=1)
    ram_type: str
    kv_cache_type: str
    flash_attention: bool
    max_loaded_models: int = Field(ge=1)
    quantization: str
    gpu: Optional[str] = None

    @field_validator("allowed_cpus")
    @classmethod
    def validate_allowed_cpus(cls, v: str) -> str:
        # P-core trap: must include HT siblings (0-11), NOT just physical (0,2,4,6,8,10)
        if v == "0,2,4,6,8,10":
            raise ValueError("P-core trap: allowed_cpus must include HT siblings (0-11), not physical-only (0,2,4,6,8,10). See ollama #17916.")
        return v


class Reproducibility(BaseModel):
    """MLPerf-style reproducibility metadata (§2.1)"""
    seed: int = 42
    config_hash: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    environment: dict = Field(default_factory=dict)


class ModelCardFrontmatter(BaseModel):
    """OMER v1.0 Model Card Frontmatter Schema (§2.1)"""

    # --- Required (validated by `omer validate`) ---
    card_version: Literal["1.0"]
    model_id: str
    provider: str
    research_status: VALID_RESEARCH_STATUS
    deployment: VALID_DEPLOYMENT
    last_verified: str  # YYYY-MM-DD
    confidence: str     # "metadata:high,performance:low" format
    license: str
    context_length: int = Field(ge=1)
    modalities_in: List[str] = Field(min_length=1)
    modalities_out: List[str] = Field(min_length=1)

    # --- Hardware Profile for Local Deployments ---
    local_hardware_profile: Optional[LocalHardwareProfile] = None

    # --- MLPerf-style Reproducibility ---
    reproducibility: Optional[Reproducibility] = None

    @field_validator("last_verified")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("last_verified must be YYYY-MM-DD")
        return v

    @field_validator("confidence")
    @classmethod
    def validate_confidence_format(cls, v: str) -> str:
        # Expect "metadata:high,performance:low" format
        parts = v.split(",")
        for part in parts:
            if ":" not in part:
                raise ValueError(f"confidence must be 'key:value,key:value' format, got '{v}'")
        return v

    @model_validator(mode="after")
    def validate_local_hardware_if_local_deployment(self):
        if self.deployment in ("local", "hybrid") and self.local_hardware_profile is None:
            raise ValueError(f"deployment='{self.deployment}' requires local_hardware_profile")
        return self


# =============================================================================
# VALIDATION LOGIC
# =============================================================================

EVIDENCE_LABELS: set = {
    "Provider claim",
    "Community benchmark",
    "Independent eval",
    "Local measurement",
    "Reproduced"
}

REPRODUCTION_STATUS: set = {
    "Indicative",
    "Reported",
    "Controlled",
    "Verified",
    "Independent"
}


def extract_frontmatter(filepath: Path) -> tuple[dict, str]:
    """Extract YAML frontmatter from markdown file. Returns (frontmatter_dict, remaining_content)."""
    content = filepath.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    try:
        fm = yaml.safe_load(parts[1])
        return fm or {}, parts[2]
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML frontmatter: {e}")


def validate_evidence_labels(content: str, filepath: Path) -> list[str]:
    """Validate evidence labels in the markdown body match allowed labels."""
    errors = []
    # Match both key-value table rows and table column headers:
    # 1. | Evidence label | **Label** |
    # 2. | ... | ... | **Label** | (when header has Evidence)
    lines = content.splitlines()
    in_table = False
    evidence_col_idx = -1

    for line_idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            in_table = False
            evidence_col_idx = -1
            continue

        cols = [c.strip() for c in stripped.strip("|").split("|")]

        # Check key-value table row
        if len(cols) == 2 and cols[0].lower() in ("evidence", "evidence label"):
            val = re.sub(r"^\*\*|\*\*$", "", cols[1]).strip()
            if val and val not in EVIDENCE_LABELS:
                errors.append(f"{filepath}:{line_idx}: Invalid evidence label '{val}'. Valid: {sorted(EVIDENCE_LABELS)}")
            continue

        # Check column header
        if not in_table:
            in_table = True
            for idx, col in enumerate(cols):
                if col.lower() in ("evidence", "evidence label"):
                    evidence_col_idx = idx
                    break
            continue

        # Skip separator line |---|---|
        if re.match(r"^[\s\-:|]+$", stripped):
            continue

        # Data row under table with Evidence column
        if evidence_col_idx >= 0 and evidence_col_idx < len(cols):
            val = re.sub(r"^\*\*|\*\*$", "", cols[evidence_col_idx]).strip()
            if val and val not in EVIDENCE_LABELS:
                errors.append(f"{filepath}:{line_idx}: Invalid evidence label '{val}'. Valid: {sorted(EVIDENCE_LABELS)}")

    return errors


def validate_reproduction_status(content: str, filepath: Path) -> list[str]:
    """Validate reproduction status in the markdown body matches allowed levels."""
    errors = []
    lines = content.splitlines()
    in_table = False
    status_col_idx = -1

    for line_idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            in_table = False
            status_col_idx = -1
            continue

        cols = [c.strip() for c in stripped.strip("|").split("|")]

        # Key-value row
        if len(cols) == 2 and cols[0].lower() in ("reproduction status", "reproduction"):
            val = re.sub(r"^\*\*|\*\*$", "", cols[1]).strip()
            if val and val not in REPRODUCTION_STATUS:
                errors.append(f"{filepath}:{line_idx}: Invalid reproduction status '{val}'. Valid: {sorted(REPRODUCTION_STATUS)}")
            continue

        # Header check
        if not in_table:
            in_table = True
            for idx, col in enumerate(cols):
                if col.lower() in ("reproduction status", "reproduction"):
                    status_col_idx = idx
                    break
            continue

        if re.match(r"^[\s\-:|]+$", stripped):
            continue

        if status_col_idx >= 0 and status_col_idx < len(cols):
            val = re.sub(r"^\*\*|\*\*$", "", cols[status_col_idx]).strip()
            if val and val not in REPRODUCTION_STATUS:
                errors.append(f"{filepath}:{line_idx}: Invalid reproduction status '{val}'. Valid: {sorted(REPRODUCTION_STATUS)}")

    return errors


def validate_required_sections(content: str, filepath: Path) -> list[str]:
    """Validate required markdown sections exist."""
    errors = []
    required_sections = [
        "## Local Measurement",
        "## Provider Claims",
        "## Omega Verdict",
    ]
    for section in required_sections:
        if section not in content:
            errors.append(f"{filepath}: Missing required section '{section}'")
    return errors


def validate_model_card(filepath: Path) -> list[str]:
    """Validate a single model card file. Returns list of error strings."""
    errors = []

    try:
        fm, body = extract_frontmatter(filepath)
        if not fm:
            errors.append(f"{filepath}: No YAML frontmatter found")
            return errors

        # Validate frontmatter against schema
        try:
            card = ModelCardFrontmatter(**fm)
        except Exception as e:
            errors.append(f"{filepath}: Frontmatter validation failed: {e}")
            return errors

        # Validate body content
        errors.extend(validate_evidence_labels(body, filepath))
        errors.extend(validate_reproduction_status(body, filepath))
        errors.extend(validate_required_sections(body, filepath))

    except Exception as e:
        errors.append(f"{filepath}: Unexpected error: {e}")

    return errors


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate OMER model cards")
    parser.add_argument("paths", nargs="*", default=["docs/models"], help="Paths to model card files or directories")
    parser.add_argument("--strict", action="store_true", help="Exit with error on any validation failure")
    args = parser.parse_args()

    all_errors = []
    cards_found = 0

    for path_str in args.paths:
        path = Path(path_str)
        if path.is_dir():
            for md_file in path.rglob("*.md"):
                if md_file.name == "README.md":
                    continue  # Skip registry README
                errors = validate_model_card(md_file)
                if errors:
                    all_errors.extend(errors)
                else:
                    print(f"✓ {md_file}")
                cards_found += 1
        elif path.is_file() and path.suffix == ".md":
            errors = validate_model_card(path)
            if errors:
                all_errors.extend(errors)
            else:
                print(f"✓ {path}")
            cards_found += 1

    if cards_found == 0:
        print("No model cards found to validate")
        return 1

    if all_errors:
        print(f"\n❌ VALIDATION FAILED ({len(all_errors)} errors):")
        for err in all_errors:
            print(f"  {err}")
        return 1

    print(f"\n✅ All {cards_found} model card(s) passed validation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
