# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Omega Engine — Lens Registry (WAD-Backed)
# ⬡ OMEGA ⬡ MEDITATE ⬡ LENS_REGISTRY ⬡ M2-COMPLIANT
#
# Loads meditation lens definitions from WAD YAML configuration,
# eliminating hardcoded entity names from engine core.
# M2 Firewall Phase A: meditate/protocol.py violations eliminated.
#
# Dependency note: This module depends on yaml and config_resolver.
# For zero-dep contexts (e.g., embedded use), import PersonaSpec
# directly from protocol.py and use get_default_lenses().

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from src.omega.governance.config_resolver import WADS_DIR, get_active_iwad
from src.omega.meditate.protocol import DissentStyle, PersonaLibrary, PersonaSpec

# ── Constants ──────────────────────────────────────────────────────────────────

LENSES_DIRNAME = "meditate"
LENSES_FILENAME = "lenses.yaml"
LENSES_SECTION_KEY = "meditate"
LENSES_KEY = "lenses"
LIBRARIES_KEY = "libraries"

# ── Public API ─────────────────────────────────────────────────────────────────


def load_lens_library(name: str, iwad: str | None = None) -> PersonaLibrary:
    """Load a named lens library from the active WAD's lenses.yaml.

    Args:
        name: Library name key (e.g., 'omega_nodes', 'makali_triad').
        iwad: IWAD name. If None, uses active_iwad from config/omega.yaml.

    Returns:
        PersonaLibrary with all lens PersonaSpecs loaded from YAML.

    Raises:
        FileNotFoundError: If no lenses.yaml exists for the WAD.
        KeyError: If the named library is not defined in lenses.yaml.
        ValueError: If YAML data is malformed.
    """
    iwad_name = iwad or get_active_iwad()
    config = _load_lenses_config(iwad_name)

    libraries = config.get(LIBRARIES_KEY, {})
    if name not in libraries:
        available = list(libraries.keys())
        raise KeyError(
            f"Lens library '{name}' not found in WAD '{iwad_name}' lenses.yaml. "
            f"Available libraries: {available}"
        )

    lib_def = libraries[name]
    lens_ids: list[str] = lib_def["lens_ids"]
    all_lenses: list[dict[str, Any]] = config.get(LENSES_KEY, [])

    # Build a lookup by lens id
    lens_map: dict[str, dict[str, Any]] = {}
    for lens_def in all_lenses:
        lid = lens_def.get("id")
        if lid:
            lens_map[lid] = lens_def

    # Resolve each lens id to a PersonaSpec
    specs: list[PersonaSpec] = []
    for lid in lens_ids:
        if lid not in lens_map:
            raise KeyError(
                f"Lens id '{lid}' referenced in library '{name}' "
                f"but not defined in WAD '{iwad_name}' lenses.yaml"
            )
        specs.append(_def_to_spec(lens_map[lid]))

    return PersonaLibrary(
        name=lib_def.get("name", name),
        personas=specs,
    )


def load_all_lenses(iwad: str | None = None) -> dict[str, PersonaSpec]:
    """Load all individual lens definitions from the active WAD.

    Args:
        iwad: IWAD name. If None, uses active_iwad from config/omega.yaml.

    Returns:
        Dict mapping lens id -> PersonaSpec.
    """
    iwad_name = iwad or get_active_iwad()
    config = _load_lenses_config(iwad_name)
    lenses = config.get(LENSES_KEY, [])
    return {lens_def["id"]: _def_to_spec(lens_def) for lens_def in lenses if "id" in lens_def}


def load_lens_by_id(lens_id: str, iwad: str | None = None) -> PersonaSpec:
    """Load a single lens by its id.

    Args:
        lens_id: The unique lens identifier (e.g., 'engineering', 'thesis').
        iwad: IWAD name. If None, uses active_iwad from config/omega.yaml.

    Returns:
        The PersonaSpec for the requested lens.

    Raises:
        KeyError: If the lens id is not found.
    """
    all_lenses = load_all_lenses(iwad)
    if lens_id not in all_lenses:
        raise KeyError(
            f"Lens id '{lens_id}' not found. Available lenses: {list(all_lenses.keys())}"
        )
    return all_lenses[lens_id]


def get_lenses_config_path(iwad: str | None = None) -> Path:
    """Get the path to the lenses.yaml for a given WAD.

    Args:
        iwad: IWAD name. If None, uses active_iwad from config/omega.yaml.

    Returns:
        Path to the lenses.yaml file (may not exist).
    """
    iwad_name = iwad or get_active_iwad()
    return WADS_DIR / iwad_name / LENSES_DIRNAME / LENSES_FILENAME


# ── Internal Helpers ──────────────────────────────────────────────────────────


def _load_lenses_config(iwad: str) -> dict[str, Any]:
    """Load and parse lenses.yaml for a given WAD.

    Args:
        iwad: The IWAD name.

    Returns:
        Parsed YAML dict under the 'meditate' key.

    Raises:
        FileNotFoundError: If lenses.yaml doesn't exist.
        ValueError: If YAML is malformed or missing meditate key.
    """
    config_path = get_lenses_config_path(iwad)
    if not config_path.exists():
        raise FileNotFoundError(
            f"No meditate lens config found at {config_path}. "
            f"Create {config_path} or use get_default_lenses() fallback."
        )

    try:
        raw = config_path.read_text(encoding="utf-8")
        data: dict[str, Any] = yaml.safe_load(raw) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"Malformed YAML in lens config: {config_path}\n{exc}") from exc

    meditate_section = data.get(LENSES_SECTION_KEY)
    if not meditate_section or not isinstance(meditate_section, dict):
        raise ValueError(
            f"Missing top-level '{LENSES_SECTION_KEY}' section in {config_path}. "
            f"Ensure the file has a 'meditate:' key at the root."
        )

    return meditate_section


def _def_to_spec(defn: dict[str, Any]) -> PersonaSpec:
    """Convert a raw YAML lens definition to a PersonaSpec.

    All fields are optional except those with defaults in PersonaSpec.
    """
    dissent_raw = defn.get("dissent_style", "direct")
    try:
        dissent = DissentStyle(dissent_raw.lower())
    except ValueError:
        dissent = DissentStyle.DIRECT

    return PersonaSpec(
        name=defn.get("name", defn.get("id", "Unknown")),
        domain=defn.get("domain", "General"),
        mandate_lens=defn.get("mandate_lens", "Speak from your domain."),
        anti_domains=defn.get("anti_domains", []),
        node=defn.get("node"),
        element=defn.get("element"),
        known_for=defn.get("known_for"),
        dissent_style=dissent,
    )
