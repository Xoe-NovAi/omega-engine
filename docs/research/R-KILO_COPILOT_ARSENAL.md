# 🔱 Omega Engine — Copilot & Kilo Arsenal
**AP Token**: `AP-ARSENAL-v1.0.0`
**Status**: ACTIVE | **Last Updated**: 2026-05-17

## ⬡ The Discovery
Through the discovery of the Kilo CLI and the GitHub Copilot free-tier integration, the Omega Engine has expanded its inference reach. We have moved from a restricted set of providers to a comprehensive frontier access layer.

## 📊 Model Tiering Strategy

### T1: Reflex (Low Latency / Syntax / Guard)
| Model | Provider | Role |
| :--- | :--- | :--- |
| `claude-haiku-4.5` | GitHub Copilot | Primary Reflex / Fast Iteration |
| `gpt-5-mini` | GitHub Copilot | Logic-heavy Reflex |
| `deepseek-v4-flash:free` | Kilo | High-speed reasoning fallback |

### T2: Reason (Implementation / Feature Work)
| Model | Provider | Role |
| :--- | :--- | :--- |
| `gpt-4.1` | GitHub Copilot | Stable implementation |
| `gpt-4o` | GitHub Copilot | Multimodal / General Reason |
| `qwen3-coder-plus` | Kilo | Advanced Coding Logic |

### T3: Gnosis (Architecture / Synthesis / Audit)
| Model | Provider | Role |
| :--- | :--- | :--- |
| `claude-opus-4.6` | Kilo | Strategic Oversight / Logic Audit |
| `gpt-5.4-pro` | Kilo | Maximum Reasoning / Complex Synthesis |
| `qwen3-max-thinking` | Kilo | Deep Chain-of-Thought Research |

## 🛠️ Integration Path
1. **Copilot**: Routed via the OpenCode-Copilot bridge.
2. **Kilo**: Routed via the `kilo` CLI wrapper (TUI/Headless).
3. **GenLabs**: Routed via REST API (`api.genlabs.ai`).

## 🛡️ Sovereign Guard Note
All these models are "Remote". The Omega Engine remains **Local-First**. These providers are treated as high-capability extensions of the core runtime. All session data is persisted locally in `data/sessions/`, ensuring that while the reasoning is remote, the memory is sovereign.
