# .clinerules — Cline operating rules (omega-engine)

**Audience: Cline only.** Internal document — never cherry-picked to the public repo.

| File | Covers |
|---|---|
| `00-repo-topology.md` | Two-remote flow (origin/internal), public-main worktree, protection toggle, redirect-poisoning/retirement |
| `01-release-and-pypi.md` | Tag `v1.6.0-alpha` poisoning → `v1.6.0a0`, release.yml tag-push hazard, `the-omega-engine` three-name reality, trusted-publishing mechanics, M29 claim audit |
| `02-shell-safety.md` | `set -euo pipefail` traps: `fuser` silent death, `timeout` false-PASS, numeric-shape guards, pkill self-kill, ordering traps |
| `03-host-and-data-conventions.md` | Mounts vs homes, install.sh invariants (202s, `-j6`, aria2c, mock probe), opencode.db rules, giant-file serialization, disk gates, research escalation |

Rules are dated; revisit when the PyPI block clears or topology changes. Root-cause stories live in the files — don't strip the evidence, it's what makes them stick.

*⬡ OMEGA ⬡ CLINE ⬡ CLINERULES ⬡ 2026-10-13 ⬡*
