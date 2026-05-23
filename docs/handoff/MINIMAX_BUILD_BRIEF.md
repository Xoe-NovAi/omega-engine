# 🔱 Build Brief — Background Researcher Autonomous Hardening

⬡ OMEGA ⬡ SOPHIA ⬡ OVERSEER ⬡ opencode ⬡ trc_strategic ⬡ PHASE‑B  
**Target**: MiniMax M2.5 (Builder mode)  
**Core principle**: The researcher **never idles**. If the queue is empty, it crawls the project for gaps and enqueues the most critical topics itself.  

---

## What Already Exists

The researcher is **already running** — systemd timer fires every 15 minutes. 14 files at `src/omega/workers/background_researcher/`. It runs clean cycles but always skips because the queue is empty. The exclusion is `_grow_frontier()` which is a TODO placeholder.

**Do not rebuild from scratch.** The state machine, checkpoint recovery, credit budget, SearXNG client, search fleet, distiller, convergence detector, soul updater, and CLI commands all work. The gap is **queue population** — the researcher has nothing to research.

---

## Task 1 — Implement `_grow_frontier()` (Autonomous Gap Crawler) [P0]

**File**: `src/omega/workers/background_researcher/loop.py`

Replace the TODO with a multi-source gap crawler that scans the project when idle:

```python
async def _grow_frontier(self) -> None:
    """When queue is empty, crawl the project for knowledge gaps.
    
    Priority order:
    1. Research index — 🔲 not started items
    2. Source code — TODO/FIXME/HACK comments
    3. Roadmap — uncompleted current phase tasks
    4. Entity knowledge bases — missing directories
    5. Checkpoints — previously deferred research
    6. Fallback — tech stack landscape
    """
    import re
    from pathlib import Path
    from .models import ResearchTask
    
    candidates = []
    
    # ── Source 1: Research Index ──────────────────────────────────────
    index_path = Path("docs/research/INDEX.md")
    if index_path.exists():
        text = index_path.read_text()
        for line in text.split("\n"):
            # Match rows with 🔲 (not started) or 🔄 (in progress)
            if "| R-" in line and "|" in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 4:
                    title = parts[2]  # Title column
                    status_col = parts[3] if len(parts) > 3 else ""
                    if "🔲" in status_col or "🔄" in status_col:
                        candidates.append({
                            "topic": title,
                            "source": "research_index",
                            "priority": 0.7,
                            "depth": 2,
                        })
    
    # ── Source 2: Source code TODO/FIXME/HACK ─────────────────────────
    src_dir = Path("src/omega")
    if src_dir.exists():
        for pattern in ["*.py"]:
            for path in src_dir.rglob(pattern):
                try:
                    content = path.read_text()
                    for keyword, pri in [("FIXME", 0.9), ("HACK", 0.8), ("TODO", 0.5)]:
                        if keyword in content:
                            for line in content.split("\n"):
                                if keyword in line:
                                    # Extract the comment after the keyword
                                    idx = line.find(keyword)
                                    comment = line[idx + len(keyword):].strip().strip(": ")
                                    if comment:
                                        candidates.append({
                                            "topic": f"[{keyword}] {comment} — {path.relative_to(src_dir.parent)}",
                                            "source": "codebase",
                                            "priority": 0.9 if keyword == "FIXME" else (0.8 if keyword == "HACK" else 0.5),
                                            "depth": 1,
                                        })
                                    break  # One entry per file per keyword
                except (IOError, OSError):
                    continue
    
    # ── Source 3: Roadmap uncompleted tasks ────────────────────────────
    roadmap_path = Path("docs/ROADMAP.md")
    if roadmap_path.exists():
        text = roadmap_path.read_text()
        # Find Phase headers and their task statuses
        current_phase = None
        for line in text.split("\n"):
            phase_match = re.match(r"^### Phase (\w):", line)
            if phase_match:
                current_phase = phase_match.group(1)
            task_match = re.match(r"^\|\s*(\w[\w.]*)\s*\|.*?\|.*?\|.*?(🔴|🟡)", line)
            if task_match and current_phase:
                task_id = task_match.group(1)
                candidates.append({
                    "topic": f"Phase {current_phase} task {task_id} — implementation research",
                    "source": "roadmap",
                    "priority": 0.6,
                    "depth": 1,
                })
    
    # ── Source 4: Entity knowledge directories ─────────────────────────
    entities_dir = Path("data/entities")
    if entities_dir.exists():
        for entity_dir in entities_dir.iterdir():
            if entity_dir.is_dir() and entity_dir.name != "arch":
                knowledge_dir = entity_dir / "knowledge"
                if not knowledge_dir.exists() or not any(knowledge_dir.iterdir()):
                    candidates.append({
                        "topic": f"Knowledge base scaffolding for entity {entity_dir.name}",
                        "source": "entity_gap",
                        "priority": 0.5,
                        "depth": 1,
                    })
    
    # ── Source 5: Deferred checkpoints ─────────────────────────────────
    checkpoint_dir = Path("data/research/checkpoints")
    if checkpoint_dir.exists():
        for path in checkpoint_dir.glob("*.json"):
            try:
                import json
                data = json.loads(path.read_text())
                if data.get("state") in ("defer", "skip") and data.get("attempts", 0) < 3:
                    candidates.append({
                        "topic": data.get("topic", "Unknown deferred topic"),
                        "source": "checkpoint",
                        "priority": 0.4 + (data.get("attempts", 0) * 0.1),
                        "depth": data.get("depth", 1) + 1,
                    })
            except (json.JSONDecodeError, OSError):
                continue
    
    # ── Limit and Enqueue ──────────────────────────────────────────────
    # Sort by priority descending, limit to 5
    candidates.sort(key=lambda c: c["priority"], reverse=True)
    enqueued = 0
    for c in candidates[:5]:
        # Avoid re-enqueuing active topics
        if any(c["topic"] == t.topic for _, _, t in self.queue._items):
            continue
        task = self.queue.enqueue(
            c["topic"],
            base_priority=c["priority"],
            current_depth=c["depth"] * 2.5,
        )
        enqueued += 1
        logger.info(f"Frontier gap found: '{c['topic']}' (p={c['priority']:.1f}) from {c['source']}")
    
    if enqueued == 0:
        # ── Source 6: Absolute fallback — tech stack landscape ──────────
        fallback_topics = [
            "Gemma 4 31B latest features and API changes May 2026",
            "AnyIO latest patterns for background workers in Python 3 13",
            "OpenCode custom mode plugin development best practices 2026",
            "SearXNG rootless Podman deployment troubleshooting",
            "Ollama v0 6 GGUF model optimization for Zen 2 AVX2",
        ]
        for topic in fallback_topics:
            self.queue.enqueue(topic, base_priority=0.3, current_depth=0)
            enqueued += 1
            logger.info(f"Fallback topic enqueued: '{topic}'")
    
    logger.info(f"Frontier growth complete — enqueued {enqueued} topics")
```

---

## Task 2 — Add Observability to Research Cycles [P0]

**File**: `src/omega/workers/background_researcher/loop.py`

Every research cycle should:
1. Generate a unique `trace_id` for observability
2. Post cycle results to the Hivemind MCP (so the Overseer can monitor)
3. Log structured JSON events for `omega stats`

Add to `run_cycle()`:
```python
import uuid

# At top of run_cycle():
trace_id = f"trc_res_{uuid.uuid4().hex[:12]}"
self.checkpoint.trace_id = trace_id

# At end of run_cycle(), before returning result:
result["trace_id"] = trace_id

# Post to Hivemind MCP (non-blocking — fire and forget)
try:
    async with httpx.AsyncClient(timeout=3.0) as client:
        await client.post(
            "http://127.0.0.1:8013/post",
            json={
                "source": "background-researcher",
                "type": "cycle_complete",
                "trace_id": trace_id,
                "result": result,
            }
        )
except Exception:
    pass  # Hivemind down is non-fatal
```

---

## Task 3 — Harden the Systemd Service [P0]

**File**: `config/systemd/omega-research.service`

```ini
[Unit]
Description=Omega Background Researcher — Sovereign Research Worker
Documentation=https://github.com/Xoe-NovAi/omega-engine
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=%h/Documents/Xoe-NovAi/omega-engine/.venv/bin/python3 -m omega.workers.background_researcher.run
WorkingDirectory=%h/Documents/Xoe-NovAi/omega-engine
Environment=PYTHONPATH=%h/Documents/Xoe-NovAi/omega-engine/src
Environment=OMEGA_ENV=production
StandardOutput=journal
StandardError=journal

# Memory protection
MemoryMax=512M
MemoryHigh=384M

# Auto-restart on failure (catch crashes)
Restart=on-failure
RestartSec=30s

# Security hardening — less strict than before (allows .env loading)
ProtectSystem=full
ReadWritePaths=%h/Documents/Xoe-NovAi/omega-engine/data %h/Documents/Xoe-NovAi/omega-engine/docs
PrivateTmp=yes
NoNewPrivileges=yes

[Install]
WantedBy=default.target
```

Then enable boot persistence:
```bash
systemctl --user daemon-reload
systemctl --user enable omega-research.timer
systemctl --user enable omega-research.service
systemctl --user enable omega-hivemind.service
systemctl --user enable omega-hub.service
systemctl --user enable omega-stats.service
systemctl --user list-unit-files | grep omega
```

---

## Task 4 — Verify End-to-End Flow [Must Do]

```bash
# 1. Manually trigger a cycle — should crawl gaps and enqueue
omega research run
# Expected: "Frontier gap found" logs + topic enqueued

# 2. Check the status — should show queue populated
omega research status
# Expected: Queue size > 0

# 3. Run another cycle — should research the first enqueued topic
omega research run
# Expected: Research cycle complete — sources found, claims, distillations

# 4. Show what was researched
omega research history
# Expected: completed topic listed

# 5. Full test suite
make test
# Expected: 230/230 passing
```

---

## Summary

| Task | What | Why |
|------|------|-----|
| Task 1 | `_grow_frontier()` gap crawler | Researcher never idles — scans 6 sources |
| Task 2 | Observability + Hivemind | Can monitor what's being researched |
| Task 3 | systemd hardening | Auto-start at boot, auto-restart on crash |
| Task 4 | End-to-end verification | Manual test of the full chain |

**Key change from previous brief**: `_grow_frontier()` no longer just scans the research index. It now crawls TODOs, roadmap gaps, entity knowledge holes, deferred checkpoints, and falls back to tech landscape research. The researcher is truly autonomous.
