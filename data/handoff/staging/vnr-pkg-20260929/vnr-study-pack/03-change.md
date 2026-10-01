<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 03 — Change First: Diffs, Oracles, Verdicts

Change is the first signal in the law and the cheapest question worth asking.
Two frames and a threshold answer "is anything happening," "how much," and
"where" before any model is involved.

## `diff_maps` — the change map

`differential.diff_maps(a, b, block, thresh)` walks both frames in block steps
and emits `.` unchanged, `+` mild (`d > thresh*0.25`), `#` big (`d > thresh`),
where `d` is mean absolute RGB difference per block. Returns
`(rows, n_changed, n_total, bbox_of_big_changes)`.

Real output:

```
DIFF vs ab_B_...png  block=8 thresh=20.0
  changed: 197/81000 blocks (0.2%)  bbox=(1256, 1368, 1376, 1584)
```

Read the **bbox alongside the fraction**. A single scalar cannot separate a
concentrated change (a progress bar: small fraction, short-wide bbox) from a
distributed one (gameplay: larger fraction, tall bbox). A frozen frame reads
~0% with no bbox at all.

## `abdiff` — the A/B oracle

`differential.abdiff(a, b, noise_floor=10.0)`: difference a **paired** pair of
frames that differ only in the thing under test, floor the noise, flood-fill
connected components over changed pixels, keep the largest. Returns
`(mask, footprint, bbox, n_changed, n_total)`; `footprint is None` means
nothing survived the floor.

The method is the point. **Capture a paired frame with one variable toggled
and nothing else changed**, and a vague "looks different" becomes a measured
region. Any harness that can emit frame-with-X and frame-without-X gets a
free, exact mask of X.

Real output:

```
ABDIFF vs ab_B_...png  changed_pixels=11745/5184000  bbox=(1260, 1368, 1385, 1592)
  VERDICT: HEAD_PRESENT  [state-aware]
```

## `verdict` — three values, two paths

`differential.verdict(footprint, bbox, head_region=None, ...)` returns
`PRESENT` / `ABSENT` / `SPRITE_ABSENT` (no surviving component at all).

Two paths, in priority order:

1. **State-aware** — the capture sidecar records where the thing *should* be
   (`head_region`); the verdict checks footprint density (≥ 0.1) inside that
   expected band. Authoritative, because it knows the answer's location.
2. **Heuristic** — no sidecar; compare bbox height against expected height.
   Fallback only.

Generalise the pattern: whenever the capture side knows ground truth (object
position, expected size, HUD layout), write it into a JSON sidecar next to the
frame and let the analyser read it. The sidecar format is `{player, sprite,
viewport, capture, head_region}` — viewport dims, capture version, file names,
and the expected region in final-image coordinates. Cheap to write, and it
turns every heuristic into a measurement.

`head_row_profile(footprint, head_region)` returns per-row pixel counts
top-to-bottom inside the expected band. Zero rows on top with populated rows
below means truncation; a uniform deficit means absence. Read the profile
shape, not just the total.

## Full source — `differential.py`

```python
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
    """Paired-frame differential oracle. Noise-floored pixel mask ->
    largest connected component = footprint. The pair differs ONLY in the
    thing under test, so the footprint IS that thing.
    Returns (mask, footprint, bbox, n_changed, n_total)."""
    h, w = a.shape[:2]
    diff = np.abs(a[:, :, :3].astype(int) - b[:, :, :3].astype(int)).mean(axis=2)
    mask = diff > noise_floor
    n_changed = int(mask.sum())
    n_total = h * w
    if n_changed == 0:
        return mask, None, None, 0, n_total
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
    """Three-valued verdict. State-aware path (expected region from the
    capture sidecar, density >= 0.1) is authoritative; the bbox-height
    heuristic is fallback only."""
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
    bbox_height = y1 - y0 + 1
    ratio = bbox_height / expected_height
    return "HEAD_PRESENT" if ratio >= head_height_ratio else "HEAD_ABSENT"


def head_row_profile(footprint: np.ndarray, head_region: dict) -> list[int]:
    """Per-row pixel counts in the expected band, top to bottom.
    Zero top rows + populated lower rows = truncation."""
    hr_x0 = max(0, int(head_region["x_left"]))
    hr_y0 = max(0, int(head_region["y_top"]))
    hr_x1 = min(footprint.shape[1] - 1, int(head_region["x_right"]))
    hr_y1 = min(footprint.shape[0] - 1, int(head_region["y_bottom"]))
    if hr_x1 < hr_x0 or hr_y1 < hr_y0:
        return []
    return [int(footprint[y, hr_x0:hr_x1 + 1].sum()) for y in range(hr_y0, hr_y1 + 1)]
```
