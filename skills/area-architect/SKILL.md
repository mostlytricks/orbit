---
name: area-architect
description: Review and restructure orbit's top-level area architecture — audit tree vs contract, add/rename/merge/retire areas per the lifecycle rules, and push back against top-layer sprawl.
---

# area-architect

Keeps the top layer of an orbit instance small, named right, and matched to the filing
contract. The lifecycle rules and budget live in `.gravity/filing/SPEC.md` ("Area
lifecycle & top-layer budget") — **this skill contains no rules of its own**.

## Procedure

1. **Load the contract.** Read `.gravity/filing/SPEC.md` from the orbit root. If it
   can't be found, stop — never restructure without it.
2. **Inventory.** For each top-level directory: name, file count (recursive), depth,
   and whether it's in the contract's Areas table. Run
   `python tests/check_structure.py .` and include its output.
3. **Diagnose** against the contract: rogue directories, missing areas, tombstone
   violations, overlapping What-belongs rows (two areas that could claim the same
   file), budget pressure, and names that no longer describe their contents.
4. **Propose a plan** — one table: `change (add/rename/merge/split/retire) → area →
   justification (the lifecycle rule that allows it) → files affected`. For a
   requested **new area**, the default answer is **push back**: name the existing
   area + subfolder where it fits, and require the two Add conditions (immediate
   files, non-overlapping row) to be met before agreeing. **Wait for approval.**
5. **Execute in the change order — contract before tree:**
   a. edit the SPEC's Areas table (and tombstones) first;
   b. then create/rename folders to match (renames via `mv`/`git mv`, files rehomed
      before a merge/split/retire — never orphaned, never deleted);
   c. then `python tests/check_structure.py .` → must PASS.
6. **Regenerate the browsing cards.** `python skills/area-architect/generate_cards.py .`
   — refreshes each area's `README.md` from the (just-edited) contract so a rename/add
   picks up new text and a retired area's folder takes its card with it. The cards are a
   generated artifact (gitignored, like `dashboard.html`); never hand-edit one.
7. **Report.** What changed, the lint output, and any files that still need triage
   into restructured areas.

## Never

- Never delete a file; retiring an area means rehoming its contents first.
- Never change an area's number, and never reuse a retired number.
- Never create a top-level directory that isn't in an approved plan.
- Never leave the tree and the contract disagreeing — the lint must end green.
