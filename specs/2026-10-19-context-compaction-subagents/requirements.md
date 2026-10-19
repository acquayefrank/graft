# Context Compaction & Architecture Exploration — Requirements

**Roadmap source:** `specs/roadmap.md`, Phase 3 — "Context Compaction & Architecture Exploration". Phases 1 and 2 successfully eliminated path traversal bugs and established the Stop-and-Submit protocol, lifting resolution rate to 53.3% (16/30 tasks) in `recovered_v2`. Phase 3 explores sampling hyperparameters (temperature, thinking token budget) and a read-only `code_analyzer` sub-agent to prevent context window bloat and generate ablation data for the Paper Track.

**Branch:** `context-compaction-subagents`, cut from `main` at commit `c22da0f` (baseline repository commit containing all specs, evaluation harness, prompt assets, and paper manuscript).

---

## Scope

In scope, per roadmap Phase 3 plus the user decisions confirmed in Step 3:

1. **Sampling & Generation Budget Optimization (Micro-Phase 3.1)**:
   - Benchmark generation temperature ($0.0$ vs $0.1$ vs $0.2$) and nucleus sampling $top\_p$ ($0.95$).
   - Calibrate `thinking_budget` in `submission/agent.yaml` ($1024$ vs $2048$ tokens) to determine whether deeper reasoning improves complex edit synthesis without triggering turn latency timeouts.
   - Deliver optimized `agent.yaml` parameters.

2. **Read-Only Analyzer Sub-Agent Implementation (Micro-Phase 3.2)**:
   - Define declarative sub-agent `submission/sub_agents/code_analyzer.yaml` powered by `gemma-4-31b-it-qat-w4a16-ct`.
   - Wrap `code_analyzer` as an `AgentTool` with `skip_summarization: true` within root `agent.yaml`.
   - Implement the **Hybrid Tool Responsibility Model**:
     - Sub-agent (`code_analyzer`): Assigned `search_similar_code`, `get_code_neighbors`, `get_code_subgraph`, `read_file`, and `run_command` (restricted to grep/find operations). Its prompt focuses strictly on symbol localization, code navigation, and identifying responsible files/functions.
     - Root agent (`coder`): Retains `read_file` (for reviewing exact lines before editing and inspecting diffs), `edit_file`, `write_file`, `submit_patch`, `get_status`, and the `code_analyzer` tool. This avoids the multi-turn latency penalty of delegating trivial line reads while isolating massive repository search dumps outside the root context.

3. **Curated 10-Task Screening Benchmark (`eval/dev10.json`)**:
   - Create a fast 10-task subset representative of the 30-task dev benchmark across both repositories (`Textualize/rich` and `fastapi/fastapi`) and all difficulty buckets (`tiny`, `small`, `medium`).
   - Use `dev10` for rapid ablation screening of candidate hyperparameter and sub-agent configurations.

4. **Paper Track Architecture & Hyperparameter Ablation (Micro-Phase 3.3)**:
   - Formulate and populate `paper/tables/architecture_ablation.md` with empirical comparisons across metrics: resolution rate, mean agent seconds, mean wall-clock seconds, root context token efficiency, and tool call distributions.
   - Document trade-offs between single-agent velocity and hierarchical sub-agent reasoning for the manuscript.

---

## Explicitly Out of Scope

1. **Python Dynamic Entrypoints or Host Execution**:
   - The competition sandbox strictly prohibits Python hooks or dynamic wrapper scripts on the host (`adk-submission` declarative YAML only). All sub-agent interactions must adhere strictly to Google ADK declarative syntax.

2. **Recursive or Multi-Level Hierarchies**:
   - Sub-agents may not invoke further sub-agents. The hierarchy is capped at 1 level (Root `coder` $\to$ Sub-agent `code_analyzer`) to prevent unbounded recursive turn expansions and timeout exhaustion.

3. **Modifying Phase 2 Verification Sandboxes**:
   - Offline container lifecycle, wheel caching, and JUnit XML verification mechanisms remain fixed as defined in `specs/tech-stack.md`.

4. **Exhaustive Grid Search on Dev30**:
   - To conserve Kaggle 4x L4 GPU quota, exhaustive 30-task runs are not executed for every sub-variation; screening runs are restricted to `dev10`.

---

## Decisions (Confirmed with the User)

1. **Hybrid Tool Responsibility Model**:
   - *Decision*: The root `coder` agent retains `read_file` alongside `edit_file`, `write_file`, and `submit_patch`, while `code_analyzer` handles symbol graph queries, regex grep scans, and deep exploration.
   - *Rationale*: Forcing the root agent to invoke `code_analyzer` for every 10-line inspection introduces an unnecessary 15–20s LLM forward pass per turn; allowing direct local `read_file` preserves velocity while the sub-agent absorbs large exploratory traces.

2. **2-Tier Staged Remote Evaluation**:
   - *Decision*: Screening passes will evaluate on a representative 10-task split (`dev10.json`). Only the top-performing candidate architecture will be dispatched for the full 30-task `dev30` run.
   - *Rationale*: A full 30-task run requires ~2 hours of 4x L4 compute. Running `dev10` cuts evaluation time to ~35 minutes, accelerating ablation iterations.

3. **Strict Leaderboard Adoption Resolution Gate**:
   - *Decision*: The sub-agent architecture will only replace the single-agent baseline (`recovered_v2`, 53.3% resolution, 229.1s latency) as the primary leaderboard entry if it achieves $\ge 56.7\%$ resolution (17+ of 30 tasks) on `dev30` while keeping mean agent latency under 260s.
   - *Rationale*: In accordance with `mission.md` Principle 2 (Parsimony Over Complexity), multi-agent overhead is only justified on the leaderboard if it yields measurable net resolution gains; if it matches or underperforms, it remains an empirical contribution for the Paper Track.

---

## Guardrails from mission.md / tech-stack.md

1. **Parsimony Over Complexity (`mission.md`, Section 4)**:
   - Sub-agent instruction prompts must be dense, clear, and focused solely on localization. Never allow exploratory loops between sub-agent and root.

2. **Zero-Timeout Pacing (`mission.md`, Section 2)**:
   - Invocations to `code_analyzer` count toward the root agent's turn and time budgets. Total session budget remains bounded by `eval_config.yaml` (`max_time_minutes: 6`, `timeout_seconds: 30`).

3. **Declarative Compliance (`tech-stack.md`, Section 3)**:
   - All sub-agents must reside under `submission/sub_agents/` and be referenced via valid YAML without path traversal (`!include`).

4. **Archive Size Constraint (`tech-stack.md`, Section 3)**:
   - The compiled `submission.zip` package must remain well under the 3 GiB limit (< 10 KB for prompt and configuration files).
