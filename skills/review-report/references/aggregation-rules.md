# Aggregation Rules

How the main agent merges shard reports into the final findings-first `<plan-stem>.review-report.md`.

## Upstream contract

`code-review-plan/references/aggregation-contract.md` is the canonical source for dedup rules and final-recommendation computation. This file specializes those rules for the `review-report` execution context (where the main agent has just spawned the subagents and written the sidecar files itself). When this file says something different from the upstream contract, treat the upstream as authoritative and patch this file.

## Step 1: Collect

Walk `<plan-stem>.review-report/<R*>.md`. Cross-reference with `<plan-stem>.review.md` §6 to detect missing shards.

For each shard in §6:

| Sidecar state | Classification |
|---|---|
| File exists, schema-check passed | `COMPLETE`; use the report's verdict + findings. |
| File exists, schema-check failed (file has `Status: MALFORMED` header) | `MALFORMED`; route to `BLOCKED_BY_MISSING_EVIDENCE`; surface in §3 Evidence Gaps as `R*-MALFORMED`. |
| File does not exist | `MISSING`; route to `BLOCKED_BY_MISSING_EVIDENCE`; surface in §3 Evidence Gaps as `R*-MISSING`; record in §0 `Shards missing:`. |

## Step 2: Schema check

Apply the rules in `references/shard-report-schema.md`. The check **marks** malformed reports — it does not reject them. The main agent always writes the sidecar; aggregation continues.

No retry. No fix-up agent.

## Step 3: Deduplicate findings

Merge findings only if **≥2 of these signals match**:

- same plan anchor
- same code area
- same invariant (the `Background` + `Expected behavior` framing)
- same root cause
- same failing test / evidence reference

When merging:

- Keep the highest severity across the merged set.
- Keep all source `Shard ID`s.
- Preserve every reviewer's evidence excerpt verbatim (do not collapse evidence; collapse only the row in the findings index table).
- Keep the strongest recommendation. If reviewers disagree, surface both with `Recommendations from R<X>:` / `Recommendations from R<Y>:` sub-bullets.
- If only one signal matches, do NOT merge; instead add `Related findings: <Finding ID>` to each.

## Step 4: Group findings

By `Severity` (BLOCKER → HIGH → MEDIUM → LOW → NOTE), then by `Finding type` within severity.

## Step 5: Extract routing recommendations

| Routing field | Destination |
|---|---|
| `Routing.Debug-log update` (not `none`) | §4 Debug-log Updates Required (one row per finding; aggregator does NOT assign `BUG-*` IDs) |
| `Routing.PLAN.md revision` (not `none`) | §5 Plan Revision Suggestions |
| `Routing.Rerun needed` (not `none`) | Consolidated into §0 dashboard line `Reruns recommended: tldr-plan / scope-triage / both / none` |

The aggregator never auto-actions these. They are recommendations for the human.

## Step 6: Compute final recommendation

Severity-tally rule, mirrors `code-review-plan`'s aggregation contract. Evaluate top-down; first matching condition wins:

| # | Condition | Final recommendation |
|---|---|---|
| 1 | **Missing or malformed required shard** | `BLOCKED`. A shard is "required" by default; "optional" only if `<plan-stem>.review.md` §6 explicitly marks it (e.g., a row with `Optional: yes` annotation). §0 records `Main reason: incomplete review coverage — missing shards: <R*>; malformed shards: <R*>`. |
| 2 | Any `BLOCKER` severity finding OR any required shard verdict `BLOCKED_BY_MISSING_EVIDENCE` | `BLOCKED` |
| 3 | Any shard verdict `NEEDS_FIX` OR any `HIGH` finding | `NEEDS_FIX` |
| 4 | Any shard verdict `PLAN_REVISION_NEEDED` not already counted | `NEEDS_FIX` |
| 5 | All `PASS` / `PASS_WITH_NOTES`, no `BLOCKER` / `HIGH`, but `MEDIUM` / `LOW` present | `APPROVE_WITH_FOLLOWUPS` |
| 6 | All `PASS` / `PASS_WITH_NOTES`, only `NOTE` (or none) | `APPROVE` |

There is no human-waiver override. If a missing/malformed shard is not acceptable for the round, the human reruns `review-report` (which re-spawns the missing/malformed shard). If a missing/malformed shard IS acceptable, the human marks it `Optional: yes` in `<plan-stem>.review.md` §6 and reruns — that's the only way to suppress its contribution to the final recommendation.

## Step 7: Compute report readiness

Two values only — `Report readiness:` is NOT a workflow state, it's a freshness flag for the human:

| Condition | `Report readiness:` |
|---|---|
| All shards `COMPLETE` (no MALFORMED, no MISSING) | `COMPLETE` |
| Any shard MALFORMED or MISSING | `INCOMPLETE` |

There is no `BLOCKED_AT_INPUT` value. Input-blocked runs (review-plan missing, `Review readiness != READY`, runtime can't spawn subagents) fail BEFORE writing the report — they don't produce an artifact at all; the user sees a single chat error reason.

## Step 8: Write the final report

Per `references/output-layout.md` — findings-first.

Aggregator MUST NOT:

- Edit `PLAN.md`, `<plan-stem>.tldr.md`, `<plan-stem>.scope.md`, `<plan-stem>.debug.md`, or `<plan-stem>.review.md`.
- Change shard verdicts (the aggregator merges, it does not re-review).
- Invent findings the reviewers did not report.
- Silently drop low-severity findings — they go to §6.
- Assign `BUG-*` IDs unilaterally.
- Auto-rerun any sibling skill.
