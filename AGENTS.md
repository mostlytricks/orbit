# Agent Instructions

Use `CLAUDE.md` as the canonical operating manual for this project.

This file exists as a Codex-compatible discovery shim only. Do not duplicate
project rules here; update `CLAUDE.md` when stable project instructions change.

For in-flight state, read `CONTEXT.md`.

## Skills

orbit ships nine agent skills. Each is a folder under `skills/<name>/` with a
`SKILL.md` (the canonical, astra-shaped source). When a task matches one, **read
that skill's `SKILL.md` and follow its procedure** — the skills carry no filing
rules of their own; those live in `.gravity/filing/SPEC.md`.

| Skill | Use when | Path |
|---|---|---|
| `file-scout` | Gather work files from *other* directories (Desktop, Downloads, old dumps) into `00-inbox/` — scan named source roots read-only, move from dumps / copy from live sources, dedup, record provenance, never delete a source. The front door before `file-triage`. | `skills/file-scout/SKILL.md` |
| `file-triage` | Sort a messy directory (usually `00-inbox/`) into the orbit areas — plan first, move never delete, leave unclassifiable files behind with a question. | `skills/file-triage/SKILL.md` |
| `area-architect` | Review/restructure the top-level area tree — add/rename/merge/retire an area per the lifecycle rules; push back on top-layer sprawl. | `skills/area-architect/SKILL.md` |
| `orbit-dashboard` | Generate the self-contained tree-health dashboard and hunt useless huge files (duplicates, big+stale). | `skills/orbit-dashboard/SKILL.md` |
| `locate` | Answer "where is X?" over a deep tree cheaply — read the generated waypoint index of curated directories and route to the right path *without* listing payload. Governed by `.gravity/waypoint/SPEC.md`. | `skills/locate/SKILL.md` |
| `process-architect` | Document *how a process works* — interview the user to define a healthy approval chain or handoff pipeline, pressure-test it against a health rubric, then render it as a self-contained HTML guideline from a JSON definition. Not a filing skill; carries no filing rules. | `skills/process-architect/SKILL.md` |
| `file-find` | Answer "where is X?" — predict the file's home by running the SPEC decision procedure forward over the ask, search narrow-to-wide, present ranked candidates with evidence; a miss becomes a filing diagnosis (never-ingested / misfiled / ambiguous contract). Read-only; walled by `tests/check_find.py`. | `skills/file-find/SKILL.md` |
| `daily-note` | Open today's worklog — create it at its filing-SPEC home with the notes-SPEC template, carrying forward yesterday's unfinished In-progress items (`(carried)`, once). Never overwrites. Walled by `tests/check_notes.py`. | `skills/daily-note/SKILL.md` |
| `weekly-report` | Assemble the week's report from the daily worklogs + a tree-activity scan (done-by-day, dated decisions, carried items, per-area files touched). Highlights are written *from* the facts, never invented. Walled by `tests/check_notes.py`. | `skills/weekly-report/SKILL.md` |

(Claude Code discovers the same skills under `.claude/skills/` via machine-local
junctions — recreate with `python .claude/setup-skills.py`. `skills/` is the one
source of truth; the junctions are gitignored.)
