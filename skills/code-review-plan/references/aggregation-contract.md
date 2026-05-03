# Aggregation Contract

Rules for merging subagent shard reports into a final review report.

**v1 does NOT execute aggregation.** This contract is *embedded verbatim* in §8 of the artifact and is consumed by a human aggregator (or a future `review-report` skill). `code-review-plan` only ships the contract; it does not run it.

## Inputs

- Per-shard subagent reports, one per `R*` shard ID, conforming to §7 Subagent Report Template.
- The original `<plan-stem>.review.md` artifact (for shard-anchor lookup).
- Optionally: `<plan-stem>.debug.md` (for opening new `BUG-*` entries).

## Step 1 — Collect

Index every shard report by `Shard ID`. Detect missing reports (a shard in `<plan-stem>.review.md` §6 with no corresponding report file).

If any required shard report is missing, the aggregator MUST set `Final recommendation: BLOCKED` with `aggregation incomplete: <list of missing shard IDs>` until the human resolves.

## Step 2 — Deduplicate findings

Merge findings across shards by these equivalence rules (in order):

1. **Same root cause**: canonical signature is `(plan anchor, code area, invariant)`. If two findings share all three, they are duplicates.
2. **Same code area + same `Finding type`**: weaker dedup; surfaces in §3 of the final report as "potential duplicates" rather than auto-merged.
3. **Same failing test / evidence reference**: if two findings cite the same failing assertion, merge.

When merging:

- Preserve **every reviewer's evidence excerpt** verbatim (do not collapse evidence; collapse only the finding row).
- Preserve every reviewer's recommendation (different reviewers may suggest different fixes for the same root cause; keep all).
- Use the highest severity across the merged set.

## Step 3 — Group findings

Within the deduplicated set, group findings:

- Primary grouping: by `Severity` (`BLOCKER` → `HIGH` → `MEDIUM` → `LOW` → `NOTE`).
- Secondary grouping within severity: by `Finding type`.
- Tertiary: by code area (so a reader can scan one subsystem at a time).

## Step 4 — Extract Plan Revision Suggestions

For any shard report with `Verdict: PLAN_REVISION_NEEDED` OR `Plan Impact: Does PLAN.md need revision? = yes`:

- Open a corresponding `BUG-*` entry in `<plan-stem>.debug.md` with `Class: BUG-PLAN-GAP` or `BUG-PLAN-WRONG` (whichever fits) — let `debug-log` record the revision suggestion in its §5, rather than duplicating the suggestion in the final review report.
- The aggregator does NOT assign `BUG-*` IDs directly; it lets the human or the `debug-log` skill do it.
- The final review report's "Plan revisions surfaced" section enumerates these as `[debug-log update needed]` placeholders with the proposed `Class:` and `Plan impact:`.

## Step 5 — Extract debug-log updates needed

Any shard finding that would constitute a new `BUG-*` (recurrence of a known issue, new bug discovered during review, missed regression) is enumerated in the final report's "Debug-log updates required" section:

- Cite the source shard report and finding ID.
- Suggest the `Class:` and `Plan impact:` for the new bug entry.
- Do NOT assign `BUG-*` IDs (let the human or `debug-log` skill assign them).

## Step 6 — Compute final recommendation

Apply the severity tally:

| Condition | `Final recommendation` |
|---|---|
| Any `BLOCKER` severity finding OR any shard verdict `BLOCKED_BY_MISSING_EVIDENCE` (without explicit human waiver) | `BLOCKED` |
| Any shard verdict `NEEDS_FIX`, OR any `HIGH` severity finding | `NEEDS_FIX` |
| All shard verdicts `PASS` / `PASS_WITH_NOTES`, no `BLOCKER` / `HIGH` findings, but `MEDIUM` / `LOW` findings present | `APPROVE_WITH_FOLLOWUPS` |
| All shard verdicts `PASS` / `PASS_WITH_NOTES`, only `NOTE` findings (or no findings) | `APPROVE` |
| Any shard verdict `PLAN_REVISION_NEEDED` (without already counting toward another tier) | `NEEDS_FIX` (the plan revision must land before re-review) |

## Step 7 — Final report shape

The aggregator produces a final report (separate file, not part of `<plan-stem>.review.md`). Suggested layout:

```markdown
# Code Review Report

Source plan:
Code review plan: <plan-stem>.review.md
Reports collected: <list of shard report files>
Aggregation date:

## 0. Executive Summary

- Final recommendation:
- Shard reports: <count> collected, <count> missing
- Findings: <count BLOCKER>, <count HIGH>, <count MEDIUM>, <count LOW>, <count NOTE>
- Plan revisions surfaced:
- Debug-log updates required:

## 1. Blocking Findings (BLOCKER + HIGH)

## 2. Non-blocking Findings (MEDIUM + LOW + NOTE)

## 3. Evidence Gaps

## 4. Adversarial Review Results

## 5. Debug-log Recurrence Risks

## 6. Plan Revisions Surfaced

## 7. Debug-log Updates Required

## 8. Test Coverage Assessment

## 9. Final Recommendation

`APPROVE | APPROVE_WITH_FOLLOWUPS | NEEDS_FIX | BLOCKED`

Rationale:
```

## What the aggregator MUST NOT do

- Do not edit `PLAN.md`, `<plan-stem>.tldr.md`, `<plan-stem>.scope.md`, or `<plan-stem>.debug.md` directly.
- Do not change shard verdicts; the aggregator merges, it does not re-review.
- Do not invent findings the reviewers did not report.
- Do not silently drop low-severity findings — they go to §2.
- Do not assign `BUG-*` IDs unilaterally; defer to the human or the `debug-log` skill.
