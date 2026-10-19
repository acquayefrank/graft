# Implementation Roadmap

This roadmap breaks down the development of **Project Graft** into small, sequential micro-phases. Each micro-phase has concrete deliverables, explicit verification steps, and clear exit criteria.

---

## Phase 1: Prompt & Timeout Hardening

The smoke test run (`smoke5`) achieved 40% (2/5 resolved), but 2 out of 3 failures were due to the agent exceeding the **5.0-minute wall-clock timeout** while trapped in unproductive exploration loops, and attempting invalid `/tmp` paths with `write_file`.

### Micro-Phase 1.1: Fix Tool Usage & Scratchpad Pathing
- **Task**: Update [`submission/prompts/system.md`](file:///c:/Users/acquayefrank/Code/graft/submission/prompts/system.md) to explicitly distinguish filesystem tools from bash commands:
  - `write_file` accepts workspace-relative paths only (e.g., `build/repro.py`). Emphasize that passing `/tmp/...` triggers `Path traversal detected` errors.
  - If using `/tmp`, write via `run_command` with bash redirection or `python3 -c`.
- **Deliverable**: Refined `system.md` with explicit tool parameter rules.
- **Verification**: Inspect prompt diff; verify no contradictory instructions.

### Micro-Phase 1.2: Enforce Wall-Clock & Turn Discipline
- **Task**: Implement strict pacing rules in the system prompt:
  - Cap thought duration to 2–3 sentences before emitting a tool call.
  - Spend at most 2 tool calls attempting reproduction; if reproduction fails, proceed directly to locating and fixing the issue.
  - Instruct the agent to check `get_status` if it has performed > 15 tool calls.
  - Mandate that if time is running out (elapsed > 3.5 minutes), immediately apply the best plausible fix and call `submit_patch()`.
- **Deliverable**: Pacing and timeout prevention section in `prompts/system.md`.
- **Verification**: Review prompt wording for clarity and imperative tone.

### Micro-Phase 1.3: Remote Push & Smoke5 Validation
- **Task**: Package the Phase 1 submission, push to Kaggle via [`push_submission_dataset.sh`](file:///c:/Users/acquayefrank/Code/graft/push_submission_dataset.sh), and execute `smoke5` on Kaggle 4x L4 GPUs.
- **Deliverable**: New run results downloaded to `results/smoke5_v2/`.
- **Exit Criteria**: Zero tasks failing due to `Agent exceeded session timeout (5.0 min)`; resolution rate >= 60% (3/5).

---

## Phase 2: Repro/Scratchpad Hygiene & Tool Guardrails

### Micro-Phase 2.1: Pre-Submission Cleanup Guardrails
- **Task**: Because `submit_patch()` runs `git add -N . && git diff HEAD`, untracked files in `/workspace` outside `build/` contaminate the diff.
  - Reinforce rule to only write scratch scripts to `build/repro.py` (which is in `.gitignore` / `.git/info/exclude`).
  - Instruct the agent to run `git status` and `rm` any rogue scratch files before calling `submit_patch()`.
- **Deliverable**: Updated pre-submission protocol in `prompts/system.md`.
- **Verification**: Verify generated patches from `results/` contain zero untracked test scripts.

### Micro-Phase 2.2: Precision `edit_file` & Code Intelligence Tuning
- **Task**:
  - Instruct the agent to keep `old_string` in `edit_file` to 2–6 exact lines to prevent matching ambiguities or token limits.
  - Teach effective usage of graph tools: pass short symbol names (e.g. `Class.method`) to `search_similar_code` and `get_code_neighbors`.
  - Warn against running missing test targets (e.g. `tests/test_union_body` without `.py`) and advise running targeted test functions with `-k <test_name>`.
- **Deliverable**: Enhanced editing and test execution guidelines in `prompts/system.md`.
- **Verification**: Trace analysis confirming fewer `FileEditError` and `CommandError` instances.

### Micro-Phase 2.3: Remote Smoke5 Regression Check
- **Task**: Push dataset version and validate against the `smoke5` set.
- **Deliverable**: Downloaded results and summary.
- **Exit Criteria**: Target task `fastapi_12942` resolves cleanly; resolution rate >= 60–80% on `smoke5`.

---

## Phase 3: Context Compaction & Architecture Exploration

### Micro-Phase 3.1: Sampling & Generation Budget Tuning
- **Task**: Benchmark `temperature` (0.0 vs 0.2), `top_p` (0.95), and `thinking_budget` (2048 vs 4096) in [`submission/agent.yaml`](file:///c:/Users/acquayefrank/Code/graft/submission/agent.yaml).
- **Deliverable**: Optimized `agent.yaml` generation config.
- **Verification**: Compare token consumption and solution quality in traces.

### Micro-Phase 3.2: Read-Only Analyzer Sub-Agent Evaluation
- **Task**: Test separating repository exploration from code editing:
  - Configure a read-only `code_analyzer` wrapped as an `AgentTool` (`skip_summarization: true`).
  - Keeps large `read_file` outputs and symbol searches in an isolated sub-agent context, preserving the root coder agent's context window.
- **Deliverable**: `submission/sub_agents/code_analyzer.yaml` and updated root `agent.yaml`.
- **Verification**: Evaluate on 10 dev tasks; assess whether context savings outweigh the slight multi-agent latency overhead.

### Micro-Phase 3.3: Paper Track - Architecture & Token Ablation
- **Task**: Synthesize the empirical comparison between single-agent and sub-agent architectures, plus thinking token budget trade-offs.
- **Deliverable**: `paper/tables/architecture_ablation.md` with metrics (resolution rate, token efficiency, turn latency).

---

## Phase 4: Dev30 Benchmark Scaling & Competition Submission

### Micro-Phase 4.1: Dev30 Benchmark Run
- **Task**: Run the full 30-task development benchmark ([`eval/dev30.json`](file:///c:/Users/acquayefrank/Code/graft/eval/dev30.json)) on Kaggle.
- **Deliverable**: Comprehensive evaluation metrics across all 30 tasks, categorized by repository and issue complexity buckets (`tiny`, `small`, `medium`).
- **Verification**: Resolution rate >= 40–50% across the full 30 tasks within the 12-hour compute window.

### Micro-Phase 4.2: Comprehensive Trace Post-Mortem & Error Taxonomy
- **Task**: Run [`eval/summarize_trace.py`](file:///c:/Users/acquayefrank/Code/graft/eval/summarize_trace.py) across all failed tasks in Dev30. Categorize remaining failure modes:
  - Incomplete edits
  - Over-broad regex replacements
  - Test suite import failures
  - Token exhaustion
- **Deliverable**: Failure taxonomy table for paper Section 4 ("Failure Analysis").

### Micro-Phase 4.3: Submission Packaging & Verification
- **Task**: Run [`build_submission.sh`](file:///c:/Users/acquayefrank/Code/graft/build_submission.sh) to assemble `submission.zip`.
  - Validate total package size < 3 GiB.
  - Verify that `agent.yaml` is at the zip root with valid YAML syntax.
  - Confirm all `!include` references resolve correctly without path traversal.
- **Deliverable**: Production-ready `submission.zip`.
- **Verification**: Test extraction and schema check against competition validator.

### Micro-Phase 4.4: Dual Track Submission
- **Task 1 (Leaderboard)**: Upload `submission.zip` to the primary competition ([`gemma-4-developer-agent`](https://www.kaggle.com/competitions/gemma-4-developer-agent)).
- **Task 2 (Paper Track)**: Finalize `paper/draft.md` (<= 3,000 words), generate plots/tables, and publish the research writeup to the Paper Track ([`gemma-4-developer-agent-paper`](https://www.kaggle.com/competitions/gemma-4-developer-agent-paper)).
- **Deliverable**: Official public leaderboard score and published Kaggle research paper.
