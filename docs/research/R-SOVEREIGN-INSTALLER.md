# 🔱 Research Report: One-Click Sovereign Installer Architecture
**Document ID**: R-SOVEREIGN-INSTALLER
**Status**: PROPOSED
**Target**: Omega Engine Deployment
**Author**: Sovereign Master Researcher

## 1. Executive Summary
The Sovereign Installer is designed to transition the Omega Engine from a development repository to a consumer-ready "Sovereign Appliance." The architecture prioritizes **rootless execution**, **hardware-aware optimization**, and **zero-friction onboarding**. By leveraging Podman Quadlets and a `gum`-powered TUI, the installer ensures that the AI stack is persistent, performant, and entirely owned by the user.

---

## 2. The Sovereign Installation Blueprint

### 2.1 The Deployment Pipeline (Sequence of Operations)
The installer follows a strict **Bootstrap $\rightarrow$ Configure $\rightarrow$ Deploy** flow.

1.  **Phase 0: Toolchain Bootstrap**
    - Detect OS (Ubuntu/Fedora/Arch).
    - Verify/Install `podman` and `systemd`.
    - Download/Install `gum` (TUI engine) to a temporary directory.
    - Verify `subuid`/`subgid` configuration for rootless Podman.

2.  **Phase 1: The Sovereign Wizard (TUI)**
    - **Hardware Audit**: Auto-detect CPU architecture (Zen 2/3/4) and suggest optimization flags.
    - **Provider Setup**: Collect API keys for cloud fallbacks (Google, OpenRouter).
    - **Model Selection**: Define the primary local GGUF model to be pulled.
    - **Path Confirmation**: Confirm installation directories (default: `~/omega-engine`).

3.  **Phase 2: Engine Deployment**
    - Clone/Extract Omega Engine source to the target directory.
    - Create Python virtual environment (`.venv`).
    - Install dependencies via `pip`.
    - Generate `config/providers.yaml` and `config/models.yaml` based on Wizard input.

4.  **Phase 3: Container Orchestration (The Quadlet Layer)**
    - Deploy `.container` files to `~/.config/containers/systemd/`.
    - Execute `systemctl --user daemon-reload`.
    - Enable and start services: `redis`, `qdrant`, `postgres`.
    - Execute `loginctl enable-linger <username>` to ensure background persistence.

---

## 3. Technical Deep Dives

### 3.1 Rootless Podman & Quadlets
To achieve a "One-Click" experience without requiring sudo, the installer uses **Quadlets**.

**The `.container` Specification**:
All distributed containers must include:
- `UserNS=keep-id`: Maps the host UID 1000 directly into the container.
- `User=1000`: Ensures the process runs as the user.
- `Volume=/home/<user>/omega-data:/data:Z`: (Note: `:Z` used for SELinux/Fedora, stripped for Ubuntu).

**Automation Command Chain**:
```bash
mkdir -p ~/.config/containers/systemd/
cp ./configs/containers/*.container ~/.config/containers/systemd/
systemctl --user daemon-reload
systemctl --user enable --now omega-redis.service omega-qdrant.service omega-postgres.service
loginctl enable-linger $USER
```

### 3.2 Hardware-Aware Optimization
The installer detects the AMD Zen microarchitecture to set the correct `-march` flags for any local compilation or optimization.

**Detection Logic**:
- **Zen 2**: Family 23 $\rightarrow$ `-march=znver2`
- **Zen 3**: Family 25 $\rightarrow$ `-march=znver3`
- **Zen 4**: Family 25 + Model range $\rightarrow$ `-march=znver4`

**Implementation**:
The installer queries `/proc/cpuinfo` or `lscpu` and writes the resulting flag to a `.env` file or the `config/cpu_optimizer.yaml`.

### 3.3 Local-AI Orchestration
- **Ollama**: Installed via the official shell script. The installer then triggers a `ollama pull <selected_model>` to ensure the engine is ready immediately.
- **LM Studio**: Since LM Studio is a GUI-first app, the installer provides a "Setup Guide" link and checks for the existence of the LM Studio binary. If found, it attempts to create a `systemd` user unit to launch the Local Server in the background.

---

## 4. Proposed Directory Structure

```text
omega-installer/
├── install.sh                # Entry point (The "One-Click" script)
├── wizard/
│   └── setup_wizard.sh       # TUI logic using 'gum'
├── configs/
│   ├── containers/           # Quadlet definitions
│   │   ├── redis.container
│   │   ├── qdrant.container
│   │   └── postgres.container
│   └── hardware/             # Zen architecture mapping table
├── scripts/
│   ├── detect_cpu.sh         # Hardware detection logic
│   ├── setup_podman.sh       # Podman & Linger configuration
│   └── bootstrap_venv.sh     # Python environment setup
└── assets/
    └── logo.txt              # Omega Engine ASCII Art
```

---

## 5. Risk Matrix & Mitigation

| Risk | Impact | Mitigation |
| :--- | :--- | :--- |
| **Missing subuid/subgid** | Container fail | Installer checks files; if missing, prompts user to run a specific `usermod` command. |
| **Distro Divergence** | Path failures | Use a "Sovereign Trinity" support list (Ubuntu, Fedora, Arch). |
| **OOM on Ryzen 5700U** | System crash | Installer sets memory limits in `.container` files based on detected total RAM. |
| **Selinux Blocks** | Permission Denied | Installer detects `.config/selinux` and applies `:Z` labels only on RedHat-family distros. |

## 6. Heritage & Principles
- **Right Approximation**: The installer supports the most common 3 distros rather than trying to be universal.
- **Worse is Better**: Use a shell script wrapper for the initial bootstrap to avoid dependency on a complex installer language (like Ansible/Terraform).
- **Sovereign-Siloing**: All installer data and the resulting engine live entirely within the user's `$HOME` directory.
