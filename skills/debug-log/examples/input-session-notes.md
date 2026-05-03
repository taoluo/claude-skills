# Example: input session notes

A short worked example demonstrating how a smoke-test debugging session feeds `debug-log`.

The session's source plan is the (real) `plans/miles-port-unified-plan.md`. The example uses plan anchors that align with the C20 router 0-active suspend contract added in commit `7319df1`.

## Scenario

The implementer is running the M11 router smoke tests. One test, `tests/router/test_zero_active_suspend.py`, is timing out. Three chat events feed `debug-log` over the course of one session.

## Event 1 — failure observed

User invokes:

```text
/debug-log @plans/miles-port-unified-plan.md "smoke test failed: tests/router/test_zero_active_suspend.py — TimeoutError after 30s. Test disables all workers, then enables one, expects request to resume."
```

Expected `debug-log` behavior:

- Resolve sibling artifacts: `miles-port-unified-plan.tldr.md` (present), `miles-port-unified-plan.scope.md` (present, optional).
- File `miles-port-unified-plan.debug.md` does not exist yet — create it with Write.
- Open `BUG-001` with `Status: OPEN`, `Class: BUG-INTEGRATION` (initial classification; may transition to `BUG-RACE-CONDITION` once root cause is known).
- Plan anchors: search the source plan / TLDR for the C20 zero-active-suspend contract. Record `C20, AC13, E14` if found; otherwise `unknown`.
- Open `SESSION-001` row in §0 with today's date.
- Write `RUN-001` row in §4 with the failing pytest command.

## Event 2 — root cause suspected

A short while later, the user reads the router code and pastes a hypothesis:

```text
/debug-log @plans/miles-port-unified-plan.md "BUG-001 root cause hypothesis: enable_worker mutates enabled_workers but does not call _workers_changed.notify_all(). Other endpoints (disable_worker, set_worker_capacity) likely have the same gap."
```

Expected `debug-log` behavior:

- Read existing `miles-port-unified-plan.debug.md`; recover `BUG-001` ID.
- Apply Conservative merge rule — same component (`enable_worker`), same plan anchors (C20), same symptom (timeout). ≥2 signals match → update existing `BUG-001`, do NOT create `BUG-002`.
- Patch `BUG-001` via Edit:
  - `Status: ROOT_CAUSE_SUSPECTED`
  - `Root cause: enable_worker updates enabled_workers but does not notify _workers_changed`
  - `Root cause confidence: MEDIUM`
- Append a §6 Remaining Risks row noting the broader audit risk (other state-mutating endpoints).
- Do NOT create a §5 Plan Revision Suggestion yet — the user has not confirmed whether C20 explicitly requires `notify_all` on every mutation. The skill records `Plan impact: NO_PLAN_CHANGE` as the working assumption and surfaces the audit risk in §6 instead.

## Event 3 — fix applied and verified

After the user implements the fix and reruns the test:

```text
/debug-log @plans/miles-port-unified-plan.md "BUG-001 fixed: added _workers_changed.notify_all() after enabled_workers mutation in miles/router/router.py. Added regression test test_zero_active_suspend_resume in tests/router/test_zero_active_suspend.py covering the disable-all → wait → enable-one path. Both tests pass."
```

Expected `debug-log` behavior:

- Read existing log; recover `BUG-001`.
- Patch `BUG-001`:
  - `Status: RESOLVED`
  - `Root cause confidence: CONFIRMED_BY_TEST`
  - `Fix: Added _workers_changed.notify_all() after enabled_workers mutation in enable_worker.`
  - `Files changed: miles/router/router.py, tests/router/test_zero_active_suspend.py`
  - `Verification: TEST_PASS — pytest tests/router/test_zero_active_suspend.py -q passed.`
  - `Regression coverage: Added test_zero_active_suspend_resume covering disable-all → wait → enable-one path.`
  - `Plan impact: NO_PLAN_CHANGE`
  - `Follow-up: Audit other state-mutating router endpoints (disable_worker, set_worker_capacity) for similar missing notify_all calls.`
- Move `BUG-001` row from §1 Active Bugs to §2 Resolved Bugs.
- Append `RUN-002` to §4 Retest Timeline (`PASS`, `Related bugs: BUG-001`).
- Update `SESSION-001` in §0: `Bugs resolved: 1`, `Result: PASS`.
- Keep §6 Remaining Risks row (the broader audit risk survives the fix).

## What the example demonstrates

- The append-only pattern: three events, one growing artifact, `BUG-001` updated in place across two of them.
- The Conservative merge rule: Event 2 merges into Event 1; if Event 2 had landed in a different component, it would have opened `BUG-002` instead.
- Verification evidence type: `TEST_PASS` with a one-line evidence string.
- Plan-anchor-only linking: `C20`, `AC13`, `E14` from the source plan; **no `F*` scope anchors** even though the scope artifact is present. The scope artifact is acknowledged via `Related artifacts:` only.
- An empty §5 Plan Revision Suggestions: this scenario is the common case where the plan was correct and the bug was an implementation gap.
- A non-empty §6 Remaining Risks: the broader "audit other endpoints" concern survives the resolved bug.
