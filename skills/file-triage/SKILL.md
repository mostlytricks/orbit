---
name: file-triage
description: Sort a messy directory (usually 00-inbox) into the orbit area structure per the filing contract — plan first, move never delete, leave unclassifiable files behind with a question.
---

# file-triage

Files every item in a target directory into the orbit areas, following the filing
contract. The contract lives in `.gravity/filing/SPEC.md` at the orbit root — **this
skill contains no filing rules of its own**; if sorting behavior should change,
change the SPEC.

## Procedure

1. **Load the contract.** Read `.gravity/filing/SPEC.md` from the orbit root (walk up
   from the target directory if needed). If it can't be found, stop — never sort
   without it.
2. **Inventory.** List every file in the target directory (default: `00-inbox/`).
   Note name, extension, and — for readable text files — a skim of the content.
3. **Classify** each file using the SPEC's decision procedure, in its order
   (project → policy → design/operations → daily → unclear). Record the destination
   *and the rule that fired*. Unclear means unclear: no confidence, no move.
4. **Present the plan** as a table — `file → destination (rule)` — including the
   "stays in inbox" rows with their questions. **Wait for approval** before moving
   anything (skip approval only if the user already said "just sort it").
5. **Execute.** Moves are renames (`mv`), never copy+delete. Create destination
   folders as needed (`YYYY/MM/`, new project slugs only if approved in the plan).
   Name collision → append `-2`, `-3`, … before the extension; never overwrite.
6. **Report.** Files moved (with destinations), files left in inbox (each with its
   one-line question), and a count check: files before = files after, nowhere lost.

## Never

- Never delete a file, for any reason. Not even duplicates — flag them instead.
- Never guess a destination for an unclear file — it stays in inbox with a question.
- Never invent a new area or project folder that isn't in the approved plan.
- Never touch files outside the target directory.
