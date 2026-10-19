"""Compare two evaluation runs side-by-side.

Usage:
    python eval/compare_runs.py results/<run_a>/results/<run_a> results/<run_b>/results/<run_b>
    python eval/compare_runs.py results/<run_a>/dev_summary.json results/<run_b>/dev_summary.json
"""

import json
import sys
from pathlib import Path


def load_run(path_str: str) -> tuple[dict, dict[str, dict]]:
    path = Path(path_str)

    # 1. Direct JSON file
    if path.is_file() and path.name.endswith(".json"):
        summary = json.loads(path.read_text(encoding="utf-8"))
        rows_file = path.parent / "dev_rows.jsonl"
        if not rows_file.exists():
            candidates = list(path.parent.glob("**/dev_rows.jsonl"))
            rows_file = candidates[0] if candidates else rows_file

    # 2. Directory or path search
    else:
        # If path doesn't exist, try resolving from parent directories
        search_root = path
        while not search_root.exists() and search_root.parent != search_root:
            search_root = search_root.parent

        if not search_root.exists():
            raise ValueError(f"Path does not exist: {path_str}")

        # Search for dev_summary.json
        candidate_summaries = []
        if (search_root / "dev_summary.json").is_file():
            candidate_summaries.append(search_root / "dev_summary.json")
        candidate_summaries.extend(search_root.rglob("dev_summary.json"))

        if not candidate_summaries:
            raise ValueError(f"Could not find dev_summary.json in {search_root}")

        summary_file = candidate_summaries[0]
        summary = json.loads(summary_file.read_text(encoding="utf-8"))
        rows_file = summary_file.parent / "dev_rows.jsonl"
        if not rows_file.exists():
            candidate_rows = list(search_root.rglob("dev_rows.jsonl"))
            rows_file = candidate_rows[0] if candidate_rows else rows_file

    rows = {}
    if rows_file and rows_file.exists():
        for line in rows_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                item = json.loads(line)
                rows[item["id"]] = item
    return summary, rows


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    sum_a, rows_a = load_run(sys.argv[1])
    sum_b, rows_b = load_run(sys.argv[2])

    name_a = sum_a.get("run", sys.argv[1])
    name_b = sum_b.get("run", sys.argv[2])

    print("=" * 80)
    print(f"RUN COMPARISON: {name_a} vs {name_b}")
    print("=" * 80)
    print(f"{'Metric':<30} | {name_a:<20} | {name_b:<20} | {'Delta':<10}")
    print("-" * 80)

    for metric, fmt in [
        ("tasks", "{:d}"),
        ("resolved", "{:d}"),
        ("resolution_rate", "{:.1%}"),
        ("mean_agent_seconds", "{:.1f}s"),
        ("mean_wall_seconds", "{:.1f}s"),
        ("mean_tool_calls", "{:.1f}"),
    ]:
        val_a = sum_a.get(metric)
        val_b = sum_b.get(metric)
        str_a = fmt.format(val_a) if val_a is not None else "-"
        str_b = fmt.format(val_b) if val_b is not None else "-"
        delta = ""
        if val_a is not None and val_b is not None and isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
            diff = val_b - val_a
            sign = "+" if diff > 0 else ""
            delta = f"{sign}{diff:.2f}"
        print(f"{metric:<30} | {str_a:<20} | {str_b:<20} | {delta:<10}")

    print("-" * 80)
    print("PER-TASK BREAKDOWN:")
    all_tasks = sorted(set(rows_a.keys()) | set(rows_b.keys()))
    print(f"{'Task ID':<16} | {name_a + ' Res':<12} | {name_b + ' Res':<12} | {name_a + ' Time':<12} | {name_b + ' Time':<12}")
    print("-" * 80)

    for tid in all_tasks:
        ra = rows_a.get(tid, {})
        rb = rows_b.get(tid, {})
        res_a = "RESOLVED" if ra.get("resolved") else ("TIMEOUT" if "timeout" in ra.get("error", "").lower() else ("FAIL" if ra else "-"))
        res_b = "RESOLVED" if rb.get("resolved") else ("TIMEOUT" if "timeout" in rb.get("error", "").lower() else ("FAIL" if rb else "-"))
        time_a = f"{ra.get('agent_seconds', 0.0):.1f}s" if ra else "-"
        time_b = f"{rb.get('agent_seconds', 0.0):.1f}s" if rb else "-"
        marker = "  "
        if not ra.get("resolved") and rb.get("resolved"):
            marker = "++"
        elif ra.get("resolved") and not rb.get("resolved"):
            marker = "--"
        print(f"{marker} {tid:<14} | {res_a:<12} | {res_b:<12} | {time_a:<12} | {time_b:<12}")
    print("=" * 80)


if __name__ == "__main__":
    main()
