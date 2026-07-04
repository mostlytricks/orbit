"""Build orbit's waypoint index: scan every _waypoint.md manifest, emit waypoint-index.md.

Usage:
    python skills/locate/build_index.py <orbit-root>   # usually: ... .

Walks the tree for waypoints (any dir holding a `_waypoint.md`), reads each manifest's
YAML frontmatter (a tiny scalar + inline-list subset — orbit carries no PyYAML),
computes that directory's file-count and size, and writes a single `waypoint-index.md`
at the root: the one cheap file an agent reads to answer "where is X?" without listing
payload. See `.gravity/waypoint/SPEC.md`.

Stdlib only, relative paths, ASCII console output (safe on Korean-Windows cp949).
`waypoint-index.md` is a generated artifact (gitignored, per-instance runtime).
"""

import sys
from datetime import date
from pathlib import Path

MANIFEST = "_waypoint.md"
INDEX = "waypoint-index.md"
# Never descend into these when hunting for manifests / counting payload.
INFRA = {".git", ".gravity", ".claude", "skills", "tests", "docs",
         "__pycache__", ".venv", "node_modules"}


def parse_frontmatter(text: str) -> dict | None:
    """Tiny YAML subset between `---` fences: `key: scalar` and `key: [a, b]`. None if absent."""
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


def walk_dirs(root: Path):
    """Yield every directory under root (inclusive), pruning infra and hidden dirs."""
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
        yield d


def dir_stats(d: Path) -> tuple[int, int]:
    """(file_count, size_bytes) recursively under d, excluding the manifest and hidden/junk."""
    count, size = 0, 0
    stack = [d]
    while stack:
        cur = stack.pop()
        try:
            children = list(cur.iterdir())
        except OSError:
            continue
        for c in children:
            if c.name.startswith(".") or c.name in INFRA:
                continue
            if c.is_dir():
                stack.append(c)
            elif c.is_file() and c.name != MANIFEST:
                count += 1
                try:
                    size += c.stat().st_size
                except OSError:
                    pass
    return count, size


def human(n: int) -> str:
    x = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if x < 1024:
            return f"{int(x)} {unit}" if unit == "B" else f"{x:.1f} {unit}"
        x /= 1024
    return f"{x:.1f} TB"


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    rows = []
    for d in walk_dirs(root):
        if not (d / MANIFEST).is_file():
            continue
        fm = parse_frontmatter((d / MANIFEST).read_text(encoding="utf-8", errors="replace")) or {}
        count, size = dir_stats(d)
        kw = fm.get("keywords", [])
        rows.append({
            "path": d.relative_to(root).as_posix() + "/",
            "purpose": str(fm.get("purpose", "")).replace("|", "\\|"),
            "keywords": ", ".join(kw) if isinstance(kw, list) else str(kw),
            "status": str(fm.get("status", "")),
            "period": str(fm.get("period", "")),
            "files": count,
            "size": human(size),
        })
    rows.sort(key=lambda r: r["path"])

    n = len(rows)
    out = [
        "# Waypoint index -- curated directories (generated; do not edit)",
        "",
        "<!-- Built by skills/locate/build_index.py from every _waypoint.md in the tree.",
        "     Answer location questions from THIS file; never ls a waypoint's payload dir. -->",
        "",
        f"_{n} waypoint{'' if n == 1 else 's'} - scanned {date.today().isoformat()}_",
        "",
    ]
    if rows:
        out += ["| Path | Status | Period | Files | Size | Purpose | Keywords |",
                "|---|---|---|---|---|---|---|"]
        out += [f"| {r['path']} | {r['status']} | {r['period']} | {r['files']} | "
                f"{r['size']} | {r['purpose']} | {r['keywords']} |" for r in rows]
    else:
        out.append("_No waypoints yet. Add a `_waypoint.md` to a directory worth finding "
                   "(see .gravity/waypoint/SPEC.md)._")
    out.append("")
    (root / INDEX).write_text("\n".join(out), encoding="utf-8")
    print(f"OK: {n} waypoint{'' if n == 1 else 's'} indexed -> {INDEX}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
