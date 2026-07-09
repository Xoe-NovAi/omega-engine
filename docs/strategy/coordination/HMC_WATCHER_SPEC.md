# 🔱 HMC Coordination Watcher Specification
**AP Token**: `AP-HMC-WATCHER-SPEC-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_coordination ⬡ SPEC

## 1. Overview
The `HMCWatcher` is a sovereign orchestration component designed to automate the Hivemind Mastermind Council (HMC) cycle. It eliminates the need for manual handoffs by monitoring the coordination directory for specific signal files.

## 2. Coordination Cycle
The watcher implements the following state machine:

`Researcher Brief` $\rightarrow$ `@john_carmack` (Synthesis) $\rightarrow$ `S_SYNTHESIS` $\rightarrow$ `@roc_racoon` (Coordination) $\rightarrow$ `ROC_RESULTS` $\rightarrow$ `User Notification`

## 3. Trigger Logic
| Signal File Pattern | Action | Target Entity |
|-------------------|--------|----------------|
| `*RESEARCHER_BRIEF*.md` | Trigger Synthesis | `@john_carmack` |
| `*S_SYNTHESIS*.md` | Trigger Coordination | `@roc_racoon` |
| `*ROC_RESULTS*.md` | Finalize Cycle | User / Hivemind |

## 4. Implementation Details
- **Monitoring**: Uses `anyio.Path.watch` for low-latency, event-driven filesystem monitoring.
- **Dispatch**: Uses `Oracle.summon` to inject tasks directly into the target agent's workflow.
- **Sovereignty**: Runs as a background process, independent of the main Oracle loop.

## 5. Verification
- **T7 (HMCWatcher)**: Verified via  (pending).
