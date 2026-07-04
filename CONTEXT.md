# CONTEXT — orbit

<!-- This file is a ROLLING SNAPSHOT of *now*, not a log. git history is the changelog
     (`git log -p CONTEXT.md` recovers every past version), so pruning here loses nothing.
     Keep it small: Completed = last 1-2 sessions, Current State overwritten to present
     reality, Next Step = one item. Trim when Completed > ~6 bullets or file > ~80 lines.
     See workspace CLAUDE.md §6 "Keeping CONTEXT.md small". -->

Last touched: 2026-07-04

## Completed
- **Intake loop** — new `file-scout` skill (the front door: gathers files from other dirs into `00-inbox/`) governed by a new "Intake" section in `filing/SPEC.md`: named sources tagged `dump`=move / `live`=copy, relevance filter, md5 dedup, `.orbit-provenance.jsonl`. Walled by `tests/check_scout.py` on `tests/fixture-sources/` (desktop+downloads dump, onedrive-sync live) — PASS + FAIL-on-violation (junk ingested / live moved / unrecorded) all verified. Wired into SPEC, AGENTS, CLAUDE router+test, plan.
- **Skills wiring + repo safety** — 4 skills discoverable by both agents via `.claude/setup-skills.py` junctions (single source stays in `skills/`) + AGENTS.md table; repo is **public** now, hardened `.gitignore` to deny-by-default inside areas (real content can never be committed), proven with planted files.

## Current State
- The design instance lives here (no corporate data); the populated instance will live on the work machine (structure by copy, skills via astra later). All scripts are stdlib-only so they run at work too.
- Gate (all green 2026-07-04): `python tests/check_structure.py .` + fixture sort → `check_triage.py` + fixture scout → `check_scout.py`. Dashboard regen: `python skills/orbit-dashboard/generate.py` (output gitignored). After clone/copy, run `python .claude/setup-skills.py` to re-wire Claude Code skill discovery.
- Four skills now: `file-scout` (intake) → `file-triage` (sort) → `area-architect` (restructure) → `orbit-dashboard` (monitor). All derive from `.gravity/filing/SPEC.md`; none carry filing rules.
- No remote (work has no GitHub).

## Next Step
- User picks the next slice. Candidates: exercise `file-scout` on the user's *real* Desktop/Downloads to shake out the intake rules; or the `daily-note` skill (likely mints a `notes` domain via the gate).
