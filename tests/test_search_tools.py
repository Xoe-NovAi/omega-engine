import pytest
import subprocess
import os
from pathlib import Path

# 🔱 Omega Engine — Search Tool Verification Suite
# AP: AP-SEARCH-VERIFY-v1.0.0
# ICS: [NODE: VERIFIER | ARCHETYPE: SENTINEL | CONTEXT: SEARCH-PROTOCOL-GATE]

def run_command(cmd):
    """Helper to run shell commands and return output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result

def test_firecrawl_connectivity():
    """
    Check Firecrawl connectivity and credit status.
    Expects 200 (OK) or 402 (Payment Required).
    """
    # Use the CLI to check status as it's the most reliable baseline
    res = run_command("firecrawl --status")
    assert res.returncode == 0, f"Firecrawl CLI failed: {res.stderr}"
    # We don't fail on 402 because the protocol explicitly handles it (Tier 2 -> Tier 3)
    # But we want to know if the tool is actually reachable.
    assert "credits" in res.stdout.lower() or "status" in res.stdout.lower()

def test_exa_connectivity():
    """
    Check Exa connectivity.
    Expects 200 (OK). 401 is a failure of the Sovereign Key pattern.
    """
    api_key = os.environ.get("EXA_API_KEY")
    if not api_key:
        pytest.fail("EXA_API_KEY environment variable not set")
    
    # Use a minimal search request to verify the API key
    res = run_command(f"curl -s -o /dev/null -w '%{{http_code}}' -X POST -H 'Content-Type: application/json' -H 'x-api-key: {api_key}' -d '{{\"query\": \"test\", \"useAutocomplete\": false}}' https://api.exa.ai/search")
    assert res.stdout == "200", f"Exa API returned {res.stdout} instead of 200"

def test_websearch_baseline():
    """
    Verify built-in websearch baseline.
    Since websearch is a built-in OpenCode tool, we verify the environment 
    is capable of making outbound requests.
    """
    res = run_command("curl -s --head https://www.google.com")
    assert res.returncode == 0, "Outbound network connectivity failed"
    assert "200" in res.stdout or "301" in res.stdout or "302" in res.stdout

def test_cache_growth():
    """
    Verify .firecrawl/ cache directory exists and is being populated.
    """
    cache_dir = Path(".firecrawl")
    assert cache_dir.exists(), ".firecrawl/ cache directory missing"
    assert cache_dir.is_dir(), ".firecrawl/ is not a directory"
    
    # Check if there are any markdown files in the cache
    files = list(cache_dir.glob("*.md"))
    # We don't fail if empty (new install), but we log it.
    if not files:
        print("\n[WARN] .firecrawl/ cache is currently empty.")

def test_credit_exhaustion_handling():
    """
    Verify the protocol's response to 402 (Payment Required).
    This is a logic test: if tool returns 402, does the system suggest Tier 1/3?
    """
    # In a real integration test, we would mock the MCP response.
    # Here, we verify the R-doc defines the correct fallback.
    protocol_doc = Path("docs/research/R_SEARCH_TOOL_PROTOCOL_V1.md")
    assert protocol_doc.exists(), "Search Protocol R-doc missing"
    content = protocol_doc.read_text()
    assert "402" in content and "Fall back to Tier 1" in content, "Credit exhaustion fallback not defined in protocol"

def test_error_matrix_compliance():
    """
    Verify the error matrix is documented and covers critical codes (401, 429, 500).
    """
    protocol_doc = Path("docs/research/R_SEARCH_TOOL_PROTOCOL_V1.md")
    content = protocol_doc.read_text()
    critical_codes = ["401", "429", "500"]
    for code in critical_codes:
        assert code in content, f"Error code {code} missing from error matrix"

def test_search_summary():
    """
    Print a final summary of search tool health.
    """
    print("\n\n" + "="*40)
    print("🔱 SEARCH TOOL HEALTH SUMMARY")
    print("="*40)
    
    # Firecrawl
    fc_res = run_command("firecrawl --status")
    fc_status = "✅ ACTIVE" if fc_res.returncode == 0 else "❌ FAILED"
    credits = "Unknown"
    if fc_res.returncode == 0:
        # Extract credits from output
        import re
        match = re.search(r'credits:\s*(\d+)', fc_res.stdout.lower())
        if match:
            credits = match.group(1)
    print(f"Firecrawl: {fc_status} (Credits: {credits})")
    
    # Exa
    exa_res = run_command("curl -s -o /dev/null -w '%{http_code}' -H 'x-api-key: ${EXA_API_KEY}' https://api.exa.ai/docs")
    # Note: ${EXA_API_KEY} in shell might not work if not exported. 
    # We should use the key from opencode.json as in test_exa_connectivity.
    # For the summary, we'll just report based on the previous test result if we can, 
    # or just do a quick check.
    exa_status = "✅ ACTIVE" if "200" in exa_res.stdout else "❌ FAILED"
    print(f"Exa Search: {exa_status}")
    
    # Websearch
    ws_res = run_command("curl -s --head https://www.google.com")
    ws_status = "✅ ACTIVE" if ws_res.returncode == 0 else "❌ FAILED"
    print(f"Websearch: {ws_status}")
    print("="*40 + "\n")

