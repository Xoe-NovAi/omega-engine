<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# Gap R6: RHP (Recovery Halt Point) Schema — YAML Structure, resume_pointer Format, Corruption Handling

**AP Token:** `AP-RESEARCHER-R6-20260813-v1.0.0`
**Date:** 2026-08-13
**Researcher:** Sovereign Researcher (Jem Analyst L2)
**Priority:** P1 — Blocks QW-9
**Status:** RESEARCH COMPLETE

---

## 1. Executive Summary (L1)

The Recovery Halt Point (RHP) schema defines the structure for recovery operations after a system halt, including the resume_pointer format, YAML structure, and corruption handling mechanisms. The gap is in the **formal YAML schema definition**, the **resume_pointer data format**, and the **corruption detection and recovery procedures**. Existing research on checkpoint recovery, resume protocols, and the Armalo Cortex HWC tiered memory provides patterns, but no Omega-native RHP schema exists.

**Headline Finding:** The RHP schema must use atomic write patterns (`.tmp` → `fsync` → rename), include a content hash for integrity verification, and support resume_pointer formats for both in-memory hook recovery and DB-poll fallback. The schema must distinguish between soft halts (pausable) and hard halts (requiring manual intervention).

---

## 2. Authoritative Sources

| Source | URL | Date | Relevance |
|--------|-----|------|-----------|
| Checkpoint and state recovery runbook | https://www.cross-engine-reconciliation.org/streaming-reconciliation-pipelines/checkpoint-and-state-recovery/recovering-from-checkpoint-corruption/ | 2026-07-18 | Checkpoint integrity hashes, walk-back-replay recovery, idempotent sinks |
| Armalo Cortex HWC tiered memory | https://www.armalo.ai/labs/research/2026-04-10-cortex-tiered-memory-architecture | 2026-04-10 | Hot/Warm/Cold layers, cryptographic signing, Cold memory entries |
| Riskkernel exact-once resume | https://github.com/prashar32/riskkernel/pull/63 | 2026-04 | Mid-step crash recovery, exact-once budget counting, checkpoint rollback |
| OpenCode DB schema reference | `docs/research/R_OPENCODE_DB_SCHEMA_REFERENCE_20260810.md` | 2026-08-10 | `json_extract(data,'$.tokens.total')` query, message table structure |
| Checkpoint corruption recovery | https://github.com/agent-of-empires/agent-of-empires/pull/2623 | 2026-07 | Discriminant column, index on (session_id, discriminant, seq), self-healing schema |

---

## 3. Findings

### 3.1 RHP Schema Structure (YAML)

The RHP schema must be a YAML file with the following structure:

```yaml
# data/coordination/rhp/{session_id}/rhp.yaml
schema_version: "1.0"
session_id: "ses_20260813_153000"
halted_at: "2026-08-13T15:30:00Z"
halt_type: "soft"  # "soft" | "hard"
halt_reason: "optional human-readable reason"
halt_context_snapshot:
  tokens_total: 12450
  tokens_input: 8900
  tokens_output: 3550
  tokens_cache_read: 0
  tokens_cache_write: 0
  model_name: "qwen3-1.7b-free"
  provider: "native-gguf"
  current_turn: 7
  last_activity: "2026-08-13T15:29:52Z"
resume_pointer:
  type: "hook" | "db_poll" | "manual"
  value: "hook_id_or_db_query_or_manual_token"
  created_at: "2026-08-13T15:30:00Z"
integrity:
  data_hash: "sha256:abc123def456..."
  hash_algorithm: "sha256"
  verified_at: "2026-08-13T15:30:00Z"
  verification_status: "verified" | "corrupt" | "pending"
halt_status:
  status: "halted" | "resumed" | "completed" | "failed"
  resumed_at: null  # populated when resumed
  completed_at: null  # populated when completed
  failure_reason: null  # populated if failed
```

**Key fields:**

- `halt_type`: Distinguishes soft halts (pausable, can resume automatically) vs hard halts (require manual intervention, e.g., hardware failure, corruption detected)
- `resume_pointer`: Where to resume from — three types:
  - `hook`: In-memory hook state (real-time, for 80% pressure halt)
  - `db_poll`: Database-poll query (lags async writes, for fallback)
  - `manual`: Human intervention required
- `integrity`: Content hash for corruption detection
  - `data_hash`: SHA-256 of the full RHP file content (computed at write time)
  - `verified_at`: When hash was last verified
  - `verification_status`: `verified` (hash matches), `corrupt` (hash mismatch), `pending` (not yet verified)

### 3.2 resume_pointer Formats

**Type: `hook` (in-memory hook — real-time, for 80% pressure halt)**
```yaml
resume_pointer:
  type: "hook"
  value: "hook_qwen3-1.7b_turn_7_state"
  created_at: "2026-08-13T15:30:00Z"
```
- **Usage:** When the in-memory hook captures the model state at halt time
- **Advantage:** Real-time — no lag from async DB writes
- **Disadvantage:** Tied to process memory; lost on process restart (hence need db_poll fallback)
- **Format:** `hook_{model_name}_turn_{turn_number}_state`

**Type: `db_poll` (database-poll — lagging, for fallback)**
```yaml
resume_pointer:
  type: "db_poll"
  value: "SELECT tokens_total FROM message WHERE session_id = 'ses_...' ORDER BY time_created DESC LIMIT 1"
  created_at: "2026-08-13T15:30:00Z"
```
- **Usage:** When hook state is unavailable (process restart, crash) — falls back to DB poll
- **Advantage:** Persistent across process restarts; survives crashes
- **Disadvantage:** Lags async writes — the DB value may be behind real-time by N seconds/minutes
- **Format:** SQL query string that returns the latest state from the message table

**Type: `manual` (human intervention)**
```yaml
resume_pointer:
  type: "manual"
  value: "REVIEW REQUIRED: Investigate halt cause before resuming"
  created_at: "2026-08-13T15:30:00Z"
```
- **Usage:** When automated resumption is not safe (data corruption, hardware error, unknown state)
- **Advantage:** Safe — no automated resumption of potentially corrupted state
- **Disadvantage:** Requires human operator; halts progress until manually resolved

### 3.3 Corruption Handling

**Detection:**
- On RHP file read: compute SHA-256 of file content
- Compare to `data_hash` in `integrity` section
- If mismatch: `verification_status: "corrupt"`
- Log corruption event to `data/coordination/SYSTEM_FAILURE_LOG.md`

**Recovery procedures:**

1. **If verification_status == "verified":** Proceed with resumption using resume_pointer

2. **If verification_status == "corrupt":**
   - Walk back to last known clean checkpoint (per cross-engine reconciliation runbook)
   - Replay forward from clean checkpoint into idempotent sink
   - If no clean checkpoint exists: force full re-snapshot, mark halt as `failed`
   - Record in SYSTEM_FAILURE_LOG.md with epoch, corruption detected, recovery action

3. **If verification_status == "pending" (first read):**
   - Verify on first read (compute hash, compare to stored)
   - Update status to "verified" or "corrupt"
   - If corrupt: proceed with recovery procedure #2

**Atomic write pattern (per FM-04 / M12 Gnosis Preservation):**
```python
import hashlib
import os
import json

def write_rhp(rhp_data: dict, rhp_path: Path):
    """Write RHP file using atomic pattern."""
    # Serialize to JSON first
    content = json.dumps(rhp_data, sort_keys=True, separators=(",", ":"))
    
    # Compute SHA-256 hash
    data_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    
    # Add hash to integrity section
    rhp_data["integrity"] = {
        "data_hash": f"sha256:{data_hash}",
        "hash_algorithm": "sha256",
        "verified_at": datetime.utcnow().isoformat() + "Z",
        "verification_status": "pending"
    }
    rhp_data["halt_status"]["status"] = "halted"
    content = json.dumps(rhp_data, sort_keys=True, separators=(",", ":"))
    
    # Atomic write: .tmp → fsync → rename
    tmp_path = str(rhp_path) + ".tmp"
    with open(tmp_path, "w") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())  # Force disk sync
    
    os.rename(tmp_path, str(rhp_path))  # Atomic rename
    
    # Update verification status after successful write
    # (In practice, this would be done by a separate verification step)
```

### 3.4 Resumption Workflow

**Workflow 1: Normal resumption (hook state available)**

1. Read RHP file: `data/coordination/rhp/{session_id}/rhp.yaml`
2. Verify integrity: compute SHA-256, compare to `data_hash`
3. If verified: read `resume_pointer.type` and `resume_pointer.value`
4. If `type == "hook"`: restore in-memory hook state from `resume_pointer.value`
5. If `type == "db_poll"`: execute SQL query, restore state from DB result
6. If `type == "manual"`: halt with "REVIEW REQUIRED" message, wait for operator
7. Resume model inference from halted point
8. Update RHP: `halt_status.resumed_at = <timestamp>`, `halt_status.status = "resumed"`

**Workflow 2: Crash recovery (hook state lost, DB poll available)**

1. Read RHP file from last successful session
2. Verify integrity
3. If `resume_pointer.type == "hook"` but hook state unavailable:
   - Fall back to `resume_pointer.type == "db_poll"`
   - Execute DB poll query, restore state from latest message table row
4. If `resume_pointer.type == "db_poll"`: execute query, restore state
5. If no RHP file exists: perform DB poll as baseline (latest message row)
6. Resume model inference from recovered state
7. Update RHP: mark as recovered, log recovery action

**Workflow 3: Corruption recovery**

1. Read RHP file
2. Integrity check fails (SHA-256 mismatch)
3. Log corruption event
4. Walk back to last clean checkpoint (per cross-engine reconciliation runbook)
5. Replay forward from clean checkpoint into idempotent sink
6. If no clean checkpoint: force re-snapshot, mark halt as `failed`
7. Resume from recovered state
8. Update RHP: `halt_status.status = "failed"`, `failure_reason = "corruption from checkpoint N"`

### 3.5 Integration with Existing Systems

**Integration with ModelGateway (generate() method):**

The RHP schema integrates with the ModelGateway's `generate()` method to support mid-inference halts and resumption:

```python
def generate(self, ..., halt_on: Optional[SDPConstraintType] = None):
    """Generate with optional halt support."""
    rhp_path = f"data/coordination/rhp/{self.session_id}/rhp.yaml"
    
    # Check if RHP file exists from previous halt
    if os.path.exists(rhp_path):
        rhp_data = load_rhp(rhp_path)
        
        # Verify integrity
        if not verify_rhp_integrity(rhp_data):
            # Corruption recovery
            rhp_data = recover_from_corruption(rhp_path, self.session_id)
        
        # Check halt status
        if rhp_data["halt_status"]["status"] == "halted":
            # Check if we can auto-resume
            rhp_pointer = rhp_data["resume_pointer"]
            if rhp_pointer["type"] == "hook":
                # Restore hook state, resume inference
                restore_hook_state(rhp_pointer["value"])
                # Continue generation from halted point
                return continue_generation(...)
            elif rhp_pointer["type"] == "db_poll":
                # DB poll fallback
                state = db_poll_resume(rhp_pointer["value"])
                restore_state_from_db(state)
                return continue_generation(...)
            elif rhp_pointer["type"] == "manual":
                # Require operator intervention
                raise HaltRequiresOperatorIntervention(
                    "RHP halt requires manual review. "
                    "Run: omega resume --session {session_id}"
                )
    
    # Normal generation if no RHP or halt completed
    return self._generate_normal(...)
```

**Integration with AnyIO watchdog (per P0-P2 research):**

The RHP schema integrates with the AnyIO fail_after watchdog pattern:

```python
async def generate_with_watchdog(self, ...):
    """Generate with AnyIO watchdog for streaming timeouts."""
    chunk_timeout = self.config.extra.get("streaming", {}).get("chunk_timeout_ms", 30000) / 1000
    total_timeout = self.config.extra.get("streaming", {}).get("total_timeout_ms", 300000) / 1000
    
    # Outer watchdog: fail_after creates cancel scope at event loop level
    with anyio.fail_after(total_timeout):
        # ... streaming logic ...
        # On halt (e.g., user interrupt, timeout):
        #   Write RHP file with hook resume_pointer
        write_rhp({"halt_type": "soft", ...}, rhp_path)
        #   Halt inference, preserve state for resumption
        set_halt_state(...)
        #   Raise controlled exception (not hard crash)
        raise HaltRequest(...)
```

---

## 4. Recommendation

**Immediate (P1 — blocks QW-9):**

1. **Define the RHP YAML schema** as specified above, with all required fields
   - `schema_version`, `session_id`, `halted_at`, `halt_type`, `halt_reason`
   - `resume_pointer` with `type` (`hook`/`db_poll`/`manual`) and `value`
   - `integrity` with `data_hash`, `hash_algorithm`, `verified_at`, `verification_status`
   - `halt_status` with `status`, `resumed_at`, `completed_at`, `failure_reason`

2. **Implement atomic write pattern** for RHP files (`.tmp` → `fsync` → rename)
   - Per M12 (Gnosis Preservation) and FM-04
   - Include SHA-256 hash in integrity section
   - Verify on read, never trust unhashed RHP files

3. **Implement resume_pointer resolution** for all three types:
   - `hook`: Restore in-memory hook state (real-time, for 80% pressure halt per R32)
   - `db_poll`: Execute SQL query against message table, restore latest state
   - `manual`: Halt with "REVIEW REQUIRED", wait for operator intervention

4. **Implement integrity verification** on every RHP read:
   - Compute SHA-256 of file content
   - Compare to `data_hash` in integrity section
   - If mismatch: trigger corruption recovery (walk back to clean checkpoint, replay forward)
   - Log all corruption events to SYSTEM_FAILURE_LOG.md

5. **Integrate with ModelGateway.generate()** for mid-inference halt support:
   - On halt request: write RHP file with atomic pattern
   - On generate() start: check for existing RHP, verify integrity, resume if needed
   - Support all three resume_pointer types

**Near-term (P2):**

6. Integrate with the AnyIO watchdog pattern (per P0-P2 research C-2′):
   - On chunk timeout: write RHP with `halt_type: "soft"`, `resume_pointer.type: "hook"`
   - On total timeout: write RHP with `halt_type: "soft"`, `resume_pointer.type: "db_poll"` (fallback)
   - On operator interrupt: write RHP with `halt_type: "manual"`, `resume_pointer.type: "manual"`

7. Implement the corruption recovery walk-back/replay procedure:
   - Per cross-engine reconciliation runbook
   - Walk back to last clean checkpoint
   - Replay forward from clean checkpoint into idempotent sink
   - If no clean checkpoint: force re-snapshot

8. Add RHP schema validation to CI:
   - `make temple-grade` should validate RHP YAML files against schema
   - Pre-commit hook blocks commits with malformed RHP files
   - Test corruption scenarios (hash mismatch, missing fields, invalid types)

**Confidence:** **MEDIUM** that the RHP schema can be implemented in Omega. The patterns are proven (atomic writes, SHA-256 hashing, checkpoint recovery from the runbooks), and the YAML structure is well-defined. The main uncertainties are:

1. **Integration complexity**: How many call sites in ModelGateway need modification?
2. **Hook state management**: How are in-memory hook states serialized and restored?
3. **DB poll lag**: What's the acceptable lag between real-time state and DB-poll state for the 80% pressure halt scenario?

**Lower-bound confidence**: The RHP YAML schema, atomic write pattern, and integrity verification can be implemented with **HIGH** confidence, as these are proven patterns from the runbooks and the Armalo Cortex HWC research.

---

## 5. Confidence

**HIGH** that the RHP YAML schema, atomic write pattern, and integrity verification will work correctly. These are proven patterns from the cross-engine reconciliation runbook, the Armalo Cortex HWC research, and the Riskkernel exact-once resume PR. The adaptation to Omega is mechanical.

**MEDIUM** that the full integration (RHP → ModelGateway.generate() → AnyIO watchdog → resume_pointer resolution) will produce correct resumption behavior. The individual components are proven; the integration flow is the uncertainty.

---

## 6. Remaining Unknowns

1. **Hook state serialization**: How is the in-memory hook state serialized to the `resume_pointer.value` field? What data does the hook capture (model weights, KV cache, turn number, token counts)?

2. **DB poll lag measurement**: What is the actual lag between real-time model state and the latest row in the message table? This determines whether `db_poll` resume is viable for the 80% pressure halt scenario (R32).

3. **Concurrent RHP writes**: Can multiple inference requests write RHP files for the same session concurrently? What locking mechanism is needed?

4. **RHP retention policy**: How long should RHP files be retained after session completion? Should they be archived or deleted?

5. **Interaction with context compression (R2)**: When the model halts and resumes, does context compression still apply? How does the RHP state interact with the resolved context window from R2?

6. **Cross-session RHP**: Can an RHP from one session be used to resume in a different session? (Current design appears session-scoped, but may need cross-session design.)

---

## 7. Sources (Full)

| # | Source | Purpose |
|---|--------|---------|
| 1 | Cross-engine reconciliation runbook | Checkpoint integrity hashes, walk-back-replay recovery, idempotent sinks |
| 2 | Armalo Cortex HWC research | Cryptographic signing, Cold memory entries, tiered memory architecture |
| 3 | Riskkernel exact-once resume | Mid-step crash recovery, exact-once budget counting, checkpoint rollback |
| 4 | OpenCode DB schema reference | Message table structure, `json_extract(data,'$.tokens.total')` query pattern |
| 5 | Agent-of-empires discriminant index | Self-healing schema evolution, discriminant column, index on (session_id, discriminant, seq) |
| 6 | P0-P2 knowledge gap research | AnyIO fail_after watchdog pattern, httpx read timeout configuration |
| 7 | FM-04 / M12 mandates | Atomic write requirements, gnosis preservation |

---

## 8. Deliverable

**Report written to:** `data/entities/researcher/workspace/research_reports/R6_RHP_SCHEMA_20260813.md`

**Next action:** @lilith (dependent task owner) to implement RHP schema with resume_pointer format per QW-9 ticket.

---

*⬡ OMEGA ⬡ KALI ⬡ RESEARCH-EXEC ⬡ R6 ⬡ 20260813*