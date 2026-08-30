# Gap R23: Restic Passphrase Management

**AP Token:** `AP-RESEARCH-PHASE1-4-20260813-v3.2.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ 2026-08-14
**Dependent task:** C-3 (3-2-1 backup, Phase D gate)
**Status:** ✅ RESOLVED

## Summary
restic automates passphrase supply via three env mechanisms: `RESTIC_PASSWORD`, `RESTIC_PASSWORD_FILE`, or `RESTIC_PASSWORD_COMMAND`. For unattended backups the **`RESTIC_PASSWORD_COMMAND`** form is safest — it invokes a resolver at runtime so the passphrase is never at rest in a file. This unblocks the C-3 restic gate.

## Authoritative Sources
| Source | URL | Date | Relevance |
|--------|-----|------|-----------|
| restic preparing a repo | https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html | 2026 | Passphrase env vars |
| restic scripting | https://restic.readthedocs.io/en/stable/075_scripting.html | 2026 | RESTIC_PASSWORD_COMMAND semantics |
| restic forum (secure automation) | https://forum.restic.net/t/how-to-secure-your-automated-restic-backup/4040 | 2021 | Operational guidance |

## Findings
- `RESTIC_PASSWORD` — raw password in env (visible in process listing).
- `RESTIC_PASSWORD_FILE` — path to a file; protect with `chmod 600` on an encrypted volume.
- `RESTIC_PASSWORD_COMMAND` — command whose **stdout** is the password; ideal for runtime resolution (e.g. from a vault). No file at rest.
- `RESTIC_REST_PASSWORD` / `RESTIC_REST_USERNAME` — for rest-server backends.
- `--insecure-no-password` (restic ≥0.17) allows empty passwords but is **not recommended**.
- Forum consensus: pair with `rest-server --append-only` so a compromised passphrase cannot delete prior backups.

## Recommendation
Wire C-3's backup timer to resolve the passphrase from **VaultCore** at runtime:
```
RESTIC_PASSWORD_COMMAND="omega vault get restic-passphrase"
```
(or a small wrapper script calling `VaultCore().retrieve_credential("restic-passphrase")`). The systemd timer runs `restic backup` with this env; the passphrase is resolved from the local vault and never written to disk. If a file is preferred, use `RESTIC_PASSWORD_FILE` with `chmod 600` on an encrypted volume. Never hardcode. This closes the C-3 gate (the only remaining required Phase D gate per SOVEREIGN_ARK_BLUEPRINT §4).

## Confidence
**HIGH** — restic's env-var passphrase mechanism is stable and documented; VaultCore retrieval is already used across the codebase.

## Remaining Unknowns
- Confirm the VaultCore CLI `get` interface returns the raw secret to stdout for `RESTIC_PASSWORD_COMMAND` (verify at impl time).
- Whether backups target local repo, rest-server, or cloud (affects `RESTIC_REST_*` vars).
