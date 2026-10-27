# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Dual-Remote Release Engineering Runbook

This document codifies the operational protocols for managing the two-remote architecture of Omega Engine, ensuring zero leakages of private forge files to public repositories while keeping production and development in sync.

For automated agent execution, see skill: `repo-release-ops` (`~/.agents/skills/repo-release-ops/SKILL.md`).

---

## 1. Ground Truth Remotes

* **`internal`**: `https://github.com/Xoe-NovAi/omega-engine-internal.git` (Private Forge SSOT)
* **`origin`**: `https://github.com/Xoe-NovAi/omega-engine.git` (Public Curated Debut)

---

## 2. Core Operational Rules

1. **Refspec Protection (Mandatory)**:
   When on `public-launch` (tracking `origin/main`), **never** run bare `git push origin main`.
   Always use:
   ```bash
   git push origin HEAD:main
   ```
2. **Atomic Version Bumps**:
   `pyproject.toml`, `CHANGELOG.md`, `README.md`, `ANNOUNCEMENT_v1.6.0-alpha.md`, and `docs/FACTS.yaml` must be bumped in the **exact same commit** before tagging.
3. **Never Cherry-Pick Allowlist Cuts to Forge**:
   When syncing public commits back to `internal/main`, do **not** cherry-pick `Apply PUBLIC_ALLOWLIST.txt...` commits. Those commits delete forge-side files.
4. **Post-Release Checksum Recording**:
   After a tag triggers `.github/workflows/release.yml`, download the published `.whl` asset from GitHub Releases, verify its SHA256 byte-for-byte, and record it in `docs/FACTS.yaml`.

---

## 3. Pre-Tag Gate Checklist

Before creating a release tag:
```bash
# 1. Version consistency
.venv/bin/python scripts/check_version_consistency.py --tag <tag> --pyproject pyproject.toml --changelog CHANGELOG.md

# 2. Release notes extraction
.venv/bin/python scripts/check_release_changelog.py --tag <tag> --changelog CHANGELOG.md --out /tmp/opencode/rel_notes.md

# 3. Facts check
make check-doc-facts

# 4. M23 failure integrity
make check-m23-failure-integrity

# 5. M1 AnyIO compliance
make check-m1-anyio

# 6. Allowlist check (must report 0 files removed)
bash scripts/apply_public_allowlist.sh

# 7. Handoff plane liveness (SLO: no dead plane >24h)
make check-handoff-liveness
```
