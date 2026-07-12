"""Create today's daily worklog - template + carry-forward, per .gravity/notes/SPEC.md.

Usage:
    python skills/daily-note/new_note.py [orbit-root] [--date YYYY-MM-DD]

Defaults: root = current directory, date = today. Creates
10-daily/YYYY/MM/YYYY-MM-DD-daily-worklog.md (placement per the filing SPEC),
carrying forward the most recent earlier worklog's "## In progress" bullets with a
single "(carried)" prefix. NEVER overwrites an existing note (exit 1). Stdlib only,
relative paths, ASCII console output (Korean-Windows cp949 safe).
"""

import re
import sys
from datetime import date, datetime
from pathlib import Path

NOTE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-daily-worklog\.md$")
SECTIONS = ["## Done", "## In progress", "## Decisions", "## Notes"]


def find_previous(root: Path, day: date):
    """Most recent worklog strictly before `day` (path scan, no payload reads elsewhere)."""
    best = None
    daily = root / "10-daily"
    if not daily.is_dir():
        return None
    for p in daily.rglob("*-daily-worklog.md"):
        m = NOTE_RE.match(p.name)
        if not m:
            continue
        d = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        if d < day and (best is None or d > best[0]):
            best = (d, p)
    return best[1] if best else None


def carried_items(prev: Path):
    """Non-empty bullets under '## In progress', each carrying one '(carried)' prefix."""
    items, inside = [], False
    for line in prev.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            inside = line.strip() == "## In progress"
            continue
        if inside and line.strip().startswith("- ") and line.strip() != "-":
            text = line.strip()[2:].strip()
            if text:
                if not text.startswith("(carried)"):
                    text = f"(carried) {text}"
                items.append(f"- {text}")
    return items


def main() -> int:
    args = list(sys.argv[1:])
    day = date.today()
    if "--date" in args:
        i = args.index("--date")
        day = datetime.strptime(args[i + 1], "%Y-%m-%d").date()
        del args[i:i + 2]
    root = Path(args[0]) if args else Path(".")

    out = (root / "10-daily" / f"{day:%Y}" / f"{day:%m}"
           / f"{day:%Y-%m-%d}-daily-worklog.md")
    if out.exists():
        print(f"REFUSED: {out} already exists - never overwrite a note; edit it instead")
        return 1

    prev = find_previous(root, day)
    carried = carried_items(prev) if prev else []

    body = [f"# Daily worklog - {day:%Y-%m-%d} ({day:%a})", ""]
    for s in SECTIONS:
        body.append(s)
        if s == "## In progress" and carried:
            body.extend(carried)
        body.append("")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(body), encoding="utf-8")
    src = f", carried {len(carried)} item(s) from {prev.name}" if prev else ", nothing to carry"
    print(f"wrote {out}{src}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
