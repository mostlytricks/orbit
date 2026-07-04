"""The orbit intake gate: verify a scouted scratch against the filing contract's
Intake section (.gravity/filing/SPEC.md).

Usage:
    cp -r tests/fixture-sources <scratch>/sources   # the "external" dirs
    mkdir <scratch>/00-inbox
    (run the file-scout skill: desktop+downloads = dump, onedrive-sync = live,
     ingesting into <scratch>/00-inbox)
    python tests/check_scout.py <scratch>

PASS requires: exactly the four work files in 00-inbox (installer + photo skipped),
each with a provenance entry; dump sources emptied of their ingested files; the live
source's file preserved (copied, not moved); skipped files left in their source.
Exit 0 on PASS, 1 on FAIL.
"""

import sys
from pathlib import Path

# ingested filename -> (source folder under sources/, expected action)
INGESTED = {
    "2026-06-30-team-meeting-notes.md": ("desktop", "move"),
    "q3-budget-planning.xlsx": ("desktop", "move"),
    "acme-vendor-contract.pdf": ("downloads", "move"),
    "security-policy-draft.docx": ("onedrive-sync", "copy"),
}

# skipped filename -> source it must remain in (never reaches the inbox)
SKIPPED = {
    "vacation-photo.jpg": "desktop",
    "app-setup-installer.exe": "downloads",
}

PROVENANCE = ".orbit-provenance.jsonl"


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    root = Path(sys.argv[1])
    inbox, sources = root / "00-inbox", root / "sources"
    if not inbox.is_dir() or not sources.is_dir():
        print(f"FAIL: {root} must contain 00-inbox/ and sources/")
        return 1

    failures = []

    # what actually landed in the inbox (ignore .gitkeep + dotfiles like the manifest)
    in_inbox = {
        p.name for p in inbox.iterdir()
        if p.is_file() and not p.name.startswith(".")
    }

    # 1. every expected file ingested; nothing extra
    for name in INGESTED:
        if name not in in_inbox:
            failures.append(f"NOT INGESTED: {name} missing from 00-inbox/")
    for name in in_inbox - set(INGESTED):
        failures.append(f"UNEXPECTED: {name} in 00-inbox/ (should not have been ingested)")

    # 2. skipped files never reached the inbox and stayed in their source
    for name, src in SKIPPED.items():
        if name in in_inbox:
            failures.append(f"WRONGLY INGESTED: {name} (junk/personal, should stay in {src}/)")
        if not (sources / src / name).exists():
            failures.append(f"LOST SKIP: {name} vanished from sources/{src}/ (must be left in place)")

    # 3. move vs copy semantics at the source
    for name, (src, action) in INGESTED.items():
        still_there = (sources / src / name).exists()
        if action == "move" and still_there:
            failures.append(f"NOT MOVED: {name} still in sources/{src}/ (dump source must be emptied)")
        if action == "copy" and not still_there:
            failures.append(f"WRONGLY MOVED: {name} gone from sources/{src}/ (live source must be preserved)")

    # 4. provenance recorded for each ingested file
    manifest = inbox / PROVENANCE
    if not manifest.is_file():
        failures.append(f"NO PROVENANCE: {PROVENANCE} missing from 00-inbox/")
    else:
        text = manifest.read_text(encoding="utf-8", errors="replace")
        for name in INGESTED:
            if name in in_inbox and name not in text:
                failures.append(f"UNRECORDED: {name} has no provenance entry")

    if failures:
        print(f"FAIL ({len(failures)}):")
        for f in failures:
            print(f"  {f}")
        return 1
    print(f"PASS: {len(INGESTED)} files ingested with provenance, "
          f"{len(SKIPPED)} correctly skipped, move/copy semantics honored")
    return 0


if __name__ == "__main__":
    sys.exit(main())
