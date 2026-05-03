# Author Clarification Protocol

Full spec for `code-review-plan`'s author clarification mechanism. Parallel to `scope-triage`'s `clarification-protocol.md`, but lighter — clarifications do NOT get their own state; they affect the 3-value `Review readiness:` enum.

## Core rule

**Only ask if the answer changes the review workplan.** Otherwise record the working assumption in §1.2 Review Assumptions and proceed.

## When to ask (trigger taxonomy)

The skill scans for these conditions during Step 3 of the workflow:

| Trigger | Tier | Why it matters |
|---|---|---|
| Code diff / changed files missing or ambiguous | blocking | Can't draft shards without knowing the implementation surface |
| Unresolved / reopened bug in `<plan-stem>.debug.md` | blocking (usually) | Affects whether parallel review proceeds or blocks on the bug |
| `PROPOSED` Plan Revision Suggestions in `debug-log` §5 | blocking | Source plan may be stale; review would be against wrong target |
| Unresolved Scope Delta rows / low-confidence defaults in `.scope.md` | blocking | Boundary is unstable; shards would be classified wrong |
| `PLAN.md` ↔ derived artifact conflict | blocking | Don't know which intent to review against |
| User asks to "review all code" but diff is large | blocking | Need to scope or shard it intentionally |
| Deferred-hardening boundary unclear for this round | blocking | Avoid reviewing items the team chose to defer |
| Possibly-implemented `NO-OVERENGINEERING` items | non-blocking → blocking if confirmed | Need to know if this is a bug or an intentional change |
| Reviewer-fleet budget / depth unclear | non-blocking | Affects shard count and adversarial-prompt density |
| Adversarial-review aggressiveness unclear | non-blocking | Affects §5 prompt count per shard |

## When NOT to ask

- The answer would only refine wording, not shard boundaries.
- The default is conservative and clearly correct (e.g., "if unclear whether a `P3-DEFER-HARDENING` item is in scope this round, default to `excluded` per scope-triage classification").
- The information is mechanically recoverable from the artifacts (don't ask the user to look up something the skill can read itself).

For these, record the working assumption in §1.2 Review Assumptions:

```markdown
| Assumption ID | Assumption | Used for | Risk if wrong |
|---|---|---|---|
| RA-01 | Reviewer fleet optimizes for correctness + recurrence (per debug-log BUG-001 history); not release-readiness depth. | Shard angle selection | Under-emphasis of release-blocker concerns |
```

## Question shape

Every §1.1 row MUST be option-shaped:

```markdown
| QID | Question | Options | Affects | Default if unanswered | Why it matters |
|---|---|---|---|---|---|
| Q1 | Should deferred M11.5 bounded-timeout behavior be included in this review round? | A. Exclude; only review M11.1/M11.2 MVP. B. Include only as accidental-scope-creep check. C. Include as full correctness review. D. Block review until PLAN.md/scope-triage updated. | R02, R05 (changes shard count and angles); tier: blocking | B (scope-triage classifies M11.5 as deferred hardening) | Determines whether the review fleet spends effort on deferred work |
```

Hard rules:

- A / B / C / D options (or A / B if binary). No open-ended questions.
- `Default if unanswered` is mandatory.
- `Affects` cites concrete shard ID(s), shard angle, or scope boundary, AND includes `tier: blocking` or `tier: non-blocking`.
- `Why it matters` is one short line — what changes if the answer is wrong.

## Question budget

- At most **5 blocking questions per run**.
- If more would be needed, group by boundary (scope / depth / unresolved-bug / drift) and consolidate into combined questions with multi-axis options.
- Non-blocking questions don't count against the budget but should still be ≤10 to avoid noise.

## Two-tier model

- `tier: blocking` → pushes `Review readiness: NEEDS_INPUT`. §6 Subagent Assignment Plan rows carry `Status: NEEDS_INPUT — author clarification pending`. Workplan still ships so the human can read what the questions affect.
- `tier: non-blocking` → recorded as a §1.2 Review Assumption with the skill's working assumption; no readiness change.

## Answer routing rule

Author answers patch the **review plan**, not the source plan.

- When the author answers in chat (and chooses not to patch source artifacts), the skill writes the answers into §1.2 Review Assumptions for this run as rows with `Source: chat answer (single-run)`.
- On the next `code-review-plan` rerun, the skill checks whether the answer is now present in source artifacts (`PLAN.md` / `.scope.md` / `.debug.md`); if not, the same question is asked again.
- Chat = single-run. Source-artifact patch = durable.

If an answer reveals genuine plan drift (the plan itself is wrong, not just unclear for review), the skill adds `unresolved plan drift: <one-line summary>` to §0 `Blocking issues` and pushes `Review readiness: BLOCKED`; recommend patching `PLAN.md` before review. Do not edit `PLAN.md` directly.

## Worked example questions

Five canonical question patterns (the skill adapts these to the actual situation):

### Q1 — Code diff completeness

> Is the changed-file list complete for this review round?

- A. Yes; review only the listed files.
- B. No; reviewers should include repository search for related call sites.
- C. Unknown; create a BLOCKED shard asking for changed-file discovery.
- Default: C.
- Tier: blocking (changes which shards can have concrete `Code areas to inspect`).

### Q2 — Deferred hardening boundary

> Should deferred hardening items from `scope-triage` be reviewed in this round?

- A. Exclude from review.
- B. Review only for accidental implementation / scope creep.
- C. Review as full correctness requirements.
- D. Block until `scope-triage` is updated.
- Default: B (conservative; scope-triage classified them as deferred).
- Tier: blocking (changes shard count and angles).

### Q3 — Unresolved debug-log bug

> `BUG-004` is still `OPEN` in `debug-log`. Should parallel review proceed?

- A. Block review until `BUG-004` is resolved.
- B. Proceed, but create a dedicated high-priority shard for `BUG-004`.
- C. Proceed, but mark final recommendation cannot be `APPROVE`.
- D. Ignore for this review round.
- Default: B.
- Tier: blocking (affects readiness and shard inventory).

### Q4 — Adversarial depth

> What adversarial review depth should reviewers use?

- A. Standard: 3–5 invariant-breaking prompts per high-risk shard.
- B. Deep: 8–12 prompts, include partial failure and repeated-call attacks.
- C. Release-critical: require adversarial evidence before any `PASS` verdict.
- Default: A.
- Tier: non-blocking (affects §5 prompt count, not shard inventory).

### Q5 — Primary review objective

> What is the primary review objective?

- A. Release readiness.
- B. Correctness and race-risk review.
- C. Scope adherence / no-overengineering review.
- D. Regression review after `debug-log` fixes.
- Default: A.
- Tier: non-blocking (affects shard angle selection at the margin; defaults are reasonable).
