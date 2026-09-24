# Ponytail — Integration Guide for Omega Engine

## Quick Start

```bash
# 1. Copy plugin files to Omega Engine's plugin directory
cp -r omega-ponytail/plugin/* $OMEGA_ENGINE_ROOT/.opencode/plugins/

# 2. Copy skills
cp -r omega-ponytail/plugin/SKILL.md $OMEGA_ENGINE_ROOT/.opencode/skills/ponytail/SKILL.md

# 3. Copy commands
cp omega-ponytail/plugin/*.toml $OMEGA_ENGINE_ROOT/.opencode/command/

# 4. Register plugin in opencode.json
# Add to your opencode.json:
# {
#   "plugin": ["omega-ponytail"]
# }
```

## Plugin Registration

Add to `opencode.json`:

```json
{
  "plugin": ["omega-ponytail"],
  "agent": {
    "permission": {
      "skill": {
        "ponytail-*": "allow"
      }
    }
  }
}
```

## Skills Directory

Ensure the skills directory is registered in OpenCode config:

```json
{
  "skills": {
    "paths": [".opencode/skills", "~/.config/opencode/skills"]
  }
}
```

The Ponytail plugin auto-registers its skills directory:

```javascript
config.skills.paths = config.skills.paths || [];
config.skills.paths.push(ponytailSkillsDir);
```

## Commands

Copy command files to OpenCode's command directory:

```bash
cp *.toml $OMEGA_ENGINE_ROOT/.opencode/command/
```

Commands available:
- `ponytail.toml` → `/ponytail [lite|full|ultra|off]`
- `ponytail-review.toml` → `/ponytail-review`
- `ponytail-audit.toml` → `/ponytail-audit`
- `ponytail-debt.toml` → `/ponytail-debt`
- `ponytail-gain.toml` → `/ponytail-gain`
- `ponytail-help.toml` → `/ponytail-help`

## Hook Registration

The plugin registers two hooks automatically:

1. **`experimental.chat.system.transform`** — Injects ruleset into system prompt every turn
2. **`command.execute.before`** — Persists mode changes from `/ponytail` command

## Mode Persistence

Mode is stored in `.ponytail-active` file in OpenCode config directory:

```bash
# Location: ~/.config/opencode/.ponytail-active
# Content: single line (off|lite|full|ultra)
```

## Config Resolution

Mode resolution order:
1. `PONYTAIL_DEFAULT_MODE` environment variable
2. Config file: `~/.config/ponytail/config.json`
3. Default: `full`

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `PONYTAIL_DEFAULT_MODE` | Override default mode |
| `PONYTAIL_QUIET_STARTUP` | Hide startup toast |
| `PONYTAIL_HIDE_STATUS` | Hide status indicator |

## Verification Checklist

- [ ] Plugin loads: `opencode` starts without errors
- [ ] Mode injection: `/ponytail lite` → next turn uses lite rules
- [ ] Mode persistence: Restart OpenCode → mode persists
- [ ] Skill loading: `/ponytail-review` works
- [ ] Commands work: `/ponytail-help` shows help
- [ ] Config file: `~/.config/ponytail/config.json` respected
- [ ] Env var override: `PONYTAIL_DEFAULT_MODE=lite opencode`

## Skill Permissions

Configure skill permissions in `opencode.json`:

```json
{
  "permission": {
    "skill": {
      "ponytail-*": "allow"
    }
  }
}
```

Per-agent override:

```yaml
# In agent frontmatter
---
permission:
  skill:
    "ponytail-*": "allow"
---
```

Or in `opencode.json`:

```json
{
  "agent": {
    "code-reviewer": {
      "permission": {
        "skill": {
          "ponytail-*": "allow"
        }
      }
    }
  }
}
```

## Testing

```bash
# Test plugin loads
opencode --help | grep plugin

# Test mode switching
echo "/ponytail lite" | opencode
# Next message should use lite rules

# Test skill
echo "/ponytail-review" | opencode

# Test commands
echo "/ponytail-help" | opencode
```

## Integration with Omega Engine's Existing Systems

### With The Well

Ponytail can reference The Well corrections:
- Ponytail rules reference Well corrections by ID
- Well supersession chain mirrors Ponytail's "delete over addition"

### With Context Engineering Protocol

- Ponytail mode persists across compactions (state file survives)
- Gnosis-Leash injection includes Ponytail mode in context
- Pre-compaction ritual captures current Ponytail mode

### With Gnosis-Lock

- Pre-compaction ritual captures current Ponytail mode in git state
- Post-reflection, Ponytail mode restored from `.ponytail-active`

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Plugin not loading | Check `opencode.json` plugin array |
| Mode not persisting | Check `.ponytail-active` file permissions |
| Commands not found | Verify `.toml` files in `.opencode/command/` |
| Skills not found | Verify `SKILL.md` in `.opencode/skills/ponytail/` |
| Mode not injecting | Check `experimental.chat.system.transform` hook |

## License

MIT — see LICENSE in source repo.