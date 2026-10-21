# Failure Mode Taxonomy & Post-Mortem Analysis (`dev30`)

Empirical failure mode taxonomy derived from trace-level post-mortem analysis across the 30-task development benchmark ([`eval/dev30.json`](file:///c:/Users/acquayefrank/Code/graft/eval/dev30.json)) under the production `recovered_v2` single-agent configuration.

---

## 1. Failure Mode Taxonomy Table

| Failure Category | Primary Mechanism | Frequency in Dev30 | Exemplar Tasks | Root Cause Analysis | Architectural / Pacing Mitigation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **I. Scale Horizon Timeout** | Diff volume exceeds single-turn editing capacity under time budget | **6 / 14 (42.9%)** | `rich_3061` (134L)<br>`rich_4070` (88L)<br>`fastapi_14419` (102L)<br>`rich_3930` (176L)<br>`fastapi_15661` (155L)<br>`rich_4006` (45L) | Multi-site refactoring across 3+ files exhausts the operational budget during symbol location and call-graph traversal before all edit hunks can be synthesized. | Time-awareness ceiling ensures clean exit rather than unbounded hang; future work requires hierarchical multi-hunk patch planning. |
| **II. Partial Patch / Tool Parameter Mangling** | Token concatenation corrupts JSON parameters, forcing fallback to crude regex | **4 / 14 (28.6%)** | `rich_4076` (6L)<br>`rich_3052` (34L)<br>`rich_3675` (18L)<br>`fastapi_15588` (23L) | Across `rich_4076`, `3052`, and `3675`, 39 consecutive `edit_file` calls failed as docstrings with parentheses and quotes caused the model to emit `,old_string:` inside text scalars, dropping mandatory parameters. Panicked fallbacks to `sed -i` broke secondary assertions. In `fastapi_15588`, the agent sanitized `\n` but missed `\r` carriage returns. | Mandatory 1-strike fallback to Python one-liners via `run_command` prevents turn wasting; strict `old_string`-first parameter ordering eliminates JSON key corruption. |
| **III. Harness Deadlock & Turn Blindness** | Protocol violation after submission or unbounded repro-thrashing from lack of temporal grounding | **4 / 14 (28.6%)** | `fastapi_13920` (4L)<br>`rich_3063` (2L)<br>`rich_3935` (7L)<br>`rich_3938` (28L) | In `fastapi_13920`, a valid 1566-byte patch was submitted at Turn 37, but the agent emitted `submit_patch()` tool calls for 36 consecutive turns, violating the harness termination contract (`not has_function_call`) until timing out at 6.0m. In `rich_3063` and `3935`, turn blindness (0/30 tasks heeded turn-based prompts) caused 15+ turns of repro rewriting without ever touching library source. | Mandatory Clean-Exit protocol (text-only final turn with zero tool calls) guarantees clean harness exit; event-driven telemetry checkpoints replace ineffective turn counts. |

---

## 2. Complexity Bucket Resolution Breakdown (`dev30`)

Empirical resolution rate structured by ground-truth patch complexity:

| Patch Complexity Bucket | Ground-Truth Size | Evaluated Tasks | Resolved Tasks | Resolution Rate | Mean Latency | Primary Failure Mode |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Tiny** | 1–5 lines | 12 | **10** | **83.3%** | 172.4s | Termination Deadlock (1), Repro Thrashing (1) |
| **Small** | 6–15 lines | 8 | **6** | **75.0%** | 204.8s | Repro Thrashing (1), Tool Mangling (1) |
| **Combined (Tiny + Small)** | **1–15 lines** | **20** | **16** | **80.0%** | **184.6s** | **80% Production Baseline** |
| **Medium** | 16–50 lines | 5 | 0 | 0.0% | 311.2s | Tool Parameter Mangling (3), Scale Timeout (2) |
| **Large** | 51–150 lines | 3 | 0 | 0.0% | 360.0s | Scale Horizon Timeout (3) |
| **Huge** | > 150 lines | 2 | 0 | 0.0% | 360.0s | Scale Horizon Timeout (2) |
| **Overall Dev30** | — | **30** | **16** | **53.3%** | **229.1s** | **Projected 7.64h for 120 Tasks** |

---

## 3. Key Research Insights for Paper Section 4

1. **The 15-Line Competence Boundary**:
   Under an offline, ~5-minute budget with open-weight 31B models, autonomous agents exhibit a sharp phase transition at $\approx 15$ lines of diff complexity. Below 15 lines, the agent resolves **80.0% (16 of 20)** of real-world bugs across heterogeneous repositories. Beyond 15 lines, cognitive drift across multi-file edits and turn-latency ceilings dominate.

2. **The Agent-Harness Termination Handshake**:
   In SWE-bench evaluation harnesses, calling a terminal tool (`submit_patch()`) is insufficient on its own. The session orchestrator requires a conversational completion event (`not has_function_call and context.patch_submitted`). When models emit tool calls alongside final completion text, a fatal deadlock ensues. In `fastapi_13920`, this single pathology converted a 100% correct 4-line patch into a 0-point timeout.

3. **Tool Parameter Serialization Fragility**:
   When editing complex docstrings with parentheses, quotes, and newlines, Gemma 4 frequently concatenated argument identifiers into string scalars (e.g. `...,old_string:`), causing 39 consecutive tool invocation errors across `rich_4076`, `3052`, and `3675`. Agents must have immediate 1-strike execution fallbacks (such as direct Python one-liners via bash) rather than retrying fragile tool APIs.

4. **Zero-Telemetry Turn Blindness**:
   Prompt instructions directing agents to "check status if you reach Turn 10/15" failed universally: across 30 tasks, `get_status` was called exactly 0 times. Open-weight LLMs have no internal counter or temporal grounding. Pacing triggers must be tied to deterministic tool failure events (e.g., failure of `build/repro.py` on attempt 1) rather than abstract turn numbers.

5. **Single vs. Hierarchical Failure Dynamics**:
   Comparing `recovered_v2` single-agent failure logs with `subagent_v1` traces demonstrates that hierarchical sub-agents did not resolve the Scale Horizon boundary; instead, sub-agent delegation introduced an additional turn-latency tax that pushed previously resolved tiny/small tasks (e.g. `rich_3470`) across the timeout boundary.

