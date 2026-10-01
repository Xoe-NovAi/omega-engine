# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
"""VNR 2.0 P0.2 regression tests (run: python3 tests/vnr/test_vnr2.py).

Anchors:
- v1 groundtruth: tests/baseline/*.txt (captured 2026-09-02 21:48)
- cards image:    assets/photos/real-world/playing_cards_50pct.png
Baseline source screenshot lives in gitignored assets/screenshots/archive/
(shot_0.0.2_x01_y06_2026-09-01T042105.png).
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

from scripts.vnr import differential, locate, modes, signals  # noqa: E402

BASELINE = REPO / "tests" / "baseline"
CARDS = REPO / "assets" / "photos" / "real-world" / "playing_cards_50pct.png"

failures = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        failures.append(name)


def t_tokens() -> None:
    print("tokens:")
    # F2: cap vs roof split
    check("game cap-red -> R", signals.game_token(216, 38, 38) == "R")
    check("game roof-brown -> #", signals.game_token(135, 79, 39) == "#")
    # v1 game anchors byte-stable
    check("game water -> ~", signals.game_token(40, 120, 200) == "~")
    check("game foliage -> W", signals.game_token(60, 140, 60) == "W")
    # v2 man-made: neutral gate
    check("photo white card -> N", signals.photo_token(220, 224, 222) == "N")
    check("photo tinted white -> l", signals.photo_token(210, 230, 225) == "l")
    check("photo black ink -> K", signals.photo_token(30, 30, 30) == "K")


def t_salience() -> None:
    print("salience (F1):")
    # 4x4 block with ONE salient red pixel: v1 fired R, v2 must not
    blk = np.zeros((4, 4, 4), dtype=np.uint8)
    blk[..., :3] = 100
    blk[..., 3] = 255
    blk[0, 0, :3] = (216, 38, 38)
    check("1/16 red px does not flip block", signals.branch(blk) != "R")
    blk2 = np.zeros((4, 4, 4), dtype=np.uint8)
    blk2[..., :3] = 100
    blk2[..., 3] = 255
    blk2[:2, :2, :3] = (216, 38, 38)  # 4/16 = 25% >= 12%
    check("4/16 red px fires R", signals.branch(blk2) == "R")


def t_structure() -> None:
    print("structure taxonomy:")
    flat = np.full((8, 8, 4), 128, dtype=np.uint8)
    flat[..., 3] = 255
    check("flat -> f", signals.structure_block(flat) == "f")
    dith = np.indices((8, 8)).sum(axis=0) % 2  # 2x2 checker
    dith = (dith * 255).astype(np.uint8)
    da = np.stack([dith] * 3 + [np.full((8, 8), 255, np.uint8)], axis=-1)
    check("checker -> d", signals.structure_block(da) == "d")
    edge = np.full((8, 8, 4), 30, dtype=np.uint8)
    edge[..., 3] = 255
    edge[:, 4:, :3] = 240
    check("hard edge -> e", signals.structure_block(edge) == "e")
    empty = np.zeros((8, 8, 4), dtype=np.uint8)
    check("empty -> ' '", signals.structure_block(empty) == " ")


def t_scale() -> None:
    print("native scale (F4):")
    check("960 -> 3x", signals.detect_integer_scale(960) == 3)
    check("downscale_native shape", signals.downscale_native(np.zeros((600, 960, 4), np.uint8), 3).shape == (200, 320, 4))


def t_locate_diff() -> None:
    print("locate/differential:")
    a = np.zeros((10, 10, 4), dtype=np.uint8)
    a[2:5, 3:7, :3] = (216, 38, 38)
    a[..., 3] = 255
    bb = locate.find_bbox(a, [200, 255, 20, 60, 20, 60])
    check("find_bbox exact", bb == (3, 2, 6, 4, 12), str(bb))
    b = a.copy()
    b[6:9, 1:4, :3] = (40, 120, 200)
    rows, nch, tot, bbox = differential.diff_maps(a, b, 2, 20.0)
    check("diff counts change", nch > 0 and tot == 25, f"{nch}/{tot}")


def t_ab_oracle() -> None:
    print("A/B paired-frame oracle (P2):")
    h, w = 200, 300
    # Synthetic "sprite": a 60x90 block (20x30 native at 3x) with a dense
    # head band (top 45 rows) + body (bottom 45 rows). Background neutral.
    bg = np.full((h, w, 4), 128, dtype=np.uint8)
    bg[..., 3] = 255
    # Frame A: sprite present (head + body)
    a = bg.copy()
    a[30:75, 120:180, :3] = 200   # head band (rows 30-74)
    a[75:120, 120:180, :3] = 80   # body (rows 75-119)
    a[30:120, 120:180, 3] = 255
    # Frame B: sprite absent (background only)
    b = bg.copy()
    mask, footprint, bbox, nch, ntot = differential.abdiff(a, b, noise_floor=10.0)
    check("abdiff finds one component", footprint is not None)
    check("abdiff n_changed > 0", nch > 0, str(nch))
    fx0, fy0, fx1, fy1 = bbox
    check("bbox x covers sprite", fx0 <= 125 and fx1 >= 175, str(bbox))
    check("bbox y covers full sprite", fy0 <= 35 and fy1 >= 115, str(bbox))
    # Heuristic verdict: full-height bbox => HEAD_PRESENT
    v = differential.verdict(footprint, bbox, expected_height=90)
    check("heuristic verdict HEAD_PRESENT", v == "HEAD_PRESENT", v)
    # State-aware verdict: head band = top 45 rows (native 0-14 at 3x).
    # Sprite occupies rows 30-119; head band = rows 30-74.
    hr = {"x_left": 115, "y_top": 25, "x_right": 185, "y_bottom": 74}
    v2 = differential.verdict(footprint, bbox, head_region=hr)
    check("state-aware verdict HEAD_PRESENT", v2 == "HEAD_PRESENT", v2)
    # Headless variant: only body, no head band
    a_hl = bg.copy()
    a_hl[75:120, 120:180, :3] = 80
    a_hl[75:120, 120:180, 3] = 255
    _, fp_hl, bb_hl, _, _ = differential.abdiff(a_hl, b, noise_floor=10.0)
    v_hl = differential.verdict(fp_hl, bb_hl, expected_height=90)
    check("headless heuristic HEAD_ABSENT", v_hl == "HEAD_ABSENT", v_hl)
    # Headless: body at rows 75-119, no overlap with head band 25-74 -> HEAD_ABSENT
    v_hl2 = differential.verdict(fp_hl, bb_hl, head_region=hr)
    check("headless state-aware HEAD_ABSENT", v_hl2 == "HEAD_ABSENT", v_hl2)
    # Sprite-absent variant: both frames identical
    _, fp_none, _, _, _ = differential.abdiff(b, b, noise_floor=10.0)
    check("identical frames -> no footprint", fp_none is None)
    v_none = differential.verdict(fp_none, (0, 0, 0, 0))
    check("identical frames -> SPRITE_ABSENT", v_none == "SPRITE_ABSENT", v_none)
    # Noise floor: tiny diffs ignored
    b_noisy = bg.copy()
    b_noisy[5, 5, :3] = 130  # one pixel changed by 2 (< floor 10)
    _, fp_noise, _, _, _ = differential.abdiff(b, b_noisy, noise_floor=10.0)
    check("sub-noise pixel ignored", fp_noise is None)


def t_groundtruth() -> None:
    print("groundtruth sidecar:")
    from scripts.vnr import groundtruth as gt
    src = REPO / "assets" / "screenshots" / "archive" / "shot_0.0.2_x09_y07_2026-09-01T042053.png"
    if not src.exists():
        print(f"  SKIP  (source absent: {src.name})")
        return
    sc = gt.build_sidecar(str(src))
    # 0.0.2 walk captures are 2880x1800 = 9x the 320x200 world
    check("sidecar scale=9 (2880x1800 captures)", sc["capture_scale"] == 9)
    check("sidecar native 320x200", sc["native"] == [320, 200])
    check("sidecar has islands", len(sc["islands"]) > 0)
    sc2 = gt.build_sidecar(str(src))
    import json as _json
    check("sidecar deterministic", _json.dumps(sc, sort_keys=True) == _json.dumps(sc2, sort_keys=True))


def t_gist_stability() -> None:
    print("gist output format:")
    a = modes.load(str(CARDS))
    g = modes.gist(a)
    check("gist header", g.startswith("GIST 369x243"), g.splitlines()[0])
    check("gist has dominant colors", "dominant colors:" in g)


if __name__ == "__main__":
    t_tokens()
    t_salience()
    t_structure()
    t_scale()
    t_locate_diff()
    t_ab_oracle()
    t_groundtruth()
    t_gist_stability()
    print()
    if failures:
        print(f"VNR2 TESTS: {len(failures)} FAILED: {failures}")
        sys.exit(1)
    print("VNR2 TESTS: ALL PASS")
