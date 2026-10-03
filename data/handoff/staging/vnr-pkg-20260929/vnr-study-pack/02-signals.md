<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 02 — Signal Taxonomies

Block the frame into N×N cells, classify each cell with one character, emit a
text grid. The grid is the interface: everything downstream reads characters,
not pixels.

## Photo tokens (`--class photo`)

The general palette. Use these on real rendered frames.

| Token | Meaning | Test |
|---|---|---|
| `N` | true neutral: white/gray achromatic surfaces | sat < 12 and lum ≥ 128 |
| `.` | near-white | lum > 238 and sat < 36 |
| `K` | black | lum < 35 |
| `l` / `M` | light / mid gray | sat < 34, above / below lum 118 |
| `R` | red-dominant | r ≥ g, r ≥ b |
| `O` / `Y` | orange / yellow | r-dominant with g ≥ b + 42 (r < 188 → O) |
| `P` | pink-magenta | r-dominant with b ≥ g + 42 |
| `G` / `D` | green / dark green | g-dominant (g ≥ 88 → G) |
| `T` | teal | g ≥ r + 22 and b < g + 40 |
| `B` | blue | fallthrough |

Blocks vote by **majority** (`branch_photo`).

## Structure tokens (`--mode structure`)

The strongest flat-vs-rendered discriminator. Classification is by luminance
statistics inside the block, not by colour at all.

| Token | Meaning | Test |
|---|---|---|
| ` ` | empty | no opaque pixels |
| `f` | **flat** | per-channel std < 2.5 |
| `d` | **dither** | lag-1 autocorrelation < −0.15 and std ≥ 3.0 (checker periodicity) |
| `e` | **edge** | std > 45.0 |
| `g` | **gradient** | lag-1 autocorrelation > 0.9 |
| `n` | noise | everything else |

UI screens, menus, loaders, and letterboxed frames are dominated by `f`.
Rendered 3D scenes are dense with `e` and `n`. Count tokens; do not eyeball.

## Texture tokens (`--mode texture`)

Local luminance std as surface quality: `~` flat (std<4), `-` smooth (<10),
`=` light texture (<22), `*` textured (<45), `#` dense detail. Same 10-step
ramp string as `--mode luma` (`WRAMPS = " .:-=+*#%@"`).

## Salience gate

A priority token fires for a block only when it holds at least `salience`
fraction of the block (default **0.12**). Without the gate, a single stray
pixel flips a 64-pixel block — the noisiest failure mode in the system.
`salience = 0` fires on ≥1 px; this is the v1 counting behaviour.

## Grid construction

`modes.grid_rows(a, mode, block, cset, salience)` walks the frame in block
steps and emits one string per row. `modes.render_rows(...)` prefixes each row
with its y-coordinate (`y{yy:3d} {row}`). `--world W H` rescales first (BOX
resampling, which averages rather than aliasing). All modes return data; only
the CLI prints.

## Full source — `signals.py`

```python
WRAMPS = list(" .:-=+*#%@")   # luminance ramp (10 steps)
SIG_TOKENS = "~W#xKR"          # game priority tokens (any-signal family, v2)
DEFAULT_SALIENCE = 0.12        # min block fraction for a priority token to fire


def game_token(r: int, g: int, b: int, a: int = 255) -> str:
    """Domain palette for the project VNR was built in. Prefer photo_token
    for general frames; this exists to show the saturation-split pattern."""
    r, g, b, a = int(r), int(g), int(b), int(a)
    if a == 0:
        return " "
    lum = (r + g + b) / 3.0
    if b >= 120 and b >= r + 25 and b >= g + 15:
        return "~"
    if b >= r + 10 and b >= g + 5 and lum < 120:
        return "x"
    if g >= r + 8 and g >= b + 8:
        return "W"
    if r >= b + 16 and r >= g + 14:
        sat = max(r, g, b) - min(r, g, b)
        return "R" if sat >= 140 else "#"   # salient vs muted warm split
    if lum > 175:
        return "."
    if lum < 42:
        return "K"
    return "-"


def photo_token(r: int, g: int, b: int, a: int = 255) -> str:
    """Perceptual token. 'N' = true neutral (sat<12, lum>=128): separates
    achromatic manufactured surfaces from tinted backgrounds."""
    r, g, b, a = int(r), int(g), int(b), int(a)
    if a == 0:
        return " "
    r, g, b = int(r), int(g), int(b)
    lum = (r + g + b) / 3.0
    mx = max(r, g, b); mn = min(r, g, b); sat = mx - mn
    if sat < 12 and lum >= 128:
        return "N"
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


def branch(block, salience: float = DEFAULT_SALIENCE) -> str:
    """Block -> game token. A priority token fires only when it holds >=
    salience of the block. Otherwise the majority token wins."""
    pxs = block.reshape(-1, block.shape[-1])
    toks = [game_token(px[0], px[1], px[2], px[3]) for px in pxs]
    n = len(toks)
    thresh = 1 if salience <= 0 else max(1, salience * n)
    for s in SIG_TOKENS:
        if toks.count(s) >= thresh:
            return s
    return max(set(toks), key=toks.count)


def branch_photo(block) -> str:
    """Block -> photo token (majority)."""
    pxs = block.reshape(-1, block.shape[-1])
    toks = [photo_token(px[0], px[1], px[2], px[3]) for px in pxs]
    return max(set(toks), key=toks.count)


def luma_block(block) -> str:
    subl = block[..., 3] > 0
    lum = block[subl][..., :3].mean() if subl.any() else 0.0
    return WRAMPS[min(9, int(lum * 10 / 256))]


def texture_block(block) -> str:
    """Local luminance std = surface quality."""
    subl = block[..., 3] > 0
    if not subl.any():
        return " "
    lum = block[subl][..., :3].astype(float).mean(axis=1)
    std = float(lum.std())
    if std < 4:  return "~"
    if std < 10: return "-"
    if std < 22: return "="
    if std < 45: return "*"
    return "#"


def structure_block(block) -> str:
    """Structure taxonomy. Backgrounds dither, flat fills are islands,
    edges and noise mark rendered detail."""
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
```

Note the saturation-split pattern inside `game_token`: two surfaces sharing a
hue family are separated by chroma magnitude (`sat >= 140` → salient `R`, else
muted `#`). When a single token conflates two things you need apart, split by
saturation before inventing new machinery.
