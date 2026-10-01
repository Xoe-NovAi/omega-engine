<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# VAULT_REVIEW_delta — Carmack Vault Spec Review → Debut Decision Chain

**Session**: ses_fdef2be4effe4pAaLXCTUx62GO (paging return, 2026-08-21)
**Source work**: Synthesis of `VAULT_SYSTEM_OVERHAUL_SPEC_20260818` (5 parts) + `VAULT_OVERHAUL_REVIEW_ENHANCEMENTS_20260818` (3 parts) + gap research A–J (pyrage wheels, flashtext2, keyring headless, wincred 2560B, systemd ProtectHome, AppArmor dbus, bwrap dbus, CVE-2024-56327, micro supply chain, sanitizer latency).
**Decision chain covered**: D-535 → D-562 → D-565 → D-566 → D-567 → D-568.

---

## 1. Forgotten findings relevant to the decision chain

### FF-1: Headless keyring crash survives Path B (review finding F-3) — Confidence 9/10
Even a "50-line minimal, keyring-only" CredentialProvider crashes on headless Linux if it calls
`keyring.get_password()` unconditionally (`NoKeyringError`; keyring issue #609, official docs).
Deeper research (keybay 2026 headless plan, aws-vault #670/#74): headless vs locked vs
transiently-unavailable CANNOT be auto-detected reliably; silent file-fallback causes split-brain
KEK loss (two stores, silent divergence). Minimal impl MUST: use a deterministic chain
(keyring → `OMEGA_*` env → typed error), NEVER silently create a second KEK store. If a file KEK
is ever added post-debut, write a marker (`kek.source`) and hard-error on dual-store detection.

### FF-2: Typed error is not optional (G-6 / M9) — Confidence 10/10
Bare `KeyError` from credential resolution violates M9 (Error Integrity). Even the minimal Path B
needs `CredentialNotFoundError(OmegaError)` — ~3 lines of cost. This survived every review round;
do not let "minimal" drop it.

### FF-3: Format-pattern redaction is the highest value/LOC item in the spec (G-2)
P0-1 rotated keys, but residual exposure remains (P0-1-RESIDUAL: SECURITY_AUDIT ancestor commit,
gitleaks wiring still in_progress). A ~10-regex layer (`sk-or-v1-`, `AIza…`, `ghp_`, `AKIA`,
`xox[baprs]-`, bearer tokens) redacts UNREGISTERED future leaks across logs/Hivemind/SSE.
It catches keys that were never registered — the exact class P0-1 just suffered. Lead the
post-debut V-1 sprint with this.

### FF-4: Deletion reference sweep must be repo-wide, not src/omega-only — Confidence 10/10
Spec Part 4's deletion plan verified only `rg -n "vault" src/omega/`. D-568 found 13 consumers /
19 sites including 5 OUTSIDE src/omega — empirically confirming the original sweep radius was
wrong. Post-debut deletion checklist must cover scripts/, .opencode/, config/, tests/, docs/
pointers, and any CLI registration tables.

### FF-5: python-age primary validates and simplifies my pyrage research (D-568) — Confidence 8/10
Gap-A research: pyrage has NO musllinux/armv7 wheels; CVE-2024-56327 plugin-execution surface
(attacker-controlled recipient/identity strings); Rust supply-chain class risk. python-age (pure
Python) eliminates all three at once — better than the greenlit pyrage→cryptography chain.
Carry-over guidance unchanged: passphrase-only usage; pin with upper bound; confirm age-python
never parses recipient/identity strings on our path (plugin analog of CVE-2024-56327).

### FF-6: Sanitizer latency budget is a non-issue; regex fallback rebuild was the real risk
flashtext2/aho-corasick at 32 secrets × 12 variants ≈ 384 keywords → <0.2ms per egress call.
The eager `_rebuild_patterns()` regex alternation (~50KB compiled per register()) was the only
real perf defect. If SecretRegistry returns post-debut: lazy-compile or require pyahocorasick
(musllinux wheels confirmed v2.3.0). flashtext2 has NO musllinux wheels (gap-B answer).

---

## 2. Adopted / superseded — what to resurrect for post-debut V-1

### ADOPTED (survived into decisions)
- VaultCore deletion as dead code → D-568 (= spec Component 10; core of my GREENLIGHT verdict).
- Call-time credential resolution → INST-1-fix4 removes `_load_sovereign_secrets()`
  (= my "Carmack Insight": the vault problem was resolution TIMING, not storage; 2,039 LOC
  existed to serve import-time key loading).
- CredentialProvider as replacement shape → D-568.

### SUPERSEDED (scope collapsed ~10x — correctly, per debut discipline)
- pyrage primary → python-age primary (D-568). Better than my greenlit chain (see FF-5).
- Envelope encryption, YAML-editor-bridge, RBAC matrix, 4 sanitizer hooks, systemd/AppArmor
  hardening, sandbox backends → all deferred to post-debut V-1 MVP ticket.
- T1–T30 test matrix → deferred. Salvage the minimal trio for Path B: T16/T17 (headless
  fallback), T24 (typed error isinstance OmegaError), plus a round-trip set/get test.
- My 3 mandatory modifications (lazy regex rebuild; micro commit-hash pin alongside SHA256;
  `loginctl enable-linger` doc for hub unit) → moot under D-565 zero-code-change; resurrect
  only if the corresponding components return.

### RESURRECT for post-debut V-1 sprint (priority order)
1. FF-1 headless-safe chain + split-brain guard (marker file, hard-error on dual KEK store).
2. FF-3 format-pattern redaction layer (~15 LOC, catches unregistered leaks).
3. G-3 audit log (`~/.omega/audit.log`, provider/account/role/backend, never values) — M22
   provenance requires knowing which backend served each credential.
4. G-1 export/import/rekey — without it, KEK loss = total secret loss.
5. F-9 tmpfs temp dir + F-6 micro checksum + commit pin IF the YAML-editor bridge returns.

---

## 3. Flagged important, never executed

- **INST-1-fix4** (`_load_sovereign_secrets()` removal from model_gateway.py) — still `ready`,
  not started; atomic with Fix 2 per blockers section. Until it lands, `.env` dumps to
  `os.environ` at import time — the exact violation the entire vault effort existed to kill.
  This is the single highest-value vault-adjacent fix and it is pure deletion.
- **P0-1d** full secret sweep + cline checkpoint prune — in_progress; FF-3's format layer is the
  systemic backstop if any residual slips through.
- **T16/T17/T24** headless + typed-error tests — never ran (matrix deferred with the spec).
  Reattach to Path B implementation as its acceptance tests.
- **D-562's "50-line" budget vs M9/M22**: nothing in the decision chain contradicts FF-1/FF-2,
  but no ticket currently carries them. Recommend V-1 MVP acceptance criteria explicitly list:
  deterministic resolution chain, typed error, repo-wide reference sweep (FF-4), python-age
  passphrase-only pin note (FF-5).

## Verdict on the chain
D-535→D-568 is directionally correct and matches my review's core finding (delete VaultCore,
resolve at call time). The scope collapse from 8-part spec → allowlist-hide → dead-code-delete
is the Right Approximation. Only correction: ensure the 5 out-of-src/omega consumers are in the
deletion sweep, and carry FF-1/FF-2 into Path B so "minimal" doesn't mean "crashes headless."

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ x-preview-f-free ⬡ opencode ⬡ trc_vault_review_delta ⬡ 2026-08-21*

