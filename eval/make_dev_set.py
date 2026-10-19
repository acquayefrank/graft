"""Pick a stratified dev subset of the training tasks (by fix size, then repo)."""

import argparse
import json
import re
from pathlib import Path

BUCKETS = [(0, 5, "tiny"), (6, 20, "small"), (21, 50, "medium"), (51, 150, "large"), (151, 10**9, "huge")]


def changed_lines(patch: str) -> int:
    return sum(1 for l in patch.splitlines() if l[:1] in "+-" and not l.startswith(("+++", "---")))


def bucket(n: int) -> str:
    return next(name for lo, hi, name in BUCKETS if lo <= n <= hi)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", default="data/tasks.jsonl")
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--out", default="eval/dev30.json")
    ap.add_argument("--solvable", help="gold_calibration.jsonl; keep only tasks whose gold patch passes")
    args = ap.parse_args()

    keep = None
    if args.solvable:
        keep = {r["id"] for r in map(json.loads, open(args.solvable)) if r["gold_resolved"]}

    rows = []
    for line in open(args.tasks):
        t = json.loads(line)
        if keep is not None and t["instance_id"] not in keep:
            continue
        n = changed_lines(t["patch"])
        rows.append({
            "instance_id": t["instance_id"],
            "repo": t["repo"],
            "lines": n,
            "files": len(re.findall(r"^\+\+\+ b/", t["patch"], re.M)),
            "new_file": "@@ -0,0 " in t["patch"],
            "bucket": bucket(n),
        })

    # Systematic sampling over a list sorted by (size bucket, repo) keeps both proportions.
    order = {name: i for i, (_, _, name) in enumerate(BUCKETS)}
    rows.sort(key=lambda r: (order[r["bucket"]], r["repo"], r["instance_id"]))
    step = len(rows) / args.n
    picked = [rows[int(i * step + step / 2)] for i in range(args.n)]
    httpx = next((r for r in rows if r["repo"] == "encode/httpx"), None)
    if httpx and httpx not in picked:
        picked[-1] = httpx

    Path(args.out).write_text(json.dumps(picked, indent=1) + "\n")
    print(f"wrote {len(picked)} tasks to {args.out}")
    for key in ("bucket", "repo"):
        counts = {}
        for r in picked:
            counts[r[key]] = counts.get(r[key], 0) + 1
        print(f"  by {key}: {counts}")


if __name__ == "__main__":
    main()
