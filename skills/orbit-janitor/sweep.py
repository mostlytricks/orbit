"""Janitor sweep - the tree nags instead of waiting to be asked. Read-only.

Usage:
    python skills/orbit-janitor/sweep.py [orbit-root] [--date YYYY-MM-DD] [--force]

Five checks, signals only (payload never read except md5 for exact-dupe grouping,
same as the dashboard): inbox age, duplicate waste, structure lint, waypoint
staleness, cleanup candidates. Writes one short day-dated chore record to
10-daily/YYYY/MM/YYYY-MM-DD-janitor-report.md (placement per the filing SPEC;
derived artifact - refuses to overwrite unless --force). Never moves or deletes
anything. Stdlib only, relative paths, ASCII console output (cp949 safe).
Ages are computed against --date so the gate is deterministic.
"""

import hashlib
import subprocess
import sys
from datetime import date, datetime, time
from pathlib import Path

BIG_BYTES = 5 * 2**20
STALE_DAYS = 180
INBOX_ACT_DAYS = 7


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:,.0f} {unit}" if unit == "B" else f"{n:,.1f} {unit}"
        n /= 1024
    return f"{n} B"


def collect(root: Path):
    rows = []
    for d in sorted(root.iterdir()):
        if d.is_dir() and d.name[:1].isdigit():
            for p in d.rglob("*"):
                if p.is_file() and p.name != ".gitkeep":
                    st = p.stat()
                    rows.append((p, st.st_size, st.st_mtime, d.name))
    return rows


def dupe_groups(rows):
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
            h = hashlib.md5(p.read_bytes()).hexdigest()
            by_hash.setdefault(h, []).append(p)
        groups += [(size, ps) for ps in by_hash.values() if len(ps) > 1]
    return groups


def check_inbox(root, rows, now_ts):
    inbox = [(p, m) for p, _s, m, a in rows if a.startswith("00-")]
    if not inbox:
        return "OK", ["inbox empty - as it should be after triage"]
    oldest = max(int((now_ts - m) / 86400) for _p, m in inbox)
    sev = "ACT" if oldest >= INBOX_ACT_DAYS else "WARN"
    return sev, [f"{len(inbox)} file(s) waiting; oldest {oldest}d (target: 0 after each triage)",
                 "-> run file-triage"]


def check_dupes(rows):
    groups = dupe_groups(rows)
    if not groups:
        return "OK", ["no exact duplicates"]
    waste = sum(size * (len(ps) - 1) for size, ps in groups)
    return "WARN", [f"{len(groups)} group(s) / {human(waste)} wasted",
                    "-> keep one, remove the rest yourself (orbit never deletes)"]


def check_structure(root):
    script = root / "tests" / "check_structure.py"
    if not script.is_file():
        return "WARN", ["tests/check_structure.py not found - cannot verify the contract"]
    r = subprocess.run([sys.executable, str(script), str(root)], capture_output=True, text=True)
    if r.returncode == 0:
        return "OK", ["contract lint PASS"]
    return "ACT", ["contract lint FAIL:", *(f"  {ln}" for ln in (r.stdout + r.stderr).strip().splitlines()[:6]),
                   "-> follow the SPEC change order (contract -> tree -> lint)"]


def check_waypoints(root):
    manifests = [p for p in root.rglob("_waypoint.md")
                 if p.parts[len(root.parts)][:1].isdigit()]
    if not manifests:
        return "OK", ["no curated directories yet - nothing to go stale"]
    lines, sev = [], "OK"
    for m in manifests:
        newest = max((f.stat().st_mtime for f in m.parent.rglob("*")
                      if f.is_file() and f.name not in ("_waypoint.md", ".gitkeep")), default=0)
        if newest > m.stat().st_mtime:
            sev = "WARN"
            lines.append(f"stale manifest (content newer than _waypoint.md): "
                         f"{m.parent.relative_to(root).as_posix()}")
    if not (root / "waypoint-index.md").is_file():
        sev = "WARN"
        lines.append("index missing -> python skills/locate/build_index.py .")
    return sev, lines or [f"{len(manifests)} manifest(s) fresh, index present"]


def check_cleanup(rows, now_ts):
    cand = [(p, s) for p, s, m, _a in rows
            if s >= BIG_BYTES and (now_ts - m) / 86400 >= STALE_DAYS]
    if not cand:
        return "OK", [f"nothing over {human(BIG_BYTES)} and {STALE_DAYS}d+ stale"]
    return "WARN", [f"{len(cand)} candidate(s), {human(sum(s for _p, s in cand))} total",
                    "-> review via orbit-dashboard; keepers to deep archive, junk you remove yourself"]


def main() -> int:
    args = list(sys.argv[1:])
    force = False
    while "--force" in args:
        args.remove("--force")
        force = True
    day = date.today()
    if "--date" in args:
        i = args.index("--date")
        day = datetime.strptime(args[i + 1], "%Y-%m-%d").date()
        del args[i:i + 2]
    root = Path(args[0]) if args else Path(".")
    now_ts = datetime.combine(day, time(12, 0)).timestamp()

    out = (root / "10-daily" / f"{day:%Y}" / f"{day:%m}"
           / f"{day:%Y-%m-%d}-janitor-report.md")
    if out.exists() and not force:
        print(f"REFUSED: {out} already exists - rerun with --force to re-sweep")
        return 1

    rows = collect(root)
    checks = [
        ("Inbox", *check_inbox(root, rows, now_ts)),
        ("Duplicates", *check_dupes(rows)),
        ("Structure", *check_structure(root)),
        ("Waypoints", *check_waypoints(root)),
        ("Cleanup candidates", *check_cleanup(rows, now_ts)),
    ]
    acts = sum(1 for _n, s, _l in checks if s == "ACT")
    warns = sum(1 for _n, s, _l in checks if s == "WARN")
    overall = "ACT" if acts else ("WARN" if warns else "OK")

    lines = [f"# Janitor sweep - {day:%Y-%m-%d} ({day:%a})", "",
             f"Overall: {overall} ({acts} act / {warns} warn / "
             f"{len(checks) - acts - warns} ok)", ""]
    for name, sev, detail in checks:
        lines.append(f"## {name} [{sev}]")
        lines.extend(f"- {d}" if not d.startswith("  ") else d for d in detail)
        lines.append("")
    lines.append("(read-only sweep - the janitor reports, humans and filing skills act)")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out} - overall {overall} ({acts} act, {warns} warn)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
