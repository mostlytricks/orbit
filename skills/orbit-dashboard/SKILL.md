---
name: orbit-dashboard
description: Generate orbit's tree-health dashboard — one self-contained HTML file with contract verdict, cleanup candidates (big + stale), exact duplicates, size-by-type, age profile, area census — and guide the hunt for useless huge files.
---

# orbit-dashboard

Renders the health of an orbit instance as a single static HTML page. Monitoring
only — it changes nothing. Follows the astra `dashboarding` skill rules: one file,
zero external resources, generated never hand-edited, one question per panel.

## Procedure

1. From the orbit root (design instance or the populated work copy), run:
   ```bash
   python skills/orbit-dashboard/generate.py --open   # generate AND open in browser
   ```
   Optional: `<root>` as first arg, `-o <file>` for a different output path,
   `--open` (or `-O`) to launch the result in the default browser (stdlib `webbrowser`;
   omit it for headless/CI use — the file is still written).
2. The dashboard opens (or open `dashboard.html` yourself). KPI strip first (contract · files · size ·
   areas/9 · inbox · dupe waste), then panels, each answering one question:
   - **Cleanup candidates** — probably-useless files: > 5 MB and untouched 180+ days, ranked by size × staleness.
   - **Heaviest files** — top 15 by size, with age.
   - **Exact duplicates** — md5-verified same-bytes groups; waste counts extra copies only.
   - **Where the bytes live, by type** — extension share donut.
   - **Age profile** — files by modified year (the 10-year cold mass).
   - **Area census · Top-layer budget · Contract verdict · Recent activity.**
3. Regenerate whenever you want fresh numbers — the file is disposable output
   (gitignored), never a source.

## Hunting useless huge files (the guide)

1. Start at the **dupe waste** KPI and the **Exact duplicates** panel: extra copies
   are the only files that are *provably* useless — keep one, remove the rest yourself.
2. Walk **Cleanup candidates** top-down (biggest × stalest first). For each, ask:
   - superseded? (a newer version exists elsewhere — check the project folder) → junk;
   - historical? (final deliverable, audit trail, contract) → keeper, leave in place
     or move to the deep-archive area when that exists (SPEC `OPEN`);
   - unknown? → open it before deciding; never judge by name alone.
3. Cross-check **by type**: installer/media extensions (`.iso`, `.zip`, `.mp4`)
   dominating an area usually means downloads that never belonged in orbit.
4. **The wall: orbit never deletes.** This skill only finds; *you* delete, outside
   the skills. Anything worth keeping but rarely touched is a deep-archive candidate,
   not a deletion.

## Never

- Never hand-edit `dashboard.html` — fix the generator or the tree, then regenerate.
- Never add external resources (CDN, web fonts) to the generator's HTML — it must
  render on an offline intranet.
- Never let the dashboard mutate the tree — it is read-only by contract; deletion
  advice is advice, executed by the human only.
