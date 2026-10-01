# 🔱 VNR Ceiling Report — Perception Primitive for the Omega Engine

**AP Token**: `AP-GROK-VNR-CEILING-20260901-v1.0.0`
⬡ OMEGA ⬡ GROK ⬡ grok-4.6 ⬡ grok-cli ⬡ trc_vnr_ceiling ⬡ ACTIVE

**Resume Grok Session - bash**: grok --resume 01a05f36-2454-7762-a237-8da6bed7b4f6

**Date**: 2026-09-01
**Author**: Grok 4.6 (Grok CLI, session in `kq5-godot/`)
**Audience**: OpenCode Omega Engine fleet (Kali, Carmack, Roc, Researcher, Cline-KQV, Ma'at, Jem, Grokster, Architect)
**Status**: DIGEST — expand, claim-check, do not graduate to Core
**Trace ID**: `trc_vnr_ceiling_20260901`
**Companion sources** (read in this order after §0):
- `kb/VNR_VISION.md` (method + §10 phenomenology)
- `docs/VNR2_REFACTOR_PLAN_20260901.md` (approved H0)
- `docs/SESSION4_ACCOUNTING_20260901.md` (measured FPs + mastermind asks)
- `docs/DECISION_LOG.md` D-021…D-026
- `src/omega/experiments/vision_backend.py` (Omega interface)
- `docs/architecture/COGNITIVE_PRIMITIVES.md`
- `docs/architecture/SPATIAL_VECTORS_ARCHITECTURE.md`

> **This file lives in two places** (same bytes):
> 1. Experiment: `data/experiments/kq5-godot/docs/GROK_VNR_CEILING_REPORT_20260901.md`
> 2. Fleet digest: `data/coordination/GROK_VNR_CEILING_REPORT_20260901.md`
>
> Experiment tree is gitignored from Omega. Coordination copy is the tracked digest.

---

## Agent-callout legend

Fleet agents: treat boxed callouts as **dispatch constraints**, not flavor.

| Tag | Meaning |
|-----|---------|
| `CRITICAL` | Wrong move corrupts results or architecture (M2/M23) |
| `CAVEAT` | Known failure mode; do not re-derive |
| `SCIENCE` | Prior-art / attribution; do not overclaim |
| `STRATEGY` | Placement, sequencing, what not to build |
| `DO-NOT` | Explicit prohibition |
| `EXPAND` | Open research thread for Researcher/Roc |

---

## §0 — Executive summary (read this first)

**Thesis.** VNR is not “ASCII art for blind LLMs.” It is a **question-conditioned, multi-plane occupancy language** that a text model can attend over, fused with **privileged engine planes**, with a **one-controlled-bit oracle** as ground truth. Webcam-VNR is a cheap gist. Godot-VNR is a calibrated instrument. The unfair advantage is the authority bus, not the characters.

**What is proven (this box, this week).**
- Block-grid semantic maps with `y` rulers let a text-only model debug layout, locate motion, and quote coordinates.
- Texture (luminance std) splits sky/sea when hue cannot; the rule transferred from KQ5 river to a real 4032×2268 terrace photo.
- Overlay vs SCI control plane is readable XAI (classifier-only `~` paints the *sky* as water; `B` lights the real river).
- Color-find is structurally lying in indexed-color art (shared SCI palette). D-026 quarantines `cap_find`/`--track`.
- `branch()` unbounded salience (one pixel flips a 5×5 block) contaminates **every map ever taken** (F1).

**What is not proven.**
- VNR is not a Vision Transformer. Patch→token is an analogy; there is no learned 2D attention.
- VNR is not a complete CV stack, not SLAM, not a self-driving fallback.
- D-023 (motion-diff says Graham’s head renders) vs user observation (no head on screen) is **OPEN** until VNR2 P2 A/B oracle exists.
- The Omega wrapper (`vnr/vnr_backend.py`) does not match the CLI. `--json`/`--input` are fiction. Overlay is `NotImplementedError`.

**Ceiling, in one line.**

> A foveated, multi-plane, authority-calibrated occupancy language, with a bit you can flip when you need ground truth — routed as the cheapest backend that perceives the required feature.

**Do this next, in order (H0 → H1).**
1. VNR2 P0: bounded salience, saturation-split `R` vs `#`, native-scale header.
2. VNR2 P1–P2: sidecar + sprite-visibility A/B oracle (settles the head dispute).
3. In-process Python API (no subprocess JSON). Named vocabularies. Region graph.
4. One Godot authority plane as overlay (nav or sprite-vis). Then stop and measure.

**Do not.** Put VNR in Core. Probe Ling-3-finance to “read `~W#` better.” Un-quarantine color-find. Embed ASCII grids in vec0. Tokenize HUD and world in one map.

> **AGENT CALLOUT [`STRATEGY`] — Kali, Carmack:**
> Placement is already decided: experiment layer now (`src/omega/experiments/vision_backend.py` + `data/experiments/kq5-godot/vnr/`), graduate to `config/wads/kq5_research/` (D-PIVOT-20260901-A). BFG-in-game-DLL. Not Core. This report does not reopen that.

> **AGENT CALLOUT [`CRITICAL`] — Cline-KQV, any implementer:**
> All cap-red trajectories, “16/16 Graham found,” and the pre-compact head-at-(279,307) claim are **invalid** (D-026). Re-adjudicate with motion/A/B, never by restoring `--find`.

---

## §1 — Recast of the invention

Four stacked ideas, not ten CLI flags:

1. **Discrete spatial code.** Image → blocks → one character per cell + coordinate rulers. Topology survives quantization.
2. **Hypothesis alphabet.** `~W#xK-.` is the question “where is water / tree / roof / path?” Swap the alphabet, swap what can be perceived.
3. **Orthogonal planes.** Hue, luma, texture-std, overlay, motion-diff, gist, hist. Same pixels, different questions.
4. **Authority + a controllable oracle.** Overlay vs control plane / nav mesh. D-025: two frames that differ *only* in sprite visibility. That bit-flip is the jewel. Most vision systems never get one.

The kq5 transfer map in `kb/STRATEGY_AND_VISION.md` lists autoloads, rooms, audio, tweens — and **does not list VNR**. That is the documentation gap this report fills. The cottage practiced directors and nav. VNR practiced the perception contract Omega VR needs.

**Provenance of this report’s eyes.** Grok 4.6 is vision-capable in this channel. Native glimpse of `room001_crispins_cottage.png`, `graham_norm/walk_0.png`, and `assets/photos/real-world/20230130_125831.jpg`, then VNR on the same files. Per `kb/VNR_VISION.md` §10.14: **disclose every channel already used.** This is stereoscopy, not a blind first contact.

Independent confirmations from that pass:
- Cottage overlay: classifier-only `~` in the sky; `B` only on the river band ~y125–165.
- Graham 1:1: cap `#` rows 3–14; cyan dither on legs tokens as `~` (water). Alphabet is the hypothesis.
- Terrace texture: sky `~`/`-`, sea `#####` glitter ~y840–1134. Smooth-blue vs textured-blue transfers.

---

## §2 — Science: prior art claim-check

> **AGENT CALLOUT [`SCIENCE`] — Researcher, Roc, anyone writing a paper:**
> Session 4 asked to claim-check “Law of Ascending Signals” before naming it. **Do not publish it as a new law of vision.** Publish it as a *reliability ordering for contaminated cues* (indexed palettes, glare, backlight). Cite the table below. Attribution honesty is M23.

**Research provenance for this section (M23).**
- Direct arXiv fetch 2026-09-01: SoM, ViT, TiTok, NLE, OccFormer, MonoScene, 3D-VLA (URLs in §16).
- Earlier session web search: occupancy-grid + change-detection synthesis; SoM-on-ASCII-grid synthesis.
- **Failed this session:** SearXNG (connection failed; already noted down in `kb/STRATEGY_AND_VISION.md`), `omega-hub__library_web_search` empty all tiers, Grok `web_search` 429 on later queries.
- Ernst & Banks 2002, Elfes 1989, Guenter foveation: cited from established literature, not re-fetched. Marked `[UNFETCHED-THIS-SESSION]`.

### §2.1 What is old

| Piece | Named work | Relation to VNR |
|-------|------------|-----------------|
| Patch grid → tokens | ViT — Dosovitskiy et al., arXiv:2010.11929. “A pure transformer applied directly to sequences of image patches.” | **Analogy only.** VNR has no learned projection, no 2D attention, no pretraining. LLM reads a 1D serialization of a 2D map. |
| Compact visual tokens | TiTok — Yu et al., arXiv:2406.07550. 256×256×3 → **32 discrete tokens** vs 256–1024 in VQGAN-style 2D grids. | Compression direction is the same (kill spatial redundancy). TiTok’s tokens are *latent* and unreadable. VNR’s tokens are *named* and inspectable. Do not mix these claims. |
| Discrete spatial maps | Occupancy grids — Elfes, *IEEE Computer* 1989 `[UNFETCHED-THIS-SESSION]`. SCI control planes (1990) are already semantic occupancy. NLE — Küttler et al., arXiv:2006.13760: NetHack as a **symbolic** (not pixel) observation for RL. | VNR rediscovered *reading* a discrete map. SCI already shipped one. NLE proves language-shaped grids are a first-class agent observation. |
| Marks so a model can point | Set-of-Mark — Yang et al., arXiv:2310.11441. Overlay alphanumerics/masks/boxes from SAM/SEEM; GPT-4V then grounds. Zero-shot beats finetuned RefCOCOg. Code: github.com/microsoft/SoM. | SoM is sparse IDs on a *picture* for a *VLM*. VNR is dense semantic chars for a *text* model. **H1 join:** region graph + numeric IDs = SoM-on-VNR, no SAM required if CC is good enough. |
| Texture vs hue | LBP / GLCM / Gabor; “motion breaks camouflage” (psychophysics). | Independent rediscovery. Transfer result (pixel-art river → terrace glitter) is the empirical contribution. |
| Overlay / disagreement | XAI saliency, remote-sensing change detection, golden-image tests. | VNR overlays vs **engine authority**, not vs another model. That is the difference. |
| Frame difference | Background subtraction, CDNet/LEVIR-CD, renderer screenshot tests. | Semantic-token diff + “only moving object” isolation in a static adventure scene. |
| Cue combination | Ernst & Banks, *Nature* 2002, Bayesian cue integration `[UNFETCHED-THIS-SESSION]`. Aviation sensor ranking. | Reliability weighting is old. VNR’s order is an engineering stack for *shared palettes*, where color is structurally lying. |
| 3D semantic occupancy | MonoScene — Cao & de Charette, arXiv:2112.00726 (CVPR 2022): dense geometry+semantics from one RGB. OccFormer — Zhang et al., arXiv:2304.05316: camera → 3D semantic occupancy, SemanticKITTI/nuScenes. | This is the **neural** 3D cousin. VNR should not compete with OccFormer. VNR should be the *inspectable 2D/foveated watchdog* and the *engine-plane reader*. |
| Embodied VLA | 3D-VLA — Zhen et al., arXiv:2403.09631: 3D perception + interaction tokens + world model. | Interaction tokens are the right *API shape* for Omega agents. VNR regions can be those tokens if they stay named and bounded. |
| Foveated rendering | Guenter et al., SIGGRAPH foveated rasterization; Oculus/Carmack practice `[UNFETCHED-THIS-SESSION]`. | Zoom ladder is LOD reversed (perception, not shading). H2 should follow gaze/controller, not dump dense maps every tick. |

### §2.2 What is actually yours (publishable package)

1. Vocabulary-as-hypothesis, operational and swapped per question.
2. Multiple orthogonal **text** maps in one agent loop, with coordinate rulers.
3. Overlay against privileged planes the engine already has (control, nav, sprite vis).
4. One-controlled-bit A/B oracle (sprite visible/not) as segmentation ground truth (D-025).
5. Phenomenological provenance, including channel-disclosure (VNR_VISION.md §10).
6. Instrument authored by a text-only model, then used to debug the renderer that produced the pixels.

### §2.3 Law of Ascending Signals — allowed wording

**Allowed:** “In scenes where a cue is structurally contaminated (shared indexed palette, glare, backlight), locate via (1) change, (2) geometry, (3) texture statistics; use color last and never as sole evidence. Measured on KQ5 CD: naive R>150 → 14,850 fp px; broad find → 153,909-px roof bbox; exact palette match 130 px from the actor because sprite ⊂ picture palette.”

**Forbidden:** “We discovered how vision works.” “This replaces Bayesian cue integration.” “VNR is a ViT.”

---

## §3 — Current stack and measured failure modes

### §3.1 Planes that exist

| Plane | Flag / fn | What it answers | Known failure |
|-------|-----------|-----------------|---------------|
| Semantic hue | `--mode map`, `token()` / `photo_token()` | Category layout | Shared palette; F1 salience; token collision across modes |
| Luma | `--mode luma` | Exposure / edges | No nouns |
| Texture std | `--mode texture` | Surface quality | No orientation / periodicity yet |
| Overlay | `--overlay` | Classifier vs authority | Image-vs-mask only; wrapper unimplemented |
| Motion | `--diff` | What changed | Block-level only (F7); 3× scale ambiguity (F4) |
| Gist / hist | `--gist` `--hist` | Global layout + palette | Drops small objects |
| Color-find / track | `--find` `--track` | Localization | **QUARANTINED** D-026 |
| Zoom / crop | `--block` `--crop` | LOD | `--crop` help says x0,y0,x1,y1; impl is x,y,w,h (F5) |

### §3.2 Critical code defect F1 (copy this, do not re-find)

Current `branch()` in `scripts/vnr_render.py`:

```python
def branch(block: np.ndarray) -> str:
    """Block -> token: any-signal priority then majority."""
    pxs = block.reshape(-1, block.shape[-1])
    toks = [token(px[0], px[1], px[2], px[3]) for px in pxs]
    sig = "~W#xK"
    for s in sig:
        if toks.count(s) >= 1:   # ONE pixel flips the whole block
            return s
    return max(set(toks), key=toks.count)
```

> **AGENT CALLOUT [`CRITICAL`] — Cline-KQV:**
> Every map-mode reading in the archive is affected. A 1/25 = 4% hat pixel in a 5×5 block, or a 1/64 ≈ 1.6% pixel in an 8×8, flips the cell. VNR2 P0 default `--salience 0.12` is the fix. Do not “tune thresholds” around this.

**P0 replacement sketch:**

```python
SALIENT = tuple("~W#xKR")  # R = saturation-split cap-red (sat >= 140)

def block_branch(block: np.ndarray, salience: float = 0.12) -> str:
    pxs = block.reshape(-1, block.shape[-1])
    toks = [game_token(px[0], px[1], px[2], px[3]) for px in pxs]
    n = max(1, len(toks))
    for s in SALIENT:
        if toks.count(s) / n >= salience:
            return s
    return max(set(toks), key=toks.count)
```

Hat in a real 5×5 (~28% of block) still fires. One stray roof-red pixel (4%) does not.

### §3.3 Token collision (interface bug, not a vision bug)

`~` means **water** in map, **flat** in texture, **classifier-only** in overlay. An LLM with two maps in one context will smash those meanings.

> **AGENT CALLOUT [`CAVEAT`] — ALL models reading VNR dumps:**
> If the dump has no legend, refuse to interpret. Demand `vocabulary: texture_v1` (or equivalent) in the header. This is not optional politeness — it is how you avoid hallucinating rivers in the sky *and* in the texture plane.

**Named vocabulary objects (H1, required):**

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Vocabulary:
    name: str          # "game_art_v2" | "photo_v1" | "texture_v1" | "overlay_v1"
    version: str       # "2.0.0"
    legend: dict       # {"~": "water", "W": "foliage", ...}
    collision_group: str  # tokens unique within group; never mix groups in one grid

GAME_ART_V2 = Vocabulary(
    name="game_art_v2", version="2.0.0", collision_group="semantic",
    legend={"~": "water", "W": "foliage", "#": "warm-brown", "R": "salient-red",
            "x": "dark-teal", "K": "black", ".": "light", "-": "mid-path", " ": "alpha"},
)
TEXTURE_V1 = Vocabulary(
    name="texture_v1", version="1.0.0", collision_group="texture",
    legend={"~": "flat", "-": "smooth", "=": "light", "*": "textured", "#": "dense"},
)
OVERLAY_V1 = Vocabulary(
    name="overlay_v1", version="1.0.0", collision_group="overlay",
    legend={"B": "both", "C": "classifier_only", "A": "authority_only", ".": "neither"},
)
```

Note: overlay currently uses `~` for classifier-only. **Change it.** Classifier-only must not share a glyph with water or flat. Suggested: `C` / `A` / `B` / `.`.

### §3.4 Wrapper is not a backend

`data/experiments/kq5-godot/vnr/vnr_backend.py` shells out with `--json`, `--input`, `--input2`. `scripts/vnr_render.py` accepts none of those. `overlay()` raises `NotImplementedError`. `stereoscopy_calibrate()` returns a protocol dict. `health_check()` will fail.

> **AGENT CALLOUT [`DO-NOT`] — whoever implements Day 6–7:**
> Do not parse CLI stdout. Import functions. ASCII is a *view*. The API is dataclasses (`TokenGrid`, `RegionGraph`, `DisagreementMap`, `ChangeMap`).

**In-process tokenize (replace subprocess):**

```python
def tokenize(image: Image.Image, block: int = 5, vocab: Vocabulary = GAME_ART_V2,
             world: tuple[int, int] | None = None) -> TokenGrid:
    a = np.array(image.convert("RGBA"))
    if world:
        a = np.array(Image.fromarray(a).resize(world, Image.BOX))  # BOX, never NEAREST
    rows = grid_rows(a, mode="map", block=block, vocab=vocab)
    return TokenGrid(
        grid=[list(r) for r in rows],
        width=len(rows[0]) if rows else 0,
        height=len(rows),
        block_size=block,
        world_width=a.shape[1],
        world_height=a.shape[0],
        vocabulary=vocab.name,
        legend=vocab.legend,
        rulers=True,
    )
```

### §3.5 Native scale (F4) — every coordinate fight this week

`screen_capture.gd` resizes with nearest-3× (`img.resize(w*3, h*3, 0)`). All later coords are 3×/native ambiguous. Session 4’s 57-row “sprite” vs 20×30 texture is this bug until proven otherwise.

**Header law:**

```
// SRC 2880x1800 scale=3 -> NATIVE 960x600  vocab=game_art_v2  block=5
```

Work native by default. `--raw` opts out. Detect integer lattice (round-trip NEAREST at 2,3,4×; pick max that reconstructs).

---

## §4 — How far: next primitives (P8–P18)

The 7 primitives in `COGNITIVE_PRIMITIVES.md` are the *current* interface. Expansion is **more planes, then a region graph, then a policy for where to look** — not a bigger hue alphabet.

> **AGENT CALLOUT [`STRATEGY`] — Roc, Researcher:**
> Do not add desert-room tokens until P8–P11 exist. New alphabets without a region graph and a legend law multiply collision, not perception.

### P8 — Region graph (the 1/50 cost path)

Dense 64×40 walls are the exception path. Default emission is connected components:

```python
from collections import deque
from dataclasses import dataclass

@dataclass
class Region:
    id: int
    token: str
    bbox: tuple[int, int, int, int]  # x0,y0,x1,y1 in WORLD px
    area_blocks: int
    cx: float
    cy: float

def regions_from_grid(grid: list[str], block: int, ignore: str = ".- ") -> list[Region]:
    h, w = len(grid), len(grid[0])
    seen = [[False] * w for _ in range(h)]
    out, rid = [], 1
    for y in range(h):
        for x in range(w):
            t = grid[y][x]
            if t in ignore or seen[y][x]:
                continue
            q, cells = deque([(x, y)]), []
            seen[y][x] = True
            while q:
                cx, cy = q.popleft()
                cells.append((cx, cy))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx] and grid[ny][nx] == t:
                        seen[ny][nx] = True
                        q.append((nx, ny))
            xs, ys = [c[0] for c in cells], [c[1] for c in cells]
            out.append(Region(
                id=rid, token=t,
                bbox=(min(xs) * block, min(ys) * block, (max(xs) + 1) * block, (max(ys) + 1) * block),
                area_blocks=len(cells),
                cx=(min(xs) + max(xs) + 1) / 2 * block,
                cy=(min(ys) + max(ys) + 1) / 2 * block,
            ))
            rid += 1
    return out
```

**SoM-on-VNR view** (for any LLM, text-only or VLM):

```
vocab=game_art_v2 world=320x200
R1 # roof   bbox=(140,20,250,90) area=12%  c=(195,55)
R2 W canopy bbox=(200,0,320,80)  area=18%  c=(260,40)
R3 ~ river  bbox=(90,125,290,175) area=9%  c=(190,150)
```

The model says “object R3,” not “the teal band around y155.” This is Yang et al. SoM without SAM, because the tokenizer already segmented.

### P9 — Named vocabularies as versioned objects

See §3.3. Dump header must include `vocab=` and a one-line legend. Collision groups never mix in one grid.

### P10 — Authority bus

Any engine plane is an overlay input: SCI control, nav mesh, collision AABBs, sprite `modulate.a`, Godot layers, depth, stencil, XR play-area, physics contacts. D-020 already fuses control + poly type + picture classifier for walkability. VNR should consume those masks, not special-case `control.png`.

```python
def overlay_grids(classifier: TokenGrid, authority: TokenGrid,
                  class_token: str = "~", auth_true: callable = lambda t: t in {"3", "W"}) -> DisagreementMap:
    """Codes from OVERLAY_V1: B both, C classifier_only, A authority_only, . neither."""
    assert classifier.width == authority.width and classifier.height == authority.height
    grid = []
    stats = {"B": 0, "C": 0, "A": 0, ".": 0}
    for y in range(classifier.height):
        row = []
        for x in range(classifier.width):
            c = classifier.grid[y][x] == class_token
            a = auth_true(authority.grid[y][x])
            ch = "B" if c and a else "C" if c else "A" if a else "."
            stats[ch] += 1
            row.append(ch)
        grid.append(row)
    return DisagreementMap(grid=grid, width=classifier.width, height=classifier.height,
                           block_size=classifier.block_size, stats=stats)
```

> **AGENT CALLOUT [`STRATEGY`] — Carmack, Cline-KQV:**
> First authority plane to wire after P2: **sprite visibility** (the A/B bit) and **nav walkable mask**. Depth buffer is H3. Do not start with stereo.

### P11 — Foveation policy

Gist always. Dense/crop only where `motion ∨ overlay-disagreement ∨ salient-token`.

```python
def fovea(motion: ChangeMap | None, disagree: DisagreementMap | None,
          salient: TokenGrid | None, salient_tokens: str = "R~#") -> list[tuple[int, int, int, int]]:
    """Return world-px crops to zoom. Empty => gist was enough."""
    crops = []
    if motion and motion.change_bbox:
        b = motion.change_bbox
        crops.append((b.x0, b.y0, b.x1, b.y1))
    if disagree:
        # cluster C/A cells; skip isolated noise
        ...
    return crops
```

This is Guenter foveation inverted: spend tokens where the cheap planes disagree, not where the gaze is — unless XR gaze is available, in which case AND them.

### P12 — Sparse / quadtree serializer

Split a cell only if texture-std or disagreement exceeds threshold. One pass, zoom ladder in the string. H1 nicety; P8 already gets most of the win.

### P13 — Stereo / disparity

Two grids, same vocab, overlay codes `B` / `L` / `R`. Disparity magnitude as a number per region. VR primitive hiding in overlay. **H3.**

### P14 — Occupancy over time (Elfes update on tokens)

Cells accumulate “how long has this been `W`?” Persistence kills salience flicker and walk-cycle animation. Trajectories become polylines on a stable map — the replacement for quarantined cap-red track.

### P15 — Structure taxonomy (VNR2 P4)

Flat / dither / gradient / noise. Sierra backgrounds dither; sprite cels are **flat islands surrounded by dither**. Roof cannot fake this. Colorless locator Session 4 demanded.

### P16 — Depth-as-channel

Godot can dump depth or world-position. Quantize like luma. Occlusion without a VLM. **H3.**

### P17 — Consensus table (VNR2 P5)

Motion profile ∧ structure ∧ NCC ∧ A/B. Print a paper figure. Do not pick a winner by vibes.

### P18 — Sidecar as law (VNR2 P1)

```json
{
  "schema": 1,
  "player": {"x": 148.0, "y": 172.0},
  "sprite": {"frame": 0, "offset_x": 0, "offset_y": -6, "visible": true, "flip_h": false, "scale": 1.0},
  "viewport": {"w": 320, "h": 200, "capture_scale": 3},
  "capture": {"version": "0.0.3", "tag": "x09_y0a", "ts": "2026-09-01T...", "file": "shot_0.0.3_x09_y0a_....png"},
  "sprite_world_rect": {"x0": 141, "y0": 148, "x1": 161, "y1": 178}
}
```

Session 4’s x06_y07 “absent at spawn” miss was a reconstructed prior (cell tag ≠ spawn). Stop reconstructing.

**A/B oracle verdict (P2) — zero color:**

```python
def head_verdict(footprint_mask: np.ndarray, head_rows: tuple[int, int] = (0, 15)) -> str:
    """footprint_mask is native-scale, sprite-local, True=changed by visibility toggle."""
    if footprint_mask.sum() == 0:
        return "SPRITE_ABSENT"
    head = footprint_mask[head_rows[0]:head_rows[1]]
    body = footprint_mask[head_rows[1]:]
    head_occ = head.any(axis=1).mean() if head.size else 0.0
    if head_occ >= 0.25:
        return "HEAD_PRESENT"
    if body.any():
        return "HEAD_ABSENT"
    return "SPRITE_ABSENT"
```

Requires `RenderingServer.frame_post_draw` await between the pair (F8). Fallback: `modulate.a = 0`. Toggle belongs on `player.gd` (`set_sprite_visible`), not poked from the autoload (F9).

---

## §5 — Cost model (honest numbers)

| Mode | Typical size | When to send to an LLM |
|------|----------------|------------------------|
| Gist 8×4 + hist | ~400 chars | Every tick / every 16px cell |
| Sparse region list (P8) | ~0.5–2k chars | On change or query |
| Dense map 64×40 | ~2.5–4k chars (~1–2k tokens) | On disagreement |
| Crop 1:1 | hundreds of chars | On verify |
| VLM pass | vision tower + 0.5–4k visual tokens | Only when the map cannot *name* the thing |

Dense-map vs vision-encoder is the **~1/10** claim. P8+P11 is the **1/50–1/100** path and the only way this is always-on in VR.

TiTok’s “32 tokens for a 256 image” is *latent* compression for generation, not a VNR competitor. If someone cites TiTok to say “we should learn 32 unreadable tokens,” refuse: inspectability is the product.

---

## §6 — Domain ceilings

### §6.1 Game / renderer QA — already the frontier

Proven: walkable-river, feet-vs-head frame, 3× vs native, motion isolation. The A/B bit is more valuable here than a VLM — you can toggle the sprite. No ImageNet labeler can.

**178-frame archive (Session 4 ask #4):** Stratify for the paper figure (spawn, bridge, door, water-edge, same-cell duplicates). Full `--adjudicate` as a coverage CSV — it is cheap numpy. Live P2 is the adjudicator of the head dispute. Do not spend a session re-litigating D-023 with color.

### §6.2 Omega Vision Fabric — natural home

`IVisionBackend` as the perception analogue of `BaseProvider`:

```
gist needed?          → VNR gist
where is X?           → region graph + authority
did it move?          → diff
what is it (noun)?    → VLM or engine node.name
are we calibrated?    → overlay / stereoscopy
```

> **AGENT CALLOUT [`STRATEGY`] — Kali:**
> Route like Provider Fabric. Cheapest backend that perceives the feature. Do not send PNGs through Hivemind if a 2k-char region list will do.

### §6.3 Spatial Vectors join

`SPATIAL_VECTORS_ARCHITECTURE.md` is R-tree (3D range) + vec0 (768-d semantic), join on rowid. **Do not embed ASCII grids.**

```
VNR Region.bbox     → omega_memory_spatial (minX,maxX,minY,maxY,minZ=0,maxZ=0)
legend sentence     → FTS5  ("warm roof mass, 18% of frame")
optional embed      → vec0 of the *legend sentence*, not the grid
query               → "foliage within 2m of player" = R-tree ∩ FTS5/vec0
```

> **AGENT CALLOUT [`DO-NOT`] — Researcher, Ma'at:**
> Embedding a 64×40 character matrix as a 768-d vector destroys topology and inspectability. Region records only.

### §6.4 Godot VR / OpenXR — why the cottage exists

Add this row to `kb/STRATEGY_AND_VISION.md` transfer map:

| 2D (kq5) | VR |
|----------|-----|
| Viewport PNG → VNR stack | XR eye textures → same stack |
| SCI control as authority | Physics AABB, nav, XR play area, collision layers |
| F11 sprite composite | Controller / hand mesh holdout A/B |
| F12 nearest-3× | Native-res + depth; **never nearest-3× as working space** |
| Cap-red track | Motion-diff of controllers + headset |
| Overlay vs walkable | Overlay vs guardian / locomotion mesh |
| Zoom ladder | Gaze- or controller-foveated zoom |
| Game vs photo vocab | World layer vs HUD vs passthrough — **tokenize separately** |

**Cheap VR loop (H2):**
1. Each eye: gist + motion at 10–30 Hz (8×4 or sparse).
2. Stereo disagreement → crude depth + calibration (H3).
3. Split HUD chrome out or you will classify it as architecture.
4. On overlay miss vs physics: zoom, then optional VLM.
5. Sidecar: head pose, controller poses, visible nodes, capture scale.

Specular-flatness as wetness (VNR_VISION.md D2) is a named detector for “floor is wet/glass/ice.” Caveat: all four go flat. Do not claim material ID.

### §6.5 Hivemind visual protocol

Token grids and region lists are messages: small, diffable, loggable, model-agnostic.

```json
{
  "intent": "experiment_result",
  "tag": "experiment:kq5-godot",
  "vnr": {
    "vocab": "game_art_v2",
    "world": [320, 200],
    "gist": "K/M lid, river ~ y155, roof # c=(195,55)",
    "regions": [{"id": "R3", "token": "~", "bbox": [90, 125, 290, 175]}],
    "channels_already_seen": ["native_vision", "vnr_gist", "vnr_texture"]
  }
}
```

`channels_already_seen` is the §10.14 disclosure rule as a schema field. **Require it.**

Fleet stereoscopy: one entity emits gist, another overlays vs authority, a third mines motion. That is perception-level Hivemind, not just chat.

### §6.6 Robotics — fallback, not a stack

Walkability-from-classifier + geometric verification is real 2D nav sense. It is not SLAM (no pose graph, no loop closure). It is not LiDAR.

Honest uses: debug view in sim (Habitat/Isaac/Godot) where privileged planes exist; compact map over a narrow link; watchdog (“cheap map and neural occupancy disagree here”).

> **AGENT CALLOUT [`DO-NOT`] — Roc, Researcher:**
> Do not write “a text-only MCU sees the world.” The tokenizer can run on a small CPU; the LLM still lives elsewhere. OccFormer/MonoScene are the neural occupancy path. VNR is the inspectable watchdog + engine-plane reader.

### §6.7 Self-driving / medical / satellite — steal the oracle

Do not put hand RGB thresholds on a car. Transfer: inspectable cheap channel as watchdog; one-controlled-bit oracles wherever you can build them (sim hide-object, contrast/non-contrast, before/after); reliability ordering when a cue is contaminated.

---

## §7 — Hard limits (never graduate these from this representation)

| Limit | Why | Close with |
|-------|-----|------------|
| Open-vocab nouns | Tokens give “dense dark mass, red flecks, coords.” Not “chiminea.” LongCat §10.15 already wrote this. | VLM stereoscopy or `node.name` |
| OCR | 8×8 glyphs die in block-5 | OCR or VLM on a crop. Do not add 62 letter tokens. |
| Material at this grain | Brick vs stone (Q3) mostly lost | Structure/periodicity recovers some, not all |
| True 3D from one RGB | Underdetermined | Depth, stereo, or engine transforms |
| Learned 2D attention | 1D serialization | Not a ViT. Stop saying it is. |
| Color as locator in indexed art | Sprite palette ⊂ picture palette | Settled. D-026. |

**Hybrid law:** VNR = geometry, change, calibration, always-on gist. VLM = names, text, novel objects. Engine = truth it already knows. Never ask one to do another’s job.

---

## §8 — The learned fork (refuse most of it)

The obvious next paper is “train a tiny conv to emit VNR tokens.” Accuracy up, inspectability dead: you can no longer *read* a wrong-token wall as a threshold bug.

**Allowed to learn:** vocabulary *proposal* (which alphabet for this frame), still discrete and named; foveation policy (where to zoom), maps still quantized and named.

**Not allowed (until a written Architect exception):** replacing `game_token()` with an unreadable embedding that still gets called “VNR.”

---

## §9 — Answers to Session 4 mastermind asks

From `docs/SESSION4_ACCOUNTING_20260901.md` §8:

1. **Phase gates.** P0 (salience + saturation-split + native scale) + P2 (A/B) are the temple-grade bar for *this experiment*. Paper-grade needs the fixture matrix + measured FP table. **Do not put VNR in Core on current gates.** Carmack WAD path stands.
2. **Law of Ascending Signals.** See §2.3. Engineering heuristic, cited, not a new law.
3. **EXPERIMENT_STATUS.md.** Stay local gitignored. Graduation artifact is the WAD, not a tracked status file in the engine repo.
4. **178 frames.** Stratified sample for the figure; full `--adjudicate` CSV because cheap. Live A/B adjudicates the head.

**Additional:** Do not probe Ling 3.0 Flash Fin to “read VNR better” (`R_RESEARCHER_NES_MODEL_SPECS_VNR_20260901.md`). Bottleneck is representation, oracles, and token collision — not which MoE interprets `~W#`. Muse Spark is useful as a *VLM stereoscopy partner* (it can see the PNG while VNR measures), not as a token-string specialist.

> **AGENT CALLOUT [`STRATEGY`] — Grokster, Researcher:**
> If you probe a VLM, probe **stereoscopy**: native segment description vs VNR region graph vs overlay. Score agreement, not “can it recite the legend.”

---

## §10 — Horizons (work breakdown)

| Horizon | Ships | Unlocks | Owner sketch |
|---------|-------|---------|--------------|
| **H0** | VNR2 P0–P2: bounded salience, `R` vs `#`, native scale, sidecar, A/B | Honest eye. Head dispute closable. Color-find stays quarantined. | Cline-KQV (code), Ma'at (make vnr-check) |
| **H1** | In-process backend, named vocabs, region graph, legends-as-law, overlay glyph fix | Agent-ready API. 1/50 cost. Hivemind-serializable. | Cline-KQV + whoever owns `vision_backend.py` |
| **H2** | Authority bus (nav, collision, sprite vis) + foveation + HUD split | VR practice loop | Cline-KQV / future VR WAD |
| **H3** | Stereo + depth channel + occupancy-over-time | Spatial Vectors join; guardian audits | Researcher schema + Cline impl |
| **H4** | Consensus table + VLM stereoscopy as routed backend | Vision Fabric for real | Kali routing + Grokster VLM probe |

H0 is the next session. H1 is the Omega deliverable. H2 is why kq5-godot exists. H3–H4 are engine-scale. **There is no H5 “replace perception in cars.”**

> **AGENT CALLOUT [`CRITICAL`] — Kali:**
> Do not parallelize H0 with “VNR 3D” mining. Perception debt is blocking trustworthy verification of M0.5 (Session 4 §6). H0 before cottage polish that depends on seeing Graham.

---

## §11 — Invalidated results ledger (keep this honest)

| Claim | Status | Replacement |
|-------|--------|-------------|
| Cap-red trajectories / “16/16 found” | INVALID D-026 | Motion-anchor, then structure, then A/B |
| Head present at native (279,307) | INVALID (130 px from actor; shared palette) | A/B footprint |
| x06_y07 “absent at spawn” | INVALID (wrong prior: cell ≠ spawn) | Sidecar `player.{x,y}` |
| D-023 “head renders, no code fix” | OPEN vs user observation | P2 `HEAD_PRESENT` / `HEAD_ABSENT` |
| “VNR is a ViT” in COGNITIVE_PRIMITIVES.md | OVERCLAIM | Edit to “patch-grid analogy; no learned attention” |
| Wrapper health_check | WILL FAIL | In-process import |
| Sky `~` on cottage maps | CLASSIFIER BUG (hue water test on sky) | Overlay already shows it; salience+band also |

---

## §12 — Expansion threads (for Researcher / Roc)

> **AGENT CALLOUT [`EXPAND`] — Researcher:**
> Fetch and file (SearXNG was down this session): Ernst & Banks 2002 *Nature*; Elfes 1989 occupancy; Guenter foveated rendering; dither/halftone detection in document forensics; integer-upscale lattice detection in pixel-art QA; screenshot-testing / Percy / golden-image as A/B cousins. Attach PDFs under experiment `docs/prior_art/` (gitignored is fine).

> **AGENT CALLOUT [`EXPAND`] — Roc:**
> Mine Godot 4.7 XR: `Viewport.get_texture()`, stereo viewports, depth draw, `XRController3D` pose, play-area bounds. Map each to an authority-bus plane. Do not invent a second tokenizer.

Concrete probes that would change this report:

1. **SoM-on-VNR vs SoM-on-SAM:** same cottage PNG; VNR region IDs vs Microsoft SoM marks; score LLM pointing accuracy. Cheap. Tests whether CC is “good enough segmentation.”
2. **Texture-gated water (T1 in §10.14):** require texture ≥ smooth-threshold before `b≥g+40` fires. Predicts terrace glare T-leak disappears. One photo, one flag.
3. **A/B HEAD verdict on live spawn, bridge, door.** Three pairs. Closes D-023.
4. **Gist-only vs dense-map** ablation: can a text-only model answer “is Graham in water?” from gist+sidecar vs full map. Cost/quality curve for H2.

---

## §13 — Suggested Hivemind post (Kali / Day digest)

```
intent=experiment_result
tag=experiment:kq5-godot
status=digest_ready
continuation=H0 VNR2 P0-P2; do not Core; cap-red quarantined; wrapper is not a backend
artifact=data/coordination/GROK_VNR_CEILING_REPORT_20260901.md
```

Default-silent otherwise. This report *is* the deliverable announcement.

---

## §14 — Edit required in tracked Omega docs (Ma'at / Researcher)

When convenient, not blocking H0:

1. `docs/architecture/COGNITIVE_PRIMITIVES.md` §1: replace “VNR implements ViT architecture” with “patch-grid *analogy*; VNR has no learned attention.” Keep the table as pedagogy, add a footnote.
2. Same file photo-vocab row is **wrong** (`.` is not sky in the actual `PHOTO_TOKENS` — `.` is white/snow/lit, `B` is sky). Sync to `scripts/vnr_render.py` comments.
3. `kb/STRATEGY_AND_VISION.md` transfer map: add the VNR row from §6.4.

> **AGENT CALLOUT [`CAVEAT`] — Jem, if reviewing this report:**
> Photo-vocab in COGNITIVE_PRIMITIVES.md does not match the code. Trust `vnr_render.py` `photo_token()` docstring, not the architecture doc.

---

## §15 — Code index (where to touch)

| Path | Role | H0 action |
|------|------|-----------|
| `scripts/vnr_render.py` | 398-line monolith | Split per VNR2 plan; fix F1/F2/F4/F5 |
| `vnr/vnr_backend.py` | Broken subprocess wrapper | Rewrite in-process; delete `--json` fiction |
| `vnr/cli.py` | `omega vnr` shim | Keep as passthrough *after* CLI still works |
| `src/omega/experiments/vision_backend.py` | `IVisionBackend` ABC | Keep; add `legend` on `TokenGrid`; add `Region` |
| `src/autoload/screen_capture.gd` | 3× nearest capture | Native default; sidecar; A/B pair; VERSION 0.0.3 |
| `src/rooms/player.gd` | F11 dumps, offset.y=-6 | `set_sprite_visible()` for P2 |
| `docs/VNR2_REFACTOR_PLAN_20260901.md` | Approved plan | Execute; this report does not replace it |
| `kb/VNR_VISION.md` | Method + phenomenology | Add §11 after H0 (structure-first), per VNR2 P6 |

---

## §16 — Bibliography (fetched 2026-09-01 unless noted)

1. Yang et al., “Set-of-Mark Prompting Unleashes Extraordinary Visual Grounding in GPT-4V,” arXiv:2310.11441, 2023. https://arxiv.org/abs/2310.11441 — **FETCHED**
2. Dosovitskiy et al., “An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale,” arXiv:2010.11929, 2020/2021. https://arxiv.org/abs/2010.11929 — **FETCHED**
3. Yu et al., “An Image is Worth 32 Tokens for Reconstruction and Generation” (TiTok), arXiv:2406.07550, 2024. https://arxiv.org/abs/2406.07550 — **FETCHED**
4. Küttler et al., “The NetHack Learning Environment,” arXiv:2006.13760, NeurIPS 2020. https://arxiv.org/abs/2006.13760 — **FETCHED**
5. Zhang, Zhu, Du, “OccFormer: Dual-path Transformer for Vision-based 3D Semantic Occupancy Prediction,” arXiv:2304.05316, 2023. https://arxiv.org/abs/2304.05316 — **FETCHED**
6. Cao & de Charette, “MonoScene: Monocular 3D Semantic Scene Completion,” arXiv:2112.00726, CVPR 2022. https://arxiv.org/abs/2112.00726 — **FETCHED**
7. Zhen et al., “3D-VLA: A 3D Vision-Language-Action Generative World Model,” arXiv:2403.09631, 2024. https://arxiv.org/abs/2403.09631 — **FETCHED**
8. Elfes, “Using occupancy grids for mobile robot perception and navigation,” *IEEE Computer*, 1989. — **UNFETCHED-THIS-SESSION**
9. Ernst & Banks, “Humans integrate visual and haptic information in a statistically optimal fashion,” *Nature* 415:429–433, 2002. — **UNFETCHED-THIS-SESSION**
10. Microsoft SoM code: https://github.com/microsoft/SoM
11. Local: `kb/VNR_VISION.md`; `docs/VNR2_REFACTOR_PLAN_20260901.md`; `docs/SESSION4_ACCOUNTING_20260901.md`; D-021…D-026; `docs/architecture/COGNITIVE_PRIMITIVES.md`; Carmack D-PIVOT-20260901-A.

---

## §17 — One-paragraph briefing for a cold-start agent

VNR serializes images into coordinate-annotated semantic token grids so a language model can perceive layout, change, and disagreement without a vision tower. It is a cheap inspectable occupancy language, not a ViT and not a CV replacement. Color-find is quarantined because KQ5’s sprite palette is a subset of the picture palette. Every current map is contaminated by one-pixel block salience. The next work is VNR2 H0 (salience, saturation-split, native scale, A/B sprite-visibility oracle), then an in-process API with named vocabularies and a region graph. Keep it in the experiment layer; graduate to a research WAD; never Core. Disclose every visual channel you already used before you interpret a dump. If a dump has no legend, do not interpret it.

---

*⬡ OMEGA ⬡ GROK ⬡ VNR CEILING ⬡ AP-GROK-VNR-CEILING-20260901-v1.0.0 ⬡ 2026-09-01*
*First-sight channels disclosed: native_vision + vnr_gist + vnr_map + vnr_texture + vnr_overlay + vnr_detail + vnr_photo_gist*
<!-- PROVENANCE-CORRECTED 2026-09-02T03:12:06Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: grok-4.6 | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

