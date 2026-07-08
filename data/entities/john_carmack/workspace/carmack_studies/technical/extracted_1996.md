# 🔱 John Carmack studies — Technical Extraction 1996
# AP: AP-JC-TECH-1996-v1.0.0
# ⬡ OMEGA ⬡ john_carmack ⬡ technical ⬡ 1996
#
# Technical facts, performance numbers, and architectural decisions extracted from John Carmack's 1996 .plan files.

---

## 1. QuakeWorld Network Architecture (Aug 1996)

### 1.1 Server Loop Paradigm Shift
- **Legacy Model**: Game-style loop (fetch all input $\rightarrow$ simulate world $\rightarrow$ send updates to all clients). Run at 20 Hz (50ms frames).
- **QuakeWorld Model**: Fileserver/database style loop. Deals with each packet immediately as it arrives.
  - Only the sending player is moved forward in time.
  - A custom response is sent back immediately.
  - Non-player objects are spread out between incoming packets (non-uniform time advancement).
  - **Performance**: Reduced packet processing latency from **>50ms to <4ms** on a Pentium 90.
  - **Bandwidth**: Server never blindly broadcasts; updates must be requested (streaming requests without waiting for replies).

### 1.2 Client-Side Prediction (CSP)
- **Initial Experiment**: Attempted full simulation of movement, missiles, and interactions.
- **Failure Mode**: Full 300ms simulation on the client side caused severe artifacts (running in front of own missiles, missiles clipping through enemies until server ACK).
- **The "Right Approximation" CSP**: Restricted client-side simulation to **<100ms** of motion.
  - Used to smooth out beat-frequency interactions between server packet arrival and client frame times.
  - Client predicts its own movement (solidity, friction, gravity) based on the last known authoritative server state.
  - Projectiles and doors are evaluated parametrically rather than iteratively.

### 1.3 Protocol & Bandwidth Optimization
- Scrapped the reliable stream primitive (from qtest) in favor of the **unreliable packet** as the basic primitive.
- Implemented bandwidth estimation on the client-server link to prevent router buffer pileup (latency spikes).
- Cut average packet sizes by 17 bytes (server-to-client) and 8 bytes (client-to-server) to save modem latency (every byte saved = 1ms of latency on dial-up).

---

## 2. Compilation & Map Utilities

### 2.1 qcc Compiler Optimization (Sep 1996)
- **The Bottleneck**: Linear search for definitions (`defs`) during compilation.
- **The Fix**: Moved definitions to the head of the search list each time they were accessed (MRU / Move-to-Front heuristic).
- **Performance**: Sped up compilation **4x** (full recompile reduced from 20s to 5s on Pentium Pro 200). Fully recursive parsing.

### 2.2 qbsp Map Tool Hardening
- Converted from `double` to `float` to reduce memory footprint, though it introduced minor numeric instabilities.
- Expanded qbsp to 32-bit values for edges and faces.
- Optimized the portalization process: **20% faster, 1/5 the memory footprint**.
- Split qbsp into two programs (`qcsg` and `qbsp2`) to run on machines with <32MB RAM.
- Flood-filled away outside sky fragments to save polygons.

### 2.3 qrad (Radiosity Lighting Tool)
- Full physical simulation of light transport (radiosity) replacing the legacy heuristic `light.exe`.
- Surfaces tagged as light emitters (fluorescent ceiling textures, lava surfaces) instead of placing floating light entities.
- Light reflects off surfaces (e.g., ceilings are lit by reflection from floors).
- Parallel sun/moon lighting passing through sky volumes based on specified angles and intensity.
- **Constraints**: Required a completed `vis` pass first (otherwise qrad would take 1000x longer). Memory footprint **>100MB**, optimized using a halved bit array for visibility interconnects and sparse scaled shorts for energy transference.

---

## 3. Graphics & 3D APIs

### 3.1 OpenGL vs. Direct3D Immediate Mode (Dec 1996)
- **Verdict**: Strongly rejected Direct3D Immediate Mode (D3D IM) in favor of OpenGL.
- **D3D IM Critiques**:
  - "Horribly broken API" that inflicts pain via COM, expandable structs, and execute buffers.
  - Execute buffers force the programmer to manually batch commands into structures, requiring the application to know the optimal batch size for every hardware configuration.
- **OpenGL Virtues**:
  - Procedural API (`glBegin`, `glVertex`, `glEnd`) is clean, simple, and easy to use.
  - Scales seamlessly from a $300 Permedia card to a $250,000 SGI Infinite Reality system.
  - Clean driver extension model (ICD/MCD) and rigorous conformance tests.

### 3.2 Hardware Evaluations
- **3DFX Voodoo**: Highest textured fill rate (50 Mpixels/sec peak). Stomped professional workstation cards at 640x480.
- **3Dlabs Permedia**: Only well-supported low-end OpenGL card. Suffered from 15-bit internal paths (no dithered 24-bit color blending). Fill rate dropped from 40 Mpixels to 10 Mpixels under realistic gaming conditions (bilinear, z-buffered, 16-bit textures).
- **Matrox**: Critiqued for lack of true alpha blending ("screen door transparency is not a valid replacement").

---

## 4. Memory & Runtime Systems

### 4.1 Hunk Allocator
- Optimized memory usage by using all memory between the static hunks as a dynamic cache.
- Implemented `COM_LoadStackFile` to load temporary files directly on the stack to prevent heap fragmentation.
