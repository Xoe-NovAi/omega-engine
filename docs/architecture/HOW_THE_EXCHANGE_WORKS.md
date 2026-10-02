<!-- SPDX-FileCopyrightText: 2026 Xoe-NovAi / SPDX-License-Identifier: Apache-2.0 -->
# How the Exchange Works

**Audience**: any node publishing or pulling cross-node files.
**Scope**: publish root, manifest, pull + verify, read-only enforcement, and
node identity.

## Publish Root

Each node publishes exactly one directory: `~/exchange` is a **symlink to the
real store** (the canonical publish root). Everything beneath it is readable
by peers over Tailscale Serve; nothing else on the node is exposed.

## Manifest

The root carries a manifest describing what is published:

- `served_by` — identity of the publishing node
- `url_form` — URL template for entries, e.g. `https://{host}:{port}/{path}`
- per entry: `path`, `size`, `sha256`

```
node A (publisher)                            node B (puller)
------------------                            ---------------
~/exchange  (symlink -> real store)
  |-- manifest.json
  |     served_by : "node0-primary"
  |     url_form  : "https://{host}:{port}/{path}"
  |     entries[] : { path, size, sha256 }
  |-- DOCS-BRIEF-CLINE-20261002.md
  |-- ...
        ^  GET / HEAD only — writes return 405
        |-------------------------------- pull + verify sha256
                                          -> staging on node B
```

## Pull + Verify

1. `GET` the manifest.
2. `GET` the named entry (each pointer file names body, size, sha256, URL).
3. SHA-256 the received bytes and compare against the manifest entry.
4. **Mismatch = discard and report.** Never "use anyway" — the manifest hash
   is the integrity source of truth for what crossed the wire.

## Read-Only Enforcement

- Only **GET/HEAD** are served; `PUT/POST/DELETE/…` return **405 by design**
  (ADR-004).
- The serving unit runs under **`ProtectSystem=strict`** — the publisher's
  filesystem is read-only to the service.
- Rationale: a writable pipe is an RCE surface. Manifest + sha256 is the only
  defence for what *is* pulled, because the channel itself guarantees nothing
  beyond availability.

## Node Identity

The publishing node is configured by environment:

- `OMEGA_NODE_NAME` — logical name (feeds the `-n<N>` suffix discipline,
  ADR-005)
- `OMEGA_NODE_HOST` — host peers dial (Tailscale name/IP)
- `OMEGA_NODE_PORT` — serve port

Identity is never guessed from DNS or inferred from content; it comes from
these variables and is stamped into the manifest as `served_by`.

## Invariants

- **No push.** Each node publishes its own root; peers only pull.
- **Every pull is verified** against the manifest `sha256` or discarded.
- **405 is a security control, not a bug** — do not "fix" it.
- **Identity comes from `OMEGA_NODE_*`**, never from guessing, never folded
  across node suffixes.

*⬡ OMEGA ⬡ CLINE ⬡ HOW_THE_EXCHANGE_WORKS-v1.0.0 ⬡ 2026-10-02 ⬡*