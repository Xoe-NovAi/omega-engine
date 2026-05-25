# 🔱 Iris Intent Matcher
# AP: AP-NOVA-MATCHER-v1.0.0
# Lightweight intent detection for the always-on Iris container.

import re
from typing import Optional, Tuple


class IntentMatcher:
    """Detects user intent from query text."""

    # Patterns for entity-less routing
    GREETING = re.compile(r"^(hi|hello|hey|greetings|good\s+(morning|afternoon|evening))", re.IGNORECASE)
    FAREWELL = re.compile(r"^(bye|goodbye|exit|quit|thanks?|thank you)", re.IGNORECASE)
    HELP = re.compile(r"(help|what can you do|commands|how do)", re.IGNORECASE)

    # Voice-specific patterns
    REPEAT = re.compile(r"(repeat|say that again|what did you say)", re.IGNORECASE)
    VOLUME = re.compile(r"(volume|louder|softer|quieter)", re.IGNORECASE)
    SPEED = re.compile(r"(speed|faster|slower)", re.IGNORECASE)

    # @summon pattern: single word entity name only
    AT_SUMMON = re.compile(r"^@(\w+)[,:\s]+(.+)$", re.IGNORECASE)
    # Hey/Summon + multi-word entity until comma or colon
    HEY_SUMMON = re.compile(r"^(?:hey\s+|summon\s+)(.+?)[,:]\s*(.*)$", re.IGNORECASE)

    def classify(self, text: str) -> Tuple[str, Optional[str]]:
        """Classify intent and return (intent_type, entity_name).

        Returns:
            ("summon", entity_name) — explicit entity summon
            ("domain", None) — needs domain routing
            ("direct", None) — Iris can answer directly
            ("voice_cmd", None) — voice control command
        """
        # Check for @summon pattern (@Entity query)
        match = self.AT_SUMMON.match(text.strip())
        if match:
            return ("summon", match.group(1).strip())

        # Check for Hey Entity or Summon Entity patterns
        match = self.HEY_SUMMON.match(text.strip())
        if match:
            return ("summon", match.group(1).strip())

        # Check for voice commands
        if self.REPEAT.search(text):
            return ("voice_cmd", "repeat")
        if self.VOLUME.search(text):
            return ("voice_cmd", "volume")
        if self.SPEED.search(text):
            return ("voice_cmd", "speed")

        # Check for greetings/farewells (Iris can handle directly)
        if self.GREETING.match(text):
            return ("direct", None)
        if self.FAREWELL.match(text):
            return ("direct", None)

        # Route everything else to Oracle domain matching
        return ("domain", None)

    def is_iris_capable(self, text: str) -> bool:
        """Can Iris answer this directly without routing to a Pillar Keeper?"""
        return bool(
            self.GREETING.match(text)
            or self.FAREWELL.match(text)
            or self.HELP.search(text)
        )

    def iris_response(self, text: str) -> Optional[str]:
        """Generate a direct response from Iris for simple queries."""
        if self.GREETING.match(text):
            return "Greetings, seeker. I am Iris, your voice interface. Speak your question, and I will carry it to the one who knows."
        if self.FAREWELL.match(text):
            return "May your path be illuminated. Call on me anytime."
        if self.HELP.search(text):
            return (
                "I can help you connect with any entity in your active IWAD. Try:\n"
                "  'summon [entity name]' — to converse with a specific entity\n"
                "  'ask [entity] about [topic]' — for expert guidance on a topic\n"
                "  '@[entity] [query]' — quick summon syntax\n"
                "  'add-entity [name]' — to create your own custom entity"
            )
        return None
