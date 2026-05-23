# 🔱 Phase C — Community-Ready Presentation  
## Execution Plan

⬡ OMEGA ⬡ SOPHIA ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_strategic ⬡ PHASE-C  
**Gate**: A stranger can understand, install, and use Omega in 10 minutes.  
**Current Status**: 🔴 All tasks open  
**Executor**: Gemma 4 31B (Builder mode) — I review and approve  

---

## Dependency Graph

```
C4 (Prune docs) ──┐
                   ├──→ C1 (README rewrite) ──→ C2 (Demo) ──→ Gate
C5 (QUICKSTART) ──┘
                      C3 (Changelog) ─── independent
                      C6 (CI/CD) ─────── independent
```

C4 + C5 must finish before C1. C2 needs C1. C3 and C6 are independent.

---

## Task C4 — Prune docs/research/ [4h]

**Goal**: Move internal-only research documents to `docs/archives/` so the public face of the project isn't cluttered with raw research.

**Step 1 — Categorize all files in `docs/research/`**

Keep (public-facing, useful to a new user):
| File | Why Keep |
|------|----------|
| `FREE_TIER_MODEL_INDEX.md` | Practical — which free models to use |
| `R00_opencode_best_practices.md` | Relevant for IDE users |
| `R01_google_api_reference.md` | Provider guide |
| `R02_sambanova_spec.md` | Provider guide |
| `R03_cerebras_spec.md` | Provider guide |
| `R04_fallback_chain_design.md` | Architecture doc |
| `R05_model_capability_matrix.md` | Practical reference |
| `R25_gemma_free_terms.md` | Important for Gemma users |
| `R-MAKALI-SYNC` link | Core architecture |
| `R-JEM-CUSTOM-MODE.md` | Custom mode documentation |
| `R_OPENC_MCP_CONFIG.md` | Practical MCP guide |
| `R_OPENC_PERMISSIONS.md` | Practical permission guide |
| `model_db/CURRENT_MODELS.md` | Always-current reference |

Archive (internal reasoning, not useful to strangers):
Everything else — ~140 research docs, patterns, legacy analyses, internal architecture designs.

**Step 2 — Move archived files**
```bash
mkdir -p docs/archives/research
for f in docs/research/*.md; do
  if [ "$f" is not in the keep list ]; then
    mv "$f" docs/archives/research/
  fi
done
```

**Step 3 — Rewrite INDEX.md** to only show public-facing items.

**Step 4 — Add a header to INDEX.md**: *"Research archive moved to `docs/archives/research/`. Contact the Foundation for the full index."*

---

## Task C5 — Write QUICKSTART.md [1h]

**Goal**: A new user can install and chat with Omega in 5 commands.

```markdown
# 🔱 Omega Engine — Quick Start

## Prerequisites
- Python 3.12+
- Git
- (Optional) LM Studio or Ollama for local inference

## Install
```bash
git clone https://github.com/Xoe-NovAi/omega-engine.git
cd omega-engine
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Test
```bash
make test   # 230 tests should pass
```

## Chat
```bash
omega talk "What is the Omega Engine?"
omega summon SOPHIA "What is the Akashic Record?"
```

## Customize
See `docs/guides/CUSTOMIZATION.md` for entity creation, WAD stacks, and voice setup.

## Next Steps
- `docs/ROADMAP.md` — full project vision
- `docs/guides/` — customization, provider setup, VR
```

**Files to create**: `docs/guides/QUICKSTART.md`  
**Reference**: existing `README.md` (will be rewritten in C1)

---

## Task C4+C5 Complete → Task C1 — Rewrite README.md [4h]

**Goal**: 60 seconds to understand what Omega is and whether you want it.

**Structure**:
```
README.md
├── Tagline (1 line)
├── What is Omega? (3 sentence elevator pitch)
├── Quick Start (5 commands — embed from QUICKSTART.md)
├── Architecture (one ASCII diagram — the pillar template)
├── Key Features (bullet list — local-first, multi-provider, entity system)
├── Who is this for? (tinkerers, AI enthusiasts, privacy advocates)
├── Project Status (Phase C — Community-Ready)
├── Contributing (link to CONTRIBUTING.md)
├── License (MIT)
└── Foundation (Xoe-NovAi link)
```

**Key constraints**:
- No internal jargon that hasn't been defined (e.g., "MaKaLi" gets a footnote)
- No mention of "Omegaverse" or "42 Ideals" — those are stack-specific, not engine
- No raw research docs linked
- All URLs in the README must resolve

---

## Task C2 — Record asciinema Demo [2h]

**Goal**: A 3-minute terminal recording showing the sovereign loop.

**Script**:
```bash
# 1. Install and test (10s)
git clone https://github.com/Xoe-NovAi/omega-engine.git && cd omega-engine
pip install -e ".[dev]"
make test --quiet

# 2. Start the REPL (10s)
omega repl

# 3. Talk to an entity (30s)
/entity SOPHIA
omega talk "What is the Omega Engine?"

# 4. Summon a specific entity (20s)
omega summon LILITH "What is sovereignty?"

# 5. Show transient mode (10s)
/transient
omega talk "This won't be saved"

# 6. Show help (10s)
omega --help

# Exit (5s)
/exit
```

**Tool**: `asciinema rec omega-demo.cast`  
**Output**: Link the cast file in README.md and CONTRIBUTING.md  

---

## Task C3 — Clean Changelog [2h]

**Goal**: A single accurate `CHANGELOG.md` that tells the story, not every commit.

```
# Changelog

## Phase C — Community-Ready (2026-05)

### Added
- Sovereign Loop: Query → TriageRouter → ModelGateway → Response → Memory → Soul Update
- Interactive REPL with slash commands
- Health Monitor with circuit breakers
- Dynamic Inference Protocol (temperature/context window now model-native)
- MaKaLi Trine governance (Kali → Ma'at → Lilith)

### Fixed
- Provider Fabric: Google API key env var, openrouter wiring, lmster double-slash URL
- 8 critical runtime bugs from R-44 audit
- YAML schema corruption in entities.yaml
- All 230 tests passing

### Changed
- Gemma 4 31B is now the primary workhorse (unlimited Google AI Studio tier)
- DeepSeek V4 Flash reserved for strategic architecture
- Session headers now auto-generated by ICS middleware
```

---

## Task C6 — Verify CI/CD [1h]

**Goal**: `.github/workflows/ci.yml` runs `make test` and `make lint` on every push.

**Checklist**:
```bash
# Simulate CI locally
OMEGA_ENV=test PYTHONPATH=src python3 -m pytest tests/ --tb=short -q
# Expect: 230 passed

flake8 src/omega/ --count --select=E9,F63,F7,F82 --show-source --statistics
# Expect: 0 errors
```

**If CI is green**: Update the badge in README.md: `[![CI](https://github.com/Xoe-NovAi/omega-engine/actions/workflows/ci.yml/badge.svg)](...)`  
**If CI is red**: Fix the pipeline before any other Phase C task.

---

## Gate Checklist

Before signing off Phase C:

```markdown
- [ ] README.md — rewritten, jargon-free, 60-second understanding
- [ ] QUICKSTART.md — 5 commands, zero to chat
- [ ] asciinema demo — recorded, linked in README
- [ ] CHANGELOG.md — clean, accurate, one entry per phase
- [ ] docs/research/ — pruned to public-facing only
- [ ] CI/CD — green on GitHub
- [ ] `make test` — 230/230
- [ ] `make lint` — 0 errors (cosmetic warnings OK)
- [ ] A stranger can install and chat in ≤10 minutes (verified by fresh clone test)
```

---

*Plan approved by Overseer. Gemma to execute in order: C4 → C5 → C1 → C2 → C3 → C6.*
