# Shard Template

Canonical shard template + sizing rule + anti-patterns.

## Template

Each shard in §4 Parallel Review Shards must use this structure:

```markdown
### R<NN>: <feature area / invariant>

- Goal:
- Must-read anchors:           (canonical plan-level IDs only: AC* / C* / D* / E* / M* / A*)
- Scope categories / scope notes:  (optional; P0/P1/etc. labels + non-canonical F* navigation refs)
- Code areas to inspect:
- Review angles:               (2–5 from references/review-axes.md)
- Adversarial questions:       (3–8 specialized prompts for high-risk shards; cross-link to §5)
- Required tests / evidence:
- Known bugs from debug-log:   (BUG-* IDs from <plan-stem>.debug.md, if any)
- Expected reviewer output:    (point to §7 Subagent Report Template)
- Stop conditions:             (when reviewer should halt and ask the human)
```

## Sizing rule

If a shard would require reviewing more than **~200–400 LOC** or more than **~60 min** of review time, split into multiple shards. (Source: SmartBear peer-review research — defect detection drops sharply past these thresholds.)

Each split inherits the parent shard's anchors and adds a `Parent shard:` field for traceability:

```markdown
### R03.a: Router suspend — disable_worker path
- Parent shard: R03
- ...

### R03.b: Router suspend — enable_worker / notify path
- Parent shard: R03
- ...
```

## Shard ID convention

- Top-level shards: `R01`, `R02`, `R03`, … (zero-padded, monotonic).
- Splits: `R03.a`, `R03.b`, `R03.c`, …
- IDs are stable across the artifact (cited in §3 Feature Review Matrix, §5 Adversarial Prompts, §6 Subagent Assignment Plan).

## Anchor canonicality

- `Must-read anchors:` carries canonical plan-level IDs only: `AC*` / `C*` / `D*` / `E*` / `M*` / `A*` from `PLAN.md` or `<plan-stem>.tldr.md`.
- `Scope categories / scope notes:` carries category labels (`P0-CORRECTNESS-FLOOR`, etc.) and MAY append optional `F*` navigation refs in parentheses (e.g., `P0-CORRECTNESS-FLOOR (F39)`).
- `F*` MUST NOT appear in `Must-read anchors:`. Scope IDs are derived; only plan-level anchors are canonical.

## Anti-patterns (rejected)

The skill must reject these as "not a shard":

- **"Review all changed files"** — this is the absence of a shard. Cluster by invariant.
- **"Review all router code"** — too broad; split by invariant (suspend / dispatch / health).
- **"Review everything related to training"** — too broad; split by lifecycle phase or by `M*` milestone.
- **"Generic style review"** — `MAINTAINABILITY_REVIEW` is fine, but must be scoped to a subsystem and bound to specific code areas. "Review the codebase for style" is not a shard.
- **"Review for security"** without specifying invariants — `ADVERSARIAL_INVARIANT_REVIEW` requires concrete attack questions in §5, not a vague directive.

## Cluster heuristics (how to choose shard boundaries)

- **By invariant**: e.g., "router zero-active suspend correctness" — one suspend/resume invariant, multiple touched files.
- **By subsystem lifecycle**: e.g., "NCCL group lifecycle" — init / use / teardown.
- **By risk cluster**: e.g., "all state-mutating router endpoints not yet audited for `notify_all`" — collected from `debug-log` follow-up risks.
- **By plan anchor cluster**: e.g., "all `C*` constraints touching atomic publication".

Avoid:

- Sharding by file (file is an implementation detail; invariants cross files).
- Sharding by author (review is about code, not authorship).
- Sharding by review angle alone (a shard with only `MAINTAINABILITY_REVIEW` and no scope is a checklist, not a shard).
