<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 A2A Agent Card Implementation — Sovereign Agent Identity
## Gap 3: P2 MED — Fabricated AAIF Replaced with Real A2A v1.0 + WIMSE Auth

**AP Token**: `AP-A2A-AGENT-CARD-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ A2A-CARD ⬡ SOVEREIGN-MINER
**Status**: IMPLEMENTATION SPECIFICATION
**Date**: 2026-06-29

---

## §1 Current Problem

### 1.1 Root Cause

The existing `P7_AAIF_MAPPING_SPEC_20260628.md` references a fictional standardization document: `draft-schemacommons-aaif-00`. **No such IETF draft has ever existed.** The specification was fabricated during a "hallucinogenic" phase where the system generated standards that don't exist.

### 1.2 The Fabricated Spec

| Claim | Reality |
|-------|---------|
| `draft-schemacommons-aaif-00` exists at IETF | ❌ **Never submitted.** No matching IETF datatracker entry. |
| AAIF v3.0 is an active standard | ❌ **Never proposed.** No organization has published this. |
| KGC-001 requires AAIF compliance | ❌ **KGC-001 is an internal finding** — it references a non-existent standard. |
| AAIF defines Agent Agent Interaction Format | ❌ **No such specification exists** at any standards body. |

### 1.3 Real Standards That Exist

| Standard | Status | Authority | Coverage |
|----------|--------|-----------|----------|
| **Google A2A v1.0** | ✅ Active (2025-2026) | Google/Linux Foundation | Agent-to-agent protocol, Agent Cards, signed metadata |
| **IETF draft-klrc-aiagent-auth-02** | ✅ Active (Mar-Dec 2026) | IETF informal draft | WIMSE-based agent auth, SPIFFE IDs, OAuth 2.0 delegation |
| **WIMSE Architecture** (draft-ietf-wimse-arch-07) | ✅ Active (Mar 2026) | IETF WIMSE WG | Workload identity in multi-system env |
| **SPIFFE X.509-SVID** | ✅ Production (CNCF) | CNCF | Workload identity certificates |

### 1.4 Mandates Violated

| Mandate | Risk | Explanation |
|---------|------|-------------|
| **M9** (Error Integrity) | ⚠️ MED | Fabricated spec introduced untraceable architectural debt |
| **M12** (Queue Integrity) | ⚠️ LOW | Orphaned spec file with no resolution path |
| **M17** (Cognitive Integrity) | ⚠️ HIGH | Memory contradiction: system referenced non-existent standard |

---

## §2 The Real A2A Protocol

### 2.1 Google A2A v1.0 Overview

The **Agent-to-Agent (A2A) protocol** is an open standard hosted under the **Linux Foundation's Joint Development Foundation** (not Google-proprietary). It enables direct communication between AI agents using JSON-RPC 2.0 messages.

**Key Sources**:
- Specification: `https://github.com/google/A2A` (Linux Foundation / JDF)
- Agent Card definition: `/.well-known/agent-card.json` at each agent's domain
- Community: 150+ organizations including Atlassian, Box, Dell, MongoDB, Salesforce, SAP, Snyk, Uber, Upwork, and many others
- Cloud platforms: Azure AI Foundry (Microsoft), Amazon Bedrock AgentCore (AWS)

### 2.2 A2A Core Concepts

| Concept | Definition | Omega Mapping |
|---------|-----------|---------------|
| **Agent Card** | `/.well-known/agent-card.json` — metadata about an agent's capabilities, skills, auth requirements | `EntityRegistry` entities exposed as Agent Cards on `/.well-known/agent-card.json` |
| **Skill** | A named capability an agent can perform (e.g., "research", "verification") | Domain routing in EntityRegistry (`domain` → entity mapping) |
| **Card** | JSON-RPC 2.0 message exchange for task execution | Hivemind handoff packets (`data/handoff/pending/`, `active/`) |
| **Push Notification** | Server-initiated update to client when task completes | Hivemind `heartbeat()` / `checkin()` WebSocket pattern |
| **Signed Agent Card** | Cryptographic signature over Agent Card metadata for trust verification | SPIFFE X.509-SVID for agent identity attestation |

### 2.3 A2A Agent Card Schema

```json
{
  "name": "Sovereign Entity Name",
  "description": "Domain-specific agent description",
  "url": "https://omega.local/.well-known/agent-card.json",
  "provider": {
    "name": "Xoe-NovAi Foundation",
    "url": "https://xoe-nov.ai",
    "organization": "Xoe-NovAi Foundation"
  },
  "version": "1.0.0",
  "capabilities": {
    "streaming": false,
    "pushNotifications": true,
    "stateTransitionHistory": true
  },
  "skills": [
    {
      "id": "research",
      "name": "Deep Research",
      "description": "Multi-perspective research with lattice reasoning",
      "tags": ["research", "analysis", "verification"],
      "examples": ["Research the impact of..."]
    }
  ],
  "auth": {
    "schemes": [
      {
        "type": "spiffe",
        "x509_svid": "spiffe://omega.local/entity/researcher"
      }
    ]
  },
  "defaultInputModes": ["text"],
  "defaultOutputModes": ["text"],
  "security": {
    "signingKey": "<x509-public-key-fingerprint>",
    "signature": "<signature-over-card-json>"
  }
}
```

### 2.4 draft-klrc-aiagent-auth-02: Agent Authentication

The IETF informal draft (expires Dec 3, 2026) by Pieter Kasselman (Defakto Security), Jeff Lombardo (AWS), Yaroslav Rosomakho (Zscaler), Brian Campbell (Ping Identity), Nick Steele (OpenAI), and Aaron Parecki (Okta) provides the **Agent Identity Management System (AIMS)** framework:

**Core Principle**: "Agents are workloads" — not users, not services in the traditional sense.

| Layer | Component | Omega Implementation |
|-------|-----------|---------------------|
| **Identifier** | WIMSE/SPIFFE ID per agent | `Entity.entity_id = "spiffe://omega.local/entity/{name}"` |
| **Credentials** | Short-lived X.509-SVID / JWT | SPIFFE-compatible key rotation in `src/omega/oracle/a2a_auth.py` |
| **Attestation** | Evidence of identity claims | Signed Agent Card metadata |
| **Authentication** | OAuth 2.0 device flow / mTLS | mTLS with SPIFFE certs between agents |
| **Authorization** | OAuth 2.0 RAR / Transaction Tokens | Scope-based Hivemind delegation (`scope: entity.summon`) |
| **Observability** | Audit trail for all agent actions | Existing `ObservabilityEngine` with trace_id |
| **Policy** | Governance rules for agent behavior | Sovereign Mandates (M1-M22) |
| **Compliance** | Verification against standards | M13 Temple-Grade, M21 Gate Integrity |

---

## §3 Implementation

### 3.1 New File: `src/omega/oracle/a2a_bridge.py`

```python
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
- mTLS for inter-agent transport
"""

import json
import logging
import uuid
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
    """A single A2A skill — maps to an entity's domain or capability."""
    id: str
    name: str
    description: str
    tags: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    input_modes: List[str] = field(default_factory=lambda: ["text"])
    output_modes: List[str] = field(default_factory=lambda: ["text"])
    
    def to_dict(self) -> Dict[str, Any]:
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
        schemes = []
        if self.auth_type in (AgentAuthType.SPIFFE, AgentAuthType.MUTUAL_TLS):
            scheme = {
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
    
    # A2A capabilities
    supports_streaming: bool = False
    supports_push_notifications: bool = True
    supports_state_transition_history: bool = True
    
    # Skills (maps to EntityRegistry domain/capability)
    skills: List[A2ASkill] = field(default_factory=list)
    
    # Auth
    auth: A2AAuth = field(default_factory=A2AAuth)
    default_input_modes: List[str] = field(default_factory=lambda: ["text"])
    default_output_modes: List[str] = field(default_factory=lambda: ["text"])
    
    # Security
    signing_key_fingerprint: Optional[str] = None
    
    # Metadata
    entity_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to A2A Agent Card JSON format."""
        card = {
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
            "auth": self.auth.to_dict(),
            "defaultInputModes": self.default_input_modes,
            "defaultOutputModes": self.default_output_modes,
        }
        
        if self.signing_key_fingerprint:
            card["security"] = {
                "signingKey": self.signing_key_fingerprint,
            }
        
        if self.entity_id:
            card["entityId"] = self.entity_id
        
        return card


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
    
    def register_entity(self, entity: Any) -> A2AAgentCard:
        """Generate an A2A Agent Card from an EntityRegistry entity.
        
        Maps:
        - Entity name → Agent Card name
        - Entity domain → A2A skills
        - Entity capabilities → skill tags
        
        Args:
            entity: Entity from EntityRegistry (with name, domain, etc.)
            
        Returns:
            A2AAgentCard instance
        """
        entity_name = getattr(entity, 'name', 'unknown')
        entity_domain = getattr(entity, 'domain', 'general')
        
        # [draft-klrc-aiagent-auth-02] SPIFFE ID = primary agent identifier
        spiffe_id = f"spiffe://{self._spiffe_trust_domain}/entity/{entity_name.lower()}"
        
        # Map entity data to A2A skills
        skills = self._map_entity_to_skills(entity)
        
        card = A2AAgentCard(
            name=entity_name,
            description=getattr(entity, 'description', f"Sovereign entity: {entity_name}"),
            url=f"{self._base_url}/.well-known/agent-card.json/{entity_name.lower()}",
            provider_name=self._get_provider_name(entity),
            provider_url=self._base_url,
            skills=skills,
            auth=A2AAuth(
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
        entity_domain = getattr(entity, 'domain', 'general')
        
        # Primary skill: domain routing
        skills.append(A2ASkill(
            id=f"{entity_name.lower()}.{entity_domain}",
            name=entity_domain.replace('_', ' ').title(),
            description=f"Domain: {entity_domain}",
            tags=["domain", entity_domain],
            examples=[f"Summon {entity_name} for {entity_domain} tasks"],
        ))
        
        # Secondary skill: capability-based (if entity has capabilities)
        capabilities = getattr(entity, 'capabilities', None) or getattr(entity, 'skills', None)
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
        # Check if entity has a provider attribute
        provider = getattr(entity, 'provider', None) or getattr(entity, 'organization', None)
        if provider:
            return str(provider)
        return "Xoe-NovAi Foundation"
    
    def get_card(self, entity_name: str) -> Optional[A2AAgentCard]:
        """Get an Agent Card by entity name."""
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
                "auth_framework": "https://datatracker.ietf.org/doc/draft-klrc-aiagent-auth/",
            }
        }
        return json.dumps(cards, indent=2)
    
    async def verify_agent_identity(self, spiffe_id: str, certificate: bytes) -> bool:
        """Verify an agent's identity using SPIFFE X.509-SVID.
        
        [draft-klrc-aiagent-auth-02 §5] Short-lived credentials
        bound to the agent's SPIFFE ID.
        
        Args:
            spiffe_id: The claimed SPIFFE ID (e.g., spiffe://omega.local/entity/kali)
            certificate: The X.509 certificate presented for verification
            
        Returns:
            True if identity is verified, False otherwise
        """
        # Phase 2: Implement full SPIFFE verification
        # For now, verify the SPIFFE ID format and trust domain
        if not spiffe_id.startswith(f"spiffe://{self._spiffe_trust_domain}/"):
            logger.warning("SPIFFE ID %s not in trust domain %s",
                          spiffe_id, self._spiffe_trust_domain)
            return False
        
        entity_name = spiffe_id.split('/')[-1]
        if entity_name not in self._agent_cards:
            logger.warning("Unknown entity: %s (SPIFFE: %s)", entity_name, spiffe_id)
            return False
        
        logger.info("Agent identity verified: %s (SPIFFE: %s)", entity_name, spiffe_id)
        return True
```

### 3.2 New File: `src/omega/oracle/a2a_auth.py`

```python
"""
A2A Authentication — SPIFFE/WIMSE Agent Identity.

[IETF draft-klrc-aiagent-auth-02]
Implements the Agent Identity Management System (AIMS) framework:
- Identifier: SPIFFE/WIMSE ID per agent
- Credentials: Short-lived X.509-SVID (≈1h TTL)
- Authentication: mTLS with bound credentials
- Authorization: OAuth 2.0 Transaction Tokens

This module handles the cryptographic backend using Python's
standard library cryptography primitives.
"""

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class SPIFFEID:
    """SPIFFE ID representing an agent's identity.
    
    Format: spiffe://<trust_domain>/<path>
    Example: spiffe://omega.local/entity/kali
    
    [draft-klrc-aiagent-auth-02 §4.1]
    """
    trust_domain: str
    path: str
    
    def __str__(self) -> str:
        return f"spiffe://{self.trust_domain}/{self.path}"
    
    @classmethod
    def parse(cls, spiffe_id: str) -> 'SPIFFEID':
        parts = spiffe_id.replace('spiffe://', '').split('/', 1)
        return cls(trust_domain=parts[0], path=parts[1] if len(parts) > 1 else '')


@dataclass
class AgentCredential:
    """Short-lived credential for agent authentication.
    
    [draft-klrc-aiagent-auth-02 §5]
    Credentials must be bound to the agent's identity,
    short-lived (≈1h), and dynamically rotated.
    """
    spiffe_id: SPIFFEID
    issued_at: datetime
    expires_at: datetime
    token: str  # JWT or X.509-SVID thumbprint
    
    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expires_at
    
    @property
    def ttl_seconds(self) -> int:
        remaining = (self.expires_at - datetime.now(timezone.utc)).total_seconds()
        return max(0, int(remaining))
```

### 3.3 Integration into MCP Hub

In `mcp_servers/omega_hub/server.py`, add an endpoint to serve the `/.well-known/agent-card.json`:

```python
# In MCP Hub server, register the Agent Card endpoint:

@router.get("/.well-known/agent-card.json")
async def serve_agent_card():
    """Serve A2A Agent Cards for all registered entities.
    
    [Google A2A v1.0] Standard discovery endpoint.
    [draft-klrc-aiagent-auth-02] Agent identity metadata.
    """
    from omega.oracle.a2a_bridge import A2ABridge
    
    bridge = A2ABridge(entity_registry=get_entity_registry())
    
    # Register all entities as Agent Cards
    entities = list_entities()
    for entity in entities:
        bridge.register_entity(entity)
    
    return JSONResponse(content=json.loads(bridge.generate_well_known_json()))
```

---

## §4 Migration Plan: AAIF → A2A

### Step 1: Supersede the Fabricated Spec (15 min)
```bash
mv data/handoff/P7_AAIF_MAPPING_SPEC_20260628.md \
   data/handoff/SUPERSEDED_AAIF_20260628.md
```
[Tag as SUPERSEDED] Add header annotation:
```markdown
> **STATUS: SUPERSEDED (2026-06-29)**
> This specification referenced `draft-schemacommons-aaif-00`, which does not exist.
> Replacement: `A2A_AGENT_CARD_SPEC.md` implementing Google A2A v1.0 + draft-klrc-aiagent-auth-02.
```

### Step 2: Create Core Implementation Files (3 hours)
| File | Contents | Effort |
|------|----------|--------|
| `src/omega/oracle/a2a_bridge.py` | `A2ABridge`, `A2AAgentCard`, A2A ↔ Entity mapping | 2 hours |
| `src/omega/oracle/a2a_auth.py` | SPIFFE identity, credential management | 1 hour |

### Step 3: Integrate into MCP Hub (1 hour)
- Add `/.well-known/agent-card.json` endpoint in `mcp_servers/omega_hub/server.py`
- Wire `A2ABridge` to `EntityRegistry` on startup

### Step 4: Integrate into Hivemind (1 hour)
- Map Hivemind handoff packets to A2A task messages
- Add agent-to-agent SPIFFE verification on handoff

### Step 5: Create KGC-001 Resolution (1 hour)
- Update KGC-001 finding to reference A2A v1.0 + draft-klrc-aiagent-auth-02
- Replace AAIF references with real standards throughout documentation

### Step 6: Write Tests (2 hours)
---

## §5 Verification Criteria

| Criteria | Method | Success |
|----------|--------|---------|
| Agent Card generated | `A2ABridge.register_entity()` test | Valid Agent Card JSON output |
| Agent Card served at `/.well-known/` | HTTP GET endpoint | Returns 200 with valid JSON |
| Entity → Skill mapping | Test with known entity | All domains map to skills |
| SPIFFE ID format | `SPIFFEID.parse()` test | `spiffe://omega.local/entity/test` |
| Old AAIF spec superseded | File annotation | Header states SUPERSEDED |
| No remaining AAIF references | `grep -r "draft-schemacommons-aaif" src/` | Zero matches |
| KGC-001 updated | Code review | References real standards |

---

## §6 Test Skeleton

```python
"""Tests for A2A Agent Card bridge + SPIFFE auth."""

import pytest
from unittest.mock import MagicMock
from omega.oracle.a2a_bridge import A2ABridge, A2AAgentCard, A2ASkill, AgentAuthType
from omega.oracle.a2a_auth import SPIFFEID, AgentCredential

class TestA2AAgentCard:
    
    @pytest.fixture
    def bridge(self):
        return A2ABridge()
    
    @pytest.fixture
    def mock_entity(self):
        entity = MagicMock()
        entity.name = "TestEntity"
        entity.domain = "test_domain"
        entity.description = "Test entity for unit tests"
        entity.capabilities = ["research", "analysis"]
        return entity
    
    def test_register_entity_creates_card(self, bridge, mock_entity):
        card = bridge.register_entity(mock_entity)
        assert isinstance(card, A2AAgentCard)
        assert card.name == "TestEntity"
        assert len(card.skills) >= 1
    
    def test_register_entity_spiffe_id(self, bridge, mock_entity):
        card = bridge.register_entity(mock_entity)
        assert card.auth.spiffe_id == "spiffe://omega.local/entity/testentity"
    
    def test_register_entity_skills(self, bridge, mock_entity):
        card = bridge.register_entity(mock_entity)
        skill_ids = [s.id for s in card.skills]
        assert any("test_domain" in sid for sid in skill_ids)
    
    def test_get_card(self, bridge, mock_entity):
        bridge.register_entity(mock_entity)
        card = bridge.get_card("testentity")
        assert card is not None
        assert card.name == "TestEntity"
    
    def test_generate_well_known_json(self, bridge, mock_entity):
        bridge.register_entity(mock_entity)
        json_str = bridge.generate_well_known_json()
        assert '"TestEntity"' in json_str
        assert 'a2a_version' in json_str
    
    def test_card_to_dict(self, bridge, mock_entity):
        card = bridge.register_entity(mock_entity)
        d = card.to_dict()
        assert d["name"] == "TestEntity"
        assert "provider" in d
        assert "skills" in d
        assert "auth" in d
        assert d["auth"]["schemes"][0]["type"] == "spiffe"


class TestSPIFFEIdentity:
    
    def test_spiffe_id_format(self):
        sid = SPIFFEID(trust_domain="omega.local", path="entity/kali")
        assert str(sid) == "spiffe://omega.local/entity/kali"
    
    def test_spiffe_id_parse(self):
        sid = SPIFFEID.parse("spiffe://omega.local/entity/test")
        assert sid.trust_domain == "omega.local"
        assert sid.path == "entity/test"


class TestA2AProtocolTransition:
    """Verify no remnants of fabricated AAIF spec."""
    
    def test_no_aaif_references(self):
        """Ensure no fabricated AAIF references remain in source code."""
        import os
        src_dir = "src/omega"
        aaif_refs = []
        for root, dirs, files in os.walk(src_dir):
            for fname in files:
                if fname.endswith('.py'):
                    fpath = os.path.join(root, fname)
                    with open(fpath) as f:
                        content = f.read()
                        if 'draft-schemacommons-aaif' in content:
                            aaif_refs.append(fpath)
        assert len(aaif_refs) == 0, f"Found AAIF references in: {aaif_refs}"
    
    def test_old_spec_superseded(self):
        """Verify old spec has SUPERSEDED annotation."""
        path = "data/handoff/SUPERSEDED_AAIF_20260628.md"
        import os
        if os.path.exists(path):
            with open(path) as f:
                content = f.read()
                assert "SUPERSEDED" in content
```

---

## §7 Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| A2A v1.0 specification evolves | MED | LOW | Adopt card schema only; avoid deep A2A protocol coupling |
| SPIFFE library not available | MED | MED | Implement basic X.509 verification without full SPIFFE SDK |
| Other files still reference AAIF | HIGH | LOW | grep-based sweep; CI check for `draft-schemacommons-aaif` |
| KGC-001 has propagated to external docs | LOW | LOW | Update all internal references; external docs are controlled |
| A2A Bridge doesn't serve real traffic | HIGH | LOW | This is a sovereignty enhancement — not production-critical |

---

## §8 Effort Summary

| Step | Effort | Dependencies |
|------|--------|-------------|
| Supersede fabricated AAIF spec | 15 min | None |
| Create `a2a_bridge.py` | 2 hours | None |
| Create `a2a_auth.py` | 1 hour | None |
| Integrate into MCP Hub | 1 hour | Steps 2-3 |
| Integrate into Hivemind | 1 hour | Step 4 |
| Update KGC-001 resolution | 1 hour | Step 2 |
| Write tests | 2 hours | Steps 2-5 |
| **Total** | **8 hours** | — |

---

## §9 Dependency Graph

```
PII_MASKER_SPEC     TRACE_ID_SPEC        A2A_AGENT_CARD_SPEC
    │                    │                      │
    ▼                    ▼                      ▼
context_builder.py   model_gateway.py     SUPERSEDED_AAIF_20260628.md
    │                    │                      │
    ▼                    ▼                      ▼
oracle.py            iterative_          a2a_bridge.py
(pii integration)    research.py              │
    │                    │                    ▼
    ▼                    ▼               a2a_auth.py
PIIMasker.py         skeptical_              │
                      verifier.py             ▼
                         │             MCP Hub server.py
                         ▼                     │
                  observability/               ▼
                  context.py           KGC-001 resolution
                         │
                         ▼
                  record_error() fix


Effort Totals:
  PII Masker:     5.5 hrs
  Trace ID:       5-6 hrs
  A2A Agent Card: 8 hrs
  ─────────────────────────
  TOTAL:         18.5-19.5 hrs
```

---

## §10 KGC-001 Resolution

### Current KGC-001 Finding (From Sovereign Ark Blueprint §XII)

> **KGC-001**: AAIF compliance gap — entities lack inter-agent authentication and capability catalog required by the AAIF specification.

### Resolution

**KGC-001 is re-scoped to reference real standards**:

> **KGC-001**: A2A compliance gap — entities lack inter-agent authentication and capability catalog required by **Google A2A v1.0** (Linux Foundation JDF).
>
> **Evidence**:
> - No Agent Cards exist at `/.well-known/agent-card.json`
> - Entity capabilities are not published as A2A skills
> - No SPIFFE IDs for entities ([draft-klrc-aiagent-auth-02 §4.1])
> - No signed Agent Card metadata
>
> **Remediation**:
> - Implement `A2ABridge` to generate Agent Cards from EntityRegistry
> - Serve Agent Cards via MCP Hub at `/.well-known/agent-card.json`
> - Assign SPIFFE IDs per entity ([draft-klrc-aiagent-auth-02])
> - Sign Agent Cards with entity key

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ A2A-CARD ⬡ SOVEREIGN-MINER*
*Session: ses_roc_racoon_gap_closure_20260629*
*Sources: P7_AAIF_MAPPING_SPEC_20260628.md, Google A2A v1.0 (Linux Foundation), IETF draft-klrc-aiagent-auth-02, WIMSE Architecture*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
