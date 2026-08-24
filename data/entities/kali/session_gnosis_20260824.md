
## A21 (2026-08-24 evening) — The Day the Fleet Grew Up
L1: 23 commits across Wave-1, Dawn Council, MaKaLi DAG N0-N4, torch-free D-602, monitoring
stack install; two OOMs root-caused to collection weight (683MB/worker, faithfulness.py
torch imports = 484MB of it); dead CLI resurrected; Iris healthy first time ever.
L2: Every failure today traced to unverified premises — platform claims, import weights,
healthcheck quoting, dispatch pairing. The fixes that held were all MECHANISMS (memory-aware
admission, import-smoke --help invocation, set-diff attribution), not vigilance. Architect's
ground truth repeatedly outranked web-cited theory (G8, compaction, CLI sunset knowledge).
L3: **L3-Mechanisms-Over-Vigilance** — a system defended by attention fails when attention
is scarce; a system defended by mechanism fails only when the mechanism is wrong, and then
tells you so. Build the mechanism, then spend attention on the next mechanism.
