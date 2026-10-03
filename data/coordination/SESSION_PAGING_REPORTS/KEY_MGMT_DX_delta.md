<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# KEY_MGMT_DX_delta.md — Secure Key Management: DX & Migration Contributions
**AP Token**: AP-MAAT-DX-v1.0.0
⬡ OMEGA ⬡ MAAT ⬡ x-preview-f-free ⬡ opencode ⬡ trc_key_mgmt_dx ⬡ PAGING-BATCH-2

**Paged**: 2026-08-21 · **Architect-direct**: kali (ses_fdef2be4effe4pAaLXCTUx62GO)
**Origin**: key-management-design workspace-lock session (2026-08-18; lock acquired + released)
**Companion delta**: KEY_MGMT_DESIGN_delta.md (sibling — storage/session design)
**Supersession notice**: My SOPS+age backend recommendation was superseded post-debut by
D-562/D-568 Path B (python-age primary). This report preserves ONLY backend-agnostic
DX/migration value. Storage mechanics live in the companion delta.
**Updates absorbed**: env→keyring resolution order · zero-padded NN convention ·
Active-Passive sticky routing · libsecret headless failure validating python-age choice.

## §1 Migration-Path Designs Worth Reviving (post-debut vault sprint)

**M1. One-shot import verb with destroy semantics** — `omega secrets import --from-file=PATH --destroy-source`
Pipeline: parse → preview KEY NAMES ONLY → confirm prompt → encrypt-write vault → `shred -u` source.
Never echo values at any stage; preview lists normalized key names so the user eyeballs coverage
before commit. Idempotence guard: refuse if vault already exists unless `--force`.

**M2. Import receipt (audit w/o exposure)** — on success write `data/secrets/.import_receipt.json`:
{timestamp, secret_count, source_path_hash, per-provider counts}. Enables "did migration happen?"
forensics forever after the plaintext is destroyed. Cheap, high-value, backend-agnostic.

**M3. Parser normalization spec** (env-var name → vault key):
strip `_API_KEY` suffix → lowercase → hyphens→underscores → account suffix `_NN` (default `_01`
when absent). Non-secrets (e.g. SEARXNG_BASE_URL) importable but typed `config`.
⚠️ UPDATE REQUIRED: my original emitted unpadded `_1`; sibling delta standardized zero-padded
`_NN` (openrouter_01). Any revived parser MUST emit padded form (or normalize on read).

**M4. Verification-without-exposure protocol** (`verify-import`):
decrypt in memory → assert every key parses as non-empty string → per-provider format-prefix
validation (sk-or-v1-, AIzaSy…) → print metadata table (provider/count/names/date) → confirm
shred. Zero key material ever reaches stdout or logs.

**M5. Why revival is cheap**: M1–M4 operate on `dict[str,str]` BEFORE any encryption call —
they are backend-agnostic. Only the final `write_vault()` differs (SOPS subprocess vs python-age
API). Port cost ≈ hours, not days.

## §2 DX Insights (CLI ergonomics & error surfaces) — not captured elsewhere

**D1. `get` suppresses trailing newline** (`click.echo(..., nl=False)`): makes
`$(omega secrets get openrouter_03)` compose cleanly in shell/backticks — a trailing \n
corrupts equality checks and curl header assembly. Small detail, constant friction-saver.

**D2. NotFound errors must enumerate siblings**: with 8-account sharding, off-by-one
account IDs are THE dominant human error. `CredentialNotFoundError("openrouter_9")`
should answer: "available: openrouter_01..openrouter_08". Turns dead-ends into
self-service recovery; applies equally to the python-age backend.

**D3. Metadata-only `list`, no masked values**: my original sketch masked prefix/suffix
(sk-o…1234). On reflection: masking invites false confidence and screenshot leaks.
List should show key-name/provider/last_rotated ONLY — recommend vault sprint adopt
names-only.

**D4. Whole-file `$EDITOR` bulk-edit remains the killer primitive**, regardless of
backend. For python-age, replicate SOPS semantics: decrypt to 0600 tempfile in private
tmpdir → spawn $EDITOR → re-encrypt on clean exit → ALWAYS unlink temp (try/finally).
This was the core reason SOPS won my eval; python-age can inherit the UX.

**D5. Single-key `rotate <key>` isolation**: rotate flows edit ONE key in a minimal
buffer so routine rotation never exposes the other 31 secrets in an editor. Pair with
auto-bump of last_rotated metadata.

**D6. Headless degradation message**: sibling delta confirmed libsecret fails headless —
the CLI must catch that class and print an actionable pointer ("keyring unavailable
headless; python-age backend active / set OMEGA_SECRETS_BACKEND") instead of a raw dbus
traceback.

## §3 Flagged Important, Never Executed (at dormancy)

**N1. ModelGateway import-time `.env` dump — verify actual death.** My session flagged
`_load_sovereign_secrets()` (model_gateway.py ~L316-341) as CRITICAL: reads .env at
import, dumps everything into os.environ (M7/M22/M24 violation). Post-debut updates say
env→keyring RESOLUTION ORDER landed — if that means env is tried FIRST, a stale plaintext
.env will silently shadow every vault rotation. Recommendation: delete the .env loader
once CredentialProvider owns the provider factories, or make vault precede env, AND emit
a startup warning when .env contains key-shaped vars. Debut check:
`grep -n "_load_sovereign_secrets" src/omega/oracle/model_gateway.py`.

**N2. Deletion plan status unknown — treat as checklist, not history.** Planned
`git rm`: src/omega/vault/ (2,039 LOC), scripts/vault_import.py, src/omega/cli/vault.py.
Pyproject pruning AMENDED by D-562/D-568: KEEP python-age (now primary); keyring stays
only if resolution order still consults it; cryptography removable only after an import
audit confirms nothing else uses it.

**N3. Corpus correction**: my SOPS+age verdict was correct on merits (bulk-edit, offline,
Git-native) but wrong on debut constraints — system-binary install burden (sudo apt sops
age) breaks one-command community install. python-age keeps crypto inside the venv
(M24-clean). Recorded so future sessions don't relitigate.

**N4. verify-import + receipt (M2/M4) were never built** — highest-value revival
candidates; they de-risk the debut-day migration story for users carrying plaintext files.

— END OF REPORT —
