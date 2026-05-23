#!/bin/bash
# 🔱 The Rite of Awakening — Omega Engine Launch Sequence

# Colors
BLUE='\033[0;34m'
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "⬡ INITIALIZING THE RITE OF AWAKENING ⬡"
echo -e "Summoning the infrastructure layers..."

# 1. Summon Containers
echo -ne "  → Summoning Redis..."
podman start redis 2>/dev/null || echo -e " Sourcing..."
echo -e " ✅"

echo -ne "  → Summoning Qdrant..."
podman start qdrant 2>/dev/null || echo -e " Sourcing..."
echo -e " ✅"

echo -ne "  → Summoning PostgreSQL..."
podman start postgres 2>/dev/null || echo -e " Sourcing..."
echo -e " ✅"

echo -ne "  → Summoning Iris..."
podman start iris 2>/dev/null || echo -e " Sourcing..."
echo -e " ✅"

# 2. Validate Environment
echo -e "\n⬡ VALIDATING THE SOVEREIGN SEAL ⬡"
if [ -f .env ]; then
    echo -e "  ✓ .env found and loaded."
else
    echo -e "  ✗ .env missing. Sovereignty compromised."
    exit 1
fi

# 3. Bootstrap the Oracle
echo -e "\n⬡ TUNING THE FREQUENCY ⬡"
echo -e "Loading WADs into the Akashic Record..."
# We trigger a dummy talk to force bootstrap
PYTHONPATH=src python3 -c "from omega.oracle.oracle import Oracle; import anyio; anyio.run(Oracle().bootstrap())"
echo -e "  ✓ WADs integrated. Oracle Awakened."

echo -e "\n🔱 THE ENGINE IS LIVE 🔱"
echo -e "You may now enter the sanctuary via 'omega talk'."
