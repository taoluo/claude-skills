# Scope Delta / Human Review Protocol

`scope-triage` MUST NOT silently replace the source plan's declared scope with its own classification. For every extracted work item, compare three columns and surface disagreement explicitly to the human reviewer.

## Three-column comparison

For every item:

1. **Source plan declared scope** — what the raw source plan appears to declare about the item's scope/milestone.
2. **TLDR mirrored scope** — what the sibling `<plan-stem>.tldr.md` mirrors (if available).
3. **Scope-triage classification** — this skill's inferred implementation-boundary category.

The source plan is authoritative. The TLDR is only a derived navigation aid. If source and TLDR disagree, label `PLAN_TLDR_DRIFT` and ask a Blocking Question.

In addition to the three comparison columns and the `Delta` label, every Scope Delta Matrix row carries an explicit **`MVP set impact`** column with values `yes` / `no` / `unclear`. The full table format is canonical:

```
| ID | Feature / Item | Source plan scope | TLDR mirrored scope | Triage classification | Delta | MVP set impact | Review action | Anchors |
```

`MVP set impact` makes blocking-vs-non-blocking determination mechanical, not interpretive. See `## Blocking rule` below for how it drives §1 vs §11 routing.

## Normalized `SOURCE-*` labels

Translate plan markers into one of these labels for column 1 of the matrix:

- `SOURCE-MVP` — explicitly MVP / "must ship now" / current milestone
- `SOURCE-MILESTONE:<Mn>` — pinned to a specific milestone (e.g., `SOURCE-MILESTONE:M11.1`)
- `SOURCE-RELEASE-BLOCKER` — must complete before release / migration / rollback
- `SOURCE-DEFERRED` — deferred to a named follow-up
- `SOURCE-FUTURE` — future / nice-to-have / not yet scheduled
- `SOURCE-OUT-OF-SCOPE` — explicitly excluded from this plan
- `SOURCE-FORBIDDEN` — explicitly prohibited (must not / never / fail-fast)
- `SOURCE-DEV-ONLY` — debug / test / dev tooling only
- `SOURCE-POLISH` — nice-to-have ergonomics / docs / formatting
- `SOURCE-UNKNOWN` — no scope marker found in source plan

## Marker recognition heuristics

| Source plan phrasing | Normalized label |
|---|---|
| `MVP`, `must ship`, `Phase 1`, `current milestone`, `M<current>` | `SOURCE-MVP` or `SOURCE-MILESTONE:<Mn>` |
| `before release`, `ship blocker`, `migration required`, `rollback required` | `SOURCE-RELEASE-BLOCKER` |
| `future`, `follow-up`, `M11.5`, `production hardening`, `defer` | `SOURCE-DEFERRED` / `SOURCE-FUTURE` |
| `out of scope`, `non-goal`, `do not support`, `rejected alternative` | `SOURCE-OUT-OF-SCOPE` |
| `must not`, `never`, `forbidden`, `fail-fast reject` | `SOURCE-FORBIDDEN` |
| `debug only`, `test helper`, `mock`, `simulator` | `SOURCE-DEV-ONLY` |
| `nice to have`, `polish`, `docs`, `formatting` | `SOURCE-POLISH` |
| (no marker) | `SOURCE-UNKNOWN` |

## Expected mapping (alignment check)

| Source plan scope | Expected scope-triage category |
|---|---|
| `SOURCE-MVP` / `SOURCE-MILESTONE:<current>` | `P0-CORRECTNESS-FLOOR`, `P1-HAPPY-PATH`, `P1-OBSERVABILITY-FLOOR`, `P1-LIGHTWEIGHT-DEFENSIVE`, `DEV-ONLY` (P1) |
| `SOURCE-FORBIDDEN` | `P0-FORBIDDEN` |
| `SOURCE-RELEASE-BLOCKER` | `P2-RELEASE-BLOCKER` |
| `SOURCE-DEFERRED` / `SOURCE-FUTURE` | `P3-DEFER-HARDENING`, `P4-POLISH`, future-milestone note |
| `SOURCE-OUT-OF-SCOPE` | `NO-OVERENGINEERING` or `P0-FORBIDDEN` (depending on whether excluded for scope or correctness reasons) |
| `SOURCE-DEV-ONLY` | `DEV-ONLY` |
| `SOURCE-POLISH` | `P4-POLISH` |
| `SOURCE-UNKNOWN` | any category, but `Confidence` must be ≤ `medium` unless strongly anchored to `AC*` / `C*` / `D*` / `M*` |

## Delta labels (8 fixed values)

- `ALIGNED` — source scope and triage category agree per the expected mapping.
- `PLAN_MORE_AGGRESSIVE` — plan wants the item in MVP / current milestone, but triage classifies as deferred / polish / overengineering.
- `TRIAGE_MORE_AGGRESSIVE` — plan marks future / deferred / out-of-scope, but triage classifies as P0 / P1 / P2.
- `PLAN_TLDR_DRIFT` — source plan and sibling TLDR disagree on milestone / AC / hard constraint / stop condition / scope.
- `MISSING_SOURCE_SCOPE` — source plan does not declare scope/milestone for the item.
- `UNANCHORED_TRIAGE` — triage classification lacks `AC*` / `C*` / `D*` / `M*` / source-quote anchor.
- `CATEGORY_REFRAMED` — source plan and triage agree the item belongs in the **current implementation/review set**, but disagree on **category framing**. Example: `SOURCE-MVP` (plan §3.1 Layer 7 lightweight defensive) ↔ triage `DEV-ONLY` (test-only fixture). Always non-MVP-affecting → §11. Distinct from `HUMAN_REVIEW_REQUIRED` which signals classification cannot be safely defaulted.
- `HUMAN_REVIEW_REQUIRED` — classification cannot be safely defaulted (multiple plausible categories with **similar evidence**, OR the row's MVP-set impact is genuinely unclear). Use this when no labeled default is defensible; use `CATEGORY_REFRAMED` when source/triage clearly agree on inclusion but pick different categories.

## Blocking rule

The `MVP set impact` column drives routing mechanically:

| MVP set impact | Required action |
|---|---|
| `yes` | Blocking Question (§1) |
| `unclear` | Blocking question OR strong non-blocking — depends on `Confidence` |
| `no` | §11 Non-blocking Questions / Low-confidence Defaults |

`Delta=ALIGNED` rows always have `MVP set impact: no` (alignment by definition does not flip membership). `Delta=CATEGORY_REFRAMED` rows always have `MVP set impact: no` (same set, different framing). All other delta labels require evaluating impact per row.

Examples of MVP-affecting deltas (always `MVP set impact: yes` → blocking):

| Source plan | Triage | Delta | MVP set impact | Blocking? |
|---|---|---|---|---|
| `SOURCE-MVP` | `P3-DEFER-HARDENING` | `PLAN_MORE_AGGRESSIVE` | yes | YES — plan wants in MVP, triage wants out |
| `SOURCE-MVP` | `NO-OVERENGINEERING` | `PLAN_MORE_AGGRESSIVE` | yes | YES |
| `SOURCE-FUTURE` | `P0-CORRECTNESS-FLOOR` | `TRIAGE_MORE_AGGRESSIVE` | yes | YES — plan defers what triage thinks is correctness floor |
| `SOURCE-OUT-OF-SCOPE` | `P1-HAPPY-PATH` | `TRIAGE_MORE_AGGRESSIVE` | yes | YES |
| `SOURCE-MVP` | `P1-LIGHTWEIGHT-DEFENSIVE` | `ALIGNED` | no | NO — both in MVP |
| `SOURCE-MVP` | `P1-OBSERVABILITY-FLOOR` | `ALIGNED` | no | NO — both in MVP |
| `SOURCE-MVP` (Layer 7 lightweight defensive) | `DEV-ONLY` | `CATEGORY_REFRAMED` | no | NO — same MVP set, different category framing |
| `SOURCE-FUTURE` ("nice-to-have") | `NO-OVERENGINEERING` | `TRIAGE_MORE_AGGRESSIVE` | no | NO — both reject from MVP, just stricter on whether to ever build |

## Display strategy for large plans

**Hard rule** — the visible "Divergent rows" table MUST contain only rows whose `Delta != ALIGNED`. Mixing `ALIGNED` rows under a "Divergent" heading directly contradicts the section's framing and is forbidden.

`Delta=ALIGNED` rows that are nonetheless noteworthy (e.g., a special-class item the auditor should glance at, a row carrying `Confidence: medium` that you want surfaced once) go into the optional `### Aligned but noteworthy` sub-section described below — never under "Divergent rows".

When the plan has ≥ 20 items OR ≥ 12 ALIGNED rows:

```markdown
## 2. Scope Delta Matrix

### Divergent rows (require human review)

| ID | Feature / Item | Source plan scope | TLDR mirrored scope | Triage classification | Delta | MVP set impact | Review action | Anchors |
|---|---|---|---|---|---|---|---|---|
[only non-ALIGNED rows]

### Aligned but noteworthy (optional)

| ID | Item | Why notable | Anchors |
|---|---|---|---|
[only ALIGNED rows worth surfacing once; omit this sub-heading entirely when no rows]

### Aligned summary

- `ALIGNED`: F02, F03, F06–F15 (12 items match the expected mapping per source plan declared scope)
```

For small plans (< 20 items), include all rows in the §2 visible table directly (still using the canonical 9-column format including `MVP set impact`).

If a full matrix is needed for any plan size, emit optional `Appendix H: Full Scope Delta Matrix` with all rows including `ALIGNED`.

## Forbidden behavior

`scope-triage` MUST NOT silently downgrade a plan-declared MVP item to `P3` / `NO-OVERENGINEERING` without surfacing the disagreement. Triage may DISAGREE with the plan, but it must NEVER SILENTLY OVERRIDE.

If the skill suspects a plan-declared MVP item is overengineering, the correct path is:

1. Classify the item as `NO-OVERENGINEERING` (or `P3`) with `Confidence: medium` (since plan disagrees).
2. Add a Scope Delta Matrix row with Delta=`PLAN_MORE_AGGRESSIVE`.
3. If the disagreement changes MVP membership, also add a §1 Blocking Question.
4. Let the human resolve in the source plan.

## Bind to AC Coverage Check (§4)

Each AC row in §4 AC Coverage Check surfaces any Delta warnings on items covering it (e.g., "AC13 covered by F01, F04 — F01 has Delta=`PLAN_MORE_AGGRESSIVE`, human review required").

## Bind to Post-Review Handoff Draft (§14)

The §14 draft template MUST include an explicit clause inheriting the source-plan-authoritative rule:

> Stop and ask if PLAN.md (source plan) and PLAN.scope.md (this scope file) disagree on any item's scope/category. Do NOT let PLAN.scope.md silently override PLAN.md — Scope Delta Matrix entries with non-`ALIGNED` deltas surface real plan disagreement that the human must resolve in PLAN.md (or explicitly accept).

This prevents downstream coding agents from treating the scope artifact as an override of the source plan when triage and plan disagree.
