# The Well — Injection Design

How active corrections reach an agent's system prompt, and why it is built the way it
is. Implementation: `scripts/well_storage.py`, tests: `tests/test_well_injection.py`.

The Well exists because of a specific failure: corrections were stored but never
delivered at the moment they mattered, so agents re-derived the same traps every
session. Injection is the fix.

---

## 1. Why injection at all

Alternatives considered and rejected:

| Option | Why not |
|---|---|
| Put everything in `AGENTS.md` | Instruction count degrades adherence **uniformly**. HumanLayer's summary of the research: frontier models follow ~150–200 instructions reliably, and Claude Code's system prompt already spends ~50 of them before you add anything. Bloating the always-loaded file degrades the rules you already had. |
| A `rules.md` agents read on demand | Optional reading is optional. A correction that is *available* is not a correction that is *applied*. The P-core pin trap stayed violated for weeks because nothing forced it into context. |
| Recall from past sessions at runtime | Good for "what did we decide about X", wrong for "do not do this again". The recall stack (`ochist`) answers the first; only injection answers the second. |

## 2. The budget-before-retrieve rule

The most important design constraint, from research on memory systems
(<https://machinelearningmastery.com/ai-agent-memory-design-what-works-and-what-doesnt/>):

> "A memory search returns a set of relevant entries, and the context assembler injects
> all of them into the prompt. As more memories are added, the context window gradually
> fills... The resulting symptoms are often misleading: retrieval quality appears high,
> relevant memories are successfully found, system performance still degrades. In many
> cases the memory system has done its job correctly. The failure occurs because context
> assembly lacks a budgeting mechanism."

The fix is **retrieval-aware context assembly** — allocate the budget *before*
retrieving, then retrieve only what fits:

```python
async def retrieve_for_step(self, step, max_tokens: int) -> str:
    candidates = await self.memory.search(...)   # fills a KNOWN budget
```

Applied here: selection is budget-capped during injection, not truncated after.
A Well that grows unbounded would degrade every session it touches.

## 3. Selection

An injected record is chosen by **trigger match**, not recency. Weighting:

- **Domain match** — the record's `domain` vs the session's domain
- **Trigger specificity** — a tight trigger beats a broad one
- **Pack membership** — packs are the curation unit (see `gnosis/well/WISDOM.md`)

An empty or oversized corpus must degrade to *nothing injected*, never to a partial
or malformed block. Both edges are covered in `tests/test_well_injection.py`.

## 4. Conflict resolution

The Well can contradict `AGENTS.md`. When it does:

**Well wins.** Rationale: `AGENTS.md` is static and written by a human at one moment;
the Well is a correction to a mistake that was *observed to happen*. A correction
earned by observation outranks an instruction written in the abstract.

The current `AGENTS.md` cites the two Well records directly (`3becf4f3`, `a3675a88`)
so an agent can check the reasoning rather than obey an unexplained command.

## 5. Known gap: nobody measures whether a correction worked

A research hit worth acting on — AgentRecall-X is described as:

> "A measurement instrument — the only open-source system that tracks whether a
> correction actually changed what the agent does in a later session. Every correction
> accumulates retrieved_count, and every time the agent encounters the same situation,
> the outcome is recorded (heeded or recurred)."
> — <https://github.com/goldentrii/agentrecall-x>

The Well currently records that a correction was *injected*. It does not record
whether the agent then **obeyed** it. A correction that is injected 40 times and
violated 39 times is worse than no correction: it costs context and teaches agents
that this document can be ignored.

Proposed, not built — fields to add to `well.jsonl`:

```json
"retrieved_count": 12,
"last_retrieved": "2026-10-01T00:00:00Z",
"outcomes": [ {"ts": "...", "session": "ses_...", "result": "heeded|recurred"} ]
```

A record with a high recur-rate and a clear trigger is a *bad trigger* — fix the
trigger wording or retire the record. That loop does not exist yet.

## 6. Memory poisoning — the threat model

Unit 42 documented cross-session injection: an indirect prompt injection on a webpage
contaminates an agent's cross-session memory, and the stored summary is re-injected
as part of the system prompt in later sessions.

Direct implications for this system:

1. **The Well must only ever contain operator-approved text.** Corrections are seeded
   deliberately via `make well-add`, never harvested from transcripts automatically.
2. **Provenance is mandatory.** Every record carries `source_file` and `ts`; a
   correction with no provenance is a candidate for rejection.
3. **Records are the highest-leverage injection point in the whole harness.** Anything
   that can write a Well record can influence every future session on the machine.
   Treat `gnosis/well/well.jsonl` with the same care as a secrets file.

Note that `gnosis/well/` is gitignored yet `well.jsonl` and `WISDOM.md` are already
**tracked**. Git's ignore rule does not apply to tracked files, so this is a
one-time condition rather than a conflict — but it means Well edits commit even
though the directory looks ignored. Verified, not assumed.

## 7. Files

| Path | Role |
|---|---|
| `gnosis/well/well.jsonl` | The corpus. Append-only, one JSON record per line |
| `gnosis/well/WISDOM.md` | Curated index / packs that group records |
| `scripts/well_storage.py` | Loading, selection, budget, injection |
| `tests/test_well_injection.py` | 183 lines — selection, truncation, empty/oversized |
| `make well-add` | Seed a record (requires explicit TRIGGER/RULE/RATIONALE) |
| `make well-list` / `well-show ID=` | Inspect |