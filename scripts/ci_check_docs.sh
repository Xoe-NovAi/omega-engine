#!/bin/bash
# Omega Engine Documentation Lint
# Ensures all research and decision docs follow the DMS standards.

FAILED=0
FILES=$(find docs/research docs/decisions -name "*.md")

echo "Checking Omega Documentation Standards..."

for file in $FILES; do
    # Check for session header in first line
    FIRST_LINE=$(head -n 1 "$file")
    if [[ ! "$FIRST_LINE" == *"⬡ OMEGA"* ]]; then
        echo "❌ $file: Missing or invalid session header in first line."
        FAILED=1
    fi

    # Check for AP Token in first 5 lines
    if ! head -n 5 "$file" | grep -q "AP Token:"; then
        echo "❌ $file: Missing AP Token in first 5 lines."
        FAILED=1
    fi
done

if [ $FAILED -eq 1 ]; then
    echo "Documentation lint failed. Please refer to R97_omega_doc_architect.md."
    exit 1
else
    echo "✅ All documentation standards met."
    exit 0
fi
