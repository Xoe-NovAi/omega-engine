# LFM Thread-Curve Fill — threads 2/3/5/10 (2026-10-13)

Closes `BENCHMARK_STUDY_20260926.md` item 3 ("LFM only swept at 4/6/8/12;
no 2/3/5/10 data"). Raw: `docs/research/bench-data/lfm25_512_curve_fill.json`.

## Full ranked curve (zRAM-ON, 512 fixed tokens, n=3)

| Threads | t/s ± 95% CI | CV% | Status |
|---|---|---|---|
| 12 | 20.63 ± 0.04 | 0.2 | zram_on series |
| 8 | 20.54 ± 0.00 | 0.0 | zram_on series |
| 6 | 20.49 ± 0.20 | 0.9 | zram_on series |
| 10 | 19.75 ± 0.05 | 0.2 | curve_fill (new) |
| 4 | 19.44 ± 0.29 | 1.3 | zram_on series |
| 5 | 19.32 ± 0.13 | 0.6 | curve_fill (new) |
| 3 | 17.62 ± 0.11 | 0.6 | curve_fill (new) |
| 2 | 16.44 / 15.79 / 14.49 | 6.4 | **EXCLUDED (CV > 6%)** |

All gates passed (`-t` verified 4/4 on the new configs).

## Reads

1. **Plateau 6–12, cliff below 4.** t6/t8/t12 sit within 0.14 t/s of each
   other; t10 dips slightly (19.75, real: exceeds combined CI vs t5).
   t5 ≈ t4 (~19.3–19.4). t3 drops to 17.6 (−14% vs t12). t2 is unstable
   (6.4% CV, downward drift across reps 16.44 → 14.49).
2. **6-thread recommendation stands** — the plateau means 6 threads buys
   full throughput with least CPU contention for the embed sidecar.
3. **t2 instability is itself a finding:** at 2 threads the run is not
   repeatable (thermal/power allocation hunting). Do not quote t2 numbers.
4. Combined with the zRAM verdict (production ≈ clean-lab), the LFM
   operating picture is now: **20–21 t/s plateau at 6–12 threads,
   ~19.3 at 4–5 and 10, ~17.6 at 3, unstable at 2.**
