# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
"""VNR 2.0 locate — pixel-mask bounding boxes (geometry prime)."""
from __future__ import annotations

import numpy as np


def find_bbox(a: np.ndarray, rng):
    """Axis-aligned bbox of pixels inside an RGB range. Returns
    (x0, y0, x1, y1, count) or None. NOTE (I-013): a bbox over a whole frame
    is NOT a localization — background pixels inside the range dominate.
    Always sanity-check bbox area against the expected object size."""
    r0, r1, g0, g1, b0, b1 = rng
    mask = ((a[...,0]>=r0)&(a[...,0]<=r1)&(a[...,1]>=g0)&(a[...,1]<=g1)&(a[...,2]>=b0)&(a[...,2]<=b1))
    ys, xs = np.where(mask)
    if ys.size == 0:
        return None
    return xs.min(), ys.min(), xs.max(), ys.max(), int(mask.sum())