#!/usr/bin/env python3
"""Builds submission.zip from submission/ directory and validates required assets."""

import os
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SUBMISSION_DIR = ROOT / "submission"
OUT_ZIP = ROOT / "submission.zip"

required_entries = {
    "agent.yaml",
    "eval_config.yaml",
    "prompts/system.md",
    "prompts/analyzer.md",
    "sub_agents/code_analyzer.yaml",
}

if OUT_ZIP.is_file():
    OUT_ZIP.unlink()

with zipfile.ZipFile(OUT_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(SUBMISSION_DIR):
        for file in files:
            if file.endswith((".DS_Store", ".pyc")) or "__pycache__" in root:
                continue
            full_path = Path(root) / file
            arcname = full_path.relative_to(SUBMISSION_DIR).as_posix()
            zf.write(full_path, arcname)

with zipfile.ZipFile(OUT_ZIP, "r") as zf:
    namelist = set(zf.namelist())
    print("--- Archive Contents ---")
    for info in zf.infolist():
        print(f"  {info.filename:<35} {info.file_size:>6} B  (deflated: {info.compress_size:>6} B)")
    
    missing = required_entries - namelist
    if missing:
        sys.exit(f"Error: Missing required files in submission.zip: {missing}")

size_kb = OUT_ZIP.stat().st_size / 1024
if size_kb > 100:
    sys.exit(f"Error: submission.zip size ({size_kb:.1f} KB) exceeds 100 KB ceiling.")

print(f"\n[OK] submission.zip created and verified: {size_kb:.2f} KB (< 100 KB ceiling).")
print(f"[OK] All {len(required_entries)} required declarative assets and sub-agents present.")
