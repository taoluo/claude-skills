# claude-skills

Reusable skills for Claude Code.

A skill is a self-contained directory with a `SKILL.md` (frontmatter +
instructions) and optional `references/`, `scripts/`, `assets/` subdirectories.
Drop a skill into `~/.claude/skills/<name>/` (user-level) or
`<repo>/.claude/skills/<name>/` (project-level) to make it available to Claude
Code, then invoke with `/<name>` or have the model trigger it via the skill's
`description` heuristics.

## What this is NOT

`tldr-plan` is **not** a plan validator. It does not approve or reject
the plan, emit severity findings, or perform the audit itself. It is
also not a one-shot summarizer that runs once and is done.

What it does: distill a raw implementation plan into a compact-first,
self-contained **TLDR artifact** — problem context, assumptions, scope
and out-of-scope, hard constraints, D0–D6 decision trace, acceptance
criteria, evidence requirements, stop conditions, and optional diagrams.

**Iterative by design.** Run it after each plan revision; the human
audits the TLDR, fixes gaps in the plan, re-runs the skill, audits
again. Handoff to a coding agent happens only after the human audit
passes — `tldr-plan` is the audit surface, not the handoff event.

```
plan v1 → tldr-plan v1 → human audit finds gaps
       → revise plan v2 → tldr-plan v2 → human audit
       → … → human audit passes → THEN hand the plan to a coding agent
```

**Single reader: the human auditor.** The implementation agent does NOT
read this artifact; the agent reads the original plan file directly.

If you want findings/severity, use a validator skill (see "vs related
skills" below). If you want forward-looking ADR/design-spec generation,
use a preflight skill. This skill sits upstream of all those: it
translates a long or ambiguous plan into a compact artifact a human can
audit before handing the plan to an agent.

## Skills

| Skill | Description |
|---|---|
| [`tldr-plan`](skills/tldr-plan/SKILL.md) | Compile a raw implementation plan into a compact-first, self-contained **TLDR artifact for human audit** — problem context, assumptions, scope, hard constraints, D0–D6 decision trace, critical diagrams, evidence, and stop conditions. **Iterative**: re-run after each plan revision until the human audit passes; only then hand the plan to a coding agent. Use when a plan is too long to audit directly or too vague to hand to an agent. |

## vs related skills

| If you need... | Use | Why |
|---|---|---|
| An independent audit report with findings/severity tags | [`b-mendoza/agent-skills@validate-implementation-plan`](https://skills.sh/b-mendoza/agent-skills/validate-implementation-plan) (1.4K installs) | It performs the audit and emits severity-tagged findings |
| ADR / design-spec generation from a feature idea | [`terrylica/cc-skills@implement-plan-preflight`](https://skills.sh/terrylica/cc-skills/implement-plan-preflight) | It creates forward-looking decision artifacts (MADR + spec) |
| Post-implementation drift check (work vs plan) | [`xiaolai/vmark@plan-audit`](https://skills.sh/xiaolai/vmark/plan-audit) | It compares git history against plan after implementation |
| Reframe an ambiguous high-stakes decision | [`shanezzzz/decision-clarity-skill@decision-clarity`](https://skills.sh/shanezzzz/decision-clarity-skill/decision-clarity) | It clarifies fuzzy decisions, not concrete plans |
| **A compact, traceable artifact for iterative human audit of a plan** before it ships to an agent | **`tldr-plan`** (this repo) | It distills a long or ambiguous plan into a self-contained TLDR — context, assumptions, constraints, D0–D6 trace, AC, evidence, stop conditions — that a human re-reads after each plan revision until the plan is ready to hand off (the agent reads the source plan, not this) |

## Repo layout

```
claude-skills/
  README.md
  LICENSE
  skills/
    <skill-name>/
      SKILL.md
      references/    # optional supporting docs
      scripts/       # optional helper scripts
      assets/        # optional binary assets
  docs/              # cross-skill authoring guides
  scripts/           # repo-level tooling (lint, package)
```

## Installing a skill

Recommended (via the open `skills` CLI from Vercel Labs — works against any
repo with this layout):

```bash
# user-level (available across all projects)
npx skills add https://github.com/taoluo/claude-skills --skill tldr-plan -g -y

# project-level (scoped to one repo, run from project root)
npx skills add https://github.com/taoluo/claude-skills --skill tldr-plan -y
```

Manual fallback:

```bash
git clone --depth 1 https://github.com/taoluo/claude-skills.git /tmp/cs
cp -R /tmp/cs/skills/tldr-plan ~/.claude/skills/   # or <repo>/.claude/skills/
rm -rf /tmp/cs
```

Then in Claude Code: `/tldr-plan <plan-file-path>` (or let the model
trigger it based on the skill's `description`).

## Authoring your own skill

See [`docs/authoring-guide.md`](docs/authoring-guide.md) for SKILL.md
structure, frontmatter gotchas (especially the colon-in-description
trap), description tuning for the CLI's trigger heuristic, and a
checklist for verifying before you publish.

## License

MIT. See [LICENSE](LICENSE).
