import os
from omega.vault import KeyVault

with open(".env", "r") as f:
    for line in f:
        if "VAULT_MASTER_KEY=" in line:
            os.environ["VAULT_MASTER_KEY"] = line.split("=")[1].strip()

vault = KeyVault()
providers = ["exa", "google", "openrouter", "opencode_zen"]
for p in providers:
    print(f"--- {p} ---")
    print(f"Active: {vault._data['keys'][p].get('active_account')}")
    for acc, key in vault._data['keys'][p].get('accounts', {}).items():
        print(f"  {acc}: {key[:10]}...")
