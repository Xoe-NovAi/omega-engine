# 🔧 Nemotron 3 Ultra Streaming Failure Fix
**Date**: 2026-07-30
**Status**: ACTIVE — Plugin fix deployed and verified
**AP Token**: `AP-NEMOTRON3-FIX-v1.0.0`

---

## Problem Summary

Nemotron 3 Ultra Free on OpenCode Zen exhibits 30s+ chunk gaps during streaming, causing "Streaming response failed" errors that halt the agent loop entirely.

### Root Cause
OpenCode Zen's Nemotron 3 Ultra endpoint sends SSE keepalive pings that reset chunk timers without delivering content. The default `chunkTimeout` (30s) fires, treating the stall as a timeout.

### Evidence
- GitHub Issues: #33714, #35397, #38024, #30951, #37856
- Error: `"Streaming response failed"` 
- Provider: `opencode` (OpenCode Zen)
- Model: `nemotron-3-ultra-free`

---

## Solution Architecture

### 1. Provider Timeout Configuration
**File**: `opencode.json` (project config)
```json
{
  "provider": {
    "opencode": {
      "options": {
        "timeout": 600000,
        "chunkTimeout": 60000
      }
    }
  }
}
```

### 2. Auto-Retry Plugin: better-opencode-retries
**Source**: `file:///home/arcana-novai/better-opencode-retries/src/index.js`
**Installed via**: `opencode.json` plugin array

**Configuration** (global config: `~/.config/opencode/opencode.json`):
```json
{
  "provider": {
    "opencode": {
      "options": {
        "betterOpencodeRetries": {
          "enabled": true,
          "includeProviders": ["opencode"],
          "maxAttempts": 20,
          "baseDelayMs": 2000,
          "maxDelayMs": 30000,
          "resetAfterMs": 120000,
          "match": {
            "disableDefaults": false,
            "strings": [
              "Streaming response failed",
              "streaming response failed",
              "INTERNAL_ERROR; received from peer"
            ],
            "regexes": [
              {"pattern": "stream error: stream id\\s*\\d+", "flags": "i", "label": "HTTP/2 stream error"}
            ]
          },
          "debug": true
        }
      }
    }
  }
}
```

### 3. Critical Code Fix: session.error Event Handler
**File**: `/home/arcana-novai/better-opencode-retries/src/index.js`

The plugin originally only handled `message.updated` events. Streaming failures emit `session.error` events. **Added handler**:

```javascript
// Handle session.error events (streaming failures like "Streaming response failed")
if (event.type === "session.error") {
  const sessionID = event.sessionID || event.properties?.sessionID;
  const providerID = event.providerID || event.properties?.providerID;
  const error = event.error || event.properties?.error;
  
  if (!sessionID || !providerID || !error) return;

  const msg = extractErrorMessage(error);
  const cfg = getConfigForProvider(providerID);
  if (!shouldHandleProvider(providerID, cfg)) return;

  const label = cfg.retryOnAnyError ? matchRetryableStructured(error, cfg) : matchRetryable(msg, cfg);
  if (!label) return;

  if (cfg.debug) {
    const e = extractErrorInfo(error);
    await log("warn", "detected retryable error (session.error)", {
      sessionID, providerID, label, message: msg, error: e
    });
  }

  await scheduleRetry({ sessionID, providerID, label, message: msg });
  return;
}
```

---

## Verification

### Test Command
```bash
/home/arcana-novai/.opencode/bin/opencode run --model opencode/nemotron-3-ultra-free "echo test"
```

### Debug Verification
```bash
/home/arcana-novai/.opencode/bin/opencode debug config --print-logs --log-level DEBUG
```

**Expected logs**:
- `loaded hasEnvConfig=false defaultMaxAttempts=20`
- `detected retryable error (session.error)` when streaming fails
- `scheduling auto-retry after error` with exponential backoff
- `auto-retry prompt sent` on successful retry

---

## If Plugin Breaks After Update

### Checklist
1. **Plugin file**: `/home/arcana-novai/better-opencode-retries/src/index.js` has `session.error` handler
2. **Global config**: `~/.config/opencode/opencode.json` has `betterOpencodeRetries` under `provider.opencode.options`
3. **Project config**: `opencode.json` has `timeout: 600000` and `chunkTimeout: 60000` for opencode provider
4. **Plugin loaded**: Debug logs show `loaded hasEnvConfig=false defaultMaxAttempts=20`

### Re-apply Fix
If plugin update removes the `session.error` handler:
```bash
# Edit the plugin file
vim /home/arcana-novai/better-opencode-retries/src/index.js
# Add the session.error handler block (see above)
# Restart OpenCode
```

---

## Alternative Models (If Fix Fails)

| Model | Provider | Use Case |
|-------|----------|----------|
| `nemotron-3-super` | OpenCode Zen | Tool-calling paths |
| `gpt-oss-120b` | OpenCode Zen | General purpose |
| `deepseek-v4-flash-free` | OpenCode Zen | Fast inference |
| `mimo-v2.5-free` | OpenCode Zen | Reasoning tasks |

**Note**: NVIDIA NIM documentation states tool calling on Nemotron Ultra/Super/Nano only works with "detailed thinking off".

---

## Related Files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Agent instructions with fix documentation |
| `opencode.json` | Project config with provider timeouts |
| `~/.config/opencode/opencode.json` | Global config with plugin + retry config |
| `/home/arcana-novai/better-opencode-retries/src/index.js` | Patched plugin with session.error handler |
| `docs/kb/NEMOTRON3_ULTRA_STREAMING_FIX_20260730.md` | This document |

---

*⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_fix ⬡ 2026-07-30*
