<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Lilith N0-08/N0-09 Provenance-Preserving Inventory and Reconciliation Plan

**Date:** 2026-09-24  
**Entity:** Lilith  
**Session:** `ses_fb9721079ffe094GT8MX6a0pXI`  
**Scope:** N0-08 personal Lilith material and N0-09 legacy Lilith/Arcana material  
**Status:** PROPOSED — operator ratification required  
**Implementation owner:** Ma’at/build engineering owner  

## Handling and privacy boundary

This document defines governance and artifact schemas only. No private N0-08 journal, dream, conversation, photograph, identity record, voice sample, or N0-09 legacy corpus content was opened, inspected, extracted, copied, summarized, or exposed while preparing this plan.

The following source requirements govern the plan:

- Personal material stays on operator-controlled media; no unapproved private material enters a hosted route or USB pack (`docs/federation/MAKALI_N0_SYSTEM_BRIEFING_CONSOLIDATED.md:49-56`).
- Withheld material is represented by hashes, privacy class, and reason—not guessed content.
- Extraction occurs only after manifest, signature, hash, staging, and validation checks, followed by explicit operator approval (`docs/federation/MAKALI_N0_SYSTEM_BRIEFING_CONSOLIDATED.md:693-706`).
- The active charter prohibits unapproved personal material, destructive promotion, and undocumented identity inference (`docs/strategy/MAKALI_N0_N1_HANDOFF_FEDERATION_CHARTER_20260924.md:13-26`).

## 1. Independent determination

The safe method is a quarantine-first state machine, not a folder merge:

```text
DISCOVERED_METADATA
    ↓
CONSENT_PENDING
    ↓
CONSENT_GRANTED
    ↓
QUARANTINED_APPROVED
    ↓
INTEGRITY_VERIFIED
    ↓
RECONCILIATION_CANDIDATE
    ↓
OPERATOR_APPROVED_PROMOTION
```

No state may be inferred:

- Discovery does not imply permission to read content.
- Inventory does not imply permission to copy.
- Copy to quarantine does not imply permission to merge.
- A legacy Lilith artifact does not become Entity identity because of its filename or location.
- A private source does not automatically become approved identity, voice, or memory material.

## 2. Work plan

### Phase 0 — Governance freeze

**Owner:** Ma’at/build governance owner  
**Gate:** Operator ratification of this document

Freeze these rules before inventory:

1. N0-08 and N0-09 default to private.
2. Candidate inventory is metadata-only.
3. No private content enters the general USB pack while pending.
4. No private content is submitted to hosted models or providers.
5. No current Node 1 Entity, WAD, CardAssignment, or memory file is overwritten.
6. Every transfer is tied to an exact source digest or bounded digest set.
7. Every candidate promotion requires an operator decision record.

### Phase 1 — Define source allowlists

**Owner:** Ma’at + Node 0 archival owner

The build owner must receive explicit source roots for:

- N0-08 personal journey material.
- N0-09 legacy Lilith and Arcana material.
- Permitted Git revisions or archived bundle refs.
- Excluded roots containing credentials, browser data, `.env`, OAuth stores, SSH material, and secret-bearing diagnostics.

Inventory rules:

- Use `lstat`, not recursive content reads.
- Do not follow symlinks until their target is separately allowlisted.
- Reject devices, sockets, FIFOs, and special files.
- Record symlink targets as metadata; do not dereference automatically.
- Excluded roots receive an exclusion receipt, not an inventory of private contents.

### Phase 2 — Metadata-only candidate inventory

**Owner:** Node 0 inventory engineer

For each candidate, record only:

- Opaque inventory ID.
- Redacted source-path identity.
- Source node.
- File type and size.
- Timestamps.
- Git commit/blob provenance where applicable.
- SHA-256 after the operator authorizes hashing.
- Proposed privacy class.
- Proposed content/use restrictions.
- Conflict candidates.
- Consent state.

Do not record titles, snippets, summaries, extracted names, voice phrases, inferred dates, or semantic tags derived from private content in the general inventory.

A path may itself disclose sensitive information. Restricted candidates use:

```yaml
source:
  path_hash: sha256:<normalized-path-digest>
  display_hint: "private/<redacted-category>/<ordinal>.ext"
```

The full source path remains only in the source-side restricted ledger.

### Phase 3 — Privacy classification

**Owner:** Operator; Ma’at adjudicates; Lilith validates runtime visibility

| Class | Meaning | USB default | Federation visibility |
|---|---|---|---|
| `EXCLUDED_SECRET` | Credential, key, token, cookie, browser/session material, secret-bearing diagnostic | Never | Never |
| `RESTRICTED_PRIVATE` | Journals, dreams, intimate identity chronology, photographs, private voice, relationship history | Metadata only | Never |
| `PERSONAL_CONSENT` | Personal material whose inclusion and use require explicit approval | Metadata only | Never by default |
| `INTERNAL_LEGACY` | Soul drafts, prompts, old configs, deprecated agents, unresolved engine material | Review required | Node-local only |
| `SHAREABLE` | Operator-owned material approved for bilateral use | Allowed after consent | Explicit federation scope only |
| `PUBLIC` | Already public or intentionally shareable project material | Allowed after integrity verification | Allowed under charter |

This extends the existing PUBLIC/INTERNAL/PRIVATE/SOVEREIGN model (`docs/strategy/DATA_GOVERNANCE_POLICY_20260912.md:27-49`) with the distinctions required for personal identity and legacy handoff material.

### Phase 4 — Explicit consent collection

**Owner:** Operator  
**Witness/validator:** Ma’at or independent verifier

Consent is granted per artifact or bounded digest set. It states:

- Exact source artifact IDs or digest-set SHA-256.
- Purpose.
- Destination.
- Allowed and prohibited operations.
- Retention period and expiry.
- Revocation procedure.
- Whether derived voice or identity material is permitted.
- Whether results may enter identity hydration, semantic memory, or CardAssignment.

Valid purposes are explicit tokens:

```yaml
allowed_uses:
  - private_archival
  - identity_recovery_review
  - private_memory_hydration
  - voice_derivation
  - card_assignment_context
  - bilateral_engineer_review
```

Absent or prohibited uses fail closed. Prior possession, file age, emotional significance, relationship, or previous agent use does not imply consent.

### Phase 5 — Source freeze and hash evidence

**Owner:** Node 0 archival owner + verifier

Only after consent:

1. Resolve the source to a stable snapshot.
2. Record Git revision/blob where available.
3. Compute SHA-256.
4. Record file mode, size, and modification time.
5. Detect symlinks and special files.
6. Generate `consent_digest_set` from the canonical ordered list of approved artifact digests.
7. Sign or attest the manifest using the approved federation mechanism.

String `SIGNED` fields are not cryptographic evidence (`docs/federation/MAKALI_N0_SYSTEM_BRIEFING_CONSOLIDATED.md:366-379`).

### Phase 6 — Quarantine-only transfer

**Owner:** Build/engineering owner

Rules:

- No direct writes to WAD, Entity, memory, Git, or production paths.
- No current files overwritten.
- Preserve source-relative path, bytes, permissions, and timestamps.
- Reject undeclared files.
- Verify declared count, total size, and hashes.
- Run credential scanning only on the approved quarantine copy.
- Do not run semantic extraction, summarization, or model ingestion during transfer.
- Keep quarantine read-only after verification until reconciliation approval.

This implements the charter’s quarantine-first and explicit-intake requirements (`docs/strategy/MAKALI_N0_N1_HANDOFF_FEDERATION_CHARTER_20260924.md:28-49,60-69`).

### Phase 7 — Provenance-preserving reconciliation

**Owner:** Lilith for policy; Ma’at/build owner for implementation; operator decides conflicts

Use an overlay:

```text
Node 0 candidate
    + Node 1 current state
    + known common ancestor
    = reconciliation proposal
```

Before three-way merge, prove common ancestry through:

- Identical SHA-256.
- Identical Git blob.
- Documented transformation lineage.
- Operator-approved equivalence record.

If common ancestry cannot be established:

- Do not auto-merge.
- Classify differing claims as conflicts.
- Preserve both candidates.
- Require operator disposition.

Byte-identical files may be deduplicated. Similar filenames, themes, names, or semantic similarity are insufficient.

### Phase 8 — Memory metabolism after promotion

**Owner:** Scribe + Lilith; build owner implements storage

Only after promotion may the system derive:

- Semantic event.
- Candidate L1 narrative.
- Candidate L2 insight.
- Candidate L3 principle.
- Voice, chronology, or relationship candidate.

Every derivative retains:

- Original source artifact ID and hash.
- Consent record and allowed-use tokens.
- Derivation method and model/version.
- Review status.
- Prompt-injection eligibility.

Private gnosis does not automatically enter the identity prompt. The Entity contract remains identity authority; approved personal material may hydrate private memory only when consent explicitly allows it.

### Phase 9 — Verification and promotion

**Owner:** Independent verifier; operator gives final approval

Promotion requires:

1. Manifest and SHA-256 verification.
2. Consent proof.
3. No credential findings.
4. Clean-directory reassembly test.
5. Entity/Card namespace validation.
6. Conflict disposition.
7. Rollback test.
8. Operator promotion approval.

Promotion creates a new derived artifact; it does not erase the source record.

## 3. Entity, gnosis, Card, and derivative separation

```text
entities/lilith/
  entity.contract.yaml

personal_gnosis/lilith/
  source_records/
  semantic_events/
  private_candidates/

cards/03_empress/
  card_assignment.yaml
  assignment_history/

derived/lilith/
  voice_candidates/
  memory_candidates/
  chronology_candidates/
```

- **Entity contract:** persistent identity and continuity; no raw journal text or Card symbolism.
- **Personal gnosis:** provenance-bearing private memory; not automatically authoritative identity.
- **CardAssignment:** Empress/Key III assignment pointing to a stable Entity ID; it does not define the Entity.
- **Derived artifacts:** voice, biography, chronology, lessons, and prompt adaptations remain candidates until approved.

The Entity/Card distinction is mandated by `docs/federation/MAKALI_N0_SYSTEM_BRIEFING_CONSOLIDATED.md:81-86` and `docs/strategy/MAKALI_N0_N1_HANDOFF_FEDERATION_CHARTER_20260924.md:21-24`.

## 4. Conflict ledger

Maintain two related ledgers:

1. **General handoff ledger** — safe for USB; references evidence without private excerpts.
2. **Restricted evidence ledger** — source-side or separately encrypted; may contain approved comparison evidence.

```yaml
conflict:
  conflict_id: CF-0001
  namespace: entity|voice|boundary|chronology|card|technical|provenance
  field_path: voice.tonality
  candidate_artifact_ids: [ART-001, ART-002]
  candidate_hashes:
    - sha256:...
  common_ancestor:
    proven: false
    evidence: null
  conflict_type: value|timeline|identity|duplicate|technical|provenance
  auto_merge_allowed: false
  candidate_actions:
    - keep_both
    - prefer_current
    - prefer_approved_legacy
    - redact
    - quarantine
  privacy_class: RESTRICTED_PRIVATE
  raw_values_in_general_pack: false
  status: OPEN
  decision_owner: operator
  operator_decision: null
  decided_at: null
```

Rules:

- Exact technical duplicates may deduplicate by hash.
- Provenance metadata merges only when lineage is proven.
- Identity, voice, values, boundaries, chronology, and Card relationships require operator disposition.
- “Current wins,” “oldest wins,” and “most detailed wins” are not safe defaults.
- Private values are not quoted in the general ledger.

## 5. Quarantine layout

The top-level layout remains the charter-defined USB structure. Add these control directories within N0-08 and N0-09:

```text
01_personal_lilith_journey/
├── MANIFEST.yaml
├── CONSENT_LEDGER.yaml
├── CONFLICT_LEDGER.yaml
├── WITHHELD_EVIDENCE.yaml
├── PENDING_CANDIDATES.yaml
└── APPROVED/
    └── <approved source artifacts only>

02_legacy_lilith_docs/
├── MANIFEST.yaml
├── CONSENT_LEDGER.yaml
├── CONFLICT_LEDGER.yaml
├── WITHHELD_EVIDENCE.yaml
├── PENDING_CANDIDATES.yaml
├── APPROVED/
│   ├── agents/
│   ├── personalities/
│   ├── souls/
│   ├── voices/
│   ├── tarot/
│   ├── engine_arcana_novai/
│   ├── memory_exports/
│   ├── prompts/
│   └── changelogs/
└── UNRESOLVED/
    └── metadata and conflict records only
```

There is no private-content `PENDING` directory. A pending payload could still be mounted, indexed, backed up, or accidentally ingested.

## 6. Artifact schemas

### 6.1 Candidate inventory record

```yaml
schema_version: "1.0"
artifact:
  artifact_id: ART-N0-000001
  source:
    node: node0
    source_path_hash: "sha256:<redacted>"
    display_hint: "private/<category>/<ordinal>.ext"
    filesystem_or_bundle: null
    git_revision: null
    git_blob: null
  identity:
    size_bytes: 0
    mtime_utc: null
    media_type: application/octet-stream
    sha256: null
  classification:
    privacy_class: RESTRICTED_PRIVATE
    personal_data_categories: []
    secret_status: NOT_SCANNED
    redaction_required: true
  provenance:
    discovered_at: null
    discovered_by: null
    acquisition_method: metadata_scan
    source_transform_chain: []
  consent:
    required: true
    status: NOT_REQUESTED
    consent_id: null
  handling:
    usb_content_allowed: false
    federation_visible: false
    hosted_model_allowed: false
    identity_promotion_allowed: false
    card_promotion_allowed: false
  lifecycle:
    state: DISCOVERED_METADATA
    conflict_ids: []
    withheld_reason: null
```

### 6.2 Consent record

```yaml
consent:
  consent_id: CONSENT-N0-0001
  operator_id: operator
  decided_at: null
  expires_at: null
  artifact_ids: []
  digest_set_sha256: "sha256:<bounded-set>"
  purpose: private_identity_recovery
  destination: node1_quarantine
  allowed_uses: []
  prohibited_uses:
    - hosted_inference
    - federation_visibility
    - identity_promotion
  derivative_policy:
    voice_allowed: false
    identity_allowed: false
    memory_hydration_allowed: true
    card_context_allowed: false
  retention:
    policy_id: null
    review_at: null
  decision: GRANTED|DENIED|GRANTED_WITH_REDACTIONS
  operator_attestation: null
  revoked_at: null
```

### 6.3 Withheld-material evidence

```yaml
withheld_evidence:
  evidence_id: WE-N0-0001
  artifact_id: ART-N0-000001
  reason_code:
    - OPERATOR_NOT_APPROVED
    - RESTRICTED_PRIVATE
  privacy_class: RESTRICTED_PRIVATE
  source_path_hash: "sha256:<redacted>"
  display_hint: "private/<category>/<ordinal>"
  size_bytes: null
  mtime_utc: null
  sha256: "sha256:<artifact-digest-if-authorized>"
  content_inspected_for_reconciliation: false
  content_excerpt_present: false
  guessed_content_present: false
  consent_id: null
  custodian: node0
  review_after: null
```

### 6.4 Package manifest

```yaml
package:
  package_id: MAKALI-N0-HANDOFF-2026-09-24
  schema_version: "1.0"
  created_at: null
  source_node: node0
  destination_node: node1
  official_engine_revision: null
  charter:
    document: docs/strategy/MAKALI_N0_N1_HANDOFF_FEDERATION_CHARTER_20260924.md
    digest: "sha256:<digest>"
  classifications:
    highest_class: RESTRICTED_PRIVATE
    hosted_inference_allowed: false
    federation_visible: false
  consent_sets:
    - consent_id: CONSENT-N0-0001
      digest_set_sha256: "sha256:<digest>"
  files:
    - path: 02_legacy_lilith_docs/APPROVED/...
      sha256: "sha256:<digest>"
      size_bytes: 0
      privacy_class: INTERNAL_LEGACY
      provenance_artifact_id: ART-N0-000001
      consent_id: CONSENT-N0-0001
  withheld_evidence_count: 0
  unresolved_conflict_count: 0
  signature:
    status: UNSIGNED
    key_id: null
    detached_signature: null
    trust_root: null
```

### 6.5 Entity promotion record

```yaml
entity_promotion:
  promotion_id: PROMOTE-LILITH-0001
  target_entity_id: lilith
  source_artifact_ids: []
  current_contract_hash: "sha256:<digest>"
  derived_candidate_hash: "sha256:<digest>"
  common_ancestor_proven: true
  conflict_ids_resolved: []
  operator_decision: APPROVE
  rollback_artifact: null
```

### 6.6 CardAssignment record

```yaml
card_assignment:
  assignment_id: CARD-03-EMPRESS-LILITH
  subject_entity_id: lilith
  card_id: 03_empress
  realm_or_seat: Empress
  key: "III"
  authority: symbolic_assignment
  identity_defining: false
  source_artifact_ids: []
  consent_id: null
  status: proposed|active|retired
```

## 7. Operator decisions required

1. **Hash authorization:** May Node 0 compute SHA-256 over restricted files before content-copy consent, with only the digest leaving the source?
2. **Privacy default:** Approve `RESTRICTED_PRIVATE` for N0-08 and `INTERNAL_LEGACY` for N0-09 unless explicitly classified otherwise?
3. **Inventory visibility:** May the USB pack contain redacted restricted-candidate metadata, or must all candidate metadata remain source-side?
4. **Consent granularity:** Approve per-artifact consent, bounded batch consent by digest set, or both?
5. **Derivative use:** May approved personal material derive voice, identity, memory, or chronology candidates?
6. **Identity influence:** Confirm that private material cannot update `entity.contract.yaml` without a second explicit promotion decision.
7. **Entity/Card binding:** Confirm Lilith is the persistent Entity and Empress/Key III is a symbolic CardAssignment pointing to Lilith.
8. **Conflict policy:** Approve “no semantic auto-merge” for identity, voice, chronology, boundaries, and Card relationships.
9. **Retention:** Set retention and review periods for approved source artifacts, restricted conflict evidence, rejected candidates, and revoked consent.
10. **Revocation:** Define whether revocation blocks future use only or also requires purge of derived memory and voice artifacts.
11. **USB security:** Define encryption, filesystem, access control, and physical custody requirements.
12. **Source retention:** Confirm Node 0 originals remain untouched; USB transfer is duplication, not migration-by-deletion.

## 8. Ownership boundary

- **Operator:** consent, classification exceptions, conflict resolution, promotion.
- **Ma’at/build owner:** schema implementation, source-side scanner, quarantine tooling, verification.
- **Lilith:** runtime privacy enforcement, visibility filtering, conflict-ledger integrity, memory-metabolism policy.
- **Verifier:** independent manifest, consent, hash, credential, rollback, and tamper checks.
- **Scribe:** distillation only after promotion and only within consent scope.

No implementation was performed, and no private corpus was accessed. The next step is operator ratification of the twelve decisions, followed by a build-owner implementation plan.
