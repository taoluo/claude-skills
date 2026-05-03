# Plan Audit, Boundary, Debug & Review Skills

Cooperative skills that turn a raw implementation plan into something safe to hand to a coding agent, record what actually happens once implementation begins, and brief a parallel reviewer fleet once end-to-end tests pass.

The skills do **not** replace human review. They produce artifacts a human iterates on:

- `tldr-plan` produces a compact human-audit surface for the plan and surfaces traceability gaps.
- `scope-triage` classifies plan items into implementation-scope buckets and surfaces where its classification disagrees with the plan's declared scope.
- `debug-log` records execution reality during smoke / integration / E2E debugging as an append-only, plan-linked bug log.
- `code-review-plan` turns the four artifacts above plus the code diff into a parallelizable code-review workplan: bounded review shards, controlled review angles, adversarial prompts, subagent assignments, and an aggregation contract.

Coding-agent handoff happens **only after** a human reviews the scope artifact and explicitly invokes the agent. Neither `tldr-plan` nor `scope-triage` auto-fires anything, `debug-log` never silently edits the source plan, and `code-review-plan` never reviews code itself — it only briefs the reviewer fleet.

`debug-log` can be used after agent-driven implementation, manual fixes, or any smoke / integration / E2E debugging event — not only post-agent. `code-review-plan` is invoked after end-to-end tests pass; tests-passing evidence can come from `debug-log` `Current status: PASSING` or from a CI-summary note in the invocation. Both skills are invocation-agnostic about who ran the tests.

## Pipeline

```mermaid
flowchart TD
  P[PLAN.md source of truth] --> T[tldr-plan]
  T --> TLDR[PLAN.tldr.md human audit artifact]
  TLDR --> H1[Human audits and revises PLAN.md]
  H1 --> S[scope-triage]
  S --> SC[PLAN.scope.md human boundary artifact]
  SC --> H2[Human reviews questions and deltas]
  H2 --> A[Human explicitly invokes coding agent]
  A --> AGENT[Coding agent or human implements feature]
  AGENT --> SMK[Smoke / integration / E2E tests]
  SMK --> DBG[debug-log]
  DBG --> DBG_ART[PLAN.debug.md execution record]
  DBG_ART --> H3{Plan impact?}
  H3 -- NO_PLAN_CHANGE --> SMK
  H3 -- plan impact needs revision --> H4[Human patches PLAN.md]
  H4 --> T
  H4 --> S
  DBG_ART --> H_TEST{Tests pass end-to-end?}
  H_TEST -- no --> SMK
  H_TEST -- yes --> RP[code-review-plan]
  RP --> RP_ART[PLAN.review.md review workplan]
  RP_ART --> H_READY{Review readiness?}
  H_READY -- BLOCKED or NEEDS_INPUT --> RP_FIX[Human resolves Blocking issues / answers questions / refreshes inputs]
  RP_FIX --> RP
  H_READY -- READY --> RV_FLEET[Parallel review fleet — humans or AI subagents]
  RV_FLEET --> RV_REPORTS[Per-shard subagent reports]
  RV_REPORTS --> AGG[Aggregator → final review report]
  AGG --> H5{Findings?}
  H5 -- bugs found --> DBG
  H5 -- plan drift --> H4
  H5 -- approve --> SHIP[Ship]
```

Tests-passing evidence for `code-review-plan` can come from any of three sources (in priority order): `debug-log` header `Current status: PASSING`, an invocation note with CI / test output, or an explicit user assertion in the invocation note. The diagram's "Tests pass end-to-end?" gate is satisfied by any of them — `debug-log` is convenient but not the only path.

## When to use which

| Question | Skill |
|---|---|
| Do I need a compact human audit surface for context / assumptions / AC / D0-D6 / evidence, with traceability gaps surfaced? | `tldr-plan` |
| Of the items in the plan, which are MVP / forbidden / deferred / overengineering? | `scope-triage` |
| Did smoke / integration / E2E tests fail (whether agent-driven or manual) and do I need a per-bug execution record? | `debug-log` |
| Did implementation finish, do smoke / integration / E2E tests pass end-to-end, and do I now need to brief a parallel review fleet (humans or AI subagents) on what to review and how to report? | `code-review-plan` |
| Do I need the full current flow? | Run `tldr-plan` first; iterate plan until audit surface is acceptable; then `scope-triage` for boundary control; then `debug-log` during implementation debugging; then `code-review-plan` once end-to-end tests pass to brief the parallel review fleet. |

## Cross-skill invariants

- **Source plan is authoritative.** Pipeline skills read `PLAN.md` as ground truth. Derived artifacts never override the plan. `debug-log` may emit `Plan Revision Suggestions` but never silently edits `PLAN.md`. `code-review-plan` may surface plan drift via subagent reports but never edits `PLAN.md`.
- **Human-iterated.** All artifacts are designed for human review. If review surfaces issues, the user revises `PLAN.md` and re-runs the relevant skill.
- **No auto-handoff.** Coding-agent handoff is a deliberate human action, never a triggered side effect of writing an artifact. `code-review-plan` produces a brief; the human launches the reviewer fleet.
- **Cooperative, not duplicative.** `tldr-plan` audits traceability (AC ↔ D ↔ E grid). `scope-triage` classifies boundary (forbidden / MVP / deferred / overengineering). `debug-log` records execution reality (symptom → root cause → fix → verification → plan impact). `code-review-plan` brief the reviewer fleet (shards / angles / adversarial prompts / report contract / aggregation contract). None does another's job; in particular, `code-review-plan` does NOT review code itself.
- **Different update models on purpose.** Three of four skills (`tldr-plan` / `scope-triage` / `code-review-plan`) regenerate from scratch on every run (pure projections of the source plan + sibling artifacts). Only `debug-log` is **append-only** — it reads its prior output and updates entries by stable `BUG-*` / `REV-*` / `RUN-*` IDs.

## Quick links

- [`tldr-plan/SKILL.md`](tldr-plan/SKILL.md) — entry doc + `## When not to use`
- [`scope-triage/SKILL.md`](scope-triage/SKILL.md) — entry doc + `## When not to use`
- [`debug-log/SKILL.md`](debug-log/SKILL.md) — entry doc + `## When not to use`
- [`code-review-plan/SKILL.md`](code-review-plan/SKILL.md) — entry doc + `## When not to use`

## Examples

- Small example (scope-triage on a single-feature plan):
  - [`scope-triage/examples/input-plan.md`](scope-triage/examples/input-plan.md)
  - [`scope-triage/examples/output-scope.md`](scope-triage/examples/output-scope.md)
- Smoke-debug example (debug-log on a router zero-active-suspend session):
  - [`debug-log/examples/input-session-notes.md`](debug-log/examples/input-session-notes.md)
  - [`debug-log/examples/output-debug-log.md`](debug-log/examples/output-debug-log.md)
- Code-review-plan example (continues the router zero-active-suspend story; same C20 / BUG-001 anchors):
  - [`code-review-plan/examples/input-artifact-index.md`](code-review-plan/examples/input-artifact-index.md)
  - [`code-review-plan/examples/output-review-plan.md`](code-review-plan/examples/output-review-plan.md)
- Multi-milestone walk-through (tldr-plan → scope-triage on a complex plan): TODO. The repo's `plans/miles-port-unified-plan.{md,tldr.md,scope.md}` triple is currently the closest real-world reference.
