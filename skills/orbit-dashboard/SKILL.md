---
name: orbit-dashboard
description: Generate orbit's tree-health dashboard — one self-contained HTML file showing contract verdict, inbox backlog, top-layer budget, area census, and recent activity.
---

# orbit-dashboard

Renders the health of an orbit instance as a single static HTML page. Monitoring
only — it changes nothing. Follows the astra `dashboarding` skill rules: one file,
zero external resources, generated never hand-edited, one question per panel.

## Procedure

1. From the orbit root (design instance or the populated work copy), run:
   ```bash
   python skills/orbit-dashboard/generate.py
   ```
   Optional: `<root>` as first arg, `-o <file>` for a different output path.
2. Open `dashboard.html` in a browser. Panels answer, in order:
   - **Does the tree match the contract?** — live `check_structure.py` verdict.
   - **Is triage keeping up?** — inbox backlog count + oldest file age.
   - **How close to the ceiling?** — area count vs the 7/9 budget, slot chips.
   - **Where does the mass live?** — files + size per area.
   - **What changed lately?** — the 10 most recent files.
3. Regenerate whenever you want fresh numbers — the file is disposable output
   (gitignored), never a source.

## Never

- Never hand-edit `dashboard.html` — fix the generator or the tree, then regenerate.
- Never add external resources (CDN, web fonts) to the generator's HTML — it must
  render on an offline intranet.
- Never let the dashboard mutate the tree — it is read-only by contract.
