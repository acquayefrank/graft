# Project Graft: Master Strategy for Top 3 / Top 5 & Paper Track

This document details the critical competitive strategy for **Project Graft** to reach the **Top 3 / Top 5** in the [Gemma 4 Developer Agent Competition](https://www.kaggle.com/competitions/gemma-4-developer-agent) and win in the [Gemma 4 Developer Agent Paper Track](https://www.kaggle.com/competitions/gemma-4-developer-agent-paper) ($35,000 prize pool).

---

## 1. The Competitive Reality & The "1 Submission / Day" Constraint

### The Leaderboard Dynamics
- **120 hidden test tasks** run sequentially in a **12-hour global window** on 4x NVIDIA L4 GPUs.
- Each task gets an average of **~4.5 to 5.0 minutes** in the agent loop (after sandbox setup and wheel installation).
- **Hard Truth**: Most participants fail not because their model cannot code, but because:
  1. Their agent enters exploratory rabbit holes and **times out** without submitting (scoring 0.0).
  2. Their agent writes scratch test scripts into `/workspace`, which pollute `git diff HEAD` and fail verification.
  3. Their agent exceeds the per-task timeout or starves later tasks toward the end of the 12-hour window.
- **The 1 Submission/Day Protocol**: You cannot brute-force submissions. Every leaderboard submission must be pre-vetted against our internal benchmark (`smoke5` and `dev30`) before uploading.

### The Paper Track Dynamics ($35,000 Prize Pool)
- Evaluated on **novel empirical methodology, clarity of findings, and reproducibility** (<= 3,000 words writeup).
- The strongest papers do not just present high numbers; they show **why baseline agents fail**, provide **granularity through ablation studies**, and propose **reproducible systems principles** (such as time-aware pacing and AST graph grounding).
- Every experiment run on Kaggle directly feeds our manuscript tables and figures in [`paper/draft.md`](file:///c:/Users/acquayefrank/Code/graft/paper/draft.md).

---

## 2. The 4 Pillars to Win

```
+---------------------------------------------------------------------------------------------------+
|                                 THE 4 PILLARS OF PROJECT GRAFT                                    |
+---------------------------------------------------------------------------------------------------+
| 1. ZERO-TIMEOUT PACING & STOP-AND-SUBMIT RULE                                                     |
|    - Eliminate post-fix over-verification (the exact bug that killed `rich_3470`).               |
|    - If repro passes, SUBMIT IMMEDIATELY. Continued testing risks hitting the 5-min ceiling.     |
|    - At Minute 3.5 (or Turn 20), freeze exploration and submit the best candidate patch.         |
+---------------------------------------------------------------------------------------------------+
| 2. PRISTINE SCRATCHPAD & TOOL HYGIENE                                                             |
|    - `write_file` strictly restricted to `build/repro.py` (excluded from git by baseline commit).  |
|    - Zero `Path traversal` errors on `/tmp`.                                                      |
|    - `git status` check before `submit_patch` ensures zero scratch files leak into unified diff.   |
+---------------------------------------------------------------------------------------------------+
| 3. GRAPH-GROUNDED ACCELERATED LOCALIZATION                                                        |
|    - Use `search_similar_code` & `get_code_neighbors` for 1-turn symbol localization.             |
|    - Replaces 8-10 linear grep turns with 1 targeted graph query, saving 60-90s per task.        |
+---------------------------------------------------------------------------------------------------+
| 4. RIGOROUS DUAL-TRACK RESEARCH PIPELINE                                                          |
|    - Standardized ATIF session traces log every thought, tool call, error, and token.             |
|    - Automated side-by-side comparison (`eval/compare_runs.py`).                                  |
|    - High-impact paper draft already structured and updated in `paper/draft.md`.                 |
+---------------------------------------------------------------------------------------------------+
```

---

## 3. What Was Implemented Tonight While You Slept

1. **Hardened System Prompt ([`submission/prompts/system.md`](file:///c:/Users/acquayefrank/Code/graft/submission/prompts/system.md))**:
   - **Stop-and-Submit Rule**: Mandates immediate patch submission as soon as a fix is verified.
   - **Minute 3.5 Hard Ceiling**: Enforces submitting candidate fixes before the 5.0-minute timeout.
   - **Scratchpad Standard**: Explicitly teaches the model to use `build/repro.py`, eliminating `Path traversal detected` errors on `/tmp`.
   - **Precision Editing**: Enforces uniquely anchored 3–8 line replacements with `edit_file`.

2. **Kaggle Dataset Sync**:
   - Pushed the new submission package to the private Kaggle dataset [`acquayefrank/graft-submission`](https://www.kaggle.com/datasets/acquayefrank/graft-submission) via [`push_submission_dataset.sh`](file:///c:/Users/acquayefrank/Code/graft/push_submission_dataset.sh).
   - Verified that the new dataset version is processed and **`ready`**.

3. **Production Archive Compiled ([`submission.zip`](file:///c:/Users/acquayefrank/Code/graft/submission.zip))**:
   - Built cleanly with [`build_submission.sh`](file:///c:/Users/acquayefrank/Code/graft/build_submission.sh).
   - Contains `agent.yaml`, `eval_config.yaml`, and `prompts/system.md` at root (< 5 KB, well within 3 GiB limit).

4. **Remote Dev-Eval Automation**:
   - [`push_notebook.sh`](file:///c:/Users/acquayefrank/Code/graft/push_notebook.sh): Compiles and pushes `graft-dev-eval.ipynb` to Kaggle with one command.
   - [`pull_results.sh`](file:///c:/Users/acquayefrank/Code/graft/pull_results.sh): Downloads and unpacks remote run artifacts into `results/<run_name>/`.
   - [`eval/compare_runs.py`](file:///c:/Users/acquayefrank/Code/graft/eval/compare_runs.py): Compares any two evaluation runs side-by-side with resolution delta and timing analysis.

5. **Paper Track Manuscript ([`paper/draft.md`](file:///c:/Users/acquayefrank/Code/graft/paper/draft.md))**:
   - Fully expanded into a structured research paper draft with empirical baseline figures from `smoke5`, system architecture diagrams, and mathematical formulation.

---

## 4. Morning Action Plan (Your Step-by-Step Guide)

When you wake up, follow this exact 4-step sequence:

### Step 1: Trigger the Dev-Eval Run on Kaggle (5 Tasks)
Open your terminal (or WSL) and run:
```bash
wsl -d Ubuntu-24.04 bash -l -c "cd /mnt/c/Users/acquayefrank/Code/graft && ./push_notebook.sh"
```
*Alternatively, open [graft-dev-eval on Kaggle](https://www.kaggle.com/code/acquayefrank/graft-dev-eval), click "Edit", verify Accelerator is **GPU L4 x4**, and click **Run All**.*

The notebook will run the 5 smoke tasks with our new hardened agent. Execution takes ~15–20 minutes.

### Step 2: Download the Results
Once the notebook finishes on Kaggle:
```bash
wsl -d Ubuntu-24.04 bash -l -c "cd /mnt/c/Users/acquayefrank/Code/graft && ./pull_results.sh smoke5_v2"
```

### Step 3: Compare Results Side-by-Side
Run the comparison tool to see the delta against baseline:
```bash
python eval/compare_runs.py results/smoke5/results/smoke5 results/smoke5_v2/results/smoke5_v2
```
*Expected Outcome*:
- `rich_3470` now resolves (submits at ~288s instead of timing out at 305s).
- `rich_3278` no longer hits `/tmp` path traversal errors.
- Resolution rate jumps from **40% (2/5)** to **60%–80% (3/5 or 4/5)**.

### Step 4: Submit Today's Official Entry to Kaggle!
Once verified by the comparison tool, use your **1 daily submission** on Kaggle:
1. Go to the [Gemma 4 Developer Agent Competition Submissions page](https://www.kaggle.com/competitions/gemma-4-developer-agent/submissions).
2. Upload [`submission.zip`](file:///c:/Users/acquayefrank/Code/graft/submission.zip) from this repo.
3. Add a description: *"Graft v1: Time-aware pacing, stop-and-submit protocol, and build/ scratchpad isolation"*.
4. Track your score on the leaderboard!
