"""orbit structure lint: verify the top-level tree against .gravity/filing/SPEC.md.

Usage:
    python tests/check_structure.py <orbit-root>     # usually: python tests/check_structure.py .

Reads the Areas table straight from the SPEC (single source of truth — the checker
holds no area list of its own), then verifies:
  - every non-tombstone contract area exists as a top-level directory
  - every top-level directory is a contract area or known infrastructure (no rogues)
  - numbering is legal: two digits, multiple of 10, unique, 00-inbox present
  - top-layer budget: WARN at 7+ areas, FAIL at 9+
Runs anywhere Python stdlib runs — including the populated work instance.
Exit 0 on PASS (warnings allowed), 1 on FAIL.
"""

import re
import sys
from pathlib import Path

INFRA = {".git", ".gravity", ".claude", "skills", "tests", "docs"}
AREA_ROW = re.compile(r"^\|\s*`(\d{2}-[a-z0-9-]+)/`\s*\|")
AREA_DIR = re.compile(r"^\d")

WARN_AT = 7
FAIL_AT = 9


def contract_areas(spec: Path) -> tuple[list[str], list[str]]:
    """(active areas, tombstoned areas) from the SPEC's Areas table."""
    active, retired = [], []
    for line in spec.read_text(encoding="utf-8").splitlines():
        m = AREA_ROW.match(line)
        if m:
            (retired if "retired" in line.lower() else active).append(m.group(1))
    return active, retired


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    spec = root / ".gravity" / "filing" / "SPEC.md"
    if not spec.is_file():
        print(f"FAIL: no contract at {spec}")
        return 1

    active, retired = contract_areas(spec)
    if not active:
        print(f"FAIL: no area rows parsed from {spec} (table format changed?)")
        return 1

    tree = {p.name for p in root.iterdir() if p.is_dir()}
    failures, warnings = [], []

    for area in active:
        if area not in tree:
            failures.append(f"MISSING: contract area {area}/ has no directory")
    for area in retired:
        if area in tree:
            failures.append(f"UNRETIRED: {area}/ is tombstoned in the contract but still on disk")
    for d in sorted(tree - set(active) - INFRA):
        kind = "ROGUE AREA" if AREA_DIR.match(d) else "ROGUE DIR"
        failures.append(f"{kind}: {d}/ is not in the contract's Areas table")

    if "00-inbox" not in active:
        failures.append("NUMBERING: 00-inbox missing from the contract")
    seen = set()
    for area in active + retired:
        num = area[:2]
        if int(num) % 10 != 0:
            failures.append(f"NUMBERING: {area} is not a multiple of 10")
        if num in seen:
            failures.append(f"NUMBERING: slot {num} used twice")
        seen.add(num)

    n = len(active)
    if n >= FAIL_AT:
        failures.append(f"BUDGET: {n} areas (fail at {FAIL_AT}+) — width is expensive; use subfolders")
    elif n >= WARN_AT:
        warnings.append(f"BUDGET: {n} areas — approaching the 7±2 ceiling; next addition needs strong evidence")

    for w in warnings:
        print(f"  WARN: {w}")
    if failures:
        print(f"FAIL ({len(failures)}):")
        for f in failures:
            print(f"  {f}")
        return 1
    print(f"PASS: {n} areas match the contract ({len(retired)} tombstoned), numbering legal, budget ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
