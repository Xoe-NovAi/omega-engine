# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
"""VNR 2.0 CLI — thin argument parser over vnr.signals/modes/locate/differential.

Flag-compatible with v1.0.2 vnr_render.py. New in v2: --mode structure,
--salience, and the package architecture (P0.1). See kb/VNR_VISION.md.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

from . import differential, locate, modes, signals, track


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("image", nargs="?", default=None)
    ap.add_argument("--mode", default="map",
                    choices=["map", "detail", "luma", "overlay", "texture", "structure"])
    ap.add_argument("--block", type=int, default=0)
    ap.add_argument("--cols", type=int, default=0, help="auto block from target columns")
    ap.add_argument("--world", type=int, nargs=2, default=None, help="rescale to W,H game coords")
    ap.add_argument("--overlay", default=None, help="reference PNG to cross-check (block any)")
    ap.add_argument("--find", default=None, help="r0,r1,g0,g1,b0,b1 -> bbox + count")
    ap.add_argument("--crop", type=int, nargs=4, default=None)
    ap.add_argument("--diff", default=None, help="second image -> change map (MOTION)")
    ap.add_argument("--abdiff", default=None, help="second image -> A/B footprint + HEAD verdict (P2 oracle)")
    ap.add_argument("--diff-thresh", type=float, default=20.0, help="big-change threshold")
    ap.add_argument("--track", default=None,
                    help="dir of shot_*.png -> trajectory + path map (LEGACY F3)")
    ap.add_argument("--class", dest="cset", default="game", choices=["game", "photo"],
                    help="game tokens (default) or perceptual photo tokens")
    ap.add_argument("--salience", type=float, default=signals.DEFAULT_SALIENCE,
                    help="min block fraction for a priority game token (v2, F1 fix)")
    ap.add_argument("--legacy-warm", action="store_true",
                    help=argparse.SUPPRESS)  # parity: disable R-split exact v1 warm
    ap.add_argument("--gist", action="store_true", help="compact named-region + histogram summary")
    ap.add_argument("--hist", action="store_true", help="perceptual color histogram")
    ap.add_argument("--version", action="version", version=f"VNR {__import__('scripts.vnr', fromlist=['__version__']).__version__}")
    return ap


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.legacy_warm:
        signals.LEGACY_WARM = True

    if args.track:
        room_pic = Path(__file__).resolve().parents[2] / "assets" / "rooms" / "room001_crispins_cottage.png"
        version = os.path.basename(args.image).split("_")[1] if args.image else ""
        result = track.track_shots(args.track, str(room_pic), version)
        print(result["legacy_warning"])
        for line in result["trajectory"]:
            print(line)
        print("\nPATH MAP (P=magenta path/dots, ~=water, #=roof, W=trees):")
        for line in result["path_map"]:
            print(line)
        return 0

    if args.image is None:
        parser.error("image required (or use --track DIR)")

    a = modes.load(args.image)
    if args.world:
        a = modes.to_world(a, tuple(args.world))
        print(f"// rescaled to world {args.world}")
    if args.find:
        bb = locate.find_bbox(a, [int(x) for x in args.find.split(",")])
        print("FIND", args.find, "->", bb)
        return 0
    if args.diff:
        b = modes.load(args.diff)
        if a.shape[:2] != b.shape[:2]:
            b = modes.to_world(b, (a.shape[1], a.shape[0]))
        h, w = a.shape[:2]
        blk = args.block or max(1, round(w / 64))
        rows, nch, tot, bbox = differential.diff_maps(a, b, blk, args.diff_thresh)
        print(f"DIFF vs {args.diff}  block={blk} thresh={args.diff_thresh}")
        print(f"  changed: {nch}/{tot} blocks ({nch/tot*100:.1f}%)  bbox={bbox}")
        print("  legend: . unchanged  + small  # BIG CHANGE")
        for i, row in enumerate(rows):
            print(f"y{i*blk:3d} {row}")
        return 0
    if args.abdiff:
        # A/B paired-frame oracle: footprint + HEAD verdict (P2, D-025).
        # State-aware path: read the capture sidecar for the expected head band.
        b = modes.load(args.abdiff)
        if a.shape[:2] != b.shape[:2]:
            b = modes.to_world(b, (a.shape[1], a.shape[0]))
        mask, footprint, bbox, nch, ntot = differential.abdiff(a, b)
        if footprint is None:
            print("ABDIFF -> SPRITE_ABSENT (no footprint above noise floor)")
            return 0
        # Look for a matching state sidecar (ab_state_<tag>.json) next to frame A.
        head_region = None
        sidecar_dir = Path(args.image).parent
        for cand in sidecar_dir.glob("ab_state_*.json"):
            try:
                sc = json.loads(cand.read_text())
                if sc.get("capture", {}).get("file_a") == Path(args.image).name:
                    head_region = sc.get("head_region")
                    break
            except Exception:
                pass
        if head_region is not None:
            v = differential.verdict(footprint, bbox, head_region=head_region)
            print(f"ABDIFF vs {args.abdiff}  changed_pixels={nch}/{ntot}  bbox={bbox}")
            print(f"  head_region (sidecar): {head_region}")
            print(f"  VERDICT: {v}  [state-aware]")
            # DIAGNOSTIC 5b: per-row profile in head region
            profile = differential.head_row_profile(footprint, head_region)
            if profile:
                print(f"  HEAD ROW PROFILE (top->bottom, {len(profile)} rows):")
                for i, count in enumerate(profile):
                    bar = "#" * min(count // 2, 40)
                    print(f"    row {i:2d}: {count:4d} {bar}")
        else:
            # Heuristic fallback: expected_height = 30 native rows * 9x capture.
            v = differential.verdict(footprint, bbox, expected_height=270)
            print(f"ABDIFF vs {args.abdiff}  changed_pixels={nch}/{ntot}  bbox={bbox}")
            print(f"  VERDICT: {v}  [heuristic — no sidecar found]")
        return 0
    if args.crop:
        x, y, w, h = args.crop
        a = a[y:y+h, x:x+w]
        print(f"// cropped x{x} y{y} {w}x{h} -> now {a.shape[:2]}")

    if args.gist:
        print(modes.gist(a))
        return 0
    if args.hist:
        print(modes.hist(a))
        return 0

    if args.overlay:
        ref = np.array(Image.open(args.overlay).convert("L"))
        ref = modes.to_world(ref, (a.shape[1], a.shape[0])) if args.world else ref
        block = args.block or 4
        print("overlay legend: ~=classifier-water 3=ref-water B=both .=other")
        for y in range(0, a.shape[0], block):
            line = []
            for x in range(0, a.shape[1], block):
                cls = signals.branch(a[y:y+block, x:x+block], args.salience)
                refany = bool((ref[y:y+block, x:x+block] == 3).any())
                ch = "~" if cls == "~" else "."
                if refany and cls == "~":
                    ch = "B"
                elif refany:
                    ch = "3"
                line.append(ch)
            print(f"y{y:3d} " + "".join(line))
        return 0

    if args.cols:
        args.block = max(1, round(a.shape[1] / args.cols))
    block = args.block or (8 if args.mode == "map" else 1)
    for line in modes.render_rows(a, args.mode, block, args.cset, args.salience):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())