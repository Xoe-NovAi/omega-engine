# 🔱 Omega Engine Research: R-45
# OpenCode TUI & REPL Scroll Optimization
**Date**: 2026-06-23
**Author**: Ma'at / Roc Racoon
**Tags**: UX, TUI, Prompt Toolkit, OpenCode, CLI

## 1. The Problem Statement
The OpenCode Terminal User Interface (TUI) and the Omega CLI REPL suffered from severe scrolling UX degradation. 
1. **OpenCode TUI**: Scrolling operated in large, jarring chunks (typically 7+ lines per tick), making it extremely difficult to read long agent outputs or trace code blocks without losing visual context.
2. **Omega REPL**: Outputting large text blocks caused terminal buffer mismatches, resulting in the prompt jumping erratically.

## 2. Root Cause Analysis
### 2.1 OpenCode TUI (Prompt Toolkit)
OpenCode relies on `prompt_toolkit` for its UI. By default, mouse wheel events in many terminal emulators translate to multiple arrow-key presses or chunked scroll events. Without explicit acceleration and speed dampening configurations, the TUI passes these raw chunked events directly to the buffer view, resulting in the "jumpy" UX.

### 2.2 Omega REPL (`src/omega/cli/repl.py`)
The REPL was using standard Python `print()` statements to output agent responses while a `prompt_toolkit` session was active. Standard `print()` bypasses the application's internal buffer management, causing the terminal emulator and the TUI to fight over the cursor position.

## 3. The Implementation (The "Right Approximation")
*Heritage Tag: `[id-soft: quake3-1999] Right Approximation` — We cannot achieve pixel-perfect scrolling in a character-grid terminal, but we can achieve single-line smooth velocity.*

### 3.1 OpenCode Configuration (`opencode.json`)
We injected the following block into the user's `opencode.json`:
```json
"tui": {
  "scroll_acceleration": {
    "enabled": true
  },
  "scroll_speed": 3,
  "mouse": true,
  "leader_timeout": 1500,
  "diff_style": "auto"
}
```
**Result**: Forces the TUI to interpret scroll events with a dampened velocity, resulting in a smooth, single-line-at-a-time scroll that preserves visual continuity.

### 3.2 Omega REPL Fix
Replaced `print(response)` with `self.session.print(response)` in `src/omega/cli/repl.py`.
**Result**: Routes all output through the `prompt_toolkit` renderer, keeping the buffer synchronized and eliminating cursor jumping.

## 4. Future Evolution (Pixel-Perfect Scrolling)
The user noted that while this is a "life-changing" improvement, it is not "iPhone-level pixel-by-pixel smooth." 

**Why?** Terminal emulators operate on a strict character grid (e.g., 80x24 cells). They do not natively understand pixels. 
**Future Path**: To achieve true pixel-perfect scrolling in the future, we would need:
1. A modern GPU-accelerated terminal emulator (e.g., Kitty, WezTerm, Alacritty).
2. Upstream patches to `prompt_toolkit` to support the Kitty Keyboard Protocol or specific pixel-scroll escape sequences (e.g., CSI `? 1004 h` / `1006 h` extensions).

For Epoch 1-3, the single-line dampening is the accepted Sovereign Standard for terminal UX.