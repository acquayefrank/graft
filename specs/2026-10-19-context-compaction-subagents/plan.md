# Context Compaction & Architecture Exploration — Plan

Numbered task groups. Each task group is small enough to be reviewable and independently committed.

---

## 1. Curate the Fast Screening Benchmark (`eval/dev10.json`)

- Extract 10 balanced tasks from `eval/dev30.json` spanning both repositories and difficulty tiers:
  - 5 tasks from `Textualize/rich` (2 tiny, 2 small, 1 medium).
  - 5 tasks from `fastapi/fastapi` (2 tiny, 2 small, 1 medium).
- Include known diagnostic tasks: `rich_3470` (post-fix verification benchmark) and `fastapi_14301` (dependency schema complexity).
- Commit as: `feat(eval): add 10-task screening benchmark dev10.json`.

---

## 2. Declarative Read-Only Sub-Agent (`code_analyzer.yaml`)

- Create directory `submission/sub_agents/`.
- Author `submission/sub_agents/code_analyzer.yaml`:
  - `name: code_analyzer`
  - `model: gemma-4-31b-it-qat-w4a16-ct`
  - `description: "Read-only code intelligence agent that navigates the repository, locates responsible files, and analyzes call graphs."`
  - `instruction: !include ../prompts/analyzer.md`
  - `tools: [search_similar_code, get_code_neighbors, get_code_subgraph, read_file, run_command]`
  - `generate_content_config`: `temperature: 0.1`, `thinking_budget: 1024`, `max_output_tokens: 4096`.
- Author `submission/prompts/analyzer.md`:
  - Enforce read-only constraint (no edits, no file creation).
  - Enforce concise output reporting: return exact filepaths, symbol definitions, caller-callee chains, and line spans.
- Commit as: `feat(agent): create declarative read-only code_analyzer sub-agent`.

---

## 3. Root Agent Integration & Hybrid Prompt Tuning

- Update `submission/agent.yaml`:
  - Declare `code_analyzer` as an `AgentTool` with `skip_summarization: true`.
  - Retain local tools: `[run_command, read_file, edit_file, write_file, get_status, submit_patch, code_analyzer]`.
- Update `submission/prompts/system.md`:
  - Instruct root `coder` to invoke `code_analyzer` for repository exploration, symbol mapping, and caller searches.
  - Instruct root `coder` to use direct `read_file` for local verification before applying `edit_file`.
  - Maintain the strict Stop-and-Submit rule and Minute 3.5 hard ceiling.
- Commit as: `feat(agent): integrate code_analyzer into root coder agent with hybrid prompt`.

---

## 4. Submission Packaging & Schema Verification

- Update `build_submission.sh` to ensure `sub_agents/` and all prompt references are bundled cleanly into `submission.zip`.
- Verify that `unzip -l submission.zip` includes:
  - `agent.yaml`
  - `eval_config.yaml`
  - `prompts/system.md`
  - `prompts/analyzer.md`
  - `sub_agents/code_analyzer.yaml`
- Confirm total package size < 100 KB (well within 3 GiB limit).
- Commit as: `feat(build): update packaging script for sub-agent submission`.

---

## 5. Remote Evaluation & Paper Ablation Harness

- Update `notebook/build_notebook.py` to support running either `dev10` (for screening) or `dev30` (for full validation).
- Add `paper/tables/architecture_ablation.md` template capturing:
  - Baseline (single-agent, unconstrained)
  - Iteration 1 (`recovered_v1`: pacing & 1024 thinking)
  - Iteration 2 (`recovered_v2`: 80 tools, 30s timeout, build/ scratchpad)
  - Iteration 3 (`subagent_v1`: hybrid code_analyzer architecture)
- Commit as: `feat(paper): add architecture ablation table and evaluation dispatch scripts`.

---

## 6. Validation Pass

- Run the validation checks in `validation.md`:
  - Local schema and YAML parse tests.
  - Zip structure inspection.
  - Test run on `dev10` via Kaggle dev-eval notebook.
  - Apply the strict resolution gate ($\ge 56.7\%$ on dev30 to promote to leaderboard entry; otherwise keep `recovered_v2` for leaderboard and record sub-agent in paper ablation).

---

## 7. PR

- Open a PR from `context-compaction-subagents` into `main` once `validation.md` passes in full.
- PR description details Phase 3 deliverables, the hybrid sub-agent architecture, the dev10 screening metrics, and the ablation results for `paper/tables/architecture_ablation.md`.
