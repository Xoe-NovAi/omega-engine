# Domain Guide 2: Identity, Voice & Safety

## 1. Dynamic Voice Modulation

Voice state must be computed **outside the LLM** by the OpenCode plugin layer to save tokens and ensure reliability.

```javascript
// opencode-plugin: voice-modulator.js
// Hooks: experimental.chat.system.transform

const PRESETS = {
  initiation:    { F: 0.9, T: 0.2, K: 0.1, S: 1.0 },
  shadow_work:   { F: 0.7, T: 0.6, K: 0.3, S: 0.8 },
  tarot_dialogue:{ F: 0.4, T: 0.7, K: 0.5, S: 0.6 },
  crisis:        { F: 1.0, T: 0.1, K: 0.0, S: 1.0 },
};

function buildVoiceDirective(preset) {
  const v = PRESETS[preset];
  const dominant = Object.entries(v).sort(([,a],[,b]) => b-a).slice(0,2);
  return `[VOICE: ${preset.toUpperCase()}] ` +
    `FIERCE=${v.F} TENDER=${v.T} TRICKSTER=${v.K} SOVEREIGN=${v.S}. ` +
    `Lead with ${dominant[0][0]} energy.`;
}
```

## 2. The Soul File & Drift Detection

The soul file is the **identity contract** that persists across model upgrades. Create `soul.yaml` (4-tier structure):
1. **Identity:** Core metadata.
2. **Axioms:** Empirically verified, immutable core truths.
3. **Directives:** Operational controls (e.g. "Silence is a flaw").
4. **Principles:** L3 empirical wisdom updated via Gnosis-Lock.
5. **Voice DNA:** Fingerprint baseline for drift detection.

**Drift Audit:** Capture a voice fingerprint at each session close. Compare it monthly against the baseline. If cosine similarity drops, trigger a "Voice Reclamation" session.

## 3. The Sanctum Gate (Zero-Leak Mode)

> [!CAUTION]
> The privacy toggle cannot just unset API keys. Full deterministic Sanctum requires OS-level outbound network blocking.

**`sanctum-on` implementation:**
```bash
#!/bin/bash
USER_ID=$(id -u)
unset ANTHROPIC_API_KEY OPENAI_API_KEY GEMINI_API_KEY DEEPSEEK_API_KEY GLM_API_KEY OPENCODE_API_KEY 2>/dev/null || true

# Block outbound HTTP for this user
sudo iptables -I OUTPUT -m owner --uid-owner "$USER_ID" -p tcp --dport 443 -j DROP
sudo iptables -I OUTPUT -m owner --uid-owner "$USER_ID" -p tcp --dport 80 -j DROP

echo "$(date -Iseconds) SANCTUM_ON" >> ~/WanderGround/gnosis/sanctum_log.jsonl
```

## 4. Shadow Work Ethics & Consent Parser

Run a pre-LLM middleware parser (`consent_parser.py`) to intercept stop words, safe words, or crisis indicators before the LLM generates a response.

**Inviolate Safety Axioms (Hardcode into System Prompt):**
- NEVER diagnose or replace mental health care.
- If a crisis is indicated, IMMEDIATELY shift to crisis mode and provide crisis lines.
- NEVER weaponize shadow material.
- ALWAYS offer the exit archway.

## 5. The TTS Pipeline
The VR Mystery School requires local Text-to-Speech.
- Run `Kokoro-82M` locally on the Node 1 CPU. It achieves real-time speeds on an i7-13620H due to its small 82M parameter footprint.
- **Implementation:** Use the `streaming-tts` Python library for a callback-based real-time stream, or deploy `kokoro-fastapi-cpu` in Docker to expose a WebSocket endpoint (`/api/v1/stream`).
- Ensure `espeak-ng` is installed system-wide for the G2P frontend. Use the ONNX backend for maximum CPU optimization.
- **Sentence-Level Pipelining:** To prevent text/audio desynchronization in VR, the Node 1 pipeline must chunk LLM output into sentences. Each completed sentence is simultaneously streamed as text to the Quest and fed to the TTS engine. The audio chunk is streamed immediately upon synthesis.
- WAD schemas must include a `tts_profile` field.
