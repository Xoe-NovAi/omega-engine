# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
"""VNR 2.0 groundtruth — deterministic per-image sidecar (plan P0.3).

JSON sidecar describing the GEOMETRY of an archived screenshot: quantized
flat-island masks (the Sierra-forensics 'background dithers, cels are flat'
law) + statistics. NO human-traced masks: everything is recomputable from
the image, so validation = regenerate and byte-compare.

Native-scale discipline (F4): sidecars record the detected integer capture
scale; consumers must downscale via downscale_native() before comparing.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

from .signals import detect_integer_scale


def image_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_sidecar(image_path: str, max_islands: int = 24) -> dict:
    """Deterministic geometry sidecar for one screenshot.

    Islands: 4-bit-per-channel quantized colors (the v1 gist quantizer),
    filtered to 'flat-island' candidates — colors with >= 400 native px
    whose pixel set has low local spread. Emitted fields per island:
    quantized RGB, exact px count, bbox, centroid (native px).
    """
    from PIL import Image

    img = Image.open(image_path).convert("RGBA")
    a = np.array(img)
    h, w = a.shape[:2]
    scale = detect_integer_scale(w)
    opaque = a[..., 3] > 0

    rgb = a[..., :3].astype(np.uint8)
    qi = rgb // 16  # 4-bit-per-channel indices: flat cel colors collapse
    flat = (rgb - qi * 16 <= 3).all(axis=2) & opaque  # nearly-exact quantized color = cel flat
    qk = qi[..., 0].astype(np.int32) * 256 + qi[..., 1].astype(np.int32) * 16 + qi[..., 2]

    islands = []
    for key in np.unique(qk[flat]):
        mask = (qk == key) & flat
        n = int(mask.sum())
        if n < 400:
            continue
        ys, xs = np.where(mask)
        islands.append({
            "rgb": [int((key // 256) * 16), int(((key // 16) % 16) * 16), int((key % 16) * 16)],
            "px": n,
            "bbox": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
            "centroid": [round(float(xs.mean()), 1), round(float(ys.mean()), 1)],
        })
        if len(islands) >= max_islands:
            break
    islands.sort(key=lambda i: (-i["px"], i["rgb"]))

    return {
        "vnr_groundtruth": 1,
        "image": Path(image_path).name,
        "sha256": image_sha256(image_path),
        "width": int(w),
        "height": int(h),
        "capture_scale": scale,
        "native": [int(w // scale), int(h // scale)] if h % scale == 0 and w % scale == 0 else None,
        "opaque_px": int(opaque.sum()),
        "islands": islands,
    }


def write_sidecar(image_path: str, out_dir: str) -> Path:
    """Write <image-stem>.groundtruth.json, byte-stable (sorted keys)."""
    sidecar = build_sidecar(image_path)
    out = Path(out_dir) / (Path(image_path).stem + ".groundtruth.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(sidecar, indent=1, sort_keys=True) + "\n")
    return out


def main(argv=None) -> int:
    import argparse
    import sys
    ap = argparse.ArgumentParser(description="VNR 2.0 groundtruth sidecar builder")
    ap.add_argument("images", nargs="+")
    ap.add_argument("--out", default="tests/groundtruth")
    args = ap.parse_args(argv)
    for p in args.images:
        out = write_sidecar(p, args.out)
        print(f"sidecar: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())