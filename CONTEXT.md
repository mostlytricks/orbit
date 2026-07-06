# CONTEXT — orbit

<!-- This file is a ROLLING SNAPSHOT of *now*, not a log. git history is the changelog
     (`git log -p CONTEXT.md` recovers every past version), so pruning here loses nothing.
     Keep it small: Completed = last 1-2 sessions, Current State overwritten to present
     reality, Next Step = one item. Trim when Completed > ~6 bullets or file > ~80 lines.
     See workspace CLAUDE.md §6 "Keeping CONTEXT.md small". -->

Last touched: 2026-07-05

## Completed
- **`file-find` skill (retrieval loop closed)** — the mission's "still findable" half now has a skill *and* a wall: predict-the-home via the SPEC decision procedure, narrow-to-wide search, ranked candidates with evidence, miss-as-diagnosis (never-ingested / misfiled / ambiguous-contract). Gate: `tests/fixture-find/` planted tree + 7 queries + `check_find.py` (exact hits, no silent pick, miss diagnosis, misfile flag, md5 read-only wall); PASS + FAIL-on-planted-violations verified.
- **`process-architect` skill + release 0.3.0** — first non-filing skill: documents *how a process works* (approval chains / handoff pipelines) as one self-contained HTML guideline. Interview procedure + health rubric in `SKILL.md`; `generate.py` renders a tracked JSON definition → disposable gitignored `*.process.html` (data-in/HTML-out like the dashboard). Ships two sample defs (fake purchase-order chain; orbit's own file-fix process). Wired into `AGENTS.md`, CLAUDE.md router + entry points, `.gitignore`, plan. `VERSION` 0.2.0→0.3.0, `CHANGELOG` entry. Out as **PR #1**.
- **Area browsing cards** — `skills/area-architect/generate_cards.py` writes one `NN-*/README.md` per area *from the SPEC areas table* (single source, no drift). Generated artifact: gitignored by the area wall (like `dashboard.html`), never hand-edited; regeneration is the last step of the area-architect restructure procedure.

## Current State
- The design instance lives here (no corporate data); the populated instance will live on the work machine (structure by copy, skills via astra later). All scripts are stdlib-only so they run at work too.
- Gate (all green 2026-07-06): `python tests/check_structure.py .` + fixture sort → `check_triage.py` + fixture scout → `check_scout.py` + fixture find → `check_find.py`. Dashboard regen: `python skills/orbit-dashboard/generate.py` (output gitignored). After clone/copy, run `python .claude/setup-skills.py` to re-wire Claude Code skill discovery.
- Six skills: five filing-side — `file-scout` (intake) → `file-triage` (sort) → `file-find` (retrieve) → `area-architect` (restructure, also emits area cards) → `orbit-dashboard` (monitor); plus `process-architect` (documents how a process works). The filing skills derive from `.gravity/filing/SPEC.md`; none carry filing rules.
- Three generated, gitignored artifacts regenerate at work: `dashboard.html` (`skills/orbit-dashboard/generate.py`), the per-area `README.md` cards (`skills/area-architect/generate_cards.py`), and `*.process.html` process guidelines (`skills/process-architect/generate.py` from a JSON def).
- Design instance only; the `origin` → github.com/mostlytricks/orbit remote is PUBLIC — never commit corporate content (the area wall enforces it).

## Next Step
- Merge **PR #1** (0.3.0 + `file-find` complete as unreleased), tag `v0.3.0` on `main`. Then user picks the next slice — candidates: `daily-note` (queued `next`), run `process-architect` on a real process, or exercise `file-scout`/`file-find` on the real work tree.
