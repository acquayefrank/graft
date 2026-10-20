# Pacing Recalibration & Leaderboard Resubmission — Requirements

**Roadmap source:** `specs/roadmap.md`, Phase 5 — "Pacing Recalibration & Leaderboard Resubmission". Phase 4 concluded with the baseline submission `57407885` (scoring 0.15) and trace failure analysis revealing premature emergency aborts (at 3.5m / 18 calls) caused hasty patch synthesis on tasks that needed just 1–2 more inspection turns. With a dense cluster of competitors at 0.17 (10/60 tasks) on the public leaderboard, Phase 5 recalibrates agent pacing envelopes to prevent premature patch synthesis while strictly observing the competition's 6.0-minute per-task ceiling, verifies packaging integrity, and dispatches an official leaderboard resubmission.

**Branch:** `pacing-recalibration-resubmission`, cut from `main` at commit `ce11dd5`.

---

## Scope

In scope, per roadmap Phase 5 and confirmed scoping decisions:

1. **Pacing Envelope & Status Check Recalibration (`submission/prompts/system.md`)**:
   - Relax the emergency hard ceiling from 3.5 minutes / 18 tool calls to 4.5 minutes / 30 tool calls. This provides ample headroom beyond the 229s dev30 mean runtime while keeping a 30s safety margin before 5.0m (and well within the 6.0m competition container limit).
   - Shift `get_status` telemetry check instruction from Turn 10 to Turn 15, matching the expanded turn envelope.
   - Retain and reinforce the mandatory Stop-and-Submit rule: the moment reproduction or target test passes, immediately call `submit_patch()` to prevent session overrun.

2. **Submission Packaging & Sandboxed Verification (`build_submission.py`)**:
   - Execute `build_submission.py` to package [`submission.zip`](file:///c:/Users/acquayefrank/Code/graft/submission.zip).
   - Perform strict schema validation against ADK `SandboxedAgentConfig` (from `build/wheels/adk_submission-0.2.13-py3-none-any.whl`).
   - Verify zero schema errors and archive size < 100 KB (actual package ~3.1 KB).

3. **Official Kaggle Leaderboard Resubmission**:
   - Dispatch `submission.zip` to the primary competition [`gemma-4-developer-agent`](https://www.kaggle.com/competitions/gemma-4-developer-agent) via Kaggle CLI.
   - Record submission ID, timestamp, sha256 checksum, and status in [`results/leaderboard_submissions.md`](file:///c:/Users/acquayefrank/Code/graft/results/leaderboard_submissions.md).

---

## Explicitly Out of Scope

- **Screening on `dev10` or `dev30` Remote Benchmark**: Excluded by user decision to conserve remote 4x L4 GPU compute quota and prioritize fast turnaround on the live competition leaderboard. The dev30 baseline and trace taxonomy already established behavioral grounding.
- **Architectural Changes to Tools or Sub-Agents**: Root agent configuration ([`submission/agent.yaml`](file:///c:/Users/acquayefrank/Code/graft/submission/agent.yaml)) remains the proven single-agent `recovered_v2` baseline with 9 native tools. No sub-agent delegation is introduced.
- **Dynamic Code Hooks or Host Python Entrypoints**: Strictly adhere to declarative YAML and Markdown prompts per ADK sandboxed constraints.

---

## Decisions

1. **Pacing Thresholds**: We are setting the hard ceiling to 4.5 minutes / 30 tool calls with status check at Turn 15, because post-mortem analysis of submission `57407885` and `dev30` traces demonstrated that the prior 3.5m ceiling triggered premature aborts during code exploration on solvable tasks, while 4.5m provides headroom over the 229s mean while preserving a safe buffer before the 5.0m target and 6.0m container timeout.
2. **Execution Workflow**: We are using a direct verification and dispatch workflow (updating `submission/prompts/system.md`, running `build_submission.py`, and immediately submitting to Kaggle) rather than running an intermediate `dev10` benchmark, because remote GPU quota is limited and the prompt calibration is targeted and low-risk.
3. **Merge Gate**: Merging this branch requires clean `build_submission.py` schema verification (< 100 KB, 0 errors) and a confirmed, logged Kaggle submission ID in `results/leaderboard_submissions.md`. We do not block merge on waiting for Kaggle scoring to complete, since evaluation runs asynchronously over multiple hours.

---

## Guardrails from mission.md / tech-stack.md

- **Strict Zero-Timeout Policy (`mission.md` Section 2.1)**: While relaxing from 3.5m to 4.5m, the hard ceiling must remain strictly under the ~5.0m task budget (and 6.0m competition limit).
- **Clean Code Hygiene (`mission.md` Section 2.1)**: Ensure scratch scripts and temporary artifacts are isolated under `build/` and removed before patch submission.
- **Sandboxed Agent Compiler Integrity (`tech-stack.md` Section 3)**: Declarative YAML and Markdown files must pass `SandboxedAgentConfig` Pydantic validation without warnings or errors, package size < 3 GiB (target < 100 KB).
- **Tool Registry Budget Discipline (`tech-stack.md` Section 4)**: `submit_patch` and `get_status` remain free/uncounted, while filesystem and graph tools consume step budget.
