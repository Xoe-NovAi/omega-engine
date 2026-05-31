# 🔱 Gemma Build Brief — Background Researcher Hardening Sprint

⬡ OMEGA ⬡ SOPHIA ⬡ OVERSEER ⬡ opencode ⬡ trc_strategic ⬡ PHASE‑B  
**Target**: Gemma 4 31B (Builder mode) — unlimited + vision capable  
**Models available**: Gemma 4 31B‑it (vision), MiniMax M2.5 (deep reasoning), DeepSeek V4 Flash (reserve)  

---

## Context — What Already Exists

The background researcher is **already running** on the system. Do not rebuild from scratch. The state is:

| Aspect | Status |
|--------|--------|
| `src/omega/workers/background_researcher/` | ✅ 14 files, full state machine |
| CLI commands (`omega research run/status/queue/history`) | ✅ Wired in `oracle_cli.py` |
| `omega-research.timer` (15‑min schedule) | ✅ Active — systemd |
| `omega-research.service` | ✅ Runs — but skips because queue is empty |
| `_grow_frontier()` | ❌ TODO — placeholder, never seeds the queue |
| SearXNG | ❌ Dead container — needs restart or removal as dependency |
| Vision integration | 🔲 Not yet used |

---

## Task 1 — Implement `_grow_frontier()` [High Priority]

**File**: `src/omega/workers/background_researcher/loop.py`

**Current state** (line 374):
```python
async def _grow_frontier(self) -> None:
    logger.info("Queue empty — frontier scan skipped (not yet implemented)")
```

**Goal**: When the queue is empty, scan `docs/research/` for topics with shallow coverage and enqueue deeper research.

**Implementation**:
```python
async def _grow_frontier(self) -> None:
    """Scan research index for low‑depth topics and enqueue deeper research."""
    from .models import ResearchTask
    import re
    
    # 1. Check docs/research/INDEX.md for topics with depth < 2
    index_path = Path("docs/research/INDEX.md")
    if not index_path.exists():
        return
    
    text = index_path.read_text()
    # Find all research entries
    topics = []
    for line in text.split("\n"):
        # Match lines like "| R-XX | Title | ... | ... | ... |"
        if line.startswith("| R-") and "|" in line[3:]:
            parts = line.split("|")
            if len(parts) >= 3:
                title = parts[2].strip()
                topics.append(title)
    
    # 2. Seed up to 3 topics into queue with moderate priority
    for i, topic in enumerate(topics[:3]):
        task = ResearchTask(
            topic=topic,
            priority=0.4,  # Moderate — user requests get priority
            depth=1,
        )
        self.queue.enqueue(topic, base_priority=0.4, current_depth=1)
        logger.info(f"Frontier seeded: '{topic}'")
```

**Verification**: After a cycle with empty queue, `omega research status` shows `Queue size: 3`.

---

## Task 2 — Add Seed Topics for First‑Run Autonomy [High Priority]

**File**: `src/omega/workers/background_researcher/loop.py`

**Goal**: On first ever run (no checkpoints exist), auto‑seed the queue with high‑value topics.

**Location**: Add check at the top of `_get_next_task()`:
```python
async def _get_next_task(self) -> Optional[ResearchTask]:
    """Get the next task from queue or checkpoints."""
    # First run detection: no checkpoints exist → seed topics
    seed_topics = [
        "SearXNG Docker Podman rootless deployment best practices 2026",
        "Gemma 4 31B vision API capabilities for sovereign AI research",
        "OpenCode MCP configuration patterns for multi‑provider search",
        "Ollama GGUF model loading optimization for Zen 2 Ryzen 5700U",
    ]
    checkpoint_dir = Path("data/research/checkpoints")
    if not checkpoint_dir.exists() or not any(checkpoint_dir.iterdir()):
        for topic in seed_topics:
            self.queue.enqueue(topic, base_priority=0.7, current_depth=0)
        logger.info(f"First run — seeded {len(seed_topics)} topics")
    
    # ... rest of existing method ...
```

---

## Task 3 — Add Vision‑Aware Research Mode [Medium Priority]

**File**: Create `src/omega/workers/background_researcher/vision_extractor.py`

**Goal**: Use Gemma 4 31B's vision capability to extract information from screenshots and diagrams during research cycles.

```python
# 🔱 Omega Engine — Vision Extractor for Background Researcher
# ⬡ OMEGA ⬡ SOPHIA ⬡ sovereign ⬡ vision ⬡ WORKER
#
# Uses Gemma 4 31B's vision capability to analyze:
# - Screenshots of documentation pages
# - Architecture diagrams
# - UI layouts
# - Charts and data visualizations

import logging
import base64
from pathlib import Path
from typing import Optional

import anyio
import httpx

logger = logging.getLogger(__name__)


class VisionExtractor:
    """Extract structured information from images using Gemma 4 31B vision."""

    def __init__(self, api_key: str = "", model: str = "gemma-4-31b-it"):
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY", "")
        self.model = model

    async def analyze_screenshot(self, image_path: str, prompt: str = "") -> str:
        """Analyze a screenshot or diagram with a custom prompt."""
        # Read image and base64 encode
        async with await anyio.Path(image_path).open("rb") as f:
            image_data = await f.read()
        encoded = base64.b64encode(image_data).decode("utf-8")

        # Default prompt for documentation screenshots
        vision_prompt = prompt or (
            "Extract all technical information from this image. "
            "Include: commands, configuration values, error messages, "
            "architecture components, and their relationships."
        )

        # Call Google AI Studio Gemini API with image
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        payload = {
            "contents": [{
                "parts": [
                    {"text": vision_prompt},
                    {"inline_data": {"mime_type": "image/png", "data": encoded}}
                ]
            }]
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    f"{url}?key={self.api_key}",
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()
                text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                return text
        except Exception as e:
            logger.error(f"Vision extraction failed: {e}")
            return ""
```

**Integration**: Add `VisionExtractor` to `BackgroundResearcherLoop.__init__()` and use it in `_extract()` when a source is an image.

---

## Task 4 — Systemd Service Auto‑Start [High Priority]

**Enable all Omega services to start at boot**:

```bash
# Enable the researcher timer for boot persistence
systemctl --user enable omega-research.timer
systemctl --user enable omega-research.service  # (for manual runs)

# Enable Hivemind and Hub at boot
systemctl --user enable omega-hivemind.service
systemctl --user enable omega-hub.service
systemctl --user enable omega-stats.service

# Fix SearXNG (restart container)
systemctl --user restart omega-searxng.service
systemctl --user enable omega-searxng.service

# Check what's enabled
systemctl --user list-unit-files | grep omega
```

**Files**: `config/systemd/omega-research.service`, `.timer`, `omega-hivemind.service` — verify they have `[Install]` section with `WantedBy=default.target`.

---

## Task 5 — Harden the Research Service [Medium Priority]

**File**: `config/systemd/omega-research.service`

Current service has `ProtectSystem=strict` which can block `.env` loading. Fix:

```ini
# Change from:
ProtectSystem=strict
ReadWritePaths=%h/Documents/Xoe-NovAi/omega-engine/data %h/Documents/Xoe-NovAi/omega-engine/docs/research

# To:
ProtectSystem=full
ReadWritePaths=%h/Documents/Xoe-NovAi/omega-engine/data %h/Documents/Xoe-NovAi/omega-engine/docs/research
ReadOnlyPaths=%h/Documents/Xoe-NovAi/omega-engine/.env
```

Also add auto‑restart on failure:
```ini
[Service]
Restart=on-failure
RestartSec=30s
```

---

## Task 6 — Harden Core CLI Commands [Medium Priority]

**Verify** `omega research` commands work correctly:
```bash
omega research queue "Gemma 4 31B vision API usage patterns" --depth 2
omega research status
omega research run
omega research history
```

If any command fails, fix the wiring in `src/omega/cli/oracle_cli.py`.

---

## Task 7 — Fix SearXNG Container (Optional, Vision‑Assisted) [Low Priority]

**Use Gemma's vision** to diagnose the SearXNG failure. Take a screenshot:
```bash
# Capture the SearXNG container logs
journalctl --user -u omega-searxng.service --no-pager > /tmp/searxng.log
# If there's a UI error page, screenshot it and analyze with vision
```

Common SearXNG issues on rootless Podman:
- Port conflict (8017 already in use)
- Permission denied on `/etc/searxng/` within container
- Missing `.searxng.env` or `settings.yml`

---

## Verification Checklist

```bash
# Run after each task
make test                                            # 230 tests must pass
omega research status                                # Show researcher state
systemctl --user list-timers | grep omega-research   # Verify timer active
omega research run                                   # Force one cycle
omega research history                               # Verify something was researched
```

---

## Vision Use Cases During This Sprint

| Task | Screenshot Opportunity |
|------|----------------------|
| Task 1 `_grow_frontier()` | Code structure of `loop.py` for review |
| Task 4 systemd | `systemctl --user list-units` output |
| Task 5 hardening | `journalctl` error output |
| Task 7 SearXNG | SearXNG web UI error page |

---

*Build brief prepared by Overseer. Gemma to execute in order: Task 1 → Task 2 → Task 3 → Task 4 → Task 5 → Task 6 → Task 7. Run `make test` after each task.*
