#!/usr/bin/env bash
# Downloads kernel output from graft-dev-eval into results/<run_name>
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
cd "$(dirname "$0")"

run_name="${1:-latest}"
out_dir="results/$run_name"
mkdir -p "$out_dir"
echo "Downloading results for graft-dev-eval into $out_dir..."
kaggle kernels output acquayefrank/graft-dev-eval -p "$out_dir" -o

# Unpack any result zip
for z in "$out_dir"/*_results.zip; do
  if [ -f "$z" ]; then
    echo "Unpacking $z..."
    unzip -qo "$z" -d "$out_dir/results"
  fi
done
echo "Results downloaded to $out_dir"
if [ -f "$out_dir/results/dev_summary.json" ]; then
  cat "$out_dir/results/dev_summary.json"
fi
