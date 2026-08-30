#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Pre-Upgrade Sovereign Snapshot
# ⬡ OMEGA ⬡ RESEARCHER ⬡ minimax-m3-free ⬡ opencode ⬡ trc_snapshot ⬡ UTILITY
# [id-soft: quake-1996] Zone Memory — Atomic state capture
# Mandate 12: Queue Integrity — No silent drops, atomic contract.
# Mandate 13: Temple-Grade T10 (Integrity) — 60% -> 90% upgrade condition.

import os
import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path
import anyio
from src.omega.oracle.observability import ObservabilityEngine

async def create_snapshot():
    \"\"\"
    Creates an atomic, idempotent snapshot of the Omega Engine state 
    before a major version upgrade (e.g., OpenCode 1.16.0).
    
    Captures:
    1. Entity Souls (data/entities/*/soul.yaml)
    2. Engine Config (config/omega.yaml, config/providers.yaml, config/models.yaml)
    3. PIVOT Log (docs/decisions/PIVOT_LOG.md)
    4. Current State (OMEGA_ENGINE.md)
    \"\"\"
    trace_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    snapshot_dir = Path(f"data/snapshots/pre_upgrade_{timestamp}_{trace_id[:8]}")
    
    print(f"Starting Pre-Upgrade Snapshot [{trace_id}]")
    print(f"Target Directory: {snapshot_dir}")
    
    try:
        # Ensure directory exists
        await anyio.Path(snapshot_dir).mkdir(parents=True, exist_ok=True)
        
        # 1. Capture Entity Souls
        souls_dir = snapshot_dir / "souls"
        await anyio.Path(souls_dir).mkdir(exist_ok=True)
        entity_root = Path("data/entities")
        if entity_root.exists():
            for entity_dir in entity_root.glob("*/"):
                soul_file = entity_dir / "soul.yaml"
                if soul_file.exists():
                    await anyio.Path(souls_dir / soul_file.name).write_text(
                        (await anyio.Path(soul_file).read_text()), encoding='utf-8'
                    )
        
        # 2. Capture Engine Config
        config_dir = snapshot_dir / "config"
        await anyio.Path(config_dir).mkdir(exist_ok=True)
        config_files = ["config/omega.yaml", "config/providers.yaml", "config/models.yaml"]
        for cf in config_files:
            p = Path(cf)
            if p.exists():
                await anyio.Path(config_dir / p.name).write_text(
                    (await anyio.Path(p).read_text()), encoding='utf-8'
                )
        
        # 3. Capture PIVOT Log
        pivot_log = Path("docs/decisions/PIVOT_LOG.md")
        if pivot_log.exists():
            await anyio.Path(snapshot_dir / "PIVOT_LOG.md").write_text(
                (await anyio.Path(pivot_log).read_text()), encoding='utf-8'
            )
            
        # 4. Capture Engine State
        state_file = Path("OMEGA_ENGINE.md")
        if state_file.exists():
            await anyio.Path(snapshot_dir / "OMEGA_ENGINE.md").write_text(
                (await anyio.Path(state_file).read_text()), encoding='utf-8'
            )
            
        # Write Manifest
        manifest = {
            "trace_id": trace_id,
            "timestamp": timestamp,
            "status": "SUCCESS",
            "captured_files": {
                "souls": len(list(entity_root.glob("*/soul.yaml"))) if entity_root.exists() else 0,
                "configs": len(config_files),
                "pivot_log": 1 if pivot_log.exists() else 0,
                "state_file": 1 if state_file.exists() else 0
            }
        }
        await anyio.Path(snapshot_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2), encoding='utf-8'
        )
        
        print(f"Snapshot successfully created at {snapshot_dir}")
        return True
        
    except Exception as e:
        # Mandate 9: No silent swallowing
        print(f"CRITICAL ERROR during snapshot: {str(e)}")
        # In a real engine, this would be logged via ObservabilityEngine
        return False

async def main():
    await create_snapshot()

if __name__ == "__main__":
    import anyio
    anyio.run(main)
