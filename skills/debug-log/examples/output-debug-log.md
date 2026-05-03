# Debug Log

Feature: MILES → RLix port
Source plan: plans/miles-port-unified-plan.md
TLDR context: plans/miles-port-unified-plan.tldr.md
Scope context: plans/miles-port-unified-plan.scope.md (optional)
Current smoke target: tests/router/test_zero_active_suspend.py
Current status: PASSING

## 0. Session Summary

| Session | Date | Test target | Result | Bugs opened | Bugs resolved | Remaining blockers |
|---|---|---|---|---:|---:|---|
| SESSION-001 | 2026-05-03 | tests/router/test_zero_active_suspend.py | PASS | 1 | 1 | none |

## 1. Active Bugs

| Bug ID | Status | Class | Symptom | Root cause confidence | Blocking test | Plan anchors |
|---|---|---|---|---|---|---|

(none)

## 2. Resolved Bugs

| Bug ID | Class | Symptom | Root cause | Fix | Verification | Plan impact |
|---|---|---|---|---|---|---|
| BUG-001 | BUG-RACE-CONDITION | Router request hangs after all workers disabled | enable_worker mutated enabled_workers but did not notify _workers_changed | Added _workers_changed.notify_all() after enabled_workers mutation | TEST_PASS — pytest tests/router/test_zero_active_suspend.py -q passed. | NO_PLAN_CHANGE |

## 3. Bug Entries

### BUG-001: Router request hangs after all workers disabled

- Status: RESOLVED
- Class: BUG-RACE-CONDITION
- First observed: 2026-05-03 (SESSION-001)
- Repro / test command: `pytest tests/router/test_zero_active_suspend.py -q`
- Environment: branch `miles`, commit `7319df1`, single-node CPU runner
- Observed behavior: Router request times out after 30s when all workers are disabled and a new one is enabled. The test's `enable_worker` call returns successfully but the in-flight request never resumes.
- Expected behavior: Per C20 (router 0-active suspend contract), the request should suspend on `_workers_changed` and resume when `enable_worker` notifies the condition.
- Failure excerpt: `TimeoutError: request did not complete within 30s` raised at `tests/router/test_zero_active_suspend.py:42`.
- Root cause: `enable_worker` mutated `enabled_workers` but did not call `_workers_changed.notify_all()`. Suspended requests never woke.
- Root cause confidence: CONFIRMED_BY_TEST
- Fix: Added `_workers_changed.notify_all()` after `enabled_workers` mutation in `enable_worker`.
- Files changed: miles/router/router.py, tests/router/test_zero_active_suspend.py
- Verification: TEST_PASS — pytest tests/router/test_zero_active_suspend.py -q passed.
- Regression coverage: Added `test_zero_active_suspend_resume` covering the disable-all → wait → enable-one path.
- Plan anchors: C20, AC13, E14
- Related artifacts: miles-port-unified-plan.tldr.md current; miles-port-unified-plan.scope.md present, not used as anchor source
- Related bugs: (none)
- Plan impact: NO_PLAN_CHANGE
- Follow-up: Audit other state-mutating router endpoints (`disable_worker`, `set_worker_capacity`) for similar missing `notify_all` calls.

## 4. Retest Timeline

| Run | Command | Result | Related bugs | Notes |
|---|---|---|---|---|
| RUN-001 | pytest tests/router/test_zero_active_suspend.py -q | FAIL | BUG-001 | TimeoutError after 30s; surfaced BUG-001. |
| RUN-002 | pytest tests/router/test_zero_active_suspend.py -q | PASS | BUG-001 | Post-fix; both `test_zero_active_suspend` and `test_zero_active_suspend_resume` green. |

## 5. Plan Revision Suggestions

| Revision ID | Status | Triggered by bug | Source-plan gap | Suggested source-plan location | Rerun needed |
|---|---|---|---|---|---|

(none — BUG-001 was a pure implementation gap; C20 already specifies the contract.)

## 6. Remaining Risks

| Risk | Evidence | Suggested next action |
|---|---|---|
| Other state-mutating router endpoints may have the same missing `notify_all` pattern. | BUG-001 root cause was a missing `notify_all` in `enable_worker`; `disable_worker` and `set_worker_capacity` not yet audited. | Audit `disable_worker` and `set_worker_capacity`; if any are missing the notify, open new `BUG-*` entries. If audit reveals C20 should explicitly enumerate the endpoints requiring `notify_all`, open a §5 Plan Revision Suggestion with `Plan impact: PLAN_CONSTRAINT_MISSING`. |
