# orbit

**O**rganized **R**epository for **B**usiness & **IT** **T**asks — a personal work OS for an
IT manager: one long-lived, numbered directory that survives 4–10 years of files, plus
agent skills that do the daily filing labor. The first job it does: *"sort this messy
directory into my structure."*

Claude Code is the primary interface; the only app surface is a generated, self-contained
HTML dashboard — there is no server.

## The idea

Ten years of work files die in `misc/` folders and desktop dumps. orbit gives every file
**exactly one home** and makes an agent do the filing:

- **A numbered area tree** — six top-level areas (`00-inbox` … `50-policy`), in gaps of ten
  so new areas insert without renumbering. Top-layer width is capped on purpose; depth is
  where things live.
- **One filing contract** — [`.gravity/filing/SPEC.md`](.gravity/filing/SPEC.md) is the single
  source of truth for *where a file goes*. The human filing by hand and every skill follow
  the same tables.
- **Agent skills** — small, composable procedures that ingest, sort, restructure, monitor,
  and locate. They carry **no filing rules of their own** — they execute the contract.

Two walls that never bend: **never lose a file** (skills move, never delete; anything that
can't be classified waits in `00-inbox/` with a question), and **no corporate data in this
repo** (see *Design here, deploy at work* below).

## The tree

| Area | Holds (glance) |
|---|---|
| `00-inbox/` | the only drop zone — everything unsorted enters here and leaves via triage |
| `10-daily/` | recurring personal work: worklogs, weekly reports, checklists |
| `20-design/` | architecture & design: decisions, blueprints, standards |
| `30-operations/` | running systems: runbooks, incidents, maintenance records |
| `40-projects/` | one folder per named project |
| `50-policy/` | corporate / security / compliance documents |

*Authoritative meanings, the decision procedure, and the area lifecycle & budget rules live
in [`.gravity/filing/SPEC.md`](.gravity/filing/SPEC.md) — this table is only a glance.*

## How you use it

Open Claude Code at the orbit root and ask. The daily loop:

1. **Scout** — `file-scout` gathers scattered files (Desktop, Downloads, old dumps) into
   `00-inbox/` (move from dumps, copy from live sources; dedup + provenance, never deletes a
   source).
2. **Triage** — `file-triage` sorts the inbox into areas per the contract; anything ambiguous
   stays put with a question.
3. **Find** — two layers. `locate` answers "where's the 2026 design guideline?" from a cheap
   index of curated directories, *without* scanning giant folders. When the index can't
   answer — or you need the exact file — `file-find` runs the filing contract in reverse:
   it predicts the file's one home, searches narrow-to-wide, and diagnoses a miss
   (never ingested / misfiled / ambiguous contract) instead of shrugging.
4. **Journal** — `daily-note` opens today's worklog (unfinished items carry forward
   automatically); on Friday `weekly-report` assembles the week from those notes plus what
   actually changed in the tree — you only write the highlights.
5. **Monitor** — `orbit-dashboard` renders a tree-health page (cleanup candidates, duplicates,
   size and age), and `orbit-janitor` runs the weekly nag — a read-only sweep filed as a
   chore record next to your daily notes, each finding routed to the skill that fixes it:

   ```bash
   python skills/orbit-dashboard/generate.py   # -> dashboard.html (open in a browser)
   ```

Restructuring the areas themselves is `area-architect`; documenting a business process is
`process-architect`. All eleven skills live under `skills/<name>/SKILL.md` and are discovered by
Claude Code and Codex alike.

## Orbit Deck (the desktop app)

When a terminal isn't enough, [`app/`](app/README.md) is a local Electron shell — no
server, no installer: a live **area explorer**, the **tree-health dashboard** embedded and
regenerated on demand, and an **agent panel** that runs the Claude Code CLI against your
root with tool calls streamed as a working-process timeline. The Windows portable zip
builds via the `build-orbit-deck` GitHub Actions workflow.

## Design here, deploy at work

This public repo is the **design instance** — structure, skills, the contract, and *fake*
fixtures. The populated instance lives on a work machine and never gets this remote.

It is safe to be public because of a **deny-by-default safety wall**: `.gitignore` commits
nothing inside a numbered area except its `.gitkeep` keepalive, so real work content cannot
leak regardless of file type. Structure is versioned; content never is. Skills use relative
paths only, so the structure travels by copy.

## Where to look

| For… | Read |
|---|---|
| What orbit is, stack, run/test, gotchas (the agent's manual) | [`CLAUDE.md`](CLAUDE.md) |
| Where files go — the filing contract | [`.gravity/filing/SPEC.md`](.gravity/filing/SPEC.md) |
| Finding curated deep directories cheaply | [`.gravity/waypoint/SPEC.md`](.gravity/waypoint/SPEC.md) |
| What's next — the slice queue | [`.gravity/IMPLEMENTATION_PLAN.md`](.gravity/IMPLEMENTATION_PLAN.md) |
| Current state + the single next step | [`CONTEXT.md`](CONTEXT.md) |

## Status

**v0.4.x** — three domains (`filing`, `waypoint`, `notes`) and eleven skills, with every mechanical gate a
real wall (`tests/check_*.py`, all stdlib-only so they run on the work instance too). Built on
the *gravity* workspace doc-system (v1.4). Full history in [`CHANGELOG.md`](CHANGELOG.md).
