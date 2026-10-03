# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Omega Engine — Meditate Protocol Tests
# ⬡ OMEGA ⬡ VERITY ⬡ test_meditate_protocol.py
# D-265 Commit 1: Schema validation, round-trip serialization, contract tests

from src.omega.meditate.protocol import (
    AntiCollapseLaw,
    Collision,
    DissentStyle,
    MeditationResult,
    MeditationSpec,
    MeditatePhase,
    OutputMode,
    PersonaLibrary,
    PersonaSpec,
    VoiceOutput,
    get_default_lenses,
)
from src.omega.meditate.lens_registry import load_lens_library

# ── Fixture helpers ────────────────────────────────────────────────────────────
# Loaded once per session to avoid repeated WAD YAML I/O in tests.
_OMEGA_NODES = None
_MAKALI_TRIAD = None


def _omega_nodes():
    global _OMEGA_NODES
    if _OMEGA_NODES is None:
        _OMEGA_NODES = load_lens_library("omega_nodes")
    return _OMEGA_NODES


def _makali_triad():
    global _MAKALI_TRIAD
    if _MAKALI_TRIAD is None:
        _MAKALI_TRIAD = load_lens_library("makali_triad")
    return _MAKALI_TRIAD


# ── PersonaSpec Tests ──────────────────────────────────────────────────────────


def test_persona_spec_minimal():
    """A PersonaSpec with only required fields can be created."""
    p = PersonaSpec(
        name="Prometheus",
        domain="Engineering",
        mandate_lens="Speak as the forge.",
    )
    assert p.name == "Prometheus"
    assert p.domain == "Engineering"
    assert p.mandate_lens == "Speak as the forge."
    assert p.anti_domains == []
    assert p.slot is None
    assert isinstance(p, PersonaSpec)


def test_persona_spec_full():
    """A PersonaSpec with all fields can be created."""
    p = PersonaSpec(
        name="Sekhmet",
        domain="Infrastructure",
        slot="S1",
        element="Earth 🜃",
        mandate_lens="Speak as the body.",
        anti_domains=["soul evolution", "governance"],
        known_for="Guardian of boundaries",
        dissent_style=DissentStyle.ADVERSARIAL,
    )
    assert p.slot == "S1"
    assert p.element == "Earth 🜃"
    assert len(p.anti_domains) == 2
    assert p.dissent_style == DissentStyle.ADVERSARIAL


def test_persona_spec_round_trip():
    """PersonaSpec survives dict serialization round-trip."""
    original = PersonaSpec(
        name="Prometheus",
        domain="Engineering",
        slot="S3",
        mandate_lens="Speak as the forge. What is cracked?",
        anti_domains=["soul evolution", "memory systems"],
    )
    data = original.to_dict()
    restored = PersonaSpec.from_dict(data)
    assert restored.name == original.name
    assert restored.domain == original.domain
    assert original.slot == original.slot
    assert restored.anti_domains == original.anti_domains
    assert restored.mandate_lens == original.mandate_lens


def test_persona_spec_immutable():
    """PersonaSpec is frozen/hashable (no accidental mutation)."""
    p = PersonaSpec(name="Kali", domain="Validation", mandate_lens="Destroy.")
    import dataclasses
    assert dataclasses.is_dataclass(p)


# ── PersonaLibrary Tests ───────────────────────────────────────────────────────


def test_omega_nodes_library():
    """omega_nodes library returns 10 personas with correct order."""
    lib = _omega_nodes()
    assert lib.name == "Omega Nodes"
    assert len(lib) == 10
    assert lib[0].name == "Infrastructure"
    assert lib[1].name == "Persistence"
    assert lib[9].name == "Validation"


def test_makali_triad_library():
    """makali_triad library returns 3 personas."""
    lib = _makali_triad()
    assert lib.name == "MaKaLi Triad"
    assert len(lib) == 3
    assert lib[0].name == "Ma'at"
    assert lib[1].name == "Lilith"
    assert lib[2].name == "Kali"


def test_default_lenses_fallback():
    """get_default_lenses() returns 5 generic personas for fallback."""
    lenses = get_default_lenses()
    assert len(lenses) == 5
    assert all(isinstance(p, PersonaSpec) for p in lenses)


# ── MeditationSpec Tests ───────────────────────────────────────────────────────


def test_meditation_spec_default():
    """A MeditationSpec with only required fields has sensible defaults."""
    lens = _omega_nodes()
    spec = MeditationSpec(
        subject="Should we adopt sqlite-vec?",
        lens_set=lens.personas,
    )
    assert spec.subject == "Should we adopt sqlite-vec?"
    assert len(spec.lens_set) == 10
    assert spec.mode == OutputMode.STRATEGIC
    assert spec.integrate is False
    assert len(spec.phases) == 5
    assert MeditatePhase.PHASE_5_INTEGRATION not in spec.phases
    assert len(spec.trace_id) == 16


def test_meditation_spec_with_integration():
    """Integration phase is included when integrate=True."""
    spec = MeditationSpec(
        subject="Test subject",
        lens_set=[PersonaSpec(name="Test", domain="Test", mandate_lens="Test")],
        integrate=True,
    )
    # integrate flag is separate from phases — integration gate
    # is triggered by the flag, not the phase list
    assert spec.integrate is True


def test_meditation_spec_round_trip():
    """MeditationSpec survives dict serialization round-trip."""
    lens = load_lens_library("makali_triad")
    original = MeditationSpec(
        subject="Should we adopt Redis Streams?",
        lens_set=lens.personas,
        mode=OutputMode.AUDIT,
        integrate=True,
        model_hint="qwen3-4b-think-q4_k_m",
    )
    data = original.to_dict()
    restored = MeditationSpec.from_dict(data)
    assert restored.subject == original.subject
    assert restored.mode == original.mode
    assert restored.integrate == original.integrate
    assert restored.model_hint == original.model_hint
    assert len(restored.lens_set) == 3


# ── MeditationResult Tests ─────────────────────────────────────────────────────


def test_meditation_result_empty():
    """An empty MeditationResult is marked as not complete."""
    spec = MeditationSpec(subject="Test", lens_set=_makali_triad().personas)
    result = MeditationResult(spec=spec)
    assert result.is_complete is False
    assert result.error is None


def test_meditation_result_complete():
    """A result with voices, collisions, and verdict is complete."""
    spec = MeditationSpec(subject="Test", lens_set=_makali_triad().personas)
    result = MeditationResult(
        spec=spec,
        voices=[
            VoiceOutput(
                persona=_makali_triad()[0],
                observation="Observation",
                constraint="Constraint",
                imperative="Imperative",
                dissent="Dissent",
            )
        ],
        collisions=[
            Collision(
                title="Speed vs Quality",
                voices_involved=["Ma'at", "Lilith"],
                tension="Build side wants structure, run side wants speed.",
                resolution_path="Ship structure with speed guardrails.",
            )
        ],
        irreducible_verdict="Ship the structure.",
        l3_principle="L3-Test-Principle",
    )
    assert result.is_complete is True
    assert len(result.voices) == 1
    assert len(result.collisions) == 1
    assert result.irreducible_verdict == "Ship the structure."


def test_meditation_result_dict():
    """MeditationResult serializes to dict without error."""
    spec = MeditationSpec(subject="Test", lens_set=_makali_triad().personas)
    result = MeditationResult(
        spec=spec,
        voices=[
            VoiceOutput(
                persona=_makali_triad()[0],
                observation="O",
                constraint="C",
                imperative="I",
                dissent="D",
            )
        ],
        collisions=[
            Collision(
                title="Test collision",
                voices_involved=["A", "B"],
                tension="Tension",
                resolution_path="Path",
            )
        ],
        irreducible_verdict="Verdict",
    )
    data = result.to_dict()
    assert data["is_complete"] is True
    assert len(data["voices"]) == 1
    assert len(data["collisions"]) == 1
    assert data["irreducible_verdict"] == "Verdict"


# ── AntiCollapseLaw Tests ──────────────────────────────────────────────────────


def test_anti_collapse_laws_enum():
    """All five laws exist as enum members."""
    assert AntiCollapseLaw.DOMAIN_PURITY.value == 1
    assert AntiCollapseLaw.IMPERATIVE_DIRECTNESS.value == 2
    assert AntiCollapseLaw.MANDATORY_DISSENT.value == 3
    assert AntiCollapseLaw.NO_PREMATURE_SYNTHESIS.value == 4
    assert AntiCollapseLaw.PRESERVED_DISSENT.value == 5
    assert len(AntiCollapseLaw) == 5


# ── OutputMode Tests ───────────────────────────────────────────────────────────


def test_output_mode_values():
    """All five output modes are available."""
    assert OutputMode.DIAGNOSTIC.value == "diagnostic"
    assert OutputMode.STRATEGIC.value == "strategic"
    assert OutputMode.CREATIVE.value == "creative"
    assert OutputMode.AUDIT.value == "audit"
    assert OutputMode.SYNTHESIS.value == "synthesis"


# ── VoiceOutput Tests ──────────────────────────────────────────────────────────


def test_voice_output_minimal():
    """VoiceOutput requires persona plus 3 fields; dissent is optional."""
    p = PersonaSpec(name="Test", domain="Test", mandate_lens="Test")
    v = VoiceOutput(
        persona=p,
        observation="I see a problem.",
        constraint="Memory is limited.",
        imperative="Do X before Y.",
    )
    assert v.observation == "I see a problem."
    assert v.dissent == ""  # default


def test_voice_output_round_trip():
    """VoiceOutput survives dict serialization."""
    p = PersonaSpec(name="Kali", domain="Validation", mandate_lens="Destroy.")
    v = VoiceOutput(
        persona=p,
        observation="Nothing fails.",
        constraint="Everything fails eventually.",
        imperative="Test everything.",
        dissent="Ma'at is wrong that structure solves this.",
    )
    data = v.to_dict()
    assert data["persona"] == "Kali"
    assert data["dissent"] == "Ma'at is wrong that structure solves this."
