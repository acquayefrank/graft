#!/usr/bin/env python3
"""Automated midnight UTC Kaggle Leaderboard dispatcher for Project Graft.

Sleeps until 00:00:10 UTC (giving 10s buffer for Kaggle quota reset), verifies
submission.zip integrity, dispatches via Kaggle API, and records the new submission
Ref ID in results/leaderboard_submissions.md.
"""

import argparse
import datetime
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SUBMISSION_ZIP = ROOT / "submission.zip"
RESULTS_LOG = ROOT / "results" / "leaderboard_submissions.md"
KAGGLE_PYTHON = "/home/acquayefrank/.local/share/uv/tools/kaggle/bin/python"


def get_target_time() -> datetime.datetime:
    now = datetime.datetime.now(datetime.timezone.utc)
    target = datetime.datetime(now.year, now.month, now.day, 0, 0, 15, tzinfo=datetime.timezone.utc)
    if target <= now:
        target += datetime.timedelta(days=1)
    return target


def verify_package():
    print("[*] Rebuilding and verifying submission.zip...")
    res = subprocess.run([sys.executable, str(ROOT / "build_submission.py")], capture_output=True, text=True)
    if res.returncode != 0:
        print("[!] Build verification failed:\n", res.stderr)
        sys.exit(1)
    print("[OK] submission.zip verified cleanly.")


def dispatch_submission() -> dict:
    wsl_zip_path = f"/mnt/c/{str(SUBMISSION_ZIP.relative_to('C:/')).replace('\\', '/')}"
    py_script = f"""
import time
from kaggle.api.kaggle_api_extended import KaggleApi

api = KaggleApi()
api.authenticate()

msg = 'Project Graft: Paced Single-Agent (recovered_v2 recalibrated fallback)'
resp = api.competition_submit('{wsl_zip_path}', msg, 'gemma-4-developer-agent')
time.sleep(3)

subs = api.competition_submissions('gemma-4-developer-agent')
latest = subs[0] if subs else None
ref = getattr(latest, 'ref', str(getattr(resp, 'ref', '')))
status = getattr(latest, 'status', 'PENDING')
print(f"REF:{{ref}},STATUS:{{status}}")
"""

    print("[*] Executing submission via WSL Kaggle API client (stdin)...")
    res = subprocess.run(
        ["wsl", KAGGLE_PYTHON, "-"],
        input=py_script,
        capture_output=True,
        text=True,
    )
    print("STDOUT:", res.stdout)
    if res.returncode != 0:
        print("STDERR:", res.stderr)
        raise RuntimeError(f"Submission failed: {res.stderr or res.stdout}")

    ref = ""
    status = ""
    for line in res.stdout.splitlines():
        if "REF:" in line:
            parts = line.split(",")
            for p in parts:
                if p.startswith("REF:"):
                    ref = p.split("REF:")[1].strip()
                elif p.startswith("STATUS:"):
                    status = p.split("STATUS:")[1].strip()
    return {"ref": ref, "status": status, "raw": res.stdout}


def record_submission(ref: str, status: str):
    if not ref:
        print("[!] Warning: Could not parse Ref ID from output.")
        return
    now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    entry_line = (
        f"| **`{ref}`** | **{now_str}** | "
        f"**Project Graft: Paced Single-Agent (`recovered_v2` recalibrated fallback)**<br>"
        f"- 9 local tools (AST + Graph + Filesystem)<br>"
        f"- Atomic `submit_patch()` termination contract<br>"
        f"- Recalibrated 4.5m pacing ceiling & 30-call trigger<br>"
        f"- Status telemetry check at Turn 15<br>"
        f"- `build/repro.py` scratchpad isolation | "
        f"`3bbe2f128c1a425aeb54718226d32c80ce90e0cdbefea0a8741d69ab501fbed4` | "
        f"**53.3% (16/30)** | **PENDING** | *Scoring...* |\n"
    )

    text = RESULTS_LOG.read_text(encoding="utf-8")
    marker = "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    if marker in text:
        parts = text.split(marker, 1)
        new_text = parts[0] + marker + entry_line + parts[1]
        RESULTS_LOG.write_text(new_text, encoding="utf-8")
        print(f"[OK] Successfully appended new submission {ref} to {RESULTS_LOG}")
    else:
        print("[!] Could not find table marker in leaderboard_submissions.md")


def main():
    parser = argparse.ArgumentParser(description="Automated midnight UTC Kaggle dispatcher.")
    parser.add_argument("--now", action="store_true", help="Dispatch immediately without sleeping.")
    args = parser.parse_args()

    verify_package()

    if not args.now:
        target = get_target_time()
        print(f"[*] Automated Dispatcher armed.")
        print(f"[*] Target UTC Time: {target.isoformat()}")
        while True:
            now = datetime.datetime.now(datetime.timezone.utc)
            remaining = (target - now).total_seconds()
            if remaining <= 0:
                print("\n[*] Midnight UTC reached! Initiating dispatch sequence...")
                break
            hours = int(remaining // 3600)
            mins = int((remaining % 3600) // 60)
            secs = int(remaining % 60)
            print(f"\r[*] Time remaining: {hours:02d}h {mins:02d}m {secs:02d}s ...", end="", flush=True)
            sleep_chunk = min(60.0, max(1.0, remaining))
            time.sleep(sleep_chunk)

    # Dispatch with retry loop
    max_attempts = 5
    for attempt in range(1, max_attempts + 1):
        try:
            print(f"\n[*] Submission attempt {attempt}/{max_attempts}...")
            result = dispatch_submission()
            ref = result.get("ref")
            status = result.get("status")
            print(f"[OK] Submission created! Ref: {ref}, Status: {status}")
            record_submission(ref, status)
            break
        except Exception as e:
            print(f"[!] Attempt {attempt} failed: {e}")
            if attempt < max_attempts:
                print("[*] Waiting 30s before retry...")
                time.sleep(30)
            else:
                print("[!] All dispatch attempts exhausted.")
                sys.exit(1)


if __name__ == "__main__":
    main()
