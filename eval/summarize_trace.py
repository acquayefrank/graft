"""Print a compact step-by-step view of swegemma trace files.

Usage: python3 eval/summarize_trace.py results/<run>/traces/trace_<id>.json [...]
"""

import json
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def short(value, n: int) -> str:
    text = value if isinstance(value, str) else json.dumps(value)
    text = " ".join(text.split())
    return text if len(text) <= n else text[: n - 3] + "..."


def summarize(path: str) -> None:
    trace = json.loads(Path(path).read_text(encoding="utf-8"))
    m = trace.get("final_metrics", {})
    print(f"=== {path}")
    print(f"steps={m.get('total_steps')} prompt_tok={m.get('total_prompt_tokens')} "
          f"completion_tok={m.get('total_completion_tokens')} cached_tok={m.get('total_cached_tokens')}")
    for step in trace["steps"]:
        if step["source"] != "agent":
            continue
        obs = step.get("observation") or {}
        content = obs.get("content", "")
        try:
            parsed = json.loads(content)
            status = parsed.get("status", "?")
            detail = parsed.get("error_message") or parsed.get("stdout") or parsed.get("content") or ""
        except (json.JSONDecodeError, AttributeError):
            status, detail = "-", content
        elapsed = (obs.get("extra") or {}).get("elapsed_s")
        timing = f"{elapsed:5.1f}s" if isinstance(elapsed, (int, float)) else "     "
        for call in step.get("tool_calls") or [{"function_name": "(text)", "arguments": step.get("message", "")}]:
            print(f"  #{step['step_id']:<3} {timing} {call['function_name']:<20} {short(call.get('arguments'), 90)}")
        if content:
            print(f"        -> {status}: {short(detail, 110)}")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        summarize(p)
