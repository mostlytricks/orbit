#!/usr/bin/env python3
"""Wire orbit's canonical skills into `.claude/skills/` so Claude Code discovers them.

orbit keeps ONE astra-shaped source of truth under `skills/<name>/SKILL.md` (see
CLAUDE.md). Claude Code only auto-discovers skills under `.claude/skills/`, so this
script creates a link there for each skill folder — a directory junction on Windows,
a symlink on POSIX. The links are machine-local (they resolve to absolute paths) and
are gitignored; run this once after cloning/copying the design instance.

Idempotent. Stdlib only. Relative paths only (never hardcode a machine path), per the
orbit "design here, deploy at work" constraint.

    python .claude/setup-skills.py
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # repo root (parent of .claude/)
SRC = ROOT / "skills"                                   # canonical, astra-shaped
DST = ROOT / ".claude" / "skills"                       # Claude Code discovery root


def is_link(p: Path) -> bool:
    """True if p is a POSIX symlink or a Windows junction/reparse point."""
    if p.is_symlink():
        return True
    try:                                                # Windows junctions aren't symlinks
        return bool(getattr(os.lstat(p), "st_reparse_tag", 0))
    except OSError:
        return False


def each_skill():
    """Yield skill folder names: any `skills/<name>/` containing a SKILL.md."""
    if not SRC.is_dir():
        sys.exit(f"no skills/ dir at {SRC}")
    for child in sorted(SRC.iterdir()):
        if child.is_dir() and (child / "SKILL.md").is_file():
            yield child.name


def link(name: str) -> None:
    src, dst = SRC / name, DST / name
    if is_link(dst):                                    # stale link -> recreate cleanly
        dst.unlink()
    if os.name == "nt":
        # Directory junction: no admin / Developer Mode needed on Windows.
        subprocess.run(["cmd", "/c", "mklink", "/J", str(dst), str(src)],
                       check=True, capture_output=True, text=True)
    else:
        os.symlink(src, dst, target_is_directory=True)
    print(f"linked .claude/skills/{name} -> skills/{name}")


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    names = list(each_skill())
    for name in names:
        dst = DST / name
        if dst.exists() and not is_link(dst):           # real dir with copied-in files
            print(f"skip {name}: real dir at .claude/skills/{name} (not a link)")
            continue
        link(name)
    print(f"\n{len(names)} skill(s) wired for Claude Code. skills/ remains canonical.")


if __name__ == "__main__":
    main()
