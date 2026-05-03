# Scope-Triage Categories

Every work item is classified into exactly one **primary category**. Optionally, a row may list secondary labels when an item legitimately spans categories.

## Quick reference table

| Category | One-line definition |
|---|---|
| `P0-FORBIDDEN` | Behaviors that must not be allowed; block / fail-fast / assert. |
| `P0-CORRECTNESS-FLOOR` | Minimum requirements for the feature to be semantically correct. |
| `P1-HAPPY-PATH` | Main implementation path delivering the feature's primary value (must be AC-backed). |
| `P1-OBSERVABILITY-FLOOR` | Minimum logging / tracing / metrics needed to debug the MVP. |
| `P1-LIGHTWEIGHT-DEFENSIVE` | Small, local, low-maintenance safeguards (no recovery semantics). |
| `DEV-ONLY` | Dev / test / simulation scaffolding, isolated from production. |
| `P2-RELEASE-BLOCKER` | Required before safe release / migration / rollback. |
| `P3-DEFER-HARDENING` | Valuable robustness work deferred until evidence / production need. |
| `P4-POLISH` | Non-essential ergonomics / docs / formatting. |
| `NO-OVERENGINEERING` | Speculative design that should not be implemented now. |

## P0-FORBIDDEN

Behaviors or implementation paths that **must not be allowed**.

Use when an item would:

- silently produce wrong results
- violate resource ownership / namespace / scheduler accounting
- bypass safety, permission, or invariant boundaries
- corrupt persistent state, data, checkpoints, or external side effects
- make debugging impossible by swallowing critical errors
- introduce dual state sources, broken state machines, or architectural reverse dependencies
- violate the feature's core contract

Treatment: block, fail fast, assert, reject, deny by default, make the failure explicit.

A `P0-FORBIDDEN` item is forbidden under the **current plan, milestone, and stated invariants**. If future work wants to allow it, that future plan must introduce new correctness boundaries, tests, and evidence — `scope-triage` does not pre-commit to "permanently never". This separates `P0-FORBIDDEN` from `P3-DEFER-HARDENING` ("not now, maybe later under existing invariants"): forbidden = changing the invariants is required before re-allowing; deferred = same invariants, just timing.

## P0-CORRECTNESS-FLOOR

Minimum requirements for the feature to be **semantically correct**.

Use when the feature cannot be trusted without the item. The implementation may be moderately complex, but the boundary is strict and narrow.

This is **not** hardening. This is the minimum correctness contract.

## P1-HAPPY-PATH

The main implementation path that delivers the feature's primary user-visible or system-visible value.

**HARD rule:** must be AC-backed (`AC*` / `C*` / `M*` anchor in source plan). If an item lacks an anchor but appears to be "main path", it is more likely `NO-OVERENGINEERING` (speculative future-use support framed as current value).

## P1-OBSERVABILITY-FLOOR

Minimum logging, tracing, metrics, error context, or debug surface needed to debug the MVP.

Do not expand into a full dashboard / SLO suite unless explicitly required by the plan.

## P1-LIGHTWEIGHT-DEFENSIVE

Small, local, low-maintenance safeguards that reduce likely mistakes without changing architecture or recovery semantics.

Use only when the item is:

- low complexity (a few lines, not a new abstraction)
- local (does not span multiple components)
- low maintenance (does not introduce a new state machine or tracking system)
- easy to test
- not a new framework / DSL / policy engine

If the item adds recovery, retry, fault tolerance, compensation, cross-state-window attribution, or production timeout — it is **not** lightweight defensive; it is `P3-DEFER-HARDENING` (or even `NO-OVERENGINEERING`).

## DEV-ONLY

Development, testing, simulation, or debugging scaffolding.

Must be isolated from the production code path:

- env-flag gated (`ENV=1`)
- `if DEBUG:` branched
- separate test-only module / import
- not extending production receiver/sender API surface

Examples: hash-based weight verification behind an env flag; mock workers; simulation harnesses; CI test wrappers that don't run in production.

## P2-RELEASE-BLOCKER

Items required before safe release, migration, rollback, or operator usage.

May not block local MVP correctness, but blocks the release event.

Examples: migration scripts, rollback procedures, operator runbooks, security review sign-off, license audit.

## P3-DEFER-HARDENING

Valuable robustness work that should be deferred until evidence, production need, or explicit release-stage requirement exists.

Distinguishing markers from `P0-CORRECTNESS-FLOOR`:

- adds recovery / retry / fault tolerance / compensation
- changes runtime recovery semantics
- introduces production-grade SLA timeouts
- handles failure modes that don't violate correctness when ignored

Always cite a **revisit trigger** (e.g., "production observation of X collision", "SLA requirement", "milestone Mn").

## P4-POLISH

Non-essential improvements to ergonomics, docs, naming, UI, formatting, or examples.

Keep this category short. If it grows large, the plan probably mixes finished feature work with unfinished feature work.

## NO-OVERENGINEERING

Speculative design that should **not** be implemented now.

Use when the item:

- mainly supports hypothetical future use cases
- introduces a framework / abstraction layer / plugin system before the second concrete consumer exists
- creates a DSL, policy engine, or generic resolver prematurely
- generalizes beyond current requirements

Distinct from `P3-DEFER-HARDENING`: deferred hardening has known value but premature timing; overengineering may have no value at all.

## Classification decision order

Use this **ordered decision process** for every item — first matching answer wins for the primary category. Secondary labels can be added afterwards.

1. Would allowing this make results, state, safety, ownership, or irreversible side effects untrustworthy? → `P0-FORBIDDEN`
2. Without this, is the feature semantically incorrect or unverifiable? → `P0-CORRECTNESS-FLOOR`
3. Is this speculative generalization, framework expansion, or future-use-case support **without a current `AC*` / `C*` / `M*` anchor**? → `NO-OVERENGINEERING`
4. Is this the main path that delivers **current acceptance-criterion-backed** feature value? → `P1-HAPPY-PATH`
5. Without this, would MVP failures be opaque or hard to debug? → `P1-OBSERVABILITY-FLOOR`
6. Is this a small, local, low-maintenance safeguard that does not add recovery semantics, new state machine, or new abstraction? → `P1-LIGHTWEIGHT-DEFENSIVE`
7. Is this only for development, testing, simulation, or debugging? → `DEV-ONLY`
8. Would this block safe release, migration, rollback, or operator usage but not local MVP correctness? → `P2-RELEASE-BLOCKER`
9. Is this valuable robustness work but too complex / production-specific for MVP? → `P3-DEFER-HARDENING`
10. Is this mostly ergonomics, docs, naming, formatting, examples, or presentation? → `P4-POLISH`

If multiple categories apply, choose the **highest-risk** category as primary (`P0-FORBIDDEN` > `P0-CORRECTNESS-FLOOR` > `NO-OVERENGINEERING` > `P1-*` > `P2-*` > `P3-*` > `P4-*`) and list the others as secondary labels in the same row.
