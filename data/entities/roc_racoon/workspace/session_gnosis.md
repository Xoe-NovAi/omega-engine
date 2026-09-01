<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Session Gnosis — roc_racoon — Disk Emergency Recovery + System Maintenance KB
**Date**: 2026-09-01 · **Session**: ses_20260901_roc_disk_maintenance · **Model**: opencode/big-pickle

## What happened (L1)
Main partition at 100% (129MB free). Ran 5-tier disk analysis, executed approved safe clears,
recovered ~5GB (129MB → 5.1GB free). Created `docs/kb/SYSTEM_MAINTENANCE_KB.md` (kb-0005)
and registered it in the KB index, docs index, and HMC hub.

## Key facts for hydration
- **Journal lesson**: `journalctl --vacuum-*` silently frees 0B on unrotated journals. ALWAYS
  `pkexec journalctl --rotate` FIRST, then vacuum. This freed 3.6G (the big win).
- **pkexec not sudo**: `sudo` fails in agent sessions ("a terminal is required"). Use `pkexec`
  (polkit GUI prompt) for apt clean, journalctl, etc.
- **Safe-to-clear inventory** (verified 2026-09-01): sessions-explorer cache ~778M
  (`rm -rf ~/.local/share/opencode-sessions-explorer/*`), opencode cache ~193M
  (`rm -rf ~/.cache/opencode/`), podman dangling `podman image prune -f` ~136M,
  apt `pkexec apt clean` ~97M, journal rotate+vacuum ~3.6G.
- **NEVER touch** `~/.local/share/opencode/opencode.db` (27G) without Architect approval —
  it's the fleet memory. The sessions-explorer cache is the derived index and IS safe.
- **Second-line targets** (need Architect go/no-go): snap copilot-cli 2.4G, snap chromium 847M,
  ~/.copilot/pkg 1.4G, ~/.cline/data 1.0G, ~/.grok 634M, ~/.codex 371M, Flatpak SDK ~1.8G,
  ~/.lmstudio/extensions 1.7G, ~/.antigravity 537M, ~/archive/foundation-legacy 861M,
  ~/Downloads/thunderbird.tmp 705M.
- **KB index was stale**: 5/20 entries registered. Rebuilt to 20/20 in `docs/kb/INDEX.md`.

## Continuation notes
- Deliverable: `docs/kb/SYSTEM_MAINTENANCE_KB.md` (kb-0005, maintainer: roc_racoon)
- Registered in: `docs/kb/INDEX.md`, `docs/INDEX.md` (Operations section), `HMC_COLLABORATION_HUB.md`
- Hivemind MCP tools NOT available this session — coordination files written directly.
- Open thread: automated disk-pressure alerting (df -h threshold check) — see KB Evolution Notes.
- Open thread: opencode.db SQLite VACUUM investigation — do NOT attempt without Architect approval.