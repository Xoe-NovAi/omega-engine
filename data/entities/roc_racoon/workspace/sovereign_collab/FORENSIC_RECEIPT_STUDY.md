# 🔱 FORENSIC RECEIPT PATTERN STUDY — M22 Upgrade Target
**AP Token**: `AP-FORENSIC_RECEIPT_STUDY-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_forensic_receipt ⬡ PLANNING

**Date**: 2026-07-18
**Status**: PLANNING — Pattern analysis complete, implementation design pending
**Source**: `kenwalger/sovereign-sdk/packages/sovereign-core/src/sovereign_core/crypto.py`, `gateway.py`
**Target**: Upgrade M22 Response Provenance from observational → cryptographic

---

## 🎯 CURRENT M22 STATE (Observational)

```python
# Current: src/omega/observability/provenance.py
@dataclass
class GenerateResult:
    content: str
    provider_name: str  # From ACTUAL response, not config intent
    model: str
    usage: Usage
    trace_id: str
```

**Gap**: `provider_name` is logged observationally. No cryptographic proof that:
1. The response wasn't modified after generation
2. The provider name is accurate (could be spoofed in logs)
3. The token counts are authentic
4. The request→response chain is intact

---

## 🔐 KEN'S FORENSIC RECEIPT (Cryptographic)

### Core Structure (from `sovereign_core/crypto.py`)

```python
@dataclass
class ForensicReceipt:
    # The signed manifest
    metadata: dict          # Includes prose_tax_summary, runtime, py_ver, etc.
    payload_hash: str       # SHA-256 of sieved content
    timestamp: str          # UTC ISO 8601
    signature: str          # Ed25519 base64
    public_key: str         # Base64 Ed25519 public key
```

### What Is Signed (Canonical Manifest)

```json
{
  "metadata": {
    "prose_tax_summary": {
      "raw_token_count": 12,
      "optimized_token_count": 4,
      "tokens_eliminated": 8,
      "tax_savings_percentage": 66.6667,
      "total_tokens_saved": 8
    },
    "runtime": "async-sovereign-node",
    "py_ver": "3.12.x",
    "execution_success": true
  },
  "payload_hash": "4fec03e7083cca73cfb1152ae1d941b5a5a581fc725a43b3ee7df1d9ce697954",
  "timestamp": "2026-05-22T15:00:00.000000+00:00"
}
```

**Key Property**: `metadata` (including token counts) is **sealed under the same signature** as `payload_hash`. Token savings are as tamper-evident as the content hash.

### Verification (Independent, Public-Key Only)

```python
from sovereign_core.crypto import SovereignKeyManager

is_valid = SovereignKeyManager.verify_receipt(
    receipt=forensic_receipt,
    payload={"content": sieved_content},
    expected_public_key=gateway.export_public_key()
)
# Returns True/False — no private key needed
```

### Key Rotation with Auditable Succession

```python
# Rotate keypair, sign succession with OUTGOING key
receipt = manager.rotate_keypair()
# receipt contains:
# - previous_public_key
# - new_public_key
# - rotation_timestamp
# - succession_signature (signed by outgoing key)

# Verify with TRUSTED copy of previous public key (out-of-band)
is_valid = SovereignKeyManager.verify_succession(
    receipt,
    trusted_previous_public_key=previous_key_from_audit_log
)
```

---

## 🏗️ OMEGA INTEGRATION ARCHITECTURE

### New Module: `src/omega/provenance/forensic_receipt.py`

```python
"""
Cryptographic Response Provenance — M22 Upgrade
Implements ForensicReceipt pattern from sovereign-sdk.
"""

from dataclasses import dataclass
from typing import Optional
import hashlib
import json
import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
import anyio
from pathlib import Path

@dataclass
class ForensicReceipt:
    metadata: dict
    payload_hash: str
    timestamp: str
    signature: str
    public_key: str
    receipt_id: str  # UUID for indexing

@dataclass
class ProvenanceConfig:
    key_dir: Path = Path(".keys/omega_provenance")
    algorithm: str = "Ed25519"
    hash_algorithm: str = "SHA-256"

class ForensicProvenance:
    """
    Mints and verifies ForensicReceipts for every GenerateResult.
    Upgrades M22 from observational to cryptographic.
    """
    
    def __init__(self, config: ProvenanceConfig):
        self.config = config
        self._private_key: Optional[Ed25519PrivateKey] = None
        self._public_key: Optional[Ed25519PublicKey] = None
        self._key_id: Optional[str] = None
    
    async def initialize(self):
        """Load or generate Ed25519 keypair."""
        self.config.key_dir.mkdir(parents=True, exist_ok=True)
        key_path = self.config.key_dir / "identity.pem"
        
        if key_path.exists():
            pem = await anyio.to_thread.run_sync(key_path.read_bytes)
            self._private_key = serialization.load_pem_private_key(pem, password=None)
        else:
            self._private_key = Ed25519PrivateKey.generate()
            pem = self._private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            await anyio.to_thread.run_sync(key_path.write_bytes, pem)
        
        self._public_key = self._private_key.public_key()
        self._key_id = base64.b64encode(
            self._public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
        ).decode()
    
    def _canonical_manifest(self, metadata: dict, payload_hash: str, timestamp: str) -> bytes:
        """Deterministic serialization for signing."""
        manifest = {
            "metadata": metadata,
            "payload_hash": payload_hash,
            "timestamp": timestamp
        }
        # Canonical JSON: sorted keys, no whitespace
        return json.dumps(manifest, sort_keys=True, separators=(',', ':')).encode()
    
    async def mint_receipt(
        self,
        content: str,
        provider_name: str,
        model: str,
        usage: dict,
        trace_id: str,
        sieve_metadata: Optional[dict] = None
    ) -> ForensicReceipt:
        """Mint ForensicReceipt for a GenerateResult."""
        import uuid
        from datetime import datetime, timezone
        
        # Hash the exact content delivered
        payload_hash = hashlib.sha256(content.encode()).hexdigest()
        timestamp = datetime.now(timezone.utc).isoformat()
        receipt_id = str(uuid.uuid4())
        
        # Build metadata (includes M22 fields + sieve telemetry)
        metadata = {
            "provider_name": provider_name,
            "model": model,
            "usage": usage,
            "trace_id": trace_id,
            "receipt_id": receipt_id,
            "runtime": "omega-engine",
            "execution_success": True
        }
        
        if sieve_metadata:
            metadata["prose_tax_summary"] = sieve_metadata
        
        # Sign canonical manifest
        manifest_bytes = self._canonical_manifest(metadata, payload_hash, timestamp)
        signature = self._private_key.sign(manifest_bytes)
        signature_b64 = base64.b64encode(signature).decode()
        
        # Export public key
        public_key_b64 = base64.b64encode(
            self._public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
        ).decode()
        
        return ForensicReceipt(
            metadata=metadata,
            payload_hash=payload_hash,
            timestamp=timestamp,
            signature=signature_b64,
            public_key=public_key_b64,
            receipt_id=receipt_id
        )
    
    @staticmethod
    def verify_receipt(receipt: ForensicReceipt, content: str, expected_public_key: Optional[str] = None) -> bool:
        """Independent verification — public key only."""
        import base64
        import json
        import hashlib
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        from cryptography.exceptions import InvalidSignature
        
        # Recompute payload hash
        payload_hash = hashlib.sha256(content.encode()).hexdigest()
        if payload_hash != receipt.payload_hash:
            return False
        
        # Verify public key matches (if provided)
        if expected_public_key and receipt.public_key != expected_public_key:
            return False
        
        # Reconstruct manifest
        manifest = {
            "metadata": receipt.metadata,
            "payload_hash": receipt.payload_hash,
            "timestamp": receipt.timestamp
        }
        manifest_bytes = json.dumps(manifest, sort_keys=True, separators=(',', ':')).encode()
        
        # Verify signature
        try:
            public_key = Ed25519PublicKey.from_public_bytes(base64.b64decode(receipt.public_key))
            public_key.verify(base64.b64decode(receipt.signature), manifest_bytes)
            return True
        except InvalidSignature:
            return False
    
    def export_public_key(self) -> str:
        """Export base64 public key for distribution."""
        return self._key_id
    
    def export_public_key_bundle(self, node_id: str) -> dict:
        """Export signed public key bundle (self-attested)."""
        from datetime import datetime, timezone
        import uuid
        
        bundle = {
            "public_key": self._key_id,
            "node_id": node_id,
            "issued_at": datetime.now(timezone.utc).isoformat(),
            "bundle_id": str(uuid.uuid4())
        }
        
        # Self-sign the bundle
        manifest_bytes = json.dumps(bundle, sort_keys=True, separators=(',', ':')).encode()
        signature = self._private_key.sign(manifest_bytes)
        bundle["attestation"] = base64.b64encode(signature).decode()
        
        return bundle
```

---

## 🔗 INTEGRATION POINTS

### 1. ModelGateway → ForensicReceipt Minting

```python
# src/omega/model_gateway.py
from omega.provenance.forensic_receipt import ForensicProvenance

class ModelGateway:
    def __init__(self, ...):
        self.provenance = ForensicProvenance(ProvenanceConfig())
    
    async def generate(self, ...) -> GenerateResult:
        result = await self._generate(...)
        
        # Mint ForensicReceipt
        receipt = await self.provenance.mint_receipt(
            content=result.content,
            provider_name=result.provider_name,  # ACTUAL provider (M22)
            model=result.model,
            usage=result.usage,
            trace_id=result.trace_id,
            sieve_metadata=getattr(result, 'sieve_metadata', None)
        )
        
        # Attach to result
        result.forensic_receipt = receipt
        
        # Log to observability (structured)
        self.observability.log_provenance(receipt)
        
        return result
```

### 2. Observability Enhancement

```python
# src/omega/observability/provenance.py
def log_provenance(self, receipt: ForensicReceipt):
    """Structured log with cryptographic provenance."""
    self.logger.info("forensic_receipt_minted", extra={
        "receipt_id": receipt.receipt_id,
        "payload_hash": receipt.payload_hash,
        "provider_name": receipt.metadata["provider_name"],
        "model": receipt.metadata["model"],
        "trace_id": receipt.metadata["trace_id"],
        "tax_savings_pct": receipt.metadata.get("prose_tax_summary", {}).get("tax_savings_percentage"),
        "signature_valid": True  # Always true at mint time
    })
```

### 3. Verification CLI

```bash
# Verify a receipt from logs
omega provenance verify \
    --receipt-id <uuid> \
    --content "actual response text" \
    --public-key <base64>

# Batch verify from log export
omega provenance verify-batch --log-file observability.log
```

### 4. Sovereign Ledger Integration (Optional, Phase 2)

```python
# Append to sovereign-ledger (SQLite + hash chain)
from sovereign_ledger import SovereignLedger

ledger = SovereignLedger(".keys/omega_audit.db")
ledger.append_receipt(receipt.__dict__, content)

# Verify chain integrity anytime
assert ledger.verify_ledger_integrity()
```

---

## 📊 M22 UPGRADE MATRIX

| Property | Current M22 | ForensicReceipt M22+ | Gain |
|----------|-------------|---------------------|------|
| Provider authenticity | Observational log | Cryptographic (Ed25519) | **Tamper-proof** |
| Content integrity | None | SHA-256 hash sealed | **Detects modification** |
| Token count authenticity | Observational | Sealed in metadata | **FinOps audit trail** |
| Request→Response chain | Trace ID only | Signed manifest | **Non-repudiation** |
| Key compromise recovery | N/A | Succession receipts | **Auditable rotation** |
| Third-party verification | Impossible | Public key only | **Zero-trust audit** |
| Storage overhead | ~200 bytes | ~500 bytes | +300 bytes/request |

---

## 🧪 TEST PLAN

| Test | Description |
|------|-------------|
| `test_mint_receipt_basic` | Mint receipt for simple GenerateResult |
| `test_verify_receipt_valid` | Verify valid receipt with correct content |
| `test_verify_receipt_tampered_content` | Fail on content modification |
| `test_verify_receipt_tampered_metadata` | Fail on metadata modification |
| `test_verify_receipt_wrong_key` | Fail with incorrect public key |
| `test_key_rotation_succession` | Rotate keys, verify succession receipt |
| `test_integration_model_gateway` | End-to-end: generate → mint → verify |
| `test_performance_overhead` | Measure latency added per request |
| `test_concurrent_minting` | Thread-safety under load |

---

## 📋 IMPLEMENTATION CHECKLIST

- [ ] Add `cryptography` to `pyproject.toml` (already in deps for other uses)
- [ ] Create `src/omega/provenance/forensic_receipt.py`
- [ ] Add `ForensicReceipt` to `GenerateResult` dataclass
- [ ] Initialize `ForensicProvenance` in `ModelGateway.__init__`
- [ ] Mint receipt in `ModelGateway.generate()` after response
- [ ] Add observability logging for receipts
- [ ] Create `omega provenance` CLI commands
- [ ] Write contract tests (21 tests minimum)
- [ ] Benchmark overhead (target: <5ms per request)
- [ ] Document in `docs/reference/provenance.md`
- [ ] Add M22 compliance test: `test_m22_cryptographic_provenance`

---

## 🔐 THREAT MODEL

| Threat | Mitigation |
|--------|------------|
| Log tampering | Receipt signed at generation; verify against stored content |
| Provider spoofing | `provider_name` sealed in signed metadata |
| Token count inflation | `prose_tax_summary` sealed under same signature |
| Key compromise | Rotation with auditable succession receipts |
| Replay attack | `receipt_id` (UUID) + `timestamp` + `trace_id` uniqueness |
| Private key extraction | File permissions (600), consider HSM/TPM for production |

---

## 📝 NOTES

**Why Ed25519?**
- 32-byte private key, 32-byte public key, 64-byte signature
- Fast signing/verification (~100μs)
- No parameter negotiation (unlike ECDSA)
- Deterministic signatures (RFC 8032)
- Widely supported (cryptography, libsodium, Go, Rust)

**Why SHA-256?**
- 256-bit security matches Ed25519
- Fast, hardware-accelerated
- Standard for hash chains

**Key Storage**: `.keys/omega_provenance/identity.pem` (gitignored, 600 perms)
**Rotation**: Manual via CLI or automated on schedule (succession receipts preserved)

---

*⬡ OMEGA ⬡ FORENSIC_RECEIPT_STUDY v1.0 ⬡ 2026-07-18 ⬡ PLANNING*