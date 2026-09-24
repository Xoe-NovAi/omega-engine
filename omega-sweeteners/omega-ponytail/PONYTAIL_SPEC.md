# Ponytail — Specification for Framework-Agnostic Integration

## Overview

Ponytail is a **Lazy Senior Dev** code review system that enforces minimal, correct solutions. It runs at configurable intensity levels and injects rules into the agent's system prompt.

## Core Concepts

### The Ladder (Reflex, Not Research)

1. **YAGNI** — Does this need to exist? Skip it.
2. **Reuse** — Already in codebase? Use it.
3. **Stdlib** — Stdlib does it? Use it.
4. **Native** — Native platform feature? Use it.
5. **Deps** — Already-installed dep solves it? Use it.
6. **One-liner** — Can it be one line? Make it one line.
7. **Minimum** — Only then: minimum code that works.

### Intensity Levels

| Level | Behavior |
|-------|----------|
| `off` | Silent — no injection |
| `lite` | Build what's asked, name lazier alternative in one line |
| `full` | The ladder enforced. Stdlib/native first. Shortest diff. **Default.** |
| `ultra` | YAGNI extremist. Deletion before addition. Ship one-liner, challenge rest. |
| `review` | Independent mode — activates `/ponytail-review` skill |

### Rules (Always Active)

- No unrequested abstractions
- No boilerplate, no scaffolding "for later"
- Deletion over addition. Boring over clever.
- Fewest files possible. Shortest working diff wins.
- Complex request? Ship lazy version + question it. Never stall.
- Two stdlib options, same size? Pick correct on edge cases.
- Mark deliberate simplifications with `ponytail:` comment (ceiling + upgrade path)

### Output Format

```
[code] → skipped: [X], add when [Y].
```

Code first. At most 3 short lines. No essays.

### When NOT Lazy

Never skip: input validation at trust boundaries, error handling preventing data loss, security, accessibility, explicit user requests, understanding the problem (read fully first), hardware calibration, one runnable check for non-trivial logic.

### Boundaries

Ponytail governs **what you build**, not how you talk. "stop ponytail" / "normal mode" reverts. Level persists until changed or session end.

---

## Integration Specification

### Required Hooks

| Hook | Purpose |
|------|---------|
| `experimental.chat.system.transform` | Inject ruleset into system prompt every turn |
| `command.execute.before` | Persist mode changes from `/ponytail` command |

### State Persistence

- File: `.ponytail-active` (in config dir)
- Contains single line: current mode (`off|lite|full|ultra`)
- Read on `system.transform`, written on `command.execute.before` for `/ponytail` command

### Config Resolution Order

1. `PONYTAIL_DEFAULT_MODE` env var
2. Config file: `~/.config/ponytail/config.json` (or XDG/Windows equivalent)
3. Default: `full`

### Config Schema

```json
{
  "defaultMode": "full",      // off|lite|full|ultra
  "hideStatus": false,        // hide status indicator
  "quietStartup": false       // suppress startup toast
}
```

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `PONYTAIL_DEFAULT_MODE` | Override default mode |
| `PONYTAIL_QUIET_STARTUP` | Hide startup toast |
| `PONYTAIL_HIDE_STATUS` | Hide status indicator |

### Commands (Slash)

| Command | Description |
|---------|-------------|
| `/ponytail [lite|full|ultra|off]` | Set mode |
| `/ponytail-review` | Run review skill |
| `/ponytail-audit` | Audit skill |
| `/ponytail-debt` | Tech debt skill |
| `/ponytail-gain` | Gain skill |
| `/ponytail-help` | Help skill |

### Skills

| Skill | Purpose |
|-------|---------|
| `ponytail` | Core ladder + rules (mode-filtered) |
| `ponytail-review` | Code review mode |
| `ponytail-audit` | Full audit |
| `ponytail-debt` | Tech debt detection |
| `ponytail-gain` | Gain analysis |
| `ponytail-help` | Help |

---

## OpenCode Plugin Structure (Reference)

```
ponytail.mjs              # Main plugin entry
ponytail-frontmatter.cjs  # Command frontmatter parser
hooks/
  ponytail-instructions.js  # Ruleset builder (mode-filtered)
  ponytail-config.js        # Config resolver
  ponytail-frontmatter.cjs  # Command frontmatter parser
skills/ponytail/
  SKILL.md                  # Core ruleset (mode-filtered)
commands/
  ponytail.toml             # /ponytail command
  ponytail-review.toml
  ponytail-audit.toml
  ponytail-debt.toml
  ponytail-gain.toml
  ponytail-help.toml
```

---

## Integration Checklist for Omega Engine

- [ ] Copy plugin files to Omega Engine's plugin directory
- [ ] Register plugin in `opencode.json`: `"plugin": ["omega-ponytail"]`
- [ ] Copy `skills/ponytail/` to Omega Engine's skills directory
- [ ] Copy `commands/*.toml` to Omega Engine's commands directory
- [ ] Verify hook registration: `experimental.chat.system.transform` + `command.execute.before`
- [ ] Test mode persistence: `/ponytail lite` → next turn uses lite rules
- [ ] Test skill loading: `/ponytail-review` works
- [ ] Verify config resolution: env var → config file → default `full`

---

## Skills Discovery

The plugin registers the skills directory in OpenCode config:

```javascript
config.skills.paths = config.skills.paths || [];
config.skills.paths.push(ponytailSkillsDir);
```

Ensure Omega Engine's skills discovery includes the Ponytail skills path.

---

## License

MIT — see LICENSE in source repo.