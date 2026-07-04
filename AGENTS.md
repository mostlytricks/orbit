# Agent Instructions

Use `CLAUDE.md` as the canonical operating manual for this project.

This file exists as a Codex-compatible discovery shim only. Do not duplicate
project rules here; update `CLAUDE.md` when stable project instructions change.

For in-flight state, read `CONTEXT.md`.

## Skills

orbit ships three agent skills. Each is a folder under `skills/<name>/` with a
`SKILL.md` (the canonical, astra-shaped source). When a task matches one, **read
that skill's `SKILL.md` and follow its procedure** — the skills carry no filing
rules of their own; those live in `.gravity/filing/SPEC.md`.

| Skill | Use when | Path |
|---|---|---|
| `file-triage` | Sort a messy directory (usually `00-inbox/`) into the orbit areas — plan first, move never delete, leave unclassifiable files behind with a question. | `skills/file-triage/SKILL.md` |
| `area-architect` | Review/restructure the top-level area tree — add/rename/merge/retire an area per the lifecycle rules; push back on top-layer sprawl. | `skills/area-architect/SKILL.md` |
| `orbit-dashboard` | Generate the self-contained tree-health dashboard and hunt useless huge files (duplicates, big+stale). | `skills/orbit-dashboard/SKILL.md` |

(Claude Code discovers the same three under `.claude/skills/` via machine-local
junctions — recreate with `python .claude/setup-skills.py`. `skills/` is the one
source of truth; the junctions are gitignored.)
