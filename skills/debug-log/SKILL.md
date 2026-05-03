---
name: debug-log
description: Records smoke-test and execution-time debugging findings as an append-only, plan-linked bug log. Use during implementation debugging to capture observed behavior, expected behavior, root cause, fix, verification evidence, regression coverage, and plan-revision implications.
---

# Debug Log

> **Append-only execution record. Primary readers: the implementer mid-debug and the postmortem reviewer afterward. The source plan stays authoritative — `debug-log` records execution reality and may suggest plan revisions, but never silently edits `PLAN.md`.**

## What this is

`debug-log` records what actually happened during implementation debugging — observed failures, hypotheses, attempted fixes, retests, regressions, and (when applicable) findings that prove the source plan was wrong or incomplete. Each event is captured as a structured entry in a single per-plan artifact: `<plan-stem>.debug.md`.

It is the **execution-record sibling** to `tldr-plan` (audit projection) and `scope-triage` (boundary review):

```text
tldr-plan     = makes the plan auditable by a human         (overwrite-from-scratch)
scope-triage  = makes the implementation boundary reviewable (overwrite-from-scratch)
debug-log     = records execution reality during debugging  (append-only)
```

The debug log is not a Jira tracker, not a plan, not a coding skill. It does not modify code, does not run tests, does not open issues, and does not modify the source plan, the TLDR artifact, or the scope artifact.

## What this is NOT

- **Not a coding skill.** Does not modify code, run tests, install dependencies, or shell out to runtime tools.
- **Not a plan or scope generator.** Does not classify items as MVP / forbidden / overengineering — that is `scope-triage`'s job. Does not generate D0–D6 decision traces — that is `tldr-plan`'s job.
- **Not an issue tracker.** No status workflows beyond the controlled status vocabulary; no assignees; no priorities beyond the bug-class taxonomy; no integration with external systems.
- **Not a changelog.** Vague entries like "fixed router bug" must be rejected; every entry separates symptom, root cause, fix, and verification.
- **Not an automatic plan-patcher.** When a bug reveals plan drift, the skill emits a `Plan Revision Suggestion`. It does not edit `PLAN.md`.

## Relationship to sibling skills

- `tldr-plan` makes the source plan auditable.
- `scope-triage` makes the implementation boundary reviewable.
- `debug-log` records execution reality during implementation and smoke-test debugging.

The source plan is authoritative. The debug log is a derived execution record.

If a bug reveals plan drift:

- patch `PLAN.md` only when the user explicitly asks
- otherwise emit a `Plan Revision Suggestion` (§5 of the artifact)
- rerun `tldr-plan` if assumptions / constraints / AC / evidence changed
- rerun `scope-triage` if MVP / defer / forbidden / overengineering boundaries changed

`debug-log` answers two questions:

- *Does this bug require patching `PLAN.md`?*
- *After patching, do `tldr-plan` / `scope-triage` need to rerun?*

It does not maintain traceability to derived scope IDs — every long-lived fact should trace back to the source plan.

## When not to use

- Pre-implementation work (planning, brainstorming, architecture exploration). Use `tldr-plan` / `scope-triage` instead.
- A general activity log or changelog of code changes. Use `git log` + commit messages.
- A one-off fix the user does not care to record. Append-only logs work best when the team will read them later.
- Recording user feedback / feature requests / non-bug observations. Use the appropriate planning surface.

## Source-of-truth rule

**Primary input** (authoritative):

```text
<plan-dir>/<plan-stem>.md
```

**Optional context** (anchor navigation only):

```text
<plan-dir>/<plan-stem>.tldr.md
```

**Optional context** (presence noted, but never an anchor source):

```text
<plan-dir>/<plan-stem>.scope.md
```

Rules:

- The source plan is authoritative. The TLDR artifact may be read to recover plan anchors (`AC*` / `C*` / `D*` / `E*` / `M*` / `A*`) when the source plan is large.
- The scope artifact is **optional context only**. Its path is recorded in the header (`Scope context: <path | missing, optional>`) and may be acknowledged in a per-bug `Related artifacts:` line, but `debug-log` never anchors bugs to `F*` scope IDs.
- Every long-lived fact should trace back to `PLAN.md` (or its TLDR projection). This keeps the three sibling skills cleanly layered: `tldr-plan` projects, `scope-triage` classifies, `debug-log` records — and only the source plan is shared ground.
- The debug log records execution observations and may suggest plan revisions but **never silently edits the source plan**.

## Invocation

The user invokes the skill with one of:

```text
/debug-log @PLAN.md "<short note about the event>"
/debug-log @PLAN.md
/debug-log current plan "<short note>"
/debug-log
```

Behavior:

- If `<short note>` is omitted, prompt the user in chat for the note before writing anything.
- If no plan path is supplied, fall back to current plan inference (most recent `plans/*.md` referenced in the conversation, or `./PLAN.md` in CWD).
- The note is the user's framing of the event (new failure / suspected root cause / fix applied / retest passed / etc.). The skill classifies the event type from this note + any logs the user pasted.

### Refuse-list

If the user supplies a path that already ends in `.tldr.md`, `.scope.md`, or `.debug.md`, refuse with one of:

> Input appears to be a TLDR artifact. Run debug-log on the source plan instead.
> Input appears to be a scope-triage artifact. Run debug-log on the source plan instead.
> Input appears to be an existing debug log. Run debug-log on the source plan instead — debug-log will read the existing `.debug.md` automatically and append/update entries by stable ID.

## Output file

**Naming rule**: `<plan-dir>/<plan-stem>.debug.md`

| Input plan | tldr-plan output | scope-triage output | debug-log output |
| --- | --- | --- | --- |
| `plans/miles-port-unified-plan.md` | `plans/miles-port-unified-plan.tldr.md` | `plans/miles-port-unified-plan.scope.md` | `plans/miles-port-unified-plan.debug.md` |
| `docs/proposal.md` | `docs/proposal.tldr.md` | `docs/proposal.scope.md` | `docs/proposal.debug.md` |
| `PLAN.md` | `PLAN.tldr.md` | `PLAN.scope.md` | `PLAN.debug.md` |

If the input plan path is read-only / outside the workspace, write to `./<plan-stem>.debug.md` in CWD with a console note explaining the relocation.

If no plan file is supplied, fall back to `./current-plan.debug.md`.

### Append-only rule (load-bearing — inverts the sibling pattern)

`tldr-plan` and `scope-triage` regenerate their artifacts from scratch on every run. **`debug-log` does not.**

- If the file exists, **read it** to recover existing `BUG-*` / `SESSION-*` / `REV-*` / `RUN-*` IDs.
- Update existing debug logs by **targeted patch/edit, not full-file regeneration**. In Claude Code, use Edit rather than Write when `<plan-stem>.debug.md` already exists. (Phrasing is tool-agnostic so the rule survives if the skill is reused under a different runtime; the Claude Code mapping is given as a concrete instance.)
- Resolved entries stay in §3 Bug Entries — never delete them, never renumber `BUG-*` IDs.
- Do not rewrite history unless the user explicitly asks. The whole point of an append-only log is to preserve the trail of failed hypotheses and partial fixes that led to the eventual root cause.

### Merge discipline

Use the canonical Conservative merge rule in `references/classification-rules.md`: merge a new note into an existing bug only when at least two match signals line up. If unsure, create a new `BUG-*` and cross-link with `Related bugs:`.

## Core model

Every bug entry must separate four orthogonal layers:

1. **Symptom** (what failed) — Observed behavior + Failure excerpt.
2. **Root cause** (why) — confidence-tagged.
3. **Fix** (what changed) — Files changed + Verification command + Regression coverage.
4. **Plan impact** (does this require revising `PLAN.md`?) — orthogonal to the first three.

A reader scanning the log should be able to extract any of the four layers without reading the others.

Bad entry:

```text
Fixed router bug.
```

Good entry:

```text
Symptom: router request hangs forever after all workers disabled.
Root cause: enable_worker updated enabled_workers but did not notify _workers_changed.
Fix: added notify_all() after state mutation in enable_worker.
Verification: TEST_PASS — pytest tests/router/test_zero_active_suspend.py -q passed.
```

The skill must reject vague entries unless the user has truly exhausted available evidence — in which case the missing fields are explicitly marked `unknown` and surfaced in §6 Remaining Risks.

## Taxonomies

Use the canonical vocabularies and decision rules in `references/classification-rules.md`:

- bug class
- bug status and resolution rule
- root-cause confidence
- verification evidence type and `Verification:` field format
- plan impact and sibling-rerun recommendation
- revision suggestion status
- Conservative merge rule

Keep `SKILL.md` free of duplicate taxonomy definitions; when a rule is needed during execution, read the reference file.

## Workflow

### Step 1 — Resolve artifacts

Given the input plan path, locate sibling artifacts:

```text
<plan-stem>.tldr.md     (optional — read for plan-anchor navigation)
<plan-stem>.scope.md    (optional — presence noted, never anchored)
<plan-stem>.debug.md    (existing debug log — read in full if present)
```

Record paths in the artifact header. Mark missing siblings as `missing`. Mark `Scope context` as `<path | missing, optional>`.

### Step 2 — Determine event type

Classify the user's note as one of:

- new bug observed
- root cause suspected
- root cause confirmed
- fix applied
- retest passed
- retest failed
- bug reopened
- session summary
- final smoke-test pass
- plan revision suggestion

### Step 3 — Match to existing bug or create new

Apply the Conservative merge rule from `references/classification-rules.md`. Otherwise create a new `BUG-*` and add `Related bugs:`.

### Step 4 — Extract evidence

Capture: test command, observed behavior, expected behavior, failure excerpt (short — summarize long logs), environment, root cause, files changed, verification, regression coverage. Do not invent logs, commands, files, or fixes — use `unknown` and surface in §6 Remaining Risks.

### Step 5 — Link anchors

**Required when available**: source-plan / TLDR anchors `AC*` / `C*` / `D*` / `E*` / `M*` / `A*`. Use `unknown` when no plan anchor exists.

The skill **does not require or maintain `F*` scope anchors** — every long-lived fact should trace back to `PLAN.md`. Cross-references inside the debug log itself (`BUG-*` / `REV-*` / `RUN-*`) are tracked normally.

### Step 6 — Decide plan impact

Classify against the 6-value Plan impact taxonomy. If not `NO_PLAN_CHANGE`, add a row to §5 Plan Revision Suggestions with `Status: PROPOSED` and the appropriate `Rerun needed` value (`tldr-plan` / `scope-triage` / `both` / `none`).

Do not directly edit `PLAN.md`.

### Step 7 — Update the debug log

Update `<plan-stem>.debug.md` via targeted patch/edit (Edit, not Write, when the file already exists). If creating the file for the first time, use Write.

### Step 8 — Update status tables

After appending or updating a bug entry, follow the status-table update protocol in `references/output-layout.md`. Do not remove resolved entries from §3 Bug Entries — they stay forever.

## Output layout

The artifact has a fixed structure (§0–§6). Full template skeleton + per-section column specs in `references/output-layout.md`.

```text
Header → §0 Session Summary → §1 Active Bugs → §2 Resolved Bugs
       → §3 Bug Entries → §4 Retest Timeline → §5 Plan Revision Suggestions
       → §6 Remaining Risks
```

§4 Retest Timeline precedes §5 Plan Revision Suggestions intentionally: during debugging the chronological evidence usually matters more than plan patches.

## Style rules

- Direct, technical language.
- Tables for status / timeline / revisions; bullets for per-bug entries.
- Never accept "fixed bug" or similar vague entries.
- Mandatory separation of symptom / root cause / fix / verification.
- Short log excerpts only — summarize long logs and reference the full log path if needed.
- Use `unknown` when information is unavailable; `pending verification` when a fix is applied but not retested.
- Stable IDs (`BUG-001`, `SESSION-001`, `REV-001`, `RUN-001`) — never renumber across edits.

## Quality checklist

Before finalizing the artifact, verify:

- File path is `<plan-dir>/<plan-stem>.debug.md` (or fallback per the Output file rules).
- Header lists Source plan, TLDR context, Scope context (optional), Current smoke target, Current status.
- No bug is `RESOLVED` without an evidence-typed `Verification:` line.
- Every bug entry separates Symptom / Root cause / Fix / Verification.
- Every `Plan impact` value other than `NO_PLAN_CHANGE` has a corresponding §5 row with `Status: PROPOSED` (or later) and a `Rerun needed` value.
- Append-only preserved: existing `BUG-*` / `REV-*` / `RUN-*` IDs are not renumbered; resolved entries are still present.
- No fabricated logs, commands, files, or fixes — `unknown` is used wherever evidence is absent.
- Source plan, TLDR, and scope artifacts have NOT been modified.
- `Plan anchors:` populated when available; no `F*` scope anchors anywhere.

## What NOT to do

- Do not edit `PLAN.md`, `<plan-stem>.tldr.md`, or `<plan-stem>.scope.md`.
- Do not regenerate `<plan-stem>.debug.md` from scratch when it already exists. Read it; update by stable ID.
- Do not classify implementation scope (MVP / defer / forbidden / overengineering) — that is `scope-triage`'s job.
- Do not generate a D0–D6 decision trace — that is `tldr-plan`'s job.
- Do not maintain `F*` scope anchors. Bugs link to source plan / TLDR only.
- Do not paste long logs verbatim into the artifact. Summarize and reference.
- Do not mark a bug `RESOLVED` without an evidence-typed verification line.
- Do not delete or renumber resolved bug entries, retest timeline rows, or plan revision suggestions. Transition status; never remove rows.
- Do not silently merge two distinct bugs (Conservative merge rule).
- Do not auto-trigger `tldr-plan` or `scope-triage` reruns. The artifact only **recommends** reruns via the `Rerun needed` column.

## References

This skill is part of the shared plan-artifact pipeline. See `.claude/skills/README.md` for the overview.

Read these only when needed (per progressive disclosure):

- `references/output-layout.md` — full §0–§6 template + per-section column specs + status-table update protocol
- `references/bug-entry-template.md` — canonical bug entry field list + per-field rules + Verification format
- `references/classification-rules.md` — full taxonomies (bug class, plan impact, verification evidence type, revision status) + resolution rule + conservative merge rule + plan revision rule

Examples:

- `examples/input-session-notes.md` — a router zero-active-suspend smoke-debug session
- `examples/output-debug-log.md` — the corresponding `.debug.md` artifact
