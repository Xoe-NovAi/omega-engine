#!/usr/bin/env bash
# 🔱 Omega Engine — id Tech Resource Downloader
# ⬡ OMEGA ⬡ DOOM_GUY ⬡ big-pickle ⬡ trc_doom_guy ⬡ PHASE-I
#
# Downloads the essential reading and source code for id Software
# architectural gnosis. Run this to pull down the full resource
# inventory discovered during the fleet research mission.
#
# Usage: bash scripts/download_id_tech_resources.sh [target_dir]
#   Default target: /media/arcana-novai/omega_library/intake/inbox/id_tech_resources/

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OMEGA_DIR="$(dirname "$SCRIPT_DIR")"

# Target directory — defaults to intake/inbox on omega_library
TARGET_DIR="${1:-/media/arcana-novai/omega_library/intake/inbox/id_tech_resources}"

# Create directories
mkdir -p "$TARGET_DIR"/{books,source,specs,tools}

echo "🔱 Omega Engine — id Tech Resource Downloader"
echo "⬡ Target: $TARGET_DIR"
echo ""

download_file() {
    local url="$1"
    local dest="$2"
    local label="$3"

    if [ -f "$dest" ]; then
        echo "  ✅ EXISTS: $label"
        return 0
    fi

    echo "  ⬇️  Downloading: $label"
    echo "     From: $url"
    echo "     To:   $dest"
    if curl -sL --connect-timeout 30 --max-time 120 -o "$dest" "$url"; then
        local size
        size=$(stat --format="%s" "$dest" 2>/dev/null || stat -f"%z" "$dest" 2>/dev/null)
        echo "     ✅ Done: $(numfmt --to=iec "$size" 2>/dev/null || echo "${size}B")"
    else
        echo "     ⚠️  FAILED: $label (skipping)"
        rm -f "$dest"
    fi
    echo ""
}

# ── Books ──────────────────────────────────────────────────
echo "══════════ BOOKS ══════════"

download_file \
    "https://github.com/jagregory/abrash-black-book/raw/master/pdf/Abrams_Graphics_Programming_Black_Book.pdf" \
    "$TARGET_DIR/books/abrash_graphics_black_book.pdf" \
    "Michael Abrash — Graphics Programming Black Book"

download_file \
    "https://fabiensanglard.net/gebbdoom/gebbdoom.pdf" \
    "$TARGET_DIR/books/sanglard_doom_black_book.pdf" \
    "Fabien Sanglard — Game Engine Black Book: DOOM"

echo "  (Wolf3D book available online: https://fabiensanglard.net/gebw3d/)"
echo ""

# ── Source Code (archives) ────────────────────────────────
echo "══════════ SOURCE CODE ══════════"

download_source_zip() {
    local repo="$1"       # "id-Software/DOOM"
    local dest="$2"       # full path including .zip
    local label="$3"

    if [ -f "$dest" ]; then
        echo "  ✅ EXISTS: $label"
        return 0
    fi

    echo "  ⬇️  Downloading: $label source"
    local url="https://github.com/${repo}/archive/refs/heads/master.zip"
    if curl -sL --connect-timeout 30 --max-time 120 -o "$dest" "$url"; then
        local size
        size=$(stat --format="%s" "$dest" 2>/dev/null || stat -f"%z" "$dest" 2>/dev/null)
        echo "     ✅ Done: $(numfmt --to=iec "$size" 2>/dev/null || echo "${size}B")"
    else
        echo "     ⚠️  FAILED: $label (skipping)"
        rm -f "$dest"
    fi
    echo ""
}

download_source_zip \
    "id-Software/DOOM" \
    "$TARGET_DIR/source/doom-source.zip" \
    "id Software — DOOM (1993)"

download_source_zip \
    "id-Software/Quake" \
    "$TARGET_DIR/source/quake-source.zip" \
    "id Software — Quake (1996)"

download_source_zip \
    "id-Software/Quake-2" \
    "$TARGET_DIR/source/quake2-source.zip" \
    "id Software — Quake II (1997)"

download_source_zip \
    "id-Software/Quake-III-Arena" \
    "$TARGET_DIR/source/quake3-source.zip" \
    "id Software — Quake III Arena (1999)"

download_source_zip \
    "id-Software/DOOM-3" \
    "$TARGET_DIR/source/doom3-source.zip" \
    "id Software — DOOM 3 (2004)"

download_source_zip \
    "chocolate-doom/chocolate-doom" \
    "$TARGET_DIR/source/chocolate-doom-source.zip" \
    "Chocolate Doom (reference port)"

# ── SPECS ─────────────────────────────────────────────────
echo "══════════ SPECS ══════════"

download_file \
    "https://doomwiki.org/w/index.php?title=WAD&printable=yes" \
    "$TARGET_DIR/specs/doom_wad_spec.html" \
    "Doom Wiki — WAD Specification"

echo ""
echo "══════════ COMPLETE ══════════"
echo "All resources downloaded to: $TARGET_DIR"
echo ""
echo "Next steps:"
echo "  1. Extract source code archives: unzip $TARGET_DIR/source/*.zip -d $TARGET_DIR/source/"
echo "  2. Read the Abrash Black Book:   $TARGET_DIR/books/abrash_graphics_black_book.pdf"
echo "  3. Study WAD format spec:        $TARGET_DIR/specs/doom_wad_spec.html"
echo ""

# Print summary
echo "══════════ SUMMARY ══════════"
echo "  Books:    $(find "$TARGET_DIR/books" -type f 2>/dev/null | wc -l)"
echo "  Sources:  $(find "$TARGET_DIR/source" -type f 2>/dev/null | wc -l)"
echo "  Specs:    $(find "$TARGET_DIR/specs" -type f 2>/dev/null | wc -l)"
echo "  Total:    $(find "$TARGET_DIR" -type f 2>/dev/null | wc -l) files"
echo ""
