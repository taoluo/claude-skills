# Debug Log Classification Rules

## Bug class

Use exactly one primary class per bug. Highest-risk wins on ties.

| Class | Use when |
|---|---|
| `BUG-IMPLEMENTATION` | Plan was correct; implementation violated it. |
| `BUG-PLAN-GAP` | Plan omitted a needed detail. Pair with `Plan impact: PLAN_CONSTRAINT_MISSING` (or `PLAN_CLARIFICATION` if the gap is just wording). |
| `BUG-PLAN-WRONG` | Plan specified the wrong behavior. Pair with `Plan impact: PLAN_ACCEPTANCE_CRITERION_CHANGE` or `PLAN_TEST_GATE_CHANGE`. |
| `BUG-TEST-HARNESS` | Test setup / assertion / fixture was wrong; product code was correct. |
| `BUG-ENVIRONMENT` | Failure caused by machine / container / dependency / runtime environment, not by product code or plan. |
| `BUG-INTEGRATION` | Components individually work but fail at a boundary. Common when plan describes components in isolation. |
| `BUG-RACE-CONDITION` | Ordering / concurrency / timing issue. Often presents as a non-deterministic `BUG-INTEGRATION`; classify as race when timing is the load-bearing variable. |
| `BUG-PERFORMANCE` | Correctness passes but latency / resource / throughput behavior breaks the smoke target. |
| `BUG-REGRESSION` | Previously passing behavior broke after a later change. Use even if the underlying class is also `BUG-IMPLEMENTATION` — `BUG-REGRESSION` carries the "this used to work" signal. |

## Status

Use exactly one status per bug.

| Status | Meaning |
|---|---|
| `OPEN` | Bug observed; root cause not yet investigated. |
| `ROOT_CAUSE_SUSPECTED` | Hypothesis recorded; not yet confirmed. |
| `FIX_IN_PROGRESS` | Fix being implemented; not yet committed. |
| `FIXED_PENDING_VERIFY` | Fix applied; verification not yet run. `Verification:` field must record `pending — planned command: <command>`. |
| `RESOLVED` | Fix applied and verified. `Verification:` field must record `<TYPE> — <one-line evidence>`. |
| `REOPENED` | Previously `RESOLVED` bug is failing again. Move row back from §2 to §1; record reason in `Verification:` line as `n/a — reopened: <reason>`. |
| `WONT_FIX` | Bug is intentional behavior, duplicate, or out of scope. `Verification:` records `n/a — wont-fix rationale: <reason>`. |

## Root cause confidence

| Value | Use when |
|---|---|
| `LOW` | One hypothesis, no supporting evidence beyond the symptom. |
| `MEDIUM` | Hypothesis with supporting evidence (logs, code reading), but not yet confirmed by a test or repro. |
| `HIGH` | Hypothesis confirmed by manual repro or by a code-reading argument that exhausts alternatives. |
| `CONFIRMED_BY_TEST` | A passing automated test (or equivalent recorded evidence) demonstrates the fix addresses the root cause. Required for `Status: RESOLVED` with `Verification: TEST_PASS`. |

## Verification evidence type

| Type | Use when |
|---|---|
| `TEST_PASS` | An automated test (unit / integration / smoke / E2E) is now green. Strongest evidence; prefer this when feasible. |
| `MANUAL_REPRO_PASS` | The original repro was re-run by hand and now passes. Use when the bug was discovered via manual exploration and writing an automated test would be disproportionate. |
| `LOG_CONFIRMED` | A log line, metric, or trace confirms the fix took effect. Use when correctness is observable from telemetry but the test surface is hard to reach. |
| `USER_REPORTED_PASS` | A user observed the fix in their own environment. Weakest evidence; pair with a follow-up `Plan Revision Suggestion` to add a real test if possible. |

## Plan impact

Use exactly one value per bug. Anything other than `NO_PLAN_CHANGE` adds a row to §5 Plan Revision Suggestions.

| Value | Meaning | Downstream action |
|---|---|---|
| `NO_PLAN_CHANGE` | Code fix only; plan remains accurate. | None. |
| `PLAN_CLARIFICATION` | Plan was ambiguous; clarify wording. | Patch source plan; rerun `tldr-plan` if the clarification touches `AC*` / `C*` / `E*`. |
| `PLAN_CONSTRAINT_MISSING` | Bug reveals missing hard guard or constraint. | Add new `C*`; rerun `tldr-plan`. |
| `PLAN_SCOPE_CHANGE` | Bug changes MVP / defer / forbidden / overengineering boundary. | Patch source plan; rerun `scope-triage`. |
| `PLAN_ACCEPTANCE_CRITERION_CHANGE` | Bug changes expected outcome — an `AC*` is wrong or missing. | Update `AC*`; rerun `tldr-plan`; rerun `scope-triage` if AC change shifts the MVP boundary. |
| `PLAN_TEST_GATE_CHANGE` | Bug changes the verification gate — an `E*` is wrong or missing. | Update `E*`; rerun `tldr-plan`. |

## Revision suggestion status

Used in §5 Plan Revision Suggestions. Append-only — rows transition status, never get deleted.

| Status | Meaning |
|---|---|
| `PROPOSED` | New suggestion. Default state when a non-`NO_PLAN_CHANGE` bug adds a §5 row. |
| `APPLIED` | The user has patched `PLAN.md` accordingly. (Optionally pair with a follow-up `tldr-plan` / `scope-triage` rerun mention in §6 Remaining Risks.) |
| `SUPERSEDED` | A later finding obsoletes this row. Record the superseding `REV-*` ID in the `Source-plan gap` cell. |

## Resolution rule

A bug can be `RESOLVED` only when **all** of the following hold:

- root cause is identified
- fix is applied
- verification command (or equivalent) has run and passed
- evidence is recorded with an evidence-type tag (`TEST_PASS` / `MANUAL_REPRO_PASS` / `LOG_CONFIRMED` / `USER_REPORTED_PASS`)

Otherwise use:

- `FIXED_PENDING_VERIFY` (fix applied, verification pending)
- `ROOT_CAUSE_SUSPECTED` (hypothesis only)
- `OPEN` (no hypothesis yet)

## Conservative merge rule

When deciding whether a new note refers to an existing bug, merge only if **at least two** of the following signals match:

- same test command / smoke target
- same observed symptom
- same failing component
- same root-cause hypothesis
- same plan anchors (`AC*` / `C*` / `D*` / `E*` / `M*` / `A*`)

If only one signal matches, create a new `BUG-*` and add `Related bugs:` cross-link.

Rationale: over-splitting is recoverable (a later note can mark the duplicate `WONT_FIX` with `Related bugs:`); over-merging silently corrupts root-cause history.

## Plan revision rule

Mapping `Plan impact` → `Rerun needed` value in §5:

| Plan impact | Rerun needed |
|---|---|
| `NO_PLAN_CHANGE` | `none` (and no §5 row at all) |
| `PLAN_CLARIFICATION` | `tldr-plan` (or `none` if purely cosmetic wording with no AC/C/E touch) |
| `PLAN_CONSTRAINT_MISSING` | `tldr-plan` |
| `PLAN_SCOPE_CHANGE` | `scope-triage` |
| `PLAN_ACCEPTANCE_CRITERION_CHANGE` | `tldr-plan` (rerun `scope-triage` too if the AC change shifts MVP boundary → use `both`) |
| `PLAN_TEST_GATE_CHANGE` | `tldr-plan` |

The recommendation is always plan-driven: the user patches `PLAN.md` first, then reruns the named sibling. `debug-log` does not anchor recommendations to existing scope artifact rows (`F*` IDs); it only points at where the source plan is incomplete.
