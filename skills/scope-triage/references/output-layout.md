# Scope-Triage Output Layout

The structure is fixed; depth scales with plan size. **Gates first** (§1 Blocking Questions + §2 Scope Delta Matrix), then categorization (§3), then per-AC coverage (§4), then per-category drill-downs (§5–§11), then audit gaps + order + handoff (§12–§14).

```markdown
# Scope Triage

Feature: <feature name or unknown>
Source plan: <path>
TLDR context: <path | missing | stale>
Scope review state: <SCOPE_REVIEW_READY | SCOPE_REVIEW_READY_WITH_DEFAULTS | SCOPE_REVIEW_BLOCKED>

## 0. Executive Summary

- MVP boundary: <one-line description of what MVP includes vs excludes>
- P0 risks: <one-line — most dangerous items that must be blocked / asserted>
- Main correctness floor: <one-line — biggest non-trivial correctness requirement>
- Main overengineering risk: <one-line — biggest item that should NOT be built>
- Blocking questions: <count, with one-line summary if any; "None" if empty>
- Scope delta divergent rows: <count of non-`ALIGNED` rows in §2; "None" if all aligned>

## 1. Blocking Questions

Questions that MUST be answered before coding-agent handoff (§14). Empty = no blockers.

Format if empty:

> None. Ambiguous low-risk items (if any) are marked `Confidence: Low` in §3 Category Table and detailed in §11. Non-`ALIGNED` Scope Delta rows that don't change MVP membership go to §11.

Format if rows exist:

| QID | Feature / Item | Question | Options | Affects | Default if unanswered | Reason |
|---|---|---|---|---|---|---|

Constraints (see `references/clarification-protocol.md` + `references/scope-delta-protocol.md` for full rules):

- At most 5 rows per run; if more would be needed, group by boundary (P0 / MVP / release / defer-vs-overengineering / drift) and consolidate.
- Every row MUST have option labels (A/B/C/...) and a `Default if unanswered` value.
- Reason MUST cite which boundary the answer changes (P0 / MVP / release / overengineering / drift). Scope Delta-driven blocking questions cite the Delta label (e.g., `Delta=PLAN_MORE_AGGRESSIVE`).

## 2. Scope Delta Matrix

This table compares the source plan's declared scope with `scope-triage`'s inferred classification. Any row with a non-`ALIGNED` delta should be reviewed by a human. See `references/scope-delta-protocol.md` for label semantics.

For small plans (< 20 items): include all rows directly.

For large plans (≥ 20 items OR ≥ 12 ALIGNED rows): split into `### Divergent rows (require human review)` + optional `### Aligned but noteworthy` + `### Aligned summary` sub-headings. **Hard rule**: the `### Divergent rows` table MUST contain only rows whose `Delta != ALIGNED`. Aligned rows worth surfacing once go in `### Aligned but noteworthy`; everything else goes to the bullet `### Aligned summary`.

Canonical 9-column format (used for both small-plan single-table and large-plan divergent sub-table):

| ID | Feature / Item | Source plan scope | TLDR mirrored scope | Triage classification | Delta | MVP set impact | Review action | Anchors |
|---|---|---|---|---|---|---|---|---|

Where:
- **Source plan scope** ∈ `SOURCE-MVP` / `SOURCE-MILESTONE:<Mn>` / `SOURCE-RELEASE-BLOCKER` / `SOURCE-DEFERRED` / `SOURCE-FUTURE` / `SOURCE-OUT-OF-SCOPE` / `SOURCE-FORBIDDEN` / `SOURCE-DEV-ONLY` / `SOURCE-POLISH` / `SOURCE-UNKNOWN`
- **Delta** ∈ `ALIGNED` / `PLAN_MORE_AGGRESSIVE` / `TRIAGE_MORE_AGGRESSIVE` / `PLAN_TLDR_DRIFT` / `MISSING_SOURCE_SCOPE` / `UNANCHORED_TRIAGE` / `CATEGORY_REFRAMED` / `HUMAN_REVIEW_REQUIRED` (8 fixed values; full definitions in `references/scope-delta-protocol.md`)
- **MVP set impact** ∈ `yes` / `no` / `unclear` — drives blocking-vs-non-blocking routing mechanically
- **Review action** ∈ `Blocking question (§1 QID)` / `Non-blocking (§11 QID)` / `No action` / `Patch source plan`

Routing rule:

| MVP set impact | Required action |
|---|---|
| `yes` | §1 Blocking Question (cross-referenced via `Review action`) |
| `unclear` | §1 Blocking question OR strong §11 non-blocking, depending on `Confidence` |
| `no` | §11 Non-blocking row |

`Delta=ALIGNED` and `Delta=CATEGORY_REFRAMED` rows always have `MVP set impact: no` by definition.

If full matrix is needed for any plan size, emit optional `Appendix H: Full Scope Delta Matrix` with all rows including `ALIGNED`.

## 3. Category Table

| ID | Item | Category | Priority | Action | Anchors | Confidence | Reason |
|---|---|---|---|---|---|---|---|

`Confidence` column uses `high` / `medium` / `low` per `references/clarification-protocol.md`. Every `Confidence: Low` row MUST have a corresponding §11 row.

**Large-plan display strategy** (when extracted items > 50):

The §3 visible Category Table shows ONLY:

- all `P0-FORBIDDEN` and `P0-CORRECTNESS-FLOOR` rows
- all rows with non-`ALIGNED` Delta (per §2 Scope Delta Matrix)
- all rows with `Confidence: Low` or `Confidence: medium`
- all rows with `Action != "implement"` (i.e., `defer`, `not implement`, `keep behind flag`, `keep behind audit`)

Routine `ALIGNED` `P1-*` / `P3-*` / `P4-*` rows with `Confidence: high` are summarized by ID range, e.g.:

> `F42–F64`: 23 P1-HAPPY-PATH items, all ALIGNED, all Confidence: high. See Appendix I for details.

When summarization triggers, emit `## Appendix I: Full Category Table` (see Appendix I spec at the bottom of this file) containing every extracted row.

For plans with ≤ 50 items, include all rows directly in §3 and skip Appendix I.

## 4. AC Coverage Check

Maps each AC to the scope items that cover it. **Does NOT validate the AC-D-E grid; for AC↔D↔E integrity use `tldr-plan` and its Step 9a integrity script.**

For every `AC*` declared in the source plan (or `<plan-stem>.tldr.md` if available), show which scope items cover it and whether any covering item has a non-`ALIGNED` delta:

| AC | Source milestone | Covered by scope items | Delta warnings | Missing? |
|---|---|---|---|---|

Where:
- **Covered by scope items** lists IDs from §3 Category Table that implement the AC.
- **Delta warnings** flags non-`ALIGNED` deltas on the covering items (e.g., "F01 has Delta=`PLAN_MORE_AGGRESSIVE`, human review required").
- **Missing?** = `yes` if no scope item covers this AC; surfaces the AC to §12 Drift.

If the plan declares no `AC*`, write `No AC declared in source plan; AC Coverage Check skipped. See §12 Drift.`

## 5. P0 Must-Address

For each `P0-FORBIDDEN` and `P0-CORRECTNESS-FLOOR` item:

### <ID> <short title>

- Category: <P0-FORBIDDEN | P0-CORRECTNESS-FLOOR>
- Why it matters: <what breaks if violated>
- Required implementation: <restate from source plan; do NOT invent — flag in §12 if plan is silent>
- Required test/evidence: <how to verify>
- Anchors: <C* / AC* / D* / E* refs>

## 6. MVP Implementation Set

Items in MVP scope. Include only:

- `P1-HAPPY-PATH`
- `P1-OBSERVABILITY-FLOOR`
- `P1-LIGHTWEIGHT-DEFENSIVE`
- selected `DEV-ONLY` (P1) if needed to safely build/test MVP

Plus the `P0-CORRECTNESS-FLOOR` items (cross-referenced from §5).

## 7. Dev-Only Scaffolding

For each `DEV-ONLY` item:

- Purpose: <what it accelerates>
- How it accelerates implementation/debugging: <concrete example>
- Required isolation from production: <env flag / branch / module>
- Remove/keep policy: <delete after gate? keep behind flag indefinitely?>

## 8. Release Blockers

List `P2-RELEASE-BLOCKER` items.

For each:

- Why it blocks release: <reason>
- What must be true before shipping: <criterion>
- Whether it blocks local MVP: <yes/no>

## 9. Deferred Hardening

List `P3-DEFER-HARDENING`.

For each:

- Why deferred: <complexity / production-only / SLA-driven>
- Revisit trigger: <observation / milestone / evidence>
- Risk if never implemented: <consequence>

## 10. Explicitly Not Doing

List `NO-OVERENGINEERING` (and any `P4-POLISH` rolled in as one-line entries since polish is short).

For each `NO-OVERENGINEERING`:

- Why not now: <speculative / no second consumer / premature abstraction>
- What evidence would justify revisiting: <concrete trigger>
- How to prevent accidental implementation: <forbidden-line / spec note / test>

For `P4-POLISH` items, keep one-line entries (no detail block).

## 11. Non-blocking Questions / Low-confidence Defaults

Non-blocking deltas and low-confidence defaults. Three populating sources:

1. Items with `Confidence: Low` in §3 Category Table.
2. Non-`ALIGNED` Scope Delta rows where `MVP set impact: no`.
3. `CATEGORY_REFRAMED` rows (always non-blocking by definition).

Empty = no low-confidence rows AND no non-MVP-affecting deltas.

| QID | Feature / Item | Question | Suggested default | Affects | Reason |
|---|---|---|---|---|---|

These do not block §14 handoff in `SCOPE_REVIEW_READY` state, but in `SCOPE_REVIEW_READY_WITH_DEFAULTS` state the human MUST explicitly accept these defaults (or patch the source plan) before invoking a coding agent — see §14 precondition callout.

## 12. Drift / Missing Constraints

Surface gaps and inconsistencies. Categories:

- **TLDR/source drift**: TLDR claims X but source plan does not support → also reflected in §2 as `PLAN_TLDR_DRIFT` rows
- **Missing P0 boundary**: implied boundary should exist but plan is silent
- **Missing test/evidence**: `P0-CORRECTNESS-FLOOR` without verification
- **Missing observability**: failure mode without diagnostic surface
- **Missing AC coverage**: AC declared but no scope item covers it (§4 flagged)
- **Ambiguous plan item**: cannot classify with confidence > medium → cross-link to §1 or §11
- **Unanchored item**: implementation detail without `AC` / `C` / `D` parent
- **Stale TLDR**: TLDR appears to predate source plan revisions

Do not fabricate fixes. Phrase as audit findings the human should resolve in the *plan*.

## 13. Recommended Implementation Order

1. P0 forbidden guards (assert / reject / deny)
2. P0 correctness floor
3. P1 happy path
4. P1 observability floor
5. P1 lightweight defensive checks
6. P1/P2 dev-only test/simulation support (only what's needed to build MVP safely)
7. P2 release blockers (before shipping)
8. P3 deferred hardening (only after explicit approval or evidence)

## 14. Post-Review Handoff Draft (copy-paste, conditional on human review)

**This handoff is conditional on human review.** It does NOT auto-fire when the artifact is written. The human reviewer must accept §1 Blocking Questions resolved + §2 Scope Delta Matrix reviewed + §4 AC Coverage Check acceptable + §11 Non-blocking defaults accepted (or patched into source plan) BEFORE invoking a coding agent with this block.

When `Scope review state:` is `SCOPE_REVIEW_READY_WITH_DEFAULTS`, the §14 template MUST begin with this precondition callout (verbatim) above the handoff body:

> **Precondition for `SCOPE_REVIEW_READY_WITH_DEFAULTS`**: the human reviewer MUST accept §11 defaults (or patch them into the source plan) before passing this block to a coding agent. The state name signals "human review can proceed" — NOT "agent ready". Defaults that have NOT been explicitly accepted leave this artifact in an unbound state — the agent has no authority to act on them.

In `SCOPE_REVIEW_READY` state the callout is omitted (no defaults to accept).

If `Scope review state:` is `SCOPE_REVIEW_BLOCKED`, output ONLY this stub:

```text
HANDOFF BLOCKED — scope-triage has §1 Blocking Questions OR MVP-affecting §2 Scope Delta divergence outstanding.

Resolve §1 / §2 in the source plan, then rerun scope-triage. Do not begin implementation.
```

Otherwise (state is `SCOPE_REVIEW_READY` or `SCOPE_REVIEW_READY_WITH_DEFAULTS`), output (with the precondition callout above the body when state is `_WITH_DEFAULTS`):

```text
PRECONDITION (HUMAN ONLY) — before passing this block to a coding agent, confirm:
- §1 Blocking Questions: resolved (in source plan)
- §2 Scope Delta Matrix: divergent rows reviewed; PLAN_MORE_AGGRESSIVE / TRIAGE_MORE_AGGRESSIVE accepted or patched into source plan
- §4 AC Coverage Check: every AC has at least one covering item; delta warnings reviewed
- §11 Non-blocking defaults: accepted or patched

If any of the above is unresolved, do NOT use this handoff. Resolve in source plan and rerun scope-triage.

You are implementing the feature described in <source-plan-path>.

Source of truth: the source plan above.
Boundary control: <scope-file-path>

Before writing code:
1. Read the source plan in full.
2. Read the scope file's §3 Category Table and §5 P0 Must-Address.
3. Implement only items classified P0-CORRECTNESS-FLOOR and P1-* in the scope file.
4. Add P0-FORBIDDEN guards (asserts / rejects) at the boundaries the scope file identifies.
5. Add the minimum observability listed under P1-OBSERVABILITY-FLOOR.
6. Add only the P1-LIGHTWEIGHT-DEFENSIVE checks listed; do not invent additional defenses.
7. Add DEV-ONLY scaffolding only if §7 lists it as needed for MVP.
8. If `Scope review state:` is SCOPE_REVIEW_READY_WITH_DEFAULTS, you MUST have explicitly accepted §11 defaults (or patched them into the source plan) before this handoff is valid; the listed defaults do NOT apply automatically.

Do NOT:
- Implement any item classified NO-OVERENGINEERING.
- Pull P3-DEFER-HARDENING items into MVP without explicit approval from the user.
- Generalize beyond the explicit source-plan scope.

Stop and ask if:
- Implementation requires crossing a P0-FORBIDDEN boundary.
- A required item is missing both source plan and scope file (§12 flags a gap).
- PLAN.md (source plan) and PLAN.scope.md (this scope file) disagree on any item's scope/category. Do NOT let PLAN.scope.md silently override PLAN.md — Scope Delta Matrix entries with non-`ALIGNED` deltas surface real plan disagreement that the human must resolve in PLAN.md (or explicitly accept).
- Implementation pulls a P3 or NO-OVERENGINEERING item into MVP path.
```

## Appendix H: Full Scope Delta Matrix (optional, large plans only)

If §2 Scope Delta Matrix used the divergent-rows-only format because the plan has many ALIGNED items, this appendix lists the complete matrix with every row including ALIGNED. Uses the canonical 9-column format.

| ID | Feature / Item | Source plan scope | TLDR mirrored scope | Triage classification | Delta | MVP set impact | Review action | Anchors |
|---|---|---|---|---|---|---|---|---|

For small plans (< 20 items), omit Appendix H entirely.

## Appendix I: Full Category Table (optional, large plans only)

If §3 Category Table used the large-plan summarization strategy because the plan has > 50 extracted items, this appendix lists every extracted row.

| ID | Item | Category | Priority | Action | Anchors | Confidence | Reason |
|---|---|---|---|---|---|---|---|

For plans with ≤ 50 items, omit Appendix I entirely (§3 contains everything).
```
