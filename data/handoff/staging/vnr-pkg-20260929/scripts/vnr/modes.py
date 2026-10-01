# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
"""VNR 2.0 modes — grid construction, rendering payloads, gist/hist.

Modules RETURN data; only cli.py prints (VNR2 plan P0.1 discipline).
"""
from __future__ import annotations

import numpy as np
from PIL import Image

from .signals import (
    branch,
    branch_photo,
    luma_block,
    photo_token,
    pname,
    structure_block,
    texture_block,
)


def load(path: str) -> np.ndarray:
    img = Image.open(path).convert("RGBA")
    return np.array(img)


def to_world(a: np.ndarray, wandh) -> np.ndarray:
    h, w = a.shape[:2]
    if wandh:
        tw, th = wandh
        if (w, h) != (tw, th):
            # downscale by a lot => average (BOX); nearest would alias to noise
            a = np.array(Image.fromarray(a).resize((tw, th), Image.BOX))
    return a


def grid_rows(a: np.ndarray, mode: str, block: int, cset: str = "game",
              salience: float = 0.12) -> list[str]:
    h, w = a.shape[:2]
    rows = []
    for y in range(0, h, block):
        line = []
        for x in range(0, w, block):
            blk = a[y:y + block, x:x + block]
            if mode == "luma":
                ch = luma_block(blk)
            elif mode == "texture":
                ch = texture_block(blk)
            elif mode == "structure":
                ch = structure_block(blk)
            elif cset == "photo":
                ch = branch_photo(blk)
            else:
                ch = branch(blk, salience)
            line.append(ch)
        rows.append("".join(line))
    return rows


def render_rows(a: np.ndarray, mode: str, block: int, cset: str = "game",
                salience: float = 0.12, xy0=(0, 0)) -> list[str]:
    out = []
    for i, row in enumerate(grid_rows(a, mode, block, cset, salience)):
        y = xy0[1] + i * block
        out.append(f"y{y:3d} {row}")
    return out


def gist(a: np.ndarray) -> str:
    """Coarse named-region layout: 8x4 cells + dominant color list (v1 format)."""
    h, w = a.shape[:2]
    cell_h, cell_w = max(1, h // 4), max(1, w // 8)
    lines = [f"GIST {w}x{h}  cells {w//cell_w}x{h//cell_h} (cell {cell_h}x{cell_w})"]
    for gy in range(0, h - cell_h + 1, cell_h):
        parts = []
        for gx in range(0, w - cell_w + 1, cell_w):
            blk = a[gy:gy+cell_h, gx:gx+cell_w].reshape(-1, a.shape[-1])
            toks = [photo_token(px[0], px[1], px[2], px[3]) for px in blk]
            dom = max(set(toks), key=toks.count)
            fr = toks.count(dom) / max(1, len(toks))
            parts.append(f"{dom}{fr:.0%}")
        lines.append(f"  y{gy:3d} | " + " | ".join(parts))
    # dominant perceptual colors
    a2 = a[::max(1, a.shape[0]//120), ::max(1, a.shape[1]//200)]
    q = (a2.reshape(-1, a2.shape[-1]) // 24) * 24
    from collections import Counter
    cnt = Counter(map(lambda p: (int(p[0]), int(p[1]), int(p[2])), q[:, :3]))
    tot = sum(cnt.values())
    lines.append("  dominant colors:")
    for col, n in cnt.most_common(12):
        lines.append(f"    {pname(*col):16s} ({col[0]:3d},{col[1]:3d},{col[2]:3d}) {n/tot*100:4.1f}%")
    return "\n".join(lines)


def hist(a: np.ndarray) -> str:
    q = (a.reshape(-1, a.shape[-1]) // 24) * 24
    from collections import Counter
    cnt = Counter(map(lambda p: (int(p[0]), int(p[1]), int(p[2])) if p[3] > 0 else None, q))
    cnt.pop(None, None)
    tot = sum(cnt.values())
    lines = [f"HIST {tot} opaque px"]
    for col, n in cnt.most_common(16):
        lines.append(f"  {pname(*col):16s} ({col[0]:3d},{col[1]:3d},{col[2]:3d}) {n/tot*100:5.1f}%")
    return "\n".join(lines)