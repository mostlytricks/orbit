# CONTEXT — orbit

<!-- This file is a ROLLING SNAPSHOT of *now*, not a log. git history is the changelog
     (`git log -p CONTEXT.md` recovers every past version), so pruning here loses nothing.
     Keep it small: Completed = last 1-2 sessions, Current State overwritten to present
     reality, Next Step = one item. Trim when Completed > ~6 bullets or file > ~80 lines.
     See workspace CLAUDE.md §6 "Keeping CONTEXT.md small". -->

Last touched: 2026-07-05

## Completed
- **Area browsing cards** — `skills/area-architect/generate_cards.py` writes one `NN-*/README.md` per area *from the SPEC areas table* (single source, no drift), so browsing the tree at work self-explains without an agent. Cards are a generated artifact: gitignored by the existing area wall (like `dashboard.html`), never hand-edited; regeneration is now the last step of the area-architect restructure procedure. Wired router row in CLAUDE.md + a `.gitignore` note; 6 cards generated and confirmed ignored by git.
- **Intake loop** (2026-07-04) — `file-scout` skill + SPEC "Intake" section (named sources `dump`=move/`live`=copy, relevance filter, md5 dedup, `.orbit-provenance.jsonl`), walled by `tests/check_scout.py`; PASS + FAIL-on-violation all verified.

## Current State
- The design instance lives here (no corporate data); the populated instance will live on the work machine (structure by copy, skills via astra later). All scripts are stdlib-only so they run at work too.
- Gate (all green 2026-07-04): `python tests/check_structure.py .` + fixture sort → `check_triage.py` + fixture scout → `check_scout.py`. Dashboard regen: `python skills/orbit-dashboard/generate.py` (output gitignored). After clone/copy, run `python .claude/setup-skills.py` to re-wire Claude Code skill discovery.
- Four skills: `file-scout` (intake) → `file-triage` (sort) → `area-architect` (restructure, now also emits area cards) → `orbit-dashboard` (monitor). All derive from `.gravity/filing/SPEC.md`; none carry filing rules.
- Two generated, gitignored artifacts regenerate at work: `dashboard.html` (`skills/orbit-dashboard/generate.py`) and the per-area `README.md` cards (`skills/area-architect/generate_cards.py`).
- Design instance only; the `origin` → github.com/mostlytricks/orbit remote is PUBLIC — never commit corporate content (the area wall enforces it).

## Next Step
- User picks the next slice. Candidates: exercise `file-scout` on the user's *real* Desktop/Downloads to shake out the intake rules; or the `daily-note` skill (likely mints a `notes` domain via the gate).
