# Trace-Grounded Protocol Calibration & Paper Track Integration — Requirements

**Roadmap source:** `specs/roadmap.md`, Phase 6 — "Trace-Grounded Protocol Calibration & Paper Track Integration". Deep-dive analysis across all 14 failed tasks in [`results/smoke5_v2/results/recovered_v2/traces/`](file:///c:/Users/acquayefrank/Code/graft/results/smoke5_v2/results/recovered_v2/traces/) and harness audit of [`swegemma/harness/agent_runner.py`](file:///c:/Users/acquayefrank/Code/graft/build/wheels/swegemma-0.2.11-py3-none-any.whl) uncovered three critical execution failures: (1) a termination deadlock on `fastapi_13920` (36 consecutive redundant `submit_patch()` tool calls violating the harness completion condition), (2) 39 consecutive failed `edit_file` calls across `rich_4076`, `rich_3052`, and `rich_3675` caused by token concatenation mangling JSON parameters, and (3) complete turn blindness resulting in 0 of 30 tasks ever calling `get_status`. Phase 6 hardens agent execution protocols in `submission/prompts/system.md`, pre-stages `submission.zip` for the 00:00 UTC quota reset, and integrates these empirical discoveries into the paper track manuscript.

**Branch:** `trace-protocol-paper-integration`, cut from `main` at commit `8512577`.

---

## Scope

In scope, per roadmap Phase 6 and confirmed scoping decisions:

1. **Execution Protocol Hardening (`submission/prompts/system.md`)**:
   - **Mandatory Clean-Exit Rule**: Immediately upon `submit_patch()` returning `status: ok`, output ONLY a concise plain-text message (e.g. "Patch complete.") with ZERO tool calls. Explicitly warn the model that emitting any tool call after `submit_patch()` prevents session termination and triggers a fatal container timeout.
   - **`edit_file` Fast-Fallback Rule**: Strictly emit `old_string` before `new_string`. If `edit_file` fails even once with missing `old_string` or syntax error, do not retry with `edit_file`; immediately apply the fix using a Python one-liner via `run_command` (`python -c "p=open('file.py').read(); open('file.py','w').write(p.replace('''OLD''','''NEW'''))"`) or rewrite with `write_file`.
   - **Event-Driven Telemetry Checkpoints**: Replace turn-number prompts ("Turn 10/15") with concrete event triggers:
     - If `python build/repro.py` does not reproduce the bug on attempt 1, immediately stop reproducing, call `get_status()`, and move directly to fixing library code.
     - If any tool returns an error, call `get_status()`.
     - If `time_seconds_remaining < 90`, trigger the emergency abort protocol immediately.

2. **Submission Packaging & Pre-Staging (`build_submission.py`)**:
   - Rebuild [`submission.zip`](file:///c:/Users/acquayefrank/Code/graft/submission.zip) with hardened `prompts/system.md`.
   - Validate against ADK `SandboxedAgentConfig` Pydantic model with 0 errors and size < 100 KB.
   - Pre-stage package for dispatch to `gemma-4-developer-agent` once daily quota resets at 00:00 UTC.

3. **Paper Track Empirical Insights Integration (`paper/draft.md`, `paper/tables/failure_taxonomy.md`)**:
   - Update [`paper/tables/failure_taxonomy.md`](file:///c:/Users/acquayefrank/Code/graft/paper/tables/failure_taxonomy.md) to document the Termination Deadlock, Tool Argument Mangling, and Turn Blindness mechanisms.
   - Integrate empirical discussion into [`paper/draft.md`](file:///c:/Users/acquayefrank/Code/graft/paper/draft.md) Section 4 ("Empirical Failure Mode Taxonomy").
   - Strictly maintain overall word count $\le 3,000$ words.

---

## Explicitly Out of Scope

- **Modifying Tools or Sub-Agent Hierarchy**: The declarative agent configuration ([`submission/agent.yaml`](file:///c:/Users/acquayefrank/Code/graft/submission/agent.yaml)) remains the single-agent `recovered_v2` baseline with 9 native tools.
- **Model Checkpoint Tuning**: Model remains offline `gemma-4-31b-it-qat-w4a16-ct`.

---

## Decisions

1. **Protocol Package Selection**: We are adopting the full protocol package (Clean-Exit text-only turn, 1-strike edit fallback to Python one-liners, and event-driven telemetry triggers). Analysis revealed that turn-based triggers failed completely (0/30 calls) and tool retry loops cost 39 wasted calls on small, solvable tasks.
2. **Sequenced Workflow**: We are hardening and packaging `submission/prompts/system.md` first to have `submission.zip` pre-staged for the 00:00 UTC daily quota reset, followed immediately by updating `paper/draft.md` with the new findings.
3. **Multi-Gate Validation**: Merging Phase 6 requires 0 schema validation errors on `build_submission.py` (< 100 KB), pre-staged `submission.zip`, and an updated `paper/draft.md` within the 3,000-word limit.

---

## Guardrails from mission.md / tech-stack.md

- **Strict Zero-Timeout Policy (`mission.md` Section 2.1)**: Clean-exit and event-driven triggers directly enforce termination before the 5.0m task budget and 6.0m container hard ceiling.
- **Paper Track Word Ceiling (`mission.md` Section 2.2)**: Total text must strictly remain $\le 3,000$ words.
- **Sandboxed Agent Compiler Integrity (`tech-stack.md` Section 3)**: Submissions must be purely declarative and pass `SandboxedAgentConfig` validation.
