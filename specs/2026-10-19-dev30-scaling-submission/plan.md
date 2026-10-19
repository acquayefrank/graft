# Dev30 Benchmark Scaling & Competition Submission — Plan

Numbered task groups. Each task group is small enough to be reviewable and independently committed.

---

## 1. Restore Production Single-Agent Configuration (`recovered_v2`)

- Update [`submission/agent.yaml`](file:///c:/Users/acquayefrank/Code/graft/submission/agent.yaml):
  - Remove `agent_tool` block.
  - Declare the full 9 local tools: `[run_command, read_file, edit_file, write_file, search_similar_code, get_code_neighbors, get_code_subgraph, get_status, submit_patch]`.
  - Maintain `temperature: 0.1`, `top_p: 0.95`, `max_output_tokens: 8192`, `thinking_budget: 1024`.
- Update [`submission/prompts/system.md`](file:///c:/Users/acquayefrank/Code/graft/submission/prompts/system.md):
  - Remove references to `code_analyzer`.
  - Re-establish single-agent LOCATE instructions utilizing `search_similar_code`, `get_code_neighbors`, and targeted `read_file`.
  - Maintain the strict 3.5-minute hard ceiling and Stop-and-Submit rule.
- Commit as: `feat(agent): restore production recovered_v2 single-agent configuration`.

---

## 2. Production Packaging & Sandboxed Compiler Verification

- Update [`build_submission.py`](file:///c:/Users/acquayefrank/Code/graft/build_submission.py):
  - Define required entries for production single-agent: `agent.yaml`, `eval_config.yaml`, `prompts/system.md`.
  - Validate that `sub_agents/` is excluded from production `submission.zip` to maintain minimal attack surface and package size.
  - Run Pydantic schema validation using `SandboxedAgentConfig` from `build/wheels/adk_submission-0.2.13-py3-none-any.whl`.
  - Confirm `submission.zip` is < 100 KB and contains zero path traversal artifacts.
- Commit as: `feat(build): verify production submission.zip packaging and schema`.

---

## 3. Official Competition Leaderboard Submission

- Dispatch `submission.zip` to the official competition:
  - Command: `kaggle competitions submit -c gemma-4-developer-agent -f submission.zip -m "Project Graft: Paced Single-Agent (recovered_v2, 53.3% dev30 baseline)"`
- Verify submission acceptance and retrieve submission ID:
  - Command: `kaggle competitions submissions -c gemma-4-developer-agent`
- Create `results/leaderboard_submissions.md` logging:
  - Submission ID, submission date/time (UTC).
  - Model name (`gemma-4-31b-it-qat-w4a16-ct`).
  - SHA256 checksum of `submission.zip`.
  - Benchmark performance context (53.3% Dev30 baseline, 229.1s latency).
- Commit as: `feat(eval): dispatch official competition leaderboard submission`.

---

## 4. Trace Post-Mortem & Failure Taxonomy

- Run post-mortem analysis across evaluation traces (`results/smoke5_v2/` and calibration runs) using [`eval/summarize_trace.py`](file:///c:/Users/acquayefrank/Code/graft/eval/summarize_trace.py).
- Synthesize failure taxonomy across remaining failure modes:
  - Incomplete Edits / Scope Overreach.
  - Regex / Indentation Mismatch in `edit_file`.
  - Test Suite / Helper Import Failures.
  - Hard Timeouts / Turn Limit Ceilings.
- Author `paper/tables/failure_taxonomy.md` with:
  - Error category, frequency, exemplar task IDs, root causes, and mitigation impact.
- Commit as: `feat(paper): add dev30 failure taxonomy and error distribution table`.

---

## 5. Research Paper Manuscript Finalization

- Update [`paper/draft.md`](file:///c:/Users/acquayefrank/Code/graft/paper/draft.md):
  - Section 1: Introduction & Problem Setting (SWE-bench-style evaluation of Gemma 4 under strict time/compute budgets).
  - Section 2: System Architecture & Pacing Guardrails (`recovered_v2` design, Stop-and-Submit protocol, scratchpad isolation).
  - Section 3: Empirical Evaluation & Architecture Ablations (Integrate [`paper/tables/architecture_ablation.md`](file:///c:/Users/acquayefrank/Code/graft/paper/tables/architecture_ablation.md)).
  - Section 4: Failure Analysis & Qualitative Post-Mortem (Integrate `paper/tables/failure_taxonomy.md`).
  - Section 5: Discussion & Conclusion (Lessons learned on single vs multi-agent trade-offs in offline execution).
- Verify manuscript word count is $\le 3,000$ words.
- Commit as: `docs(paper): finalize research manuscript within 3000-word limit`.

---

## 6. Validation Pass

- Run all checks in `validation.md`:
  - `submission.zip` structure and schema check.
  - Leaderboard submission status check.
  - Word count and link validation for `paper/draft.md`.
  - Working tree cleanliness.

---

## 7. PR & Merge

- Open PR from `dev30-scaling-submission` into `main` and execute merge commit.
- PR description details final production packaging metrics, leaderboard submission ID, and finalized paper artifacts.
