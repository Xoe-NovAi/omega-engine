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

# Copy the Makefile fragment (self-contained; no host Makefile required)
cp "$SOURCE_DIR/Makefile.well" "$PROJECT_ROOT/Makefile.well"

echo "✅ The Well installed successfully"
echo ""
echo "Next steps:"
echo "  1. Run tests:  python3 -m unittest discover -s tests -p 'test_well*.py' -v"
echo "  2. Verify corpus:  make -f Makefile.well well-verify"
echo "  3. Add your first record:"
echo "     make -f Makefile.well well-add KIND=correction DOMAIN=harness \\"
echo "       TRIGGER=\"<the thing that surprised you>\" RULE=\"<what to do instead>\" \\"
echo "       RATIONALE=\"<why>\""
echo ""
echo "  To make 'make well-*' work without -f, append the target block from"
echo "  Makefile.well into your project Makefile."
echo ""
echo "  Set WELL_DIR_OVERRIDE=\$PROJECT_ROOT/gnosis/well if auto-detection fails."