---
name: review-report
description: Spawns parallel reviewer subagents from a code-review brief, collects their structured shard reports, and aggregates them into a findings-first review report. Use after code-review-plan to actually execute the parallel review and produce a decision-ready report.
---

# Review Report

> **Single-pass: invoke once, get either a findings-first review report or a single error. No retry, no interactive clarification, no manual fanout fallback, no override flags. The user reads `<plan-stem>.review-report.md` and decides ship / no-ship / iterate.**

## What this is

`review-report` is a review **execution + aggregation** orchestrator. It reads `<plan-stem>.review.md` (produced by `code-review-plan`), spawns ≤8 read-only reviewer subagents in parallel (batching in waves if there are more shards), collects each subagent's strict shard report into `<plan-stem>.review-report/<R*>.md`, then aggregates findings into a findings-first `<plan-stem>.review-report.md`.

Lightweight orchestration; complexity lives in subagent instructions + result schema, not in workflow state machines.

## What this is NOT

- **Not a code reviewer itself.** Subagents review code; the main agent only spawns them and aggregates their structured returns.
- **Not an editor.** Does NOT edit code, source plan, TLDR, scope, debug log, or review plan.
- **Not a test runner.** Subagents do NOT run tests unless a shard explicitly grants that capability.
- **Not auto-handoff.** Does NOT auto-create `BUG-*` IDs (suggests them); does NOT auto-rerun siblings (recommends them); does NOT auto-ship.
- **Not a workflow engine.** No retry loop, no interactive clarification mid-run, no manual fallback, no override flags. Single-pass.

## Relationship to sibling skills

`code-review-plan` produces the brief; `review-report` executes against it. Routing back to `debug-log` (new bugs found), `PLAN.md` (drift surfaced), or `tldr-plan` / `scope-triage` (rerun needed) is recommendation-only — the human acts on the routing fields, the skill never auto-triggers.

## When not to use

- `<plan-stem>.review.md` doesn't exist — run `code-review-plan` first.
- `<plan-stem>.review.md` has `Review readiness` other than `READY` — resolve the listed issues and rerun `code-review-plan` first.
- You only want to brief the fleet without running the review — use `code-review-plan` alone.
- You want a human reviewer fleet — this skill spawns AI subagents only.

## Source-of-truth rule

`PLAN.md` is authoritative. `<plan-stem>.review.md` is the brief that defines shard scope and the report contract. `<plan-stem>.debug.md` provides recurrence-risk context. Subagents must use evidence from these artifacts plus the code; fabrication is forbidden (use evidence-gap rows instead).

## Invocation

- `/review-report @PLAN.md`
- `/review-report @PLAN.md "<note: run context, audit comment, etc.>"` — optional free-text note. **Recorded in §0 as run context only**; it does NOT change shard selection, parallelism, or any other behavior. v1 always runs all shards listed in `<plan-stem>.review.md` §6 — no subset-execution, no shard skipping. (To narrow scope, rerun `code-review-plan` with a smaller scope first.)
- `/review-report current plan`
- `/review-report` (uses current plan)

**Refuse-list**: paths ending in `.tldr.md`, `.scope.md`, `.debug.md`, `.review.md`, `.review-report.md`, or under `.review-report/` are rejected with a directive to rerun on the source plan.

**No flags**: no `--force`, no `--parallelism`. The free-text note is recorded as run context only — it does NOT override readiness, shard selection, batching, or tool policy.

## Output files

Two outputs:

- **Sidecar dir**: `<plan-dir>/<plan-stem>.review-report/<R*>.md` — one file per shard subagent report (e.g., `<plan-stem>.review-report/R01.md`). Created by the skill; subagents return content, the main agent writes the file.
- **Final report**: `<plan-dir>/<plan-stem>.review-report.md` — aggregated findings-first report.

If the input plan is read-only / outside the workspace, write to `./` in CWD with a console note. If no plan supplied, fall back to `./current-plan.review-report.md` + `./current-plan.review-report/`.

### Overwrite rules

- Final `<plan-stem>.review-report.md`: overwrite-from-scratch on every run.
- Per-shard sidecar files: overwrite per-shard on rerun (each shard re-reviewed independently).
- Iteration happens by re-running `code-review-plan` (which may reshape shards) and then re-running `review-report`. Never evolve the report files in place.

## Subagent fan-out rule (single-pass, fail-fast, deterministic batching)

- **Run 5 reviewer subagents per batch by default. If the total shard count is ≤8, the skill may run all shards in one batch. Never exceed 8 parallel subagents.** No flag to override.
- **Take shard rows from `<plan-stem>.review.md` §6 in order.** No priority-sort logic, no reordering.
- The default of 5 is conservative: AI review is context-hungry, and a smaller batch produces more focused reviewers.
- All batches complete before final aggregation.
- **Fail-fast if subagent spawning is unavailable.** The skill assumes the runtime supports direct subagent spawning (e.g., Claude Code's `Agent` tool). If spawning is unavailable, **stop before writing any output** with a clear single-line reason. Do NOT emit prompt files for the user to run by hand. Do NOT degrade to a manual workflow.
- No `--parallelism` flag, no manual override, no fallback mode. The skill is single-pass.

## Subagent rules

Full template + tool allowlist in `references/subagent-instructions.md`. Summary:

- Each subagent receives a **bounded shard-specific prompt** — only the data needed for that shard. Context isolation is the whole point of using subagents.
- Subagents are **read-only by default**. Tool allowlist: `Read`, `Grep`, `Glob`, read-only `Bash` subset (`git diff`, `git log`, `git show`, `find`, `grep`, `wc`, `head`, `tail`, `cat`). Forbidden by default: `Edit`, `Write`, `NotebookEdit`, write-mode `Bash`, test runners. Per-shard escalation requires explicit annotation in the shard's `Required tests / evidence` field.
- Subagents must return **exactly the strict shard report schema** (see `references/shard-report-schema.md`). Malformed output is **marked** by the schema check (Workflow Step 3); the main agent still writes the sidecar with `Status: MALFORMED`, surfaces it as an evidence gap, and continues aggregation.
- Subagents must NOT review outside their assigned shard, NOT edit files, NOT fix bugs, NOT auto-trigger anything.

## Workflow

4 steps, single-pass; no retry, no interactive clarification, no manual handoff in the middle.

1. **Read review brief.** Resolve `PLAN.md` and `<plan-stem>.review.md`. Stop if `<plan-stem>.review.md` is missing or its `Review readiness` is not `READY`. (`NEEDS_INPUT` / `BLOCKED` → tell the human to rerun `code-review-plan` after resolving the listed issues; do NOT introduce an override flag.)
2. **Run shard reviewers.** For each review shard in `<plan-stem>.review.md` §6, spawn one read-only reviewer subagent. **Run 5 reviewer subagents per batch by default. If the total shard count is ≤8, the skill may run all shards in one batch. Never exceed 8 parallel subagents.** Take shard rows in §6 order (no priority-sort). All batches complete before final aggregation. Each subagent receives only its shard-specific inputs (per `references/subagent-instructions.md`) and must return the strict shard report schema (per `references/shard-report-schema.md`). If the runtime cannot spawn subagents, fail fast with one clear reason — do NOT degrade to a manual workflow.
3. **Persist shard reports.** Two failure modes, recorded distinctly:
   - **MALFORMED** (subagent returned but schema check failed): write `<plan-stem>.review-report/<R*>.md` with `Status: MALFORMED` + a one-line reason prepended; surface the shard as an evidence gap in §3 of the final report and route it to `BLOCKED_BY_MISSING_EVIDENCE` in aggregation.
   - **MISSING** (subagent never returned — timed out, refused, runtime error mid-spawn): do NOT create a sidecar file at all; record the shard as MISSING in §0 / §3 / §10 of the final report and route it to `BLOCKED_BY_MISSING_EVIDENCE` in aggregation.

   Schema check is behavioral, not a parser script. Do not retry. Do not spawn a fix-up subagent.
4. **Aggregate findings.** Apply the rules in `references/aggregation-rules.md`: deduplicate conservatively (≥2-signal rule), preserve evidence verbatim, group by severity then finding type, extract debug-log updates and PLAN revision suggestions as recommendation lists (no auto-actions), compute final recommendation per the severity-tally rule. Write `<plan-stem>.review-report.md` per `references/output-layout.md` — **findings-first**, with `Review Coverage` near the bottom.

## Style rules

- Final report is **findings-first**. §0 Decision Summary, §1 Blocking Findings, §2 High Findings come BEFORE §8 Review Coverage.
- **Background-rich findings**: every BLOCKER and HIGH finding MUST include background (why the invariant matters), expected behavior, the finding itself, evidence, impact, recommended action, and routing. A finding that only says "X is broken" is invalid. Full rules in `references/finding-rules.md`.
- **Anchor canonicality**: same as `code-review-plan` — canonical anchors are plan-level (`AC*` / `C*` / `D*` / `E*` / `M*` / `A*`); `F*` may appear as optional navigation refs only, never in `Plan anchors:` fields.
- Tables for findings index, evidence gaps, debug-log updates, PLAN revisions.
- `unknown` markers when a subagent reported missing evidence; never invent.
- Dashboard short-rule: if §0 + §8 bookkeeping outweighs §1–§3 findings, compress bookkeeping.

## Quality checklist

Before finalizing the artifact, verify:

- File path is `<plan-dir>/<plan-stem>.review-report.md` + sidecar dir `<plan-stem>.review-report/`.
- Final report has `Report readiness:` ∈ {`COMPLETE`, `INCOMPLETE` (some shards malformed/missing)}. Input-blocked cases (review-plan missing or `Review readiness != READY`, runtime can't spawn subagents) fail before writing the report — they do NOT produce a `BLOCKED_AT_INPUT` artifact; the user gets a single chat error reason instead.
- Subagent count ≤8 per batch.
- Every shard in `<plan-stem>.review.md` §6 has a corresponding sidecar file (or is explicitly recorded as MISSING in §0 / §10).
- Every BLOCKER and HIGH finding in §1 / §2 has all 7 required fields (Background, Expected behavior / invariant, Finding, Evidence, Impact, Recommended action, Routing).
- Findings-first order: §0 / §1 / §2 / §3 BEFORE §8.
- Final recommendation ∈ {`APPROVE`, `APPROVE_WITH_FOLLOWUPS`, `NEEDS_FIX`, `BLOCKED`} (matches `code-review-plan`'s aggregation contract).
- Missing or malformed required shard → `Final recommendation: BLOCKED` (per `references/aggregation-rules.md`).
- No source-plan / TLDR / scope / debug / review-plan edits.
- No auto-creation of `BUG-*` IDs (only suggestions in §4 Debug-log Updates Required).
- No auto-rerun of any sibling skill (only recommendations).

## What NOT to do

- Don't spawn >8 parallel subagents.
- Don't grant subagents write tools.
- Don't aggregate without the schema check.
- Don't edit any source artifact.
- Don't auto-fix bugs.
- Don't auto-create `BUG-*` IDs in `debug-log`.
- Don't auto-rerun `tldr-plan` / `scope-triage`.
- Don't write a coverage-first report (findings-first is mandatory).
- Don't accept findings that lack background (invalid per `finding-rules.md`).
- Don't add per-cause `Review readiness:` enums (use the 2-value `Report readiness:` plus dashboard bullets).
- Don't introduce a manual-fanout fallback, a prompt-export mode, or any sidecar subdirectories (`prompts/`, `pending/`, `manual/`, `raw/`). Sidecar dir contains exactly `<R*>.md` files — nothing else.
- Don't retry a malformed subagent. Don't spawn a fix-up agent. The malformed sidecar + §3 Evidence Gap row is the entire failure path.
- Don't add `--force`, `--parallelism`, or any other flag. The free-text invocation note is the only override channel (and it's audit-only — does not change behavior).
- Don't ask the user mid-run. Single-pass means: invoke once, get a result.

## References

This skill is part of the shared plan-artifact pipeline. See `.claude/skills/README.md` (or `claude-skills/skills/README.md`) for the overview.

Read these only when needed (per progressive disclosure):

- `references/subagent-instructions.md` — bounded reviewer-subagent prompt template + tool allowlist + spawn rules + failure handling
- `references/shard-report-schema.md` — strict per-shard report schema + behavioral schema-check rules
- `references/finding-rules.md` — what makes a finding valid (background rule), severity rules, finding-type guidance, routing rules, evidence-gap rules
- `references/aggregation-rules.md` — collection, dedup, grouping, extraction, final-recommendation tally
- `references/output-layout.md` — final report layout (findings-first §0–§10) + per-section field specs

Examples:

- `examples/input-review-plan.md` — minimal `<plan-stem>.review.md` with 3 shards (router zero-active suspend example chain)
- `examples/input-shard-report-r01.md` — R01 reviewer return: `NEEDS_FIX` with one HIGH `remove_worker` recurrence finding
- `examples/input-shard-report-r02.md` — R02 reviewer return: `PASS_WITH_NOTES` with one MEDIUM finding
- `examples/output-review-report.md` — aggregated `<plan-stem>.review-report.md` showing R01 + R02 + R03-MISSING (BLOCKED final recommendation)
