---
name: daily-note
description: Open today's daily worklog in an orbit tree — create it from the notes-SPEC template at its filing-SPEC home (10-daily/YYYY/MM/), carrying forward yesterday's unfinished "In progress" items automatically. Never overwrites an existing note. Use at the start of the workday, or whenever "today's note" is asked for.
---

# daily-note

Opens the day. One command creates today's worklog at its one home with the four
contract sections, and — the labor part — **carries forward** every unfinished
`## In progress` bullet from the most recent earlier note, prefixed `(carried)`.
The note *shape* and carry rule live in `.gravity/notes/SPEC.md`; the *placement*
comes from `.gravity/filing/SPEC.md`. This skill carries no rules of its own.

## Procedure

1. From the orbit root (design instance or the populated work copy):
   ```bash
   python skills/daily-note/new_note.py            # today
   python skills/daily-note/new_note.py --date 2026-07-14   # a specific day
   ```
2. If it prints `REFUSED: ... already exists` — good: the note is already open;
   today's work continues in the existing file. Never delete-and-recreate.
3. Open the note and work it through the day:
   - **Done** — completed items, one bullet each, written as facts.
   - **In progress** — the live task list; strike or move bullets to Done as they
     finish. Carried items keep their `(carried)` prefix so stale work is visible.
   - **Decisions** — anything decided today worth finding in year 8 (these feed the
     weekly report verbatim).
   - **Notes** — loose thoughts; triage-style filing questions go here too.
4. When asked to *add* to today's note (e.g. "log that the patch window moved"),
   append a bullet under the right section — never reorder or rename sections
   (headings are load-bearing for the weekly report and the gate).

## An item that keeps carrying

Three or more `(carried)` days in a row is a signal, not a nag: either it's a real
project (→ propose a `40-projects/<slug>/` via triage) or it's dead (→ the human
strikes it). Say so when you notice it; don't silently keep carrying.

## Never

- Never overwrite or regenerate an existing daily note — append to it.
- Never rename or reorder the four section headings (contract-breaking).
- Never file the note anywhere but its filing-SPEC home — if the path looks wrong,
  fix the SPEC discussion first, not the script output.
