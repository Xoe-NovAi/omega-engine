#!/usr/bin/env bash
# Clean up the historic .env exposure from the repo history.
# This script is safe to run multiple times – it will only delete the file
# from the working tree if it exists, then suggest a history rewrite.

set -euo pipefail

FILE="deploy/infra/.env"
if [[ -f "$FILE" ]]; then
    echo "Removing $FILE from working tree..."
    rm -f "$FILE"
    echo "Deleted $FILE"
else
    echo "$FILE not present – nothing to delete."
fi

# Suggest a history rewrite (requires git-filter-repo or BFG)
cat <<'EOF'
If you need to purge the file from the entire repository history, run:
    git filter-repo --path $FILE --invert-paths
or, with BFG:
    bfg --delete-files $FILE

After rewriting, force‑push the cleaned history:
    git push --force --all && git push --force --tags
EOF
