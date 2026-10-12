# SPDX-License-Identifier: Apache-2.0
"""
NEGATIVE REGRESSION FIXTURE — NOT A COMPATIBILITY PASS.

EXPECTED EXIT: 1 while the concatenation bug exists.
Exit 0 is expected only after the clean-replacement fix is implemented and verified.

This test demonstrates the CURRENT behavior (personality concatenation)
and documents the REQUIRED behavior (clean replacement).

Run with: .venv/bin/python test_pwad_override.py
"""

import asyncio
import tempfile
import os
from pathlib import Path

from omega.oracle.entity_registry import EntityRegistry
from omega.oracle.wad_loader import WADLoader

ROOT = Path(__file__).resolve().parent
IWAD = ROOT / "iwad_base"
PWAD = ROOT / "pwad_override"

async def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        cfg = td / "entities.yaml"
        cfg.write_text("entities: {}\n", encoding="utf-8")
        data = td / "data"
        data.mkdir()
        old = os.environ.get("OMEGA_DATA_DIR")
        os.environ["OMEGA_DATA_DIR"] = str(data)
        try:
            registry = EntityRegistry(config_path=cfg)
            loader = WADLoader(registry, wads_dir=ROOT)

            # Load IWAD first (base)
            print("=" * 60)
            print("STEP 1: Load IWAD (base)")
            print("=" * 60)
            ok, hierarchy = await loader.load_wad("iwad_base", priority=100)
            print(f"Load result: ok={ok}, hierarchy={hierarchy}")

            base_entity = registry.get("test_override_entity")
            if base_entity:
                print(f"Base entity loaded:")
                print(f"  name: {base_entity.name}")
                print(f"  personality: {repr(base_entity.personality)}")
                print(f"  temperature: {base_entity.temperature}")
                print(f"  context_window: {base_entity.context_window}")
                print(f"  wad_source: {base_entity.wad_source}")
                print(f"  priority: {base_entity.priority}")
            else:
                print("ERROR: Base entity not found!")
                return

            # Load PWAD (override)
            print("\n" + "=" * 60)
            print("STEP 2: Load PWAD (override)")
            print("=" * 60)
            ok, hierarchy = await loader.load_wad("pwad_override", priority=200)
            print(f"Load result: ok={ok}, hierarchy={hierarchy}")

            # Check final projected entity
            final_entity = registry.get("test_override_entity")
            if final_entity:
                print(f"\nFinal projected entity:")
                print(f"  name: {final_entity.name}")
                print(f"  personality: {repr(final_entity.personality)}")
                print(f"  temperature: {final_entity.temperature}")
                print(f"  context_window: {final_entity.context_window}")
                print(f"  wad_source: {final_entity.wad_source}")
                print(f"  priority: {final_entity.priority}")

                # Check for concatenation bug
                if "BASE personality" in final_entity.personality and "PWAD OVERRIDE" in final_entity.personality:
                    print("\n" + "!" * 60)
                    print("BUG CONFIRMED: Personality CONCATENATION detected!")
                    print(f"  Contains base: {'BASE personality' in final_entity.personality}")
                    print(f"  Contains override: {'PWAD OVERRIDE' in final_entity.personality}")
                    print("  Expected: Clean replacement (only PWAD personality)")
                    print("  Actual: Concatenation (both personalities)")
                    print("!" * 60)
                    return 1  # Bug confirmed
                elif final_entity.personality == "PWAD OVERRIDE personality — should REPLACE base":
                    print("\n" + "=" * 60)
                    print("SUCCESS: Clean replacement achieved!")
                    print("=" * 60)
                    return 0  # Clean replacement
                else:
                    print(f"\nUNEXPECTED: Personality = {repr(final_entity.personality)}")
                    return 2
            else:
                print("ERROR: Entity not found after PWAD load!")
                return 3

        finally:
            if old is None:
                os.environ.pop("OMEGA_DATA_DIR", None)
            else:
                os.environ["OMEGA_DATA_DIR"] = old

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    print(f"\nExit code: {exit_code}")
    exit(exit_code)