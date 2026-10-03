# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
"""VNR 2.0 P1 byte-parity harness: v2 package (legacy mode) vs v1.0.2 script.

v2 --salience -1 --legacy-warm = EXACT v1.0.2 semantics (v1 SIG set, fire on
>=1 px, no R-split). Therefore EVERY game-token render (map/luma/texture)
must be BYTE-IDENTICAL to scripts/vnr_render.py on the same image. Photo
renders are not parity-tested ('N' neutral token is an intentional v2
addition; see docs/VNR2_REFACTOR_PLAN_20260901.md P0.3).

Run: python3 tests/vnr/parity_v1.py            (1 shot, map+luma)
     python3 tests/vnr/parity_v1.py full       (2 shots, map+luma+texture)
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

V1 = REPO / "scripts" / "vnr_render.py"
SHOTS = [
    REPO / "assets" / "screenshots" / "archive" / "shot_0.0.2_x01_y06_2026-09-01T042105.png",
    REPO / "assets" / "screenshots" / "archive" / "shot_0.0.2_x09_y07_2026-09-01T042053.png",
]
MODES = {
    "map": ["--mode", "map", "--block", "12"],
    "luma": ["--mode", "luma", "--block", "12"],
    "texture": ["--mode", "texture", "--block", "12"],
}


def run(cmd: list[str]) -> str:
    r = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{cmd[:3]}... rc={r.returncode}: {r.stderr[-300:]}")
    return r.stdout


def main() -> int:
    full = len(sys.argv) > 1 and sys.argv[1] == "full"
    shots = SHOTS if full else SHOTS[:1]
    use_modes = MODES if full else {k: MODES[k] for k in ("map", "luma")}
    failures = []
    for shot in shots:
        if not shot.exists():
            print(f"SKIP (missing): {shot.name}")
            continue
        for mname, margs in use_modes.items():
            out1 = run([sys.executable, str(V1), str(shot)] + margs)
            out2 = run([sys.executable, "-m", "scripts.vnr.cli", str(shot),
                        "--salience", "-1", "--legacy-warm"] + margs)
            ok = out1 == out2
            print(f"  {'PASS' if ok else 'FAIL'}  {shot.name} {mname}"
                  + ("  [byte-identical]" if ok else ""))
            if not ok:
                failures.append(f"{shot.name}:{mname}")
                l1s, l2s = out1.splitlines(), out2.splitlines()
                for i, (l1, l2) in enumerate(zip(l1s, l2s)):
                    if l1 != l2:
                        print(f"    first diff line {i}:")
                        print(f"      v1: {l1[:120]}")
                        print(f"      v2: {l2[:120]}")
                        break
                else:
                    print(f"    line counts: v1={len(l1s)} v2={len(l2s)}")
    print()
    if failures:
        print(f"PARITY: {len(failures)} FAILED: {failures}")
        return 1
    print("PARITY: ALL BYTE-IDENTICAL")
    return 0


if __name__ == "__main__":
    sys.exit(main())