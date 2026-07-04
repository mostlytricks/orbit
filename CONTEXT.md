# CONTEXT — orbit

<!-- This file is a ROLLING SNAPSHOT of *now*, not a log. git history is the changelog
     (`git log -p CONTEXT.md` recovers every past version), so pruning here loses nothing.
     Keep it small: Completed = last 1-2 sessions, Current State overwritten to present
     reality, Next Step = one item. Trim when Completed > ~6 bullets or file > ~80 lines.
     See workspace CLAUDE.md §6 "Keeping CONTEXT.md small". -->

Last touched: 2026-07-05

## Completed
- **waypoint domain (birth)** — new `.gravity/waypoint/SPEC.md`: a deep directory opts in by holding a `_waypoint.md` manifest (YAML: purpose/keywords/types); `skills/locate/build_index.py` scans every manifest → one root `waypoint-index.md`; the `locate` skill answers "where is X?" from that index **without ever `ls`-ing payload** (the token-bomb it prevents). Walled by `tests/check_waypoint.py` + `tests/fixture-waypoint/` (PASS on 2 manifests; FAIL-on-missing-purpose verified). Index gitignored; wired all four indexes (Doc Map, router, spine, queue) + AGENTS. Names confirmed (`waypoint`/`_waypoint.md`). Shipped as **v0.4.0** (tagged, unpushed).
- **Area browsing cards** — `skills/area-architect/generate_cards.py` writes one `NN-*/README.md` per area from the SPEC areas table (single source, no drift), gitignored like `dashboard.html`; regeneration wired into the area-architect procedure. Shipped in **v0.2.0** (tagged, not pushed).

## Current State
- The design instance lives here (no corporate data); the populated instance will live on the work machine (structure by copy, skills via astra later). All scripts are stdlib-only so they run at work too.
- Gate — four mechanical walls: `check_structure.py .` + fixture sort→`check_triage.py` + fixture scout→`check_scout.py` + `check_waypoint.py tests/fixture-waypoint`. Waypoint verified green this session; triage/scout last green 2026-07-04. After clone/copy, run `python .claude/setup-skills.py`.
- Skills: the filing chain (`file-scout`→`file-triage`→`area-architect`→`orbit-dashboard`) **+ `locate`** (waypoint navigation). Note: a **`process-architect`** skill was added in a *parallel session* (another VS Code window) and shipped as **v0.3.0** — it's on disk, in AGENTS, and committed; I didn't build/verify it.
- Three generated, gitignored artifacts regenerate at work: `dashboard.html`, the per-area `README.md` cards, and `waypoint-index.md` (`skills/locate/build_index.py`).
- Design instance only; `origin` → github.com/mostlytricks/orbit is PUBLIC — never commit corporate content (area wall enforces it). `main` is at **v0.4.0** (waypoint), tags v0.1.0–v0.4.0 all present, VERSION==tag (no drift). Fixed the parallel session's gap by retro-tagging **v0.3.0** on its Release-0.3.0 commit. **Nothing pushed yet.**

## Next Step
- Push `main` + tags when ready: `git push origin main --follow-tags` (pushes v0.3.0/v0.4.0 too). Then pick the next slice: real-Desktop `file-scout` shakedown, or the `waypoint` per-directory dashboard view (feature-1 — `build_index.py` already computes the counts).
