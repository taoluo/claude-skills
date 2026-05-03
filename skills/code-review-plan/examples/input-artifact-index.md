# Example: input artifact index

A small example showing what `code-review-plan` consumes. Continues the same router zero-active-suspend example used in `debug-log/examples/`, so a reader can trace one feature across both execution-stage skills (`debug-log` → `code-review-plan`).

## Scenario

The implementer has finished `BUG-001` (router zero-active suspend race) per the `debug-log` example. End-to-end smoke tests now pass. The team is ready to launch a parallel code-review pass before shipping.

## Input artifacts

- **Source plan**: `plans/miles-port-unified-plan.md` — the authoritative spec.
- **TLDR artifact**: `plans/miles-port-unified-plan.tldr.md` — present, used for `AC*` / `C*` / `D*` / `E*` / `M*` / `A*` anchor recovery.
- **Scope artifact**: `plans/miles-port-unified-plan.scope.md` — present, used to surface `P0-CORRECTNESS-FLOOR` items and identify any `NO-OVERENGINEERING` items that may have been accidentally implemented. `F*` IDs from this file appear only as optional navigation refs in shard `Scope categories / scope notes`, never as canonical anchors.
- **Debug log**: `plans/miles-port-unified-plan.debug.md` — present. `BUG-001` is the **resolved** router suspend race from the `debug-log` example, with `Verification: TEST_PASS — pytest tests/router/test_zero_active_suspend.py -q passed.` and **`Current status: PASSING`** in the debug-log header (this is the tests-passing evidence source that lets `code-review-plan` reach `Review readiness: READY` without the human needing to add a `"tests passing as of …"` string to the invocation note).
- **Code diff / changed files** (supplied via invocation note):
  - `miles/router/router.py` (the fix to `enable_worker`)
  - `tests/router/test_zero_active_suspend.py` (the new regression test)

## Sample invocation

```text
/code-review-plan @plans/miles-port-unified-plan.md "Changed files: miles/router/router.py, tests/router/test_zero_active_suspend.py. E2E green per debug-log Current status: PASSING. Round goal: correctness + recurrence review for the C20 contract before shipping."
```

## Expected resolution

- `<plan-stem>.review.md` does not yet exist → fresh write.
- All four sibling artifacts present and `present-current` → no freshness warnings.
- Tests-passing evidence: `debug-log Current status: PASSING` (the invocation note's mention is corroborating, not the primary source).
- Code diff supplied via the invocation note → present.
- High-risk constraint anchor: `C20` (router 0-active suspend contract) — the C20 area is the natural seed for the highest-priority shard.
- `BUG-001`'s `Follow-up:` field in `debug-log` ("Audit other state-mutating router endpoints (`disable_worker`, `set_worker_capacity`) for similar missing `notify_all` calls") seeds a recurrence-review shard.

## Plan anchors used in the example output

- `C20` — router 0-active suspend contract
- `AC13` — request resumes after enable_worker notifies _workers_changed
- `E14` — pytest test_zero_active_suspend covers the disable-all → wait → enable resume path

These align with the anchors used in the `debug-log` example so the two examples form a continuous walkthrough.

## What this example demonstrates

- The clean path: `Review readiness: READY` with `Blocking issues: none` and `Warnings: none`.
- Plan-anchor canonicality: shards cite `C20`, `AC13`, `E14`; `F*` scope IDs (if shown) are non-canonical navigation refs.
- The handoff from `debug-log` to `code-review-plan`: the debug log's `Current status: PASSING` is the tests-passing evidence; `BUG-001`'s `Follow-up:` field becomes a recurrence shard.
- Author Clarification clean-path: §1.1 contains `Author clarification: none required`; §1.2 has 1–2 illustrative non-blocking working assumptions.
