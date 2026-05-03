# Pattern Triggers — Workflow Step 3a + mode auto-detection

## Step 3a — pattern activation pre-pass

Run this scan **before** committing to D0-D6, because some triggers are surface markers that do not appear in the high-level decision graph (milestone tags, fail-fast asserts, wire-schema fields). Missing them at this stage means missing them entirely.

### Trigger rules

| Trigger | Effect |
|---|---|
| Out-of-scope markers (`Out of Scope` / `不做` / `out-of-scope` / `non-goal` / `rejected alternative` / `已决边界`) | Always produce `## 3.1 Out of Scope`. If silent, write `none declared` (silence is itself an audit signal). |
| Fail-fast asserts, critical invariants, `must` / `必须` constraints, startup validation blocks | Produce numbered `## 3.2 Hard Constraints` table (`C1, C2, ...` for hard contract; `FF1, FF2, ...` for fail-fast asserts specifically). |
| Phase / milestone / version tags (`M11.x`, `Phase 1`, `v2`, `Week 1`, `gate N`) | Produce single canonical `## 3.4 Milestones` table. |
| One decision with ≥3 named alternatives shipped under different conditions (transports, backends, algorithms) | Produce `## 3.5 Strategy Comparison` matrix. |
| Hardware/resource words in goal (`GPU`, `node`, `port`, `file descriptor`, `NUMA`, `socket`, `lane`, `rank`, `worker`, `shard`) where topology affects correctness, placement, scheduling, ownership, or lifecycle | Add `### 4.3 Physical Topology View` to Critical Views. |
| New wire / RPC / HTTP / callback / event / config schemas | Produce `## Appendix F: Activated Pattern Details` with Wire-Format Quick Reference table. |
| Subsystems with independent lifecycle and ≥3 meaningful states (router admission, cache slot, port pool, scheduler queue, worker, connection) | Produce `stateDiagram-v2` in Appendix F. Promote to Critical Views only when lifecycle correctness is one of the top audit risks. |
| Cross-cutting role/path dimensions (`rank × role`, `phase × component`, `transport × path`) | Produce role matrix in Appendix F, or visible section if central. |
| Rejected alternatives / "已决边界" / design tradeoffs scattered through plan | Consolidate into `## 3.1` (rejection rationale) and `## 3.5` (alternatives table). Do not duplicate across appendices. |
| Alternative-axis numbering in source plan (e.g. `F1..F12` features, `Component A..G`, `Workstream 1..N`, `Module M1..Mk`) different from D0-D6 axis | Produce navigation crosswalk table in `Appendix F`. Format: `\| Source-axis ID \| Primary D \| Secondary D \| Notes \|`. |

When a trigger fires, include the corresponding pattern. When it does not fire, omit the pattern and do not invent placeholder content. Do not invent fake topology for software-only plan or fabricate constraints to fill `## 3.2`.

### Plan Patch Suggestions trigger (Appendix G)

If the workflow encounters `unknown` markers OR audit-checkpoint gaps that the human should address in the source plan, produce `## Appendix G: Plan Patch Suggestions` with a structured table of patches the human should apply to source plan, then rerun tldr-plan.

Table format:

| Gap | Why it matters | Suggested source-plan location |
|---|---|---|

Conditional: omit Appendix G entirely if plan is clean (no `unknown` markers, no audit gaps).

## Mode auto-detection heuristics

The `--mode=` flag picks one of `compact / standard / complex`. Auto-detection rules:

| Plan signals | Auto-detected mode |
|---|---|
| Plan < 200 lines AND no `M*` milestone tags AND no D0-D6 architecture markers | `compact` |
| Plan ≥ 200 lines AND no multi-milestone topology | `standard` |
| Plan has multi-milestone / multi-actor / runtime topology / resource scheduling | `complex` |

### Override

User can override with `/tldr-plan @PLAN.md --mode=compact` (or `standard` / `complex`). User override always wins over auto-detection.

### Fallback

If detection is uncertain (mixed signals — e.g., short plan with milestones, or long plan without architecture markers), default to `standard`.

### Per-mode behavior summary

(Full behavior table is in `references/output-layout.md` under "Mode-aware behavior".)

| Mode | Must include | May omit | Integrity check |
|---|---|---|---|
| `compact` | §0 Dashboard, §3 Scope (3.1+3.3 condensed), §7 Audit Checkpoints (gaps only), Appendix G if patches needed | Mermaid DAG, §3.4 if no staged delivery, §3.5, §4.2/4.3, §5 Decision Map can be table-only (no DAG), Appendix A-E | runs (cheap on small artifact) |
| `standard` (default) | current default minimal trace (all visible region §0-§7, Appendix A-D conditional) | extra topology Appendix F | runs |
| `complex` | all visible region + critical views + Appendix A-F + Appendix G if gaps + AC integrity + mermaid validation | none unless plan is genuinely silent | runs (mandatory) |

### Canonical anchor invariant (across all modes)

Even compact mode MUST preserve these section anchors (used by `check_tldr_integrity.py` and downstream `scope-triage`):

- `### 3.3 Acceptance Criteria`
- `## 5. Decision Map` (table form OK; DAG optional in compact)
- `#### 6.1 Evidence Required` when AC rows exist
- `### 3.4 Milestones` when staged delivery exists

Compact mode reduces *content density* (no Mermaid DAG, condensed prose, omittable Appendix A-E) but does NOT remove canonical section *anchors*. Integrity script treats absent optional sections as "not required" not "malformed", and skips Mermaid validation when no Mermaid blocks are present.
