---
name: file-find
description: Retrieval — answer "where is X?" against an orbit tree. Parse the ask into the SPEC's own filing signals (project, nature, date, rhythm), predict the file's one home by running the decision procedure forward, search narrow-to-wide, and present ranked candidates with evidence. Read-only; a miss is reported as a filing diagnosis (never ingested / misfiled / ambiguous contract), never shrugged off. The acceptance test of the whole filing promise: "ten years later it's still findable."
---

# file-find

The flip side of `file-triage`: triage asks *"where does this file go?"*, find asks
*"where did it go?"* — and answers by running the **same** decision procedure in
`.gravity/filing/SPEC.md`, forward, over the question instead of the file. The place
the contract files things is the place to look. That is the whole design bet of
orbit, and this skill is what tests it: **every miss is a filing bug with an
address**, not bad luck.

Read-only by contract. Find never moves, renames, or deletes anything — a misfiled
file it stumbles on is *reported* as a triage candidate, never fixed silently.

## Procedure

### 1 — Parse the ask into filing signals

Take the question in the user's words ("the DR plan we wrote around 2023", "the
vendor proposal for the ERP upgrade", "last March's weekly reports") and extract
the same signals triage files by:

- **project** — a named project or something that smells like one (→ slug guess);
- **nature** — policy / design-decision / procedure-incident-record / recurring
  personal rhythm;
- **time** — a year, month, date, or range ("around 2023", "last spring");
- **content cues** — words likely *inside* the file (vendor name, system name)
  as distinct from words likely in its *name*.

### 2 — Predict the home

Run the SPEC decision procedure (steps 1–4) on those signals, exactly as triage
would: project → `40-projects/<slug>/`; policy → `50-policy/`; design vs
operations → `20-` vs `30-`; recurring rhythm → `10-daily/YYYY/(MM/)`. Note the
prediction *before* searching — it is the hypothesis being tested, and it's what
makes a miss diagnostic instead of noise.

### 3 — Search narrow → wide (stop as soon as you're confident)

1. **The predicted home**, using the naming conventions as the index: date
   prefixes (`YYYY-MM-DD-`, `YYYY-Www-`), kebab topic words, `YYYY/MM/` nesting,
   project slugs. This resolves most asks in one directory listing.
2. **Name search across the whole tree** — filename tokens from the ask, fuzzy on
   word order, tolerant of the pre-orbit names triage preserves when a rename
   wasn't lossless.
3. **Content search** in readable formats (text, md, csv, and whatever the host
   can read) for the content cues — scoped to the predicted area first, then the
   tree.
4. **The edges:** `00-inbox/` (it may still be awaiting triage — check open
   question rows) and `00-inbox/.orbit-provenance.jsonl` (it may have been
   ingested under a different name, or never ingested at all — provenance shows
   what scout has actually seen).

### 4 — Present candidates with evidence

Rank and show, never bare paths: for each candidate give **path · date · size ·
why it matches** (which signals hit). Multiple plausible candidates → show all of
them ranked; **never silently pick one**. If versions/duplicates surface, say
which is newest and note the duplication (dashboard's territory to quantify).

### 5 — Miss protocol (the part that earns the skill its keep)

"Not found" is never the whole answer. Report:

1. **Where it should have been** — the step-2 prediction, stated as a path.
2. **Which failure it looks like**, checked in this order:
   - *never ingested* — no trace in tree, inbox, or provenance → a `file-scout`
     gap: name the source directory probably still holding it;
   - *misfiled* — found, but somewhere the decision procedure wouldn't put it →
     report as a triage candidate (file + current path + predicted path);
   - *ambiguous contract* — the ask legitimately maps to two areas → the Areas
     table's What-belongs rows overlap for this case; that's `area-architect`
     input, cite both rows.
3. **The question row** — one line the user can answer to close the loop, same
   shape as triage's unclear-file questions.

## Never

- **Never mutate the tree.** No moves, renames, deletions, or "helpful" fixes —
  misfiles become triage candidates, not silent corrections.
- **Never guess a single answer.** Ambiguity is shown as ranked candidates;
  absence is shown as a miss report with a prediction. Confidence is earned by
  evidence, not asserted.
- **Never encode filing rules.** The prediction is computed from the live SPEC at
  ask-time; if find and triage would disagree about a home, the SPEC is broken —
  fix it there (Gotchas: a file matching two areas means the table is broken).
- **Never leak the provenance manifest.** It may name sensitive machine paths;
  quote from it only what the answer needs, never dump it.

## Gate (planned — not yet built)

A fixture tree (`tests/fixture-find/`) with planted files plus a query set with
expected answers: hits that must resolve to exact paths, near-misses that must
return ranked candidates, and true misses that must produce the right diagnosis
(never-ingested vs misfiled vs ambiguous). `tests/check_find.py` verifies the
skill's written answer report mechanically, like `check_triage` verifies a sorted
tree. Until that wall exists this skill is a draft.
