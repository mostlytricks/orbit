---
name: locate
description: Answer "where is X?" in an orbit tree cheaply — read the generated waypoint index of curated directories and route to the right path without listing or reading payload files. Use for location/retrieval questions over a deep tree.
---

# locate

Answers location questions ("where's the 2026 architecture guideline?", "which folder
holds the ERP vendor contracts?") over a large orbit tree **without walking payload** —
the token-bomb this skill exists to avoid. It reads only the generated waypoint index. The
manifest schema and the read-index-never-tree rule live in `.gravity/waypoint/SPEC.md`;
this skill carries none of its own.

## Procedure

1. **Read the index.** Open `waypoint-index.md` at the orbit root. If it is missing or
   looks stale, rebuild it first: `python skills/locate/build_index.py .` — a bounded
   filesystem scan that costs *you* no tokens. Never substitute an `ls` of the tree.
2. **Match the query** against the index rows: `period` (year/range), then `keywords`,
   then `purpose` text. Prefer an exact period + keyword overlap.
3. **Answer with the path(s).** Return the winning curated-directory path and its
   purpose. For more detail, open *at most* the single matched `_waypoint.md` — never list
   the directory's contents to answer "where is X".
4. **No match?** Say so and offer to (a) rebuild the index, or (b) curate the likely
   directory — add an `_waypoint.md` per the SPEC's "When to curate" gate. Never guess a
   path by scanning the payload.

## Maintain the index

`python skills/locate/build_index.py .` rebuilds `waypoint-index.md` from every `_waypoint.md`
in the tree, filling in each curated directory's file-count and size. Run it after adding
or editing manifests, or after a big content change. The index is a generated artifact
(gitignored) — never hand-edit it.

## Never

- Never `ls` or read a curated directory's payload to answer a location question — that
  is the exact cost this skill removes. Route by the index.
- Never hand-edit `waypoint-index.md`; regenerate it.
- Never return a path that isn't backed by an index row.
