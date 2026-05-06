# Code Review Plan Output Layout

Use this layout for `<plan-stem>.review.md`. Header + 10 sections.

## Document skeleton

```markdown
# Code Review Plan

Feature: <feature name or unknown>
Source plan: <path>
TLDR artifact: <path | missing>
Scope artifact: <path | missing, optional>
Debug log: <path | missing, optional>
Code diff / changed files: <path | inline list | missing>
Review readiness: <READY | NEEDS_INPUT | BLOCKED>

## 0. Review Dashboard

- Review readiness:
- Blocking issues:
- Warnings:
- Tests-passing evidence:
- Code diff / changed files:
- Author clarification:

## 1. Author Clarification

### 1.1 Author Clarification Questions

| QID | Question | Options | Affects | Default if unanswered | Why it matters |
|---|---|---|---|---|---|

### 1.2 Review Assumptions

| Assumption ID | Assumption | Used for | Risk if wrong |
|---|---|---|---|

## 2. Review Input Index

| Artifact | Path | Role | Required? | Status | Freshness notes |
|---|---|---|---|---|---|

## 3. Feature Review Matrix

| Review ID | Feature / area | Plan anchors | Scope categories | Debug bugs | Review angles | Priority | Suggested reviewer |
|---|---|---|---|---|---|---|---|

## 4. Parallel Review Shards

### R01: <title>

- Goal:
- Must-read anchors:
- Scope categories / scope notes:
- Code areas to inspect:
- Review angles:
- Adversarial questions:
- Required tests / evidence:
- Known bugs from debug-log:
- Expected reviewer output:
- Stop conditions:

## 5. Adversarial Review Prompts

### R01

- ...

## 6. Subagent Assignment Plan

| Subagent | Shards | Required inputs | Output file | Independence notes | Estimated effort | Status |
|---|---|---|---|---|---|---|

## 7. Subagent Report Template

(verbatim copy of the report template — see below)

## 8. Final Aggregation Contract

(verbatim copy of the aggregation contract — see references/aggregation-contract.md)

## 9. Review Execution Checklist

- [ ] Author clarification answers (if any) have been folded into §1.2 Review Assumptions or applied to source artifacts and `code-review-plan` re-run.
- [ ] All §6 rows have `Status: READY`.
- [ ] Each subagent has been briefed with their assigned shard(s).
- [ ] Aggregator (human or future `review-report` skill) has the §8 contract.
- [ ] Plan and code diff are at the commits cited in §0.
- [ ] Reviewers know to surface `PLAN_REVISION_NEEDED` findings via the report contract.
```

## Per-section field rules

### Header

| Field | Required | Notes |
|---|---|---|
| `Feature` | yes | Inferred from source-plan title; `unknown` if absent. |
| `Source plan` | yes | Absolute or repo-relative path. |
| `TLDR artifact` | yes | Path if `<plan-stem>.tldr.md` exists; otherwise `missing`. |
| `Scope artifact` | yes | Path if `<plan-stem>.scope.md` exists; otherwise `missing, optional`. |
| `Debug log` | yes | Path if `<plan-stem>.debug.md` exists; otherwise `missing, optional`. |
| `Code diff / changed files` | yes | Inline list, path to a diff file, or `missing`. |
| `Review readiness` | yes | Mirrors §0 — `READY` / `NEEDS_INPUT` / `BLOCKED`. |

### §0 Review Dashboard

Compact human-readable summary. Required fields:

- `Review readiness: READY | NEEDS_INPUT | BLOCKED`
- `Blocking issues: none` OR a bulleted list of plain-language reasons. The only `BLOCKED` cause is `source plan missing` (or `source plan unreadable: <reason>`); every other concern lives in `Warnings:`.
- `Warnings: none` OR a bulleted list (e.g., `code diff / changed files not supplied — shards mark Code areas as unknown`, `tests-passing evidence missing — TEST_EVIDENCE_REVIEW shards depend on smoke evidence the reviewer must supply at exec time`, `.scope.md mtime predates PLAN.md; treat scope categories as possibly stale`, `.debug.md missing — recurrence-risk shards reconstruct bug history from git log`, `human override rationale recorded: "external reviewer requested mid-debug look"`).
- `Tests-passing evidence: debug-log Current status: PASSING | invocation note: <quoted note> | none` (no evidence is **not** a Blocking issue; it is a Warning).
- `Code diff / changed files: present | missing` (missing is a Warning, not a Blocking issue).
- `Author clarification: 0 | N questions in §1.1 (M blocking)`

This dashboard is the **only** place where readiness state lives. There is no separate `Blocking reason:` enum, no `Override reason:` field, no `Soft warnings:` count — everything is plain-language bullets.

### §1 Author Clarification

Two sub-tables.

**§1.1 Author Clarification Questions** — 6 columns: `QID` / `Question` / `Options` / `Affects` / `Default if unanswered` / `Why it matters`. At most 5 rows; every row option-shaped; `Affects` cites concrete shard ID(s), shard angle, or scope boundary, AND includes `tier: blocking` or `tier: non-blocking`. If empty, write `Author clarification: none required`.

**§1.2 Review Assumptions** — 4 columns: `Assumption ID` / `Assumption` / `Used for` / `Risk if wrong`. Records (a) non-blocking working assumptions the skill made instead of asking, and (b) any prior-round chat answers folded in for this run. Each chat-folded row carries `Source: chat answer (single-run)` so reviewers can distinguish from durable assumptions.

**Durability rule**: chat answers landed here are **single-run** — on the next `code-review-plan` rerun, the skill checks whether the answer is now present in source artifacts; if not, the same question is asked again.

**Tier rule**: any §1.1 row with `tier: blocking` pushes `Review readiness:` to at least `NEEDS_INPUT`. Non-blocking questions don't change readiness on their own.

### §2 Review Input Index

6 columns: Artifact / Path / Role / Required? / Status / Freshness notes.

`Status` ∈ `present-current` / `present-stale-suspected` / `missing` / `unknown`. `Freshness notes` is one-line free text — e.g., `mtime aligned with PLAN.md`, `mtime predates PLAN.md by 3 days; rerun tldr-plan if needed`, `BUG-007 PROPOSED revision (REV-002) implicates this artifact`.

### §3 Feature Review Matrix

8 columns: Review ID / Feature or area / Plan anchors / Scope categories / Debug bugs / Review angles / Priority / Suggested reviewer.

- `Plan anchors` carries canonical `AC*` / `C*` / `D*` / `E*` / `M*` / `A*`.
- `Scope categories` carries category labels (`P0-CORRECTNESS-FLOOR`, etc.) and MAY append optional `F*` navigation refs in parentheses (e.g., `P0-CORRECTNESS-FLOOR (F39)`).
- `Priority` ∈ `high` / `medium` / `low` (per the priority-ordering rule in `SKILL.md` Methodology).

### §4 Parallel Review Shards

One subsection per shard, using the canonical shard template (see `references/shard-template.md`).

### §5 Adversarial Review Prompts

Grouped by shard ID; specialized prompts only (no verbatim copies of `references/adversarial-prompts.md` families). Each high-risk shard gets 3–8 specialized prompts.

### §6 Subagent Assignment Plan

7 columns: Subagent / Shards / Required inputs / Output file / Independence notes / Estimated effort / Status.

- When `Review readiness: BLOCKED` (only cause: `PLAN.md` missing), every row carries `Status: BLOCKED — source plan missing` and shards are mostly empty scaffold.
- When readiness is `NEEDS_INPUT`, rows carry `Status: NEEDS_INPUT — <reason>` (a `tier: blocking` author-clarification question is open). The workplan is complete enough to inspect, but the human should resolve the listed input before launching the review fleet unless they explicitly accept the risk.
- When readiness is `READY`, rows carry `Status: READY`. Rows MAY include `(advisory)` annotations — e.g. `Status: READY (advisory: code diff not supplied; reviewer scopes shard manually from PLAN.md anchors)` — to surface optional-input gaps without changing readiness.
- **Special case (code diff missing on a `READY` workplan)**: shard definitions in §4 still exist (the workplan is useful as-is), and every shard's `Code areas to inspect` field is set to `unknown — code diff not supplied; reviewer maps anchors to code at exec time`. §6 rows stay `Status: READY (advisory: code diff missing)`.

### §7 Subagent Report Template

Verbatim-copyable template that subagents use for their per-shard reports:

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

Severity values: `BLOCKER`, `HIGH`, `MEDIUM`, `LOW`, `NOTE`. Finding-type values: `CORRECTNESS`, `RACE`, `RESOURCE_LEAK`, `ERROR_HANDLING`, `TEST_GAP`, `PLAN_DRIFT`, `REGRESSION`, `OVERENGINEERING`, `OBSERVABILITY_GAP`, `PERFORMANCE`, `MAINTAINABILITY`.

### §8 Final Aggregation Contract

Verbatim copy of `references/aggregation-contract.md`. The future aggregator (a `review-report` skill or a human) follows this contract to merge subagent reports.

### §9 Review Execution Checklist

Pre-flight checklist for the human kicking off the review fleet. At minimum 6 items, including the author-clarification checkbox and the §0 readiness gate.

## Placement rationale

§0 Dashboard is first so a reader can determine readiness without scrolling. §1 Author Clarification is second so blocking questions are visible immediately. §4 Parallel Review Shards is the artifact's bulk — it should outweigh §0 + §1 + §2 + §3 combined. If it doesn't, compress the bookkeeping.
