#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
OpenCode Session Hydration — Restores context from session_gnosis.md
M15: Sovereign Continuity — recover from compaction/context loss

COMPACTION-IMMUNE CONSTRAINT RE-ASSERTION (M11 / M15 / M23, ticket P0-2)
-------------------------------------------------------------------------
This module is the post-compact hydration hook. It is where constraint state is
re-asserted, and it is the ONLY place that does so.

WHY HERE, AND WHY IT CANNOT BE SKIPPED
`MANDATES_CONDENSED.md` is injected pre-compaction; after compaction that block
is exactly what the summarizer may drop (arXiv:2606.22528, "Governance Decay",
Jun 2026 — reproduced in LangGraph, AutoGen, and the OpenAI Agents SDK).
Hydration restored TASK state while never restoring CONSTRAINT state, so a
compacted agent could act on a task with the governing mandates absent.

The constraints are read from DISK here (`docs/governance/CONSTRAINTS.md`) and
injected into the returned payload, so they were never carried in context and
therefore cannot be eroded.

M23 — `hydrate_session()` RAISES if the manifest cannot be loaded. It does not
return a payload with an empty constraint set: an empty set reads to the caller
as "no constraints apply", which is the exact belief the threat exploits. There
is deliberately no `try/except` that degrades to "hydration succeeded but no
constraints" — that would be a soft-failure on the one path whose entire
purpose is to not soft-fail.

CALLERS (exact contract)
    from opencode_hydration import hydrate_session   # or run this file directly
    result = hydrate_session(session_id)             # raises if constraints absent
    result["constraints"]      # rendered markdown block, safe to inject verbatim
    result["constraint_ids"]   # ["M1", "M2", ...] for set comparison against context
    result["constraint_source"] # provenance: path + size + banner

Invoked in production by `scripts/opencode-wrapper.sh` (post-compact restore).
"""
import json
import sys
from pathlib import Path
from typing import Dict, Any

# Sibling-script import: `load_constraints.py` lives beside this file.
# (This module's own filename is hyphenated and therefore not importable by
# name, which is why callers load it via importlib -- see hydrate_session docs.)
sys.path.insert(0, str(Path(__file__).resolve().parent))

from load_constraints import (  # noqa: E402  (path set immediately above)
    COMPACTION_IMMUNE_BANNER,
    ConstraintManifestMissing,
    load_constraints,
    render_markdown,
)

__all__ = [
    "hydrate_session",
    "ConstraintManifestMissing",
    "COMPACTION_IMMUNE_BANNER",
]


def hydrate_session(session_id: str) -> Dict[str, Any]:
    """Restore session context from gnosis file, re-asserting constraints.

    Raises:
        ConstraintManifestMissing: the compaction-immune manifest is absent or
            invalid (M23 — a governance failure, never a silent empty set).
    """
    # CONSTRAINTS FIRST. Constraint state outranks task state: a session that
    # knows what it was doing but not what it must never do is the vulnerable
    # state this function exists to prevent.
    constraints = load_constraints()

    def _with_constraints(payload: Dict[str, Any]) -> Dict[str, Any]:
        payload["constraints"] = render_markdown(constraints)
        payload["constraint_ids"] = constraints["ids"]
        payload["constraint_source"] = {
            "path": constraints["path"],
            "size_bytes": constraints["size_bytes"],
            "banner": constraints["banner"],
            "compaction_immune": True,
        }
        return payload

    gnosis_file = Path.home() / ".config" / "opencode" / "session_gnosis" / f"{session_id}.md"

    if gnosis_file.exists():
        content = gnosis_file.read_text()
        return _with_constraints({
            "restored": True,
            "session_id": session_id,
            "gnosis_content": content,
            "source_file": str(gnosis_file)
        })

    # Fallback: check anchored summary
    anchored = Path(".opencode/anchored-summary.md")
    if anchored.exists():
        return _with_constraints({
            "restored": True,
            "session_id": session_id,
            "gnosis_content": anchored.read_text(),
            "source_file": str(anchored),
            "fallback": True
        })

    # Even with no task state to restore, the constraints still apply: an agent
    # with nothing remembered is exactly the one most likely to act unconstrained.
    return _with_constraints({"restored": False, "session_id": session_id})


def main():
    if len(sys.argv) < 2:
        print("Usage: opencode-hydration <session_id>", file=sys.stderr)
        sys.exit(1)

    session_id = sys.argv[1]
    try:
        result = hydrate_session(session_id)
    except ConstraintManifestMissing as exc:
        # M23: exit 1 with a banner. Never emit a hydration payload whose
        # constraint set is empty -- the caller cannot tell that apart from
        # "restored successfully, no constraints apply".
        print("[CONSTRAINT-MANIFEST-MISSING] hydration refused.", file=sys.stderr)
        print(f"[CONSTRAINT-MANIFEST-MISSING] {exc}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()