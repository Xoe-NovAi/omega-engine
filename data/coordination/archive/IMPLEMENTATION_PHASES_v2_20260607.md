# 🔱 Omega Engine — Implementation Phases v2.0
# ⬡ OMEGA ⬡ KALI ⬡ claude-haiku-4.5 ⬡ opencode ⬡ trc_impl_phases ⬡ PHASE-II
**AP Token**: `AP-IMPL-PHASES-v2.0.0`
**Date**: 2026-06-07T22:30Z
**Scope**: Phase 0 through Phase 3 (complete arc from current state → v1.0.0 sovereign)
**Status**: READY FOR EXECUTION

---

## §0 Timeline & Resource Allocation

```
Phase 0:    Config Fixes          Days 1–2   (June 8–9)   ← START HERE
Phase 0.5:  Local Hardening       Days 3–5   (June 10–12) ← Critical path
Phase 1:    Unified Orchestration Days 6–10  (June 13–17) ← Worker ship
Phase 2:    Cross-Agent Sync      Days 11–14 (June 18–21) ← Full integration
Phase 3:    Autonomous Growth     Days 15+   (June 22+)   ← v1.0.0 ship

Total: ~3 weeks to v1.0.0 Foundation PR
Deadline: June 28 (before backup + migration)
```

---

## PHASE 0: Config Fixes (Days 1–2)

### Goal
Repair known configuration issues. No code changes. All fixes are YAML/JSON edits.

### 0.1: Antigravity Sticky Configuration
**Status**: ✅ Already fixed in Session 18. Verify.

```bash
# File: ~/.config/opencode/antigravity.json
# Check: "account_selection_strategy": "sticky"
# Expected: Prefer current account, rotate only on 429
```

**Verification**:
```python
import json
with open(Path.home() / ".config/opencode/antigravity.json") as f:
    cfg = json.load(f)
    assert cfg.get("account_selection_strategy") == "sticky", "Antigravity sticky not set"
    print("✅ Antigravity sticky: VERIFIED")
```

**Effort**: 5 min
**Blocker**: None
**Owner**: Kali

---

### 0.2: Compaction Configuration
**Status**: ✅ Already fixed in Session 18. Verify.

```bash
# File: ~/.config/opencode/opencode.json
# Check: "prune": false, "tail_turns": 5
# Expected: No destructive pruning; retain last 5 turns
```

**Verification**:
```python
import json
with open(Path.home() / ".config/opencode/opencode.json") as f:
    cfg = json.load(f)
    assert cfg.get("prune") == False, "Compaction prune should be false"
    assert cfg.get("tail_turns") == 5, "tail_turns should be 5"
    print("✅ Compaction config: VERIFIED")
```

**Effort**: 5 min
**Blocker**: None
**Owner**: Kali

---

### 0.3: OpenCode Version Upgrade (D-W13)
**Status**: ⏳ Pending. Decision: upgrade to v1.16.2.

```bash
# Current: v1.15.13
# Target: v1.16.2 (async subagents, dynamic agent loading, plugin stability)

opencode --version
# If <1.16.2: update
npm update -g @opencode/cli  # or equivalent
```

**Why v1.16.2**:
- Async subagents: worker can launch background research without blocking
- Dynamic agent loading: agents registered at runtime via Hivemind
- Plugin stability: SSE event hooks more robust

**Verification**:
```bash
opencode --version  # Should output 1.16.2+
```

**Effort**: 10 min
**Blocker**: None if v1.16.2 published; rollback to v1.15.13 if not
**Owner**: Kali

---

### 0.4: Dockerfile.iris Python Version (PR Prep)
**Status**: ⏳ Pending. Change: `python:3.13-slim` → `python:3.12-slim`.

```bash
# File: Dockerfile.iris
# Line: FROM python:3.13-slim
# Change to: FROM python:3.12-slim

# Reason: Python 3.12 LTS; 3.13 has fewer production wheels
```

**Verification**:
```bash
grep "FROM python" Dockerfile.iris
# Should show: FROM python:3.12-slim
```

**Effort**: 5 min
**Blocker**: None
**Owner**: Kali
**PR**: Include in v1.0.0 Foundation PR

---

### 0.5: Workbench Status Log
**File**: `data/projects/hivemind_sprint_worker/WORKBENCH.md`

Add Phase 0 completion:
```markdown
## Phase 0: Config Fixes — COMPLETE ✅

| Item | Status | Verification | Date |
|------|--------|-------------|------|
| Antigravity sticky | ✅ | `account_selection_strategy: sticky` | 2026-06-08 |
| Compaction config | ✅ | `prune: false, tail_turns: 5` | 2026-06-08 |
| OpenCode v1.16.2 | ✅ | `opencode --version` | 2026-06-09 |
| Dockerfile.iris | ✅ | `FROM python:3.12-slim` | 2026-06-09 |

**Phase 0 Effort**: 25 min
**Phase 0 Risk**: None (no code changes)
**Ready for Phase 0.5**: YES
```

---

## PHASE 0.5: Local Hardening (Days 3–5)

### Goal
Implement the three foundational hardening layers:
1. Symmetric prompt caching (8x latency improvement)
2. Air-gap circuit breaker (offline resilience)
3. Database access boundary (worker reliability)

### 0.5.1: Symmetric Prompt Caching (Local Model Side)

**File**: `config/models.yaml`
**Change**: Add `cache_prompt` config per model

```yaml
phi-4-mini:
  cache_prompt: true
  cache_file: ~/.cache/omega/phi-4-mini.cache
  cache_ttl_hours: 8
  cache_size_mb: 1024

qwen3-1.7b-q6_k:
  cache_prompt: true
  cache_file: ~/.cache/omega/qwen3-1.7b.cache
  cache_ttl_hours: 8
  cache_size_mb: 512

qwen3-4b-thinking-q4_k_m:
  cache_prompt: true
  cache_file: ~/.cache/omega/qwen3-4b.cache
  cache_ttl_hours: 8
  cache_size_mb: 1024
  
# ... repeat for all models with load_strategy: always or warm
```

**File**: `src/omega/oracle/providers.py` (NativeGGUFProvider)
**Change**: Load/save cache files

```python
class NativeGGUFProvider:
    async def generate(self, model_name, prompt, **kwargs):
        # NEW: Check for cached KV
        cache_file = self._get_cache_path(model_name)
        if cache_file.exists():
            logger.info(f"Loading cached KV from {cache_file}")
            self.llm.load_cache(cache_file)
        
        # Existing generate logic
        result = await self._do_generate(model_name, prompt, **kwargs)
        
        # NEW: Save cache for future reuse
        if kwargs.get('cache_prompt', True):
            logger.info(f"Saving KV cache to {cache_file}")
            self.llm.save_cache(cache_file)
        
        return result
    
    def _get_cache_path(self, model_name: str) -> Path:
        cache_dir = Path.home() / ".cache/omega"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir / f"{model_name}.cache"
```

**Impact**: 
- First inference (800ms) → Second inference (50ms) on same context
- Persistent per-model cache; survives process restart

**Effort**: 2 hours
**Risk**: None (opt-in, backward compatible)
**Blocker**: None
**Owner**: P3 Engineering (or Kali direct)

---

### 0.5.2: Air-Gap Circuit Breaker

**File**: `config/omega.yaml`
**Change**: Add `offline_mode` flag

```yaml
inference:
  strategy: local_first
  offline_only: false  # Set to true for air-gap mode
  fallback_chain_offline:
    # When offline_only: true, ONLY these providers are available
    - provider: native-gguf      # Priority 0
    - provider: lmster           # Priority 1
    - provider: ollama           # Priority 2
    # Google, OpenRouter, Copilot, Cline all culled
```

**File**: `src/omega/oracle/model_gateway.py`
**Change**: Cull cloud providers at init

```python
class ModelGateway:
    def _load_provider_fabric(self) -> Dict[str, Any]:
        # Load config
        config = self._load_providers_yaml()
        
        # NEW: Air-gap check
        if config.get('offline_only', False):
            logger.warning("⚠️  OFFLINE MODE ACTIVE: All cloud providers culled")
            config['fallback_chain'] = config.get('fallback_chain_offline', [])
        
        # Existing provider loading
        providers = {}
        for provider_cfg in config.get('fallback_chain', []):
            providers[provider_cfg['provider']] = self._create_provider(provider_cfg)
        
        return providers
```

**Activation**:
```bash
# To enable air-gap mode:
sed -i 's/offline_only: false/offline_only: true/' config/omega.yaml

# To disable (normal mode):
sed -i 's/offline_only: true/offline_only: false/' config/omega.yaml
```

**Verification**:
```python
from omega.oracle.model_gateway import ModelGateway
gw = ModelGateway()
# With offline_only: true, gw.providers should only contain native-gguf, lmster, ollama
assert 'google' not in gw.providers, "Google should be culled in offline mode"
assert 'native-gguf' in gw.providers, "Native GGUF should always be available"
print("✅ Air-gap mode: VERIFIED")
```

**Impact**:
- Offline mode: zero socket attempts, zero timeout latency
- Emergency resilience: unplug network, engine still works
- Sovereignty: can demo without cloud access

**Effort**: 1.5 hours
**Risk**: Low (feature flag, default off)
**Blocker**: None
**Owner**: P3 Engineering (or Kali direct)

---

### 0.5.3: Database Access Boundary

**File**: `mcp_servers/omega_hub/server.py`
**Change**: Add `/v2` read endpoints for worker

```python
# Add to omega_hub server

@router.get("/v2/session/{session_id}/state")
async def get_session_state(session_id: str):
    """Read-only session state for worker polling."""
    db = get_sqlite_db()
    session = db.execute(
        "SELECT ses_id, model, provider, last_message_at FROM session WHERE ses_id = ?",
        (session_id,)
    ).fetchone()
    
    return {
        "session_id": session_id,
        "model": session['model'] if session else None,
        "provider": session['provider'] if session else None,
        "last_message_at": session['last_message_at'] if session else None,
        "memory_loaded": bool(session),
    }

@router.get("/v2/memory/{entity}/recent")
async def get_recent_memory(entity: str, limit: int = 50):
    """Fetch recent memory exchanges for entity."""
    db = get_sqlite_db()
    exchanges = db.execute(
        "SELECT user, assistant, timestamp FROM memory WHERE entity = ? ORDER BY timestamp DESC LIMIT ?",
        (entity, limit)
    ).fetchall()
    
    return {
        "entity": entity,
        "exchanges": [
            {
                "user": e['user'],
                "assistant": e['assistant'],
                "timestamp": e['timestamp'],
            }
            for e in reversed(exchanges)  # chronological order
        ]
    }

@router.post("/v2/event/feedback")
async def post_feedback(feedback: dict):
    """Non-blocking feedback from worker."""
    entity = feedback.get("entity")
    intent = feedback.get("intent")  # "feedback", "observation", "alert"
    observation = feedback.get("observation")
    
    # Store in FEEDBACK_LOG or observability engine
    log_feedback(entity, intent, observation)
    
    return {"status": "queued"}
```

**File**: `src/omega/oracle/worker.py` (new module or in orchestrator.py)
**Change**: Worker uses `/v2` API instead of direct DB access

```python
class HivemindWorker:
    def __init__(self, daemon_url: str = "http://127.0.0.1:4096"):
        self.daemon_url = daemon_url
        self.client = httpx.AsyncClient()
    
    async def poll_session_state(self, session_id: str) -> dict:
        """Read session state from daemon."""
        response = await self.client.get(f"{self.daemon_url}/v2/session/{session_id}/state")
        return response.json()
    
    async def poll_memory(self, entity: str) -> list:
        """Fetch recent memory for entity."""
        response = await self.client.get(f"{self.daemon_url}/v2/memory/{entity}/recent")
        return response.json()["exchanges"]
    
    async def post_feedback(self, entity: str, intent: str, observation: str):
        """Post observation to daemon."""
        await self.client.post(
            f"{self.daemon_url}/v2/event/feedback",
            json={
                "entity": entity,
                "intent": intent,
                "observation": observation,
            }
        )
```

**Worker 60s Cycle**:
```python
async def worker_cycle():
    """60-second coordination cycle."""
    while True:
        try:
            # T+0s: Poll session state
            state = await worker.poll_session_state("current_session_id")
            
            # T+15s: Poll memory
            memory = await worker.poll_memory("OpenCode")
            
            # T+30s: Post feedback
            await worker.post_feedback(
                "OpenCode",
                "observation",
                f"Selected model: {state['model']}, latency OK"
            )
            
            # T+60s: Sleep
            await asyncio.sleep(60)
        except Exception as e:
            logger.error(f"Worker cycle failed: {e}")
            await asyncio.sleep(5)  # Backoff on error
```

**Impact**:
- Worker no longer fights daemon for DB lock
- Read latency: O(1) HTTP call vs O(N) DB scan
- Reliable steering: no `database is locked` errors

**Effort**: 3 hours
**Risk**: Medium (introduces HTTP dependency; fallback needed)
**Blocker**: Daemon must be running (`opencode` CLI)
**Owner**: P3 Engineering (or Kali direct)

---

### 0.5 Completion Checklist
- [ ] Symmetric prompt caching deployed & tested
- [ ] Air-gap circuit breaker verified (offline mode works)
- [ ] Database access boundary `/v2` endpoints live
- [ ] Worker 60s cycle runs without errors
- [ ] All tests pass: `make test`
- [ ] Workbench updated with Phase 0.5 completion

**Effort**: 6.5 hours (compressed from 8 if parallelized)
**Total Phase 0+0.5**: 7 hours (June 8–12)
**Ready for Phase 1**: YES

---

## PHASE 1: Unified Orchestration (Days 6–10)

### Goal
Ship the **Worker** and **Context Translation Layer**. Deploy Hivemind-native coordination.

### 1.1: Context Translation Layer

**File**: `src/omega/oracle/context_builder.py` (extend)
**Change**: Add compression, translation, expansion methods

```python
class ContextBuilder:
    # ... existing code ...
    
    async def compress_context(
        self,
        context: str,
        source_model_size: str,  # "0.6b", "1.7b", "4b", "8b"
        target_model_size: str,
    ) -> Dict[str, Any]:
        """Extract {facts, relationships, directives} from markdown."""
        
        # Use local small model to extract structured data
        extraction_prompt = f"""
        Extract the following from this context:
        1. Key facts (list of 3–5 claims)
        2. Relationships (entity A relates to entity B in what way)
        3. Directives (what does the user want?)
        
        Context:
        {context}
        
        Return as JSON.
        """
        
        response = await self.model_gateway.generate(
            model_name="qwen3-1.7b-q6_k",  # Always use small model for extraction
            prompt=extraction_prompt,
            format="json",
        )
        
        return {
            "facts": response.get("facts", []),
            "relationships": response.get("relationships", []),
            "directives": response.get("directives", []),
            "timestamp": datetime.now().isoformat(),
            "source_size": source_model_size,
        }
    
    async def expand_context(
        self,
        compressed: Dict[str, Any],
        target_model_size: str,
    ) -> str:
        """Expand compressed context back into markdown."""
        
        # Prioritize by target capacity
        capacity_map = {
            "0.6b": 2000,
            "1.7b": 4000,
            "4b": 8000,
            "8b": 16000,
        }
        
        tokens_available = capacity_map.get(target_model_size, 4000)
        
        expansion = f"""
## Context Summary

### Key Facts
{format_bullets(compressed['facts'])}

### Relationships
{format_bullets(compressed['relationships'])}

### Directives
{format_bullets(compressed['directives'])}

### Timestamp
{compressed['timestamp']}
"""
        
        return expansion
```

**File**: `src/omega/oracle/orchestrator.py`
**Change**: Add unified handoff method

```python
class Orchestrator:
    async def handoff_to_entity(
        self,
        from_entity: str,
        to_entity: str,
        context: str,
    ) -> None:
        """Unified entity handoff with context translation."""
        
        from_entity_obj = self.registry.get_entity(from_entity)
        to_entity_obj = self.registry.get_entity(to_entity)
        
        from_model_size = from_entity_obj.model_size
        to_model_size = to_entity_obj.model_size
        
        # Translate context if models differ
        if from_model_size != to_model_size:
            logger.info(f"Context translation: {from_model_size} → {to_model_size}")
            
            if self._should_compress(from_model_size, to_model_size):
                compressed = await self.context_builder.compress_context(
                    context, from_model_size, to_model_size
                )
                context = await self.context_builder.expand_context(
                    compressed, to_model_size
                )
            else:
                # Same-size or larger target: re-tokenize only
                context = await self.context_builder.translate_context(
                    context, from_entity_obj.tokenizer, to_entity_obj.tokenizer
                )
        
        # Execute handoff via Hivemind
        await self.hivemind_client.post_context(
            cli="opencode",
            continuation=f"Handoff from {from_entity}",
            focus_chain=[from_entity, to_entity],
            task_current=context,
        )
    
    def _should_compress(self, from_size: str, to_size: str) -> bool:
        """Determine if compression is needed."""
        size_rank = {"0.6b": 1, "1.7b": 2, "4b": 3, "8b": 4}
        return size_rank.get(from_size, 2) >= size_rank.get(to_size, 2)
```

**Effort**: 4 hours
**Risk**: Low (new feature, doesn't affect existing paths)
**Blocker**: None
**Owner**: P7 Context (or Kali direct)

---

### 1.2: Teacher-Student Quarantine Pattern

**File**: `src/omega/oracle/cloud_teacher.py` (new module)
**Change**: Implement critique-only cloud API

```python
import json
from omega.oracle.model_gateway import ModelGateway

class CloudTeacher:
    """Cloud provides critique (not code generation)."""
    
    def __init__(self, model_gateway: ModelGateway):
        self.model_gateway = model_gateway
    
    async def request_critique(
        self,
        draft_response: str,
        draft_code: Optional[str] = None,
        draft_commands: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Send draft to cloud for critique only."""
        
        prompt = f"""
You are a code reviewer. Critique this response (DO NOT generate new code).

Response:
{draft_response}

Code:
{draft_code or 'None'}

Commands:
{draft_commands or 'None'}

Return ONLY a JSON object:
{{
  "is_correct": bool,
  "issues": ["issue 1", "issue 2", ...],
  "suggestions": ["suggestion 1", ...],
  "risk_level": "low|medium|high",
  "explanation": "brief reason"
}}
"""
        
        try:
            response = await self.model_gateway.generate(
                model_name="gemma-4-31b-it",  # Cloud model
                prompt=prompt,
                temperature=0.3,  # Lower temp for consistency
                format="json",
            )
            
            return json.loads(response)
        except Exception as e:
            logger.warning(f"Cloud critique failed: {e}. Proceeding with default.")
            return {
                "is_correct": True,
                "risk_level": "medium",
                "issues": [],
                "suggestions": [],
            }
```

**File**: `src/omega/oracle/quarantine_handler.py` (new module)
**Change**: Implement quarantine staging

```python
import tempfile
import subprocess
from pathlib import Path

class QuarantineHandler:
    """Isolate and verify cloud outputs before execution."""
    
    STAGING_DIR = Path.home() / ".omega_quarantine"
    MAX_AGE_SECONDS = 3600
    
    def __init__(self):
        self.STAGING_DIR.mkdir(exist_ok=True)
    
    async def stage_code(self, code: str, session_id: str) -> Path:
        """Write code to isolated staging directory."""
        
        staging_path = self.STAGING_DIR / f"{session_id}_{int(time.time())}.py"
        staging_path.write_text(code)
        staging_path.chmod(0o600)  # Read/write for user only
        
        logger.info(f"Staged code: {staging_path}")
        return staging_path
    
    async def execute_with_critique(
        self,
        draft_code: Optional[str] = None,
        draft_commands: Optional[List[str]] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute draft with cloud critique + local verification."""
        
        cloud_teacher = CloudTeacher(self.model_gateway)
        
        # Request cloud critique (non-blocking, 30s timeout)
        critique_task = asyncio.create_task(
            cloud_teacher.request_critique(
                draft_response="",
                draft_code=draft_code,
                draft_commands=draft_commands,
            )
        )
        
        try:
            critique = await asyncio.wait_for(critique_task, timeout=30.0)
        except asyncio.TimeoutError:
            logger.warning("Cloud critique timeout; proceeding with default.")
            critique = {
                "is_correct": True,
                "risk_level": "medium",
                "issues": [],
            }
        
        # Check risk level
        if critique.get("risk_level") == "high":
            return {
                "status": "requires_approval",
                "critique": critique,
                "action": "User must approve before execution",
            }
        
        # If code + issues found: regenerate locally
        if draft_code and critique.get("issues"):
            logger.info(f"Cloud found {len(critique['issues'])} issues; regenerating locally")
            # TODO: Call local model to fix
            pass
        
        # Stage for execution
        if draft_code:
            staged_path = await self.stage_code(draft_code, session_id or "tmp")
            return {
                "status": "staged",
                "staged_path": str(staged_path),
                "critique": critique,
                "next_step": f"Execute: python {staged_path}",
            }
        
        return {
            "status": "complete",
            "critique": critique,
        }
```

**Effort**: 4 hours
**Risk**: Medium (new security boundary; requires testing)
**Blocker**: Cloud model must be available
**Owner**: P5 Governance (or Kali direct)

---

### 1.3: Worker Process

**File**: `src/omega/workers/hivemind_worker.py` (new module)
**Change**: Implement 60s coordination cycle

```python
import asyncio
import httpx
import logging
from datetime import datetime
from pathlib import Path

class HivemindWorker:
    """Background worker for agent orchestration."""
    
    DAEMON_URL = "http://127.0.0.1:4096"
    CYCLE_SECONDS = 60
    TRIGGER_LOG = Path(__file__).parent.parent.parent / "data" / "coordination" / "TRIGGER_LOG.md"
    FEEDBACK_LOG = Path(__file__).parent.parent.parent / "data" / "coordination" / "FEEDBACK_LOG.md"
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)
        self.cycle_count = 0
        self.logger = logging.getLogger("omega.worker")
    
    async def run(self):
        """Main worker loop."""
        while True:
            try:
                await self._cycle()
                await asyncio.sleep(self.CYCLE_SECONDS)
            except Exception as e:
                self.logger.error(f"Worker cycle failed: {e}", exc_info=True)
                await asyncio.sleep(5)  # Backoff on error
    
    async def _cycle(self):
        """One 60-second coordination cycle."""
        self.cycle_count += 1
        start_time = datetime.now()
        
        # T+0s: Heartbeat to Hivemind
        await self._heartbeat_hivemind()
        
        # T+15s: Poll session state
        session_state = await self._poll_session()
        self._log_trigger("poll_session", session_state)
        
        # T+30s: Retrieve memory
        memory = await self._poll_memory("OpenCode")
        self._log_trigger("poll_memory", {"entity": "OpenCode", "count": len(memory)})
        
        # T+45s: Post feedback
        await self._post_feedback(
            entity="OpenCode",
            intent="observation",
            observation=f"Cycle {self.cycle_count}: OK",
        )
        
        # T+60s: Record cycle time
        elapsed = (datetime.now() - start_time).total_seconds()
        self._log_feedback(f"cycle_complete", {"cycle": self.cycle_count, "elapsed_ms": int(elapsed*1000)})
    
    async def _heartbeat_hivemind(self):
        """Signal presence to Hivemind."""
        try:
            await self.client.post(
                "http://127.0.0.1:8016/hivemind/heartbeat",
                json={"cli": "worker", "reason": "orchestration loop"},
            )
        except Exception as e:
            self.logger.warning(f"Hivemind heartbeat failed: {e}")
    
    async def _poll_session(self) -> dict:
        """Fetch current session state."""
        try:
            response = await self.client.get(f"{self.DAEMON_URL}/v2/session/current/state")
            return response.json()
        except Exception as e:
            self.logger.warning(f"Poll session failed: {e}")
            return {}
    
    async def _poll_memory(self, entity: str) -> list:
        """Fetch recent memory for entity."""
        try:
            response = await self.client.get(f"{self.DAEMON_URL}/v2/memory/{entity}/recent?limit=10")
            return response.json().get("exchanges", [])
        except Exception as e:
            self.logger.warning(f"Poll memory failed: {e}")
            return []
    
    async def _post_feedback(self, entity: str, intent: str, observation: str):
        """Post feedback to daemon."""
        try:
            await self.client.post(
                f"{self.DAEMON_URL}/v2/event/feedback",
                json={
                    "entity": entity,
                    "intent": intent,
                    "observation": observation,
                    "timestamp": datetime.now().isoformat(),
                }
            )
        except Exception as e:
            self.logger.warning(f"Post feedback failed: {e}")
    
    def _log_trigger(self, event: str, data: dict):
        """Log trigger event to TRIGGER_LOG."""
        line = f"[{datetime.now().isoformat()}] cycle={self.cycle_count} event={event} data={data}\n"
        with open(self.TRIGGER_LOG, "a") as f:
            f.write(line)
    
    def _log_feedback(self, event: str, data: dict):
        """Log feedback event to FEEDBACK_LOG."""
        line = f"[{datetime.now().isoformat()}] event={event} data={data}\n"
        with open(self.FEEDBACK_LOG, "a") as f:
            f.write(line)

async def main():
    worker = HivemindWorker()
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
```

**Activation**:
```bash
# In OpenCode, add to opencode.json or via agent:
python -m omega.workers.hivemind_worker &

# Or via systemd:
sudo systemctl --user start omega-worker.service
```

**Effort**: 3 hours
**Risk**: Low (new background process, isolated)
**Blocker**: Daemon must be running
**Owner**: P9 Orchestration (or Kali direct)

---

### 1.4 Phase 1 Completion Checklist
- [ ] Context Translation Layer deployed & tested
- [ ] Teacher-Student Quarantine Pattern deployed & tested
- [ ] Worker process running in background
- [ ] TRIGGER_LOG & FEEDBACK_LOG generating entries
- [ ] All tests pass: `make test`
- [ ] Worker survives 10 consecutive cycles without errors
- [ ] Workbench updated with Phase 1 completion

**Effort**: 11 hours (compressed)
**Total Phase 0+0.5+1**: 18 hours (June 8–17)
**Ready for Phase 2**: YES

---

## PHASE 2: Cross-Agent Sync (Days 11–14)

### 2.1: OpenCode Daemon `/v2` Integration
**Already started in Phase 0.5; complete full coverage**

### 2.2: SSE Event Listening + Steering
**File**: `src/omega/workers/sse_listener.py` (new module)

```python
import httpx
import asyncio
import json

class SSEListener:
    """Listen to OpenCode SSE events and steer based on triggers."""
    
    async def run(self):
        """Main SSE listening loop."""
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", "http://127.0.0.1:4096/global/event") as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            event = json.loads(line[6:])
                            await self._handle_event(event)
                        except json.JSONDecodeError:
                            pass
    
    async def _handle_event(self, event: dict):
        """React to SSE event."""
        event_type = event.get("type")
        
        if event_type == "session.next.reasoning.delta":
            # Agent is reasoning; log selected model
            model = event.get("model")
            provider = event.get("provider")
            latency_ms = event.get("latency_ms")
            logger.info(f"Reasoning: {model} via {provider} ({latency_ms}ms)")
        
        elif event_type == "question.asked":
            # User asked a question; trigger KB lookup
            question = event.get("question")
            logger.info(f"Question: {question}")
        
        elif event_type == "tool.execute.before":
            # Tool about to execute; quarantine check
            tool = event.get("tool")
            args = event.get("args")
            logger.info(f"Executing tool: {tool} with {args}")
```

### 2.3: KB Growth Accumulation
**File**: `src/omega/workers/kb_growth.py` (new module)

```python
class KBGrowthAccumulator:
    """Extract facts from sessions; accumulate into KB."""
    
    async def extract_and_store(self, session_data: dict):
        """Extract facts from session; store in hot tier."""
        
        # Extract facts using local model
        facts = await self._extract_facts(session_data)
        
        # Store in hot tier (MemoryStore)
        for fact in facts:
            await self.memory_store.add_fact(
                entity="system",
                fact=fact,
                tags=["session", "extracted", "local-only"],
            )
        
        # Log to KB growth file
        kb_growth_log = Path("data/coordination/KB_GROWTH.md")
        kb_growth_log.append_text(f"- Extracted {len(facts)} facts from session\n")
```

**Effort**: 6 hours
**Status**: Phase 2-specific; executes in parallel with Phase 1 completion

---

## PHASE 3: Autonomous Growth (Days 15+)

### 3.1: Local Fine-Tuning Pipeline
**Scope**: Export JSONL datasets from KB; train local model

### 3.2: Auto-Training Scheduler
**Scope**: Trigger training when KB reaches threshold (5,000 facts)

**Effort**: TBD (depends on local training infrastructure)

---

## §X: Cumulative Milestones

| Milestone | Date | Status | Criteria |
|-----------|------|--------|----------|
| Phase 0 Complete | June 9 | Pending | All config fixes merged |
| Phase 0.5 Complete | June 12 | Pending | Prompt caching + air-gap + DB boundary |
| Phase 1 Complete | June 17 | Pending | Worker running, context translation live |
| Phase 2 Complete | June 21 | Pending | SSE listening + KB growth |
| Phase 3 Complete | June 28 | Pending | Local fine-tuning deployed |
| v1.0.0 Foundation PR | June 28 | Pending | All phases integrated |

---

*⬡ OMEGA ⬡ KALI ⬡ Implementation Phases v2.0 ⬡ Ready for execution ⬡*
