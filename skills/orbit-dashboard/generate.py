"""Generate dashboard.html — orbit tree health as one self-contained HTML file.

Usage:
    python skills/orbit-dashboard/generate.py [orbit-root] [-o output.html]

Defaults: root = current directory, output = <root>/dashboard.html.
Follows the astra `dashboarding` skill rules: one file, zero external resources,
generated never hand-edited, one question per panel, numbers get context.
Stdlib only — runs on the populated work instance too.
"""

import html
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

INBOX = "00-inbox"


def area_dirs(root: Path) -> list[Path]:
    return sorted(d for d in root.iterdir() if d.is_dir() and d.name[:1].isdigit())


def files_of(d: Path) -> list[Path]:
    return [p for p in d.rglob("*") if p.is_file() and p.name != ".gitkeep"]


def human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n} B"


def age_days(p: Path) -> int:
    return int((time.time() - p.stat().st_mtime) / 86400)


def lint(root: Path) -> tuple[bool, str]:
    script = root / "tests" / "check_structure.py"
    if not script.is_file():
        return False, "tests/check_structure.py not found — cannot verify the contract"
    r = subprocess.run([sys.executable, str(script), str(root)],
                       capture_output=True, text=True)
    return r.returncode == 0, (r.stdout + r.stderr).strip()


def main() -> int:
    args = [a for a in sys.argv[1:]]
    out = None
    if "-o" in args:
        i = args.index("-o")
        out = Path(args[i + 1])
        del args[i:i + 2]
    root = Path(args[0]) if args else Path(".")
    out = out or root / "dashboard.html"

    areas = area_dirs(root)
    census = [(d.name, files_of(d)) for d in areas]
    inbox_files = dict(census).get(INBOX, [])
    total = sum(len(f) for _, f in census)
    ok, lint_out = lint(root)

    all_files = [p for _, fs in census for p in fs]
    recent = sorted(all_files, key=lambda p: p.stat().st_mtime, reverse=True)[:10]

    n_areas = len(areas)
    slots = [f"{i:02d}" for i in range(10, 100, 10)]
    used = {d.name[:2] for d in areas}

    inbox_n = len(inbox_files)
    oldest = max((age_days(p) for p in inbox_files), default=0)
    inbox_cls = "ok" if inbox_n == 0 else ("warn" if oldest < 7 else "bad")
    budget_cls = "ok" if n_areas < 7 else ("warn" if n_areas < 9 else "bad")
    max_count = max((len(f) for _, f in census), default=1) or 1

    def bar_rows() -> str:
        rows = []
        for name, fs in census:
            w = int(100 * len(fs) / max_count) if fs else 0
            size = human_size(sum(p.stat().st_size for p in fs))
            rows.append(
                f'<div class="brow"><span class="mono lbl">{html.escape(name)}</span>'
                f'<span class="track"><span class="fill" style="width:{w}%"></span></span>'
                f'<span class="mono num">{len(fs)} files · {size}</span></div>')
        return "\n".join(rows)

    def recent_rows() -> str:
        if not recent:
            return '<p class="dim">no files in the areas yet — the design instance is empty by design</p>'
        rows = []
        for p in recent:
            rel = p.relative_to(root).as_posix()
            d = datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d")
            rows.append(f'<div class="frow"><span class="mono">{html.escape(rel)}</span>'
                        f'<span class="mono dim">{d}</span></div>')
        return "\n".join(rows)

    def slot_chips() -> str:
        chips = ['<span class="slot used mono">00</span>' if "00" in used
                 else '<span class="slot bad mono">00!</span>']
        for s in slots:
            cls = "used" if s in used else "free"
            chips.append(f'<span class="slot {cls} mono">{s}</span>')
        return "\n".join(chips)

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    doc = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>orbit — tree health</title>
<style>
:root {{ --bg:#08090c; --card:#12151d; --line:#1e2330; --ink:#e8ebf4; --dim:#9aa3ba;
  --ok:#4ade80; --warn:#fbbf24; --bad:#f87171; --accent:#8ab4ff;
  --mono:"Cascadia Code",Consolas,monospace; }}
* {{ box-sizing:border-box; margin:0; }}
body {{ background:var(--bg); color:var(--ink); font:15px/1.6 system-ui,"Segoe UI",sans-serif; padding:32px 24px; max-width:960px; margin:0 auto; }}
h1 {{ font-size:22px; letter-spacing:-.5px; }} h1 .mono {{ color:var(--accent); }}
.sub {{ color:var(--dim); font-size:13px; margin-bottom:24px; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:16px; }}
.panel {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:18px; }}
.panel h2 {{ font-size:12px; text-transform:uppercase; letter-spacing:2px; color:var(--dim); margin-bottom:10px; }}
.big {{ font-size:34px; font-family:var(--mono); }}
.ctx {{ color:var(--dim); font-size:13px; }}
.mono {{ font-family:var(--mono); font-size:13px; }}
.dim {{ color:var(--dim); }}
.ok {{ color:var(--ok); }} .warn {{ color:var(--warn); }} .bad {{ color:var(--bad); }}
.wide {{ grid-column:1/-1; }}
.brow,.frow {{ display:flex; align-items:center; gap:10px; padding:4px 0; }}
.lbl {{ width:130px; }} .num {{ color:var(--dim); white-space:nowrap; }}
.track {{ flex:1; height:8px; background:var(--bg); border-radius:4px; overflow:hidden; }}
.fill {{ display:block; height:100%; background:var(--accent); }}
.frow {{ justify-content:space-between; border-bottom:1px solid var(--line); }}
.slot {{ display:inline-block; padding:2px 8px; border-radius:6px; border:1px solid var(--line); margin:2px; }}
.slot.used {{ color:var(--accent); border-color:var(--accent); }}
.slot.free {{ color:var(--dim); opacity:.45; }} .slot.bad {{ color:var(--bad); border-color:var(--bad); }}
pre {{ background:var(--bg); border:1px solid var(--line); border-radius:8px; padding:10px; font:12px/1.5 var(--mono); overflow-x:auto; white-space:pre-wrap; }}
footer {{ margin-top:24px; color:var(--dim); font-size:12px; }}
</style></head><body>
<h1><span class="mono">✦ orbit</span> tree health</h1>
<p class="sub">generated {stamp} · root <span class="mono">{html.escape(str(root.resolve()))}</span> · do not hand-edit</p>
<div class="grid">
  <div class="panel"><h2>Does the tree match the contract?</h2>
    <div class="big {'ok' if ok else 'bad'}">{'PASS' if ok else 'FAIL'}</div>
    <pre>{html.escape(lint_out)}</pre></div>
  <div class="panel"><h2>Is triage keeping up?</h2>
    <div class="big {inbox_cls}">{inbox_n}</div>
    <p class="ctx">files waiting in 00-inbox · oldest {oldest}d — target is 0 after each triage</p></div>
  <div class="panel"><h2>How close to the ceiling?</h2>
    <div class="big {budget_cls}">{n_areas}<span class="ctx"> areas</span></div>
    <p class="ctx">warn at 7 · fail at 9 — width is expensive, depth is cheap</p>
    <div>{slot_chips()}</div></div>
  <div class="panel wide"><h2>Where does the mass live?</h2>
    {bar_rows()}
    <p class="ctx" style="margin-top:8px">{total} files across {n_areas} areas</p></div>
  <div class="panel wide"><h2>What changed lately?</h2>
    {recent_rows()}</div>
</div>
<footer>orbit-dashboard · self-contained (zero external resources) · regenerate: <span class="mono">python skills/orbit-dashboard/generate.py</span></footer>
</body></html>
"""
    out.write_text(doc, encoding="utf-8")
    # console output stays ASCII-only: Korean-Windows consoles default to cp949
    print(f"wrote {out} ({len(doc):,} bytes) - lint {'PASS' if ok else 'FAIL'}, "
          f"{total} files, inbox {inbox_n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
