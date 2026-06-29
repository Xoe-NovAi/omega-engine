"""Tests for A2A Agent Card bridge + SPIFFE auth.

Covers:
- A2AAgentCard.to_dict() generates valid A2A schema
- A2ABridge.build_agent_card() for known entities
- SPIFFE ID validity
- Skills from entity domains
- JSON serialization
- Graceful handling of non-existent entity
"""

import json
from datetime import datetime, timedelta, timezone

import pytest
from unittest.mock import MagicMock, patch

from omega.oracle.a2a_bridge import (
    A2ABridge, A2AAgentCard, A2ASkill, A2AAuth,
    AgentAuthType, SkillCategory,
)
from omega.oracle.a2a_auth import SPIFFEID, AgentCredential


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def bridge():
    """A2ABridge with no entity registry."""
    return A2ABridge()


@pytest.fixture
def bridge_with_registry():
    """A2ABridge with a mock entity registry."""
    bridge = A2ABridge()

    # Create a mock registry with get() returning entities
    registry = MagicMock()

    # Mock entity: Sophia
    sophia = MagicMock()
    sophia.name = "Sophia"
    sophia.domains = ["wisdom", "council", "oracle"]
    sophia.description = "The Akashic Record — containing field for all entities"
    sophia.capabilities = ["council", "oracle", "wisdom"]
    sophia.provider = None
    sophia.organization = None

    # Mock entity: Kali
    kali = MagicMock()
    kali.name = "Kali"
    kali.domains = ["transcendence", "oversight", "synthesis"]
    kali.description = "Grand Oversight — unifies Ma'at and Lilith"
    kali.capabilities = ["oversight", "synthesis", "council"]
    kali.provider = "Xoe-NovAi Foundation"
    kali.organization = None

    # Mock entity: Sentinel (P5)
    sentinel = MagicMock()
    sentinel.name = "Sentinel"
    sentinel.domains = ["security", "governance"]
    sentinel.description = "Sentinel — Mandate Enforcement"
    sentinel.capabilities = []
    sentinel.provider = None
    sentinel.organization = "Omega Engine"

    registry.get.side_effect = lambda name: {
        "sophia": sophia,
        "kali": kali,
        "sentinel": sentinel,
    }.get(name.lower(), None)

    bridge.set_entity_registry(registry)
    return bridge


@pytest.fixture
def mock_entity():
    """A simple mock entity for direct registration tests."""
    entity = MagicMock()
    entity.name = "TestEntity"
    entity.domains = ["test_domain"]
    entity.description = "Test entity for unit tests"
    entity.capabilities = ["research", "analysis"]
    entity.provider = None
    entity.organization = None
    return entity


# =============================================================================
# Tests: A2AAgentCard
# =============================================================================

class TestA2AAgentCard:
    """Tests for the A2AAgentCard dataclass and its serialization."""

    def test_to_dict_has_required_fields(self):
        """A2AAgentCard.to_dict() must include all A2A v1.0 required fields."""
        card = A2AAgentCard(
            name="Test",
            description="A test agent card",
            url="https://omega.local/.well-known/agent-card.json",
        )
        result = card.to_dict()

        # Required fields per A2A v1.0 spec
        assert result["name"] == "Test"
        assert result["description"] == "A test agent card"
        assert result["url"] == "https://omega.local/.well-known/agent-card.json"
        assert "provider" in result
        assert "version" in result
        assert "capabilities" in result
        assert "skills" in result
        assert "defaultInputModes" in result
        assert "defaultOutputModes" in result

    def test_to_dict_capabilities_structure(self):
        """Capabilities dict must have streaming, pushNotifications, stateTransitionHistory."""
        card = A2AAgentCard(
            name="Test",
            description="Test",
            url="https://omega.local",
        )
        result = card.to_dict()
        caps = result["capabilities"]
        assert "streaming" in caps
        assert "pushNotifications" in caps
        assert "stateTransitionHistory" in caps

    def test_to_dict_with_auth(self):
        """Card with SPIFFE authentication must include auth block."""
        card = A2AAgentCard(
            name="Test",
            description="Test",
            url="https://omega.local",
            authentication=A2AAuth(
                auth_type=AgentAuthType.SPIFFE,
                spiffe_id="spiffe://omega.local/entity/test",
            ),
        )
        result = card.to_dict()
        assert "authentication" in result
        auth = result["authentication"]
        assert "schemes" in auth
        assert auth["schemes"][0]["type"] == "spiffe"
        assert "x509_svid" in auth["schemes"][0]

    def test_to_dict_with_entity_id(self):
        """Card with entity_id must include entityId in output."""
        card = A2AAgentCard(
            name="Test",
            description="Test",
            url="https://omega.local",
            entity_id="spiffe://omega.local/entity/test",
        )
        result = card.to_dict()
        assert result["entityId"] == "spiffe://omega.local/entity/test"

    def test_to_json_valid_json(self):
        """to_json() must produce valid JSON."""
        card = A2AAgentCard(
            name="Test",
            description="Test",
            url="https://omega.local",
        )
        json_str = card.to_json()
        parsed = json.loads(json_str)
        assert parsed["name"] == "Test"

    def test_to_dict_with_skills(self):
        """Skills must be included as a list in the serialized output."""
        skill = A2ASkill(
            id="test.skill1",
            name="Test Skill",
            description="A test skill",
            tags=["test", "skill"],
            examples=["Do something"],
        )
        card = A2AAgentCard(
            name="Test",
            description="Test",
            url="https://omega.local",
            skills=[skill],
        )
        result = card.to_dict()
        assert len(result["skills"]) == 1
        assert result["skills"][0]["id"] == "test.skill1"
        assert result["skills"][0]["inputModes"] == ["text"]
        assert result["skills"][0]["outputModes"] == ["text"]


# =============================================================================
# Tests: A2ABridge
# =============================================================================

class TestA2ABridge:
    """Tests for the A2ABridge class."""

    def test_bridge_initialization(self, bridge):
        """A2ABridge must initialize cleanly with no registry."""
        assert bridge is not None
        assert bridge._entity_registry is None

    def test_set_entity_registry(self, bridge):
        """set_entity_registry must accept a registry object."""
        registry = MagicMock()
        bridge.set_entity_registry(registry)
        assert bridge._entity_registry is registry

    def test_register_entity_creates_card(self, bridge, mock_entity):
        """register_entity must return an A2AAgentCard."""
        card = bridge.register_entity(mock_entity)
        assert isinstance(card, A2AAgentCard)
        assert card.name == "TestEntity"

    def test_register_entity_generates_skills(self, bridge, mock_entity):
        """register_entity must generate at least one skill from entity domains."""
        card = bridge.register_entity(mock_entity)
        assert len(card.skills) >= 1
        # Should have domain skill + capability skills
        # Domain skills have IDs like "testentity.domain.0", domain name is in tags
        domain_tag_found = any("test_domain" in s.tags for s in card.skills)
        cap_skill_found = any("capability" in s.tags for s in card.skills)
        assert domain_tag_found or cap_skill_found

    def test_register_entity_spiffe_id(self, bridge, mock_entity):
        """register_entity must assign a valid SPIFFE ID."""
        card = bridge.register_entity(mock_entity)
        assert card.authentication is not None
        assert card.authentication.spiffe_id == "spiffe://omega.local/entity/testentity"
        assert card.entity_id == "spiffe://omega.local/entity/testentity"

    def test_get_card_after_register(self, bridge, mock_entity):
        """get_card must return the cached Agent Card."""
        bridge.register_entity(mock_entity)
        card = bridge.get_card("testentity")
        assert card is not None
        assert card.name == "TestEntity"

    def test_get_card_case_insensitive(self, bridge, mock_entity):
        """get_card must be case-insensitive."""
        bridge.register_entity(mock_entity)
        card = bridge.get_card("TESTENTITY")
        assert card is not None

    def test_get_card_not_found(self, bridge):
        """get_card must return None for unknown entity."""
        card = bridge.get_card("nonexistent")
        assert card is None

    def test_get_all_cards(self, bridge, mock_entity):
        """get_all_cards must return all registered cards."""
        bridge.register_entity(mock_entity)
        cards = bridge.get_all_cards()
        assert len(cards) == 1
        assert "testentity" in cards

    def test_generate_well_known_json(self, bridge, mock_entity):
        """generate_well_known_json must include all agents."""
        bridge.register_entity(mock_entity)
        json_str = bridge.generate_well_known_json()
        data = json.loads(json_str)
        assert data["a2a_version"] == "1.0.0"
        assert "TestEntity" in json_str
        assert "agents" in data
        assert len(data["agents"]) == 1
        assert "metadata" in data
        assert data["metadata"]["total_agents"] == 1

    def test_generate_well_known_json_empty(self, bridge):
        """generate_well_known_json must work with no registered agents."""
        json_str = bridge.generate_well_known_json()
        data = json.loads(json_str)
        assert data["metadata"]["total_agents"] == 0

    # --- build_agent_card tests ---

    def test_build_agent_card_no_registry(self, bridge):
        """build_agent_card must return None when no registry is set."""
        card = bridge.build_agent_card("sophia")
        assert card is None

    def test_build_agent_card_known_entity(self, bridge_with_registry):
        """build_agent_card must return a card for a known entity."""
        card = bridge_with_registry.build_agent_card("Sophia")
        assert card is not None
        assert isinstance(card, A2AAgentCard)
        assert card.name == "Sophia"

    def test_build_agent_card_spiffe_id(self, bridge_with_registry):
        """build_agent_card must assign SPIFFE ID based on entity name."""
        card = bridge_with_registry.build_agent_card("Kali")
        assert card is not None
        assert card.authentication is not None
        expected_spiffe = "spiffe://omega.local/entity/kali"
        assert card.authentication.spiffe_id == expected_spiffe

    def test_build_agent_card_skills_from_domains(self, bridge_with_registry):
        """build_agent_card must generate skills from entity domains."""
        card = bridge_with_registry.build_agent_card("Sentinel")
        assert card is not None
        # Sentinel has domains: ["security", "governance"]
        # Domain names appear in skill tags (not in the auto-generated ID)
        all_tags = [tag for s in card.skills for tag in s.tags]
        assert "security" in all_tags
        assert "governance" in all_tags

    def test_build_agent_card_nonexistent(self, bridge_with_registry):
        """build_agent_card must return None for unknown entity."""
        card = bridge_with_registry.build_agent_card("Nosferatu")
        assert card is None

    def test_build_agent_card_multiple_domains(self, bridge_with_registry):
        """Entity with multiple domains must generate a skill per domain."""
        card = bridge_with_registry.build_agent_card("Sophia")
        assert card is not None
        # Sophia has domains: ["wisdom", "council", "oracle"]
        assert len([s for s in card.skills if "domain" in s.id]) == 3

    def test_get_agent_card_json(self, bridge_with_registry):
        """get_agent_card_json must return valid JSON for a known entity."""
        json_str = bridge_with_registry.get_agent_card_json("Kali")
        assert json_str is not None
        parsed = json.loads(json_str)
        assert parsed["name"] == "Kali"
        assert "authentication" in parsed
        assert parsed["authentication"]["schemes"][0]["type"] == "spiffe"

    def test_get_agent_card_json_nonexistent(self, bridge_with_registry):
        """get_agent_card_json must return None for unknown entity."""
        result = bridge_with_registry.get_agent_card_json("Nosferatu")
        assert result is None

    def test_get_agent_card_json_no_registry(self, bridge):
        """get_agent_card_json must return None when no registry is set."""
        result = bridge.get_agent_card_json("Sophia")
        assert result is None

    def test_verify_agent_identity_valid(self, bridge, mock_entity):
        """verify_agent_identity must return True for a known SPIFFE ID."""
        bridge.register_entity(mock_entity)
        import anyio
        result = anyio.run(
            bridge.verify_agent_identity,
            "spiffe://omega.local/entity/testentity",
            b"fake_cert",
        )
        assert result is True

    def test_verify_agent_identity_wrong_domain(self, bridge):
        """verify_agent_identity must return False for wrong trust domain."""
        import anyio
        result = anyio.run(
            bridge.verify_agent_identity,
            "spiffe://other.domain/entity/test",
            b"fake_cert",
        )
        assert result is False

    def test_verify_agent_identity_unknown_entity(self, bridge):
        """verify_agent_identity must return False for unknown entity."""
        import anyio
        # Register one entity
        entity = MagicMock()
        entity.name = "Known"
        entity.domains = ["test"]
        entity.description = "Known entity"
        entity.capabilities = []
        entity.provider = None
        entity.organization = None
        bridge.register_entity(entity)

        # Try verifying a different SPIFFE ID
        result = anyio.run(
            bridge.verify_agent_identity,
            "spiffe://omega.local/entity/unknown",
            b"fake_cert",
        )
        assert result is False

    # --- Edge cases ---

    def test_entity_without_domains(self, bridge):
        """Entity without domains must still generate a card with a general skill."""
        entity = MagicMock()
        entity.name = "Generic"
        entity.domains = []
        entity.description = "A generic entity"
        entity.capabilities = []
        entity.provider = None
        entity.organization = None

        # Try with no domains attribute at all
        del entity.domains

        card = bridge.register_entity(entity)
        assert card is not None
        assert card.name == "Generic"

    def test_entity_with_string_domain(self, bridge):
        """Entity with a string domain (not list) must still work."""
        entity = MagicMock()
        entity.name = "StringDomain"
        entity.domains = "single_domain"
        entity.description = "Entity with string domain"
        entity.capabilities = []
        entity.provider = None
        entity.organization = None

        card = bridge.register_entity(entity)
        assert card.name == "StringDomain"

    def test_entity_with_capabilities_as_dict(self, bridge):
        """Entity with capabilities as dict must generate skills for each key."""
        entity = MagicMock()
        entity.name = "DictCap"
        entity.domains = ["test"]
        entity.description = "Entity with dict capabilities"
        entity.capabilities = {"deep_research": "Performs deep analysis"}
        entity.provider = None
        entity.organization = None

        card = bridge.register_entity(entity)
        skill_ids = [s.id for s in card.skills]
        assert any("deep_research" in sid for sid in skill_ids)

    def test_provider_name_from_entity(self, bridge):
        """Entity with provider attribute must use it."""
        entity = MagicMock()
        entity.name = "WithProvider"
        entity.domains = ["test"]
        entity.description = "Entity with provider"
        entity.capabilities = []
        entity.provider = "Custom Provider"
        entity.organization = None

        card = bridge.register_entity(entity)
        assert card.provider_name == "Custom Provider"

    def test_organization_fallback(self, bridge):
        """Entity with organization but no provider must use organization."""
        entity = MagicMock()
        entity.name = "OrgOnly"
        entity.domains = ["test"]
        entity.description = "Entity with org"
        entity.capabilities = []
        entity.provider = None
        entity.organization = "Org Name"

        card = bridge.register_entity(entity)
        assert card.provider_name == "Org Name"

    def test_register_multiple_entities(self, bridge):
        """Multiple entities must each get their own Agent Card."""
        entities = []
        for name in ["Alpha", "Beta", "Gamma"]:
            e = MagicMock()
            e.name = name
            e.domains = ["domain_" + name.lower()]
            e.description = f"Entity {name}"
            e.capabilities = []
            e.provider = None
            e.organization = None
            entities.append(e)
            bridge.register_entity(e)

        cards = bridge.get_all_cards()
        assert len(cards) == 3
        assert "alpha" in cards
        assert "beta" in cards
        assert "gamma" in cards


# =============================================================================
# Tests: A2ASkill
# =============================================================================

class TestA2ASkill:
    """Tests for the A2ASkill dataclass."""

    def test_to_dict_required_fields(self):
        """A2ASkill.to_dict() must include all required fields."""
        skill = A2ASkill(
            id="test.skill",
            name="Test Skill",
            description="A test skill",
        )
        result = skill.to_dict()
        assert result["id"] == "test.skill"
        assert result["name"] == "Test Skill"
        assert result["description"] == "A test skill"
        assert "tags" in result
        assert "examples" in result
        assert "inputModes" in result
        assert "outputModes" in result

    def test_to_dict_with_tags_and_examples(self):
        """Tags and examples must be included when provided."""
        skill = A2ASkill(
            id="test.full",
            name="Full Skill",
            description="A skill with all fields",
            tags=["tag1", "tag2"],
            examples=["Example 1", "Example 2"],
        )
        result = skill.to_dict()
        assert result["tags"] == ["tag1", "tag2"]
        assert result["examples"] == ["Example 1", "Example 2"]


# =============================================================================
# Tests: A2AAuth
# =============================================================================

class TestA2AAuth:
    """Tests for the A2AAuth dataclass."""

    def test_spiffe_scheme(self):
        """SPIFFE auth must produce correct scheme."""
        auth = A2AAuth(
            auth_type=AgentAuthType.SPIFFE,
            spiffe_id="spiffe://omega.local/entity/test",
        )
        result = auth.to_dict()
        assert len(result["schemes"]) == 1
        assert result["schemes"][0]["type"] == "spiffe"
        assert result["schemes"][0]["x509_svid"] == "spiffe://omega.local/entity/test"

    def test_none_auth(self):
        """NONE auth must produce a scheme with type 'none'."""
        auth = A2AAuth(auth_type=AgentAuthType.NONE)
        result = auth.to_dict()
        assert len(result["schemes"]) == 1
        assert result["schemes"][0]["type"] == "none"

    def test_oauth_scopes(self):
        """OAuth 2.0 scopes must be included when provided."""
        auth = A2AAuth(
            auth_type=AgentAuthType.OAUTH2,
            oauth_scopes=["entity.summon", "entity.read"],
        )
        result = auth.to_dict()
        assert len(result["schemes"]) == 1
        assert result["schemes"][0]["type"] == "oauth2"
        assert result["schemes"][0]["scopes"] == ["entity.summon", "entity.read"]

    def test_dual_scheme(self):
        """Both SPIFFE and OAuth must be included when both are configured."""
        auth = A2AAuth(
            auth_type=AgentAuthType.SPIFFE,
            spiffe_id="spiffe://omega.local/entity/test",
            oauth_scopes=["entity.summon"],
        )
        result = auth.to_dict()
        assert len(result["schemes"]) == 2
        types = [s["type"] for s in result["schemes"]]
        assert "spiffe" in types
        assert "oauth2" in types

    def test_mutual_tls_scheme(self):
        """mTLS auth must produce correct scheme."""
        auth = A2AAuth(
            auth_type=AgentAuthType.MUTUAL_TLS,
            spiffe_id="spiffe://omega.local/entity/test",
        )
        result = auth.to_dict()
        assert result["schemes"][0]["type"] == "mtls"
        assert result["schemes"][0]["x509_svid"] == "spiffe://omega.local/entity/test"


# =============================================================================
# Tests: SPIFFEID (a2a_auth)
# =============================================================================

class TestSPIFFEID:
    """Tests for the SPIFFEID class."""

    def test_spiffe_id_format(self):
        """SPIFFEID must produce correct string format."""
        sid = SPIFFEID(trust_domain="omega.local", path="entity/kali")
        assert str(sid) == "spiffe://omega.local/entity/kali"

    def test_spiffe_id_parse(self):
        """SPIFFEID.parse must correctly split trust_domain and path."""
        sid = SPIFFEID.parse("spiffe://omega.local/entity/test")
        assert sid.trust_domain == "omega.local"
        assert sid.path == "entity/test"

    def test_spiffe_id_parse_root(self):
        """SPIFFEID.parse must handle IDs with no path."""
        sid = SPIFFEID.parse("spiffe://omega.local/")
        assert sid.trust_domain == "omega.local"
        assert sid.path == ""

    def test_spiffe_id_round_trip(self):
        """str(parse(x)) == x must hold."""
        original = "spiffe://omega.local/entity/kali"
        sid = SPIFFEID.parse(original)
        assert str(sid) == original

    def test_spiffe_id_path_with_slashes(self):
        """SPIFFEID must handle multi-segment paths."""
        sid = SPIFFEID.parse("spiffe://omega.local/entity/pillar/p6")
        assert sid.trust_domain == "omega.local"
        assert sid.path == "entity/pillar/p6"


# =============================================================================
# Tests: AgentCredential (a2a_auth)
# =============================================================================

class TestAgentCredential:
    """Tests for the AgentCredential class."""

    def test_credential_ttl_seconds(self):
        """ttl_seconds must return positive time until expiry."""
        sid = SPIFFEID(trust_domain="omega.local", path="entity/test")
        now = datetime.now(timezone.utc)
        cred = AgentCredential(
            spiffe_id=sid,
            issued_at=now,
            expires_at=now + timedelta(hours=1),
            token="test-token",
        )
        assert 3599 <= cred.ttl_seconds <= 3601

    def test_credential_is_expired(self):
        """is_expired must return True when past expiry."""
        sid = SPIFFEID(trust_domain="omega.local", path="entity/test")
        now = datetime.now(timezone.utc)
        cred = AgentCredential(
            spiffe_id=sid,
            issued_at=now - timedelta(hours=2),
            expires_at=now - timedelta(hours=1),
            token="test-token",
        )
        assert cred.is_expired is True

    def test_credential_not_expired(self):
        """is_expired must return False when within validity."""
        sid = SPIFFEID(trust_domain="omega.local", path="entity/test")
        now = datetime.now(timezone.utc)
        cred = AgentCredential(
            spiffe_id=sid,
            issued_at=now,
            expires_at=now + timedelta(hours=1),
            token="test-token",
        )
        assert cred.is_expired is False

    def test_credential_is_valid_for(self):
        """is_valid_for must return True for matching SPIFFE ID and non-expired."""
        sid = SPIFFEID(trust_domain="omega.local", path="entity/test")
        now = datetime.now(timezone.utc)
        cred = AgentCredential(
            spiffe_id=sid,
            issued_at=now,
            expires_at=now + timedelta(hours=1),
            token="test-token",
        )
        assert cred.is_valid_for(sid) is True

    def test_credential_wrong_spiffe_id(self):
        """is_valid_for must return False for mismatched SPIFFE ID."""
        sid = SPIFFEID(trust_domain="omega.local", path="entity/test")
        wrong_sid = SPIFFEID(trust_domain="omega.local", path="entity/other")
        now = datetime.now(timezone.utc)
        cred = AgentCredential(
            spiffe_id=sid,
            issued_at=now,
            expires_at=now + timedelta(hours=1),
            token="test-token",
        )
        assert cred.is_valid_for(wrong_sid) is False

    def test_credential_ttl_zero_when_expired(self):
        """ttl_seconds must return 0 when credential is expired."""
        sid = SPIFFEID(trust_domain="omega.local", path="entity/test")
        now = datetime.now(timezone.utc)
        cred = AgentCredential(
            spiffe_id=sid,
            issued_at=now - timedelta(hours=2),
            expires_at=now - timedelta(hours=1),
            token="test-token",
        )
        assert cred.ttl_seconds == 0


# =============================================================================
# Tests: Integration / Protocol Transition
# =============================================================================

class TestA2AProtocolTransition:
    """Verify no remnants of fabricated AAIF spec remain in source code."""

    def test_no_aaif_references_in_a2a_bridge(self):
        """Ensure no fabricated AAIF references exist in the new bridge module."""
        import os
        filepath = "src/omega/oracle/a2a_bridge.py"
        if os.path.exists(filepath):
            with open(filepath) as f:
                content = f.read()
                assert 'draft-schemacommons-aaif' not in content, (
                    "AAIF reference found in a2a_bridge.py"
                )

    def test_skill_category_enum_values(self):
        """SkillCategory must have expected values."""
        assert SkillCategory.DOMAIN_ROUTING.value == "domain_routing"
        assert SkillCategory.RESEARCH.value == "research"
        assert SkillCategory.VERIFICATION.value == "verification"

    def test_agent_auth_type_values(self):
        """AgentAuthType must have expected values."""
        assert AgentAuthType.SPIFFE.value == "spiffe"
        assert AgentAuthType.OAUTH2.value == "oauth2"
        assert AgentAuthType.MUTUAL_TLS.value == "mtls"
        assert AgentAuthType.NONE.value == "none"
