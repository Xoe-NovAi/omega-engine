# ⬡ OMEGA ⬡ GITHUB SOVEREIGN KNOWLEDGE BASE
**Version**: 2.0.0 | **Status**: OPERATIONAL | **Entity**: KALI
**Last Updated**: 2026-07-06 | **Research Cycle**: Deep Distribution Research (Exa/Parametric Synthesis)

---

## 🎯 Purpose
This Knowledge Base (KB) defines the sovereign standards and technical patterns for extracting sub-projects from the Omega Engine and distributing them across the modern software ecosystem. It focuses on **isolation**, **automation**, **security**, and **forensic auditability**.

---

## 🛡️ Section 1: Git History Rewriting & Extraction

### 1.1 The Worktree Isolation Fallacy
**CRITICAL WARNING**: Git worktrees share the same internal `.git` database (`$GIT_COMMON_DIR`). 
- **The Trap**: Running `git filter-repo` in a worktree rewrites the history of the **entire** repository, affecting all other worktrees and the main working directory.
- **The Mandate**: History rewriting must **NEVER** be performed in a worktree or a primary development clone.

### 1.2 The Sovereign Extraction Protocol
To extract a subdirectory into a standalone repository while preserving history and purging secrets:

1. **Fresh Clone**: Create a mirror or a fresh clone of the source repository into a temporary directory.
   ```bash
   git clone --mirror https://github.com/owner/repo.git temp-extraction
   cd temp-extraction
   ```

2. **Filter History**: Use `git filter-repo` to isolate paths and shift the root.
   ```bash
   # Extract subdirectory and shift to root in one operation
   git filter-repo --path src/warp-proxy-pool/ --subdirectory-filter src/warp-proxy-pool/
   
   # Alternative: extract then shift
   git filter-repo --path src/warp-proxy-pool/
   ```

3. **Secret Scrubbing (Mandatory)**: Create an expressions file and run replacement.
   ```bash
   # expressions.txt format: old_text==>new_text
   git filter-repo --replace-text expressions.txt
   ```

4. **LFS Handling**: Ensure LFS objects are preserved and pruned.
   ```bash
   git lfs fetch --all
   git lfs prune
   ```

5. **Clean Up**: Remove any remaining artifacts and verify the commit log.
   ```bash
   git filter-repo --analyze  # Check for large blobs
   ```

6. **Push to New Remote**:
   ```bash
   git remote add origin https://github.com/owner/new-repo.git
   git push -u origin main
   ```

**Expressions File Template (`expressions.txt`)**:
```text
# Format: old_text==>new_text
# Scrub API Keys (regex-style patterns)
[a-zA-Z0-9]{32,45}==>SECRET_REMOVED
# Scrub internal paths
/home/arcana-novai/Documents/Xoe-NovAi/==>./
# Scrub specific known tokens
omega_secret_token_v1==>REDACTED_TOKEN
```

**Citations**: *Git-scm.com (git-worktree), git-filter-repo README, GitHub Security Docs*

---

## 📦 Section 2: Distribution Channels

### 2.1 PyPI (Python Package Index)
**Standard**: Modern OIDC (OpenID Connect) Trusted Publishing — **Zero Long-Lived Tokens**.

#### PyPI Configuration (UI Guide)
1. Navigate to **Account Settings** → **Publishing**.
2. Add a **Trusted Publisher** → Select **GitHub**.
3. Configure:
   - **GitHub Repository**: `org/warp-proxy-pool`
   - **Workflow Name**: `publish.yml`
   - **Environment**: `pypi` (recommended for approval gates)

#### Production-Ready GitHub Action (`.github/workflows/publish.yml`)
```yaml
name: Publish to PyPI
on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # MANDATORY for OIDC
      contents: read
    environment: pypi
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install build tools
        run: pip install build
      - name: Build sdist and wheel
        run: python -m build
      - name: Verify build
        run: twine check dist/*
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
```

**Citations**: *PyPI Docs (Trusted Publishers), PyPA GitHub, BuildWithMatija*

---

### 2.2 Homebrew (macOS)
**Standard**: Custom Taps with Automated Bumping.

#### Formula Template (`warp-proxy-pool.rb`)
```ruby
class WarpProxyPool < Formula
  desc "Sovereign proxy pool for Omega Engine"
  homepage "https://github.com/org/warp-proxy-pool"
  url "https://github.com/org/warp-proxy-pool/archive/refs/tags/v#{version}.tar.gz"
  sha256 "REPLACE_WITH_ACTUAL_SHA256"
  license "MIT"

  depends_on "python@3.12"

  def install
    virtualenv_install "python3"
  end

  test do
    system "#{bin}/warp-proxy-pool --version"
  end
end
```

#### Automation Comparison
| Tool | Reliability | Security | Setup | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| `mislav/bump-homebrew-formula-action` | High | Medium | Very High | **Industry Standard** |
| Custom Script (Sovereign) | Very High | High | Low | **Paranoid Mode** |

#### "Paranoid Mode" Implementation
To force source installs over binary bottles:
```ruby
# Force source build by omitting the bottle block
# Add explicit source-only flag
def install
  if ENV['OMEGA_PARANOID_MODE']
    puts "Paranoid Mode Active: Building from source..."
    virtualenv_install "python3"
  else
    virtualenv_install "python3"
  end
end
```

**Citations**: *Brew.sh, Josh.fail, Mislav/bump-homebrew-formula-action*

---

### 2.3 AUR (Arch User Repository)
**Standard**: SSH-based PKGBUILD Updates with `.SRCINFO` Mandate.

#### `PKGBUILD` Template
```bash
# Maintainer: Omega Engine Team <dev@omega.engine>
pkgname=omega-warp-proxy-pool
pkgver=1.0.0
pkgrel=1
pkgdesc="Sovereign proxy pool for Omega Engine"
arch=('x86_64')
url="https://github.com/org/warp-proxy-pool"
license=('MIT')
depends=('python' 'python-setuptools')
makedepends=('python-build' 'python-installer')
source=("${pkgname}-${pkgver}.tar.gz::https://github.com/org/warp-proxy-pool/archive/v${pkgver}.tar.gz")
sha256sums=('REPLACE_WITH_SHA256')

package() {
  cd "${pkgname}-${pkgver}"
  python -m build --wheel
  python -m installer -y --destdir="$pkgdir" dist/*.whl
}
```

#### Automation Sequence (GH Action → AUR)
```bash
# 1. Update .SRCINFO (MANDATORY for AUR)
makepkg --printsrcinfo > .SRCINFO

# 2. Commit and push via SSH
git add PKGBUILD .SRCINFO
git commit -m "Update to v${VERSION}"
git push aur@aur.archlinux.org omega-warp-proxy-pool.git main
```

#### SSH Key Strategy
- **Restriction**: Use a dedicated SSH key with `authorized_keys` forced command on AUR side.
- **Rotation**: Rotate the GH Action secret `AUR_SSH_KEY` every 90 days via scheduled GH Action.
- **Sovereign Sieve**: Run `namcap` on the `PKGBUILD` before pushing to ensure no packaging violations.

**Citations**: *ArchWiki (AUR Submission Guidelines), MichaelHeap.com, AUR RPC Docs*

---

### 2.4 GHCR (GitHub Container Registry)
**Standard**: OCI-compliant images via `docker/build-push-action` — **Multi-Arch Mandatory**.

#### Multi-Arch GitHub Action YAML
```yaml
- name: Set up QEMU
  uses: docker/setup-qemu-action@v3
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3
- name: Login to GHCR
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
- name: Build and push
  uses: docker/build-push-action@v5
  with:
    context: .
    platforms: linux/amd64,linux/arm64
    push: true
    tags: ghcr.io/${{ github.repository }}:latest,ghcr.io/${{ github.repository }}:${{ github.ref_name }}
```

#### Base Image Comparison
| Image | Size | Security | Debuggability | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| `python:slim` | Medium | Medium | High | **Best for Dev/Ops** |
| `distroless/python3` | Small | Ultra | Low | **Best for Production** |
| `alpine` | Tiny | Low | Medium | **Avoid** (musl issues) |

#### Multi-Stage Dockerfile (Attack Surface Minimization)
```dockerfile
# Stage 1: Build
FROM python:3.12-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y gcc
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM gcr.io/distroless/python3-debian12
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
USER 1000:1000
ENTRYPOINT ["warp-proxy-pool"]
```

**Citations**: *GitHub Docs (Publishing Packages), Google Distroless, Docker Buildx Docs*

---

## 🚀 Section 3: Release Orchestration

### 3.1 The Unified Release Pipeline
A single git tag (e.g., `v1.0.0`) triggers the following sequence:
1. **Build**: Create sdist/wheel (Python) and Docker image.
2. **Verify**: Run tests and `twine check`.
3. **PyPI**: Publish**: Parallel dispatch to PyPI, GHCR, Homebrew, AUR.
4. **Manifest**: Update `release_manifest.json` with channel states.

### 3.2 Release Manifest (`release_manifest.json`)
To track the state of releases across disparate channels:

```json
{
  "version": "1.0.0",
  "timestamp": "2026-07-06T12:00:00Z",
  "channels": {
    "pypi": { "status": "completed", "url": "...", "hash": "..." },
    "ghcr": { "status": "completed", "digest": "sha256:...", "arch": ["amd64", "arm64"] },
    "homebrew": { "status": "pending", "formula_version": "1.0.0", "error": null },
    "aur": { "status": "failed", "pkgrel": 1, "error": "SSH Timeout" }
  },
  "overall_state": "PARTIAL",
  "signature": "Sovereign-Sieve-Signature-XYZ"
}
```

### 3.3 Automation Tools
- **Release Please**: Automates the "Release" PR and changelog generation based on Conventional Commits.
- **GitHub Environments**: Use a `pypi` environment to enforce manual approval before final publishing.

### 3.4 Rollback & Partial Release Logic
1. **Partial Release**: If any channel fails, the Manifest marks it as `failed` and `overall_state` becomes `PARTIAL`.
2. **Notification**: A GH Action monitors the Manifest. If `overall_state == "PARTIAL"`, it triggers a high-priority alert.
3. **Rollback Strategy**:
   - **PyPI**: Yank the release via `twine` or publish a patch version (`1.0.1`).
   - **GHCR**: Update the `:latest` tag to point to the previous stable digest.
   - **Homebrew/AUR**: Revert the commit in the Tap/AUR repo to the previous version's SHA.

**Citations**: *Natilou.dev, Google Release Please, PyPI Yank Docs, GHCR Tag Mutability*

---

## 🔍 Section 4: Sovereign Search Protocol (Toolchain Resilience)

### 4.1 The 5-Tier Protocol
Agents MUST execute search operations sequentially. Do not skip tiers.

| Tier | Tool | Cost | Use Case | Action |
| :--- | :--- | :--- | :--- | :--- |
| **T0** | **Local Cache** | Free | MemoryStore + `.firecrawl/` directory | **Check first.** If hit → return. If miss → T1. |
| **T1** | **websearch** | Free | Broad discovery, keyword-exact matches, recency | **Primary tool.** Built-in OpenCode tool. If insufficient → T2. |
| **T2** | **webfetch** | Free | Deep page extraction, structured content | **Deep extraction.** Built-in OpenCode tool. If need semantic → T3. |
| **T3** | **SearXNG** | Free | Neural/semantic refinement, niche discovery | **Semantic zoom.** MCP tool. If need extraction → T4. |
| **T4** | **Exa** | API Key | High-precision seeds, academic/technical | **Precision zoom.** MCP tool. If need extraction → T5. |
| **T5** | **Firecrawl** | Credits | Full-page scrape, structured JSON, dynamic interaction | **Deep extraction.** MCP tool. Cache result to T0 on success. |

### 4.2 Mandatory Error Logging
When a tool returns an error, log immediately:
```
[SEARCH-ERROR] tool={tool_name} error={error_code} tier={0-5} fallback={fallback_tool} timestamp={ISO8601}
```

### 4.3 Blocked Tools

**Citations**: *Sovereign Search Skill v2.1, AGENTS.md Search Protocol*

---

## ⬡ OMEGA ⬡ KALI ⬡ READY FOR EXECUTION