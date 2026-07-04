# Changelog

All notable changes to **orbit** are recorded here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); versioning is [SemVer](https://semver.org/).
This is orbit's own product version; the gravity system version it adopted (`v1.4`)
is separate and lives in `CLAUDE.md`.

## [Unreleased]

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
