# Code Review Report

Feature: MILES → RLix port — router zero-active suspend
Source plan: plans/miles-port-unified-plan.md
Review plan: plans/miles-port-unified-plan.review.md
Debug log: plans/miles-port-unified-plan.debug.md
Shard reports: plans/miles-port-unified-plan.review-report/
Report readiness: INCOMPLETE

## 0. Decision Summary

- Final recommendation: `BLOCKED`
- Main reason: incomplete review coverage — R03 (recurrence-review shard) missing; R01 also surfaced HIGH recurrence risk in `remove_worker` that the human should address regardless of R03 outcome.
- Report readiness: `INCOMPLETE`
- Shards completed: 2 of 3 (missing: R03; malformed: none)
- Findings: 0 BLOCKER, 1 HIGH, 1 MEDIUM, 0 LOW, 0 NOTE
- Evidence gaps: 1
- Reruns recommended: none
- Debug-log updates suggested: 1
- PLAN.md revisions suggested: 0

## 1. Blocking Findings

(none from finding-level severity; the `BLOCKED` recommendation is driven by missing required shard R03 — see §0 Main reason and §3 Evidence Gaps.)

## 2. High Findings

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

Add `_workers_changed.notify_all()` under the condition lock at `miles/router/router.py:217`. Add a regression test analogous to `test_zero_active_suspend_resume` covering the disable-then-remove path. Consider auditing whether C20 should be revised to explicitly enumerate the endpoints requiring `notify_all`.

#### Routing

- Debug-log update: open `BUG-002`, Class: `BUG-RACE-CONDITION`, Plan impact: `NO_PLAN_CHANGE`.
- PLAN.md revision: none.
- Rerun needed: none.

(Source: R01.)

## 3. Evidence Gaps

| Gap ID | Missing evidence | Why it matters | Suggested next action | Source shard |
|---|---|---|---|---|
| R03-MISSING | R03 (Debug-log recurrence — state-mutating router endpoints) subagent never returned | The shard was specifically scoped to widen the audit beyond R01. R01 found one new instance (`remove_worker`); R03 was supposed to confirm there are no others (e.g., `set_worker_capacity`, `evacuate_worker`). Without R03, the human can't tell whether R01-01 is the complete set of recurrences. | Re-run `review-report`; the missing shard will be re-spawned. If R03 fails again, the human should review the recurrence-risk endpoints manually. | R03 |

## 4. Debug-log Updates Required

| Suggested BUG-* class | Source finding | Suggested Plan impact | One-line summary |
|---|---|---|---|
| `BUG-RACE-CONDITION` | R01-01 | `NO_PLAN_CHANGE` | `remove_worker` missing `notify_all` — same class as resolved BUG-001, different endpoint |

## 5. Plan Revision Suggestions

(none)

## 6. Medium / Low Findings

| Finding ID | Severity | Title | One-line summary | Source shard |
|---|---|---|---|---|
| R02-01 | MEDIUM | C7 missing-env-var error message is non-actionable | Error reads `"missing required configuration"` without naming `RLIX_ROUTER_BIND`; fail-fast behavior is correct, but operator UX is poor | R02 |

## 7. Adversarial Review Results

### R01

| Check | Result | Source |
|---|---|---|
| Waiter starts waiting between disable_worker completing and enable_worker mutating | PASSED | R01 |
| enable_worker mutates state but notify_all() raises | PASSED | R01 |
| disable_worker and enable_worker called concurrently | PASSED | R01 |

### R02

| Check | Result | Source |
|---|---|---|
| C5 port-held fail-fast vs silent retry | PASSED | R02 |
| C7 missing env var fail-fast vs warning-and-default | PASSED (with R02-01 note) | R02 |

### R03

(no adversarial results — shard MISSING)

## 8. Review Coverage

| Shard ID | Code areas covered | Anchors covered | % of changed files touched | Status |
|---|---|---|---|---|
| R01 | miles/router/router.py (enable_worker, disable_worker, remove_worker, _workers_changed, request waiter loop), tests/router/test_zero_active_suspend.py | C20, AC13, E14 | 100% (2 of 2 changed files) | COMPLETE |
| R02 | miles/router/router.py (init, validate, bind) | C5, C7, AC4 | 50% (1 of 2; tests/ not touched by this shard) | COMPLETE |
| R03 | (none — shard MISSING) | (none) | 0% | MISSING |

## 9. Accepted Risks / Follow-ups

- Whether to revise C20 to enumerate every state-mutating endpoint requiring `notify_all` is a `MAINTAINABILITY` follow-up, not a correctness gap. Surfaced by R01-01's recommended-action note; not a separate finding.

## 10. Appendix: Per-shard Report Index

| Shard ID | Sidecar file | Verdict | Findings count | Status |
|---|---|---|---|---|
| R01 | `plans/miles-port-unified-plan.review-report/R01.md` | `NEEDS_FIX` | 1 (HIGH) | COMPLETE |
| R02 | `plans/miles-port-unified-plan.review-report/R02.md` | `PASS_WITH_NOTES` | 1 (MEDIUM) | COMPLETE |
| R03 | (none) | (n/a) | 0 | MISSING |
