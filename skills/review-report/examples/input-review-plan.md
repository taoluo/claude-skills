# Code Review Plan

Feature: MILES → RLix port — router zero-active suspend
Source plan: plans/miles-port-unified-plan.md
TLDR artifact: plans/miles-port-unified-plan.tldr.md
Scope artifact: plans/miles-port-unified-plan.scope.md (optional)
Debug log: plans/miles-port-unified-plan.debug.md (optional)
Code diff / changed files: miles/router/router.py, tests/router/test_zero_active_suspend.py
Review readiness: READY

> **Example input for `review-report`.** This is a condensed `<plan-stem>.review.md` produced by `code-review-plan`. The full version would have all 10 sections (`§0`–`§9`); this example shows just §6 Subagent Assignment Plan in detail since that's what `review-report` consumes for fan-out, plus enough §3 / §4 / §5 / §7 / §8 context for each subagent's bounded prompt.
>
> Continues the router zero-active-suspend story from the `debug-log` and `code-review-plan` examples.

## 0. Review Dashboard

- Review readiness: `READY`
- Blocking issues: none
- Warnings: none
- Tests-passing evidence: `debug-log Current status: PASSING`
- Code diff / changed files: present
- Author clarification: 0

## 3. Feature Review Matrix

| Review ID | Feature / area | Plan anchors | Scope categories | Debug bugs | Review angles | Priority | Suggested reviewer |
|---|---|---|---|---|---|---|---|
| R01 | Router zero-active suspend correctness | C20, AC13, E14 | P0-CORRECTNESS-FLOOR (F39) | BUG-001 (resolved) | PLAN_ADHERENCE_REVIEW, CORRECTNESS_REVIEW, CONCURRENCY_RACE_REVIEW, ADVERSARIAL_INVARIANT_REVIEW, DEBUG_REGRESSION_REVIEW | high | Subagent A |
| R02 | Startup fail-fast constraints | C5, C7, AC4 | P0-CORRECTNESS-FLOOR | (none) | PLAN_ADHERENCE_REVIEW, ERROR_HANDLING_FAIL_FAST_REVIEW | medium | Subagent B |
| R03 | Debug-log recurrence: state-mutating router endpoints | C20, D7, M11.2 | P0-CORRECTNESS-FLOOR | BUG-001 follow-up | DEBUG_REGRESSION_REVIEW, CONCURRENCY_RACE_REVIEW, ADVERSARIAL_INVARIANT_REVIEW | high | Subagent C |

## 4. Parallel Review Shards (condensed for example)

### R01: Router zero-active suspend correctness
- Goal: Verify C20 contract is implemented correctly and BUG-001 fix is robust under adversarial sequences.
- Must-read anchors: C20, AC13, E14
- Code areas to inspect: miles/router/router.py (enable_worker, disable_worker, _workers_changed condition variable, request waiter loop), tests/router/test_zero_active_suspend.py
- Review angles: PLAN_ADHERENCE_REVIEW, CORRECTNESS_REVIEW, CONCURRENCY_RACE_REVIEW, ADVERSARIAL_INVARIANT_REVIEW, DEBUG_REGRESSION_REVIEW

### R02: Startup fail-fast constraints
- Goal: Verify startup-time C* constraints are enforced fail-fast (not silently degraded).
- Must-read anchors: C5, C7, AC4
- Code areas to inspect: miles/router/router.py (init, validate, bind)
- Review angles: PLAN_ADHERENCE_REVIEW, ERROR_HANDLING_FAIL_FAST_REVIEW

### R03: Debug-log recurrence — state-mutating router endpoints
- Goal: Audit other state-mutating router endpoints (disable_worker, set_worker_capacity) for the same notify_all gap that caused BUG-001.
- Must-read anchors: C20, D7, M11.2
- Code areas to inspect: every function in miles/router/router.py that mutates enabled_workers / worker_capacity / related router state
- Review angles: DEBUG_REGRESSION_REVIEW, CONCURRENCY_RACE_REVIEW, ADVERSARIAL_INVARIANT_REVIEW

## 5. Adversarial Review Prompts (condensed)

### R01
1. What if a request waiter starts waiting on _workers_changed *between* disable_worker completing and enable_worker mutating enabled_workers?
2. What if enable_worker mutates state but the notify_all() call raises?
3. What if disable_worker and enable_worker are called concurrently?

### R03
1. What if disable_worker mutates enabled_workers but does NOT notify?
2. What if set_worker_capacity(0) is functionally equivalent to disabling but lacks notify_all?

## 6. Subagent Assignment Plan

| Subagent | Shards | Required inputs | Output file | Independence notes | Estimated effort | Status |
|---|---|---|---|---|---|---|
| Subagent A | R01 | PLAN.md (C20, AC13, E14); router.py; test_zero_active_suspend.py; BUG-001 entry | review-report/R01.md | Independent | ~25 min | READY |
| Subagent B | R02 | PLAN.md (C5, C7, AC4); router.py startup paths | review-report/R02.md | Independent of R01/R03 | ~20 min | READY |
| Subagent C | R03 | PLAN.md (C20, D7, M11.2); router.py state-mutating endpoints; BUG-001 follow-up | review-report/R03.md | Independent | ~20 min | READY |

All shards required (no `Optional: yes` annotations).

## 7. Subagent Report Template

(Embedded verbatim — see `code-review-plan/references/output-layout.md` §7 for canonical version. Each subagent copies this template and fills it in.)

## 8. Final Aggregation Contract

(Embedded verbatim — see `code-review-plan/references/aggregation-contract.md`.)

## 9. Review Execution Checklist

- [x] All §6 rows have `Status: READY`.
- [ ] Each subagent has been briefed.
- [ ] Aggregator has the §8 contract.
- [ ] Reviewers know to surface PLAN_REVISION_NEEDED via the report contract.
