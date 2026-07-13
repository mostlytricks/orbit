"""Generate dashboard.html — orbit tree health as one self-contained HTML file.

Usage:
    python skills/orbit-dashboard/generate.py [orbit-root] [-o output.html] [--open]

Defaults: root = current directory, output = <root>/dashboard.html.
--open (or -O) launches the written file in the default browser (stdlib webbrowser).
Follows the astra `dashboarding` skill rules: one file, zero external resources,
generated never hand-edited, one question per panel, numbers get context.
Stdlib only - runs on the populated work instance too. Console output stays
ASCII-only (Korean-Windows consoles default to cp949).
"""

import hashlib
import os
import html
import subprocess
import sys
import time
import webbrowser
from datetime import datetime
from pathlib import Path

INBOX = "00-inbox"
HEAVY_TOP = 15          # rows in the heavy-files panel
BIG_BYTES = 5 * 2**20   # "huge" threshold for cleanup candidates: 5 MB
STALE_DAYS = 180        # "useless" threshold: untouched this long
PALETTE = ["#8ab4ff", "#b48aff", "#4ade80", "#fbbf24", "#f87171",
           "#38bdf8", "#fb923c", "#5c6478"]


def esc(s) -> str:
    return html.escape(str(s))


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:,.0f} {unit}" if unit == "B" else f"{n:,.1f} {unit}"
        n /= 1024
    return f"{n} B"


def collect(root: Path):
    """One pass over the areas via os.scandir - DirEntry.stat() is free on Windows
    (served from the directory read; no per-file syscall or AV hook), which keeps
    40k-file directories at seconds, not minutes."""
    rows = []
    for d in sorted(root.iterdir()):
        if d.is_dir() and d.name[:1].isdigit():
            area = d.name
            stack = [str(d)]
            while stack:
                cur = stack.pop()
                try:
                    entries = os.scandir(cur)
                except OSError:
                    continue
                with entries:
                    for e in entries:
                        try:
                            if e.is_dir(follow_symlinks=False):
                                stack.append(e.path)
                                continue
                            if e.name == ".gitkeep":
                                continue
                            st = e.stat(follow_symlinks=False)
                        except OSError:
                            continue
                        rows.append((Path(e.path), st.st_size, st.st_mtime, area))
    return rows


def find_dupes(rows):
    """Exact duplicates: group by size, then md5 only within same-size groups."""
    by_size = {}
    for p, size, _, _ in rows:
        if size > 0:
            by_size.setdefault(size, []).append(p)
    groups = []
    for size, paths in by_size.items():
        if len(paths) < 2:
            continue
        by_hash = {}
        for p in paths:
            h = hashlib.md5()
            with open(p, "rb") as f:
                for chunk in iter(lambda: f.read(1 << 20), b""):
                    h.update(chunk)
            by_hash.setdefault(h.hexdigest(), []).append(p)
        groups += [(size, ps) for ps in by_hash.values() if len(ps) > 1]
    return sorted(groups, key=lambda g: g[0] * (len(g[1]) - 1), reverse=True)


def lint(root: Path):
    script = root / "tests" / "check_structure.py"
    if not script.is_file():
        return False, "tests/check_structure.py not found - cannot verify the contract"
    r = subprocess.run([sys.executable, str(script), str(root)],
                       capture_output=True, text=True)
    return r.returncode == 0, (r.stdout + r.stderr).strip()


def main() -> int:
    args = list(sys.argv[1:])
    open_after = False
    for flag in ("--open", "-O"):
        while flag in args:
            args.remove(flag)
            open_after = True
    out = None
    if "-o" in args:
        i = args.index("-o")
        out = Path(args[i + 1])
        del args[i:i + 2]
    root = Path(args[0]) if args else Path(".")
    out = out or root / "dashboard.html"

    now = time.time()
    rows = collect(root)
    areas = sorted({a for *_, a in rows} | {d.name for d in root.iterdir()
                                            if d.is_dir() and d.name[:1].isdigit()})
    ok, lint_out = lint(root)

    total_files = len(rows)
    total_bytes = sum(s for _, s, _, _ in rows)
    inbox = [(p, s, m) for p, s, m, a in rows if a == INBOX]
    oldest_inbox = max((int((now - m) / 86400) for *_, m in inbox), default=0)

    heavy = sorted(rows, key=lambda r: r[1], reverse=True)[:HEAVY_TOP]
    candidates = sorted(
        (r for r in rows if r[1] >= BIG_BYTES and (now - r[2]) / 86400 >= STALE_DAYS),
        key=lambda r: r[1] * (now - r[2]), reverse=True)[:HEAVY_TOP]
    dupes = find_dupes(rows)
    dupe_waste = sum(size * (len(ps) - 1) for size, ps in dupes)

    ext, years, census = {}, {}, {}
    for p, size, mtime, area in rows:
        e = p.suffix.lower() or "(none)"
        ext[e] = (ext.get(e, (0, 0))[0] + size, ext[e][1] + 1 if e in ext else 1)
        y = datetime.fromtimestamp(mtime).year
        years[y] = (years.get(y, (0, 0))[0] + 1, years.get(y, (0, 0))[1] + size)
        census[area] = (census.get(area, (0, 0))[0] + 1, census.get(area, (0, 0))[1] + size)
    for a in areas:
        census.setdefault(a, (0, 0))
    recent = sorted(rows, key=lambda r: r[2], reverse=True)[:10]

    n_areas = len(areas)
    used = {a[:2] for a in areas}
    inbox_cls = "ok" if not inbox else ("warn" if oldest_inbox < 7 else "bad")
    budget_cls = "ok" if n_areas < 7 else ("warn" if n_areas < 9 else "bad")

    # --- render helpers -----------------------------------------------------
    def age_label(mtime: float) -> str:
        d = int((now - mtime) / 86400)
        return f"{d // 365}y {d % 365 // 30}mo" if d >= 365 else (f"{d // 30}mo" if d >= 30 else f"{d}d")

    def file_rows(items, score=False) -> str:
        if not items:
            return '<p class="dim empty">nothing here - clean tree</p>'
        mx = max(s for _, s, *_ in items) or 1
        out_ = []
        for p, size, mtime, _a in items:
            stale = (now - mtime) / 86400 >= STALE_DAYS
            mark = ' <span class="tag bad">stale</span>' if stale and score else ""
            out_.append(
                f'<div class="frow"><span class="cell path mono">{esc(p.relative_to(root).as_posix())}{mark}</span>'
                f'<span class="cell track"><span class="fill" style="width:{int(100 * size / mx)}%"></span></span>'
                f'<span class="cell mono dim">{human(size)} · {age_label(mtime)}</span></div>')
        return "\n".join(out_)

    def dupe_rows() -> str:
        if not dupes:
            return '<p class="dim empty">no exact duplicates found</p>'
        out_ = []
        for size, ps in dupes[:8]:
            shown = ps[:6]
            paths = "<br>".join(esc(p.relative_to(root).as_posix()) for p in shown)
            if len(ps) > len(shown):
                paths += f"<br>&hellip; and {len(ps) - len(shown):,} more copies"
            out_.append(f'<div class="dgroup"><span class="tag warn">{len(ps)}x · {human(size)}</span>'
                        f'<div class="mono dim dpaths">{paths}</div></div>')
        return "\n".join(out_)

    def donut() -> str:
        if not total_bytes:
            return '<p class="dim empty">no bytes yet</p>'
        top = sorted(ext.items(), key=lambda kv: kv[1][0], reverse=True)
        slices = top[:7]
        other = sum(sz for _, (sz, _) in top[7:])
        if other:
            slices.append(("(other)", (other, sum(c for _, (_, c) in top[7:]))))
        C = 282.74  # circumference for r=45
        segs, legend, off = [], [], 0.0
        for i, (name, (sz, cnt)) in enumerate(slices):
            frac = sz / total_bytes
            segs.append(f'<circle r="45" cx="60" cy="60" fill="none" stroke="{PALETTE[i % 8]}" '
                        f'stroke-width="14" stroke-dasharray="{frac * C:.2f} {C:.2f}" '
                        f'stroke-dashoffset="{-off:.2f}" transform="rotate(-90 60 60)"/>')
            legend.append(f'<div class="lrow"><span class="dot" style="background:{PALETTE[i % 8]}"></span>'
                          f'<span class="mono">{esc(name)}</span>'
                          f'<span class="mono dim">{human(sz)} · {cnt}</span></div>')
            off += frac * C
        return (f'<div class="donutwrap"><svg viewBox="0 0 120 120" width="130" height="130">{"".join(segs)}'
                f'<text x="60" y="57" text-anchor="middle" class="dtxt">{esc(human(total_bytes))}</text>'
                f'<text x="60" y="72" text-anchor="middle" class="dsub">{total_files} files</text></svg>'
                f'<div class="legend">{"".join(legend)}</div></div>')

    def year_bars() -> str:
        if not years:
            return '<p class="dim empty">no files yet</p>'
        mx = max(c for c, _ in years.values()) or 1
        out_ = []
        for y in sorted(years, reverse=True):
            c, sz = years[y]
            out_.append(f'<div class="frow"><span class="cell mono lbl">{y}</span>'
                        f'<span class="cell track"><span class="fill alt" style="width:{int(100 * c / mx)}%"></span></span>'
                        f'<span class="cell mono dim">{c} files · {human(sz)}</span></div>')
        return "\n".join(out_)

    def census_rows() -> str:
        mx = max((c for c, _ in census.values()), default=1) or 1
        return "\n".join(
            f'<div class="frow"><span class="cell mono lbl">{esc(a)}</span>'
            f'<span class="cell track"><span class="fill" style="width:{int(100 * census[a][0] / mx)}%"></span></span>'
            f'<span class="cell mono dim">{census[a][0]} files · {human(census[a][1])}</span></div>'
            for a in sorted(census))

    def recent_rows() -> str:
        if not recent:
            return '<p class="dim empty">no files in the areas yet - the design instance is empty by design</p>'
        return "\n".join(
            f'<div class="frow"><span class="cell path mono">{esc(p.relative_to(root).as_posix())}</span>'
            f'<span class="cell mono dim">{datetime.fromtimestamp(m).strftime("%Y-%m-%d")}</span></div>'
            for p, _s, m, _a in recent)

    def slot_chips() -> str:
        chips = []
        for s in ["00"] + [f"{i}" for i in range(10, 100, 10)]:
            cls = "used" if s in used else "free"
            chips.append(f'<span class="slot {cls} mono">{s}</span>')
        return "\n".join(chips)

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    kpi = f"""
<div class="kpis">
  <div class="kpi"><span class="klabel">contract</span><span class="kval {'ok' if ok else 'bad'}">{'PASS' if ok else 'FAIL'}</span></div>
  <div class="kpi"><span class="klabel">files</span><span class="kval">{total_files:,}</span></div>
  <div class="kpi"><span class="klabel">size</span><span class="kval">{esc(human(total_bytes))}</span></div>
  <div class="kpi"><span class="klabel">areas</span><span class="kval {budget_cls}">{n_areas}<small>/9</small></span></div>
  <div class="kpi"><span class="klabel">inbox</span><span class="kval {inbox_cls}">{len(inbox)}</span></div>
  <div class="kpi"><span class="klabel">dupe waste</span><span class="kval {'warn' if dupe_waste else 'ok'}">{esc(human(dupe_waste))}</span></div>
</div>"""

    doc = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>orbit &mdash; tree health</title>
<style>
:root {{ --bg:#08090c; --panel:#101319; --card:#12151d; --line:#1e2330; --line2:#2a3145;
  --ink:#e8ebf4; --dim:#9aa3ba; --faint:#5c6478; --ok:#4ade80; --warn:#fbbf24; --bad:#f87171;
  --accent:#8ab4ff; --accent2:#b48aff; --mono:"Cascadia Code",Consolas,monospace; }}
* {{ box-sizing:border-box; margin:0; }}
body {{ background:var(--bg); color:var(--ink); font:15px/1.6 system-ui,"Segoe UI",sans-serif; }}
header {{ position:sticky; top:0; background:rgba(8,9,12,.88); backdrop-filter:blur(8px);
  border-bottom:1px solid var(--line); padding:14px 28px; display:flex; align-items:baseline; gap:14px; z-index:9; }}
header .wordmark {{ font:600 17px var(--mono); color:var(--ink); }} header .wordmark b {{ color:var(--accent2); font-weight:600; }}
header .meta {{ color:var(--faint); font:12px var(--mono); }}
main {{ max-width:1060px; margin:0 auto; padding:26px 24px 60px; }}
.kpis {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(130px,1fr)); gap:12px; margin-bottom:22px; }}
.kpi {{ background:linear-gradient(160deg,var(--panel),var(--card)); border:1px solid var(--line);
  border-radius:10px; padding:12px 16px; }}
.klabel {{ display:block; font:11px var(--mono); text-transform:uppercase; letter-spacing:2px; color:var(--faint); }}
.kval {{ font:600 26px var(--mono); }} .kval small {{ font-size:14px; color:var(--faint); }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(320px,1fr)); gap:16px; }}
.panel {{ background:var(--card); border:1px solid var(--line); border-radius:12px; padding:20px; }}
.panel:hover {{ border-color:var(--line2); }}
.panel h2 {{ font-size:12px; text-transform:uppercase; letter-spacing:2.5px; color:var(--faint);
  border-bottom:1px solid var(--line); padding-bottom:8px; margin-bottom:12px; }}
.panel .q {{ color:var(--dim); font-size:13px; margin-bottom:10px; }}
.wide {{ grid-column:1/-1; }}
.mono {{ font-family:var(--mono); font-size:12.5px; }} .dim {{ color:var(--dim); }} .empty {{ padding:8px 0; }}
.ok {{ color:var(--ok); }} .warn {{ color:var(--warn); }} .bad {{ color:var(--bad); }}
.frow {{ display:flex; align-items:center; gap:12px; padding:5px 0; border-bottom:1px solid var(--line); }}
.frow:last-child {{ border-bottom:none; }}
.cell.path {{ flex:2; overflow-wrap:anywhere; }} .cell.lbl {{ width:120px; }}
.cell.track {{ flex:1.2; height:8px; background:var(--bg); border-radius:4px; overflow:hidden; min-width:70px; }}
.fill {{ display:block; height:100%; background:linear-gradient(90deg,var(--accent),var(--accent2)); }}
.fill.alt {{ background:linear-gradient(90deg,var(--accent2),var(--accent)); }}
.cell.mono.dim {{ white-space:nowrap; }}
.tag {{ font:11px var(--mono); border:1px solid; border-radius:6px; padding:1px 7px; }}
.tag.bad {{ color:var(--bad); }} .tag.warn {{ color:var(--warn); }}
.dgroup {{ padding:8px 0; border-bottom:1px solid var(--line); }} .dgroup:last-child {{ border-bottom:none; }}
.dpaths {{ margin-top:4px; line-height:1.8; }}
.donutwrap {{ display:flex; gap:20px; align-items:center; flex-wrap:wrap; }}
.dtxt {{ fill:var(--ink); font:600 13px var(--mono); }} .dsub {{ fill:var(--faint); font:10px var(--mono); }}
.legend {{ flex:1; min-width:220px; }}
.lrow {{ display:flex; align-items:center; gap:8px; padding:3px 0; }} .lrow .mono:last-child {{ margin-left:auto; }}
.dot {{ width:9px; height:9px; border-radius:3px; flex:none; }}
.slot {{ display:inline-block; padding:2px 9px; border-radius:6px; border:1px solid var(--line); margin:2px; font-size:12px; }}
.slot.used {{ color:var(--accent); border-color:var(--accent); }} .slot.free {{ color:var(--faint); opacity:.4; }}
pre {{ background:var(--bg); border:1px solid var(--line); border-radius:8px; padding:10px;
  font:12px/1.5 var(--mono); overflow-x:auto; white-space:pre-wrap; color:var(--dim); }}
footer {{ text-align:center; color:var(--faint); font:12px var(--mono); padding:18px; border-top:1px solid var(--line); }}
</style></head><body>
<header><span class="wordmark"><b>&#10022;</b> orbit &middot; tree health</span>
<span class="meta">generated {stamp} &middot; {esc(root.resolve())}</span></header>
<main>
{kpi}
<div class="grid">
  <div class="panel wide"><h2>Cleanup candidates</h2>
    <p class="q">Which files are probably useless? &mdash; bigger than {esc(human(BIG_BYTES))} and untouched for {STALE_DAYS}+ days, ranked by size &times; staleness. <b>Review, never auto-delete</b> &mdash; orbit skills don't delete; keepers go to deep archive, junk you remove yourself.</p>
    {file_rows(candidates, score=True)}</div>
  <div class="panel"><h2>Heaviest files</h2>
    <p class="q">Where do the biggest bytes sit? &mdash; top {HEAVY_TOP} by size.</p>
    {file_rows([(p, s, m, a) for p, s, m, a in heavy])}</div>
  <div class="panel"><h2>Exact duplicates</h2>
    <p class="q">Same bytes stored twice? &mdash; md5-verified; waste = extra copies only.</p>
    {dupe_rows()}</div>
  <div class="panel"><h2>Where the bytes live, by type</h2>
    <p class="q">What kind of content dominates?</p>
    {donut()}</div>
  <div class="panel"><h2>Age profile</h2>
    <p class="q">How old is the archive? &mdash; files by modified year.</p>
    {year_bars()}</div>
  <div class="panel"><h2>Area census</h2>
    <p class="q">Where does the mass live?</p>
    {census_rows()}</div>
  <div class="panel"><h2>Top-layer budget</h2>
    <p class="q">How close to the ceiling? &mdash; warn at 7, fail at 9; width is expensive, depth is cheap.</p>
    <div>{slot_chips()}</div></div>
  <div class="panel"><h2>Contract verdict</h2>
    <p class="q">Does the tree match .gravity/filing/SPEC.md?</p>
    <pre>{esc(lint_out)}</pre></div>
  <div class="panel wide"><h2>Recent activity</h2>
    <p class="q">What changed lately? &mdash; 10 newest files. Inbox oldest: {oldest_inbox}d (target 0 after each triage).</p>
    {recent_rows()}</div>
</div>
</main>
<footer>orbit-dashboard &middot; self-contained, zero external resources &middot; regenerate:
python skills/orbit-dashboard/generate.py</footer>
</body></html>
"""
    out.write_text(doc, encoding="utf-8")
    print(f"wrote {out} ({len(doc):,} bytes) - lint {'PASS' if ok else 'FAIL'}, "
          f"{total_files} files, {human(total_bytes)}, inbox {len(inbox)}, "
          f"candidates {len(candidates)}, dupe groups {len(dupes)}")
    if open_after:
        webbrowser.open(out.resolve().as_uri())
        print(f"opened {out.resolve()} in the default browser")
    return 0


if __name__ == "__main__":
    sys.exit(main())
