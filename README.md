# claude-skills

Reusable skills for Claude Code.

A skill is a self-contained directory with a `SKILL.md` (frontmatter +
instructions) and optional `references/`, `scripts/`, `assets/` subdirectories.
Drop a skill into `~/.claude/skills/<name>/` (user-level) or
`<repo>/.claude/skills/<name>/` (project-level) to make it available to Claude
Code, then invoke with `/<name>` or have the model trigger it via the skill's
`description` heuristics.

## Skills

| Skill | Description |
|---|---|
| [`plan-viz`](skills/plan-viz/SKILL.md) | Translate an implementation plan into a compact-first hierarchical decision visualization document with Mermaid diagrams, audit checkpoints, and execution anchors. Use after planning, before implementation. |

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

```bash
# user-level (available across all projects)
cp -R skills/plan-viz ~/.claude/skills/

# project-level (scoped to one repo)
cp -R skills/plan-viz <your-repo>/.claude/skills/
```

Then in Claude Code: `/plan-viz <plan-file-path>` (or let the model trigger it
based on the skill's `description`).

## License

MIT. See [LICENSE](LICENSE).
