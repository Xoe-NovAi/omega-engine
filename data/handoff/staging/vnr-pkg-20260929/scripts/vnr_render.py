#!/usr/bin/env python3
"""VNR — Von-Neu-Ryan Renderer: serialize an image to a semantic text matrix.

Turns a screenshot into an annotated ASCII map a TEXT-ONLY agent can read as
structure: category tokens (water/tree/roof/dark/light/path) plus an optional
per-row y-coordinate ruler. Modes:
  map     block-averaged semantic grid        (context / whole frame)
  detail  1 px = 1 char semantic grid          (small images: sprites, crops)
  luma    block luminance ramp                 (shading information)
  overlay cross-reference a mask/reference     (authoritative vs classifier)
  find    bounding-box of a color range        (locate Graham / features)
  crop    render only a sub-rectangle          (zoom discipline)
Resolution-aware: rescales to a 'world' size first so block coords = game coords.
"""
import argparse, sys
from pathlib import Path
import numpy as np
from PIL import Image

# ---------- semantic classifier (tuned on KQ5 room001 palette; generic enough) ----------
def token(r: int, g: int, b: int, a: int = 255) -> str:
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
        return "#"                      # warm roof / wood / rust-red
    if lum > 175:
        return "."                      # light wall / sky / highlight
    if lum < 42:
        return "K"                      # black shadow / interior
    return "-"                          # mid-tone path / ground

WRAMPS = list(" .:-=+*#%@")             # luminance ramp (10 steps)

PHOTO_TOKENS = list(".KYlMPYOGRDTB")  # documented legend in kb/VNR_VISION.md
def photo_token(r: int, g: int, b: int, a: int = 255) -> str:
    r, g, b, a = int(r), int(g), int(b), int(a)   # uint8 wrap corrupts lum (sum overflow)
    # Perceptual tokens for real-life photos (not game art):
    #   . white/snow/lit   K black/shadow    l light gray/fog/concrete
    #   M mid gray/rock    P pink/magenta    Y yellow/gold/sand-lit
    #   O orange/tan/skin  R red/brick/rust  G green/grass/foliage
    #   D dark green/forest  T teal/cyan/water  B sky/blue
    if a == 0:
        return " "
    r, g, b = int(r), int(g), int(b)
    lum = (r + g + b) / 3.0
    mx = max(r, g, b); mn = min(r, g, b); sat = mx - mn
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


def branch_photo(block):
    pxs = block.reshape(-1, block.shape[-1])
    toks = [photo_token(px[0], px[1], px[2], px[3]) for px in pxs]
    return max(set(toks), key=toks.count)


def pname(r: int, g: int, b: int) -> str:
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


CLASS_SET = "game"

def branch(block: np.ndarray) -> str:
    """Block -> token: any-signal priority then majority."""
    pxs = block.reshape(-1, block.shape[-1])
    toks = [token(px[0], px[1], px[2], px[3]) for px in pxs]
    sig = "~W#xK"
    for s in sig:
        if toks.count(s) >= 1:
            return s
    return max(set(toks), key=toks.count)

def luma_block(block: np.ndarray) -> str:
    subl = block[..., 3] > 0
    lum = block[subl][..., :3].mean() if subl.any() else 0.0
    return WRAMPS[min(9, int(lum * 10 / 256))]

def load(path: str):
    img = Image.open(path).convert("RGBA")
    return np.array(img)

def to_world(a: np.ndarray, wandh):
    h, w = a.shape[:2]
    if wandh:
        tw, th = wandh
        if (w, h) != (tw, th):
            # downscale by a lot => average (LANCZOS); nearest would alias to noise
            a = np.array(Image.fromarray(a).resize((tw, th), Image.BOX))
    return a

def grid_rows(a, mode, block):
    h, w = a.shape[:2]
    bs = block
    rows = []
    for y in range(0, h, bs):
        line = []
        for x in range(0, w, bs):
            blk = a[y:y + bs, x:x + bs]
            if mode == "luma":
                ch = luma_block(blk)
            elif mode == "texture":
                ch = texture_block(blk)
            elif CLASS_SET == "photo":
                ch = branch_photo(blk)
            else:
                ch = branch(blk)
            line.append(ch)
        rows.append("".join(line))
    return rows

def render(a, mode, block, xy0=(0, 0), scale_note=""):
    for i, row in enumerate(grid_rows(a, mode, block)):
        y = xy0[1] + i * block
        print(f"y{y:3d} {row}")

def find_bbox(a, rng):
    r0, r1, g0, g1, b0, b1 = rng
    mask = ((a[...,0]>=r0)&(a[...,0]<=r1)&(a[...,1]>=g0)&(a[...,1]<=g1)&(a[...,2]>=b0)&(a[...,2]<=b1))
    ys, xs = np.where(mask)
    if ys.size == 0:
        return None
    return xs.min(), ys.min(), xs.max(), ys.max(), int(mask.sum())

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


def cap_find(a):
    """Saturated red = Graham's cap (216,38,38) family. Returns (cx, cy, count)."""
    mask = (a[..., 0] >= 180) & (a[..., 0] <= 255) & (a[..., 1] <= 90) & (a[..., 2] <= 90)
    ys, xs = np.where(mask)
    if not len(xs):
        return None
    return float(xs.mean()), float(ys.mean()), int(len(xs))


def diff_maps(a, b, block: int, thresh: float):
    """Block-wise change map: . unchanged, + small, # big. Returns bbox of big changes."""
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


def track_shots(dirpath: str, room_pic_path: str, version: str = ""):
    """Scan shot_*.png sorted, find cap-red per shot -> trajectory + path map.
    version: only track shots whose filename carries this version token (the
    seed image's own version) so separate walk campaigns never mix."""
    import glob, os
    from PIL import ImageDraw
    shots = sorted(glob.glob(os.path.join(dirpath, "shot_*.png")))
    if version:
        shots = [p for p in shots if f"_{version}_" in os.path.basename(p)]
    positions = []
    for p in shots:
        a = load(p)
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
    print("TRAJECTORY (world coords, timestamp order):")
    prev = None
    total = 0.0
    for name, x, y in positions:
        if x is None:
            print(f"  {name}: NO CAP FOUND")
            continue
        if prev is not None:
            dist = ((x-prev[0])**2 + (y-prev[1])**2) ** 0.5
            total += dist
            print(f"  {name}: ({x},{y})  step={dist:.1f}px")
        else:
            print(f"  {name}: ({x},{y})  START")
        prev = (x, y)
    print(f"  total path: {total:.1f} world px over {len(pts)} shots")
    arr = np.array(room)
    print("\nPATH MAP (P=magenta path/dots, ~=water, #=roof, W=trees):")
    for i, row in enumerate(grid_rows(arr, "map", 5)):
        print(f"y{i*5:3d} {row}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("image", nargs="?", default=None)
    ap.add_argument("--mode", default="map", choices=["map","detail","luma","overlay","texture"])
    ap.add_argument("--block", type=int, default=0)
    ap.add_argument("--cols", type=int, default=0, help="auto block from target columns")
    ap.add_argument("--world", type=int, nargs=2, default=None, help="rescale to W,H game coords")
    ap.add_argument("--overlay", default=None, help="reference PNG to cross-check (block any)")
    ap.add_argument("--find", default=None, help="r0,r1,g0,g1,b0,b1 -> bbox + count")
    ap.add_argument("--crop", type=int, nargs=4, default=None)
    ap.add_argument("--diff", default=None, help="second image -> change map (MOTION)")
    ap.add_argument("--diff-thresh", type=float, default=20.0, help="big-change threshold")
    ap.add_argument("--track", default=None, help="dir of shot_*.png -> trajectory + path map")
    ap.add_argument("--class", dest="cset", default="game", choices=["game", "photo"],
                    help="game tokens (default) or perceptual photo tokens")
    ap.add_argument("--gist", action="store_true", help="compact named-region + histogram summary")
    ap.add_argument("--hist", action="store_true", help="perceptual color histogram")
    args = ap.parse_args(argv)

    if args.track:
        import os
        room_pic = Path(__file__).resolve().parents[1] / "assets" / "rooms" / "room001_crispins_cottage.png"
        version = os.path.basename(args.image).split("_")[1] if args.image else ""
        track_shots(args.track, str(room_pic), version)
        return

    if args.image is None:
        ap.error("image required (or use --track DIR)")

    a = load(args.image)
    if args.world:
        a = to_world(a, tuple(args.world))
        print(f"// rescaled to world {args.world}")
    if args.find:
        bb = find_bbox(a, [int(x) for x in args.find.split(",")])
        print("FIND", args.find, "->", bb)
        return
    if args.diff:
        b = load(args.diff)
        if a.shape[:2] != b.shape[:2]:
            b = to_world(b, (a.shape[1], a.shape[0]))
        h, w = a.shape[:2]
        blk = args.block or max(1, round(w / 64))
        rows, nch, tot, bbox = diff_maps(a, b, blk, args.diff_thresh)
        print(f"DIFF vs {args.diff}  block={blk} thresh={args.diff_thresh}")
        print(f"  changed: {nch}/{tot} blocks ({nch/tot*100:.1f}%)  bbox={bbox}")
        print("  legend: . unchanged  + small  # BIG CHANGE")
        for i, row in enumerate(rows):
            print(f"y{i*blk:3d} {row}")
        return
    if args.crop:
        x, y, w, h = args.crop
        a = a[y:y+h, x:x+w]
        print(f"// cropped x{x} y{y} {w}x{h} -> now {a.shape[:2]}")
    h, w = a.shape[:2]
    global CLASS_SET
    CLASS_SET = args.cset

    if args.gist:
        _gist(a)
        return
    if args.hist:
        _hist(a)
        return

    if args.overlay:
        ref = np.array(Image.open(args.overlay).convert("L"))
        ref = to_world(ref, (w, h)) if args.world else ref
        rh, rw = ref.shape
        block = args.block or 4
        print("overlay legend: ~=classifier-water 3=ref-water B=both .=other")
        for y in range(0, h, block):
            line = []
            for x in range(0, w, block):
                cls = branch(a[y:y+block, x:x+block])
                refany = bool((ref[y:y+block, x:x+block] == 3).any())
                ch = "~" if cls == "~" else "."
                if refany and cls == "~": ch = "B"
                elif refany: ch = "3"
                line.append(ch)
            print(f"y{y:3d} " + "".join(line))
        return

    if args.cols:
        args.block = max(1, round(w / args.cols))
    block = args.block or (8 if args.mode == "map" else 1)
    mode = args.mode or "map"
    render(a, mode, block)



def _gist(a):
    # coarse named-region layout: 8x4 cells + dominant color list
    h, w = a.shape[:2]
    cell_h, cell_w = max(1, h // 4), max(1, w // 8)
    print(f"GIST {w}x{h}  cells {w//cell_w}x{h//cell_h} (cell {cell_h}x{cell_w})")
    for gy in range(0, h - cell_h + 1, cell_h):
        parts = []
        for gx in range(0, w - cell_w + 1, cell_w):
            blk = a[gy:gy+cell_h, gx:gx+cell_w].reshape(-1, a.shape[-1])
            toks = [photo_token(px[0], px[1], px[2], px[3]) for px in blk]
            dom = max(set(toks), key=toks.count)
            fr = toks.count(dom) / max(1, len(toks))
            parts.append(f"{dom}{fr:.0%}")
        print(f"  y{gy:3d} | " + " | ".join(parts))
    # dominant perceptual colors
    a2 = a[::max(1, a.shape[0]//120), ::max(1, a.shape[1]//200)]
    q = (a2.reshape(-1, a2.shape[-1]) // 24) * 24
    from collections import Counter
    cnt = Counter(map(lambda p: (int(p[0]), int(p[1]), int(p[2])), q[:, :3]))
    tot = sum(cnt.values())
    print("  dominant colors:")
    for col, n in cnt.most_common(12):
        print(f"    {pname(*col):16s} ({col[0]:3d},{col[1]:3d},{col[2]:3d}) {n/tot*100:4.1f}%")


def _hist(a):
    q = (a.reshape(-1, a.shape[-1]) // 24) * 24
    from collections import Counter
    cnt = Counter(map(lambda p: (int(p[0]), int(p[1]), int(p[2])) if p[3] > 0 else None, q))
    cnt.pop(None, None)
    tot = sum(cnt.values())
    print(f"HIST {tot} opaque px")
    for col, n in cnt.most_common(16):
        print(f"  {pname(*col):16s} ({col[0]:3d},{col[1]:3d},{col[2]:3d}) {n/tot*100:5.1f}%")

if __name__ == "__main__":
    main()
