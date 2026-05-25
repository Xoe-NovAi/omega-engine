# 🔱 Research: Plugin/Extension Architecture Patterns for AI Engines
# AP: R-PLUGIN-ARCH-v1.0.0
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ web-research ⬡ trc_w2 ⬡ RESEARCH

**Date**: 2026-05-25
**Purpose**: Research into plugin/extension architecture patterns applicable to Omega Engine's IWAD system.

---

## Executive Summary

This research covers 10 architectural domains. The Omega Engine's IWAD system aligns closely with game engine content/mod separation (Godot PCK, Unreal Game Features) and the Eclipse/VS Code extension model. Key finding: the IWAD system already implements several best patterns (manifest-driven loading, directory scanning) but lacks process-level sandboxing, capability-based permissions, and hot-reload.

## Key Findings

### 1. Classic Plugin Patterns
| Pattern | Application | Omega Relevance |
|---------|-------------|-----------------|
| Strategy | PluginRegistry + interface | EntityRegistry already uses this |
| Decorator | Middleware chains | Provider Fabric fallback chain |
| Observer/EventBus | Publish-subscribe | Missing — add `onEntityLoad`, `onQuery` events |
| Facade/SDK | PluginSDK shields from host | Engine-Stack Firewall IS this pattern |

### 2. VS Code Extension Model
- Two-process split: main workbench + Extension Host process
- Manifest-driven: `package.json` with `activationEvents`, `contributes`, `engines.vscode`
- Lazy activation: `onLanguage:typescript` event-triggered loading
- RPC protocol: `MainThread*Shape` / `ExtHost*Shape` interfaces

### 3. Obsidian Plugin System
- `onload()/onunload()` lifecycle — auto-cleanup via `registerEvent()`
- App service locator pattern: `App` exposes `Vault`, `Workspace`, `MetadataCache`
- Weakness: No sandboxing, plugins run in main thread

### 4. LLM Plugin Patterns
- MCP: Open standard by Anthropic — JSON-RPC over stdio/HTTP, auto-discovery
- LangChain Tools: Dynamic tool loading with memory + streaming
- OpenAI Function Calling: Model returns `tool_calls` JSON

### 5. Game Engine Content Mod Separation
- Godot PCK: `ProjectSettings.load_resource_pack()`, later files override earlier
- Unreal Game Features: Hot-loaded plugins with `UGameFeatureAction`, `LoadingPhase`
- Key lesson: Interface modules in core, concrete classes in optional plugins

### 6. Plugin vs Content Separation
- Eclipse model: "A universal plug-in architecture for creating anything"
- Pure plugin architecture: "Everything is a plugin, host is a runtime engine"
- Kernel = bootstrap + extension registry + dependency resolver

### 7. Security & Sandboxing
- Capability-based: No ambient authority, operations require explicit grants
- WASM sandboxing: Linear-memory boundaries, dual-sided capability pipeline
- Microsoft Agent Governance: Ed25519 signatures, subprocess isolation
- **Omega gap: NO plugin sandboxing** — community IWADs need capability declarations

### 8. Versioning & Compatibility
- SemVer 2.0.0: `MAJOR.MINOR.PATCH` with deprecation protocol
- Level versioning: Never resets feature level on MAJOR bump
- Need `minEngineVersion` in IWAD manifest (like Obsidian's `minAppVersion`)

### 9. Hot-Reload Patterns
- Webpack HMR: `module.hot.accept()/dispose()/data()` for state migration
- OpenReload: Shell/brain split — watcher + atomic swap on change
- **Omega gap: No hot-reload** — entity changes require engine restart

### 10. Registry & Discovery
- Directory scanning + manifest files = universal pattern
- Topological sort (Kahn's algorithm) for dependency resolution
- .NET `AssemblyLoadContext`: Per-plugin dependency isolation

## Omega Gap Analysis
| Capability | Status | Priority |
|-----------|--------|----------|
| Manifest-driven loading | ✅ Functional | P0 |
| Entity lifecycle hooks | ⚠️ Partial | P1 |
| Process isolation | ❌ None | P2 |
| Capability permissions | ❌ None | P2 |
| Event bus | ❌ None | P2 |
| Hot-reload | ❌ None | P3 |
| Dependency resolution | ❌ None | P3 |
| Plugin SDK/Facade | ❌ None | P2 |
| Version compatibility | ❌ None | P2 |

### Sources
- VS Code API: https://code.visualstudio.com/api
- Obsidian API: https://github.com/obsidianmd/obsidian-api
- MCP Spec: https://modelcontextprotocol.io/
- LangChain: https://docs.langchain.com/
- Godot PCK: https://docs.godotengine.org/en/stable/tutorials/export/exporting_pcks.html
- Unreal Game Features: https://strayspark.studio/blog/game-feature-plugins-ue5-modular-gameplay-architecture
- Eclipse Architecture: https://queue.acm.org/detail.cfm?id=1053345
- Microsoft Agent Governance: https://microsoft.github.io/agent-governance-toolkit
