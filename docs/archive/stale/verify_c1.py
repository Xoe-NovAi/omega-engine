import asyncio
import unittest
from unittest.mock import MagicMock, patch
from src.omega.oracle.search_providers import FirecrawlProvider
from src.omega.vault import KeyVault
from omega.errors import ProviderRateLimitError

async def test_429_rotation():
    print("Testing 429 rotation for FirecrawlProvider...")
    
    # Setup Vault with rotation accounts
    vault = KeyVault()
    # Manually inject rotation data for testing
    vault._loaded = True
    vault._data["keys"]["firecrawl"] = {
        "active_account": "primary",
        "accounts": {
            "primary": "key-1",
            "secondary": "key-2"
        }
    }
    
    provider = FirecrawlProvider()
    print(f"Initial key: {provider.api_key}")
    assert provider.api_key == "key-1"

    # Mock httpx.AsyncClient.post to return 429
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_post.return_value = mock_response
        
        try:
            await provider.search("test query")
        except ProviderRateLimitError:
            print("Caught expected ProviderRateLimitError")
        except Exception as e:
            print(f"Caught unexpected exception: {type(e).__name__}: {e}")
            raise e
        
        # Verify vault was marked rate limited
        cooldown = vault._data["keys"]["firecrawl"].get("_cooldown_until", 0)
        print(f"Cooldown until: {cooldown}")
        assert cooldown > 0

    # Now create a NEW provider instance (which calls _resolve_from_vault)
    # This should trigger resolve_and_handle_429 and rotate the key
    provider_new = FirecrawlProvider()
    print(f"New provider key: {provider_new.api_key}")
    assert provider_new.api_key == "key-2"
    print("SUCCESS: Key rotated after 429!")

if __name__ == "__main__":
    asyncio.run(test_429_rotation())
