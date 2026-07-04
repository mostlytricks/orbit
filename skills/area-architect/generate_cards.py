"""orbit per-area README cards: one browsing card per area, generated from the contract.

Usage:
    python skills/area-architect/generate_cards.py <orbit-root>   # usually: ... .

Writes an `NN-*/README.md` into every active area folder so someone browsing the tree
in a file manager (at work, no agent) sees what belongs there. The text is pulled
straight from the Areas table in `.gravity/filing/SPEC.md` — the SPEC is the single
source of truth; these cards are a *generated artifact* (like dashboard.html) and are
gitignored by the deny-by-default area wall. Edit the contract, never a card.

Tombstoned rows (retired/renumbered) are skipped. Stdlib only, relative paths, ASCII
console output (safe on Korean-Windows cp949). Exit 0 on success, 1 if the SPEC or a
table can't be found.
"""

import re
import sys
from pathlib import Path

# Same row shape check_structure.py keys on, extended to capture both prose columns.
AREA_ROW = re.compile(
    r"^\|\s*`(\d{2}-[a-z0-9-]+)/`\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*$"
)

FOOTER = (
    "---\n"
    "_Generated from [`.gravity/filing/SPEC.md`](../.gravity/filing/SPEC.md) — the filing "
    "contract. Edit the contract, not this card; then regenerate with "
    "`python skills/area-architect/generate_cards.py .`. This file is gitignored "
    "(structure travels by copy, cards regenerate)._\n"
)


def areas(spec: Path) -> list[tuple[str, str, str]]:
    """(name, belongs, not_belongs) for each active (non-tombstone) area row."""
    out = []
    for line in spec.read_text(encoding="utf-8").splitlines():
        m = AREA_ROW.match(line)
        if not m:
            continue
        name, belongs, not_belongs = m.group(1), m.group(2), m.group(3)
        if "retired" in line.lower() or "renumbered" in line.lower():
            continue  # tombstone row — no folder on disk, no card
        out.append((name, belongs.strip(), not_belongs.strip()))
    return out


def card(name: str, belongs: str, not_belongs: str) -> str:
    num, label = name.split("-", 1)
    return (
        f"# {num} — {label}\n\n"
        f"**Belongs here:** {belongs}\n\n"
        f"**Not here:** {not_belongs}\n\n"
        f"{FOOTER}"
    )


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    spec = root / ".gravity" / "filing" / "SPEC.md"
    if not spec.is_file():
        print(f"FAIL: no contract at {spec}")
        return 1

    rows = areas(spec)
    if not rows:
        print(f"FAIL: no area rows parsed from {spec} (table format changed?)")
        return 1

    wrote, skipped = 0, 0
    for name, belongs, not_belongs in rows:
        area_dir = root / name
        if not area_dir.is_dir():
            print(f"  skip: {name}/ has no directory (run check_structure.py)")
            skipped += 1
            continue
        (area_dir / "README.md").write_text(card(name, belongs, not_belongs), encoding="utf-8")
        print(f"  wrote: {name}/README.md")
        wrote += 1

    print(f"OK: {wrote} area card(s) generated{f', {skipped} skipped' if skipped else ''}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
