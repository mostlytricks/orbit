# Changelog

All notable changes to **orbit** are recorded here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); versioning is [SemVer](https://semver.org/).
This is orbit's own product version; the gravity system version it adopted (`v1.8`)
is separate and lives in `CLAUDE.md`.

## [Unreleased]

### Added
- **`memory-map` skill — the waypoint domain's face.** One self-contained page that
  colors the tree by *memory*, not just mass: curated-and-fresh tiles lit with their
  manifest's purpose, stale tiles flickering amber (content newer than the manifest),
  partial tiles for directories with deeper waypoints, and big uncurated directories as
  **dark territory** whose click-card carries a ready-to-paste `_waypoint.md` skeleton
  (small dirs stay neutral — the SPEC's anti-sprawl gate). Memory-coverage KPI = curated
  mass / mass that deserves memory. Read-only lens: sizes, counts, mtimes and manifests
  only; `memory-map.html` is gitignored generated output. Verified on a planted
  five-state tree including live click-cards in headless Chromium.

## [0.5.0] - 2026-07-12

The habit release: retrieval closed, the desktop shell born, the weekly rhythm built
(daily-note -> weekly-report -> janitor) - design-complete for v1, now waiting on
First Light (the first run against real files).

### Added
- **`orbit-janitor` skill — the weekly nag.** A read-only sweep of five signals (inbox
  age, exact-duplicate waste, structure lint, stale waypoint manifests / missing index,
  big+stale cleanup candidates) filed as a day-dated chore record in `10-daily/YYYY/MM/`
  so tree health lands next to the daily notes. Verdict per check (OK/WARN/ACT) and every
  finding routes to the skill that fixes it - the janitor diagnoses, never treats: it
  moves and deletes nothing (md5-inventory-verified by its gate). Walled by the seventh
  gate `tests/check_janitor.py` + `tests/fixture-janitor/` (self-driving, pinned clocks);
  PASS + FAIL-on-planted-violations verified.
- **Daily loop (`notes` domain)** — the habit-forming half of "work OS".
  `.gravity/notes/SPEC.md` contracts the note shape (four load-bearing sections),
  the carry-forward rule (unfinished In-progress bullets follow you to today's note,
  `(carried)` once, never overwrite an existing note) and the weekly assembly.
  `daily-note` opens the day (`skills/daily-note/new_note.py`); `weekly-report`
  assembles the week (`skills/weekly-report/generate.py`): Done grouped by day,
  Decisions date-tagged, the last note's In-progress as "Carried into next week",
  and a per-area tree-activity table (mtime window, payload never read) — Highlights
  are then written *from* those facts, never invented. Walled by the sixth gate:
  `tests/check_notes.py` on a planted fixture week (self-driving, deterministic
  dates/utimes); PASS + FAIL-on-planted-violations verified. Placement authority
  stays with the filing SPEC.
- **Orbit Deck: celestial theme & meteor micro-interactions** — the wordmark is a burning
  comet, the tree pane floats over a faint pure-CSS starfield, and the explorer narrates
  change: a removed file/directory burns up like a meteor (streak + ember fade) before the
  tree closes over the gap, arrivals land with a touchdown glow, and the inbox badge fires
  a shockwave when new files drop. Deck still never deletes - the meteor animates removals
  it *observes*. All effects respect `prefers-reduced-motion`; verified in the Electron-free
  smoke test (burnout / touchdown / ping assertions).
- **Orbit Deck (`app/`)** — the first real app surface: a local Electron desktop shell
  (Windows portable zip, no installer, no server) with three panes. *Areas*: live tree
  explorer (fs-watch auto-refresh, amber inbox badge, double-click opens). *Tree health*:
  the existing `orbit-dashboard` page regenerated via `python` and embedded — Deck renders
  orbit's outputs, it re-implements nothing. *Agent*: chat that spawns the Claude Code CLI
  (`claude -p --output-format stream-json`, session resume, permission modes
  plan/acceptEdits/bypass) with tool calls streamed as a working-process timeline.
  Smoke-tested without an Electron binary (`app/tests/deck-smoke.js`: scanner counts on
  the find fixture + renderer UI in headless Chromium). The Windows zip builds on GitHub
  Actions (`build-orbit-deck` workflow) because the dev container cannot fetch Electron
  binaries; grab the `OrbitDeck-win-portable` artifact.
- **`file-find` skill** — retrieval, the flip side of `file-triage`: parse the ask
  into the SPEC's filing signals, predict the file's one home by running the decision
  procedure forward, search narrow-to-wide (predicted home → name → content →
  inbox/provenance), present ranked candidates with evidence. Read-only; a miss is
  diagnosed (never-ingested / misfiled / ambiguous contract) and routed to the right
  skill, never shrugged off. Walled by the fourth mechanical gate:
  `tests/fixture-find/` (planted tree with a deliberate misfile, an inbox straggler
  and a provenance manifest, plus a 7-query set) + `tests/check_find.py` (exact hits,
  no-silent-pick ambiguity, correct miss diagnosis, misfile flagging, md5-verified
  read-only wall); PASS and FAIL-on-planted-violations both verified.

## [0.4.0] - 2026-07-05

### Added
- **`waypoint` domain — curated-directory manifests & a cheap index.** A deep directory
  opts into being findable by holding a `_waypoint.md` manifest (YAML: purpose, keywords,
  file types); `skills/locate/build_index.py` scans every manifest and writes one root
  `waypoint-index.md`. The `locate` skill answers "where is X?" from that index alone —
  **never listing or reading payload**, which is the token-bomb the domain exists to
  prevent. Walled by `tests/check_waypoint.py` + `tests/fixture-waypoint/`. Contract in
  `.gravity/waypoint/SPEC.md`; `waypoint-index.md` is a gitignored generated artifact.

## [0.3.0] - 2026-07-05

### Added
- **`process-architect` skill** — documents *how a process works* (approval chains,
  handoff pipelines), the counterpart to the filing skills that decide *where files
  go*. An interview procedure (`SKILL.md`) draws a process out and pressure-tests it
  against a health rubric — one owner per gate, explicit entry/exit criteria, named
  `go`/`hold`/`stop` decision states, no dead ends, a per-gate SLA, escape hatches —
  then `generate.py` renders the agreed JSON definition as one self-contained,
  theme-aware, print-clean HTML guideline. Data-in/HTML-out like `orbit-dashboard`:
  the JSON definition is the tracked source, `*.process.html` is disposable gitignored
  output, never hand-edited. Ships two sample definitions — a fake five-gate
  purchase-order approval chain (internal sign-offs then the external supplier) and
  orbit's own file/directory fix process (scout → triage → file → verify →
  restructure). Carries no filing rules; registered in `AGENTS.md`.

## [0.2.0] - 2026-07-05

### Added
- **Per-area browsing cards** — `skills/area-architect/generate_cards.py` generates one
  `NN-*/README.md` per area *from the SPEC areas table* (single source, no drift), so
  browsing the tree in a file manager at work self-explains without an agent. Cards are a
  generated artifact — gitignored by the existing deny-by-default area wall (like
  `dashboard.html`), never hand-edited — and regeneration is now the final step of the
  `area-architect` restructure procedure, so a rename/add/retire can't orphan a stale card.

## [0.1.0] - 2026-07-05

First tagged release — the filing system's whole first arc, exercised on real files.

### Added
- **Six-area numbered tree** (`00-inbox` … `50-policy`) and the filing contract in
  `.gravity/filing/SPEC.md` — one home per file, gaps-of-10 numbering, a mechanical
  top-layer budget.
- **`file-triage` skill** — sorts a messy inbox into areas per the contract; walled by
  `tests/check_triage.py` on a 12-file fixture (10 filed, 2 correctly held).
- **`area-architect` skill** + `tests/check_structure.py` — restructure the tree under
  lifecycle rules; structure lint checks tree ↔ contract, numbering, and budget.
- **`file-scout` skill** — the front door: gathers files from named external dirs into
  `00-inbox/` (dump = move / live = copy, md5 dedup, provenance manifest); walled by
  `tests/check_scout.py`. Intake rules live in `filing/SPEC.md`.
- **`orbit-dashboard` skill** — one self-contained HTML page (contract verdict, cleanup
  candidates, md5 duplicate groups, size-by-type, age profile, area census); `--open`
  launches it in the default browser.
- **`.gravity/` doc system** (gravity v1.4): `IMPLEMENTATION_PLAN.md` and a `filing`
  domain SPEC with enforcement-tagged rules and a behavioral contract.
- **Dual-agent skill discovery** — `.claude/skills` junctions for Claude Code (via
  `.claude/setup-skills.py`) and an `AGENTS.md` skills table for Codex, off one
  canonical source in `skills/`.

### Security
- Repo made public behind a **deny-by-default `.gitignore`**: nothing inside a numbered
  area is ever committed (any file type) — only `.gitkeep`. Real work content cannot
  leak; verified with planted files.

### Notes
- Design instance only — no corporate data; the skeleton travels by copy, skills via astra.
- Known open questions (`IMPLEMENTATION_PLAN.md`): deep-archive policy for old years,
  Korean-filename normalization in `file-scout`, and a possible dedicated reference area.
