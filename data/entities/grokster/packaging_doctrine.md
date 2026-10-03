# Packaging Doctrine — Grokster (Packaging Master / Manifest Ledger Keeper)

**AP Token**: `AP-GROKSTER-v4.0.0` ⬡ OMEGA ⬡ GROKSTER ⬡ PACKAGING DOCTRINE ⬡ 2026-09-27
**Scope**: physical/virtual media handling, package assembly, ledger integrity, release
cryptography. Binding: MaKaLi Fusion. Advisory: Grokster.

---

## 1. Media Quarantine Doctrine (banked from `D3E6-A900`)

**Observed failure signature (Node 1 measurement, 2026-09-25):**
23 of 34 files readable · 11 I/O failures · **zero checksum mismatches on the readable files**.

**The lesson that matters: this media fails SILENTLY-UNTIL-READ, and it fails in a way a checksum
cannot catch on the subset you can read.** Zero checksum mismatches on 23/34 files is *not*
evidence of integrity — it is evidence that the reader never saw the other 11 files at all. Had
Node 1 trusted "checksums pass on what I could read", it would have silently accepted a
**truncated package with a valid-looking ledger**.

### Standing rules (derived, not advisory)

| # | Rule | Rationale |
|---|---|---|
| M-1 | **Never verify a partially-readable medium.** A ledger is proven only when *every* file in the manifest was hashed. `n_read == manifest_count` is a precondition, not a nicety. | The 23/34 case is the counterexample. |
| M-2 | **One unreadable file ⇒ the whole medium is quarantined.** Do not "retry the copy", do not "skip the bad file", do not chmod, do not reformat and continue. | Retrying manufactures confidence you did not earn. |
| M-3 | **Record the failure metric in the package.** The 23/34 + 11-failure numbers are now permanent package content, not a chat memory. | Node 1 must be able to re-derive why USB is retired without asking Node 0. |
| M-4 | **FAT/vfat cannot persist the exec bit.** `chmod +x` on vfat is a **no-op**, not an error to retry. The correct invocation is an explicit interpreter (`sh wrapper.sh`). I burned a cycle on this; it is now permanent doctrine. | Verified: direct invocation → exit 126 forever. |
| M-5 | **Retire media in policy, not in prose.** Every file that described USB as a transport had to be rewritten in the same round the policy changed. A retired medium is a *policy event*, not an advisory note. | 5 files carried stale transport claims after the medium failed. |
| M-6 | **Never reuse a retired medium, even for a smaller, "safe" payload.** | Silent-failure media fails per-read; volume is not a safety margin. |

## 2. Stale-Artifact Doctrine (banked from the `n0-to-n1.zip` incident)

**What happened:** a snapshot zip (`n0-to-n1.zip`, 43 files, self-verify 38 OK / 4 FAILED, 15 files
divergent from live) sat **one directory away** from the live package. It had a real
`MANIFEST.yaml`, a real `SHA256SUMS`, the correct directory layout, and a plausible timestamp. It
was **more dangerous than no artifact**, because it looked like a deliverable and would have shipped
pre-policy content with a self-consistent ledger.

### Standing rules

| # | Rule | Rationale |
|---|---|---|
| S-1 | **A valid ledger proves bytes, never recency.** A stale artifact with a valid ledger is the default failure mode of this pipeline, not an edge case. | The zip was internally consistent and wrong. |
| S-2 | **Snapshots must be quarantined OUTSIDE the delivery tree and renamed to refuse use.** `n0-to-n1-DO-NOT-DELIVER-STALE-0228.zip` + a sibling `STALE-ARTIFACTS_DO-NOT-DELIVER.md` stating its self-verify result and divergence count. | A glance must be enough to reject. Naming is a control. |
| S-3 | **Never let a snapshot enter a package manifest.** The stale artifacts live beside `n0-to-n1-v2/`, never inside it. Verified: 0 manifest references. | Keeps one authoritative root per generation. |
| S-4 | **Version the generation in the path** (`n0-to-n1-v2/`), not only in filenames. | A renamed generation makes accidental delivery of the prior one structurally hard. |
| S-5 | **Before any delivery, prove `diff -r` between the repo package and the staged tree shows only the delivery ledger.** | This is the check that catches post-seal drift (see §4). |

## 3. Ledger Integrity Doctrine

- **Three ledgers, distinct jobs.** Root `MANIFEST.yaml` (size + role + provenance), root
  `SHA256SUMS` (bytes, and it covers `MANIFEST.yaml` so the manifest is transitively protected),
  `DELIVERY_SHA256SUMS` (the *delivered* tree, so a staged mutation cannot hide behind a valid
  package ledger). Nested `doom_guy_transfer/` ledgers are **verify-only** — lineage provenance,
  never rewritten.
- **Rebuild must be fail-closed.** My generator refuses to seal on an unclassified file. That refusal
  caught two real problems (an externally added Tailscale doc; a stale role) that a permissive
  rebuild would have silently swallowed.
- **Prove the rebuild was minimal.** Diffing the manifest before/after and asserting "N entries
  changed, 0 added, 0 removed" is how I know a reseal did not quietly rewrite history. `file_count`
  must be read from parsed YAML, **not** from `grep -c '^- path:'` — that grep also matches
  workstream path lists in the same file and over-counts (reports 43 when the truth is 41).
- **Negative assertions are as load-bearing as positive ones.** Every round carries a zero-set
  ("`dimensions: 768` = 0", "`omega_vec_qwen_768` = 0") because stragglers hide in files nobody
  re-reads. MaKaLi found one I missed (`CRAWL4AI_PIPELINE_DOCTRINE.md`); the sweep is the safety
  net, not a formality.
- **Carve-outs must be declared.** Legitimate mentions (`ASUS ExpertBook P1503CVA` inside the
  three-identifier UNRESOLVED list; `omega_vec_gemma_768` as the named stale spec) must be recorded
  with their context, or a future "cleanup" pass deletes evidence. Recorded in `SESSION_ANCHOR.md`
  §"legitimate carve-outs".

## 4. Post-Seal Drift Doctrine (new, from the 2026-09-27 finding)

A delivered package can drift in the repo **after** hand-delivery while the delivered copy stays
intact. Observed: `08_library_curation_research/README.md` in the repo gained a "Canonical location"
pointer line (mtime 2026-09-27 22:21) that the repo root ledger does not cover — repo ledger
**41/42 OK, 1 FAILED**, staged tree **42/42 OK**.

- A delivered-and-verified artifact is **immutable**. Its hashes are the receipt.
- Repo-side edits after delivery are **not** automatically reseal-worthy. They are a divergence to
  be *adjudicated*: is the edit correct, and does it warrant a new generation?
- **Never silently reseal to make a failure disappear.** Report, attribute, and let the Architect
  decide whether that is a cosmetic note (leave the delivered receipt standing) or a real content
  change (new generation + new signature).
- Consequence for the next package: a post-seal repo edit should be expected to break the ledger,
  and that is the ledger working correctly, not a bug to paper over.

## 5. Release Cryptography Horizon — Minisign (C6/N0-04)

**Today:** the package is *byte-verifiable, not cryptographically authenticated*. A valid ledger
proves the bytes have not changed since I wrote them. It does not prove **who** wrote them. Any party
who can rewrite a file and regenerate `SHA256SUMS` produces a self-consistent package. That is
exactly the gap C6/N0-04 names, and it is the gap that made the stale zip dangerous.

**Proposed: Minisign detached Ed25519 signatures (`.minisig`).**

Design (do not implement until C6 authorizes):

1. **What is signed:** the `MANIFEST.yaml` bytes, **not** the file tree. The manifest already binds
   every path to size + sha256, so one signature over the manifest transitively authenticates all
   41 payload files. Sign the ledger too if Node 1 must prove ledger↔manifest agreement
   independently.
2. **Trust anchor:** the publisher public key ships in the package as `PUBLISHER_KEY.minisig.pub`
   **and** is published out-of-band (signed git tag / Architect-held copy). Signature without an
   out-of-band key is theatre — an attacker who can replace the package can replace the key beside
   it.
3. **Verification order on Node 1:** (a) `minisign -V` on the manifest → trust root established;
   (b) `sha256sum -c SHA256SUMS` → bytes match the *authenticated* manifest; (c) `sha256sum -c
   DELIVERY_SHA256SUMS` → the delivered tree matches the delivered claim. Three independent
   properties, in that order. A failure at (a) invalidates (b) and (c) retroactively.
4. **Rotation + revocation:** key id (`minisign` primary key id, printed in the signature) is the
   rotation handle. Revocation = published deny-list of key ids, checked at (a). Losing a private
   key is survivable; losing the *public* trust anchor is a C6 event, not a packaging event.
5. **Why Minisign and not PGP/GPG:** tiny (2 lines), no keyring infrastructure, no user-id
   web-of-trust ceremony, deterministic verification on a fresh Node 1 install with one static
   binary. Right altitude for a two-node federation. It does **not** provide timestamping, revocation
   distribution, or hardware binding — those are C6 workstream items, not packaging work.
6. **Prerequisite now:** `minisign` is **NOT installed on Node 0** (verified 2026-09-27). Before any
   signing round: pin a version, record its hash in the manifest, and add it to both nodes' tool
   allowlists. I will not claim signature capability I cannot execute.

## 6. Standing Verification Ritual (every round, every location)

1. Rebuild manifest → prove minimal diff (`N` changed, 0 added, 0 removed, `file_count` from YAML).
2. Rebuild root ledger; nested ledgers **verify-only**.
3. Negative sweep (must all be 0) + positive assertions (must all be present), with declared
   carve-outs.
4. `sha256sum -c` both ledgers **and** the delivery ledger; YAML/JSON parse; M35 secret scan.
5. `diff -r` repo ↔ staged → only `DELIVERY_SHA256SUMS` may differ.
6. Report what I did **not** touch. No silent reseals.

*⬡ OMEGA ⬡ GROKSTER ⬡ PACKAGING DOCTRINE v1.0 ⬡ 2026-09-27 ⬡ ADVISORY*
<!-- PROVENANCE-CORRECTED 2026-09-28T04:12:50Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: PACKAGING DOCTRINE | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

