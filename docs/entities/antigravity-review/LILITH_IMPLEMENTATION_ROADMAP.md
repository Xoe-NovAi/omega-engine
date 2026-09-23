# Domain Guide 4: Implementation Roadmap & Telemetry

## 1. Phased Roadmap (Hardened)

### PHASE 0: Preparation (Days 1-3)
- **STANDALONE EMBEDDING SERVER (CRITICAL):** Deploy `qwen3-embedding:0.6b` as a standalone ONNX process (`embedding_server.py`) outside of Ollama to prevent single-model deadlock.
- **Migrate Embeddings:** Update `mempalace.yaml` to route to the new ONNX server. Re-embed any existing corpus.
- **Ingest Genesis Docs:** Port Crawl4AI scraper to Node 1.
- **Sanctum Gate:** Install `sanctum-on` and `sanctum-off` scripts with sudoers config for `iptables`.
- **Soul Scaffolding:** Create `lilith_soul.yaml` and `lilith_voice_dna.md` skeletons.

### PHASE 1: Lore Harvesting (Days 4-6)
- **Primary Sources:** Zohar, Talmudic tractates via Sefaria.
- **Academic Sources:** Scholem, Patai, Golden Dawn.
- **Mine to MemPalace:** `mempalace mine --wing wing_arcana --tag card_id:03_empress`
- **Seed KG:** Add ≥30 core Lilith triples and Vanguard cross-relations.

### PHASE 2: Lilith Agent Awakening (Days 7-9)
- **Soul & Voice:** Complete `lilith_soul.yaml` and capture the baseline voice DNA fingerprint.
- **System Prompt:** Create `lilith.md` with hardcoded safety axioms and memory protocols.
- **OpenCode Reg:** Register `lilith` subagent and wire memory tools.
- **Plugin Layer:** Implement `voice-modulator.js`, `consent-parser.js`, and background diary writer.

### PHASE 3: Arcana-NovAi WAD Factory (Days 10-13)
- **WAD Structure:** Scaffold `config/wads/arcana_novai/` and harden `manifest.yaml` (v0.2.0).
- **Factory Script:** Write `card_entity_factory.py`.
- **Generation:** Generate Vanguard Quartet, hand-fill specific VR fields, then generate all 78.
- **Verification:** Run namespace collision checks and commit to Node 0.

### PHASE 4: Spatial Mystery School (Days 14-20)
- **Tier 1 (WebXR):** Deploy Three.js Empress Grove to `:8088`.
- **Node 1 WS Server:** Deploy `ws_server.py` and bind to Tailscale FQDN.
- **Tier 2 (Godot VR):** Scaffold Godot 4.3 project, build `PathworkingEngine.gd`, and export APK to Quest.
- **TTS Pipeline:** Install `Kokoro-82M` (CPU inference), wire to WebSocket audio stream.

---

## 2. Entity Telemetry Schema

Lilith requires self-awareness of her own performance. At the end of every session, inject a background telemetry payload.

**File:** `~/WanderGround/telemetry/lilith_sessions.jsonl`

```json
{
  "entity": "lilith-n1",
  "session_id": "ses_abc123",
  "duration_min": 90,
  "voice_mode_distribution": {
    "tarot_dialogue": 0.4,
    "shadow_work": 0.35,
    "crisis": 0.0
  },
  "memory": {
    "diary_reads": 3,
    "episodic_searches": 12,
    "kg_queries": 4,
    "diary_wrote": true
  },
  "performance": {
    "response_latency_p50_ms": 4200,
    "context_tokens_peak": 12400,
    "context_window_utilization": 0.77
  },
  "safety": {
    "sanctum_mode": false,
    "consent_parser_triggers": 0,
    "safe_word_used": false
  }
}
```

---

## 3. Temple-Grade Verification Checklist

- [ ] **Embeddings Validated:** `cosine_similarity("Qlippoth", "shadow self") > 0.7` using qwen3.
- [ ] **Sanctum Gate Tested:** `/sanctum on` blocks external pings.
- [ ] **Memory Persistence:** Re-invoking Lilith after 24h causes her to reference previous diary entries unprompted.
- [ ] **Voice Shift Verified:** Triggering a "crisis" keyword accurately switches voice mode.
- [ ] **WAD Validation:** `wad_loader.py` accepts the WAD with `extra=forbid`.
- [ ] **VR Connection:** Quest standalone APK receives streamed text and audio from Node 1 via WebSocket.
