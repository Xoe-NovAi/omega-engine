# SPDX-License-Identifier: Apache-2.0
"""Run the disposable WAD against the checked-out Node 0 loader.

This is evidence, not a production WAD. It proves manifest acceptance,
entity envelope loading, hierarchy path resolution, and explicit priority
override. It does not prove Node 1 compatibility.
"""
from pathlib import Path
import asyncio
import tempfile
import os
import yaml

from omega.oracle.entity_registry import Entity, EntityRegistry
from omega.oracle.wad_loader import WADLoader

ROOT = Path(__file__).resolve().parent
WAD = ROOT / "disposable_test_wad"

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
            loader = WADLoader(registry, wads_dir=WAD.parent)
            base = Entity(name="n0_disposable_probe", domains=["base"],
                          model="qwen3-1.7b-q6_k", personality="base")
            await registry.add(base)
            ok, hierarchy = await loader.load_wad(WAD.name, priority=10)
            loaded = registry.get("n0_disposable_probe")
            assert ok is True
            assert hierarchy == WAD / "hierarchy.yaml"
            assert loaded is not None
            print("PASS: manifest accepted")
            print("PASS: entity envelope loaded")
            print("PASS: hierarchy override resolved")
            print(f"OBSERVED: source={loaded.wad_source!r} priority={loaded.priority!r} personality={loaded.personality!r}")
            if loaded.wad_source != WAD.name or loaded.priority != 10:
                print("BLOCKED: priority/entity override did not replace the base registry entity")
                raise SystemExit(2)
            if loaded.personality != "disposable WAD loader probe":
                print("BLOCKED: entity personality was not replaced by the PWAD")
                raise SystemExit(3)
            print("PASS: priority override observed")
        finally:
            if old is None:
                os.environ.pop("OMEGA_DATA_DIR", None)
            else:
                os.environ["OMEGA_DATA_DIR"] = old

if __name__ == "__main__":
    asyncio.run(main())
