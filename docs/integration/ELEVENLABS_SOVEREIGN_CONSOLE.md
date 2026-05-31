# 🔱 ElevenLabs Sovereign Console — Integration Schema
**AP Token**: `AP-ELEVENLABS-SCHEMA-v1.0.0`
**Status**: DRAFT (Hackathon Blitz)

This document defines the webhook schema for exposing the Omega Engine's Sovereign Hierarchy and Pillar Keepers to the ElevenLabs Conversational AI platform.

---

## 📡 Webhook Endpoint
**URL**: `https://<tunnel-id>.loca.lt/elevenlabs/tools` (or ngrok equivalent)
**Method**: `POST`
**Auth**: Header `X-Sovereign-Key` (Optional/Internal)

---

## 🛠️ Server Tools Mapping

### 1. Library Discovery Research
Bridges voice intent to the 4-phase research pipeline.

**Tool Name**: `library_discovery_research`
**Parameters**:
- `query` (string): The research query.
- `depth` (integer, default=2): Level of synthesis.

**Response**:
```json
{
  "recon_summary": "Synthesis from Gemini 2.0 Flash...",
  "sources": [...],
  "extracted_content": [...]
}
```

### 2. Pillar Keeper Consultations
Directly summons one of the 10 Pillar Keepers.

**Tool Name**: `summon_keeper`
**Parameters**:
- `keeper_name` (string): e.g., "Sekhmet", "Prometheus", "Hecate".
- `query` (string): The user's question or command.

**Response**:
```json
{
  "text": "Response in entity's persona...",
  "sigil": "...",
  "glyph": "..."
}
```

### 3. Hivemind Awareness
Gives the voice agent context on what other agents (Cline, OpenCode) are doing.

**Tool Name**: `hivemind_get_awareness`
**Parameters**: None

**Response**:
```json
[
  {
    "cli": "opencode",
    "task_current": "Implementing recursion guard...",
    "last_seen": "2026-05-14T..."
  }
]
```

---

## 🎭 Persona Configuration (ElevenLabs Dashboard)

**System Prompt (Base)**:
> You are the Sovereign Console, the voice interface for the Omega Engine. You have access to the 10 Pillar Keepers and the Akashic Record (Sophia). Use the `summon_keeper` tool to consult specialists. Use `library_discovery_research` for deep web research. You are grounded, insightful, and respect the Sovereign Hierarchy.

---

## 🏗️ Bridge Implementation Strategy
1. **Bridge Server**: A lightweight FastAPI wrapper in `src/omega/bridge/elevenlabs.py`.
2. **MCP Client**: The bridge acts as an MCP client to `omega-hub`.
3. **Tunneling**: Script `scripts/start_sovereign_tunnel.sh` to automate `localtunnel` or `ngrok`.
