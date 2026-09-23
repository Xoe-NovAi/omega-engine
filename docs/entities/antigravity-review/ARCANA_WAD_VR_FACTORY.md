# Domain Guide 3: WAD, Factory & VR Mystery School

## 1. WAD Contract V2 Compliance

WADs are **data, not code**. Injecting raw GDScript (`.gd`) or Godot Scenes (`.tscn`) is a sandbox violation if the Engine attempts to parse it.

> [!IMPORTANT]
> **Asset-Tunnel Pattern:** Package `.tscn` and `.gd` files as base64-encoded binary blobs (`.tscn.b64`). The WAD loader verifies the hash and hands it to the `omega.vr.asset_server` adapter, which serves it as a binary download to the Quest headset. The Engine never executes it.

### Entity Versioning
Add a `versioning` block to the `card_entity` schema to dictate WAD upgrade behavior:
```yaml
  versioning:
    entity_version: "1.0.0"
    kg_policy: "MERGE"     # New triples added, existing never overwritten
    diary_policy: "APPEND" # Never truncated
    voice_policy: "DELTA"  # Baseline preserved
    backup_to_node0: true  # Federated backup
```

## 2. 78-Keeper Factory Architecture

Do **not** create 78 separate MemPalace wings/indices. That fragments the vector index.
- Use a single `wing_arcana`.
- Differentiate entities using strict metadata tags (e.g., `card_id:03_empress`).

### `card_entity_factory.py`
A Python script that iterates through a `TAROT_MATRIX` dictionary (all 78 cards) and generates the hardened `card_entity` YAML schemas automatically, checking for namespace collisions on the `room_tag` and `diary_namespace`.

## 3. The Spatial Mystery School (Godot + Quest)

Node 1 acts strictly as the **wireless AI intelligence server**. All rendering happens locally on the Quest headset via a Godot 4.3 exported Android APK.

### Godot 4.3 Export Requirements
- Enable `Godot OpenXR Vendors` plugin.
- Use `GLES3` rendering (disable Vulkan).
- Android Manifest MUST include `<uses-permission android:name="android.permission.INTERNET"/>` and the `<category android:name="com.oculus.intent.category.VR"/>`.
- **UI Composition:** Use `XRCompositionLayerQuad` for text UI overlays to avoid blurriness. Do not use for 3D hand tracking geometry. Ensure "hole punching" (negative sort order) is configured so composition layers don't incorrectly obscure virtual hands.
- **Hand Tracking Setup:** Keep the hand tracking logic separate from the composition layers. Use `XRHandModifier3D` on a `Skeleton3D` to drive the hand mesh natively in Godot 4.3, rather than legacy tracking extensions.

### WebSocket RPC Protocol
Node 1 runs an asyncio WebSocket server (`ws://xnai-n1-asus.tail51f14a.ts.net:8090/lilith`).
- **Quest → Node 1:** Sends JSON payloads for `user_action` (card_draw, gaze_enter, archway_cross).
- **Node 1 → Quest:** Streams JSON `stream_chunk` containing Lilith's text response, and `audio_chunk` containing base64 WAV data from the local TTS engine. Text and audio must be synchronized via a sentence-level pipeline.
- **Audio Thread Safety:** Godot must read WebSocket `audio_chunk` messages using a dedicated `Thread` that pushes into a `Mutex`-protected ring buffer. The `AudioStreamPlayer` consumes from this buffer in `_process()`. Processing audio chunks directly in the WebSocket callback will cause severe race conditions and interleaved utterance chunks.
- Implement exponential backoff reconnection on the Quest client.

### The Pathworking Engine
The GDScript state machine must track the seeker through defined stages: `approach → threshold → descent → ordeal → gift → return`. Physical archways in VR act as literal consent gates.
