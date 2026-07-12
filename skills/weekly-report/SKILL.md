---
name: weekly-report
description: Assemble the week's report from the daily worklogs plus a tree-activity scan — Done grouped by day, Decisions date-tagged, the last note's In-progress as "carried into next week", per-area files-touched table. The facts assemble mechanically; Highlights are then written FROM those facts, never invented. Use on Fridays or whenever "this week's report" is asked for.
---

# weekly-report

The Friday payoff of the daily habit: the report *writes itself* from what the week's
worklogs already recorded, plus what actually changed in the tree. Assembly rules live
in `.gravity/notes/SPEC.md` ("Weekly assembly"); this skill adds only the polish pass.

## Procedure

1. From the orbit root:
   ```bash
   python skills/weekly-report/generate.py                    # this ISO week
   python skills/weekly-report/generate.py --date 2026-07-08  # the week containing that day
   ```
   `REFUSED: ... already exists` → rerun with `--force` (the report is a regenerable
   assembly, unlike a daily note, so reassembling is safe — hand-written Highlights
   are the only loss; re-add them after).
2. Open the report. The mechanical sections are done: **Done this week** (by day),
   **Decisions** (date-tagged), **Carried into next week** (the last note's live
   In-progress), **Tree activity** (per-area files touched inside the week — mtime
   signals, payload never read), **Sources** (which notes were read).
3. **Write the Highlights** — 2–4 bullets max, each one traceable to a bullet below
   it. This is summarization, not authorship: if a highlight isn't backed by a Done,
   a Decision, or the activity table, it doesn't go in.
4. Read the result back for the two smells worth flagging to the human:
   - a **carried item aging across weeks** (appeared in last week's "Carried" too) —
     propose: project folder, or strike it;
   - **tree activity without Done items** (or the reverse) — the notes and the tree
     disagree; ask which one is lying.

## Never

- Never invent a highlight or reword a Done item into a bigger claim — the report
  quotes the week, it does not market it.
- Never read area file *contents* for the activity table — mtime/size signals only
  (same discipline as the dashboard).
- Never hand-edit the mechanical sections and call it done — fix the daily notes and
  reassemble with `--force`, or the notes and the report drift apart.
