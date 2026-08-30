
## N3 INST-1 Fresh-Venv Acceptance Run (2026-08-24)

**L1 (Narrative)**: Executed the fresh-venv acceptance gate I amended. unshare -rn was blocked by host seccomp → substituted bwrap --unshare-net. First clean-room install crashed twice at import (aiofiles, then opentelemetry-sdk) — both masked on this machine by transitive installs (Crawl4AI, otlp-exporter). Fixed both in core deps (d16558c7), rebuilt clean venv, talk went green inside no-network sandbox with all keys unset. Trace receipts confirmed provider_name=native-gguf.

**L2 (Insight)**: Environment drift doesn't just hide breakage — it hides it TRANSITIVELY. A dep you never declared arrives as someone else's dependency, so even "grep pyproject for X" audits miss the gap. Only a cold-room install enumerates the true core closure. The fresh-venv gate isn't a packaging nicety; it's the only honest dependency census we have.

**L3 (Universal Principle)**: *A system's real dependencies are defined by what a cold room requires, not by what a warm machine tolerates.* Every acceptance gate that runs on a long-lived environment measures the environment, not the system.
