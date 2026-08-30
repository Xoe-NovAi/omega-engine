# 🔱 R19: Soul Privacy Model Design
**AP Token**: `AP-R19-SOUL-PRIVACY-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_soul_privacy ⬡ ACTIVE

**Date**: 2026-07-24
**Status**: COMPLETE — Ready for Implementation
**Priority**: P0 (Unblocks R30 Identity Fluidity Phase 0, feeds C-3 Privacy Model)

---

## Executive Summary

This report designs a **privacy-first soul architecture** for the Omega Engine that splits `soul.yaml` into **public identity** + **private fragments**, implements **conversation-level privacy controls**, enforces **gitignored config splits**, enables **restic selective backup**, and defines **actor-model token scopes** for capability-based authorization.

**Key Decision**: Adopt a **three-layer privacy model** inspired by Soul Protocol's `PUBLIC/BONDED/PRIVATE` visibility tiers, CAMP's cumulative PII exposure scoring, CloakBot's local privacy kernel, and 1Password's delegated authority architecture — adapted for Omega's 10-pillar sovereign engine.

---

## Part 1: Soul.yaml Public/Private Split Architecture

### 1.1 Current State Analysis

Omega's `soul.yaml` currently contains:
- **Identity**: DID, name, archetype, OCEAN traits, communication style
- **Memory**: L1 narrative, L2 insights, L3 universal principles
- **Evolution**: Incarnation count, lineage, mutation history
- **Bonds**: Relationship strengths, interaction history
- **Skills**: XP, proficiency levels, learning events
- **Configuration**: Model preferences, provider settings, API keys (should not be here)

### 1.2 Proposed Split: `soul.yaml` → `soul.public.yaml` + `soul.private/`

```
data/entities/{entity}/
├── soul.public.yaml          # PUBLIC — git-tracked, shareable, backupable
│   ├── identity:
│   │   ├── did: "did:omega:entity:researcher"
│   │   ├── name: "Researcher"
│   │   ├── archetype: "Sovereign Researcher"
│   │   ├── ocean: {openness: 0.8, conscientiousness: 0.9, ...}
│   │   └── communication_style: "analytical, evidence-based"
│   ├── evolution:
│   │   ├── incarnation: 3
│   │   ├── lineage: ["genesis", "v1.0", "v2.0"]
│   │   └── mutation_log: [...]
│   ├── bonds:                # PUBLIC bond metadata only (strength, entity_id)
│   │   - entity_id: "maat"
│   │     strength: 87
│   │     bond_type: "professional"
│   └── skills:               # PUBLIC skill names + levels only
│       - name: "deep_research"
│         level: 5
│         xp: 12400
│
├── soul.private/             # PRIVATE — gitignored, encrypted at rest
│   ├── memories/
│   │   ├── L1_narrative.jsonl      # Full conversation narratives
│   │   ├── L2_insights.jsonl       # Detailed analytical insights
│   │   └── L3_principles.jsonl     # Universal principles with provenance
│   ├── bonds/
│   │   └── detailed_history.jsonl  # Full interaction transcripts
│   ├── skills/
│   │   └── learning_events.jsonl   # Detailed XP grants, rubric scores
│   ├── config/
│   │   ├── model_preferences.yaml  # Local model paths, quantization prefs
│   │   └── provider_keys.yaml      # API keys (encrypted)
│   └── evolution/
│       └── mutation_details.jsonl  # Full mutation diffs, rejected proposals
│
├── .gitignore                # Excludes soul.private/ entirely
└── .soulignore               # Optional: fine-grained exclusions for restic
```

### 1.3 Visibility Tiers (Adapted from Soul Protocol v0.2.5+)

| Tier | Scope | Stored In | Git | Restic | Cloud Fallback |
|------|-------|-----------|-----|--------|----------------|
| **PUBLIC** | Identity, public bonds, skill names, evolution metadata | `soul.public.yaml` | ✅ Tracked | ✅ Full backup | ✅ Allowed |
| **BONDED** | Bonded-entity memories, shared context | `soul.private/bonds/` | ❌ Ignored | ✅ Encrypted | ❌ Never |
| **PRIVATE** | Full narratives, insights, config, keys, mutation details | `soul.private/` | ❌ Ignored | ✅ Encrypted | ❌ Never |

**Implementation**: Add `visibility: "public|bonded|private"` field to every memory entry in `L1/L2/L3` JSONL files. Recall engine filters by requester identity + bond strength.

### 1.4 Recall Engine Privacy Filtering

```python
# src/omega/soul/recall.py
async def recall(entity: str, query: str, requester: str, bond_strength: int) -> List[MemoryEntry]:
    """Privacy-filtered recall based on Soul Protocol visibility tiers."""
    all_entries = await load_all_memory_entries(entity)
    
    filtered = []
    for entry in all_entries:
        vis = entry.get("visibility", "public")
        if vis == "public":
            filtered.append(entry)
        elif vis == "bonded" and bond_strength >= 50:  # Threshold configurable
            filtered.append(entry)
        elif vis == "private" and requester == entity:  # Only self sees private
            filtered.append(entry)
        # Else: filtered out silently
    
    return await rank_by_relevance(filtered, query)
```

---

## Part 2: Conversation Privacy Patterns

### 2.1 Threat Model

| Threat | Vector | Impact | Mitigation |
|--------|--------|--------|------------|
| **PII in context window** | User shares SSN, medical data, keys | Irreversible cloud exposure | Pre-execution redaction (CAMP/CloakBot) |
| **Cross-turn accumulation** | Name in turn 1, location in turn 3, salary in turn 5 | Re-identifiable profile | Cumulative PII Exposure (CPE) scoring |
| **Subagent context inheritance** | Parent agent passes full context to child | PII propagates across agents | Signal/Domain pattern — only pass needed fields |
| **Tool call leakage** | Agent calls external API with raw PII | Data leaves trust boundary | Capability tokens + pre-execution policy (Waxell/agent-kernel) |
| **Vector store memorization** | Embeddings of PII stored in Qdrant | Reconstruction attacks | Local-only vector store for private data; redacted embeddings for cloud |

### 2.2 CAMP-Inspired Cumulative PII Exposure (CPE) Scoring

Adapted from Panjwani et al. (2026) — `arXiv:2604.16521`:

```python
# src/omega/privacy/cpe_scorer.py
class CPESession:
    """Tracks cumulative PII exposure across conversation turns."""
    
    ENTITY_WEIGHTS = {
        "PERSON": 0.3, "LOCATION": 0.2, "ORGANIZATION": 0.25,
        "FINANCIAL": 0.5, "MEDICAL": 0.6, "CREDENTIAL": 0.8,
        "CONTACT": 0.25, "IDENTITY": 0.4,
    }
    
    COOCCURRENCE_BOOST = {
        ("PERSON", "FINANCIAL"): 0.4,
        ("PERSON", "MEDICAL"): 0.5,
        ("LOCATION", "IDENTITY"): 0.3,
        ("ORGANIZATION", "CREDENTIAL"): 0.45,
    }
    
    THRESHOLDS = {
        "LOW": 1.0,      # Pass — send original
        "MODERATE": 2.0, # Warn — log but allow
        "HIGH": 3.0,     # Pseudonymize — rewrite history
        "CRITICAL": 4.0, # Block — hard stop
    }
    
    def __init__(self, threshold: float = 2.0, alpha: float = 0.3):
        self.threshold = threshold
        self.alpha = alpha  # Graph amplifier
        self.registry: Dict[str, List[PIIEntity]] = defaultdict(list)
        self.cooccurrence_graph: nx.Graph = nx.Graph()
    
    def process_turn(self, turn_id: int, text: str) -> CPEAction:
        """Extract PII, update graph, compute CPE, decide action."""
        entities = self._extract_pii(text)  # Presidio + custom regex
        
        # Update registry
        for ent in entities:
            self.registry[ent.type].append(PIIEntity(
                value=ent.value, type=ent.type, turn=turn_id, span=ent.span
            ))
            self.cooccurrence_graph.add_node(ent.type)
        
        # Add co-occurrence edges
        types_in_turn = {e.type for e in entities}
        for t1 in types_in_turn:
            for t2 in types_in_turn:
                if t1 != t2:
                    self.cooccurrence_graph.add_edge(t1, t2, weight=1)
        
        # Compute CPE score
        cpe = self._compute_cpe()
        
        # Decide action
        if cpe >= self.THRESHOLDS["CRITICAL"]:
            return CPEAction.BLOCK
        elif cpe >= self.THRESHOLDS["HIGH"]:
            return CPEAction.PSEUDONYMIZE
        elif cpe >= self.THRESHOLDS["MODERATE"]:
            return CPEAction.WARN
        return CPEAction.PASS
    
    def _compute_cpe(self) -> float:
        """CPE = Σ(entity_weight * count) + α * Σ(edge_weight * cooccurrence_boost)"""
        base = sum(
            self.ENTITY_WEIGHTS.get(t, 0.1) * len(ents) 
            for t, ents in self.registry.items()
        )
        graph_boost = sum(
            self.COOCCURRENCE_BOOST.get((u, v), 0) * d.get("weight", 1)
            for u, v, d in self.cooccurrence_graph.edges(data=True)
        )
        return base + self.alpha * graph_boost
    
    def pseudonymize_history(self, history: List[Turn]) -> List[Turn]:
        """Retroactive pseudonymization — consistent synthetic substitutes."""
        fake = Faker()
        pseudonym_map = {}
        
        for ent_type, entities in self.registry.items():
            for ent in entities:
                if ent.value not in pseudonym_map:
                    if ent_type == "PERSON":
                        pseudonym_map[ent.value] = fake.name()
                    elif ent_type == "LOCATION":
                        pseudonym_map[ent.value] = fake.city()
                    elif ent_type == "ORGANIZATION":
                        pseudonym_map[ent.value] = fake.company()
                    elif ent_type == "FINANCIAL":
                        pseudonym_map[ent.value] = f"${fake.random_int(1000, 100000)}"
                    else:
                        pseudonym_map[ent.value] = f"<<{ent_type}_{len(pseudonym_map)}>>"
        
        # Rewrite history
        rewritten = []
        for turn in history:
            new_text = turn.text
            for real, fake_val in pseudonym_map.items():
                new_text = new_text.replace(real, fake_val)
            rewritten.append(Turn(text=new_text, role=turn.role, turn_id=turn.turn_id))
        
        return rewritten
    
    def demask_response(self, response: str) -> str:
        """Restore original values in LLM response before showing user."""
        for real, fake_val in self.pseudonym_map.items():
            response = response.replace(fake_val, real)
        return response
```

### 2.3 CloakBot-Inspired Local Privacy Kernel

**Architecture**: Local Gemma 4 E2B (or Qwen3-1.7B) runs as privacy detector *before* any cloud call.

```yaml
# config/privacy/kernel.yaml
privacy_kernel:
  enabled: true
  model: "gemma-4-e2b-q4_k_m"  # Local only, ~5GB
  detectors:
    general:
      enabled: true
      prompt_template: "privacy/core/detection/general_prompt.txt"
    digit:
      enabled: true
      prompt_template: "privacy/core/detection/digit_prompt.txt"
    visual:
      enabled: true
      ocr_engine: "tesseract"
  vault:
    path: "data/privacy/vaults/{session_id}.json"
    cross_turn_alias_reuse: true
  math_executor:
    enabled: true
    ast_validation: true
  streaming_restoration:
    enabled: true
    carryover_window: 1024  # chars
```

**Flow**:
```
User Input → [Pre-LLM Hook] → PrivacyRuntime (Gemma 4 E2B)
    → Detect spans → Session Vault (<<TYPE_N>> placeholders)
    → Sanitized payload → Remote LLM (Claude/Gemini/Grok)
    → Response with placeholders → [Post-LLM Hook]
    → Local restoration via Vault → User sees original values
```

**Key Guarantee**: Remote LLM *never* sees raw PII. Detection runs locally on user-controlled hardware.

---

## Part 3: Gitignored Config Split

### 3.1 Current Problem

`config/` contains mixed sensitivity:
```
config/
├── omega.yaml           # PUBLIC — engine config
├── providers.yaml       # MIXED — endpoint URLs (public) + API keys (private)
├── models.yaml          # PUBLIC — model definitions
├── wads/                # PUBLIC — stack definitions
└── glossary.md          # PUBLIC
```

### 3.2 Proposed Split

```
config/
├── public/                    # Git-tracked
│   ├── omega.yaml
│   ├── models.yaml
│   ├── providers.public.yaml  # Endpoint URLs, model mappings, rate limits
│   ├── wads/
│   └── glossary.md
│
├── private/                   # Gitignored, encrypted at rest
│   ├── providers.private.yaml # API keys, secrets, OAuth tokens
│   ├── vault.yaml             # Encrypted credential store
│   └── local_overrides.yaml   # Machine-specific paths, hardware config
│
├── .gitignore                 # Excludes private/
└── config.yaml                # Loader: merges public + private at runtime
```

### 3.3 Runtime Config Loader

```python
# src/omega/config/loader.py
class ConfigLoader:
    """Merges public + private config with private taking precedence."""
    
    def __init__(self, config_root: Path = Path("config")):
        self.public_root = config_root / "public"
        self.private_root = config_root / "private"
    
    def load_providers(self) -> ProvidersConfig:
        public = self._load_yaml(self.public_root / "providers.public.yaml")
        private = self._load_yaml(self.private_root / "providers.private.yaml")
        
        # Deep merge: private overrides public
        merged = self._deep_merge(public, private)
        
        # Decrypt secrets if encrypted
        if private and "encrypted" in private:
            merged = self._decrypt_secrets(merged, private["encrypted"])
        
        return ProvidersConfig(**merged)
    
    def _deep_merge(self, base: dict, override: dict) -> dict:
        result = base.copy()
        for k, v in override.items():
            if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                result[k] = self._deep_merge(result[k], v)
            else:
                result[k] = v
        return result
```

### 3.4 `.gitignore` Entry

```gitignore
# Soul private data
data/entities/*/soul.private/

# Config private
config/private/
config/providers.private.yaml
config/vault.yaml
config/local_overrides.yaml

# Privacy vaults
data/privacy/vaults/

# Encrypted backups (restic handles these)
*.enc
*.age
```

---

## Part 4: Restic Selective Backup for Private Data

### 4.1 Backup Policy by Tier

| Data Tier | Path | Restic Policy | Encryption | Retention |
|-----------|------|---------------|------------|-----------|
| **PUBLIC** | `data/entities/*/soul.public.yaml` | Standard repo | AES-256 (restic default) | 365 daily, 52 weekly, 12 monthly |
| **BONDED** | `data/entities/*/soul.private/bonds/` | Separate repo `soul-bonded` | AES-256 + age envelope | 90 daily, 12 weekly |
| **PRIVATE** | `data/entities/*/soul.private/` (excl bonds) | Separate repo `soul-private` | AES-256 + age + scrypt KDF | 30 daily, 4 weekly |
| **CONFIG PRIVATE** | `config/private/` | Separate repo `config-private` | AES-256 + age | 7 daily |
| **PRIVACY VAULTS** | `data/privacy/vaults/` | **NO BACKUP** — ephemeral | N/A | N/A |

### 4.2 Restic Repository Structure

```bash
# Initialize repos with different keys
restic -r b2:omega-backups/soul-public init
restic -r b2:omega-backups/soul-bonded init --key-file=/etc/restic/keys/bonded.key
restic -r b2:omega-backups/soul-private init --key-file=/etc/restic/keys/private.key
restic -r b2:omega-backups/config-private init --key-file=/etc/restic/keys/config.key

# Backup commands (in systemd timer)
restic -r b2:omega-backups/soul-public backup data/entities/ --include=soul.public.yaml
restic -r b2:omega-backups/soul-bonded backup data/entities/ --include=soul.private/bonds/
restic -r b2:omega-backups/soul-private backup data/entities/ --include=soul.private/ --exclude=soul.private/bonds/
restic -r b2:omega-backups/config-private backup config/private/
```

### 4.3 Selective Restore

```bash
# Restore only public souls forensics: restore single entity's private memories
restic -r b2:omega-backups/soul-private restore latest \
  --target=/tmp/restore \
  --include="data/entities/researcher/soul.private/memories/*"

# Emergency: restore config private
restic -r b2:omega-backups/config-private restore latest --target=/tmp/config-restore
```

### 4.4 Verification Without Full Restore

```bash
# Verify backup integrity (run weekly via systemd)
restic -r b2:omega-backups/soul-private check --read-data-subset=5%

# Verify specific file exists in backup
restic -r b2:omega-backups/soul-private ls latest "data/entities/researcher/soul.private/memories/L1_narrative.jsonl"
```

---

## Part 5: Actor-Model Token Scopes (Capability-Based Authorization)

### 5.1 Design Principles (from 1Password, Auth0, agent-kernel, AIP)

1. **Capabilities over scopes** — `billing.refund.issue_under_50_usd` not `billing:write`
2. **Task-scoped credentials** — Short-lived (5-10 min), purpose-bound, auto-expiring
3. **Layered enforcement** — Identity provider → Runtime policy → Tool-layer enforcement
4. **Delegated authority** — Human principal + agent actor = delegated token (RFC 8693)
5. **Intent binding** — Per-call transaction tokens with declared intent hash (CIBA + RAR)

### 5.2 Omega Capability Token Schema

```python
# src/omega/auth/capability_token.py
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime, timedelta
import uuid

class CapabilityConstraints(BaseModel):
    """Fine-grained constraints on capability usage."""
    max_calls: Optional[int] = None
    max_spend_usd: Optional[float] = None
    allowed_resources: Optional[list[str]] = None  # e.g., ["repo:omega-engine/*"]
    denied_resources: Optional[list[str]] = None
    time_window: Optional[str] = None  # "09:00-17:00 UTC"
    require_approval: bool = False
    approval_threshold_usd: Optional[float] = None

class CapabilityToken(BaseModel):
    """HMAC-signed, time-bounded, principal-scoped capability token."""
    # Identity
    token_id: str = Field(default_factory=lambda: f"cap_{uuid.uuid4().hex[:16]}")
    principal_id: str  # Human DID: "did:omega:human:arcana"
    actor_id: str      # Agent DID: "did:omega:agent:researcher"
    delegation_depth: int = 0  # 0 = direct, 1 = subagent, etc.
    
    # Capability
    capability_id: str  # e.g., "mcp.tools.call", "web.search", "file.read"
    purpose: str        # Human-readable: "Research Gemma 4 workhorse alternatives"
    constraints: CapabilityConstraints = Field(default_factory=CapabilityConstraints)
    
    # Time
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    not_before: Optional[datetime] = None
    
    # Crypto
    signature: str  # HMAC-SHA256 over canonical JSON
    key_id: str     # Key identifier for rotation
    
    # Audit
    justification: str = ""  # Why this capability was granted
    approval_ref: Optional[str] = None  # CIBA approval ID if required
    
    def is_valid(self, now: datetime = None) -> bool:
        now = now or datetime.utcnow()
        return self.not_before <= now < self.expires_at if self.not_before else now < self.expires_at
    
    def can_access(self, resource: str) -> bool:
        if self.constraints.allowed_resources:
            return any(fnmatch(resource, pattern) for pattern in self.constraints.allowed_resources)
        if self.constraints.denied_resources:
            return not any(fnmatch(resource, pattern) for pattern in self.constraints.denied_resources)
        return True
```

### 5.3 Capability Registry (Omega-Specific)

```yaml
# config/public/capabilities.yaml
capabilities:
  # MCP Tool Invocation
  - id: "mcp.tools.call"
    display: "Invoke MCP tool"
    risk_class: "READ"  # READ | WRITE | DESTRUCTIVE
    sensitivity: "LOW"
    default_constraints:
      max_calls: 100
      time_window: "00:00-23:59"
  
  - id: "mcp.tools.call.destructive"
    display: "Invoke destructive MCP tool (delete, modify)"
    risk_class: "DESTRUCTIVE"
    sensitivity: "HIGH"
    default_constraints:
      max_calls: 10
      require_approval: true
      approval_threshold_usd: 0
  
  # Web Search
  - id: "web.search"
    display: "Search the web"
    risk_class: "READ"
    sensitivity: "LOW"
    default_constraints:
      max_calls: 50
      allowed_providers: ["searxng", "exa", "brave"]
  
  # File System
  - id: "file.read"
    display: "Read file from local filesystem"
    risk_class: "READ"
    sensitivity: "MEDIUM"
    default_constraints:
      allowed_resources: ["~/Documents/**", "~/Projects/**"]
      denied_resources: ["~/.ssh/**", "~/.aws/**", "~/.config/gcloud/**"]
  
  - id: "file.write"
    display: "Write file to local filesystem"
    risk_class: "WRITE"
    sensitivity: "HIGH"
    default_constraints:
      allowed_resources: ["~/Projects/**/output/**", "~/tmp/**"]
      require_approval: true
  
  # Cloud Provider Calls
  - id: "provider.call.google"
    display: "Call Google Gemini API"
    risk_class: "READ"
    sensitivity: "HIGH"  # Sends data to Google
    default_constraints:
      max_calls: 20
      require_approval: false  # But CPE scorer may block
  
  - id: "provider.call.openrouter"
    display: "Call OpenRouter (BYOK)"
    risk_class: "READ"
    sensitivity: "MEDIUM"
    default_constraints:
      max_calls: 100
  
  # Code Execution
  - id: "code.exec.python"
    display: "Execute Python code in sandbox"
    risk_class: "DESTRUCTIVE"
    sensitivity: "CRITICAL"
    default_constraints:
      max_calls: 5
      require_approval: true
      allowed_resources: ["sandbox:*"]
  
  # Agent Spawning
  - id: "agent.spawn"
    display: "Spawn subagent"
    risk_class: "WRITE"
    sensitivity: "HIGH"
    default_constraints:
      max_calls: 3
      max_delegation_depth: 2
      require_approval: true
```

### 5.4 Token Broker (Issues Short-Lived Capability Tokens)

```python
# src/omega/auth/token_broker.py
class TokenBroker:
    """Issues capability tokens after policy evaluation."""
    
    def __init__(self, policy_engine: PolicyEngine, hmac_key: bytes, key_id: str):
        self.policy = policy_engine
        self.hmac_key = hmac_key
        self.key_id = key_id
    
    async def request_capability(
        self,
        principal_id: str,
        actor_id: str,
        capability_id: str,
        purpose: str,
        constraints: CapabilityConstraints = None,
        justification: str = "",
    ) -> CapabilityToken:
        """Evaluate policy, issue token if allowed."""
        
        # 1. Check principal has this capability in their grant
        grant = await self.policy.get_grant(principal_id)
        if capability_id not in grant.capabilities:
            raise PermissionDenied(f"Principal {principal_id} not granted {capability_id}")
        
        # 2. Check actor is authorized for this principal
        if not await self.policy.is_authorized_actor(principal_id, actor_id):
            raise PermissionDenied(f"Actor {actor_id} not authorized for {principal_id}")
        
        # 3. Evaluate policy constraints (time, spend, resource limits)
        effective_constraints = self._merge_constraints(
            grant.constraints.get(capability_id, CapabilityConstraints()),
            constraints or CapabilityConstraints()
        )
        
        # 4. Check if approval required
        if effective_constraints.require_approval:
            approval_id = await self._request_ciba_approval(
                principal_id, capability_id, purpose, effective_constraints
            )
            if not approval_id:
                raise PermissionDenied("Human approval required but not granted")
        
        # 5. Issue token
        token = CapabilityToken(
            principal_id=principal_id,
            actor_id=actor_id,
            capability_id=capability_id,
            purpose=purpose,
            constraints=effective_constraints,
            expires_at=datetime.utcnow() + timedelta(minutes=10),
            justification=justification,
            approval_ref=approval_id,
            key_id=self.key_id,
        )
        token.signature = self._sign_token(token)
        
        # 6. Audit log
        await self.audit_log.log(TokenIssuedEvent(
            token_id=token.token_id,
            principal=principal_id,
            actor=actor_id,
            capability=capability_id,
            purpose=purpose,
            constraints=effective_constraints.model_dump(),
        ))
        
        return token
    
    def _sign_token(self, token: CapabilityToken) -> str:
        canonical = token.model_dump_json(exclude={"signature"}, sort_keys=True)
        return hmac.new(self.hmac_key, canonical.encode(), hashlib.sha256).hexdigest()
    
    def verify_token(self, token: CapabilityToken) -> bool:
        expected = self._sign_token(token)
        return hmac.compare_digest(token.signature, expected)
```

### 5.5 Runtime Enforcement (Pre-Execution Policy Layer)

```python
# src/omega/auth/enforcer.py
class CapabilityEnforcer:
    """Enforces capability tokens at tool-call boundary."""
    
    def __init__(self, broker: TokenBroker, audit_log: AuditLog):
        self.broker = broker
        self.audit = audit_log
    
    async def authorize_and_execute(
        self,
        principal_id: str,
        actor_id: str,
        capability_id: str,
        purpose: str,
        tool_call: ToolCall,
        constraints: CapabilityConstraints = None,
    ) -> ToolResult:
        """Full authorization → execution → audit pipeline."""
        
        # 1. Request capability token
        token = await self.broker.request_capability(
            principal_id=principal_id,
            actor_id=actor_id,
            capability_id=capability_id,
            purpose=purpose,
            constraints=constraints,
            justification=f"Tool call: {tool_call.name}({tool_call.args})",
        )
        
        # 2. Verify token
        if not self.broker.verify_token(token):
            raise SecurityError("Invalid capability token signature")
        
        if not token.is_valid():
            raise SecurityError("Capability token expired")
        
        # 3. Check resource constraints
        resource = self._extract_resource(tool_call)
        if not token.can_access(resource):
            raise PermissionDenied(f"Token does not permit access to {resource}")
        
        # 4. Check call limits
        if token.constraints.max_calls:
            used = await self.audit.count_calls(token.token_id)
            if used >= token.constraints.max_calls:
                raise RateLimited(f"Capability {capability_id} call limit exceeded")
        
        # 5. Execute with context firewall (agent-kernel pattern)
        # Raw tool output NEVER reaches LLM — only bounded Frame
        frame = await self._execute_with_firewall(tool_call, token)
        
        # 6. Audit
        await self.audit.log(ActionTrace(
            action_id=uuid.uuid4().hex,
            token_id=token.token_id,
            principal=principal_id,
            actor=actor_id,
            capability=capability_id,
            tool=tool_call.name,
            args=self._redact_args(tool_call.args, token),
            result=frame.facts,  # Only sanitized facts
            timestamp=datetime.utcnow(),
            success=True,
        ))
        
        return frame
    
    def _redact_args(self, args: dict, token: CapabilityToken) -> dict:
        """Redact sensitive args based on token sensitivity level."""
        if token.constraints.sensitivity in ("HIGH", "CRITICAL"):
            return {"[REDACTED]": "args hidden per capability sensitivity"}
        return args
```

---

## Part 6: Integration with Omega Engine

### 6.1 File Structure Changes

```
src/omega/
├── soul/
│   ├── __init__.py
│   ├── loader.py           # Public/private split loader
│   ├── recall.py           # Privacy-filtered recall
│   ├── evolution.py        # Evolution with private mutation details
│   └── privacy.py          # Visibility tier constants
│
├── privacy/
│   ├── __init__.py
│   ├── cpe_scorer.py       # Cumulative PII Exposure
│   ├── kernel.py           # Local privacy kernel (Gemma 4 E2B)
│   ├── vault.py            # Session vault for placeholder mapping
│   ├── redaction.py        # PII redaction patterns
│   └── hooks.py            # Pre/post LLM hooks
│
├── auth/
│   ├── __init__.py
│   ├── capability_token.py # Capability token schema
│   ├── token_broker.py     # Issues tokens after policy eval
│   ├── enforcer.py         # Pre-execution enforcement
│   ├── policy_engine.py    # Policy evaluation (Cedar/OPA)
│   └── audit_log.py        # Tamper-evident action traces
│
├── config/
│   └── loader.py           # Public/private config merger
```

### 6.2 Configuration Updates

```yaml
# config/public/omega.yaml
omega:
  soul:
    privacy:
      enabled: true
      visibility_tiers: ["public", "bonded", "private"]
      bonded_threshold: 50
      private_encryption: "age"  # or "sops", "gpg"
  
  privacy:
    cpe:
      enabled: true
      threshold: 2.0
      alpha: 0.3
    kernel:
      enabled: true
      model: "gemma-4-e2b-q4_k_m"
      local_only: true
  
  auth:
    capabilities:
      enabled: true
      token_ttl_minutes: 10
      hmac_key_env: "WEAVER_KERNEL_SECRET"
      policy_backend: "cedar"  # or "opa", "builtin"
```

```yaml
# config/private/providers.private.yaml
providers:
  google:
    api_key: "ENCRYPTED[age:...]"
    project_id: "omega-engine-prod"
  openrouter:
    api_key: "ENCRYPTED[age:...]"
  antigravity:
    oauth_token: "ENCRYPTED[age:...]"
    refresh_token: "ENCRYPTED[age:...]"
```

### 6.3 Systemd Service Updates

```ini
# quadlet-test/omega-iris.service (updated)
[Service]
Environment=OMEGA_CONFIG_PUBLIC=/app/config/public
Environment=OMEGA_CONFIG_PRIVATE=/app/config/private
Environment=OMEGA_SOUL_PUBLIC=/app/data/entities/iris/soul.public.yaml
Environment=OMEGA_SOUL_PRIVATE=/app/data/entities/iris/soul.private
Environment=WEAVER_KERNEL_SECRET_FILE=/run/secrets/weaver_kernel_secret
# ... rest unchanged
```

---

## Part 7: Implementation Roadmap

### Phase 1: Foundation (Week 1) — P0
| Task | Owner | Deliverable |
|------|-------|-------------|
| Split `soul.yaml` → `soul.public.yaml` + `soul.private/` | @maat/P3 | Loader + recall privacy filter |
| Implement visibility tiers (PUBLIC/BONDED/PRIVATE) | @maat/P3 | `soul/privacy.py` + recall engine |
| Gitignore `soul.private/` + `config/private/` | @maat/P3 | `.gitignore` updates |
| Config loader: public/private merge | @maat/P3 | `config/loader.py` |

### Phase 2: Conversation Privacy (Week 2) — P0
| Task | Owner | Deliverable |
|------|-------|-------------|
| CPE scorer implementation | @researcher | `privacy/cpe_scorer.py` |
| Local privacy kernel (Gemma 4 E2B) | @pillar P6 | `privacy/kernel.py` + model download |
| Session vault + placeholder restoration | @researcher | `privacy/vault.py` |
| Pre/post LLM hooks integration | @maat/P3 | `privacy/hooks.py` in Oracle.talk() |

### Phase 3: Backup & Authorization (Week 3) — P1
| Task | Owner | Deliverable |
|------|-------|-------------|
| Restic multi-repo setup (public/bonded/private) | @maat/P1 | Systemd timers + repo init scripts |
| Selective restore procedures documented | @maat/P1 | Runbook |
| Capability token schema + HMAC signing | @maat/P3 | `auth/capability_token.py` |
| Token broker + policy engine | @maat/P3 | `auth/token_broker.py` + Cedar policies |
| Enforcer integration at tool boundary | @maat/P3 | `auth/enforcer.py` in MCP tool handlers |

### Phase 4: Hardening (Week 4) — P1
| Task | Owner | Deliverable |
|------|-------|-------------|
| End-to-end privacy test suite | @verity | `tests/privacy/` |
| Red-team evaluation (CloakBot eval harness) | @researcher | Leak detection report |
| Documentation: Soul Privacy Model | @scribe | `docs/architecture/SOUL_PRIVACY_MODEL.md` |
| Migration script for existing souls | @maat/P3 | `scripts/migrate_soul_privacy.py` |

---

## Part 8: Decision Gates

| Gate | Criteria | Decision |
|------|----------|----------|
| **G1: Split Complete** | All entities have `soul.public.yaml` + `soul.private/`; recall filters work | Go/No-Go |
| **G2: Privacy Kernel Live** | CPE scorer blocks/pseudonymizes correctly; kernel detects PII locally | Go/No-Go |
| **G3: Backup Verified** | All 4 restic repos backup + restore successfully; `check --read-data-subset` passes | Go/No-Go |
| **G4: Capability Tokens Work** | Token broker issues, enforcer validates, audit log captures full trace | Go/No-Go |

---

## Part 9: Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Gemma 4 E2B too slow on CPU** | Medium | High | Fallback to Qwen3-1.7B; regex fast-path for common PII |
| **CPE false positives block legitimate work** | Medium | Medium | Tunable threshold; per-entity weight overrides; audit log review |
| **Restic key management complexity** | High | Medium | Age envelope encryption; keys in 1Password / systemd-creds |
| **Capability token explosion** | Medium | Low | Start with 15 core capabilities; add via PR review |
| **Subagent token delegation broken** | Medium | High | Enforce `delegation_depth` in token; test multi-level spawn |
| **Migration breaks existing souls** | Low | High | Dry-run script; backup before migrate; rollback procedure |

---

## Part 10: Appendix — Key References

| Source | Key Insight Applied |
|--------|---------------------|
| **Soul Protocol (qbtrix)** | PUBLIC/BONDED/PRIVATE visibility tiers; trust chain; .soul ZIP format; domain isolation |
| **soul.py (menonpg)** | SOUL.md/MEMORY.md split; modulizer for token savings; hybrid RAG+RLM |
| **CAMP (Panjwani 2026)** | Cumulative PII Exposure scoring; co-occurrence graph; retroactive pseudonymization |
| **CloakBot (Spire Studio)** | Local Gemma 4 E2B privacy kernel; session vault; streaming placeholder restoration |
| **local-private-orchestration (jlynshue)** | 8-layer defense; consent gates; tamper-proof audit chain; SQLCipher |
| **1Password Agent Identity** | Delegated authority; SPIFFE JWT-SVID; OAuth 2.0 Token Exchange; intent-bound txn tokens |
| **agent-kernel (dgenio)** | HMAC capability tokens; policy engine; context firewall (Frame); audit traces |
| **Auth0 Agent Permissions** | Capability-scoped permissions; task-scoped credentials; layered enforcement |
| **AIP (Singla IETF)** | DID-based agent identity; capability manifests; delegation chains; tiered security |
| **Waxell** | Signal/Domain pattern; pre-execution policy layer; data minimization |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ R19 COMPLETE ⬡ 2026-07-24*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
