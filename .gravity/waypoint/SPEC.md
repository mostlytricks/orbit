# SPEC — waypoint (curated-directory manifests & the cheap index)

The compact agent-loadable contract for the `waypoint` domain: **how a deep directory
opts into being findable**, and **how an agent locates it without ever scanning its
payload**. Where `filing` governs the *top layer's* width, `waypoint` governs *depth*
selectively — a five-levels-deep folder with a thousand files is a token-bomb to `ls`;
a manifest turns it into a navigable point the agent routes to for near-zero cost.

**The seam:** a directory becomes a *waypoint* by holding a manifest (`_waypoint.md`)
with YAML frontmatter (purpose, keywords, types). A generator (`build_index.py`) reads
every manifest and computes each directory's file-count/size, writing one root **index**
(`waypoint-index.md`). The `locate` skill answers "where is X?" from that index alone.
Skills carry no rules of their own — change waypoint behavior *here*.

**Gate:**
```bash
python tests/check_waypoint.py tests/fixture-waypoint   # schema: every _waypoint.md is valid
python skills/locate/build_index.py .                   # (re)build waypoint-index.md from all manifests
```

## Core Definition

A **waypoint** is any directory containing a `_waypoint.md` manifest — the manifest's
*presence is the opt-in flag*; there is no other mechanism. The **waypoint index** is a
generated file at the orbit root (`waypoint-index.md`) with one row per waypoint: its
declared purpose/keywords/types plus generator-computed file-count/size/last-scanned.

**The invariant this domain exists to protect:** a location query is answered from the
index (and at most the *one* matched manifest) — **never** by listing or reading a
waypoint's payload. The expensive filesystem walk happens once, in Python
(`build_index.py`), and costs the agent zero tokens; the query cost is bounded by the
number of waypoints, not the number of files.

## Minimal Shape

```text
20-design/2024/corporate-guideline/
  _waypoint.md                       # the manifest (below) — this dir is now a waypoint
  architecture-standard-v3.pdf
  samples/…                          # 900 files the agent never lists
```

`_waypoint.md`:
```markdown
---
purpose: Corporate architecture & design guidelines devs must follow.
keywords: [architecture, guideline, standard, design-system, corporate]
file_types: [pdf, docx, md]
status: active            # active | archive | frozen
period: 2024              # optional temporal scope (year or range)
---

# 20-design / 2024 / corporate-guideline

What lives here, how it's organized, what a reader should expect. Human prose.
```

## Manifest schema

| Field | Required | Type | Meaning |
|---|---|---|---|
| `purpose` | **yes** | scalar | One line: what/why. The primary match target for a query. |
| `keywords` | **yes** | inline list | Search terms that route "where is X?" to this row. |
| `file_types` | recommended | inline list | Extensions expected here (a drift signal for the dashboard). |
| `status` | recommended | enum | `active` \| `archive` \| `frozen`. |
| `period` | optional | scalar | Year or range, for temporal queries ("…in 2026"). |
| `owner` / `review_by` | optional | scalar | Stewardship, if useful. |

**YAML is a deliberately tiny subset:** scalars and inline `[a, b]` lists only — no
block lists (`- item`), no nesting. The stdlib-only parser supports exactly this (orbit
carries no PyYAML). Keep lists inline.

**Generator-computed stats** (`file_count`, `size`, `last_scanned`) live in the **index
only** — the generator *never edits your manifest*, so hand-authored intent and machine
counts never fight over the same file.

## The index (`waypoint-index.md`)

Generated at the orbit root, **gitignored** (per-instance runtime, like `dashboard.html`),
rebuilt by `build_index.py` — one markdown-table row per waypoint. It is the single file
an agent reads to route a location query. Never hand-edit it; regenerate.

## Retrieval protocol (what `locate` does)

1. **Read `waypoint-index.md` only.** If missing/stale, rebuild it first
   (`build_index.py`) — a bounded scan, never an `ls` of the tree.
2. **Match** the query against rows: `period` (year/range), `keywords`, then `purpose`.
3. **Answer with the path(s)** + purpose. For detail, open *at most* the one matched
   `_waypoint.md`.
4. **Never** list/read the payload to answer "where is X" — that is the exact cost this
   domain removes.

## When to set a waypoint (the opt-in gate)

A manifest is **deliberate, not automatic**. Add a `_waypoint.md` to a directory when it
is (a) something you'll later want to *find by description*, (b) deep/large enough that
scanning it is expensive (the token-bomb), or (c) a curated canonical collection
(guidelines, standards, a project's home). **Do not manifest every folder** — that's
depth-sprawl, and the index is only useful while it stays a short list of *waypoints*.
An un-manifested giant directory is a smell the dashboard surfaces: either set a waypoint
+ clean it, or it's junk for cleanup.

## Rules

- `[test:check_waypoint]` every `_waypoint.md` parses and carries a non-empty `purpose` and a non-empty `keywords` list.
- `[test:check_waypoint]` `keywords` and `file_types`, when present, are lists (inline `[…]`), not scalars.
- `[test:check_waypoint]` `status`, when present, is one of `active` / `archive` / `frozen`.
- `[review]` a manifest is added only to a *waypoint-worthy* directory (find-by-description / expensive-to-scan / canonical collection) — not to every folder.
- `[review]` location queries are answered from `waypoint-index.md` (+ at most the one matched manifest), never by listing the payload.
- `[review]` the generator never edits manifests; computed stats live in the index only.
- `[—]` `waypoint-index.md` is a generated artifact (gitignored) — rebuild it, never hand-edit.

## Behavioral Contract

- `[test:check_waypoint]` given the fixture tree (two valid manifests + one un-manifested dir), when the checker runs → PASS naming 2 waypoints; when a manifest drops `purpose`, → FAIL naming it.
- `[review]` given "where's the 2026 design guideline?", when `locate` runs → it reads `waypoint-index.md`, matches the `20-design/2026/…` row on period + keywords, and returns that path *without listing the directory*.

## Gotchas

- Manifests inside real areas are **gitignored by the area wall** — they live with the
  payload on the work machine, never in this public repo. The *schema, generator, and
  skill* are the tracked design artifacts; the manifests + index are per-instance runtime.
- Stale counts are expected between rebuilds — the index is a snapshot; rerun
  `build_index.py` (or the dashboard) after big content changes.
- A block list (`- item`) won't parse — keep lists inline (`[a, b]`).

## OPEN

- OPEN: per-directory dashboard view (a select box in `orbit-dashboard`, or a sub-page) — the "feature 1" slice; the index already computes the counts it needs.
- OPEN: should the index flag drift (declared `file_types` vs actual extensions, `active`-but-oversized) as findings, like the junk hunt?

---

Skills executing this contract: `skills/locate/` (retrieval + `build_index.py`).
