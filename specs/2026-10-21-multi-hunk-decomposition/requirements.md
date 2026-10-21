# Multi-Hunk Patch Decomposition & Syntax Pre-Flight — Requirements

**Roadmap source:** `specs/roadmap.md`, Phase 7 — "Multi-Hunk Patch Decomposition & Syntax Pre-Flight".

Trace analysis across `dev30` revealed a sharp 15-line competence boundary: Gemma 4 31B resolves 80.0% (16/20) of tasks requiring 1–15 lines of diff, but 0.0% (0/10) of tasks requiring > 15 lines. Across medium tasks (`rich_3052`, `rich_3675`, `rich_3938`, `rich_4006`, `fastapi_15588`), the agent experienced multi-site edit thrashing (partially applying a fix, prematurely re-testing, rolling back valid edits) and syntax dropouts that failed Container B's `py_compile` verification layer.

Phase 7 hardens the agent's multi-site editing capabilities and pre-submission validation to break the 0% medium-task barrier and expand resolution beyond the 15-line boundary.

**Branch:** `multi-hunk-decomposition`, cut from `main` at commit `7352a04`.

---

## Scope

In scope, per roadmap Phase 7 and confirmed scoping decisions:

1. **Multi-Hunk Decomposition Protocol (`submission/prompts/system.md`)**:
   - **Upfront Hunk Enumeration**: When a bug spans multiple functions or files (or > 15 lines of logic), the agent must explicitly enumerate all target hunks (files, functions, exact line ranges) in its reasoning thought *before* calling `edit_file`.
   - **Deferred Verification**: Full reproduction and test re-runs are deferred until all enumerated hunks are placed, preventing premature rollback of partial fixes.
   - **Orderly Multi-File Placement**: Place edits sequentially file-by-file following the enumerated plan.

2. **Pre-Submission Syntax Pre-Flight Guardrail (`submission/prompts/system.md`)**:
   - **Mandatory `py_compile` Check**: Before calling `submit_patch()`, the agent must run `python -m py_compile <modified_file>` via `run_command` on all modified source files.
   - **Syntax Error Remediation**: If `py_compile` reports an `IndentationError` or `SyntaxError`, the agent must remediate it immediately using the 1-strike Python one-liner fallback before submission.

3. **Packaging & Schema Validation (`build_submission.py`)**:
   - Rebuild [`submission.zip`](file:///c:/Users/acquayefrank/Code/graft/submission.zip) with updated prompt definitions.
   - Verify zero schema validation errors under `SandboxedAgentConfig` and archive size < 100 KB.

4. **Empirical Evaluation on Medium Tasks**:
   - Evaluate the 5 medium-complexity tasks from `dev30` (`rich_3052`, `rich_3675`, `rich_3938`, `rich_4006`, `fastapi_15588`) on Kaggle 4x L4 GPUs to empirically verify resolution of at least 1 medium task.

---

## Explicitly Out of Scope

- **Modifying Agent Tools**: The 9 native sandboxed tools remain unchanged.
- **Sub-Agent Delegation**: Production architecture remains the single-agent `recovered_v2` baseline; no multi-agent routing.
- **Physical Checklist Files**: The agent plans hunks in reasoning thoughts; no scratchpad files (like `build/hunks.txt`) are created to avoid filesystem clutter.

---

## Decisions

1. **Upfront Thought Planning**: Enforce explicit upfront hunk enumeration in reasoning thoughts before applying edits, deferring test re-runs until all listed hunks are placed. This eliminates the cognitive thrashing observed on `rich_3052` and `rich_3675`.
2. **Pre-Submission Syntax Gate**: Insert a mandatory pre-submission check in Step 5 (VERIFY): run `python -m py_compile` on all modified files, falling back to 1-strike Python one-liners if syntax errors appear. This catches malformed indentations before Container B rejects them.
3. **Medium-Task Verification Split**: Evaluate on the 5 medium-complexity tasks from `dev30` on Kaggle 4x L4 GPUs, requiring at least 1 task resolved (breaking the 0% medium barrier) and zero syntax failures.

---

## Guardrails from mission.md / tech-stack.md

- **Strict Zero-Timeout Policy (`mission.md` Section 2.1)**: Multi-hunk planning must observe the 4.5m pacing ceiling and Stop-and-Submit rule.
- **Clean Diff Hygiene (`mission.md` Section 2.1)**: Only library source files are modified; `py_compile` runs in-memory without generating `.pyc` files in tracked directories.
- **Sandboxed Agent Compiler Integrity (`tech-stack.md` Section 3)**: Purely declarative YAML/Markdown configuration passing `SandboxedAgentConfig` validation.
