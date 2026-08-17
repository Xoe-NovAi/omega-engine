# 🔱 Omega Engine — Meditate Protocol
# ⬡ OMEGA ⬡ MEDITATE ⬡ protocol.py ⬡ D-265
#
# D-265 Commit 1: Zero-dep dataclasses for the Meditate protocol.
# Portable enough to import from any context — no engine dependencies.
# The schema definitions that power `/meditate` and `oracle.meditate()`.

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ── Enums ──────────────────────────────────────────────────────────────────────


class DissentStyle(str, Enum):
    """How a persona voices disagreement with prior voices."""

    DIRECT = "direct"
    SOCRATIC = "socratic"
    ADVERSARIAL = "adversarial"
    CONSTRUCTIVE = "constructive"


class OutputMode(str, Enum):
    """The mode of the meditation — what kind of output to produce."""

    DIAGNOSTIC = "diagnostic"
    STRATEGIC = "strategic"
    CREATIVE = "creative"
    AUDIT = "audit"
    SYNTHESIS = "synthesis"


class MeditatePhase(str, Enum):
    """The five phases of a meditation. Phase 5 is optional."""

    PHASE_0_CALIBRATION = "calibration"
    PHASE_1_IMMERSION = "immersion"
    PHASE_2_COLLISION = "collision"
    PHASE_3_SEQUENCING = "sequencing"
    PHASE_4_VERDICT = "verdict"
    PHASE_5_INTEGRATION = "integration"


class AntiCollapseLaw(int, Enum):
    """The five Anti-Collapse Laws that govern meditation integrity."""

    DOMAIN_PURITY = 1
    IMPERATIVE_DIRECTNESS = 2
    MANDATORY_DISSENT = 3
    NO_PREMATURE_SYNTHESIS = 4
    PRESERVED_DISSENT = 5


# ── Persona & Meditation Specs ─────────────────────────────────────────────────


@dataclass(frozen=True)
class PersonaSpec:
    """Definition of a single persona for meditation.

    Each persona represents one lens that the model will adopt.
    The constraints (mandate_lens, anti_domains) are what prevent
    attention bleeding between voices.
    """

    name: str
    """Display name (e.g., 'Infrastructure', 'Engineering')."""

    domain: str
    """The ONE domain this voice speaks from (e.g., 'Infrastructure')."""

    mandate_lens: str
    """The single question this voice answers (e.g., 'Speak as the forge...')."""

    anti_domains: List[str] = field(default_factory=list)
    """Domains this voice must NOT speak about."""

    node: Optional[str] = None
    """Omega node slot (N1-N10), if applicable."""

    element: Optional[str] = None
    """Elemental/archetypal anchor (e.g., 'Fire 🜂')."""

    known_for: Optional[str] = None
    """Used for non-Omega custom personas (e.g., Carmack bio)."""

    dissent_style: DissentStyle = DissentStyle.DIRECT

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "domain": self.domain,
            "mandate_lens": self.mandate_lens,
            "anti_domains": self.anti_domains,
            "node": self.node,
            "element": self.element,
            "known_for": self.known_for,
            "dissent_style": self.dissent_style.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PersonaSpec":
        return cls(
            name=data["name"],
            domain=data["domain"],
            mandate_lens=data["mandate_lens"],
            anti_domains=data.get("anti_domains", []),
            node=data.get("node"),
            element=data.get("element"),
            known_for=data.get("known_for"),
            dissent_style=DissentStyle(data.get("dissent_style", "direct")),
        )


class PersonaLibrary:
    """A named collection of PersonaSpecs.

    Corresponds to a named collection of lenses (e.g., 'Omega Pantheon',
    'Thesis/Antithesis/Synthesis triad') or a custom user-defined set.
    """

    def __init__(self, name: str, personas: List[PersonaSpec]) -> None:
        self.name = name
        self._personas = personas

    @property
    def personas(self) -> List[PersonaSpec]:
        return list(self._personas)

    def __len__(self) -> int:
        return len(self._personas)

    def __getitem__(self, index: int) -> PersonaSpec:
        return self._personas[index]


@dataclass
class MeditationSpec:
    """Specification for a single meditation session.

    This is the complete input — what to meditate on, with which lenses,
    in what mode, and whether to integrate outputs.
    """

    subject: str
    """The precise subject of the meditation (one sentence)."""

    lens_set: List[PersonaSpec]
    """The personas to adopt, in order."""

    mode: OutputMode = OutputMode.STRATEGIC
    """What kind of output to produce."""

    anti_collapse_laws: List[AntiCollapseLaw] = field(default_factory=lambda: list(AntiCollapseLaw))
    """Which laws to enforce. Default: all five."""

    phases: List[MeditatePhase] = field(
        default_factory=lambda: [
            MeditatePhase.PHASE_0_CALIBRATION,
            MeditatePhase.PHASE_1_IMMERSION,
            MeditatePhase.PHASE_2_COLLISION,
            MeditatePhase.PHASE_3_SEQUENCING,
            MeditatePhase.PHASE_4_VERDICT,
        ]
    )
    """Which phases to execute. Phase 5 (INTEGRATION) is optional."""

    integrate: bool = False
    """If True, write PIVOT_LOG entry, update files, check gates."""

    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    """Trace identifier for observability."""

    model_hint: Optional[str] = None
    """Model to use for this meditation (e.g., 'qwen3-4b-think-q4_k_m')."""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subject": self.subject,
            "lens_set": [p.to_dict() for p in self.lens_set],
            "mode": self.mode.value,
            "phases": [p.value for p in self.phases],
            "integrate": self.integrate,
            "trace_id": self.trace_id,
            "model_hint": self.model_hint,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MeditationSpec":
        return cls(
            subject=data["subject"],
            lens_set=[PersonaSpec.from_dict(p) for p in data["lens_set"]],
            mode=OutputMode(data.get("mode", "strategic")),
            phases=[
                MeditatePhase(p)
                for p in data.get(
                    "phases", ["calibration", "immersion", "collision", "sequencing", "verdict"]
                )
            ],
            integrate=data.get("integrate", False),
            trace_id=data.get("trace_id", uuid.uuid4().hex[:16]),
            model_hint=data.get("model_hint"),
        )


# ── Results ────────────────────────────────────────────────────────────────────


@dataclass
class VoiceOutput:
    """The output of a single persona voice during Phase 1."""

    persona: PersonaSpec
    observation: str
    constraint: str
    imperative: str
    dissent: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "persona": self.persona.name,
            "observation": self.observation,
            "constraint": self.constraint,
            "imperative": self.imperative,
            "dissent": self.dissent,
        }


@dataclass
class Collision:
    """A cross-domain conflict surfaced during Phase 2."""

    title: str
    voices_involved: List[str]
    tension: str
    resolution_path: str


@dataclass
class MeditationResult:
    """The complete output of a meditation session.

    Contains all phases, all collisions, the emergent sequence,
    the final synthesis (verdict), and optional integration data.
    """

    spec: MeditationSpec
    voices: List[VoiceOutput] = field(default_factory=list)
    collisions: List[Collision] = field(default_factory=list)
    emergent_sequence: List[str] = field(default_factory=list)
    convergence: List[str] = field(default_factory=list)
    preserved_dissent: List[str] = field(default_factory=list)
    irreducible_verdict: str = ""
    l3_principle: str = ""
    integration_gate: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    @property
    def is_complete(self) -> bool:
        """A meditation is complete if it has voices, collisions, and a verdict."""
        return bool(self.voices) and bool(self.collisions) and bool(self.irreducible_verdict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "spec": self.spec.to_dict(),
            "voices": [v.to_dict() for v in self.voices],
            "collisions": [
                {
                    "title": c.title,
                    "voices_involved": c.voices_involved,
                    "tension": c.tension,
                    "resolution_path": c.resolution_path,
                }
                for c in self.collisions
            ],
            "emergent_sequence": self.emergent_sequence,
            "convergence": self.convergence,
            "preserved_dissent": self.preserved_dissent,
            "irreducible_verdict": self.irreducible_verdict,
            "l3_principle": self.l3_principle,
            "integration_gate": self.integration_gate,
            "error": self.error,
            "is_complete": self.is_complete,
        }


# ── Lens Registry Functions ───────────────────────────────────────────────────
#
# M2 COMPLIANT: Entity names are loaded from WAD YAML config at
# config/wads/<iwad>/meditate/lenses.yaml, NOT hardcoded here.
# Use lens_registry.py for WAD-backed loading.
# Fallback below uses generic lens IDs only (no entity names).


def get_default_lenses() -> list[PersonaSpec]:
    """Minimal generic fallback when no WAD lens config is available.

    Uses abstract lens IDs (not entity names) to remain M2-compliant.
    WAD-backed loading via ``lens_registry.py`` is the primary path.
    """
    return [
        PersonaSpec(
            name="Infrastructure",
            domain="Infrastructure",
            mandate_lens="Focus on physical substrate, systems, and reliability.",
        ),
        PersonaSpec(
            name="Engineering",
            domain="Engineering",
            mandate_lens="Focus on code quality, architecture, and implementation.",
        ),
        PersonaSpec(
            name="Governance",
            domain="Governance",
            mandate_lens="Focus on compliance, standards, and mandates.",
        ),
        PersonaSpec(
            name="Integration",
            domain="Integration",
            mandate_lens="Focus on APIs, protocols, and connections between systems.",
        ),
        PersonaSpec(
            name="Validation",
            domain="Validation",
            mandate_lens="Focus on testing, stress, and breaking assumptions.",
        ),
    ]
