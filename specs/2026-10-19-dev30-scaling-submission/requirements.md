# Dev30 Benchmark Scaling & Competition Submission — Requirements

**Roadmap source:** `specs/roadmap.md`, Phase 4 — "Dev30 Benchmark Scaling & Competition Submission". Phase 3 concluded with the empirical evaluation of the hierarchical sub-agent architecture (`subagent_v1`) on the 10-task screening benchmark (`dev10`) and populated `paper/tables/architecture_ablation.md`. Because the sub-agent triggered the formal fallback condition (< 56.7% resolution, > 260s latency), Phase 4 scales to full packaging and submission of the production single-agent candidate (`recovered_v2`), alongside comprehensive failure taxonomy analysis and finalization of the research manuscript.

**Branch:** `dev30-scaling-submission`, cut from `main` at commit `fe7b00a`.

---

## Scope

In scope, per roadmap Phase 4 and confirmed scoping decisions:

1. **Production Single-Agent Configuration Restoration (`recovered_v2`)**:
   - Reconfigure [`submission/agent.yaml`](file:///c:/Users/acquayefrank/Code/graft/submission/agent.yaml) to remove the `code_analyzer` sub-agent delegation tool and restore the full suite of local tools: `run_command`, `read_file`, `edit_file`, `write_file`, `search_similar_code`, `get_code_neighbors`, `get_code_subgraph`, `get_status`, and `submit_patch`.
   - Update [`submission/prompts/system.md`](file:///c:/Users/acquayefrank/Code/graft/submission/prompts/system.md) to single-agent navigation, strict time pacing (3.5-minute stop-and-submit ceiling), and scratchpad isolation (`build/repro.py`).
   - Retain sub-agent files (`submission/sub_agents/code_analyzer.yaml` and `submission/prompts/analyzer.md`) in the repository for research reproducibility while excluding them from the production submission manifest.

2. **Submission Packaging & Strict Sandboxed Compiler Verification**:
   - Update [`build_submission.py`](file:///c:/Users/acquayefrank/Code/graft/build_submission.py) to package and validate the production single-agent archive [`submission.zip`](file:///c:/Users/acquayefrank/Code/graft/submission.zip).
   - Validate against the official competition Pydantic model (`SandboxedAgentConfig` from `build/wheels/adk_submission-0.2.13-py3-none-any.whl`).
   - Verify archive size remains < 100 KB (well within the 3 GiB competition threshold).

3. **Official Competition Leaderboard Submission**:
   - Submit `submission.zip` to the primary Kaggle competition ([`gemma-4-developer-agent`](https://www.kaggle.com/competitions/gemma-4-developer-agent)) using the Kaggle CLI.
   - Record submission ID, timestamp, file hashes, and status in `results/leaderboard_submissions.md`.

4. **Comprehensive Trace Post-Mortem & Error Taxonomy**:
   - Execute trace post-mortem analysis across benchmark evaluation logs using [`eval/summarize_trace.py`](file:///c:/Users/acquayefrank/Code/graft/eval/summarize_trace.py).
   - Construct a structured failure taxonomy table in `paper/tables/failure_taxonomy.md` categorizing primary failure modes (patch synthesis errors, regex mismatch, import/dependency failures, and timeout/step ceilings).

5. **Research Paper Manuscript Finalization**:
   - Complete the empirical research manuscript in [`paper/draft.md`](file:///c:/Users/acquayefrank/Code/graft/paper/draft.md) targeting the *Google - The Gemma 4 Developer Agent Paper Track*.
   - Incorporate empirical results from [`paper/tables/architecture_ablation.md`](file:///c:/Users/acquayefrank/Code/graft/paper/tables/architecture_ablation.md) and the new failure taxonomy table.
   - Strictly enforce the competition paper track constraint: $\le 3,000$ words total.

---

## Explicitly Out of Scope

- **Additional Remote GPU Runs for `subagent_v1` on `dev30`**: Excluded by user decision to preserve GPU compute quota. The empirical findings from the 10-task screening benchmark (`dev10`) documented in Phase 3 provide sufficient empirical data for the architecture ablation study.
- **Model Weight Quantization or Fine-Tuning**: Model weights are fixed to the offline Google Gemma 4 31B W4A16 QAT checkpoint (`gemma-4-31b-it-qat-w4a16-ct`).
- **Dynamic Host Code / Arbitrary Python Imports**: All submissions must strictly conform to the declarative YAML specification without custom runtime hooks on the competition host.

---

## Decisions

1. **Architecture Focus for Production**: We are focusing production packaging and final evaluation exclusively on the single-agent `recovered_v2` configuration (53.3% dev30 baseline, 229.1s latency) because `subagent_v1` triggered the formal fallback condition during `dev10` screening. The sub-agent architecture is preserved and reported as an ablation study in the paper track.
2. **Sequencing of Deliverables**: We are packaging, validating, and submitting `submission.zip` to the Kaggle leaderboard first to initiate official scoring as early as possible, followed immediately by trace failure taxonomy extraction and finalization of `paper/draft.md`.
3. **Formal Merge Gate**: Merging Phase 4 into `main` requires:
   - Clean `submission.zip` validation (< 100 KB, 0 schema errors).
   - Successful Kaggle leaderboard submission logging with verified submission ID.
   - A finalized, publication-ready `paper/draft.md` ($\le 3,000$ words) incorporating empirical tables and failure taxonomy.

---

## Guardrails from mission.md / tech-stack.md

- **Dual-Track Mission Alignment (`mission.md` Section 2)**: Both Track 1 (Leaderboard) and Track 2 (Paper Track) deliverables must be completed and aligned with empirical provenance.
- **Strict Zero-Timeout Policy (`mission.md` Section 2.1)**: Production prompt must preserve the 3.5-minute hard ceiling and mandatory Stop-and-Submit rule.
- **Clean Code Hygiene (`mission.md` Section 2.1)**: Untracked reproduction scripts or temporary files must never leak into the patch diff (`build/` isolation + `rm` pre-submission cleanup).
- **Declarative Framework Constraints (`tech-stack.md` Section 3)**: Declarative YAML only (`agent.yaml`, `eval_config.yaml`, `prompts/system.md`), single declared model `gemma-4-31b-it-qat-w4a16-ct`, total package size $< 3\text{ GiB}$.
- **Paper Track Limits (`tech-stack.md` Section 7)**: Word count strictly bounded to $\le 3,000$ words.
