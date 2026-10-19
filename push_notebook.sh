#!/usr/bin/env bash
# Builds notebook/graft-dev-eval.ipynb and pushes it to Kaggle for remote execution.
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
cd "$(dirname "$0")"

python3 notebook/build_notebook.py
kaggle kernels push -p notebook/
echo "Notebook pushed to Kaggle."
echo "Check status: kaggle kernels status acquayefrank/graft-dev-eval"
