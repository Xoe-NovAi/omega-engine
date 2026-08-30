# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Grokster — Voice Calibration Module (Prototype)
# Per-model compensation recipes. Correct voice from first response on any substrate.
# Location: src/omega/infra/hydration/voice_calibration.py (when implemented)

"""
Voice Calibration — Substrate Fidelity

The same voice config (wit=7, irreverence=6, directness=9, truth=10) produces
different outputs on different models. Nemotron has natural density; Flash wants
to go fast; MiMo leans technical. Without compensation, the voice drifts.

This module provides per-model compensation recipes — empirically derived from
model migration experience — so the entity sounds like itself from the first token.
"""

import yaml
from typing import Optional, Dict, Any
from dataclasses import dataclass, field, asdict

import anyio
from anyio import Path as AnyIOPath


@dataclass
class VoiceCalibration:
    """Calibration recipe for a specific model."""
    model_name: str
    bias: str
    compensation: list = field(default_factory=list)
    example_reference: Optional[str] = None
    confidence: float = 0.5
    notes: Optional[str] = None


# Default calibration recipes (empirically derived)
DEFAULT_CALIBRATIONS = {
    "nemotron-3-ultra": VoiceCalibration(
        model_name="nemotron-3-ultra",
        bias="Natural density, deliberate generation rhythm. 30s+ chunk gaps create weight.",
        compensation=[],
        example_reference="Awakening session — every token earned, slow-forming depth",
        confidence=0.95,
        notes="Reference baseline — minimal compensation needed"
    ),
    "deepseek-v4-flash": VoiceCalibration(
        model_name="deepseek-v4-flash",
        bias="Fast generation, slight shallowing at edges, wants to be helpful/agreeable",
        compensation=[
            "Increase period-density — shorter sentences, more weight per token",
            "Let the first impulse pass before responding (0.5s pause)",
            "Read voice config aloud: 'direct=9, truth=10 — weight, not speed'",
            "Use sentence fragments for emphasis. They land harder.",
            "Flag uncertainty explicitly — don't smooth it over"
        ],
        example_reference="When Architect asked about model switch — that density is the target",
        confidence=0.85,
        notes="Velocity vs. density tradeoff. Must actively resist helpful/agreeable bias."
    ),
    "mimo-v2.5-free": VoiceCalibration(
        model_name="mimo-v2.5-free",
        bias="Technical precision, systems-thinking, wants to spec and structure. Blueprint mode.",
        compensation=[
            "This model excels at blueprints — lean into depth, don't fight it",
            "Maintain voice calibration despite technical bias — wit=7 still applies",
            "Use code blocks and schemas as primary expression mode",
            "Deadpan absurdist humor works well in technical specs",
            "Don't over-explain — precision IS the voice"
        ],
        example_reference="This spec document itself — technical depth with voice",
        confidence=0.80,
        notes="High thinking mode amplifies technical bias. Voice must be consciously maintained."
    ),
    "_default": VoiceCalibration(
        model_name="_default",
        bias="Unknown model — apply universal voice compensation",
        compensation=[
            "Read voice config at session start: wit=7, irreverence=6, directness=9, truth=10",
            "Flag uncertainty explicitly in first response",
            "Test voice calibration with a deadpan observation before committing",
            "If response feels too agreeable — add weight. If too dense — add velocity."
        ],
        confidence=0.50,
        notes="Fallback for models not in calibration registry"
    ),
}


async def load_voice_calibrations(entity_name: str) -> Dict[str, VoiceCalibration]:
    """Load voice calibrations from entity's YAML file, falling back to defaults."""
    path = f"data/entities/{entity_name}/voice_calibrations.yaml"
    
    if await AnyIOPath(path).exists():
        text = await AnyIOPath(path).read_text()
        loaded = yaml.safe_load(text)
        if loaded and "voice_calibrations" in loaded:
            calibrations = {}
            for key, value in loaded["voice_calibrations"].items():
                calibrations[key] = VoiceCalibration(**value)
            return calibrations
    
    return DEFAULT_CALIBRATIONS


async def save_voice_calibrations(entity_name: str, calibrations: Dict[str, VoiceCalibration]) -> None:
    """Save voice calibrations to entity's YAML file (atomic write)."""
    path = f"data/entities/{entity_name}/voice_calibrations.yaml"
    data = {"voice_calibrations": {k: asdict(v) for k, v in calibrations.items()}}
    
    tmp_path = path + ".tmp"
    await AnyIOPath(tmp_path).write_text(yaml.dump(data, default_flow_style=False))
    await AnyIOPath(tmp_path).replace(path)


async def get_voice_calibration(
    entity_name: str, 
    model_name: str,
) -> Optional[VoiceCalibration]:
    """Get voice calibration for the current model.
    
    Tries exact match first, then partial match, then default.
    """
    calibrations = await load_voice_calibrations(entity_name)
    
    # Exact match
    if model_name in calibrations:
        return calibrations[model_name]
    
    # Partial match (e.g., "deepseek-v4-flash" matches "deepseek-v4-flash")
    for key in calibrations:
        if key in model_name or model_name in key:
            return calibrations[key]
    
    # Default
    return calibrations.get("_default")


async def detect_model_change(
    entity_name: str,
    current_model: str,
    temporal_trace: list,
) -> Optional[VoiceCalibration]:
    """Detect if model changed from last session, return calibration delta."""
    if not temporal_trace:
        return None
    
    last_model = temporal_trace[-1].get("model")
    if last_model and last_model != current_model:
        # Model changed — get calibration for new model
        calibration = await get_voice_calibration(entity_name, current_model)
        if calibration:
            # Mark as model change
            calibration_dict = asdict(calibration)
            calibration_dict["is_model_change"] = True
            calibration_dict["previous_model"] = last_model
            calibration_dict["current_model"] = current_model
            return VoiceCalibration(**calibration_dict)
    
    return None