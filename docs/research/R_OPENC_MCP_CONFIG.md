# OpenCode MCP Configuration Guide

## 🛠️ MCP Server Types

OpenCode supports two primary transport types for Model Context Protocol (MCP) servers:

| Type | Transport | Configuration Requirements | Use Case |
| :--- | :--- | :--- | :--- |
| **`stdio`** | **Standard I/O** | `command` (required), `args` (optional), `env` (optional) | Local binaries or scripts (e.g., `npx`, `python`, `node`). This is the **default type**. |
| **`sse`** | **HTTP/SSE** | `url` (required), `headers` (optional) | Servers running as network services or remote APIs. |

*Note: While some third-party integrations mention `type: local` or `type: remote`, these are typically aliases or part of specialized schemas. For the standard `opencode.json` configuration, use `stdio` for local processes and `sse` for network endpoints.*

---

## 🔄 Configuration Merging & Precedence

OpenCode employs a layered configuration system that merges settings from multiple sources.

### 1. Precedence Order
Settings are applied in the following order (later sources **override** earlier ones):
**Built-in Defaults** $\rightarrow$ **Global Config** $\rightarrow$ **Environment Variables** $\rightarrow$ **Project Config** $\rightarrow$ **CLI Flags**

### 2. File Locations
* **Global Configuration:** `~/.config/opencode/opencode.json` (or `~/.opencode.json`). Used for user-wide preferences and general-purpose tools.
* **Project Configuration:** `opencode.json` in the current project root. Used for project-specific tools and overrides.

### 3. Merge Behavior
OpenCode performs a **deep merge** of the configuration objects:
* **Additive Merge**: If a setting (e.g., `autoupdate`) exists in the global config but not the local one, it is preserved in the final runtime configuration.
* **Conflict Resolution**: If the same key exists in both, the **Project Config (local) takes precedence**.
* **MCP Server Merging**: The `mcpServers` map is merged by server name:
    * **Unique Names**: Servers defined only in global or only in local are all loaded.
    * **Overlapping Names**: If a server name (e.g., `"filesystem"`) exists in both, the **local configuration completely overrides** the global definition for that specific server.

---

## 📖 Definitive Configuration Example

To have a global "Memory" server and a project-specific "Database" server (while overriding a global "Filesystem" server), use the following:

**Global (`~/.config/opencode/opencode.json`):**
```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "type": "stdio"
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/global-docs"],
      "type": "stdio"
    }
  }
}
```

**Project (`./opencode.json`):**
```json
{
  "mcpServers": {
    "database": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/db"],
      "type": "stdio"
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "./src"],
      "type": "stdio"
    }
  }
}
```

**Final Resulting Runtime Config:**
* ✅ `memory`: Loaded from **Global**.
* ✅ `database`: Loaded from **Local**.
* ✅ `filesystem`: Loaded from **Local** (overriding the Global path).
