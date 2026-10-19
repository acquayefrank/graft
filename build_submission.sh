#!/usr/bin/env bash
# Packages submission/ into submission.zip with agent.yaml at the archive root.
# Validates required declarative files, sub-agents, and prompt assets.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_BIN="$(command -v python3 || command -v python)"
"$PYTHON_BIN" "$ROOT_DIR/build_submission.py"
