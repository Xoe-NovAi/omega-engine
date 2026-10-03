# GNOSIS-LOCK SKILL

**File:** `~/.config/opencode/skills/gnosis-lock/SKILL.md`

## Flow
1. Run ritual → creates pack (manifest + git_state + config_state + mcp_state + system_state + evolution_event)
2. Read identity → current_session
3. **Dynamic reflection via `question` tool:** 3 core (Decision, Pattern, Gnosis) + session-specific (0–10+)
4. Write narrative.md (replaces TODO with human answers)
5. **Step 4b:** Flip manifest → reflected + reflected_at + ready_for_compaction=true + clear pending_pack
6. **Step 4c:** Well sweep → extract corrections → `make well-add`
7. Commit gnosis records
