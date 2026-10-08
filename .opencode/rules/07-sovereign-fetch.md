---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
rule_id: "RULE-07-SOVEREIGN-FETCH"
authority: "M23 Failure Integrity + M24 Venv Sovereignty"
applies_to: "all-agents"
date: "2026-10-07"
status: "ACTIVE"
---

# Architecture Rule: Sovereign Fetch

> **⚡ aria2c is MANDATORY for every download >1MB on Node 0. Never `wget`/`curl` a large
> file — single-connection fetchers forfeit most of the link.**

## The Core Rule

All downloads above 1MB on Node 0 go through **aria2c** (multi-connection, resumable,
sovereign profile). `wget`/`curl` on a large file is a soft-failure waiting to happen
(M23) — a single dropped connection restarts the whole transfer.

## Anchors

| Item | Location |
| :--- | :--- |
| **Profile** | `~/.config/aria2/aria2.conf` |
| **Skill** | `sovereign-fetch` |

## Invariants for All Agents

1. **Verify archives after download**: `xz -t` for `.xz`, `unzip -t` for `.zip` — a
   truncated archive is a silent corruption (M23).
2. **Never bypass the profile**: ad-hoc aria2c flags forfeit the tuned connection/retry
   settings captured in the sovereign profile.
3. **Python stays sovereign** (M24): wheels/sdists installed only inside `.venv/`, never
   `--break-system-packages`. This rule governs direct file downloads; pip handles its own
   fetch path through the same aria2c-hardened network stack where configured.
