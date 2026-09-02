<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 🗺️ Omega Engine — Public Roadmap

> **Prometheus' Fire** — A universal, community-owned runtime for sovereign AI.

This is the public-facing roadmap for the Omega Engine. For detailed internal planning, see the source documentation in the repository. Dates are aspirational and may shift as the project evolves.

---

## 🎯 Vision

A sovereign AI runtime that runs **entirely on your hardware**, with **zero cloud dependency**, that gives you **full ownership of your data, your models, and your stack**.

We believe AI should be:
- **Local-First**: Your data never leaves your machine
- **Sovereign**: You own your stack, your keys, your models
- **Community-Owned**: Built by and for the people who use it
- **Interoperable**: Works with the models and tools you already use

---

## ✅ Released

### v1.6.0 — Public Debut (2026-09)
- First public release under Apache 2.0
- Native local inference (GGUF models, CPU/GPU)
- 14-agent orchestration fleet
- Sovereign memory layer (SQLite-vec)
- Hivemind P2P coordination
- Sovereign WAD protocol
- Document reader (DOCX, PDF, ODT, RTF, HTML, MD, TXT, JSON, YAML)
- One-click installer (`scripts/install.sh`)

### v1.5.0 — Heritage Registry (2026-07)
- Third-party repository registry (18/19 repos)
- Heritage vetting pipeline
- Sovereign Sieve (web research)

---

## 🔨 In Progress

### v1.7.0 — Hardening & Stability (Q4 2026)

| Ticket | Description | Status |
|--------|-------------|--------|
| H-1 | Fix `omega.library` import (broken in D-565 cleanup) | 🟡 P0 |
| H-2 | CI test suite green on all Python 3.12/3.13 | 🟡 P0 |
| H-3 | Allowlist enforcement on `main` branch | 🟡 P1 |
| H-4 | Mandate compliance hardening (M1-M37) | 🟢 Ongoing |
| H-5 | REUSE v3.3 compliance for all files | 🟢 Ongoing |

### v1.8.0 — Knowledge Domains (Q4 2026)

| Ticket | Description | Status |
|--------|-------------|--------|
| KD-1 | Runtime knowledge domain modules | 🟡 Planned |
| KD-2 | Domain curator model | 🟡 Planned |
| KD-3 | Knowledge domain discovery | 🟡 Planned |

### v1.9.0 — Local Inference Optimization (Q1 2027)

| Ticket | Description | Status |
|--------|-------------|--------|
| LI-1 | Sequential model loading | 🟡 Planned |
| LI-2 | Adaptive context window management | 🟡 Planned |
| LI-3 | Multi-model orchestration | 🟡 Planned |

---

## 🔮 Future

### v2.0.0 — Scholarly Research (Q1 2027)

| Ticket | Description | Status |
|--------|-------------|--------|
| SR-1 | Multi-agent research delegation | 🔵 Backlog |
| SR-2 | Citation intelligence (CitationAgent) | 🔵 Backlog |
| SR-3 | Sovereign knowledge persistence (SSKB) | 🔵 Backlog |
| SR-4 | Free academic API integration (OpenAlex, Crossref) | 🔵 Backlog |

### v2.1.0 — Documentation System (Q2 2027)

| Ticket | Description | Status |
|--------|-------------|--------|
| DS-1 | Modular domain documentation | 🔵 Backlog |
| DS-2 | LLM-friendly doc generation | 🔵 Backlog |
| DS-3 | Living documentation pipeline | 🔵 Backlog |

### v2.2.0 — Headroom Integration (Q2 2027)

| Ticket | Description | Status |
|--------|-------------|--------|
| HR-1 | Semantic compression for tools | 🔵 Backlog |
| HR-2 | Semantic compression for RAG | 🔵 Backlog |
| HR-3 | Headroom-aware scheduling | 🔵 Backlog |

### v2.3.0 — Zswap Subsystem (Q3 2027)

| Ticket | Description | Status |
|--------|-------------|--------|
| ZS-1 | 16GB NVMe swap configuration | 🔵 Backlog |
| ZS-2 | Zswap-enabled kernel parameters | 🔵 Backlog |
| ZS-3 | Memory pressure monitoring | 🔵 Backlog |

### v3.0.0 — Heritage 2.0 (Q4 2027)

| Ticket | Description | Status |
|--------|-------------|--------|
| H2-1 | Full heritage registry public mirror | 🔵 Backlog |
| H2-2 | Heritage-aware model selection | 🔵 Backlog |
| H2-3 | Heritage citation system | 🔵 Backlog |

---

## 🤝 Community Contributions

We welcome contributions in these areas:

| Area | Skills Needed | How to Help |
|------|---------------|-------------|
| Documentation | Writing, technical docs | See [CONTRIBUTING.md](CONTRIBUTING.md) |
| Testing | QA, pytest | Look for `good first issue` label |
| Translations | i18n | Help localize docs and UI |
| Heritage Vetting | C/C++/Rust, game dev | Review third-party repos |
| Model Adapters | Python, ML | Add support for new model formats |
| Integrations | API design | Connect Omega to your favorite tools |

---

## 📊 Release Cadence

- **Minor versions** (v1.x.0): Every 4-6 weeks
- **Patch versions** (v1.6.x): As needed for bugs
- **Major versions** (v2.0.0): Every 12-18 months

We follow [Semantic Versioning](https://semver.org/).

---

## 🗣️ How to Influence the Roadmap

1. **Open an issue** with the `enhancement` label
2. **Join the discussion** in [GitHub Discussions](https://github.com/Xoe-NovAi/omega-engine/discussions)
3. **Submit a PR** that implements a roadmap item
4. **Review PRs** — your feedback shapes what ships

---

## 📜 License

This roadmap is released under [Apache 2.0](LICENSE). The Omega Engine itself is also Apache 2.0.

---

*⬡ OMEGA ⬡ PROMETHEUS ⬡ community ⬡ ROADMAP*
