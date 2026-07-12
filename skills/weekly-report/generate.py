"""Assemble the weekly report from the week's daily worklogs + a tree-activity scan.

Usage:
    python skills/weekly-report/generate.py [orbit-root] [--date YYYY-MM-DD] [--force]

Defaults: root = current directory, week = the ISO week containing --date (or today).
Writes 10-daily/YYYY/YYYY-Www-weekly-report.md per .gravity/notes/SPEC.md "Weekly
assembly": Done grouped by day, Decisions date-tagged, the last worklog's In-progress
as "Carried into next week", and a per-area table of files modified inside the week
(mtime window - signals only, payload never read). Refuses to overwrite unless
--force (the report is a regenerable assembly, unlike a hand-written daily note).
Stdlib only, relative paths, ASCII console output (cp949 safe).
"""

import re
import sys
from datetime import date, datetime, time
from pathlib import Path

NOTE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-daily-worklog\.md$")


def parse_sections(p: Path):
    out = {"Done": [], "In progress": [], "Decisions": [], "Notes": []}
    current = None
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            name = line[3:].strip()
            current = name if name in out else None
            continue
        if current and line.strip().startswith("- "):
            text = line.strip()[2:].strip()
            if text:
                out[current].append(text)
    return out


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:,.0f} {unit}" if unit == "B" else f"{n:,.1f} {unit}"
        n /= 1024
    return f"{n} B"


def tree_activity(root: Path, start: date, end: date):
    """{area: (count, bytes)} for files whose mtime falls inside [start, end]."""
    lo = datetime.combine(start, time.min).timestamp()
    hi = datetime.combine(end, time.max).timestamp()
    acc = {}
    for d in sorted(root.iterdir()):
        if d.is_dir() and d.name[:1].isdigit():
            for p in d.rglob("*"):
                if p.is_file() and p.name != ".gitkeep":
                    st = p.stat()
                    if lo <= st.st_mtime <= hi:
                        c, b = acc.get(d.name, (0, 0))
                        acc[d.name] = (c + 1, b + st.st_size)
    return acc


def main() -> int:
    args = list(sys.argv[1:])
    force = False
    while "--force" in args:
        args.remove("--force")
        force = True
    anchor = date.today()
    if "--date" in args:
        i = args.index("--date")
        anchor = datetime.strptime(args[i + 1], "%Y-%m-%d").date()
        del args[i:i + 2]
    root = Path(args[0]) if args else Path(".")

    iso_y, iso_w, _ = anchor.isocalendar()
    week = f"{iso_y}-W{iso_w:02d}"
    start = date.fromisocalendar(iso_y, iso_w, 1)
    end = date.fromisocalendar(iso_y, iso_w, 7)

    notes = []
    daily = root / "10-daily"
    if daily.is_dir():
        for p in daily.rglob("*-daily-worklog.md"):
            m = NOTE_RE.match(p.name)
            if not m:
                continue
            d = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            if start <= d <= end:
                notes.append((d, p))
    notes.sort()
    if not notes:
        print(f"REFUSED: no daily worklogs found in {week} ({start} ~ {end}) - nothing to assemble")
        return 1

    out = root / "10-daily" / f"{iso_y}" / f"{week}-weekly-report.md"
    if out.exists() and not force:
        print(f"REFUSED: {out} already exists - rerun with --force to reassemble")
        return 1

    parsed = [(d, p, parse_sections(p)) for d, p in notes]
    lines = [f"# Weekly report - {week} ({start} ~ {end})", "",
             "## Highlights", "- (fill from the sections below - facts only)", "",
             "## Done this week"]
    for d, _p, sec in parsed:
        if sec["Done"]:
            lines.append(f"### {d} ({d:%a})")
            lines.extend(f"- {t}" for t in sec["Done"])
    lines += ["", "## Decisions"]
    any_dec = False
    for d, _p, sec in parsed:
        for t in sec["Decisions"]:
            lines.append(f"- {d}: {t}")
            any_dec = True
    if not any_dec:
        lines.append("- (none recorded this week)")
    lines += ["", "## Carried into next week"]
    last_prog = parsed[-1][2]["In progress"]
    lines.extend(f"- {t}" for t in last_prog) if last_prog else lines.append("- (clean slate)")
    lines += ["", "## Tree activity", "", "| Area | Files touched | Size |", "|---|---|---|"]
    act = tree_activity(root, start, end)
    if act:
        for area in sorted(act):
            c, b = act[area]
            lines.append(f"| {area} | {c} | {human(b)} |")
    else:
        lines.append("| (no files modified in the areas this week) | 0 | 0 B |")
    lines += ["", "## Sources",
              *(f"- {p.relative_to(root).as_posix()}" for _d, p, _s in parsed), ""]

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out} - {len(parsed)} daily note(s), "
          f"{sum(len(s['Done']) for _, _, s in parsed)} done item(s), "
          f"{len(act)} active area(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
