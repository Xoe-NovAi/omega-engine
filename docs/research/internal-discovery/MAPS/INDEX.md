# 🔱 Knowledge Graph Maps Index

This directory stores relationship maps and diagrams that visualize the connections between research documents, discoveries, and tools.

## Available Maps

| Map | Type | Description | Location |
|-----|------|-------------|----------|
| — | (No maps yet) | — | — |

## How to Create a Map

### Option 1: Mermaid Diagram (in Markdown)
Embed directly in any research document:
```mermaid
graph LR
    A[stack-cat] --> B[prepare_handoff]
    B --> C[Omnidroid Ω]
    C --> D[Holographic Lattice]
```

### Option 2: Graphviz DOT (for complex maps)
Save as `.gv` in this directory and render with `dot -Tpng map.gv -o map.png`.

### Option 3: Obsidian Graph Export
1. Open the `docs/` vault in Obsidian
2. Open Graph View
3. Filter by tag or path
4. Screenshot or use the `Copy Graph` plugin
