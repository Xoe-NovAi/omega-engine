# VNR 2.0 — full package (Node 0 → Node 1)

**Verified before dispatch:** `test_vnr2.py` 28/28 PASS and `parity_v1.py`
ALL BYTE-IDENTICAL, both executed **from this staged copy** in isolation.

## Layout
- `scripts/vnr/`     — the 7-module package (854 lines). numpy + Pillow only.
- `scripts/vnr_render.py` — frozen v1.0.2, needed by the parity harness.
- `tests/vnr/`       — test_vnr2.py (28 assertions) + parity_v1.py.
- `tests/baseline/`  — v1 golden text fixtures for the parity harness.
- `assets/`          — fixture IMAGES the tests load. Required; the suite fails
                       without them.
- `vnr-study-pack/`  — the six design documents already ingested on Node 1.

## Run
```bash
python3 -m venv .venv && .venv/bin/pip install numpy pillow
.venv/bin/python tests/vnr/test_vnr2.py     # expect: VNR2 TESTS: ALL PASS
.venv/bin/python tests/vnr/parity_v1.py     # expect: PARITY: ALL BYTE-IDENTICAL
```

## Verify integrity
```bash
sha256sum -c MANIFEST.sha256
```

## Do not
Do not reconstruct modules from the markdown study pack. `02-signals.md` and
`03-change.md` embed source for 2 of 7 modules; the other 5, plus the tests and
fixtures, exist only here. A partial reconstruction would pass your tests and
diverge from ours — the worst outcome, because it would look validated.
