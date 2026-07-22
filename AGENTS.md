# Agent Instructions

**`CLAUDE.md` is the canonical operating manual for this project.** Everything in this file is *routing*, not rules — do not duplicate project rules here; when stable instructions change, change `CLAUDE.md`.

## Required reading protocol — do this, in this order

1. **Before any work:** read `CLAUDE.md` (identity, stack, run/test commands, the doc router) **and** `CONTEXT.md` (current state + the single next step). Do not start without both.
2. **If a `.gravity/` directory exists:** read `.gravity/GRAVITY.md` — the protocol card explaining every doc kind under `.gravity/` and how to navigate them. Required before touching anything inside `.gravity/`.
3. **Before changing code in a domain:** read that domain's `.gravity/<domain>/SPEC.md` — the change contract. Find its path in `CLAUDE.md`'s Doc Map / router table; never guess paths.
4. **Before any cross-service or boundary change** (API shape, generated types, auth/session, ports, shared env, queues, data access): read `.gravity/integration/SPEC.md` first (or `CONTRACT.md` if that's what exists), then the affected domain SPECs.
5. **Before ending the session:** update `CONTEXT.md` (Completed / Current State / Next Step). A session that doesn't update it is incomplete.

## If instructions conflict

1. Higher-priority system/developer instructions.
2. Explicit user instructions in the current conversation.
3. This project's `CLAUDE.md` / `CONTEXT.md` (and, under `.gravity/`, the protocol card + domain SPECs).

## Skills

orbit ships eleven agent skills. Each is a folder under `skills/<name>/` with a
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
| `orbit-janitor` | Weekly nag — read-only sweep (inbox age, dupe waste, structure lint, stale waypoints, cleanup candidates) filed as a day-dated chore report in `10-daily/`; every finding routes to the skill that fixes it. Walled by `tests/check_janitor.py`. | `skills/orbit-janitor/SKILL.md` |
| `memory-map` | Render the tree colored by *memory*: curated-fresh tiles lit with their manifest's purpose, stale ones amber, big uncurated dirs as dark territory (click-card carries a `_waypoint.md` skeleton). Read-only lens over the waypoint SPEC; `memory-map.html` is gitignored generated output. | `skills/memory-map/SKILL.md` |

(Claude Code discovers the same skills under `.claude/skills/` via machine-local
junctions — recreate with `python .claude/setup-skills.py`. `skills/` is the one
source of truth; the junctions are gitignored.)
