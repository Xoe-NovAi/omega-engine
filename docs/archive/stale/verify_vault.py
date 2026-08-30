import os
from omega.vault import KeyVault

# Load from .env
with open(".env", "r") as f:
    for line in f:
        if "VAULT_MASTER_KEY=" in line:
            os.environ["VAULT_MASTER_KEY"] = line.split("=")[1].strip()

vault = KeyVault()
providers = ["exa", "firecrawl", "openrouter", "opencode_zen", "google"]
for p in providers:
    try:
        print(f"{p}: {vault.resolve(p)[:10]}...")
    except Exception as e:
        print(f"{p}: ERROR {e}")
