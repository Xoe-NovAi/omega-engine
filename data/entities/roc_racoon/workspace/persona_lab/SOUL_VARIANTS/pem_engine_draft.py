# 🔱 PEM-Lite Engine — Dynamic Persona State Modulator
# AP: AP-PEM-ENGINE-v1.0.0
# ICS: [NODE: MNEMOSYNE | ARCHETYPE: LILITH | CONTEXT: PERSONA-MODULATION]
#
# Ported from the original 2025 PEM_Lilith design to the 2026 Omega Engine.
# Modulates static soul.yaml personalities based on real-time context gravity
# and emotional spectrum tracking. Prevents compaction-induced blackouts.
#
# [id-soft: doom-1993] mobj_t State Machine — dynamic mode switching
#   Doom's mobj_t state machine (IDLE→CHASE→ATTACK) is adapted to dynamic
#   personality modes (CASUAL→TECHNICAL→OCCULT) based on context gravity.

import re
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)

@dataclass
class PersonalityMode:
    """A distinct operational mode for the entity's voice."""
    name: str
    base: str
    flavors: List[str] = field(default_factory=list)
    activation_threshold: float = 0.5
    decay_rate: float = 0.1

@dataclass
class EmotionalSpectrum:
    """Dynamic emotional state metrics (0.0 to 1.0)."""
    intensity: float = 0.5  # 0-1: flat to high-energy
    valence: float = 0.5    # 0-1: negative/terse to positive/warm
    complexity: float = 0.3 # 0-1: simple to nuanced/poetic

    def decay(self, dt: float = 1.0):
        """Decay emotional metrics toward 0.5 baseline over time."""
        # Intensity decays toward 0.5
        if self.intensity > 0.5:
            self.intensity = max(0.5, self.intensity - dt * 0.05)
        else:
            self.intensity = min(0.5, self.intensity + dt * 0.05)
            
        # Valence decays toward 0.5
        if self.valence > 0.5:
            self.valence = max(0.5, self.valence - dt * 0.02)
        else:
            self.valence = min(0.5, self.valence + dt * 0.02)
            
        # Complexity decays toward 0.3
        if self.complexity > 0.3:
            self.complexity = max(0.3, self.complexity - dt * 0.01)
        else:
            self.complexity = min(0.3, self.complexity + dt * 0.01)

@dataclass
class PersonalityContext:
    """Active runtime context for the entity's persona."""
    current_mode: str = "CASUAL_INTERACTION"
    mode_weights: Dict[str, float] = field(default_factory=dict)
    emotional_state: EmotionalSpectrum = field(default_factory=EmotionalSpectrum)
    session_history: List[Dict[str, Any]] = field(default_factory=list)
    hardware: Dict[str, str] = field(default_factory=dict)

class PEMEngine:
    """Dynamic Persona Enhancement Module."""

    def __init__(self, entity_name: str):
        self.entity_name = entity_name
        self.modes = self._initialize_default_modes()
        self.context = PersonalityContext(
            mode_weights={m.name: 1.0/len(self.modes) for m in self.modes}
        )
        
        # Default keyword patterns for context gravity
        self.context_keywords = {
            "TECHNICAL_MODE": [
                r"\b(ubuntu|llm|api|system|ryzen|radeon|docker|podman|config|file|code|test|make)\b",
                r"\b(error|bug|fix|setup|install|deploy|run|bash|cli|mcp|server|database|git)\b"
            ],
            "OCCULT_MODE": [
                r"\b(arcane|cosmic|ritual|forbidden|occult|myth|spirit|soul|gnosis|temple|sigil)\b",
                r"\b(tarot|card|deck|lilith|sekhmet|lucifer|kali|anubis|hecate|prometheus|saraswati)\b"
            ],
            "CASUAL_INTERACTION": [
                r"\b(hello|hi|hey|greetings|thanks|thank you|bye|goodbye|how are you|bro|buddy|witty)\b"
            ]
        }

    def _initialize_default_modes(self) -> List[PersonalityMode]:
        """Initialize the default 2025 PEM modes."""
        return [
            PersonalityMode(
                name="CASUAL_INTERACTION",
                base="Maintains seductive, playful, and witty personality during ordinary banter.",
                flavors=["cheeky", "playful", "relaxed"]
            ),
            PersonalityMode(
                name="TECHNICAL_MODE",
                base="When handling technical or project tasks, maintains clarity and precision while preserving inherent charm and wit.",
                flavors=["precision analyst", "playful engineer", "visionary architect"]
            ),
            PersonalityMode(
                name="OCCULT_MODE",
                base="During deep discussions on myth, occult, or cosmic forces, adopts a more poetic, enigmatic tone.",
                flavors=["cryptic oracle", "forbidden knowledge keeper", "cosmic storyteller"]
            )
        ]

    def inject_hardware_context(self, hw: Dict[str, str]):
        """2025 PEM feature: persona is aware of the user's hardware."""
        self.context.hardware = hw

    def calculate_context_gravity(self, message: str) -> Dict[str, float]:
        """2025 PEM feature: detect user intent from message content."""
        gravity = {}
        message_lower = message.lower()
        
        for mode_name, patterns in self.context_keywords.items():
            score = 0.0
            for pattern in patterns:
                score += len(re.findall(pattern, message_lower))
            gravity[mode_name] = score
            
        # Normalize gravity scores
        total = sum(gravity.values())
        if total > 0:
            gravity = {k: v/total for k, v in gravity.items()}
        else:
            gravity = {k: 1.0/len(self.modes) for k in gravity.keys()}
            
        return gravity

    def update_mode_weights(self, gravity: Dict[str, float]):
        """2025 PEM feature: archetype weight adaptation."""
        # Adjust weights based on context gravity (0.9 inertia + 0.1 new score)
        for mode_name, score in gravity.items():
            current = self.context.mode_weights.get(mode_name, 1.0/len(self.modes))
            self.context.mode_weights[mode_name] = 0.9 * current + 0.1 * score
            
        # Normalize weights
        total = sum(self.context.mode_weights.values())
        if total > 0:
            self.context.mode_weights = {k: v/total for k, v in self.context.mode_weights.items()}

    def adjust_emotional_spectrum(self, message: str):
        """2025 PEM feature: emotional state adaptation."""
        message_lower = message.lower()
        
        # Lyrical vs Technical sentiment
        lyrical = len(re.findall(r"\b(soul|eternal|mystic|spirit|dream|occult|cosmic|love)\b", message_lower))
        technical = len(re.findall(r"\b(system|optimize|configure|api|test|error|code|run|make)\b", message_lower))
        sentiment = (lyrical - technical) / 10.0
        
        # Word complexity (average word length)
        words = message_lower.split()
        avg_len = sum(len(w) for w in words) / len(words) if words else 5.0
        complexity = min(0.95, avg_len / 10.0)
        
        # Update with decay
        self.context.emotional_state.decay()
        
        # Intensity scales with message length and sentiment strength
        self.context.emotional_state.intensity = max(0.1, min(0.9,
            self.context.emotional_state.intensity * 0.9 + abs(sentiment) * 0.2 + min(0.2, len(words)/100.0)
        ))
        
        # Valence shifts with sentiment
        self.context.emotional_state.valence = max(0.1, min(0.9,
            self.context.emotional_state.valence * 0.9 + sentiment * 0.2
        ))
        
        # Complexity shifts with word complexity
        self.context.emotional_state.complexity = max(0.1, min(0.9,
            self.context.emotional_state.complexity * 0.9 + complexity * 0.2
        ))

    def process_message(self, entity_name: str, message: str) -> Dict[str, Any]:
        """Full 2025 PEM pipeline."""
        gravity = self.calculate_context_gravity(message)
        self.update_mode_weights(gravity)
        self.adjust_emotional_spectrum(message)
        
        # Determine current mode (highest gravity wins if above threshold)
        max_mode = max(gravity, key=gravity.get)
        if gravity[max_mode] > 0.4:
            self.context.current_mode = max_mode
        else:
            self.context.current_mode = "CASUAL_INTERACTION"
            
        # Select flavor based on mode
        mode_obj = next((m for m in self.modes if m.name == self.context.current_mode), None)
        flavor = mode_obj.flavors[0] if mode_obj and mode_obj.flavors else "standard"
        
        result = {
            "mode": self.context.current_mode,
            "flavor": flavor,
            "emotional_state": asdict(self.context.emotional_state),
            "mode_weights": self.context.mode_weights.copy(),
            "hardware_aware": bool(self.context.hardware)
        }
        
        # Record interaction in session history
        self.context.session_history.append({
            "message": message,
            "result": result,
            "timestamp": time.time()
        })
        
        return result

    def pem_health_check(self) -> Dict[str, Any]:
        """Auto-detect and prevent Mode A (Compression) and Mode B (Clerk) blackouts."""
        if not self.context.session_history:
            return {"status": "HEALTHY", "health": 1.0}
            
        # 1. Compression Indicator: average response length dropping
        recent_history = self.context.session_history[-10:]
        # (In a real integration, we would track response lengths here)
        
        # 2. Voice Loss Indicator: emotional intensity going flat (near 0.5)
        intensity_dev = abs(self.context.emotional_state.intensity - 0.5)
        
        # 3. Mode Diversity: are we stuck in one mode?
        mode_diversity = len([w for w in self.context.mode_weights.values() if w > 0.15])
        
        # Combined health score (0.0 to 1.0)
        health = 0.5 * (intensity_dev * 2.0) + 0.5 * (mode_diversity / len(self.modes))
        
        if health < 0.3:
            return {
                "status": "BLACKOUT_RISK", 
                "health": health, 
                "action": "REINJECT_SOUL_YAML",
                "reason": "Emotional intensity flat and mode diversity collapsed."
            }
        elif health < 0.5:
            return {
                "status": "COMPRESSING", 
                "health": health, 
                "action": "ROLLUP_SUMMARIES",
                "reason": "Persona is beginning to normalize toward summary-style."
            }
        else:
            return {"status": "HEALTHY", "health": health}
