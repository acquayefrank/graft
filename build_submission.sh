#!/usr/bin/env bash
# Packages submission/ into submission.zip with agent.yaml at the archive root.
# Validates required declarative files, sub-agents, and prompt assets.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR/submission"

rm -f ../submission.zip
zip -r ../submission.zip . -x '*.DS_Store' '*__pycache__*'

echo "--- Archive Contents ---"
unzip -l ../submission.zip

# Verification of required bundle components
PYTHON_BIN="$(command -v python3 || command -v python)"
"$PYTHON_BIN" - <<'PY'
import sys
import zipfile
from pathlib import Path

zip_path = Path("../submission.zip")
if not zip_path.is_file():
    sys.exit("Error: submission.zip was not created.")

required_entries = {
    "agent.yaml",
    "eval_config.yaml",
    "prompts/system.md",
    "prompts/analyzer.md",
    "sub_agents/code_analyzer.yaml",
}

with zipfile.ZipFile(zip_path, 'r') as zf:
    namelist = set(zf.namelist())
    missing = required_entries - namelist
    if missing:
        sys.exit(f"Error: Missing required files in submission.zip: {missing}")

size_kb = zip_path.stat().st_size / 1024
if size_kb > 100:
    sys.exit(f"Error: submission.zip size ({size_kb:.1f} KB) exceeds 100 KB ceiling.")

print(f"\n[OK] submission.zip verified successfully: {size_kb:.2f} KB (< 100 KB ceiling).")
print(f"[OK] All {len(required_entries)} required declarative assets and sub-agent files present.")
PY
