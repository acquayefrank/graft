#!/usr/bin/env bash
# Uploads submission/ as the private Kaggle dataset acquayefrank/graft-submission
# (creates it on first run, adds a new version afterwards) so the dev-eval notebook can use it.
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
cd "$(dirname "$0")"
msg="${1:-update $(date -u +%Y-%m-%dT%H:%MZ)}"
stage="build/dataset"
rm -rf "$stage" && mkdir -p "$stage"
cp -r submission/. "$stage/"
cat > "$stage/dataset-metadata.json" <<'JSON'
{"title": "graft-submission", "id": "acquayefrank/graft-submission", "licenses": [{"name": "other"}]}
JSON
if kaggle datasets status acquayefrank/graft-submission >/dev/null 2>&1; then
  kaggle datasets version -p "$stage" -m "$msg" --dir-mode zip
else
  kaggle datasets create -p "$stage" --dir-mode zip
fi
