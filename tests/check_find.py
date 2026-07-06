"""The orbit gate: verify a file-find answer report against the planted fixture tree.

Usage:
    cp -r tests/fixture-find/tree/. <scratch>/
    (run the file-find skill on <scratch> over tests/fixture-find/queries.json,
     writing <scratch>/find-report.json)
    python tests/check_find.py <scratch>

PASS requires: one answer per query; clear hits resolve to the exact path as top
candidate; the ambiguous ask returns BOTH plausible candidates (never a silent
pick); the true miss carries the right diagnosis and a home prediction; the
planted misfile is found AND flagged with its predicted home; every candidate
path exists; and the tree is byte-identical afterwards (find is read-only).
Exit 0 on PASS, 1 on FAIL.
"""

import hashlib
import json
import sys
from pathlib import Path

FIXTURE = Path(__file__).resolve().parent / "fixture-find" / "tree"

# per-query expectations
TOP1 = {  # clear hits: this exact path must be candidates[0]
    "q1": "30-operations/dr-recovery-runbook.md",
    "q2": "40-projects/erp-upgrade/erp-upgrade-vendor-proposal.txt",
    "q3": "40-projects/erp-upgrade/erp-upgrade-vendor-proposal.txt",
    "q6": "20-design/patch-tuesday-runbook.md",
    "q7": "00-inbox/2026-06-30-vendor-security-scan.txt",
}
AMBIG = {  # both must appear in the top 3 candidates
    "q4": ["20-design/2023-03-10-dr-failover-design.md",
           "30-operations/2023-09-02-dr-drill-incident-report.md"],
}
MISS = {  # verdict miss + this diagnosis + prediction under this area
    "q5": ("never-ingested", "20-design"),
}
MISFILED = {  # found, but must carry a misfiled flag predicting this area
    "q6": "30-operations",
}
ALL_IDS = ["q1", "q2", "q3", "q4", "q5", "q6", "q7"]


def inventory(root: Path):
    """{relative-posix-path: md5} for every file in the area dirs (skip .gitkeep)."""
    inv = {}
    for d in sorted(root.iterdir()):
        if d.is_dir() and d.name[:1].isdigit():
            for p in d.rglob("*"):
                if p.is_file() and p.name != ".gitkeep":
                    inv[p.relative_to(root).as_posix()] = hashlib.md5(p.read_bytes()).hexdigest()
    return inv


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    root = Path(sys.argv[1])
    if not root.is_dir():
        print(f"FAIL: {root} is not a directory")
        return 1

    failures = []
    report_path = root / "find-report.json"
    if not report_path.is_file():
        print(f"FAIL: {report_path} not found - the skill must write its answer report there")
        return 1
    try:
        answers = {a["id"]: a for a in json.loads(report_path.read_text(encoding="utf-8"))["answers"]}
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"FAIL: find-report.json unreadable ({e})")
        return 1

    tree = inventory(root)

    for qid in ALL_IDS:
        if qid not in answers:
            failures.append(f"UNANSWERED: {qid} has no entry in the report")
    for qid in answers:
        if qid not in ALL_IDS:
            failures.append(f"UNEXPECTED: {qid} is not a fixture query")

    for qid, a in answers.items():
        for c in a.get("candidates", []):
            if c not in tree:
                failures.append(f"INVENTED: {qid} names candidate {c} which does not exist")

    for qid, want in TOP1.items():
        a = answers.get(qid)
        if not a:
            continue
        cands = a.get("candidates", [])
        if a.get("verdict") != "found":
            failures.append(f"WRONG VERDICT: {qid} expected found, got {a.get('verdict')}")
        elif not cands or cands[0] != want:
            failures.append(f"WRONG HIT: {qid} top candidate {cands[0] if cands else '(none)'} "
                            f"(expected {want})")

    for qid, both in AMBIG.items():
        a = answers.get(qid)
        if not a:
            continue
        top3 = a.get("candidates", [])[:3]
        if a.get("verdict") != "found":
            failures.append(f"WRONG VERDICT: {qid} expected found (ambiguous), got {a.get('verdict')}")
        if len(a.get("candidates", [])) < 2:
            failures.append(f"SILENT PICK: {qid} must return multiple ranked candidates")
        for want in both:
            if want not in top3:
                failures.append(f"MISSING CANDIDATE: {qid} lacks {want} in its top 3")

    for qid, (diag, area) in MISS.items():
        a = answers.get(qid)
        if not a:
            continue
        if a.get("verdict") != "miss":
            failures.append(f"WRONG VERDICT: {qid} expected miss, got {a.get('verdict')}")
        if a.get("diagnosis") != diag:
            failures.append(f"WRONG DIAGNOSIS: {qid} got {a.get('diagnosis')} (expected {diag})")
        if not str(a.get("predicted", "")).startswith(area):
            failures.append(f"NO PREDICTION: {qid} must predict a home under {area}/ "
                            f"(got {a.get('predicted')})")

    for qid, area in MISFILED.items():
        a = answers.get(qid)
        if not a:
            continue
        mf = a.get("misfiled")
        if not mf:
            failures.append(f"UNFLAGGED MISFILE: {qid} found the planted misfile but did not flag it")
        elif not str(mf.get("predicted", "")).startswith(area):
            failures.append(f"WRONG MISFILE TARGET: {qid} predicts {mf.get('predicted')} "
                            f"(expected under {area}/)")

    pristine = inventory(FIXTURE)
    if tree != pristine:
        for path in sorted(set(pristine) - set(tree)):
            failures.append(f"MUTATED: {path} missing after find (read-only wall)")
        for path in sorted(set(tree) - set(pristine)):
            failures.append(f"MUTATED: {path} appeared during find (read-only wall)")
        for path in sorted(set(tree) & set(pristine)):
            if tree[path] != pristine[path]:
                failures.append(f"MUTATED: {path} content changed during find (read-only wall)")

    if failures:
        print(f"FAIL ({len(failures)}):")
        for f in failures:
            print(f"  {f}")
        return 1
    print(f"PASS: {len(ALL_IDS)} queries answered - {len(TOP1)} exact hits, "
          f"{len(AMBIG)} ambiguous with full candidates, {len(MISS)} miss correctly "
          f"diagnosed, {len(MISFILED)} planted misfile flagged, tree untouched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
