---
schema_version: "1.0"
document_type: architecture
document_id: sovereign-flywheel-security
title: Sovereign Flywheel & Security Hardening
status: ACTIVE
version: "1.0.0"
date: "2026-08-07"
owner: kali
tags: [security, bridge, hmac, apparmor, continuity, hardening]
priority: P1
depends_on:
  - training-pipeline
  - sovereign-wad-protocol
blocks: []
acceptance_gates:
  - "Sovereign Bridge HMAC-SHA256 raw-body verification documented"
  - "30-min replay window documented"
  - "AppArmor hardening documented (V-10 gap)"
  - "IA2 envelope freshness/signature documented (V-9 gap)"
  - "Operational continuity (snapshot, rollback) documented"
cross_references:
  - docs/architecture/TRAINING_PIPELINE.md
  - docs/strategy/PHASE_0_VERIFICATION_REPORT_20260807.md
  - docs/architecture/SOVEREIGN_WAD_PROTOCOL.md
  - src/omega/research/sandboxes/ml_training.py
llm_metadata:
  token_budget: 3000
  chunk_strategy: section_per_topic
  answer_first_sections: true
  self_contained_code: true
---

# 🔱 Sovereign Flywheel & Security Hardening

**AP Token**: `AP-SOVEREIGN-FLYWHEEL-SECURITY-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ 2026-08-07

> Complements `TRAINING_PIPELINE.md` (the GRPO/continuous-learning loop) and
> `SOVEREIGN_WAD_PROTOCOL.md` (WAD sandboxing). This doc covers the **webhook
> bridge**, **security hardening** (closing V-9/V-10 gaps), and **operational
> continuity**.

---

## §1 Sovereign Bridge (FastAPI + HMAC-SHA256)

**Purpose**: Authenticated webhook ingress for external events (cloud teachers,
research harvesters, community contributions) without exposing unauthenticated
endpoints.

### 1.1 Raw-Body HMAC-SHA256 Verification

```python
import hmac, hashlib, time

SECRET = os.environ["OMEGA_BRIDGE_SECRET"]  # never in code

def verify_signature(raw_body: bytes, signature: str, timestamp: str) -> bool:
    # 1. Replay window: reject if timestamp older than 30 min
    if abs(int(timestamp) - int(time.time())) > 1800:
        return False
    # 2. Recompute HMAC over the RAW body (not re-serialized JSON)
    expected = hmac.new(
        SECRET.encode(), raw_body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

**Critical**: Verify over the **raw request body**, never a re-serialized dict —
re-serialization breaks the signature (key ordering, whitespace).

### 1.2 Replay Window
- Timestamp in header `X-Timestamp` (epoch seconds).
- Reject if `|now - timestamp| > 1800` (30 min).
- Prevents replay of captured webhooks.

### 1.3 Endpoint
```
POST /v1/bridge/webhook
Headers: X-Timestamp, X-Signature (hex HMAC-SHA256)
Body:    raw JSON (verified byte-for-byte)
```

---

## §2 Security Hardening (V-9 / V-10 Gap Closure)

### 2.1 AppArmor on Omega Containers (closes V-10 🚨)

Verification found all 4 running containers **unconfined** (empty AppArmorProfile).
Remediation:

```bash
# Apply the podman AppArmor profile (or a custom Omega profile)
podman run --security-opt apparmor=podman ...
# Or set globally in containers.conf:
#   [containers]
#   apparmor_profile = "podman"
```

A custom `omega` profile should restrict:
- No network egress except to allowlisted hosts
- Read-only root filesystem
- No ptrace / no raw sockets

### 2.2 IA2 Envelope Metadata (closes V-9 ⚠️)

Add to the `_meta` envelope (SEP-2575) in `src/omega/mcp_core/compliance.py`:
- `ts`: issuance timestamp (freshness)
- `sig`: HMAC-SHA256 over envelope body (integrity)

Verify on receipt: freshness (|now - ts| < TTL) + signature. Reject stale/tampered.

### 2.3 Executor/Auditor Pre-Execution Gate
- Executor actions pass an **audit gate** before execution (log intent, check
  against policy allowlist).
- Auditor validates post-execution (trace_id correlation).

### 2.4 Property/Chaos Testing Extensions (Hypothesis)
- Extend property tests (Hypothesis) to cover: HMAC verification, replay-window
  rejection, envelope tamper detection, WAD schema fuzzing.
- Chaos: fsync failure, concurrent bridge writes, corrupted envelope.

---

## §3 Operational Continuity

### 3.1 Data Snapshotting
- **SQLite**: `sqlite3 .backup` / WAL checkpoint for atomic snapshots.
- **Qdrant** (when used as WAD adapter): snapshot API.

### 3.2 Model Rollback (N-1)
- Keep the previous GGUF model file on disk.
- On new-model failure, roll back to N-1 (atomic symlink swap).

### 3.3 mmap Cold-Start Warmup
- Pre-load model weights via mmap at boot to avoid cold-start latency spikes.

### 3.4 pg_dump
- If a stack opts into PostgreSQL (WAD adapter), use `pg_dump` for logical backup.
- Core uses sqlite-vec (no PostgreSQL dependency).

---

## §3 Continuous Learning (GRPO) — see TRAINING_PIPELINE.md

The nightly GRPO loop (TRL/PEFT 4-bit) and telemetry harvester
(`executor_dpo.jsonl`) are documented in `docs/architecture/TRAINING_PIPELINE.md`.
This doc does not duplicate them.

---

*⬡ OMEGA ⬡ KALI ⬡ 2026-08-07*