#!/usr/bin/env python3
# 🔱 Omega Engine — Session End Hook (Simplified)
# AP Token: AP-SESSION-END-HOOK-v3.0.0
# ⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ session_end ⬡ ACTIVE
#
# Purpose: Write session timestamp for M5/M11 compliance + refresh codex.
#          Called by .opencode/wrapper.sh AFTER OpenCode process exits.
#
# Carmack Verdict 2026-07-30: Soul Distillation Pipeline SCRAPPED.
#   - Regex-based L1/L2/L3 extraction was fortune-cookie generation.
#   - Real soul growth: agents write their own lessons. That works.
#   - This hook now: timestamp + codex refresh. 40 lines. No false promises.
#
# M5/M11: proposed_lessons.yaml written every session end (empty proposals OK).
# M22: model_used recorded from OPENCODE_MODEL env.
# M23: Hard timeout, never crashes wrapper.
# M1: Uses anyio.

import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import anyio

LOG_DIR = Path(__file__).parent.parent / "logs"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
    stream=sys.stderr,
)
# Persistent file log [2026-08-25 jem fix]: stderr is captured by wrapper.sh
# but lost when the terminal closes. Future silence becomes diagnosable.
try:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    _fh = logging.FileHandler(LOG_DIR / "session_end.log")
    _fh.setFormatter(logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%dT%H:%M:%SZ"))
    logging.getLogger().addHandler(_fh)
except OSError as e:  # never crash the hook over a log file (M23)
    logging.getLogger().warning(f"File logging unavailable: {e}")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent
CODEX_CAT_PATH = PROJECT_ROOT / "scripts" / "codex_cat.py"


async def _write_timestamp(entity: str, session_id: str, model: str) -> None:
    """Write minimal session timestamp to proposed_lessons.yaml (M5/M11).
    
    Preserves any agent-written proposals from the just-completed session
    rather than overwriting with an empty stub. This prevents the destructive
    race where agents write proposals per AGENTS.md step 6.5, then the hook
    fires and erases them.
    """
    import yaml

    entity_name = entity if entity != "unknown" else "sophia"
    proposed_path = PROJECT_ROOT / "data" / "entities" / entity_name / "proposed_lessons.yaml"

    # Read existing proposals first — preserve agent-written content
    existing = {}
    if proposed_path.exists():
        with open(proposed_path) as f:
            existing = yaml.safe_load(f) or {}

    existing_proposals = existing.get("proposals", [])

    proposed_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "proposals": existing_proposals,
        "metadata": {
            "entity": entity_name,
            "session_id": session_id,
            "model_used": model,
            "last_session_end": datetime.now(timezone.utc).isoformat(),
        },
    }

    tmp = proposed_path.with_suffix(".yaml.tmp")
    with open(tmp, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(str(tmp), str(proposed_path))
    logger.info(f"[Session] Timestamp written for {entity_name}")


async def _regenerate_codex() -> None:
    """Regenerate OMEGA_CODEX.md (non-blocking, timeout)."""
    if not CODEX_CAT_PATH.exists():
        return
    try:
        def _run():
            return subprocess.run(
                [sys.executable, str(CODEX_CAT_PATH)],
                capture_output=True, text=True, timeout=30, cwd=str(PROJECT_ROOT),
            )

        result = await anyio.to_thread.run_sync(_run)
        if result.returncode == 0:
            logger.info("[Codex] OMEGA_CODEX.md refreshed")
        else:
            # [2026-08-25 jem fix] surface WHY it failed, not just that it did
            tail = (result.stderr or result.stdout or "")[-500:].strip()
            logger.warning(f"[Codex] Refresh failed (exit {result.returncode}): {tail}")
    except Exception as e:
        logger.warning(f"[Codex] Refresh error: {e}")


async def main() -> int:
    entity = os.environ.get("OPENCODE_ENTITY", "unknown")
    session_id = os.environ.get("OPENCODE_SESSION_ID", "unknown")
    model = os.environ.get("OPENCODE_MODEL", "unknown")
    logger.info(f"[Session] Hook triggered for {entity} / {session_id} / {model}")

    await _write_timestamp(entity, session_id, model)
    await _regenerate_codex()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(anyio.run(main))
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        logger.error(f"[Session] Fatal: {e}")
        sys.exit(1)
