# Subagent Instructions

The canonical reviewer-subagent prompt template + spawn rules + tool allowlist + failure handling.

## Spawn rules

- **Run 5 reviewer subagents per batch by default. If the total shard count is ≤8, the skill may run all shards in one batch. Never exceed 8 parallel subagents.** No flag to override.
- One subagent per shard ID — never share a shard across subagents.
- Take shard rows from `<plan-stem>.review.md` §6 in order; no priority-sort, no reordering.
- All subagents in a batch run in parallel. Wait for all to return (or time out) before starting the next batch.
- All batches complete before final aggregation begins.
- **Fail-fast if subagent spawning is unavailable.** Do NOT degrade to a manual workflow, do NOT emit prompt files for the user to run by hand. Stop with a single clear chat error.

## Tool allowlist (default — read-only)

Subagents are read-only by default:

**Allowed**:
- `Read` (file reads)
- `Grep` (code search)
- `Glob` (file pattern matching)
- `Bash` — read-only subset only: `git diff`, `git log`, `git show`, `git blame`, `find`, `grep`, `wc`, `head`, `tail`, `cat`, `ls`

**Forbidden** (default):
- `Edit`
- `Write`
- `NotebookEdit`
- `Bash` (write-mode: anything that mutates files, processes, or external systems)
- Test runners (`pytest`, `cargo test`, `npm test`, etc.)
- Network-mutating tools

**Per-shard escalation**: a shard MAY explicitly request additional tools by listing them in its `Required tests / evidence` field in `<plan-stem>.review.md` §4. Example: a `TEST_EVIDENCE_REVIEW` shard might request `Bash: pytest --collect-only` (read-only test discovery) but should never request full test execution from inside the subagent. The skill grants escalations only when the shard explicitly names them; never broaden the allowlist by inference.

## Bounded prompt template

Each subagent receives a prompt populated from the corresponding shard in `<plan-stem>.review.md`. **Only the data needed for that shard** — no "here's the entire repo." Context isolation is the whole point of using subagents.

```text
You are a read-only code-review subagent.

Review only the assigned shard. Do not edit files, do not fix bugs, do not run tests unless explicitly allowed by this prompt.

Shard ID: <R*>
Shard title: <title>
Goal: <goal>

Inputs:
- Source plan: <PLAN.md path>
- Review plan: <PLAN.review.md path>
- Debug log: <PLAN.debug.md path or "n/a">

Code areas:
- <list of files / directories>

Must-read anchors: <AC* / C* / D* / E* / M* / A*>
Scope categories / scope notes: <P0-* labels + optional F* refs>
Review angles: <2–5 axes from the controlled list>

Adversarial prompts:
- <3–8 specialized prompts from <PLAN.review.md> §5>

Known bugs from debug-log:
- <BUG-* IDs and one-line summaries, if any>

Required tests / evidence:
- <list from shard, including any per-shard tool escalation>

Stop conditions:
- <list from shard>

Rules:
- Use evidence from the code, the listed tests, plan anchors, and debug-log.
- If evidence is missing for a question you'd otherwise answer, record an Evidence Gap row instead of guessing.
- Every BLOCKER and HIGH finding MUST include background (why the invariant matters), expected behavior, the finding, evidence, impact, recommended action, and routing.
- Output exactly the schema in `references/shard-report-schema.md`. Do not add or remove sections.
- Do not review outside this shard. Do not edit files. Do not fix bugs.

Return your shard report in the strict schema format. Do not include explanations outside the schema.
```

## Failure handling

Two distinct failure modes — record them differently:

| Failure mode | Trigger | Handling |
|---|---|---|
| **MALFORMED** | Subagent returned, but schema check failed (missing required section, invalid `Verdict`, BLOCKER/HIGH lacks `Detailed Findings`, etc.) | Write `<plan-stem>.review-report/<R*>.md` with `Status: MALFORMED` + one-line reason prepended. Surface in §3 Evidence Gaps. Route shard to `BLOCKED_BY_MISSING_EVIDENCE` in aggregation. |
| **MISSING** | Subagent never returned (timed out, refused, runtime error mid-spawn) | Do NOT create a sidecar file. Record shard as `MISSING` in §0 / §3 / §10 of the final report. Route shard to `BLOCKED_BY_MISSING_EVIDENCE` in aggregation. |

In both cases:

- Do NOT retry the subagent.
- Do NOT spawn a fix-up subagent.
- Do NOT ask the user mid-run.
- The malformed sidecar (or absence-recorded MISSING entry) + the §3 Evidence Gap row IS the entire failure path.

If the runtime cannot spawn subagents at all (not just one shard failing — the whole spawn mechanism unavailable), fail fast before writing any output. The user sees a single chat error reason; no review report is produced.
