# FILING — the orbit filing contract

The one source of truth for **where a file goes**. Agents load this before sorting
anything; humans follow it when filing by hand. Change filing behavior *here*, never
inside a skill. (Seam statement: CLAUDE.md Entry Points.)

## The areas

| Area | What belongs | What does NOT |
|---|---|---|
| `00-inbox/` | Everything unsorted. The **only** drop zone — files enter orbit here and leave via triage. | Nothing lives here long-term. |
| `10-daily/` | Recurring personal work: daily worklogs, weekly reports, routine checklists, chore records. Nested `YYYY/` and, for day-dated files, `YYYY/MM/`. | System procedures (→ 30), project status (→ 40). |
| `20-design/` | Architecture & design: decision records, system/solution designs, diagrams, tech standards and patterns. | Operational how-to (→ 30). |
| `30-operations/` | Running systems: runbooks, incident reports, maintenance/patch records, monitoring, DR plans. | One-off project deliverables (→ 40). |
| `40-projects/` | Everything belonging to a named project, one folder per project: `40-projects/<project-slug>/` — plans, meeting notes, vendor docs, status reports. | Recurring personal reports (→ 10). |
| `50-policy/` | Corporate policy, security policy, compliance, official process documents. | Your own conventions (→ 20 as a standard). |

## Decision procedure (for triage)

Classify each file **from its name and, when readable, its content** — in this order:

1. **Named project?** File mentions a known project (existing `40-projects/<slug>/` folder) → that folder. Clearly a project but no folder yet → **propose** the new `<slug>/`, don't silently invent taxonomy.
2. **Policy?** Official corporate/security/compliance document → `50-policy/`.
3. **Design vs operations:** *decision or blueprint* → `20-design/`; *procedure, incident, or record of running systems* → `30-operations/`.
4. **Personal recurring rhythm** (worklog, weekly report, routine checklist) → `10-daily/YYYY/` (day-dated → `YYYY/MM/`, year from the filename date, else file mtime).
5. **Unclear → it stays in `00-inbox/`** with a one-line question attached to the triage report. Never guess. Never delete. (Mission wall — CLAUDE.md Why.)

**Moves are renames, never copies or deletes.** Name collision at the destination → append `-2`, `-3`, … before the extension; never overwrite.

## Naming

- Kebab-case; no spaces, no leading dots/numbers except the area prefix.
- Dated material: `YYYY-MM-DD-<topic>.<ext>` (week-scoped: `YYYY-Www-<topic>`).
- Project slugs: short kebab (`erp-upgrade`, not `ERP Upgrade Project 2026`).
- Triage may **rename to conform** only when the mapping is lossless and obvious (`Weekly Report 2026-07-03.docx` → `2026-07-03-weekly-report.docx`); otherwise keep the original name.

## OPEN

- OPEN: deep-archive policy for old years (e.g. `10-daily/2019/` after N years — zip? separate cold area?) — decide when the tree is populated at work.
- OPEN: does `30-operations/` need per-system subfolders once real volume arrives?
