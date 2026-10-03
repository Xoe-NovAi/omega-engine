<!-- SPDX-FileCopyrightText: 2026 Xoe-NovAi / SPDX-License-Identifier: Apache-2.0 -->
# ADR-004: Read-Only Exchange Pipe

**Status:** Accepted — 2026-10-02 · Federation Exchange subsystem

## Context
Two nodes must move files to each other. Any channel that accepts writes from a
remote peer is, by definition, a remote-code-execution surface: whoever can
write a file can often choose its path, its name, or the script that later
consumes it.

## Decision
The Exchange is **GET/HEAD only**, served over Tailscale Serve. Write methods
are rejected with **405 by design** — not by oversight, but as the security
control itself. There is no push: each node publishes its own root and the
other node pulls.

## Consequences
- A writable pipe would be an RCE surface; removing write removes the entire
  class of remote-write exploits.
- The **manifest + sha256** is the only defence for what is pulled: the
  receiver verifies integrity because it cannot assume the channel protected it.
- Cost: **no push**. A node that wants to share must publish its own root —
  symmetric, but both sides must run the publisher.
- Cost: no remote deletion or rename; lifecycle is owned by the publishing
  node only.

## Alternatives Considered
- **rsync/SSH push**: authenticated, but distributes shell and credential
  surface to both ends — a compromised peer gains a login, not just a read.
- **WebDAV/HTTP PUT with auth**: write capability with auth bolted on; any auth
  bug then becomes a write bug. Higher complexity, same blast radius.
- **Shared mutable mount**: no boundary at all between peers; one rogue write
  corrupts both nodes' views.