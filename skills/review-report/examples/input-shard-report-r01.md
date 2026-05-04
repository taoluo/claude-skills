# Review Shard Report

Shard ID: R01
Shard title: Router zero-active suspend correctness review
Reviewer: Subagent A
Inputs reviewed: plans/miles-port-unified-plan.md (C20, AC13, E14 sections), plans/miles-port-unified-plan.review.md (R01 spec), plans/miles-port-unified-plan.debug.md (BUG-001 entry)
Code areas reviewed: miles/router/router.py (enable_worker, disable_worker, remove_worker, _workers_changed condition variable, request waiter loop), tests/router/test_zero_active_suspend.py
Plan anchors: C20, AC13, E14
Debug-log bugs reviewed: BUG-001 (resolved 2026-05-03 — TEST_PASS verified)
Review angles: PLAN_ADHERENCE_REVIEW, CORRECTNESS_REVIEW, CONCURRENCY_RACE_REVIEW, ADVERSARIAL_INVARIANT_REVIEW, DEBUG_REGRESSION_REVIEW

## Verdict

`NEEDS_FIX`

## Findings

| Finding ID | Severity | Type | Title | Plan anchors | Code area | Evidence | Recommendation |
|---|---|---|---|---|---|---|---|
| R01-01 | HIGH | RACE | `remove_worker` mutates state without notifying `_workers_changed` | C20, AC13 | miles/router/router.py:217 | `remove_worker` pops from `enabled_workers` without acquiring the condition or calling `notify_all`; no test exercises remove_worker mid-suspend | Add `_workers_changed.notify_all()` under condition lock; add regression test |

## Detailed Findings

### R01-01: `remove_worker` mutates state without notifying `_workers_changed`

#### Background

The router zero-active suspend path (C20) prevents requests from failing or spinning when workers are temporarily disabled during runtime shrink/expand. The plan validates this through AC13 / E14, and BUG-001 already fixed one missing notify path in `enable_worker`, so all worker-state mutation paths are recurrence-sensitive. The R01 shard's `DEBUG_REGRESSION_REVIEW` angle specifically asked the reviewer to look for the same class of bug elsewhere.

#### Expected behavior / invariant

Every state-mutating router endpoint that changes worker availability MUST notify `_workers_changed` so blocked request waiters can re-check the predicate. This is the implicit invariant of C20 — if a request is blocked waiting on `_workers_changed` and a state mutation makes the wait condition newly false, the waiter must be woken.

#### Finding

`remove_worker` mutates active worker state but does not call `_workers_changed.notify_all()`.

#### Evidence

- `miles/router/router.py:217` — `remove_worker` pops from `enabled_workers` without acquiring `_workers_changed` or notifying.
- `tests/router/` — no test exercises `remove_worker` mid-suspend; the regression test from BUG-001 only covers `enable_worker`.
- Code search confirms `remove_worker` is the only state-mutating router endpoint not covered by `notify_all` (ignoring the BUG-001-fixed `enable_worker`).

#### Impact

Requests blocked waiting for worker availability when `remove_worker` is called concurrently with worker disable will hang until the next state mutation that does notify (or the test timeout). This is a recurrence of BUG-001's class, just on a different endpoint.

#### Recommended action

Add `_workers_changed.notify_all()` under the condition lock at `miles/router/router.py:217`. Add a regression test analogous to `test_zero_active_suspend_resume` covering the disable-then-remove path. Consider auditing whether C20 should be revised to explicitly enumerate the endpoints requiring `notify_all` (this would prevent future recurrence at the spec level).

#### Routing

- Debug-log update: open `BUG-002`, Class: `BUG-RACE-CONDITION`, Plan impact: `NO_PLAN_CHANGE`.
- PLAN.md revision: none. (Optional follow-up consideration: revise C20 to enumerate the endpoints — but that's a `MAINTAINABILITY` improvement, not a correctness gap.)
- Rerun needed: none.

## Evidence Gaps

(none)

## Adversarial Checks

| Check | Result | Evidence |
|---|---|---|
| What if a request waiter starts waiting on _workers_changed *between* disable_worker completing and enable_worker mutating enabled_workers? | PASSED | enable_worker now correctly acquires the condition before mutating + notifies after (BUG-001 fix verified at miles/router/router.py:198-204). |
| What if enable_worker mutates state but the notify_all() call raises? | PASSED | notify_all is called inside the with-statement; if it raises, the lock is still released. The waiter would be stuck for one suspended duration but the next legitimate notify wakes it. Acceptable per C20. |
| What if disable_worker and enable_worker are called concurrently? | PASSED | Both acquire `_workers_changed` before mutation; serialized correctly. |

## Reviewer Notes

R01-01 is the only HIGH finding from this shard. The C20 contract itself appears correctly implemented; the gap is at a sibling endpoint not explicitly named in C20. R03 (recurrence-review) was assigned to widen the audit — its findings should be cross-referenced with R01-01 in aggregation.
