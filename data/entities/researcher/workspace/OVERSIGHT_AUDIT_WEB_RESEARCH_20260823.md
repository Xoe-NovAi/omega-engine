<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Oversight-Audit Gap Closure — Web Research (W1–W4)

**AP Token**: `AP-RESEARCHER-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_research ⬡ OVERSIGHT-WEB

**Date**: 2026-08-23
**Mission**: kali · Web-only lane (Roc holds local ground-truth lane)
**Feeds**: `MEDITATION_KALI_20260823_SESSION_TRACKING_OVERSIGHT_AUDIT.md` — 4 open design questions
**Method**: Parallel web search against primary docs + local venv verification for W4 availability claims.

---

## Executive Summary (L1)

| # | Question | Recommendation | Confidence |
|---|----------|----------------|------------|
| W1 | Class-based TTL | Yes — adopt class-based thresholds. Precedent is unanimous: Argo (`ttlStrategy` per-outcome), K8s (`ttlSecondsAfterFinished`), Airflow (`execution_timeout` per task), GH Actions (`retention-days` per artifact). Proposed classes: standard=7d, research=21d, blocked=14d. | High |
| W2 | Liveness trigger | systemd **user timer** (`Persistent=true`, daily) running the validator in dry-run/report mode; keep pre-commit gate as-is. Rejects GH Actions cron (unreliable, cloud, M8 violation). | High |
| W3 | Audit log | JSONL append-only with SHA-256 hash chain (`prev_hash` → `entry_hash`). Schema below. Rotate by size/date; verify chain on read or weekly. No HMAC/Merkle needed for single-user local engine. | High |
| W4 | YAML annotation validation | **Pydantic v2** model over `yaml.safe_load`. Already installed (pydantic 2.13.4, venv-verified); clearest field-level errors; supports partial-required via Optional/defaults. jsonschema 4.26.0 also installed but gives worse errors and more boilerplate. yamllint NOT installed — rejected (new dep, and it lints style not schema). | High |

---

## L2 — Detailed Dialectic

### W1 — Class-Based TTL / Staleness Policy

**The Architect**: Every mature scheduler we surveyed implements *per-class* retention/timeout — none uses a single global constant. The pattern is: a default at the system level, overridable per workload class.

**Evidence**:

1. **Argo Workflows — `ttlStrategy`**: outcome-classed TTL fields on every Workflow:
   - `secondsAfterCompletion` (fallback, covers Error phase), `secondsAfterSuccess`, `secondsAfterFailure`.
   - Canonical production example retains successes 1 day but failures/errors 7 days (`604800`s).
   - Controller-level defaults via `workflowDefaults` in the ConfigMap; workflow-level values take precedence.
   - Sources: https://argo-workflows.readthedocs.io/en/latest/default-workflow-specs/ ; field reference https://argo-workflows.readthedocs.io/en/latest/fields/ ; production-policy walkthrough https://oneuptime.com/blog/post/2026-08-02-argo-workflows-podgc-ttl-archive/view (accessed 2026-08-23).
   - Note: Argo had NO default TTL until explicitly added (issue #2217, https://github.com/argoproj/argo-workflows/issues/2217) — i.e., "no TTL = zombies accumulate forever" was a known defect they fixed.

2. **Kubernetes Jobs — `ttlSecondsAfterFinished`**: per-Job field, no global default (unset = live forever); KEP-592 exists precisely because unbounded finished jobs accumulated cluster-wide. Recommended to set explicitly.
   - https://kubernetes.io/docs/concepts/workloads/controllers/ttlafterfinished/ ; KEP: https://www.kubernetes.dev/resources/keps/592/ (accessed 2026-08-23).

3. **Apache Airflow — `execution_timeout` / `sla` per task**, with DAG-level `default_args` inheritance and even a cluster policy hook (`airflow_local_settings.py`) that can CAP timeouts by task class ("no tasks run more than 48 hours").
   - https://airflow.apache.org/docs/apache-airflow/1.10.9/concepts.html (policy section) (accessed 2026-08-23).

4. **GitHub Actions artifacts — `retention-days` per artifact**, default 90d, classed override at enterprise/org/repo/artifact level (public repos capped at 90d, private up to 400d).
   - https://github.blog/changelog/2020-10-08-github-actions-ability-to-change-retention-days-for-artifacts-and-logs/ ; https://docs.github.com/en/organizations/managing-organization-settings/configuring-the-retention-period-for-github-actions-artifacts-and-logs-in-your-organization (accessed 2026-08-23).

5. **MLflow Model Registry**: lifecycle stages (`None/Staging/Production/Archived`) are class-based lifecycle management with transition audit trails — same shape of problem (long-lived artifacts need stage-dependent governance).
   - https://mlflow.org/classical-ml/model-registry (accessed 2026-08-23).

**The Adversary**: The failure mode of a single 7d threshold is exactly what Argo solved with outcome-split fields: different workloads have legitimately different horizons. But beware over-classing — each class needs maintenance. Also note staleness ≠ timeout: our validator flags *lack of heartbeat*, not runtime overrun, so our classes should be keyed on task *type*, not outcome.

**Recommended threshold classes** (mirroring Argo's default-vs-override pattern):

| Class | Stale threshold | Rationale |
|-------|----------------|-----------|
| `standard` (default) | 7 days | Current rule retained; matches Argo's common 7d completion-TTL practice |
| `research` / long-horizon | 21 days | Mirrors multi-week research cycles; Argo-style explicit override |
| `blocked` | 14 days + mandatory blocker note | Blocked tasks age differently than running ones |
| Any class | Extendable only via registry field `stale_override_days` (per-task), validated ≤ class max | Argo's workflow-level-overrides-default contract |

Escalation should be *notification* (dry-run report), never auto-mutation without audit (see W3).

### W2 — Between-Commit Liveness Checking

**Trigger-model comparison matrix**:

| Criterion | Commit-only (status quo) | systemd user timer (local) | GitHub Actions `schedule:` cron | GitLab pipeline schedules |
|-----------|-------------------------|---------------------------|--------------------------------|---------------------------|
| Reliability | Only fires when someone commits — zombies accumulate silently | High; `Persistent=true` catches up missed runs after downtime | Documentedly unreliable: delays under load, dropped jobs during high-load windows, min 5-min spacing | Server-side cron; requires GitLab infra |
| Noise | Zero between commits | One daily journal entry; controllable | N/A locally | N/A locally |
| Sovereignty (M8 zero-telemetry / M7 local-first) | ✅ | ✅ fully local, journald logging | ❌ cloud-hosted, external service dependency | ❌ unless self-managed GitLab (heavy) |
| Maintenance cost | None | Two small unit files (~10 lines each); testable via `systemctl start` | Workflow YAML + runner | Full CI platform |
| Working-directory handling | Native | Set `WorkingDirectory=` in `.service`; works fine with non-bare repo checkout | Runner checks out fresh clone | Same |

**Key evidence**:
- systemd timers vs cron: `Persistent=true` runs missed jobs after boot (cron skips them); journald structured logging; testable immediately with `systemctl start foo.service`; cgroup resource limits built in. https://www.computingforgeeks.com/systemd-timers-linux/ ; SUSE guide https://documentation.suse.com/smart/systems-management/html/systemd-working-with-timers/index.html ; ArchWiki https://wiki.archlinux.org/title/Systemd/Timers (accessed 2026-08-23).
- GitHub Actions schedule unreliability is documented in official docs ("schedule event can be delayed during periods of high load… some queued jobs may be dropped") and repeatedly reported in the wild (15–20 min drift even on idle self-hosted runners): https://docs.github.com/actions/using-workflows/workflow-syntax-for-github-actions#scheduled-events-runs-later-than-scheduled ; https://stackoverflow.com/questions/79534419/ ; https://github.com/orgs/community/discussions/158356 (accessed 2026-08-23).
- GitLab scheduled pipelines run independently of code changes but require the GitLab platform: https://docs.gitlab.com/ci/pipelines/schedules/ (accessed 2026-08-23).
- **Plan/apply split precedent**: Terraform's plan→apply discipline and Ansible check mode (`--check`) establish strong industry precedent for "scheduler computes proposed mutations, human/tool applies them." Our sweep script already has `--dry-run`/`--apply`; the timer should invoke **dry-run only**, writing a report file; `--apply` remains manual (or commit-hook gated) and always writes the W3 audit record. This mirrors `git gc --auto`: safe automatic mode triggered opportunistically, aggressive mode manual.

**Recommendation**: Daily (or twice-daily) **systemd user timer** (`OnCalendar=daily`, `Persistent=true`, `RandomizedDelaySec=300`) → runs validator in report/dry-run mode → writes `data/coordination/tracking_report.jsonl` + surfaces stale count in next session hydration. Keep pre-commit validator as the enforcement gate. This satisfies reliability (catch-up), sovereignty (100% local), and noise (one journal line/day). User-level units need `loginctl enable-user linger` if runs must occur while logged out.

### W3 — Append-Only Mutation Audit Log

**Pattern space surveyed**:
- Hash chaining is the canonical lightweight tamper-evidence mechanism: `entry_hash = SHA-256(prev_hash ‖ canonical_serialization(entry))`. Modifying/deleting/reordering any entry breaks all subsequent hashes; verification is a linear re-walk. Used identically across implementations from IETF draft MVPS log format to minimal Python stdlib-only systems. https://datatracker.ietf.org/doc/draft-melegassi-opsawg-mvps-logging/00/ ; https://auditkit.dev/blog/hash-chaining-tamper-proof-audit-logs ; reference stdlib implementation: https://github.com/ShivangiDas-03/Tamper-Evident-Logging-System (accessed 2026-08-23).
- Counterpoint (Burp AI agent audit design): plain JSONL with per-record payload hashes but **no chain** — acceptable when threat model excludes line deletion; they explicitly note "hashes catch payload edits but not line deletion." For us, the chain costs ~5 lines of code and closes that gap — worth it. https://burp-ai-agent.six2dez.com/privacy-and-logging/audit-logging.md (accessed 2026-08-23).
- Rotation: size/date-based file rotation (e.g., monthly files `audit-2026-08.jsonl`) keeps verification walks bounded; store last hash of rotated segment in a small `chain-heads.json` so cross-file chains stay verifiable. Periodic verification routine recommended (walk chain, escalate any break) — lexpartis.com pattern: https://www.lexpartis.com/en/blog/hash-chain-append-only (accessed 2026-08-23).
- Enterprise extras (HMAC signing, Merkle proofs, external anchoring, XorIDA splitting) are **overkill** for single-user local engine — flagged and excluded.

**Proposed JSONL record schema** (one object per line):

```json
{
  "seq": 42,
  "ts": "2026-08-23T14:02:11Z",
  "actor": "kali",
  "tool": "tracking_sweep.py --apply",
  "action": "task.status_update",
  "target": "TASK_REGISTRY.json#trc_research-20260812-03",
  "before": {"status": "in_progress", "updated_at": "2026-08-12T09:00:00Z"},
  "after": {"status": "superseded", "updated_at": "2026-08-23T14:02:11Z"},
  "reason": "stale per class=research threshold 21d, no heartbeat since Aug 12",
  "prev_hash": "a1b2…",
  "entry_hash": "c3d4…"
}
```

Minimal compliance-surviving fields: who (`actor`) / when (`ts`, RFC3339 UTC) / what (`target` + `before`/`after` old→new) / why (`reason`) / integrity (`seq`, `prev_hash`, `entry_hash`). Guidance:
- Write atomically: append full line + fsync before mutating the registry (order: audit first, mutation second — an audited-but-failed mutation is recoverable; a mutated-but-unaudited one is not).
- Rotate monthly or at ~5 MB; keep `chain-heads.json` anchor.
- Weekly chain verification (can ride the W2 timer).
- Never rewrite the file; corrections are new compensating records.

### W4 — Lightweight YAML Annotation Governance

**Venv ground truth (verified locally, 2026-08-23)**: `pydantic 2.13.4` ✅, `jsonschema 4.26.0` ✅, `PyYAML 6.0.3` ✅, `yamllint` ❌ absent.

**Comparison**:

| Option | Available? | Partial-required-fields support | Error clarity | New dep? |
|--------|-----------|-------------------------------|---------------|----------|
| `yaml.safe_load` + manual checks | ✅ | Manual, ad hoc | Poor (you write your own errors) | No |
| **Pydantic v2** | ✅ 2.13.4 | Native: required vs `Optional`+defaults; `model_validator` for cross-field rules | Excellent — field-path errors with machine-readable types, e.g. `[type=int_parsing]` + docs URL | No |
| jsonschema Draft 2020-12 | ✅ 4.26.0 | Via `required` array | Adequate but verbose; error paths need manual assembly; schema is a second language | No |
| yamllint custom rules | ❌ not installed | Wrong tool — lints style/syntax, not semantic schema | N/A | Yes (rejected) |

**Evidence**:
- Pydantic-as-YAML-config-validator is the established pattern; ValidationError messages name the exact field, input value, and fix URL: https://www.sarahglasmacher.com/how-to-validate-config-yaml-pydantic ; https://www.c-sharpcorner.com/article/validating-yaml-and-toml-configurations-in-python-with-pydantic/ (accessed 2026-08-23). Pattern: `Settings.model_validate(yaml.safe_load(f))` wrapped in `try/except ValidationError` with fail-fast exit.
- yamllint scope confirmation (syntax validity + style weirdness like key repetition — not schema semantics): https://github.com/adrienverge/yamllint ; https://yamllint.readthedocs.io/ (accessed 2026-08-23).
- OSS precedent for gating structured contributions with schemas: GitHub itself gates workflow YAML with the SchemaStore JSON Schemas (https://www.schemastore.org/json/ — the `github-workflow.json` schema powers IDE validation for millions of repos); Ansible gates playbook YAML with yamllint + schema validators combined. Both ecosystems pair a *style* linter with a *semantic* schema validator — we get both by pairing PyYAML parse (syntax) + Pydantic (semantics).

**Concrete minimal validator approach** (zero new deps):

```python
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator
import yaml

class SessionAnnotation(BaseModel):
    session_id: str
    assessed_by: str
    assessed_at: datetime                      # ISO-8601 enforced free
    verdict: Literal["pass", "fail", "flagged"]
    comment: str = ""
    # partial-required: anything optional gets a default; unknown keys rejected:
    model_config = {"extra": "forbid"}

    @field_validator("session_id")
    @classmethod
    def _sid(cls, v: str) -> str:
        if not v.startswith(("ses_", "msg_")):
            raise ValueError("session_id must be an OpenCode session/message id")
        return v

def validate_annotations(path):
    data = yaml.safe_load(open(path))          # syntax layer
    return [SessionAnnotation.model_validate(d) for d in data["annotations"]]
```

ValidationError output names file-field, offending value, and expected type — clear enough to paste into an agent handoff.

---

## L3 — Raw Signal & Verification Notes

- All URLs accessed **2026-08-23** via parallel-search web tooling.
- Verified primary sources: argo-workflows.readthedocs.io, kubernetes.io, airflow.apache.org, docs.github.com, github.blog, docs.gitlab.com, documentation.suse.com, wiki.archlinux.org, datatracker.ietf.org, mlflow.org, pydantic docs (via secondary tutorials quoting official error output), yamllint.readthedocs.io.
- **Could not independently verify**: MLflow stage-transition audit-trail details beyond marketing page (flagged; low stakes for our decision). apt history.log / sudo journaling internals were not directly fetched — the W3 schema derives from IETF MVPS draft + multiple independent hash-chain references instead; noted per constraint to flag unverified items.
- Local venv package versions verified directly via `.venv/bin/pip list` (read-only check; no repo files modified other than this deliverable).
- Known caveat: Argo `Error` phase ignores `secondsAfterFailure` — analog for us: ensure our fallback class covers ALL terminal states, not just named ones.

## RECOMMENDATION TABLE (final)

| W | Recommendation | Confidence | Key citation |
|---|----------------|-----------|--------------|
| W1 | Adopt class-based stale thresholds: standard=7d, research=21d, blocked=14d(+note); per-task `stale_override_days` ≤ class max; defaults-with-override pattern per Argo `workflowDefaults` | High | https://argo-workflows.readthedocs.io/en/latest/default-workflow-specs/ |
| W2 | systemd user timer (daily, `Persistent=true`, randomized delay) → validator dry-run report; `--apply` stays manual + audit-logged; reject CI cron (unreliable + violates M8) | High | https://www.computingforgeeks.com/systemd-timers-linux/ + https://docs.github.com/actions/using-workflows/workflow-syntax-for-github-actions (schedule unreliability) |
| W3 | JSONL append-only, SHA-256 hash-chained records (seq/ts/actor/action/target/before/after/reason/prev_hash/entry_hash); audit-before-mutate; monthly rotation + chain-heads anchor; weekly verify | High | https://datatracker.ietf.org/doc/draft-melegassi-opsawg-mvps-logging/00/ |
| W4 | Pydantic v2 model over `yaml.safe_load`, `extra="forbid"`, Literal verdict enum, ISO datetime coercion; no new deps (pydantic 2.13.4 venv-verified) | High | https://www.sarahglasmacher.com/how-to-validate-config-yaml-pydantic |

---
*⬡ OMEGA ⬡ RESEARCHER ⬡ OVERSIGHT-WEB-LANE ⬡ 2026-08-23*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
