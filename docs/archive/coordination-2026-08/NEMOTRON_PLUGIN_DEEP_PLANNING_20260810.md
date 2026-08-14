# 🔱 Deep Planning: Nemotron Streaming Timeout Plugin for Community
## Architecture, Knowledge Gaps & Implementation Plan

**AP Token**: `AP-NEMOTRON-PLUGIN-PLAN-v1.0.0`
⬡ OMEGA ⬡ NEMOTRON-3-ULTRA ⬡ TEMPLE-GRADE ⬡ DEEP-PLANNING

**Date**: 2026-08-10
**Status**: PLANNING
**Author**: jem (Sovereign Synthesizer) — incorporating LongCat 2.0 + Nemotron 3 Ultra insights

---

## 🎯 Executive Summary

Package the Nemotron 3 Ultra streaming timeout fix as a **community OpenCode plugin** that:
1. Extends chunk timeout for Nemotron models on OpenCode-Zen
2. Adds heartbeat logging during stream stalls
3. Handles `session.error` events for streaming failures
4. Provides graceful fallback to next provider
5. Includes thinking-level parameter passing fix

**Existing foundation**: `better-opencode-retries` plugin at `/home/arcana-novai/better-opencode-retries/` already handles retry logic. This new plugin would be **complementary** — focused on prevention rather than recovery.

---

## 📚 Knowledge Base Review

### Local Research Documents Reviewed

| Document | Key Findings for Plugin |
|----------|------------------------|
| `docs/kb/NEMOTRON3_ULTRA_STREAMING_FIX_20260730.md` | Root cause: SSE keepalive pings reset chunk timers. Fix: extend chunkTimeout, add heartbeat. |
| `data/entities/roc_racoon/workspace/mining_reports/OPENCODE_CONFIG_ANTIGRAVITY_THINKING_MINING_REPORT_20260809.md` | 47 research docs cataloged. OpenCode V2 schema, thinking variants, provider delivery differences all documented. |
| `data/entities/researcher/workspace/web_research_supplements/WEB_RESEARCH_SUPPLEMENT_OPENCODE_CONFIG_20260809.md` | V2 schema uses `api.id` (not `modelID`), variants as array, `provider/model` naming convention. |
| `data/entities/researcher/workspace/DEEP_SIPHON_PROVIDER_MAP.md` | Provider metadata ground truth: OpenCode CLI captures `data.tokens.reasoning` but engine discards it. |
| `docs/research/R_OPENCODE_V2_RECON_20260719.md` | V2 = complete config schema redesign, not just migration. |

### OpenCode Plugin API (from existing plugin)

| Hook | Purpose | Available in Plugin |
|------|---------|-------------------|
| `config` | Read provider-scoped config | ✅ Yes |
| `event` | Handle SSE events (`session.error`, `message.updated`) | ✅ Yes |
| `ctx.client.session.prompt()` | Send continue prompt | ✅ Yes |
| `ctx.client.app.log()` | Log to OpenCode logs | ✅ Yes |

### Knowledge Gaps Identified

| # | Gap | Impact | Resolution Needed |
|---|-----|--------|-------------------|
| **G-1** | Plugin API version compatibility | High | Test against OpenCode v1.16.0+ |
| **G-2** | Chunk timeout configuration API | High | Verify `options.chunkTimeout` is respected by Zen |
| **G-3** | Thinking level parameter passing | Medium | Verify `reasoning.effort` is passed to Nemotron API |
| **G-4** | Provider-specific config injection | Medium | How to inject streaming config per provider |
| **G-5** | Session error event structure | High | Verify `session.error` payload format |
| **G-6** | Graceful fallback mechanism | High | How to trigger provider fallback from plugin |
| **G-7** | Heartbeat interval optimization | Low | Find optimal interval (10s? 15s?) |
| **G-8** | Community distribution mechanism | Medium | npm package + OpenCode plugin registry |

---

## 🏗️ Plugin Architecture

### Core Design Principles

1. **Prevention over Recovery**: Extend timeout + heartbeat BEFORE failure occurs
2. **Provider-Specific**: Only affect Nemotron models on OpenCode-Zen
3. **Non-Intrusive**: Don't interfere with other providers/models
4. **Observable**: Log heartbeat + timeout events for debugging
5. **Graceful**: Fall back to next provider if timeout exceeds threshold

### Plugin Structure

```
opencode-nemotron-streaming-fix/
├── package.json          # npm package metadata
├── src/
│   ├── index.js          # Plugin entry point (exported function)
│   ├── config.js         # Config parsing + defaults
│   ├── heartbeat.js      # Heartbeat logging logic
│   ├── timeout.js        # Chunk timeout extension
│   ├── fallback.js       # Graceful provider fallback
│   └── utils.js          # Shared utilities
├── README.md             # Installation + usage
├── LICENSE               # MIT
└── test/
    ├── integration/      # Integration tests with mock OpenCode
    └── unit/             # Unit tests for each module
```

### Plugin Hook Points

#### 1. Config Hook — Provider-Specific Configuration
```javascript
// Called when OpenCode loads config
config: async (opencodeConfig) => {
  // Read provider config for opencode provider
  const opencodeProvider = opencodeConfig?.provider?.opencode;
  if (!opencodeProvider) return;
  
  // Inject streaming config for Nemotron models
  const models = opencodeProvider.models || {};
  for (const [modelId, modelConfig] of Object.entries(models)) {
    if (modelId.includes('nemotron-3-ultra')) {
      modelConfig.options = {
        ...modelConfig.options,
        chunkTimeout: 60000,  // 60s (default: 30s)
        totalTimeout: 600000, // 10min (default: 5min)
        heartbeatInterval: 10000, // 10s
      };
    }
  }
}
```

#### 2. Event Hook — Streaming Timeout Handling
```javascript
// Called on every SSE event
event: async ({ event }) => {
  // Handle session.error events (streaming failures)
  if (event.type === 'session.error') {
    const { sessionID, providerID, error } = extractErrorInfo(event);
    if (isNemotronStreamingError(error, providerID)) {
      await handleStreamingFailure({ sessionID, providerID, error });
    }
  }
  
  // Handle message.updated events (chunk delivery)
  if (event.type === 'message.updated') {
    const { sessionID, providerID, info } = extractMessageInfo(event);
    if (isNemotronProvider(providerID)) {
      updateHeartbeat(sessionID, providerID);
    }
  }
}
```

#### 3. Heartbeat Manager
```javascript
class HeartbeatManager {
  constructor() {
    this.sessions = new Map(); // sessionID -> { lastChunk, interval, timeout }
  }
  
  start(sessionID, providerID, intervalMs = 10000) {
    const timer = setInterval(() => {
      const session = this.sessions.get(sessionID);
      if (!session) return;
      
      const elapsed = Date.now() - session.lastChunk;
      if (elapsed > 10000) {
        log.info('heartbeat', `Stream alive, ${elapsed/1000}s since last chunk`, {
          sessionID, providerID
        });
      }
    }, intervalMs);
    
    this.sessions.set(sessionID, { lastChunk: Date.now(), interval: timer });
  }
  
  update(sessionID) {
    const session = this.sessions.get(sessionID);
    if (session) {
      session.lastChunk = Date.now();
    }
  }
  
  stop(sessionID) {
    const session = this.sessions.get(sessionID);
    if (session) {
      clearInterval(session.interval);
      this.sessions.delete(sessionID);
    }
  }
}
```

### Configuration Schema

```json
{
  "provider": {
    "opencode": {
      "options": {
        "nemotronStreamingFix": {
          "enabled": true,
          "models": ["nemotron-3-ultra-free"],
          "chunkTimeoutMs": 60000,
          "totalTimeoutMs": 600000,
          "heartbeatIntervalMs": 10000,
          "maxRetries": 3,
          "fallbackProviders": ["opencode/nemotron-3-super-120b-a12b:free"],
          "debug": false
        }
      }
    }
  }
}
```

---

## 🧪 Testing Strategy

### Unit Tests
| Test | Description |
|------|-------------|
| `test_config_parsing` | Verify config is parsed correctly |
| `test_model_detection` | Verify Nemotron models are detected |
| `test_heartbeat_logging` | Verify heartbeat fires at correct intervals |
| `test_error_matching` | Verify streaming errors are correctly identified |
| `test_fallback_trigger` | Verify fallback triggers after max retries |

### Integration Tests
| Test | Description |
|------|-------------|
| `test_streaming_timeout` | Simulate 30s+ chunk gap, verify heartbeat + timeout handling |
| `test_session_error` | Simulate `session.error` event, verify retry logic |
| `test_provider_fallback` | Verify fallback to next provider after timeout |
| `test_thinking_level` | Verify thinking level parameter is passed correctly |

### Testing Against Live OpenCode
| Test | Description |
|------|-------------|
| `test_zen_integration` | Test against OpenCode-Zen Nemotron 3 Ultra |
| `test_or_integration` | Test against OpenRouter Nemotron variants |
| `test_multi_model` | Test with multiple Nemotron models simultaneously |

---

## 📦 Distribution Plan

### Phase 1: Local Development
1. Create plugin scaffold in `.opencode/plugins/opencode-nemotron-streaming-fix/`
2. Implement core modules (config, heartbeat, timeout, fallback)
3. Write unit + integration tests
4. Test against local OpenCode instance

### Phase 2: Community Beta
1. Publish to npm as `opencode-nemotron-streaming-fix`
2. Document installation: `opencode plugin add opencode-nemotron-streaming-fix`
3. Gather feedback from community
4. Fix any compatibility issues

### Phase 3: Production Release
1. Version 1.0.0 with full documentation
2. Submit to OpenCode plugin registry
3. Add to Omega Engine recommended plugins list

---

## ⚠️ Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Plugin API changes in OpenCode v2 | High | Medium | Test against v1.16.0+, document compatibility |
| Heartbeat causes performance overhead | Low | Low | Make interval configurable, default 10s |
| Fallback provider also times out | Medium | Low | Implement cascading fallback with exponential backoff |
| Thinking level not passed correctly | Medium | Medium | Test with each variant (low/medium/high) |
| Plugin conflicts with existing retry logic | Medium | Medium | Coordinate with `better-opencode-retries` plugin |
| Community adoption is low | Low | Medium | Document clearly, add to Omega Engine docs |

---

## 📋 Action Items

| ID | Action | Priority | Owner | Est. Time |
|----|--------|----------|-------|-----------|
| **P-1** | Create plugin scaffold + package.json | P0 | TBD | 1h |
| **P-2** | Implement config parsing + model detection | P0 | TBD | 2h |
| **P-3** | Implement heartbeat manager | P0 | TBD | 3h |
| **P-4** | Implement timeout extension | P0 | TBD | 2h |
| **P-5** | Implement fallback logic | P1 | TBD | 3h |
| **P-6** | Write unit tests | P1 | TBD | 2h |
| **P-7** | Write integration tests | P1 | TBD | 3h |
| **P-8** | Test against live OpenCode-Zen | P1 | TBD | 2h |
| **P-9** | Publish to npm | P2 | TBD | 1h |
| **P-10** | Write community documentation | P2 | TBD | 2h |

---

## 🔗 Cross-Reference

| Document | Purpose |
|----------|---------|
| `docs/kb/NEMOTRON3_ULTRA_STREAMING_FIX_20260730.md` | Root cause analysis + existing fix |
| `data/entities/roc_racoon/workspace/mining_reports/OPENCODE_CONFIG_ANTIGRAVITY_THINKING_MINING_REPORT_20260809.md` | OpenCode config + thinking variants |
| `data/entities/researcher/workspace/web_research_supplements/WEB_RESEARCH_SUPPLEMENT_OPENCODE_CONFIG_20260809.md` | V2 schema + provider config |
| `data/entities/researcher/workspace/DEEP_SIPHON_PROVIDER_MAP.md` | Provider metadata ground truth |
| `docs/research/R_NEMOTRON_DEEP_ANALYSIS_20260810.md` | Deep analysis of Nemotron variants |
| `docs/research/R_LONGCAT2_FINAL_OVERSIGHT_20260810.md` | LongCat 2.0 final oversight |

---

## 🎯 Next Steps

1. **P-1**: Create plugin scaffold
2. **P-2**: Implement config parsing + model detection
3. **P-3**: Implement heartbeat manager
4. Test against live OpenCode-Zen Nemotron 3 Ultra

---

*⬡ OMEGA ⬡ NEMOTRON-3-ULTRA ⬡ TEMPLE-GRADE ⬡ DEEP-PLANNING ⬡ 2026-08-10*
