# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Automated distillation for the omega_federation entity.

Watches mesh events (netsplits, latency spikes, key rotations, auth
failures) and appends L1→L2→L3 lessons to the federation entity's
proposed_lessons.yaml. Called by the Scribe pipeline or cron.

Mandates: M11 (Soul Integrity), M15 (Continuity), M19 (Adversarial Alchemy)
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import anyio

ENTITY_DIR = Path("data/entities/federation")
LESSONS_FILE = ENTITY_DIR / "proposed_lessons.yaml"
EVENTS_LOG = Path("data/coordination/FEDERATION_LIVE_FEED.md")


async def fetch_federation_events(since: str | None = None) -> list[dict]:
    """Parse the live feed for mesh events since a given timestamp."""
    if not EVENTS_LOG.exists():
        return []
    text = await anyio.to_thread.run_sync(EVENTS_LOG.read_text)
    events = []
    for line in text.splitlines():
        if line.startswith("- 20"):
            events.append({"raw": line, "ts": line[2:19]})
    return events


async def synthesize_lesson(event: dict) -> str:
    """Convert a raw mesh event into an L1→L2→L3 lesson string."""
    raw = event.get("raw", "")
    ts = event.get("ts", datetime.now(timezone.utc).isoformat())
    # Heuristic: extract the event type from the raw line
    event_type = "mesh_event"
    for kw in ("netsplit", "latency", "key", "auth", "join", "leave", "ACL"):
        if kw.lower() in raw.lower():
            event_type = kw.lower()
            break
    return (
        f"L1: {ts} — {raw}\n"
        f"  L2: Federation {event_type} event observed. "
        f"Mesh anomalies are empirical diagnostics of distributed state.\n"
        f"  L3: Every netsplit, DNS desync, and key expiry failure is an "
        f"empirical diagnostic. Documenting failures as L3 principles turns "
        f"operational friction into resilient infrastructure."
    )


async def append_proposed_lesson(entity: str, lesson: str) -> None:
    """Append a lesson to the entity's proposed_lessons.yaml."""
    path = Path(f"data/entities/{entity}/proposed_lessons.yaml")
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        await anyio.to_thread.run_sync(
            lambda: path.write_text("# 🔱 Omega Engine — Proposed Lessons\n")
        )
    text = await anyio.to_thread.run_sync(path.read_text)
    if not text.endswith("\n"):
        text += "\n"
    await anyio.to_thread.run_sync(
        lambda: path.write_text(text + f'- "{lesson}"\n')
    )


async def distill_federation_events() -> int:
    """Main entry: fetch events, synthesize lessons, append to entity soul."""
    events = await fetch_federation_events()
    if not events:
        return 0
    count = 0
    for event in events[-5:]:  # last 5 events max per run
        lesson = await synthesize_lesson(event)
        await append_proposed_lesson("federation", lesson)
        count += 1
    return count


# ── CLI entry ───────────────────────────────────────────────────────


def main() -> int:
    """Run distillation synchronously (for cron/systemd)."""
    import asyncio  # noqa: PLC0415 — CLI entry, not src/omega core

    result = asyncio.run(distill_federation_events())
    print(f"Distilled {result} federation event(s) to proposed_lessons.yaml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())