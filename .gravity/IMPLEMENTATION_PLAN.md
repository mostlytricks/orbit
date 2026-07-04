# orbit — Implementation plan & resume sheet

> One-line working scenario: a messy directory goes in, every file lands in its one home in the numbered tree (or stays in inbox with a question), and ten years later it's still findable.
> Branch `master` · last updated 2026-07-04.

## Status right now

Two slices shipped 2026-07-04: the **triage loop** (tree + contract + `file-triage` + fixture gate) and the **restructure loop** (`.gravity/` adoption, contract → `filing/SPEC.md` with tagged rules, `area-architect` skill, `check_structure.py` structure lint). Next slice: user's pick — see queue.

## Domain status spine

| Domain | Status | Docs |
|---|---|---|
| filing | ◑ building (contract + two skills + two walls; lifecycle rules fresh) | `filing/SPEC.md` |

## Slice queue

Rolling lanes (growing project — skills accrete, phases would be fake). Rules:
- **Exactly one slice in `now`**; `next` ordered and short; `later` is an unordered pool.
- A shipped slice leaves the queue; its detail survives in git history.
- New slices enter via `/interview orbit <feature>`; run the domain gate first — most features are slices under `filing` (or a future `notes` domain), not new domains.

| Lane | Slice | Status |
|---|---|---|
| now | OPEN: user picks the next slice (candidates below) | ○ |
| next | `daily-note` skill — templated daily worklog auto-placed in `10-daily/YYYY/MM/` (likely mints a `notes` domain) | ○ |
| later | `weekly-report` skill — assemble the week's report from daily notes | ○ |
| later | Publish orbit skills to astra (`astra-publish` loop — dogfood both projects) | ○ |
| later | Per-area README.md files for human browsing at work | ○ |
| later | Deep-archive procedure for old years (see SPEC OPEN) | ○ |

Shipped (details in git history): **triage loop** — tree + contract + file-triage skill + fixture gate (2026-07-04) · **restructure loop** — `.gravity/` adoption + `filing/SPEC.md` (tagged rules, lifecycle & budget) + area-architect skill + structure lint (2026-07-04).

## Locked decisions

- **Numbered areas, gaps of 10, kebab-case** — insertable later without renumbering; CLI/git/agent-safe names.
- **`.gravity/filing/SPEC.md` is the seam** — all sorting/restructuring behavior lives in the contract; skills contain no filing rules of their own.
- **Never lose a file** — moves only, unclear stays in inbox with a question (mission wall).
- **Top-layer budget is mechanical** — the structure lint warns at 7 areas, fails at 9; numbers never change and are never reused (tombstones in the Areas table).
- **Design here, deploy at work** — no corporate data in this repo; skills use relative paths; structure travels by copy, skills via astra.
- **Hybrid git** — skeleton tracked, payload binaries ignored (`tests/`, `skills/` whitelisted).
- **No runtime app for now** — Claude Code is the interface; the only code is the two stdlib gate scripts.
- **`.gravity/` adopted early on purpose** — orbit's root is the product; docs may not pile up on the layer the budget protects.

## Open questions

- OPEN: walls not yet confirmed by user — **no renumbering ever** is now a SPEC rule `[review]` (confirm it's truly permanent) and **no app, ever** (is a UI a betrayal or a maybe-later?).
- OPEN: the real work-machine root path + how the populated instance stays in sync with design changes made here.
- OPEN: (SPEC) deep-archive policy for old years; per-system subfolders under `30-operations/`.

## The gate

```bash
python tests/check_structure.py .              # tree ↔ contract, numbering, budget
cp -r tests/fixture-inbox <scratch>/00-inbox   # + empty area dirs
# run the file-triage skill on <scratch>
python tests/check_triage.py <scratch>
```

Last green: 2026-07-04 (both checkers PASS; both verified to FAIL on planted violations).
