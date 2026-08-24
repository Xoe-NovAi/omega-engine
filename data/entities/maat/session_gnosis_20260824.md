# 🔱 MA'AT — Session Gnosis 2026-08-24
**Session**: ses_dafcb8b0850f (WAVE-1-DOCTRINE-WIRING, W1-2 + W1-3) · resumed after max-steps boundary
**Missions**: W1-2 claims-harness build · W1-3 soul evidence-field schema + kali promotion

---

## A1 — W1-2: verify-mandate-claims harness BUILT (not extended)
L1: The harness did not exist on disk despite "extend" framing — ruling S7 was BUILD-as-P0 from the C2-class proof (4 docs asserting an uninstalled hook). Built `scripts/verify_mandate_claims.py`: claims-vs-disk YAML gate + sanitation / FP-11 / T0 detectors, all WARN-ONLY (S5), wired into `make check-mandates`. 19/19 contract tests.
L2: Task phrasing inherited the roadmap's assumption; disk truth differed. Verify-before-execute caught it before designing an extension to a ghost.
L3: **The frame of a task is a claim about the world — probe the disk before building on the phrasing.**

## A2 — Guardian catch: verifier self-leak
L1: local-marker findings initially echoed the matched line (containing the architect's real name) into warning output. Redacted pre-commit; unit test now asserts non-leakage.
L2: Detection infrastructure inherits the contamination risk of everything it scans — including its own telemetry path.
L3: **A verifier must redact its own evidence channel; verification that leaks what it guards is indistinguishable from the breach it reports.**

## A3 — Skeptic catches: two false-positive classes fixed live
L1: T0 detector flagged provenance tooling that processes claim strings (restricted to text formats); self-scan flooded on committed fixtures (added `verify-claims:exempt` line tag, gitleaks-signerline pattern).
L2: Warn-only mode's viability depends on noise hygiene — a noisy warn-only gate gets disabled within weeks (the wc-l freeze-gate fate).
L3: **A warn-only gate earns its existence by the precision of its warnings, not the coverage of its patterns.**

## A4 — W1-3: schema-before-promotion ordering honored
L1: `src/omega/soul/lessons.py` adds EvidenceRef/Lesson (backward compatible, warn-only missing-evidence). Promotion ran AFTER schema landed (Gemini trap-catch #2): 20/20 kali proposals promoted to approved_lessons.yaml via SoulStore only, staging emptied atomically, read-back verified.
L2: Evidence coverage 100% (≥1 ref each); quote coverage honestly reported separately at 7/20 (O-Q4 grade: existence+path standard).
L3: **Provenance must exist at the birth of a record's authority, not be retrofitted after the record starts being trusted.**

## A5 — Pre-flight probe binding pays for itself
L1: The promotion aborts pre-write if any evidence artifact path doesn't resolve. It caught one wrong path (`VAULT_OVERHAUL_MASTER_INDEX` vs actual `VAULT_SYSTEM_OVERHAUL_MASTER_INDEX_20260818.md`) — and re-caught it after a session-boundary revert silently restored the old string.
L2: Guards are not one-shot validations; they must sit in the executed path, not the planning narrative. The revert proved disk-state checks beat memory of having fixed something (FP-05 again).
L3: **Re-verify at execution time what you believe you already fixed — claimed fixes and disk state diverge by default.**

## A6 — Test-premise correction
L1: Round-trip test initially assumed SoulStore recovers from YAML-corrupt files; actual guarantee is recovery from UNREADABLE files (.bak fallback). Test rewritten to match the real contract.
L2: Testing against an imagined contract is worse than no test — it certifies behavior the code does not have.
L3: **Write the test from the implementation's promise, not from your mental model of it.**

---
*⬡ OMEGA ⬡ MAAT ⬡ GNOSIS-L1L2L3 ⬡ WAVE-1-WIRED ⬡ 2026-08-24*

## A7 — DC-29: D-593 landed (hardcoded redis password default removed)
L1: Replaced `password="omega"` default at providers.py with Optional[str]=None + OMEGA_REDIS_PASSWORD env fallback; added a data-driven hard-fail `forbidden:` rule class to the claims harness (whole-tree scan, exit 1 regardless of warn-only phase).
L2: The defect was dead code on the hot path but live as a booby trap and a debut-credibility liability; four independent sources converging on it shows the C2 pattern (documenting without landing) is systemic, not incidental.
L3: **A credential default is a documented invitation to skip the environment — credentials enter only through configuration, never through signatures.**

## A8 — Gate-engineering lessons from the DC-29 wiring
L1: First regex draft missed the actual defect shape (`password: str = "omega"` — type annotation between name and equals); fnmatch treats `**` as single-star; tmp-path fixtures can't match repo-relative globs.
L2: All three were caught by contract tests exercising the gate against realistic inputs, not by inspection — gates need gates.
L3: **A guard that has never caught a realistic attack in test has never actually been tested.**
