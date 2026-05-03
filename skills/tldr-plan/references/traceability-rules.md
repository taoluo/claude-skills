# Traceability Rules — AC-D-E + ID grid + integrity check spec

## Core model

Code implementation is determined by a hierarchy of decisions:

```text
D0: Goal / Problem
D1: Architecture Integration
D2: Module Boundary
D3: Runtime Behavior
D4: Data / State / API Shape
D5: Implementation Details
D6: Evidence / Tests
```

Lower-level decisions must trace back to higher-level decisions.

Translation order:

```text
why change
-> where the feature integrates into the architecture
-> how module boundaries are drawn
-> how runtime/data paths change
-> how API/state shape changes
-> how implementation details follow from those decisions
-> what evidence is needed to confirm the implementation did not drift
```

## Four-axis layered model

| Axis | Section | What it answers |
|---|---|---|
| **Requirement (AC)** | §3.3 Acceptance Criteria | What does the user receive at delivery? |
| **Schedule (Milestone)** | §3.4 Milestones | When does each AC ship? |
| **Mechanism (D)** | §5 Decision Map | How is each AC delivered? |
| **Verification (E)** | §6.1 Evidence Required | How do we know each AC is met? |

`AC` is the deepest concept. Every `D` must serve at least one `AC`. Every `AC` must be verified by at least one `E`. Milestones organize AC delivery into sign-off boundaries — `Done(Mn) = AC<i> ∧ AC<j> ∧ ...`.

## Citation grid

Use stable IDs so cross-references survive editing and PR review can reference them precisely. Each ID type has one canonical definition table:

| Kind | ID | Defined in | Used by |
| ---- | -- | ---------- | ------- |
| Assumption | `A1, A2, ...` | `## 2 Assumptions` | `## 3.3 AC`, `## 5 Decision Map`, `## 6 Evidence`, `## 7 Audit Checkpoints` |
| Hard constraint | `C1, C2, ...` | `## 3.2 Hard Constraints` | `## 3.3 AC`, `## 5`, `## 6`, `## 7`, `Appendix C` |
| Fail-fast assert | `FF1, FF2, ...` | `## 3.2` (when distinguished from hard contract) | same as `C` |
| Acceptance criterion | `AC1, AC2, ...` | `## 3.3 Acceptance Criteria` (REQUIREMENT axis) | `## 3.4` (Delivers AC), `## 5` (AC served), `## 6.1` (AC verified), `## 7`, `Appendix E` (Done lines) |
| Milestone | `M11.x / Phase N / vN` | `## 3.4 Milestones` (SCHEDULE axis) | `## 3.3 AC` (Milestone column, forward-ref), decision rows, evidence rows, audit checkpoints, Appendix E Done lines |
| Decision | `D0..D6` | `## 5 Decision Map` | `## 6`, `## 7`, all appendices |
| Evidence | `E1, E2, ...` | `## 6.1 Evidence Required` | `## 3.3 AC` (Verified by), `## 7 Audit Checkpoints`, Appendix C cross-ref |

Define each ID exactly once in its canonical table. Other sections cite by ID only — do not redefine the content.

## Citation-grid integrity (no orphan IDs)

Every ID that appears in any canonical table MUST also appear in at least one cross-reference, AND every ID that appears in a *trace table* (Appendices A / C / D) MUST also appear in the corresponding *visible* table or diagram.

Concrete checks:

- For every row in `Appendix A: Full Decision Trace`, the decision ID MUST appear in `## 5 Decision Map` (both DAG node *and* compact decision table). Drift example: `Appendix A` lists `D3.F` but `## 5` only has `D3A..D3E` — visible region under-represents a decision the trace claims exists. Add the node to DAG or remove from trace; never let them drift.
- For every `ACn` in `## 3.3`, at least one `Dn` row in `## 5` MUST cite it in `AC served`, AND at least one `En` row in `## 6.1` MUST cite it in `AC verified`, AND (if `## 3.4` exists) one `Mn` row MUST cite it in `Delivers AC`. Orphan AC = unfulfilled / unverifiable / unscheduled promise. Conversely, every `Dn` row MUST cite ≥1 AC in its `AC served` cell. Orphan decision = over-engineering or hidden goal.
- §3.3 `Derives from` allow-list is **strict**: `Goal | An | Cn` only. **`Mn` is forbidden** (milestone is schedule, not requirement; lives in §3.4). `Dn` / `En` / `Risk*` / `OpenQuestion*` also forbidden.
- For every `Cn` in §3.2, at least one row in `Appendix C` or `## 6.1` should reference it (otherwise constraint has no verification handle).
- For every `An` in §2, at least one row in `## 6.2 Stop Conditions` or `## 7` should reference it (otherwise no one notices when assumption fails).
- For every `En` in §6.1, at least one checkpoint in §7 should reference it (otherwise evidence has no audit handle).
- For every `M*` in §3.4, `Delivers AC` MUST contain ≥1 `ACn` token. Bidirectional consistency: each `ACn` in `Delivers AC` must exist in §3.3 with `Milestone = M*` matching the row. Appendix E `Done(M*)` lines must reference only `ACn` IDs that exist in §3.3.

## Artifact integrity check (Step 9a)

This validates only the **TLDR artifact's internal citation grid** — NOT the source plan. Run `scripts/check_tldr_integrity.py <tldr-file>` for automated check. The script enforces this mutation table:

| Mutation | Expected exit |
|---|---|
| Remove the only `AC1` from §5 `AC served` (D1 has no AC) | 1 |
| Remove the only `AC1` from §6.1 `AC verified` (AC uncovered) | 1 |
| `D1.AC served` = `AC999` (cites token not defined in §3.3) | 1 |
| `E1.AC verified` = `AC999` (cites token not defined in §3.3) | 1 |
| Change §3.3 `Derives from` to `Goal, D1` (forbidden — Dn is mechanism) | 1 |
| Change §3.3 `Derives from` to `Goal, M11.1` (forbidden — Mn is schedule) | 1 |
| Change `AC1` ID in §3.3 to `AC 1` (format inconsistent) | 1 |
| §3.4 Milestone row `M11.1.Delivers AC` empty AND `Scope` not marked `(future)` | 1 |
| §3.4 `M11.1.Delivers AC` cites `AC999` (token not in §3.3) | 1 |
| §3.3 `AC1.Milestone = M11.1` but §3.4 `M11.1.Delivers AC` does NOT include `AC1` | 1 |
| §3.4 `M11.1.Delivers AC` includes `AC1` but §3.3 `AC1.Milestone = M11.2` | 1 |
| All consistent, no orphans, no forbidden tokens, bidir matches | 0 |

The script also accepts `--self-test` to verify expected behavior on bundled fixtures.

## Style rules

Use direct, technical language. Prefer tables, diagrams, and checkboxes over prose.

- `unknown` when plan lacks information
- `(inferred)` when deriving decisions from context
- `unanchored` when implementation detail lacks parent decision

Cross-reference whenever possible. Examples:
- `D3 depends on A2 and C2; first delivered in M11.2`
- `E4 verifies C5 and A3`
- `Implementation detail I7 (Appendix D) must not violate FF2`

Unnumbered prose constraints decay; do not leave them only in prose.

Before declaring document complete, do final pass over each canonical table and grep the rest of document for IDs. Orphan IDs are the most common silent decay path.
