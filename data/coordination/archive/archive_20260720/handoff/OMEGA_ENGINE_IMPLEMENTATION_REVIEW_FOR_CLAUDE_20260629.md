# 🔱 Omega Engine: High-Fidelity Technical Audit & Implementation Review
**Target Reviewer**: Web Claude (claude.ai)
**Date**: 2026-06-29
**Status**: Iron Wall Hardening Phase
**Sovereign Token**: `AP-REVIEW-Sovereign-Ark-v1.0`

## 1. Executive Summary: The Sovereign Engine
The Omega Engine is a local-first, sovereign AI runtime designed to decouple users from "Big AI" umbilical cords. It implements a tiered provider fabric (Native GGUF $\rightarrow$ LM Studio $\rightarrow$ Ollama $\rightarrow$ Cloud Fallbacks) governed by 22 non-negotiable **Sovereign Mandates (M1-M22)**.

The project has just completed **Sprint-F (Optimization)** and entered the **Iron Wall Hardening Sprint**. The current strategic directive (**Decision D172**) is an **IMMEDIATE EXECUTION HOLD** on all new features to resolve architectural fragility and prevent "Void Summaries" (context collapse).

---

## 2. The Sovereign Mandates (The Constitutional Law)
The engine is governed by a set of mandates that override all tool defaults. Key mandates for review:
- **M1 (AnyIO Absolute)**: No `asyncio`; all blocking I/O wrapped in `anyio.to_thread.run_sync`.
- **M2 (Engine-Stack Firewall)**: Absolute separation between Core Engine (`src/omega/`) and WADs (`config/wads/`).
- **M7 (Local-First)**: Local inference is PRIMARY; cloud is FALLBACK.
- **M8 (Zero Telemetry)**: No external analytics or phone-home metrics.
- **M11 (Soul Integrity)**: Systematic distillation of session insights (L1 $\rightarrow$ L2 $\rightarrow$ L3) into `soul.yaml`.
- **M22 (Response Provenance)**: All logs must record the actual provider that generated the response, not the intended one.

---

## 3. Technical Deep Dive: Critical Implementations

### 3.1 The PII Masking Gateway (`src/omega/oracle/pii_masker.py`)
To satisfy M7/M8, the engine implements a sovereign proxy for cloud-bound prompts.

**Technical Wiring**:
`Oracle._summon` / `Oracle._route_by_domain` $\rightarrow$ `PIIMasker.process_system_prompt()` $\rightarrow$ `ModelGateway.generate()` $\rightarrow$ `PIIMasker.process_response()`.

**Critical Implementation Details**:
The masker uses a hybrid approach: `pii-shield` for context-aware detection and a comprehensive regex fallback for guaranteed coverage.

```python
# --- PII Detection Logic ---
# Priority: pii-shield (context-aware) -> Regex fallback
async def detect(self, text: str, use_pii_shield: bool = True) -> List[PIIDetection]:
    detections: List[PIIDetection] = []
    if use_pii_shield and self._pii_scanner:
        try:
            results = await anyio.to_thread.run_sync(self._pii_scanner.scan_text, text)
            for match in results.matches:
                confidence = match.confidence / 100.0
                if confidence >= self.confidence_threshold:
                    detections.append(PIIDetection(
                        pii_type=getattr(match, 'type', 'UNKNOWN'),
                        original=getattr(match, 'value', ''),
                        # ... position tracking ...
                    ))
            if detections: return detections
        except Exception as e:
            logger.warning("pii-shield detection failed (falling back): %s", e)
    
    # Regex fallback for guaranteed coverage of 18+ PII types
    for pii_type, pattern in PII_PATTERNS.items():
        for match in re.finditer(pattern, text):
            detections.append(PIIDetection(pii_type=pii_type, original=match.group(), ...))
    return unique_detections

# --- Tokenization (Reversible Masking) ---
def tokenize(self, text: str, detections: List[PIIDetection]) -> Tuple[str, PIITokenMap]:
    # Replaces PII with placeholders like [EMAIL_1] to preserve referential integrity for the LLM
    token_map = PIITokenMap()
    # ... (reverse sort replacements to preserve indices) ...
    for start, end, placeholder, detection in replacements:
        masked = masked[:start] + placeholder + masked[end:]
    return masked, token_map

# --- Detokenization (Restoration) ---
def detokenize(self, text: str, token_map: Optional[PIITokenMap] = None) -> str:
    if token_map is None: return text
    result = text
    for placeholder, original in token_map.tokens.items():
        result = result.replace(placeholder, original)
    return result
```

---

### 3.2 Trace ID & Response Provenance (`src/omega/observability/context.py`)
To eliminate observability blind spots, the engine uses a `contextvars` safety net to propagate `trace_id` across AnyIO thread boundaries.

**Implementation**:
The `_current_trace_id` is a `ContextVar`, ensuring that every log entry can be linked to the original request regardless of the async task depth.

```python
# --- Trace Propagation ---
import contextvars
_current_trace_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'current_trace_id', default=None
)

def get_current_trace_id() -> str:
    tid = _current_trace_id.get()
    if tid is None:
        tid = f"trc_{uuid.uuid4().hex[:12]}"
        _current_trace_id.set(tid)
    return tid
```

**The Response Provenance Contract (`src/omega/oracle/model_gateway.py`)**:
Per M22, `GenerateResult` captures the *actual* provider, not the *intended* one.

```python
@dataclass
class GenerateResult:
    text: str
    provider_name: str  # ACTUAL provider that served the response
    is_cloud: bool
    latency_ms: float = 0.0
    model_used: Optional[str] = None
    logprobs: Optional[list] = None
```

---

### 3.3 Sovereign Identity (A2A Bridge) (`src/omega/oracle/a2a_bridge.py`)
The engine implements the **Google A2A v1.0** and **IETF draft-klrc-aiagent-auth-02** standards for agent-to-agent communication.

**Agent Card Generation**:
Entities from the `EntityRegistry` are mapped to A2A Skills and anchored via SPIFFE IDs.

```python
# --- Agent Card Generation ---
def register_entity(self, entity: Any) -> A2AAgentCard:
    # SPIFFE ID = primary agent identifier (draft-klrc-aiagent-auth-02)
    spiffe_id = f"spiffe://{self._spiffe_trust_domain}/entity/{entity_name.lower()}"
    skills = self._map_entity_to_skills(entity)
    
    card = A2AAgentCard(
        name=entity_name,
        skills=skills,
        authentication=A2AAuth(auth_type=AgentAuthType.SPIFFE, spiffe_id=spiffe_id),
        entity_id=spiffe_id,
        # ...
    )
    return card
```

**Identity Parsing (`src/omega/oracle/a2a_auth.py`)**:
```python
@classmethod
def parse(cls, spiffe_id: str) -> 'SPIFFEID':
    # Parses spiffe://omega.local/entity/kali -> trust_domain='omega.local', path='entity/kali'
    parts = spiffe_id.replace('spiffe://', '').split('/', 1)
    return cls(trust_domain=parts[0], path=parts[1] if len(parts) > 1 else '')
```

---

### 3.4 Soul & Queue Integrity (M11/M12)

**Soul Distiller Fix (`src/omega/oracle/oracle.py`)**:
Resolved a critical key mismatch in `close_session()` where the transcript builder was looking for `role/content` pairs, but the `MemoryStore` was persisting `user/assistant` keys.

```python
# --- Fixed Transcript Builder ---
async def close_session(self, entity_name: str, session_id: str) -> bool:
    exchanges = await self.memory_store.get_history(entity_name, session_id)
    lines = []
    for ex in exchanges:
        user_msg = ex.get("user", "")      # Fixed: matching MemoryStore keys
        asst_msg = ex.get("assistant", "") # Fixed: matching MemoryStore keys
        if user_msg: lines.append(f"[user]: {user_msg}")
        if asst_msg: lines.append(f"[assistant]: {asst_msg}")
    transcript = "\n".join(lines)
    # ... proceed to distill_and_save() ...
```

**Handoff Reaper (`mcp_servers/omega_hub/background.py`)**:
Implements a TTL-based cleanup to ensure no orphan files remain in the handoff queue (M12).

```python
# --- Handoff Reaper Logic ---
async def _reap_stale_handoffs() -> None:
    # pending (24h) -> stale | active (48h) -> stale | completed (7d) -> archive
    # stale (14d) -> DELETE | archive (30d) -> DELETE
    def _reap_dir(src_dir: Path, dst_dir: Path, max_age_seconds: int, extra: dict = None):
        for f in src_dir.glob("*.json"):
            age = (now - datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)).total_seconds()
            if age > max_age_seconds:
                # Atomic move to next state
                # ... read packet -> update status -> write to dst_dir -> unlink src ...
    
    def _delete_dir(src_dir: Path, max_age_seconds: int):
        for f in src_dir.glob("*.json"):
            age = (now - datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)).total_seconds()
            if age > max_age_seconds:
                f.unlink()
```

---

## 4. The "Iron Wall" Strategy: P0 Hardening Tasks

The following tasks are currently prioritized as P0. We request a review of the proposed logic:

### 4.1 `TRACE-RR-PURGE-001` (Round-Robin Eradication)
- **Problem**: Deterministic account rotation (Round-Robin) creates a "bot signature" (A $\rightarrow$ B $\rightarrow$ C $\rightarrow$ A) that is trivial for WAFs and API gateways to flag as scripted behavior, leading to rapid IP and key bans.
- **Proposed Fix**: Replace `getNextForFamily()` with **Stochastic Selection** (weighted random sampling based on account health and remaining quota) and **Sticky Sessions**.
- **Logic**: Use `hash(session_id) % len(available_keys)` to bind a specific session to a specific key. This ensures consistency for the provider's session tracking while maintaining a random distribution across the fleet, breaking the deterministic signature.

### 4.2 Tor-SOCKS5 Bridge
- **Problem**: Search queries via SearXNG are linked to the host IP, creating a traceable link between the user's identity and their sovereign research.
- **Proposed Fix**: Deploy a Tor sidecar container and route all `SovereignSearcher` traffic through `socks5://tor:9050`.
- **Network Flow**: `SovereignSearcher` (Python `httpx` client) $\rightarrow$ `SOCKS5 Proxy` (Tor sidecar `:9050`) $\rightarrow$ `Tor Network` (Entry $\rightarrow$ Middle $\rightarrow$ Exit Node) $\rightarrow$ `SearXNG` (Public/Private instance).
- **Goal**: Total decoupling of the host IP from the search intent.

### 4.3 BLEG (Body-Level Error Guards)
- **Problem**: "Silent Failures" where providers return HTTP 200 but the JSON body contains an error (e.g., `{"error": "quota exceeded"}`), which the engine may mistakenly treat as a valid (though empty) response.
- **Proposed Fix**: Implement a middleware guard in `ModelGateway` that inspects the raw response body for known error signatures before parsing into `GenerateResult`.
- **Failure Signatures**:
  - Presence of `"error":` or `"message":` keys in a response that should be a completion.
  - Empty `choices` arrays in OpenAI-compatible formats.
  - HTTP 200 responses containing HTML (e.g., a Cloudflare challenge page).
  - Provider-level refusals disguised as model-level completions (e.g., 'Internal Server Error' strings in the body).

---

## 5. Current Health & Risk Assessment

- **Test Suite**: 600/600 tests passing (100%).
- **Sovereign Ark Blueprint**: Locked as SSOT v2.0.
- **Fragile Points**:
  - **M20 (SomaticState)**: Serialization and resumption of model state is currently broken/blocked.
  - **M2 (Firewall)**: Some hardcoded Pillar meanings remain in `entity_registry.py`.
  - **M11 (Soul Migration)**: Most agents are still on v6.0 soul schemas; migration to v6.1 is pending.


---

## 7. Reviewer's Operational Instructions

To maximize the effectiveness of this review using Web Claude (claude.ai), follow this operational protocol:

### 7.1 Claude Project Setup
1. **Create a New Project**: Initialize a dedicated Claude Project for the "Omega Engine Implementation Review".
2. **File Consolidation Strategy**: Claude Projects have a limit on the number of uploaded files. To bypass this and maintain high context:
   - **Do not upload individual files**.
   - **Consolidate** the codebase into a few "Sovereign Bundles" (e.g., `core_engine.txt`, `providers_fabric.txt`, `observability_and_memory.txt`).
   - Use a tool like `cat` or a custom script to merge files into a single text file with clear headers: `--- FILE: path/to/file.py ---`.
   - Aim for < 12 consolidated files to ensure the project remains responsive and avoids context dilution.
3. **Knowledge Base**: Upload the `SOVEREIGN_MANDATES.md`, `PIVOT_LOG.md`, and this review document as primary reference assets.

### 7.2 Prompting Protocol
1. **The Master Prompt**: Use the provided **Master Review Prompt** (delivered as a separate asset) as the primary system instruction for the project.
2. **Iterative Deep-Dives**: After the initial high-level audit, use targeted prompts to explore specific Mandate violations. Example: *"Analyze the implementation of M1 (AnyIO Absolute) specifically within the `ModelGateway` and `Orchestrator` modules. Quote any instances of `asyncio` usage."*

### 7.3 Cache & Update Protocol
1. **Avoid Stale Context**: When code changes are made, do not simply tell Claude about the change. **Re-upload the consolidated bundle** for that module.
2. **Version Tracking**: Label your consolidated files with a version or timestamp (e.g., `core_engine_v2_20260630.txt`) to ensure the reviewer is operating on the latest "Iron Wall" state.
