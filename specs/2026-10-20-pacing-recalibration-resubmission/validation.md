# Pacing Recalibration & Leaderboard Resubmission — Validation

How to know Phase 5 is actually done and `pacing-recalibration-resubmission` can merge into `main`.

---

## 1. System Prompt Pacing Calibration

- Inspect [`submission/prompts/system.md`](file:///c:/Users/acquayefrank/Code/graft/submission/prompts/system.md):
  - Hard ceiling specifies: `If elapsed time reaches 4.5 minutes (or tool calls reach 30), STOP ALL SEARCHING.`
  - Status check specifies: `Check get_status if you reach Turn 15.`
  - Mandatory Stop-and-Submit rule is present under Section 5 ("VERIFY & STOP") and Section 6 ("Pacing & Timeout Prevention").
  - Diff check against `main` confirms only pacing parameters and telemetry turns changed without inadvertent deletions.

## 2. Submission Packaging & Sandboxed Schema Conformance

- Run submission build script:
  ```bash
  python build_submission.py
  ```
- Validation criteria:
  - Return code is `0`.
  - Console outputs `SandboxedAgentConfig validation: PASSED (0 errors)`.
  - `submission.zip` size is strictly `< 100 KB` (actual ~3.1 KB).
  - Package contains only declarative runtime assets (`agent.yaml`, `prompts/system.md`).

## 3. Kaggle Leaderboard Submission Dispatch & Provenance

- Dispatch verification:
  - Command `kaggle competitions submissions -c gemma-4-developer-agent` reflects the newly created submission ID.
- Provenance logging:
  - [`results/leaderboard_submissions.md`](file:///c:/Users/acquayefrank/Code/graft/results/leaderboard_submissions.md) includes a new table row with:
    - Official Kaggle Submission ID / Ref.
    - Timestamp (UTC).
    - Architecture label: `recovered_v2 (4.5m / 30 calls pacing recalibration)`.
    - Exact SHA256 checksum matching local `submission.zip`.
    - Submission status (e.g., `pending` / `successfully submitted`).

---

## Merge Criteria

All three check categories above pass cleanly. The formal merge gate requires clean ADK schema validation (`SandboxedAgentConfig` PASSED, 0 errors, < 100 KB) and a confirmed, logged Kaggle submission ID in `results/leaderboard_submissions.md`.

Once merged into `main`, re-open `specs/roadmap.md` to identify subsequent evaluation or analysis milestones.
