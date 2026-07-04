# orbit — Implementation plan & resume sheet

> One-line working scenario: a messy directory goes in, every file lands in its one home in the numbered tree (or stays in inbox with a question), and ten years later it's still findable.
> Branch `master` · last updated 2026-07-04.

## Status right now

First slice shipped 2026-07-04: the six-area tree, `FILING.md` (the contract), the `file-triage` skill, and the fixture gate (`tests/check_triage.py` — 12 files, PASS + verified it fails on misfile/loss). Next slice: user's pick — see queue.

## Slice queue

Rolling lanes (growing project — skills accrete, phases would be fake). Rules:
- **Exactly one slice in `now`**; `next` ordered and short; `later` is an unordered pool.
- A shipped slice leaves the queue; its detail survives in git history.
- New slices enter via `/interview orbit <feature>`.

| Lane | Slice | Status |
|---|---|---|
| now | OPEN: user picks the next slice (candidates below) | ○ |
| next | `daily-note` skill — templated daily worklog auto-placed in `10-daily/YYYY/MM/` | ○ |
| later | `weekly-report` skill — assemble the week's report from daily notes | ○ |
| later | Publish orbit skills to astra (`astra-publish` loop — dogfood both projects) | ○ |
| later | Per-area README.md files for human browsing at work | ○ |
| later | Deep-archive procedure for old years (see FILING.md OPEN) | ○ |

Shipped (details in git history): **triage loop** — tree + FILING.md + file-triage skill + fixture gate (2026-07-04).

## Locked decisions

- **Numbered areas, gaps of 10, kebab-case** — insertable later without renumbering; CLI/git/agent-safe names.
- **FILING.md is the seam** — all sorting behavior lives in the contract; skills contain no filing rules of their own.
- **Never lose a file** — moves only, unclear stays in inbox with a question (mission wall).
- **Design here, deploy at work** — no corporate data in this repo; skills use relative paths; structure travels by copy, skills via astra.
- **Hybrid git** — skeleton tracked, payload binaries ignored (`tests/`, `skills/` whitelisted).
- **No runtime app for now** — Claude Code is the interface; the only code is the stdlib gate script.

## Open questions

- OPEN: walls not yet confirmed by user — **no renumbering ever** (are area numbers permanent?) and **no app, ever** (is a UI a betrayal or a maybe-later?).
- OPEN: the real work-machine root path + how the populated instance stays in sync with design changes made here.
- OPEN: (FILING.md) deep-archive policy for old years; per-system subfolders under `30-operations/`.

## The gate

```bash
cp -r tests/fixture-inbox <scratch>/00-inbox    # + empty area dirs
# run the file-triage skill on <scratch>
python tests/check_triage.py <scratch>
```

Mechanical wall: 12 fixture files — 10 must be filed exactly per FILING.md, 2 must remain in inbox, none lost or invented. The filing rules themselves stay `[review]`.

Last green: 2026-07-04 (PASS; negative test confirmed FAIL on misfile + loss).
