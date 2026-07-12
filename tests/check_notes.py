"""The orbit gate: verify the notes contract (.gravity/notes/SPEC.md) end to end.

Usage:
    cp -r tests/fixture-notes/tree/. <scratch>/
    python tests/check_notes.py <scratch>

Self-driving (like check_structure, unlike the triage-style gates): the scripts under
test are deterministic stdlib code, so the checker runs them itself with pinned dates -
fixture week 2026-W24 (Mon 06-08 .. Wed 06-10 notes planted; the checker creates Thu).

Verifies: daily creation at the filing-SPEC path with the four contract sections and a
single-(carried) forward of the previous In-progress; refusal to overwrite (bytes
identical after a re-run); weekly assembly (Done grouped by day, Decisions date-tagged,
last note's In-progress as Carried, per-area activity counting ONLY files whose mtime
falls inside the week, sources cited). Exit 0 on PASS, 1 on FAIL. ASCII-only output.
"""

import os
import subprocess
import sys
from datetime import date, datetime, time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
NEW_NOTE = REPO / "skills" / "daily-note" / "new_note.py"
WEEKLY = REPO / "skills" / "weekly-report" / "generate.py"

THU = date.fromisocalendar(2026, 24, 4)          # 2026-06-11
TUE_NOON = datetime.combine(date.fromisocalendar(2026, 24, 2), time(12, 0)).timestamp()
OUTSIDE = datetime.combine(date(2026, 5, 1), time(12, 0)).timestamp()

SECTIONS = ["## Done", "## In progress", "## Decisions", "## Notes"]
DONE_BULLETS = [
    "patched WSUS ring 1",
    "closed firewall ticket FW-102",
    "vendor call - ERP upgrade quote review",
    "closed incident INC-42 (db failover drill)",
    "finished firewall rule cleanup",
]


def run(script, scratch, *extra):
    return subprocess.run([sys.executable, str(script), str(scratch), *extra],
                          capture_output=True, text=True)


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    scratch = Path(sys.argv[1])
    if not (scratch / "10-daily").is_dir():
        print(f"FAIL: {scratch} does not look like a copied fixture-notes tree")
        return 1
    failures = []
    check = lambda cond, msg: None if cond else failures.append(msg)

    # ---- daily creation + carry-forward ----
    r = run(NEW_NOTE, scratch, "--date", THU.isoformat())
    note = scratch / "10-daily" / "2026" / "06" / f"{THU.isoformat()}-daily-worklog.md"
    check(r.returncode == 0, f"new_note.py exited {r.returncode}: {r.stdout}{r.stderr}")
    check(note.is_file(), f"daily note not at the filing-SPEC path {note}")
    if note.is_file():
        text = note.read_text(encoding="utf-8")
        pos = -1
        for s in SECTIONS:
            p = text.find(s)
            check(p >= 0, f"daily note missing section '{s}'")
            check(p > pos, f"daily note sections out of order at '{s}'")
            pos = p if p >= 0 else pos
        check("- (carried) prepare Q3 budget sheet" in text,
              "carry-forward missing: '(carried) prepare Q3 budget sheet'")
        check("(carried) (carried)" not in text, "double (carried) prefix - must apply once")
        check("firewall rule cleanup" not in text,
              "finished item carried anyway (it was Done on Wed, not In progress)")

        before = note.read_bytes()
        r2 = run(NEW_NOTE, scratch, "--date", THU.isoformat())
        check(r2.returncode != 0, "second run must refuse to overwrite (exit nonzero)")
        check(note.read_bytes() == before, "note changed after refused re-run (must be byte-identical)")

    # ---- weekly assembly ----
    os.utime(scratch / "20-design" / "dr-failover-notes.md", (TUE_NOON, TUE_NOON))
    os.utime(scratch / "40-projects" / "erp-upgrade" / "erp-quote-summary.txt", (TUE_NOON, TUE_NOON))
    os.utime(scratch / "50-policy" / "security-policy-draft.md", (OUTSIDE, OUTSIDE))

    r = run(WEEKLY, scratch, "--date", THU.isoformat())
    report = scratch / "10-daily" / "2026" / "2026-W24-weekly-report.md"
    check(r.returncode == 0, f"generate.py exited {r.returncode}: {r.stdout}{r.stderr}")
    check(report.is_file(), f"weekly report not at {report}")
    if report.is_file():
        rt = report.read_text(encoding="utf-8")
        for b in DONE_BULLETS:
            check(f"- {b}" in rt, f"report missing Done bullet: {b}")
        check("### 2026-06-08" in rt and "### 2026-06-10" in rt, "Done not grouped by day")
        check("- 2026-06-09: chose active-passive DR for the ERP stack" in rt,
              "Decision missing or not date-tagged")
        carried_zone = rt.split("## Carried into next week", 1)[-1].split("## Tree activity", 1)[0]
        check("(carried) prepare Q3 budget sheet" in carried_zone,
              "Carried section must show the last note's In-progress")
        activity = rt.split("## Tree activity", 1)[-1].split("## Sources", 1)[0]
        check("| 20-design | 1 |" in activity, "activity table missing 20-design (touched in-week)")
        check("| 40-projects | 1 |" in activity, "activity table missing 40-projects (touched in-week)")
        check("50-policy" not in activity, "activity table counts an out-of-week file (50-policy)")
        check("10-daily" not in activity or f"{THU.isoformat()}" not in activity,
              "activity should not be polluted by the checker's own note writes in-window")
        for n in ("2026-06-08", "2026-06-09", "2026-06-10", THU.isoformat()):
            check(f"{n}-daily-worklog.md" in rt.split("## Sources", 1)[-1],
                  f"Sources must cite {n}'s note")

    if failures:
        print(f"FAIL ({len(failures)}):")
        for f in failures:
            print(f"  {f}")
        return 1
    print("PASS: daily creation + single-(carried) forward + no-overwrite; weekly assembly "
          "(done-by-day, dated decisions, carried, in-window-only activity, sources cited)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
