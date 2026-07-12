# SPEC — notes (the daily/weekly note contract)

The compact agent-loadable contract for the `notes` domain: **what a daily worklog
and a weekly report look like**, **how unfinished work carries forward**, and **how
the weekly report assembles itself**. Skills (`daily-note`, `weekly-report`) execute
this contract and carry no rules of their own — change note behavior *here*.

**Where notes live is NOT this SPEC's call** — placement belongs to
`.gravity/filing/SPEC.md` (day-dated → `10-daily/YYYY/MM/`, week-scoped →
`10-daily/YYYY/`). This SPEC owns the note *content*: shape, carry-forward, assembly.

**Gate:**
```bash
cp -r tests/fixture-notes/tree/. <scratch>/
python tests/check_notes.py <scratch>    # self-driving: runs both scripts with pinned dates, then verifies
```

## Core Definition

A **daily worklog** is `10-daily/YYYY/MM/YYYY-MM-DD-daily-worklog.md` with exactly
these H2 sections, in this order (mechanically parseable — the weekly report and the
gate both rely on the headings verbatim):

```md
# Daily worklog - YYYY-MM-DD (Ddd)

## Done

## In progress

## Decisions

## Notes
```

A **weekly report** is `10-daily/YYYY/YYYY-Www-weekly-report.md` (ISO week), an
*assembled artifact*: its facts come from the week's daily worklogs and a tree-activity
scan — a human (or agent) may polish the Highlights, but never invents facts the
sources don't carry.

## Carry-forward (the labor rule)

- Creating today's note copies every non-empty bullet under **## In progress** from
  the *most recent* earlier worklog into today's **## In progress**, each prefixed
  `(carried)` once (never `(carried) (carried)`).
- An existing note is **never overwritten** — creation refuses if today's file exists
  (never lose a file; edit by hand instead).
- Done items never carry; Decisions never carry (they are records, not tasks).

## Weekly assembly

The report for ISO week `YYYY-Www` (Mon–Sun) is assembled from:

1. **Done this week** — every bullet under `## Done` from each of the week's worklogs,
   grouped by day, in date order.
2. **Decisions** — every bullet under `## Decisions` from the week, flat, date-tagged.
3. **Carried into next week** — the `## In progress` bullets of the week's *last*
   worklog (that is the live state; earlier days' lists are history).
4. **Tree activity** — files modified inside the areas during the week (mtime window,
   same one-pass scan discipline as the dashboard; count + size per area). Signals
   only — never payload content.
5. **Highlights** — left as a stub for the human/agent to fill *from the above*.

## Rules

- `[test:check_notes]` a created daily note lands at the filing-SPEC path, carries all
  four H2 sections verbatim, and carries forward the previous note's In-progress
  bullets with a single `(carried)` prefix.
- `[test:check_notes]` creation never overwrites: a second run for the same date fails
  loudly and leaves the existing note byte-identical.
- `[test:check_notes]` the weekly report lands at `10-daily/YYYY/YYYY-Www-weekly-report.md`,
  includes every Done bullet of the week grouped by day, every Decision, the last
  worklog's In-progress as "Carried into next week", and a tree-activity table that
  counts only files whose mtime falls inside the week.
- `[review]` Highlights are written from the assembled facts, never invented; the
  report cites which daily notes it read.
- `[review]` scripts are stdlib-only, relative-path safe, ASCII console output
  (they run on the Korean-Windows work instance).

## Behavioral Contract

- `[test:check_notes]` given the fixture week of worklogs, when `new_note.py` runs for
  the next morning → the new note exists with the four sections and the carried
  bullets; a re-run refuses and changes nothing.
- `[test:check_notes]` given the same fixture and two area files touched inside the
  week plus one outside, when `generate.py` runs for that week → the report contains
  the week's Done/Decisions/Carried content and a tree-activity table listing exactly
  the two inside-window files' areas.

## Gotchas

- Section headings are load-bearing: renaming `## In progress` breaks carry-forward
  *and* the gate. Rename here first (change order: contract → scripts → gate), or not
  at all.
- ISO weeks straddle years (a January note can belong to `YYYY-1-W53`). Both scripts
  derive the week from `date.isocalendar()` — never string-slice the year.

## OPEN

- OPEN: should the daily template gain a `## Meetings` section once real use shows the
  need? (Add here first; scripts + gate follow.)
- OPEN: weekly report enrichment — let the agent read the week's git log on the design
  instance for a "repo activity" section? (Work instance has no git; must stay optional.)

---

Skills executing this contract: `skills/daily-note/` (create + carry-forward),
`skills/weekly-report/` (assemble). Placement authority: `.gravity/filing/SPEC.md`.
