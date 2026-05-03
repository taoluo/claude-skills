# Review Axes

The 11 controlled review angles. Each shard in §4 of the artifact must carry 2–5 angles from this list.

| Axis | Use when | Typical questions |
|---|---|---|
| `PLAN_ADHERENCE_REVIEW` | Verify implementation follows `PLAN.md`, not a different design | Did code implement the planned behavior? Are the planned abstraction boundaries preserved? Does any code add behavior not in any `AC*`? |
| `CORRECTNESS_REVIEW` | Verify core semantic correctness | Can it silently produce a wrong result? Are edge cases handled per `AC*`? Are off-by-one / boundary conditions correct? |
| `CONCURRENCY_RACE_REVIEW` | Review locks, async ordering, state transitions | Can two calls interleave and break invariant? Is there a TOCTOU window? Is notify/wait paired correctly? |
| `RESOURCE_LIFECYCLE_REVIEW` | Review GPU / Ray actor / NCCL / tmpfs / file / process lifecycle | Are resources released exactly once? What happens if cleanup partially fails? Are double-frees / use-after-release possible? |
| `ERROR_HANDLING_FAIL_FAST_REVIEW` | Review failure behavior | Are critical errors swallowed or converted into generic retries? Are fail-fast `C*` constraints honored? Does silent fallback hide real failures? |
| `ADVERSARIAL_INVARIANT_REVIEW` | Attack invariants with hostile sequences | What breaks under repeated, stale, reordered, or partial calls? Specialized prompts go in §5. |
| `TEST_EVIDENCE_REVIEW` | Check whether tests prove the claimed invariant | Does test evidence actually cover the AC? Is the assertion the right one? Would the test pass with the bug present? |
| `DEBUG_REGRESSION_REVIEW` | Check whether `debug-log` bugs can recur | Did the fix address root cause or only symptom? Are similar code paths protected? Are there other endpoints with the same pattern? |
| `OBSERVABILITY_REVIEW` | Check debuggability | Can failures be diagnosed from logs / errors / metrics alone? Are error messages actionable? |
| `PERFORMANCE_RESOURCE_REVIEW` | Check latency / memory / contention | Any OOM, leak, unbounded wait, or hot-loop risk? Are batch sizes / timeouts reasonable? |
| `MAINTAINABILITY_REVIEW` | Check long-term code health | Is the implementation too complex or hard to modify? Does it violate `NO-OVERENGINEERING`? Are abstractions justified by current consumers? |

## High-risk-shard hard rule

Every **high-risk shard** (P0-derived OR `debug-log`-derived OR highest-risk-decision-derived) MUST include at least one of:

- `CORRECTNESS_REVIEW`
- `CONCURRENCY_RACE_REVIEW`
- `RESOURCE_LIFECYCLE_REVIEW`
- `ADVERSARIAL_INVARIANT_REVIEW`
- `ERROR_HANDLING_FAIL_FAST_REVIEW`

The skill rejects high-risk shards that only carry `MAINTAINABILITY_REVIEW` / `OBSERVABILITY_REVIEW` axes — those are valid review angles, but insufficient on their own for high-risk areas. A high-risk shard with only "is the code clean?" framing misses the point of running the review at this phase.

## Risk classification (informal)

A shard is high-risk if any of the following hold:

- It covers a `P0-FORBIDDEN` or `P0-CORRECTNESS-FLOOR` item from `.scope.md`.
- It covers a highest-risk decision / assumption / constraint from `.tldr.md` (e.g., a `D*` flagged as critical, a `C*` that's a hard guard).
- It covers a feature where `debug-log` recorded a `BUG-RACE-CONDITION` / `BUG-INTEGRATION` / `BUG-PERFORMANCE` (whether resolved or not), since recurrence in similar code paths is the most common review finding.
- It covers a milestone gate (`M*`) where a regression would block release.

Medium-risk and low-risk shards may carry any combination of angles, including `MAINTAINABILITY_REVIEW` / `OBSERVABILITY_REVIEW` alone.
