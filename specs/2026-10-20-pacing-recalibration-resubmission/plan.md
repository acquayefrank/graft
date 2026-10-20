# Pacing Recalibration & Leaderboard Resubmission — Plan

Numbered task groups. Each represents a discrete, reviewable step moving toward the final leaderboard resubmission.

---

## 1. Recalibrate Pacing & Telemetry Envelopes in System Prompt

- Edit [`submission/prompts/system.md`](file:///c:/Users/acquayefrank/Code/graft/submission/prompts/system.md):
  - In Section 5 ("Pacing & Timeout Prevention"), update the telemetry check instruction: `Check get_status if you reach Turn 15.` (formerly Turn 10).
  - Update the emergency hard ceiling: `If elapsed time reaches 4.5 minutes (or tool calls reach 30), STOP ALL SEARCHING.` (formerly 3.5 minutes / 18 calls).
  - Retain the mandatory Stop-and-Submit rule: immediately call `submit_patch()` once reproduction or target tests pass.
- Verify prompt syntax and review diff for clarity and absence of conflicting instructions.

## 2. Build Submission Archive & Validate Sandboxed Schema

- Execute [`build_submission.py`](file:///c:/Users/acquayefrank/Code/graft/build_submission.py).
- Verify:
  - `submission.zip` is assembled containing `agent.yaml` and `prompts/system.md`.
  - Pydantic schema validation against `SandboxedAgentConfig` completes with 0 errors.
  - Archive uncompressed and compressed size is < 100 KB.
  - SHA256 checksum is calculated and logged.

## 3. Dispatch Submission to Kaggle Leaderboard & Update Tracking

- Dispatch `submission.zip` to competition `gemma-4-developer-agent` using Kaggle CLI via WSL:
  `kaggle competitions submit -c gemma-4-developer-agent -f submission.zip -m "recovered_v2 with 4.5m / 30-call pacing recalibration"`
- Query Kaggle CLI for submission status and retrieve official submission ID (`ref`).
- Update [`results/leaderboard_submissions.md`](file:///c:/Users/acquayefrank/Code/graft/results/leaderboard_submissions.md) with new row recording:
  - Ref ID
  - Date and time (UTC)
  - Submission message / config summary
  - Archive size and SHA256 hash
  - Status (Pending / Successfully submitted)

## 4. Validation Pass

- Run the checks specified in [`validation.md`](file:///c:/Users/acquayefrank/Code/graft/specs/2026-10-20-pacing-recalibration-resubmission/validation.md).
- Fix any discrepancies or validation errors prior to PR merge.

## 5. PR & Merge Gate

- Open / prepare merge from `pacing-recalibration-resubmission` into `main`.
- Document confirmed submission ID and schema validation outcome in merge commit description.
