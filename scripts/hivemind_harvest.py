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


def load_control_plane():
    """Load the control plane read-only, or return None.

    DEFENSIVE BY DESIGN. The harvester must keep producing a fleet overview even
    if the control plane is missing or broken — a dead radar is worse than a
    radar that admits it is blind. When this returns None the caller publishes
    `control_plane_ok: false` rather than fabricating zero kills.

    M23: a degraded-but-honest projection beats a synthesized one.
    """
    try:
        repo_root = get_repo_root()
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))
        from mcp_servers.omega_hub import control_plane as cp
        return cp
    except Exception as e:  # noqa: BLE001
        print(f"[harvest] control plane unavailable: {e}", file=sys.stderr)
        return None


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

        # ── CONTROL PLANE (P1-1) ────────────────────────────────────────────
        # Four planes: kill / escalate / approve / throttle. The radar surfaces
        # the two that change what an operator must do next: how many sessions
        # are halted, and how many destructive ops are waiting on a human.
        cp = load_control_plane()
        killed_ids: set = set()
        control_radar = {"control_plane_ok": False, "killed_count": None,
                         "pending_approvals": None}
        if cp is not None:
            try:
                control_radar = cp.radar_block()
                if control_radar.get("control_plane_ok"):
                    killed_ids = cp.killed_session_ids()
                else:
                    gaps.append({
                        "session_id": "control_plane",
                        "reason": f"control plane unreadable: "
                                  f"{control_radar.get('control_plane_error')}",
                    })
            except Exception as e:
                control_radar = {"control_plane_ok": False, "killed_count": None,
                                 "pending_approvals": None,
                                 "control_plane_error": str(e)}
                gaps.append({"session_id": "control_plane",
                             "reason": f"control plane read failed: {e}"})
        
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

            # A killed session is not ACTIVE, IDLE, or EXPIRED — it was halted
            # on purpose. The kill tier wins over the heartbeat tier so a halted
            # agent never reads as merely idle.
            is_killed = sid in killed_ids
            if is_killed:
                tier = "🔴 KILLED"
            elif tier in ("🟢 ACTIVE", "⚪ EXTENDED"):
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
                "digest_parsed": parsed,
                "killed": is_killed,
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
                "active_agents_count": active_count,
                # ── Control plane (P1-1) ──
                # null (not 0) when the control plane is unreadable: an
                # unreadable store is not an all-clear (M23).
                "killed_count": control_radar.get("killed_count"),
                "pending_approvals": control_radar.get("pending_approvals"),
                "throttled_entities": control_radar.get("throttled_entities"),
                "control_plane_ok": control_radar.get("control_plane_ok", False),
                "enforced_planes": control_radar.get("enforced_planes", []),
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
        # ── 3-LINE TRIAGE RADAR (control plane appended) ──
        killed_n = control_radar.get("killed_count")
        pending_appr = control_radar.get("pending_approvals")
        # "?" not "0": a blind radar must not claim zero kills.
        killed_s = "?" if killed_n is None else str(killed_n)
        appr_s = "?" if pending_appr is None else str(pending_appr)
        md_lines.append(f"🔴 {len(blockers)} BLOCKERS | ⚡ {pending_handoff_count} PENDING HANDOFFS | 🟢 {active_count} AGENTS ACTIVE")
        md_lines.append(f"☠️ {killed_s} KILLED | ⏳ {appr_s} PENDING APPROVALS"
                        + ("" if control_radar.get("control_plane_ok") else " | ⚠️ CONTROL PLANE UNREADABLE"))
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