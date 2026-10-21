# Trace-Grounded Protocol Calibration & Paper Track Integration — Validation

How to know Phase 6 is actually done and `trace-protocol-paper-integration` can merge into `main`.

---

## 1. System Prompt Protocol Conformance

- Inspect [`submission/prompts/system.md`](file:///c:/Users/acquayefrank/Code/graft/submission/prompts/system.md):
  - Clean-Exit Rule is present and explicit: emit text only with zero tool calls after `submit_patch()`.
  - `edit_file` fallback rule is present: 1-strike fallback to Python one-liner or `write_file`.
  - Event-driven telemetry trigger is present: call `get_status` if repro fails on attempt 1, or after any tool error.
  - Diff check against `main` confirms additions are coherent and preserve pacing invariants.

## 2. Submission Packaging & Schema Conformance

- Run submission build script:
  ```bash
  python build_submission.py
  ```
- Validation criteria:
  - Return code is `0`.
  - Console outputs `SandboxedAgentConfig validation: PASSED (0 errors)`.
  - `submission.zip` size is strictly `< 100 KB` (actual ~3.1 KB).
  - SHA256 checksum is computed and ready for logging upon dispatch.

## 3. Paper Track Manuscript & Taxonomy Conformance

- Word count audit:
  ```bash
  python -c "p = open('paper/draft.md').read(); words = len(p.split()); assert words <= 3000, f'Word count {words} exceeds 3000'"
  ```
- Taxonomy table inspection:
  - [`paper/tables/failure_taxonomy.md`](file:///c:/Users/acquayefrank/Code/graft/paper/tables/failure_taxonomy.md) incorporates Termination Deadlock, Parameter Mangling, and Turn Blindness.
- Manuscript content inspection:
  - [`paper/draft.md`](file:///c:/Users/acquayefrank/Code/graft/paper/draft.md) Section 4 discusses the termination loop and token concatenation dynamics.

---

## Merge Criteria

All checks above pass cleanly. The formal merge gate requires clean ADK schema validation (`SandboxedAgentConfig` PASSED, 0 errors, < 100 KB), pre-staged `submission.zip`, and an updated `paper/draft.md` within the 3,000-word limit.
