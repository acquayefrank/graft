# Trace-Grounded Protocol Calibration & Paper Track Integration — Plan

Numbered task groups. Each represents a discrete, reviewable step moving toward submission readiness and paper completion.

---

## 1. Harden Execution Protocols in System Prompt

- Edit [`submission/prompts/system.md`](file:///c:/Users/acquayefrank/Code/graft/submission/prompts/system.md):
  - In Section 5 ("VERIFY & STOP") and Section 6 ("SUBMIT"), add the mandatory Clean-Exit protocol:
    `After submit_patch() returns {"status": "ok"}, on your NEXT turn you MUST output ONLY a short completion text message with ZERO tool calls. DO NOT call submit_patch() or any tool again.`
  - In Section 4 ("FIX"), update `edit_file` instructions:
    Always emit `old_string` before `new_string`. Add 1-strike fallback rule: if `edit_file` fails once, do not retry with `edit_file`; immediately use a Python one-liner with `run_command` or rewrite with `write_file`.
  - In Section "Pacing & Timeout Prevention", replace Turn 15 check with event-driven triggers: call `get_status` if repro fails on attempt 1, or after any tool error; trigger emergency abort when `time_seconds_remaining < 90`.
- Verify prompt diff and confirm no conflicting instructions.

## 2. Package & Pre-Stage Submission Archive

- Run [`build_submission.py`](file:///c:/Users/acquayefrank/Code/graft/build_submission.py).
- Verify:
  - `submission.zip` is assembled containing `agent.yaml`, `eval_config.yaml`, and updated `prompts/system.md`.
  - Pydantic schema validation passes with 0 errors.
  - Archive size is < 100 KB.
  - SHA256 checksum is calculated and logged.

## 3. Update Paper Track Taxonomy & Manuscript

- Update [`paper/tables/failure_taxonomy.md`](file:///c:/Users/acquayefrank/Code/graft/paper/tables/failure_taxonomy.md):
  - Expand Failure Category I and III with the empirical discoveries: Termination Deadlock (`fastapi_13920`), Parameter Mangling (`rich_4076`, `rich_3052`), and Turn Blindness.
- Update [`paper/draft.md`](file:///c:/Users/acquayefrank/Code/graft/paper/draft.md) Section 4:
  - Add subsection discussing the open-weight agent-harness termination handshake and token concatenation failure modes.
  - Audit word count to ensure the manuscript remains strictly $\le 3,000$ words.

## 4. Validation Pass

- Run the checks specified in [`validation.md`](file:///c:/Users/acquayefrank/Code/graft/specs/2026-10-20-trace-protocol-paper-integration/validation.md).
- Fix any discrepancies or schema issues prior to merge.

## 5. PR & Merge Gate

- Open / prepare merge from `trace-protocol-paper-integration` into `main`.
- Pre-stage submission dispatch instructions for the 00:00 UTC daily quota reset.
