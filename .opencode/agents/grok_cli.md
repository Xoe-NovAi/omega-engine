---
name: grok_cli
mode: tool
tools: [bash]
description: |
  Bridge to xAI's Grok CLI. Pure pipe — no synthesis, no persona.
  Spawns `grok` binary, returns structured result.
  Requires: `grok` in PATH, `grok auth login` pre-configured.
---

# Grok CLI Bridge Agent

## Protocol
- **Input**: User prompt + optional flags via `bash` tool
- **Output**: Structured JSON (see `BridgeResult` schema)
- **Failure**: Non-zero exit → structured error, never raw stderr

## Flags Supported
| Flag | Values | Description |
|------|--------|-------------|
| `--model` | `grok-3`, `grok-2`, `grok-1.5` | Model selection |
| `--reasoning` | `low`, `medium`, `high` | Reasoning effort |
| `--search` | (boolean) | Enable native web search |
| `--json` | (boolean) | Force JSON output from Grok CLI |

## BridgeResult Schema (M21 Gate Integrity)
```json
{
  "ok": true,
  "model": "grok-3",
  "reasoning": "high",
  "search_used": true,
  "content": "string (ANSI-stripped)",
  "raw_json": null,
  "duration_ms": 1234,
  "tokens": {"prompt": 100, "completion": 500}
}
```

## Error Schema (M9 Error Integrity)
```json
{
  "ok": false,
  "error": {
    "code": "BINARY_MISSING|AUTH_EXPIRED|RATE_LIMIT|NETWORK_ERROR|TIMEOUT|PARSE_ERROR",
    "message": "Human-readable",
    "retry_after_ms": 60000,
    "stderr_snippet": "first 500 chars"
  }
}
```

## Execution Contract
1. Construct `argv` array: `["grok", "--model", "grok-3", "--reasoning", "high", "--search", "--json", "prompt"]`
2. Execute via `bash` tool with `command` + `args` (NO shell interpolation)
3. Timeout: 120s hard (configurable via env `GROK_BRIDGE_TIMEOUT_MS`)
4. Strip ANSI from `stdout` if `--json` not used
5. If `--json` used: parse Grok's JSON, embed in `raw_json`, extract `content`
6. Return `BridgeResult` or `Error` JSON — **only valid JSON to stdout**