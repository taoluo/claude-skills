# Mermaid Rules — full cookbook

## Purpose-bound diagram allowance

Use Mermaid diagrams when they improve auditability. Prefer focused diagrams over large diagrams.

**Allowed visible diagrams**:
- Decision DAG (§5)
- Architecture Integration View (§4.1)
- Runtime / Data Path View (§4.2)
- Physical Topology View (§4.3) — only when workflow Step 3a triggers it

Additional diagrams must go into visible appendices (Appendix F).

For subsystems with independent lifecycle, use `stateDiagram-v2` only when the lifecycle has at least 3 meaningful states (router admission, cache slot, port pool, scheduler queue, worker, connection). Place in `## Appendix F` by default; promote to Critical Views only when lifecycle correctness is one of the top audit risks. Skip trivial 2-state on/off lifecycles.

## Each diagram answers ONE audit question

If you cannot state the question in one sentence (e.g. "where does the new feature integrate into the existing architecture?", "how does request routing change after admission close?", "which logical roles share GPU 0?"), the diagram does not belong in the document. Put a one-line statement of the question immediately above each diagram, in italics or as a comment.

### Audit-question reference per view

| View | Audit question |
| ---- | -------------- |
| Architecture Integration | Where does the new feature attach to existing architecture, and what stays unchanged? |
| Runtime / Data Path | How does a critical path's behavior change? |
| Physical Topology | Which logical roles map to which physical resources, and where do they overlap? |
| Decision DAG | Which assumptions and constraints derive each decision? |
| Sub-system State Machine | Is the lifecycle complete and all transitions accounted for? |
| Wire-format Quick Reference | What does each new schema field mean, who produces it, who consumes it? |

## Style guide

- Use simple labels.
- All important arrows must be directional.
- Label important arrows when useful.
- Avoid decorative diagrams.
- Keep visible diagrams small enough to inspect at a glance.

## Mermaid syntax traps (cookbook)

These trip up Mermaid's parser. Common problems first:

- **Do not use lowercase `end` as a node label.** Reserved keyword in flowchart subgraphs.
- **Use short node IDs.** Long IDs are hard to wire.
- **Avoid punctuation-heavy node IDs.**
- **Put complex labels inside brackets or quotes.**
- **Do not use HTML tags** such as `<br/>`, `<sub>`, `<sup>`, or `<span>` inside any Mermaid diagram. Use plain text, shorter labels, separate nodes, or prose outside the diagram.
- **Avoid Markdown formatting inside diagram text.** Put detailed formatting in the prose below the diagram.
- **For multi-line labels**, prefer separate nodes, shorter aliases, or Mermaid-native quoted labels. Do not rely on HTML line breaks.

### `sequenceDiagram` — extra strict

- Participants, notes, and messages should be plain single-line text.
- **No `;` semicolons inside `Note over ...` text.** Mermaid's sequence parser treats `;` as a statement terminator and silently splits the note, producing confusing parse errors that point at the *next* line (e.g. `got NEWLINE` where it expected an arrow). Use `and`, `,`, or split into two notes.
- **Avoid free-standing `=` and other operator-looking glyphs in `Note` text** (e.g. `x = 3`). Prefer wording like `set x to 3`. The parser sometimes treats them as the start of a participant or arrow token, producing errors that appear to be on the *following* line.
- In arrow lines, the message after `:` is plain text, but parens, brackets, and `=` can still tokenize unexpectedly. Keep arrow messages short and descriptive (`request_cluster_gpus actor_train step3`) rather than literal call signatures (`request_cluster_gpus(actor_train, ACTOR_TRAINING, step=3)`).

### Debugging tip

When the parser reports an error on a line that looks fine, **check the *previous* `Note` / arrow message** — almost always the real culprit.

## Diagram syntax check (Step 10)

This validates only the **TLDR artifact's mermaid block syntax** — NOT the source plan. Run `scripts/validate_mermaid.sh <tldr-file>`.

Exit codes:

- **exit 0**: no Mermaid blocks present, OR all blocks compile
- **exit 1**: at least one Mermaid block fails to parse — script prints offending block path + parse error
- **exit 2**: dependency missing (`node` or `npx` unavailable) — clear message: `SKIP mermaid syntax check: npx unavailable; install Node.js for mermaid validation` — NOT a hard failure

If `npx` / `node` is unavailable, state that the mechanical check could not run and ask the user how to proceed instead of skipping the step silently.
