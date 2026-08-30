#!/usr/bin/env python3
"""
Legacy Context Packer — thin wrapper around the Enhanced Context Packer.

This module exists for backward compatibility with the original `packer.py`
CLI (`python packer.py <profile_name>`). It delegates ALL work to
`enhanced_packer.py` (the canonical v2 implementation) so that the insecure
legacy v1 pipeline (no PII masking, no XML escaping, no Ed25519 signing,
no injection scanning) is never used.

M23 (Failure Integrity): if the enhanced packer cannot be imported, this
wrapper raises — it never silently falls back to the legacy v1 logic.

AP: AP-CONTEXT-PACKER-LEGACY-WRAPPER-v1.0.0
"""

import sys
from pathlib import Path

import anyio

# Ensure the enhanced packer is importable from the same directory.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))


async def _run(profile_name: str):
    # M23: hard dependency on the enhanced packer. No legacy fallback.
    try:
        from enhanced_packer import EnhancedContextPacker
    except ImportError as e:
        raise RuntimeError(
            "[SEC-BLOCKER] enhanced_packer.py unavailable — refusing to run "
            f"legacy v1 packer (no PII masking / no signing). ImportError: {e}"
        ) from e

    packer = EnhancedContextPacker()
    await packer.load_config()
    output_dir = await packer.pack(profile_name)
    print(f"✅ Pack '{profile_name}' generated at: {output_dir}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python packer.py <profile_name>")
        print("(delegates to enhanced_packer.py — the canonical v2 implementation)")
        return
    anyio.run(_run, sys.argv[1])


if __name__ == "__main__":
    main()