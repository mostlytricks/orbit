# SPEC — filing (the orbit filing contract)

The compact agent-loadable contract for the `filing` domain: **how a file arrives**,
**where it goes**, **how it is found again**, and **what the area tree may look
like**. Skills (`file-scout`, `file-triage`, `file-find`, `area-architect`) execute
this contract and carry no rules of their own — change filing behavior *here*.
Humans follow the same tables when filing by hand.

**Gate:**
```bash
python tests/check_structure.py .            # structure lint: tree ↔ this contract, numbering, budget
python tests/check_triage.py <scratch>       # behavior: fixture sort per the decision procedure
python tests/check_scout.py <scratch>        # behavior: intake from fixture source roots
python tests/check_find.py <scratch>         # behavior: retrieval on the planted fixture tree
```

## Core Definition

A valid orbit instance is a directory tree whose top layer contains **exactly the areas
in the table below** (plus the infrastructure dirs `.git`/`.github`/`.gravity`/`skills`/
`tests`/`app` and the root docs — infrastructure is *skeleton*, never a filing
destination), where
every file sits in the one area the decision procedure assigns it — or in `00-inbox/`
awaiting triage.

## The areas

| Area | What belongs | What does NOT |
|---|---|---|
| `00-inbox/` | Everything unsorted. The **only** drop zone — files enter orbit here and leave via triage. | Nothing lives here long-term. |
| `10-daily/` | Recurring personal work: daily worklogs, weekly reports, routine checklists, chore records. Nested `YYYY/` and, for day-dated files, `YYYY/MM/`. | System procedures (→ 30), project status (→ 40). |
| `20-design/` | Architecture & design: decision records, system/solution designs, diagrams, tech standards and patterns. | Operational how-to (→ 30). |
| `30-operations/` | Running systems: runbooks, incident reports, maintenance/patch records, monitoring, DR plans. | One-off project deliverables (→ 40). |
| `40-projects/` | Everything belonging to a named project, one folder per project: `40-projects/<project-slug>/` — plans, meeting notes, vendor docs, status reports. | Recurring personal reports (→ 10). |
| `50-policy/` | Corporate policy, security policy, compliance, official process documents. | Your own conventions (→ 20 as a standard). |

<!-- Retired or renumbered areas stay in this table with "(retired YYYY-MM-DD)" or
     "(renumbered → NN, YYYY-MM-DD)" in the What-belongs cell and no folder on disk —
     the number is a tombstone, never reused for a different subject. check_structure.py
     skips such rows. -->

## Minimal Shape

The smallest correctly-filed slice — copy this pattern when creating destinations:

```text
00-inbox/                                            # empty after triage, or holding files + questions
10-daily/2026/07/2026-07-03-daily-worklog.md         # day-dated → YYYY/MM/
10-daily/2026/2026-W27-weekly-report.md              # week-scoped → YYYY/
40-projects/erp-upgrade/erp-upgrade-vendor-proposal.pdf   # one kebab slug folder per project
```

## Intake (getting files to the front door)

`00-inbox/` is the **only** way in, but files rarely start there — they're scattered
across the machine (Desktop, Downloads, Documents, old dumps). The `file-scout` skill
gathers them into the inbox; it derives from these rules and carries none of its own.

**Sources are named, never discovered.** Scout operates only on source roots you name
explicitly (`~/Desktop`, `~/Downloads`, `D:\old-work`). It never scans a whole drive,
never touches system/program/app-data directories, and never re-ingests orbit's own tree.
Skip on sight: hidden files/dirs, `node_modules`, `.venv`, `__pycache__`, `.git`.

**Each source is tagged, and the tag picks the verb:**

| Source kind | Meaning | Action |
|---|---|---|
| `dump` | clutter that *should* empty — Desktop, Downloads, an old `misc/` | **move** into `00-inbox/` (consolidation: the file leaves the mess) |
| `live` | authoritative / synced / still in use — OneDrive, an active project dir | **copy** into `00-inbox/` (the source stays; orbit gets a working copy) |

A `dump` move is a *relocation*, never a deletion; a `live` copy leaves the original
untouched. **Scout never deletes a source file** (mission wall — CLAUDE.md Why).

**Relevance filter.** Ingest work documents (notes, decisions, reports, policies,
project files, spreadsheets, presentations, PDFs, archives). Leave personal media,
installers, app binaries, temp files. Unsure → the file becomes a **question row** in
the plan, decided by the human — never guessed in, never guessed out.

**Dedup on ingest.** md5 each candidate; if identical bytes already live anywhere in the
orbit tree (or already in the inbox), skip it and report "already filed" — intake never
manufactures the duplicates the dashboard then has to hunt.

**Provenance.** Every ingested file gets one line in `00-inbox/.orbit-provenance.jsonl`
(original absolute path · source tag · action · md5 · date), so a file's origin survives
the move and a `live` copy is traceable back to its authoritative source. The manifest is
inbox-local and gitignored — it may name sensitive paths and never leaves the machine.

**Plan first, like triage.** Scout presents `source → action → 00-inbox/name → reason`
and waits for approval; collisions get `-2`, `-3`, … suffixes, never overwrite. After
ingest the inbox is a normal messy inbox — hand off to `file-triage`.

## Decision procedure (for triage)

Classify each file **from its name and, when readable, its content** — in this order:

1. **Named project?** File mentions a known project (existing `40-projects/<slug>/` folder) → that folder. Clearly a project but no folder yet → **propose** the new `<slug>/`, don't silently invent taxonomy.
2. **Policy?** Official corporate/security/compliance document → `50-policy/`.
3. **Design vs operations:** *decision or blueprint* → `20-design/`; *procedure, incident, or record of running systems* → `30-operations/`.
4. **Personal recurring rhythm** (worklog, weekly report, routine checklist) → `10-daily/YYYY/` (day-dated → `YYYY/MM/`, year from the filename date, else file mtime).
5. **Unclear → it stays in `00-inbox/`** with a one-line question attached to the triage report. Never guess. Never delete. (Mission wall — CLAUDE.md Why.)

## Area lifecycle & top-layer budget (for restructuring)

The top layer is the product; width is expensive, depth is cheap.

- **Budget:** the numbering scheme is the governor — two digits, multiples of 10, `00` reserved for inbox. The lint **warns at 7 areas and fails at 9**: past 7±2 the map stops fitting in a head and decision-procedure steps become ambiguous. The answer to "I need a new area" is almost always **a subfolder inside an existing area**.
- **Add** — allowed only if (a) a real set of files would move there *immediately*, and (b) its What-belongs row overlaps no existing area. New area takes a free multiple-of-10 slot.
- **Rename** — the name may clarify; the number stays (cheap, safe).
- **Renumber** — allowed, but as a **deliberate migration**, never casually: follow the change order, move the whole folder in one step, and tombstone the old number in the Areas table (`(renumbered → NN, YYYY-MM-DD)`) so old links and muscle memory stay traceable.
- **Repurpose / merge / split** — allowed only after every affected file is rehomed first; never orphans.
- **Retire** — files rehomed, folder removed, the number tombstoned `(retired YYYY-MM-DD)`; **never reuse a tombstoned number for a different subject** — year-8 you must be able to trust old references.
- **Change order — contract before tree:** 1. edit this SPEC (table + tombstones) → 2. create/rename folders to match → 3. run `check_structure.py` → green. The tree is never ahead of the contract.

## Naming

- Kebab-case; no spaces, no leading dots/numbers except the area prefix.
- Dated material: `YYYY-MM-DD-<topic>.<ext>` (week-scoped: `YYYY-Www-<topic>`).
- Project slugs: short kebab (`erp-upgrade`, not `ERP Upgrade Project 2026`).
- Triage may **rename to conform** only when the mapping is lossless and obvious (`Weekly Report 2026-07-03.docx` → `2026-07-03-weekly-report.docx`); otherwise keep the original name.

## Rules

- `[test:check_scout]` intake ingests only relevant files, leaves junk/personal in the source, and writes a provenance entry for each ingested file.
- `[test:check_scout]` a `dump` source is **moved** (source emptied of the ingested file); a `live` source is **copied** (original preserved).
- `[review]` sources are named explicitly; scout never scans a whole drive, system/app dirs, or orbit's own tree.
- `[review]` dedup on ingest: byte-identical files already in orbit are skipped, not re-imported.
- `[review]` scout never deletes a source file; unsure files become question rows, never guessed in.
- `[test:check_structure]` top-level area folders match the Areas table 1:1 (tombstone rows excluded) — no rogue directories, no missing areas.
- `[test:check_structure]` area numbers are two-digit multiples of 10, unique, with `00-inbox/` present.
- `[test:check_structure]` area count ≤ 8 passes (warning from 7); the 9th area fails the lint.
- `[test:check_triage]` triage never loses a file: files before = files after; unclear files remain in `00-inbox/`.
- `[review]` moves are renames, never copy+delete; collisions get `-2`, `-3`, … suffixes, never overwrite.
- `[review]` renumbering is a deliberate migration (change order + tombstone), and a tombstoned number is never reused for a different subject.
- `[review]` a new area requires immediate files + a non-overlapping What-belongs row.
- `[—]` the change order (contract → tree → lint) is mandatory for any restructure.

## Behavioral Contract

- `[test:check_scout]` given fixture source roots (`desktop`/`downloads` tagged `dump`, `onedrive-sync` tagged `live`), when scout runs → the four work files land in `00-inbox/` each with a provenance entry, the installer + photo stay behind, the dump files leave their source, and the live file is copied (original preserved).
- `[test:check_triage]` given the fixture inbox (12 files), when triage runs per the decision procedure → 10 files land at their exact homes, `IMG_2041.png` + `notes.txt` remain in inbox, none lost or invented.
- `[test:check_structure]` given a tree with a rogue top-level directory or a missing area, when the lint runs → FAIL naming the offender.

## Gotchas

- A file matching two areas means the Areas table is broken, not the file — fix the What-belongs rows (via `area-architect`), don't special-case in a skill.
- The populated work instance drifts by hand-filing: run `check_structure.py` there too; it needs only this SPEC + Python stdlib.

## OPEN

- OPEN: deep-archive policy for old years (e.g. `10-daily/2019/` after N years — zip? separate cold area?) — decide when the tree is populated at work.
- OPEN: does `30-operations/` need per-system subfolders once real volume arrives?

---

Skills executing this contract: `skills/file-scout/` (intake from the wild), `skills/file-triage/` (sorting), `skills/file-find/` (retrieval — the decision procedure run forward over an ask), `skills/area-architect/` (restructuring).
