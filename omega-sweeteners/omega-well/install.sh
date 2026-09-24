#!/bin/bash
# Install The Well into a project

set -euo pipefail

PROJECT_ROOT="${1:-$(pwd)}"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing The Well into $PROJECT_ROOT"

# Create directories
mkdir -p "$PROJECT_ROOT/gnosis/well"
mkdir -p "$PROJECT_ROOT/scripts"
mkdir -p "$PROJECT_ROOT/tests"

# Copy corpus
cp -r "$SOURCE_DIR/gnosis/well/"* "$PROJECT_ROOT/gnosis/well/"

# Copy scripts
cp "$SOURCE_DIR/scripts/well_storage.py" "$PROJECT_ROOT/scripts/well_storage.py"
chmod +x "$PROJECT_ROOT/scripts/well_storage.py"

# Copy tests
cp "$SOURCE_DIR/tests/test_well.py" "$PROJECT_ROOT/tests/test_well.py"

echo "✅ The Well installed successfully"
echo ""
echo "Next steps:"
echo "  1. Add WELL_DIR_OVERRIDE to your environment if needed:"
echo "     export WELL_DIR_OVERRIDE=\$PROJECT_ROOT/gnosis/well"
echo "  2. Run tests: python3 tests/test_well.py"
echo "  3. Try: python3 scripts/well_storage.py add correction harness \"trigger\" \"rule\" \"rationale\" --tags test --pack test"
echo "  4. Add Make targets from WELL_INTEGRATION.md to your Makefile"