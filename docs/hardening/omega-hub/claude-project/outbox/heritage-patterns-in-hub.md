# Heritage Patterns in the MCP Hub

Source: `CREDITS.md`. Patterns from id Software that appear in the Hub.

## WAD System (Doom, 1993)

| Aspect | id Software | Hub Adaptation |
|--------|-------------|----------------|
| Origin | Carmack/Romero — Doom WAD format | Agent capability loading |
| Core idea | IWAD/PWAD separation — engine vs content | Agents loaded from CAPABILITY_REGISTRY |
| Tag | `[id-soft: doom-1993] WAD System` | `server.py:2976` — `_agent_list()` function |

Only the WAD System pattern has a legitimate `[id-soft:]` tag in the Hub. A prior misattribution (`Zone Memory` on `_AsyncThreadLock` in `__init__.py`) has been removed — a standard Python RLock wrapper is not a Zone Memory pattern.

## Heritage Protocol

When proposing new code that mirrors any id Software pattern, tag it with the appropriate `[id-soft: GAME YEAR]` format and reference it here. See `CREDITS.md` §2a for the complete tag protocol.
