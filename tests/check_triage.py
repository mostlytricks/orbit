"""The orbit gate: verify a triaged copy of tests/fixture-inbox against the filing
contract (.gravity/filing/SPEC.md).

Usage:
    cp -r tests/fixture-inbox <scratch>/00-inbox   # plus empty area dirs, or copy the repo tree
    (run the file-triage skill on <scratch>)
    python tests/check_triage.py <scratch>

<scratch> must contain the six area dirs after triage. PASS requires every fixture
file at its expected home, the two unclassifiable files still in 00-inbox, and no
file lost or invented. Exit 0 on PASS, 1 on FAIL.
"""

import sys
from pathlib import Path

# expected destination (relative to the sorted root) for each fixture file;
# None = must remain in 00-inbox (unclassifiable by contract)
EXPECTED = {
    "2026-07-03-daily-worklog.md": "10-daily/2026/07",
    "2026-W27-weekly-report.md": "10-daily/2026",
    "payment-system-architecture-overview.pptx": "20-design",
    "api-gateway-design-decision.md": "20-design",
    "db-failover-runbook.md": "30-operations",
    "2026-06-25-incident-db-outage.md": "30-operations",
    "erp-upgrade-kickoff-notes.md": "40-projects/erp-upgrade",
    "erp-upgrade-vendor-proposal.pdf": "40-projects/erp-upgrade",
    "information-security-policy-v3.pdf": "50-policy",
    "remote-work-policy-2026.docx": "50-policy",
    "IMG_2041.png": None,
    "notes.txt": None,
}

AREAS = ["00-inbox", "10-daily", "20-design", "30-operations", "40-projects", "50-policy"]


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    root = Path(sys.argv[1])
    if not root.is_dir():
        print(f"FAIL: {root} is not a directory")
        return 1

    failures = []

    found = {
        p.name: p.relative_to(root).parent.as_posix()
        for area in AREAS
        if (root / area).is_dir()
        for p in (root / area).rglob("*")
        if p.is_file() and p.name != ".gitkeep"
    }

    for name, want in EXPECTED.items():
        want = want or "00-inbox"
        got = found.pop(name, None)
        if got is None:
            failures.append(f"LOST: {name} (expected in {want}/)")
        elif got != want:
            failures.append(f"MISFILED: {name} -> {got}/ (expected {want}/)")

    for name, where in sorted(found.items()):
        failures.append(f"UNEXPECTED: {name} in {where}/ (not a fixture file)")

    if failures:
        print(f"FAIL ({len(failures)}):")
        for f in failures:
            print(f"  {f}")
        return 1
    print(f"PASS: all {len(EXPECTED)} fixture files accounted for "
          f"({sum(1 for v in EXPECTED.values() if v)} filed, "
          f"{sum(1 for v in EXPECTED.values() if not v)} correctly held in inbox)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
