---
name: code-review-plan
description: Creates a parallelizable code-review workplan from a source plan. Optional sibling artifacts (TLDR, scope, debug log) and code-diff hints sharpen the workplan but are not required. Use whenever a planned change has reached a state worth reviewing — pre- or post-smoke — to identify review shards, review angles, adversarial prompts, subagent assignments, and final aggregation requirements.
---

# Code Review Plan

> **Review-work planner. Generates a parallelizable code-review brief — bounded shards, controlled review angles, adversarial prompts, subagent assignments, fixed report contract, aggregation contract. Does NOT review code itself; the reviewer fleet (humans or AI subagents) does that, and a human aggregator (or future `review-report` skill) merges their findings.**

## What this is

`code-review-plan` is a review work *planner*, not a code reviewer. It generates bounded shards, controlled review angles, adversarial prompts, subagent instructions, and a final aggregation contract. Designed for parallel AI or human review.

**Required input**: `PLAN.md` only. Everything else — code diff / changed-file list, sibling `.tldr.md` / `.scope.md` / `.debug.md` artifacts, smoke-test evidence — is **optional**. When optional inputs are missing the skill records a Warning, sharpens what shards it can from `PLAN.md` content, and marks shards that needed the missing input with `Code areas: unknown` / `Bug history: not available`. The Review Dashboard reports `Review readiness:` (`READY` / `NEEDS_INPUT` / `BLOCKED`); the only hard `BLOCKED` cause is `PLAN.md` itself missing.

## What this is NOT

- **Not a code reviewer.** Does not actually review code, fix bugs, run tests, or approve implementation.
- **Not a workflow / orchestration engine.** Only 3 readiness values; specific concerns live in plain natural-language `Blocking issues:` / `Warnings:` lists, not in a sprawling state machine.
- **Not a CLI tool.** No `--force-review` flag; the user's free-text invocation note is the only override channel, and it lands as a recorded warning rather than a magic state transition.
- **Not a final review report generator.** v1 emits the aggregation contract only; the actual final report is a downstream artifact produced by a human or future `review-report` skill.

## Relationship to sibling skills

- `tldr-plan` — makes the source plan auditable (audit projection).
- `scope-triage` — makes the implementation boundary reviewable (boundary projection).
- `debug-log` — records execution-time bugs / fixes / verification (append-only).
- `code-review-plan` — consumes any combination of the artifacts above plus an optional code diff and produces a parallelizable review workplan.

Workflow position: after `PLAN.md` exists. The other artifacts are *recommended* (a workplan with TLDR + scope + debug + code diff is sharper than one drawn from `PLAN.md` alone), but **not required**. The source plan stays authoritative — `code-review-plan` reads the inputs but never edits any of them.

## When not to use

- `PLAN.md` does not yet exist (write the plan first).
- You only want to record one new bug (use `debug-log`).
- You want the actual review done (this skill *plans* the review; reviewers execute it).

## Phase position and preconditions

```text
PLAN.md                                ← only hard input
  ± tldr-plan / scope-triage           (pre-implementation, sharpens the workplan)
  ± implementation                      (sharpens shards via code diff)
  ± debug-log                           (debug phase, sharpens recurrence-risk shards)
  ± smoke / integration / E2E tests    (sharpens TEST_EVIDENCE_REVIEW shards)
  → code-review-plan                   (this skill — runs whenever a review brief is wanted)
  → parallel review fleet
  → review-report (future skill) or human aggregator
  → ship
```

`code-review-plan` assumes:

- **`PLAN.md` is resolvable.** Everything else is optional and recorded as Warning when absent.
- **The reviewer fleet will exercise judgment** about whether a given shard's evidence is strong enough to ship. Missing optional inputs reduce shard sharpness but do not prevent a workplan from being generated.

If `PLAN.md` is missing, the skill emits an empty scaffold with `Review readiness: BLOCKED` and `source plan missing` in `Blocking issues`. Any other absence is at most a `NEEDS_INPUT` (and usually just a `Warnings:` entry on a `READY` workplan).

## Source-of-truth rule

`PLAN.md` is authoritative. `.tldr.md` / `.scope.md` / `.debug.md` are derived sibling artifacts read as input. If they disagree with `PLAN.md`, record the inconsistency in §2 Review Input Index and turn it into a review target rather than silently rewriting any artifact.

## Invocation

Mirror sibling forms (no flags; the skill's only knob is the optional free-text note):

```text
/code-review-plan @PLAN.md
/code-review-plan @PLAN.md "<note: changed files, diff hint, CI summary, override rationale, etc.>"
/code-review-plan current plan
/code-review-plan
```

The free-text note is the single user-controlled input channel. Whatever the user wants the artifact to record — test evidence, override rationale, scope hint — goes in the note and the skill folds it into the dashboard / assumptions. This matches the sibling skills' invocation surface and keeps `code-review-plan` from drifting into CLI-tool territory.

### Refuse-list

If the user supplies a path that already ends in `.tldr.md`, `.scope.md`, `.debug.md`, or `.review.md`, refuse with a directive to rerun on the source plan instead.

## Output file

**Naming rule**: `<plan-dir>/<plan-stem>.review.md`

| Input plan | tldr-plan output | scope-triage output | debug-log output | code-review-plan output |
| --- | --- | --- | --- | --- |
| `plans/miles-port-unified-plan.md` | `.tldr.md` | `.scope.md` | `.debug.md` | `plans/miles-port-unified-plan.review.md` |
| `PLAN.md` | `PLAN.tldr.md` | `PLAN.scope.md` | `PLAN.debug.md` | `PLAN.review.md` |

If the input plan is read-only / outside the workspace, write to `./<plan-stem>.review.md` in CWD with a console note explaining the relocation. If no plan file is supplied, fall back to `./current-plan.review.md`.

### Overwrite-from-scratch rule

Matches `tldr-plan` / `scope-triage`, *inverts* `debug-log`. If the file exists, regenerate from scratch via Write. Do NOT read the prior `.review.md`. Iteration happens by re-running after `PLAN.md` / `.tldr.md` / `.scope.md` / `.debug.md` change — never by evolving the review file in place. A review plan is a snapshot of the inputs at a moment; the next round's snapshot is built from current inputs, not from the prior snapshot.

## Methodology

Encode four published code-review practices as structured artifact output (not narrative advice):

- **Small batches**: each shard ≤ ~200–400 LOC or ≤ ~60 min of review time (split otherwise). Source: SmartBear peer-review research.
- **Multi-dimensional review**: design / functionality / complexity / tests / naming / comments / style / consistency / documentation, not just "did it pass?". Source: Google eng-practices.
- **Adversarial invariant probing**: every high-risk shard generates concrete attack questions for ordering, locking, state transitions, resource lifecycle, idempotency, versioning, partial failure. Source: Microsoft SDL threat modeling, generalized to system invariants (not only web security).
- **Risk-based prioritization**: P0 → high-risk decisions → unresolved bugs → resolved bugs with recurrence risk → weak-evidence ACs → deferred-hardening leak → accidental overengineering → standalone regression-sensitive paths → observability/maintainability.

In the review phase you're **proactively probing invariants on working code** and assessing long-term code health — not chasing the next failing test.

## Review axes

11 controlled axis names (definitions, typical questions, and the high-risk-shard hard rule live in `references/review-axes.md` — read on demand):

`PLAN_ADHERENCE_REVIEW`, `CORRECTNESS_REVIEW`, `CONCURRENCY_RACE_REVIEW`, `RESOURCE_LIFECYCLE_REVIEW`, `ERROR_HANDLING_FAIL_FAST_REVIEW`, `ADVERSARIAL_INVARIANT_REVIEW`, `TEST_EVIDENCE_REVIEW`, `DEBUG_REGRESSION_REVIEW`, `OBSERVABILITY_REVIEW`, `PERFORMANCE_RESOURCE_REVIEW`, `MAINTAINABILITY_REVIEW`.

## Other controlled vocabularies

Deliberately compact — only one short readiness enum at the top level; everything else is plain natural-language list entries in the dashboard.

### Review readiness (3 values)

- `READY` — `PLAN.md` is resolvable and no `tier: blocking` author-clarification question is open; reviewer fleet may launch. **`READY` means launchable, not warning-free** — `Warnings:` may still contain advisory entries (missing optional artifacts, missing code diff, missing tests-passing evidence, mtime mismatches, recorded human override rationale). Warnings are advisory; they do not block launch.
- `NEEDS_INPUT` — workplan generated, but at least one `tier: blocking` author-clarification question is open. The workplan is complete enough to inspect, but the human should answer the question before launching the review fleet unless they explicitly accept the risk.
- `BLOCKED` — `PLAN.md` is missing or unreadable. **This is the only `BLOCKED` cause.** The workplan is still emitted as a scaffold (mostly empty) so the human can preview the planned shape and supply the missing source plan.

### Blocking issues / Warnings (free-text bulleted lists in §0, not enums)

These explain *why* readiness is `BLOCKED` or what advisory state the workplan is in. The only sample blocking-issue string is `source plan missing` (or `source plan unreadable: <reason>`). Sample warnings: `code diff / changed files not supplied — shards mark Code areas as unknown`, `tests-passing evidence missing — TEST_EVIDENCE_REVIEW shards depend on smoke evidence the reviewer must supply at exec time`, `.tldr.md mtime predates PLAN.md by 3 days; rerun tldr-plan if source plan changed semantically`, `.scope.md missing (optional but recommended)`, `.debug.md missing — recurrence-risk shards reconstruct bug history from git log`, `debug-log REV-002 PROPOSED but not yet applied to PLAN.md`, `human override rationale recorded: "external reviewer requested mid-debug look"`.

The skill records whatever rationale the human supplied verbatim — there is no fixed `force review:` prefix; that would amount to a hidden flag.

### Artifact freshness (4 values, used in §2 Review Input Index `Status` column)

`present-current`, `present-stale-suspected` (mtime mismatch — heuristic only, recorded as a Warning, never a Blocking issue), `missing`, `unknown`.

### Tests-passing evidence sources (optional)

If supplied, record which one was used in §0:

1. `<plan-stem>.debug.md` header `Current status: PASSING`.
2. User-supplied test output / CI summary in the invocation free-text note.
3. User assertion in the invocation note (e.g., `"tests passing as of abc123: pytest tests/router -q"`).

If none are present, record `tests-passing evidence missing` as a §0 `Warning` (NOT a Blocking issue). The workplan still ships at `READY`. `TEST_EVIDENCE_REVIEW`-axis shards add a note that the reviewer must supply or skip the evidence at execution time.

### Readiness decision table (single source of truth)

| Condition | Effect on readiness |
|---|---|
| `PLAN.md` missing or unreadable | `BLOCKED` (only `BLOCKED` cause) |
| At least one `tier: blocking` author-clarification question | `NEEDS_INPUT` (workplan still ships; human answers in chat or patches source artifacts and reruns) |
| Code diff / changed files not supplied | Warning in §0 (`Code areas: unknown` on affected shards); does NOT change readiness |
| No tests-passing evidence | Warning in §0; does NOT change readiness |
| `debug-log` has `PROPOSED` plan revision implicating `PLAN.md` | Warning in §0 + suggest the human resolve before launch; does NOT change readiness |
| Optional sibling artifact (`.tldr.md` / `.scope.md` / `.debug.md`) missing | Warning in §0; does NOT change readiness |
| mtime mismatch on a sibling artifact | Warning in §0 (heuristic only); does NOT change readiness |
| Free-text override rationale present in invocation note | Recorded as a §0 `Warnings:` entry; never demotes `BLOCKED` |
| Otherwise | `READY` |

`BLOCKED` dominates `NEEDS_INPUT` dominates `READY` when multiple conditions apply. The free-text override note is **audit signal only** — it never demotes a `BLOCKED` (i.e. it cannot manufacture a `PLAN.md`).

### Subagent report vocabularies

Verdict, severity, and finding-type values live in `references/output-layout.md` (which owns the §7 Subagent Report Template). Final-recommendation values live in `references/aggregation-contract.md` (which owns the computation rule). Read on demand.

## Author Clarification

The skill may ask the author targeted clarification questions during Step 3 of the workflow. Two tiers (`tier: blocking` lifts readiness to `NEEDS_INPUT`; `tier: non-blocking` is recorded as a §1.2 Review Assumption). Questions are option-shaped, ≤5 blocking per run, with `Default if unanswered`.

Full trigger taxonomy, tier rule, question shape, budget, durability rule (chat = single-run, source-artifact patch = durable), and worked example questions live in `references/clarification-protocol.md`. Read on demand.

## Workflow

6 steps — keep the workflow short so the artifact's bulk is in the review shards, not in pre-flight bookkeeping.

1. **Resolve inputs**. Read `PLAN.md` and look for sibling `.tldr.md` / `.scope.md` / `.debug.md`. Parse the invocation free-text note for tests-passing evidence, code-diff hints, and any override rationale.
2. **Draft readiness**. Apply the input-driven rows of the readiness decision table (everything *except* author clarification): source-plan / code-diff / tests-passing / `PROPOSED` plan-revision / mtime / optional-artifact / override-note checks. Hold the result as a candidate `Review readiness:`.
3. **Author clarification scan**. Walk the trigger taxonomy (`references/clarification-protocol.md`) against the resolved artifacts and invocation context. Generate ≤5 option-shaped questions with defaults. Populate §1.1 Author Clarification Questions and / or §1.2 Review Assumptions per the tier rule.
4. **Finalize readiness and build §0 Review Dashboard**. Combine the Step 2 candidate with Step 3's clarification result (a `tier: blocking` question lifts `READY` to `NEEDS_INPUT`; never lowers a `BLOCKED`). Write the final `Review readiness:` and the `Blocking issues:` / `Warnings:` / `Tests-passing evidence:` / `Code diff / changed files:` / `Author clarification:` lines into §0.
5. **Extract review targets, generate shards and adversarial prompts**. From each input artifact: P0 boundaries from `.scope.md`; high-risk decisions / assumptions / constraints from `.tldr.md`; active and resolved-with-recurrence-risk bugs from `.debug.md`; ACs and constraints from `PLAN.md`. Apply the priority order from Methodology. Cluster by subsystem / invariant / risk cluster — never by file. Assign 2–5 review angles per shard; enforce the high-risk-shard hard rule. Specialize adversarial prompts to the actual code area / invariant.
6. **Embed contracts and execution checklist**. Subagent assignments (§6, with `Status` reflecting §0 readiness), fixed subagent report template (§7, verbatim-copyable), aggregation contract (§8, verbatim-copyable), pre-flight execution checklist (§9, including "author-clarification answers folded in or applied to source artifacts").

The workflow does not have a separate "Step 0 precondition gate" — the gate logic is the readiness decision table, applied across Steps 2–4. The split between Step 2 (draft) and Step 4 (finalize) makes the dependency on Step 3 explicit so readiness never has to be revisited after §0 is written.

## Style rules

- Direct, technical language; tables for shard listings, axes, deliverables; bullets for per-shard fields.
- `unknown` / `(inferred)` markers; never invent code areas (use `unknown` and add an evidence-gap row instead).
- **Anchor canonicality**: canonical anchors are plan-level IDs only (`AC*` / `C*` / `D*` / `E*` / `M*` / `A*`). Scope item IDs (`F*`) MAY appear as **optional, non-canonical navigation references** to the scope artifact (in a shard's `Scope categories / scope notes` field), so a reviewer can jump back to the relevant `.scope.md` row — but `F*` MUST NOT replace plan anchors and MUST NOT appear in the shard's `Must-read anchors` field.
- Scope categories (`P0-FORBIDDEN`, `P3-DEFER-HARDENING`, etc.) are referenced as *labels* in shard-priority logic.
- **Dashboard short-rule**: if §0 + §1 readiness bookkeeping ever becomes longer than the §4 shard summary, compress the bookkeeping (consolidate Warnings, drop redundant phrasing) and preserve shard detail. Bookkeeping is overhead; shards are the product.

## Quality checklist

Before finalizing the artifact, verify:

- File path is `<plan-dir>/<plan-stem>.review.md` (or fallback per Output file rules).
- `Review readiness` is one of the 3 values (`READY` / `NEEDS_INPUT` / `BLOCKED`); appears in §0.
- §0 has populated `Blocking issues:` (or `none`) and `Warnings:` (or `none`) lists; both are plain natural-language bullets, not enums.
- If readiness is `BLOCKED`, every §6 Subagent Assignment Plan row carries `Status: BLOCKED — <one-line reason>`. If `BLOCKED` because of missing code diff, every shard's `Code areas to inspect` is `unknown — code diff not supplied`.
- If readiness is `READY`, no entries in §0 `Blocking issues`; `Warnings:` may still have entries.
- Every §1.1 Author Clarification Questions row is option-shaped, has a `Default if unanswered`, and cites concrete shard / angle / boundary impact in `Affects`.
- §1.1 row count ≤ 5 (or rows are grouped by boundary if logically > 5).
- If §1.1 has any blocking question, readiness is at least `NEEDS_INPUT` (cannot be `READY`).
- Tests-passing evidence source is recorded in §0 (`debug-log` / `invocation note` / `none`).
- Every shard has anchors + angles + adversarial questions (when high-risk) + output contract.
- No shard exceeds the 200–400 LOC / 60 min budget without being split.
- High-risk-shard hard rule satisfied (≥1 of `CORRECTNESS_REVIEW` / `CONCURRENCY_RACE_REVIEW` / `RESOURCE_LIFECYCLE_REVIEW` / `ADVERSARIAL_INVARIANT_REVIEW` / `ERROR_HANDLING_FAIL_FAST_REVIEW`).
- Subagent report template (§7) + aggregation contract (§8) both present and verbatim-copyable.
- No source-plan / TLDR / scope / debug edits.
- No actual code review prose in the artifact (the skill *plans* review, doesn't execute it).
- No `--force-review`-style flag mentions anywhere (removed in v1).

## What NOT to do

- Do not review code; do not run tests; do not fix bugs; do not approve implementation.
- Do not edit `PLAN.md` / sibling artifacts.
- Do not create scripts.
- Do not generate a final review report (that's a possible future `review-report` skill).
- Do not write file-by-file shards or unbounded "review everything" shards.
- Do not omit adversarial prompts on high-risk shards.
- Do not auto-trigger any reviewer fleet; the artifact is a brief, not an executor.
- Do not re-add per-cause review states (`BLOCKED_TESTS_NOT_PASSING` / `BLOCKED_STALE_REVIEW_INPUTS` / `BLOCKED_MISSING_CODE_DIFF` / `BLOCKED_PRECONDITION` / `BLOCKED_ON_AUTHOR_CLARIFICATION` / `READY_WITH_WARNINGS`) — those collapsed into `READY` / `NEEDS_INPUT` / `BLOCKED` plus dashboard `Blocking issues:` / `Warnings:` lists deliberately.
- Do not add an `--force-review` flag (or any other override flag). The user's free-text invocation note is the single override channel.
- Do not add a `Blocking reason:` enum field, an `Override reason:` field, or a `Soft warnings:` count to the dashboard. Plain natural-language `Blocking issues:` and `Warnings:` lists are the only place readiness reasons live.

## References

This skill is part of the shared plan-artifact pipeline. See `.claude/skills/README.md` for the overview of the sibling skills.

Read these only when needed (per progressive disclosure):

- `references/review-axes.md` — full 11-axis definitions + high-risk-shard rule
- `references/shard-template.md` — canonical shard template + sizing rule + anti-patterns
- `references/adversarial-prompts.md` — reusable prompt families grouped by target
- `references/clarification-protocol.md` — full question-trigger taxonomy + tier rule + worked examples
- `references/output-layout.md` — full §0–§9 template + per-section column specs
- `references/aggregation-contract.md` — deduplication rules, grouping rules, final-recommendation computation

Examples:

- `examples/input-artifact-index.md` — router zero-active suspend artifact index (continues the `debug-log` example)
- `examples/output-review-plan.md` — corresponding `<plan-stem>.review.md` artifact
