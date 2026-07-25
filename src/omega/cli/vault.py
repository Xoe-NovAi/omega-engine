# ⬡ OMEGA ⬡ MAAT ⬡ VAULT_CLI ⬡ v2.0.0 ⬡ 2026-07-25
"""
CLI commands for VaultCore operations.

Commands:
- omega vault set <provider> <key_id> <cred_type> <value>  Store a credential
- omega vault get <provider> <key_id>                       Retrieve a credential
- omega vault list [--provider PROVIDER]                    List all credential keys
- omega vault rotate <provider> <key_id> <value>            Rotate a credential
- omega vault delete <provider> <key_id>                    Delete a credential
- omega vault audit [--limit N]                             Show audit log
- omega vault audit-summary [--days N]                      Show audit summary
- omega vault verify                                        Verify vault integrity
- omega vault init                                          Initialize a new vault
- omega vault backup <output>                               Create encrypted backup
- omega vault restore <input>                               Restore from backup
- omega vault recovery-code                                 Show recovery code
- omega vault rotate-master                                 Rotate master password
"""

import anyio
import click
import json
from pathlib import Path
from typing import Optional

from src.omega.vault.vault_core import (
    VaultCore, VaultCredential, ProviderName, CredentialType, 
    CredentialTier, CredentialStatus, VaultCoreError
)


@click.group()
def vault():
    """Sovereign credential vault operations."""
    pass


def _get_vault(passphrase: str, vault_dir: Path) -> VaultCore:
    """Create VaultCore instance."""
    return VaultCore(vault_dir, passphrase)


@vault.command()
@click.argument("provider", type=click.Choice([p.value for p in ProviderName]))
@click.argument("key_id")
@click.argument("cred_type", type=click.Choice([c.value for c in CredentialType]))
@click.argument("value")
@click.option("--tier", type=click.Choice([t.value for t in CredentialTier]), default="free", help="Credential tier")
@click.option("--daily-limit", default=0, type=int, help="Daily usage limit (0 = unlimited)")
@click.option("--passphrase", envvar="OMEGA_VAULT_PASSPHRASE", prompt=True, hide_input=True, help="Vault passphrase")
@click.option("--vault-dir", default="~/.config/omega/vault", type=click.Path(path_type=Path), help="Vault directory")
def set(provider: str, key_id: str, cred_type: str, value: str, tier: str, daily_limit: int, passphrase: str, vault_dir: Path):
    """Store a credential."""
    async def _set():
        vault = _get_vault(passphrase, vault_dir)
        cred = VaultCredential(
            provider=ProviderName(provider),
            key_id=key_id,
            cred_type=CredentialType(cred_type),
            encrypted_blob=value,  # Will be encrypted by store_credential
            tier=CredentialTier(tier),
            daily_limit=daily_limit,
        )
        await vault.store_credential(cred)
        click.echo(f"Stored: {provider}:{key_id}")
    anyio.run(_set)


@vault.command()
@click.argument("provider", type=click.Choice([p.value for p in ProviderName]))
@click.argument("key_id")
@click.option("--passphrase", envvar="OMEGA_VAULT_PASSPHRASE", prompt=True, hide_input=True, help="Vault passphrase")
@click.option("--vault-dir", default="~/.config/omega/vault", type=click.Path(path_type=Path), help="Vault directory")
def get(provider: str, key_id: str, passphrase: str, vault_dir: Path):
    """Retrieve and decrypt a credential."""
    async def _get():
        vault = _get_vault(passphrase, vault_dir)
        try:
            decrypted = await vault.decrypt_credential(ProviderName(provider), key_id)
            click.echo(json.dumps(decrypted, indent=2))
        except VaultCoreError as e:
            click.echo(f"Error: {e}", err=True)
            raise click.Abort()
    anyio.run(_get)


@vault.command()
@click.option("--provider", type=click.Choice([p.value for p in ProviderName]), help="Filter by provider")
@click.option("--passphrase", envvar="OMEGA_VAULT_PASSPHRASE", prompt=True, hide_input=True, help="Vault passphrase")
@click.option("--vault-dir", default="~/.config/omega/vault", type=click.Path(path_type=Path), help="Vault directory")
def list(provider: Optional[str], passphrase: str, vault_dir: Path):
    """List all credential keys."""
    async def _list():
        vault = _get_vault(passphrase, vault_dir)
        prov = ProviderName(provider) if provider else None
        creds = await vault.list_credentials(prov)
        for c in creds:
            click.echo(f"{c.provider.value}:{c.key_id}  [{c.cred_type.value}]  tier={c.tier.value}  status={c.status.value}  used={c.used_today}/{c.daily_limit}")
    anyio.run(_list)


@vault.command()
@click.argument("provider", type=click.Choice([p.value for p in ProviderName]))
@click.argument("key_id")
@click.argument("value")
@click.option("--passphrase", envvar="OMEGA_VAULT_PASSPHRASE", prompt=True, hide_input=True, help="Vault passphrase")
@click.option("--vault-dir", default="~/.config/omega/vault", type=click.Path(path_type=Path), help="Vault directory")
def rotate(provider: str, key_id: str, value: str, passphrase: str, vault_dir: Path):
    """Rotate a credential (overwrite with new value)."""
    async def _rotate():
        vault = _get_vault(passphrase, vault_dir)
        # Get existing credential
        cred = await vault.get_credential(ProviderName(provider), key_id)
        # Update encrypted blob
        cred.encrypted_blob = value
        cred.rotation_count += 1
        cred.rotated_at = __import__('datetime').datetime.now(__import__('datetime').timezone.utc)
        await vault.store_credential(cred)
        click.echo(f"Rotated: {provider}:{key_id} (rotation #{cred.rotation_count})")
    anyio.run(_rotate)


@vault.command()
@click.argument("provider", type=click.Choice([p.value for p in ProviderName]))
@click.argument("key_id")
@click.option("--passphrase", envvar="OMEGA_VAULT_PASSPHRASE", prompt=True, hide_input=True, help="Vault passphrase")
@click.option("--vault-dir", default="~/.config/omega/vault", type=click.Path(path_type=Path), help="Vault directory")
def delete(provider: str, key_id: str, passphrase: str, vault_dir: Path):
    """Delete a credential."""
    async def _delete():
        vault = _get_vault(passphrase, vault_dir)
        ref = f"{provider}:{key_id}"
        if ref in vault._credentials:
            del vault._credentials[ref]
            await vault._save_credentials()
            await vault._audit("delete", ref, True)
            click.echo(f"Deleted: {ref}")
        else:
            click.echo(f"Key not found: {ref}", err=True)
            raise click.Abort()
    anyio.run(_delete)


@vault.command()
@click.option("--limit", default=100, type=int, help="Number of entries to show")
@click.option("--passphrase", envvar="OMEGA_VAULT_PASSPHRASE", prompt=True, hide_input=True, help="Vault passphrase")
@click.option("--vault-dir", default="~/.config/omega/vault", type=click.Path(path_type=Path), help="Vault directory")
def audit(limit: int, passphrase: str, vault_dir: Path):
    """Show audit log entries."""
    async def _audit():
        vault = _get_vault(passphrase, vault_dir)
        if not vault.audit_log.exists():
            click.echo("No audit log found")
            return
        content = vault.audit_log.read_text()
        lines = content.strip().split("\n")
        for line in lines[-limit:]:
            if line:
                entry = json.loads(line)
                status = "✓" if entry["success"] else "✗"
                error = f" ({entry['details']})" if entry.get("details") else ""
                click.echo(f"{entry['timestamp']} {status} {entry['action']} {entry['credential_ref']}{error}")
    anyio.run(_audit)


@vault.command()
@click.option("--days", default=7, type=int, help="Number of days to summarize")
@click.option("--passphrase", envvar="OMEGA_VAULT_PASSPHRASE", prompt=True, hide_input=True, help="Vault passphrase")
@click.option("--vault-dir", default="~/.config/omega/vault", type=click.Path(path_type=Path), help="Vault directory")
def audit_summary(days: int, passphrase: str, vault_dir: Path):
    """Show audit summary for the last N days."""
    async def _audit_summary():
        vault = _get_vault(passphrase, vault_dir)
        if not vault.audit_log.exists():
            click.echo("No audit log found")
            return
        
        import datetime
        cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days)
        
        actions = {}
        credentials = {}
        success_count = 0
        fail_count = 0
        
        content = vault.audit_log.read_text()
        for line in content.strip().split("\n"):
            if not line:
                continue
            entry = json.loads(line)
            ts = datetime.datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
            if ts < cutoff:
                continue
            
            action = entry["action"]
            actions[action] = actions.get(action, 0) + 1
            
            cred_ref = entry["credential_ref"]
            credentials[cred_ref] = credentials.get(cred_ref, 0) + 1
            
            if entry["success"]:
                success_count += 1
            else:
                fail_count += 1
        
        click.echo(f"\n=== Audit Summary (Last {days} days) ===")
        click.echo(f"Total operations: {success_count + fail_count}")
        click.echo(f"Successful: {success_count}")
        click.echo(f"Failed: {fail_count}")
        click.echo(f"\nBy Action:")
        for action, count in sorted(actions.items(), key=lambda x: -x[1]):
            click.echo(f"  {action}: {count}")
        click.echo(f"\nBy Credential:")
        for cred, count in sorted(credentials.items(), key=lambda x: -x[1])[:20]:
            click.echo(f"  {cred}: {count}")
    anyio.run(_audit_summary)


@vault.command()
@click.option("--passphrase", envvar="OMEGA_VAULT_PASSPHRASE", prompt=True, hide_input=True, help="Vault passphrase")
@click.option("--vault-dir", default="~/.config/omega/vault", type=click.Path(path_type=Path), help="Vault directory")
def verify(passphrase: str, vault_dir: Path):
    """Verify vault integrity (all credentials decrypt successfully)."""
    async def _verify():
        vault = _get_vault(passphrase, vault_dir)
        results = await vault.verify_integrity()
        click.echo(f"Total: {results['total']}")
        click.echo(f"Valid: {results['valid']}")
        if results["corrupted"]:
            click.echo(f"Corrupted: {results['corrupted']}", err=True)
            raise click.Abort()
        else:
            click.echo("All credentials verified successfully.")
    anyio.run(_verify)


@vault.command()
@click.option("--passphrase", envvar="OMEGA_VAULT_PASSPHRASE", prompt=True, hide_input=True, help="Vault passphrase")
@click.option("--vault-dir", default="~/.config/omega/vault", type=click.Path(path_type=Path), help="Vault directory")
def init(passphrase: str, vault_dir: Path):
    """Initialize a new vault (generate master key)."""
    async def _init():
        vault = _get_vault(passphrase, vault_dir)
        # Just loading the vault initializes it
        click.echo(f"Vault initialized at {vault_dir}")
        click.echo(f"Recovery code: {vault.get_recovery_code()}")
    anyio.run(_init)


@vault.command()
@click.argument("output", type=click.Path(path_type=Path))
@click.option("--passphrase", envvar="OMEGA_VAULT_PASSPHRASE", prompt=True, hide_input=True, help="Vault passphrase")
@click.option("--vault-dir", default="~/.config/omega/vault", type=click.Path(path_type=Path), help="Vault directory")
def backup(output: Path, passphrase: str, vault_dir: Path):
    """Create encrypted backup of vault."""
    async def _backup():
        vault = _get_vault(passphrase, vault_dir)
        
        # Create backup data
        backup_data = {
            "version": 2,
            "timestamp": __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
            "credentials": {ref: cred.to_dict() for ref, cred in vault._credentials.items()},
            "leases": {lid: lease.to_dict() for lid, lease in vault._leases.items()},
        }
        
        # Encrypt with master password
        backup_json = json.dumps(backup_data, indent=2)
        encrypted = vault.age.encrypt(backup_json)
        
        # Write backup
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encrypted)
        output.chmod(0o600)
        
        click.echo(f"Backup created: {output}")
        click.echo(f"Credentials: {len(backup_data['credentials'])}")
        click.echo(f"Leases: {len(backup_data['leases'])}")
    anyio.run(_backup)


@vault.command()
@click.argument("input", type=click.Path(exists=True, path_type=Path))
@click.option("--passphrase", envvar="OMEGA_VAULT_PASSPHRASE", prompt=True, hide_input=True, help="Vault passphrase")
@click.option("--vault-dir", default="~/.config/omega/vault", type=click.Path(path_type=Path), help="Vault directory")
def restore(input: Path, passphrase: str, vault_dir: Path):
    """Restore vault from encrypted backup."""
    async def _restore():
        vault = _get_vault(passphrase, vault_dir)
        
        # Read and decrypt backup
        encrypted = input.read_text()
        try:
            backup_json = vault.age.decrypt(encrypted)
        except Exception as e:
            click.echo(f"Failed to decrypt backup: {e}", err=True)
            raise click.Abort()
        
        backup_data = json.loads(backup_json)
        
        if backup_data.get("version", 1) != 2:
            click.echo("Unsupported backup version", err=True)
            raise click.Abort()
        
        # Restore credentials
        for ref, cred_data in backup_data.get("credentials", {}).items():
            vault._credentials[ref] = VaultCredential.from_dict(cred_data)
        
        # Restore leases
        for lid, lease_data in backup_data.get("leases", {}).items():
            lease = __import__('src.omega.vault.vault_core', fromlist=['VaultLease']).VaultLease(**lease_data)
            if lease.is_valid():
                vault._leases[lid] = lease
        
        await vault._save_credentials()
        await vault._save_leases()
        
        click.echo(f"Restored from: {input}")
        click.echo(f"Credentials: {len(backup_data.get('credentials', {}))}")
        click.echo(f"Leases: {len(backup_data.get('leases', {}))}")
    anyio.run(_restore)


@vault.command()
@click.option("--passphrase", envvar="OMEGA_VAULT_PASSPHRASE", prompt=True, hide_input=True, help="Vault passphrase")
@click.option("--vault-dir", default="~/.config/omega/vault", type=click.Path(path_type=Path), help="Vault directory")
def recovery_code(passphrase: str, vault_dir: Path):
    """Show recovery code for current master password."""
    vault = _get_vault(passphrase, vault_dir)
    code = vault.get_recovery_code()
    click.echo(f"Recovery code: {code}")
    click.echo("\nStore this securely! It can restore the vault if keychain is lost.")


@vault.command()
@click.option("--passphrase", envvar="OMEGA_VAULT_PASSPHRASE", prompt=True, hide_input=True, help="Current vault passphrase")
@click.option("--vault-dir", default="~/.config/omega/vault", type=click.Path(path_type=Path), help="Vault directory")
def rotate_master(passphrase: str, vault_dir: Path):
    """Rotate master password and re-encrypt all credentials."""
    async def _rotate():
        vault = _get_vault(passphrase, vault_dir)
        new_code = await vault.rotate_master_password()
        click.echo(f"Master password rotated successfully")
        click.echo(f"New recovery code: {new_code}")
        click.echo("\nStore the new recovery code securely!")
    anyio.run(_rotate)


@vault.command()
@click.argument("code")
@click.option("--passphrase", envvar="OMEGA_VAULT_PASSPHRASE", prompt=True, hide_input=True, help="Vault passphrase (will be replaced)")
@click.option("--vault-dir", default="~/.config/omega/vault", type=click.Path(path_type=Path), help="Vault directory")
def restore_from_code(code: str, passphrase: str, vault_dir: Path):
    """Restore vault from recovery code."""
    async def _restore():
        vault = _get_vault(passphrase, vault_dir)
        await vault.restore_from_recovery_code(code)
        click.echo("Vault restored from recovery code")
    anyio.run(_restore)


@vault.command()
@click.option("--passphrase", envvar="OMEGA_VAULT_PASSPHRASE", prompt=True, hide_input=True, help="Vault passphrase")
@click.option("--vault-dir", default="~/.config/omega/vault", type=click.Path(path_type=Path), help="Vault directory")
def fleet_status(passphrase: str, vault_dir: Path):
    """Show fleet status for FleetOrchestrator monitoring."""
    vault = _get_vault(passphrase, vault_dir)
    status = vault.get_fleet_status()
    click.echo(json.dumps(status, indent=2, default=str))


@vault.command()
@click.option("--passphrase", envvar="OMEGA_VAULT_PASSPHRASE", prompt=True, hide_input=True, help="Vault passphrase")
@click.option("--vault-dir", default="~/.config/omega/vault", type=click.Path(path_type=Path), help="Vault directory")
def reconcile(passphrase: str, vault_dir: Path):
    """Run quota reconciliation with provider APIs."""
    async def _reconcile():
        vault = _get_vault(passphrase, vault_dir)
        await vault.reconcile_quotas()
        click.echo("Quota reconciliation complete")
    anyio.run(_reconcile)


@vault.command()
@click.option("--passphrase", envvar="OMEGA_VAULT_PASSPHRASE", prompt=True, hide_input=True, help="Vault passphrase")
@click.option("--vault-dir", default="~/.config/omega/vault", type=click.Path(path_type=Path), help="Vault directory")
def cleanup_leases(passphrase: str, vault_dir: Path):
    """Clean up expired leases."""
    async def _cleanup():
        vault = _get_vault(passphrase, vault_dir)
        await vault.cleanup_expired_leases()
        click.echo("Expired leases cleaned up")
    anyio.run(_cleanup)


@vault.command()
@click.argument("provider", type=click.Choice([p.value for p in ProviderName]))
@click.argument("key_id")
@click.option("--passphrase", envvar="OMEGA_VAULT_PASSPHRASE", prompt=True, hide_input=True, help="Vault passphrase")
@click.option("--vault-dir", default="~/.config/omega/vault", type=click.Path(path_type=Path), help="Vault directory")
def lease_status(provider: str, key_id: str, passphrase: str, vault_dir: Path):
    """Show lease status for a credential."""
    vault = _get_vault(passphrase, vault_dir)
    ref = f"{provider}:{key_id}"
    if ref in vault._credentials:
        cred = vault._credentials[ref]
        click.echo(f"Credential: {ref}")
        click.echo(f"  Status: {cred.status.value}")
        click.echo(f"  Leased to: {cred.current_lease_agent or 'none'}")
        click.echo(f"  Lease expires: {cred.lease_expires_at or 'never'}")
        click.echo(f"  Used today: {cred.used_today}/{cred.daily_limit}")
    else:
        click.echo(f"Credential not found: {ref}", err=True)


if __name__ == "__main__":
    vault()