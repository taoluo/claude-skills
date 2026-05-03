# Code Review Plan

Feature: MILES → RLix port — router zero-active suspend
Source plan: plans/miles-port-unified-plan.md
TLDR artifact: plans/miles-port-unified-plan.tldr.md
Scope artifact: plans/miles-port-unified-plan.scope.md (optional)
Debug log: plans/miles-port-unified-plan.debug.md (optional)
Code diff / changed files: miles/router/router.py, tests/router/test_zero_active_suspend.py
Review readiness: READY

## 0. Review Dashboard

- Review readiness: `READY`
- Blocking issues: none
- Warnings: none
- Tests-passing evidence: `debug-log Current status: PASSING` (corroborated by invocation note: "E2E green per debug-log Current status: PASSING")
- Code diff / changed files: present (`miles/router/router.py`, `tests/router/test_zero_active_suspend.py`)
- Author clarification: 0 questions

## 1. Author Clarification

### 1.1 Author Clarification Questions

Author clarification: none required.

### 1.2 Review Assumptions

| Assumption ID | Assumption | Used for | Risk if wrong |
|---|---|---|---|
| RA-01 | Reviewer fleet optimizes for correctness + recurrence (per `BUG-001` history); not release-readiness depth. Source: skill-inferred from invocation note "Round goal: correctness + recurrence review". | Shard angle selection (R01, R03 carry adversarial / race / recurrence angles) | Under-emphasis of release-blocker concerns; if release-readiness was actually the goal, R02 should expand to cover all startup constraints |
| RA-02 | Deferred hardening items from `scope-triage` are excluded from this round (per scope-triage's `P3-DEFER-HARDENING` classification). Source: skill-inferred. | Shard scope (no shard covers `P3` items) | Accidental implementation of a `P3` item would not be caught this round — covered by R02 as a side-channel check |

## 2. Review Input Index

| Artifact | Path | Role | Required? | Status | Freshness notes |
|---|---|---|---|---|---|
| Source plan | `plans/miles-port-unified-plan.md` | source of truth | yes | `present-current` | mtime aligned with sibling artifacts |
| TLDR artifact | `plans/miles-port-unified-plan.tldr.md` | plan-anchor recovery | recommended | `present-current` | mtime aligned with PLAN.md |
| Scope artifact | `plans/miles-port-unified-plan.scope.md` | optional context | optional | `present-current` | mtime aligned; F* IDs available as navigation refs only |
| Debug log | `plans/miles-port-unified-plan.debug.md` | recurrence-risk source | optional | `present-current` | `Current status: PASSING`; `BUG-001` resolved with `Follow-up:` audit note |
| Code diff / changed files | inline (invocation note) | implementation surface | yes | `present-current` | 2 files; ~50 LOC total per `git diff --stat` |

## 3. Feature Review Matrix

| Review ID | Feature / area | Plan anchors | Scope categories | Debug bugs | Review angles | Priority | Suggested reviewer |
|---|---|---|---|---|---|---|---|
| R01 | Router zero-active suspend correctness | `C20`, `AC13`, `E14` | `P0-CORRECTNESS-FLOOR (F39)` | `BUG-001` (resolved) | `PLAN_ADHERENCE_REVIEW`, `CORRECTNESS_REVIEW`, `CONCURRENCY_RACE_REVIEW`, `ADVERSARIAL_INVARIANT_REVIEW`, `DEBUG_REGRESSION_REVIEW` | high | Subagent A |
| R02 | Startup fail-fast constraints | `C5`, `C7`, `AC4` | `P0-CORRECTNESS-FLOOR` | (none) | `PLAN_ADHERENCE_REVIEW`, `ERROR_HANDLING_FAIL_FAST_REVIEW` | medium | Subagent B |
| R03 | Debug-log recurrence: state-mutating router endpoints | `C20`, `D7`, `M11.2` | `P0-CORRECTNESS-FLOOR` | `BUG-001` follow-up | `DEBUG_REGRESSION_REVIEW`, `CONCURRENCY_RACE_REVIEW`, `ADVERSARIAL_INVARIANT_REVIEW` | high | Subagent A |

## 4. Parallel Review Shards

### R01: Router zero-active suspend correctness

- Goal: Verify the C20 contract (router 0-active suspend) is implemented correctly and the BUG-001 fix is robust under adversarial sequences.
- Must-read anchors: `C20`, `AC13`, `E14`
- Scope categories / scope notes: `P0-CORRECTNESS-FLOOR` (`F39` if present in `.scope.md`)
- Code areas to inspect: `miles/router/router.py` (`enable_worker`, `disable_worker`, the `_workers_changed` condition variable, request waiter loop), `tests/router/test_zero_active_suspend.py`
- Review angles: `PLAN_ADHERENCE_REVIEW`, `CORRECTNESS_REVIEW`, `CONCURRENCY_RACE_REVIEW`, `ADVERSARIAL_INVARIANT_REVIEW`, `DEBUG_REGRESSION_REVIEW`
- Adversarial questions: see §5 R01 (5 specialized prompts)
- Required tests / evidence: `pytest tests/router/test_zero_active_suspend.py -q` passing; the new `test_zero_active_suspend_resume` test exists and exercises disable-all → wait → enable-one path; mutation check: would the test fail if `notify_all` were removed?
- Known bugs from debug-log: `BUG-001` (resolved 2026-05-03; `Verification: TEST_PASS`)
- Expected reviewer output: report per §7 template; verdict ∈ {`PASS`, `PASS_WITH_NOTES`, `NEEDS_FIX`, `PLAN_REVISION_NEEDED`}.
- Stop conditions: stop and ask the human if (a) the C20 contract appears self-contradictory, or (b) `enable_worker` is called from more than one code path with different locking discipline.

### R02: Startup fail-fast constraints

- Goal: Verify startup-time `C*` constraints are enforced fail-fast (not silently degraded).
- Must-read anchors: `C5`, `C7`, `AC4`
- Scope categories / scope notes: `P0-CORRECTNESS-FLOOR`
- Code areas to inspect: startup paths in `miles/router/router.py` (init, validate, bind)
- Review angles: `PLAN_ADHERENCE_REVIEW`, `ERROR_HANDLING_FAIL_FAST_REVIEW`
- Adversarial questions: 2 prompts in §5 R02
- Required tests / evidence: startup misconfiguration tests assert raised exceptions, not warning logs.
- Known bugs from debug-log: (none)
- Expected reviewer output: report per §7 template.
- Stop conditions: stop if any `C*` constraint is enforced only by a runtime check that can be silently retried.

### R03: Debug-log recurrence — state-mutating router endpoints

- Goal: Audit other state-mutating router endpoints (`disable_worker`, `set_worker_capacity`) for the same `notify_all` gap that caused `BUG-001`.
- Must-read anchors: `C20`, `D7`, `M11.2`
- Scope categories / scope notes: `P0-CORRECTNESS-FLOOR` (`BUG-001` `Follow-up:` field flagged this risk)
- Code areas to inspect: every function in `miles/router/router.py` that mutates `enabled_workers`, `worker_capacity`, or related router state.
- Review angles: `DEBUG_REGRESSION_REVIEW`, `CONCURRENCY_RACE_REVIEW`, `ADVERSARIAL_INVARIANT_REVIEW`
- Adversarial questions: see §5 R03 (4 specialized prompts)
- Required tests / evidence: confirm each state-mutating endpoint either calls `_workers_changed.notify_all()` or has a documented reason it doesn't need to. If gap found, recommend opening a new `BUG-*` in `debug-log` (do not fix in this skill).
- Known bugs from debug-log: `BUG-001` (resolved); recurrence risk flagged in `BUG-001` `Follow-up:`.
- Expected reviewer output: report per §7 template; if any endpoint is missing the notify, verdict is `NEEDS_FIX` with `Plan Impact: Does debug-log need update? = yes`.
- Stop conditions: stop if `C20` is found to be ambiguous about which endpoints require `notify_all` (in which case verdict is `PLAN_REVISION_NEEDED`).

## 5. Adversarial Review Prompts

### R01

1. What if a request waiter starts waiting on `_workers_changed` *between* `disable_worker` completing and `enable_worker` mutating `enabled_workers`? Does it see consistent state?
2. What if `enable_worker` mutates `enabled_workers` but the `notify_all()` call raises? Does the request resume or hang?
3. What if `disable_worker` and `enable_worker` are called concurrently from two threads? Is the condition predicate re-checked under lock after wakeup?
4. What if the test `test_zero_active_suspend_resume` were rewritten to omit the resume assertion — would `test_zero_active_suspend` alone catch a regression where `notify_all` is removed? (mutation-test thinking)
5. What if `enable_worker` is called *before* any worker was disabled (degenerate case)? Does the notify-without-waiter case behave as expected?

### R02

1. What if `C5` (single-process binding) fails because the port is held by a stale process — is the error fail-fast or does the router silently retry on a different port?
2. What if `C7` (required environment variable) is missing — does the router log a warning and proceed with a default, or raise immediately?

### R03

1. What if `disable_worker` mutates `enabled_workers` but does NOT notify — would a request that was previously waiting incorrectly assume a worker became available?
2. What if `set_worker_capacity(0)` is functionally equivalent to disabling the worker but goes through a separate code path that lacks `notify_all`?
3. What if a future `evacuate_worker(...)` endpoint is added — does the team have a code-level invariant ensuring all mutating router endpoints notify?
4. What if the audit reveals `disable_worker` already calls `notify_all` correctly, but for the wrong reason (notifying when nothing changed) — is that a `MAINTAINABILITY` finding or a latent correctness risk?

## 6. Subagent Assignment Plan

| Subagent | Shards | Required inputs | Output file | Independence notes | Estimated effort | Status |
|---|---|---|---|---|---|---|
| Subagent A | R01, R03 | `PLAN.md` (read C20, AC13, E14, D7, M11.2 sections); `miles/router/router.py`; `tests/router/test_zero_active_suspend.py`; `debug-log` `BUG-001` entry | `subagent-a-r01.md`, `subagent-a-r03.md` | Both shards touch the router; assigning to one subagent avoids context duplication | ~45 min (R01 ~25 min + R03 ~20 min) | `READY` |
| Subagent B | R02 | `PLAN.md` (read C5, C7, AC4 sections); `miles/router/router.py` startup paths | `subagent-b-r02.md` | Independent of R01/R03 (different code area, different anchors) | ~20 min | `READY` |

## 7. Subagent Report Template

(Subagents copy this template verbatim and fill it in.)

```markdown
# Review Shard Report

Shard ID:
Reviewer:
Inputs reviewed:
Code areas reviewed:
Plan anchors:
Debug-log bugs reviewed:
Review angles:

## Verdict

`PASS | PASS_WITH_NOTES | NEEDS_FIX | BLOCKED_BY_MISSING_EVIDENCE | PLAN_REVISION_NEEDED`

## Findings

| Finding ID | Severity | Type | Evidence | Recommendation |
|---|---|---|---|---|

## Adversarial Checks

| Check | Result | Evidence |
|---|---|---|

## Tests / Evidence Reviewed

| Test / command | Result | Notes |
|---|---|---|

## Plan Impact

- Does PLAN.md need revision?
- Does debug-log need update?
- Should tldr-plan / scope-triage rerun?

## Reviewer Notes
```

Severity values: `BLOCKER`, `HIGH`, `MEDIUM`, `LOW`, `NOTE`.
Finding-type values: `CORRECTNESS`, `RACE`, `RESOURCE_LEAK`, `ERROR_HANDLING`, `TEST_GAP`, `PLAN_DRIFT`, `REGRESSION`, `OVERENGINEERING`, `OBSERVABILITY_GAP`, `PERFORMANCE`, `MAINTAINABILITY`.

## 8. Final Aggregation Contract

(The aggregator — a human or the future `review-report` skill — follows this contract verbatim. Full text in `references/aggregation-contract.md`; summary here.)

1. **Collect** all shard reports by `Shard ID`. Missing reports → `Final recommendation: BLOCKED` with `aggregation incomplete: <list>`.
2. **Deduplicate findings** by canonical signature `(plan anchor, code area, invariant)`; preserve every reviewer's evidence excerpt verbatim; use highest severity across the merged set.
3. **Group findings** by `Severity`, then by `Finding type` within severity.
4. **Extract Plan Revision Suggestions** from any shard with `Verdict: PLAN_REVISION_NEEDED` or `Plan Impact: Does PLAN.md need revision? = yes` → recommend opening a new `BUG-PLAN-GAP` / `BUG-PLAN-WRONG` in `debug-log` (do not edit `PLAN.md` directly).
5. **Extract debug-log updates needed** — any new bug discovered → enumerate with proposed `Class:` and `Plan impact:`; let `debug-log` assign `BUG-*` IDs.
6. **Compute final recommendation**:
   - any `BLOCKER` or `BLOCKED_BY_MISSING_EVIDENCE` → `BLOCKED`
   - any `NEEDS_FIX` verdict or any `HIGH` finding → `NEEDS_FIX`
   - all `PASS` / `PASS_WITH_NOTES`, no `BLOCKER` / `HIGH`, but `MEDIUM` / `LOW` present → `APPROVE_WITH_FOLLOWUPS`
   - all `PASS` / `PASS_WITH_NOTES`, only `NOTE` (or none) → `APPROVE`
   - any `PLAN_REVISION_NEEDED` not already counted → `NEEDS_FIX` (revision must land before re-review)
7. **Final report shape**: separate file (not part of `<plan-stem>.review.md`); §0 Executive Summary, §1 Blocking, §2 Non-blocking, §3 Evidence Gaps, §4 Adversarial Results, §5 Recurrence Risks, §6 Plan Revisions Surfaced, §7 Debug-log Updates Required, §8 Test Coverage Assessment, §9 Final Recommendation.

The aggregator MUST NOT: edit `PLAN.md` / sibling artifacts; change shard verdicts; invent findings; silently drop low-severity findings; assign `BUG-*` IDs.

## 9. Review Execution Checklist

- [ ] Author clarification answers (if any) have been folded into §1.2 Review Assumptions or applied to source artifacts and `code-review-plan` re-run. *(none required this round)*
- [ ] All §6 rows have `Status: READY`. *(yes)*
- [ ] Each subagent has been briefed with their assigned shard(s).
- [ ] Aggregator (human or future `review-report` skill) has the §8 contract.
- [ ] Plan and code diff are at the commits cited in §0. *(commit hash to be confirmed by the human launching the fleet)*
- [ ] Reviewers know to surface `PLAN_REVISION_NEEDED` findings via the report contract (Step 4 of aggregation).
