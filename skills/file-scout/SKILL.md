---
name: file-scout
description: Gather work files scattered across other directories (Desktop, Downloads, old dumps) into orbit's 00-inbox — scan named source roots read-only, move from dumps / copy from live sources, dedup, record provenance, never delete a source. The front door before file-triage.
---

# file-scout

The **front door** to orbit: it brings files in from the wild (Desktop, Downloads,
Documents, an old `misc/` dump, a `D:\` folder) and lands them in `00-inbox/`, from
where `file-triage` sorts them into areas. The intake rules live in
`.gravity/filing/SPEC.md` ("Intake") — **this skill contains no filing rules of its
own**; if intake behavior should change, change the SPEC.

## Procedure

1. **Load the contract.** Read `.gravity/filing/SPEC.md` ("Intake" + the areas) from the
   orbit root. If it can't be found, stop — never ingest without it.
2. **Confirm the sources.** The user names each source root explicitly and tags it
   `dump` (move) or `live` (copy) — e.g. `~/Desktop=dump`, `~/Downloads=dump`,
   `~/OneDrive/active=live`. **Never** scan a whole drive, system/program/app-data
   dirs, or orbit's own tree. If a source isn't named, ask — don't guess a path.
3. **Scan read-only.** Walk each source root. Skip on sight: hidden files/dirs,
   `node_modules`, `.venv`, `__pycache__`, `.git`. For each remaining file note name,
   extension, size, and — for readable text — a content skim.
4. **Filter for relevance** per the SPEC: ingest work documents (notes, decisions,
   reports, policies, project files, spreadsheets, presentations, PDFs, archives);
   leave personal media, installers, app binaries, temp files. Unsure → a **question
   row**, decided by the human.
5. **Dedup.** md5 each candidate; if identical bytes already live anywhere in the orbit
   tree or already in `00-inbox/`, mark it "already filed — skip" (never re-import).
6. **Present the plan** as a table — `source path → action (move/copy) → 00-inbox/name
   → reason/flag` — including "skip" and "question" rows. **Wait for approval** (skip
   only if the user already said "just pull them in").
7. **Execute into `00-inbox/`:** `dump` source → **move** (`mv`); `live` source →
   **copy** (`cp`), original untouched. Name collision → append `-2`, `-3`, … before
   the extension; never overwrite. Append one line per ingested file to
   `00-inbox/.orbit-provenance.jsonl`: `{path, source, action, md5, date}`.
8. **Report + hand off.** Files ingested (with origin + action), files skipped (dedup,
   junk) and left in place, question rows still awaiting a call, and a count check.
   Then: "inbox has N new files — run `file-triage` to sort them."

## Never

- Never delete a source file. A `dump` move relocates it; a `live` copy leaves it.
  If a moved file can't reach the inbox, it stays where it is — never lost.
- Never scan an unnamed root, a system/program directory, or orbit's own tree.
- Never re-import a byte-identical file that orbit already holds.
- Never guess an unclear file in or out — it becomes a question row for the human.
- Never write filing decisions here — landing a file in `00-inbox/` is the whole job;
  `file-triage` decides its area.
