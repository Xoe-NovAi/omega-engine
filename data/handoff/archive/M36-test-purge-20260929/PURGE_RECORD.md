# PIVOT_LOG — M36 test-spam purge
date: 2026-09-29
authorised_by: Architect (explicit instruction: 'if it's just test spam, delete those')
scope: data/handoff/pending/*.json whose task field contains 'CROSS-VALIDATOR'
count_deleted: 42
queue_before: 66   queue_after: 22
basis: all 42 were M36 cross-validator stubs, 3 targeting /nonexistent/deliverable.md;
       zero referenced a real repo path. Test traffic, not work.
restore: re-run the M36 harness with a test-only queue; these carry no work product.

deleted:
