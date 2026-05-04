# Shard Report Schema

The strict per-shard report schema. Subagents output this verbatim. The main agent's schema check (Workflow Step 3) **marks** malformed reports — does not reject them. No parser script; the check is behavioral.

## Vocabulary references

`Verdict`, `Severity`, `Finding type`, and `Final recommendation` values are owned by `code-review-plan`'s `references/output-layout.md` (verdict / severity / finding type) and `references/aggregation-contract.md` (final recommendation). This file does not redefine them — it only enforces that subagent reports use the allowed values.

## Schema

```markdown
# Review Shard Report

Shard ID:
Shard title:
Reviewer:
Inputs reviewed:
Code areas reviewed:
Plan anchors:
Debug-log bugs reviewed:
Review angles:

## Verdict

`PASS | PASS_WITH_NOTES | NEEDS_FIX | BLOCKED_BY_MISSING_EVIDENCE | PLAN_REVISION_NEEDED`

## Findings

| Finding ID | Severity | Type | Title | Plan anchors | Code area | Evidence | Recommendation |
|---|---|---|---|---|---|---|---|

## Detailed Findings

### <Finding ID>: <title>

#### Background

#### Expected behavior / invariant

#### Finding

#### Evidence

#### Impact

#### Recommended action

#### Routing

- Debug-log update:
- PLAN.md revision:
- Rerun needed:

## Evidence Gaps

| Gap ID | Missing evidence | Why it matters | Suggested next action |
|---|---|---|---|

## Adversarial Checks

| Check | Result | Evidence |
|---|---|---|

## Reviewer Notes
```

## Schema-check rules (behavioral)

The main agent performs these checks per returned shard report. Each violation marks the shard MALFORMED.

| # | Check | Marks malformed if … |
|---|---|---|
| 1 | Top-level header fields | Any of `Shard ID`, `Shard title`, `Reviewer`, `Inputs reviewed`, `Code areas reviewed`, `Plan anchors`, `Debug-log bugs reviewed`, `Review angles` is missing. |
| 2 | Verdict | `## Verdict` section absent OR value not one of the 5 allowed verdict tokens. |
| 3 | Findings table | `## Findings` table absent. (Empty table is fine if Verdict is `PASS` or `BLOCKED_BY_MISSING_EVIDENCE` with non-empty `## Evidence Gaps`.) |
| 4 | Severity / Finding type values | Any row's `Severity` ∉ {`BLOCKER`, `HIGH`, `MEDIUM`, `LOW`, `NOTE`} OR `Type` ∉ the 11 allowed Finding-type values. |
| 5 | BLOCKER/HIGH detail requirement | Any BLOCKER or HIGH row in `## Findings` lacks a corresponding `### <Finding ID>: …` subsection in `## Detailed Findings`. |
| 6 | BLOCKER/HIGH 7-field requirement | Any `## Detailed Findings` subsection for a BLOCKER/HIGH finding is missing any of the 7 required headings: `#### Background`, `#### Expected behavior / invariant`, `#### Finding`, `#### Evidence`, `#### Impact`, `#### Recommended action`, `#### Routing`. |
| 7 | Routing required cells | A `#### Routing` block lacks any of the 3 lines: `- Debug-log update:`, `- PLAN.md revision:`, `- Rerun needed:` (each may be `none`, but the cell must exist). |
| 8 | Sections present | `## Evidence Gaps`, `## Adversarial Checks`, `## Reviewer Notes` headings are absent. (Tables / content may be empty, but the headings are required for the schema check to confirm the report is intentionally complete.) |

## What "marked malformed" means

When the schema check fails:

1. The main agent **still writes** `<plan-stem>.review-report/<R*>.md` with the raw subagent return.
2. Prepends a header block:
   ```text
   Status: MALFORMED
   Reason: <one-line summary of the first failed check>
   Schema-check details: <bullet list of all failed check numbers>
   ```
3. Surfaces the shard in §3 Evidence Gaps of the final report (`Gap ID = R*-MALFORMED`).
4. Routes the shard to `BLOCKED_BY_MISSING_EVIDENCE` in aggregation.
5. Does NOT retry the subagent. Does NOT spawn a fix-up subagent.

## What "MISSING" means (distinct from MALFORMED)

If the subagent never returns (timed out, refused, runtime error mid-spawn), the main agent does NOT create a sidecar file. Instead:

1. Records the shard as MISSING in §0 (`Shards missing: <R*>`).
2. Surfaces in §3 Evidence Gaps (`Gap ID = R*-MISSING`).
3. Lists in §10 Appendix with `Sidecar file: (none)`, `Status: MISSING`.
4. Routes the shard to `BLOCKED_BY_MISSING_EVIDENCE` in aggregation.

The two failure modes are distinct because they tell the human different things:
- MALFORMED = the reviewer ran but the output is unusable; the raw return is in the sidecar for the human to inspect.
- MISSING = the reviewer never produced output; nothing to inspect, just rerun.
