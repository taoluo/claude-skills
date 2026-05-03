# Adversarial Prompts

Reusable adversarial prompt families, grouped by target. Each family is a question template the skill adapts to a specific shard.

The skill picks **3–8 adversarial prompts per high-risk shard** from the relevant categories, **specialized to the actual code area / invariant** — not pasted verbatim. The §5 Adversarial Review Prompts section of the artifact contains the specialized prompts; this reference file holds the templates.

## When to use

Adversarial prompts apply to any shard carrying the `ADVERSARIAL_INVARIANT_REVIEW` angle. They probe whether the implementation maintains its invariant under hostile sequences:

- repeated calls
- stale state
- reordered events
- partial failure
- concurrent contention
- malformed inputs

This is threat-modeling-style review (Microsoft SDL), generalized from web security to system invariants.

## Categories and templates

### Async condition / notify

- What if notify fires before the waiter starts waiting? (lost wakeup)
- What if state is mutated but notify never fires? (silent stall)
- What if multiple waiters wake but only one can proceed? (thundering herd / stale predicate)
- What if the notify happens during waiter cancellation?
- What if the waker holds the wrong lock when notifying?

### Lock / critical section

- What if the critical section is re-entered? (re-entrant lock or recursive call)
- What if the lock is dropped mid-operation (e.g., by an intervening yield / await)?
- What if two locks are acquired in different orders by different paths? (deadlock)
- What if the lock is bypassed in a cleanup path?
- What if an exception inside the critical section leaves invariants broken?

### Versioning / atomic publish

- What if the version is published before all buckets / shards load?
- What if two publishes race and one is silently lost?
- What if a reader observes the new version with old data?
- What if a publish succeeds but the version write fails?
- What if the version monotonicity assumption is violated by a rollback?

### Resource lifecycle

- What if cleanup partially succeeds (some resources released, some not)?
- What if the resource is referenced after release? (use-after-free)
- What if release is called twice? (double-free)
- What if resource acquisition fails mid-init and partial state leaks?
- What if the resource owner is killed before cleanup runs?

### Retry / preempt / fail-fast

- What if retry hides a fail-fast violation? (silent fallback)
- What if preemption happens mid-checkpoint? (inconsistent state)
- What if a retry storm overwhelms the downstream system?
- What if the error type meant to be fatal is caught by a generic handler?
- What if backoff state leaks across requests?

### Test evidence

- Does the assertion test the invariant or just the side effect?
- Would the test pass with the bug present? (mutation-test thinking)
- Does the test cover the failure mode `debug-log` recorded, or only the happy path?
- Is the test deterministic, or could it flake and hide regressions?
- Does the test exercise the boundary conditions of the `AC*`?

### Plan drift

- Did the implementation realize a different design from the planned `D*`?
- Did the code add behavior not in any `AC*`?
- Are the planned `C*` constraints actually enforced at runtime, or just documented?
- Did the implementation silently expand scope past what `scope-triage` classified as MVP?

### Overengineering

- Is this generality serving a planned consumer or a speculative one?
- Is this abstraction layer required by a current `D*`, or invented during implementation?
- Does this extension point have any current caller?
- Was this configuration knob requested in `PLAN.md`, or added "in case"?

## Specialization rule

Generic prompts ("What if notify fires before waiter starts?") become specialized prompts in §5 of the artifact:

```text
What if `_workers_changed.notify_all()` in `enable_worker` fires before a request waiter starts waiting on the condition? (Specifically: a request arrives between disable_worker completing and enable_worker mutating state — does it block forever?)
```

Specialized prompts cite:

- The specific function / module under review.
- The specific invariant being attacked.
- The specific scenario that would break the invariant.

A §5 entry that is just a template paste is rejected by the quality checklist.
