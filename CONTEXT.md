# CONTEXT — orbit

<!-- This file is a ROLLING SNAPSHOT of *now*, not a log. git history is the changelog
     (`git log -p CONTEXT.md` recovers every past version), so pruning here loses nothing.
     Keep it small: Completed = last 1-2 sessions, Current State overwritten to present
     reality, Next Step = one item. Trim when Completed > ~6 bullets or file > ~80 lines.
     See workspace CLAUDE.md §6 "Keeping CONTEXT.md small". -->

Last touched: 2026-07-12

## Completed
- **`memory-map` (the waypoint domain's face)** — depth-2 tiles colored by memory state (lit/stale/partial/dark/neutral), coverage KPI, dark-territory click-cards with manifest skeletons; verified five-state + click-cards in Chromium; absorbed both waypoint-dashboard slices. Eleven skills.
- **`orbit-janitor` (the weekly nag)** — five-check read-only sweep → day-dated chore report in `10-daily/`; verdicts OK/WARN/ACT, findings route to their owning skills; seventh wall `check_janitor.py` (self-driving; read-only proven by md5 inventory); PASS + FAIL-on-planted verified. Ten skills, seven walls.
- **Daily loop (notes domain, PR #6-in-#5)** — `.gravity/notes/SPEC.md` (four load-bearing sections, single-`(carried)` forward, never-overwrite, weekly assembly rules) + `daily-note` (`new_note.py`) + `weekly-report` (`generate.py`: done-by-day, dated decisions, carried, mtime-window per-area activity, sources cited) + the **sixth wall** `tests/check_notes.py` on `fixture-notes/` (self-driving, pinned week 2026-W24); PASS + FAIL-on-planted-violations verified. Nine skills, six walls, three domains.
- **Status review + identity razor (2026-07-12)** — verdict: *design-complete for v1, unproven on real files* (fixtures only; Deck never launched; 0 remote tags; fat `[Unreleased]`). Identity sharpened in CLAUDE.md: directory = database, agents = labor, walls = honesty; apps are viewers, contracts the product. Queue rebuilt around **First Light** → daily loop → janitor/cockpit; content-index, pre-usage theming, Tauri cut (razor). 
- **Deck celestial theme (PR #4, merged)** — burning-comet wordmark, CSS starfield, meteor burnout on observed removals + touchdown glow + inbox badge shockwave (scan-diff driven; Deck still never deletes; reduced-motion respected; smoke-tested).
- **Orbit Deck v1 (PR #3, merged)** — Electron shell: live area explorer (fs-watch), embedded `orbit-dashboard`, agent chat via `claude -p` stream-json (session resume, permission modes, tool-call timeline). Electron-free smoke test; Windows portable zip builds on CI (`build-orbit-deck`).

## Current State
- The design instance lives here (no corporate data); the populated instance will live on the work machine (structure by copy, skills via astra later). All scripts are stdlib-only so they run at work too.
- Gate — seven mechanical walls: `check_structure.py .` + fixture sort→`check_triage.py` + fixture scout→`check_scout.py` + `check_waypoint.py tests/fixture-waypoint` + fixture find→`check_find.py` + self-driving `check_notes.py` and `check_janitor.py` on their fixtures. Structure/waypoint/notes/janitor green 2026-07-12; find 2026-07-06; triage/scout 2026-07-04. After clone/copy, run `python .claude/setup-skills.py`.
- Eleven skills: the filing chain (`file-scout`→`file-triage`→`file-find`→`area-architect`→`orbit-dashboard`) + `locate` (waypoint navigation) + `memory-map` (its face) + `process-architect` (process guidelines) + the daily loop (`daily-note`→`weekly-report`, notes domain) + `orbit-janitor` (the weekly nag). Retrieval is two-layer by design; skills carry no filing/waypoint/notes rules — the SPECs do.
- Five generated, gitignored artifacts regenerate at work: `dashboard.html`, the per-area `README.md` cards, `*.process.html` guidelines, `waypoint-index.md`, and `memory-map.html`.
- Design instance only; `origin` → github.com/mostlytricks/orbit is PUBLIC — never commit corporate content (area wall enforces it). PRs #1–#5 merged; **v0.5.0 cut** (VERSION + CHANGELOG) — tag `v0.5.0` on main after merge (0 tags on the remote today; my tag pushes are rejected by the proxy).

## Next Step
- **First Light** (still the now-slice): run `build-orbit-deck` (Actions → Run workflow) and launch Deck; run scout+triage on the real Desktop/Downloads — and now also start the daily habit for real (`python skills/daily-note/new_note.py`, then Friday `python skills/weekly-report/generate.py`); tag `v0.5.0` + push tags (release already cut). Weekly: `python skills/orbit-janitor/sweep.py`. Report what breaks — next build slice is the Deck triage cockpit.
