# SPEC — filing (the orbit filing contract)

The compact agent-loadable contract for the `filing` domain: **where a file goes** and
**what the area tree may look like**. Skills (`file-triage`, `area-architect`) execute
this contract and carry no rules of their own — change filing behavior *here*.
Humans follow the same tables when filing by hand.

**Gate:**
```bash
python tests/check_structure.py .            # structure lint: tree ↔ this contract, numbering, budget
python tests/check_triage.py <scratch>       # behavior: fixture sort per the decision procedure
```

## Core Definition

A valid orbit instance is a directory tree whose top layer contains **exactly the areas
in the table below** (plus `.git`/`.gravity`/`skills`/`tests` and the root docs), where
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

<!-- Retired areas stay in this table with "(retired YYYY-MM-DD)" in the What-belongs cell
     and no folder on disk — the number is a tombstone, never reused. check_structure.py
     skips such rows. -->

## Minimal Shape

The smallest correctly-filed slice — copy this pattern when creating destinations:

```text
00-inbox/                                            # empty after triage, or holding files + questions
10-daily/2026/07/2026-07-03-daily-worklog.md         # day-dated → YYYY/MM/
10-daily/2026/2026-W27-weekly-report.md              # week-scoped → YYYY/
40-projects/erp-upgrade/erp-upgrade-vendor-proposal.pdf   # one kebab slug folder per project
```

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
- **Rename** — the name may clarify; **the number never changes** (10 years of muscle memory and links depend on it).
- **Repurpose / merge / split** — allowed only after every affected file is rehomed first; never orphans.
- **Retire** — files rehomed, folder removed, **the number is never reused**: the row stays in the Areas table as a tombstone `(retired YYYY-MM-DD)` so year-8 you knows why a number is missing.
- **Change order — contract before tree:** 1. edit this SPEC (table + tombstones) → 2. create/rename folders to match → 3. run `check_structure.py` → green. The tree is never ahead of the contract.

## Naming

- Kebab-case; no spaces, no leading dots/numbers except the area prefix.
- Dated material: `YYYY-MM-DD-<topic>.<ext>` (week-scoped: `YYYY-Www-<topic>`).
- Project slugs: short kebab (`erp-upgrade`, not `ERP Upgrade Project 2026`).
- Triage may **rename to conform** only when the mapping is lossless and obvious (`Weekly Report 2026-07-03.docx` → `2026-07-03-weekly-report.docx`); otherwise keep the original name.

## Rules

- `[test:check_structure]` top-level area folders match the Areas table 1:1 (tombstone rows excluded) — no rogue directories, no missing areas.
- `[test:check_structure]` area numbers are two-digit multiples of 10, unique, with `00-inbox/` present.
- `[test:check_structure]` area count ≤ 8 passes (warning from 7); the 9th area fails the lint.
- `[test:check_triage]` triage never loses a file: files before = files after; unclear files remain in `00-inbox/`.
- `[review]` moves are renames, never copy+delete; collisions get `-2`, `-3`, … suffixes, never overwrite.
- `[review]` a rename never changes an area's number; a retired number is never reused.
- `[review]` a new area requires immediate files + a non-overlapping What-belongs row.
- `[—]` the change order (contract → tree → lint) is mandatory for any restructure.

## Behavioral Contract

- `[test:check_triage]` given the fixture inbox (12 files), when triage runs per the decision procedure → 10 files land at their exact homes, `IMG_2041.png` + `notes.txt` remain in inbox, none lost or invented.
- `[test:check_structure]` given a tree with a rogue top-level directory or a missing area, when the lint runs → FAIL naming the offender.

## Gotchas

- A file matching two areas means the Areas table is broken, not the file — fix the What-belongs rows (via `area-architect`), don't special-case in a skill.
- The populated work instance drifts by hand-filing: run `check_structure.py` there too; it needs only this SPEC + Python stdlib.

## OPEN

- OPEN: deep-archive policy for old years (e.g. `10-daily/2019/` after N years — zip? separate cold area?) — decide when the tree is populated at work.
- OPEN: does `30-operations/` need per-system subfolders once real volume arrives?

---

Skills executing this contract: `skills/file-triage/` (sorting), `skills/area-architect/` (restructuring).
