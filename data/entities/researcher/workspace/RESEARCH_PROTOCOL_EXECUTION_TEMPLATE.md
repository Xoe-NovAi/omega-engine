# 🔱 Research Protocol Execution Template
# Copy this for every research session. Fill as you go.

## Model Profile
Model: {model_name} | Context: {size} | Depth: {fast/deep/iterative} | Tool Fidelity: {high/med/low}

## Pre-Flight (Phase 0)
- [ ] Model profile loaded
- [ ] Hivemind posted: intent=research, topic={topic}
- [ ] Workspace lock acquired: research_{topic}
- [ ] Cache checked: .firecrawl/ hits? {yes/no}
- [ ] Library searched: existing docs? {yes/no}
- [ ] Queue entry read: depth={1/2/3}, expected_output={type}
- [ ] Tools verified: {at least 2 from exa, firecrawl, native, library}

## Discovery Pass (Phase 1)
### Pass 1 — Broad
| Tool | Query | Results | Key Insight |
|------|-------|---------|-------------|
| {tool} | {query} | {count} | {insight} |
| {tool} | {query} | {count} | {insight} |

### Pass 2 — Deepen
| Tool | Query | Results | Key Insight |
|------|-------|---------|-------------|
| {tool} | {query} | {count} | {insight} |
| {tool} | {query} | {count} | {insight} |

## Synthesis Evidence Table
| Source | Core Claim | Code Location | Confidence | Counter-Evidence |
|--------|------------|---------------|------------|------------------|
| {url} | {claim} | {file:line} | {strong/medium/weak} | {contradiction?} |

## Gates (Phase 4)
- [ ] S1: ≥2 tool families used
- [ ] S2: Code locations mapped (file:line)
- [ ] S3: Counter-evidence searched
- [ ] S4: R-doc written to disk at {path}
- [ ] S5: No tool drift detected

## Shadow Protocol (§4)
- [ ] Adversarial review: "What would a harsh reviewer say?"
- [ ] Red flag audit: "may be", "state-of-the-art", "simple", "just"
- [ ] Heritage considered: Does this map to an [id-soft:] pattern?

## Closure
- [ ] Queue marked [x]: {queue_file}
- [ ] Live feed updated: {feed_path}
- [ ] Soul.yaml L1→L2→L3 appended
- [ ] Hivemind completion posted
