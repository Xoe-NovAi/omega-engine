# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Omega Engine — AxiomRegistry (Five-Fold Foundation mechanism)
# AP: AP-AXIOM-REGISTRY-v1.0.0
# ⬡ OMEGA ⬡ MAAT ⬡ N1-N5 ⬡ opencode ⬡ trc_axiom_registry ⬡ ACTIVE
#
# [heritage: id-soft-1996] cvar system split — the engine holds the cvar
#   *mechanism*; the game holds the cvar *values*. AxiomRegistry is the
#   WAD-agnostic loader (engine); the actual Five-Fold principles live in the
#   WAD's axioms.yaml (content). Same engine/stack separation as id Software.
#
# M2 Firewall: This module contains ZERO WAD-specific content. No hardcoded
#   axiom text, no `arcana_novai` literals in logic. All content is loaded from
#   the WAD directory passed as a parameter.
# M16 Portability: No hardcoded absolute paths; wad_dir is a parameter resolved
#   via pathlib.Path.
# M1 AnyIO: No asyncio runtime used. A synchronous YAML read at init is acceptable
#   for a registry loaded once (per AGENTS.md §12 bootstrap allowance).
# M9 Error Integrity: Typed errors via WADError; no bare except.

import logging
from pathlib import Path
from typing import Any, Dict, List

import yaml

from omega.errors import WADError

logger = logging.getLogger(__name__)

AXIOMS_FILENAME = "axioms.yaml"


class AxiomRegistry:
    """WAD-agnostic loader for the Five-Fold Foundation axioms.

    The registry reads an ``axioms.yaml`` from a WAD directory and exposes the
    loaded axioms for injection into entity system prompts. It does NOT interpret
    the meaning of axioms — it only loads, lists, and formats them. The actual
    philosophical content lives exclusively in the WAD, never in this core module.

    Attributes:
        wad_dir: Resolved Path to the WAD directory (parameter-injected).
    """

    def __init__(self, wad_dir: str | Path) -> None:
        """Initialize the registry for a specific WAD directory.

        Args:
            wad_dir: Path (str or Path) to the WAD directory containing
                ``axioms.yaml``. Resolved via ``pathlib.Path`` — never hardcoded.
        """
        self.wad_dir: Path = Path(wad_dir)
        self._axioms: Dict[str, Any] = {}
        self._loaded: bool = False

    def load(self) -> Dict[str, Any]:
        """Load ``axioms.yaml`` from the WAD directory.

        Returns:
            The parsed axiom mapping. Returns an empty dict (and logs a warning)
            if the file is missing — this is graceful degradation, not a crash.

        Raises:
            WADError: If the file exists but fails to parse (YAML error, read
                error, or does not resolve to a mapping). Typed per M9.
        """
        self._axioms = {}
        axioms_path = self.wad_dir / AXIOMS_FILENAME

        if not axioms_path.exists():
            logger.warning("AxiomRegistry: %s not found; returning empty registry.", axioms_path)
            self._loaded = True
            return self._axioms

        try:
            with axioms_path.open("r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh)
        except yaml.YAMLError as exc:
            raise WADError(
                f"Failed to parse axioms.yaml at {axioms_path}: {exc}",
                raw_error=exc,
            ) from exc
        except OSError as exc:
            raise WADError(
                f"Failed to read axioms.yaml at {axioms_path}: {exc}",
                raw_error=exc,
            ) from exc

        if not isinstance(data, dict):
            raise WADError(
                f"axioms.yaml at {axioms_path} did not parse to a mapping (got "
                f"{type(data).__name__})"
            )

        self._axioms = data
        self._loaded = True
        return self._axioms

    def list_axioms(self) -> List[str]:
        """Return the axiom ids from the loaded ``five_fold`` list.

        Returns:
            List of axiom id strings. Empty if no axioms are loaded.
        """
        if not self._loaded:
            self.load()
        five_fold = self._axioms.get("five_fold", [])
        return [a.get("id", "") for a in five_fold if isinstance(a, dict)]

    def get_preamble(self, entity_name: str | None = None) -> str:
        """Assemble a formatted Five-Fold Preamble string from loaded axioms.

        The registry does not interpret axiom meaning; it formats the loaded
        structured data into a readable block. If ``entity_name`` is provided,
        the header is tailored with that name for context (no semantic filtering).

        Args:
            entity_name: Optional entity name to tailor the preamble header.

        Returns:
            A non-empty formatted preamble string (or a placeholder if no axioms
            are loaded).
        """
        if not self._loaded:
            self.load()

        five_fold = self._axioms.get("five_fold", [])
        lines: List[str] = []

        header = "FIVE-FOLD FOUNDATION"
        if entity_name:
            header += f" — for {entity_name}"
        lines.append(header)
        lines.append("=" * len(header))

        if not five_fold:
            lines.append("(No axioms loaded.)")
            return "\n".join(lines)

        for axiom in five_fold:
            if not isinstance(axiom, dict):
                continue
            name = axiom.get("name", axiom.get("id", "?"))
            principle = axiom.get("principle", "")
            lines.append(f"- {name}: {principle}")

        ref = self._axioms.get("maat_ideals_reference")
        if ref:
            lines.append("")
            lines.append(f"Ethical guardrail: {ref}")

        return "\n".join(lines)


__all__ = ["AxiomRegistry", "AXIOMS_FILENAME"]
