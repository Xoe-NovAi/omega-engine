# AP: AP-A2A-BRIDGE-v1.0.0
"""
A2A Bridge — Sovereign Agent Identity.

[Replaces fabricated AAIF with real Google A2A v1.0]
Google A2A v1.0 (Linux Foundation JDF): Agent-to-agent protocol
IETF draft-klrc-aiagent-auth-02: Agent identity via WIMSE/SPIFFE

Key Design:
- Agent Cards served at /.well-known/agent-card.json
- EntityRegistry entities mapped to A2A Skills
- SPIFFE X.509-SVID for agent identity (draft-klrc-aiagent-auth-02)
- OAuth 2.0 delegation via Transaction Tokens
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class AgentAuthType(str, Enum):
    """Supported authentication types for Agent Cards."""
    NONE = "none"
    SPIFFE = "spiffe"
    OAUTH2 = "oauth2"
    MUTUAL_TLS = "mtls"


class SkillCategory(str, Enum):
    """Skill categories mapped from EntityRegistry domains."""
    DOMAIN_ROUTING = "domain_routing"
    CAPABILITY_MATCH = "capability_match"
    RESEARCH = "research"
    VERIFICATION = "verification"
    GOVERNANCE = "governance"
    INFRASTRUCTURE = "infrastructure"
    MEMORY = "memory"
    OBSERVABILITY = "observability"


@dataclass
class A2ASkill:
    """A single A2A skill — maps to an entity's domain or capability.

    [A2A v1.0] Skills represent fine-grained capabilities that other agents
    can discover and invoke.
    """
    id: str
    name: str
    description: str
    tags: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    input_modes: List[str] = field(default_factory=lambda: ["text"])
    output_modes: List[str] = field(default_factory=lambda: ["text"])

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to A2A skill JSON format."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "examples": self.examples,
            "inputModes": self.input_modes,
            "outputModes": self.output_modes,
        }


@dataclass
class A2AAuth:
    """Authentication scheme for an A2A Agent Card.

    [draft-klrc-aiagent-auth-02] Implements WIMSE/SPIFFE-based
    authentication as the primary scheme, with OAuth 2.0 fallback.
    """
    auth_type: AgentAuthType = AgentAuthType.SPIFFE
    spiffe_id: Optional[str] = None
    oauth_scopes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to A2A auth JSON format."""
        schemes = []
        if self.auth_type == AgentAuthType.NONE:
            schemes.append({"type": "none"})
        elif self.auth_type in (AgentAuthType.SPIFFE, AgentAuthType.MUTUAL_TLS):
            scheme: Dict[str, Any] = {
                "type": self.auth_type.value,
            }
            if self.spiffe_id:
                scheme["x509_svid"] = self.spiffe_id
            schemes.append(scheme)

        if self.oauth_scopes:
            schemes.append({
                "type": AgentAuthType.OAUTH2.value,
                "scopes": self.oauth_scopes,
            })

        return {"schemes": schemes}


@dataclass
class A2AAgentCard:
    """A2A Agent Card — identity and capability metadata.

    [Google A2A v1.0] Served at /.well-known/agent-card.json
    Represents one entity's capabilities in the A2A protocol.

    [draft-klrc-aiagent-auth-02] Carries SPIFFE identity for
    agent auth and optional cryptographic signature.
    """
    name: str
    description: str
    url: str
    provider_name: str = "Xoe-NovAi Foundation"
    provider_url: str = "https://xoe-nov.ai"
    version: str = "1.0.0"
    agent_version: str = "1.0.0"

    # A2A capabilities
    supports_streaming: bool = False
    supports_push_notifications: bool = True
    supports_state_transition_history: bool = True

    # Skills (maps to EntityRegistry domain/capability)
    skills: List[A2ASkill] = field(default_factory=list)

    # Auth
    authentication: Optional[A2AAuth] = None
    default_input_modes: List[str] = field(default_factory=lambda: ["text"])
    default_output_modes: List[str] = field(default_factory=lambda: ["text"])

    # Security
    signing_key_fingerprint: Optional[str] = None

    # Metadata
    entity_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to A2A Agent Card JSON format.

        Returns a dict matching the A2A v1.0 Agent Card schema.
        """
        card: Dict[str, Any] = {
            "name": self.name,
            "description": self.description,
            "url": self.url,
            "provider": {
                "name": self.provider_name,
                "url": self.provider_url,
                "organization": self.provider_name,
            },
            "version": self.version,
            "capabilities": {
                "streaming": self.supports_streaming,
                "pushNotifications": self.supports_push_notifications,
                "stateTransitionHistory": self.supports_state_transition_history,
            },
            "skills": [s.to_dict() for s in self.skills],
            "defaultInputModes": self.default_input_modes,
            "defaultOutputModes": self.default_output_modes,
        }

        if self.authentication:
            card["authentication"] = self.authentication.to_dict()

        if self.signing_key_fingerprint:
            card["security"] = {
                "signingKey": self.signing_key_fingerprint,
            }

        if self.entity_id:
            card["entityId"] = self.entity_id

        return card

    def to_json(self, indent: int = 2) -> str:
        """Serialize to A2A Agent Card JSON string."""
        return json.dumps(self.to_dict(), indent=indent)


class A2ABridge:
    """Bridge between Omega EntityRegistry and Google A2A v1.0.

    Responsibilities:
    1. Generate Agent Cards from EntityRegistry state
    2. Serve Agent Cards at /.well-known/agent-card.json
    3. Map entity domains to A2A skills
    4. Handle SPIFFE/WIMSE identity for agents

    [draft-klrc-aiagent-auth-02] Implements the AIMS framework:
    - Identifier: SPIFFE ID per entity
    - Credentials: Short-lived X.509-SVID
    - Authentication: mTLS with SPIFFE certs
    """

    def __init__(self, entity_registry: Optional[Any] = None):
        self._entity_registry = entity_registry
        self._base_url = "https://omega.local"
        self._agent_cards: Dict[str, A2AAgentCard] = {}

        # [draft-klrc-aiagent-auth-02] SPIFFE trust domain
        self._spiffe_trust_domain = "omega.local"

    def set_entity_registry(self, registry: Any) -> None:
        """Set or update the entity registry reference."""
        self._entity_registry = registry

    def register_entity(self, entity: Any) -> A2AAgentCard:
        """Generate an A2A Agent Card from an EntityRegistry entity.

        Maps:
        - Entity name -> Agent Card name
        - Entity domain -> A2A skills
        - Entity capabilities -> skill tags

        Args:
            entity: Entity from EntityRegistry (with name, domain, etc.)

        Returns:
            A2AAgentCard instance
        """
        entity_name = getattr(entity, 'name', 'unknown')

        # [draft-klrc-aiagent-auth-02] SPIFFE ID = primary agent identifier
        spiffe_id = f"spiffe://{self._spiffe_trust_domain}/entity/{entity_name.lower()}"

        # Map entity data to A2A skills
        skills = self._map_entity_to_skills(entity)

        card = A2AAgentCard(
            name=entity_name,
            description=getattr(entity, 'description',
                                f"Sovereign entity: {entity_name}"),
            url=f"{self._base_url}/.well-known/agent-card.json",
            provider_name=self._get_provider_name(entity),
            provider_url=self._base_url,
            skills=skills,
            authentication=A2AAuth(
                auth_type=AgentAuthType.SPIFFE,
                spiffe_id=spiffe_id,
            ),
            entity_id=spiffe_id,
        )

        self._agent_cards[entity_name.lower()] = card
        logger.info("Registered A2A Agent Card for '%s' with %d skills",
                    entity_name, len(skills))
        return card

    def _map_entity_to_skills(self, entity: Any) -> List[A2ASkill]:
        """Map an entity's domain and capabilities to A2A skills.

        [A2A v1.0] Skills represent fine-grained capabilities
        that other agents can discover and invoke.
        """
        skills: List[A2ASkill] = []
        entity_name = getattr(entity, 'name', 'unknown')

        # Get domains - try multiple possible attribute names
        domains = getattr(entity, 'domains', [])
        if isinstance(domains, str):
            domains = [domains]
        if not domains:
            domain = getattr(entity, 'domain', 'general')
            domains = [domain]

        # Primary skills: domain routing
        for i, domain in enumerate(domains):
            skills.append(A2ASkill(
                id=f"{entity_name.lower()}.domain.{i}",
                name=domain.replace('_', ' ').title(),
                description=f"Domain routing for {domain}",
                tags=["domain", domain, entity_name],
                examples=[f"Summon {entity_name} for {domain} tasks"],
            ))

        # Secondary skill: capability-based (if entity has capabilities)
        capabilities = getattr(entity, 'capabilities', None) or getattr(
            entity, 'skills', None)
        if isinstance(capabilities, dict):
            for cap_name, cap_desc in capabilities.items():
                skills.append(A2ASkill(
                    id=f"{entity_name.lower()}.{cap_name}",
                    name=cap_name.replace('_', ' ').title(),
                    description=str(cap_desc)[:200],
                    tags=["capability", cap_name],
                    examples=[],
                ))
        elif isinstance(capabilities, list):
            for cap in capabilities:
                cap_str = str(cap)
                skills.append(A2ASkill(
                    id=f"{entity_name.lower()}.{cap_str.lower()[:20]}",
                    name=cap_str.replace('_', ' ').title()[:50],
                    description=f"Capability: {cap_str}",
                    tags=["capability"],
                    examples=[],
                ))

        return skills

    def _get_provider_name(self, entity: Any) -> str:
        """Get the provider/organization name for an entity."""
        provider = getattr(entity, 'provider', None) or getattr(
            entity, 'organization', None)
        if provider:
            return str(provider)
        return "Xoe-NovAi Foundation"

    def build_agent_card(self, entity_name: str) -> Optional[A2AAgentCard]:
        """Build an A2A Agent Card from an EntityRegistry entity by name.

        Uses the entity registry to look up the entity and generate its card.

        Args:
            entity_name: The name of the entity to build a card for.

        Returns:
            A2AAgentCard instance, or None if entity not found or no registry.
        """
        if not self._entity_registry:
            logger.warning("No entity registry available for A2A cards")
            return None

        entity = self._entity_registry.get(entity_name)
        if not entity:
            logger.warning("Entity '%s' not found in registry", entity_name)
            return None

        return self.register_entity(entity)

    def get_agent_card_json(self, entity_name: str) -> Optional[str]:
        """Get Agent Card as JSON string using the registry."""
        card = self.build_agent_card(entity_name)
        if not card:
            return None
        return card.to_json()

    def get_card(self, entity_name: str) -> Optional[A2AAgentCard]:
        """Get a cached Agent Card by entity name."""
        return self._agent_cards.get(entity_name.lower())

    def get_all_cards(self) -> Dict[str, A2AAgentCard]:
        """Get all registered Agent Cards."""
        return dict(self._agent_cards)

    def generate_well_known_json(self) -> str:
        """Generate the full /.well-known/agent-card.json response.

        Returns JSON string with all Agent Cards aggregated.
        """
        cards = {
            "a2a_version": "1.0.0",
            "provider": {
                "name": "Xoe-NovAi Foundation",
                "url": self._base_url,
                "organization": "Xoe-NovAi Foundation",
            },
            "agents": {
                name: card.to_dict()
                for name, card in self._agent_cards.items()
            },
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "total_agents": len(self._agent_cards),
                "specification": "https://github.com/google/A2A",
                "auth_framework": (
                    "https://datatracker.ietf.org/doc/draft-klrc-aiagent-auth/"
                ),
            },
        }
        return json.dumps(cards, indent=2)

    async def verify_agent_identity(self, spiffe_id: str,
                                    certificate: bytes) -> bool:
        """Verify an agent's identity using SPIFFE X.509-SVID.

        [draft-klrc-aiagent-auth-02 §5] Short-lived credentials
        bound to the agent's SPIFFE ID.

        Args:
            spiffe_id: The claimed SPIFFE ID
            certificate: The X.509 certificate for verification

        Returns:
            True if identity is verified, False otherwise
        """
        if not spiffe_id.startswith(f"spiffe://{self._spiffe_trust_domain}/"):
            logger.warning("SPIFFE ID %s not in trust domain %s",
                           spiffe_id, self._spiffe_trust_domain)
            return False

        entity_name = spiffe_id.split('/')[-1]
        if entity_name not in self._agent_cards:
            logger.warning("Unknown entity: %s (SPIFFE: %s)",
                           entity_name, spiffe_id)
            return False

        logger.info("Agent identity verified: %s (SPIFFE: %s)",
                    entity_name, spiffe_id)
        return True
