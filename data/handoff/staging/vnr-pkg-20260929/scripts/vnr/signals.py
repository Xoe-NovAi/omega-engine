# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
"""VNR 2.0 signals — token classifiers, block classifiers, scale detection.

Law of Ascending Signals: locate/verify via (1) change, (2) geometry,
(3) texture statistics. Color LAST, never sole evidence.

This module imports numpy/stdlib ONLY (VNR2 plan P0.1).
"""
from __future__ import annotations

import numpy as np

WRAMPS = list(" .:-=+*#%@")   # luminance ramp (10 steps)
SIG_TOKENS = "~W#xKR"          # game priority tokens (any-signal family, v2)
SIG_TOKENS_V1 = "~W#xK"        # v1.0.2 priority set (pre R-split) — parity harness only
DEFAULT_SALIENCE = 0.12        # min block fraction for a priority token to fire (D-024)
LEGACY_WARM = False            # parity harness: disable R-split -> exact v1 warm '#'


def game_token(r: int, g: int, b: int, a: int = 255) -> str:
    """Game-art token (KQ5 palette).

    v1.0.2 'token' + F2 saturation split: salient warm chroma (sat>=140,
    e.g. Graham's cap 216,38,38) -> 'R'; warm surfaces (sat<140, e.g. roof
    brown 135,79,39) stay '#'. Fixes the D-023 cap/roof conflation.
    """
    r, g, b, a = int(r), int(g), int(b), int(a)   # uint8 wrap corrupts lum (sum overflow)
    if a == 0:
        return " "
    lum = (r + g + b) / 3.0
    if b >= 120 and b >= r + 25 and b >= g + 15:
        return "~"                      # bright water / river
    if b >= r + 10 and b >= g + 5 and lum < 120:
        return "x"                      # dark teal shadow / murky water
    if g >= r + 8 and g >= b + 8:
        return "W"                      # foliage
    if r >= b + 16 and r >= g + 14:
        if LEGACY_WARM:
            return "#"                      # parity: exact v1 warm semantics (no R split)
        sat = max(r, g, b) - min(r, g, b)
        return "R" if sat >= 140 else "#"   # salient red vs warm roof/wood/rust
    if lum > 175:
        return "."                      # light wall / sky / highlight
    if lum < 42:
        return "K"                      # black shadow / interior
    return "-"                          # mid-tone path / ground


def photo_token(r: int, g: int, b: int, a: int = 255) -> str:
    """Perceptual photo token, v2.

    v2 change (man-made fix): NEW 'N' = true neutral (sat<12, lum>=128).
    v1 collapsed white cards, paper and plastic into the same 'l' token as
    tinted backgrounds; the chroma gate separates achromatic surfaces from
    tinted ones. All chromatic families are unchanged from v1 (byte-stable
    for chromatic content). Legend: N true-neutral white/gray achromatic.
    """
    r, g, b, a = int(r), int(g), int(b), int(a)   # uint8 wrap corrupts lum (sum overflow)
    if a == 0:
        return " "
    r, g, b = int(r), int(g), int(b)
    lum = (r + g + b) / 3.0
    mx = max(r, g, b); mn = min(r, g, b); sat = mx - mn
    if sat < 12 and lum >= 128:
        return "N"                      # true neutral: cards, paper, plastic, concrete
    if lum > 238 and sat < 36:
        return "."
    if lum < 35:
        return "K"
    if sat < 34:
        return "l" if lum > 118 else "M"
    if r >= g and r >= b:
        if b >= g + 42:
            return "P"
        if g >= b + 42:
            return "Y" if r >= 188 else "O"
        return "R"
    if g >= r and g >= b:
        return "G" if g >= 88 else "D"
    if g >= r + 22 and b < g + 40:
        return "T"
    return "B"


def pname(r: int, g: int, b: int) -> str:
    """Named color for gist/hist (verbatim v1)."""
    r, g, b = int(r), int(g), int(b)
    lum = (r + g + b) / 3.0
    mx = max(r, g, b); mn = min(r, g, b); sat = mx - mn
    if lum > 235 and sat < 40: return "white"
    if lum < 35: return "black"
    if sat < 35:
        if lum < 90: return "dark gray"
        if lum < 160: return "gray"
        return "light gray"
    if r >= g and r >= b:
        if b >= g + 40: return "pink-magenta"
        if g >= b + 40:
            if r < 120: return "olive-khaki"
            if r < 190: return "orange-tan"
            return "yellow-gold"
        if r < 120: return "dark red-brown"
        if r < 190: return "red-orange"
        return "red"
    if g >= r and g >= b:
        if g < 80: return "dark green"
        if g < 140: return "green"
        return "light green"
    if g >= r + 20 and b < g + 40: return "teal-water"
    if b < 70: return "dark blue"
    if b < 130: return "sea blue"
    return "sky blue"


def branch(block: np.ndarray, salience: float = DEFAULT_SALIENCE) -> str:
    """Block -> game token.

    salience >= 0 (v2, default 0.12): a priority token fires only when it
    holds >= salience of the block (F1 fix — one hat pixel in a 64-px block
    no longer flips it). salience == 0: fire on >=1 px (v1 counting, v2 SIG set).
    salience <= -1: EXACT v1.0.2 semantics (v1 SIG set without the R split,
    fire on >=1 px) — reserved for the P1 byte-parity harness."""
    pxs = block.reshape(-1, block.shape[-1])
    toks = [game_token(px[0], px[1], px[2], px[3]) for px in pxs]
    n = len(toks)
    if salience <= -1:
        for s in SIG_TOKENS_V1:
            if toks.count(s) >= 1:
                return s
    else:
        thresh = 1 if salience <= 0 else max(1, salience * n)
        for s in SIG_TOKENS:
            if toks.count(s) >= thresh:
                return s
    return max(set(toks), key=toks.count)


def branch_photo(block: np.ndarray) -> str:
    """Block -> photo token (majority)."""
    pxs = block.reshape(-1, block.shape[-1])
    toks = [photo_token(px[0], px[1], px[2], px[3]) for px in pxs]
    return max(set(toks), key=toks.count)


def luma_block(block: np.ndarray) -> str:
    subl = block[..., 3] > 0
    lum = block[subl][..., :3].mean() if subl.any() else 0.0
    return WRAMPS[min(9, int(lum * 10 / 256))]


def texture_block(block: np.ndarray) -> str:
    """Local luminance std = surface quality. Flat = smooth, high = detail-or-edge."""
    subl = block[..., 3] > 0
    if not subl.any():
        return " "
    lum = block[subl][..., :3].astype(float).mean(axis=1)
    std = float(lum.std())
    if std < 4:  return "~"   # flat: sky, still water, walls
    if std < 10: return "-"   # smooth
    if std < 22: return "="   # light texture
    if std < 45: return "*"   # textured
    return "#"                # dense detail / foliage / edge


def structure_block(block: np.ndarray) -> str:
    """Structure taxonomy (man-made fix #2, P4 precursor).

    ' ' empty · 'f' flat (per-channel std<2.5) · 'd' dither (negative lag-1
    autocorrelation = 2x2 checker periodicity) · 'e' edge (std>45) ·
    'g' gradient (very high positive lag-1 autocorrelation) · 'n' noise.
    Sierra-forensics law: backgrounds dither, cels are flat islands.
    """
    subl = block[..., 3] > 0
    if not subl.any():
        return " "
    lum = block[subl][..., :3].astype(float).mean(axis=1)
    std = float(lum.std())
    if std < 2.5:
        return "f"
    if lum.size >= 16:
        ac = float(np.corrcoef(lum[:-1], lum[1:])[0, 1])
        if not np.isnan(ac) and ac < -0.15 and std >= 3.0:
            return "d"
    if std > 45.0:
        return "e"
    if lum.size >= 16:
        ac = float(np.corrcoef(lum[:-1], lum[1:])[0, 1])
        if not np.isnan(ac) and ac > 0.9:
            return "g"
    return "n"


def detect_integer_scale(width: int, base: int = 320) -> int:
    """F4: nearest integer capture scale for width (Godot captures are 3x)."""
    return max(1, round(width / base))


def downscale_native(a: np.ndarray, scale: int) -> np.ndarray:
    """Nearest-lattice downsample by an integer factor — no interpolation,
    so native pixel identity is preserved (P0.4 native-scale discipline).
    Caller must verify divisibility before calling."""
    h, w = a.shape[:2]
    nh, nw = h // scale, w // scale
    if scale == 1 or nh == 0 or nw == 0:
        return a
    return a[::scale, ::scale][:nh, :nw]