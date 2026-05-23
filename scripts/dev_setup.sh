#!/usr/bin/env bash
# 🔱 Omega Engine — Dev Environment Setup Script
# AP: AP-DEV-SETUP-v1.0.0
#
# Usage: bash scripts/dev_setup.sh
# Creates a virtual environment and installs all dependencies.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "⬡ OMEGA ⬡ Setting up development environment..."

# 1. Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3.13 -m venv .venv
fi

# 2. Activate and upgrade pip
source .venv/bin/activate
pip install --upgrade pip setuptools wheel

# 3. Install project with dev extras
echo "Installing omega with dev dependencies..."
pip install -e ".[dev]"

# 4. Source .env if present (ignored by git)
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
    echo "Environment variables loaded from .env"
fi

# 5. Verify installation
echo ""
echo "Verifying installation..."
python -c "import omega; print('omega:', omega.__version__)" 2>/dev/null || true
python -c "import apscheduler; print('apscheduler:', apscheduler.__version__)"

echo ""
echo "✅ Omega Engine dev environment ready!"
echo "Run 'make test' to verify."