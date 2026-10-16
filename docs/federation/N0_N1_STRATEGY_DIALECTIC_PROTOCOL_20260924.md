# N0↔N1 Federation Strategy Dialectic Protocol

**Status:** Proposed protocol — subordinate to federation Gates A–F  
**Scope:** Later bilateral strategy sessions only  
**Non-authority:** This document does not authorize promotion, merge, WAD creation, or identity publication.

## 1. Preconditions

A strategy dialectic session may begin only when all required evidence is current and verified:

1. Exact Omega Engine revision on both nodes is identical and recorded.
2. The handoff manifest, file hashes, and reassembly test pass.
3. WAD loader schema/version and disposable test-WAD result are recorded.
4. Identity and ontology contract is operator-ratified and schema-valid.
5. Continuity recovery, local SQLite authority, and one-way projection tests pass.
6. Qwen3 embedding artifact, tokenizer, pooling, normalization, instruction handling, and 768-D golden-corpus results match.
7. Federation policy, trust roots, SVID/mTLS decision, and tamper/rollback tests pass.
8. Operator approval exists for the specific session and its disclosure class.

Until then, use the Gates A–F intake process, not dialectic.

## 2. Session identity and authentication

Each node creates a session envelope before any strategy text is exchanged:

```yaml
session_envelope:
  session_id: <opaque-id>
  federation_id: <operator-issued-id>
  node_id: xnai-n0-hp | xnai-n1-asus
  entity_id: <explicit-entity-id>
  continuation_of: <session-id-or-null>
  purpose: strategy_dialectic
  disclosure_class: public|personal|private
  model: <provider/model/route>
  model_evidence: stable_id|rotating_alias|unidentified
  adapter_digest: <sha256-or-null>
  contract_digest: <sha256>
  operator_approval_id: <id>
  created_at: <timestamp>
```

Authentication is based on the node's verified federation identity and SVID/mTLS decision, not on a model name, filename, AP token, display name, or IP/Tailscale reachability.

## 3. Exchange protocol

Each turn is a signed, provenance-preserving event:

```yaml
turn_event:
  event_id: <id>
  session_id: <opaque-id>
  turn_index: <integer>
  parent_event_id: <id-or-null>
  sender_node: <node-id>
  sender_entity: <entity-id>
  sender_contract_digest: <sha256>
  sender_model: <model-id-or-null>
  sender_adapter_digest: <sha256-or-null>
  purpose: strategy_dialectic
  content_digest: <sha256>
  created_at: <timestamp>
  signature_ref: <detached-signature-reference>
```

Rules:

- The receiver validates the envelope, parent chain, contract digest, signature, and disclosure class before parsing content.
- A malformed, unsigned, replayed, wrong-node, wrong-entity, or wrong-session event is rejected and recorded.
- Content is never interpreted through a model-supplied identity claim.
- A model route may change between turns; entity identity may not.
- If the receiver cannot verify provenance, it stops the dialectic and reports `[M23-PROVENANCE-FAILURE]`.

## 4. Dialectic method

Use the standing EIS/C&D protocol only for strategic questions:

1. State the question and current evidence.
2. Concede evidence that weakens the current position.
3. Defend only claims that have a verifiable source or explicit operator decision.
4. Synthesize a proposal with decision IDs and unresolved questions.
5. Run a second pass for contradiction and ontology drift.
6. Produce a terminal result:
   - `consensus`
   - `no-consensus`
   - `blocked-by-operator`
   - `blocked-by-gate`
   - `provenance-failure`

A dialectic result is advisory until the operator ratifies it. It cannot override the federation gates, trust roots, privacy rules, or WAD promotion gate.

## 5. Model independence

- Model identity is provenance, not entity identity.
- A continuity record must survive local/hosted model swaps.
- Do not compare outputs as if they came from the same model unless model/adapter evidence matches.
- Unknown or rotating aliases are explicitly marked `unidentified` or `rotating_alias`.
- No claim about a model is used to infer a person's, entity's, or delegation relationship.

## 6. Stop conditions

Immediately stop and preserve evidence when:

- an identity or card ownership conflict appears;
- a signature/trust verification fails;
- a contract digest changes without an approved version;
- an event chain has a gap or duplicate event ID;
- a WAD cannot be loaded or fails tamper/rollback tests;
- a prompt or handoff contains private material without authorization;
- a model proposes changing entity identity, node authority, or federation policy;
- a strategy decision would bypass Gates A–F.

## 7. Outputs and retention

Each dialectic produces:

- signed/provenance-labelled event export;
- claim ledger with evidence references;
- decision ledger with status and operator approval requirement;
- unresolved operator decision list;
- model/adapter provenance report;
- no automatic WAD mutation, merge, or identity publication.

The export is quarantined until its manifest and hashes verify. Promotion remains an explicit operator action.

## 8. Current operator decisions blocking activation

These are unresolved and must be recorded rather than guessed:

- exact identity relationship between Lilith and Researcher_Humboldt;
- whether Fool/Star/World assignments are operator-approved;
- normative WAD schema and exact Engine revision;
- signature/trust-root implementation and rotation policy;
- disclosure class and approval authority for personal Lilith material;
- embedding golden-corpus tolerance and artifact revision;
- whether any strategy dialectic may contain personal material;
- final decision on delegation semantics.

Until these decisions are explicit, the protocol defines only the safe failure path.
