# Skill authoring guide

Practical notes for authoring skills in this repo (or anywhere that
follows the `skills/<name>/SKILL.md` convention used by the Vercel-Labs
`skills` CLI).

## Minimum viable skill

A skill is a directory with one mandatory file:

```
skills/<skill-name>/
  SKILL.md            # required: frontmatter + instructions
  references/         # optional: supporting docs the skill loads
  scripts/            # optional: helper scripts the skill runs
  assets/             # optional: binary resources (templates, images)
```

The directory name SHOULD match the `name:` field in `SKILL.md`
frontmatter. The `skills` CLI uses the directory name as the package
identifier; Claude Code uses the `name:` field as the slash command.
Mismatched names create a confusing install path.

## SKILL.md structure

```markdown
---
name: <skill-name>
description: <one-paragraph trigger description>
---

# <Display name>

<body — instructions to Claude when this skill is invoked>
```

Both `name:` and `description:` are **required**. The `skills` CLI
rejects any SKILL.md missing either field with `No skills found. Skills
require a SKILL.md with name and description.`

## Frontmatter gotchas (read this before writing)

### 1. No unquoted colons in `description:`

The frontmatter is YAML, and YAML treats `:` as a key-value separator
on unquoted scalars. A description like:

```yaml
description: Compile an existing plan into a handoff brief for human audit and agent execution: problem context, assumptions, scope, ...
```

…parses as a malformed map and the `skills` CLI silently rejects the
skill. The fix is one of:

| Option | Example |
|---|---|
| **Em-dash instead of colon** (recommended) | `for human audit and agent execution — problem context, ...` |
| **Double-quote the value** | `description: "...for human audit and agent execution: problem context, ..."` |
| **Multi-line block scalar** | `description: \|\n  ...for human audit and agent execution: problem context, ...` |

The em-dash form is cleanest because it stays single-line and reads
naturally. Most existing skills in the registry use this convention.

### 2. Em-dashes and en-dashes are fine; smart quotes are not

UTF-8 punctuation in the description is fine (`—`, `–`, `…`). But avoid
typographic quotes (`"..."`, `'...'`) inside an unquoted YAML scalar —
they don't break YAML, but some terminals + JSON marshallers re-encode
them inconsistently. Stick to ASCII `"` and `'` if you need to quote
something inside the description.

### 3. The description IS the trigger heuristic

When a user doesn't type `/<skill-name>` explicitly, Claude decides
whether to invoke a skill by reading the `description:` field. This
makes description text more important than the body for discoverability.

Tune the description for the **trigger words** a user would actually
type:

- ✅ "Compile **an existing implementation plan** into a self-contained
  **pre-handoff audit brief** for a **human auditor** ... Use
  **after planning** and **before handing the plan to an agent**."
- ❌ "Translates raw input into a structured artifact." (vague; no
  trigger anchors)

Verify by running `npx skills find "<keywords>"` after publishing — if
your skill doesn't surface for the keywords your target user would type,
rewrite the description.

### 4. Keep `name:` short, kebab-case, and unambiguous

- `plan-handoff-brief` ✅
- `Plan_Handoff_Brief` ❌ (mixed case + underscores; doesn't match URL
  conventions)
- `pre-handoff` ❌ (too generic; collides with other skills)
- `plan-audit-brief` ⚠️ (fine syntactically, but the registry already
  has `xiaolai/vmark@plan-audit` — name-level collision causes
  discoverability problems)

Search the registry for adjacent names before you commit:

```bash
npx skills find <intended-name>
npx skills find <intended-keywords>
```

## SKILL.md body

The body runs after Claude decides to invoke the skill. Treat it as the
implementation. Useful sections to include:

- **What this is NOT** — disambiguate from adjacent skills near the top.
- **Invocation** — show the canonical command form (`/<skill-name> @file`).
- **Output file** — if the skill produces an artifact, name the path
  unambiguously (e.g. `docs/<skill-name>.md`). Match the path to the
  skill name to avoid orphaned outputs after a rename.
- **Workflow** — numbered steps Claude follows.
- **Self-validation** — any deterministic check the skill should run
  before declaring done (e.g. Mermaid block validation, output
  consistency check).

Skills that load `references/*.md` lazily (read-only) keep token usage
down vs. inlining everything. Skills that ship `scripts/*.py` should
document the exact invocation and expected runtime.

## Verifying before you publish

Run these checks locally before pushing:

```bash
# 1. SKILL.md frontmatter parses as valid YAML
node -e '
const fs=require("fs");
const txt=fs.readFileSync("skills/<name>/SKILL.md","utf8");
const m=txt.match(/^---\n([\s\S]*?)\n---/);
if(!m){console.log("NO FRONTMATTER");process.exit(1)}
console.log(m[1]);
'

# 2. The skills CLI discovers the skill from your local repo URL
#    (after pushing — uses git, not local files)
npx skills add https://github.com/<owner>/<repo> --list

# 3. The description shows the trigger words you intended
npx skills find "<keywords-a-user-would-type>"
```

Step 2 is the canonical test. If `--list` shows
`No skills found. Skills require a SKILL.md with name and description.`,
the YAML is malformed (most commonly: unquoted colon in description).

## Renaming a published skill

`git mv skills/<old-name> skills/<new-name>` preserves git history. Then:

1. Update `name:` in frontmatter.
2. Update H1 + body mentions (`replace_all`).
3. Update any output paths inside the skill that embed the name (e.g.
   `docs/<old>.md` → `docs/<new>.md`, `tmp/<old>-*` scratch dirs).
4. Update `references/*.md` headings.
5. Update repo `README.md` skill index + install commands.
6. Verify with `npx skills add <repo-url> --list`.
7. Single commit, push, then sync any local working copies (`~/.claude/skills/`
   or `<project>/.claude/skills/`) — those don't update automatically.

Renames are cheap on the repo side and free at the registry — but each
rename invalidates everyone's local install path. Avoid more than one
rename per skill once you have non-zero installs.

## Positioning against existing skills

Before publishing, run a market scan:

```bash
# What's in the same space?
npx skills find <your-domain-keywords>

# What does the dominant peer claim to do?
# (visit https://skills.sh/<owner>/<repo>/<skill> for each top hit)
```

Then add a `## vs related skills` table to your repo README. Do this
explicitly — listing the dominant peers with install counts and a
one-line "use peer X if you need Y" — instead of implicitly competing.
Users who land on your README via search are deciding between you and
the peers anyway; making the comparison explicit makes the decision
faster and the rejection of "wrong-fit" users cleaner.

## Lessons from this repo

- **2026-05-02**: Initial publish as `plan-viz`. Name implied
  visualization-centric tool; SKILL.md body says diagrams are
  secondary. Fixed via rename → `plan-audit-brief` →
  `plan-handoff-brief` after peer-comparison review surfaced collision
  with `xiaolai/vmark@plan-audit` (60 installs) and adjacency to
  `b-mendoza/agent-skills@validate-implementation-plan` (1.4K installs).
  Lesson: search the registry for adjacent names before publishing,
  and lead with the unique workflow position in the description.
- **2026-05-02**: Description colon broke YAML frontmatter; CLI
  silently rejected the skill ("No skills found"). Fixed by replacing
  `:` with em-dash. Lesson: the colon/comma punctuation rule is
  invisible until the CLI rejects you. Always run `npx skills add
  <url> --list` after pushing.
- **2026-05-02**: Description rolled back from "for human audit AND
  agent execution" → "for human audit, before agent handoff." A
  reviewer flagged that "agent execution" contradicted the SKILL.md
  body's load-bearing single-reader rule ("the implementation agent
  does NOT read this artifact"). Lesson: when expanding scope via
  description text, audit whether the body voice still matches. If the
  body says single-reader, the description must too — otherwise the
  rendered output reads awkwardly under either reader's hat. Ship
  description and body changes together, never just one.
