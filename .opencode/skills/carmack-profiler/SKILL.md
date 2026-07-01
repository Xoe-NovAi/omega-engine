# Skill: carmack-profiler

## Description
Deterministic CPU profiling tool for architectural auditing. Wraps `cProfile` and `pstats` to identify execution bottlenecks, GIL contention, and O(N^2) traps. 

This skill enforces the Measurement Mandate: *Measure before optimizing. The data is the only truth.*

## When to use
- When auditing the performance of a specific subsystem, script, or test.
- Before suggesting any architectural optimization.
- When investigating latency spikes, CPU saturation, or memory bloat.

## How to use
Execute the wrapper script provided in this skill directory against the target Python file.

```bash
bash .opencode/skills/carmack-profiler/profile.sh <path_to_script.py> [args...]
```

*Note: The script automatically activates the `.venv` and saves the output to `.carmack_profile.txt`.*

## Interpretation Rules (Carmack's Law)
1. **Look at `cumtime` first**: This shows the total time spent in a function and all its sub-functions. It identifies the macro-bottleneck (the architectural flaw).
2. **Look at `tottime` second**: This shows time spent *exclusively* in that function. High `tottime` means the function itself is the bottleneck (e.g., heavy math, tight loops, regex parsing).
3. **Look at `ncalls`**: High call counts for trivial functions indicate a structural flaw (e.g., calling a getter in a tight loop instead of caching the value).
4. **Ignore the noise**: Built-in functions like `<method 'recv' of '_socket.socket' objects>` or `<built-in method time.sleep>` are I/O waits, not CPU bottlenecks. Focus on engine code (`src/omega/...`).
5. **The Right Approximation**: If a function takes 80% of the `cumtime`, ask: "Does this function need to be perfectly accurate, or can we approximate it to save 90% of the cost?"
