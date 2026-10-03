#!/bin/sh
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
#
# ⬡ OMEGA ⬡ DOOM_GUY ⬡ S1 ⬡ omega-research-parked
#
# WHY THIS EXISTS
#   omega-research.service previously pointed ExecStart at
#     omega.workers.background_researcher.run
#   That package was deliberately RETIRED on 2026-07-30 (commit 704c5028,
#   "C-6' Unification" — circuit-breaker clones were never migrated). The
#   unit and its 20-minute timer were never disabled to match, so systemd
#   re-launched the dead target every 30 seconds for 62 days, producing
#   46.9 MB of traceback noise in a flat file.
#
#   This stub is what the parked unit executes instead. It refuses to run,
#   states exactly why, and exits 4 — the status the unit declares in
#   RestartPreventExitStatus, so systemd does NOT restart and the loop is
#   structurally impossible while the unit is parked.
#
# EXIT CODES (consumed by RestartPreventExitStatus in the unit)
#   3 — ModuleNotFoundError class: venv/package broken, needs `pip install -e .`
#   4 — ConfigurationError class: no research daemon is wired to this unit
#
# WHEN YOU DELETE THIS FILE
#   Only when the Architect has ruled on which research module owns the
#   background-researcher daemon slot. That decision is NOT S1's to make.
#   See: docs/federation/ (Antigravity Stage-3 ruling, 2026-09-30) —
#   "A patch that does not stop the crash loop it describes is not a fix."

echo "omega-research.service is PARKED." >&2
echo "" >&2
echo "  No research daemon is wired to this unit." >&2
echo "  Target 'omega.workers.background_researcher.run' was retired on" >&2
echo "  2026-07-30 (commit 704c5028, C-6' Unification) and archived to" >&2
echo "  archive/research_pipeline_20260730/ (4,204 lines, DEPRECATED)." >&2
echo "" >&2
echo "  This is deliberate, not a missing file. Exiting 4 (ConfigurationError)." >&2
echo "  systemd will not restart this unit: 4 is in RestartPreventExitStatus." >&2
echo "" >&2
echo "  To restore a live researcher: Architect must name the owning module." >&2
echo "  Candidates are NOT interchangeable — all three currently on disk are" >&2
echo "  library components, not daemons:" >&2
echo "    - omega.library.research           (ResearchEngine class, depth levels)" >&2
echo "    - omega.oracle.iterative_research  (IterativeResearcher component)" >&2
echo "    - omega.model_registry.research    (21 lines of dataclasses)" >&2
echo "" >&2
echo "  Operator notes: scripts/omega-research-parked.sh" >&2

exit 4