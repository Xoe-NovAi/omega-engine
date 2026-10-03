# SPDX-FileCopyrightText: 2026 XoE-NovAi
#
# SPDX-License-Identifier: Apache-2.0
"""VNR 2.0 track — LEGACY cap-red trajectory (quarantined, F3/D-026).

cap_find() is the instrument that produced the roof-contaminated
trajectories (153,900 roof px vs ~2,000 sprite px). Kept ONLY for
comparative re-adjudication until P3 replaces it with structure-based
tracking. Every output is stamped with a loud legacy warning.
"""
from __future__ import annotations

import glob
import os

import numpy as np
from PIL import Image, ImageDraw


def cap_find(a: np.ndarray):
    """Saturated red = Graham's cap (216,38,38) family. Returns (cx, cy, count)."""
    mask = (a[..., 0] >= 180) & (a[..., 0] <= 255) & (a[..., 1] <= 90) & (a[..., 2] <= 90)
    ys, xs = np.where(mask)
    if not len(xs):
        return None
    return float(xs.mean()), float(ys.mean()), int(len(xs))


def track_shots(dirpath: str, room_pic_path: str, version: str = "") -> dict:
    """Scan shot_*.png sorted, find cap-red per shot -> trajectory + path map.
    version: only track shots whose filename carries this version token.
    LEGACY (F3): cap-red centroids are roof-contaminated; results invalid
    for anatomy claims (see docs/VNR2_REFACTOR_PLAN_20260901.md)."""
    shots = sorted(glob.glob(os.path.join(dirpath, "shot_*.png")))
    if version:
        shots = [p for p in shots if f"_{version}_" in os.path.basename(p)]
    positions = []
    for p in shots:
        img = Image.open(p).convert("RGBA")
        a = np.array(img)
        sw, sh = a.shape[1], a.shape[0]
        r = cap_find(a)
        if r is None:
            positions.append((os.path.basename(p), None, None))
            continue
        cx, cy, n = r
        wx = cx * 320.0 / sw
        wy = cy * 200.0 / sh
        positions.append((os.path.basename(p), round(wx, 1), round(wy, 1)))
    room = Image.open(room_pic_path).convert("RGBA").resize((320, 200), Image.BOX)
    d = ImageDraw.Draw(room)
    pts = [(p[1], p[2]) for p in positions if p[1] is not None]
    if len(pts) >= 2:
        d.line(pts, fill=(255, 0, 255), width=2)
    for x, y in pts:
        d.ellipse([x-3, y-3, x+3, y+3], fill=(255, 0, 255))
    traj = ["TRAJECTORY (world coords, timestamp order):"]
    prev = None
    total = 0.0
    for name, x, y in positions:
        if x is None:
            traj.append(f"  {name}: NO CAP FOUND")
            continue
        if prev is not None:
            dist = ((x-prev[0])**2 + (y-prev[1])**2) ** 0.5
            total += dist
            traj.append(f"  {name}: ({x},{y})  step={dist:.1f}px")
        else:
            traj.append(f"  {name}: ({x},{y})  START")
        prev = (x, y)
    traj.append(f"  total path: {total:.1f} world px over {len(pts)} shots")
    arr = np.array(room)
    from .modes import grid_rows
    return {
        "legacy_warning": (
            "!! LEGACY cap-red trajectory (F3/D-026): cap_find centroids are "
            "roof-contaminated (153,900 roof px vs ~2,000 sprite px measured "
            "2026-09-01). INVALID for head/anatomy claims. Quarantined pending "
            "P3 motion-profile + P4 structure tracking."
        ),
        "trajectory": traj,
        "path_map": [
            f"y{i*5:3d} {row}"
            for i, row in enumerate(grid_rows(arr, "map", 5))
        ],
    }