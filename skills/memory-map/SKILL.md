---
name: memory-map
description: Render the waypoint domain's face — a directory-level map of the orbit tree colored by MEMORY, not just mass: curated-and-fresh blocks lit with their manifest's purpose, stale ones flickering amber, big uncurated directories as dark territory whose click-card carries a ready-to-paste _waypoint.md skeleton. Answers "how much of my own tree have I forgotten?" at a glance. Read-only, self-contained HTML.
---

# memory-map

Every disk tool shows what's *big*; only orbit can show what you still *remember* —
the `_waypoint.md` manifests are the tree's curated memory, and this page makes their
coverage visible. Watching dark territory shrink over the years is the memory loop
made visible. Governed by `.gravity/waypoint/SPEC.md` (manifest schema, the opt-in
curation gate); this skill renders, it rules nothing.

## Procedure

1. From the orbit root (design instance or the populated work copy):
   ```bash
   python skills/memory-map/generate.py --open   # generate AND open memory-map.html
   ```
   Optional: `<root>` first arg, `-o <file>`, `--open`/`-O` (omit for headless).
2. Read the KPI strip first: **memory coverage** (curated mass / mass that deserves
   memory — lit + stale + dark), then fresh / stale / dark counts.
3. Walk the map. One tile per area subdirectory (depth 2, plus a loose-files tile),
   sized by recursive bytes, colored by state:
   - **lit** — has its own `_waypoint.md`, content older than it. Label = the
     manifest's purpose. `locate` routes here.
   - **stale** (amber flicker) — manifest exists but content is newer. Update the
     manifest, then `python skills/locate/build_index.py .`
   - **partial** (dashed) — no own manifest, but waypoints exist deeper; the card
     lists them.
   - **dark** — big (>= 15 files or >= 5 MB, a mechanical proxy for the SPEC's
     "expensive to scan" gate) and completely uncurated. The card carries a
     ready-to-paste `_waypoint.md` skeleton. SPEC rule verbatim: *either set a
     waypoint + clean it, or it's junk for cleanup.*
   - **neutral** — small and uncurated: fine as-is. **Do not manifest every
     folder** — the SPEC's anti-sprawl warning is the reason small dirs never
     render dark.
4. When the user asks you to act on a dark tile: draft the manifest *from the tile's
   actual contents* (open a few file names, not payloads, to describe the purpose),
   get it approved, save, rebuild the index, regenerate the map.

## Never

- Never hand-edit `memory-map.html` — fix the tree or the manifests, regenerate.
- Never auto-create manifests for every dark tile in one sweep — curation is
  deliberate (SPEC gate); one approved manifest at a time.
- Never read payload contents to build the map — sizes, counts, mtimes, and the
  manifests themselves only.
- Never add external resources — offline intranet, one self-contained file.
