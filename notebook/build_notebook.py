"""Build the Kaggle dev-eval notebook (notebook/graft-dev-eval.ipynb) and its kernel metadata.

Run from the repo root:  python3 notebook/build_notebook.py
The task list is embedded from eval/dev30.json at build time.
Optional env vars: RUN_NAME (default "baseline"), MAX_TASKS (default: all).
"""

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KAGGLE_USER = "acquayefrank"
DATASET_SLUG = "graft-submission"
KERNEL_SLUG = "graft-dev-eval"


# Cell 1 is copied from the official starter notebook (ryanholbrook/getting-started-gemma-4-developer-agent).
SETUP = r'''import glob
import importlib
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path

os.environ['TRANSFORMERS_NO_TF'] = '1'
os.environ['TRANSFORMERS_NO_FLAX'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['VLLM_NO_USAGE_STATS'] = '1'
os.environ['VLLM_WORKER_MULTIPROC_METHOD'] = 'spawn'
os.environ['VLLM_ENGINE_READY_TIMEOUT_S'] = '1200'
os.environ['VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS'] = '1'
os.environ['NCCL_DEBUG'] = 'WARN'
os.environ['LITELLM_LOCAL_MODEL_COST_MAP'] = 'True'
os.environ['LITELLM_TELEMETRY'] = 'False'
os.environ['LITELLM_LOG'] = 'WARNING'
os.environ['OPENAI_API_KEY'] = os.environ.get('OPENAI_API_KEY', 'EMPTY')
os.environ['LOCAL_API_KEY'] = os.environ.get('LOCAL_API_KEY', 'EMPTY')
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'
os.environ['OTEL_SDK_DISABLED'] = 'true'
os.environ['OTEL_PYTHON_DISABLED'] = 'true'


def configure_logging() -> None:
    """Silence verbose third-party loggers."""
    for name in ('LiteLLM', 'LiteLLM Router', 'LiteLLM Proxy', 'litellm', 'httpx', 'httpcore',
                 'openai', 'urllib3', 'opentelemetry', 'opentelemetry.context'):
        lg = logging.getLogger(name)
        lg.setLevel(logging.WARNING)
        if 'litellm' in name.lower():
            lg.propagate = False
            lg.handlers.clear()


configure_logging()

WHEELHOUSE_DIR = Path('/kaggle/input/datasets/metric/gemma-4-developer-agent-wheelhouse')

# Remove broken cutlass .pth hooks if present
for pth_pattern in ('/usr/local/lib/python*/dist-packages/*cutlass*.pth',
                    '/usr/local/lib/python*/site-packages/*cutlass*.pth'):
    for pth in glob.glob(pth_pattern):
        try:
            os.unlink(pth)
        except OSError:
            pass

# Restore PEP 440 '+cu128' wheel filenames stripped by Kaggle dataset uploads
tmp_whl = Path('/tmp/wheelhouse')
tmp_whl.mkdir(parents=True, exist_ok=True)
for w in WHEELHOUSE_DIR.glob('*.whl'):
    if 'cutlass' in w.name.lower():
        continue
    target_name = w.name.replace('cu128', '+cu128') if ('cu128' in w.name and '+' not in w.name) else w.name
    target = tmp_whl / target_name
    if not target.exists():
        try:
            os.symlink(w, target)
        except OSError:
            shutil.copyfile(w, target)

wheels = sorted(str(w) for w in tmp_whl.glob('*.whl'))
print(f'Installing {len(wheels)} wheels from {WHEELHOUSE_DIR}...')
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', '--no-deps', '--force-reinstall', *wheels], check=True)
importlib.invalidate_caches()
configure_logging()
print('Wheelhouse installation complete.')'''

CONFIG = r'''import json
import re
import tarfile
import time
import zipfile
from swegemma.models import load_tasks

# ---- knobs ---------------------------------------------------------------
RUN_NAME = __RUN_NAME__          # results go to /kaggle/working/results/<RUN_NAME>
MODEL_OVERRIDE = None          # e.g. 'gemma-4-12b-it-qat-w4a16-ct' to try another size (drops adapters)
MAX_TASKS = __MAX_TASKS__               # e.g. 5 for a quick smoke test
# --------------------------------------------------------------------------

TASK_META = __TASK_META__
DEV_TASK_IDS = list(TASK_META)

DATA_DIR = Path('/kaggle/input/competitions/gemma-4-developer-agent')
WORKING_DIR = Path('/kaggle/working')
GRAPH_DIR = str(DATA_DIR / 'graphs')
EMBEDDINGS_DIR = str(DATA_DIR / 'embeddings')
TASKS_PATH = DATA_DIR / 'tasks.jsonl'

# Locate the uploaded submission dataset.
candidates = [Path('/kaggle/input/datasets/__USER__/__SLUG__'), Path('/kaggle/input/__SLUG__'),
              *Path('/kaggle/input/datasets').glob('*/__SLUG__')]
AGENT_SRC = next((p for p in candidates if p.is_dir()), None)
assert AGENT_SRC is not None, 'Attach the __USER__/__SLUG__ dataset to this notebook.'

# Copy to a writable dir and unpack any folders Kaggle stored as archives.
AGENT_DIR = WORKING_DIR / 'agent'
shutil.rmtree(AGENT_DIR, ignore_errors=True)
shutil.copytree(AGENT_SRC, AGENT_DIR)
for archive in list(AGENT_DIR.rglob('*')):
    if archive.suffix == '.zip' and zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(archive.parent / archive.stem)
        archive.unlink()
    elif archive.name.endswith(('.tar', '.tar.gz', '.tgz')) and tarfile.is_tarfile(archive):
        with tarfile.open(archive) as tf:
            tf.extractall(archive.parent, filter='data')
        archive.unlink()
(AGENT_DIR / 'dataset-metadata.json').unlink(missing_ok=True)
assert (AGENT_DIR / 'agent.yaml').is_file(), f'agent.yaml missing; found: {sorted(p.name for p in AGENT_DIR.iterdir())}'

if MODEL_OVERRIDE:
    for yaml_path in [AGENT_DIR / 'agent.yaml', *sorted((AGENT_DIR / 'sub_agents').glob('*.yaml'))]:
        if yaml_path.is_file():
            text = yaml_path.read_text(encoding='utf-8')
            text = re.sub(r'^(\s*model:\s*).*$', rf'\g<1>{MODEL_OVERRIDE}', text, flags=re.MULTILINE)
            text = re.sub(r'^\s*adapter:\s*.*\n?', '', text, flags=re.MULTILINE)
            yaml_path.write_text(text, encoding='utf-8')
    shutil.rmtree(AGENT_DIR / 'adapters', ignore_errors=True)

all_tasks = {t.instance_id: t for t in load_tasks(TASKS_PATH)}
tasks = [all_tasks[i] for i in DEV_TASK_IDS][:MAX_TASKS]
RESULTS_DIR = WORKING_DIR / 'results' / RUN_NAME
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

print(f'Submission: {AGENT_SRC} -> {AGENT_DIR}')
for p in sorted(AGENT_DIR.rglob('*')):
    if p.is_file():
        print(f'  {p.relative_to(AGENT_DIR)} ({p.stat().st_size} B)')
print(f'Tasks: {len(tasks)} of {len(DEV_TASK_IDS)} dev tasks; results -> {RESULTS_DIR}')
print((AGENT_DIR / 'agent.yaml').read_text())'''

# Cell 3 follows the starter's vLLM cell, which mirrors the scorer's server settings.
SERVER = r'''import litellm
import torch
from adk_submission import VllmConfig, VllmServer, discover_adapters
from adk_submission.discovery import discover_declared_models
from swegemma.config import ALLOWED_ADAPTER_EXTENSIONS

litellm.drop_params = True

ALLOWED_MODEL_NAMES = frozenset({'gemma-4-31b-it-qat-w4a16-ct', 'gemma-4-12b-it-qat-w4a16-ct',
                                 'gemma-4-e4b-it-qat-w4a16-ct', 'gemma-4-e2b-it-qat-w4a16-ct'})
MODEL_VLLM_EXTRA_ARGS = {
    'gemma-4-12b-it-qat-w4a16-ct': ('--hf-overrides', '{"architectures": ["Gemma4ForCausalLM"], "model_type": "gemma4"}'),
}
_SAFE_PATH_COMPONENT = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]*')
INFERENCE_API_KEY = os.environ.get('LOCAL_API_KEY', 'EMPTY')

declared_models = discover_declared_models(AGENT_DIR)
assert len(declared_models) == 1, f'Expected exactly 1 declared model, got: {sorted(declared_models)}'
declared_model = next(iter(declared_models))
assert declared_model in ALLOWED_MODEL_NAMES, f'Unsupported model {declared_model!r}'

MODEL_PATH = Path(f'/kaggle/input/models/google/gemma-4/other/{declared_model}/2')
assert MODEL_PATH.exists(), f'Model weights not found at {MODEL_PATH}. Attach the model input.'

adapters = discover_adapters(str(AGENT_DIR), adapter_extensions=ALLOWED_ADAPTER_EXTENSIONS)
adapter_map = getattr(adapters, 'adapters', None) or {}
for adapter_name in adapter_map:
    assert _SAFE_PATH_COMPONENT.fullmatch(adapter_name), f'Unsafe adapter name {adapter_name!r}'
detected_ranks = [r for info in adapter_map.values() if (r := getattr(info, 'rank', None)) is not None and r > 0]

gpu_count = torch.cuda.device_count() if torch.cuda.is_available() else 1
tp_size = 4 if gpu_count >= 4 else (2 if gpu_count >= 2 else 1)

if 'server_instance' in globals() and server_instance is not None:
    server_instance.stop()

vllm_cfg = VllmConfig(
    model=str(MODEL_PATH),
    port=8000,
    host='127.0.0.1',
    tool_call_parser='gemma4',
    reasoning_parser='gemma4',
    max_model_len=32768,
    dtype='bfloat16' if (torch.cuda.is_available() and torch.cuda.is_bf16_supported()) else 'auto',
    gpu_memory_utilization=0.90,
    enable_auto_tool_choice=True,
    enable_lora=bool(adapter_map),
    max_loras=max(1, len(adapter_map)),
    max_lora_rank=max(detected_ranks) if detected_ranks else 128,
    scheduler_reserve_full_isl=False,
    tensor_parallel_size=tp_size,
    startup_timeout=60 * 20,
    extra_args=MODEL_VLLM_EXTRA_ARGS.get(declared_model, ()),
)
t0 = time.time()
server_instance = VllmServer(vllm_cfg, adapter_manifest=adapters)
server_instance.start()
print(f'vLLM server started on {server_instance.base_url} (tp={tp_size}, model={declared_model}) in {time.time() - t0:.0f}s')

models = server_instance.create_model_registry(aliases=[declared_model], model_prefix='openai/', api_key=INFERENCE_API_KEY)'''

EVAL = r'''import asyncio
import concurrent.futures
import pandas as pd
import yaml
from google.adk.agents.context_cache_config import ContextCacheConfig
from google.adk.apps._configs import EventsCompactionConfig
from swegemma.config import EvalConfig, build_submission_limits
from swegemma.evaluate import Evaluator


def run_sync(coro_or_fn, *args, **kwargs):
    """Run an async coroutine synchronously inside a notebook event loop."""
    if callable(coro_or_fn) and not asyncio.iscoroutine(coro_or_fn):
        fn = lambda: coro_or_fn(*args, **kwargs)
    else:
        fn = lambda: coro_or_fn
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop is not None and loop.is_running():
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(lambda: asyncio.run(fn())).result()
    return asyncio.run(fn())


eval_config_file = next((c for n in ('eval_config.yaml', 'eval_config.yml') if (c := AGENT_DIR / n).is_file()), None)
raw_eval_cfg = (yaml.safe_load(eval_config_file.read_text(encoding='utf-8')) or {}) if eval_config_file else {}
eval_section = raw_eval_cfg.get('evaluation', raw_eval_cfg)
timeout_seconds = int(eval_section.get('timeout_seconds', 300))
verification_timeout_seconds = int(eval_section.get('verification_timeout_seconds', 300))
max_tool_calls = int(eval_section.get('max_tool_calls', 100))
max_time_minutes = float(eval_section.get('max_time_minutes', 60.0))
turns_raw = eval_section.get('max_turns', eval_section.get('max_llm_calls'))
max_turns = int(turns_raw) if turns_raw is not None else None
print(f'Budget per task: {max_time_minutes} min, {max_tool_calls} tool calls, {max_turns} turns, {timeout_seconds}s/command')

limits, gen_constraints = build_submission_limits()
eval_config = EvalConfig(
    tasks_path=TASKS_PATH,
    snapshots_dir=DATA_DIR / 'snapshots',
    results_dir=RESULTS_DIR,
    submission_dir=AGENT_DIR,
    models=models,
    sandbox='subprocess',
    timeout_seconds=timeout_seconds,
    verification_timeout_seconds=verification_timeout_seconds,
    max_time_minutes=max_time_minutes,
    max_tool_calls=max_tool_calls,
    max_turns=max_turns,
    limits=limits,
    generation_constraints=gen_constraints,
    adapter_manifest=adapters,
    context_cache_config=ContextCacheConfig(min_tokens=2048, ttl_seconds=1800, cache_intervals=10),
    events_compaction_config=EventsCompactionConfig(compaction_interval=15, overlap_size=2,
                                                    token_threshold=14336, event_retention_size=5),
    graph_dir=GRAPH_DIR,
    embeddings_dir=EMBEDDINGS_DIR,
    wheels_dir=DATA_DIR / 'wheels',
    verbose=False,
)
evaluator = Evaluator(eval_config)

rows_path = RESULTS_DIR / 'dev_rows.jsonl'
rows_path.unlink(missing_ok=True)
rows = []
run_start = time.time()
for idx, task in enumerate(tasks, start=1):
    meta = TASK_META[task.instance_id]
    print(f'[{idx}/{len(tasks)}] {task.instance_id} ({meta["bucket"]}, {meta["lines"]} lines)...', flush=True)
    t0 = time.time()
    row = {'id': task.instance_id, **meta}
    try:
        result = run_sync(evaluator.evaluate_task, task=task, task_index=idx, total_tasks=len(tasks))
        patch = (result.agent_patch or '').strip()
        row.update(
            resolved=bool(result.resolved),
            test_exit_code=result.test_exit_code,
            patch_chars=len(patch),
            tool_calls=result.tool_calls,
            agent_seconds=round(result.duration_seconds or 0, 1),
            error=str(getattr(result, 'error', '') or '')[:300],
            test_output_tail=(result.test_output or '')[-1500:],
        )
    except Exception as exc:  # keep going; one broken task must not kill the run
        row.update(resolved=False, patch_chars=0, error=f'{type(exc).__name__}: {exc}'[:300])
    row['wall_seconds'] = round(time.time() - t0, 1)
    rows.append(row)
    with rows_path.open('a') as f:
        f.write(json.dumps(row) + '\n')
    solved = sum(r['resolved'] for r in rows)
    print(f'    resolved={row["resolved"]} patch_chars={row["patch_chars"]} tool_calls={row.get("tool_calls")} '
          f'wall={row["wall_seconds"]}s | running {solved}/{len(rows)}' + (f' | error={row["error"]}' if row.get('error') else ''),
          flush=True)
print(f'Done in {(time.time() - run_start) / 60:.1f} min')'''

SUMMARY = r'''df = pd.DataFrame(rows)
df['no_patch'] = df['patch_chars'] == 0
n = len(df)
summary = {
    'run': RUN_NAME,
    'model': declared_model,
    'tasks': n,
    'resolved': int(df['resolved'].sum()),
    'resolution_rate': round(df['resolved'].mean(), 3),
    'no_patch': int(df['no_patch'].sum()),
    'errors': int((df['error'].fillna('') != '').sum()) if 'error' in df else 0,
    'mean_agent_seconds': round(df.get('agent_seconds', pd.Series(dtype=float)).mean(), 1),
    'mean_wall_seconds': round(df['wall_seconds'].mean(), 1),
    'mean_tool_calls': round(df.get('tool_calls', pd.Series(dtype=float)).mean(), 1),
}
# Wall time here includes Phase 2 verification, which the scorer's 12h limit excludes,
# so this projection is pessimistic if the scorer runs tasks one at a time.
summary['projected_hours_for_120_tasks'] = round(summary['mean_wall_seconds'] * 120 / 3600, 2)
print(json.dumps(summary, indent=1))
(RESULTS_DIR / 'dev_summary.json').write_text(json.dumps(summary, indent=1))

order = ['tiny', 'small', 'medium', 'large', 'huge']
by_bucket = df.groupby('bucket')['resolved'].agg(['sum', 'count']).reindex(order).dropna()
by_repo = df.groupby('repo')['resolved'].agg(['sum', 'count'])
display(by_bucket)
display(by_repo)
display(df.sort_values(['resolved', 'bucket']))'''

PACKAGE = r'''archive = shutil.make_archive(str(WORKING_DIR / f'{RUN_NAME}_results'), 'zip', root_dir=RESULTS_DIR)
print(f'Results archive: {archive} ({Path(archive).stat().st_size / 1e6:.1f} MB)')
server_instance.stop()'''


def code(src: str) -> dict:
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": src.splitlines(keepends=True)}


def md(src: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": src.splitlines(keepends=True)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Kaggle dev-eval notebook.")
    parser.add_argument("--benchmark", choices=["dev10", "dev30", "medium5"], default=os.environ.get("BENCHMARK", "dev10"),
                        help="Benchmark split to evaluate: dev10 (screening), dev30 (full validation), or medium5 (Phase 7 medium bugs)")
    parser.add_argument("--run-name", default=os.environ.get("RUN_NAME", None),
                        help="Run name for results folder and metrics summary")
    parser.add_argument("--max-tasks", default=os.environ.get("MAX_TASKS", "None"),
                        help="Max number of tasks to run (default: all tasks in benchmark)")
    args = parser.parse_args()

    benchmark_name = args.benchmark
    benchmark_file = ROOT / "eval" / f"{benchmark_name}.json"
    if not benchmark_file.is_file():
        sys.exit(f"Benchmark file not found: {benchmark_file}")

    dev_tasks = json.loads(benchmark_file.read_text(encoding="utf-8"))
    task_meta = {t["instance_id"]: {"repo": t["repo"], "bucket": t["bucket"], "lines": t["lines"]} for t in dev_tasks}

    run_name = args.run_name or (f"phase7_{benchmark_name}" if benchmark_name == "medium5" else ("subagent_v1_dev10" if benchmark_name == "dev10" else "subagent_v1_dev30"))
    max_tasks_val = args.max_tasks

    intro = f"""# graft: dev evaluation ({benchmark_name})

Runs the submission from the `{KAGGLE_USER}/{DATASET_SLUG}` dataset against a fixed {len(dev_tasks)}-task dev set (`eval/{benchmark_name}.json`)
from the public training tasks, then summarises resolution rate, timing and failures.

**Settings:** Accelerator = GPU L4 x4, Internet = off. Inputs: the competition data,
`metric/gemma-4-developer-agent-wheelhouse`, the Gemma 4 model(s) you use, and `{KAGGLE_USER}/{DATASET_SLUG}`.

Edit the `RUN_NAME` / `MODEL_OVERRIDE` / `MAX_TASKS` knobs in the config cell, then Run All.
Download `/kaggle/working/<RUN_NAME>_results.zip` afterwards (traces, logs, patches, summary)."""

    config = (CONFIG.replace("__TASK_META__", json.dumps(task_meta, indent=1))
              .replace("__RUN_NAME__", repr(run_name))
              .replace("__MAX_TASKS__", max_tasks_val)
              .replace("__USER__", KAGGLE_USER).replace("__SLUG__", DATASET_SLUG))
    cells = [
        md(intro),
        md("## 1. Install the harness wheelhouse"), code(SETUP),
        md("## 2. Config: submission, model, dev tasks"), code(config),
        md("## 3. Start vLLM (same settings as the scorer)"), code(SERVER),
        md("## 4. Run the dev set (Phase 1 agent + Phase 2 verification)"), code(EVAL),
        md("## 5. Summary"), code(SUMMARY),
        md("## 6. Package results for download"), code(PACKAGE),
    ]
    nb = {
        "cells": cells,
        "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                     "language_info": {"name": "python"}},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    out_dir = ROOT / "notebook"
    (out_dir / f"{KERNEL_SLUG}.ipynb").write_text(json.dumps(nb, indent=1) + "\n")

    kernel_meta = {
        "id": f"{KAGGLE_USER}/{KERNEL_SLUG}",
        "title": KERNEL_SLUG,
        "code_file": f"{KERNEL_SLUG}.ipynb",
        "language": "python",
        "kernel_type": "notebook",
        "is_private": True,
        "enable_gpu": True,
        "enable_tpu": False,
        "enable_internet": False,
        "machine_shape": "NvidiaL4",
        # Pinned Python 3.12 image from the starter notebook; the wheelhouse only has cp312 wheels.
        "docker_image": "gcr.io/kaggle-private-byod/python@sha256:37c64f7dd9c54116ecd1bcc88817c5469b88387388fade02bfa8bf3fc647d461",
        "competition_sources": ["gemma-4-developer-agent"],
        "dataset_sources": ["metric/gemma-4-developer-agent-wheelhouse", f"{KAGGLE_USER}/{DATASET_SLUG}"],
        "model_sources": [
            "google/gemma-4/Other/gemma-4-31b-it-qat-w4a16-ct/2",
            "google/gemma-4/Other/gemma-4-12b-it-qat-w4a16-ct/2",
        ],
        "kernel_sources": [],
    }
    (out_dir / "kernel-metadata.json").write_text(json.dumps(kernel_meta, indent=2) + "\n")
    print(f"wrote notebook/{KERNEL_SLUG}.ipynb ({len(cells)} cells) and notebook/kernel-metadata.json")


if __name__ == "__main__":
    main()
