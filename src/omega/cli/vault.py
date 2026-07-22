# ⬡ OMEGA ⬡ MAAT ⬡ VAULT_CLI ⬡ v1.0.0 ⬡ 2026-07-22
"""
CLI commands for VaultCore operations.

Commands:
- omega vault set <key> <value>     Store a credential
- omega vault get <key>             Retrieve a credential
- omega vault list                  List all credential keys
- omega vault rotate <key> <value>  Rotate a credential
- omega vault delete <key>          Delete a credential
- omega vault audit [--limit N]     Show audit log
- omega vault verify                Verify vault integrity
"""

import anyio
import click
from pathlib import Path
from typing import Optional

from src.omega.vault.vault_core import VaultCore, VaultError


@click.group()
def vault():
    """Sovereign credential vault operations."""
    pass


def _get_vault(passphrase: str, vault_dir: Path) -> VaultCore:
    """Create VaultCore instance."""
    return VaultCore(vault_dir, passphrase)


@vault.command()
@click.argument("key")
@click.argument("value")
@click.option("--passphrase", envvar="OMEGA_VAULT_PASSPHRASE", prompt=True, hide_input=True, help="Vault passphrase")
@click.option("--vault-dir", default="data/vault", type=click.Path(path_type=Path), help="Vault directory")
def set(key: str, value: str, passphrase: str, vault_dir: Path):
    """Store a credential."""
    async def _set():
        vault = _get_vault(passphrase, vault_dir)
        await vault.store(key, value)
        click.echo(f"Stored: {key}")
    anyio.run(_set)


@vault.command()
@click.argument("key")
@click.option("--passphrase", envvar="OMEGA_VAULT_PASSPHRASE", prompt=True, hide_input=True, help="Vault passphrase")
@click.option("--vault-dir", default="data/vault", type=click.Path(path_type=Path), help="Vault directory")
def get(key: str, passphrase: str, vault_dir: Path):
    """Retrieve a credential."""
    async def _get():
        vault = _get_vault(passphrase, vault_dir)
        value = await vault.retrieve(key)
        if value is None:
            click.echo(f"Key not found: {key}", err=True)
            raise click.Abort()
        click.echo(value)
    anyio.run(_get)


@vault.command()
@click.option("--passphrase", envvar="OMEGA_VAULT_PASSPHRASE", prompt=True, hide_input=True, help="Vault passphrase")
@click.option("--vault-dir", default="data/vault", type=click.Path(path_type=Path), help="Vault directory")
def list(passphrase: str, vault_dir: Path):
    """List all credential keys."""
    async def _list():
        vault = _get_vault(passphrase, vault_dir)
        keys = await vault.list_keys()
        for k in keys:
            click.echo(k)
    anyio.run(_list)


@vault.command()
@click.argument("key")
@click.argument("new_value")
@click.option("--passphrase", envvar="OMEGA_VAULT_PASSPHRASE", prompt=True, hide_input=True, help="Vault passphrase")
@click.option("--vault-dir", default="data/vault", type=click.Path(path_type=Path), help="Vault directory")
def rotate(key: str, new_value: str, passphrase: str, vault_dir: Path):
    """Rotate a credential (overwrite with new value)."""
    async def _rotate():
        vault = _get_vault(passphrase, vault_dir)
        await vault.rotate(key, new_value)
        click.echo(f"Rotated: {key}")
    anyio.run(_rotate)


@vault.command()
@click.argument("key")
@click.option("--passphrase", envvar="OMEGA_VAULT_PASSPHRASE", prompt=True, hide_input=True, help="Vault passphrase")
@click.option("--vault-dir", default="data/vault", type=click.Path(path_type=Path), help="Vault directory")
def delete(key: str, passphrase: str, vault_dir: Path):
    """Delete a credential."""
    async def _delete():
        vault = _get_vault(passphrase, vault_dir)
        deleted = await vault.delete(key)
        if deleted:
            click.echo(f"Deleted: {key}")
        else:
            click.echo(f"Key not found: {key}", err=True)
            raise click.Abort()
    anyio.run(_delete)


@vault.command()
@click.option("--limit", default=100, type=int, help="Number of entries to show")
@click.option("--passphrase", envvar="OMEGA_VAULT_PASSPHRASE", prompt=True, hide_input=True, help="Vault passphrase")
@click.option("--vault-dir", default="data/vault", type=click.Path(path_type=Path), help="Vault directory")
def audit(limit: int, passphrase: str, vault_dir: Path):
    """Show audit log entries."""
    async def _audit():
        vault = _get_vault(passphrase, vault_dir)
        entries = await vault.get_audit_log(limit)
        for entry in entries:
            status = "✓" if entry["success"] else "✗"
            error = f" ({entry['error']})" if entry.get("error") else ""
            click.echo(f"{entry['timestamp']} {status} {entry['operation']} {entry['key']}{error}")
    anyio.run(_audit)


@vault.command()
@click.option("--passphrase", envvar="OMEGA_VAULT_PASSPHRASE", prompt=True, hide_input=True, help="Vault passphrase")
@click.option("--vault-dir", default="data/vault", type=click.Path(path_type=Path), help="Vault directory")
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
@click.option("--vault-dir", default="data/vault", type=click.Path(path_type=Path), help="Vault directory")
def init(passphrase: str, vault_dir: Path):
    """Initialize a new vault (generate master key)."""
    async def _init():
        vault = VaultCore(vault_dir, passphrase)
        await vault._ensure_identity()
        click.echo(f"Vault initialized at {vault_dir}")
        click.echo(f"Master public key: {vault._recipient}")
    anyio.run(_init)