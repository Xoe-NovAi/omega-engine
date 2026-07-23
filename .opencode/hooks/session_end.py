#!/usr/bin/env python3
"""OpenCode session end hook — Soul Distillation.

This hook runs at the end of each OpenCode session to distill
the session's exchanges into L1→L2→L3 lessons for the entity's
proposed_lessons.yaml (blind staging per M5/M11).

Environment variables (set by OpenCode):
- OPENCODE_ENTITY: The entity name (e.g., "kali", "john_carmack")
- OPENCODE_SESSION_ID: The session ID (e.g., "ses_20260723_john_carmack_001")
- OPENCODE_MODEL: The model used (e.g., "nemotron-3-ultra-free")
"""

import os
import sys
import asyncio
import logging

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from omega.scribe import SoulDistiller

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Run soul distillation for the current session."""
    entity = os.environ.get("OPENCODE_ENTITY", "unknown")
    session_id = os.environ.get("OPENCODE_SESSION_ID", "unknown")
    model = os.environ.get("OPENCODE_MODEL", "unknown")
    
    logger.info(f"[Scribe] Session end hook triggered for {entity} / {session_id}")
    
    if entity == "unknown" or session_id == "unknown":
        logger.warning("[Scribe] Missing entity or session_id, skipping distillation")
        return
    
    try:
        distiller = SoulDistiller(entity_name=entity, session_id=session_id, model=model)
        proposals = await distiller.distill_session()
        logger.info(f"[Scribe] Distilled {len(proposals)} lessons for {entity}")
    except Exception as e:
        logger.error(f"[Scribe] Distillation failed: {e}")
        # Don't fail the hook - distillation is best-effort
        pass


if __name__ == "__main__":
    asyncio.run(main())