# Multi-Hunk Patch Decomposition & Syntax Pre-Flight — Plan

Numbered task groups. Each represents a discrete, reviewable step moving from prompt engineering to benchmark validation and merge readiness.

---

## 1. Update System Prompt with Multi-Hunk & Syntax Rules

- Edit [`submission/prompts/system.md`](file:///c:/Users/acquayefrank/Code/graft/submission/prompts/system.md):
  - In Section 4 ("FIX"):
    - Add multi-hunk planning rule: when modifying multiple locations or files, enumerate all target hunks in thoughts before modifying the first file.
    - Explicitly mandate deferring test runs until all planned hunks are placed.
  - In Section 5 ("VERIFY & STOP"):
    - Add mandatory syntax check: run `python -m py_compile <modified_file>` via `run_command` on each edited source file before running tests or calling `submit_patch()`.
    - If syntax or indentation error is reported, apply immediate fix via 1-strike Python one-liner.
- Inspect prompt diff and confirm alignment with existing Stop-and-Submit and Clean-Exit protocols.

## 2. Rebuild & Validate Submission Archive

- Run [`build_submission.py`](file:///c:/Users/acquayefrank/Code/graft/build_submission.py).
- Verify:
  - Archive contains exactly `agent.yaml`, `eval_config.yaml`, and updated `prompts/system.md`.
  - Size remains < 100 KB.
  - Pydantic schema validation passes with 0 errors.
  - Compute and log new SHA256 checksum.

## 3. Prepare Medium Benchmark & Dataset Synchronization

- Create `eval/medium5.json` targeting the 5 medium-complexity tasks from `dev30`:
  `rich_3052`, `rich_3675`, `rich_3938`, `rich_4006`, `fastapi_15588`.
- Push updated submission dataset to Kaggle via [`push_submission_dataset.sh`](file:///c:/Users/acquayefrank/Code/graft/push_submission_dataset.sh).
- Build and push `notebook/graft-dev-eval.ipynb` configured for `medium5`.

## 4. Remote GPU Execution & Empirical Measurement

- Trigger `graft-dev-eval` on Kaggle 4x NVIDIA L4 GPUs.
- Await completion and download execution results to `/tmp/medium5_results/`.
- Analyze traces:
  - Check resolution on target medium tasks.
  - Verify zero `py_compile` syntax rejections.
  - Check mean latency and tool count.

## 5. Validation Pass & Merge

- Run all verification checks defined in [`validation.md`](file:///c:/Users/acquayefrank/Code/graft/specs/2026-10-21-multi-hunk-decomposition/validation.md).
- Update roadmap Phase 7 with empirical results.
- Merge `multi-hunk-decomposition` into `main`.
