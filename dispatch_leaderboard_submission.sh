#!/usr/bin/env bash
# Dispatches verified Phase 7 submission.zip to the Kaggle Leaderboard.
# Run after daily quota resets at 00:00:00 UTC.
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
cd "$(dirname "$0")"

echo "Verifying submission archive..."
python3 build_submission.py

echo "Dispatching to competition: gemma-4-developer-agent..."
kaggle competitions submit -c gemma-4-developer-agent -f submission.zip -m "Project Graft: Phase 7 Multi-Hunk Decomposition & Pre-Flight Syntax Check"

echo "Querying latest submissions:"
kaggle competitions submissions -c gemma-4-developer-agent
