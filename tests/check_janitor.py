"""The orbit gate: verify the janitor sweep against a tree with planted problems.

Usage:
    cp -r tests/fixture-janitor/tree/. <scratch>/
    python tests/check_janitor.py <scratch>

Self-driving (the sweep is deterministic stdlib): the checker stages the lint
infrastructure into the scratch (.gravity + tests/check_structure.py, which the sweep
shells out to), pins mtimes (old inbox file 42d before the pinned sweep date; waypoint
payload newer than its manifest), runs sweep.py, then verifies every planted problem is
called out at the right severity - and that the clean checks stay OK, the sweep is
read-only (md5 inventory unchanged except the report), a same-day rerun refuses, and
--force re-sweeps. Exit 0 on PASS, 1 on FAIL. ASCII-only output.
"""

import hashlib
import os
import shutil
import subprocess
import sys
from datetime import date, datetime, time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SWEEP = REPO / "skills" / "orbit-janitor" / "sweep.py"

DAY = date(2026, 7, 13)                                     # pinned sweep date
OLD = datetime.combine(date(2026, 6, 1), time(12, 0)).timestamp()    # 42d before DAY
NEWER = datetime.combine(date(2026, 6, 20), time(12, 0)).timestamp() # after the manifest


def inventory(root: Path, skip):
    inv = {}
    for d in sorted(root.iterdir()):
        if d.is_dir() and d.name[:1].isdigit():
            for p in d.rglob("*"):
                if p.is_file() and p.name != ".gitkeep":
                    rel = p.relative_to(root).as_posix()
                    if rel not in skip:
                        inv[rel] = hashlib.md5(p.read_bytes()).hexdigest()
    return inv


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    scratch = Path(sys.argv[1])
    if not (scratch / "00-inbox").is_dir():
        print(f"FAIL: {scratch} does not look like a copied fixture-janitor tree")
        return 1
    failures = []
    check = lambda cond, msg: None if cond else failures.append(msg)

    # stage lint infrastructure the sweep shells out to
    (scratch / "tests").mkdir(exist_ok=True)
    shutil.copy2(REPO / "tests" / "check_structure.py", scratch / "tests" / "check_structure.py")
    if not (scratch / ".gravity").is_dir():
        shutil.copytree(REPO / ".gravity", scratch / ".gravity")

    # pin the planted problems' clocks
    os.utime(scratch / "00-inbox" / "vendor-quote-unsorted.txt", (OLD, OLD))
    os.utime(scratch / "40-projects" / "erp-upgrade" / "_waypoint.md", (OLD, OLD))
    os.utime(scratch / "40-projects" / "erp-upgrade" / "erp-quote.txt", (NEWER, NEWER))

    report_rel = f"10-daily/2026/07/{DAY.isoformat()}-janitor-report.md"
    before = inventory(scratch, skip={report_rel})

    r = subprocess.run([sys.executable, str(SWEEP), str(scratch), "--date", DAY.isoformat()],
                       capture_output=True, text=True)
    report = scratch / report_rel
    check(r.returncode == 0, f"sweep.py exited {r.returncode}: {r.stdout}{r.stderr}")
    check(report.is_file(), f"report not at the filing-SPEC chore path {report_rel}")

    if report.is_file():
        t = report.read_text(encoding="utf-8")
        check("Overall: ACT" in t, "overall verdict must be ACT (inbox is 42d old)")
        check("## Inbox [ACT]" in t, "inbox must be ACT at 42d")
        check("oldest 42d" in t, "inbox age must be computed against --date (expected 42d)")
        check("## Duplicates [WARN]" in t and "1 group(s)" in t,
              "the planted byte-identical pair must be one WARN dupe group")
        check("## Structure [OK]" in t and "PASS" in t, "structure lint should be OK on the fixture")
        check("## Waypoints [WARN]" in t, "stale waypoint must WARN")
        check("40-projects/erp-upgrade" in t, "the stale manifest's directory must be named")
        check("index missing" in t, "missing waypoint-index.md must be flagged")
        check("## Cleanup candidates [OK]" in t, "no big+stale files planted - must stay OK")

        # read-only wall: nothing but the report appeared or changed
        after = inventory(scratch, skip={report_rel})
        check(before == after, "sweep must be read-only (area inventory changed beyond the report)")

        # rerun refuses; --force re-sweeps
        bytes_before = report.read_bytes()
        r2 = subprocess.run([sys.executable, str(SWEEP), str(scratch), "--date", DAY.isoformat()],
                            capture_output=True, text=True)
        check(r2.returncode != 0, "same-day rerun must refuse without --force")
        check(report.read_bytes() == bytes_before, "refused rerun must leave the report byte-identical")
        r3 = subprocess.run([sys.executable, str(SWEEP), str(scratch), "--date", DAY.isoformat(), "--force"],
                            capture_output=True, text=True)
        check(r3.returncode == 0, f"--force re-sweep failed: {r3.stdout}{r3.stderr}")

    if failures:
        print(f"FAIL ({len(failures)}):")
        for f in failures:
            print(f"  {f}")
        return 1
    print("PASS: all planted problems called out at the right severity (inbox ACT 42d, dupe WARN, "
          "stale waypoint + missing index WARN), clean checks stay OK, sweep read-only, "
          "rerun refused, --force re-sweeps")
    return 0


if __name__ == "__main__":
    sys.exit(main())
