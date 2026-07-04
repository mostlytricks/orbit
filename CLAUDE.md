# orbit

**O**rganized **R**epository for **B**usiness & **IT** **T**asks — an IT manager's personal work OS: one long-lived numbered directory architecture (4–10 years of files) plus agent skills that do the daily labor, starting with *"sort this messy directory into my structure."* Claude Code is the interface; there is no app.

> **alias:** `orbit`

---

## Docs in this project

- **CONTEXT.md** — start here: current state + the single next step. *Now.*
- **CLAUDE.md** (this file) — stable identity: what orbit is, conventions, gotchas. *How.*
- **FILING.md** — **the filing contract**: what each area means + the decision procedure. An agent loads this before sorting anything; a human reads it to file by hand. One contract, both audiences.
- **IMPLEMENTATION_PLAN.md** — slice queue & locked decisions. *What's next* (may lag; CONTEXT wins on "now").

## Why (and what would betray it)

10 years of work files die in `misc/` folders and desktop dumps. orbit gives every file exactly one home and makes an agent do the filing. Non-goals (betrayals):

- **Never lose a file.** Skills move, never delete. A file that can't be classified stays in `00-inbox/` with a question — never guessed into a folder.
- **No corporate data in this repo.** This machine holds the *design* (structure, contract, skills, fake fixtures); the populated instance lives on the work machine. Nothing corporate is ever committed here.

## Stack

- **No runtime app.** Markdown + directory conventions + agent `SKILL.md`s.
- **Python 3.x (stdlib only)** for the mechanical gate (`tests/check_triage.py`) — no venv needed.
- Skills are astra-shaped (folder with `SKILL.md`) so they can be published to the astra registry later.

## Run

There is nothing to run. Claude Code opens here (or on the work machine's populated copy) and uses the skills; `FILING.md` is the contract they follow.

## Test

```bash
# the gate: copy the fixture, sort it per the skill, verify mechanically
cp -r tests/fixture-inbox <scratch>/inbox   # then run the file-triage skill on it
python tests/check_triage.py <scratch>      # PASS = every file at its expected home, none lost
```

`tests/check_triage.py` holds the expected mapping for the fixture — a wall, not eyeballing. The filing *rules themselves* stay `[review]` (only you can say where your files belong).

## Conventions

- **Numbered areas, gaps of 10** (`10-daily`, `20-design`, …) — room to insert areas later without renumbering. Kebab-case, never spaces or dots (`1. Daily chore` is legal on Windows but hostile to CLI/git/agents).
- Dated files carry a `YYYY-MM-DD-` prefix; daily material nests `10-daily/YYYY/MM/`.
- Projects nest one folder per project: `40-projects/<project-slug>/`.
- Commit style: imperative one-liner.

## Constraints & Gotchas

- **Design here, deploy at work.** The work machine has no GitHub — the structure travels by copy (and skills via astra). Skills must use **relative paths only**; never hardcode a machine path.
- **Hybrid git:** the skeleton (docs, skills, contract, fixtures) is tracked; payload binaries (`pptx/xlsx/docx/pdf/zip/msg`, images) in the areas are `.gitignore`d — structure is versioned, content is not. `tests/` is whitelisted so fixture files with real extensions stay tracked.
- Area folders are kept alive by `.gitkeep` — don't delete them when an area is empty.

## Entry Points

- `FILING.md` — **the architectural seam**: the one contract that both the human filing habit and every sorting skill derive from. Change filing behavior here, never inside a skill.
- `skills/<name>/SKILL.md` — the daily-work skills (`file-triage` first).
- `00-inbox/ … 50-policy/` — the six areas (see FILING.md for meanings).
- `tests/` — fixture inbox + mechanical checker (the gate).

## Git

- Remote: none (local only — the work machine can't reach GitHub anyway).
- Default branch: `master`.

---

<!--
This file is stable identity — it changes rarely. For in-flight session state
(what was just done, what's broken, what's next), use CONTEXT.md.
-->
