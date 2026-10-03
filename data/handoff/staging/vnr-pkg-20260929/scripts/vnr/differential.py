# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
"""VNR 2.0 differential — change maps (the FIRST signal in the law)."""
from __future__ import annotations

import numpy as np


def diff_maps(a: np.ndarray, b: np.ndarray, block: int, thresh: float):
    """Block-wise change map: . unchanged, + small, # big.
    Returns (rows, n_changed, n_total, bbox_of_big_changes)."""
    h, w = a.shape[:2]
    rows = []
    changed = []
    for y in range(0, h, block):
        line = []
        for x in range(0, w, block):
            da = a[y:y+block, x:x+block, :3].astype(int)
            db = b[y:y+block, x:x+block, :3].astype(int)
            d = float(np.abs(da - db).mean())
            if d > thresh:
                line.append("#")
                changed.append((x, y))
            elif d > thresh * 0.25:
                line.append("+")
            else:
                line.append(".")
        rows.append("".join(line))
    bbox = None
    if changed:
        cxs = [c[0] for c in changed]
        cys = [c[1] for c in changed]
        bbox = (min(cxs), min(cys), max(cxs), max(cys))
    return rows, len(changed), ((h + block - 1) // block) * ((w + block - 1) // block), bbox


def abdiff(a: np.ndarray, b: np.ndarray, noise_floor: float = 10.0):
    """A/B paired-frame differential oracle (plan P2, D-025).

    Noise-floored pixel mask -> largest connected component = sprite footprint.
    The pair differs ONLY in sprite presence, so the footprint IS the sprite.
    Returns (mask, footprint, bbox, n_changed, n_total); footprint/bbox are None
    when no component survives the noise floor (=> SPRITE_ABSENT).
    """
    h, w = a.shape[:2]
    diff = np.abs(a[:, :, :3].astype(int) - b[:, :, :3].astype(int)).mean(axis=2)
    mask = diff > noise_floor
    n_changed = int(mask.sum())
    n_total = h * w
    if n_changed == 0:
        return mask, None, None, 0, n_total

    # Connected components over changed pixels only (sparse BFS, O(n_changed)).
    visited = np.zeros_like(mask)
    changed = np.argwhere(mask)
    components: list = []
    for idx in range(len(changed)):
        py, px = int(changed[idx][0]), int(changed[idx][1])
        if visited[py, px]:
            continue
        component: list = []
        stack = [(py, px)]
        while stack:
            cy, cx = stack.pop()
            if cy < 0 or cy >= h or cx < 0 or cx >= w:
                continue
            if visited[cy, cx] or not mask[cy, cx]:
                continue
            visited[cy, cx] = True
            component.append((cy, cx))
            stack.extend([(cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)])
        components.append(component)

    if not components:
        return mask, None, None, n_changed, n_total
    largest = max(components, key=len)
    footprint = np.zeros_like(mask)
    for py, px in largest:
        footprint[py, px] = True
    ys = [p[0] for p in largest]
    xs = [p[1] for p in largest]
    bbox = (int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys)))
    return mask, footprint, bbox, n_changed, n_total


def verdict(footprint, bbox, head_region: dict = None,
             expected_height: int = 90, head_height_ratio: float = 0.6) -> str:
    """HEAD verdict from a sprite footprint (plan P2, D-025).

    Three-valued: HEAD_PRESENT / HEAD_ABSENT / SPRITE_ABSENT.

    State-aware path (head_region from the capture sidecar): checks whether the
    footprint overlaps the EXPECTED head band (rows 0-14 native = top 45 screen
    rows at 3x capture). Density in that band >= 0.1 => HEAD_PRESENT. This is
    the AUTHORITATIVE path — it knows where the head SHOULD be.

    Heuristic path (no sidecar): compares bbox height to the expected full sprite
    height. The head band is the top ~15 native rows; a headless sprite renders
    at roughly half the full height. bbox_height / expected_height >= ratio =>
    HEAD_PRESENT. Use only when the state sidecar is unavailable.
    """
    if footprint is None:
        return "SPRITE_ABSENT"
    total = int(footprint.sum())
    if total == 0:
        return "SPRITE_ABSENT"
    x0, y0, x1, y1 = bbox

    if head_region is not None:
        hr_x0 = max(x0, int(head_region["x_left"]))
        hr_y0 = max(y0, int(head_region["y_top"]))
        hr_x1 = min(x1, int(head_region["x_right"]))
        hr_y1 = min(y1, int(head_region["y_bottom"]))
        if hr_x1 < hr_x0 or hr_y1 < hr_y0:
            return "HEAD_ABSENT"
        head_pixels = int(footprint[hr_y0:hr_y1 + 1, hr_x0:hr_x1 + 1].sum())
        if head_pixels == 0:
            return "HEAD_ABSENT"
        region_area = (hr_x1 - hr_x0 + 1) * (hr_y1 - hr_y0 + 1)
        density = head_pixels / region_area
        return "HEAD_PRESENT" if density >= 0.1 else "HEAD_ABSENT"

    # Heuristic: bbox height vs expected full sprite height (30 native rows * 3x).
    bbox_height = y1 - y0 + 1
    ratio = bbox_height / expected_height
    return "HEAD_PRESENT" if ratio >= head_height_ratio else "HEAD_ABSENT"


def head_row_profile(footprint: np.ndarray, head_region: dict) -> list[int]:
    """DIAGNOSTIC 5b: per-row pixel count in the head region.
    
    Returns list of pixel counts per row (top to bottom).
    If top rows are zero while lower rows populated -> crown truncation.
    """
    hr_x0 = max(0, int(head_region["x_left"]))
    hr_y0 = max(0, int(head_region["y_top"]))
    hr_x1 = min(footprint.shape[1] - 1, int(head_region["x_right"]))
    hr_y1 = min(footprint.shape[0] - 1, int(head_region["y_bottom"]))
    if hr_x1 < hr_x0 or hr_y1 < hr_y0:
        return []
    return [int(footprint[y, hr_x0:hr_x1 + 1].sum()) for y in range(hr_y0, hr_y1 + 1)]