#!/usr/bin/env python3
"""OpenCode session end hook — Soul Distillation + Codex Refresh.

This hook runs at the end of each OpenCode session to:
  1. Distill the session's exchanges into L1→L2→L3 lessons for the entity's
     proposed_lessons.yaml (blind staging per M5/M11).
  2. Regenerate OMEGA_CODEX.md (Stack-Cat Protocol) so the next session
     starts with fresh context — prevents the >24h stale-Codex gap.

Environment variables (set by OpenCode):
- OPENCODE_ENTITY: The entity name (e.g., "kali", "john_carmack")
- OPENCODE_SESSION_ID: The session ID (e.g., "ses_20260723_john_carmack_001")
- OPENCODE_MODEL: The model used (e.g., "nemotron-3-ultra-free")
"""

import os
import sys
import subprocess
import anyio
import logging

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from omega.scribe import SoulDistiller

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to the codex regenerator, relative to this hook file
CODEX_CAT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "codex_cat.py")


async def _regenerate_codex() -> None:
    """Regenerate OMEGA_CODEX.md via codex_cat.py (non-blocking)."""
    try:
        def _run_codex():
            return subprocess.run(
                [sys.executable, CODEX_CAT_PATH],
                capture_output=True, text=True, timeout=30,
            )
        result = await anyio.to_thread.run_sync(_run_codex)
        if result.returncode == 0:
            # Extract line count from output for logging
            for line in result.stdout.strip().split("\n"):
                if "Lines:" in line or "successfully" in line:
                    logger.info(f"[Codex] {line.strip()}")
            logger.info("[Codex] OMEGA_CODEX.md refreshed for next session")
        else:
            logger.warning(f"[Codex] Refresh failed (exit {result.returncode}): {result.stderr.strip()}")
    except subprocess.TimeoutExpired:
        logger.warning("[Codex] Refresh timed out after 30s — skipping")
    except Exception as e:
        logger.warning(f"[Codex] Refresh error: {e}")


async def main():
    """Run soul distillation + Codex refresh for the current session."""
    entity = os.environ.get("OPENCODE_ENTITY", "unknown")
    session_id = os.environ.get("OPENCODE_SESSION_ID", "unknown")
    model = os.environ.get("OPENCODE_MODEL", "unknown")
    
    logger.info(f"[Scribe] Session end hook triggered for {entity} / {session_id}")
    
    # --- Step 1: Soul Distillation ---
    if entity != "unknown" and session_id != "unknown":
        try:
            distiller = SoulDistiller(entity_name=entity, session_id=session_id, model=model)
            proposals = await distiller.distill_session()
            logger.info(f"[Scribe] Distilled {len(proposals)} lessons for {entity}")
        except Exception as e:
            logger.error(f"[Scribe] Distillation failed: {e}")
            # Don't fail the hook - distillation is best-effort
    else:
        logger.warning("[Scribe] Missing entity or session_id, skipping distillation")
    
    # --- Step 2: Codex Refresh ---
    await _regenerate_codex()


if __name__ == "__main__":
    anyio.run(main)