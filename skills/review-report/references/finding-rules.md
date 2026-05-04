# Finding Rules

What makes a finding valid + the load-bearing background rule + severity / finding-type / routing / evidence-gap rules.

## Background rule (load-bearing)

A finding is **invalid** if it only says "what is wrong" without "why the invariant matters." Every BLOCKER and HIGH finding MUST include the background — the reader should understand the problem without re-reading `PLAN.md`, `<plan-stem>.debug.md`, or the source code.

### Bad

```text
remove_worker may miss notify_all
```

This is unactionable. The reader doesn't know what `remove_worker` is, what `notify_all` is for, why missing it matters, or how to confirm the finding.

### Good

```markdown
#### Background

The router zero-active suspend path (C20) prevents requests from failing or spinning when workers are temporarily disabled during runtime shrink/expand. The plan validates this through AC13 / E14, and BUG-001 already fixed one missing notify path in `enable_worker`, so all worker-state mutation paths are recurrence-sensitive.

#### Expected behavior / invariant

Every state-mutating router endpoint that changes worker availability MUST notify `_workers_changed` so blocked request waiters can re-check the predicate.

#### Finding

`remove_worker` mutates active worker state but does not call `_workers_changed.notify_all()`.

#### Evidence

`miles/router/router.py:217` — `remove_worker` pops from `enabled_workers` without acquiring the condition or notifying. `tests/router/` has no test exercising `remove_worker` mid-suspend.

#### Impact

Requests blocked when `remove_worker` is called concurrently with worker disable will hang until the next state mutation that does notify (or the test timeout). Recurrence of BUG-001's class.

#### Recommended action

Add `_workers_changed.notify_all()` under the condition lock at `miles/router/router.py:217`. Add a regression test analogous to `test_zero_active_suspend_resume` covering the disable-then-remove path.

#### Routing

- Debug-log update: open `BUG-002`, Class: `BUG-RACE-CONDITION`, Plan impact: `NO_PLAN_CHANGE`.
- PLAN.md revision: none.
- Rerun needed: none.
```

This is decision-ready. The human can ship/no-ship without re-reading anything else.

## Severity rules

| Severity | Use when |
|---|---|
| `BLOCKER` | Must fix before ship. Correctness violation, data loss, security gap, or release-blocker contract violated. |
| `HIGH` | Should fix before ship. Subtle correctness risk, race window, resource leak, or recurrence of a `debug-log` bug class. |
| `MEDIUM` | Fix before next iteration. Non-blocking correctness improvement, observability gap, test gap. |
| `LOW` | Fix when convenient. Maintainability, naming, comment. |
| `NOTE` | Informational; no action required. |

## Finding type guidance

Same 11 values as `code-review-plan`'s aggregation contract. Pick the most specific:

- `CORRECTNESS`, `RACE`, `RESOURCE_LEAK`, `ERROR_HANDLING`, `TEST_GAP`, `PLAN_DRIFT`, `REGRESSION`, `OVERENGINEERING`, `OBSERVABILITY_GAP`, `PERFORMANCE`, `MAINTAINABILITY`.

If a finding genuinely spans two types, pick the one that drives the recommended action. If you can't pick one, the finding is probably two findings — split it.

## Routing rules

Every BLOCKER/HIGH finding's `#### Routing` block MUST have all three lines (each may be `none`):

| Line | Allowed values |
|---|---|
| `Debug-log update:` | `none` OR `open BUG-* with Class: <bug class>, Plan impact: <plan impact>` (suggestion only — the aggregator does not assign `BUG-*` IDs) |
| `PLAN.md revision:` | `none` OR a one-line gap description (e.g., `add new C* enforcing notify_all on every state-mutating router endpoint`) |
| `Rerun needed:` | `none` / `tldr-plan` / `scope-triage` / `both` |

The aggregator extracts these into §4 Debug-log Updates Required, §5 Plan Revision Suggestions, and the §0 dashboard `Reruns recommended:` line — without auto-actions.

## Evidence-gap rules

Prefer reporting an Evidence Gap over guessing. A subagent that fabricates evidence is worse than one that returns `BLOCKED_BY_MISSING_EVIDENCE`.

Use Evidence Gap rows when:

- The shard's `Required tests / evidence` field listed something the subagent couldn't access (e.g., a coverage report that doesn't exist).
- The subagent would need to escalate beyond the read-only tool allowlist to confirm a finding (e.g., needs to run a test).
- A code path the subagent inspected has unclear behavior under conditions the test suite doesn't cover.
- The subagent identified a likely finding but couldn't verify the impact without information the shard didn't provide.

Each gap row should explain:

- `Missing evidence`: what specifically is missing.
- `Why it matters`: what conclusion the gap blocks.
- `Suggested next action`: what the human (or a follow-up shard) should do.

A shard with non-empty `## Evidence Gaps` may still have `Verdict: PASS_WITH_NOTES` or `NEEDS_FIX` — the gaps don't automatically force `BLOCKED_BY_MISSING_EVIDENCE`. Use `BLOCKED_BY_MISSING_EVIDENCE` only when the gaps prevent the reviewer from forming any verdict.
