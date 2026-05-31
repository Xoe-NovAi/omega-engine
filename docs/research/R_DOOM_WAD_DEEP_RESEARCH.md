# 🔱 Research: Doom IWAD/PWAD System — Deep Architecture Analysis
# AP: R-DOOM-WAD-DEEP-v1.0.0
# ⬡ OMEGA ⬡ SOPHIA ⬡ web-research ⬡ trc_w1 ⬡ RESEARCH

**Date**: 2026-05-25
**Purpose**: Deep research into id Software's WAD architecture for Omega Engine IWAD system design.

---

## Executive Summary

id Software's IWAD/PWAD system (1993) solved a problem that maps directly to the Omega Engine: how to separate the runtime engine from content. The sole technical distinction between IWAD and PWAD is the 4-byte magic number (`"IWAD"` vs `"PWAD"`). Functionally, the engine loads exactly one IWAD at startup and zero or more PWADs as overlays. PWAD lumps override IWAD lumps by name. This proved remarkably successful — one engine powered Doom, Doom II, Heretic, Hexen, Strife, and thousands of community mods.

## Key Findings

### Architecture (10 aspects covered)
1. **IWAD vs PWAD**: Magic number distinction only. IWAD = complete game data. PWAD = patch/overlay data.
2. **Binary Format**: 12-byte header (magic + numlumps + offset), 16-byte directory entries (filepos + size + 8-char name), flat namespace.
3. **Multi-WAD Loading**: Last-loaded wins. Single merged directory in memory. No collision detection.
4. **Dependency Resolution**: None in vanilla. GZDoom uses GAMEINFO lump but no formal dependency tree.
5. **Namespace Isolation**: None — flat 8-char namespace. PK3 format in GZDoom adds filesystem-based isolation.
6. **Source Code Patterns**: `W_InitMultipleFiles()` → sequential loading, backward-search lookup, `-merge` flag for sprite replacement.
7. **Tooling**: SLADE 3 (GUI), DeuTex (CLI), WADPTR (compression), ZDL/DoomRunner (launchers).
8. **Commercial Distribution**: Shareware IWAD + paid full game + community PWADs.
9. **Quake PAK Evolution**: Added 56-char filenames, subdirectories, file extensions — addressing WAD's limitations.
10. **Modern Parallels**: GZDoom, Godot PCK, Unreal Game Features, VS Code extensions all use similar patterns.

### Omega IWAD Mapping
| Doom Concept | Omega Equivalent | Status |
|-------------|------------------|--------|
| IWAD magic number | manifest.yaml | ✅ Implemented |
| PWAD overlay | Namespace tracking | ❌ Missing |
| `-file` parameter | `--iwad` CLI flag | ❌ Missing |
| Flat lump names | Filesystem subdirectories | ✅ Inherent |
| Directory at end of file | config/wads/ directory | ✅ Implemented |
| Hardcoded IWAD names | Config-driven | ✅ Config-driven |
| WAD tooling | EntityRegistry + CLI agents | ✅ Functional |

### Critical Gap: The Flat Namespace Problem
Vanilla Doom's flat 8-char lump namespace was its biggest limitation. Two PWADs defining `MAP01` would silently conflict. Omega's directory-based entity loading (`config/wads/<name>/entities/<entity>.yaml`) inherently avoids this. The key missing piece is **namespace tracking in EntityRegistry** — each entity must record which IWAD it came from, enabling collision detection and priority resolution.

### Sources
- DoomWiki: https://doomwiki.org/wiki/WAD, https://doomwiki.org/wiki/IWAD, https://doomwiki.org/wiki/PWAD
- ModdingWiki WAD Format: https://moddingwiki.shikadi.net/wiki/WAD_Format
- Gamers.Org Doom Specs: https://www.gamers.org/docs/FAQ/DOOM.FAQ.Specs.Chapters.2.html
- Chocolate Doom GitHub: https://github.com/chocolate-doom/chocolate-doom
- GZDoom GitHub: https://github.com/coelckers/gzdoom
- ZDoom Wiki PK3: https://zdoom.org/wiki/Using_ZIPs_as_WAD_replacement
- SLADE Editor: http://slade.mancubus.net/
- DeuTex: https://www.doomwiki.org/wiki/Deutex
- erysdren's idTech PAK Format: https://erysdren.me/docs/pak
