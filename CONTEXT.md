# CONTEXT — orbit

<!-- This file is a ROLLING SNAPSHOT of *now*, not a log. git history is the changelog
     (`git log -p CONTEXT.md` recovers every past version), so pruning here loses nothing.
     Keep it small: Completed = last 1-2 sessions, Current State overwritten to present
     reality, Next Step = one item. Trim when Completed > ~6 bullets or file > ~80 lines.
     See workspace CLAUDE.md §6 "Keeping CONTEXT.md small". -->

Last touched: 2026-07-04

## Completed
- Day one shipped the triage loop: six numbered areas, `FILING.md` contract, `file-triage` skill, fixture gate (`tests/check_triage.py`) — PASS on a full agent-executed sort, FAIL verified on misfile/loss.

## Current State
- The design instance lives here (no corporate data); the populated instance will live on the work machine (structure by copy, skills via astra later).
- Gate: fixture sort → `python tests/check_triage.py <scratch>` — green 2026-07-04.
- No remote (work has no GitHub). Two OPEN walls await user confirmation (no-renumbering, no-app-ever — see IMPLEMENTATION_PLAN.md Open questions).

## Next Step
- User picks the next slice — `daily-note` skill is the top `next` candidate; also confirm the two OPEN walls.
