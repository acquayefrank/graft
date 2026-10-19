# Dev30 Benchmark Scaling & Competition Submission — Validation

How to verify that Phase 4 is complete and branch `dev30-scaling-submission` is ready to merge into `main`.

---

## 1. Production Submission Packaging & Schema Integrity

- [ ] `submission/agent.yaml` parses without error and contains the 9 production local tools (`run_command`, `read_file`, `edit_file`, `write_file`, `search_similar_code`, `get_code_neighbors`, `get_code_subgraph`, `get_status`, `submit_patch`).
- [ ] No `agent_tool` block exists in production `submission/agent.yaml`.
- [ ] Running `python build_submission.py` outputs `[OK]` and produces `submission.zip`:
  - Contains `agent.yaml`, `eval_config.yaml`, and `prompts/system.md`.
  - Excludes `sub_agents/` and `prompts/analyzer.md` from the production archive.
  - Archive size is < 100 KB (< 3 GiB limit).
- [ ] Direct Pydantic validation of `submission/agent.yaml` against `SandboxedAgentConfig` succeeds with 0 validation errors.

---

## 2. Official Kaggle Leaderboard Submission Logging

- [ ] Official submission command executed successfully via Kaggle CLI:
  ```bash
  kaggle competitions submit -c gemma-4-developer-agent -f submission.zip -m "Project Graft: Paced Single-Agent (recovered_v2, 53.3% dev30 baseline)"
  ```
- [ ] Submission ID is verified via `kaggle competitions submissions -c gemma-4-developer-agent` and confirmed in `KernelWorkerStatus.QUEUED` or `RUNNING`/`COMPLETE`.
- [ ] `results/leaderboard_submissions.md` exists and contains:
  - Submission ID.
  - UTC Timestamp.
  - SHA256 checksum of `submission.zip`.
  - Baseline metrics reference (53.3% resolution on Dev30, 229.1s latency).

---

## 3. Failure Taxonomy & Empirical Evidence Integrity

- [ ] `paper/tables/failure_taxonomy.md` exists and categorizes failure modes across benchmark evaluations.
- [ ] Every categorized failure mode cites concrete task IDs from the benchmark dataset.
- [ ] `paper/tables/architecture_ablation.md` contains the completed empirical ablation metrics from Phase 3 (`dev10` screening results for `subagent_v1`).

---

## 4. Research Paper Manuscript Compliance

- [ ] `paper/draft.md` is populated with all five core sections:
  - Introduction & SWE-bench Problem Setting
  - System Architecture & Pacing Guardrails
  - Empirical Evaluation & Architecture Ablation
  - Failure Analysis & Taxonomy
  - Discussion & Open Research Challenges
- [ ] All table links and figure references in `paper/draft.md` resolve to valid files.
- [ ] Total word count of `paper/draft.md` is verified to be $\le 3,000$ words (competition paper track limit):
  ```bash
  python -c "text = open('paper/draft.md', encoding='utf-8').read(); words = len(text.split()); print(f'Word count: {words}'); assert words <= 3000"
  ```
- [ ] Zero placeholder tokens (`TODO`, `TBD`, `__FILL__`) remain in `paper/draft.md`.

---

## 5. Scope & Git Discipline

- [ ] No untracked files or scratch files in working tree outside `specs/`, `results/`, and `scratch/`.
- [ ] All changes committed in atomic, well-described commits.

---

## Merge Criteria

All five verification groups above pass. The production submission archive is verified and submitted to the competition leaderboard with its submission ID logged, the failure taxonomy is synthesized, and the research paper manuscript is finalized within the 3,000-word limit. Once merged into `main`, Project Graft reaches full competition submission and research publication completion.
