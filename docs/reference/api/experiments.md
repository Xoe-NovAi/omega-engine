# 🔱 Experiments — Vision Backend & Perception Primitives
**AP Token**: `AP-EXPERIMENTS-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_doc_ref ⬡ STANDARD

**Date**: 2026-10-02
**Purpose**: Reference documentation for the Experiments package — Vision Backend interface and perception primitives for cognitive architecture research.
**Tags**: experiments, vision, perception, cognitive-primitives, backend, abstraction
**Cross-references**: src/omega/experiments/vision_backend.py, docs/architecture/COGNITIVE_PRIMITIVES.md

---

## Overview

The `experiments` package contains **experimental-layer** interfaces for perception and cognitive primitives. This is **not Core** — it lives in the Experiment layer because perception primitives are still in research phase.

The primary component is the **Vision Backend Interface** — an abstraction layer for vision providers (VNR, neural vision, hybrid) analogous to the Provider Fabric for language models.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Experiments Package                       │
├─────────────────────────────────────────────────────────────┤
│  vision_backend.py   │  IVisionBackend — perception ABC     │
│                      │  Data classes (TokenGrid, etc.)      │
│                      │  Backend registry                    │
└─────────────────────────────────────────────────────────────┘
```

**Key Principle**: The Vision Fabric routes to the cheapest backend that perceives the required features — same philosophy as the Provider Fabric for LLMs.

---

## Perception Primitives (7 Primitives)

Defined in `docs/architecture/COGNITIVE_PRIMITIVES.md`:

| # | Primitive | Description | ViT Equivalent |
|---|-----------|-------------|----------------|
| 1 | **Semantic Tokenization** | Image → semantic token grid with coordinate rulers | Patch embedding → discrete tokens |
| 2 | **Texture Classification** | Surface texture per block via luminance std dev | — |
| 3 | **Overlay / Disagreement Maps** | Spatial disagreement between classifier & ground truth | XAI / attribution |
| 4 | **Color-Find / Object Localization** | Locate objects by RGB range | — |
| 5 | **Semantic Diff / Motion Detection** | Change detection between two images | — |
| 6 | **Zoom Ladder / Multi-Scale** | 3 levels: Context (5px) → ID (2px) → Verification (1px) | Pyramid / FPN |
| 7 | **Multi-Model Stereoscopy** | Cross-calibrate VNR with vision-capable model | Ensemble / distillation |

---

## Data Classes

### TokenGrid
```python
@dataclass
class TokenGrid:
    grid: List[List[str]]        # [row][col] = token character
    width: int
    height: int
    block_size: int
    world_width: int
    world_height: int
    vocabulary: str              # "game_art" or "photo"
    rulers: bool = True          # Row/col rulers included
```

### BoundingBox
```python
@dataclass
class BoundingBox:
    x0: int; y0: int; x1: int; y1: int
    pixel_count: int
    
    @property
    def width(self) -> int: return self.x1 - self.x0
    @property
    def height(self) -> int: return self.y1 - self.y0
    @property
    def center(self) -> Tuple[int, int]: return ((x0+x1)//2, (y0+y1)//2)
```

### DisagreementMap
```python
@dataclass
class DisagreementMap:
    grid: List[List[str]]        # 'B'=both, '~'=classifier_only, '3'=ground_truth_only
    width: int
    height: int
    block_size: int
    stats: dict                  # {'B': count, '~': count, '3': count}
```

### ChangeMap
```python
@dataclass
class ChangeMap:
    grid: List[List[str]]        # Change indicators per block
    width: int
    height: int
    block_size: int
    change_percentage: float
    change_bbox: Optional[BoundingBox]
```

### Analysis
```python
@dataclass
class Analysis:
    token_grid: TokenGrid
    texture_map: Optional[List[List[str]]] = None
    color_histogram: Optional[dict] = None
    gist: Optional[str] = None
    metadata: Optional[dict] = None
```

---

## IVisionBackend (Abstract Base Class)

```python
class IVisionBackend(ABC):
    """Perception equivalent of Provider Fabric's BaseProvider."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable backend name."""
    
    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """Supported capabilities: 'tokenize', 'texture', 'overlay', 
        'find_color', 'diff', 'zoom', 'stereoscopy'."""
    
    @abstractmethod
    def tokenize(self, image: Image.Image, block_size: int = 5,
                 vocabulary: str = "game_art",
                 world_width: Optional[int] = None,
                 world_height: Optional[int] = None) -> TokenGrid:
        """Primitive 1: Semantic Tokenization."""
    
    @abstractmethod
    def analyze_texture(self, image: Image.Image, block_size: int = 5) -> List[List[str]]:
        """Primitive 2: Texture Classification.
        Thresholds: flat(~4) → smooth(~10) → light(~22) → textured(~45) → dense"""
    
    @abstractmethod
    def overlay(self, classifier_grid: TokenGrid, ground_truth_grid: TokenGrid) -> DisagreementMap:
        """Primitive 3: Overlay / Disagreement Maps (XAI).
        Codes: 'B'=both, '~'=classifier_only, '3'=ground_truth_only"""
    
    @abstractmethod
    def find_color(self, image: Image.Image, 
                   rgb_range: Tuple[int, int, int, int, int, int]) -> BoundingBox:
        """Primitive 4: Color-Find / Object Localization.
        rgb_range = (r0, r1, g0, g1, b0, b1)"""
    
    @abstractmethod
    def diff(self, image1: Image.Image, image2: Image.Image, 
             block_size: int = 5) -> ChangeMap:
        """Primitive 5: Semantic Diff / Motion Detection."""
    
    @abstractmethod
    def zoom(self, image: Image.Image, level: int,
             block_size: Optional[int] = None,
             crop: Optional[Tuple[int, int, int, int]] = None) -> TokenGrid:
        """Primitive 6: Zoom Ladder / Multi-Scale Perception.
        Level 1: Context (5px blocks, whole room)
        Level 2: Identification (2px blocks, ROI crop)
        Level 3: Verification (1px blocks, detail)"""
    
    @abstractmethod
    def stereoscopy_calibrate(self, vnr_grid: TokenGrid, 
                              vision_model_grid: TokenGrid) -> dict:
        """Primitive 7: Multi-Model Stereoscopy.
        Returns calibration data: token threshold adjustments, agreement stats."""
    
    def health_check(self) -> bool:
        """Quick health check — does backend load and run?"""
        try:
            test_img = Image.new('RGB', (10, 10), (255, 255, 255))
            _ = self.tokenize(test_img, block_size=5)
            return True
        except Exception:
            return False
```

---

## Backend Registry

```python
from omega.experiments import (
    register_vision_backend,
    get_vision_backend,
    list_vision_backends
)

# Register custom backend
register_vision_backend("my_backend", MyVisionBackend)

# Get backend instance
backend = get_vision_backend("vnr")

# List available
backends = list_vision_backends()  # ["vnr", ...]
```

**Built-in**: VNR backend (if available) — `from .vnr_backend import VisionBackendVNR`

---

## Usage Example

```python
from omega.experiments import get_vision_backend
from PIL import Image

# Load image
image = Image.open("screenshot.png")

# Get VNR backend (cheapest for tokenization)
backend = get_vision_backend("vnr")

# Primitive 1: Tokenize
token_grid = backend.tokenize(
    image, 
    block_size=5, 
    vocabulary="game_art",
    world_width=800,
    world_height=600
)
print(f"Grid: {token_grid.width}x{token_grid.height}, vocab: {token_grid.vocabulary}")

# Primitive 2: Texture
texture_map = backend.analyze_texture(image, block_size=5)

# Primitive 4: Find red objects
red_box = backend.find_color(image, (200, 255, 0, 50, 0, 50))
print(f"Red object at: {red_box.center}, pixels: {red_box.pixel_count}")

# Primitive 5: Detect change
prev_image = Image.open("prev_screenshot.png")
change_map = backend.diff(prev_image, image, block_size=5)
print(f"Change: {change_map.change_percentage:.1f}%")

# Primitive 6: Multi-scale
context_grid = backend.zoom(image, level=1)      # 5px, whole room
id_grid = backend.zoom(image, level=2, crop=(100,100,300,300))  # 2px, ROI
detail_grid = backend.zoom(image, level=3, crop=(150,150,200,200)) # 1px, detail

# Primitive 7: Stereoscopy calibration
vision_model = get_vision_backend("neural_vision")
vision_grid = vision_model.tokenize(image, block_size=5)
calibration = backend.stereoscopy_calibrate(token_grid, vision_grid)
print(f"Calibration: {calibration}")
```

---

## Texture Classification Thresholds

| Class | Luminance Std Dev Range |
|-------|------------------------|
| `flat` | ~0-4 |
| `smooth` | ~4-10 |
| `light` | ~10-22 |
| `textured` | ~22-45 |
| `dense` | >45 |

---

## Mandate Compliance

| Mandate | Compliance |
|---------|------------|
| **M1 AnyIO** | Sync interface; async callers wrap in `anyio.to_thread` |
| **M2 Firewall** | Experiment layer — no engine dependencies |
| **M7 Local-First** | VNR backend runs locally; no cloud vision APIs |
| **M13 Temple-Grade** | Abstract interface enables swap/test |
| **M23 Failure Integrity** | `health_check()` for liveness; abstract methods = explicit contract |

---

## Heritage

- [heritage: quake3-1999] netchan — perception primitives as networked cognitive channels

---

## Testing

```bash
pytest tests/test_vision_backend.py -v
```

Key test scenarios:
- VNR backend tokenization accuracy
- Texture classification thresholds
- Disagreement map codes
- Color-find bounding box accuracy
- Change detection sensitivity
- Zoom ladder level consistency
- Stereoscopy calibration output format

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ EXPERIMENTS-v1.0.0 ⬡ 2026-10-02 ⬡*