# Changelog

All notable changes to **orbit** are recorded here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); versioning is [SemVer](https://semver.org/).
This is orbit's own product version; the gravity system version it adopted (`v1.4`)
is separate and lives in `CLAUDE.md`.

## [Unreleased]

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
