# 🔱 Sovereign TUI Optimization: Smooth Scrolling & Velocity Navigation

**Project**: OpenCode R&D  
**Status**: ✅ IMPLEMENTED / VERIFIED  
**Target**: Omega Engine Interface  

## 1. Executive Summary
The interface of the Omega Engine is the primary lens through which the Architect interacts with the Pillar Keepers. A "clunky" or "stepped" scrolling experience breaks cognitive flow and immersion during deep-context synthesis. This research identifies the mechanism for implementing **Velocity-Based Scrolling** (macOS-style) within the OpenCode TUI to ensure a seamless, high-performance user experience.

## 2. Technical Analysis

### 2.1 The Mechanism: `scroll_acceleration`
OpenCode's TUI is powered by the `@opentui/core` library. The scrolling behavior is governed by the `ScrollAcceleration` interface.

*   **Linear Scrolling (`scroll_speed`)**: Moves the viewport by a fixed number of lines per event. While precise, it is inefficient for navigating long-form research outputs or extensive chat histories.
*   **Accelerated Scrolling (`scroll_acceleration`)**: Implements the `MacOSScrollAccel` class. This class tracks the timing between scroll events; as the frequency of events increases (faster wheel spin/swipe), the scroll distance increases exponentially.

### 2.2 Configuration Matrix

| Setting | Value | Effect | Recommendation |
| :--- | :--- | :--- | :--- |
| `scroll_acceleration.enabled` | `true` | Activates velocity-based scrolling. | **REQUIRED** for Sovereign UX. |
| `scroll_speed` | `3` (default) | Sets the base linear speed. | Keep as fallback; ignored when acceleration is on. |
| `mouse` | `true` | Enables mouse/touchpad capture. | **REQUIRED** for acceleration to function. |

## 3. Terminal Compatibility & Environmental Impact

The effectiveness of `scroll_acceleration` depends on the terminal's ability to pass high-frequency scroll events to the application.

| Terminal | Support Level | Notes |
| :--- | :--- | :--- |
| **iTerm2** | 🟢 Full | Best-in-class event pass-through. |
| **Kitty** | 🟢 Full | Highly efficient; native support for acceleration. |
| **Zed** | 🟢 High | Recent updates (v0.221.0+) specifically fixed fast-scrolling issues. |
| **VS Code** | 🟡 Partial | Depends on the integrated terminal's handling of mouse wheel events. |
| **Alacritty** | 🟢 Full | Low-latency event delivery. |

## 4. Sovereign UI Recommendations

To elevate the OpenCode TUI from a "tool" to a "Sovereign Interface," the following combined configuration is recommended for the Omega Engine:

```json
{
  "$schema": "https://opencode.ai/tui.json",
  "scroll_acceleration": {
    "enabled": true
  },
  "scroll_speed": 3,
  "mouse": true,
  "leader_timeout": 1500,
  "diff_style": "auto"
}
```

**Rationale**:
- **`leader_timeout: 1500`**: Reduces the perceived lag between the leader key and the command, making the interface feel more responsive to the Architect's will.
- **`diff_style: "auto"`**: Ensures that architectural diffs are readable regardless of the terminal window size.

## 5. Conclusion
Enabling `scroll_acceleration` is a zero-cost performance win. It removes a significant point of friction in the user experience, allowing the Architect to glide through vast amounts of intelligence without the cognitive load of "stepped" navigation.
