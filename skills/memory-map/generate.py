"""Generate memory-map.html - the waypoint domain's face: a directory-level map
colored by MEMORY, not just mass.

Usage:
    python skills/memory-map/generate.py [orbit-root] [-o output.html] [--open]

One block per area subdirectory (depth 2, plus a loose-files block per area),
sized by recursive bytes and colored by memory state:
  lit     - has its own _waypoint.md, content older than the manifest (fresh memory)
  stale   - has a manifest, but content is newer than it (memory outdated)
  partial - no own manifest, but curated waypoints exist deeper inside
  dark    - big (>= 15 files or >= 5 MB) and completely uncurated: dark territory
  neutral - small and uncurated; fine as-is (the SPEC warns against manifest-sprawl)
Clicking a block opens a detail card; dark territory's card carries a ready-to-paste
_waypoint.md skeleton. Self-contained HTML (no CDN, inline CSS/JS), gitignored output,
stdlib only, ASCII console (cp949 safe). Read-only - signals and manifests, no payload.
"""

import html
import json
import sys
import webbrowser
from datetime import datetime
from pathlib import Path

DARK_FILES = 15
DARK_BYTES = 5 * 2**20


def esc(s) -> str:
    return html.escape(str(s))


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:,.0f} {unit}" if unit == "B" else f"{n:,.1f} {unit}"
        n /= 1024
    return f"{n} B"


def parse_manifest(p: Path):
    """purpose + keywords from _waypoint.md YAML frontmatter (line-level, stdlib)."""
    purpose, keywords, inside = "", "", False
    try:
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip() == "---":
                if inside:
                    break
                inside = True
                continue
            if inside and line.startswith("purpose:"):
                purpose = line.split(":", 1)[1].strip()
            elif inside and line.startswith("keywords:"):
                keywords = line.split(":", 1)[1].strip().strip("[]")
    except OSError:
        pass
    return purpose, keywords


def dir_stats(d: Path):
    """(bytes, files, newest_payload_mtime, deeper_manifest_paths) - one pass."""
    total, count, newest, deeper = 0, 0, 0.0, []
    for p in d.rglob("*"):
        if p.is_file():
            if p.name == "_waypoint.md":
                if p.parent != d:
                    deeper.append(p.parent)
                continue
            if p.name == ".gitkeep":
                continue
            st = p.stat()
            total += st.st_size
            count += 1
            newest = max(newest, st.st_mtime)
    return total, count, newest, deeper


def block_state(d: Path, size, files, newest, deeper):
    m = d / "_waypoint.md"
    if m.is_file():
        purpose, keywords = parse_manifest(m)
        state = "stale" if newest > m.stat().st_mtime else "lit"
        return state, purpose, keywords
    if deeper:
        return "partial", "", ""
    if files >= DARK_FILES or size >= DARK_BYTES:
        return "dark", "", ""
    return "neutral", "", ""


def collect(root: Path):
    areas = []
    for d in sorted(root.iterdir()):
        if not (d.is_dir() and d.name[:1].isdigit()):
            continue
        blocks = []
        loose_bytes, loose_files = 0, 0
        for child in sorted(d.iterdir()):
            if child.is_dir():
                size, files, newest, deeper = dir_stats(child)
                state, purpose, keywords = block_state(child, size, files, newest, deeper)
                blocks.append({
                    "name": child.name, "path": child.relative_to(root).as_posix(),
                    "bytes": size, "files": files, "state": state,
                    "purpose": purpose, "keywords": keywords,
                    "deeper": [p.relative_to(root).as_posix() for p in deeper],
                })
            elif child.is_file() and child.name not in (".gitkeep", "_waypoint.md"):
                loose_bytes += child.stat().st_size
                loose_files += 1
        if loose_files:
            blocks.append({"name": "(loose files)", "path": d.name, "bytes": loose_bytes,
                           "files": loose_files, "state": "neutral", "purpose": "",
                           "keywords": "", "deeper": []})
        areas.append({"name": d.name, "blocks": blocks,
                      "bytes": sum(b["bytes"] for b in blocks),
                      "files": sum(b["files"] for b in blocks)})
    return areas


STATE_LABEL = {
    "lit": "curated - memory fresh",
    "stale": "curated, but content is newer than the manifest",
    "partial": "uncurated itself; waypoints exist deeper inside",
    "dark": "DARK TERRITORY - big and completely uncurated",
    "neutral": "small and uncurated - fine as-is",
}


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
    out = out or root / "memory-map.html"

    areas = collect(root)
    all_blocks = [b for a in areas for b in a["blocks"]]
    n_lit = sum(1 for b in all_blocks if b["state"] == "lit")
    n_stale = sum(1 for b in all_blocks if b["state"] == "stale")
    n_dark = sum(1 for b in all_blocks if b["state"] == "dark")
    dark_bytes = sum(b["bytes"] for b in all_blocks if b["state"] == "dark")
    mem_mass = sum(b["bytes"] for b in all_blocks if b["state"] in ("lit", "stale", "dark"))
    curated_mass = sum(b["bytes"] for b in all_blocks if b["state"] in ("lit", "stale"))
    coverage = f"{100 * curated_mass / mem_mass:.0f}%" if mem_mass else "n/a"

    sections = []
    for a in areas:
        if not a["blocks"]:
            sections.append(f'<section><h2>{esc(a["name"])}</h2>'
                            f'<p class="dim">(empty area)</p></section>')
            continue
        mx = max(b["bytes"] for b in a["blocks"]) or 1
        tiles = []
        for b in a["blocks"]:
            grow = max(1, int(100 * b["bytes"] / mx))
            label = b["purpose"] if b["state"] in ("lit", "stale") and b["purpose"] else b["name"]
            tiles.append(
                f'<div class="tile {b["state"]}" style="flex-grow:{grow}" '
                f'data-block="{esc(json.dumps(b))}" title="{esc(STATE_LABEL[b["state"]])}">'
                f'<span class="tname">{esc(b["name"])}</span>'
                f'<span class="tlabel">{esc(label[:70])}</span>'
                f'<span class="tmeta">{b["files"]} files - {esc(human(b["bytes"]))}</span></div>')
        sections.append(f'<section><h2>{esc(a["name"])} <span class="dim">{a["files"]} files - '
                        f'{esc(human(a["bytes"]))}</span></h2><div class="mosaic">{"".join(tiles)}</div></section>')

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    doc = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>orbit &mdash; memory map</title>
<style>
:root {{ --bg:#08090c; --panel:#101319; --card:#12151d; --line:#1e2330; --line2:#2a3145;
  --ink:#e8ebf4; --dim:#9aa3ba; --faint:#5c6478; --ok:#4ade80; --warn:#fbbf24; --bad:#f87171;
  --accent:#8ab4ff; --accent2:#b48aff; --mono:"Cascadia Code",Consolas,monospace; }}
* {{ box-sizing:border-box; margin:0; }}
body {{ background:var(--bg); color:var(--ink); font:15px/1.6 system-ui,"Segoe UI",sans-serif; }}
header {{ position:sticky; top:0; background:rgba(8,9,12,.88); backdrop-filter:blur(8px);
  border-bottom:1px solid var(--line); padding:14px 28px; display:flex; align-items:baseline; gap:14px; z-index:9; }}
header .wordmark {{ font:600 17px var(--mono); }} header .wordmark b {{ color:var(--warn); }}
header .meta {{ color:var(--faint); font:12px var(--mono); }}
main {{ max-width:1060px; margin:0 auto; padding:26px 24px 60px; }}
.kpis {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; margin-bottom:22px; }}
.kpi {{ background:linear-gradient(160deg,var(--panel),var(--card)); border:1px solid var(--line); border-radius:10px; padding:12px 16px; }}
.klabel {{ display:block; font:11px var(--mono); text-transform:uppercase; letter-spacing:2px; color:var(--faint); }}
.kval {{ font:600 24px var(--mono); }}
section {{ background:var(--card); border:1px solid var(--line); border-radius:12px; padding:16px 18px; margin-bottom:14px; }}
section h2 {{ font:600 13px var(--mono); color:var(--accent); margin-bottom:10px; }}
section h2 .dim {{ color:var(--faint); font-weight:400; margin-left:8px; font-size:11px; }}
.dim {{ color:var(--dim); }}
.mosaic {{ display:flex; flex-wrap:wrap; gap:6px; }}
.tile {{ flex-basis:120px; min-height:66px; border-radius:8px; padding:8px 10px; cursor:pointer;
  display:flex; flex-direction:column; gap:1px; border:1px solid var(--line2); overflow:hidden; }}
.tile:hover {{ outline:1px solid var(--accent); }}
.tname {{ font:600 11.5px var(--mono); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.tlabel {{ font-size:11px; color:var(--dim); line-height:1.35; max-height:2.7em; overflow:hidden; }}
.tmeta {{ font:10px var(--mono); color:var(--faint); margin-top:auto; }}
.tile.lit {{ background:#16213a; border-color:var(--accent); box-shadow:inset 0 0 18px rgba(138,180,255,.15); }}
.tile.lit .tname {{ color:var(--accent); }}
.tile.stale {{ background:#2a2313; border-color:var(--warn); animation:flick 2.6s infinite; }}
.tile.stale .tname {{ color:var(--warn); }}
@keyframes flick {{ 0%,100% {{ box-shadow:inset 0 0 12px rgba(251,191,36,.12); }} 50% {{ box-shadow:inset 0 0 22px rgba(251,191,36,.28); }} }}
.tile.partial {{ background:#141a2b; border-style:dashed; border-color:var(--accent2); }}
.tile.partial .tname {{ color:var(--accent2); }}
.tile.dark {{ background:#050608; border-color:#151820; color:var(--faint); }}
.tile.dark .tname {{ color:var(--faint); }}
.tile.dark .tlabel::after {{ content:"here be dragons"; color:#3a4152; font-style:italic; }}
.tile.neutral {{ background:var(--panel); }}
#card {{ position:fixed; right:18px; bottom:18px; width:380px; max-width:92vw; background:var(--panel);
  border:1px solid var(--line2); border-radius:12px; padding:16px 18px; display:none; z-index:99;
  box-shadow:0 8px 40px rgba(0,0,0,.6); }}
#card.show {{ display:block; }}
#card h3 {{ font:600 13px var(--mono); margin-bottom:6px; }}
#card p {{ font-size:13px; color:var(--dim); margin-bottom:8px; }}
#card pre {{ background:var(--bg); border:1px solid var(--line); border-radius:8px; padding:9px;
  font:11.5px/1.5 var(--mono); color:var(--dim); overflow:auto; max-height:220px; white-space:pre-wrap; }}
#card .x {{ float:right; cursor:pointer; color:var(--faint); font:600 13px var(--mono); }}
.legend {{ display:flex; flex-wrap:wrap; gap:14px; margin-bottom:18px; font:11.5px var(--mono); color:var(--dim); }}
.legend span::before {{ content:"\\25A0 "; }}
.lg-lit::before {{ color:var(--accent); }} .lg-stale::before {{ color:var(--warn); }}
.lg-partial::before {{ color:var(--accent2); }} .lg-dark::before {{ color:#22262f; }} .lg-neutral::before {{ color:var(--line2); }}
footer {{ text-align:center; color:var(--faint); font:12px var(--mono); padding:18px; border-top:1px solid var(--line); }}
</style></head><body>
<header><span class="wordmark"><b>&#9732;</b> orbit &middot; memory map</span>
<span class="meta">generated {stamp} &middot; {esc(root.resolve())}</span></header>
<main>
<div class="kpis">
  <div class="kpi"><span class="klabel">memory coverage</span><span class="kval">{esc(coverage)}</span></div>
  <div class="kpi"><span class="klabel">curated fresh</span><span class="kval" style="color:var(--accent)">{n_lit}</span></div>
  <div class="kpi"><span class="klabel">stale memory</span><span class="kval" style="color:var(--warn)">{n_stale}</span></div>
  <div class="kpi"><span class="klabel">dark territory</span><span class="kval" style="color:var(--bad)">{n_dark}<small style="font-size:12px;color:var(--faint)"> &middot; {esc(human(dark_bytes))}</small></span></div>
</div>
<div class="legend"><span class="lg-lit">lit = curated &amp; fresh</span><span class="lg-stale">stale = manifest older than content</span>
<span class="lg-partial">partial = waypoints deeper inside</span><span class="lg-dark">dark = big &amp; uncurated</span><span class="lg-neutral">neutral = small, fine as-is</span></div>
{"".join(sections)}
<p class="dim" style="font:11.5px var(--mono)">coverage = curated mass / mass that deserves memory (lit + stale + dark). Click any tile for its card;
dark territory's card carries a ready-to-paste _waypoint.md skeleton (curation stays deliberate - SPEC gate applies).</p>
</main>
<div id="card"><span class="x" onclick="this.parentNode.classList.remove('show')">x</span><div id="cardBody"></div></div>
<footer>memory-map &middot; self-contained, zero external resources &middot; regenerate: python skills/memory-map/generate.py</footer>
<script>
const LABELS = {json.dumps(STATE_LABEL)};
document.querySelectorAll('.tile').forEach(t => t.addEventListener('click', () => {{
  const b = JSON.parse(t.dataset.block);
  let x = '<h3>' + b.path + '</h3><p>' + LABELS[b.state] + ' - ' + b.files + ' files</p>';
  if (b.state === 'lit' || b.state === 'stale') {{
    x += '<p><b>purpose:</b> ' + (b.purpose || '(none)') + '<br><b>keywords:</b> ' + (b.keywords || '(none)') + '</p>';
    if (b.state === 'stale') x += '<p style="color:var(--warn)">Update the _waypoint.md, then rebuild:</p><pre>python skills/locate/build_index.py .</pre>';
    else x += '<p>locate routes here from the index.</p>';
  }} else if (b.state === 'partial') {{
    x += '<p>waypoints inside:</p><pre>' + b.deeper.join('\\n') + '</pre>';
  }} else if (b.state === 'dark') {{
    x += '<p>Either set a waypoint + clean it, or it is junk for cleanup (SPEC gate). Skeleton:</p>' +
         '<pre>---\\npurpose: (what lives in ' + b.path + '?)\\nkeywords: []\\nfile_types: []\\nstatus: active\\nperiod: \\n---</pre>' +
         '<pre>save as ' + b.path + '/_waypoint.md\\nthen: python skills/locate/build_index.py .</pre>';
  }} else {{
    x += '<p>Small and uncurated - fine. Curate only if the SPEC gate applies (find-by-description / expensive to scan / canonical collection).</p>';
  }}
  document.getElementById('cardBody').innerHTML = x;
  document.getElementById('card').classList.add('show');
}}));
</script>
</body></html>
"""
    out.write_text(doc, encoding="utf-8")
    print(f"wrote {out} ({len(doc):,} bytes) - {len(all_blocks)} blocks: "
          f"{n_lit} lit, {n_stale} stale, {n_dark} dark, coverage {coverage}")
    if open_after:
        webbrowser.open(out.resolve().as_uri())
    return 0


if __name__ == "__main__":
    sys.exit(main())
