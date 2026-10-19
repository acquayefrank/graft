"""Build the gold-patch calibration notebook (notebook/calibration/).

It applies each task's reference patch and runs the Phase 2 verifier in the same subprocess sandbox
the dev-eval notebook uses. Tasks whose gold patch fails there cannot be solved in that environment,
so they should be excluded from (or reported separately in) dev scores. CPU only; no model needed.

Run from the repo root:  python3 notebook/build_calibration.py
"""

import json
from pathlib import Path

from build_notebook import KAGGLE_USER, ROOT, SETUP, code, md

KERNEL_SLUG = "graft-gold-calibration"

INTRO = """# graft: gold-patch calibration

Verifies every training task's reference patch in the notebook's subprocess sandbox, so dev scores can be
read against what is solvable here. Writes `/kaggle/working/gold_calibration.jsonl`. CPU only."""

RUN = r'''import asyncio
import concurrent.futures
import json
import time
from adk_submission import ModelRegistry
from swegemma.config import EvalConfig
from swegemma.deduplication import resolve_task_snapshot_paths
from swegemma.evaluate import Evaluator
from swegemma.harness.verification import verify_task
from swegemma.models import load_tasks

DATA_DIR = Path('/kaggle/input/competitions/gemma-4-developer-agent')
WORKING_DIR = Path('/kaggle/working')
OUT = WORKING_DIR / 'gold_calibration.jsonl'

config = EvalConfig(
    tasks_path=DATA_DIR / 'tasks.jsonl',
    snapshots_dir=DATA_DIR / 'snapshots',
    results_dir=WORKING_DIR / 'calibration',
    submission_dir=DATA_DIR / 'sample_submission',
    models=ModelRegistry(),
    sandbox='subprocess',
    graph_dir=str(DATA_DIR / 'graphs'),
    embeddings_dir=str(DATA_DIR / 'embeddings'),
    wheels_dir=DATA_DIR / 'wheels',
    verbose=False,
)
evaluator = Evaluator(config)


def run_sync(coro):
    """Run a coroutine to completion even though the notebook kernel already has an event loop."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()

tasks = load_tasks(config.tasks_path)

done = set()
if OUT.exists():
    done = {json.loads(l)['id'] for l in OUT.read_text().splitlines() if l.strip()}

for idx, task in enumerate(tasks, start=1):
    if task.instance_id in done:
        continue
    t0 = time.time()
    row = {'id': task.instance_id, 'repo': task.repo}
    try:
        snapshot_path, base_snapshot_path, patch_path = resolve_task_snapshot_paths(
            config.snapshots_dir, task.instance_id, task.repo)
        res = run_sync(verify_task(
            evaluator.docker, config, task, snapshot_path,
            base_snapshot_path=base_snapshot_path, patch_path=patch_path,
            agent_patch=task.patch, start_time=time.perf_counter()))
        row.update(gold_resolved=bool(res.resolved), test_exit_code=res.test_exit_code,
                   error=str(getattr(res, 'error', '') or '')[:300],
                   test_output_tail=(res.test_output or '')[-1500:])
    except Exception as exc:
        row.update(gold_resolved=False, error=f'{type(exc).__name__}: {exc}'[:300])
    row['seconds'] = round(time.time() - t0, 1)
    with OUT.open('a') as f:
        f.write(json.dumps(row) + '\n')
    print(f'[{idx}/{len(tasks)}] {task.instance_id}: gold_resolved={row["gold_resolved"]} '
          f'({row["seconds"]}s){" " + row["error"][:120] if row.get("error") else ""}', flush=True)'''

SUMMARY = r'''import pandas as pd
df = pd.read_json(OUT, lines=True)
print(f'gold resolves {df.gold_resolved.sum()}/{len(df)} tasks in this sandbox')
display(df.groupby('repo').gold_resolved.agg(['sum', 'count']))
display(df[~df.gold_resolved][['id', 'test_exit_code', 'error']])'''


def main() -> None:
    cells = [md(INTRO), md("## 1. Install the harness wheelhouse"), code(SETUP),
             md("## 2. Verify every gold patch"), code(RUN), md("## 3. Summary"), code(SUMMARY)]
    nb = {"cells": cells,
          "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                       "language_info": {"name": "python"}},
          "nbformat": 4, "nbformat_minor": 5}
    out_dir = ROOT / "notebook" / "calibration"
    out_dir.mkdir(exist_ok=True)
    (out_dir / f"{KERNEL_SLUG}.ipynb").write_text(json.dumps(nb, indent=1) + "\n")
    dev_meta = json.loads((ROOT / "notebook" / "kernel-metadata.json").read_text())
    meta = {**dev_meta, "id": f"{KAGGLE_USER}/{KERNEL_SLUG}", "title": KERNEL_SLUG,
            "code_file": f"{KERNEL_SLUG}.ipynb", "enable_gpu": False,
            "dataset_sources": ["metric/gemma-4-developer-agent-wheelhouse"], "model_sources": []}
    meta.pop("machine_shape", None)
    (out_dir / "kernel-metadata.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"wrote notebook/calibration/{KERNEL_SLUG}.ipynb and kernel-metadata.json")


if __name__ == "__main__":
    main()
