# Context Compaction & Architecture Exploration — Validation

How to verify that Phase 3 is complete and branch `context-compaction-subagents` is ready to merge into `main`.

---

## 1. Declarative YAML Schema & Packaging Integrity

- [ ] `submission/agent.yaml` parses without YAML errors (`python -c "import yaml; yaml.safe_load(open('submission/agent.yaml'))"`).
- [ ] `submission/sub_agents/code_analyzer.yaml` parses without YAML errors.
- [ ] All `!include` directives resolve valid relative files without path traversal outside `submission/`.
- [ ] Running `./build_submission.sh` produces `submission.zip` containing:
  - `agent.yaml` at root
  - `eval_config.yaml` at root
  - `prompts/system.md`
  - `prompts/analyzer.md`
  - `sub_agents/code_analyzer.yaml`
- [ ] `submission.zip` total archive size is < 1 MB (well below the 3 GiB competition threshold).

---

## 2. Benchmark Dataset Integrity

- [ ] `eval/dev10.json` exists and contains exactly 10 tasks:
  - 5 tasks from `Textualize/rich`
  - 5 tasks from `fastapi/fastapi`
  - Stratified across `tiny`, `small`, and `medium` patch complexity buckets.
- [ ] All task IDs in `eval/dev10.json` are strict subsets of `eval/dev30.json`.
- [ ] `eval/dev30.json` remains intact and unmodified.

---

## 3. Remote Execution & Paper Ablation Artifacts

- [ ] Evaluation notebook can run against `dev10` without timeout hangs or container initialization failures.
- [ ] ATIF v1.7 traces from the sub-agent run are downloaded into `results/subagent_dev10/`.
- [ ] Root context token usage is extracted from traces: verify that exploratory grep/read outputs are housed inside `code_analyzer` traces.
- [ ] `paper/tables/architecture_ablation.md` is populated with empirical metrics comparing:
  - Single-agent baseline (`smoke5` / `recovered_v1`)
  - Paced single-agent (`recovered_v2`, 53.3% resolution)
  - Sub-agent architecture (`subagent_v1`)

---

## 4. Production Promotion & Fallback Decision Gate

- [ ] **Promotion Condition**: If the sub-agent architecture achieves $\ge 56.7\%$ resolution (17+ of 30 tasks) on `dev30` with mean agent latency $\le 260\text{s}$, update `submission.zip` to package the sub-agent architecture for Kaggle leaderboard submission.
- [ ] **Fallback Condition**: If the sub-agent architecture achieves $< 56.7\%$ resolution or exceeds $260\text{s}$ mean latency, retain the single-agent `recovered_v2` configuration (53.3% resolution, 229.1s latency) as `submission.zip` for today's leaderboard submission, and publish the sub-agent results in the Paper Track manuscript.

---

## 5. Scope & Git Discipline

- [ ] No untracked files or scratch files in working tree outside `specs/` and `submission/`.
- [ ] All changes committed in atomic, well-described commits.

---

## Merge Criteria

All five verification groups above pass. The promotion decision is documented, the paper ablation table is updated, and the official Kaggle submission for today is submitted and logged. Once merged, re-open `specs/roadmap.md` to proceed to Phase 4 (Dev30 Benchmark Scaling & Competition Submission).
