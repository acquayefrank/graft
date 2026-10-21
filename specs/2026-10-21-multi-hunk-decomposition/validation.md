# Multi-Hunk Patch Decomposition & Syntax Pre-Flight — Validation

How to know Phase 7 is actually done and `multi-hunk-decomposition` can merge into `main`.

---

## 1. System Prompt Protocol Conformance

- Inspect [`submission/prompts/system.md`](file:///c:/Users/acquayefrank/Code/graft/submission/prompts/system.md):
  - Multi-hunk planning rule is present: enumerate all target hunks in thought before editing, and defer test re-runs until all hunks are placed.
  - Syntax pre-flight rule is present: run `python -m py_compile <file>` on all modified source files prior to submission.
  - Diff check against `main` confirms additions are coherent, preserving the Clean-Exit protocol, 1-strike fallback, and Stop-and-Submit pacing.

## 2. Packaging & Schema Conformance

- Run submission build script:
  ```bash
  python build_submission.py
  ```
- Validation criteria:
  - Exit code is `0`.
  - Schema validation against `SandboxedAgentConfig` passes with `0` errors.
  - `submission.zip` size is strictly `< 100 KB`.
  - SHA256 checksum is computed and logged.

## 3. Remote Benchmark Verification (`medium5`)

- Execute remote evaluation on Kaggle 4x L4 GPUs across the 5 medium-complexity tasks from `dev30`:
  `rich_3052`, `rich_3675`, `rich_3938`, `rich_4006`, `fastapi_15588`.
- Validation criteria:
  - **Resolution Rate**: At least 1 of 5 medium tasks resolved cleanly ($\ge 20.0\%$), successfully breaking the 0.0% medium-task boundary.
  - **Zero Syntax Rejections**: No task fails in Container B due to syntax or compilation errors.
  - **Clean Execution**: All resolved tasks observe the Clean-Exit protocol and Stop-and-Submit rule without infinite loops or runner deadlocks.

---

## Merge Criteria

All checks above pass cleanly. The formal merge gate requires clean ADK schema validation (`SandboxedAgentConfig` PASSED, 0 errors, < 100 KB), empirical resolution of $\ge 1$ medium task on the remote GPU benchmark, and clean `build_submission.py` packaging.
