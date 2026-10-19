# Mission & Operating Constitution

## 1. Executive Summary

**Project Graft** is an autonomous software engineering agent built for the **Google Gemma 4 Developer Agent Competition** on Kaggle.

The competition evaluates agents against real-world GitHub issues across diverse Python repositories in SWE-bench-style environments. The objective is to produce clean, minimal, and fully passing unified git diff patches that resolve reported bugs and feature requests while passing hidden unit tests.

---

## 2. Core Mission & Objectives: Dual-Track Execution

Project Graft operates as a **dual-track project**:

### Track 1: Leaderboard Benchmark Track (`gemma-4-developer-agent`)
1. **Maximize Resolution Rate**: Maximize the fraction of benchmark tasks resolved (`resolved = True`, `score = 1.0`) on the official evaluation split under strict operational budgets.
2. **Deterministic & Robust Patch Generation**: Generate surgical, syntactically valid patches targeting the repository's library code. Never modify protected test suites or test runner configurations (`conftest.py`, `pytest.ini`, `setup.cfg`).
3. **Strict Zero-Timeout Policy**: Tasks operate under a hard wall-clock budget (~5.0 minutes average per task over ~120 tasks in a 12-hour window). An imperfect or plausible patch submitted at minute 4 is infinitely more valuable than a perfect patch lost to a timeout at minute 5.
4. **Clean Code Hygiene**: Guarantee that scratch reproduction scripts, temporary debug files, or untracked artifacts never leak into `agent_patch` through `git add -N .`.

### Track 2: Research Paper Track (`gemma-4-developer-agent-paper`)
1. **Empirical Agentic SE Research**: Author an impactful research paper (up to 3,000 words Kaggle writeup / paper) documenting novel empirical findings on deploying Gemma 4 in constrained, offline software engineering environments.
2. **Rigorous Ablation Studies**: Systematically ablate and measure:
   - *Prompt & Budget Engineering*: The impact of time-awareness, concise thinking limits, and early submission fail-safes on resolution rate vs. timeout rates.
   - *Tool Modalities*: Comparing AST/embedding code intelligence tools (`search_similar_code`, `get_code_neighbors`) against raw bash/grep exploration.
   - *Architecture*: Single-agent baseline vs. read-only sub-agent delegation (`code_analyzer` with `skip_summarization: true`).
   - *Thinking Token Dynamics*: Trade-offs between reasoning token budget (`thinking_budget: 2048` vs `4096`), generation latency, and tool-call truncation.
3. **Open Research Artifacts**: Share reproducible traces (ATIF format), evaluation methodologies, and failure taxonomy to advance open-weight agent research.

---

## 3. Operating Philosophy: Remote-First Execution

Due to hardware and storage constraints on the local developer machine:
- **No Local Model Inference**: Gemma 4 31B W4A16 requires 4x NVIDIA L4 GPUs (96 GB total VRAM) and heavy vLLM serving infrastructure.
- **No Local Repository Bloat**: Git snapshots, dependency wheels, and container sandboxes remain hosted entirely in the Kaggle cloud environment.
- **Local Role**:
  - Declarative agent architecture design (`agent.yaml`, sub-agents).
  - Prompt engineering and behavioral calibration (`prompts/system.md`).
  - Budget optimization (`eval_config.yaml`).
  - Automated dataset synchronization and remote dispatching.
  - Granular post-mortem analysis of downloaded execution traces (`traces/trace_*.json`).
- **Remote Role**:
  - Kaggle cloud notebook execution on dedicated 4x NVIDIA L4 GPUs.
  - Headless batch evaluation across benchmark tasks (`graft-dev-eval.ipynb`).
  - Hermetic Phase 2 verification in isolated Docker containers with JUnit XML report scoring.

---

## 4. Guiding Engineering Principles

- **Trace-Driven Development**: Every prompt or architectural change must be justified and evaluated by analyzing execution traces (`final_metrics`, tool call timelines, error observations, and token consumption).
- **Parsimony Over Complexity**: Start with a single, highly disciplined `LlmAgent` before adding hierarchical multi-agent overhead. Every additional agent turn adds latency and token cost.
- **Fail Gracefully**: The agent must catch failed commands, missing modules, or failed edits, adapt immediately without entering repetitive loops, and call `submit_patch` as its fail-safe terminal action.
- **Strict Compliance**: Adhere strictly to the competition constraints (single declared model, declarative YAML only, no dynamic Python entrypoints, < 3 GiB total submission size).
