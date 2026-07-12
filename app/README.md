# Orbit Deck

The desktop shell for orbit — see the tree without a terminal. Three panes:

- **Areas** — live explorer over the numbered tree (auto-refreshes on file changes;
  inbox badge turns amber when files wait). Double-click opens a file.
- **Tree health** — the existing `orbit-dashboard` page, regenerated on demand and
  embedded (spawns `python skills/orbit-dashboard/generate.py` under your root).
- **Agent** — chat with Claude about the tree. Each message runs the **Claude Code
  CLI** (`claude -p --output-format stream-json`) with your orbit root as cwd, so the
  real orbit skills apply; tool calls stream in as a working-process timeline. The
  session resumes across messages; **new** starts fresh.

No server, no telemetry, nothing leaves the machine except what the Claude CLI itself
does. Config lives in one JSON under your user profile.

## The orbit theme (celestial micro-interactions)

The wordmark is a burning comet, the tree floats over a faint pure-CSS starfield, and
the explorer *narrates* change: a file or directory that **leaves** the tree burns up
like a meteor (streak + ember fade) before the tree closes over the gap; something that
**arrives** lands with a touchdown glow; the inbox badge fires a shockwave when new
files drop in. Important boundary: **Deck never deletes anything** — the meteor is not
a delete button, it is the animation for removals Deck *observes* (you deleted in
Explorer, or triage moved a file to its home). All effects respect
`prefers-reduced-motion`.

## Requirements on the target machine

- Windows 10/11 (portable zip — unzip anywhere, run `OrbitDeck.exe`; no installer/admin).
- **Python 3.x** on PATH (for the dashboard) — same requirement orbit already has.
- **Claude Code CLI** installed and signed in (for the agent panel only; the tree and
  dashboard work without it).

## Agent permissions

Settings → *Agent permissions*:

| Mode | Meaning |
|---|---|
| plan only | agent proposes; never touches files |
| accept edits *(default)* | file moves/writes auto-approved — what file-triage needs |
| bypass all | no permission gates; use only if you know why |

The agent runs headless (`-p`), so there is no interactive permission prompt — pick the
mode that matches your trust level. `plan only` is the safe demo mode.

## Build

The Windows portable zip is built by CI (`.github/workflows/build-deck.yml` — run the
`build-orbit-deck` workflow, download the `OrbitDeck-win-portable` artifact). Locally:

```bash
cd app
npm ci
npm test          # smoke: scanner + renderer UI in headless Chromium (no Electron needed)
npm start         # run the app (needs the Electron binary, i.e. normal internet)
npm run dist:win  # package the Windows portable zip (dist/)
```

Dev override: `ORBIT_DECK_ROOT=/path/to/orbit npm start` pins the root without clicking.
