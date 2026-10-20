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

## Phase 3: Context Compaction & Architecture Exploration (Completed)

Phase 3 designed, implemented, and empirically evaluated a hierarchical sub-agent architecture (`subagent_v1`) featuring an isolated, read-only `code_analyzer` agent tool vs. the paced single-agent baseline (`recovered_v2`).

### Deliverables & Empirical Findings:
- **`eval/dev10.json`**: Curated balanced 10-task screening benchmark (5 Rich, 5 FastAPI).
- **Sub-Agent Implementation**: [`submission/sub_agents/code_analyzer.yaml`](file:///c:/Users/acquayefrank/Code/graft/submission/sub_agents/code_analyzer.yaml) and [`submission/prompts/analyzer.md`](file:///c:/Users/acquayefrank/Code/graft/submission/prompts/analyzer.md), integrated into root agent with ADK `SandboxedAgentConfig` schema compliance.
- **Remote Benchmark Screening**: Completed on Kaggle 4x L4 GPUs (4/10 resolved, 40.0% resolution, 298.7s mean latency).
- **Architecture Ablation Artifact**: Populated [`paper/tables/architecture_ablation.md`](file:///c:/Users/acquayefrank/Code/graft/paper/tables/architecture_ablation.md). Findings confirm strong compaction advantages on modular repos (3/5 on FastAPI), but show that turn-latency tax and delegation thrashing on open-ended tasks (Rich) cause session timeouts.
- **Decision Gate Outcome**: Fallback condition triggered (< 56.7% resolution, > 260s latency); `recovered_v2` is retained as the production configuration for competition leaderboard submission, while `subagent_v1` is documented in the Paper Track manuscript.
- **Branch**: Merged into `main`.

---

## Phase 4: Dev30 Benchmark Scaling & Competition Submission (Completed)

Phase 4 scaled benchmark validation, packaged the production single-agent architecture (`recovered_v2`), dispatched the official Kaggle leaderboard submission, extracted the empirical failure taxonomy, and finalized the research paper manuscript.

### Deliverables & Empirical Accomplishments:
- **Production Configuration (`recovered_v2`)**: Restored full 9 local tools (AST, graph embeddings, filesystem, telemetry), 3.5m pacing ceiling, and `build/repro.py` isolation in [`submission/agent.yaml`](file:///c:/Users/acquayefrank/Code/graft/submission/agent.yaml) and [`submission/prompts/system.md`](file:///c:/Users/acquayefrank/Code/graft/submission/prompts/system.md).
- **Packaging & Sandboxed Schema Validation**: [`build_submission.py`](file:///c:/Users/acquayefrank/Code/graft/build_submission.py) verified 3-file production archive [`submission.zip`](file:///c:/Users/acquayefrank/Code/graft/submission.zip) (3.02 KB) passing ADK `SandboxedAgentConfig` Pydantic validation with 0 errors.
- **Official Competition Submission**: Successfully dispatched to `gemma-4-developer-agent` via Kaggle CLI. Logged as **Ref `57407885`** (2026-10-19 20:00:09 UTC) in [`results/leaderboard_submissions.md`](file:///c:/Users/acquayefrank/Code/graft/results/leaderboard_submissions.md).
- **Trace Post-Mortem & Error Taxonomy**: Populated [`paper/tables/failure_taxonomy.md`](file:///c:/Users/acquayefrank/Code/graft/paper/tables/failure_taxonomy.md) analyzing all 14 failures in `dev30`, discovering the 15-line competence boundary (80% resolution on $\le 15$ line bugs, 0% on $> 15$ line bugs).
- **Finalized Research Manuscript**: Completed [`paper/draft.md`](file:///c:/Users/acquayefrank/Code/graft/paper/draft.md) at 2,327 words ($\le 3,000$ words limit) with full empirical tables, architecture ablation insights, and post-mortem analysis.
- **Branch**: Merged into `main`.

---

## Phase 5: Pacing Recalibration & Leaderboard Resubmission (Completed)

Following trace post-mortem and leaderboard analysis showing a 515-team cluster at 0.17 (10/60 tasks) and a premature emergency abort trigger in submission `57407885`, Phase 5 recalibrates agent pacing envelopes to prevent premature patch synthesis while strictly observing the competition's 6.0-minute per-task ceiling, verifies packaging integrity, and dispatches an official leaderboard resubmission.

### Deliverables & Empirical Accomplishments:
- **Pacing Envelope & Telemetry Recalibration**: Updated [`submission/prompts/system.md`](file:///c:/Users/acquayefrank/Code/graft/submission/prompts/system.md) to relax the emergency hard ceiling from 3.5m / 18 calls to 4.5m / 30 calls and shifted the `get_status` telemetry check to Turn 15, preventing premature aborts while maintaining a 30s buffer before the 5.0m target and preserving the mandatory Stop-and-Submit rule.
- **Packaging & Sandboxed Schema Conformance**: Built and validated [`submission.zip`](file:///c:/Users/acquayefrank/Code/graft/submission.zip) (3.01 KB) via [`build_submission.py`](file:///c:/Users/acquayefrank/Code/graft/build_submission.py) passing all schema and budget checks with 0 errors.
- **Official Competition Leaderboard Resubmission**: Dispatched `submission.zip` to `gemma-4-developer-agent` via Kaggle CLI. Assigned official **Ref `57454091`** (2026-10-20 21:51:18 UTC), currently pending evaluation, and logged in [`results/leaderboard_submissions.md`](file:///c:/Users/acquayefrank/Code/graft/results/leaderboard_submissions.md).
- **Branch**: Merged into `main`.

---

## Phase 6: Trace-Grounded Protocol Calibration & Paper Track Integration

Following trace-level empirical discovery across `dev30` execution logs showing termination deadlocks (`fastapi_13920`), 39 repeated `edit_file` parameter-mangling failures (`rich_4076`, `rich_3052`, `rich_3675`), zero-telemetry turn blindness (0/30 calls to `get_status`), and repro-script thrashing (`rich_3063`, `rich_3935`), Phase 6 hardens agent protocol contracts, updates paper track findings, and prepares a verified candidate package ready for leaderboard dispatch upon daily quota reset.

### Micro-Phase 6.1: Execution Protocol Hardening
- **Task**: Update [`submission/prompts/system.md`](file:///c:/Users/acquayefrank/Code/graft/submission/prompts/system.md):
  - Add mandatory Clean-Exit Termination rule: emit zero tool calls and a plain-text confirmation on the turn following `submit_patch()`, satisfying harness completion criteria (`not has_function_call and context.patch_submitted`).
  - Add immediate `edit_file` fallback rule: if `edit_file` fails once with missing `old_string`, immediately fall back to a python one-liner with `run_command` or `write_file`.
  - Shift telemetry triggers from abstract turn counts to event-driven checkpoints: call `get_status` if reproduction fails on turn 1, or after any search error.
- **Deliverable**: Hardened `submission/prompts/system.md`.
- **Verification**: Prompt diff review and internal contract validation.

### Micro-Phase 6.2: Submission Packaging & Sandboxed Verification
- **Task**: Build [`submission.zip`](file:///c:/Users/acquayefrank/Code/graft/submission.zip) using [`build_submission.py`](file:///c:/Users/acquayefrank/Code/graft/build_submission.py) and verify against `adk_submission` SandboxedAgentConfig schema (< 100 KB package size).
- **Deliverable**: Verified `submission.zip` candidate ready for Kaggle dispatch at 00:00 UTC.
- **Verification**: Run `python build_submission.py` with 0 validation errors.

### Micro-Phase 6.3: Paper Track Empirical Insights Integration
- **Task**: Update [`paper/draft.md`](file:///c:/Users/acquayefrank/Code/graft/paper/draft.md) and [`paper/tables/failure_taxonomy.md`](file:///c:/Users/acquayefrank/Code/graft/paper/tables/failure_taxonomy.md) with trace-level discoveries:
  - Document the Termination Deadlock phenomenon in open-weight agent harnesses.
  - Document tool argument mangling (token concatenation of JSON keys) on docstrings with parentheses.
  - Document turn blindness and the failure of turn-based telemetry prompts.
  - Verify total paper word count remains strictly $\le 3,000$ words.
- **Deliverable**: Updated manuscript [`paper/draft.md`](file:///c:/Users/acquayefrank/Code/graft/paper/draft.md) and taxonomy table.
- **Verification**: Word count audit and empirical citation consistency check.



