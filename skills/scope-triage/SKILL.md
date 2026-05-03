---
name: scope-triage
description: Classifies feature-plan work items into implementation-scope buckets (forbidden, correctness floor, happy path, observability, lightweight defensive, dev-only, release blocker, deferred hardening, polish, overengineering) and produces a Scope Delta Matrix that surfaces where the classification disagrees with the plan's declared scope. The artifact is for human reviewers; agent handoff happens only after human acceptance. Use after tldr-plan audit passes, when implementation-boundary classification is needed before coding-agent handoff. Source plan is authoritative.
---

# Scope Triage

> **Primary reader: human reviewer. Coding-agent handoff happens only after human acceptance — never automatically when this artifact is written.**

## What this is

`scope-triage` reads a raw implementation plan and classifies every meaningful work item into a fixed set of **implementation-scope buckets**. The output is a **human scope-triage artifact**: it tells a human reviewer what must be blocked, what must be in MVP, what is dev-only, what can be deferred, and what should not be built — and where the skill's classification disagrees with the plan's declared scope.

The scope artifact is NOT an automatic agent-handoff trigger. After `scope-triage` writes the artifact, a human reviews §1 Blocking Questions + §2 Scope Delta Matrix + §4 AC Coverage Check + §11 Non-blocking low-confidence defaults, iterates the **source plan** to resolve disagreements, and only then chooses to invoke a coding agent.

It is the **boundary-control sibling** to `tldr-plan`:

```text
tldr-plan     = makes the plan auditable by a human
scope-triage  = makes the implementation boundary reviewable by a human
                (then, after human acceptance, the boundary is also usable as
                 coding-agent guardrail — but the human-review loop comes first)
```

`scope-triage` is **not** a plan summarizer, not a D0-D6 generator, not an automatic agent-handoff event, not a validator that approves/rejects the whole plan, not a coding skill. It does not modify the source plan, does not modify code, and does not run tests.

## Relationship to `tldr-plan`

`tldr-plan` produces a compact-first, self-contained TLDR artifact for human audit before agent implementation. It extracts:

- problem context, assumptions, hard constraints, acceptance criteria
- milestones, D0-D6 decision trace, evidence, stop conditions

`scope-triage` does not duplicate any of that. It **reuses** those IDs:

```text
Item F01 → Category P0-CORRECTNESS-FLOOR → Source anchors: C13, AC11, D3.d, E5
```

i.e. it is a **classification overlay** on top of plan-defined IDs, not another plan summary.

If both skills run on the same plan, the workflow is:

```text
plan → tldr-plan → human audit → plan revisions
plan → scope-triage → MVP boundary + agent handoff
```

`tldr-plan` answers *"is the plan internally consistent and auditable?"*
`scope-triage` answers *"of the items in the plan, which are MVP, which are forbidden, which are deferred, and which should not be built at all?"*

## When not to use

- For large or ambiguous plans, run `tldr-plan` first; for small, already-clear plans, `scope-triage` may run directly. (`tldr-plan` is a *recommended* upstream, not a *mandatory* dependency.)
- You want a global "approve / reject" verdict — `scope-triage` classifies items, it does not bless plans.
- You want the skill to fire a coding agent automatically — it does not; agent handoff is a human gate.
- You want AC-D-E integrity validation — that is `tldr-plan`'s job.

## Source-of-truth rule

**Primary input** (authoritative):

```text
<plan-dir>/<plan-stem>.md
```

**Optional context** (navigation/anchor recovery only):

```text
<plan-dir>/<plan-stem>.tldr.md
```

Rules:

- The source plan is authoritative. Every classification must be defensible against the source plan.
- If a sibling `<plan-stem>.tldr.md` exists, read it to recover IDs (`A*` / `C*` / `AC*` / `M*` / `D*` / `E*`) and section structure, but do not invent scope rules from TLDR text that are not supported by the source plan.
- If source plan and TLDR disagree on a fact, classify based on the source plan and emit a `TLDR/source drift` finding in §12 of the output.
- If TLDR is missing or appears stale, continue from source plan and mark `TLDR context: missing` (or `stale`) in the output header.

## Invocation

The user invokes the skill with:

```text
/scope-triage @PLAN.md
```

Also support:

- `/scope-triage current plan`
- `/scope-triage current diff`
- `/scope-triage` (no arg)

### Alternative: `--ask-first` interactive mode

For early-stage plans where the operator wants to clarify ambiguities BEFORE producing the artifact:

```text
/scope-triage @PLAN.md --ask-first
```

Behavior:

1. Run extraction and classification (same as default mode).
2. If §1 Blocking Questions has rows, list those rows in chat — at most 5, decision-shaped (A/B/C/D options + default if unanswered) per `references/clarification-protocol.md`.
3. **Wait for user replies in chat** (e.g., "Q1: B, Q2: A, Q3: D"). Apply replies as if they were resolutions in the source plan.
4. After all blocking questions are resolved, write the final `.scope.md` artifact with the user's answers folded into the relevant rows.
5. If §1 has no rows in step 2, skip the chat round and write the artifact immediately (degenerates to default mode).

Notes:

- Chat-mode answers are treated as **single-run resolutions**; they do NOT durably update the source plan. To make answers durable, the user must patch `PLAN.md` and re-run.
- `--ask-first` does NOT replace the human-review loop downstream — even after chat resolutions, the user still reviews §2 Scope Delta Matrix + §4 AC Coverage Check + §11 Non-blocking Questions before invoking a coding agent.

### Refuse-list

If the user supplies a path that already ends in `.tldr.md`, refuse with:

> Input appears to be a TLDR artifact. Run scope-triage on the source plan instead. You may optionally use the sibling TLDR as context.

If the path already ends in `.scope.md`, refuse with:

> Input appears to be an existing scope-triage artifact. Run scope-triage on the source plan instead.

## Output file

Same extension-style convention as `tldr-plan`:

**Naming rule**: `<plan-dir>/<plan-stem>.scope.md`

| Input plan | tldr-plan output | scope-triage output |
| --- | --- | --- |
| `plans/miles-port-unified-plan.md` | `plans/miles-port-unified-plan.tldr.md` | `plans/miles-port-unified-plan.scope.md` |
| `docs/proposal.md` | `docs/proposal.tldr.md` | `docs/proposal.scope.md` |
| `claude/plans/giggly-tumbling-cook.md` | `claude/plans/giggly-tumbling-cook.tldr.md` | `claude/plans/giggly-tumbling-cook.scope.md` |
| `PLAN.md` | `PLAN.tldr.md` | `PLAN.scope.md` |

If the input plan path is read-only / outside the workspace, write to `./<plan-stem>.scope.md` in CWD with a console note explaining the relocation.

If no plan file is supplied, fall back to `./current-plan.scope.md`.

### Overwrite-from-scratch rule

When a prior `<plan-stem>.scope.md` already exists at the output path:

- **Regenerate the artifact from scratch from the source plan** (and, optionally, the sibling `<plan-stem>.tldr.md` for ID navigation per the source-of-truth rule). Do NOT read the prior `.scope.md` as input. Do NOT merge, diff, or carry over rows, classifications, blocking questions, or §11 defaults from the prior version.
- Use the Write tool (full-file overwrite), not Edit / patch / append.
- Iteration happens by re-extracting and re-classifying from the (possibly revised) source plan — NOT by evolving the scope file in place. Items that have been removed from the source plan must disappear from the scope artifact; categories must be re-derived from current plan text, not preserved from the prior run.
- The single permitted exception is when the user is invoking the skill on a *different* plan and explicitly asks to compare classifications across plans — that is out of the default workflow and must be requested.

Rationale: incremental update is silently lossy and category-warping. A row whose source-plan anchor was deleted may survive in the scope artifact; a category that flipped under a plan revision may keep its old label because the prior file biased the re-classification. Full regeneration guarantees every row in the scope artifact is defensible against the source plan as it exists right now.

(This mirrors the same rule in `tldr-plan` — both artifacts are pure projections of the current source plan.)

## Categories

Every work item is classified into exactly one **primary category**. Use the canonical category definitions, examples, and ordered decision process in `references/categories.md`.

Allowed primary categories: `P0-FORBIDDEN`, `P0-CORRECTNESS-FLOOR`, `P1-HAPPY-PATH`, `P1-OBSERVABILITY-FLOOR`, `P1-LIGHTWEIGHT-DEFENSIVE`, `DEV-ONLY`, `P2-RELEASE-BLOCKER`, `P3-DEFER-HARDENING`, `P4-POLISH`, `NO-OVERENGINEERING`.

## Workflow

### Step 1 — Resolve inputs

1. Read the source plan.
2. Look for sibling `<plan-stem>.tldr.md`.
3. If found, read it as optional context (anchor recovery + structure navigation only — source plan remains authoritative).
4. Record in the output:
   - `Source plan:` `<path>`
   - `TLDR context:` `<path>` if found, else `missing` or `stale`

### Step 2 — Extract work items

Extract meaningful implementation items from the source plan: features, subtasks, hard constraints, fail-fast rules, ACs, design decisions, failure modes, recovery paths, tests, observability notes, migration notes, release requirements, future work, rejected alternatives, implicit risks.

Rules:

- Do not over-split tiny implementation details (e.g., one variable rename per line).
- Do not merge semantically different risks into one row.
- Each item should be phrased as an action or requirement, not a description.

Attach **source anchors** in a single column when possible: `A*` / `C*` / `AC*` / `M*` / `D*` / `E*`, or source plan heading / quoted phrase.

### Step 3 — Classify each item

Use the ordered decision process in `references/categories.md` (10 steps; first matching answer wins for the primary category). Highest-risk wins on ties: `P0-FORBIDDEN` > `P0-CORRECTNESS-FLOOR` > `NO-OVERENGINEERING` > `P1-*` > `P2-*` > `P3-*` > `P4-*`.

**Hard rule**: `P1-HAPPY-PATH` MUST be AC-backed. Items without `AC*` / `C*` / `M*` anchor that look like main path are more likely `NO-OVERENGINEERING`.

### Step 4 — Compare against source plan and detect drift

For every item, build the three-column Scope Delta row (source plan declared scope, TLDR mirrored scope, triage classification) and assign a Delta label. Full protocol in `references/scope-delta-protocol.md`.

While classifying, surface in §12 of the output:

- plan ↔ TLDR drift, missing P0 boundaries, P0-CORRECTNESS-FLOOR without test/evidence, AC without coverage, unanchored items, dev-only tools not isolated, deferred hardening accidentally pulled into MVP, speculative framework without evidence.

Do not fabricate missing implementation details. Phrase them as audit findings, not as new spec.

### Step 5 — Apply Clarification Protocol

If any item lands in low confidence, or if Scope Delta produces non-`ALIGNED` MVP-affecting rows, follow the Clarification Protocol in `references/clarification-protocol.md`:

- Decision-shaped Blocking Questions only (A/B/C labels + `Default if unanswered`).
- At most 5 blocking questions per run; group by boundary if more.
- Conservative defaults table for unanswered questions.
- Source/TLDR drift question template.
- Set `Scope review state:` per the state table (`SCOPE_REVIEW_READY` / `SCOPE_REVIEW_READY_WITH_DEFAULTS` / `SCOPE_REVIEW_BLOCKED`). The field was previously called `Handoff readiness:` — renamed to remove the agent-handoff misreading; it gates **human review**, not agent execution.

### Step 6 — Write the scope artifact

Write `<plan-stem>.scope.md` using the layout in `references/output-layout.md` via the Write tool (full-file overwrite). The structure is fixed; the depth of each section scales with plan size.

If a prior `<plan-stem>.scope.md` exists at that path, do NOT read it — regenerate from scratch from the source plan (and optional sibling `.tldr.md`) per the `Overwrite-from-scratch rule` above.

## Style rules

- Use direct, technical language.
- Prefer tables over prose for the category list.
- Use plan-defined IDs (`A*` / `C*` / `AC*` / `M*` / `D*` / `E*`) as anchors.
- When the plan has nested sub-items, use `F01.a`, `F01.b` rather than re-numbering.
- Use `unknown` when the plan does not provide enough context to classify.
- Use `(inferred)` when classifying based on context rather than explicit plan text.

## Quality checklist

Before finalizing the output file, verify:

- Header lists Source plan, TLDR context (path or `missing`/`stale`), and `Scope review state:` field (NOT the legacy `Handoff readiness:`).
- Executive Summary is ≤ 6 lines and includes a `Blocking questions:` line + `Scope delta divergent rows:` line.
- §1 Blocking Questions appears BEFORE §2 Scope Delta Matrix and §3 Category Table.
- If §1 has rows, header state is `SCOPE_REVIEW_BLOCKED` AND §14 outputs the blocked stub (not the full draft).
- Every §1 row has option labels (`A` / `B` / ...) and a `Default if unanswered` value.
- §1 row count ≤ 5 (or rows are grouped by boundary if logically > 5).
- Every `Confidence: Low` row in §3 has a corresponding §11 row.
- §2 Scope Delta Matrix uses the canonical 9-column format (`ID | Feature/Item | Source plan scope | TLDR mirrored scope | Triage classification | Delta | MVP set impact | Review action | Anchors`).
- §2 "Divergent rows" sub-table contains zero rows with `Delta = ALIGNED`.
- §2 routing rule respected: `MVP set impact: yes` rows generate §1 Blocking Questions; `MVP set impact: no` rows go to §11.
- Category Table has every extracted item, each with one primary Category.
- For plans with > 50 extracted items, §3 uses the large-plan summarization strategy AND `Appendix I: Full Category Table` is emitted with every row.
- Every `P0-FORBIDDEN` and `P0-CORRECTNESS-FLOOR` item has a §5 detail block.
- §11 intro lists the three populating sources (Confidence: Low rows; non-`ALIGNED` deltas with `MVP set impact: no`; `CATEGORY_REFRAMED` rows).
- If `Scope review state:` is `SCOPE_REVIEW_READY_WITH_DEFAULTS`, §14 template includes the explicit precondition callout binding §11 acceptance to handoff use.
- §14 Post-Review Handoff Draft (when not blocked) references the source plan path explicitly.
- No D0-D6 generation (that's `tldr-plan`'s job).
- No global approve/reject of the plan.
- No fabricated implementation details — §5 `Required implementation` restates from source plan; if plan is silent, item moves to §10 instead.
- No coding behavior, no shell-out to runtime tools.

## What NOT to do

- Do not generate D0-D6 decision trace — that is `tldr-plan`'s job.
- Do not approve or reject the plan globally — `scope-triage` only classifies items.
- Do not modify the source plan or TLDR.
- Do not implement any feature.
- Do not run tests, run linters, or otherwise execute code.
- Do not invent scope rules from TLDR text not supported by source plan.
- Do not silently merge items across milestones.
- Do not ask open-ended blocking questions (`"what should we do?"`) — every §1 row needs labeled options + a default.
- Do not put low-risk ambiguity into §1 — if the answer doesn't change a P0 / MVP / release / overengineering boundary, it goes to §11 with a default.
- Do not treat user chat answers as durable source-of-truth — when the user resolves a §1 question, the resolution should be patched into the source plan and `scope-triage` rerun.
- Do not call the same item both `P0-FORBIDDEN` and `P3-DEFER-HARDENING` — pick one (highest-risk wins; the other can be a secondary label).
- Do not read or merge a prior `<plan-stem>.scope.md` into the new run — overwrite from scratch (see `Overwrite-from-scratch rule` above). The sibling `.tldr.md` is the only optional context file.

## References

This skill is part of the shared plan-artifact pipeline. See `.claude/skills/README.md` for the overview.

Read these only when needed (per progressive disclosure):

- `references/categories.md` — full 10-category definitions + ordered classification decision process
- `references/clarification-protocol.md` — blocking-question rules, confidence levels, conservative defaults, drift template, scope review state table
- `references/scope-delta-protocol.md` — three-column comparison + `MVP set impact` column, SOURCE-* labels, marker recognition, expected mapping, **8 delta labels** (incl. `CATEGORY_REFRAMED`), blocking rule, display strategy (incl. divergent-rows hard rule + `Aligned but noteworthy` sub-section)
- `references/output-layout.md` — full §0–§14 + Appendix H (Full Scope Delta Matrix) + Appendix I (Full Category Table, large-plan only) output template

Examples:

- `examples/input-plan.md` — compact source-plan example
- `examples/output-scope.md` — corresponding scope-triage output
