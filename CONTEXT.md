# CONTEXT — orbit

<!-- This file is a ROLLING SNAPSHOT of *now*, not a log. git history is the changelog
     (`git log -p CONTEXT.md` recovers every past version), so pruning here loses nothing.
     Keep it small: Completed = last 1-2 sessions, Current State overwritten to present
     reality, Next Step = one item. Trim when Completed > ~6 bullets or file > ~80 lines.
     See workspace CLAUDE.md §6 "Keeping CONTEXT.md small". -->

Last touched: 2026-07-08

## Completed
- **Orbit Deck v1 (`app/`)** — Electron desktop shell answering "I can't *see* the tree from a terminal": live area explorer (fs-watch), embedded `orbit-dashboard` (regen via python), agent chat panel spawning `claude -p` stream-json (session resume; plan/acceptEdits/bypass permission modes; tool calls as a working-process timeline). Smoke-tested Electron-free (`app/tests/deck-smoke.js` — scanner on the find fixture + real-Chromium UI test). Windows portable zip builds on CI (`build-orbit-deck` workflow) since this container can't download Electron binaries. Out as **PR #3**.
- **`file-find` skill + seam with `locate`** — file-level retrieval, walled: predict-the-home via the SPEC decision procedure run forward, narrow-to-wide search (waypoint index consulted first), ranked candidates with evidence, miss-as-diagnosis (never-ingested / misfiled / ambiguous-contract). Gate: `tests/fixture-find/` planted tree + 7 queries + `check_find.py`; PASS + FAIL-on-planted-violations verified. Cross-referenced with `locate` in both SKILLs: locate = cheap directory routing from the index, file-find = file-level deep pass + diagnosis. Rebased onto post-waypoint `main`; out as **PR #2**.
- **waypoint domain (birth)** — `.gravity/waypoint/SPEC.md`: a deep directory opts in via `_waypoint.md` (purpose/keywords/types); `skills/locate/build_index.py` → one root `waypoint-index.md`; `locate` answers "where is X?" from the index without ever `ls`-ing payload. Walled by `tests/check_waypoint.py` + fixture. Shipped as **v0.4.0**; README added as **v0.4.1**.
- **`process-architect` skill** — interviews a process into health (rubric), renders JSON → self-contained HTML guideline. Shipped as **v0.3.0** via PR #1 (merged).

## Current State
- The design instance lives here (no corporate data); the populated instance will live on the work machine (structure by copy, skills via astra later). All scripts are stdlib-only so they run at work too.
- Gate — five mechanical walls: `check_structure.py .` + fixture sort→`check_triage.py` + fixture scout→`check_scout.py` + `check_waypoint.py tests/fixture-waypoint` + fixture find→`check_find.py`. Structure/find green 2026-07-06; waypoint 2026-07-05; triage/scout 2026-07-04. After clone/copy, run `python .claude/setup-skills.py`.
- Seven skills: the filing chain (`file-scout`→`file-triage`→`file-find`→`area-architect`→`orbit-dashboard`) + `locate` (waypoint navigation) + `process-architect` (process guidelines). Retrieval is two-layer by design: `locate` routes to curated directories from the cheap index; `file-find` pinpoints files and diagnoses misses. Skills carry no filing/waypoint rules — the SPECs do.
- Four generated, gitignored artifacts regenerate at work: `dashboard.html`, the per-area `README.md` cards, `*.process.html` guidelines, and `waypoint-index.md`.
- Design instance only; `origin` → github.com/mostlytricks/orbit is PUBLIC — never commit corporate content (area wall enforces it). `main` is at **v0.4.1**, pushed with tags; PR #1 merged.

## Next Step
- Merge **PR #3** (Orbit Deck), run the `build-orbit-deck` workflow, download the `OrbitDeck-win-portable` artifact and try it on the work machine (needs Python on PATH; Claude Code CLI only for the agent pane). Cut `[Unreleased]` (file-find + Deck) as **v0.5.0** when satisfied. Then: `daily-note`, waypoint per-dir dashboard, or real-Desktop scout shakedown.
