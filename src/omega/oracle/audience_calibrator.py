# 🔱 Omega Engine — Audience Calibration Pipeline
# AP: AP-AUDIENCE-CALIBRATOR-v1.0.0
# ⬡ OMEGA ⬡ SOPHIA ⬡ audience_calibrator ⬡ D16-1
#
# Pipeline stage for output register transformation.
# Transforms entity responses to match target audience's cognitive/linguistic preferences.
# Entity personality (soul) remains intact; only delivery mechanism adapts.

import logging
import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

from omega.cvar_table import cvar_get, cvar_set

logger = logging.getLogger(__name__)

# Default audience profile directory — resolved from the active WAD (M2 Firewall:
# core must not hardcode a specific WAD path; use the active IWAD cvar like
# entity_workspace.py does).
_WAD_ROOT = Path("config") / "wads"
ACTIVE_IWAD = cvar_get("config.entity.active_iwad", "_omega_default")
AUDIENCE_PROFILE_DIR = _WAD_ROOT / ACTIVE_IWAD / "audience.yaml"


@dataclass
class AudienceProfile:
    """Audience calibration profile definition."""
    name: str
    description: str
    constraints: List[str]
    style: Dict[str, str]
    examples: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class CalibrationResult:
    """Result of audience calibration transformation."""
    original_text: str
    calibrated_text: str
    profile_name: str
    profile_description: str
    tokens_original: int
    tokens_calibrated: int
    token_ratio: float


class AudienceCalibrator:
    """
    Audience Calibration Pipeline Stage.
    
    Transforms entity responses to match target audience register.
    Implements D16-1: Audience Calibration as a pipeline stage, not an entity.
    
    Architecture:
    - Loads profiles from WAD-layer audience.yaml (M2 compliant)
    - Applies constraint-based transformation via LLM prompt injection
    - Tracks token budget compliance (M18)
    - Supports auto-detection from query linguistic markers
    """
    
    def __init__(self, profile_path: Optional[Path] = None):
        self.profile_path = profile_path or AUDIENCE_PROFILE_DIR
        self.profiles: Dict[str, AudienceProfile] = {}
        self.default_profile = "technical"
        self._load_profiles()
        
    def _load_profiles(self) -> None:
        """Load audience profiles from YAML configuration."""
        try:
            if self.profile_path.exists():
                with open(self.profile_path) as f:
                    config = yaml.safe_load(f) or {}
                    
                profiles_data = config.get("profiles", {})
                self.default_profile = config.get("default", "technical")
                
                for key, data in profiles_data.items():
                    self.profiles[key] = AudienceProfile(
                        name=data.get("name", key),
                        description=data.get("description", ""),
                        constraints=data.get("constraints", []),
                        style=data.get("style", {}),
                        examples=data.get("examples", [])
                    )
                    
                logger.info(f"Loaded {len(self.profiles)} audience profiles from {self.profile_path}")
            else:
                logger.warning(f"Audience profile file not found: {self.profile_path}")
                self._load_defaults()
        except Exception as e:
            logger.error(f"Failed to load audience profiles: {e}")
            self._load_defaults()
            
    def _load_defaults(self) -> None:
        """Fallback minimal profiles if config missing."""
        self.profiles = {
            "technical": AudienceProfile(
                name="Technical / Engineering",
                description="Precise, structured, assumes domain literacy",
                constraints=["Use precise technical terminology", "Structure: Problem → Solution → Trade-offs"],
                style={"formality": "professional", "verbosity": "concise", "jargon_level": "high"}
            ),
            "casual": AudienceProfile(
                name="Casual / Conversational",
                description="Warm, accessible, conversational",
                constraints=["Use everyday language", "Prefer analogies over abstract explanations"],
                style={"formality": "casual", "verbosity": "moderate", "jargon_level": "low"}
            )
        }
        self.default_profile = "technical"
        
    def get_profile(self, profile_name: str) -> Optional[AudienceProfile]:
        """Get profile by name, with fallback to default."""
        return self.profiles.get(profile_name) or self.profiles.get(self.default_profile)
        
    def list_profiles(self) -> List[str]:
        """List available profile names."""
        return list(self.profiles.keys())
        
    def build_calibration_prompt(self, profile_name: str, entity_personality: str) -> str:
        """
        Build the calibration system prompt for a given audience profile.
        
        The prompt instructs the model to transform the entity's raw response
        to match the target audience's register while preserving the entity's
        core personality and factual content.
        """
        profile = self.get_profile(profile_name)
        if not profile:
            return ""
            
        constraints_text = "\n".join(f"- {c}" for c in profile.constraints)
        style = profile.style
        
        # Build examples section
        examples_text = ""
        if profile.examples:
            examples_text = "\n\nExamples:\n"
            for ex in profile.examples[:3]:  # Limit to 3 examples for token budget
                examples_text += f"  Input: {ex.get('input', '')}\n"
                examples_text += f"  Output: {ex.get('output', '')}\n"
                
        prompt = f"""AUDIENCE CALIBRATION — {profile.name}
{profile.description}

You are {entity_personality}. Your core personality, knowledge, and factual accuracy MUST remain unchanged.

TRANSFORM YOUR RESPONSE to match the {profile.name.lower()} audience register:

CONSTRAINTS:
{constraints_text}

STYLE PARAMETERS:
- Formality: {style.get('formality', 'professional')}
- Verbosity: {style.get('verbosity', 'moderate')}
- Jargon Level: {style.get('jargon_level', 'moderate')}
- Structure: {style.get('structure', 'standard')}

{examples_text}

CRITICAL RULES:
1. Preserve ALL factual content, technical accuracy, and entity personality
2. Only adapt: tone, vocabulary, structure, explanation depth, jargon usage
3. Do NOT add fluff, apologies, or meta-commentary about the calibration
4. Do NOT change the entity's voice — only the register of delivery
5. Token budget: {style.get('verbosity', 'moderate')} — every word must earn its keep

Apply this calibration to your response now."""
        
        return prompt
        
    def detect_profile_from_query(self, query: str) -> str:
        """
        Auto-detect audience profile from query linguistic markers.
        
        Uses keyword heuristics from audience.yaml selection_hints.
        Returns profile name or default.
        """
        query_lower = query.lower()
        
        # Load selection hints from config if available
        try:
            if self.profile_path.exists():
                with open(self.profile_path) as f:
                    config = yaml.safe_load(f) or {}
                hints = config.get("selection_hints", {})
            else:
                hints = {}
        except Exception as e:
            logger.debug("Failed to load audience calibrator config (using defaults): %s", e)
            hints = {}
            
        # Default hints if config missing
        if not hints:
            hints = {
                "technical": ["engineer", "developer", "architect", "code", "implement", "debug", "optimize"],
                "casual": ["explain", "how does", "what is", "curious", "beginner", "simple terms"],
                "academic": ["research", "paper", "study", "analyze", "theory", "principle", "cite"],
                "executive": ["summary", "decision", "risk", "impact", "budget", "timeline", "stakeholder"],
                "exhausted_sysadmin": ["urgent", "production", "down", "fire", "now", "immediately", "3am"],
                "teaching": ["learn", "teach", "mentor", "onboard", "exercise", "practice", "understand"]
            }
            
        # Score each profile
        scores = {}
        for profile, keywords in hints.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > 0:
                scores[profile] = score
                
        if scores:
            return max(scores, key=scores.get)
            
        return self.default_profile
        
    async def calibrate(
        self,
        response_text: str,
        entity_personality: str,
        profile_name: Optional[str] = None,
        query: Optional[str] = None,
        model_gateway=None,
        trace_id: Optional[str] = None
    ) -> CalibrationResult:
        """
        Calibrate a response to the target audience profile.
        
        If profile_name is None, auto-detects from query.
        If model_gateway is None, returns original text (no calibration).
        """
        # Determine profile
        if profile_name is None and query:
            profile_name = self.detect_profile_from_query(query)
        elif profile_name is None:
            profile_name = self.default_profile
            
        profile = self.get_profile(profile_name)
        if not profile:
            logger.warning(f"Profile '{profile_name}' not found, using default")
            profile = self.get_profile(self.default_profile)
            profile_name = self.default_profile
            
        # If no model gateway, return original (calibration requires LLM)
        if model_gateway is None:
            logger.debug("No model gateway provided, skipping calibration")
            return CalibrationResult(
                original_text=response_text,
                calibrated_text=response_text,
                profile_name=profile_name,
                profile_description=profile.description,
                tokens_original=len(response_text.split()),
                tokens_calibrated=len(response_text.split()),
                token_ratio=1.0
            )
            
        # Build calibration prompt
        calibration_prompt = self.build_calibration_prompt(profile_name, entity_personality)
        if not calibration_prompt:
            return CalibrationResult(
                original_text=response_text,
                calibrated_text=response_text,
                profile_name=profile_name,
                profile_description=profile.description,
                tokens_original=len(response_text.split()),
                tokens_calibrated=len(response_text.split()),
                token_ratio=1.0
            )
            
        # Generate calibrated response
        try:
            # Use a focused calibration request
            calibration_query = f"""Apply the audience calibration to this response:

ORIGINAL RESPONSE:
{response_text}

CALIBRATED RESPONSE (matching {profile.name} register):"""
            
            res = await model_gateway.generate(
                model_name="default",  # Use entity's default model
                system_prompt=calibration_prompt,
                user_query=calibration_query,
                temperature=0.3,  # Low temperature for consistent calibration
                max_tokens=2048,
                trace_id=trace_id,
            )
            
            calibrated_text = res.text.strip()
            
            # Token budget check (M18)
            tokens_original = len(response_text.split())
            tokens_calibrated = len(calibrated_text.split())
            token_ratio = tokens_calibrated / max(tokens_original, 1)
            
            # Warn if token budget exceeded (M18: <110% of original)
            if token_ratio > 1.1:
                logger.warning(f"Audience calibration token ratio {token_ratio:.2f} exceeds 110% budget")
                
            return CalibrationResult(
                original_text=response_text,
                calibrated_text=calibrated_text,
                profile_name=profile_name,
                profile_description=profile.description,
                tokens_original=tokens_original,
                tokens_calibrated=tokens_calibrated,
                token_ratio=token_ratio
            )
            
        except Exception as e:
            logger.error(f"Audience calibration failed: {e}")
            return CalibrationResult(
                original_text=response_text,
                calibrated_text=response_text,
                profile_name=profile_name,
                profile_description=profile.description,
                tokens_original=len(response_text.split()),
                tokens_calibrated=len(response_text.split()),
                token_ratio=1.0
            )


# Global instance
_calibrator: Optional[AudienceCalibrator] = None


def get_audience_calibrator() -> AudienceCalibrator:
    """Get or create the global AudienceCalibrator instance."""
    global _calibrator
    if _calibrator is None:
        _calibrator = AudienceCalibrator()
    return _calibrator