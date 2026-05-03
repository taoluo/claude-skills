# Debug Log Output Layout

The structure is fixed; only §3 Bug Entries grows over time. Tables in §0–§2, §4, §5, §6 are dashboards that are updated in place as bugs transition status.

## Append-only invariant

This artifact is **append-only**. Updates use targeted patch/edit (in Claude Code: Edit, not Write) on an existing file. Resolved entries are never deleted from §3; revision suggestions in §5 transition status (`PROPOSED` → `APPLIED` / `SUPERSEDED`) but are never removed; retest timeline rows in §4 are never reordered.

## Document skeleton

```markdown
# Debug Log

Feature: <feature name or unknown>
Source plan: <path>
TLDR context: <path | missing>
Scope context: <path | missing, optional>
Current smoke target: <test target>
Current status: <IN_PROGRESS | PASSING | BLOCKED | UNKNOWN>

## 0. Session Summary

| Session | Date | Test target | Result | Bugs opened | Bugs resolved | Remaining blockers |
|---|---|---|---|---:|---:|---|

## 1. Active Bugs

| Bug ID | Status | Class | Symptom | Root cause confidence | Blocking test | Plan anchors |
|---|---|---|---|---|---|---|

## 2. Resolved Bugs

| Bug ID | Class | Symptom | Root cause | Fix | Verification | Plan impact |
|---|---|---|---|---|---|---|

## 3. Bug Entries

### BUG-001: <short title>

- Status:
- Class:
- First observed:
- Repro / test command:
- Environment:
- Observed behavior:
- Expected behavior:
- Failure excerpt:
- Root cause:
- Root cause confidence:
- Fix:
- Files changed:
- Verification:
- Regression coverage:
- Plan anchors:
- Related artifacts:
- Related bugs:
- Plan impact:
- Follow-up:

## 4. Retest Timeline

| Run | Command | Result | Related bugs | Notes |
|---|---|---|---|---|

## 5. Plan Revision Suggestions

These are not edits to the source plan. Patch `PLAN.md`, then rerun `tldr-plan` or `scope-triage` if the revision changes audit or scope boundaries.

| Revision ID | Status | Triggered by bug | Source-plan gap | Suggested source-plan location | Rerun needed |
|---|---|---|---|---|---|

## 6. Remaining Risks

| Risk | Evidence | Suggested next action |
|---|---|---|
```

## Header field rules

| Field | Required | Notes |
|---|---|---|
| `Feature` | yes | Inferred from source-plan title; `unknown` if absent. |
| `Source plan` | yes | Absolute or repo-relative path. |
| `TLDR context` | yes | Path if `<plan-stem>.tldr.md` exists; otherwise `missing`. |
| `Scope context` | yes | Path if `<plan-stem>.scope.md` exists; otherwise `missing, optional`. The `optional` suffix is load-bearing — it signals that `debug-log` does not depend on the scope artifact. |
| `Current smoke target` | yes | The test command or smoke target currently being debugged. |
| `Current status` | yes | One of `IN_PROGRESS` / `PASSING` / `BLOCKED` / `UNKNOWN`. |

## Per-section column rules

### §0 Session Summary

One row per debugging session. A "session" is loosely defined — typically one continuous block of debugging work, capped by either the user explicitly opening a new session or by the date changing.

| Column | Type | Notes |
|---|---|---|
| `Session` | `SESSION-NNN` (zero-padded) | Stable ID; never renumber. |
| `Date` | absolute date `YYYY-MM-DD` | Convert relative dates from user notes. |
| `Test target` | string | The smoke target the session worked on. |
| `Result` | `PASS` / `FAIL` / `MIXED` / `IN_PROGRESS` | Session-level summary. |
| `Bugs opened` | int | Count of `BUG-*` rows that gained `OPEN` / `ROOT_CAUSE_SUSPECTED` status during this session. |
| `Bugs resolved` | int | Count of `BUG-*` rows that transitioned to `RESOLVED` during this session. |
| `Remaining blockers` | string | Free-text list of `BUG-*` IDs still blocking the smoke target. |

### §1 Active Bugs

One row per non-`RESOLVED` bug. Remove the row from §1 (and add a row to §2) when status transitions to `RESOLVED` or `WONT_FIX`. Re-add the row to §1 (and remove from §2) on `REOPENED`.

| Column | Notes |
|---|---|
| `Bug ID` | `BUG-NNN`; matches the §3 entry heading. |
| `Status` | One of the 7 status values. |
| `Class` | One of the 9 bug-class values. |
| `Symptom` | One-line restate of the observed failure. |
| `Root cause confidence` | One of `LOW` / `MEDIUM` / `HIGH` / `CONFIRMED_BY_TEST`. |
| `Blocking test` | The test command this bug currently blocks; `unknown` if not yet identified. |
| `Plan anchors` | Comma-separated `AC*` / `C*` / `D*` / `E*` / `M*` / `A*`; `unknown` if no anchor exists. |

### §2 Resolved Bugs

One row per `RESOLVED` (or `WONT_FIX`) bug. Same `BUG-*` ID as §3.

| Column | Notes |
|---|---|
| `Bug ID` | `BUG-NNN`. |
| `Class` | One of the 9 bug-class values. |
| `Symptom` | One-line restate. |
| `Root cause` | One-line root cause statement. |
| `Fix` | One-line fix description. |
| `Verification` | `<TYPE> — <one-line evidence>` for `RESOLVED`. For `WONT_FIX`, `n/a — wont-fix rationale: <reason>`. |
| `Plan impact` | One of the 6 Plan impact values. |

### §3 Bug Entries

One subsection per bug, in `BUG-NNN` order (never reorder; `BUG-001` always comes first). The full template is in `bug-entry-template.md`. Resolved entries stay here forever — they are the durable narrative that the §1 / §2 dashboards summarize.

### §4 Retest Timeline

One row per test run. Append in chronological order; never reorder.

| Column | Notes |
|---|---|
| `Run` | `RUN-NNN`; stable, never renumber. |
| `Command` | Exact test command. |
| `Result` | `PASS` / `FAIL` / `ERROR` / `SKIP`. |
| `Related bugs` | Comma-separated `BUG-*` IDs that this run was intended to verify or that newly surfaced. |
| `Notes` | Short — failure excerpt, regression flag, environment delta, etc. |

### §5 Plan Revision Suggestions

One row per suggested source-plan revision. Append in `REV-NNN` order; transition `Status` in place; never delete rows.

```text
| Revision ID | Status | Triggered by bug | Source-plan gap | Suggested source-plan location | Rerun needed |
```

| Column | Allowed values |
|---|---|
| `Revision ID` | `REV-NNN`; stable. |
| `Status` | `PROPOSED` (new) / `APPLIED` (`PLAN.md` patched) / `SUPERSEDED` (later finding obsoletes this row). |
| `Triggered by bug` | `BUG-NNN` (or `BUG-NNN, BUG-MMM` if multiple). |
| `Source-plan gap` | One-line description of what `PLAN.md` is missing or got wrong. |
| `Suggested source-plan location` | Section / `C*` / `AC*` / `E*` / etc. anchor where the revision should land. |
| `Rerun needed` | `tldr-plan` / `scope-triage` / `both` / `none`. |

`Rerun needed` mapping (full rule in `classification-rules.md`):

- assumptions / constraints / AC / evidence changed → `tldr-plan`
- if the bug implies a source-plan change that may alter MVP / defer / forbidden / overengineering boundaries → `scope-triage`
- both → `both`
- none of the above → `none`

### §6 Remaining Risks

Risks that survive even after bugs are resolved. Examples: classes of similar bugs not yet audited; environment assumptions not yet verified; tests that pass but cover only the happy path.

| Column | Notes |
|---|---|
| `Risk` | One-line risk statement. |
| `Evidence` | What in the debug log makes this risk visible (e.g., "BUG-001 root cause was a missing `notify_all`; other state-mutating endpoints not yet audited"). |
| `Suggested next action` | Concrete follow-up; usually a `Plan Revision Suggestion` cross-reference or a manual audit task. |

## Status-table update protocol

When a bug transitions status, update the dashboard tables in this order (so the artifact is always internally consistent if the run is interrupted between updates):

1. Update §3 Bug Entries — patch the entry in place.
2. If a fix landed, append a §4 Retest Timeline row.
3. If status crossed the `RESOLVED` boundary (in either direction), move the row between §1 and §2.
4. If the bug introduced or transitioned a Plan Revision Suggestion, update §5.
5. Update §0 Session Summary counts for the current session.
6. Update §6 Remaining Risks if the bug surfaced a class-level concern.

## Placement rationale

§4 Retest Timeline precedes §5 Plan Revision Suggestions intentionally: during debugging the chronological evidence usually matters more than plan patches, and the plan-revision conversation is downstream of "what actually happened in the test runs."
