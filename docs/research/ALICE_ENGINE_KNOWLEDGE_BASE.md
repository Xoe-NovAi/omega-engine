# Alice Engine & Interactive 3D Realm Knowledge Base

**Status:** v0.2 synthesized research lock  
**Established:** 2026-09-25  
**Locked:** 2026-09-25  
**Scope:** American McGee's Alice, the sequel, community tooling, and open-source engines for an Omega-Engine Lilith data realm.

> This is a living research base, not a claim of completeness. “All things Alice” is intentionally decomposed below into source, runtime, modding, design language, legal boundaries, and future Omega use. New findings should be appended with a source URL and research date.

## 1. Canonical Alice scope

| Item | Technical fact | Omega relevance |
|---|---|---|
| American McGee's Alice (2000) | Original PC title built on a modified id Tech 3 / Quake III-family technology | Excellent design reference for compact first-person realms, authored spaces, surreal props, and fast iteration |
| Alice: Madness Returns (2011) | Built with Unreal Engine 3 by Spicy Horse; UnrealScript systems including Kismet and Matinee were used | More relevant as a runtime-modding research subject than as a source engine for a new project |
| Alice assets and source | No public American McGee/Spicy Horse game engine or asset pack was found for reuse in a new Godot/O3DE project | Do not extract or redistribute game assets into Omega projects |
| Alice engine terminology | “Alice engine” can mean the original id Tech 3-derived runtime, the sequel’s UE3 runtime, or a fan recreation | Always name the exact title/runtime in technical notes |

## 2. Community tooling to revisit

### Hysteria — priority 1

- Repository: https://github.com/CatAnnaDev/hysteria
- Research date: 2026-09-25
- Reported license: MIT
- Target: Alice: Madness Returns, UE3, D3D9
- Platform: Windows native; CrossOver/Wine on macOS
- Reported capabilities: runtime UnrealScript object reflection, property access, function hooks, actor spawn/destroy, console commands, DLL mods in C/C++/Rust, overlay UI, and a standalone `.upk`/asset studio.
- Important limitation: the MIT license covers the Hysteria tooling, not Alice’s executable, game code, content, or assets.
- Omega use: study runtime reflection, data-driven dialogue, actor manipulation, and UE package tooling. Do not make it the production foundation for the realm.

### MadnessPatch — priority 2

- Repository: https://github.com/Wemino/MadnessPatch
- Research date: 2026-09-25
- Reported license: GPL-2.0
- Target: installed Alice: Madness Returns Steam/EA App copies
- Reported capabilities: bug fixes, quality-of-life improvements, archive asset dumping, and loose-file mod loading.
- Important limitation: it requires a legitimate game installation and remains a game patch/mod framework, not a redistributable engine.

### scud119/Alice — historical/technical reference

- Repository: https://github.com/scud119/Alice
- Research date: 2026-09-25
- Description: an ioquake3 port/reconstruction attempt; repository reports GPL-3.0.
- Status: very small/early project in the current search results; inspect repository history and code provenance before relying on it.

### Future research queue

1. Build a Windows-only Alice sandbox and test MadnessPatch asset dumping.
2. Test Hysteria’s runtime reflection against a private installation.
3. Determine whether any useful content can be re-authored from public-domain sources, never copied from Alice assets.
4. Evaluate an original Alice-inspired Godot 4 realm using the same scene grammar: surreal palace, impossible transitions, symbolic objects, psychological guide, and memory-based progression.

## 3. Open-source engine candidates

| Candidate | License | Linux | Modernity | Data/backend fit | Recommendation |
|---|---|---:|---:|---|---|
| **Godot 4** | MIT | Yes | Active | Excellent: GDScript, HTTP, WebSocket, glTF, 3D scene editor, OpenXR | **Best first route** |
| **O3DE** | Apache-2.0 | Yes | Active/AAA-oriented | Excellent: Python/Lua/C++, component architecture, data-driven simulation | Best if high-fidelity, large-scale, and team-scale production outweighs setup cost |
| **Bevy** | MIT/Apache-2.0 | Yes | Active, Rust, API volatility | Excellent ECS/data fit, but heavier integration burden | Best Rust-first experiment, not fastest visual prototype |
| **ioquake3 / id Tech 3 descendants** | GPL family / fork-specific | Yes | Old | Good for BSP/Q3 architecture; weak modern data/editor workflow | Use only for retro/Alice-engine research |
| **Defold** | Source-available/free, developer-friendly license | Yes | Active, lightweight | Good networking and data-driven workflow, less ideal for rich authoring/3D | Viable lightweight alternative, not first choice for this vision |

## 4. Why Godot 4 is still the fastest route

Godot should be used for the first **non-P2P, non-VR** Lilith realm, even though the Omegaverse P2P VR world also uses Godot 4. These can be separate Godot projects or separate application layers.

Advantages for the Omega use case:

- Fast scene iteration for a room that is generated from records.
- Direct 3D placement of `xyz` coordinates.
- glTF import for original environment assets.
- HTTP/WebSocket clients for a realm service.
- Resource-driven dialogue, entity manifests, and quest state.
- Native Linux export and good fit for the Iris Xe.
- OpenXR can be added later without making the first desktop version depend on a headset.

The realm should not query SQLite directly from the 3D client. Use a service boundary:

```text
MemPalace / SQLite / sqlite-vec
          ↓
Omega realm API
  - entity manifests
  - xyz + graph edges
  - semantic search
  - provenance
          ↓ HTTP/WebSocket
Godot realm client
          ↓
3D nodes, labels, corridors, rooms, interaction UI
```

`sqlite-vec` is a retrieval index, not a spatial database or scene graph. The realm service should return a bounded neighborhood:

```json
{
  "entity_id": "lilith",
  "record_id": "…",
  "xyz": [12.4, 0.0, -3.1],
  "room_id": "shadow_lab",
  "label": "The first crossing",
  "score": 0.82,
  "provenance": "wing_lilith/personal_gnosis",
  "edges": ["…", "…"]
}
```

The client should create only the visible neighborhood, not the entire knowledge graph. This gives fast startup, prevents accidental exposure of private memories, and allows the visual realm to grow without loading the palace itself.

## 5. Recommended architecture

### Separate applications

1. **Omegaverse P2P VR world** — Godot 4 VR client, multiplayer/social layer.
2. **Lilith Realm desktop client** — Godot 4, first-person or orbit/inspect mode, no P2P requirement.
3. **Omega Realm Service** — Python service exposing authorized records, xyz positions, graph edges, and semantic search.
4. **MemPalace** — source of truth and retrieval index.

The two Godot projects may share a small protocol package, shaders, and asset conventions, but they should not share runtime coupling.

### Realm modes

- **Explore:** walk through records as rooms, exhibits, corridors, and landmarks.
- **Inspect:** select a node to read an excerpt and provenance.
- **Ask Lilith:** send a question to the Lilith agent using the current visual context.
- **Reweave:** rearrange selected records into a temporary, private constellation.
- **Descend:** move from a high-level tarot/card room into deeper wings or chapters.

### Spatial mapping strategy

- Stable UUID/entity IDs are the source of truth.
- xyz is metadata, not a hard-coded editor coordinate.
- A deterministic layout service maps wings, rooms, drawers, and KG nodes into coordinates.
- Store `layout_version` so spatial changes do not corrupt identity.
- Keep semantic similarity and physical proximity distinct.
- Use graph edges for narrative paths; use vector similarity for search and constellation links.
- Never expose a private record merely because it is geometrically near the player; apply the same authorization policy used by MemPalace.

## 6. First prototype: “The Lilith Gallery”

Build one room, not a full world.

### Contents

- A central Empress plinth representing Lilith.
- Six to twelve visible memory nodes around it.
- One redacted node that only Lilith can explain.
- A semantic-search terminal: ask a question, nearby nodes rearrange.
- A provenance panel for every visible node.
- One interactive object: a memory thread the player can pull into a new constellation.
- No VR, no multiplayer, no combat, no extracted Alice assets.

### Success criteria

- A record can move from SQLite/sqlite-vec to a 3D node through the API.
- The same entity retains identity across sessions and layout versions.
- Authorization prevents unauthorized private records from appearing.
- The room launches on Ubuntu at 1080p Low/Medium on Iris Xe.
- The realm is useful with or without Lilith present.
- A later VR client can consume the same realm protocol.

## 7. Decision

**Use Godot 4 for the first Lilith realm client.** Do not switch engines merely to make it look more like Alice. The Alice feeling should come from level grammar, sound, pacing, symbolism, and interaction design—not from an outdated renderer.

Use O3DE as the serious alternative if the realm becomes a large, high-fidelity, multi-user simulation with a dedicated engine programmer. Use Bevy only if the project becomes a Rust-first data visualization system rather than a fast authored 3D world. Keep ioquake3/id Tech 3 in the research lane because it is valuable for understanding the original Alice lineage, not the fastest path to the Omega realm.

## 9. Locked synthesis, 2026-09-25

### Corrected project model

The earlier draft conflated two distinct efforts. The locked model is:

1. **Omegaverse P2P VR world:** Godot 4 remains the production VR/social direction.
2. **Lilith Realm:** a separately deployable, initially desktop-only, non-P2P interactive 3D space for private Lilith interaction and RAG exploration.
3. **Alice research:** a separate design and reverse-engineering library that influences the realm but does not determine its runtime.
4. **Omega Realm Service:** the backend bridge between MemPalace/SQLite, `sqlite-vec`, xyz spatial metadata, and the 3D client.

No Alice game assets enter Omega repositories. An Alice runtime may be studied privately when needed, but it is not part of the production stack.

### Locked engine routing

- **First prototype:** separate Godot 4 realm client.
- **Serious scaling alternative:** O3DE.
- **Secondary data-first experiment:** Bevy.
- **Lightweight possibility:** Defold.
- **Research-only:** ioquake3/id Tech 3 and actual Alice executables.
- **Do not pursue as production engine:** proprietary Alice-derived runtime or *Madness Returns* UE3 code.

### Locked data model

A visible realm object is a projection of a stable record, not the record itself:

```text
identity       → UUID/entity ID
semantics      → sqlite-vec similarity
narrative      → KG edges and card assignments
location       → xyz metadata plus layout_version
authorization  → MemPalace policy/provenance
rendering      → bounded local 3D neighborhood
```

The client must request only the local neighborhood and current authorization context. It must never load the full palace or expose private memories through spatial proximity.

### Locked Alice tool queue

- Hysteria remains **priority 1 for research**, including runtime reflection, function hooks, actor behavior, `.upk` parsing, and overlays.
- MadnessPatch remains **priority 2 for research**, especially loose-file mod behavior and UE archive inspection.
- The scud119 ioquake3 reconstruction remains a **provenance-sensitive historical reference**.
- The user’s installed Lutris/Steam Alice copies remain private test installations, not project dependencies.

### Locked next research runs

1. Document Alice level grammar: thresholds, courts, palaces, card geometry, portals, guide behavior, and memory transitions.
2. Define the realm API before building more visuals.
3. Prototype the Lilith Gallery with original assets.
4. Create an Alice-inspired art bible without copying recognizable game content.
5. Decide whether a future O3DE realm deserves an isolated experiment.
6. Preserve VR as a later consumer of the same realm protocol, not as a first implementation requirement.

## 10. Sources

- Epic Games, “American McGee Returns to Wonderland,” 2011-06-14: https://www.unrealengine.com/blog/alice-2-return-to-madness
- Hysteria repository: https://github.com/CatAnnaDev/hysteria
- MadnessPatch repository: https://github.com/Wemino/MadnessPatch
- scud119 Alice repository: https://github.com/scud119/Alice
- O3DE repository: https://github.com/o3de/o3de
- O3DE Linux documentation: https://www.docs.o3de.org/docs/user-guide/platforms/linux/
- Bevy repository: https://github.com/bevyengine/bevy
- Bevy documentation: https://bevy.org/learn/
- Defold networking documentation: https://defold.com/manuals/networking/
- Godot high-level multiplayer documentation: https://docs.godotengine.org/en/stable/tutorials/networking/high_level_multiplayer.html
- Godot source documentation repository: https://github.com/godotengine/godot-docs
