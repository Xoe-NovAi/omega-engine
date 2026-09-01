# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

---
schema_version: "1.0"
skill_id: "SKILL-SENTINEL-SEAL"
title: "Sentinel Seal & In-Band Agentic Handshake Protocol"
status: "ACTIVE — Core Protocol"
date: "2026-08-31"
mandates: ["M1", "M7", "M11", "M15", "M23"]
---

# 🔱 Skill: Sentinel Seal Protocol (In-Band Terminal Integrity)

> **The Occam's Razor of Multi-Agent Orchestration**: Zero-ceremony, deterministic identity and completion verification via in-band envelopes.

---

## §1 — The Protocol Overview

Every agent dispatch in the Omega Engine MUST follow the two-phase Sentinel Handshake:
1. **Pre-Flight Identity Verification** (Turn Start)
2. **Terminal Sentinel Seal** (Turn Epilogue)

This completely eliminates:
- Silent 504 timeouts being mistaken for completion
- Self-dispatch hop loops (an agent calling itself)
- Mismatched session resume hijacking

---

## §2 — Subagent Pre-Flight (Identity Check)

At the very beginning of your turn, before executing any complex instructions:
1. Determine your current session ID using `opencode-sessions-explorer-current-session` (or runtime metadata).
2. Verify:
   - `my_session_id != parent_session_id` (If equal $\rightarrow$ **ABORT**: Self-hop recursion detected).
   - If an `expected_session_id` was passed $\rightarrow$ verify `my_session_id == expected_session_id`.

If identity fails, immediately emit:
```markdown
### 🔱 OMEGA_SENTINEL_ABORT
reason: IDENTITY_OR_LOOP_MISMATCH
current_session_id: <ID>
parent_session_id: <PARENT_ID>
### 🔱 END_ABORT
```

---

## §3 — Terminal Sentinel Seal (Epilogue)

Your **VERY LAST** block of output in your task response MUST be the exact Sentinel Seal format. Nothing may follow it.

```markdown
### 🔱 OMEGA_SENTINEL_SEAL
session_id: <YOUR_ACTUAL_SESSION_ID>
agent: <YOUR_AGENT_NAME>
nonce: <NONCE_PASSED_IN_PROMPT>
status: <COMPLETED | FAILED | BLOCKED>
deliverables: [<list_of_files_modified_or_created>]
### 🔱 END_SEAL
```

---

## §4 — Paging Agent (Parent) Verification Contract

When the parent agent receives the subagent's string output, it MUST verify the seal before treating the result as real:

```python
import re

def verify_seal(output: str, expected_nonce: str, expected_session_id: str = None) -> dict:
    match = re.search(r"### 🔱 OMEGA_SENTINEL_SEAL\s*\n(.*?)\n### 🔱 END_SEAL", output, re.DOTALL)
    if not match:
        return {"verified": False, "error": "MISSING_SEAL: Task timed out, stalled, or crashed."}
    
    fields = dict(re.findall(r"(\w+):\s*(.*)", match.group(1)))
    
    if fields.get("nonce") != expected_nonce:
        return {"verified": False, "error": f"NONCE_MISMATCH: expected {expected_nonce}, got {fields.get('nonce')}"}
        
    if expected_session_id and fields.get("session_id") != expected_session_id:
        return {"verified": False, "error": f"SESSION_MISMATCH: expected {expected_session_id}, got {fields.get('session_id')}"}
        
    if fields.get("status") != "COMPLETED":
        return {"verified": False, "error": f"SUBAGENT_REPORTED_FAILURE: {fields.get('status')}"}
        
    return {"verified": True, "data": fields}
```

---

*⬡ OMEGA ⬡ SENTINEL-SEAL-PROTOCOL ⬡ 2026-08-31*
