"""Generate a process-flow guideline - one self-contained HTML page from a JSON definition.

Usage:
    python skills/process-architect/generate.py <definition.json> [-o out.html] [--open] [--fragment]

Data in, HTML out: the JSON definition (produced by the process-architect
interview) is the source of truth; the HTML is disposable output
(*.process.html, gitignored), never hand-edited. One file, zero external
resources (offline intranet - no CDN, no web fonts), theme-aware (light/dark),
print-clean. --fragment emits body-only HTML (title+style+content) for embedding
in a host page. Stdlib only - runs on the populated work instance too. Console
output stays ASCII-only (Korean-Windows consoles default to cp949).
"""

import html
import json
import sys
import webbrowser
from pathlib import Path

ARROW = ('<span class="arrow" aria-hidden="true"><svg viewBox="0 0 22 14">'
         '<path d="M0 7h18M14 2l5 5-5 5" fill="none" stroke="currentColor" '
         'stroke-width="1.6"/></svg></span>')

DEFAULT_LEGEND = [
    {"state": "go", "term": "GO", "desc": "moves forward to the next gate in the chain."},
    {"state": "hold", "term": "HOLD", "desc": "loops back one step to be fixed; no restart."},
    {"state": "stop", "term": "STOP", "desc": "ejects the item or escalates it, with a reason."},
]

STATE_COLOR = {"go": "var(--go)", "hold": "var(--hold)", "stop": "var(--stop)"}

CSS = """<style>
  :root{
    --paper:#eef1f5; --card:#ffffff; --card2:#f7f9fc;
    --ink:#171b24; --muted:#5a6373; --faint:#8a93a6;
    --line:#dde3ec; --line2:#c9d2e0;
    --accent:#2b41c4; --accent-soft:#e6eaff;
    --go:#178a54; --go-soft:#e2f4ea;
    --hold:#b5791a; --hold-soft:#fbf0dc;
    --stop:#c63c33; --stop-soft:#fbe6e4;
    --serif:"Charter","Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
    --sans:system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    --mono:"Cascadia Code","SF Mono",ui-monospace,Consolas,"Liberation Mono",monospace;
  }
  @media (prefers-color-scheme:dark){
    :root{
      --paper:#0e1119; --card:#161b26; --card2:#1b2130;
      --ink:#e7ebf3; --muted:#97a0b3; --faint:#6c7688;
      --line:#262e3d; --line2:#333d50;
      --accent:#8098ff; --accent-soft:#1c2440;
      --go:#4ec98a; --go-soft:#14291f;
      --hold:#e0a94a; --hold-soft:#2c2413;
      --stop:#ef6a60; --stop-soft:#2e1917;
    }
  }
  :root[data-theme="light"]{
    --paper:#eef1f5; --card:#ffffff; --card2:#f7f9fc;
    --ink:#171b24; --muted:#5a6373; --faint:#8a93a6;
    --line:#dde3ec; --line2:#c9d2e0;
    --accent:#2b41c4; --accent-soft:#e6eaff;
    --go:#178a54; --go-soft:#e2f4ea; --hold:#b5791a; --hold-soft:#fbf0dc;
    --stop:#c63c33; --stop-soft:#fbe6e4;
  }
  :root[data-theme="dark"]{
    --paper:#0e1119; --card:#161b26; --card2:#1b2130;
    --ink:#e7ebf3; --muted:#97a0b3; --faint:#6c7688;
    --line:#262e3d; --line2:#333d50;
    --accent:#8098ff; --accent-soft:#1c2440;
    --go:#4ec98a; --go-soft:#14291f; --hold:#e0a94a; --hold-soft:#2c2413;
    --stop:#ef6a60; --stop-soft:#2e1917;
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--paper);color:var(--ink);
    font-family:var(--sans);font-size:16px;line-height:1.6;-webkit-font-smoothing:antialiased}
  .doc{max-width:900px;margin:0 auto;padding:40px 24px 72px}
  .mast{border-bottom:2px solid var(--ink);padding-bottom:20px;margin-bottom:8px}
  .eyebrow{font-family:var(--mono);font-size:11.5px;letter-spacing:.22em;
    text-transform:uppercase;color:var(--accent);margin:0 0 10px}
  .mast h1{font-family:var(--serif);font-weight:600;font-size:clamp(28px,5vw,42px);
    line-height:1.12;letter-spacing:-.01em;text-wrap:balance;margin:0}
  .mast .lede{color:var(--muted);font-size:16px;margin:12px 0 0;max-width:60ch}
  .meta{display:flex;flex-wrap:wrap;gap:8px 28px;margin:20px 0 0;padding:0;font-family:var(--mono);font-size:12px}
  .meta div{display:flex;flex-direction:column;gap:2px}
  .meta dt{color:var(--faint);text-transform:uppercase;letter-spacing:.1em;font-size:10.5px}
  .meta dd{margin:0;color:var(--ink);font-variant-numeric:tabular-nums}
  .shead{display:flex;align-items:baseline;gap:12px;margin:44px 0 18px}
  .shead h2{font-family:var(--serif);font-weight:600;font-size:22px;margin:0}
  .shead .rule{flex:1;height:1px;background:var(--line2)}
  .shead .n{font-family:var(--mono);font-size:12px;color:var(--faint)}
  .chainwrap{overflow-x:auto;padding-bottom:6px}
  .chain{display:flex;align-items:stretch;gap:0;min-width:max-content}
  .node{display:flex;flex-direction:column;justify-content:center;background:var(--card);
    border:1px solid var(--line);border-radius:10px;padding:10px 14px;min-width:118px;position:relative}
  .node .k{font-family:var(--mono);font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--faint)}
  .node .v{font-weight:600;font-size:13.5px;line-height:1.25;margin-top:2px}
  .node.start{background:var(--card2);border-style:dashed}
  .node.end{background:var(--accent);border-color:var(--accent)}
  .node.end .k{color:rgba(255,255,255,.75)} .node.end .v{color:#fff}
  .node.prov{border-color:var(--accent);box-shadow:inset 0 0 0 1px var(--accent)}
  .arrow{display:flex;align-items:center;color:var(--line2);padding:0 4px;flex:none}
  .arrow svg{width:22px;height:14px}
  .stepper{display:flex;flex-direction:column}
  .stage{display:grid;grid-template-columns:64px 1fr;gap:0}
  .rail{position:relative;display:flex;flex-direction:column;align-items:center}
  .rail .num{font-family:var(--mono);font-weight:600;font-size:15px;width:38px;height:38px;
    border-radius:50%;display:grid;place-items:center;background:var(--card);
    border:2px solid var(--accent);color:var(--accent);z-index:1;font-variant-numeric:tabular-nums}
  .rail .line{flex:1;width:2px;background:var(--line2);margin-top:2px}
  .stepper .stage:last-child .rail .line{display:none}
  .card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin:0 0 14px}
  .card .top{display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin-bottom:4px}
  .card h3{font-size:17px;font-weight:650;margin:0}
  .owner{font-family:var(--mono);font-size:11px;letter-spacing:.03em;background:var(--accent-soft);
    color:var(--accent);border-radius:999px;padding:3px 10px;white-space:nowrap}
  .sla{margin-left:auto;font-family:var(--mono);font-size:11px;color:var(--muted);
    border:1px solid var(--line2);border-radius:6px;padding:3px 8px;white-space:nowrap;font-variant-numeric:tabular-nums}
  .purpose{color:var(--muted);margin:6px 0 14px}
  .io{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px}
  .io .box{background:var(--card2);border:1px solid var(--line);border-radius:8px;padding:10px 12px}
  .io .lbl{font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--faint);margin-bottom:4px}
  .io .box p{margin:0;font-size:13.5px;line-height:1.5}
  .decisions{display:flex;flex-wrap:wrap;gap:8px}
  .pill{display:inline-flex;align-items:center;gap:7px;font-size:13px;border-radius:8px;padding:6px 11px;border:1px solid transparent}
  .pill b{font-weight:650;font-family:var(--mono);font-size:11px;letter-spacing:.04em}
  .pill.go{background:var(--go-soft);color:var(--go);border-color:color-mix(in srgb,var(--go) 30%,transparent)}
  .pill.hold{background:var(--hold-soft);color:var(--hold);border-color:color-mix(in srgb,var(--hold) 30%,transparent)}
  .pill.stop{background:var(--stop-soft);color:var(--stop);border-color:color-mix(in srgb,var(--stop) 30%,transparent)}
  .cols{display:grid;grid-template-columns:1fr 1fr;gap:16px}
  .panel{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px}
  .panel h4{margin:0 0 12px;font-size:13px;text-transform:uppercase;letter-spacing:.1em;font-family:var(--mono);color:var(--faint)}
  .legrow{display:flex;gap:10px;align-items:flex-start;padding:7px 0;border-bottom:1px solid var(--line)}
  .legrow:last-child{border-bottom:none}
  .swatch{width:12px;height:12px;border-radius:4px;margin-top:5px;flex:none}
  .legrow .t{font-size:13.5px} .legrow .t b{font-family:var(--mono);font-size:11px;letter-spacing:.04em}
  .legrow .t span{color:var(--muted)}
  .panel ul{margin:0;padding-left:18px}
  .panel li{margin:0 0 8px;font-size:14px;color:var(--muted)}
  .panel li b{color:var(--ink);font-weight:600}
  footer{margin-top:44px;padding-top:18px;border-top:1px solid var(--line2);display:flex;
    flex-wrap:wrap;justify-content:space-between;gap:8px;font-family:var(--mono);font-size:11.5px;color:var(--faint)}
  @media (max-width:640px){
    .io,.cols{grid-template-columns:1fr}
    .stage{grid-template-columns:48px 1fr} .rail .num{width:34px;height:34px} .sla{margin-left:0}
  }
  @media (prefers-reduced-motion:no-preference){
    .stepper .stage{opacity:0;transform:translateY(8px);animation:rise .5s ease forwards}
    .stepper .stage:nth-child(1){animation-delay:.02s} .stepper .stage:nth-child(2){animation-delay:.08s}
    .stepper .stage:nth-child(3){animation-delay:.14s} .stepper .stage:nth-child(4){animation-delay:.20s}
    .stepper .stage:nth-child(5){animation-delay:.26s} .stepper .stage:nth-child(6){animation-delay:.32s}
    .stepper .stage:nth-child(7){animation-delay:.38s} .stepper .stage:nth-child(8){animation-delay:.44s}
    @keyframes rise{to{opacity:1;transform:none}}
  }
  @media print{body{background:#fff} .doc{max-width:none} .card,.panel,.node{break-inside:avoid}}
</style>"""


def esc(s):
    return html.escape("" if s is None else str(s))


def render_meta(meta):
    fields = [("Doc ref", meta.get("ref")), ("Owner", meta.get("owner")),
              ("Version", meta.get("version")), ("Effective", meta.get("effective")),
              ("Review", meta.get("review")), ("Lead time", meta.get("lead_time"))]
    cells = "".join(f'<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>'
                    for k, v in fields if v)
    return f'<dl class="meta">{cells}</dl>' if cells else ""


def render_chain(chain):
    nodes = []
    for n in chain:
        kind = n.get("kind", "mid")
        cls = "node" + (" start" if kind == "start" else " end" if kind == "end" else "")
        if n.get("provider"):
            cls += " prov"
        nodes.append(f'<div class="{cls}"><span class="k">{esc(n.get("role", ""))}</span>'
                     f'<span class="v">{esc(n.get("label", ""))}</span></div>')
    return ARROW.join(nodes)


def auto_chain(stages):
    """Build an at-a-glance strip from the stages when none is supplied."""
    chain = [{"kind": "start", "role": "Start", "label": "Trigger"}]
    for i, s in enumerate(stages, 1):
        chain.append({"role": f"Gate {i}", "label": s.get("owner") or s.get("title", "")})
    chain.append({"kind": "end", "role": "Result", "label": "Done"})
    return chain


def render_decisions(decisions):
    out = []
    for d in decisions:
        state = d.get("state", "go")
        cls = state if state in STATE_COLOR else "go"
        to = f'&rarr; {esc(d["to"])}' if d.get("to") else ""
        out.append(f'<span class="pill {cls}"><b>{esc(d.get("label", ""))}</b>{to}</span>')
    return "".join(out)


def render_stage(i, s):
    owner = f'<span class="owner">{esc(s["owner"])}</span>' if s.get("owner") else ""
    sla = f'<span class="sla">SLA {esc(s["sla"])}</span>' if s.get("sla") else ""
    purpose = f'<p class="purpose">{esc(s["purpose"])}</p>' if s.get("purpose") else ""
    boxes = []
    if s.get("needs"):
        boxes.append(f'<div class="box"><div class="lbl">Needs in</div><p>{esc(s["needs"])}</p></div>')
    if s.get("produces"):
        boxes.append(f'<div class="box"><div class="lbl">Produces</div><p>{esc(s["produces"])}</p></div>')
    io = f'<div class="io">{"".join(boxes)}</div>' if boxes else ""
    decisions = s.get("decisions", [])
    dec = f'<div class="decisions">{render_decisions(decisions)}</div>' if decisions else ""
    return (f'<div class="stage"><div class="rail"><span class="num">{i}</span>'
            f'<span class="line"></span></div><div class="card"><div class="top">'
            f'<h3>{esc(s.get("title", ""))}</h3>{owner}{sla}</div>{purpose}{io}{dec}</div></div>')


def render_legend(legend):
    rows = []
    for item in legend:
        color = STATE_COLOR.get(item.get("state", "go"), "var(--go)")
        rows.append(f'<div class="legrow"><span class="swatch" style="background:{color}"></span>'
                    f'<span class="t"><b>{esc(item.get("term", ""))}</b> &mdash; '
                    f'<span>{esc(item.get("desc", ""))}</span></span></div>')
    return "".join(rows)


def render_exceptions(exceptions):
    if not exceptions:
        return ""
    items = "".join(f'<li><b>{esc(e.get("title", ""))}.</b> {esc(e.get("desc", ""))}</li>'
                    for e in exceptions)
    return (f'<div class="panel"><h4>Exceptions &amp; escalation</h4><ul>{items}</ul></div>')


def build(defn):
    meta = defn.get("meta", {})
    stages = defn.get("stages", [])
    if not stages:
        raise ValueError("definition has no 'stages'")
    chain = defn.get("chain") or auto_chain(stages)
    legend = defn.get("legend") or DEFAULT_LEGEND
    title = meta.get("title", "Process Guideline")

    eyebrow = f'<p class="eyebrow">{esc(meta["eyebrow"])}</p>' if meta.get("eyebrow") else ""
    lede = f'<p class="lede">{esc(meta["summary"])}</p>' if meta.get("summary") else ""
    stage_html = "".join(render_stage(i, s) for i, s in enumerate(stages, 1))
    exceptions_panel = render_exceptions(defn.get("exceptions"))
    foot_ref = " &middot; ".join(x for x in (meta.get("ref"), meta.get("version") and f'v{meta["version"]}',
                                             meta.get("owner") and f'owner: {meta["owner"]}') if x)

    body = f"""<div class="doc">
  <header class="mast">
    {eyebrow}
    <h1>{esc(title)}</h1>
    {lede}
    {render_meta(meta)}
  </header>
  <div class="shead"><span class="n">01</span><h2>The route at a glance</h2><span class="rule"></span></div>
  <div class="chainwrap" role="group" aria-label="Process route"><div class="chain">{render_chain(chain)}</div></div>
  <div class="shead"><span class="n">02</span><h2>Step by step</h2><span class="rule"></span></div>
  <div class="stepper">{stage_html}</div>
  <div class="shead"><span class="n">03</span><h2>How to read the gates</h2><span class="rule"></span></div>
  <div class="cols">
    <div class="panel"><h4>Decision states</h4>{render_legend(legend)}</div>
    {exceptions_panel}
  </div>
  <footer><span>{foot_ref}</span><span>generated by process-architect &middot; edit the JSON, not this page</span></footer>
</div>"""
    return title, body


def full_doc(title, body):
    return ('<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{esc(title)}</title>\n{CSS}</head><body>\n{body}\n</body></html>\n')


def fragment(title, body):
    return f'<title>{esc(title)}</title>\n{CSS}\n{body}\n'


def main():
    args = list(sys.argv[1:])
    open_after = False
    frag = False
    for flag in ("--fragment",):
        while flag in args:
            args.remove(flag)
            frag = True
    for flag in ("--open", "-O"):
        while flag in args:
            args.remove(flag)
            open_after = True
    out = None
    if "-o" in args:
        i = args.index("-o")
        out = Path(args[i + 1])
        del args[i:i + 2]
    if not args:
        print("usage: generate.py <definition.json> [-o out.html] [--open] [--fragment]")
        return 2
    src = Path(args[0])
    defn = json.loads(src.read_text(encoding="utf-8"))
    title, body = build(defn)
    doc = fragment(title, body) if frag else full_doc(title, body)
    out = out or Path(f"{src.stem}.process.html")
    out.write_text(doc, encoding="utf-8")
    n_stages = len(defn.get("stages", []))
    print(f"wrote {out} ({len(doc):,} bytes) - {n_stages} stages, "
          f"{'fragment' if frag else 'full page'}")
    if open_after:
        webbrowser.open(out.resolve().as_uri())
        print(f"opened {out.resolve()} in the default browser")
    return 0


if __name__ == "__main__":
    sys.exit(main())
