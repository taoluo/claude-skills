# Output Layout

Final report structure for `<plan-stem>.review-report.md`. **Findings-first.**

## Document skeleton

```markdown
# Code Review Report

Feature: <feature name or unknown>
Source plan: <PLAN.md path>
Review plan: <PLAN.review.md path>
Debug log: <PLAN.debug.md path | n/a>
Shard reports: <plan-stem>.review-report/
Report readiness: <COMPLETE | INCOMPLETE>

## 0. Decision Summary

- Final recommendation:
- Main reason:
- Report readiness:
- Shards completed: <count> of <total> (missing: <list>; malformed: <list>)
- Findings: <count BLOCKER>, <count HIGH>, <count MEDIUM>, <count LOW>, <count NOTE>
- Evidence gaps:
- Reruns recommended:
- Debug-log updates suggested:
- PLAN.md revisions suggested:

## 1. Blocking Findings

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

## 2. High Findings

(same shape as §1)

## 3. Evidence Gaps

| Gap ID | Missing evidence | Why it matters | Suggested next action | Source shard |
|---|---|---|---|---|

## 4. Debug-log Updates Required

| Suggested BUG-* class | Source finding | Suggested Plan impact | One-line summary |
|---|---|---|---|

## 5. Plan Revision Suggestions

| Source-plan gap | Suggested location | Source finding | Rerun needed |
|---|---|---|---|

## 6. Medium / Low Findings

(compact one-line entries grouped by severity, no full Detailed Findings unless reviewer marked important)

## 7. Adversarial Review Results

(per-shard: which adversarial prompts produced findings, which passed, which were inconclusive)

## 8. Review Coverage

| Shard ID | Code areas covered | Anchors covered | % of changed files touched | Status |
|---|---|---|---|---|

## 9. Accepted Risks / Follow-ups

(NOTE-severity items; risks the team has accepted; informational only)

## 10. Appendix: Per-shard Report Index

| Shard ID | Sidecar file | Verdict | Findings count | Status |
|---|---|---|---|---|
```

## §0 Decision Summary — required fields

Kept short — bookkeeping should not outweigh §1 / §2 findings:

- `Final recommendation: APPROVE | APPROVE_WITH_FOLLOWUPS | NEEDS_FIX | BLOCKED`
- `Main reason: <one-line>`
- `Report readiness: COMPLETE | INCOMPLETE` (only these two — input-blocked runs fail before producing the report)
- `Shards completed: <count> of <total>` (with one-line list of missing / malformed shards if any)
- `Findings: <count BLOCKER>, <count HIGH>, <count MEDIUM>, <count LOW>, <count NOTE>`
- `Evidence gaps: <count>`
- `Reruns recommended: tldr-plan | scope-triage | both | none`
- `Debug-log updates suggested: <count>`
- `PLAN.md revisions suggested: <count>`

If the user's invocation included a free-text note, append a `Run context:` line with the note verbatim (audit trail only — does not change behavior).

## §1 Blocking Findings, §2 High Findings — required structure

Every finding in §1 and §2 MUST have all 7 headings (per `references/finding-rules.md`):

- `#### Background` — why the invariant matters; the human reads this without re-opening source artifacts
- `#### Expected behavior / invariant` — what the system should do
- `#### Finding` — what the reviewer found
- `#### Evidence` — concrete file:line references, log excerpts, test names
- `#### Impact` — what happens if not fixed
- `#### Recommended action` — concrete next step
- `#### Routing` — three lines: `Debug-log update:`, `PLAN.md revision:`, `Rerun needed:`

If a row in the §3 Evidence Gaps table has severity ≥ HIGH, it should also surface as a `#### Finding`-shaped block here (with the gap explained in `#### Evidence`).

## §3–§6 specs

- **§3 Evidence Gaps** — 5 cols. `Gap ID` format: `<R*>-<num>` for shard-internal gaps, `<R*>-MALFORMED` or `<R*>-MISSING` for shard-level failures.
- **§4 Debug-log Updates Required** — 4 cols. The aggregator does NOT assign `BUG-*` IDs (that's the human's or `debug-log` skill's job); only the suggested class + plan impact.
- **§5 Plan Revision Suggestions** — 4 cols. The aggregator does NOT edit `PLAN.md`; only suggests the gap and location.
- **§6 Medium / Low Findings** — compact entries: `<Finding ID> | <severity> | <title> | <one-line summary> | <source shard>`. No `Detailed Findings` blocks unless the reviewer marked them important.

## §7–§10 specs

- **§7 Adversarial Review Results** — per-shard subsection: list each adversarial prompt from `<plan-stem>.review.md` §5, mark Passed / Failed / Inconclusive, link to the source `## Adversarial Checks` row in the sidecar.
- **§8 Review Coverage** — what was actually reviewed. Goes near the bottom — not the headline.
- **§9 Accepted Risks / Follow-ups** — NOTE-severity items + acknowledged risks. Informational only; no action.
- **§10 Appendix: Per-shard Report Index** — 5 cols including `Status`: `COMPLETE` / `MALFORMED` / `MISSING`. `Sidecar file` is the relative path or `(none)` for MISSING shards.

## Layout rationale

- §0 is first so a reader can determine the decision without scrolling.
- §1 / §2 are next because findings are the product of a code review.
- §3 (Evidence Gaps) before §4 (debug-log) and §5 (PLAN revisions) because gaps may invalidate the routing recommendations.
- §6 (Medium / Low) before §7 (Adversarial) because findings drive decisions; adversarial results are supporting evidence.
- §8 (Coverage) goes near the bottom — what was reviewed is less important than what was found.
- §9 (Accepted Risks) and §10 (Appendix) are reference material for the human's follow-up.

If §0 + §8 bookkeeping ever outweighs §1–§3 findings, compress bookkeeping. Findings are the product.
