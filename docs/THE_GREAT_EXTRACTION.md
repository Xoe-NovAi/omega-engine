# The Carmack Standard: 10-Year Temple-Grade Architecture

**Date**: 2026-10-03
**Status**: Architectural Blueprint / Active Mandate
**Context**: Transitioning Omega Engine from a monolithic repository to an "Operating System for Entities," enabling a worldwide P2P VR fabric.

## The Core Philosophy
If Omega Engine is to achieve the durability and longevity of id Software's DOOM/Quake engines (The Carmack Standard), it must adopt absolute, ruthless separation of concerns. 

The binary executable (`doom.exe`) was completely ignorant of what a "Cyberdemon" was. The engine only knew about rendering, memory, and state. The Cyberdemon, maps, and sounds were bundled in the `.WAD` (Where's All the Data). 

Because of that strict boundary, the DOOM engine remains indestructible and universally portable decades later. Omega Engine must become the identical protocol across every machine on Earth. If every user edits the engine to fit their local entities, the network shatters.

---

## The Four Sacred Boundaries

To make the Engine indestructible and universally distributable, the system must physically isolate into four distinct domains:

### 1. The Core Engine (`omega-engine`)
* **The Metaphor:** `quake.exe`
* **What it is:** The canonical, immutable software from Node 0. It handles local AI orchestration (Ollama), MCP protocol routing, SQLite database connections, Tailscale federation, and the basic Plugin API.
* **The Rule:** **No user data, no lore, no experimental tools live here.** If you run `git clean -fdx` and `git reset --hard`, you lose zero data, zero memories, and zero entities.

### 2. The Plugin ABI / The Lab (`omega-extensions` or `~/.config/omega/plugins/`)
* **The Metaphor:** `QuakeC` scripts or `.DLL` mods
* **What it is:** The experimental mechanics. The Well (`well_storage.py`), `gnosis-leash.js`, custom UI hooks, or specialized MCP servers that are not yet canonical.
* **The Rule:** The Engine loads these dynamically at boot. If a plugin crashes, the Engine survives and logs the error. This is where Node 1 does its Vanguard research. Stable mechanics are eventually PR'd to the Core Engine on Node 0.

### 3. The Payload (`arcana-novai` WAD)
* **The Metaphor:** `DOOM.WAD`
* **What it is:** The Triad, Lilith, AVGN. The Tarot mappings, the Voice DNA, the system prompts.
* **The Rule:** WADs are versioned, portable directories. WADs contain NO executable code (no `.py` or `.js` files that alter system mechanics), only data, prompts, and lore. You can zip a WAD and send it over the P2P network, and another Omega Engine will load it identically.

### 4. The Save State (`~/.local/state/omega/`)
* **The Metaphor:** `savegame1.sav`
* **What it is:** The OpenCode SQLite database, the MemPalace vector graph, the Hivemind logs, and the Pause Ledger.
* **The Rule:** The state of the universe. Entirely local to the user, living outside all git repositories. Upgrading the Engine or swapping a WAD must never corrupt the Save State.

---

## The Plan for Node 1: "The Great Extraction"

To implement this foundation, Node 1 will dismantle the monolithic `omega-engine-alpha` repository and reconstruct it according to the Four Boundaries.

### Step 1: Rescue the Payload (WAD)
Create a brand new Git repository (e.g., `~/Documents/Projects/arcana-novai`). Move the entire `wads/arcana_novai` directory into it.

### Step 2: Rescue the Lab (Plugins)
Extract `gnosis/well`, `.opencode/plugins/gnosis-leash.js`, and experimental Makefile targets into a separate Plugin incubator repo/directory. Configure the Engine to target this folder at startup.

### Step 3: Secure the State
Verify that `opencode.db` and the MemPalace databases are safely stored in a designated data directory (like `~/.local/share/opencode/`), completely untouched by Git operations.

### Step 4: Purify the Engine
Violently reset `omega-engine-alpha`. Wipe out the untracked files, remove the custom folders, and sync it 1:1 with Node 0's canonical `main` branch (v1.6.0).

### Step 5: The Boot Sequence
Boot the pure, canonical Engine. Point it at the external WAD repo and the external Plugin directory. If Lilith awakens with her memories intact and the Well injects its corrections, the Carmack Standard has been achieved.
