# CONTEXT — orbit

<!-- This file is a ROLLING SNAPSHOT of *now*, not a log. git history is the changelog
     (`git log -p CONTEXT.md` recovers every past version), so pruning here loses nothing.
     Keep it small: Completed = last 1-2 sessions, Current State overwritten to present
     reality, Next Step = one item. Trim when Completed > ~6 bullets or file > ~80 lines.
     See workspace CLAUDE.md §6 "Keeping CONTEXT.md small". -->

Last touched: 2026-07-04

## Completed
- Day one, slice 1 — triage loop: six numbered areas, filing contract, `file-triage` skill, fixture gate (12 files, PASS + FAIL-on-violation verified).
- Day one, slice 2 — restructure loop: adopted `.gravity/` (root CLAUDE.md is the router; contract now `.gravity/filing/SPEC.md` with enforcement-tagged rules + area lifecycle & top-layer budget), `area-architect` skill, `tests/check_structure.py` structure lint (PASS on repo; FAIL verified on rogue dir + missing area).

## Current State
- The design instance lives here (no corporate data); the populated instance will live on the work machine (structure by copy, skills via astra later). Both checkers are stdlib-only so they run at work too.
- Gate: `python tests/check_structure.py .` + fixture sort → `check_triage.py` — both green 2026-07-04.
- No remote (work has no GitHub). Two OPEN walls await user confirmation (no-renumbering permanence, no-app-ever — see `.gravity/IMPLEMENTATION_PLAN.md` Open questions).

## Next Step
- User picks the next slice — `daily-note` skill is the top `next` candidate (likely mints a `notes` domain via the gate); also confirm the two OPEN walls.
