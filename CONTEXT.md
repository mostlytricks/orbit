# CONTEXT — orbit

<!-- This file is a ROLLING SNAPSHOT of *now*, not a log. git history is the changelog
     (`git log -p CONTEXT.md` recovers every past version), so pruning here loses nothing.
     Keep it small: Completed = last 1-2 sessions, Current State overwritten to present
     reality, Next Step = one item. Trim when Completed > ~6 bullets or file > ~80 lines.
     See workspace CLAUDE.md §6 "Keeping CONTEXT.md small". -->

Last touched: 2026-07-12

## Completed
- **Daily loop (notes domain, PR #6)** — `.gravity/notes/SPEC.md` (four load-bearing sections, single-`(carried)` forward, never-overwrite, weekly assembly rules) + `daily-note` (`new_note.py`) + `weekly-report` (`generate.py`: done-by-day, dated decisions, carried, mtime-window per-area activity, sources cited) + the **sixth wall** `tests/check_notes.py` on `fixture-notes/` (self-driving, pinned week 2026-W24); PASS + FAIL-on-planted-violations verified. Nine skills, six walls, three domains.
- **Status review + identity razor (2026-07-12)** — verdict: *design-complete for v1, unproven on real files* (fixtures only; Deck never launched; 0 remote tags; fat `[Unreleased]`). Identity sharpened in CLAUDE.md: directory = database, agents = labor, walls = honesty; apps are viewers, contracts the product. Queue rebuilt around **First Light** → daily loop → janitor/cockpit; content-index, pre-usage theming, Tauri cut (razor). 
- **Deck celestial theme (PR #4, merged)** — burning-comet wordmark, CSS starfield, meteor burnout on observed removals + touchdown glow + inbox badge shockwave (scan-diff driven; Deck still never deletes; reduced-motion respected; smoke-tested).
- **Orbit Deck v1 (PR #3, merged)** — Electron shell: live area explorer (fs-watch), embedded `orbit-dashboard`, agent chat via `claude -p` stream-json (session resume, permission modes, tool-call timeline). Electron-free smoke test; Windows portable zip builds on CI (`build-orbit-deck`).
- **`file-find` + `locate` seam (PR #2, merged)** — two-layer retrieval: cheap index routing (locate) + file-level deep pass with miss diagnosis (file-find), walled by `check_find.py`.

## Current State
- The design instance lives here (no corporate data); the populated instance will live on the work machine (structure by copy, skills via astra later). All scripts are stdlib-only so they run at work too.
- Gate — five mechanical walls: `check_structure.py .` + fixture sort→`check_triage.py` + fixture scout→`check_scout.py` + `check_waypoint.py tests/fixture-waypoint` + fixture find→`check_find.py`. Structure/find green 2026-07-06; waypoint 2026-07-05; triage/scout 2026-07-04. After clone/copy, run `python .claude/setup-skills.py`.
- Seven skills: the filing chain (`file-scout`→`file-triage`→`file-find`→`area-architect`→`orbit-dashboard`) + `locate` (waypoint navigation) + `process-architect` (process guidelines). Retrieval is two-layer by design: `locate` routes to curated directories from the cheap index; `file-find` pinpoints files and diagnoses misses. Skills carry no filing/waypoint rules — the SPECs do.
- Four generated, gitignored artifacts regenerate at work: `dashboard.html`, the per-area `README.md` cards, `*.process.html` guidelines, and `waypoint-index.md`.
- Design instance only; `origin` → github.com/mostlytricks/orbit is PUBLIC — never commit corporate content (area wall enforces it). PRs #1–#4 merged; **0 tags on the remote** (local-only), `VERSION` 0.4.0 with three features in `[Unreleased]` — v0.5.0 pending First Light.

## Next Step
- **First Light** (still the now-slice): run `build-orbit-deck` (Actions → Run workflow) and launch Deck; run scout+triage on the real Desktop/Downloads — and now also start the daily habit for real (`python skills/daily-note/new_note.py`, then Friday `python skills/weekly-report/generate.py`); cut **v0.5.0** and push tags. Report what breaks — that feedback drives `orbit-janitor` next.
