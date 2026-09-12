#!/bin/bash

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# Install omega-meditation skill globally in isolated venv
# M16: Modularization & Portability — no hardcoded paths, proper isolation

set -euo pipefail

SKILL_NAME="autonomous-meditation-pipeline"
SKILL_DIR="$HOME/.config/opencode/skills/$SKILL_NAME"
VENV_DIR="$SKILL_DIR/.venv"
SOURCE_DIR="/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/packages/omega-meditation"

echo "[install-global-skill] Installing $SKILL_NAME to $SKILL_DIR"

# Create skill directory
mkdir -p "$SKILL_DIR"

# Create isolated virtual environment
echo "[install-global-skill] Creating virtual environment..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# Upgrade pip and install uv
pip install --upgrade pip uv

# Install the package in development mode
echo "[install-global-skill] Installing omega-meditation from $SOURCE_DIR..."
uv pip install -e "$SOURCE_DIR"

# Copy skill manifests
echo "[install-global-skill] Copying skill manifests..."
cp -r "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/skills/meditate-pipeline/"* "$SKILL_DIR/" 2>/dev/null || true
cp -r "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/skills/meditate-research-pipeline/"* "$SKILL_DIR/" 2>/dev/null || true

# Create merged SKILL.md with triggers
cat > "$SKILL_DIR/SKILL.md" << 'SKILL_EOF'
# ⬡ AUTONOMOUS MEDITATION PIPELINE SKILL
**Version**: 1.0.0 | **Heritage**: Omega Engine Meditation Protocol
**Purpose**: Full Problem → Architecture → Research → Gnosis → Integration pipeline

## Triggers
```yaml
triggers:
  - pattern: "meditate on|autonomous meditation|run meditation pipeline"
    skill: autonomous-meditation-pipeline
    agent: kali
    priority: high
  - pattern: "problem.*architecture|architecture.*problem"
    skill: autonomous-meditation-pipeline
    agent: kali
    priority: medium
  - pattern: "research.*grounded|grounded.*research"
    skill: autonomous-meditation-pipeline
    agent: kali
    priority: medium
```

## Usage
```bash
# Full pipeline
/meditate-pipeline "Your problem statement"

# Specific stages
/meditate-pipeline "problem" --stage meditate
/meditate-pipeline "problem" --stage research
```

## Entry Points
- `omega-meditation` — CLI entry point
- `meditate-auto` — Alias for omega-meditation
SKILL_EOF

# Create wrapper script in skill dir
cat > "$SKILL_DIR/omega-meditation" << 'WRAPPER_EOF'
#!/bin/bash
# Wrapper that activates skill venv and runs omega-meditation
source "$HOME/.config/opencode/skills/autonomous-meditation-pipeline/.venv/bin/activate"
exec omega-meditation "$@"
WRAPPER_EOF

chmod +x "$SKILL_DIR/omega-meditation"

# Create meditate-pipeline command wrapper
cat > "$SKILL_DIR/meditate-pipeline" << 'WRAPPER_EOF'
#!/bin/bash
# Wrapper for /meditate-pipeline slash command
source "$HOME/.config/opencode/skills/autonomous-meditation-pipeline/.venv/bin/activate"
exec omega-meditation "$@"
WRAPPER_EOF

chmod +x "$SKILL_DIR/meditate-pipeline"

deactivate

echo "[install-global-skill] ✅ Skill installed at $SKILL_DIR"
echo "[install-global-skill] Run: $SKILL_DIR/omega-meditation --help"