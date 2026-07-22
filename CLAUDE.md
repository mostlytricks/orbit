# orbit

**O**rganized **R**epository for **B**usiness & **IT** **T**asks — an IT manager's work OS where **the directory is the database, agents are the labor, and mechanical walls keep everyone honest**: one long-lived numbered tree (4–10 years of files) plus agent skills that do the daily work, starting with *"sort this messy directory into my structure."* Claude Code is the primary interface; the app surfaces — **generated static HTML** (the tree-health dashboard) and **Orbit Deck** (`app/`, a local Electron shell: tree explorer + embedded dashboard + agent panel) — are *viewers over the contracts, never the product*. Still no server anywhere. Feature razor: *does it make the tree more true, or the labor more automatic? If neither, cut it.*

> **alias:** `orbit`

> **gravity: v2.10** · _the version of the workspace gravity system this project adopted (root `VERSION` / `CHANGELOG.md`)._

> **Docs live in `.gravity/`.** This `CLAUDE.md` (identity, *how*) and `CONTEXT.md` (*now*) stay at the root and auto-load. Everything else is organized by subject domain under `.gravity/` — deliberately, because **orbit's root IS the product**: the top layer must show the areas, not a doc pile. One concern, one home — link, don't restate.

---

## Doc Map (`.gravity/`)

```
.gravity/
  IMPLEMENTATION_PLAN.md    # what/next — slice queue, locked decisions, domain status spine
  filing/  SPEC.md          # THE FILING CONTRACT — areas, decision procedure, lifecycle & budget
  waypoint/  SPEC.md        # curated-directory manifests + the cheap index — find deep dirs without scanning payload
  notes/  SPEC.md           # daily worklog & weekly report — note shape, carry-forward, weekly assembly
```

No `MISSION.html` yet (the why lives compactly in **Why** below); no per-domain `ARCHITECTURE.html` (nothing outgrows a file map). Recognized only when present.

## What to read before a change (router)

| If you're changing… | Read first |
|---|---|
| Where files go, area meanings, naming, sorting behavior | `.gravity/filing/SPEC.md` |
| How files get *into* the inbox from other dirs (move/copy, dedup, provenance) | `.gravity/filing/SPEC.md` → "Intake" |
| The area tree itself (add/rename/merge/retire an area) | `.gravity/filing/SPEC.md` → "Area lifecycle & top-layer budget" — then follow its change order |
| A skill's procedure (not filing rules — those live in the SPEC) | `skills/<name>/SKILL.md` |
| The dashboard's panels or look | `skills/orbit-dashboard/generate.py` (HTML+CSS inline; keep zero external resources) |
| A process guideline (approval chain / handoff pipeline) | Edit its JSON in `skills/process-architect/examples/`, then `python skills/process-architect/generate.py <def>.json`; the `*.process.html` is generated, never hand-edited |
| How a *file* is found (file-level retrieval, miss diagnosis; cheap *directory* routing is `locate`'s — row below) | `skills/file-find/SKILL.md` — lookup derives from the SPEC's decision procedure; if find and triage disagree, fix the SPEC, not the skill |
| A per-area browsing card (`NN-*/README.md`) | It's a *generated artifact* — edit `.gravity/filing/SPEC.md` (areas table), then `python skills/area-architect/generate_cards.py .`; never hand-edit a card |
| Finding a curated deep directory ("where is X?"), or the manifest/index format | `.gravity/waypoint/SPEC.md` (the `locate` skill executes it; never `ls` a big dir to find things) |
| The memory map (tile states, coverage math, detail cards) | `skills/memory-map/generate.py` — a *lens* over the waypoint SPEC; curation rules stay in `.gravity/waypoint/SPEC.md` |
| A daily worklog or weekly report (template, carry-forward, assembly rules) | `.gravity/notes/SPEC.md` — `daily-note`/`weekly-report` execute it; *where* notes live stays the filing SPEC's call |
| The desktop app (panes, agent bridge, packaging) | `app/README.md`, then `app/main.js` (IPC + claude/python spawns) and `app/renderer/` — the Windows zip builds on CI (`.github/workflows/build-deck.yml`), never here |
| What's next / slice queue | `.gravity/IMPLEMENTATION_PLAN.md` |

New feature? Run the domain gate in `.gravity/IMPLEMENTATION_PLAN.md`'s queue rules first — most features are slices under `filing` (or future domains), not new domains.

## Why (and what would betray it)

10 years of work files die in `misc/` folders and desktop dumps. orbit gives every file exactly one home and makes an agent do the filing. Non-goals (betrayals):

- **Never lose a file.** Skills move, never delete. A file that can't be classified stays in `00-inbox/` with a question — never guessed into a folder.
- **No corporate data in this repo.** This machine holds the *design* (structure, contract, skills, fake fixtures); the populated instance lives on the work machine. Nothing corporate is ever committed here.

## Stack

- **No runtime app.** Markdown + directory conventions + agent `SKILL.md`s.
- **Python 3.x (stdlib only)** for the mechanical gates (`tests/check_structure.py`, `tests/check_triage.py`, `tests/check_scout.py`, `tests/check_waypoint.py`, `tests/check_find.py`, `tests/check_notes.py`, `tests/check_janitor.py`) — no venv needed; they run on the work instance too.
- Skills are astra-shaped (folder with `SKILL.md`) so they can be published to the astra registry later.

## Run

No server. Claude Code opens here (or on the work machine's populated copy) and uses the skills; `.gravity/filing/SPEC.md` is the contract they follow.

```bash
python skills/orbit-dashboard/generate.py   # regenerate dashboard.html (gitignored output; open in browser)
python skills/memory-map/generate.py --open  # regenerate memory-map.html - the waypoint domain's face
cd app && npm ci && npm start               # Orbit Deck desktop shell (needs Electron download - not in this container)
cd app && npm test                          # Deck smoke: scanner + renderer UI in headless Chromium (works here)
```

## Test

```bash
python tests/check_structure.py .            # structure lint: tree ↔ contract, numbering, top-layer budget
# triage gate: copy the fixture, sort it per the file-triage skill, verify mechanically
cp -r tests/fixture-inbox <scratch>/00-inbox   # + empty area dirs
python tests/check_triage.py <scratch>
# intake gate: copy the fake source roots, scout them per file-scout, verify mechanically
cp -r tests/fixture-sources <scratch>/sources  # + empty 00-inbox/
python tests/check_scout.py <scratch>
# waypoint gate: validate curated-directory manifests on the fixture tree
python tests/check_waypoint.py tests/fixture-waypoint
# find gate: copy the planted tree, answer the queries per file-find, verify mechanically
cp -r tests/fixture-find/tree/. <scratch2>/    # then write <scratch2>/find-report.json
python tests/check_find.py <scratch2>
# notes gate: self-driving - runs new_note.py + weekly generate.py with pinned dates, then verifies
cp -r tests/fixture-notes/tree/. <scratch3>/
python tests/check_notes.py <scratch3>
# janitor gate: self-driving - stages lint infra, pins mtimes, runs sweep.py, verifies verdicts
cp -r tests/fixture-janitor/tree/. <scratch4>/
python tests/check_janitor.py <scratch4>
```

All seven are walls, not eyeballing. The filing *rules themselves* stay `[review]` (only you can say where your files belong).

## Conventions

- **Numbered areas, gaps of 10** (`10-daily`, `20-design`, …) — room to insert areas later without renumbering. Kebab-case, never spaces or dots (`1. Daily chore` is legal on Windows but hostile to CLI/git/agents).
- Dated files carry a `YYYY-MM-DD-` prefix; daily material nests `10-daily/YYYY/MM/`.
- Projects nest one folder per project: `40-projects/<project-slug>/`.
- Commit style: imperative one-liner.

## Constraints & Gotchas

- **Design here, deploy at work.** The work machine has no GitHub — the structure travels by copy (and skills via astra). Skills must use **relative paths only**; never hardcode a machine path.
- **Hybrid git:** the skeleton (docs, skills, contract, fixtures) is tracked; payload binaries (`pptx/xlsx/docx/pdf/zip/msg`, images) in the areas are `.gitignore`d — structure is versioned, content is not. `tests/` is whitelisted so fixture files with real extensions stay tracked.
- Area folders are kept alive by `.gitkeep` — don't delete them when an area is empty.
- Skills carry **no filing rules** — a skill that starts encoding "where files go" is the seam breaking.
- **Generated HTML must be self-contained** (no CDN, no web fonts — offline intranet) and ASCII-only on the console (Korean-Windows `cp949`).

## Entry Points

- `.gravity/filing/SPEC.md` — **the architectural seam**: the one contract that both the human filing habit and every sorting/restructuring skill derive from. Change filing behavior here, never inside a skill.
- `skills/<name>/SKILL.md` — the daily-work skills (`file-scout` ingests from the wild, `file-triage` sorts, `file-find` retrieves, `area-architect` restructures, `orbit-dashboard` monitors, `locate` finds curated dirs cheaply, `process-architect` documents how a process works, `daily-note` opens the day with carry-forward, `weekly-report` assembles the week, `orbit-janitor` sweeps and nags, `memory-map` shows what you still remember). This is the one canonical, astra-shaped source. Claude Code discovers them via machine-local junctions in `.claude/skills/` (gitignored; recreate with `python .claude/setup-skills.py`); Codex finds them through `AGENTS.md`. Never fork a second copy — always edit the file under `skills/`.
- `00-inbox/ … 50-policy/` — the six areas (meanings in the SPEC).
- `tests/` — fixture inbox + fixture source roots + fixture waypoint tree + fixture find-tree + fixture notes week + fixture janitor tree + the seven mechanical checkers (structure, triage, scout, waypoint, find, notes, janitor — the gate).

## Git

- Remote: `origin` → `github.com/mostlytricks/orbit` — **PUBLIC**. Only the *design instance* lives here (structure, skills, contract, fake fixtures); the populated work instance never gets this remote (and the work machine can't reach GitHub anyway).
- **Safety wall (why it's OK to be public):** `.gitignore` is deny-by-default *inside every area* — nothing under `00-inbox/ … 50-policy/` is ever committed except `.gitkeep`, so real work content can't leak regardless of file type. Adding an area means adding its two `.gitignore` lines (part of the SPEC change order). Never `git add -f` a file inside an area.
- Default branch: `main`.

---

<!--
This file is stable identity + the router — it changes rarely. For in-flight session
state (what was just done, what's broken, what's next), use CONTEXT.md.
-->
