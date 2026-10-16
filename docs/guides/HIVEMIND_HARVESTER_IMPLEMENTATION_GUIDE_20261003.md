<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# Hivemind Harvester — Autonomous Implementation Guide
**Document ID**: `GUIDE-HIVEMIND-HARVESTER-v1.0.0`  
**AP Token**: `AP-HARVESTER-IMPL-v1.0.0`  
**Target Implementer**: Autonomous Coding Agent (Nemotron 3 Ultra, Claude, GPT-4o, etc.)  
**Date**: 2026-10-03  
**Status**: `RATIFIED ARCHITECTURAL SPECIFICATION`  
**Reference Design**: `docs/architecture/HIVEMIND_HARVESTER_DESIGN_20261003.md`

---

## 🎯 Objective for the Implementer

You are tasked with implementing the **Hivemind Harvester**, an ultra-low-cost, zero-inference background aggregation service for the Omega Engine fleet.

### The Problem It Solves
Currently, when an agent or subagent wakes up (especially after context compaction or inside a paged subagent environment), determining "what is the rest of the fleet doing?" requires fanning out across multiple MCP tool calls and parsing dozens of session files. This is slow, expensive, and fails completely in environments where MCP tools are unavailable.

### The Solution
1. Agents optionally provide a micro-summary (`digest`) when calling `hivemind_awareness(action="post")`.
2. A background harvester runs every 300 seconds, performs **pure string concatenation** (zero LLM, zero GPU, $O(\text{agents})$), and publishes:
   - `data/coordination/hivemind_overview/latest.json` (Machine readable)
   - `data/coordination/hivemind_overview/latest.md` (Human/agent terminal readable via `cat`)
3. Any agent gets the complete, up-to-the-minute fleet context in **1 millisecond / 1 file read** at virtually zero token cost.

---

## 🛡️ Non-Negotiable Invariants & Guardrails

| Mandate | Requirement | Enforcement Check |
|:---|:---|:---|
| **M1 AnyIO** | **NEVER** use `import asyncio` in `mcp_servers/omega_hub/`. Use `anyio` for async sleep, tasks, file I/O, or run synchronous code via `anyio.to_thread.run_sync`. | `make check-m1-anyio` |
| **M2 Firewall** | **Zero code in `src/omega/`**. All components belong in `mcp_servers/omega_hub/`, `scripts/`, or `tests/`. | `git diff --name-only \| grep src/omega` must be empty |
| **M7 Local-First** | **Zero inference**. Never call an LLM, embeddings, or cloud API. All aggregation is pure string and JSON manipulation. | `generator.llm_used: false` asserted in output |
| **M8 Zero Telemetry** | Local files only. Never send data over external networks. | No network sockets opened outside localhost |
| **M15 Continuity** | Overview must be stable, atomic, and greppable. A fresh boot or compacted agent can read it immediately. | Atomic write via `.tmp` → rename with fsync |
| **M23 Failure Integrity** | Never guess or hallucinate missing data. Broken reads produce explicit `⚠️ GAP` markers. Total failure refuses to overwrite `latest`. | `status: STALE_PARTIAL` on partial failure; non-zero exit on fatal error |
| **M28 Preservation** | Never delete history files. Hot history (288 cycles) moves to `archive/<YYYY-MM>/` with an append-only manifest entry. | No `os.unlink()` or `rmtree()` on history |

---

## 🏛️ The 5 Frontier Enhancements to Implement

1. **Triple-Tier Temporal Heartbeat**:
   - `🟢 ACTIVE`: `generated_at - post.timestamp <= 600s` (10 min).
   - `🟡 IDLE / STANDBY`: `600s < age <= 2700s` (10–45 min).
   - `⚪ EXTENDED`: Active `extended_checkin` TTL present.
   - `⚫ EXPIRED`: Past 45-min TTL (shown in historical section).

2. **Sovereign Seat (EIS) vs. Task Fleet (NES) Partitioning**:
   - Separate standing council seats (parent_id is null / root entity sessions) from ephemeral subagent dispatches (`task_*` or parent_id not null).
   - Ensures background worker noise never buries strategic council governance.

3. **3-Line Triage Radar Header**:
   - Top 3 lines of `latest.md` must display:
     ```markdown
     # ⬡ HIVEMIND FLEET RADAR — <TIMESTAMP_UTC> [<STATUS>]
     🔴 <N> BLOCKERS | ⚡ <N> PENDING HANDOFFS | 🟢 <N> AGENTS ACTIVE
     🚨 BLOCKERS: @<entity>: "<summary>"
     ```

4. **Micro-Structured Wire Parsing**:
   - Format: `DOING <task> · NEXT <next> [· BLOCKER <blocker>]`.
   - Parse via non-failing regex into structured keys (`doing`, `next`, `blocker`) in `latest.json` while retaining the raw string.

5. **Atomic Non-Blocking Lock Guard**:
   - Acquire non-blocking file lock on `data/coordination/hivemind_overview/.harvester.lock`.
   - If locked, yield immediately (skip cycle) to prevent concurrent torn reads.

---

## 📂 File Modification Blueprint

You will modify or create exactly 5 files:

```
├── mcp_servers/omega_hub/
│   ├── hub_tools/tools.py          <-- [MODIFY] Add `digest` param & `action="overview"`
│   └── background.py               <-- [MODIFY] Add periodic 300s harvester loop
├── scripts/
│   ├── hivemind_harvest.py         <-- [CREATE] Core harvesting engine script
│   └── hivemind_overview.py        <-- [CREATE] Standalone CLI reader for no-MCP agents
└── tests/
    └── test_hivemind_harvester.py  <-- [CREATE] Full test suite
```

---

## 🔧 Detailed Step-by-Step Implementation Instructions

### Step 1: Update MCP Hub Tool (`mcp_servers/omega_hub/hub_tools/tools.py`)

#### 1.1 Accept `digest` in `action="post"`
Locate the `hivemind_awareness` function in `tools.py` (around line 2357).
1. Add `digest: Optional[str] = None` to the function parameters.
2. In the parameter docstring, document:
   ```python
   digest: Optional micro-summary (≤280 chars) in format 'DOING <task> · NEXT <next> · BLOCKER <blocker>'
   ```
3. Inside `action == "post"`:
   - Validate and normalize `digest`:
     ```python
     normalized_digest = None
     digest_truncated = False
     if digest is not None:
         # Collapse whitespace, strip
         clean_digest = " ".join(str(digest).split()).strip()
         if len(clean_digest) > 280:
             normalized_digest = clean_digest[:277] + "…"
             digest_truncated = True
         else:
             normalized_digest = clean_digest
     ```
   - Store `normalized_digest` in the snapshot dict:
     ```python
     snapshot["digest"] = normalized_digest
     ```
   - If `digest_truncated` is true, include `"digest_truncated": True` in the successful return dictionary.

#### 1.2 Add `action="overview"`
Inside `hivemind_awareness`:
1. Add support for `action == "overview"`:
   ```python
   if action == "overview":
       overview_dir = Path(repo_root) / "data" / "coordination" / "hivemind_overview"
       latest_json_path = overview_dir / "latest.json"
       latest_md_path = overview_dir / "latest.md"
       
       # Optional format override: format="json" (default) or format="md"
       req_format = kwargs.get("format", "json")
       
       if not latest_json_path.exists():
           return json.dumps({
               "status": "UNINITIALIZED",
               "message": "Hivemind overview has not run yet. Run scripts/hivemind_harvest.py or wait for cycle.",
               "rows": []
           })
           
       try:
           if req_format == "md":
               content = latest_md_path.read_text(encoding="utf-8")
               return content
           else:
               content = json.loads(latest_json_path.read_text(encoding="utf-8"))
               return json.dumps(content)
       except Exception as e:
           return json.dumps({
               "status": "ERROR",
               "error": f"Failed to read hivemind overview: {e}"
           })
   ```

---

### Step 2: Implement Core Harvester (`scripts/hivemind_harvest.py`)

Create `scripts/hivemind_harvest.py` executable (`chmod +x`).

#### Required Structure:
```python
#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
# SPDX-License-Identifier: Apache-2.0

"""
Hivemind Harvester — Zero-Inference Fleet Aggregator.
Runs every 300s to produce latest.json and latest.md.
"""

import sys
import os
import fcntl
import json
import re
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Invariant: Must not import asyncio
# Invariant: Must run locally in repo context

def get_repo_root() -> Path:
    # Resolve relative to scripts/
    return Path(__file__).resolve().parent.parent

def parse_micro_digest(raw_digest: str, task_current: str, continuation: str) -> dict:
    """Extract DOING, NEXT, BLOCKER using robust regex."""
    if not raw_digest:
        doing = (task_current[:120] if task_current else "").strip()
        next_step = (continuation[:100] if continuation else "").strip()
        return {
            "doing": doing,
            "next": next_step,
            "blocker": None,
            "source": "fallback"
        }
    
    # Regex parse for DOING ... · NEXT ... [· BLOCKER ...]
    doing_match = re.search(r'DOING\s+([^·]+)', raw_digest, re.IGNORECASE)
    next_match = re.search(r'NEXT\s+([^·]+)', raw_digest, re.IGNORECASE)
    blocker_match = re.search(r'BLOCKER\s+(.+)', raw_digest, re.IGNORECASE)
    
    doing = doing_match.group(1).strip() if doing_match else raw_digest[:120].strip()
    next_step = next_match.group(1).strip() if next_match else ""
    blocker = blocker_match.group(1).strip() if blocker_match else None
    
    if blocker and blocker.lower() in ("none", "none.", "nil", "n/a", "no"):
        blocker = None
        
    return {
        "doing": doing,
        "next": next_step,
        "blocker": blocker,
        "source": "digest"
    }

def calculate_heartbeat_tier(post_ts_iso: str, now: datetime, extended_ttl: int = 0) -> str:
    try:
        # Handle trailing Z or offsets
        ts_clean = post_ts_iso.replace("Z", "+00:00")
        post_time = datetime.fromisoformat(ts_clean)
        age_s = (now - post_time).total_seconds()
        
        if extended_ttl and age_s <= extended_ttl:
            return "⚪ EXTENDED"
        if age_s <= 600:
            return "🟢 ACTIVE"
        elif age_s <= 2700:
            return "🟡 IDLE"
        else:
            return "⚫ EXPIRED"
    except Exception:
        return "🟡 UNKNOWN"

def harvest_once() -> int:
    repo_root = get_repo_root()
    coord_dir = repo_root / "data" / "coordination"
    out_dir = coord_dir / "hivemind_overview"
    out_dir.mkdir(parents=True, exist_ok=True)
    history_dir = out_dir / "history"
    history_dir.mkdir(parents=True, exist_ok=True)
    archive_dir = out_dir / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    lock_file = out_dir / ".harvester.lock"
    
    # 1. Non-blocking lock (Enhancement 5)
    with open(lock_file, "w") as lock_fd:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (BlockingIOError, IOError):
            # Cleanly yield if another harvester is running
            return 0
        
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        
        # 2. Gather inputs: Hot store + Hall of Records
        # Attempt to read data/coordination/metrics.json or handoffs for quick stats
        handoffs_pending_dir = repo_root / "data" / "handoff" / "pending"
        pending_handoff_count = len(list(handoffs_pending_dir.glob("ho_*.json"))) if handoffs_pending_dir.exists() else 0
        
        # Collect raw records
        raw_sessions = {}
        gaps = []
        
        # Cold store traversal (bounded glob)
        records_dir = repo_root / "data" / "knowledge" / "HALL_OF_RECORDS"
        if records_dir.exists():
            for agent_folder in records_dir.iterdir():
                if not agent_folder.is_dir():
                    continue
                for session_file in agent_folder.glob("ses_*.json"):
                    try:
                        data = json.loads(session_file.read_text(encoding="utf-8"))
                        sid = data.get("session_id")
                        if sid:
                            raw_sessions[sid] = data
                    except Exception as e:
                        gaps.append({
                            "session_id": session_file.stem,
                            "reason": f"Corrupt JSON in cold store: {e}"
                        })
        
        # In addition, scan active sessions in data/coordination/ if any
        # (Or query hub state if running in-process)
        
        # 3. Partition into EIS (Sovereign Seats) vs NES (Task Fleet) (Enhancement 2)
        sovereign_rows = []
        task_rows = []
        blockers = []
        active_count = 0
        
        SOVEREIGN_ENTITIES = {"kali", "maat", "lilith", "doom_guy", "john_carmack", "roc_racoon", "researcher", "verity", "antigravity"}
        
        for sid, sess in raw_sessions.items():
            entity = sess.get("entity", "unknown")
            ts = sess.get("timestamp", now_iso)
            raw_dig = sess.get("digest")
            task_cur = sess.get("task_current", "")
            contin = sess.get("continuation", "")
            
            parsed = parse_micro_digest(raw_dig, task_cur, contin)
            tier = calculate_heartbeat_tier(ts, now)
            
            if tier in ("🟢 ACTIVE", "⚪ EXTENDED"):
                active_count += 1
                
            is_blocker = (sess.get("intent") == "blocker") or (parsed["blocker"] is not None)
            if is_blocker and tier != "⚫ EXPIRED":
                blockers.append({
                    "entity": entity,
                    "session_id": sid,
                    "blocker": parsed["blocker"] or task_cur[:140]
                })
                
            row = {
                "entity": entity,
                "session_id": sid,
                "tier": tier,
                "channel": sess.get("channel", "opencode"),
                "model": sess.get("model", "unknown"),
                "intent": sess.get("intent", "status"),
                "timestamp": ts,
                "digest": raw_dig or f"[no-digest] {parsed['doing']} | {parsed['next']}",
                "digest_parsed": parsed
            }
            
            # Identify EIS vs NES:
            # If parent_id is present or task_id format -> NES (Task Fleet)
            if sess.get("parent_id") or "task" in sid.lower() or entity not in SOVEREIGN_ENTITIES:
                task_rows.append(row)
            else:
                sovereign_rows.append(row)
        
        # Sort rows: newest first within each section
        sovereign_rows.sort(key=lambda r: r["timestamp"], reverse=True)
        task_rows.sort(key=lambda r: r["timestamp"], reverse=True)
        
        status = "FRESH" if not gaps else "STALE_PARTIAL"
        
        # 4. Build latest.json
        payload_json = {
            "schema": "hivemind-overview/v1",
            "generated_at": now_iso,
            "interval_s": 300,
            "status": status,
            "radar": {
                "blocker_count": len(blockers),
                "pending_handoff_count": pending_handoff_count,
                "active_agents_count": active_count
            },
            "blockers": blockers,
            "sovereign_fleet": sovereign_rows,
            "task_fleet": task_rows,
            "gaps": gaps,
            "generator": {"kind": "concatenation-only", "llm_used": False}
        }
        
        # 5. Build latest.md with 3-Line Triage Radar (Enhancements 1, 2, 3)
        md_lines = []
        md_lines.append(f"# ⬡ HIVEMIND FLEET RADAR — {now_iso} [{status}]")
        md_lines.append(f"🔴 {len(blockers)} BLOCKERS | ⚡ {pending_handoff_count} PENDING HANDOFFS | 🟢 {active_count} AGENTS ACTIVE")
        if blockers:
            for b in blockers:
                md_lines.append(f"🚨 BLOCKER: @{b['entity']} ({b['session_id'][:12]}): {b['blocker']}")
        else:
            md_lines.append("✨ FLEET STATUS: All operational · No active blockers reported.")
        md_lines.append("")
        
        md_lines.append("## 🏛️ Sovereign Fleet (Standing Seats / EIS)")
        if sovereign_rows:
            for r in sovereign_rows:
                md_lines.append(f"- **{r['tier']}** `@{r['entity']}` [{r['channel']}/{r['model']}] — *{r['digest']}*")
        else:
            md_lines.append("_No active sovereign seats recorded._")
        md_lines.append("")
        
        md_lines.append("## ⚡ Task Fleet (Subagent Dispatches / NES)")
        if task_rows:
            for r in task_rows[:20]:  # Cap task fleet display at 20 to prevent bloat
                md_lines.append(f"- **{r['tier']}** `@{r['entity']}` (`{r['session_id'][:12]}`) — {r['digest']}")
        else:
            md_lines.append("_No active task subagents._")
        md_lines.append("")
        
        if gaps:
            md_lines.append("## ⚠️ Gaps & Unreadable Shards")
            for g in gaps:
                md_lines.append(f"- ⚠️ GAP: `{g['session_id']}` — {g['reason']}")
            md_lines.append("")
            
        md_lines.append("_Footer: Pure zero-inference concatenation (M7). Store is truth; overview is projection._")
        payload_md = "\n".join(md_lines) + "\n"
        
        # 6. Atomic Write via .tmp files
        tmp_json = out_dir / "latest.json.tmp"
        tmp_md = out_dir / "latest.md.tmp"
        
        tmp_json.write_text(json.dumps(payload_json, indent=2), encoding="utf-8")
        tmp_md.write_text(payload_md, encoding="utf-8")
        
        tmp_json.replace(out_dir / "latest.json")
        tmp_md.replace(out_dir / "latest.md")
        
        # If fresh, update latest_good
        if status == "FRESH":
            shutil.copyfile(out_dir / "latest.json", out_dir / "latest_good.json")
            shutil.copyfile(out_dir / "latest.md", out_dir / "latest_good.md")
            
        # Write history record
        timestamp_slug = now.strftime("%Y%m%dT%H%M%SZ")
        history_file = history_dir / f"ov_{timestamp_slug}.json"
        history_file.write_text(json.dumps(payload_json), encoding="utf-8")
        
        # 7. M28 Retention: Keep 288 cycles in history/, move older to archive/<YYYY-MM>/
        history_files = sorted(history_dir.glob("ov_*.json"))
        if len(history_files) > 288:
            excess = history_files[:-288]
            month_str = now.strftime("%Y-%m")
            month_archive = archive_dir / month_str
            month_archive.mkdir(exist_ok=True)
            manifest_file = archive_dir / "MANIFEST.jsonl"
            
            with open(manifest_file, "a", encoding="utf-8") as mf:
                for old_f in excess:
                    dest = month_archive / old_f.name
                    old_f.rename(dest)
                    manifest_record = {
                        "file": old_f.name,
                        "archived_at": now_iso,
                        "destination": str(dest.relative_to(out_dir))
                    }
                    mf.write(json.dumps(manifest_record) + "\n")
                    
        return 0

if __name__ == "__main__":
    sys.exit(harvest_once())
```

---

### Step 3: Wire Harvester into Background Loop (`mcp_servers/omega_hub/background.py`)

1. Open `mcp_servers/omega_hub/background.py`.
2. Inspect the existing background tasks (reaper loop, etc.).
3. Add a periodic harvest coroutine:
   ```python
   # Invariant: Must use anyio, NEVER asyncio
   import anyio
   from scripts.hivemind_harvest import harvest_once

   async def run_harvester_loop():
       """Background coroutine running the zero-inference harvester every 300s ± jitter."""
       # Initial short delay for clean server startup
       await anyio.sleep(5)
       while True:
           try:
               # Run blocking filesystem harvest in AnyIO worker thread
               await anyio.to_thread.run_sync(harvest_once)
           except Exception as exc:
               # Fail-safe: background task must not crash the hub
               logger.warning(f"Hivemind harvester cycle encountered error: {exc}")
               
           # Sleep 300s (with small ±15s deterministic jitter if desired)
           await anyio.sleep(300)
   ```
4. Start this task inside the hub's main AnyIO task group where background loops are initialized.

---

### Step 4: Standalone Reader CLI (`scripts/hivemind_overview.py`)

Create `scripts/hivemind_overview.py` (chmod +x) for agents without MCP tools:

```python
#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
# SPDX-License-Identifier: Apache-2.0

"""
CLI Reader for Hivemind Overview.
Usable by subagents and terminal operators without MCP access.
"""

import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Read Hivemind Fleet Overview")
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Output format")
    parser.add_argument("--radar-only", action="store_true", help="Print only top 3 radar lines")
    args = parser.parse_args()
    
    repo_root = Path(__file__).resolve().parent.parent
    overview_dir = repo_root / "data" / "coordination" / "hivemind_overview"
    target_file = overview_dir / ("latest.md" if args.format == "md" else "latest.json")
    
    if not target_file.exists():
        print("⚠️ Hivemind Overview not available yet. (latest file missing)")
        sys.exit(1)
        
    content = target_file.read_text(encoding="utf-8")
    
    if args.radar_only and args.format == "md":
        lines = content.strip().split("\n")
        print("\n".join(lines[:3]))
    else:
        print(content)
        
    sys.exit(0)

if __name__ == "__main__":
    main()
```

---

### Step 5: Test Suite (`tests/test_hivemind_harvester.py`)

Create comprehensive test suite verifying all 5 enhancements and mandates:

```python
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
# SPDX-License-Identifier: Apache-2.0

import pytest
import json
from pathlib import Path
from scripts.hivemind_harvest import parse_micro_digest, calculate_heartbeat_tier, harvest_once

def test_parse_micro_digest_full():
    raw = "DOING allowlist scrub · NEXT test gates · BLOCKER none"
    parsed = parse_micro_digest(raw, "", "")
    assert parsed["doing"] == "allowlist scrub"
    assert parsed["next"] == "test gates"
    assert parsed["blocker"] is None
    assert parsed["source"] == "digest"

def test_parse_micro_digest_with_real_blocker():
    raw = "DOING cgroup check · NEXT reboot · BLOCKER kernel panic on N1"
    parsed = parse_micro_digest(raw, "", "")
    assert parsed["doing"] == "cgroup check"
    assert parsed["blocker"] == "kernel panic on N1"

def test_parse_micro_digest_fallback():
    parsed = parse_micro_digest(None, "Running tests across modules", "Continue to next step")
    assert "Running tests" in parsed["doing"]
    assert "Continue" in parsed["next"]
    assert parsed["source"] == "fallback"

def test_heartbeat_tier():
    from datetime import datetime, timezone, timedelta
    now = datetime.now(timezone.utc)
    
    active_ts = (now - timedelta(minutes=5)).isoformat()
    assert calculate_heartbeat_tier(active_ts, now) == "🟢 ACTIVE"
    
    idle_ts = (now - timedelta(minutes=20)).isoformat()
    assert calculate_heartbeat_tier(idle_ts, now) == "🟡 IDLE"
    
    expired_ts = (now - timedelta(minutes=50)).isoformat()
    assert calculate_heartbeat_tier(expired_ts, now) == "⚫ EXPIRED"

def test_harvest_execution_produces_artifacts(tmp_path, monkeypatch):
    # Ensure harvest_once runs cleanly and writes latest.md and latest.json
    res = harvest_once()
    assert res == 0
    
    repo_root = Path(__file__).resolve().parent.parent
    overview_dir = repo_root / "data" / "coordination" / "hivemind_overview"
    assert (overview_dir / "latest.json").exists()
    assert (overview_dir / "latest.md").exists()
    
    data = json.loads((overview_dir / "latest.json").read_text())
    assert data["generator"]["llm_used"] is False
    assert "radar" in data
```

---

## 🚦 Final Verification Checklist

After implementing the above steps, run these commands to verify readiness:

1. **Verify M1 AnyIO Compliance**:
   ```bash
   make check-m1-anyio
   ```
   *(Must exit 0. No `import asyncio` permitted in `mcp_servers/omega_hub/`)*

2. **Run Harvester Test Suite**:
   ```bash
   .venv/bin/pytest tests/test_hivemind_harvester.py -v
   ```

3. **Verify Manual Script Execution**:
   ```bash
   python3 scripts/hivemind_harvest.py
   python3 scripts/hivemind_overview.py --radar-only
   ```

4. **Verify Temple-Grade Gates**:
   ```bash
   make temple-grade
   ```
   *(Must report `TOTAL: 53 PASS: 53 FAIL: 0`)*

---

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ HIVEMIND-HARVESTER-IMPL-GUIDE-v1.0.0 ⬡ 2026-10-03 ⬡*
