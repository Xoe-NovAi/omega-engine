# 🔱 OpenCode Zen Model Status — ICS Model Detection Reference

⬡ OMEGA ⬡ SOPHIA ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_strategic ⬡ ICS-REPORT  
**Date**: 2026-05-19  
**Purpose**: Feed the ICS Dynamic Header middleware with live model detection data  

---

## Current Model Configuration

| Source | Key | Value |
|--------|-----|-------|
| `~/.config/opencode/opencode.json` | `model` | `"big-pickle"` |
| Local `opencode.json` | `model` | (not set — inherits from global) |
| Environment variable | `OPENCODE_MODEL` | (not set — detected via config merge) |

## What "big-pickle" Means

OpenCode uses `big-pickle` as a provider-agnostic model alias. The actual serving model is determined by:
1. The `model` key in the merged config (global → local override)
2. The currently loaded OpenCode subagent/mode
3. The active provider chain in `config/providers.yaml`

## ICS Integration Strategy

The ICS `_build_dynamic_header()` method should:

```python
def _detect_model(self) -> str:
    """Detect the currently active model."""
    # Priority 1: OpenCode env var
    model = os.environ.get("OPENCODE_MODEL", "")
    if model:
        return model
    # Priority 2: Global opencode.json model key
    try:
        global_config = Path.home() / ".config" / "opencode" / "opencode.json"
        if global_config.exists():
            import json
            data = json.loads(global_config.read_text())
            if "model" in data:
                return data["model"]
    except Exception:
        pass
    # Priority 3: TriageRouter's last selection
    if hasattr(self, 'triage_router') and self.triage_router.last_selected_model:
        return self.triage_router.last_selected_model
    # Fallback
    return "unknown"
```

## Available OpenCode Models

OpenCode Zen supports multi-provider routing. The currently configured models are:

| Provider | Models Available | Free Tier |
|----------|-----------------|-----------|
| OpenCode Zen | `deepseek-v4-flash-free`, `qwen3.6-plus-free`, `minimax-m2.5-free` | ✅ Yes |
| Google AI Studio | `gemma-4-31b-it`, `gemma-4-26b-a4b-it` | ✅ Yes (limited) |
| OpenRouter | 356 models (28 free) | ❌ No (free tier rate-limited) |
| lmster (local) | Any loaded GGUF | ✅ Yes (local) |
| Ollama (local) | Any pulled model | ✅ Yes (local) |

## Current Session

This session is running on **DeepSeek V4 Flash** via OpenCode Zen's free tier. That's what `big-pickle` resolves to at the moment.

---

*Reference document for the ICS Dynamic Header implementation. Gemma to integrate into `_build_dynamic_header()` during the ICS middleware build.*
