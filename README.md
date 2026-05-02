# claude-skills

Reusable skills for Claude Code.

A skill is a self-contained directory with a `SKILL.md` (frontmatter +
instructions) and optional `references/`, `scripts/`, `assets/` subdirectories.
Drop a skill into `~/.claude/skills/<name>/` (user-level) or
`<repo>/.claude/skills/<name>/` (project-level) to make it available to Claude
Code, then invoke with `/<name>` or have the model trigger it via the skill's
`description` heuristics.

## What this is NOT

`plan-handoff-brief` is **not** a plan validator. It does not approve or
reject the plan, emit severity findings, or perform the audit itself.

What it does: turn a plan into a self-contained handoff artifact —
problem context, assumptions, scope and out-of-scope, hard constraints,
D0–D6 decision trace, diagrams (secondary), evidence requirements,
stop conditions — so a human can audit it and an implementation agent
can execute it without drifting.

If you want findings/severity, use a validator skill (see "vs related
skills" below). If you want forward-looking ADR/design-spec generation,
use a preflight skill. This skill sits between those: it translates an
existing plan into the artifact the auditor and the agent both consume.

## Skills

| Skill | Description |
|---|---|
| [`plan-handoff-brief`](skills/plan-handoff-brief/SKILL.md) | Compile an existing implementation plan into a self-contained handoff brief for human audit and agent execution — problem context, assumptions, scope, hard constraints, D0–D6 decision trace, diagrams, evidence, and stop conditions. Use after planning, before handing work to an implementation agent. |

## vs related skills

| If you need... | Use | Why |
|---|---|---|
| An independent audit report with findings/severity tags | [`b-mendoza/agent-skills@validate-implementation-plan`](https://skills.sh/b-mendoza/agent-skills/validate-implementation-plan) (1.4K installs) | It performs the audit and emits severity-tagged findings |
| ADR / design-spec generation from a feature idea | [`terrylica/cc-skills@implement-plan-preflight`](https://skills.sh/terrylica/cc-skills/implement-plan-preflight) | It creates forward-looking decision artifacts (MADR + spec) |
| Post-implementation drift check (work vs plan) | [`xiaolai/vmark@plan-audit`](https://skills.sh/xiaolai/vmark/plan-audit) | It compares git history against plan after implementation |
| Reframe an ambiguous high-stakes decision | [`shanezzzz/decision-clarity-skill@decision-clarity`](https://skills.sh/shanezzzz/decision-clarity-skill/decision-clarity) | It clarifies fuzzy decisions, not concrete plans |
| **A handoff artifact before agent implementation** | **`plan-handoff-brief`** (this repo) | It translates an existing plan into a self-contained brief: context, assumptions, constraints, D0–D6 trace, evidence, stop conditions |

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
npx skills add https://github.com/taoluo/claude-skills --skill plan-handoff-brief -g -y

# project-level (scoped to one repo, run from project root)
npx skills add https://github.com/taoluo/claude-skills --skill plan-handoff-brief -y
```

Manual fallback:

```bash
git clone --depth 1 https://github.com/taoluo/claude-skills.git /tmp/cs
cp -R /tmp/cs/skills/plan-handoff-brief ~/.claude/skills/   # or <repo>/.claude/skills/
rm -rf /tmp/cs
```

Then in Claude Code: `/plan-handoff-brief <plan-file-path>` (or let the model
trigger it based on the skill's `description`).

## Authoring your own skill

See [`docs/authoring-guide.md`](docs/authoring-guide.md) for SKILL.md
structure, frontmatter gotchas (especially the colon-in-description
trap), description tuning for the CLI's trigger heuristic, and a
checklist for verifying before you publish.

## License

MIT. See [LICENSE](LICENSE).
