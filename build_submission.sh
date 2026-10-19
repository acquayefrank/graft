#!/usr/bin/env bash
# Packages submission/ into submission.zip with agent.yaml at the archive root.
set -euo pipefail
cd "$(dirname "$0")/submission"
rm -f ../submission.zip
zip -r ../submission.zip . -x '*.DS_Store' '*__pycache__*'
unzip -l ../submission.zip
