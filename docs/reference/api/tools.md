# 🔱 Tools — Security & Development Utilities
**AP Token**: `AP-TOOLS-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_doc_ref ⬡ STANDARD

**Date**: 2026-10-02
**Purpose**: Reference documentation for the Tools package — security scanning and development utilities.
**Tags**: tools, security, secrets, api-keys, firecrawl, searxng
**Cross-references**: src/omega/tools/detect_api_keys.py, src/omega/tools/enforce_vaultcore.py, src/omega/tools/firecrawl_direct.py, src/omega/tools/check_hardcoded_secrets.py, src/omega/tools/searxng_direct.py

---

## Overview

The `tools` package provides **security scanning and development utilities** for the Omega Engine. These are standalone CLI tools and library functions for maintaining codebase hygiene and interacting with external services.

```
┌─────────────────────────────────────────────────────────────┐
│                      Tools Package                           │
├─────────────────────────────────────────────────────────────┤
│  detect_api_keys.py       │  Scan for API key patterns       │
│  enforce_vaultcore.py     │  Enforce VaultCore usage         │
│  firecrawl_direct.py      │  Direct Firecrawl API client     │
│  check_hardcoded_secrets.py│  Git history secret detection   │
│  searxng_direct.py        │  Direct SearXNG API client       │
└─────────────────────────────────────────────────────────────┘
```

---

## detect_api_keys.py — API Key Pattern Scanner

Scan source code for API key patterns to prevent accidental commits.

### Usage

```bash
# Scan current directory
python -m omega.tools.detect_api_keys

# Scan specific path
python -m omega.tools.detect_api_keys /path/to/scan

# Output as JSON
python -m omega.tools.detect_api_keys --json

# Exit with code 1 if keys found (for CI)
python -m omega.tools.detect_api_keys --fail-on-found
```

### Detected Patterns

| Provider | Pattern Example |
|----------|-----------------|
| OpenAI | `sk-...` |
| Anthropic | `sk-ant-...` |
| Google | `AIza...` |
| OpenRouter | `sk-or-v1-...` |
| Grok | `grok-...` |
| Generic | `api_key`, `secret`, `token` in assignments |

### Library Usage

```python
from omega.tools.detect_api_keys import scan_file, scan_directory

# Scan single file
results = scan_file("config.py")
for match in results:
    print(f"Line {match.line}: {match.pattern} = {match.value[:20]}...")

# Scan directory
results = scan_directory("src/")
```

---

## enforce_vaultcore.py — VaultCore Usage Enforcer

Ensure all credential access goes through VaultCore — no hardcoded secrets.

### Usage

```bash
# Check for direct os.environ access to secrets
python -m omega.tools.enforce_vaultcore

# Check specific files
python -m omega.tools.enforce_vaultcore src/omega/integrations/

# Fix mode (auto-replace with VaultCore calls)
python -m omega.tools.enforce_vaultcore --fix
```

### Violations Detected

| Pattern | Violation | Fix |
|---------|-----------|-----|
| `os.environ["API_KEY"]` | Direct env access | `vault.get_credential("provider:api_key")` |
| `os.getenv("SECRET")` | Direct env access | `vault.get_credential("provider:secret")` |
| `dotenv.load_dotenv()` | .env loading | Use VaultCore |

### Library Usage

```python
from omega.tools.enforce_vaultcore import check_file, check_directory, fix_file

violations = check_file("src/omega/integrations/grok_cli.py")
for v in violations:
    print(f"Line {v.line}: {v.pattern} → use VaultCore")

# Auto-fix
fix_file("src/omega/integrations/grok_cli.py")
```

---

## firecrawl_direct.py — Direct Firecrawl API Client

Minimal Firecrawl client for scraping and search without MCP overhead.

### Usage

```python
from omega.tools.firecrawl_direct import FirecrawlDirect

client = FirecrawlDirect(api_key="fc-...")

# Scrape single URL
result = await client.scrape("https://example.com")
print(result.markdown)

# Search
results = await client.search("sovereign AI 2026", limit=10)
for r in results:
    print(r.url, r.title)

# Map (crawl multiple pages)
urls = await client.map("https://docs.example.com")
```

### API

```python
class FirecrawlDirect:
    def __init__(self, api_key: str, base_url: str = "https://api.firecrawl.dev"):
        ...
    
    async def scrape(self, url: str, formats: List[str] = ["markdown"]) -> ScrapeResult:
        ...
    
    async def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        ...
    
    async def map(self, url: str, limit: int = 1000) -> List[str]:
        ...
```

---

## check_hardcoded_secrets.py — Git History Secret Detection

**Full workflow** for finding key-format strings in ALL git history (not just working tree), classifying false positives, and removing with filter-repo.

### Usage

```bash
# Scan entire git history
python -m omega.tools.check_hardcoded_secrets

# Scan specific commit range
python -m omega.tools.check_hardcoded_secrets --since "2026-01-01"

# Output findings as JSON
python -m omega.tools.check_hardcoded_secrets --json > findings.json

# Generate filter-repo script for removal
python -m omega.tools.check_hardcoded_secrets --generate-filter-repo > cleanup.sh
```

### Workflow

1. **Scan** — `git log --all --full-history --source --format=...` + regex patterns
2. **Classify** — False positive detection (test keys, examples, placeholders)
3. **Report** — JSON with commit, file, line, pattern, classification
4. **Remediate** — `git filter-repo` with paths/callbacks

### Patterns

Same as `detect_api_keys.py` plus:
- Private keys (`-----BEGIN PRIVATE KEY-----`)
- JWT tokens (`eyJ...`)
- Database URLs (`postgres://user:pass@...`)
- AWS keys (`AKIA...`)

### Library Usage

```python
from omega.tools.check_hardcoded_secrets import scan_history, classify_findings, generate_filter_repo

findings = scan_history()
classified = classify_findings(findings)
script = generate_filter_repo(classified)
```

---

## searxng_direct.py — Direct SearXNG API Client

Minimal SearXNG client for search without MCP overhead.

### Usage

```python
from omega.tools.searxng_direct import SearXNGDirect

client = SearXNGDirect(base_url="http://localhost:8017")

# Search
results = await client.search("sovereign AI", categories=["general"], engines=["google", "bing"])
for r in results:
    print(r.title, r.url, r.content[:100])

# Search with specific engines
results = await client.search("Omega Engine", engines=["github", "gitlab"])
```

### API

```python
class SearXNGDirect:
    def __init__(self, base_url: str = "http://localhost:8017"):
        ...
    
    async def search(
        self,
        query: str,
        categories: List[str] = ["general"],
        engines: Optional[List[str]] = None,
        language: str = "en",
        safe_search: int = 1,
        time_range: Optional[str] = None
    ) -> List[SearchResult]:
        ...
```

---

## Mandate Compliance

| Mandate | Compliance |
|---------|------------|
| **M1 AnyIO** | All async via `anyio` / `httpx` |
| **M2 Firewall** | Tools only; no engine logic |
| **M8 Zero Telemetry** | No external analytics |
| **M13 Temple-Grade** | Structured output; exit codes for CI |
| **M23 Failure Integrity** | Hard-stop on scan errors; no silent failures |
| **M24 Venv Sovereignty** | Deps in `.venv` |

---

## Testing

```bash
pytest tests/test_detect_api_keys.py tests/test_enforce_vaultcore.py tests/test_firecrawl_direct.py tests/test_check_hardcoded_secrets.py tests/test_searxng_direct.py -v
```

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ TOOLS-v1.0.0 ⬡ 2026-10-02 ⬡*
<!-- PROVENANCE-CORRECTED 2026-10-03T06:22:36Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

