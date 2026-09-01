# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
# 🔱 Vision Backend Interface — Experiment Layer
# Perception provider abstraction for the Omega Engine.
# This is an EXPERIMENT-layer interface (not Core).
# See docs/architecture/COGNITIVE_PRIMITIVES.md for the primitive definitions.

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple
from PIL import Image


@dataclass
class TokenGrid:
    """Semantic token grid with coordinate rulers."""
    grid: List[List[str]]  # [row][col] = token character
    width: int
    height: int
    block_size: int
    world_width: int
    world_height: int
    vocabulary: str  # "game_art" or "photo"
    rulers: bool = True  # whether row/col rulers are included


@dataclass
class BoundingBox:
    """Bounding box with pixel coordinates."""
    x0: int
    y0: int
    x1: int
    y1: int
    pixel_count: int

    @property
    def width(self) -> int:
        return self.x1 - self.x0

    @property
    def height(self) -> int:
        return self.y1 - self.y0

    @property
    def center(self) -> Tuple[int, int]:
        return ((self.x0 + self.x1) // 2, (self.y0 + self.y1) // 2)


@dataclass
class DisagreementMap:
    """Spatial disagreement map between classifier and ground truth."""
    grid: List[List[str]]  # 'B'=both, '~'=classifier_only, '3'=ground_truth_only
    width: int
    height: int
    block_size: int
    stats: dict  # {'B': count, '~': count, '3': count}


@dataclass
class ChangeMap:
    """Semantic change detection between two images."""
    grid: List[List[str]]  # change indicators per block
    width: int
    height: int
    block_size: int
    change_percentage: float
    change_bbox: Optional[BoundingBox]


@dataclass
class Analysis:
    """Structured analysis result from a vision backend."""
    token_grid: TokenGrid
    texture_map: Optional[List[List[str]]] = None
    color_histogram: Optional[dict] = None
    gist: Optional[str] = None
    metadata: Optional[dict] = None


class IVisionBackend(ABC):
    """
    Abstract base class for vision backends.
    
    This is the perception equivalent of the Provider Fabric's BaseProvider.
    Different backends (VNR, neural vision, hybrid) implement this interface.
    The Vision Fabric routes to the cheapest backend that perceives the required features.
    
    This interface lives in the EXPERIMENT layer (src/omega/experiments/),
    not Core, because perception primitives are still in research phase.
    See docs/architecture/COGNITIVE_PRIMITIVES.md for primitive definitions.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable backend name."""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """List of supported capability names: 'tokenize', 'texture', 'overlay', 'find_color', 'diff', 'zoom', 'stereoscopy'."""
        pass

    @abstractmethod
    def tokenize(
        self,
        image: Image.Image,
        block_size: int = 5,
        vocabulary: str = "game_art",
        world_width: Optional[int] = None,
        world_height: Optional[int] = None,
    ) -> TokenGrid:
        """
        Convert image to semantic token grid with coordinate rulers.
        
        Primitive 1: Semantic Tokenization
        ViT-equivalent: patch embedding → discrete tokens
        """
        pass

    @abstractmethod
    def analyze_texture(
        self,
        image: Image.Image,
        block_size: int = 5,
    ) -> List[List[str]]:
        """
        Classify surface texture per block via luminance standard deviation.
        
        Primitive 2: Texture Classification
        Thresholds: flat(~4) → smooth(~10) → light(~22) → textured(~45) → dense
        """
        pass

    @abstractmethod
    def overlay(
        self,
        classifier_grid: TokenGrid,
        ground_truth_grid: TokenGrid,
    ) -> DisagreementMap:
        """
        Produce spatial disagreement map between classifier and ground truth.
        
        Primitive 3: Overlay / Disagreement Maps (XAI)
        Codes: 'B'=both, '~'=classifier_only, '3'=ground_truth_only
        """
        pass

    @abstractmethod
    def find_color(
        self,
        image: Image.Image,
        rgb_range: Tuple[int, int, int, int, int, int],  # r0,r1,g0,g1,b0,b1
    ) -> BoundingBox:
        """
        Locate objects by color range.
        
        Primitive 4: Color-Find / Object Localization
        Returns bounding box + pixel count.
        """
        pass

    @abstractmethod
    def diff(
        self,
        image1: Image.Image,
        image2: Image.Image,
        block_size: int = 5,
    ) -> ChangeMap:
        """
        Semantic change detection between two images.
        
        Primitive 5: Semantic Diff / Motion Detection
        Returns change map + percentage + change bounding box.
        """
        pass

    @abstractmethod
    def zoom(
        self,
        image: Image.Image,
        level: int,  # 1=context(5px), 2=identification(2px), 3=verification(1px)
        block_size: Optional[int] = None,
        crop: Optional[Tuple[int, int, int, int]] = None,  # x0,y0,x1,y1 in world coords
    ) -> TokenGrid:
        """
        Multi-scale perception at three levels.
        
        Primitive 6: Zoom Ladder / Multi-Scale Perception
        Level 1: Context (5px blocks, whole room)
        Level 2: Identification (2px blocks, ROI crop)
        Level 3: Verification (1px blocks, detail)
        """
        pass

    @abstractmethod
    def stereoscopy_calibrate(
        self,
        vnr_grid: TokenGrid,
        vision_model_grid: TokenGrid,
    ) -> dict:
        """
        Cross-calibrate VNR with a vision-capable model.
        
        Primitive 7: Multi-Model Stereoscopy
        Returns calibration data: token threshold adjustments, agreement stats.
        """
        pass

    def health_check(self) -> bool:
        """Quick health check — does the backend load and run?"""
        try:
            # Minimal test: 10x10 white image
            test_img = Image.new('RGB', (10, 10), (255, 255, 255))
            _ = self.tokenize(test_img, block_size=5)
            return True
        except Exception:
            return False


# Registry for available backends
_VISION_BACKENDS: dict[str, type[IVisionBackend]] = {}


def register_vision_backend(name: str, backend_class: type[IVisionBackend]) -> None:
    """Register a vision backend implementation."""
    _VISION_BACKENDS[name] = backend_class


def get_vision_backend(name: str) -> IVisionBackend:
    """Get a vision backend instance by name."""
    if name not in _VISION_BACKENDS:
        raise ValueError(f"Unknown vision backend: {name}. Available: {list(_VISION_BACKENDS.keys())}")
    return _VISION_BACKENDS[name]()


def list_vision_backends() -> List[str]:
    """List all registered vision backends."""
    return list(_VISION_BACKENDS.keys())


# Import and register VNR backend if available
try:
    from .vnr_backend import VisionBackendVNR
    register_vision_backend("vnr", VisionBackendVNR)
except ImportError:
    pass  # VNR backend not available (experiment not linked)