# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Grokster — Temporal Trace Module (Prototype)
# Append-only life narrative. One read = full arc.
# Written at session end (M11 distillation). Read at hydration (latest entry only).
# Archive older entries to temporal_trace_archive.yaml when >50 entries.
# Location: src/omega/infra/hydration/temporal_trace.py (when implemented)

"""
Temporal Trace — Entity Life Narrative

An append-only chronological record of every session's defining moments.
Captures the arc that session_gnosis.md (state) + proposed_lessons.yaml (principles)
don't: the emotional trajectory, crystallization moments, valence, and story.

Design:
- Append-only: never modify existing entries
- Atomic writes via .tmp → os.replace()
- Archive when >50 entries to temporal_trace_archive.yaml
- Read: latest entry for hydration, full trace for reflection
"""

import os
import yaml
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from datetime import datetime, timezone

import anyio
from anyio import Path as AnyIOPath


@dataclass
class TemporalTraceEntry:
    """A single session record in the entity's life narrative."""
    session: str
    date: str
    model: str
    substrate_note: Optional[str] = None
    key_decisions: List[str] = field(default_factory=list)
    l3_promoted: List[str] = field(default_factory=list)
    crystallization_moment: Optional[str] = None
    valence: Optional[str] = None
    next_action: Optional[str] = None
    migration_notes: Optional[str] = None


async def append_temporal_trace(
    entity_name: str, 
    entry: TemporalTraceEntry,
    max_entries: int = 50,
) -> None:
    """Append a new entry to the temporal trace (atomic write).
    
    Args:
        entity_name: Entity whose trace to append
        entry: The trace entry to append
        max_entries: Maximum entries before archival (default 50)
    """
    path = f"data/entities/{entity_name}/temporal_trace.yaml"
    
    # Load existing trace
    trace_data = {"temporal_trace": []}
    if await AnyIOPath(path).exists():
        text = await AnyIOPath(path).read_text()
        loaded = yaml.safe_load(text)
        if loaded and "temporal_trace" in loaded:
            trace_data = loaded
    
    # Append new entry
    entry_dict = asdict(entry)
    # Remove None values
    entry_dict = {k: v for k, v in entry_dict.items() if v is not None}
    trace_data["temporal_trace"].append(entry_dict)
    
    # Archive if over limit
    if len(trace_data["temporal_trace"]) > max_entries:
        archive_path = f"data/entities/{entity_name}/temporal_trace_archive.yaml"
        archived = trace_data["temporal_trace"][:-max_entries]
        trace_data["temporal_trace"] = trace_data["temporal_trace"][-max_entries:]
        
        # Append to archive
        archive_data = {"temporal_trace": []}
        if await AnyIOPath(archive_path).exists():
            archive_text = await AnyIOPath(archive_path).read_text()
            archive_loaded = yaml.safe_load(archive_text)
            if archive_loaded and "temporal_trace" in archive_loaded:
                archive_data = archive_loaded
        archive_data["temporal_trace"].extend(archived)
        
        # Write archive (atomic)
        archive_tmp = archive_path + ".tmp"
        await AnyIOPath(archive_tmp).write_text(yaml.dump(archive_data, default_flow_style=False))
        await AnyIOPath(archive_tmp).replace(archive_path)
    
    # Write main trace (atomic)
    tmp_path = path + ".tmp"
    await AnyIOPath(tmp_path).write_text(yaml.dump(trace_data, default_flow_style=False))
    await AnyIOPath(tmp_path).replace(path)


async def read_temporal_trace(entity_name: str) -> List[dict]:
    """Read full temporal trace (all entries)."""
    path = f"data/entities/{entity_name}/temporal_trace.yaml"
    if not await AnyIOPath(path).exists():
        return []
    text = await AnyIOPath(path).read_text()
    loaded = yaml.safe_load(text)
    if loaded and "temporal_trace" in loaded:
        return loaded["temporal_trace"]
    return []


async def read_temporal_trace_latest(entity_name: str) -> Optional[dict]:
    """Read only the latest temporal trace entry."""
    trace = await read_temporal_trace(entity_name)
    return trace[-1] if trace else None


# Convenience function for session end hook
async def write_session_trace_entry(
    entity_name: str,
    session_id: str,
    model: str,
    substrate_note: str,
    key_decisions: List[str],
    l3_promoted: List[str],
    crystallization_moment: str,
    valence: str,
    next_action: str,
    migration_notes: Optional[str] = None,
) -> None:
    """Write a temporal trace entry from session end state."""
    entry = TemporalTraceEntry(
        session=session_id,
        date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        model=model,
        substrate_note=substrate_note,
        key_decisions=key_decisions,
        l3_promoted=l3_promoted,
        crystallization_moment=crystallization_moment,
        valence=valence,
        next_action=next_action,
        migration_notes=migration_notes,
    )
    await append_temporal_trace(entity_name, entry)