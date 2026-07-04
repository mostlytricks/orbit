"""orbit waypoint-manifest lint: verify every `_waypoint.md` against the schema.

Usage:
    python tests/check_waypoint.py <root>        # e.g. tests/fixture-waypoint  (or . )

Finds every waypoint (a dir holding `_waypoint.md`), parses its YAML frontmatter
(the same tiny scalar + inline-list subset build_index.py accepts), and requires:
  - a non-empty `purpose`
  - a non-empty `keywords` list
  - `keywords` / `file_types` are lists (inline `[...]`), not scalars
  - `status`, if present, is one of active / archive / frozen
The schema lives in `.gravity/waypoint/SPEC.md`; this checker holds none of its own.
Stdlib only. Exit 0 on PASS (0 manifests is a vacuous PASS), 1 on FAIL naming offenders.
"""

import sys
from pathlib import Path

MANIFEST = "_waypoint.md"
INFRA = {".git", ".gravity", ".claude", "skills", "tests", "docs",
         "__pycache__", ".venv", "node_modules"}
STATUS = {"active", "archive", "frozen"}


def parse_frontmatter(text: str) -> dict | None:
    if not text.startswith("---"):
        return None
    lines = text.splitlines()
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return None
    data: dict = {}
    for line in lines[1:end]:
        s = line.strip()
        if not s or s.startswith("#") or ":" not in line:
            continue
        key, _, val = line.partition(":")
        key, val = key.strip(), val.strip()
        if val.startswith("[") and val.endswith("]"):
            data[key] = [x.strip().strip("\"'") for x in val[1:-1].split(",") if x.strip()]
        else:
            data[key] = val.strip("\"'")
    return data


def manifests(root: Path):
    """Yield every _waypoint.md path under root, pruning infra/hidden dirs."""
    stack = [root]
    while stack:
        d = stack.pop()
        try:
            children = list(d.iterdir())
        except OSError:
            continue
        for c in children:
            if c.is_dir() and c.name not in INFRA and not c.name.startswith("."):
                stack.append(c)
        if (d / MANIFEST).is_file():
            yield d / MANIFEST


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    if not root.is_dir():
        print(f"FAIL: no such root {root}")
        return 1

    found, failures = 0, []
    for m in manifests(root):
        found += 1
        where = m.relative_to(root).as_posix()
        fm = parse_frontmatter(m.read_text(encoding="utf-8", errors="replace"))
        if fm is None:
            failures.append(f"NO FRONTMATTER: {where} has no `---` YAML block")
            continue

        purpose = fm.get("purpose")
        if not (isinstance(purpose, str) and purpose.strip()):
            failures.append(f"NO PURPOSE: {where} is missing a non-empty `purpose`")

        kw = fm.get("keywords")
        if not isinstance(kw, list) or not kw:
            failures.append(f"BAD KEYWORDS: {where} needs a non-empty inline list `keywords: [a, b]`")

        ftypes = fm.get("file_types")
        if ftypes is not None and not isinstance(ftypes, list):
            failures.append(f"BAD FILE_TYPES: {where} `file_types` must be an inline list `[...]`")

        status = fm.get("status")
        if status and status not in STATUS:
            failures.append(f"BAD STATUS: {where} status '{status}' not in {sorted(STATUS)}")

    if failures:
        print(f"FAIL ({len(failures)}):")
        for f in failures:
            print(f"  {f}")
        return 1
    print(f"PASS: {found} waypoint{'' if found == 1 else 's'} valid "
          f"(all manifests carry purpose + keywords)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
