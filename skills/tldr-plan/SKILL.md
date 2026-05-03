---
name: tldr-plan
description: Compile a raw implementation plan into a compact-first, self-contained TLDR artifact for human audit before agent implementation. Extract problem context, assumptions, scope, hard constraints, D0-D6 decision trace, critical diagrams, evidence, and stop conditions. Iterative — re-run after each plan revision until the human audit passes; only then hand the plan to a coding agent. Use when a plan is too long to audit directly or too vague to hand to an agent. Source plan is authoritative.
---

# TLDR Plan

## What this is

Generate a **human-auditor-facing TLDR artifact** from a raw implementation plan.

Iterative by design — re-run after each plan revision until human audit passes:

```
plan v1 → tldr-plan v1 → human audit finds gaps
       → revise plan v2 → tldr-plan v2 → human audit
       → … → human audit passes → THEN hand the plan to a coding agent
```

`tldr-plan` is the audit surface, **not the handoff event**. Handoff is the destination this skill helps reach; it is not an action this skill performs.

## What this is NOT

- **Not a plan validator.** Does not approve, reject, or audit the plan itself. Does not emit findings/severity tags. Does not generate forward-looking ADRs or design specs. Does not check post-implementation drift.
- **Not a plan-summarizer hand-off generator.** The implementation agent does NOT read this artifact — the agent reads the original plan file directly.
- **Not a coding skill.** Does not modify code, run tests, or shell out to runtime tools.

The skill DOES validate **its own generated artifact's internal integrity** (citation grid + mermaid block syntax) — see `## Workflow Step 9a / Step 10`. This is artifact integrity check, not source-plan validation.

## Cooperative downstream

`tldr-plan` does NOT classify items as MVP / Defer / Forbidden / Overengineering. That is the responsibility of `scope-triage` (sibling skill).

Workflow:

1. `tldr-plan` mirrors the source plan into a human-audit artifact and surfaces traceability gaps for the human auditor (NOT a validator — does not approve/reject the plan globally).
2. Human iterates the source plan until the audit surface is acceptable.
3. `scope-triage` classifies source-plan items into implementation-boundary buckets and produces a Scope Delta Matrix.
4. Coding agent reads the SOURCE plan as ground truth (not TLDR, not scope) and uses the scope artifact only as boundary control.

If implementation-boundary classification is needed, the final TLDR output should append (as a closing line):

> Next suggested artifact: run `/scope-triage @<source-plan>.md` after human audit passes.

**Wording rule**: avoid "audits whether" / "validates whether" — `tldr-plan` SURFACES gaps and MIRRORS plan content; it does not pass judgment on the plan globally.

## When not to use

- The plan is < ~50 lines and already readable end-to-end.
- The plan is a brainstorm / exploration doc with no D / AC structure intended.
- You need scope/boundary classification, not audit traceability — use `scope-triage`.
- You want to validate code or post-implementation drift — neither skill does that.

## Source-of-truth rule

The **source plan is authoritative**. The TLDR mirrors plan content. Missing information is marked `unknown` and surfaced as audit checkpoints — `tldr-plan` does not invent answers.

## Invocation

```text
/tldr-plan @PLAN.md
/tldr-plan @PLAN.md --mode=compact
/tldr-plan @PLAN.md --mode=standard
/tldr-plan @PLAN.md --mode=complex
/tldr-plan current plan
/tldr-plan current diff
/tldr-plan
```

### Mode flag (compact / standard / complex)

| Mode | When | Per-mode behavior |
|---|---|---|
| `compact` | Small diff / single module / no architecture change | §0 Dashboard + §3 Scope (3.1+3.3 condensed) + §7 Audit Checkpoints + Appendix G if patches needed; OMIT Mermaid DAG, §3.4 if no staged delivery, §3.5, §4.2/4.3, §5 Decision Map can be table-only, Appendix A-E |
| `standard` (default) | Normal feature plan | Current default minimal trace (all §0-§7 visible, Appendix A-D conditional) |
| `complex` | Multi-milestone / multi-actor / runtime topology / resource scheduling | Full visible region + critical views + Appendix A-F + Appendix G if gaps + AC integrity (mandatory) + mermaid validation (mandatory) |

**Auto-detection** (when `--mode=` is not specified):
- plan < 200 lines AND no `M*` milestone tags AND no D0-D6 architecture markers → `compact`
- plan ≥ 200 lines AND no multi-milestone topology → `standard`
- plan has multi-milestone / multi-actor / runtime topology / resource scheduling → `complex`

User `--mode=` override always wins. If detection is mixed, default to `standard`.

**Canonical anchor invariant** (across all modes): even compact mode MUST preserve `### 3.3 Acceptance Criteria` / `## 5. Decision Map` / `#### 6.1 Evidence Required` / `### 3.4 Milestones` (when staged delivery exists). These are load-bearing for `check_tldr_integrity.py` and downstream `scope-triage` anchor recovery.

Full mode behavior + detection heuristics in `references/pattern-triggers.md`.

## Output File

Co-locate with source plan: `<plan-dir>/<plan-stem>.tldr.md`.

| Input plan | Output |
|---|---|
| `plans/PLAN.md` | `plans/PLAN.tldr.md` |
| `claude/plans/foo.md` | `claude/plans/foo.tldr.md` |
| `PLAN.md` | `PLAN.tldr.md` |

**Edge cases**:
- Input ends in `.tldr.md` → refuse: "input appears to be an existing TLDR; re-run on the source plan instead."
- Input read-only / outside workspace → write to `./<plan-stem>.tldr.md` in CWD with note.
- No plan supplied → fallback `./current-plan.tldr.md` in CWD.

### Overwrite-from-scratch rule

When a prior `<plan-stem>.tldr.md` already exists at the output path:

- **Regenerate the artifact from scratch from the source plan.** Do NOT read the prior TLDR as input. Do NOT merge, diff, or carry over content from the prior version.
- Use the Write tool (full-file overwrite), not Edit / patch / append.
- Iteration happens by re-extracting from the (possibly revised) source plan — NOT by evolving the TLDR file in place. The TLDR is a pure projection of the current source plan; any drift between source plan and TLDR must come from re-extraction, never from preserving stale TLDR text.
- The single permitted reason to read a prior `<plan-stem>.tldr.md` is when the user is invoking the skill on a *different* plan and explicitly asks to compare or borrow structure — that is out of the default workflow and must be requested.

Rationale: incremental update is silently lossy — sections that were removed from the source plan can survive in the TLDR, and stale IDs from a prior plan revision can shadow current IDs. Full regeneration guarantees the artifact reflects only what is in the source plan right now.

If writing files is unavailable, print the full Markdown result in the chat.

## Core Model

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

Lower-level decisions trace back to higher-level decisions.

### Four-axis layered model

- **AC** = Requirement (§3.3) — what the user receives at delivery
- **Milestone** = Schedule (§3.4) — when each AC ships
- **D** = Mechanism (§5) — how each AC is delivered
- **E** = Verification (§6.1) — how we know each AC is met

Every `D` must serve at least one `AC`. Every `AC` must be verified by at least one `E`. Milestones organize AC delivery into sign-off boundaries — `Done(Mn) = AC<i> ∧ AC<j> ∧ ...`.

### AC integrity hard rules (summary)

- §3.3 `Derives from` allow-list: `Goal | An | Cn` ONLY (Mn / Dn / En / Risk* / OpenQuestion* are forbidden)
- Every `Dn` row in §5 cites ≥1 `ACn` (verbatim) in `AC served`
- Every `ACn` in §3.3 covered by ≥1 `En` in §6.1
- §3.4 `Delivers AC` ↔ §3.3 `Milestone` bidirectional consistency

Full rules + ID grid + mutation table → `references/traceability-rules.md`.

## Workflow

Extract in this order (do **not** start from diagrams):

1. Read the supplied plan. If no file, use current plan or user's latest plan-like content.
2. Infer feature name when possible.
3. Extract context-first audit material:
   - a. **Problem context** — current vs gap
   - b. **Core assumptions** — `A1, A2, ...`
   - c. **Scope boundary** — in/out + rejected alternatives
   - d. **Hard constraints** — `C1, C2, ...` (`FF1, FF2, ...` for fail-fast)
   - d.5. **Acceptance criteria** — `AC1, AC2, ...` (REQUIREMENT axis; allow-list `Goal|An|Cn` ONLY)
   - d.6. **Milestones** — `M11.x` etc. (SCHEDULE axis; `Delivers AC` column)
   - e. **Decision hierarchy D0-D6** — derived from a-d.5; every `Dn` cites ≥1 `AC`
   - f. **Critical views** — diagrams that answer specific audit questions
   - g. **Evidence + stop conditions** — bind to `D` / `AC` IDs
3a. **Pattern activation pre-pass.** Scan for triggers (out-of-scope markers / fail-fast asserts / phase tags / strategy alternatives / hardware/resource words / wire schemas / lifecycle subsystems / cross-cutting matrices / alternative-axis IDs). Full trigger rules → `references/pattern-triggers.md`.
4. Mark inferred decisions with `(inferred)`.
5. Mark missing information as `unknown`.
6. Mark low-level details with no clear parent decision as `unanchored`.
7. Generate compact visible audit surface; full traceability in visible appendices.
8. Write result to `<plan-dir>/<plan-stem>.tldr.md` via the Write tool (full overwrite). If a prior TLDR exists at that path, do NOT read it — regenerate from scratch from the source plan per the `Overwrite-from-scratch rule` above. (Throughout `$OUT` denotes that path; `$STEM` denotes `<plan-stem>.tldr`.)
9. **Step 9a — Artifact integrity check** (mandatory before Step 10):

   ```bash
   python3 .claude/skills/tldr-plan/scripts/check_tldr_integrity.py "$OUT"
   ```

   This validates only the **TLDR artifact's internal citation grid** — NOT the source plan. exit 0 = pass; exit 1 = artifact AC-grid integrity failure (script prints which assertion failed). Script also accepts `--self-test` to verify against bundled fixtures.

10. **Step 10 — Diagram syntax check** (mandatory before finalizing):

    ```bash
    bash .claude/skills/tldr-plan/scripts/validate_mermaid.sh "$OUT"
    ```

    Exit codes:
    - 0 = all blocks compile, OR no Mermaid blocks present
    - 1 = at least one Mermaid block fails to parse — fix and re-run
    - 2 = `node`/`npx` unavailable (treated as SKIP — not a hard failure)

    If `npx`/`node` is unavailable, state that the mechanical check could not run and ask the user how to proceed instead of skipping silently.

## Output Layout

Top-level visible region (in fixed order — triage → context → contract → design → pre-ship gate):

```
0 Dashboard → 1 Context → 2 Assumptions → 3 Scope & Constraints
            (3.1 Out of Scope → 3.2 Hard Constraints → 3.3 AC → 3.4 Milestones → 3.5 Strategy)
            → 4 Critical Views → 5 Decision Map → 6 Evidence & Stop Conditions
            → 7 Audit Checkpoints
```

Then visible appendices (NEVER `<details>` / collapsed):

```
Appendix A: Full Decision Trace
Appendix B: Full Module / File Boundary
Appendix C: Full Risk → Evidence Matrix
Appendix D: Implementation Detail Trace
Appendix E: Plan-Mirrored Execution Anchors (auditor view)
Appendix F: Activated Pattern Details (conditional)
Appendix G: Plan Patch Suggestions (conditional — only when unknown markers / audit gaps)
```

Sections marked `conditional` appear only when their trigger fires. **Always visible**: §0 / §3.1 / §4.1 / §5 / §7. When collapsing a conditional section, **remove the heading entirely** — empty headings are worse than absent.

Why §3.3 (AC) precedes §3.4 (Milestones) and §3.5 (Strategy): AC = requirement (deepest), Milestones = schedule, Strategy = mechanism alternatives. AC must be expressible from `Goal + An + Cn` alone.

Why Decision Map (§5) follows Critical Views (§4): diagrams are the intuitive on-ramp; the DAG is the audit tool.

§6 vs Appendix C — both list evidence but cut differently:
- §6 is **decision-driven** (rows bind to `D / A / C / M`)
- Appendix C is **risk-driven** (rows bind to risk descriptions)
Never duplicate rows across §6 and Appendix C.

Full output skeleton + per-section requirements → `references/output-layout.md`.

### Appendix E framing rule (auditor view, NOT agent handoff)

Appendix E is named `Plan-Mirrored Execution Anchors (auditor view)`. Add intro line:

> This appendix mirrors execution anchors found in the source plan. **It is not a new instruction set for the implementation agent — agents must read the source plan directly.**

Stop-condition wording uses **mirror voice**: `The plan instructs the agent to stop and ask if:` (NOT `Stop and ask the user if:` — legacy template; reads as direct instruction to agent and contradicts the single-reader rule).

### Appendix G placement rule

Appendix G is **additive** — does NOT renumber visible §0-§7. Conditional: include only when `unknown` markers OR audit-checkpoint gaps exist. Cross-link from §7 Audit Checkpoints: `See Appendix G for concrete source-plan patch suggestions.`

Why Appendix G, not §8 in visible region: §0-§7 visible order is load-bearing; §7 Audit Checkpoints is the pre-ship gate. Renumbering breaks operator habit and existing TLDR cross-references.

## Mermaid

Allowed visible diagrams: Decision DAG (§5), Architecture Integration View (§4.1), Runtime / Data Path View (§4.2), Physical Topology View (§4.3 — only when Step 3a triggers it). Additional diagrams go in Appendix F.

Each diagram answers ONE audit question. State the question above the diagram in italics or as a comment. If you cannot state the question in one sentence, the diagram does not belong.

Quick principles:
- Use simple labels; all important arrows directional.
- No HTML tags inside Mermaid (`<br/>`, `<sub>`, `<span>` etc.).
- No `;` semicolons inside `Note over ...` text in `sequenceDiagram`.
- Keep arrow messages short and descriptive (avoid literal call signatures with parens/equals).

Full cookbook + parser-trap list + audit-question reference → `references/mermaid-rules.md`.

## Style rules

Use direct, technical language. Prefer tables, diagrams, and checkboxes over prose.

- `unknown` when plan lacks information
- `(inferred)` when deriving decisions from context
- `unanchored` when implementation detail lacks parent decision

Use stable IDs (`A*` / `C*` / `AC*` / `M*` / `D*` / `E*`) so cross-references survive editing. Define each ID once in its canonical table; other sections cite by ID only. Cross-reference whenever possible (`D3 depends on A2 and C2; first delivered in M11.2`).

Full citation grid + cross-reference rules → `references/traceability-rules.md`.

## Quality checklist

Before finalizing the artifact, verify:

- Header lists Source plan + (optional) TLDR mode + appropriate frontmatter.
- §0 Audit Dashboard ≤ 13 lines (was ≤ 12 before the `Artifact integrity` line was added).
- §0 Audit Dashboard includes the `Artifact integrity:` line citing AC-grid + Mermaid pass/fail/skipped status, derived from Workflow Step 9a + Step 10 script exit codes (see `references/output-layout.md` §0 mapping table).
- §3.3 Acceptance Criteria present (or explicit `(plan does not declare outcome-level AC)` placeholder + §7 checkpoint).
- §3.3 `Derives from` cells contain ONLY `Goal | An | Cn` (no `Mn` / `Dn` / `En` / `Risk*`).
- Every `Dn` in §5 cites ≥1 `AC` in `AC served`.
- Every `ACn` in §3.3 covered by ≥1 `En` in §6.1.
- §3.4 `Delivers AC` ↔ §3.3 `Milestone` bidirectional consistent.
- All Mermaid blocks compile (run `validate_mermaid.sh`).
- Appendix E uses mirror voice ("the plan instructs the agent to..."), not direct voice.
- Appendix E header is `Plan-Mirrored Execution Anchors (auditor view)`.
- Cooperative downstream note (or "Next suggested artifact: scope-triage" line) present when implementation-boundary classification is needed.
- No D0-D6 generation duplicated outside §5.
- No "validator" / "approve plan" / "reject plan" wording — only "artifact integrity" for self-checks.
- Artifact does NOT contain a coding-agent handoff block (that's `scope-triage`'s §14 responsibility, not `tldr-plan`'s).

## What NOT to do

- Do not approve / reject the plan globally; do not call it safe/unsafe.
- Do not modify the source plan.
- Do not implement any feature.
- Do not run tests, linters, or otherwise execute code beyond the artifact integrity script + mermaid validator.
- Do not invent missing plan content (`unknown` + audit checkpoint instead).
- Do not generate scope classification (forbidden / MVP / defer / overengineering / etc.) — that's `scope-triage`'s job. Use Appendix G to suggest source-plan patches; do not produce the implementation-boundary artifact yourself.
- Do not produce a coding-agent handoff block — `tldr-plan`'s artifact is for human audit only.
- Do not hide / collapse / fold appendix content (`<details>`/`<summary>`/zipped blocks). Compact-first means short visible top, not hidden bottom.

## References

This skill is part of the shared plan-artifact pipeline. See `.claude/skills/README.md` for the overview.

Read these only when needed (per progressive disclosure):

- `references/output-layout.md` — full output skeleton + per-section requirements
- `references/traceability-rules.md` — AC-D-E rules + ID grid + integrity check spec + mutation table
- `references/pattern-triggers.md` — Step 3a trigger rules + mode auto-detection heuristics
- `references/mermaid-rules.md` — full mermaid cookbook + parser traps
- `references/examples.md` — worked example
- `examples/fixture-valid.tldr.md` + `examples/fixture-invalid-ac.tldr.md` — bundled self-test fixtures

Scripts:

- `scripts/check_tldr_integrity.py` — Step 9a (also `--self-test`)
- `scripts/validate_mermaid.sh` — Step 10
