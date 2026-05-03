# Clarification and User Feedback Protocol

`scope-triage` does **not** ask a question for every ambiguous item. The default is: classify best-effort, mark `Confidence: Low` if appropriate, and keep going.

## Core rule

> Ask only if the answer would change the implementation set. Otherwise classify, mark confidence, and continue.

## When to escalate to a Blocking Question

Ask the user — and gate coding-agent handoff — only when the answer would change one of these boundaries:

- whether an item is `P0-FORBIDDEN`
- whether an item is `P0-CORRECTNESS-FLOOR`
- whether an item belongs in MVP (`P1-*`) vs deferred
- whether an item is `P2-RELEASE-BLOCKER`
- whether an item is `P3-DEFER-HARDENING` vs `NO-OVERENGINEERING`
- whether source plan and sibling `<plan-stem>.tldr.md` disagree on a hard constraint, acceptance criterion, milestone, stop condition, or P0 boundary

If the question does **not** affect any of the above, do not block. Use a `Non-blocking Question` (§11 of the output) instead.

## Default behavior for ordinary ambiguity

For ambiguity that does NOT cross the boundaries above:

- classify best-effort
- mark `Confidence: Low`
- use `Action: Needs human decision` in the table when relevant
- record in §11 Non-blocking Questions / Low-confidence Defaults
- continue generating the scope artifact

## Confidence levels (semantics)

The `Confidence` column in §3 Category Table uses these levels:

| Level | Meaning | Trigger |
|---|---|---|
| **high** | Source plan directly states the classification (explicit constraint, AC, decision, or "do not do" line) | Anchor cite is verbatim from plan |
| **medium** | Classification follows from anchors via 1-step inference (e.g., AC implies a P0 boundary) | Anchor cite is "implied by Cn + ACm" |
| **low** | Classification is best-effort guess; plan is silent or ambiguous | No anchor; OR plan signals conflict; surface as §11 row |

A `Confidence: Low` row should always have a corresponding §11 row explaining the ambiguity and the default chosen.

## Question budget

At most **5 blocking questions per run**. If more exist, group them by decision boundary so each group surfaces one consolidated question:

1. P0 / correctness floor
2. MVP scope
3. release blocker
4. defer-vs-overengineering
5. source/TLDR drift

Non-blocking questions (§11) are not capped; they're informational.

## Decision-shaped questions only

Every blocking question MUST list labeled options + a `Default if unanswered` value. Open-ended questions are forbidden.

✅ Good:

```text
Q1. Should bounded timeout for router 0-active suspend be MVP or deferred?

Options:
  A. P0-CORRECTNESS-FLOOR (must ship in MVP)
  B. P1-LIGHTWEIGHT-DEFENSIVE (small assert in MVP)
  C. P3-DEFER-HARDENING (production hardening, M11.5)
  D. NO-OVERENGINEERING (do not implement)

Default if unanswered: C, because plan §F3 §7 marks MVP as unbounded suspend.
Affects: F08 in §3 Category Table
Reason: blocking — answer changes whether F08 enters MVP.
```

❌ Bad:

```text
What should the router do about timeouts?
```

## Conservative defaults

When the user does not answer a blocking question and you must produce a default classification:

| If the item could… | Default to… |
|---|---|
| silently produce wrong results | `P0-CORRECTNESS-FLOOR` or `P0-FORBIDDEN` |
| be useful but complex | `P3-DEFER-HARDENING` |
| be speculative abstraction | `NO-OVERENGINEERING` |
| be small, local, low-maintenance | `P1-LIGHTWEIGHT-DEFENSIVE` |
| be test/debug only | `DEV-ONLY` |
| affect release safety but not local MVP | `P2-RELEASE-BLOCKER` |

Always state the default in the §1 row's `Default if unanswered` cell.

## Source/TLDR drift question template

If `<plan-stem>.tldr.md` exists and disagrees with the source plan on a P0 / MVP / hard constraint / AC / milestone / stop condition, raise a blocking question:

```text
Q. Source plan and TLDR disagree on <item>. Which is current?

A. Source plan is current; regenerate TLDR later.
B. TLDR reflects newer intent; patch source plan.
C. Mark unresolved and block coding-agent handoff.

Default if unanswered: A. Source plan is authoritative.
```

Record the conflict in §12 Drift / Missing Constraints with cross-reference to the §1 question ID.

## Scope review state

`Scope review state:` is a **human gate status** — it tells the human reviewer whether the scope artifact is clean enough to bless an agent handoff. It is NOT an "agent execution command"; the agent handoff still requires explicit human action even when state is `SCOPE_REVIEW_READY`.

The field was previously named `Handoff readiness:` — that wording reintroduced exactly the misreading the design tries to prevent (reader sees "handoff" → assumes agent gate). The field gates **human review**, not agent handoff.

Set `Scope review state:` in the output header / §0 Executive Summary based on §1 / §11 / §2:

| State | When | What human should do next |
|---|---|---|
| `SCOPE_REVIEW_READY` | §1 empty AND §11 has no `Confidence: Low` rows AND §2 has no non-`ALIGNED` rows | Review §2 and §4, then choose to invoke coding agent. |
| `SCOPE_REVIEW_READY_WITH_DEFAULTS` | §1 empty BUT §11 has low-confidence defaults OR §2 has non-`ALIGNED` rows where `MVP set impact: no` | Review §11 defaults + §2 non-blocking deltas; **explicitly accept defaults OR patch source plan**. Only after acceptance may the §14 handoff draft be passed to a coding agent. The state name signals "human review can proceed" — NOT "agent ready". |
| `SCOPE_REVIEW_BLOCKED` | §1 has rows OR §2 has any row with `MVP set impact: yes` (or `unclear` that escalated) | DO NOT invoke agent. Resolve §1 / §2 in source plan, rerun `scope-triage`. |

When state is `SCOPE_REVIEW_BLOCKED`, the §14 Post-Review Handoff Draft outputs a blocked stub instead of the full draft (see §14 template). The blocked stub itself instructs the human to resolve in the source plan and rerun.

When state is `SCOPE_REVIEW_READY_WITH_DEFAULTS`, the §14 template MUST include an explicit precondition callout binding §11 acceptance to handoff use:

> **Precondition for `SCOPE_REVIEW_READY_WITH_DEFAULTS`**: the human reviewer MUST accept §11 defaults (or patch them into the source plan) before passing this block to a coding agent.

## Feedback loop

`scope-triage` is iterative, like `tldr-plan`:

```text
source plan → optional tldr-plan → scope-triage
              ↓
              blocking questions surface
              ↓
              user revises source plan to resolve them
              ↓
              rerun scope-triage
```

Do NOT treat chat answers as durable source-of-truth. If the user answers a blocking question in chat, the answer should be **patched into the source plan**, then `scope-triage` rerun. This keeps `<plan>.md` authoritative and prevents implementation agents from acting on conversational ephemera.
