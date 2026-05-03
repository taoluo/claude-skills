# Bug Entry Template

Canonical template for one bug in §3 Bug Entries of `<plan-stem>.debug.md`.

`Scope anchors` is intentionally **omitted** — `debug-log` does not maintain `F*` scope IDs. See `SKILL.md` "Plan anchors required; scope anchors removed" rule.

## Template

```markdown
### BUG-<NNN>: <short title>

- Status: <OPEN | ROOT_CAUSE_SUSPECTED | FIX_IN_PROGRESS | FIXED_PENDING_VERIFY | RESOLVED | REOPENED | WONT_FIX>
- Class: <BUG-IMPLEMENTATION | BUG-PLAN-GAP | BUG-PLAN-WRONG | BUG-TEST-HARNESS | BUG-ENVIRONMENT | BUG-INTEGRATION | BUG-RACE-CONDITION | BUG-PERFORMANCE | BUG-REGRESSION>
- First observed: <YYYY-MM-DD or session ID>
- Repro / test command: <exact command>
- Environment: <GPU count / node / container / flags / commit / branch>
- Observed behavior: <what actually happened>
- Expected behavior: <what the plan or test expected>
- Failure excerpt: <short log / stack trace, summarized>
- Root cause: <actual cause, not symptom>
- Root cause confidence: <LOW | MEDIUM | HIGH | CONFIRMED_BY_TEST>
- Fix: <what changed>
- Files changed: <comma-separated paths>
- Verification: <see Verification field rules below>
- Regression coverage: <new test or guard added; "none" if no new coverage>
- Plan anchors: <comma-separated AC* / C* / D* / E* / M* / A*; "unknown" if none>
- Related artifacts: <free-text, optional; e.g., "PLAN.tldr.md current; PLAN.scope.md present, not used as anchor source">
- Related bugs: <comma-separated BUG-* IDs; omit if none>
- Plan impact: <NO_PLAN_CHANGE | PLAN_CLARIFICATION | PLAN_CONSTRAINT_MISSING | PLAN_SCOPE_CHANGE | PLAN_ACCEPTANCE_CRITERION_CHANGE | PLAN_TEST_GATE_CHANGE>
- Follow-up: <remaining hardening / cleanup; "none" if resolved cleanly>
```

## Per-field rules

### Required vs optional

| Field | Required | Notes |
|---|---|---|
| `Status` | yes | Always one of the 7 status values. |
| `Class` | yes | Always one of the 9 bug-class values. |
| `First observed` | yes | Convert relative dates ("yesterday", "this morning") to absolute. |
| `Repro / test command` | yes | `unknown` if the bug surfaced from a free-form repro the user did not capture. |
| `Environment` | yes | At minimum the commit / branch; `unknown` for any field the user did not record. |
| `Observed behavior` | yes | What actually happened — not "test failed" but a one-line description of the failure mode. |
| `Expected behavior` | yes | What the plan, test, or user expected. |
| `Failure excerpt` | when available | Short — summarize long logs and reference the full path. `unknown` if no log was captured. |
| `Root cause` | when known | `unknown` if not yet identified. Required when status reaches `FIX_IN_PROGRESS` or later. |
| `Root cause confidence` | yes | One of `LOW` / `MEDIUM` / `HIGH` / `CONFIRMED_BY_TEST`. `CONFIRMED_BY_TEST` requires a recorded passing verification. |
| `Fix` | when applied | `pending` / `none yet` if not yet applied. |
| `Files changed` | when applied | Comma-separated paths; `none` for plan-only fixes (paired with non-`NO_PLAN_CHANGE` Plan impact). |
| `Verification` | depends on Status | See "Verification field rules" below. |
| `Regression coverage` | when resolved | `none` is acceptable if no new test was added; recommend a §6 Remaining Risks row in that case. |
| `Plan anchors` | when available | Required when at least one anchor exists. `unknown` if no plan anchor matches. **Required when available** is the load-bearing phrasing — `unknown` is honest, omitting the line is not. |
| `Related artifacts` | optional | Free-text. Use to acknowledge sibling artifacts without anchoring to them. **Do not record `F*` scope IDs here** — `debug-log` deliberately does not maintain scope anchors. |
| `Related bugs` | optional | Cross-link `BUG-*` IDs that share symptom, root cause, or anchors but did not meet the conservative merge rule. |
| `Plan impact` | yes | One of the 6 Plan impact values. Required even on `OPEN` bugs (use `NO_PLAN_CHANGE` if the bug is purely an implementation issue). |
| `Follow-up` | yes | Either a concrete next action, or `none`. |

### `Status` transitions

```text
OPEN → ROOT_CAUSE_SUSPECTED → FIX_IN_PROGRESS → FIXED_PENDING_VERIFY → RESOLVED
                                                                     ↘
                                                                       REOPENED → (back to OPEN-class flow)
OPEN / any-state → WONT_FIX (with rationale in Verification field)
```

Hard rule: **never `RESOLVED` without an evidence-typed `Verification:` line**.

### `Verification` field rules

The exact format depends on `Status`:

| Status | Required `Verification:` format |
|---|---|
| `RESOLVED` | `<TYPE> — <one-line evidence>`, where `<TYPE>` ∈ {`TEST_PASS`, `MANUAL_REPRO_PASS`, `LOG_CONFIRMED`, `USER_REPORTED_PASS`} |
| `FIXED_PENDING_VERIFY` | `pending — planned command: <command>` (no evidence type yet) |
| `OPEN` / `ROOT_CAUSE_SUSPECTED` / `FIX_IN_PROGRESS` | `unknown` or `pending` |
| `WONT_FIX` | `n/a — wont-fix rationale: <reason>` |
| `REOPENED` | `n/a — reopened: <reason for reopening>` |

Examples:

```text
Verification: TEST_PASS — pytest tests/router/test_zero_active_suspend.py -q passed.
Verification: MANUAL_REPRO_PASS — re-ran the original repro by hand: request resumes after enable_worker.
Verification: LOG_CONFIRMED — `worker enabled, notifying _workers_changed` log line now appears.
Verification: USER_REPORTED_PASS — user confirmed in their environment on 2026-05-03.
Verification: pending — planned command: pytest tests/router/test_zero_active_suspend.py -q
Verification: n/a — wont-fix rationale: behavior is intentional per C20; closing as duplicate of BUG-007.
```

### `Plan anchors` field rules

Accepts `AC*` / `C*` / `D*` / `E*` / `M*` / `A*` from the source plan or TLDR.

- **Required when available**.
- `unknown` when no plan anchor exists.
- Never include `F*` scope anchors. The scope artifact is optional context only.

### `Related artifacts` field rules

Free-text optional field. Used to acknowledge sibling artifact presence without anchoring to them.

Acceptable:

```text
Related artifacts: PLAN.tldr.md current
Related artifacts: PLAN.scope.md present, not used as anchor source
Related artifacts: PLAN.tldr.md stale (predates 2026-05-01 plan revision)
```

Not acceptable (do **not** record `F*` here):

```text
Related artifacts: F39, F42  ← WRONG. debug-log does not maintain scope anchors.
```

## Anti-pattern: vague entries

Reject vague entries unless the user has truly exhausted available evidence.

Bad:

```markdown
### BUG-001: Router bug

- Status: RESOLVED
- Fix: Fixed router bug.
- Verification: passed.
```

Good:

```markdown
### BUG-001: Router request hangs after all workers disabled

- Status: RESOLVED
- Class: BUG-RACE-CONDITION
- Observed behavior: Router request times out after all workers are disabled and a new one is enabled.
- Expected behavior: Request should suspend, then resume when enable_worker notifies _workers_changed.
- Root cause: enable_worker mutated enabled_workers but did not call notify_all on _workers_changed.
- Root cause confidence: CONFIRMED_BY_TEST
- Fix: Added _workers_changed.notify_all() after enabled_workers mutation in enable_worker.
- Files changed: miles/router/router.py, tests/router/test_zero_active_suspend.py
- Verification: TEST_PASS — pytest tests/router/test_zero_active_suspend.py -q passed.
- Regression coverage: Added test_zero_active_suspend covering the disable-all → wait → enable resume path.
- Plan anchors: C20, AC13, E14
- Plan impact: NO_PLAN_CHANGE
- Follow-up: Audit other state-mutating router endpoints (disable_worker, set_worker_capacity) for similar missing notify_all calls.
```

If the user truly cannot supply a field, use `unknown` and add a §6 Remaining Risks row. Do not invent values.
