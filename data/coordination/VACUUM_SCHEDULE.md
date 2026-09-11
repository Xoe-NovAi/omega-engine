# VACUUM Schedule for opencode.db

## Current State (2026-09-11)
- **DB Size**: 33.78 GB (8,857,291 pages × 4096 bytes)
- **Freelist**: 0 pages (0 GB reclaimable)
- **Disk Free**: 870 MB (100% used)
- **VACUUM Required Space**: ~34 GB
- **Status**: BLOCKED — DB locked by active opencode process (PID 8691)

## Blocker Analysis
1. **DB Locked**: Current opencode session holds write lock (PID 8691)
2. **Disk Full**: 870 MB free, need ~34 GB for VACUUM
3. **No Freelist**: 0 pages = no internal fragmentation to reclaim

## Resolution Path
1. **Immediate**: Cannot VACUUM while session active
2. **Post-Session**: After opencode exits, run VACUUM (will need to free ~34 GB first)
3. **Space Recovery Options**:
   - Archive old sessions via `opencode-sessions-explorer-unarchive` / session export
   - Move DB to larger partition (if available)
   - Delete oldest sessions (keep last N sessions)
4. **Long-term**: Enable auto-VACUUM or schedule periodic maintenance

## Next Steps
- [ ] Document VACUUM as post-session task
- [ ] Investigate session archival to reduce DB size
- [ ] Monitor disk space after session ends
- [ ] Run VACUUM when 34+ GB free available

## Related
- `opencode-sessions-explorer` tools for session management
- `data/coordination/SESSION_ANCHOR.md` for session continuity
- M23 Failure Integrity: disk-full = hard blocker

---
*Generated: 2026-09-11 by Grokster CSS Turn 5*
