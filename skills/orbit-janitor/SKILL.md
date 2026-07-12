---
name: orbit-janitor
description: The weekly nag — a read-only sweep of an orbit tree (inbox age, duplicate waste, structure lint, stale waypoints, cleanup candidates) that drops one short day-dated chore report in 10-daily/. Every finding routes to the skill that fixes it; the janitor itself never moves or deletes anything. Use on Monday mornings, after big filing sessions, or whenever "how messy is it?" is asked.
---

# orbit-janitor

The dashboard answers when you *ask*; the janitor is the habit of asking. One command,
five checks, one short report filed as a chore record — so tree health shows up next to
your daily notes where you'll actually read it, and week-over-week reports become a
paper trail of whether the tree is getting better.

## Procedure

1. From the orbit root:
   ```bash
   python skills/orbit-janitor/sweep.py            # today's sweep
   python skills/orbit-janitor/sweep.py --force    # re-sweep the same day
   ```
   The report lands at `10-daily/YYYY/MM/YYYY-MM-DD-janitor-report.md` (a day-dated
   chore record — placement per the filing SPEC; derived artifact, `--force` to redo).
2. Read the verdicts top-down and **route each finding to its owner** — the janitor
   diagnoses, other skills treat:

   | Finding | Route to |
   |---|---|
   | Inbox `ACT`/`WARN` (files waiting) | `file-triage` |
   | Duplicates | `orbit-dashboard` (the hunt guide) — the *human* removes copies |
   | Structure lint `ACT` (contract broken) | `area-architect` + the SPEC change order |
   | Stale waypoint manifest / missing index | update the `_waypoint.md`, then `python skills/locate/build_index.py .` |
   | Cleanup candidates | `orbit-dashboard` review; keepers → deep archive (SPEC OPEN) |
3. When the user asks *you* to run the sweep, also read the report back and offer the
   top route ("inbox has 9 files, oldest 12d — triage now?"). One offer, not a lecture.

## Making it a schedule

orbit has no daemon, so recurrence is the host's job — pick one:
- **Work machine (Windows):** Task Scheduler, weekly Monday 08:30 →
  `python <orbit-root>\skills\orbit-janitor\sweep.py <orbit-root>`.
- **Anywhere with an agent:** a recurring agent task/routine that runs the sweep and
  reads the verdicts to you.
- **Deck (later lane):** a janitor button/badge is a natural fit; not built yet.

## Never

- Never move, rename, or delete anything — the janitor **reports**; humans and the
  filing skills act. (Same wall as the dashboard.)
- Never read payload content — mtime/size signals and md5 grouping only.
- Never hand-edit a janitor report to make it greener — fix the tree and `--force`
  a re-sweep; the report is derived truth, not a scoreboard to polish.
