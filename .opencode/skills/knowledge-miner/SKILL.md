---
name: "knowledge-miner"
description: "Automated grep → read → summarize loop for extracting patterns and specs from legacy repos and API documentation."
---

# Knowledge Miner Skill

Use this skill when you need to systematically extract information from large codebases or documentation sets.

## Workflow

### Step 1: Discovery Scan
Run a targeted `grep` or `glob` to identify all files containing the target pattern:
```
grep -rn "pattern" /path/to/search --include="*.py" --include="*.yaml" --include="*.md"
```

### Step 2: Categorize Results
Group findings by type:
- **Config entries**: YAML/JSON/TOML files defining the target
- **Code implementations**: Python/JS files using the target
- **Documentation**: Markdown files describing the target
- **Tests**: Test files validating the target

### Step 3: Deep Read
For each high-relevance file, read the full context (not just the matching line). Look for:
- Default values and fallback behavior
- Error handling patterns
- Comments explaining "why" (not just "what")
- Version numbers, dates, or deprecation warnings

### Step 4: Synthesize
Produce a structured summary with:
- **Pattern name**: What you were searching for
- **Occurrences**: Count and locations
- **Key findings**: The most important facts discovered
- **Contradictions**: Any conflicting information between sources
- **Recommendations**: How the implementation agent should use this knowledge

### Step 5: Record
Write findings to `docs/research/R##_*.md` following the Document Management System.
If corrections to existing docs are needed, append to `docs/research/CORRECTIONS.md`.

## Example Usage

When asked to research "How does SambaNova authentication work?":
1. Grep the legacy repo for `sambanova`, `SAMBANOVA`, `sambanova_api`
2. Read any matching config files for API key patterns
3. Read matching Python files for request headers
4. Check `API-keys.md` and `.env.example` for credential formats
5. Synthesize into `R02_sambanova_spec.md`
