# orbit — Implementation plan & resume sheet

> One-line working scenario: a messy directory goes in, every file lands in its one home in the numbered tree (or stays in inbox with a question), and ten years later it's still findable.
> Branch `main` · last updated 2026-07-12.

## Status right now

Design-complete for v1, unproven on real files (status review 2026-07-12). Built and walled: the whole filing loop (scout → triage → find → architect → dashboard, 5 mechanical gates), the waypoint domain (`locate` + index), `process-architect`, and **Orbit Deck** (Electron shell: tree explorer + embedded dashboard + agent panel + celestial theme; PRs #1–#4 merged). Not yet true: **zero real files have flowed through any skill** (fixtures only), Deck has never launched (`build-orbit-deck`: 0 runs), 0 release tags on the remote, and `[Unreleased]` holds three shipped features (v0.5.0 pending). Hence the now-slice: **First Light**. Identity sharpened this review: *the directory is the database, agents are the labor, walls keep everyone honest; apps are viewers, contracts are the product.*

## Domain status spine

| Domain | Status | Docs |
|---|---|---|
| filing | ◑ building (contract + four skills — scout/triage/find/architect — + four walls; retrieval fresh) | `filing/SPEC.md` |
| waypoint | ◑ building (manifest schema + `build_index.py` generator + `locate` skill + `check_waypoint` wall; per-dir dashboard pending) | `waypoint/SPEC.md` |
| notes | ◑ building (note shape + carry-forward + weekly assembly contract; `daily-note`/`weekly-report` skills + `check_notes` wall; fresh — unproven in daily use) | `notes/SPEC.md` |

## Slice queue

Rolling lanes (growing project — skills accrete, phases would be fake). Rules:
- **Exactly one slice in `now`**; `next` ordered and short; `later` is an unordered pool.
- A shipped slice leaves the queue; its detail survives in git history.
- New slices enter via `/interview orbit <feature>`; run the domain gate first — most features are slices under `filing` (or a future `notes` domain), not new domains.

| Lane | Slice | Status |
|---|---|---|
| now | **First Light** — not a feature, an *event*: run the `build-orbit-deck` workflow and launch Deck for real; run `file-scout`+`file-triage` on the real Desktop/Downloads; cut **v0.5.0** and push tags (0 tags on remote today). Converts the project from designed to true — everything below stays speculation until this happens. | ○ user-driven; agent assists |
| next | **Deck triage cockpit** — inbox rows with the agent's *proposed* home each; approve per-row, meteors fly as files leave. Plan-first rule as UI. | ○ |
| next | **`orbit-recall` — the Year-8 Exam** — orbit tests its own promise on a schedule: pick N random old files, generate natural questions from them, run `file-find` blind, score recall; misses become diagnoses (naming / waypoint / areas-table) routed to their owning skills. The mission's acceptance test as a recurring wall. | ○ |
| later | **Comet drop-zone** — Deck always-on-top mini mode (just the comet ☄): drag any file from anywhere → lands in `00-inbox/` with provenance. Kills the real failure mode: files never entering orbit at all. | ○ |
| later | **Deck command palette (Ctrl+K)** — one box: "where is X" → locate/file-find inline; "note" → today's worklog; "sweep" → janitor. Terminal power, zero terminal. | ○ |
| later | **Orbit View** — the dashboard's census/age panels as an actual orbital system (areas = planets by mass, files = satellites, inbox = asteroid belt, staleness = cold outer orbits, dupes glow, cleanup candidates = decaying orbits). Same data, Canvas, self-contained. | ○ |
| later | **Handover package generator** — assemble a leave/exit handover doc purely from existing contracts: active projects, runbook index, open carried items, recent decisions, waypoint map. Nothing invented, everything cited. | ○ |
| later | **Decision timeline** — generated HTML timeline of every date-tagged Decision from the notes domain, across years. Organizational memory of one. | ○ |
| later | **`.eml` mail intake** — a `mail-drop/` scout source: unpack `.eml` attachments (stdlib `email`) into inbox files with sender/date provenance. (`.msg` stays cut: needs non-stdlib parsing.) | ○ |
| later | **waypoint**: per-directory dashboard view (select box in `orbit-dashboard`, or a sub-page) — the "feature 1" slice; `build_index.py` already computes the counts | ○ |
| later | **waypoint**: dashboard flags drift (an un-manifested giant dir; declared `file_types` vs actual) as junk-hunt findings — natural home: an eighth janitor check | ○ |
| later | Publish orbit skills to astra (`astra-publish` loop — dogfood both projects) | ○ |
| later | Deep-archive procedure for old years (see SPEC OPEN) — correctly waits until real mass exists (post-First-Light) | ○ |

### The loops (why this order — how the dots connect)

Every slice above is a missing edge in one of five loops; nothing is an island:

1. **Intake loop** — *comet drop-zone* → `file-scout` → `00-inbox` → *triage cockpit* → areas. The drop-zone feeds the front door; the cockpit makes emptying it a pleasure. Kills the two real failure modes: files never entering, and the inbox never emptying.
2. **Truth loop** — `orbit-janitor` nags → triage/architect fix → walls verify. The *waypoint-drift check* joins as the eighth nag.
3. **Memory loop** — `daily-note` → `weekly-report` → *decision timeline* → *handover generator*. Each stage is pure assembly from the previous one's contract; the handover doc is the memory loop's final product — orbit's answer to "what if I'm hit by a bus".
4. **Proof loop** — *`orbit-recall`* asks → `file-find` answers → misses diagnose → SPEC/waypoints improve → recall score rises. The mission sentence ("ten years later it's still findable") becomes a number that trends.
5. **Seeing loop** — dashboard/Deck/*Orbit View*/*palette*: same contracts, ever-better lenses. Viewers, never the product.

Cut and staying cut (razor, 2026-07-12): semantic search / embeddings (needs a server; find+locate already answer) · gamification beyond the orbital physics metaphor · mobile companion · cloud sync (the walls exist precisely because nothing leaves).

Reviewed & cut (2026-07-12, identity razor applied — *does it make the tree more true or the labor more automatic?*): a content-search index (`file-find` already searches live content; a personal tree needs no search server) · more Deck theming before real usage · the Tauri port (stays behind its decision gate: size/startup/policy pain after real use, else never). Further cuts live under "The loops" below.

Shipped (details in git history): **memory-map (the waypoint domain's face)** — `skills/memory-map/generate.py` renders one self-contained `memory-map.html` (gitignored): one tile per depth-2 directory sized by bytes and colored by memory state (lit = curated fresh with the manifest's purpose as label · stale = amber flicker, content newer than manifest · partial = waypoints deeper inside · dark = >=15 files or >=5 MB and uncurated, click-card carries a `_waypoint.md` skeleton · neutral = small, never dark per the SPEC's anti-sprawl gate) + memory-coverage KPI (curated mass / mass deserving memory); verified on a planted five-state scratch incl. live click-cards in Chromium + empty tree; absorbed the two former waypoint-dashboard slices; built ahead of First Light at the user's call (2026-07-12) · **orbit-janitor (the weekly nag)** — read-only five-check sweep (inbox age vs 7d, md5 dupe waste, structure lint via `check_structure.py`, stale `_waypoint.md`/missing index, big+stale cleanup candidates) filed as a day-dated chore record in `10-daily/YYYY/MM/`; every finding routes to its owning skill; `--force` re-sweep; seventh wall `tests/check_janitor.py` + `fixture-janitor/` (self-driving, pinned clocks, md5 read-only inventory check); PASS + FAIL-on-planted-violations verified (2026-07-12) · **daily loop (notes domain birth)** — `.gravity/notes/SPEC.md` (note shape with four load-bearing H2 sections, single-`(carried)` forward rule, never-overwrite, weekly assembly from the week's worklogs + an mtime-window tree-activity scan; placement stays the filing SPEC's) + `skills/daily-note/` (`new_note.py`) + `skills/weekly-report/` (`generate.py`, `--force` reassembly) + the sixth wall `tests/check_notes.py` on `tests/fixture-notes/` (self-driving, pinned to fixture week 2026-W24); PASS + FAIL-on-planted-violations (missing source note, malformed pre-planted note) verified (2026-07-12) · **file-find (retrieval loop)** — SKILL (parse the ask into filing signals, predict-the-home via the SPEC decision procedure run forward, narrow-to-wide search, ranked candidates with evidence, miss-as-diagnosis: never-ingested/misfiled/ambiguous-contract) + `tests/fixture-find/` planted tree (incl. a deliberate misfile + inbox straggler + provenance manifest) + 7-query set + `check_find.py` (exact hits, no-silent-pick ambiguity, miss diagnosis, misfile flag, md5 read-only wall); PASS + FAIL-on-planted-violations verified (2026-07-06) · **process-architect skill** — interview-to-define + JSON→self-contained-HTML generator for process guidelines (approval chains / handoff pipelines), health rubric in the SKILL, `*.process.html` gitignored like `dashboard.html`; shipped with two fake/meta sample definitions (`purchase-order`, `orbit-file-fix`) (2026-07-05) · **triage loop** — tree + contract + file-triage skill + fixture gate (2026-07-04) · **restructure loop** — `.gravity/` adoption + `filing/SPEC.md` (tagged rules, lifecycle & budget) + area-architect skill + structure lint (2026-07-04) · **dashboard** — orbit-dashboard skill, one self-contained HTML page, verified on empty + populated trees (2026-07-04) · **dashboard v2 (junk hunt)** — pro redesign (KPI strip, sticky header, SVG type-donut) + cleanup candidates (>5 MB & 180d+ stale, size×staleness rank), md5 exact-duplicate groups + dupe-waste KPI, age profile; hunting guide in the SKILL; planted-junk detection verified (2026-07-04) · **intake loop** — `file-scout` skill + SPEC "Intake" section (named sources, dump=move/live=copy, dedup, provenance) + `check_scout.py` gate on fake source roots; PASS + FAIL-on-violation (junk ingested, live moved, unrecorded) verified (2026-07-04) · **area browsing cards** — `skills/area-architect/generate_cards.py` emits one `NN-*/README.md` per area *from the SPEC areas table* (single source, zero drift), gitignored like `dashboard.html`; regeneration wired into the area-architect restructure procedure (2026-07-05) · **waypoint domain (birth)** — `.gravity/waypoint/SPEC.md` (curated-directory manifests + the read-index-never-scan-payload invariant), `skills/locate/` with `build_index.py` (scan every `_waypoint.md` → one root `waypoint-index.md`), `tests/check_waypoint.py` + `tests/fixture-waypoint/` wall; PASS on 2-manifest fixture + FAIL-on-missing-purpose verified; index gitignored (2026-07-05).

## Locked decisions

- **Numbered areas, gaps of 10, kebab-case** — insertable later without renumbering; CLI/git/agent-safe names.
- **`.gravity/filing/SPEC.md` is the seam** — all sorting/restructuring behavior lives in the contract; skills contain no filing rules of their own.
- **Never lose a file** — moves only, unclear stays in inbox with a question (mission wall).
- **Top-layer budget is mechanical** — the structure lint warns at 7 areas, fails at 9. Renumbering is *allowed* but only as a deliberate migration (change order + tombstone); a tombstoned number is never reused for a different subject.
- **Design here, deploy at work** — no corporate data in this repo; skills use relative paths; structure travels by copy, skills via astra.
- **Hybrid git** — skeleton tracked, payload binaries ignored (`tests/`, `skills/` whitelisted).
- **No server, ever-thicker local apps** — Claude Code is the primary interface; app surfaces are generated static self-contained HTML (the dashboard) plus **Orbit Deck** (`app/`, local Electron shell: tree explorer + embedded dashboard + agent panel spawning the claude CLI). Deck is a *viewer/driver over the same contracts* — it re-uses `orbit-dashboard` output and the CLI's skills, never re-implements filing logic. A server app remains a maybe-later, not a wall.
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
