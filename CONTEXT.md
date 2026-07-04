# CONTEXT — orbit

<!-- This file is a ROLLING SNAPSHOT of *now*, not a log. git history is the changelog
     (`git log -p CONTEXT.md` recovers every past version), so pruning here loses nothing.
     Keep it small: Completed = last 1-2 sessions, Current State overwritten to present
     reality, Next Step = one item. Trim when Completed > ~6 bullets or file > ~80 lines.
     See workspace CLAUDE.md §6 "Keeping CONTEXT.md small". -->

Last touched: 2026-07-04

## Completed
- Day one, slices 1–2 — triage loop (areas + contract + `file-triage` + fixture gate) and restructure loop (`.gravity/` adoption, `filing/SPEC.md`, `area-architect`, structure lint); both gates PASS + FAIL-on-violation verified.
- Day one, slice 3+4 — `orbit-dashboard` skill, then its pro v2: KPI strip, cleanup candidates (>5 MB & 180d+ stale), md5 exact-duplicates + dupe-waste KPI, type donut, age profile, hunting guide in the SKILL; planted-junk detection verified, zero external refs, cp949-safe. Walls resolved: renumbering = deliberate migration; apps allowed, static HTML first.

## Current State
- The design instance lives here (no corporate data); the populated instance will live on the work machine (structure by copy, skills via astra later). All scripts are stdlib-only so they run at work too.
- Gate: `python tests/check_structure.py .` + fixture sort → `check_triage.py` — both green 2026-07-04. Dashboard regen: `python skills/orbit-dashboard/generate.py` (output gitignored).
- No remote (work has no GitHub).

## Next Step
- User picks the next slice — `daily-note` skill is the top `next` candidate (likely mints a `notes` domain via the gate).
