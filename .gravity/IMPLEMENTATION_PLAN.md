# orbit — Implementation plan & resume sheet

> One-line working scenario: a messy directory goes in, every file lands in its one home in the numbered tree (or stays in inbox with a question), and ten years later it's still findable.
> Branch `master` · last updated 2026-07-04.

## Status right now

Three slices shipped 2026-07-04: the **triage loop** (tree + contract + `file-triage` + fixture gate), the **restructure loop** (`.gravity/` adoption, `filing/SPEC.md` with tagged rules, `area-architect`, structure lint), and the **dashboard** (`orbit-dashboard` skill → self-contained `dashboard.html`). Both wall questions answered: renumbering allowed as deliberate migration; apps allowed (static HTML first). Next slice: user's pick — see queue.

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

Shipped (details in git history): **triage loop** — tree + contract + file-triage skill + fixture gate (2026-07-04) · **restructure loop** — `.gravity/` adoption + `filing/SPEC.md` (tagged rules, lifecycle & budget) + area-architect skill + structure lint (2026-07-04) · **dashboard** — orbit-dashboard skill, one self-contained HTML page, verified on empty + populated trees (2026-07-04) · **dashboard v2 (junk hunt)** — pro redesign (KPI strip, sticky header, SVG type-donut) + cleanup candidates (>5 MB & 180d+ stale, size×staleness rank), md5 exact-duplicate groups + dupe-waste KPI, age profile; hunting guide in the SKILL; planted-junk detection verified (2026-07-04).

## Locked decisions

- **Numbered areas, gaps of 10, kebab-case** — insertable later without renumbering; CLI/git/agent-safe names.
- **`.gravity/filing/SPEC.md` is the seam** — all sorting/restructuring behavior lives in the contract; skills contain no filing rules of their own.
- **Never lose a file** — moves only, unclear stays in inbox with a question (mission wall).
- **Top-layer budget is mechanical** — the structure lint warns at 7 areas, fails at 9. Renumbering is *allowed* but only as a deliberate migration (change order + tombstone); a tombstoned number is never reused for a different subject.
- **Design here, deploy at work** — no corporate data in this repo; skills use relative paths; structure travels by copy, skills via astra.
- **Hybrid git** — skeleton tracked, payload binaries ignored (`tests/`, `skills/` whitelisted).
- **No server app yet** — Claude Code is the primary interface; app surfaces are generated static self-contained HTML (the dashboard). A real server app is a maybe-later, not a wall.
- **`.gravity/` adopted early on purpose** — orbit's root is the product; docs may not pile up on the layer the budget protects.

## Open questions

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
