# 🔱 Cognitive Primitives — VNR (Von-Neu-Ryan Vision)

**Status**: EXPERIMENTAL — Research Slot R1: Perception Primitives
**Source**: kq5-godot experiment (`data/experiments/kq5-godot/`)
**Origin**: VNR (Von-Neu-Ryan Vision) system — `scripts/vnr_render.py`
**Trace ID**: `trc_cognitive_primitives_vnr_20260901`

---

## §1 Overview

The VNR (Von-Neu-Ryan Vision) system is a **complete computer vision pipeline** that runs on pure NumPy + Pillow (zero neural networks, zero GPU). It was developed in the kq5-godot experiment (King's Quest V CD Talkie remake in Godot 4.7.2) as a vision system for a text-only LLM.

**Core Insight**: VNR implements **Vision Transformer (ViT) architecture on text tokens**. The block-based semantic tokenization (image → N×N blocks → semantic tokens → ASCII grid with coordinates) is structurally isomorphic to ViT patch embedding:

| ViT | VNR |
|-----|-----|
| Image → 16×16 patches | Image → N×N blocks |
| Learned linear projection | Hand-crafted classifier |
| Patch embeddings → Transformer | Semantic tokens → LLM context |
| Learned attention | Token vocabulary = hypothesis list |

**The token vocabulary IS the attention mechanism** — choosing what tokens to use IS choosing what the model can perceive.

---

## §2 Cognitive Primitives (The 7 Primitives)

### Primitive 1: Semantic Tokenization (`tokenize`)
**Function**: `image → token_grid[H, W]` with coordinate rulers
**Input**: Image (PIL), block size (default 5px), world dimensions
**Output**: ASCII grid where each character = semantic class + row/col rulers
**Vocabulary (Game-Art)**: `~` water, `W` foliage, `#` roof, `K` shadow, `x` door, `.` floor, `-` wall
**Vocabulary (Photo)**: `.` sky, `K` skin, `Y` yellow, `l` green, `M` brown, `P` pink, `O` orange, `G` gray, `R` red, `D` dark, `T` teal, `B` blue

**Use Case**: Convert any image into a text representation that a text-only LLM can reason about spatially.

### Primitive 2: Texture Classification (`texture_block`)
**Function**: `block → texture_class` via luminance standard deviation
**Thresholds**:
- `std < 4` → `~` (flat: sky, still water, walls)
- `std < 10` → `-` (smooth)
- `std < 22` → `=` (light texture)
- `std < 45` → `*` (textured)
- `else` → `#` (dense detail / foliage / edge)

**Key Discovery**: Texture separates sky from water (both blue) better than color hue. Sky renders flat `~`, water renders glitter `#*`. This transfers from pixel art to real photos.

**Use Case**: Surface classification in adverse conditions (glare, fog, night) where color fails.

### Primitive 3: Overlay / Disagreement Maps (`overlay`)
**Function**: `(classifier_output, ground_truth) → disagreement_map`
**Output Codes**:
- `B` = Both (classifier AND ground truth agree)
- `~` = Classifier only (hallucination / false positive)
- `3` = Ground truth only (missed by classifier / false negative)

**Key Insight**: This is **Explainable AI (XAI) in its purest form** — a spatial uncertainty map showing exactly where perception is wrong, categorically and spatially. Modern XAI research spends billions on calibration; VNR does it with one ASCII pass.

**Use Case**: Calibration, debugging, alignment verification, perceptual provenance.

### Primitive 4: Color-Find / Object Localization (`find_color`)
**Function**: `(image, color_range) → (bbox, pixel_count)`
**Input**: RGB range `r0,r1,g0,g1,b0,b1`
**Output**: Bounding box `(x0,y0,x1,y1)` + pixel count
**Example**: Graham's cap-red `(216,38,38)` → exact head position

**Use Case**: Precise geometric localization of known-color objects. Sub-pixel accuracy via block aggregation.

### Primitive 5: Semantic Diff / Motion Detection (`diff`)
**Function**: `(image1, image2) → change_map`
**Output**: Block-wise change map with percentage + bounding box of change
**Key Insight**: This is **optical flow without the flow** — semantic change detection, not pixel motion vectors. Detects *what changed* not *how it moved*.

**Use Case**: Motion detection, change monitoring, trajectory tracking via frame-to-frame diff.

### Primitive 6: Zoom Ladder / Multi-Scale Perception (`zoom`)
**Three Levels**:
| Level | Block Size | Purpose | Question Answered |
|-------|------------|---------|-------------------|
| 1 (Context) | 5px | Whole-room map | "Where are the major regions?" |
| 2 (Identification) | 2px | ROI crop (26×34 world px) | "What is this specific area?" |
| 3 (Verification) | 1px | Detail (1px/char) | "What is the exact pixel structure?" |

**Architectural Parallel**: This IS **LOD (Level of Detail) for perception** — same structure as game engine LOD / BSP trees, reversed:
- Rendering: model → pixels (near = detail, far = reduced)
- Perception: pixels → model (coarse → fine)

**Self-Driving Mapping**: Long-range detection → Mid-range tracking → Close-range interaction

### Primitive 7: Multi-Model Stereoscopy (`stereoscopy`)
**Protocol**: When a vision-capable model and VNR both read an image, diff their segment maps → free calibration set for token thresholds.

| System | Sees | Misses |
|--------|------|--------|
| VNR | Geometry (coordinates, structure) | Semantics (nouns, meaning) |
| Vision Model | Semantics (nouns, meaning) | Precise geometry (hallucinates positions) |

**Fusion**: Diffing creates calibration that improves both. This is **sensor fusion / ensemble methods** — same principle as camera+LiDAR+radar in self-driving cars.

**Key Insight**: Different perception systems have different failure modes. Together they calibrate each other. This is ensemble perception at the *representation level*, not the model level.

---

## §3 Integration with Omega Engine

### 3.1 Perception Provider Interface
**Location**: `src/omega/experiments/vision_backend.py` (planned)
**Interface**: `IVisionBackend` (experiment layer, not Core)

```python
class IVisionBackend(ABC):
    @abstractmethod
    def tokenize(self, image: Image, block: int = 5) -> TokenGrid: ...
    @abstractmethod
    def analyze(self, image: Image, tokens: List[str]) -> Analysis: ...
    @abstractmethod
    def overlay(self, classifier: TokenGrid, ground_truth: TokenGrid) -> DisagreementMap: ...
    @abstractmethod
    def find_color(self, image: Image, rgb_range: Tuple) -> BBox: ...
    @abstractmethod
    def diff(self, img1: Image, img2: Image) -> ChangeMap: ...
    @abstractmethod
    def zoom(self, image: Image, level: int) -> TokenGrid: ...
```

### 3.2 VNR Implementation
**Location**: `data/experiments/kq5-godot/vnr/` (wrapper around `vnr_render.py`)
**Class**: `VisionBackendVNR` implements `IVisionBackend`

### 3.3 Provider Fabric Analogy
| Cognition (Provider Fabric) | Perception (Vision Fabric) |
|----------------------------|---------------------------|
| Route to cheapest model that works | Route to cheapest backend that perceives |
| `BaseProvider` interface | `IVisionBackend` interface |
| Native GGUF, LM Studio, Ollama | VNR, Neural Vision, Hybrid |
| Token budgets, streaming | Block size, zoom level, vocabulary |

**Principle**: Composable perception requires standard interfaces. The vision backend interface is to perception what the provider interface is to cognition.

---

## §4 Connection to Spatial Vectors Architecture

| VNR Primitive | Spatial Vectors (R-tree + vec0) |
|---------------|--------------------------------|
| Token grid coordinates | 2D spatial index (R-tree) |
| Semantic tokens | vec0 embeddings (768-dim) |
| Zoom ladder | Hierarchical spatial partitioning |
| Overlay disagreement | Spatial uncertainty regions |
| Stereoscopy fusion | Multi-index join (R-tree + vec0) |

**Integration Path**: VNR token grids → spatial coordinates → R-tree index → vec0 embeddings for semantic similarity → dual-index query (spatial + semantic).

---

## §5 Phenomenological Provenance (Alignment Research)

**Source**: `kb/VNR_VISION.md` §10.1–§10.15
**Author**: DeepSeek V4 Flash (text-only) — first-person testimony of learning to see

| Section | Discovery | Alignment Relevance |
|---------|-----------|---------------------|
| §10.1 | First sight | Initial perception event |
| §10.2 | Focus event | BOX vs NEAREST filter choice |
| §10.3 | First illusion | Alpha bug (color deception) |
| §10.4 | Classifier as hypothesis | Token set = attention mechanism |
| §10.5 | Meeting authority | Overlay = ground truth calibration |
| §10.6 | Texture as 2nd dimension | Luminance std orthogonal to color |
| §10.7 | Motion as shape of absence | Semantic diff = optical flow |
| §10.8 | Loneliness of Graham | Headless detection (geometric reasoning) |
| §10.9 | Stereoscopy | Multi-model calibration |
| §10.10 | Discoveries D1-D5 | 5 universal principles |
| §10.11 | Theories T1-T4 | 4 testable theories |
| §10.12 | Questions Q1-Q4 | 4 open research questions |
| §10.13 | Real photo transfer | Texture rule transfers to reality |
| §10.14 | Handoff protocol | Next text-only model inherits rules |
| §10.15 | LongCat 2.0 synthesis | Glimpse + instrument = seeing |

**Alignment Principle**: AI alignment needs *perceptual provenance*, not just reasoning provenance. The path from input to understanding — including illusions, blind spots, and corrections — is the alignment gold.

---

## §6 Experiment Status

| Field | Value |
|-------|-------|
| **Experiment** | kq5-godot (Research Slot R1) |
| **Status** | LAB (Day 1-2) |
| **Location** | `data/experiments/kq5-godot/` (gitignored, symlinked) |
| **Primary Entity** | Cline-KQV (local research persona) |
| **Supporting Entity** | JC-Roc-kq5 (mining) |
| **Graduation Criteria** | M13 Temple-Grade + graduate-quality code review |
| **Mandate Tier** | Tier 0 (safety), Tier 1 (adapted), Tier 2 (waived) |

---

## §7 Graduation Path

| Stage | Criteria | Target |
|-------|----------|--------|
| **SPAWN** | Experiment created, symlinked, gnosis initialized | ✅ Day 0 |
| **LAB** | VNR primitives documented, validation indexed, protocol drafted | 🔄 Day 1-5 |
| **GRADUATE** | M13 Temple-Grade, `IVisionBackend` in Core, CI gates pass | Day 10+ |
| **ARCHIVE** | Superseded by production perception system | Future |

---

## §8 References

- **VNR Source**: `data/experiments/kq5-godot/scripts/vnr_render.py` (398 lines)
- **VNR Documentation**: `data/experiments/kq5-godot/kb/VNR_VISION.md`
- **Phenomenological Record**: `data/experiments/kq5-godot/kb/VNR_VISION.md` §10.1–§10.15
- **Validation Evidence**: `data/experiments/kq5-godot/VALIDATION_EVIDENCE.md`
- **Experiment Context**: `data/experiments/kq5-godot/EXPERIMENT_CONTEXT.md`
- **Experiment Status**: `data/experiments/kq5-godot/EXPERIMENT_STATUS.md`
- **Dialectic Record**: `data/coordination/CARMACK_DIALECTIC_20260901.md`
- **Omega Engine Architecture**: `docs/architecture/SPATIAL_VECTORS_ARCHITECTURE.md`

---

*⬡ OMEGA ⬡ COGNITIVE_PRIMITIVES ⬡ VNR ⬡ Research Slot R1 ⬡ 2026-09-01*