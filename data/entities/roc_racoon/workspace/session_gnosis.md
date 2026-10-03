<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Session Gnosis — roc_racoon — Routine Disk Maintenance (Cycle 6)
**Date**: 2026-09-17 · **Session**: ses_20260917_roc_disk_maintenance · **Model**: opencode/big-pickle

## What happened (L1)
Root at 98% (2.1G free). Journal 1G. Caches regrown: tracker3 321M, opencode 292M, pip 321M,
gnome-software 78M, flatpak 7.5M, npm 475M, shaders/gstreamer ~7M. Executed journal
rotate+vacuum (freed 877.5M) + full cache clear. Result: 2.1G → 4.2G free (96%).
Journal 192.7M, cache 1.1M.

## Key facts for hydration
- **Journal lesson**: `journalctl --vacuum-*` silently frees 0B on unrotated journals. ALWAYS
  `pkexec journalctl --rotate` FIRST, then vacuum. This freed 877.5M.
- **Cache regrowth cycle**: tracker3, opencode, pip, npm, gnome-software, flatpak all
  rebuild within 3-5 days. Weekly rotate+vacuum + cache clear is the cadence.
- **opencode.db = 36G+ and growing** — the structural pressure. Vacuum deferred (needs Architect + omega_library staging).
- **~/.lmstudio data (2.1G) + ~/Local Sites remain** — apps purged, data kept. Ask user.

## Continuation notes
- Deliverable: routine maintenance cycle 6 complete
- Lessons: PL-ROC-402-009 (L3-JournalRotateIsTheLever, L3-CacheRegrowthIsPredictable, L3-DbIsTheHull)
- Open: opencode.db vacuum plan (Architect approval), ~/.lmstudio data purge (user decision)
- Open: automate weekly journal rotate+vacuum per KB cadence