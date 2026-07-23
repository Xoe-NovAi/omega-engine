"""
Scribe Hub Master — Main Event Loop
Reads Hivemind broadcasts, parses them, and updates HMC_COLLABORATION_HUB.md
"""
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# Omega Hub MCP tools (available at runtime)
try:
    from omega_hub import (
        hivemind_list_sessions,
        hivemind_get_session,
        hivemind_get_awareness,
    )
except ImportError:
    # Fallback for standalone testing
    hivemind_list_sessions = None
    hivemind_get_session = None
    hivemind_get_awareness = None

from src.omega.agents.scribe.parser import HubBroadcast, HubUpdatePlan
from src.omega.agents.scribe.lock import managed_hub_lock, atomic_write


class HubMaster:
    """
    Scribe's Hub Master loop.
    Monitors Hivemind for agent broadcasts and updates the collaboration hub.
    """
    
    def __init__(
        self,
        hub_path: str = "data/coordination/HMC_COLLABORATION_HUB.md",
        agent_id: str = "scribe-hub-master",
        poll_interval: int = 30,
        lock_ttl: int = 60,
        heartbeat_path: str = "data/coordination/scribe_heartbeat.json"
    ):
        self.hub_path = Path(hub_path)
        self.agent_id = agent_id
        self.poll_interval = poll_interval
        self.lock_ttl = lock_ttl
        self.heartbeat_path = Path(heartbeat_path)
        self._running = False
        self._last_processed_session: Optional[str] = None
        self._session_offset = 0

    async def run(self):
        """Main event loop - polls Hivemind and updates Hub."""
        self._running = True
        print(f"[{datetime.now().isoformat()}] Hub Master started for {self.hub_path}")
        
        # Ensure hub file exists
        self.hub_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.hub_path.exists():
            self._create_initial_hub()
        
        while self._running:
            try:
                await self._process_cycle()
            except Exception as e:
                print(f"[{datetime.now().isoformat()}] Hub Master error: {e}")
                await self._write_heartbeat({"status": "error", "error": str(e)})
            
            await asyncio.sleep(self.poll_interval)

    def stop(self):
        """Stop the event loop."""
        self._running = False

    async def _process_cycle(self):
        """Single processing cycle: fetch broadcasts, parse, update Hub."""
        # 1. Fetch recent Hivemind sessions
        sessions = await self._fetch_recent_sessions()
        
        # 2. Filter for new broadcasts since last cycle
        new_broadcasts = self._extract_new_broadcasts(sessions)
        
        if not new_broadcasts:
            await self._write_heartbeat({"status": "idle", "last_check": datetime.now().isoformat()})
            return
        
        # 3. Parse broadcasts into structured objects
        parsed = self._parse_broadcasts(new_broadcasts)
        
        # 4. Generate update plan
        plan = self._generate_update_plan(parsed)
        
        # 5. Apply updates to Hub file (with locking)
        await self._apply_updates(plan)
        
        # 6. Update heartbeat
        await self._write_heartbeat({
            "status": "updated",
            "broadcasts_processed": len(parsed),
            "last_update": datetime.now().isoformat()
        })

    async def _fetch_recent_sessions(self) -> List[Dict[str, Any]]:
        """Fetch recent Hivemind sessions."""
        if hivemind_list_sessions is None:
            # Fallback: read from filesystem
            return self._fetch_sessions_from_fs()
        
        try:
            result = await hivemind_list_sessions(limit=20)
            return json.loads(result) if isinstance(result, str) else result
        except Exception as e:
            print(f"[{datetime.now().isoformat()}] Failed to fetch sessions: {e}")
            return self._fetch_sessions_from_fs()

    def _fetch_sessions_from_fs(self) -> List[Dict[str, Any]]:
        """Fallback: read session files from HALL_OF_RECORDS."""
        sessions = []
        records_dir = Path("data/knowledge/HALL_OF_RECORDS")
        if records_dir.exists():
            for session_file in sorted(records_dir.glob("*.json"), reverse=True)[:20]:
                try:
                    with open(session_file) as f:
                        sessions.append(json.load(f))
                except Exception:
                    pass
        return sessions

    def _extract_new_broadcasts(self, sessions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract broadcasts from sessions newer than last processed."""
        broadcasts = []
        
        for session in sessions:
            session_id = session.get("session_id") or session.get("id")
            if not session_id:
                continue
            
            # Skip if we've processed this session
            if session_id == self._last_processed_session:
                break
            
            # Extract context posts (broadcasts)
            context_posts = session.get("context_posts", [])
            for post in context_posts:
                if post.get("entity") == "scribe":
                    continue  # Skip our own posts
                
                broadcasts.append({
                    "session_id": session_id,
                    "agent": post.get("entity", "unknown"),
                    "timestamp": post.get("timestamp", datetime.now().isoformat()),
                    "intent": post.get("intent", "status"),
                    "summary": post.get("continuation", post.get("task_current", "")),
                    "data": {
                        "decisions": post.get("decisions", []),
                        "focus_chain": post.get("focus_chain", []),
                        "task_current": post.get("task_current", ""),
                    }
                })
        
        # Update last processed marker
        if sessions:
            self._last_processed_session = sessions[0].get("session_id") or sessions[0].get("id")
        
        return broadcasts

    def _parse_broadcasts(self, broadcasts: List[Dict[str, Any]]) -> List[HubBroadcast]:
        """Parse raw broadcasts into structured HubBroadcast objects."""
        parsed = []
        
        for b in broadcasts:
            try:
                # Extract structured fields from data
                data = b.get("data", {})
                decisions = data.get("decisions", [])
                
                # Try to extract ticket_id, decision_id from decisions/summary
                ticket_id = None
                decision_id = None
                for d in decisions:
                    if d.startswith("C-") or d.startswith("P-"):
                        ticket_id = d.split()[0]
                    elif d.startswith("D-"):
                        decision_id = d.split()[0]
                
                # Check for Carmack mode indicators
                carmack_mode = "carmack" in b.get("summary", "").lower()
                leverage_ratio = None
                if "leverage" in b.get("summary", "").lower():
                    # Try to extract ratio
                    import re
                    match = re.search(r'(\d+:\d+|\d+x)', b["summary"])
                    if match:
                        leverage_ratio = match.group(1)
                
                broadcast = HubBroadcast(
                    agent=b.get("agent", "unknown"),
                    timestamp=datetime.fromisoformat(b["timestamp"].replace('Z', '+00:00')),
                    intent=b.get("intent", "status"),
                    summary=b.get("summary", "")[:500],  # Truncate
                    ticket_id=ticket_id,
                    decision_id=decision_id,
                    carmack_mode=carmack_mode,
                    leverage_ratio=leverage_ratio,
                    data=data
                )
                parsed.append(broadcast)
            except Exception as e:
                print(f"[{datetime.now().isoformat()}] Failed to parse broadcast: {e}")
        
        return parsed

    def _generate_update_plan(self, broadcasts: List[HubBroadcast]) -> HubUpdatePlan:
        """Generate Hub update plan from parsed broadcasts."""
        plan = HubUpdatePlan()
        
        for b in broadcasts:
            agent = b.agent
            
            # Update agent section
            if agent not in plan.agent_section_updates:
                plan.agent_section_updates[agent] = ""
            
            # Format entry for agent section
            timestamp = b.timestamp.strftime("%Y-%m-%d %H:%M")
            intent_emoji = {
                "status": "📋",
                "decision": "⚖️",
                "blocker": "🚧",
                "handoff_complete": "✅",
                "meta": "🔧"
            }.get(b.intent, "📋")
            
            entry = f"\n> **[{timestamp}]** {intent_emoji} {b.summary}"
            if b.ticket_id:
                entry += f" (`{b.ticket_id}`)"
            if b.decision_id:
                entry += f" **Decision: `{b.decision_id}`**"
            if b.carmack_mode:
                entry += " ⚡ **CARMACK MODE**"
            if b.leverage_ratio:
                entry += f" (Leverage: {b.leverage_ratio})"
            
            plan.agent_section_updates[agent] += entry
            
            # Handle decisions
            if b.intent == "decision" and b.decision_id:
                plan.decisions_log_entries.append({
                    "id": b.decision_id,
                    "timestamp": b.timestamp.isoformat(),
                    "agent": agent,
                    "summary": b.summary,
                    "ticket": b.ticket_id
                })
            
            # Handle blockers
            if b.intent == "blocker":
                severity = b.data.get("blocker_severity", "medium")
                plan.blockers_table_entries.append({
                    "id": f"BLK-{datetime.now().strftime('%Y%m%d-%H%M')}",
                    "timestamp": b.timestamp.isoformat(),
                    "agent": agent,
                    "severity": severity,
                    "description": b.summary,
                    "ticket": b.ticket_id
                })
        
        return plan

    async def _apply_updates(self, plan: HubUpdatePlan):
        """Apply updates to Hub file with locking."""
        # Read current Hub
        current_content = ""
        if self.hub_path.exists():
            current_content = self.hub_path.read_text()
        
        # Apply updates
        updated_content = self._merge_updates(current_content, plan)
        
        # Write atomically with lock
        with managed_hub_lock(str(self.hub_path), self.agent_id, self.lock_ttl):
            atomic_write(str(self.hub_path), updated_content)
        
        print(f"[{datetime.now().isoformat()}] Hub updated: {len(plan.agent_section_updates)} agent sections, {len(plan.decisions_log_entries)} decisions, {len(plan.blockers_table_entries)} blockers")

    def _merge_updates(self, content: str, plan: HubUpdatePlan) -> str:
        """Merge plan updates into Hub markdown content."""
        lines = content.split('\n')
        output = []
        i = 0
        
        # Track which sections we've updated
        updated_agents = set()
        decisions_added = False
        blockers_added = False
        
        while i < len(lines):
            line = lines[i]
            
            # Agent section updates
            for agent, update_text in plan.agent_section_updates.items():
                section_header = f"### @{agent}"
                if line.strip() == section_header:
                    # Find end of this agent's section (next ### or end of file)
                    output.append(line)
                    i += 1
                    # Copy existing content until next section
                    while i < len(lines) and not lines[i].startswith("### @"):
                        output.append(lines[i])
                        i += 1
                    # Append our updates
                    output.append(update_text)
                    updated_agents.add(agent)
                    continue
            
            # Decisions log
            if "## ⚖️ Decisions Log" in line and not decisions_added:
                output.append(line)
                i += 1
                # Find table or end of section
                while i < len(lines) and not lines[i].startswith("## "):
                    output.append(lines[i])
                    i += 1
                # Append new decisions
                for d in plan.decisions_log_entries:
                    output.append(f"| {d['id']} | {d['timestamp'][:19]} | {d['agent']} | {d['summary'][:60]} | {d.get('ticket', '-')} |")
                decisions_added = True
                continue
            
            # Blockers table
            if "## 🚧 Blockers" in line and not blockers_added:
                output.append(line)
                i += 1
                while i < len(lines) and not lines[i].startswith("## "):
                    output.append(lines[i])
                    i += 1
                for b in plan.blockers_table_entries:
                    output.append(f"| {b['id']} | {b['timestamp'][:19]} | {b['agent']} | {b['severity']} | {b['description'][:60]} | {b.get('ticket', '-')} |")
                blockers_added = True
                continue
            
            output.append(line)
            i += 1
        
        # Handle agents not found in file (new agents)
        for agent, update_text in plan.agent_section_updates.items():
            if agent not in updated_agents:
                # Append at end of file
                output.append(f"\n### @{agent}\n**Role**: Auto-detected\n**Current Focus**: New agent\n{update_text}")
        
        return '\n'.join(output)

    def _create_initial_hub(self):
        """Create initial Hub file if it doesn't exist."""
        initial = f"""# 🔱 HMC Collaboration Hub
**Version**: 1.0
**Created**: {datetime.now().isoformat()}
**Maintained by**: @scribe (Hub Master)

---

## 🏁 Sprint Status
| Sprint | Phase | Status | Owner |
|--------|-------|--------|-------|
| Guard & Distill | Complete | ✅ Done | @maat |
| ARF | Phase 1 | 🔄 Active | @researcher |

---

## ⚖️ Decisions Log
| ID | Timestamp | Agent | Summary | Ticket |
|----|-----------|-------|---------|--------|

---

## 🚧 Blockers & Requests
| ID | Timestamp | Agent | Severity | Description | Ticket |
|----|-----------|-------|----------|-------------|--------|

---

## 🧑‍💼 Agent Sections

### @maat
**Role**: Light Oversoul (P1-P5) — Build Governance
**Current Focus**: ARF Sprint coordination

### @lilith
**Role**: Dark Oversoul (P6-P10) — Run Governance
**Current Focus**: Provider fabric, VaultCore

### @researcher
**Role**: Deep Research — Lattice Reasoning
**Current Focus**: Phase 1 free-tier provider configs

### @pillar P1
**Role**: Infrastructure — SysAdmin
**Current Focus**: Podman hardening, WARP proxy

### @pillar P3
**Role**: Engineering — BuildMaster
**Current Focus**: Grok CLI dev workflow

### @pillar P4
**Role**: Integration — Bridge
**Current Focus**: AGY OAuth persistence fix

### @scribe
**Role**: Hub Master + Soul Distillation
**Current Focus**: Hub maintenance, L1→L2→L3 pipeline
"""
        self.hub_path.write_text(initial)

    async def _write_heartbeat(self, status: Dict[str, Any]):
        """Write heartbeat for health monitoring."""
        self.heartbeat_path.parent.mkdir(parents=True, exist_ok=True)
        heartbeat = {
            "agent": self.agent_id,
            "timestamp": datetime.now().isoformat(),
            **status
        }
        atomic_write(str(self.heartbeat_path), json.dumps(heartbeat, indent=2))


async def main():
    """Entry point for running Hub Master as a service."""
    import signal
    
    master = HubMaster()
    
    def handle_signal(signum, frame):
        print(f"[{datetime.now().isoformat()}] Received signal {signum}, shutting down...")
        master.stop()
    
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    
    await master.run()


if __name__ == "__main__":
    asyncio.run(main())