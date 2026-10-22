#!/usr/bin/env bash
# Dispatches verified fallback submission.zip to the Kaggle Leaderboard.
# Run after daily quota resets at 00:00:00 UTC.
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
cd "$(dirname "$0")"

echo "Verifying submission archive..."
python3 build_submission.py

echo "Dispatching to competition: gemma-4-developer-agent..."
kaggle competitions submit -c gemma-4-developer-agent -f submission.zip -m "Project Graft: Paced Single-Agent (recovered_v2 recalibrated fallback)"

echo "Querying latest submissions:"
kaggle competitions submissions -c gemma-4-developer-agent
