# orbit — Implementation plan & resume sheet

> One-line working scenario: a messy directory goes in, every file lands in its one home in the numbered tree (or stays in inbox with a question), and ten years later it's still findable.
> Branch `main` · last updated 2026-07-06.

## Status right now

Shipped 2026-07-04: the **triage loop** (tree + contract + `file-triage` + fixture gate), the **restructure loop** (`.gravity/` adoption, `filing/SPEC.md` with tagged rules, `area-architect`, structure lint), the **dashboard** (`orbit-dashboard` → self-contained `dashboard.html`), and the **intake loop** (`file-scout` gathers files from other dirs into `00-inbox/` — move-from-dump/copy-from-live, dedup, provenance — governed by the SPEC's new "Intake" section, walled by `check_scout.py`). Wall questions answered: renumbering allowed as deliberate migration; apps allowed (static HTML first). Also this session: skills wired for Claude Code (`.claude/skills` junctions) + Codex (AGENTS.md), and the repo went **public** with a deny-by-default `.gitignore` (areas never committed). Next slice: user's pick — see queue.

## Domain status spine

| Domain | Status | Docs |
|---|---|---|
| filing | ◑ building (contract + four skills — scout/triage/find/architect — + four walls; retrieval fresh) | `filing/SPEC.md` |
| waypoint | ◑ building (manifest schema + `build_index.py` generator + `locate` skill + `check_waypoint` wall; per-dir dashboard pending) | `waypoint/SPEC.md` |

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
| later | **waypoint**: per-directory dashboard view (select box in `orbit-dashboard`, or a sub-page) — the "feature 1" slice; `build_index.py` already computes the counts | ○ |
| later | **waypoint**: dashboard flags drift (an un-manifested giant dir; declared `file_types` vs actual) as junk-hunt findings | ○ |
| later | Publish orbit skills to astra (`astra-publish` loop — dogfood both projects) | ○ |
| later | Deep-archive procedure for old years (see SPEC OPEN) | ○ |

Shipped (details in git history): **file-find (retrieval loop)** — SKILL (parse the ask into filing signals, predict-the-home via the SPEC decision procedure run forward, narrow-to-wide search, ranked candidates with evidence, miss-as-diagnosis: never-ingested/misfiled/ambiguous-contract) + `tests/fixture-find/` planted tree (incl. a deliberate misfile + inbox straggler + provenance manifest) + 7-query set + `check_find.py` (exact hits, no-silent-pick ambiguity, miss diagnosis, misfile flag, md5 read-only wall); PASS + FAIL-on-planted-violations verified (2026-07-06) · **process-architect skill** — interview-to-define + JSON→self-contained-HTML generator for process guidelines (approval chains / handoff pipelines), health rubric in the SKILL, `*.process.html` gitignored like `dashboard.html`; shipped with two fake/meta sample definitions (`purchase-order`, `orbit-file-fix`) (2026-07-05) · **triage loop** — tree + contract + file-triage skill + fixture gate (2026-07-04) · **restructure loop** — `.gravity/` adoption + `filing/SPEC.md` (tagged rules, lifecycle & budget) + area-architect skill + structure lint (2026-07-04) · **dashboard** — orbit-dashboard skill, one self-contained HTML page, verified on empty + populated trees (2026-07-04) · **dashboard v2 (junk hunt)** — pro redesign (KPI strip, sticky header, SVG type-donut) + cleanup candidates (>5 MB & 180d+ stale, size×staleness rank), md5 exact-duplicate groups + dupe-waste KPI, age profile; hunting guide in the SKILL; planted-junk detection verified (2026-07-04) · **intake loop** — `file-scout` skill + SPEC "Intake" section (named sources, dump=move/live=copy, dedup, provenance) + `check_scout.py` gate on fake source roots; PASS + FAIL-on-violation (junk ingested, live moved, unrecorded) verified (2026-07-04) · **area browsing cards** — `skills/area-architect/generate_cards.py` emits one `NN-*/README.md` per area *from the SPEC areas table* (single source, zero drift), gitignored like `dashboard.html`; regeneration wired into the area-architect restructure procedure (2026-07-05) · **waypoint domain (birth)** — `.gravity/waypoint/SPEC.md` (curated-directory manifests + the read-index-never-scan-payload invariant), `skills/locate/` with `build_index.py` (scan every `_waypoint.md` → one root `waypoint-index.md`), `tests/check_waypoint.py` + `tests/fixture-waypoint/` wall; PASS on 2-manifest fixture + FAIL-on-missing-purpose verified; index gitignored (2026-07-05).

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
- OPEN (recommendation made, awaiting user sign-off — filing rules are `[review]`): where process guidelines live. Analysis says **no new area**: `50-policy/`'s What-belongs row already claims "official process documents", so a `60-process/` area would violate the add rule (non-overlap) and spend the 7th budget slot. Recommended: `50-policy/processes/<slug>.json` + generated `<slug>.process.html` beside it (flat pair, kebab slug, no date prefix — living documents versioned by `meta.version`); *personal* routine conventions go to `20-design/` per 50-policy's NOT column. Fake samples stay in `skills/process-architect/examples/`. If accepted: add one line to 50-policy's What-belongs row naming `processes/` — a row clarification, not a lifecycle event.

## The gate

```bash
python tests/check_structure.py .              # tree ↔ contract, numbering, budget
cp -r tests/fixture-inbox <scratch>/00-inbox   # + empty area dirs
# run the file-triage skill on <scratch>
python tests/check_triage.py <scratch>
cp -r tests/fixture-sources <scratch>/sources  # + empty 00-inbox/
# run the file-scout skill on <scratch> (desktop+downloads=dump, onedrive-sync=live)
python tests/check_scout.py <scratch>
python tests/check_waypoint.py tests/fixture-waypoint   # waypoint: curated-directory manifest schema
cp -r tests/fixture-find/tree/. <scratch2>/    # planted tree incl. one misfile
# run the file-find skill on <scratch2> over tests/fixture-find/queries.json
python tests/check_find.py <scratch2>
```

Last green: 2026-07-06 (all five checkers PASS; each verified to FAIL on planted violations).
